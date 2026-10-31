"""Agrega os resultados dos modos hf e lf e aplica a regra global de maturidade (Seção 8 dos critérios, v0.3.1 e v0.4).

Uso: python lab/bench/aggregate.py <dir_hf> <dir_lf> [saida.json]
Cada diretório contém os JSON de um job (B1.json, B2.json, ..., summary.json). A regra de TRL só é aplicada aqui,
com os dois modos: B1-B5 e B7 precisam passar em hf E em lf.

O agregador é a autoridade que transforma resultados em declaração de maturidade. Ele só emite conclusão quando:
- cada artefato B*.json traz o mesmo bloco env do summary.json do seu diretório, e o veredito de cada artefato
  coincide com o registrado no resumo;
- os metadados coincidem entre os modos;
- os campos exigidos pela versão de critérios existem e têm os valores esperados (arquivo da matriz, corte do
  B3(c)); na v0.4, o SHA-256 da matriz e o receptor coincidem com lab/bench/FREEZE_v0.4.json;
- todos os artefatos são definitivos.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = ["B1", "B2", "B3", "B4", "B5", "B7"]
ROOT = Path(__file__).resolve().parents[2]

# Campos de metadados que precisam existir e coincidir entre os modos, por versão de critérios
EXPECTED = {
    "0.3.1": {"required": ("commit", "receiver", "criteria_version", "matrix_version"),
              "values": {"matrix_file": "matrix.json", "b3c_min_snr_db": 16}},
    "0.4.0": {"required": ("commit", "receiver", "criteria_version", "matrix_version", "matrix_file", "matrix_sha256",
                           "b3c_min_snr_db", "matrix_seed", "noise_seed_offset"),
              "values": {"matrix_file": "matrix_v04.json", "b3c_min_snr_db": 20},
              "freeze": "lab/bench/FREEZE_v0.4.json"},
}


def load(d: Path, t: str) -> dict | None:
    p = d / f"{t}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def aggregate(dirs: dict[str, Path], root: Path = ROOT) -> dict:
    summaries = {m: load(d, "summary") or {} for m, d in dirs.items()}
    envs = {m: s.get("env", {}) for m, s in summaries.items()}
    results = {m: {t: load(d, t) for t in REQUIRED} for m, d in dirs.items()}
    table = {t: {m: None if results[m][t] is None else bool(results[m][t]["passed"]) for m in dirs} for t in REQUIRED}
    problems: list[str] = []

    # 1. vínculo modo <-> diretório
    for m in dirs:
        for t in REQUIRED:
            r = results[m][t]
            if r is not None and t != "B1" and m not in r.get("modes", {}):
                problems.append(f"{t}/{m}: diretório não contém o modo indicado")

    # 2. vínculo artefato <-> resumo do mesmo diretório
    for m in dirs:
        for t in REQUIRED:
            r = results[m][t]
            if r is None:
                continue
            if r.get("env") != envs[m]:
                problems.append(f"{t}/{m}: env do artefato difere do summary.json")
            sv = summaries[m].get("results", {}).get(t)
            if not isinstance(sv, bool):
                problems.append(f"{t}/{m}: veredito ausente ou não booleano no summary.json")
            elif sv != r["passed"]:
                problems.append(f"{t}/{m}: veredito do artefato difere do summary.json")

    # 3. metadados entre modos, conforme a versão de critérios
    versions = {e.get("criteria_version") for e in envs.values()}
    version = versions.pop() if len(versions) == 1 else None
    spec = EXPECTED.get(version)
    if spec is None:
        problems.append(f"versão de critérios ausente, divergente ou desconhecida: {sorted(map(str, {e.get('criteria_version') for e in envs.values()}))}")
    else:
        for k in spec["required"]:
            vals = {json.dumps(envs[m].get(k)) for m in dirs}
            if len(vals) != 1 or "null" in vals:
                problems.append(f"metadado {k} ausente ou divergente entre os modos")
        # execução não definitiva (desenvolvimento): pode usar outra matriz e não tem congelamento; ela nunca
        # gera TRL e é classificada como NÃO DEFINITIVO, salvo inconsistência real entre artefatos e modos
        dev_run = any(envs[m].get("definitive") is not True for m in dirs)
        for k, want in spec["values"].items():
            if dev_run and k == "matrix_file":
                continue
            for m in dirs:
                got = envs[m].get(k)
                if got is not None and got != want:
                    problems.append(f"{m}: {k} = {got!r}, esperado {want!r} na versão {version}")
        if "freeze" in spec:
            fp = root / spec["freeze"]
            if not fp.exists():
                # sem congelamento: execução de desenvolvimento é só não definitiva; definitiva é inconsistente
                if not dev_run:
                    problems.append(f"{spec['freeze']} ausente: sem congelamento registrado")
            elif not dev_run:
                # execução definitiva: o congelamento inteiro precisa conferir (código, matriz, semente,
                # deslocamento, receptor, critérios e versões numéricas), para cada modo
                sys.path.insert(0, str(Path(__file__).resolve().parent))
                from freeze import verify_freeze  # noqa: E402
                for m in dirs:
                    for msg in verify_freeze(root, env=envs[m]):
                        problems.append(f"{m}: {msg}")

    definitive = all(envs[m].get("definitive") is True for m in dirs) and all(
        (r or {}).get("env", {}).get("definitive") is True for m in dirs for r in results[m].values() if r is not None)
    complete = all(v is not None for t in REQUIRED for v in table[t].values())
    all_pass = complete and all(table[t][m] for t in REQUIRED for m in dirs)

    if problems:
        rule = "INCONSISTENT_RUNS: " + "; ".join(problems) + "; nenhuma conclusão de TRL"
    elif not complete:
        rule = "INCOMPLETO: falta resultado de algum ensaio ou modo; nenhuma conclusão de TRL"
    elif not definitive:
        rule = "NÃO DEFINITIVO: execução de fumaça ou de desenvolvimento; nenhuma conclusão de TRL"
    elif all_pass:
        rule = f"TRL 4 (autoavaliação) do subsistema computacional sob os critérios {version}: B1-B5 e B7 aprovados nos modos hf e lf"
    else:
        failed = [f"{t}/{m}" for t in REQUIRED for m in dirs if not table[t][m]]
        rule = f"TRL 3 sob os critérios {version}: ensaios obrigatórios reprovados: " + ", ".join(failed)
    return {"by_test_and_mode": table, "problems": problems, "complete": complete, "definitive": definitive,
            "criteria_version": version, "receiver": {m: e.get("receiver") for m, e in envs.items()},
            "commit": {m: e.get("commit") for m, e in envs.items()},
            "matrix_sha256": {m: e.get("matrix_sha256") for m, e in envs.items()}, "trl_rule": rule}


def main() -> None:
    dirs = {"hf": Path(sys.argv[1]), "lf": Path(sys.argv[2])}
    out_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("aggregate.json")
    result = aggregate(dirs)
    out_path.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
