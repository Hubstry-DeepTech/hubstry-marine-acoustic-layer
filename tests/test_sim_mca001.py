"""Testes automáticos do plano SIM-MCA-001 (Seção 7)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab.sim_mca001 import assignment as A  # noqa: E402
from lab.sim_mca001 import block1 as B1  # noqa: E402
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
    f0 = 14.3
    freqs = f0 * np.array([1, 2, 3, 4, 5, 6])
    sigma = A.sigma_matrix(freqs, 0.05)
    tmin, hstar, _ = A.search(freqs, sigma, N=40, delta_T=1.0)
    assert hstar[0][0] == (1, 2, 3, 4, 5, 6)
    assert tmin < 1e-9
    assert np.isclose(np.exp(hstar[0][1]), f0)


def test_even_only_components_get_minimal_assignment():
    f0 = 15.0
    freqs = np.array([2 * f0, 4 * f0])
    tmin, hstar, _ = A.search(
        freqs, A.sigma_matrix(freqs, 0.05), N=40, delta_T=0.0
    )
    assert hstar[0][0] == (1, 2)
    assert np.isclose(np.exp(hstar[0][1]), 2 * f0)


def test_p_empirical_minimum_and_direction():
    assert ST.p_empirical(0.1, np.ones(999)) == pytest.approx(1 / 1000)
    assert ST.p_empirical(5.0, np.ones(999)) == pytest.approx(1.0)


def test_gls_with_diagonal_sigma_equals_wls():
    rng = np.random.default_rng(1)
    y = np.log(15 * np.array([1, 2, 3, 5.0])) + rng.normal(0, 0.01, 4)
    log_h = np.log([1, 2, 3, 5.0])
    scale = np.array([0.01, 0.02, 0.005, 0.03])
    log_g, _, _, chi2 = A.gls_fit(y, log_h, np.diag(scale ** 2))
    weights = 1 / scale ** 2
    log_g_wls = np.sum(weights * (y - log_h)) / np.sum(weights)
    assert log_g == pytest.approx(log_g_wls)
    assert chi2 == pytest.approx(np.sum(weights * (y - log_h - log_g_wls) ** 2))


def test_common_mode_covariance_does_not_change_chi2():
    rng = np.random.default_rng(2)
    freqs = 15 * np.array([1, 2, 3, 4.0]) * (1 + rng.normal(0, 0.002, 4))
    log_h = np.log([1, 2, 3, 4.0])
    y = np.log(freqs)
    _, v0, _, c0 = A.gls_fit(y, log_h, A.sigma_matrix(freqs, 0.05))
    _, v1, _, c1 = A.gls_fit(
        y, log_h, A.sigma_matrix(freqs, 0.05, common_lnf=0.01)
    )
    assert c1 == pytest.approx(c0)
    assert v1 > v0


def test_rounding_search_matches_exhaustive_on_small_case():
    rng = np.random.default_rng(3)
    for _ in range(20):
        f0 = rng.uniform(10, 20)
        orders = np.sort(rng.choice(np.arange(1, 9), size=4, replace=False))
        freqs = f0 * orders * (1 + rng.normal(0, 0.003, 4))
        sigma = A.sigma_matrix(freqs, 0.05, common_lnf=0.005)
        sigma[0, 1] = sigma[1, 0] = sigma[0, 1] + 1e-7
        t_round, h_round, _ = A.search(freqs, sigma, N=10, delta_T=0.0)
        t_exact, h_exact, _ = A.search(
            freqs, sigma, N=10, delta_T=0.0, exhaustive=True, monotone=False
        )
        assert t_round == pytest.approx(t_exact)
        assert h_round[0][0] == h_exact[0][0]


def test_detection_finds_harmonics_of_clean_signal():
    rng = np.random.default_rng(4)
    signal, truth = G.harmonic(
        rng, duration=6.0, f0_start=15.0, profile="decrescente", f_gen_max=120
    )
    noisy, _ = G.add_noise(rng, signal, 30.0, (5, 900))
    times, frames, df = D.detect(noisy)
    records, false, n_true, missed, unresolved, unresolved_peaks = D.match_truth(
        times, frames, truth, tol_hz=1.0
    )
    assert len(records) / n_true > 0.8
    assert false >= 0
    assert missed >= 0
    assert unresolved >= 0
    assert unresolved_peaks >= 0
    error = np.array([record[3] - record[2] for record in records])
    assert np.median(np.abs(error)) < 0.2


def test_match_truth_is_one_to_one_and_counts_duplicate_detection_as_false():
    from lab.sim_mca001.generator import Truth

    t = np.arange(2000) / G.FS
    truth = Truth(
        t=t,
        freqs=[np.full(t.size, 20.0)],
        amps=[1.0],
        orders=[1],
        f0=np.full(t.size, 20.0),
    )
    records, false, n_true, missed, unresolved, unresolved_peaks = D.match_truth(
        np.array([0.5]),
        [[(20.1, 1.0, 100.0), (20.2, 0.5, 20.0)]],
        truth,
        tol_hz=1.0,
    )
    assert len(records) == 1
    assert false == 1
    assert n_true == 1
    assert missed == 0
    assert unresolved == 0
    assert unresolved_peaks == 0


def test_match_truth_does_not_pair_a_distant_noise_peak():
    from lab.sim_mca001.generator import Truth

    t = np.arange(2000) / G.FS
    truth = Truth(
        t=t,
        freqs=[np.full(t.size, 20.0)],
        amps=[1.0],
        orders=[1],
        f0=np.full(t.size, 20.0),
    )
    records, false, n_true, missed, unresolved, unresolved_peaks = D.match_truth(
        np.array([0.5]), [[(25.0, 1.0, 10.0)]], truth, tol_hz=1.0
    )
    assert records == []
    assert false == 1
    assert n_true == 1
    assert missed == 1
    assert unresolved == 0
    assert unresolved_peaks == 0


def test_match_truth_flags_unresolved_nearby_chirped_components():
    from lab.sim_mca001.generator import Truth

    t = np.arange(4000) / G.FS
    truth = Truth(
        t=t,
        freqs=[20.0 + 2.0 * t, 22.0 + 2.0 * t],
        amps=[1.0, 1.0],
        orders=[1, 2],
        f0=np.full(t.size, 20.0),
    )
    times = np.array([1.0])
    frames = [[(20.5, 1.0, 20.0), (21.5, 1.0, 20.0)]]
    records, false, n_true, missed, unresolved, unresolved_peaks = D.match_truth(
        times, frames, truth, win_s=2.0, df_hz=0.125
    )
    assert records == []
    assert false == 0
    assert n_true == 2
    assert unresolved == 2
    assert unresolved_peaks == 2


def test_empirical_uncertainty_uses_snr_and_modulation_strata():
    rows = []
    rng = np.random.default_rng(42)
    for bin_index, (lower, upper) in enumerate(B1.SNR_BINS):
        snr = lower + 0.5 if upper is not None else lower + 5.0
        for modulation in (0.0, 0.05):
            scale = 3.0 if bin_index == 0 else 0.1
            for index in range(250):
                rows.append(dict(
                    signal_id=f"sig-{bin_index}-{modulation}-{index}",
                    f_true=25.0,
                    f_est=25.0 + float(rng.normal(0.0, scale)),
                    snr_db=snr,
                    modulation_oct_s=modulation,
                    error_hz=float(rng.normal(0.0, scale)),
                ))
    table = B1.fit_empirical_uncertainty_table(rows, window_s=0.5)
    assert all(entry["status"] == "ok" for entry in table)
    assert all("q025_erro_log_f" in entry for entry in table)
    assert all("q95_abs_erro_centrado_log_f" in entry for entry in table)
    assert B1.select_min_snr(table) == 10.0
    assert B1.identifiability_order(0.001) == ">=2000"
    assert B1.identifiability_order(0.2) == 1


def test_ambiguous_even_only_subharmonic_is_not_labelled_as_error():
    label = B1.classify_f0(15.0, 15.0, "ausente_ambigua")
    assert label == B1.AMBIGUOUS_LABEL


def test_yin_threshold_selection_uses_calibration_partition():
    # O conjunto ver tem desempenho deliberadamente invertido; não pode alterar a seleção.
    def fake_result(partition, threshold, label):
        return dict(
            partition=partition,
            cell=dict(profile="h3_dominante", snr=10.0),
            f0={f"yin_best_{threshold}": [label] * 10},
        )

    results = []
    for partition in ("cal", "ver"):
        result = dict(
            partition=partition,
            cell=dict(profile="h3_dominante", snr=10.0),
            f0={},
        )
        for threshold in B1.YIN_THRESHOLDS:
            label = "acerto" if (
                (partition == "cal" and threshold == 0.2)
                or (partition == "ver" and threshold == 0.3)
            ) else "erro_outro"
            result["f0"][f"yin_best_{threshold}"] = [label] * 10
        results.append(result)
    chosen, _ = B1.select_yin_best_threshold(results)
    assert chosen == 0.2


def test_acceptance_rule_sizing():
    assert ST.pass_probability(2000) < 0.7
    assert ST.pass_probability(6000) >= 0.95
