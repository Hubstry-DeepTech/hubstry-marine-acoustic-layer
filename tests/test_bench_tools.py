"""Testes das ferramentas da bancada v0.4: referência idealizada, matriz nova e disjunção de sementes."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "lab" / "bench"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, BENCH / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_ideal_pe_reference_values():
    pe = _load("ideal_pe").ideal_pe
    assert pe(16) == pytest.approx(2.256e-3, rel=1e-3)
    assert pe(18) == pytest.approx(9.83e-6, rel=1e-3)
    assert pe(20) == pytest.approx(1.087e-9, rel=1e-3)


def _noise_seeds(m):
    seeds = set()
    for mode in m["modes"].values():
        for k in ("k1", "k2", "k3"):
            seeds |= {t["noise_seed"] for t in mode["b3"][k]}
        for cond in mode["b3"]["worst_pairs"]:
            seeds |= {t["noise_seed"] for t in cond}
        for k in ("k1", "k2"):
            seeds |= {t["noise_seed"] for t in mode["b4"][k]}
    for key in ("calibration_noise_seeds", "evaluation_noise_seeds"):
        lo, hi = m["b7"][key]
        seeds |= set(range(lo, hi + 1))
    return seeds


def test_new_version_shifts_every_noise_seed():
    mk = _load("make_matrix")
    old = mk.build_matrix()
    new = mk.build_matrix("0.4.0-test", 12345, 1_000_000_000)
    assert _noise_seeds(old).isdisjoint(_noise_seeds(new))
    assert new["holdout_first_index"] == {"b3": 0, "b4": 0}


@pytest.mark.skipif(not (BENCH / "matrix_v04.json").exists(), reason="matriz v0.4 ainda não gerada")
def test_matrix_v04_rebuilds_identically():
    mk = _load("make_matrix")
    stored = json.loads((BENCH / "matrix_v04.json").read_text(encoding="utf-8"))
    rebuilt = mk.build_matrix(stored["version"], stored["seed"], stored["noise_seed_offset"])
    assert json.loads(json.dumps(rebuilt, separators=(",", ":"))) == stored
    assert _noise_seeds(stored).isdisjoint(_noise_seeds(mk.build_matrix()))
    # sementes de desenvolvimento já usadas: 91.000.000 a 93.000.000 (testes da v3) e deslocamento 500.000.000
    assert all(not (91_000_000 <= s < 93_000_000) and not (500_000_000 <= s < 600_000_000) for s in _noise_seeds(stored))
