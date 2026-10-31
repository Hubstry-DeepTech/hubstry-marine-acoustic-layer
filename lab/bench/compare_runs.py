"""Compara duas rodadas da bancada (diretórios com hf/ e lf/) após normalizar só os metadados de execução.

Uso: python lab/bench/compare_runs.py <rodada_a> <rodada_b>

Removidos antes da comparação: env.commit, date_utc (no artefato e em env, formato anterior), conditions e
merged_from (metadados da junção de partes). Todo o resto, inclusive o restante de env e os erros por ensaio,
precisa ser idêntico. Sai com código 1 se houver qualquer diferença.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

TESTS = ["B1", "B2", "B3", "B4", "B5", "B7"]
DROP = {"date_utc", "conditions", "merged_from"}


def normalize(d: dict) -> dict:
    out = {k: v for k, v in d.items() if k not in DROP}
    if "env" in out:
        out["env"] = {k: v for k, v in out["env"].items() if k not in ("commit", "date_utc")}
    return out


def compare(a: Path, b: Path) -> list[str]:
    diffs = []
    for m in ("hf", "lf"):
        for t in TESTS:
            pa, pb = a / m / f"{t}.json", b / m / f"{t}.json"
            if not (pa.exists() and pb.exists()):
                diffs.append(f"{m}/{t}: ausente em uma das rodadas")
                continue
            if normalize(json.loads(pa.read_text(encoding="utf-8"))) != normalize(json.loads(pb.read_text(encoding="utf-8"))):
                diffs.append(f"{m}/{t}: resultados diferentes")
    return diffs


def main() -> None:
    diffs = compare(Path(sys.argv[1]), Path(sys.argv[2]))
    print("idênticos após normalização (12 de 12)" if not diffs else "\n".join(diffs))
    sys.exit(1 if diffs else 0)


if __name__ == "__main__":
    main()
