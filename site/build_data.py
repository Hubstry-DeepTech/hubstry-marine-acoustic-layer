"""Gera os dados da HMAL Lab (site/public/data/*.json) a partir das evidências versionadas no repositório.

Uso: python site/build_data.py [--allow-dirty]

Regras (docs/FRONTEND_PLAN.md, seções 2 e 5):
- só lê arquivos listados em lab/bench/results/MANIFEST.json e confere o SHA-256 de cada um; divergência interrompe o build;
- o status de maturidade de cada conjunto da bancada vem da execução de lab/bench/aggregate.py sobre os artefatos;
  a regra de TRL não é reimplementada aqui nem no navegador;
- cada resultado leva proveniência: caminho, SHA-256, tipo e identificador da execução, experiment_commit e
  publication_commit (commit do checkout atual);
- uma execução marcada como não definitiva nunca é apresentada como definitiva.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "lab" / "bench" / "results"
OUT = ROOT / "site" / "public" / "data"
IMG = ROOT / "site" / "public" / "img"
REPO_URL = "https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer"
TESTS = ["B1", "B2", "B3", "B4", "B5", "B7"]


class BuildError(RuntimeError):
    pass


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


HEX64 = re.compile(r"^[0-9a-f]{64}$")
# Arquivos que o pipeline consome de cada tipo de conjunto: precisam estar cobertos pelo manifesto
REQUIRED_BENCH = [f"{m}/{t}.json" for m in ("hf", "lf") for t in ("summary", "B1", "B2", "B3", "B4", "B5", "B7")]
REQUIRED_E1 = ["E1.json"]


def safe_path(results: Path, rel: str) -> Path:
    """Aceita só caminhos relativos, sem travessia, que resolvam dentro de lab/bench/results."""
    pr = Path(rel)
    if pr.is_absolute() or ".." in pr.parts or "\\" in rel or not rel or rel != pr.as_posix():
        raise BuildError(f"{rel!r}: caminho inválido no manifesto")
    full = (results / pr).resolve()
    if results.resolve() not in full.parents:
        raise BuildError(f"{rel!r}: caminho fora de lab/bench/results")
    return full


def verify_manifest(manifest: dict, results: Path = RESULTS) -> None:
    seen: set[str] = set()
    for name, s in manifest["results"].items():
        if not re.fullmatch(r"[A-Za-z0-9._-]+", name):
            raise BuildError(f"{name!r}: nome de conjunto inválido")
        files = s.get("files") or {}
        prefix = f"{name}/"
        if any(not rel.startswith(prefix) for rel in files):
            raise BuildError(f"{name}: arquivo listado fora do diretório do conjunto")
        required = REQUIRED_E1 if name == "e1" else REQUIRED_BENCH
        if name == "e1":
            e1 = json.loads(safe_path(results, f"{name}/E1.json").read_text(encoding="utf-8")) if f"{name}/E1.json" in files else {}
            required = required + [f"{k}_{d}{ext}" for d in e1.get("days", {}) for k, ext in (("series", ".json"), ("spectrogram", ".png"))]
        missing = [r for r in required if f"{prefix}{r}" not in files]
        if missing:
            raise BuildError(f"{name}: arquivos consumidos pelo pipeline sem cobertura no manifesto: {missing}")
        for rel in files:
            if rel in seen:
                raise BuildError(f"{rel}: caminho duplicado no manifesto")
            seen.add(rel)
        for key in ("execution_type", "experiment_commit", "experiment_commit_basis", "files"):
            if not s.get(key):
                raise BuildError(f"{name}: proveniência incompleta ({key})")
        if s["execution_type"] == "github_actions" and not s.get("execution_run_id"):
            raise BuildError(f"{name}: execução no GitHub Actions sem identificador")
        for rel, digest in s["files"].items():
            if not isinstance(digest, str) or not HEX64.match(digest):
                raise BuildError(f"{rel}: SHA-256 malformado no manifesto")
            p = safe_path(results, rel)
            if not p.exists():
                raise BuildError(f"{rel}: listado no manifesto, mas ausente")
            if sha256(p) != digest:
                raise BuildError(f"{rel}: SHA-256 diverge do manifesto")


def verify_reports(manifest: dict, results: Path = RESULTS) -> None:
    reports = manifest.get("reports")
    if not reports:
        raise BuildError("manifesto sem a seção reports")
    for name, digest in reports.items():
        if not re.fullmatch(r"[A-Za-z0-9._-]+\.md", name):
            raise BuildError(f"{name!r}: nome de relatório inválido")
        if not isinstance(digest, str) or not HEX64.match(digest):
            raise BuildError(f"{name}: SHA-256 malformado no manifesto")
        p = safe_path(results, name)
        if not p.exists():
            raise BuildError(f"{name}: relatório listado no manifesto, mas ausente")
        if sha256(p) != digest:
            raise BuildError(f"{name}: SHA-256 do relatório diverge do manifesto")


def run_aggregator(hf: Path, lf: Path) -> dict:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "aggregate.json"
        subprocess.run([sys.executable, str(ROOT / "lab" / "bench" / "aggregate.py"), str(hf), str(lf), str(out)],
                       check=True, capture_output=True, cwd=ROOT)
        return json.loads(out.read_text(encoding="utf-8"))


def status_of(rule: str) -> str:
    for prefix, code in (("INCONSISTENT_RUNS", "inconsistent"), ("INCOMPLETO", "incomplete"),
                         ("NÃO DEFINITIVO", "not_definitive"), ("TRL 4", "trl4"), ("TRL 3", "trl3")):
        if rule.startswith(prefix):
            return code
    raise BuildError(f"regra do agregador não reconhecida: {rule[:80]}")


def provenance(name: str, s: dict, files: list[str], pub: str) -> dict:
    return {
        "set": name,
        "execution_type": s["execution_type"],
        "execution_run_id": s.get("execution_run_id"),
        "execution_url": f"{REPO_URL}/actions/runs/{s['execution_run_id']}" if s.get("execution_run_id") else None,
        "experiment_commit": s["experiment_commit"],
        "experiment_commit_url": f"{REPO_URL}/commit/{s['experiment_commit']}",
        "experiment_commit_basis": s["experiment_commit_basis"],
        "publication_commit": pub,
        "files": [{"path": f"lab/bench/results/{f}", "sha256": s["files"][f],
                   "url": f"{REPO_URL}/blob/{pub}/lab/bench/results/{f}"} for f in files],
        "note": s.get("note"),
    }


def bench_set(name: str, s: dict, pub: str) -> dict:
    d = RESULTS / name
    agg = run_aggregator(d / "hf", d / "lf")
    status = status_of(agg["trl_rule"])
    summaries = {m: json.loads((d / m / "summary.json").read_text(encoding="utf-8")) for m in ("hf", "lf")}
    envs = {m: summaries[m]["env"] for m in summaries}
    definitive = all(e.get("definitive") is True for e in envs.values())
    if status in ("trl3", "trl4") and not definitive:
        raise BuildError(f"{name}: conclusão de TRL sobre execução não definitiva")
    b3 = {m: json.loads((d / m / "B3.json").read_text(encoding="utf-8")) for m in ("hf", "lf")}
    b4 = {m: json.loads((d / m / "B4.json").read_text(encoding="utf-8")) for m in ("hf", "lf")}
    b7 = {m: json.loads((d / m / "B7.json").read_text(encoding="utf-8")) for m in ("hf", "lf")}
    snr = b3["hf"]["snr_int_db"]
    recovery = {m: {c: v["recovery_rate"] for c, v in b3[m]["modes"][m].items()} for m in b3}
    rms = {m: b3[m]["modes"][m]["k1"]["rms_over_acrb"] for m in b3}
    b4min = {m: {k: min(v["recovery_rate"]) for k, v in b4[m]["modes"][m].items()} for m in b4}
    b7s = {m: {"fpr": b7[m]["modes"][m]["evaluation"]["fpr"],
               "cp_upper_95": b7[m]["modes"][m]["evaluation"]["clopper_pearson_upper_95"],
               "midpoints_rejected": b7[m]["modes"][m]["midpoints"]["flagged_out_of_tolerance"],
               "midpoints_total": b7[m]["modes"][m]["midpoints"]["n"]} for m in b7}
    files = [f for f in s["files"] if f.endswith(("summary.json", "B3.json", "B4.json", "B7.json", "aggregate.json"))]
    return {
        "id": name,
        "receiver": s.get("receiver"),
        "criteria_version": envs["hf"].get("criteria_version"),
        "matrix_version": envs["hf"].get("matrix_version"),
        "date_utc": envs["hf"].get("date_utc") or summaries["hf"].get("date_utc"),
        "b3c_min_snr_db": envs["hf"].get("b3c_min_snr_db", 16),
        "definitive": definitive,
        "aggregate": {"status": status, "rule": agg["trl_rule"], "by_test_and_mode": agg["by_test_and_mode"]},
        "per_mode_assessment": {m: summaries[m].get("trl_rule") for m in summaries},
        "per_mode_results": {m: summaries[m]["results"] for m in summaries},
        "snr_int_db": snr,
        "b3_recovery_rate": recovery,
        "b3_k1_rms_over_acrb": rms,
        "b4_min_recovery": b4min,
        "b7": b7s,
        "provenance": provenance(name, s, files, pub),
    }


def e1_set(s: dict, pub: str) -> dict:
    d = RESULTS / "e1"
    e1 = json.loads((d / "E1.json").read_text(encoding="utf-8"))
    days = []
    IMG.mkdir(parents=True, exist_ok=True)
    for day, v in sorted(e1["days"].items()):
        series = json.loads((d / f"series_{day}.json").read_text(encoding="utf-8"))
        png = d / f"spectrogram_{day}.png"
        webp = IMG / f"spectrogram_{day}.webp"
        try:
            from PIL import Image
            Image.open(png).save(webp, "WEBP", quality=82, method=6)
            img = f"img/{webp.name}"
        except ImportError:  # pragma: no cover - Pillow ausente: usa o PNG original
            (IMG / png.name).write_bytes(png.read_bytes())
            img = f"img/{png.name}"
        days.append({
            "day": day, "computed_ci": v["daily_mean_ci"], "reference_ci": v["reference_ci"],
            "relative_difference": v["relative_difference"], "valid_minutes": v["valid_minutes"],
            "minutes": v["minutes"], "passed": v["passed"], "wav_sha256": v["sha256"], "wav_key": v["key"],
            "series": {"minute": series["minute_utc"], "ci": series["ci"], "valid": series["valid"]},
            "spectrogram": img,
            "spectrogram_original": f"{REPO_URL}/blob/{pub}/lab/bench/results/e1/{png.name}",
        })
    return {
        "passed": e1["passed"], "tolerance_relative": e1["tolerance_relative"], "date_utc": e1["date_utc"],
        "source": e1["source"], "license": e1["license"], "env": e1["env"], "days": days,
        "series_note": series["note"],
        "provenance": provenance("e1", s, list(s["files"]), pub),
    }


def doc_status(path: str, pattern: str) -> str:
    text = (ROOT / path).read_text(encoding="utf-8-sig")
    m = re.search(pattern, text, re.M)
    if not m:
        raise BuildError(f"{path}: linha de estado não encontrada")
    return m.group(1).strip()


def build(allow_dirty: bool = False) -> dict:
    pub = git("rev-parse", "HEAD")
    if not allow_dirty and git("status", "--porcelain", "--", "lab", "docs", "LICENSE"):
        raise BuildError("há alterações não commitadas nas evidências; o publication_commit não as representaria")
    manifest = json.loads((RESULTS / "MANIFEST.json").read_text(encoding="utf-8"))
    verify_manifest(manifest)
    verify_reports(manifest)
    bench = [bench_set(n, s, pub) for n, s in manifest["results"].items() if n != "e1"]
    data = {
        "publication_commit": pub,
        "publication_commit_url": f"{REPO_URL}/commit/{pub}",
        "built_from_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "repo_url": REPO_URL,
        "documents": {
            "bench_criteria": doc_status("lab/BENCH_CRITERIA.md", r"^\*\*Versão:\*\*\s*(.+)$"),
            "preregistration_version": doc_status("lab/PREREGISTRATION.md", r"^\*\*Versão:\*\*\s*`?([^`\n]+)`?"),
            "preregistration_status": doc_status("lab/PREREGISTRATION.md", r"^\*\*Status:\*\*\s*(.+)$"),
        },
        "bench": bench,
        "e1": e1_set(manifest["results"]["e1"], pub),
        "reports": {k: {"sha256": v, "url": f"{REPO_URL}/blob/{pub}/lab/bench/results/{k}"} for k, v in manifest["reports"].items()},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "site.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-dirty", action="store_true", help="só para desenvolvimento local")
    a = ap.parse_args()
    try:
        data = build(a.allow_dirty)
    except BuildError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"site.json: {len(data['bench'])} conjuntos da bancada, E1 com {len(data['e1']['days'])} dias, "
          f"publicação {data['publication_commit'][:7]}")
    for b in data["bench"]:
        print(f"  {b['id']}: {b['aggregate']['status']}")


if __name__ == "__main__":
    main()
