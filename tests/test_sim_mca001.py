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
    assert tmin < 1e-6  # zero numérico: M tem entradas da ordem de (f/σ)²
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


def test_exact_search_matches_exhaustive_including_poor_fits():
    """Decisão D1, após o contraexemplo da Luna: a busca exata (ramificação e poda) encontra o
    mesmo mínimo e o mesmo conjunto H* que a busca exaustiva sobre atribuições crescentes,
    inclusive em ajustes ruins (nulos) e com covariância não diagonal."""
    rng = np.random.default_rng(0)
    for _ in range(150):
        K = int(rng.integers(2, 6))
        freqs = np.sort(np.exp(rng.uniform(np.log(10), np.log(150), K)))
        sigma = A.sigma_matrix(freqs, rng.uniform(0.01, 0.5, K), common_lnf=rng.uniform(0, 0.01))
        b = rng.normal(size=(K, K)) * 1e-5
        sigma = sigma + b @ b.T
        delta_t = float(rng.choice([0.0, 1.0, 5.0]))
        t_x, h_x, _ = A.search(freqs, sigma, N=10, delta_T=delta_t)
        t_e, h_e, _ = A.search(freqs, sigma, N=10, delta_T=delta_t, exhaustive=True)
        assert t_x == pytest.approx(t_e, rel=1e-9, abs=1e-9)
        assert {h for h, _, _ in h_x} == {h for h, _, _ in h_e}


def test_rounding_heuristic_is_not_complete():
    """Registro do contraexemplo: a heurística por arredondamento perde o mínimo global em
    ajustes ruins. Ela não pode ser usada para H* nem para a distribuição nula."""
    rng = np.random.default_rng(0)
    misses = 0
    for _ in range(200):
        K = int(rng.integers(3, 6))
        freqs = np.sort(np.exp(rng.uniform(np.log(10), np.log(150), K)))
        sigma = A.sigma_matrix(freqs, rng.uniform(0.01, 0.5, K))
        t_r, _, _ = A.search(freqs, sigma, N=12, delta_T=0.0, method="rounding")
        t_e, _, _ = A.search(freqs, sigma, N=12, delta_T=0.0, exhaustive=True)
        if not (np.isfinite(t_r) and np.isclose(t_r, t_e)):
            misses += 1
    assert misses > 0


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
    # Auditoria do Gemini: um componente não resolvido absorve no máximo um pico, e a porta
    # absorvente fica limitada a 45% da separação. Em t = 1 s os componentes estão em 22 e
    # 24 Hz: 21,5 Hz é absorvido pelo de 22 Hz; 20,5 Hz fica fora da porta e é falso.
    assert records == []
    assert n_true == 2
    assert unresolved == 2
    assert unresolved_peaks == 1
    assert false == 1
    assert len(records) + missed + unresolved == n_true
    assert len(records) + unresolved_peaks + false == len(frames[0])


def test_empirical_uncertainty_uses_snr_and_modulation_strata():
    rows = []
    rng = np.random.default_rng(42)
    for bin_index, (lower, upper) in enumerate(B1.SNR_BINS):
        snr = lower + 0.5 if upper is not None else lower + 5.0
        for modulation in (0.0, 0.05):
            scale = 3.0 if bin_index == 0 else 0.1
            for index in range(250):
                error = float(rng.normal(0.0, scale))
                rows.append(dict(
                    signal_id=f"sig-{bin_index}-{modulation}-{index}",
                    f_true=25.0,
                    f_est=25.0 + error,
                    snr_db=snr,
                    modulation_oct_s=modulation,
                    error_hz=error,
                ))
    table = B1.fit_empirical_uncertainty_table(rows, window_s=0.5)
    assert all(entry["status"] == "ok" for entry in table)
    assert all("q025_erro_log_f" in entry for entry in table)
    assert all("q95_abs_erro_centrado_log_f" in entry for entry in table)
    assert B1.select_min_snr(table) == 10.0
    assert B1.identifiability_order(0.00001) == ">=2000"
    assert B1.identifiability_order(0.2) == 2


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


def test_udu_reconstructs_M_and_rejects_degenerate_intermediate_pivot():
    """Parecer da Luna: a fatoração UᵀDU precisa reproduzir M e falhar, em vez de zerar em
    silêncio, se um pivô intermediário for não positivo."""
    rng = np.random.default_rng(7)
    for _ in range(30):
        K = int(rng.integers(2, 8))
        freqs = np.sort(np.exp(rng.uniform(np.log(10), np.log(500), K)))
        M = A._residual_form(A.sigma_matrix(freqs, rng.uniform(0.01, 1.0, K), common_lnf=0.003))
        d, U = A._udu(M)
        assert np.all(d[:-1] > 0) and d[-1] == 0.0
        assert np.allclose(U.T @ np.diag(d) @ U, M, rtol=0, atol=1e-8 * np.abs(np.diag(M)).max())
    bad = np.array([[1.0, 1.0, -2.0], [1.0, 1.0, -2.0], [-2.0, -2.0, 4.0]])  # 2º pivô nulo
    with pytest.raises(np.linalg.LinAlgError):
        A._udu(bad)


def test_verify_d1_batteries_small():
    """Versão reduzida das baterias de verify_d1.py (a completa fica em results/verify_d1.json)."""
    from lab.sim_mca001 import verify_d1 as V
    for cases in (V.general_cases(n=100, seed=11), V.ill_conditioned_cases(n=30, seed=12)):
        r = V.battery("teste", cases)
        assert r["falhas_fatoracao"] == 0
        assert r["minimo_igual"] == r["n"] and r["hstar_igual"] == r["n"]


# Testes propostos pela auditoria do Gemini 4 Argon (Antigravity), adaptados.

def test_g3_null_keeps_exclusion_zone_and_common_modulation():
    rng = np.random.default_rng(101)
    for _ in range(20):
        _, truth = G.null_comodulated(rng, K=6, band=(20.0, 600.0), duration=4.0, slope=-0.04,
                                      n_excl=6, eta=0.015)
        f_init = np.sort([fk[0] for fk in truth.freqs])
        assert not G._near_small_ratio(f_init, 6, 0.015)
        ratios = np.array([fk[-1] / fk[0] for fk in truth.freqs])
        assert np.allclose(ratios, ratios[0], rtol=1e-12)


def test_add_noise_respects_integrated_inband_snr():
    rng = np.random.default_rng(102)
    sig, _ = G.harmonic(rng, duration=6.0, f0_start=16.0, f_gen_max=400.0)
    band = (5.0, 900.0)
    for snr_db in (-5.0, 0.0, 10.0, 20.0):
        for alpha in (0.0, 1.0):
            noisy, _ = G.add_noise(rng, sig, snr_db, band, alpha=alpha)
            measured = 10 * np.log10(G.band_energy(sig, band) / G.band_energy(noisy - sig, band))
            assert measured == pytest.approx(snr_db, abs=1e-9)


def test_yin_best_recovers_f0_with_dominant_third_and_missing_fundamental():
    rng = np.random.default_rng(103)
    for profile in ("h3_dominante", "ausente_identificavel"):
        sig, _ = G.harmonic(rng, duration=2.0, f0_start=15.0, profile=profile, f_gen_max=250.0)
        frame = F0.prefilter(sig)[int(0.5 * G.FS): int(1.5 * G.FS)]
        f0_est, conf = F0.yin(frame, threshold=0.2, mode="best")
        assert np.isfinite(f0_est) and conf > 0.8
        assert abs(np.log2(f0_est / 15.0)) < 0.05


def test_udu_rejects_matrix_without_ones_in_kernel():
    with pytest.raises(np.linalg.LinAlgError):
        A._udu(np.eye(4))


def test_exact_search_near_harmonic_with_ill_conditioned_sigma():
    """Caso apontado pelo Gemini: T_min ≈ 0 com Σ muito mal condicionada."""
    from lab.sim_mca001 import verify_d1 as V
    rng = np.random.default_rng(104)
    for _ in range(30):
        K = 5
        f0 = rng.uniform(12.0, 25.0)
        orders = np.sort(rng.choice(np.arange(1, 15), size=K, replace=False))
        freqs = f0 * orders * (1.0 + rng.normal(0.0, 1e-4, size=K))
        sd = np.array([1e-4, 1e-4, 1e-1, 5e-1, 1.0]) / freqs
        C = rng.uniform(-1.0, 1.0, size=(K, K))
        R = C @ C.T + 0.02 * np.eye(K)
        d = np.sqrt(np.diag(R))
        sigma = np.outer(sd, sd) * (R / np.outer(d, d))
        tx, hx, _ = A.exact_search(freqs, sigma, N=20, delta_T=0.5)
        te, he = V.exhaustive_vectorized(freqs, sigma, N=20, delta_T=0.5)
        assert tx == pytest.approx(te, rel=1e-7, abs=1e-6)
        assert {h for h, _ in hx} == he


def test_match_truth_accounting_identities_on_random_frames():
    """Identidades da contabilidade: cada componente e cada pico têm exatamente um destino."""
    from lab.sim_mca001.generator import Truth
    rng = np.random.default_rng(106)
    t = np.arange(8000) / G.FS
    for _ in range(50):
        K = int(rng.integers(1, 6))
        base = np.sort(rng.uniform(10, 200, K))
        slopes = rng.uniform(-5, 5, K)
        truth = Truth(t=t, freqs=[b + s * t for b, s in zip(base, slopes)], amps=[1.0] * K,
                      orders=list(range(1, K + 1)), f0=np.full(t.size, base[0]))
        times = np.array([1.0, 2.0, 3.0])
        frames = [[(float(f), 1.0, 20.0) for f in rng.uniform(5, 220, rng.integers(0, 8))]
                  for _ in times]
        rec, false, n_true, missed, unres, unres_peaks = D.match_truth(
            times, frames, truth, win_s=1.0, df_hz=0.25)
        assert len(rec) + missed + unres == n_true
        assert len(rec) + unres_peaks + false == sum(len(f) for f in frames)
        assert unres_peaks <= unres


def test_calibration_outputs_do_not_depend_on_ver_partition():
    """Nada escolhido a partir de cal muda quando a partição ver muda."""
    from lab.sim_mca001 import block1 as B1
    cell = dict(profile="decrescente", f0=12.0, slope=0.0, snr=10.0, alpha=0.0)
    cal = B1.run_one((cell, "cal", 0))
    s_a = B1.summarize([cal, B1.run_one((cell, "ver", 0))])
    s_b = B1.summarize([cal, B1.run_one((cell, "ver", 1))])
    assert (s_a["fundamental"]["yin_best_threshold_escolhido_em_cal"]
            == s_b["fundamental"]["yin_best_threshold_escolhido_em_cal"])
    for w in B1.WINDOWS:
        assert (s_a["incerteza"][str(w)]["tabela_calibracao_cal"]
                == s_b["incerteza"][str(w)]["tabela_calibracao_cal"])
        assert (s_a["deteccao"][str(w)]["cal"] == s_b["deteccao"][str(w)]["cal"])


def test_val_partition_is_not_run_by_default():
    from lab.sim_mca001 import block1 as B1  # noqa: F401
    assert S.EXPLORATORY_PARTITIONS == ("cal", "ver")
    assert "val" in S.PARTITIONS


def test_val_partition_evaluates_frozen_rules_without_refitting(monkeypatch):
    """Parecer da Luna sobre 434ca29: val aplica regras congeladas em cal, sem recalibrar."""
    from lab.sim_mca001 import block1 as B1
    # amostra mínima reduzida só para o teste caber em segundos
    monkeypatch.setattr(B1, "MIN_CAL_RECORDS_PER_STRATUM", 5)
    monkeypatch.setattr(B1, "MIN_CAL_SIGNALS_PER_STRATUM", 1)
    cell = dict(profile="decrescente", f0=12.0, slope=0.0, snr=20.0, alpha=0.0)
    cell_mod = dict(cell, slope=-0.05)  # a calibração exige estratos plano e modulado
    cal = [B1.run_one((c, "cal", 0)) for c in (cell, cell_mod)]
    summary = B1.summarize(cal)
    window = next(w for w in B1.WINDOWS
                  if summary["incerteza"][str(w)]["limiar_minimo_snr_local_db"] is not None)
    freeze = B1.build_freeze(summary, window, 10.0, decided_by="teste")
    val = [B1.run_one((cell, "val", 0))]
    out = B1.evaluate_frozen(val, freeze)
    assert out["congelamento_sha256"] == freeze["sha256"]
    cov = out["cobertura_incerteza_val"]
    assert cov["status"] == "verificacao_descritiva_independente" and cov["n_componentes"] > 0
    assert out["deteccao_val"]["por_snr_integrada"]["20.0"]["componentes_verdadeiros"] > 0
    # população alinhada ao detector: SNR efetiva = max(SNR mínima de cal, limiar de detecção)
    assert out["snr_local_efetivo_db"] == max(freeze["limiar_minimo_snr_local_db"], 10.0)
    assert out["codigo_igual_ao_congelado"] is True
    hi = B1.build_freeze(summary, window, 15.0, decided_by="teste")
    out_hi = B1.evaluate_frozen(val, hi)
    assert out_hi["snr_local_efetivo_db"] == max(freeze["limiar_minimo_snr_local_db"], 15.0)
    with pytest.raises(ValueError):
        B1.build_freeze(summary, window, 20.0, decided_by="teste")  # fora da grade
    assert out_hi["cobertura_incerteza_val"]["n_componentes"] <= cov["n_componentes"]
    # proveniência registrada
    assert set(freeze["codigo_sha256"]) == set(B1.CODE_FILES) and "grade" in freeze["configuracao"]
    # sem recalibração: o mesmo congelamento com outra réplica val não altera a regra aplicada
    out2 = B1.evaluate_frozen([B1.run_one((cell, "val", 1))], freeze)
    assert out2["congelamento_sha256"] == out["congelamento_sha256"]
    # val não aceita mistura com cal/ver, e congelamento adulterado é recusado
    with pytest.raises(ValueError):
        B1.evaluate_frozen(val + cal[:1], freeze)
    bad = dict(freeze, limiar_minimo_snr_local_db=0.0)
    with pytest.raises(ValueError):
        B1.evaluate_frozen(val, bad)


def test_val_cli_requires_freeze_and_runs_alone():
    from lab.sim_mca001 import block1 as B1
    with pytest.raises(SystemExit):
        B1.main(["--out", "/tmp/x.json", "--particoes", "val"])
    with pytest.raises(SystemExit):
        B1.main(["--out", "/tmp/x.json", "--particoes", "cal", "val", "--congelamento", "f.json"])


def test_noise_only_control_counts_and_summary():
    """Controle de associação acidental: contagens coerentes e taxa agregada no resumo."""
    from lab.sim_mca001 import block1 as B1
    cell = dict(profile="decrescente", f0=12.0, slope=0.0, snr=10.0, alpha=0.0)
    res = B1.run_one((cell, "cal", 0))
    for w in B1.WINDOWS:
        for thr in B1.DET_THRESHOLDS_DB:
            d = res["det"][w][thr]
            assert 0 <= d["n_match_ruido_puro"] <= d["n_elegiveis_ruido_puro"] <= d["n_true"]
    lo = res["det"][1.0][min(B1.DET_THRESHOLDS_DB)]["n_match_ruido_puro"]
    hi = res["det"][1.0][max(B1.DET_THRESHOLDS_DB)]["n_match_ruido_puro"]
    assert hi <= lo  # limiar mais alto nunca aumenta associações acidentais
    entry = B1._summarize_detection([res], 1.0)["cal"]["10.0"]["por_snr_integrada"]["10.0"]
    assert 0.0 <= entry["taxa_associacao_acidental_ruido_puro"] <= 1.0


def test_search_returns_same_chi2_that_decided_hstar():
    rng = np.random.default_rng(9)
    freqs = 14.0 * np.array([2, 3, 5, 7.0]) * (1 + rng.normal(0, 1e-3, 4))
    sigma = A.sigma_matrix(freqs, 0.05, common_lnf=0.002)
    tmin, out, _ = A.search(freqs, sigma, N=20, delta_T=2.0)
    _, hx, _ = A.exact_search(freqs, sigma, N=20, delta_T=2.0)
    assert [(h, t) for h, _, t in out] == hx


def test_frozen_evaluation_uses_rows_paired_at_frozen_threshold(monkeypatch):
    """Revisão do GLM-5.3 sobre 45aa863: a população de val é a saída do detector no limiar
    congelado, com o pareamento refeito nesse limiar, e não um filtro dos pares de 6 dB."""
    from lab.sim_mca001 import block1 as B1
    monkeypatch.setattr(B1, "MIN_CAL_RECORDS_PER_STRATUM", 5)
    monkeypatch.setattr(B1, "MIN_CAL_SIGNALS_PER_STRATUM", 1)
    cell = dict(profile="decrescente", f0=12.0, slope=0.0, snr=20.0, alpha=0.0)
    val = [B1.run_one((cell, "val", 0))]
    for thr in B1.DET_THRESHOLDS_DB:
        rows = B1._rows_from_results(val, 1.0, "val", thr)
        assert rows and all(r["snr_db"] >= thr - 1e-9 for r in rows)
    cal = [B1.run_one((c, "cal", 0)) for c in (cell, dict(cell, slope=-0.05))]
    summary = B1.summarize(cal)
    w = next(w for w in B1.WINDOWS
             if summary["incerteza"][str(w)]["por_limiar_deteccao"]["15.0"]["limiar_minimo_snr_local_db"] is not None)
    freeze = B1.build_freeze(summary, w, 15.0, decided_by="teste")
    assert freeze["tabela_incerteza_cal"] == summary["incerteza"][str(w)]["por_limiar_deteccao"]["15.0"]["tabela_calibracao_cal"]
    out = B1.evaluate_frozen(val, freeze)
    expected = sum(1 for r in B1._rows_from_results(val, w, "val", 15.0)
                   if r["snr_db"] >= out["snr_local_efetivo_db"])
    assert out["cobertura_incerteza_val"]["n_componentes"] == expected


def test_frozen_evaluation_fails_closed_when_code_changed(monkeypatch):
    """Revisão da Luna sobre 2260df5: com código diferente do congelado, a validação é recusada."""
    from lab.sim_mca001 import block1 as B1
    monkeypatch.setattr(B1, "MIN_CAL_RECORDS_PER_STRATUM", 5)
    monkeypatch.setattr(B1, "MIN_CAL_SIGNALS_PER_STRATUM", 1)
    cell = dict(profile="decrescente", f0=12.0, slope=0.0, snr=20.0, alpha=0.0)
    cal = [B1.run_one((c, "cal", 0)) for c in (cell, dict(cell, slope=-0.05))]
    summary = B1.summarize(cal)
    w = next(w for w in B1.WINDOWS
             if summary["incerteza"][str(w)]["por_limiar_deteccao"]["10.0"]["limiar_minimo_snr_local_db"] is not None)
    freeze = B1.build_freeze(summary, w, 10.0, decided_by="teste")
    assert "congelar_b1.py" in freeze["codigo_sha256"]
    val = [B1.run_one((cell, "val", 0))]
    real = B1.code_fingerprint()
    monkeypatch.setattr(B1, "code_fingerprint", lambda: dict(real, **{"detection.py": "0" * 64}))
    with pytest.raises(ValueError, match="código diferente"):
        B1.evaluate_frozen(val, freeze)


def test_low_snr_false_peak_stops_stealing_pairing_at_higher_threshold():
    """Regressão do achado do GLM-5.3: um pico falso fraco, mais próximo do componente, ocupa o
    pareamento no limiar baixo; refeito no limiar alto, o pico verdadeiro é pareado."""
    from lab.sim_mca001.generator import Truth
    t = np.arange(4000) / G.FS
    truth = Truth(t=t, freqs=[np.full(t.size, 100.0)], amps=[1.0], orders=[1],
                  f0=np.full(t.size, 100.0))
    frame = [(100.1, 1.0, 10 ** (7 / 10)), (100.9, 1.0, 10 ** (20 / 10))]  # falso a 7 dB, verdadeiro a 20 dB
    for thr_db, expected_f in ((6.0, 100.1), (15.0, 100.9)):
        sel = [[p for p in frame if p[2] >= 10 ** (thr_db / 10)]]
        rec, false, n_true, missed, unres, unres_peaks = D.match_truth(
            np.array([1.0]), sel, truth, win_s=1.0, df_hz=0.25)
        assert len(rec) == 1 and rec[0][3] == pytest.approx(expected_f)
        assert false == len(sel[0]) - 1
