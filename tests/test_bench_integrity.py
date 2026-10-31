"""Testes de integridade da cadeia de execução e agregação da bancada (parecer da Luna, 31/10/2026)."""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "lab" / "bench"
sys.path.insert(0, str(BENCH))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, BENCH / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


agg = _load("aggregate")
resolve_run = _load("resolve_run")
TESTS = ["B1", "B2", "B3", "B4", "B5", "B7"]
SHA = "a" * 64


def _env(**kw):
    env = {"criteria_version": "0.4.0", "matrix_version": "0.4.0", "matrix_file": "matrix_v04.json", "matrix_sha256": SHA,
           "b3c_min_snr_db": 20, "matrix_seed": 123, "noise_seed_offset": 1_500_000_000, "commit": "c" * 40,
           "receiver": "v3", "definitive": True}
    env.update(kw)
    return env


def _write_run(root: Path, env_by_mode: dict, passed=True, tweak=None):
    dirs = {}
    for m, env in env_by_mode.items():
        d = root / m
        d.mkdir(parents=True)
        res = {}
        for t in TESTS:
            payload = {"test": t, "passed": passed, "env": env, "modes": {m: {}}}
            if tweak:
                tweak(m, t, payload)
            (d / f"{t}.json").write_text(json.dumps(payload))
            res[t] = passed
        (d / "summary.json").write_text(json.dumps({"env": env, "results": res}))
        dirs[m] = d
    return dirs


def _freeze(root: Path, sha=SHA, receiver="v3"):
    p = root / "lab" / "bench" / "FREEZE_v0.4.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"matrix_sha256": sha, "receiver": receiver, "criteria_version": "0.4.0"}))
    return root


def test_consistent_v04_gives_trl4(tmp_path):
    dirs = _write_run(tmp_path / "r", {"hf": _env(), "lf": _env()})
    out = agg.aggregate(dirs, root=_freeze(tmp_path / "repo"))
    assert out["trl_rule"].startswith("TRL 4"), out["trl_rule"]


@pytest.mark.parametrize("field", ["matrix_sha256", "matrix_file", "b3c_min_snr_db", "matrix_seed"])
def test_v04_missing_field_in_both_modes_is_inconsistent(tmp_path, field):
    env = _env()
    del env[field]
    out = agg.aggregate(_write_run(tmp_path / "r", {"hf": env, "lf": copy.deepcopy(env)}), root=_freeze(tmp_path / "repo"))
    assert out["trl_rule"].startswith("INCONSISTENT_RUNS")


def test_v04_wrong_cut_is_inconsistent(tmp_path):
    out = agg.aggregate(_write_run(tmp_path / "r", {"hf": _env(b3c_min_snr_db=16), "lf": _env(b3c_min_snr_db=16)}),
                        root=_freeze(tmp_path / "repo"))
    assert out["trl_rule"].startswith("INCONSISTENT_RUNS")


def test_v04_matrix_hash_must_match_freeze(tmp_path):
    out = agg.aggregate(_write_run(tmp_path / "r", {"hf": _env(), "lf": _env()}), root=_freeze(tmp_path / "repo", sha="b" * 64))
    assert out["trl_rule"].startswith("INCONSISTENT_RUNS")


def test_v04_without_freeze_is_inconsistent(tmp_path):
    out = agg.aggregate(_write_run(tmp_path / "r", {"hf": _env(), "lf": _env()}), root=tmp_path / "empty")
    assert out["trl_rule"].startswith("INCONSISTENT_RUNS")


def test_artifact_env_must_match_summary(tmp_path):
    def tweak(m, t, payload):
        if m == "lf" and t == "B3":
            payload["env"] = _env(commit="d" * 40)
    out = agg.aggregate(_write_run(tmp_path / "r", {"hf": _env(), "lf": _env()}, tweak=tweak), root=_freeze(tmp_path / "repo"))
    assert out["trl_rule"].startswith("INCONSISTENT_RUNS") and "B3/lf" in out["trl_rule"]


def test_artifact_verdict_must_match_summary(tmp_path):
    def tweak(m, t, payload):
        if m == "hf" and t == "B4":
            payload["passed"] = False
    out = agg.aggregate(_write_run(tmp_path / "r", {"hf": _env(), "lf": _env()}, tweak=tweak), root=_freeze(tmp_path / "repo"))
    assert out["trl_rule"].startswith("INCONSISTENT_RUNS") and "B4/hf" in out["trl_rule"]


def test_non_definitive_gives_no_trl(tmp_path):
    out = agg.aggregate(_write_run(tmp_path / "r", {"hf": _env(definitive=False), "lf": _env(definitive=False)}),
                        root=_freeze(tmp_path / "repo"))
    assert out["trl_rule"].startswith("NÃO DEFINITIVO")


def test_manual_dispatch_requires_seed_and_is_never_definitive():
    with pytest.raises(resolve_run.RunError):
        resolve_run.resolve("workflow_dispatch", {"dev_seed": "", "dev_noise_offset": "500000000"})
    with pytest.raises(resolve_run.RunError):
        resolve_run.resolve("workflow_dispatch", {"dev_seed": "7", "dev_noise_offset": "1000000000"})
    res = resolve_run.resolve("workflow_dispatch", {"dev_seed": "7", "dev_noise_offset": "500000000", "receiver": "v3", "criteria": "0.4.0"})
    assert res["kind"] == "dev" and "--smoke" in res["args"] and "--matrix" in res["args"]


def test_confirmatory_only_from_push_with_freeze(tmp_path):
    with pytest.raises(resolve_run.RunError):
        resolve_run.resolve("push", {}, freeze_path=tmp_path / "missing.json")
    fz = tmp_path / "FREEZE_v0.4.json"
    fz.write_text(json.dumps({"receiver": "v3", "criteria_version": "0.4.0", "matrix_file": "matrix_v04.json",
                              "matrix_sha256": SHA, "matrix_seed": 1, "noise_seed_offset": 1_500_000_000}))
    res = resolve_run.resolve("push", {}, freeze_path=fz)
    assert res["kind"] == "confirmatory" and "--smoke" not in res["args"]
    with pytest.raises(resolve_run.RunError):
        resolve_run.resolve("schedule", {})


@pytest.mark.parametrize("args", [
    ["--version", "0.4.0", "--seed", "999", "--noise-offset", "999999999"],
    ["--version", "0.4.0", "--seed", "20261031", "--noise-offset", "1500000000"],
])
def test_confirmatory_matrix_rules(tmp_path, args):
    r = subprocess.run([sys.executable, str(BENCH / "make_matrix.py"), *args, "--out", str(tmp_path / "m.json")],
                       capture_output=True, text=True)
    assert r.returncode != 0 and not (tmp_path / "m.json").exists()


def test_outcome_separates_misidentification_from_rejection():
    import run_bench
    truth = [[3, 2]]
    ok = {"channels": [{"f_est": 1.0, "ratio": [3, 2], "accepted": True}]}
    wrong = {"channels": [{"f_est": 1.0, "ratio": [5, 3], "accepted": True}]}
    rejected = {"channels": [{"f_est": 1.0, "ratio": [3, 2], "accepted": False}]}
    rejected_wrong = {"channels": [{"f_est": 1.0, "ratio": [5, 3], "accepted": False}]}
    assert run_bench.outcome(ok, truth) == "ok"
    assert run_bench.outcome(wrong, truth) == "misidentified"
    assert run_bench.outcome(rejected, truth) == "rejected"
    assert run_bench.outcome(rejected_wrong, truth) == "rejected"


def test_freeze_with_other_criteria_version_is_rejected(tmp_path):
    fz = tmp_path / "FREEZE_v0.4.json"
    fz.write_text(json.dumps({"receiver": "v3", "criteria_version": "0.3.1", "matrix_file": "matrix_v04.json",
                              "matrix_sha256": SHA, "matrix_seed": 1, "noise_seed_offset": 1_500_000_000}))
    with pytest.raises(resolve_run.RunError, match="0.4.0"):
        resolve_run.resolve("push", {}, freeze_path=fz)
    fz.write_text(json.dumps({"receiver": "v3", "criteria_version": "0.4.0"}))
    with pytest.raises(resolve_run.RunError, match="incompleto"):
        resolve_run.resolve("push", {}, freeze_path=fz)


def test_aggregator_checks_freeze_criteria_version(tmp_path):
    root = tmp_path / "repo"
    p = root / "lab" / "bench" / "FREEZE_v0.4.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"matrix_sha256": SHA, "receiver": "v3", "criteria_version": "0.3.1"}))
    out = agg.aggregate(_write_run(tmp_path / "r", {"hf": _env(), "lf": _env()}), root=root)
    assert out["trl_rule"].startswith("INCONSISTENT_RUNS") and "congelamento" in out["trl_rule"]


def test_summary_must_list_every_verdict(tmp_path):
    dirs = _write_run(tmp_path / "r", {"hf": _env(), "lf": _env()})
    s = json.loads((dirs["hf"] / "summary.json").read_text())
    del s["results"]["B4"]
    (dirs["hf"] / "summary.json").write_text(json.dumps(s))
    out = agg.aggregate(dirs, root=_freeze(tmp_path / "repo"))
    assert out["trl_rule"].startswith("INCONSISTENT_RUNS") and "B4/hf" in out["trl_rule"]


def test_coherent_dev_run_without_freeze_is_not_definitive(tmp_path):
    env = _env(definitive=False, matrix_file="matrix_dev.json")
    out = agg.aggregate(_write_run(tmp_path / "r", {"hf": env, "lf": copy.deepcopy(env)}), root=tmp_path / "empty")
    assert out["trl_rule"].startswith("NÃO DEFINITIVO"), out["trl_rule"]


def test_definitive_run_without_freeze_is_inconsistent(tmp_path):
    out = agg.aggregate(_write_run(tmp_path / "r", {"hf": _env(), "lf": _env()}), root=tmp_path / "empty")
    assert out["trl_rule"].startswith("INCONSISTENT_RUNS")
