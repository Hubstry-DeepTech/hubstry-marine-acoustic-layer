"""Bloco 1 — detecção, incerteza e estimador independente da fundamental (plano SIM-MCA-001).

Uso: python -m lab.sim_mca001.block1 --reps 6 --out lab/sim_mca001/results/block1_pilot.json

Fluxo: as réplicas da partição "cal" ajustam o modelo de incerteza σ_f; as da partição
"ver" verificam a cobertura desse modelo (parecer da Luna: calibração e verificação em
sementes distintas). Rótulo: EXPLORATORY/FEASIBILITY. Nenhum dado real é lido.
"""
import argparse
import hashlib
import itertools
import json
import platform
import sys
import time
from multiprocessing import Pool

import numpy as np
import scipy
from scipy import signal as sps

from . import detection as D
from . import fundamental as F0
from . import generator as G
from . import seeds as S

BAND = (5.0, 900.0)
DUR = 10.0
GRID = dict(profile=["decrescente", "h3_dominante", "ausente_identificavel", "ausente_ambigua"],
            f0=[12.0, 18.0], slope=[0.0, -0.05], snr=[-5.0, 0.0, 5.0, 10.0, 20.0], alpha=[0.0, 1.0])
WINDOWS = [0.5, 1.0, 2.0]
YIN_THRESHOLDS = [0.1, 0.2, 0.3]
DET_THRESHOLDS_DB = [6.0, 10.0, 15.0]
F0_PREFILTER = (5.0, 250.0)
TOL_LOG2 = 0.05  # acerto da fundamental: |log2(f̂/f)| < 0.05 (~3,5%)


def scenario_name(c):
    return "p={profile}|f0={f0}|s={slope}|snr={snr}|a={alpha}".format(**c)


def classify_f0(est, f0_true, profile):
    """Classes de saída do estimador. Para 'ausente_ambigua', nenhuma classe é erro:
    registra-se se o estimador devolveu o período do sinal (2f0), f0 ou outra coisa."""
    if not np.isfinite(est):
        return "indisponivel"
    r = np.log2(est / f0_true)
    if profile == "ausente_ambigua":
        if abs(r - 1) < TOL_LOG2:
            return "periodo_sinal_2f0"
        if abs(r) < TOL_LOG2:
            return "f0_fisica"
        return "outro"
    if abs(r) < TOL_LOG2:
        return "acerto"
    for m, lab in ((2, "oitava"), (3, "fator_3"), (4, "fator_4")):
        if abs(r - np.log2(m)) < TOL_LOG2:
            return f"erro_{lab}_acima"
        if abs(r + np.log2(m)) < TOL_LOG2:
            return f"erro_{lab}_abaixo"
    return "erro_outro"


def run_one(args):
    cell, partition, rep = args
    name = scenario_name(cell)
    rng = S.rng("B1", name, partition, rep)
    x, truth = G.harmonic(rng, duration=DUR, f0_start=cell["f0"], slope=cell["slope"],
                          profile=cell["profile"])
    xn, _ = G.add_noise(rng, x, cell["snr"], BAND, alpha=cell["alpha"])
    out = dict(cell=cell, partition=partition, rep=rep, det={}, f0={})
    half_spacing = 0.5 * float(truth.f0.min())
    for w in WINDOWS:
        p = D.StftParams(win_s=w, hop_s=0.5, threshold_db=min(DET_THRESHOLDS_DB))
        t, frames, df = D.detect(xn, p)
        out["det"][w] = {}
        for thr_db in DET_THRESHOLDS_DB:
            fr_thr = [[pk for pk in fr if pk[2] >= 10 ** (thr_db / 10)] for fr in frames]
            # pareamento largo (meio espaçamento harmônico): mede o erro sem truncá-lo
            rec, nfalse, ntrue = D.match_truth(t, fr_thr, truth, tol_hz=half_spacing)
            rows = []
            for j, k, ft, fe, snr in rec:
                idx = min(int(round(t[j] * G.FS)), truth.t.size - 1)
                fdot = np.gradient(truth.freqs[k])[idx] * G.FS
                rows.append((truth.orders[k], ft, fe, snr, fdot, truth.f0[idx], j))
            n_prec = sum(1 for r_ in rows if abs(r_[2] - r_[1]) <= 1.0 / w)
            out["det"][w][thr_db] = dict(n_true=ntrue, n_match=len(rec), n_prec=n_prec, n_false=nfalse,
                                         n_frames=len(frames), rows=rows if thr_db == DET_THRESHOLDS_DB[1] else [])
    xf = F0.prefilter(xn, F0_PREFILTER)
    tf, fr = F0.frames(xf, 0.5, 0.5)
    f0true = np.array([truth.f0[min(int(round(tc * G.FS)), truth.t.size - 1)] for tc in tf])
    res = {}
    for mode in ("first", "best"):
        for thr in YIN_THRESHOLDS:
            est = [F0.yin(f, threshold=thr, mode=mode)[0] for f in fr]
            res[f"yin_{mode}_{thr}"] = [classify_f0(e, ft, cell["profile"]) for e, ft in zip(est, f0true)]
    cep = [F0.cepstrum(f, min_prominence=0.0) for f in fr]
    res["cep_raw"] = [(float(e), float(pr), classify_f0(e, ft, cell["profile"])) for (e, pr), ft in zip(cep, f0true)]
    out["f0"] = res
    return out


def fit_sigma_model(rows, win_s):
    """Ajusta var(f_est − f_true) = a/snr + b·(fdot·T)² por mínimos quadrados não negativos
    em caixas de SNR local e de taxa de modulação, com variância robusta (MAD)."""
    from scipy.optimize import nnls
    r = np.array([(fe - ft, snr, fd) for _, ft, fe, snr, fd, _, _ in rows])
    if r.shape[0] < 50:
        return None
    err, snr, fd = r[:, 0], r[:, 1], np.abs(r[:, 2]) * win_s
    qs = np.quantile(snr, np.linspace(0, 1, 9))
    qf = np.quantile(fd, [0, 0.5, 0.8, 1.0])
    X, yv = [], []
    for i in range(8):
        for j in range(3):
            m = (snr >= qs[i]) & (snr <= qs[i + 1]) & (fd >= qf[j]) & (fd <= qf[j + 1])
            if m.sum() < 20:
                continue
            e = err[m]
            v = (1.4826 * np.median(np.abs(e - np.median(e)))) ** 2
            X.append([np.mean(1 / snr[m]), np.mean(fd[m] ** 2)])
            yv.append(v)
    if len(yv) < 3:
        return None
    X, yv = np.array(X), np.array(yv)
    # ajuste relativo (cada caixa pesa pelo erro relativo), para que as caixas de variância
    # grande não dominem e o termo de SNR não seja zerado
    coef, _ = nnls(X / yv[:, None], np.ones_like(yv))
    return dict(a=float(coef[0]), b=float(coef[1]))


def sigma_of(model, snr, fdot, win_s):
    return np.sqrt(model["a"] / snr + model["b"] * (np.abs(fdot) * win_s) ** 2)


def f_max_check():
    """Ganho da cadeia de decimação simulada (16 kHz → 2 kHz) medido com ruído branco."""
    rng = S.rng("B1", "fmax", "cal", 0)
    x = rng.normal(size=int(60 * 16000))
    y = G.decimation_chain(x, 8)
    f1, p_in = sps.welch(x, fs=16000, nperseg=8192)
    f2, p_out = sps.welch(y, fs=2000, nperseg=1024)
    gain_db = 10 * np.log10(p_out / np.interp(f2, f1, p_in))
    ref = np.median(gain_db[(f2 > 20) & (f2 < 500)])
    flat = np.abs(gain_db - ref) <= 0.5
    ok = f2[flat & (f2 > 20)]
    first_bad = f2[(~flat) & (f2 > 20)]
    fmax = float(first_bad.min()) if first_bad.size else float(ok.max())
    return dict(criterio="primeira frequência acima de 20 Hz com ganho fora de ±0,5 dB da mediana 20–500 Hz",
                f_max_hz=fmax, ganho_ref_db=float(ref),
                nota="filtro FIR do scipy, não o filtro do MBARI; valida o procedimento, não o valor real")


def identifiability_order(model, f0, slope, win_s):
    """Maior ordem n com ln((n+1)/n) > 2·σ_ln f(n), pelo modelo de incerteza ajustado, com SNR
    local alta (só o termo de modulação). σ_ln f(n) = σ_f(n)/(n·f0), fdot(n) = n·f0·ln2·|slope|."""
    for n in range(1, 2000):
        fdot = n * f0 * np.log(2) * abs(slope)
        sig = np.sqrt(model["a"] / 1e6 + model["b"] * (fdot * win_s) ** 2) / (n * f0)
        if np.log((n + 1) / n) <= 2 * sig:
            return n - 1
    return ">=2000"


def summarize(results, sigma_models):
    summ = {"deteccao": {}, "incerteza": {}, "fundamental": {}, "identificabilidade": {}}
    mid = DET_THRESHOLDS_DB[1]
    for w in WINDOWS:
        dw = {}
        for thr_db in DET_THRESHOLDS_DB:
            by_snr = {}
            for snr in GRID["snr"]:
                rs = [r["det"][w][thr_db] for r in results if r["cell"]["snr"] == snr]
                nt = sum(d["n_true"] for d in rs)
                nfr = sum(d["n_frames"] for d in rs)
                by_snr[str(snr)] = dict(taxa_deteccao_precisa=sum(d["n_prec"] for d in rs) / nt,
                                        falsos_por_quadro=sum(d["n_false"] for d in rs) / nfr)
            dw[str(thr_db)] = by_snr
        rows = [row for r in results for row in r["det"][w][mid]["rows"]]
        n = np.array([row[0] for row in rows])
        prec = np.array([abs(row[2] - row[1]) <= 1.0 / w for row in rows])
        dw["precisao_por_ordem_limiar_10dB"] = {f"{lo}-{hi}": float(prec[(n >= lo) & (n <= hi)].mean())
                                                for lo, hi in [(1, 5), (6, 10), (11, 20), (21, 40), (41, 80)]
                                                if ((n >= lo) & (n <= hi)).any()}
        summ["deteccao"][str(w)] = dw
        model = sigma_models.get(w)
        ver = [row for r in results if r["partition"] == "ver" for row in r["det"][w][mid]["rows"]]
        if model and ver:
            z = np.array([(fe - ft) / sigma_of(model, snr, fd, w) for _, ft, fe, snr, fd, _, _ in ver])
            snrs = np.array([row[3] for row in ver])
            bins = np.quantile(snrs, [0, 0.25, 0.5, 0.75, 1.0])
            cov = {f"snr_local_q{i + 1}": float(np.mean(np.abs(z[(snrs >= bins[i]) & (snrs <= bins[i + 1])]) <= 1.96))
                   for i in range(4)}
            summ["incerteza"][str(w)] = dict(modelo=model, cobertura_95_verificacao=float(np.mean(np.abs(z) <= 1.96)),
                                             cobertura_por_quartil_snr=cov, n=int(z.size),
                                             nota="pareamento até meio espaçamento harmônico; picos de ruído próximos contam como estimativa")
            summ["identificabilidade"][str(w)] = {
                f"f0={f0}|slope={sl}": identifiability_order(model, f0, sl, w)
                for f0 in GRID["f0"] for sl in GRID["slope"]}
    # f0 separado por partição: a escolha do estimador e do limiar usa só "cal";
    # o desempenho reportado para a escolha vem só de "ver"
    for part in S.PARTITIONS:
        summ["fundamental"][part] = {}
    for prof, part in itertools.product(GRID["profile"], S.PARTITIONS):
        ps = {}
        for snr in GRID["snr"]:
            rs = [r for r in results if r["cell"]["profile"] == prof and r["cell"]["snr"] == snr
                  and r["partition"] == part]
            entry = {}
            for key in [f"yin_{m}_{t}" for m in ("first", "best") for t in YIN_THRESHOLDS]:
                labels = [lab for r in rs for lab in r["f0"][key]]
                entry[key] = {lab: labels.count(lab) / len(labels) for lab in sorted(set(labels))}
            for pmin in (2.0, 4.0, 6.0):
                labels = [lab if pr >= pmin else "indisponivel" for r in rs for (_, pr, lab) in r["f0"]["cep_raw"]]
                entry[f"cepstro_{pmin}"] = {lab: labels.count(lab) / len(labels) for lab in sorted(set(labels))}
            ps[str(snr)] = entry
        summ["fundamental"][part][prof] = ps
    return summ


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=6, help="réplicas por célula e por partição")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    keys = list(GRID)
    cells = [dict(zip(keys, v)) for v in itertools.product(*GRID.values())]
    jobs = [(c, part, rep) for c in cells for part in S.PARTITIONS for rep in range(a.reps)]
    with Pool(a.workers) as pool:
        results = pool.map(run_one, jobs, chunksize=4)
    sigma_models = {}
    for w in WINDOWS:
        rows = [row for r in results if r["partition"] == "cal" for row in r["det"][w][DET_THRESHOLDS_DB[1]]["rows"]]
        sigma_models[w] = fit_sigma_model(rows, w)
    report = dict(
        bloco="B1", plano="SIM-MCA-001 v0.2", rotulo="EXPLORATORY/FEASIBILITY", tipo="piloto",
        grade=GRID, janelas_stft_s=WINDOWS, yin_limiares=YIN_THRESHOLDS, tol_log2_f0=TOL_LOG2,
        limiares_deteccao_db=DET_THRESHOLDS_DB, prefiltro_f0_hz=F0_PREFILTER,
        replicas_por_celula_e_particao=a.reps, n_sinais=len(jobs),
        versoes=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        f_max=f_max_check(), resultados=summarize(results, sigma_models),
        tempo_s=round(time.time() - t0, 1))
    body = json.dumps(report, ensure_ascii=False, indent=1, sort_keys=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(body)
    print(a.out, hashlib.sha256(body.encode()).hexdigest(), f"{report['tempo_s']} s")


if __name__ == "__main__":
    sys.exit(main())
