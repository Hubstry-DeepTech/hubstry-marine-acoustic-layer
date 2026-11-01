"""Atribuição de ordens, ajuste por mínimos quadrados generalizados e conjunto H*.

Perfil v0.1.4, Seção 4; decisão D1: atribuições crescentes e mínimas.

- `exact_search` (padrão de `search`): busca completa por ramificação e poda sobre a forma
  χ²(h) = vᵀMv, com fatoração UᵀDU protegida (`_udu`). Devolve todo o conjunto H*, e não só
  o mínimo. Verificação reproduzível em `verify_d1.py`.
- `rounding_candidates` e `neighbors`: heurística antiga por arredondamento com perturbações
  de ±1. NÃO é completa (contraexemplo da Luna); serve só como cota inicial da busca exata e
  como comparador em testes.
- `search(..., exhaustive=True)`: busca exaustiva, só para N e K pequenos.
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


def chi2_whitened(Sigma, V):
    """χ² de cada linha de V (resíduos y − ln h), com a escala ótima eliminada, calculado de
    forma numericamente estável: branqueamento por Cholesky e projeção explícita do resíduo,
    sem formar Σ⁻¹ (auditoria do Gemini, achado 5). Aceita V com forma (K,) ou (n, K)."""
    from scipy.linalg import cholesky, solve_triangular
    V = np.atleast_2d(np.asarray(V, float))
    L = cholesky(Sigma, lower=True)
    a = solve_triangular(L, np.ones(Sigma.shape[0]), lower=True)
    B = solve_triangular(L, V.T, lower=True)
    R = B - np.outer(a, (a @ B) / (a @ a))
    out = np.einsum("ij,ij->j", R, R)
    return out


def _residual_form(Sigma):
    """M tal que χ²(h) = vᵀMv, com v = y − ln h e a escala ótima eliminada.

    Construída por Cholesky, sem inverter Σ explicitamente (parecer da Luna sobre 434ca29):
    com Σ = LLᵀ, a = L⁻¹1 e W = L⁻¹ (triangular), M = Wᵀ(I − aaᵀ/aᵀa)W. É a mesma forma
    usada por chi2_whitened. M é semidefinida, com núcleo gerado por 1."""
    from scipy.linalg import cholesky, solve_triangular
    K = Sigma.shape[0]
    L = cholesky(Sigma, lower=True)
    W = solve_triangular(L, np.eye(K), lower=True)
    a = W @ np.ones(K)
    P = np.eye(K) - np.outer(a, a) / (a @ a)
    M = W.T @ P @ W
    return 0.5 * (M + M.T)


PIVOT_RTOL = 1e-10          # pivô relativo abaixo do qual a fatoração é considerada degenerada
RECONSTRUCTION_RTOL = 1e-6  # erro máximo relativo aceito em ‖UᵀDU − M‖; com Σ de condição ~1e9 o arredondamento chega a ~1e-8
SEARCH_SLACK_RTOL = 1e-4    # folga relativa do raio de poda (ver exact_search)


def _udu(M):
    """M = UᵀDU, com U triangular superior unitária. Então
    vᵀMv = Σ_k d_k·(v_k + Σ_{j>k} U_kj·v_j)²: cada termo depende só de v_k, …, v_{K−1}.

    Garantias exigidas (parecer da Luna sobre o piloto v2):
    - M tem núcleo gerado por 1, que não tem entradas nulas; logo toda submatriz principal
      líder de ordem k < K é definida positiva e os K − 1 primeiros pivôs são positivos.
      Um pivô intermediário não positivo é erro, e não é zerado em silêncio.
    - Só o último pivô é nulo em aritmética exata; ele é posto em zero se estiver dentro da
      tolerância, e a fatoração falha se não estiver.
    - A reconstrução UᵀDU reproduz M dentro de RECONSTRUCTION_RTOL; caso contrário, falha."""
    K = M.shape[0]
    scale = float(np.max(np.abs(np.diag(M))))
    if not np.isfinite(scale) or scale <= 0:
        raise np.linalg.LinAlgError("matriz M sem escala positiva")
    U = np.eye(K)
    d = np.zeros(K)
    for k in range(K):
        d[k] = M[k, k] - np.sum(d[:k] * U[:k, k] ** 2)
        if k < K - 1:
            if not d[k] > PIVOT_RTOL * scale:
                raise np.linalg.LinAlgError(
                    f"pivô intermediário {k} não positivo ({d[k]:.3e}); Σ mal condicionada")
            for j in range(k + 1, K):
                U[k, j] = (M[k, j] - np.sum(d[:k] * U[:k, k] * U[:k, j])) / d[k]
        else:
            if abs(d[k]) > 1e3 * PIVOT_RTOL * scale * K:
                raise np.linalg.LinAlgError(
                    f"último pivô não nulo ({d[k]:.3e}); 1 não está no núcleo de M")
            d[k] = 0.0
    err = float(np.max(np.abs(U.T @ np.diag(d) @ U - M)))
    if err > RECONSTRUCTION_RTOL * scale:
        raise np.linalg.LinAlgError(f"reconstrução UᵀDU com erro relativo {err / scale:.3e}")
    return d, U


def _factored_value(v, d, U):
    """vᵀMv pela soma dos termos fatorados, acumulada de k = K−1 até 0, como na busca."""
    tot = 0.0
    for k in range(v.size - 1, -1, -1):
        c = float(U[k, k + 1:] @ v[k + 1:]) if k + 1 < v.size else 0.0
        tot += d[k] * (v[k] + c) ** 2
    return float(tot)


def exact_search(freqs, Sigma, N, delta_T, initial_bound=np.inf):
    """Busca exata, por ramificação e poda (decodificação em esfera), de todas as atribuições
    crescentes e mínimas com χ² ≤ T_min + Δ_T.

    A cada nível k (de K−1 até 0), o termo d_k·(v_k + c_k)² é uma cota inferior parcial de
    χ², porque todos os termos são não negativos. Assim, h_k só precisa percorrer as ordens
    com |ln h_k − (y_k + c_k)| ≤ √(orçamento/d_k). Nenhuma atribuição com χ² dentro do raio é
    descartada: a busca é completa (decisão D1, parecer da Luna sobre o Bloco 1).
    Devolve (T_min, lista de (h, χ²), número de nós visitados)."""
    y = np.log(np.asarray(freqs, float))
    K = y.size
    if K < 2 or N < K:
        return np.nan, [], 0
    M = _residual_form(Sigma)
    d, U = _udu(M)
    # folga absoluta pelo erro de fatoração: |T_fatorado − vᵀMv| ≲ K²·‖UᵀDU − M‖_max·‖v‖²_∞,
    # com |v_k| ≤ max|y| + ln N (auditoria do Gemini, achado 5)
    fact_err = float(np.max(np.abs(U.T @ np.diag(d) @ U - M)))
    abs_slack = K * K * fact_err * (float(np.max(np.abs(y))) + np.log(N)) ** 2
    # cota inicial finita: qualquer atribuição viável serve; usa-se a melhor entre (1, …, K)
    # e o resultado da heurística por arredondamento
    seeds = [tuple(range(1, K + 1))] + list(neighbors(rounding_candidates(freqs, N), N))
    for hh in seeds:
        vv = y - np.log(np.asarray(hh, float))
        # a cota inicial usa a mesma aritmética da busca (soma dos termos fatorados, na mesma
        # ordem), para que a própria semente nunca seja podada por diferença de arredondamento
        initial_bound = min(initial_bound, _factored_value(vv, d, U))
    found = []
    best = [initial_bound]
    nodes = [0]
    h = np.zeros(K, dtype=int)
    v = np.zeros(K)

    def radius():
        # folga relativa generosa para o arredondamento entre vᵀMv e a soma dos termos, que
        # chegou a ~6e-5 relativo com Σ de número de condição ~1e10; a poda só pode ficar mais
        # permissiva, nunca mais restritiva, e H* é decidido depois pelo valor direto vᵀMv
        return best[0] + delta_T + SEARCH_SLACK_RTOL * max(1.0, abs(best[0])) + abs_slack

    def rec(k, partial):
        nodes[0] += 1
        hi = (h[k + 1] - 1) if k + 1 < K else N
        lo = k + 1
        if hi < lo:
            return
        c = float(U[k, k + 1:] @ v[k + 1:]) if k + 1 < K else 0.0
        if d[k] > 0:
            budget = radius() - partial
            if budget < 0:
                return
            r = np.sqrt(budget / d[k])
            center = y[k] + c
            # limites calculados no domínio logarítmico e recortados antes da exponencial,
            # para não estourar quando o orçamento é grande (casos mal condicionados)
            cap = np.log(N + 1.0)
            lo_log = min(max(center - r, -1.0), cap)
            hi_log = min(max(center + r, -1.0), cap)
            lo = max(lo, int(np.ceil(np.exp(lo_log) - 1e-12)))
            hi = min(hi, int(np.floor(np.exp(hi_log) + 1e-12)))
        for hk in range(hi, lo - 1, -1):
            h[k] = hk
            v[k] = y[k] - np.log(hk)
            term = d[k] * (v[k] + c) ** 2
            tot = partial + term
            if tot > radius():
                continue
            if k == 0:
                if gcd_all(h) == 1:
                    found.append((tuple(int(x) for x in h), tot))
                    if tot < best[0]:
                        best[0] = tot
            else:
                rec(k - 1, tot)

    rec(K - 1, 0.0)
    if not found:
        # impossível em aritmética exata: a melhor semente está sempre dentro do raio
        raise np.linalg.LinAlgError("busca exata sem candidatos; verificar condicionamento de Σ")
    # valores finais recalculados diretamente, sem a fatoração, para decidir H*
    hs = [hh for hh, _t in found]
    values = chi2_whitened(Sigma, y[None, :] - np.log(np.asarray(hs, float)))
    direct = list(zip(hs, map(float, values)))
    tmin = min(t for _, t in direct)
    tol = 1e-9 * max(1.0, abs(tmin))
    hstar = sorted([(hh, t) for hh, t in direct if t <= tmin + delta_T + tol], key=lambda e: e[1])
    return tmin, hstar, nodes[0]


def gcd_all(h):
    return reduce(gcd, map(int, h))


def search(freqs, Sigma, N, delta_T, exhaustive=False, monotone=True, method="exact"):
    """method="exact" (padrão): busca completa por ramificação e poda. method="rounding":
    heurística antiga por arredondamento, mantida só como comparador; ela NÃO é completa
    (contraexemplo da Luna na revisão do Bloco 1). Devolve (T_min, lista de (h, ln g, qui-quadrado) em H*, todas as avaliações).

    exhaustive=True avalia todas as atribuições injetivas e mínimas (crescentes se monotone,
    ou todas as permutações se não); só para N e K pequenos."""
    y = np.log(np.asarray(freqs, float))
    K = y.size
    if K < 2:
        return np.nan, [], []
    if not exhaustive and method == "exact":
        tmin, hs, _ = exact_search(freqs, Sigma, N, delta_T)
        out = []
        for h, t_exact in hs:
            # ln g vem do ajuste; o χ² devolvido é o mesmo que decidiu H* (Cholesky)
            lng = gls_fit(y, np.log(np.asarray(h, float)), Sigma)[0]
            out.append((h, lng, float(t_exact)))
        return tmin, out, out
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
