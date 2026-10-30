"""Verifica que lab/bench/matrix.json é reconstruído sem divergência por make_matrix.build_matrix()."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_builder():
    spec = importlib.util.spec_from_file_location("make_matrix", ROOT / "lab" / "bench" / "make_matrix.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_matrix_rebuilds_identically():
    mod = _load_builder()
    rebuilt = json.loads(json.dumps(mod.build_matrix(), separators=(",", ":")))
    stored = json.loads((ROOT / "lab" / "bench" / "matrix.json").read_text(encoding="utf-8"))
    assert rebuilt == stored


def test_matrix_invariants():
    m = json.loads((ROOT / "lab" / "bench" / "matrix.json").read_text(encoding="utf-8"))
    assert m["cardinality"] == 159
    assert m["min_gap_ratio"] == "1/240"
    for mode in m["modes"].values():
        assert mode["f_max_hz"] < mode["nyquist_hz"]
        for k in ("k1", "k2"):
            assert all([1, 1] not in t["channels"] for t in mode["b4"][k])
        for k in ("k1", "k2", "k3"):
            assert len(mode["b3"][k]) == 1000
