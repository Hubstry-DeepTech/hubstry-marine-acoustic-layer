"""Gera lab/bench/results/MANIFEST.json: vínculo entre cada conjunto de resultados publicado, a execução que o
produziu e o SHA-256 de cada arquivo. Uso: python lab/bench/make_manifest.py

Semântica dos campos (três fatos distintos: o que foi executado, o que foi publicado, o que o agregador concluiu):
- execution_type: "github_actions" ou "manual_vm";
- execution_run_id: identificador da execução no GitHub Actions; null quando a execução foi manual;
- experiment_commit: commit do código executado, declarado aqui de forma explícita. O script confere que todos
  os JSON do conjunto que registram um commit trazem exatamente esse valor; qualquer divergência interrompe a
  geração. Não se presume que o primeiro arquivo encontrado represente o conjunto;
- experiment_commit_basis: o que sustenta o experiment_commit (gravado pelo runner em cada artefato, ou commit
  do script versionado associado a uma execução manual);
- publication_commit: NÃO consta do manifesto, porque o arquivo não pode conter o hash do próprio commit que o
  publica. O pipeline de publicação o obtém do checkout do main no momento do build;
- a conclusão do agregador fica no aggregate.json de cada conjunto e não é repetida aqui.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"

RUNS = {
    "v1-run41120505952": {
        "execution_type": "github_actions", "execution_run_id": 41120505952, "receiver": "v1",
        "experiment_commit": "4ba2c059dc092a998abaea7be71bc38797fb1f99",
        "experiment_commit_basis": "gravado pelo runner no bloco env de cada artefato",
        "note": "execução anterior à gravação do campo receiver; o agregador conjunto devolve INCONSISTENT_RUNS; "
                "a avaliação de TRL 3 sob v0.3.1 decorre dos vereditos por modo (REPORT_v1_v2.md), não do agregador"},
    "v2-run41121711705": {
        "execution_type": "github_actions", "execution_run_id": 41121711705, "receiver": "v2",
        "experiment_commit": "972beb694d76ffee188ccf9f7cc3b1c2cf6891f0",
        "experiment_commit_basis": "gravado pelo runner no bloco env de cada artefato"},
    "v2-run41131667005": {
        "execution_type": "github_actions", "execution_run_id": 41131667005, "receiver": "v2",
        "experiment_commit": "a691855383779763714f072bf8d3bbe062e48064",
        "experiment_commit_basis": "gravado pelo runner no bloco env de cada artefato",
        "note": "inclui dados por ensaio, hold-out e diagnóstico de falhas"},
    "v04-run41231673988": {
        "execution_type": "github_actions", "execution_run_id": 41231673988, "receiver": "v3",
        "experiment_commit": "a2361a5b0bacd807b596c8068c0a4d0b378f9e32",
        "experiment_commit_basis": "commit de congelamento da v0.4, gravado pelo runner no bloco env de cada artefato e conferido por freeze.verify_freeze()",
        "note": "rodada confirmatória dos critérios 0.4.0, executada em seis partes paralelas por modo e juntada por merge_parts.py"},
    "e1": {
        "execution_type": "manual_vm", "execution_run_id": None, "receiver": None,
        "experiment_commit": "e02008f1877a0caf92638fa1816bafbaada3f946",
        "experiment_commit_basis": "commit do script versionado lab/bench/e1_mbari.py associado ao experimento, "
                                   "registrado pelo próprio script em E1.json; a execução foi manual numa VM da GCP "
                                   "(Google Cloud Platform) e não há workflow associado",
        "note": "ambiente, data e SHA-256 dos arquivos WAV de entrada estão em E1.json"},
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def recorded_commits(d: Path) -> dict[str, str]:
    out = {}
    for p in sorted(d.rglob("*.json")):
        j = json.loads(p.read_text(encoding="utf-8"))
        c = (j.get("env") or {}).get("commit") or j.get("commit")
        if isinstance(c, str):
            out[str(p.relative_to(RESULTS))] = c
    return out


def main() -> None:
    sets = {}
    for name, meta in RUNS.items():
        d = RESULTS / name
        rec = recorded_commits(d)
        wrong = {k: v for k, v in rec.items() if v != meta["experiment_commit"]}
        if not rec or wrong:
            raise SystemExit(f"{name}: commit declarado não confere com os artefatos: {wrong or 'nenhum commit gravado'}")
        files = {str(p.relative_to(RESULTS)): sha256(p) for p in sorted(d.rglob("*")) if p.is_file()}
        sets[name] = {**meta, "files_recording_commit": len(rec), "files": files}
    out = {"manifest_version": 3,
           "results": sets, "reports": {p.name: sha256(p) for p in sorted(RESULTS.glob("*.md"))}}
    (RESULTS / "MANIFEST.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(sets)} conjuntos, {sum(len(s['files']) for s in sets.values())} arquivos; commits conferidos")


if __name__ == "__main__":
    main()
