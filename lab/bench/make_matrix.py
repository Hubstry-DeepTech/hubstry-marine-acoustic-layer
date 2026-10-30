"""Gera lab/bench/matrix.json: matriz determinística de ensaios da bancada digital HMAL.

Uso: python lab/bench/make_matrix.py
A saída é versionada; qualquer alteração na matriz exige nova versão de lab/BENCH_CRITERIA.md.
"""
from __future__ import annotations

import json
import random
from fractions import Fraction
from math import gcd
from pathlib import Path

N = 16
SEED = 20261030

MODES = {
    "dolphin": {"f0_hz": 1732.0, "fs_hz": 96000, "duration_s": 0.5},
    "whale": {"f0_hz": 25.0, "fs_hz": 2000, "duration_s": 20.0},
}


def h_n(n: int) -> list[Fraction]:
    return sorted({Fraction(a, b) for a in range(1, n + 1) for b in range(1, n + 1) if gcd(a, b) == 1})


def as_pair(r: Fraction) -> list[int]:
    return [r.numerator, r.denominator]


def pick_sets(rng: random.Random, data: list[Fraction], k: int, min_sep_ratio: float, n_sets: int) -> list:
    sets: list = []
    while len(sets) < n_sets:
        cand = sorted(rng.sample(data, k))
        if all(float(b - a) >= min_sep_ratio for a, b in zip(cand, cand[1:])):
            sets.append([as_pair(r) for r in cand])
    return sets


def main() -> None:
    rng = random.Random(SEED)
    hn = h_n(N)
    pilot = Fraction(1, 1)
    data = [r for r in hn if r != pilot]
    gaps = [(a, b, b - a) for a, b in zip(hn, hn[1:])]
    min_gap = min(g for _, _, g in gaps)
    worst_pairs = [[as_pair(a), as_pair(b)] for a, b, g in gaps if g == min_gap and pilot not in (a, b)]
    midpoints = [[float((a + b) / 2)] for a, b, _ in gaps]

    modes = {}
    for name, m in MODES.items():
        f_max = float(max(hn)) * m["f0_hz"]
        assert f_max < m["fs_hz"] / 2, f"{name}: f_max {f_max} Hz >= Nyquist"
        sep10 = 10.0 / m["duration_s"] / m["f0_hz"]
        modes[name] = {
            **m,
            "f_max_hz": f_max,
            "nyquist_hz": m["fs_hz"] / 2,
            "b2_single": [as_pair(r) for r in data],
            "b2_multi": {
                "min_separation_ratio": sep10,
                "k2": pick_sets(rng, data, 2, sep10, 50),
                "k3": pick_sets(rng, data, 3, sep10, 50),
            },
        }

    matrix = {
        "version": "0.2.0",
        "seed": SEED,
        "N": N,
        "cardinality": len(hn),
        "min_gap_ratio": str(min_gap),
        "pilot": as_pair(pilot),
        "data_channels": len(data),
        "worst_case_pairs": worst_pairs,
        "modes": modes,
        "b3": {
            "k_values": [1, 2, 3],
            "snr_int_db": list(range(-10, 31, 2)),
            "trials_per_condition": 1000,
            "trial_seed_base": 100_000,
            "set_rule": "por ensaio, K canais sorteados de data_channels com random.Random(trial_seed_base + indice); K=2 inclui ainda todos os worst_case_pairs",
        },
        "b4": {
            "epsilon": [-1e-3, -5e-4, 0.0, 5e-4, 1e-3],
            "k_values": [1, 2],
            "snr_int_db": 20,
            "trials_per_condition": 1000,
            "trial_seed_base": 200_000,
        },
        "b7": {
            "target_fpr": 0.01,
            "calibration_seeds": [0, 9_999],
            "evaluation_seeds": [1_000_000, 1_009_999],
            "midpoints_ratio": midpoints,
        },
    }
    out = Path(__file__).with_name("matrix.json")
    out.write_text(json.dumps(matrix, indent=1) + "\n", encoding="utf-8")
    print(f"{out}: |H_{N}|={len(hn)}, min_gap={min_gap}, worst_pairs={len(worst_pairs)}")


if __name__ == "__main__":
    main()
