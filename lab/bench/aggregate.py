"""Agrega os resultados dos modos hf e lf e aplica a regra global de maturidade (BENCH_CRITERIA v0.3.1, Seção 8).

Uso: python lab/bench/aggregate.py <dir_hf> <dir_lf> [saida.json]
Cada diretório contém os JSON de um job (B1.json, B2.json, ...). A regra de TRL só é aplicada aqui,
com os dois modos: B1-B5 e B7 precisam passar em hf E em lf.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = ["B1", "B2", "B3", "B4", "B5", "B7"]


def load(d: Path, t: str) -> dict | None:
    p = d / f"{t}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> None:
    dirs = {"hf": Path(sys.argv[1]), "lf": Path(sys.argv[2])}
    out_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("aggregate.json")
    table: dict = {}
    for t in REQUIRED:
        table[t] = {}
        for mode, d in dirs.items():
            r = load(d, t)
            table[t][mode] = None if r is None else bool(r["passed"])
    envs = {m: (load(d, "summary") or {}).get("env", {}) for m, d in dirs.items()}
    # vínculo modo <-> diretório: os JSON de cada diretório precisam conter o modo correspondente
    wrong_mode = [f"{t}/{m}" for t in REQUIRED if t != "B1" for m, d in dirs.items()
                  if (r := load(d, t)) is not None and m not in r.get("modes", {})]
    definitive = all(e.get("definitive") for e in envs.values())
    complete = all(v is not None for t in REQUIRED for v in table[t].values())
    all_pass = complete and all(table[t][m] for t in REQUIRED for m in dirs)
    keys = ("commit", "receiver", "criteria_version", "matrix_version")
    mismatch = [k for k in keys if len({envs[m].get(k) for m in dirs}) != 1 or None in {envs[m].get(k) for m in dirs}]
    if wrong_mode:
        rule = "INCONSISTENT_RUNS: diretório não contém o modo indicado (" + ", ".join(wrong_mode) + "); nenhuma conclusão de TRL"
    elif mismatch:
        rule = "INCONSISTENT_RUNS: metadados divergentes ou ausentes entre os modos (" + ", ".join(mismatch) + "); nenhuma conclusão de TRL"
    elif not complete:
        rule = "INCOMPLETO: falta resultado de algum ensaio ou modo; nenhuma conclusão de TRL"
    elif not definitive:
        rule = "NÃO DEFINITIVO: execução de fumaça; nenhuma conclusão de TRL"
    elif all_pass:
        rule = "TRL 4 (autoavaliação) do subsistema computacional: B1-B5 e B7 aprovados nos modos hf e lf"
    else:
        failed = [f"{t}/{m}" for t in REQUIRED for m in dirs if not table[t][m]]
        rule = "TRL 3: ensaios obrigatórios reprovados: " + ", ".join(failed)
    result = {"by_test_and_mode": table, "metadata_mismatch": mismatch, "wrong_mode": wrong_mode, "complete": complete, "definitive": definitive,
              "receiver": {m: e.get("receiver") for m, e in envs.items()},
              "commit": {m: e.get("commit") for m, e in envs.items()}, "trl_rule": rule}
    out_path.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
