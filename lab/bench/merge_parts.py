"""Junta as partes de uma rodada da bancada executada em jobs paralelos (um modo por vez).

Uso: python lab/bench/merge_parts.py <saida> <parte1> <parte2> ...

Cada parte é a saída de run_bench.py com um subconjunto dos ensaios (--tests) e, no B3, um subconjunto das
condições (--b3-conditions). A junção só é feita quando:
- o bloco env (configuração: commit, receptor, critérios, matriz e SHA-256, ambiente, definitive) é idêntico
  em todas as partes e em todos os artefatos de cada parte;
- cada ensaio obrigatório aparece em exatamente uma parte, exceto o B3;
- as condições do B3 aparecem exatamente uma vez cada, com o mesmo modo e a mesma grade de SNR.
O B3 juntado é aprovado só se todas as condições forem aprovadas; os demais artefatos são copiados sem
alteração. Qualquer divergência interrompe a junção. O resultado é lido pelo aggregate.py como uma rodada única.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

TESTS = ["B1", "B2", "B3", "B4", "B5", "B7"]
B3_CONDITIONS = ["k1", "k2", "k3", "worst_pair_0", "worst_pair_1"]


class MergeError(RuntimeError):
    pass


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def merge(parts: list[Path], out: Path) -> dict:
    if not parts:
        raise MergeError("nenhuma parte informada")
    summaries = {p: load(p / "summary.json") for p in parts}
    envs = {json.dumps(s["env"], sort_keys=True) for s in summaries.values()}
    if len(envs) != 1:
        raise MergeError("env diverge entre as partes")
    env = next(iter(summaries.values()))["env"]

    found: dict[str, list[tuple[Path, dict]]] = {t: [] for t in TESTS}
    for p in parts:
        for t in TESTS:
            f = p / f"{t}.json"
            if f.exists():
                r = load(f)
                if r.get("env") != env:
                    raise MergeError(f"{p.name}/{t}.json: env do artefato diverge do resumo")
                if summaries[p]["results"].get(t) != r["passed"]:
                    raise MergeError(f"{p.name}/{t}.json: veredito diverge do resumo da parte")
                found[t].append((p, r))

    for t in TESTS:
        if t != "B3" and len(found[t]) != 1:
            raise MergeError(f"{t}: precisa aparecer em exatamente uma parte (aparece em {len(found[t])})")
    if not found["B3"]:
        raise MergeError("B3 ausente")

    # junção do B3
    base = found["B3"][0][1]
    modes = list(base["modes"])
    if len(modes) != 1:
        raise MergeError("cada parte do B3 deve conter um único modo")
    mode = modes[0]
    merged_conds: dict = {}
    for p, r in found["B3"]:
        if list(r["modes"]) != [mode] or r["snr_int_db"] != base["snr_int_db"]:
            raise MergeError(f"{p.name}/B3.json: modo ou grade de SNR divergente")
        for c, entry in r["modes"][mode].items():
            if c in merged_conds:
                raise MergeError(f"B3: condição {c} repetida")
            if c != "k1" and any(k.startswith("criterion_c") for k in entry):
                raise MergeError(f"B3: critério (c) fora da condição k1 em {c}")
            merged_conds[c] = entry
    if sorted(merged_conds) != sorted(B3_CONDITIONS):
        raise MergeError(f"B3: condições incompletas ou desconhecidas: {sorted(merged_conds)}")
    b3 = {k: v for k, v in base.items() if k not in ("modes", "passed", "conditions", "date_utc")}
    b3["modes"] = {mode: {c: merged_conds[c] for c in B3_CONDITIONS}}
    b3["conditions"] = list(B3_CONDITIONS)
    b3["passed"] = all(e["passed"] for e in merged_conds.values())
    b3["date_utc"] = min(r["date_utc"] for _, r in found["B3"])
    b3["merged_from"] = [{"part": p.name, "conditions": list(r["modes"][mode]), "date_utc": r.get("date_utc")} for p, r in found["B3"]]

    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for t in TESTS:
        r = b3 if t == "B3" else found[t][0][1]
        (out / f"{t}.json").write_text(json.dumps(r, indent=1) + "\n", encoding="utf-8")
        results[t] = r["passed"]
    summary = {
        "env": env,
        "date_utc": min(s["date_utc"] for s in summaries.values()),
        "tests": TESTS,
        "b3_conditions": list(B3_CONDITIONS),
        "results": results,
        "parts": [{"part": p.name, "tests": s.get("tests"), "b3_conditions": s.get("b3_conditions"), "date_utc": s.get("date_utc")}
                  for p, s in summaries.items()],
        "note": "rodada executada em partes paralelas e juntada por lab/bench/merge_parts.py; a regra de TRL só é aplicada por aggregate.py",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    try:
        s = merge([Path(p) for p in sys.argv[2:]], Path(sys.argv[1]))
    except MergeError as e:
        print(f"::error::junção recusada: {e}")
        sys.exit(1)
    print(json.dumps(s["results"]))


if __name__ == "__main__":
    main()
