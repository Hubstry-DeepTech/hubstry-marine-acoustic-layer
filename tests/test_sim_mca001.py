"""Testes automáticos do plano SIM-MCA-001 (Seção 7). Rápidos: rodam no CI a cada PR."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab.sim_mca001 import assignment as A  # noqa: E402
from lab.sim_mca001 import detection as D  # noqa: E402
from lab.sim_mca001 import fundamental as F0  # noqa: E402
from lab.sim_mca001 import generator as G  # noqa: E402
from lab.sim_mca001 import seeds as S  # noqa: E402
from lab.sim_mca001 import stats as ST  # noqa: E402


def test_seeds_are_deterministic_and_partitioned():
    a = S.rng("B1", "c", "cal", 0).normal(size=3)
    b = S.rng("B1", "c", "cal", 0).normal(size=3)
    c = S.rng("B1", "c", "ver", 0).normal(size=3)
    assert np.array_equal(a, b) and not np.array_equal(a, c)
    with pytest.raises(ValueError):
        S.rng("B1", "c", "teste", 0)


def test_noiseless_harmonic_recovers_exact_assignment():
    """G1 sem ruído: a busca recupera h exata e qui-quadrado próximo de zero."""
    f0 = 14.3
    freqs = f0 * np.array([1, 2, 3, 4, 5, 6])
    Sigma = A.sigma_matrix(freqs, 0.05)
    tmin, hstar, _ = A.search(freqs, Sigma, N=40, delta_T=1.0)
    assert hstar[0][0] == (1, 2, 3, 4, 5, 6)
    assert tmin < 1e-9
    assert np.isclose(np.exp(hstar[0][1]), f0)


def test_even_only_components_get_minimal_assignment():
    """Componentes só em 2f0 e 4f0 recebem a atribuição mínima (1, 2), com escala 2f0."""
    f0 = 15.0
    freqs = np.array([2 * f0, 4 * f0])
    tmin, hstar, _ = A.search(freqs, A.sigma_matrix(freqs, 0.05), N=40, delta_T=0.0)
    assert hstar[0][0] == (1, 2)
    assert np.isclose(np.exp(hstar[0][1]), 2 * f0)


def test_p_empirical_minimum_and_direction():
    assert ST.p_empirical(0.1, np.ones(999)) == pytest.approx(1 / 1000)
    assert ST.p_empirical(5.0, np.ones(999)) == pytest.approx(1.0)


def test_gls_with_diagonal_sigma_equals_wls():
    rng = np.random.default_rng(1)
    y = np.log(15 * np.array([1, 2, 3, 5.0])) + rng.normal(0, 0.01, 4)
    lnh = np.log([1, 2, 3, 5.0])
    s = np.array([0.01, 0.02, 0.005, 0.03])
    lng, _, _, chi2 = A.gls_fit(y, lnh, np.diag(s ** 2))
    w = 1 / s ** 2
    lng_wls = np.sum(w * (y - lnh)) / np.sum(w)
    assert lng == pytest.approx(lng_wls)
    assert chi2 == pytest.approx(np.sum(w * (y - lnh - lng_wls) ** 2))


def test_common_mode_covariance_does_not_change_chi2():
    """Termo comum c²·11ᵀ (comodulação) é absorvido pela escala: não muda o qui-quadrado."""
    rng = np.random.default_rng(2)
    freqs = 15 * np.array([1, 2, 3, 4.0]) * (1 + rng.normal(0, 0.002, 4))
    lnh = np.log([1, 2, 3, 4.0])
    y = np.log(freqs)
    _, v0, _, c0 = A.gls_fit(y, lnh, A.sigma_matrix(freqs, 0.05))
    _, v1, _, c1 = A.gls_fit(y, lnh, A.sigma_matrix(freqs, 0.05, common_lnf=0.01))
    assert c1 == pytest.approx(c0)
    assert v1 > v0


def test_rounding_search_matches_exhaustive_on_small_case():
    """Decisão D1: a busca por arredondamento encontra o mesmo mínimo que a exaustiva,
    inclusive com covariância não diagonal."""
    rng = np.random.default_rng(3)
    for _ in range(20):
        f0 = rng.uniform(10, 20)
        orders = np.sort(rng.choice(np.arange(1, 9), size=4, replace=False))
        freqs = f0 * orders * (1 + rng.normal(0, 0.003, 4))
        Sigma = A.sigma_matrix(freqs, 0.05, common_lnf=0.005)
        Sigma[0, 1] = Sigma[1, 0] = Sigma[0, 1] + 1e-7
        t_r, h_r, _ = A.search(freqs, Sigma, N=10, delta_T=0.0)
        t_e, h_e, _ = A.search(freqs, Sigma, N=10, delta_T=0.0, exhaustive=True, monotone=False)
        assert t_r == pytest.approx(t_e)
        assert h_r[0][0] == h_e[0][0]


def test_detection_finds_harmonics_of_clean_signal():
    rng = np.random.default_rng(4)
    x, truth = G.harmonic(rng, duration=6.0, f0_start=15.0, profile="decrescente", f_gen_max=120)
    x, _ = G.add_noise(rng, x, 30.0, (5, 900))
    t, frames, df = D.detect(x)
    rec, false_peaks, n_true = D.match_truth(t, frames, truth, tol_hz=1.0)
    assert len(rec) / n_true > 0.8
    err = np.array([r[3] - r[2] for r in rec])
    assert np.median(np.abs(err)) < 0.2


def test_yin_tracks_fundamental_and_reports_signal_period_for_even_only():
    rng = np.random.default_rng(5)
    x, _ = G.harmonic(rng, duration=4.0, f0_start=15.0, profile="decrescente", f_gen_max=200)
    _, f, _ = F0.track(x)
    assert np.nanmedian(np.abs(np.log2(f / 15.0))) < 0.02
    x2, _ = G.harmonic(rng, duration=4.0, f0_start=15.0, profile="ausente_ambigua", f_gen_max=200)
    _, f2, _ = F0.track(x2)
    assert np.nanmedian(np.abs(np.log2(f2 / 30.0))) < 0.02


def test_null_comodulated_respects_exclusion_zone():
    rng = np.random.default_rng(6)
    for _ in range(10):
        _, tr = G.null_comodulated(rng, K=4, band=(10, 300), duration=1.0, eta=0.02)
        f = np.sort([fk[0] for fk in tr.freqs])
        assert not G._near_small_ratio(f, 6, 0.02)


def test_acceptance_rule_sizing():
    """Parecer da Luna: com 2.000 réplicas a regra aprova um teste calibrado só ~60% das vezes;
    6.000 réplicas levam essa probabilidade acima de 95%."""
    assert ST.pass_probability(2000) < 0.7
    assert ST.pass_probability(6000) >= 0.95
