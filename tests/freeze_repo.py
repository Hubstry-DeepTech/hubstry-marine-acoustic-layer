"""Monta, num diretório temporário, um repositório mínimo com congelamento v0.4 válido (apoio aos testes)."""
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "lab" / "bench"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, BENCH / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


freeze = _load("freeze")
_mk = _load("make_matrix")
SEED, OFFSET = 4242, 1_500_000_000
MATRIX_TEXT = json.dumps(_mk.build_matrix("0.4.0", SEED, OFFSET), separators=(",", ":")) + "\n"
MATRIX_SHA = hashlib.sha256(MATRIX_TEXT.encode("utf-8")).hexdigest()
ENVIRONMENT = {"python": "3.11.17", "numpy": "2.4.6", "scipy": "1.17.1", "libc": "glibc2.43"}


def make_repo(root: Path, receiver: str = "v3", **overrides) -> dict:
    for rel in freeze.PROTECTED:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        src = ROOT / rel
        if src.exists():
            shutil.copy(src, dst)
        else:  # documento ainda não criado no repositório real (ex.: critérios congelados)
            dst.write_text(f"conteúdo de teste de {rel}\n", encoding="utf-8")
    (root / freeze.MATRIX_REL).write_text(MATRIX_TEXT, encoding="utf-8")
    fz = freeze.create(root, receiver, SEED, OFFSET, dict(ENVIRONMENT))
    if overrides:
        fz.update(overrides)
        (root / freeze.FREEZE_REL).write_text(json.dumps(fz), encoding="utf-8")
    return fz


def run_env(**kw) -> dict:
    env = {"criteria_version": "0.4.0", "matrix_version": "0.4.0", "matrix_file": "matrix_v04.json", "matrix_sha256": MATRIX_SHA,
           "b3c_min_snr_db": 20, "matrix_seed": SEED, "noise_seed_offset": OFFSET, "commit": "c" * 40, "receiver": "v3",
           "definitive": True, "python": ENVIRONMENT["python"], "numpy": ENVIRONMENT["numpy"], "scipy": ENVIRONMENT["scipy"]}
    env.update(kw)
    return env
