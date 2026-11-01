"""Gera o artefato de congelamento do Bloco 1 a partir de uma rodada exploratória (cal e ver).

Uso:
  python -m lab.sim_mca001.congelar_b1 --rodada results/block1_X.json --janela 1.0 \
      --limiar-deteccao 10 --decidido-por "Luna, parecer de DD/MM" --out results/block1_freeze.json

Usa só os campos calibrados em cal (tabela de incerteza, SNR mínima, limiar do YIN). A escolha
da janela e do limiar de detecção é uma decisão registrada no campo decidido_por, tomada antes
de qualquer execução da partição val.

Proveniência: grava o commit de origem (recusa código com alterações não commitadas), o
SHA-256 da rodada exploratória, a impressão digital do código e a configuração completa.
Gera também <out>.sha256, que deve ser commitado num commit próprio antes da rodada val:
o hash interno só detecta alteração sem recálculo; o commit é o registro independente.
"""
import argparse
import hashlib
import json
import subprocess

from . import block1 as B


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodada", required=True)
    ap.add_argument("--janela", type=float, required=True)
    ap.add_argument("--limiar-deteccao", type=float, required=True)
    ap.add_argument("--decidido-por", required=True)
    ap.add_argument("--notas", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    run = json.load(open(a.rodada, encoding="utf-8"))
    if "val" in run.get("particoes", []):
        raise SystemExit("a rodada de origem não pode conter val")
    with open(a.rodada, "rb") as fh:
        rodada_sha = hashlib.sha256(fh.read()).hexdigest()
    git = lambda *args: subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()
    provenance = dict(
        commit=git("rev-parse", "HEAD") or None,
        arvore_com_alteracoes=bool(git("status", "--porcelain", "--", "lab/sim_mca001/*.py")),
        rodada_arquivo=a.rodada,
        rodada_sha256=rodada_sha,
        rodada_particoes=run.get("particoes"),
        rodada_plano=run.get("plano"),
    )
    if provenance["arvore_com_alteracoes"]:
        raise SystemExit("há alterações não commitadas no código de lab/sim_mca001; commite antes")
    freeze = B.build_freeze(run["resultados"], a.janela, a.limiar_deteccao, a.decidido_por,
                            a.notas, provenance=provenance)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(freeze, fh, ensure_ascii=False, indent=1, sort_keys=True)
    with open(a.out, "rb") as fh:
        file_sha = hashlib.sha256(fh.read()).hexdigest()
    # registro independente do checksum, a commitar num commit próprio antes da rodada val
    with open(a.out + ".sha256", "w", encoding="utf-8") as fh:
        fh.write(f"{file_sha}  {a.out}\n")
    print(a.out, "conteúdo", freeze["sha256"], "arquivo", file_sha)


if __name__ == "__main__":
    main()
