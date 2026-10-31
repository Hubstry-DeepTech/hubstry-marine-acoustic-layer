"""Gera lab/bench/results/MANIFEST.json: vínculo entre cada conjunto de resultados publicado, a execução que o
produziu e o SHA-256 de cada arquivo. Uso: python lab/bench/make_manifest.py

O commit do experimento (experiment_commit) é lido dos próprios resultados. O commit de publicação é o commit
do ramo main que contém este manifesto; ele não pode ser gravado no próprio arquivo sem circularidade.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"

RUNS = {
    "v1-run41120505952": {"execution": "github_actions", "run_id": 41120505952, "receiver": "v1",
                           "note": "execução anterior à gravação do campo receiver; o agregador conjunto devolve INCONSISTENT_RUNS"},
    "v2-run41121711705": {"execution": "github_actions", "run_id": 41121711705, "receiver": "v2"},
    "v2-run41131667005": {"execution": "github_actions", "run_id": 41131667005, "receiver": "v2",
                           "note": "inclui dados por ensaio, hold-out e diagnóstico de falhas"},
    "e1": {"execution": "manual_vm", "run_id": None, "receiver": None,
           "note": "execução manual numa VM da GCP (Google Cloud Platform); ver env e hashes dos WAV em E1.json"},
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def experiment_commit(d: Path) -> str | None:
    for p in sorted(d.rglob("*.json")):
        j = json.loads(p.read_text(encoding="utf-8"))
        c = (j.get("env") or {}).get("commit") or j.get("commit")
        if isinstance(c, str):
            return c
    return None


def main() -> None:
    sets = {}
    for name, meta in RUNS.items():
        d = RESULTS / name
        files = {str(p.relative_to(RESULTS)): sha256(p) for p in sorted(d.rglob("*")) if p.is_file()}
        sets[name] = {**meta, "experiment_commit": experiment_commit(d), "files": files}
    out = {"manifest_version": 1, "results": sets, "reports": {p.name: sha256(p) for p in sorted(RESULTS.glob("*.md"))}}
    (RESULTS / "MANIFEST.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(sets)} conjuntos, {sum(len(s['files']) for s in sets.values())} arquivos")


if __name__ == "__main__":
    main()
