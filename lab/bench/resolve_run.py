"""Decide o tipo de execução da bancada no GitHub Actions (.github/workflows/bench.yml).

- push (commit de congelamento): execução confirmatória; receptor e critérios vêm de lab/bench/FREEZE_v0.4.json.
- workflow_dispatch: execução de desenvolvimento; exige semente, gera a matriz em /tmp/matrix_dev.json e
  acrescenta --smoke, de modo que o resultado nunca é definitivo.
Qualquer outro evento, ou um disparo manual sem semente, falha.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEV_MATRIX = "/tmp/matrix_dev.json"
DEV_MAX_OFFSET = 1_000_000_000  # faixa reservada às matrizes confirmatórias começa aqui


class RunError(ValueError):
    pass


def resolve(event: str, inputs: dict, freeze_path: Path = HERE / "FREEZE_v0.4.json") -> dict:
    if event == "push":
        if not freeze_path.exists():
            raise RunError("execução confirmatória sem FREEZE_v0.4.json")
        fz = json.loads(freeze_path.read_text(encoding="utf-8"))
        r, c = fz["receiver"], fz["criteria_version"]
        return {"kind": "confirmatory", "label": f"conf-{r}-{c}", "args": f"--receiver {r} --criteria {c}", "make": None}
    if event == "workflow_dispatch":
        seed = (inputs.get("dev_seed") or "").strip()
        if not seed.isdigit():
            raise RunError("disparo manual exige dev_seed numérica; não há caminho manual para rodada definitiva")
        off = int((inputs.get("dev_noise_offset") or "0").strip())
        if not 0 < off < DEV_MAX_OFFSET:
            raise RunError(f"dev_noise_offset precisa ficar entre 1 e {DEV_MAX_OFFSET - 1}")
        r, c = inputs.get("receiver") or "v3", inputs.get("criteria") or "0.4.0"
        if r not in {"v1", "v2", "v3"} or c not in {"0.3.1", "0.4.0"}:
            raise RunError(f"receptor ou critérios inválidos: {r!r}, {c!r}")
        make = ["--version", f"dev-{seed}", "--seed", seed, "--noise-offset", str(off), "--out", DEV_MATRIX]
        return {"kind": "dev", "label": f"dev{seed}-{r}-{c}",
                "args": f"--receiver {r} --criteria {c} --matrix {DEV_MATRIX} --smoke", "make": make}
    raise RunError(f"evento não suportado: {event}")


def main() -> None:
    inputs = {k: os.environ.get(f"IN_{k.upper()}", "") for k in ("receiver", "criteria")}
    inputs["dev_seed"] = os.environ.get("IN_SEED", "")
    inputs["dev_noise_offset"] = os.environ.get("IN_OFFSET", "")
    try:
        res = resolve(os.environ.get("EVENT", ""), inputs)
    except RunError as e:
        print(f"::error::{e}")
        sys.exit(1)
    if res["make"]:
        subprocess.check_call([sys.executable, str(HERE / "make_matrix.py"), *res["make"]])
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
        for k in ("kind", "label", "args"):
            fh.write(f"{k}={res[k]}\n")
    print(json.dumps({k: res[k] for k in ("kind", "label", "args")}))


if __name__ == "__main__":
    main()
