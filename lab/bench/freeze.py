"""Congelamento verificável da bancada v0.4 (lab/BENCH_CRITERIA_v0.4.md, Seção 6).

O arquivo lab/bench/FREEZE_v0.4.json registra o que define o experimento: receptor, versão dos critérios,
matriz (arquivo, SHA-256, semente e deslocamento de ruído), SHA-256 de cada arquivo de código e de
documentação protegido e o ambiente esperado (Python, NumPy, SciPy, glibc).

verify_freeze() é executada em dois momentos:
- em resolve_run.py, antes de iniciar a execução confirmatória;
- em aggregate.py, antes de emitir qualquer conclusão de TRL.
Qualquer divergência impede a execução ou a conclusão.

Uso para criar o congelamento (depois de gerar a matriz com make_matrix.py):
  python lab/bench/freeze.py create --receiver v3 --seed S --noise-offset O
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREEZE_REL = "lab/bench/FREEZE_v0.4.json"
MATRIX_REL = "lab/bench/matrix_v04.json"
CRITERIA_VERSION = "0.4.0"
# Arquivos que definem o experimento. Alterar qualquer um deles depois do congelamento invalida a rodada.
PROTECTED = (
    "lab/BENCH_CRITERIA_v0.4.md",
    "lab/bench/receiver.py",
    "lab/bench/run_bench.py",
    "lab/bench/aggregate.py",
    "lab/bench/merge_parts.py",
    "lab/bench/resolve_run.py",
    "lab/bench/make_matrix.py",
    "lab/bench/freeze.py",
    "lab/bench/constraints.txt",
    "src/hmal/core/harmonic_protocol.py",
    ".github/workflows/bench.yml",
)
ENV_KEYS = ("python", "numpy", "scipy", "libc")
REQUIRED_KEYS = ("receiver", "criteria_version", "matrix_file", "matrix_sha256", "matrix_seed", "noise_seed_offset",
                 "protected_sha256", "environment")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def current_environment() -> dict:
    import numpy
    import scipy
    return {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__,
            "libc": "".join(platform.libc_ver())}


def verify_freeze(root: Path = ROOT, env: dict | None = None, check_runtime: bool = False) -> list[str]:
    """Devolve a lista de divergências (vazia = congelamento íntegro).

    env: bloco env de uma execução, para conferir receptor, critérios e matriz efetivamente usados.
    check_runtime: confere também Python, NumPy, SciPy e glibc do processo atual (uso em resolve_run.py).
    """
    fp = root / FREEZE_REL
    if not fp.exists():
        return [f"{FREEZE_REL} ausente"]
    fz = json.loads(fp.read_text(encoding="utf-8"))
    problems = [f"campo ausente no congelamento: {k}" for k in REQUIRED_KEYS if k not in fz]
    if problems:
        return problems
    environment = fz["environment"] if isinstance(fz["environment"], dict) else {}
    if sorted(environment) != sorted(ENV_KEYS) or not all(isinstance(environment[k], str) and environment[k] for k in environment):
        problems.append(f"ambiente do congelamento precisa ter exatamente {list(ENV_KEYS)}, todos preenchidos")
    if fz["criteria_version"] != CRITERIA_VERSION:
        problems.append(f"criteria_version {fz['criteria_version']!r} no congelamento; esperado {CRITERIA_VERSION!r}")
    if fz["matrix_file"] != Path(MATRIX_REL).name:
        problems.append(f"matrix_file {fz['matrix_file']!r} no congelamento; esperado {Path(MATRIX_REL).name!r}")
    mp = root / MATRIX_REL
    if not mp.exists():
        problems.append(f"{MATRIX_REL} ausente")
    else:
        if sha256_file(mp) != fz["matrix_sha256"]:
            problems.append("SHA-256 da matriz difere do congelamento")
        m = json.loads(mp.read_text(encoding="utf-8"))
        if m.get("version") != CRITERIA_VERSION:
            problems.append(f"versão da matriz {m.get('version')!r} difere de {CRITERIA_VERSION!r}")
        if m.get("seed") != fz["matrix_seed"]:
            problems.append("semente da matriz difere do congelamento")
        if m.get("noise_seed_offset") != fz["noise_seed_offset"]:
            problems.append("deslocamento de ruído da matriz difere do congelamento")
    if sorted(fz["protected_sha256"]) != sorted(PROTECTED):
        problems.append("lista de arquivos protegidos do congelamento difere da lista do código")
    for rel, digest in fz["protected_sha256"].items():
        p = root / rel
        if not p.exists():
            problems.append(f"arquivo protegido ausente: {rel}")
        elif sha256_file(p) != digest:
            problems.append(f"arquivo protegido alterado depois do congelamento: {rel}")
    if env is not None:
        pairs = {"receiver": "receiver", "criteria_version": "criteria_version", "matrix_file": "matrix_file",
                 "matrix_sha256": "matrix_sha256", "matrix_seed": "matrix_seed", "noise_seed_offset": "noise_seed_offset"}
        for ek, fk in pairs.items():
            if env.get(ek) != fz[fk]:
                problems.append(f"{ek} da execução ({env.get(ek)!r}) difere do congelamento ({fz[fk]!r})")
        if env.get("matrix_version") != CRITERIA_VERSION:
            problems.append(f"matrix_version da execução ({env.get('matrix_version')!r}) difere de {CRITERIA_VERSION!r}")
        for k in ENV_KEYS:
            if env.get(k) is None or env.get(k) != environment.get(k):
                problems.append(f"{k} da execução ({env.get(k)!r}) difere do congelamento ({environment.get(k)!r})")
    if check_runtime:
        now = current_environment()
        for k in ENV_KEYS:
            want = environment.get(k)
            if want is None or now.get(k) != want:
                problems.append(f"ambiente: {k} = {now.get(k)!r}, congelado {want!r}")
    return problems


def create(root: Path, receiver: str, seed: int, offset: int, environment: dict) -> dict:
    mp = root / MATRIX_REL
    m = json.loads(mp.read_text(encoding="utf-8"))
    if (m.get("seed"), m.get("noise_seed_offset"), m.get("version")) != (seed, offset, CRITERIA_VERSION):
        raise SystemExit("a matriz não corresponde à semente, ao deslocamento ou à versão informados")
    fz = {
        "receiver": receiver,
        "criteria_version": CRITERIA_VERSION,
        "matrix_file": mp.name,
        "matrix_sha256": sha256_file(mp),
        "matrix_seed": seed,
        "noise_seed_offset": offset,
        "protected_sha256": {rel: sha256_file(root / rel) for rel in PROTECTED},
        "environment": environment,
        "note": "o commit que contém este arquivo é o commit de congelamento; seu hash não pode constar aqui sem circularidade",
    }
    (root / FREEZE_REL).write_text(json.dumps(fz, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return fz


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("--receiver", required=True, choices=["v1", "v2", "v3"])
    c.add_argument("--seed", type=int, required=True)
    c.add_argument("--noise-offset", type=int, required=True)
    c.add_argument("--python", required=True, help="versão exata do Python da execução confirmatória")
    c.add_argument("--libc", required=True, help="glibc da execução confirmatória, ex.: glibc2.43")
    sub.add_parser("verify")
    a = ap.parse_args()
    if a.cmd == "create":
        cons = dict(line.strip().split("==") for line in (ROOT / "lab/bench/constraints.txt").read_text().splitlines()
                    if "==" in line and not line.startswith("#"))
        env = {"python": a.python, "numpy": cons["numpy"], "scipy": cons["scipy"], "libc": a.libc}
        print(json.dumps(create(ROOT, a.receiver, a.seed, a.noise_offset, env), indent=1))
    else:
        problems = verify_freeze()
        print("congelamento íntegro" if not problems else "\n".join(problems))
        sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
