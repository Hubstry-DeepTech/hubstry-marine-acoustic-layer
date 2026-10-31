"""Gera lab/bench/matrix.json: matriz determinística e completa de ensaios da bancada digital HMAL.

Uso:
  python lab/bench/make_matrix.py                    # matriz v0.3.0 (critérios v0.3.1), lab/bench/matrix.json
  python lab/bench/make_matrix.py --version 0.4.0 --seed S --noise-offset O --out lab/bench/matrix_v04.json
A saída é versionada. O teste tests/test_bench_matrix.py verifica que o arquivo
versionado é idêntico ao que build_matrix() reconstrói.
Qualquer alteração na matriz exige nova versão de lab/BENCH_CRITERIA.md.
"""
from __future__ import annotations

import json
import random
from fractions import Fraction
from math import gcd
from pathlib import Path

VERSION = "0.3.0"
N = 16
SEED = 20261030
TRIALS = 1000

MODES = {
    "hf": {"label": "sintético de alta frequência", "f0_hz": 1732.0, "fs_hz": 96000, "duration_s": 0.5},
    "lf": {"label": "sintético de baixa frequência", "f0_hz": 25.0, "fs_hz": 2000, "duration_s": 20.0},
}

MATRIX_PATH = Path(__file__).with_name("matrix.json")
# Sementes e faixas de ruído já usadas em desenvolvimento ou em matrizes anteriores. Uma matriz confirmatória
# não pode reutilizá-las (lab/BENCH_CRITERIA_v0.4-draft.md, Seção 3).
USED_MATRIX_SEEDS = {SEED, 20261031, 777001}
CONFIRMATORY_MIN_NOISE_OFFSET = 1_000_000_000


def h_n(n: int) -> list[Fraction]:
    return sorted({Fraction(a, b) for a in range(1, n + 1) for b in range(1, n + 1) if gcd(a, b) == 1})


def as_pair(r: Fraction) -> list[int]:
    return [r.numerator, r.denominator]


def pick_set(rng: random.Random, pool: list[Fraction], k: int, min_sep_ratio: float = 0.0) -> list[Fraction]:
    while True:
        cand = sorted(rng.sample(pool, k))
        if all(float(b - a) >= min_sep_ratio for a, b in zip(cand, cand[1:])):
            return cand


def trial(rng: random.Random, channels: list[Fraction], noise_seed: int) -> dict:
    return {
        "channels": [as_pair(r) for r in channels],
        "polarities": [rng.randint(0, 1) for _ in channels],
        "noise_seed": noise_seed,
    }


def build_matrix(version: str = VERSION, seed: int = SEED, noise_offset: int = 0) -> dict:
    """Com os valores padrão, reproduz byte a byte a matriz v0.3.0. Para outras versões, `seed` define os
    sorteios de canais e polaridades e `noise_offset` desloca todas as sementes de ruído (B3, B4 e B7)."""
    hn = h_n(N)
    pilot = Fraction(1, 1)
    data = [r for r in hn if r != pilot]
    gaps = [(a, b, b - a) for a, b in zip(hn, hn[1:])]
    min_gap = min(g for _, _, g in gaps)
    worst_pairs = [[a, b] for a, b, g in gaps if g == min_gap and pilot not in (a, b)]

    modes: dict = {}
    for m_idx, (name, m) in enumerate(MODES.items()):
        rng = random.Random(seed + 1000 * m_idx)
        f_max = float(max(hn)) * m["f0_hz"]
        assert f_max < m["fs_hz"] / 2, f"{name}: f_max {f_max} Hz >= Nyquist"
        sep10 = 10.0 / m["duration_s"] / m["f0_hz"]
        noise_base = noise_offset + 10_000_000 * (m_idx + 1)

        b2 = {
            "single": [trial(rng, [r], 0) for r in data],
            "k2": [trial(rng, pick_set(rng, data, 2, sep10), 0) for _ in range(50)],
            "k3": [trial(rng, pick_set(rng, data, 3, sep10), 0) for _ in range(50)],
            "min_separation_ratio": sep10,
            "note": "sem ruído; noise_seed não utilizado",
        }

        b3: dict = {}
        for k in (1, 2, 3):
            b3[f"k{k}"] = [trial(rng, pick_set(rng, data, k), noise_base + 100_000 * k + i) for i in range(TRIALS)]
        b3["worst_pairs"] = [
            [trial(rng, pair, noise_base + 500_000 + 10_000 * p + i) for i in range(TRIALS)]
            for p, pair in enumerate(worst_pairs)
        ]

        b4: dict = {}
        for k in (1, 2):
            b4[f"k{k}"] = [
                trial(rng, pick_set(rng, data, k), noise_base + 700_000 + 100_000 * k + i) for i in range(TRIALS)
            ]

        modes[name] = {
            **m,
            "f_max_hz": f_max,
            "nyquist_hz": m["fs_hz"] / 2,
            "b2": b2,
            "b3": b3,
            "b4": b4,
        }

    midpoints = [float((a + b) / 2) for a, b, _ in gaps]
    out = {
        "version": version,
        "seed": seed,
        "N": N,
        "cardinality": len(hn),
        "min_gap_ratio": str(min_gap),
        "pilot": as_pair(pilot),
        "data_channels": len(data),
        "worst_case_pairs": [[as_pair(a), as_pair(b)] for a, b in worst_pairs],
        "snr_int_db_grid": list(range(-10, 31, 2)),
        "b4_epsilon": [-1e-3, -5e-4, 0.0, 5e-4, 1e-3],
        "b4_snr_int_db": 20,
        "rules": {
            "noise": "ruído branco gaussiano gerado por numpy.random.default_rng(noise_seed); o mesmo noise_seed é usado em todos os pontos da grade de SNR (números aleatórios comuns)",
            "polarities": "0 -> fase 0; 1 -> fase pi (generate_waveform)",
            "b3_b4_modes": "B3 e B4 são executados nos dois modos (hf e lf)",
            "worst_pairs": "cada par de pior caso tem sua própria condição de 1000 ensaios em B3, separada dos sorteios aleatórios de K=2",
            "b4_pilot": "o piloto 1/1 é acrescentado aos canais listados; os canais de dados nunca incluem 1/1",
        },
        "modes": modes,
        "b7": {
            "design_fpr": 0.005,
            "candidates_M": len(hn),
            "calibration_noise_seeds": [noise_offset + 0, noise_offset + 9_999],
            "evaluation_noise_seeds": [noise_offset + 1_000_000, noise_offset + 1_009_999],
            "modes": ["hf", "lf"],
            "midpoints_ratio": midpoints,
        },
    }
    if version != VERSION:  # campos novos só fora da v0.3.0, para não alterar a matriz congelada
        out["noise_seed_offset"] = noise_offset
        out["holdout_first_index"] = {"b3": 0, "b4": 0}
        out["rules"]["holdout"] = "nenhum ensaio desta matriz foi usado no desenvolvimento de receptores; todos são hold-out"
    return out


def main() -> None:
    import argparse
    import hashlib

    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default=VERSION)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--noise-offset", type=int, default=0)
    ap.add_argument("--out", type=Path, default=MATRIX_PATH)
    a = ap.parse_args()
    if a.version != VERSION and (a.seed == SEED or a.noise_offset == 0):
        ap.error("uma versão nova exige semente e deslocamento de ruído novos")
    if not a.version.startswith("dev"):
        if a.seed in USED_MATRIX_SEEDS:
            ap.error(f"semente {a.seed} já usada; uma matriz confirmatória exige semente nova")
        if a.noise_offset < CONFIRMATORY_MIN_NOISE_OFFSET:
            ap.error(f"uma matriz confirmatória exige --noise-offset >= {CONFIRMATORY_MIN_NOISE_OFFSET}")
    matrix = build_matrix(a.version, a.seed, a.noise_offset)
    text = json.dumps(matrix, separators=(",", ":")) + "\n"
    a.out.write_text(text, encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print(f"{a.out}: versão {a.version}, semente {a.seed}, deslocamento {a.noise_offset}, |H_{N}|={matrix['cardinality']}, sha256 {sha}")


if __name__ == "__main__":
    main()
