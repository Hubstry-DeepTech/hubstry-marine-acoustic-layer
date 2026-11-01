"""Verificação reproduzível da completude da busca exata de atribuições (decisão D1).

Uso: python -m lab.sim_mca001.verify_d1 --out lab/sim_mca001/results/verify_d1.json

Três baterias, todas com sementes fixas:
1. "geral": 3.000 casos com K de 2 a 6, N = 12, incertezas de 0,01 a 0,5 Hz, termo comum e
   perturbação não diagonal; Δ_T sorteado entre 0, 1 e 5. É a bateria citada no relatório do
   piloto v2.
2. "mal_condicionada": 500 casos com incertezas de 1e-4 a 1 Hz (razão de até 10⁴ entre
   componentes) e correlação forte não comum.
3. "escala_operacional": N de 60 a 70 e K de 4 a 6, contra busca exaustiva vetorizada sobre
   todas as combinações crescentes. K ≥ 7 com N = 60 tem mais de 3,8·10⁸ combinações e fica
   fora do alcance da comparação exaustiva; não é coberto aqui.

Em cada caso compara o mínimo e o conjunto H* inteiro. A busca exaustiva é a referência.
"""
import argparse
import json
import time
from itertools import combinations

import numpy as np

from . import assignment as A


def exhaustive_vectorized(freqs, Sigma, N, delta_T, chunk=400_000):
    """χ² de todas as atribuições crescentes e mínimas, em blocos (referência independente
    da fatoração UᵀDU: usa M diretamente)."""
    y = np.log(np.asarray(freqs, float))
    K = y.size
    M = A._residual_form(Sigma)
    combos = combinations(range(1, N + 1), K)
    best, kept = np.inf, []
    while True:
        block = np.array(list(_take(combos, chunk)), dtype=np.int64)
        if block.size == 0:
            break
        block = block[np.gcd.reduce(block, axis=1) == 1]
        V = y[None, :] - np.log(block)
        chi2 = np.einsum("ij,jk,ik->i", V, M, V)
        best = min(best, float(chi2.min()))
        kept.append((block, chi2))
    tol = 1e-9 * max(1.0, abs(best))
    hstar = set()
    for block, chi2 in kept:
        sel = chi2 <= best + delta_T + tol
        hstar.update(tuple(int(x) for x in row) for row in block[sel])
    return best, hstar


def _take(it, n):
    for _ in range(n):
        try:
            yield next(it)
        except StopIteration:
            return


def compare(freqs, Sigma, N, delta_T):
    t0 = time.time()
    tx, hx, nodes = A.exact_search(freqs, Sigma, N, delta_T)
    dt = time.time() - t0
    te, he = exhaustive_vectorized(freqs, Sigma, N, delta_T)
    # tolerância relativa 1e-7: com Σ de número de condição até ~1e9, somas em ordens diferentes
    # (einsum na referência, produto matricial na busca) diferem em até ~1e-8 relativo
    same_min = bool(np.isclose(tx, te, rtol=1e-7, atol=1e-9))
    same_set = {h for h, _ in hx} == he
    return same_min, same_set, dt, nodes


def battery(name, cases):
    res = dict(n=0, minimo_igual=0, hstar_igual=0, tempo_mediano_s=None, tempo_max_s=None,
               nos_max=0, falhas_fatoracao=0)
    times = []
    for freqs, Sigma, N, dT in cases:
        res["n"] += 1
        try:
            sm, ss, dt, nodes = compare(freqs, Sigma, N, dT)
        except np.linalg.LinAlgError:
            res["falhas_fatoracao"] += 1
            continue
        res["minimo_igual"] += sm
        res["hstar_igual"] += ss
        times.append(dt)
        res["nos_max"] = max(res["nos_max"], nodes)
    if times:
        res["tempo_mediano_s"] = float(np.median(times))
        res["tempo_max_s"] = float(np.max(times))
    print(name, res, flush=True)
    return res


def general_cases(n=3000, seed=0):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        K = int(rng.integers(2, 7))
        f = np.sort(np.exp(rng.uniform(np.log(10), np.log(150), K)))
        S = A.sigma_matrix(f, rng.uniform(0.01, 0.5, K), common_lnf=rng.uniform(0, 0.01))
        B = rng.normal(size=(K, K)) * 1e-5
        yield f, S + B @ B.T, 12, float(rng.choice([0.0, 1.0, 5.0]))


def ill_conditioned_cases(n=500, seed=1):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        K = int(rng.integers(3, 7))
        f = np.sort(np.exp(rng.uniform(np.log(10), np.log(300), K)))
        sd = np.exp(rng.uniform(np.log(1e-4), np.log(1.0), K)) / f
        C = rng.uniform(-1, 1, size=(K, K))
        R = C @ C.T + 0.05 * np.eye(K)
        d = np.sqrt(np.diag(R))
        R = R / np.outer(d, d)
        yield f, np.outer(sd, sd) * R, 20, float(rng.choice([0.0, 1.0, 5.0]))


def operational_cases(seed=2, per=6):
    rng = np.random.default_rng(seed)
    for K, N in ((4, 60), (5, 60), (5, 70), (6, 60)):
        for i in range(per if K < 6 else 3):
            if i % 2 == 0:  # quase harmônico
                f0 = rng.uniform(12, 18)
                orders = np.sort(rng.choice(np.arange(1, N // 2), size=K, replace=False))
                f = f0 * orders * (1 + rng.normal(0, 2e-3, K))
            else:  # nulo
                f = np.sort(np.exp(rng.uniform(np.log(10), np.log(900), K)))
            S = A.sigma_matrix(f, rng.uniform(0.05, 0.5, K), common_lnf=0.002)
            yield np.sort(f), S, N, 1.0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--rapido", action="store_true", help="baterias reduzidas, para teste")
    a = ap.parse_args(argv)
    t0 = time.time()
    out = dict(
        geral=battery("geral", general_cases(n=200 if a.rapido else 3000)),
        mal_condicionada=battery("mal_condicionada", ill_conditioned_cases(n=50 if a.rapido else 500)),
    )
    if not a.rapido:
        out["escala_operacional"] = battery("escala_operacional", operational_cases())
    out["limite_nao_coberto"] = "K >= 7 com N >= 60 (comparação exaustiva inviável)"
    out["tempo_total_s"] = round(time.time() - t0, 1)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
