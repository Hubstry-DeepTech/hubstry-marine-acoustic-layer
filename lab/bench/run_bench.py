"""Executa os ensaios B1–B5 e B7 da bancada digital HMAL.

Uso:
  python lab/bench/run_bench.py --criteria 0.3.1 --receiver v2      # critérios v0.3.1, matriz matrix.json
  python lab/bench/run_bench.py --criteria 0.4.0 --receiver v3      # critérios v0.4, matriz matrix_v04.json
  python lab/bench/run_bench.py --limit 10 --smoke                  # fumaça; resultados não definitivos
  python lab/bench/run_bench.py --matrix outra.json --smoke         # matriz de desenvolvimento; nunca definitiva

Saída: lab/bench/results/<ensaio>.json e lab/bench/results/summary.json.
Os critérios e a matriz não são alterados por este script.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from fractions import Fraction
from functools import lru_cache
from math import gcd, lcm
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import beta

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

from hmal.core.harmonic_protocol import HarmonicProtocol, RationalChannel  # noqa: E402
from receiver import Receiver, ReceiverV2, ReceiverV3, detection_threshold, h_n  # noqa: E402

# Cada versão de critérios fixa sua matriz e o SNR mínimo do critério B3(c). A versão 0.3.1 continua executável.
CRITERIA = {
    "0.3.1": {"matrix": "matrix.json", "b3c_min_snr_db": 16},
    "0.4.0": {"matrix": "matrix_v04.json", "b3c_min_snr_db": 20},
}
RECEIVERS = {"v1": Receiver, "v2": ReceiverV2, "v3": ReceiverV3}
# Variáveis de ambiente: herdadas pelos workers também com start_method "spawn"
RECEIVER_VERSION = os.environ.get("HMAL_RECEIVER", "v1")
CRITERIA_VERSION = os.environ.get("HMAL_CRITERIA", "0.3.1")
MATRIX_PATH = Path(os.environ.get("HMAL_MATRIX") or HERE / CRITERIA[CRITERIA_VERSION]["matrix"])
MATRIX_TEXT = MATRIX_PATH.read_text(encoding="utf-8") if MATRIX_PATH.exists() else None
MATRIX = json.loads(MATRIX_TEXT) if MATRIX_TEXT else {}
B3C_MIN_SNR = CRITERIA[CRITERIA_VERSION]["b3c_min_snr_db"]
RESULTS = HERE / "results" / RECEIVER_VERSION
# Ensaios usados no desenvolvimento do receptor v2 (lab/bench/RECEIVER_V2.md): índices 0..DEV-1 da matriz v0.3.0.
# Matrizes novas declaram seus próprios índices (0 = nenhum ensaio de desenvolvimento).
DEV_B3 = MATRIX.get("holdout_first_index", {}).get("b3", 20)
DEV_B4 = MATRIX.get("holdout_first_index", {}).get("b4", 30)


# ----------------------------------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------------------------------
def matrix_is_official() -> bool:
    return MATRIX_PATH.resolve() == (HERE / CRITERIA[CRITERIA_VERSION]["matrix"]).resolve()


def env_info(smoke: bool) -> dict:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:  # pragma: no cover
        commit = "desconhecido"
    return {
        "criteria_version": CRITERIA_VERSION,
        "matrix_version": MATRIX["version"],
        "matrix_file": MATRIX_PATH.name,
        "matrix_sha256": hashlib.sha256(MATRIX_TEXT.encode("utf-8")).hexdigest(),
        "matrix_seed": MATRIX.get("seed"),
        "noise_seed_offset": MATRIX.get("noise_seed_offset", 0),
        "b3c_min_snr_db": B3C_MIN_SNR,
        "commit": commit,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "libc": "".join(platform.libc_ver()),
        "receiver": RECEIVER_VERSION,
        "definitive": (not smoke) and matrix_is_official(),
    }


def mode_cfg(name: str) -> dict:
    return MATRIX["modes"][name]


@lru_cache(maxsize=None)
def receiver_for(name: str, f0: float | None = None) -> Receiver:
    m = mode_cfg(name)
    return RECEIVERS[RECEIVER_VERSION](m["fs_hz"], m["duration_s"], m["f0_hz"] if f0 is None else f0)


def synth(name: str, channels: list, polarities: list, f0: float | None = None) -> tuple[np.ndarray, float]:
    """Gera o sinal pelo gerador do HMAL e devolve (s, A), com A a amplitude efetiva por tom."""
    m = mode_cfg(name)
    f0 = m["f0_hz"] if f0 is None else f0
    proto = HarmonicProtocol(f0_base=f0, harmonic_order=16, mode="bench")
    pairs = [tuple(c) for c in channels]
    t, s = proto.generate_waveform(pairs, m["duration_s"], sample_rate=m["fs_hz"], phase_polarities=list(polarities))
    raw = np.zeros_like(t)
    for (a, b), p in zip(pairs, polarities):
        raw += np.sin(2 * np.pi * (a / b) * f0 * t + (np.pi if p else 0.0))
    A = 1.0 / float(np.max(np.abs(raw)))
    if not np.allclose(A * raw, s, rtol=0.0, atol=1e-9):
        raise RuntimeError("gerador divergiu da expressão analítica (tolerância absoluta 1e-9)")
    return s, A


def acrb(snr_db: float, fs: float, N: int) -> float:
    snr_lin = 10 ** (snr_db / 10)
    eta = snr_lin / N
    return math.sqrt(12 * fs**2 / ((2 * math.pi) ** 2 * eta * N * (N**2 - 1)))


def sigma_for(A: float, N: int, snr_db: float) -> float:
    return math.sqrt(A**2 * N / (2 * 10 ** (snr_db / 10)))


def exact_recovery(decoded: dict, channels: list) -> bool:
    got = sorted(tuple(c["ratio"]) for c in decoded["channels"] if c["accepted"])
    want = sorted(tuple(c) for c in channels)
    return len(got) == len(decoded["channels"]) and got == want


def outcome(decoded: dict, channels: list) -> str:
    """Classifica um ensaio: "ok" (recuperação exata), "misidentified" (algum canal aceito com razão errada)
    ou "rejected" (nenhuma razão errada aceita, mas algum canal verdadeiro não foi aceito)."""
    if exact_recovery(decoded, channels):
        return "ok"
    want = {tuple(c) for c in channels}
    if any(c["accepted"] and tuple(c["ratio"] or ()) not in want for c in decoded["channels"]):
        return "misidentified"
    return "rejected"


def save(name: str, payload: dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"{name}.json").write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------------------------
# B1
# ----------------------------------------------------------------------------------------------
def run_b1() -> dict:
    out = {}
    for n, expected in ((16, 159), (32, 647)):
        pairs = [(a, b) for a in range(1, n + 1) for b in range(1, n + 1) if gcd(a, b) == 1]
        vals = sorted(Fraction(a, b) for a, b in pairs)
        out[f"H_{n}"] = {
            "cardinality": len(pairs),
            "expected": expected,
            "all_coprime": all(gcd(a, b) == 1 for a, b in pairs),
            "unique_values": len(set(vals)) == len(vals),
        }
    hn = h_n()
    min_gap = min(b - a for a, b in zip(hn, hn[1:]))
    out["min_gap_H16"] = str(min_gap)
    passed = (
        all(v["cardinality"] == v["expected"] and v["all_coprime"] and v["unique_values"] for k, v in out.items() if k.startswith("H_"))
        and min_gap == Fraction(1, 240)
    )
    return {"test": "B1", "passed": passed, "details": out}


# ----------------------------------------------------------------------------------------------
# B2
# ----------------------------------------------------------------------------------------------
def b2_errors(name: str, trial: dict) -> list[float]:
    s, _ = synth(name, trial["channels"], trial["polarities"])
    rx = receiver_for(name)
    K = len(trial["channels"])
    dec = rx.decode(s, K)
    f0 = mode_cfg(name)["f0_hz"]
    truths = sorted(c[0] / c[1] * f0 for c in trial["channels"])
    ests = sorted(c["f_est"] for c in dec["channels"])
    if len(ests) != K:  # canal ausente não pode ser mascarado pelo zip
        return [math.inf] * K
    return [abs(e - t) for e, t in zip(ests, truths)]


def run_b2(modes: list[str], limit: int | None) -> dict:
    res: dict = {"test": "B2", "modes": {}}
    passed = True
    for name in modes:
        T = mode_cfg(name)["duration_s"]
        b2 = mode_cfg(name)["b2"]
        single = b2["single"][:limit] if limit else b2["single"]
        multi = (b2["k2"] + b2["k3"])[: limit or None]
        e_single = [max(b2_errors(name, t)) for t in single]
        e_multi = [max(b2_errors(name, t)) for t in multi]
        ok_s = max(e_single) <= 0.01 / T
        ok_m = max(e_multi) <= 0.05 / T
        passed &= ok_s and ok_m
        res["modes"][name] = {
            "single": {"n": len(e_single), "max_error_hz": max(e_single), "limit_hz": 0.01 / T, "passed": ok_s},
            "multi": {"n": len(e_multi), "max_error_hz": max(e_multi), "limit_hz": 0.05 / T, "passed": ok_m},
        }
    res["passed"] = passed
    return res


# ----------------------------------------------------------------------------------------------
# B3 (paralelo por ensaio)
# ----------------------------------------------------------------------------------------------
def b3_trial(args) -> dict:
    name, trial, snrs = args
    s, A = synth(name, trial["channels"], trial["polarities"])
    rx = receiver_for(name)
    N = rx.N
    K = len(trial["channels"])
    w = np.random.default_rng(trial["noise_seed"]).standard_normal(N)
    f0 = mode_cfg(name)["f0_hz"]
    truth = trial["channels"][0][0] / trial["channels"][0][1] * f0
    out = {"A": A, "noise_free": exact_recovery(rx.decode(s, K), trial["channels"]), "ok": [], "err": [], "cls": []}
    out["fail_diag"] = []
    for snr in snrs:
        dec = rx.decode(s + sigma_for(A, N, snr) * w, K)
        cls = outcome(dec, trial["channels"])
        ok = cls == "ok"
        out["ok"].append(ok)
        out["cls"].append(cls)
        if not ok and snr >= 20:
            out["fail_diag"].append({"snr_int_db": snr, "true": trial["channels"], "decoded": dec})
        if K == 1:
            out["err"].append(dec["channels"][0]["f_est"] - truth)
    return out


B3_CONDITIONS = ("k1", "k2", "k3", "worst_pair_0", "worst_pair_1")


def run_b3(modes: list[str], limit: int | None, workers: int, snrs: list[int], only: list[str] | None = None) -> dict:
    res: dict = {"test": "B3", "snr_int_db": snrs, "modes": {}}
    passed = True
    for name in modes:
        m = mode_cfg(name)
        rx = receiver_for(name)
        conds = {k: m["b3"][k] for k in ("k1", "k2", "k3")}
        for p, trials in enumerate(m["b3"]["worst_pairs"]):
            conds[f"worst_pair_{p}"] = trials
        res["modes"][name] = {}
        if only:
            conds = {k: v for k, v in conds.items() if k in only}
        for cname, trials in conds.items():
            trials = trials[:limit] if limit else trials
            with Pool(workers) as pool:
                rows = pool.map(b3_trial, [(name, t, snrs) for t in trials], chunksize=4)
            ok = np.array([r["ok"] for r in rows])
            rate = ok.mean(axis=0).tolist()
            nf = float(np.mean([r["noise_free"] for r in rows]))
            hi = [i for i, s in enumerate(snrs) if s >= 20]
            c_a = nf == 1.0
            c_b = all(rate[i] >= 0.99 for i in hi)
            cls = np.array([r["cls"] for r in rows])
            entry = {
                "n_trials": len(rows),
                # diagnóstico: separação entre identificação incorreta (canal aceito com razão errada),
                # rejeição/perda (canal verdadeiro não aceito) e falha total de recuperação (soma das duas)
                "diagnostic_misidentification_rate": (cls == "misidentified").mean(axis=0).tolist(),
                "diagnostic_rejection_rate": (cls == "rejected").mean(axis=0).tolist(),
                "diagnostic_total_recovery_failure_rate": (cls != "ok").mean(axis=0).tolist(),
                "noise_free_recovery": nf,
                "recovery_rate": rate,
                "criterion_a_noise_free_100": c_a,
                "criterion_b_ge99_at_snr_ge20": c_b,
                "A_effective": [r["A"] for r in rows],
                "per_trial_ok": ok.astype(int).tolist(),
                "holdout_first_index": DEV_B3,
                "holdout_recovery_rate": ok[DEV_B3:].mean(axis=0).tolist() if len(rows) > DEV_B3 else None,
                "failures_snr_ge20": [dict(d, trial_index=i, noise_seed=trials[i]["noise_seed"]) for i, r in enumerate(rows) for d in r["fail_diag"]][:50],
            }
            cond_pass = c_a and c_b
            if cname == "k1":
                err = np.array([r["err"] for r in rows])
                rms = np.sqrt(np.mean(err**2, axis=0)).tolist()
                bound = [acrb(s, rx.fs, rx.N) for s in snrs]
                gec = [i for i, s in enumerate(snrs) if s >= B3C_MIN_SNR]
                c_c = all(rms[i] <= 1.5 * bound[i] for i in gec)
                # diagnóstico complementar (não entra na decisão): erro de identificação de canal e
                # RMS condicionado à identificação correta; o RMS global continua sendo o critério
                cond = [float(np.sqrt(np.mean(err[ok[:, i], i] ** 2))) if ok[:, i].any() else None for i in range(len(snrs))]
                gross = (np.abs(err) > 1.0 / rx.T).sum(axis=0).astype(int).tolist()
                entry.update({
                    "rms_error_hz": rms, "acrb_hz": bound, "rms_over_acrb": [r / b for r, b in zip(rms, bound)],
                    f"criterion_c_rms_le_1p5_acrb_snr_ge{B3C_MIN_SNR}": c_c,
                    "diagnostic_gross_errors_gt_1_over_T": gross,
                    # RMS só entre os ensaios com identificação correta E canal aceito; não é a precisão de todos
                    "diagnostic_rms_given_correct_and_accepted_over_acrb": [None if c is None else c / b for c, b in zip(cond, bound)],
                    # erro de frequência por ensaio (Hz), linhas = ensaios, colunas = grade de SNR: permite
                    # recalcular de forma independente o RMS global e o condicional
                    "per_trial_freq_error_hz": err.tolist(),
                })
                cond_pass &= c_c
            entry["passed"] = cond_pass
            passed &= cond_pass
            res["modes"][name][cname] = entry
            print(f"  B3 {name}/{cname}: noise_free={nf:.3f} rate@20dB+={min(rate[i] for i in hi):.3f} passed={cond_pass}", flush=True)
    res["passed"] = passed
    return res


# ----------------------------------------------------------------------------------------------
# B4
# ----------------------------------------------------------------------------------------------
def b4_trial(args) -> dict:
    name, trial, eps_list, snr = args
    m = mode_cfg(name)
    rx = receiver_for(name)
    K = len(trial["channels"])
    chans = [[1, 1]] + trial["channels"]
    pols = [0] + trial["polarities"]
    w = np.random.default_rng(trial["noise_seed"]).standard_normal(rx.N)
    oks, As, diags = [], [], []
    for eps in eps_list:
        s, A = synth(name, chans, pols, f0=m["f0_hz"] * (1 + eps))
        dec = rx.decode(s + sigma_for(A, rx.N, snr) * w, K, pilot=True)
        ok = exact_recovery(dec, trial["channels"])
        oks.append(ok)
        As.append(A)
        if not ok:
            diags.append({"epsilon": eps, "f0_true": m["f0_hz"] * (1 + eps), "true": trial["channels"], "decoded": dec})
    return {"ok": oks, "A": As, "fail_diag": diags}


def run_b4(modes: list[str], limit: int | None, workers: int) -> dict:
    eps_list = MATRIX["b4_epsilon"]
    snr = MATRIX["b4_snr_int_db"]
    res: dict = {"test": "B4", "epsilon": eps_list, "snr_int_db": snr, "modes": {}}
    passed = True
    for name in modes:
        res["modes"][name] = {}
        for k in ("k1", "k2"):
            trials = mode_cfg(name)["b4"][k]
            trials = trials[:limit] if limit else trials
            with Pool(workers) as pool:
                rows = pool.map(b4_trial, [(name, t, eps_list, snr) for t in trials], chunksize=4)
            rate = np.array([r["ok"] for r in rows]).mean(axis=0).tolist()
            ok = all(r >= 0.99 for r in rate)
            passed &= ok
            okm = np.array([r["ok"] for r in rows])
            res["modes"][name][k] = {
                "n_trials": len(rows), "recovery_rate": rate, "passed": ok, "A_effective": [r["A"] for r in rows],
                "per_trial_ok": okm.astype(int).tolist(), "holdout_first_index": DEV_B4,
                "holdout_recovery_rate": okm[DEV_B4:].mean(axis=0).tolist() if len(rows) > DEV_B4 else None,
                "failures": [dict(d, trial_index=i, noise_seed=trials[i]["noise_seed"]) for i, r in enumerate(rows) for d in r["fail_diag"]][:50],
            }
            print(f"  B4 {name}/{k}: min_rate={min(rate):.3f} passed={ok}", flush=True)
    res["passed"] = passed
    return res


# ----------------------------------------------------------------------------------------------
# B5
# ----------------------------------------------------------------------------------------------
def run_b5(modes: list[str], limit: int | None) -> dict:
    res: dict = {"test": "B5", "B5_SEED": 5, "note": "o fluxo de números aleatórios é compartilhado entre modos na ordem de --modes", "modes": {}}
    passed = True
    rng = np.random.default_rng(5)  # semente fixa registrada no resultado (B5_SEED)
    for name in modes:
        m = mode_cfg(name)
        f0 = m["f0_hz"]
        proto = HarmonicProtocol(f0_base=f0, harmonic_order=16, mode="bench")
        sets = m["b2"]["single"] + m["b2"]["k2"] + m["b2"]["k3"]
        sets = sets[:limit] if limit else sets
        worst, n_min = 0.0, 0
        for trial in sets:
            ch = [tuple(c) for c in trial["channels"]]
            W = proto.sync_window(ch)
            t = rng.uniform(0, W, 1000)
            sgn = [(-1.0 if p else 1.0) for p in trial["polarities"]]

            def s(tt):
                return sum(g * np.sin(2 * np.pi * (a / b) * f0 * tt) for (a, b), g in zip(ch, sgn))

            ref = np.max(np.abs(s(np.linspace(0, W, 4001))))
            worst = max(worst, float(np.max(np.abs(s(t + W) - s(t))) / ref))
            L = lcm(*[b for _, b in ch])
            g = 0
            for a, b in ch:
                g = gcd(g, a * L // b)
            n_min += int(g == 1)
        ok = worst <= 1e-9
        passed &= ok
        res["modes"][name] = {"n_sets": len(sets), "max_relative_difference": worst, "limit": 1e-9, "W_is_minimal_period_count": n_min, "passed": ok}
    res["passed"] = passed
    return res


# ----------------------------------------------------------------------------------------------
# B7
# ----------------------------------------------------------------------------------------------
def b7_batch(args) -> int:
    name, seeds = args
    rx = receiver_for(name)
    if len(h_n()) != MATRIX["b7"]["candidates_M"]:
        raise RuntimeError("cardinalidade de H_16 do receptor diverge de candidates_M da matriz")
    gamma = detection_threshold(MATRIX["b7"]["design_fpr"], MATRIX["b7"]["candidates_M"])
    freqs = np.array([float(r) * rx.f0 for r in h_n()])
    E = rx._steering(freqs)
    hits = 0
    for sd in seeds:
        x = np.random.default_rng(sd).standard_normal(rx.N)
        P = np.abs(E @ x) ** 2 / rx.N
        hits += int(np.max(P / rx.noise_variance(x)) > gamma)
    return hits


def run_b7(modes: list[str], limit: int | None, workers: int) -> dict:
    b7 = MATRIX["b7"]
    gamma = detection_threshold(b7["design_fpr"], b7["candidates_M"])
    res: dict = {"test": "B7", "gamma": gamma, "design_fpr": b7["design_fpr"], "modes": {}}
    passed = True
    for name in modes:
        out = {}
        for label, (lo, hi) in (("calibration", b7["calibration_noise_seeds"]), ("evaluation", b7["evaluation_noise_seeds"])):
            seeds = list(range(lo, hi + 1))[: limit or None]
            chunks = [seeds[i : i + 250] for i in range(0, len(seeds), 250)]
            with Pool(workers) as pool:
                hits = sum(pool.map(b7_batch, [(name, c) for c in chunks]))
            n = len(seeds)
            upper = float(beta.ppf(0.95, hits + 1, n - hits)) if hits < n else 1.0
            out[label] = {"n": n, "false_positives": hits, "fpr": hits / n, "clopper_pearson_upper_95": upper}
        c_a = out["evaluation"]["clopper_pearson_upper_95"] <= 0.01
        rx = receiver_for(name)
        mids = b7["midpoints_ratio"][: limit or None]
        flagged = 0
        for r in mids:
            s, _ = synth_tone(name, r * rx.f0)
            dec = rx.decode(s, 1)
            flagged += int(not dec["channels"][0]["accepted"])
        c_b = flagged == len(mids)
        out["midpoints"] = {"n": len(mids), "flagged_out_of_tolerance": flagged, "passed": c_b}
        out["criterion_a_cp_upper_le_1pct"] = c_a
        out["passed"] = c_a and c_b
        passed &= out["passed"]
        res["modes"][name] = out
        print(f"  B7 {name}: eval FPR={out['evaluation']['fpr']:.4f} CPup={out['evaluation']['clopper_pearson_upper_95']:.4f} midpoints {flagged}/{len(mids)}", flush=True)
    res["passed"] = passed
    return res


def synth_tone(name: str, f: float) -> tuple[np.ndarray, float]:
    m = mode_cfg(name)
    n = np.arange(int(round(m["fs_hz"] * m["duration_s"])))
    s = np.sin(2 * np.pi * f * n / m["fs_hz"])
    return s / np.max(np.abs(s)), 1.0


# ----------------------------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", default="B1,B2,B3,B4,B5,B7")
    ap.add_argument("--modes", default="hf,lf")
    ap.add_argument("--limit", type=int, default=None, help="limita ensaios por condição (apenas fumaça)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--receiver", choices=sorted(RECEIVERS), default="v1")
    ap.add_argument("--criteria", choices=sorted(CRITERIA), default="0.3.1")
    ap.add_argument("--matrix", type=Path, default=None, help="matriz alternativa (desenvolvimento); exige --smoke")
    ap.add_argument("--out", type=Path, default=None, help="diretório de saída (padrão: results/<receptor>)")
    ap.add_argument("--b3-conditions", default=None,
                    help="subconjunto das condições do B3 (execução dividida em partes; junção por merge_parts.py)")
    a = ap.parse_args()
    if a.limit and not a.smoke:
        ap.error("--limit exige --smoke: execuções reduzidas não são definitivas")
    if a.matrix and not a.smoke:
        ap.error("--matrix exige --smoke: só a matriz oficial dos critérios produz resultado definitivo")
    os.environ["HMAL_RECEIVER"] = a.receiver
    os.environ["HMAL_CRITERIA"] = a.criteria
    os.environ["HMAL_MATRIX"] = str((a.matrix or HERE / CRITERIA[a.criteria]["matrix"]).resolve())
    if (a.receiver, a.criteria, os.environ["HMAL_MATRIX"]) != (RECEIVER_VERSION, CRITERIA_VERSION, str(MATRIX_PATH.resolve())):
        # reexecuta o módulo com as variáveis definidas, para que o processo principal e os workers
        # carreguem exatamente a mesma matriz e a mesma versão de critérios
        os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve())] + sys.argv[1:])
    if not MATRIX:
        ap.error(f"matriz {MATRIX_PATH} não encontrada")
    if a.out:
        global RESULTS
        RESULTS = a.out
    modes = a.modes.split(",")
    tests = a.tests.split(",")
    snrs = MATRIX["snr_int_db_grid"]
    env = env_info(a.smoke)
    b3_only = a.b3_conditions.split(",") if a.b3_conditions else None
    if b3_only and (set(b3_only) - set(B3_CONDITIONS) or len(set(b3_only)) != len(b3_only)):
        ap.error(f"--b3-conditions inválido: use itens distintos de {B3_CONDITIONS}")
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    # env identifica a configuração (igual em todas as partes de uma rodada); a data fica fora dele
    summary = {"env": env, "date_utc": started, "tests": tests, "b3_conditions": b3_only or list(B3_CONDITIONS), "results": {}}
    runners = {
        "B1": lambda: run_b1(),
        "B2": lambda: run_b2(modes, a.limit),
        "B3": lambda: run_b3(modes, a.limit, a.workers, snrs, b3_only),
        "B4": lambda: run_b4(modes, a.limit, a.workers),
        "B5": lambda: run_b5(modes, a.limit),
        "B7": lambda: run_b7(modes, a.limit, a.workers),
    }
    for t in tests:
        print(f"== {t}", flush=True)
        r = runners[t]()
        r["env"] = env
        r["date_utc"] = started
        if t == "B3":
            r["conditions"] = b3_only or list(B3_CONDITIONS)
        save(t, r)
        summary["results"][t] = r["passed"]
        print(f"   {t} passed={r['passed']}", flush=True)
    summary["note"] = "resultado por modo; a regra de TRL só é aplicada por lab/bench/aggregate.py com os dois modos"
    if not env["definitive"]:
        summary["note"] += "; execução NÃO definitiva (fumaça ou matriz fora da designada pelos critérios)"
    save("summary", summary)


if __name__ == "__main__":
    main()
