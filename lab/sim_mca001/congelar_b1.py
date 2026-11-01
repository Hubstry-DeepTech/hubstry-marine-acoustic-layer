"""Gera o artefato de congelamento do Bloco 1 a partir de uma rodada exploratória (cal e ver).

Uso:
  python -m lab.sim_mca001.congelar_b1 --rodada results/block1_X.json --janela 1.0 \
      --limiar-deteccao 10 --decidido-por "Luna, parecer de DD/MM" --out results/block1_freeze.json

Usa só os campos calibrados em cal (tabela de incerteza, SNR mínima, limiar do YIN). A escolha
da janela e do limiar de detecção é uma decisão registrada no campo decidido_por, tomada antes
de qualquer execução da partição val.
"""
import argparse
import json

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
    freeze = B.build_freeze(run["resultados"], a.janela, a.limiar_deteccao, a.decidido_por, a.notas)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(freeze, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(a.out, freeze["sha256"])


if __name__ == "__main__":
    main()
