"""Ferramentas estatísticas comuns."""
import numpy as np
from scipy.stats import beta, binom


def p_empirical(t_obs, t_null):
    """Cauda inferior: p = (1 + #{T_b ≤ T_obs}) / (B + 1)."""
    t_null = np.asarray(t_null, float)
    return (1 + int(np.sum(t_null <= t_obs))) / (t_null.size + 1)


def clopper_pearson(k, n, conf=0.95):
    a = 1 - conf
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return float(lo), float(hi)


def upper_one_sided(k, n, conf=0.95):
    return 1.0 if k == n else float(beta.ppf(conf, k + 1, n - k))


def pass_probability(n, alpha=0.05, delta=0.01, conf=0.95):
    """Probabilidade de um teste exatamente calibrado em alpha passar no critério
    'limite superior unilateral ≤ alpha + delta' com n réplicas (cálculo binomial exato)."""
    k = 0
    while k < n and upper_one_sided(k, n, conf) <= alpha + delta:
        k += 1
    return float(binom.cdf(k - 1, n, alpha))
