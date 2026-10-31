"""Testes do congelamento verificável da v0.4 (lab/bench/freeze.py), um por tipo de divergência."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import freeze_repo  # noqa: E402

fz_mod = freeze_repo.freeze


def test_valid_freeze_passes(tmp_path):
    freeze_repo.make_repo(tmp_path)
    assert fz_mod.verify_freeze(tmp_path, env=freeze_repo.run_env()) == []


@pytest.mark.parametrize("rel", ["lab/bench/receiver.py", "lab/bench/aggregate.py", "lab/bench/run_bench.py",
                                 "lab/bench/merge_parts.py", "lab/bench/make_matrix.py", "lab/bench/constraints.txt",
                                 "src/hmal/core/harmonic_protocol.py", ".github/workflows/bench.yml", "lab/BENCH_CRITERIA_v0.4.md",
                                 "lab/bench/freeze.py", "lab/bench/resolve_run.py"])
def test_altered_code_or_document_detected(tmp_path, rel):
    freeze_repo.make_repo(tmp_path)
    p = tmp_path / rel
    p.write_text(p.read_text(encoding="utf-8") + "\n# alteração\n", encoding="utf-8")
    assert any(rel in msg for msg in fz_mod.verify_freeze(tmp_path))


def test_altered_matrix_detected(tmp_path):
    freeze_repo.make_repo(tmp_path)
    p = tmp_path / fz_mod.MATRIX_REL
    m = json.loads(p.read_text(encoding="utf-8"))
    m["modes"]["hf"]["b3"]["k1"][0]["noise_seed"] += 1
    p.write_text(json.dumps(m, separators=(",", ":")) + "\n", encoding="utf-8")
    assert any("SHA-256 da matriz" in msg for msg in fz_mod.verify_freeze(tmp_path))


@pytest.mark.parametrize("key,value", [("matrix_seed", 1), ("noise_seed_offset", 2_000_000_000)])
def test_freeze_metadata_must_match_matrix(tmp_path, key, value):
    freeze_repo.make_repo(tmp_path, **{key: value})
    assert fz_mod.verify_freeze(tmp_path)


@pytest.mark.parametrize("key,value", [("receiver", "v2"), ("criteria_version", "0.3.1"), ("matrix_seed", 1),
                                       ("noise_seed_offset", 2_000_000_000), ("matrix_sha256", "b" * 64),
                                       ("numpy", "9.9.9"), ("scipy", "9.9.9"), ("python", "3.12.0"),
                                       ("libc", "glibc2.39"), ("libc", None), ("matrix_version", "0.3.0")])
def test_run_env_must_match_freeze(tmp_path, key, value):
    freeze_repo.make_repo(tmp_path)
    assert any(key in msg for msg in fz_mod.verify_freeze(tmp_path, env=freeze_repo.run_env(**{key: value})))


def test_missing_protected_file_detected(tmp_path):
    freeze_repo.make_repo(tmp_path)
    (tmp_path / "lab/bench/merge_parts.py").unlink()
    assert any("ausente" in msg for msg in fz_mod.verify_freeze(tmp_path))


def test_aggregator_refuses_trl_when_code_changed(tmp_path):
    sys.path.insert(0, str(ROOT / "lab" / "bench"))
    import aggregate
    repo = tmp_path / "repo"
    freeze_repo.make_repo(repo)
    dirs = {}
    for m in ("hf", "lf"):
        d = tmp_path / "r" / m
        d.mkdir(parents=True)
        env = freeze_repo.run_env()
        for t in ("B1", "B2", "B3", "B4", "B5", "B7"):
            (d / f"{t}.json").write_text(json.dumps({"passed": True, "env": env, "modes": {m: {}}}))
        (d / "summary.json").write_text(json.dumps({"env": env, "results": {t: True for t in ("B1", "B2", "B3", "B4", "B5", "B7")}}))
        dirs[m] = d
    assert aggregate.aggregate(dirs, root=repo)["trl_rule"].startswith("TRL 4")
    p = repo / "lab/bench/receiver.py"
    p.write_text(p.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    out = aggregate.aggregate(dirs, root=repo)
    assert out["trl_rule"].startswith("INCONSISTENT_RUNS") and "receiver.py" in out["trl_rule"]


@pytest.mark.parametrize("environment", [
    {"python": "3.11.17", "numpy": "2.4.6", "scipy": "1.17.1"},
    {"python": "3.11.17", "numpy": "2.4.6", "scipy": "1.17.1", "libc": ""},
    {"python": "3.11.17", "numpy": "2.4.6", "scipy": "1.17.1", "libc": "glibc2.43", "extra": "x"},
])
def test_freeze_environment_must_have_exactly_four_fields(tmp_path, environment):
    freeze_repo.make_repo(tmp_path, environment=environment)
    assert any("ambiente do congelamento" in msg for msg in fz_mod.verify_freeze(tmp_path))


def test_runtime_libc_divergence_detected(tmp_path, monkeypatch):
    freeze_repo.make_repo(tmp_path)
    monkeypatch.setattr(fz_mod, "current_environment", lambda: dict(freeze_repo.ENVIRONMENT, libc="glibc2.39"))
    assert any("libc" in msg for msg in fz_mod.verify_freeze(tmp_path, check_runtime=True))
    monkeypatch.setattr(fz_mod, "current_environment", lambda: dict(freeze_repo.ENVIRONMENT))
    assert fz_mod.verify_freeze(tmp_path, check_runtime=True) == []


def test_matrix_version_must_match(tmp_path):
    freeze_repo.make_repo(tmp_path)
    p = tmp_path / fz_mod.MATRIX_REL
    m = json.loads(p.read_text(encoding="utf-8"))
    m["version"] = "0.4.1"
    p.write_text(json.dumps(m, separators=(",", ":")) + "\n", encoding="utf-8")
    assert any("versão da matriz" in msg for msg in fz_mod.verify_freeze(tmp_path))
