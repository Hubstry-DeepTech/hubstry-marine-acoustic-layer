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
    assert sets["v04-run41231673988"]["aggregate"]["status"] == "trl4"
    assert sets["v04-run41231673988"]["b3c_min_snr_db"] == 20
    assert all(s["definitive"] for s in sets.values())


def test_unknown_aggregator_rule_fails():
    with pytest.raises(bd.BuildError):
        bd.status_of("TRL 5 de algum jeito")


@pytest.mark.parametrize("bad", ["e1/../../../README.md", "/etc/passwd", "e1/./E1.json", "e1\\\\E1.json"])
def test_path_traversal_rejected(bad):
    m = copy.deepcopy(MANIFEST)
    m["results"]["e1"]["files"][bad] = "0" * 64
    with pytest.raises(bd.BuildError):
        bd.verify_manifest(m)


def test_malformed_hash_rejected():
    m = copy.deepcopy(MANIFEST)
    k = next(iter(m["results"]["e1"]["files"]))
    m["results"]["e1"]["files"][k] = "ABC"
    with pytest.raises(bd.BuildError, match="malformado"):
        bd.verify_manifest(m)


@pytest.mark.parametrize("name,rel", [("v2-run41131667005", "v2-run41131667005/lf/B4.json"),
                                      ("v1-run41120505952", "v1-run41120505952/hf/summary.json"),
                                      ("e1", "e1/series_2016-11-11.json")])
def test_required_files_must_be_covered(name, rel):
    m = copy.deepcopy(MANIFEST)
    del m["results"][name]["files"][rel]
    with pytest.raises(bd.BuildError, match="cobertura"):
        bd.verify_manifest(m)


def test_file_outside_set_directory_rejected():
    m = copy.deepcopy(MANIFEST)
    m["results"]["e1"]["files"]["v2-run41131667005/hf/B3.json"] = MANIFEST["results"]["v2-run41131667005"]["files"]["v2-run41131667005/hf/B3.json"]
    with pytest.raises(bd.BuildError, match="fora do diretório"):
        bd.verify_manifest(m)


def test_reports_hashes_are_verified(tmp_path):
    bd.verify_reports(MANIFEST)
    res = tmp_path / "results"
    shutil.copytree(ROOT / "lab" / "bench" / "results", res)
    rep = res / "REPORT_v1_v2.md"
    rep.write_text(rep.read_text(encoding="utf-8") + "\nalteração", encoding="utf-8")
    with pytest.raises(bd.BuildError, match="relatório"):
        bd.verify_reports(MANIFEST, res)


@pytest.mark.parametrize("name,digest", [("../README.md", "0" * 64), ("REPORT_v1_v2.md", "xyz"), ("AUSENTE.md", "0" * 64)])
def test_bad_report_entries_rejected(name, digest):
    m = copy.deepcopy(MANIFEST)
    m["reports"][name] = digest
    with pytest.raises(bd.BuildError):
        bd.verify_reports(m)
