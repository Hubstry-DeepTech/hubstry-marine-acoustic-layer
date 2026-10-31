"""Testes do pipeline de dados da HMAL Lab (docs/FRONTEND_PLAN.md, seção 5)."""
import copy
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_data", ROOT / "site" / "build_data.py")
bd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bd)
MANIFEST = json.loads((ROOT / "lab" / "bench" / "results" / "MANIFEST.json").read_text(encoding="utf-8"))


def test_manifest_matches_versioned_files():
    bd.verify_manifest(MANIFEST)


def test_sha_mismatch_fails(tmp_path):
    res = tmp_path / "results"
    shutil.copytree(ROOT / "lab" / "bench" / "results", res)
    target = res / "v2-run41131667005" / "hf" / "B3.json"
    target.write_text(target.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(bd.BuildError, match="SHA-256"):
        bd.verify_manifest(MANIFEST, res)


@pytest.mark.parametrize("field", ["execution_type", "experiment_commit", "experiment_commit_basis"])
def test_missing_provenance_fails(field):
    m = copy.deepcopy(MANIFEST)
    del m["results"]["v2-run41131667005"][field]
    with pytest.raises(bd.BuildError, match="proveniência"):
        bd.verify_manifest(m)


def test_actions_run_without_id_fails():
    m = copy.deepcopy(MANIFEST)
    m["results"]["v2-run41131667005"]["execution_run_id"] = None
    with pytest.raises(bd.BuildError, match="identificador"):
        bd.verify_manifest(m)


def test_statuses_come_from_aggregator_without_conversion():
    sets = {n: bd.bench_set(n, s, "0" * 40) for n, s in MANIFEST["results"].items() if n != "e1"}
    assert sets["v1-run41120505952"]["aggregate"]["status"] == "inconsistent"
    assert sets["v2-run41131667005"]["aggregate"]["status"] == "trl3"
    assert all(s["definitive"] for s in sets.values())


def test_unknown_aggregator_rule_fails():
    with pytest.raises(bd.BuildError):
        bd.status_of("TRL 5 de algum jeito")
