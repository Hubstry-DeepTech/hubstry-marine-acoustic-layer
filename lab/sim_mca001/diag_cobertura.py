"""Diagnóstico da cobertura da incerteza empírica por ordem e por fator (auditoria do piloto v2).

Uso: python -m lab.sim_mca001.diag_cobertura --piloto lab/sim_mca001/results/block1_piloto_v2.json

Gera uma réplica da partição "ver" por célula (160 sinais), aplica a tabela de calibração
do piloto e compara duas formas de verificar a cobertura de 95%:
- "log agregado": quantis de ln(f_est/f_true) agregados sobre todas as ordens (runner v2);
- "Hz": quantis do erro em Hz, que equivalem, para cada componente, a um intervalo em ln f
  de largura proporcional a 1/f_k.
"""
import argparse
import itertools
import json
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

from . import block1 as B


def order_band(o):
    return "1-3" if o <= 3 else "4-10" if o <= 10 else "11-30" if o <= 30 else "31+"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", required=True)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args(argv)
    unc = json.load(open(a.piloto, encoding="utf-8"))["resultados"]["incerteza"]
    cells = [dict(zip(B.GRID, v)) for v in itertools.product(*B.GRID.values())]
    with Pool(a.workers) as pool:
        res = pool.map(B.run_one, [(c, "ver", 0) for c in cells], chunksize=4)
    cell_of = {r["signal_id"]: r["cell"] for r in res}
    out = {}
    for w in B.WINDOWS:
        u = unc[str(w)]
        mins = u["limiar_minimo_snr_local_db"]
        if mins is None:
            continue
        by = {(e["snr_bin"], e["modulation"]): e for e in u["tabela_calibracao_cal"]}
        sig = {"log": defaultdict(lambda: [0, 0]), "hz": defaultdict(lambda: [0, 0])}
        order = {"log": defaultdict(lambda: [0, 0]), "hz": defaultdict(lambda: [0, 0])}
        factor = defaultdict(lambda: [0, 0])
        for r in B._rows_from_results(res, w, "ver"):
            if r["snr_db"] < mins:
                continue
            e = by.get((B._snr_bin(r["snr_db"]), B._modulation_class(r["modulation_oct_s"])))
            if not e or e["status"] != "ok":
                continue
            le = np.log(r["f_est"] / r["f_true"])
            cov = {"log": e["q025_erro_log_f"] <= le <= e["q975_erro_log_f"],
                   "hz": e["q025_erro_hz"] <= r["error_hz"] <= e["q975_erro_hz"]}
            for k in ("log", "hz"):
                sig[k][r["signal_id"]][0] += cov[k]
                sig[k][r["signal_id"]][1] += 1
                order[k][order_band(r["order"])][0] += cov[k]
                order[k][order_band(r["order"])][1] += 1
            c = cell_of[r["signal_id"]]
            for f in ("profile", "f0", "slope", "snr", "alpha"):
                factor[f"{f}={c[f]}"][0] += cov["hz"]
                factor[f"{f}={c[f]}"][1] += 1
        out[str(w)] = dict(
            limiar_snr_local_db=mins,
            media_por_sinal={k: float(np.mean([x / n for x, n in sig[k].values()])) for k in sig},
            por_faixa_de_ordem={k: {b: x / n for b, (x, n) in sorted(order[k].items())} for k in order},
            hz_por_fator={f: x / n for f, (x, n) in sorted(factor.items())},
            n_sinais=len(sig["hz"]))
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
