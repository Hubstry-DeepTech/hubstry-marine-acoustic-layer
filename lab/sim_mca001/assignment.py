"""Atribuição de ordens, ajuste por mínimos quadrados generalizados e conjunto H*.

Perfil v0.1.4, Seção 4. Enumeração exata das atribuições consistentes com arredondamento
(decisão D1: h crescente), mais as perturbações de ±1 em cada ordem, e comparação com a
busca exaustiva sobre todas as funções injetivas para N e K pequenos.
"""
from itertools import combinations, permutations
from math import gcd
from functools import reduce

import numpy as np


def gls_fit(y, lnh, Sigma):
    """ln g = 1ᵀΣ⁻¹(y − ln h) / 1ᵀΣ⁻¹1; devolve (ln g, var(ln g), resíduos, qui-quadrado)."""
    one = np.ones_like(y)
    Si1 = np.linalg.solve(Sigma, one)
    z = y - lnh
    denom = one @ Si1
    lng = (Si1 @ z) / denom
    r = z - lng
    chi2 = float(r @ np.linalg.solve(Sigma, r))
    return float(lng), float(1.0 / denom), r, chi2


def is_minimal(h):
    return reduce(gcd, map(int, h)) == 1


def minimal(h):
    d = reduce(gcd, map(int, h))
    return tuple(int(v) // d for v in h)


def rounding_candidates(freqs, N):
    """Todas as atribuições crescentes h = round(f/g), para g percorrendo os intervalos entre
    os pontos de quebra f_k/(j + 1/2), com ordens em 1..N, reduzidas à forma mínima."""
    f = np.asarray(freqs, float)
    breaks = sorted({fk / (j + 0.5) for fk in f for j in range(0, N + 1)})
    gs = [np.sqrt(a * b) for a, b in zip(breaks[:-1], breaks[1:])]
    out = set()
    for g in gs:
        h = np.rint(f / g).astype(int)
        if h.min() < 1 or h.max() > N or np.any(np.diff(h) <= 0):
            continue
        out.add(minimal(h))
    return out


def neighbors(cands, N):
    out = set(cands)
    for h in cands:
        for k in range(len(h)):
            for s in (-1, 1):
                v = list(h)
                v[k] += s
                if 1 <= v[k] <= N and all(b > a for a, b in zip(v[:-1], v[1:])):
                    out.add(minimal(v))
    return out


def search(freqs, Sigma, N, delta_T, exhaustive=False, monotone=True):
    """Devolve (T_min, lista de (h, ln g, qui-quadrado) em H*, todas as avaliações).

    exhaustive=True avalia todas as atribuições injetivas e mínimas (crescentes se monotone,
    ou todas as permutações se não); só para N e K pequenos."""
    y = np.log(np.asarray(freqs, float))
    K = y.size
    if K < 2:
        return np.nan, [], []
    if exhaustive:
        base = combinations(range(1, N + 1), K)
        cands = (p for c in base for p in (permutations(c) if not monotone else [c]))
        cands = {tuple(h) for h in cands if is_minimal(h)}
    else:
        cands = neighbors(rounding_candidates(freqs, N), N)
    evals = []
    for h in cands:
        lng, _, _, chi2 = gls_fit(y, np.log(np.asarray(h, float)), Sigma)
        evals.append((h, lng, chi2))
    if not evals:
        return np.nan, [], []
    tmin = min(e[2] for e in evals)
    hstar = sorted([e for e in evals if e[2] <= tmin + delta_T], key=lambda e: e[2])
    return tmin, hstar, evals


def sigma_matrix(freqs, sigma_f, common_lnf=0.0):
    """Σ dos ln f: diagonal (σ_f/f)² mais um termo comum de comodulação c²·11ᵀ."""
    f = np.asarray(freqs, float)
    s = np.asarray(sigma_f, float) / f
    return np.diag(s ** 2) + common_lnf ** 2 * np.ones((f.size, f.size))
