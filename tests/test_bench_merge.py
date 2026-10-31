"""Testes da junção das partes paralelas da bancada (lab/bench/merge_parts.py)."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("merge_parts", ROOT / "lab" / "bench" / "merge_parts.py")
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)
ENV = {"criteria_version": "0.4.0", "commit": "c" * 40, "receiver": "v3", "matrix_sha256": "a" * 64, "definitive": True}
CONDS = ["k1", "k2", "k3", "worst_pair_0", "worst_pair_1"]


def _part(root: Path, name: str, tests: dict, env=ENV, date="2026-11-01T00:00:00+00:00"):
    d = root / name
    d.mkdir(parents=True)
    for t, payload in tests.items():
        (d / f"{t}.json").write_text(json.dumps({"test": t, "env": env, "date_utc": date, **payload}))
    (d / "summary.json").write_text(json.dumps({"env": env, "date_utc": date, "results": {t: p["passed"] for t, p in tests.items()}}))
    return d


def _b3(conds, passed=True):
    return {"passed": passed, "snr_int_db": [16, 20], "modes": {"hf": {c: {"passed": passed} for c in conds}}}


def _parts(root, b3_split=None, env_overrides=None):
    base = {t: {"passed": True, "modes": {"hf": {}}} for t in ("B1", "B2", "B4", "B5", "B7")}
    parts = [_part(root, "base", base)]
    for i, conds in enumerate(b3_split or [[c] for c in CONDS]):
        env = dict(ENV, **(env_overrides or {})) if i == 0 and env_overrides else ENV
        parts.append(_part(root, f"b3-{i}", {"B3": _b3(conds)}, env=env))
    return parts


def test_merge_ok(tmp_path):
    s = mp.merge(_parts(tmp_path / "p"), tmp_path / "out")
    assert s["results"] == {t: True for t in mp.TESTS}
    b3 = json.loads((tmp_path / "out" / "B3.json").read_text())
    assert list(b3["modes"]["hf"]) == CONDS and len(b3["merged_from"]) == 5


def test_env_divergence_refused(tmp_path):
    with pytest.raises(mp.MergeError, match="env"):
        mp.merge(_parts(tmp_path / "p", env_overrides={"commit": "d" * 40}), tmp_path / "out")


def test_missing_condition_refused(tmp_path):
    with pytest.raises(mp.MergeError, match="incompletas"):
        mp.merge(_parts(tmp_path / "p", b3_split=[["k1"], ["k2"], ["k3"], ["worst_pair_0"]]), tmp_path / "out")


def test_duplicated_condition_refused(tmp_path):
    with pytest.raises(mp.MergeError, match="repetida"):
        mp.merge(_parts(tmp_path / "p", b3_split=[["k1", "k2"], ["k2", "k3"], ["worst_pair_0", "worst_pair_1"]]), tmp_path / "out")


def test_duplicated_test_refused(tmp_path):
    parts = _parts(tmp_path / "p")
    parts.append(_part(tmp_path / "p", "extra", {"B4": {"passed": True, "modes": {"hf": {}}}}))
    with pytest.raises(mp.MergeError, match="B4"):
        mp.merge(parts, tmp_path / "out")


def test_one_failed_condition_fails_b3(tmp_path):
    root = tmp_path / "p"
    base = {t: {"passed": True, "modes": {"hf": {}}} for t in ("B1", "B2", "B4", "B5", "B7")}
    parts = [_part(root, "base", base), _part(root, "b3a", {"B3": _b3(["k1", "k2"])}),
             _part(root, "b3b", {"B3": _b3(["k3", "worst_pair_0", "worst_pair_1"], passed=False)})]
    s = mp.merge(parts, tmp_path / "out")
    assert s["results"]["B3"] is False


def test_artifact_verdict_must_match_part_summary(tmp_path):
    parts = _parts(tmp_path / "p")
    s = json.loads((parts[0] / "summary.json").read_text())
    s["results"]["B4"] = False
    (parts[0] / "summary.json").write_text(json.dumps(s))
    with pytest.raises(mp.MergeError, match="veredito"):
        mp.merge(parts, tmp_path / "out")
