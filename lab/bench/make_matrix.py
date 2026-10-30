"""Gera lab/bench/matrix.json: matriz determinística e completa de ensaios da bancada digital HMAL.

Uso: python lab/bench/make_matrix.py
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


def build_matrix() -> dict:
    hn = h_n(N)
    pilot = Fraction(1, 1)
    data = [r for r in hn if r != pilot]
    gaps = [(a, b, b - a) for a, b in zip(hn, hn[1:])]
    min_gap = min(g for _, _, g in gaps)
    worst_pairs = [[a, b] for a, b, g in gaps if g == min_gap and pilot not in (a, b)]

    modes: dict = {}
    for m_idx, (name, m) in enumerate(MODES.items()):
        rng = random.Random(SEED + 1000 * m_idx)
        f_max = float(max(hn)) * m["f0_hz"]
        assert f_max < m["fs_hz"] / 2, f"{name}: f_max {f_max} Hz >= Nyquist"
        sep10 = 10.0 / m["duration_s"] / m["f0_hz"]
        noise_base = 10_000_000 * (m_idx + 1)

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
    return {
        "version": VERSION,
        "seed": SEED,
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
            "calibration_noise_seeds": [0, 9_999],
            "evaluation_noise_seeds": [1_000_000, 1_009_999],
            "modes": ["hf", "lf"],
            "midpoints_ratio": midpoints,
        },
    }


def main() -> None:
    matrix = build_matrix()
    MATRIX_PATH.write_text(json.dumps(matrix, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{MATRIX_PATH}: |H_{N}|={matrix['cardinality']}, min_gap={matrix['min_gap_ratio']}")


if __name__ == "__main__":
    main()
