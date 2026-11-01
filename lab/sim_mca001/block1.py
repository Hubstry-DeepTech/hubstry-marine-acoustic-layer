"""Bloco 1 — detecção, incerteza empírica e estimador independente da fundamental.

O pareamento de verdade é um-a-um e usa portas de localização limitadas pela
resolução STFT e pela excursão de frequência na janela. Picos não pareados são
contabilizados como falsos; componentes sem separação suficiente são não resolvidos.

A incerteza é calibrada por quantis empíricos do erro dos componentes verdadeiros
pareados, em estratos de SNR local e modulação. Um limiar mínimo de SNR é derivado
somente da partição cal e verificado em ver. Não se assume uma distribuição gaussiana.

Uso:
  python -m lab.sim_mca001.block1 --reps 6 --workers 2 \
      --out lab/sim_mca001/results/block1_piloto_v2.json

Rótulo: EXPLORATORY/FEASIBILITY. Nenhum dado real é lido.
"""
import argparse
import hashlib
import itertools
import json
import platform
import sys
import time
from collections import defaultdict
from multiprocessing import Pool

import numpy as np
import scipy
from scipy import signal as sps

from . import detection as D
from . import fundamental as F0
from . import generator as G
from . import seeds as S

BAND = (5.0, 900.0)
DUR = 10.0
GRID = dict(
    profile=["decrescente", "h3_dominante", "ausente_identificavel", "ausente_ambigua"],
    f0=[12.0, 18.0],
    slope=[0.0, -0.05],
    snr=[-5.0, 0.0, 5.0, 10.0, 20.0],
    alpha=[0.0, 1.0],
)
WINDOWS = [0.5, 1.0, 2.0]
YIN_THRESHOLDS = [0.1, 0.2, 0.3]
DET_THRESHOLDS_DB = [6.0, 10.0, 15.0]
F0_PREFILTER = (5.0, 250.0)
TOL_LOG2_F0 = 0.05

# Faixas fixadas antes da verificação. A primeira começa no limiar mínimo do detector.
SNR_BINS = [(6.0, 10.0), (10.0, 15.0), (15.0, 20.0), (20.0, None)]
MODULATION_SPLIT_OCT_S = 0.01
MIN_CAL_RECORDS_PER_STRATUM = 200
MIN_CAL_SIGNALS_PER_STRATUM = 50
QUANTILE_LOW = 0.025
QUANTILE_HIGH = 0.975
PRECISION_BUDGET_FACTOR = 1.0
AMBIGUOUS_LABEL = "subarmonica_compativel_nao_identificavel"
IDENTIFIABLE_PROFILES = ("decrescente", "h3_dominante", "ausente_identificavel")


def scenario_name(cell):
    return "p={profile}|f0={f0}|s={slope}|snr={snr}|a={alpha}".format(**cell)


def classify_f0(estimate, f0_true, profile):
    """Classifica a saída sem transformar a ambiguidade física em erro do estimador."""
    if not np.isfinite(estimate):
        return "indisponivel"

    ratio = np.log2(estimate / f0_true)
    if profile == "ausente_ambigua":
        if abs(ratio - 1.0) < TOL_LOG2_F0:
            return "periodo_sinal_2f0"
        if abs(ratio) < TOL_LOG2_F0:
            return AMBIGUOUS_LABEL
        return "outro"

    if abs(ratio) < TOL_LOG2_F0:
        return "acerto"
    for factor, label in ((2, "oitava"), (3, "fator_3"), (4, "fator_4")):
        if abs(ratio - np.log2(factor)) < TOL_LOG2_F0:
            return f"erro_{label}_acima"
        if abs(ratio + np.log2(factor)) < TOL_LOG2_F0:
            return f"erro_{label}_abaixo"
    return "erro_outro"


def _modulation_class(slope_oct_s):
    return "plano" if abs(slope_oct_s) < MODULATION_SPLIT_OCT_S else "modulado"


def _snr_bin(snr_db):
    for index, (lower, upper) in enumerate(SNR_BINS):
        if lower <= snr_db and (upper is None or snr_db < upper):
            return index
    return None


def run_one(args):
    cell, partition, replicate = args
    name = scenario_name(cell)
    rng = S.rng("B1", name, partition, replicate)

    signal, truth = G.harmonic(
        rng,
        duration=DUR,
        f0_start=cell["f0"],
        slope=cell["slope"],
        profile=cell["profile"],
    )
    noisy, _ = G.add_noise(rng, signal, cell["snr"], BAND, alpha=cell["alpha"])
    # Controle de associação acidental: ruído puro, com a mesma escala do ruído do sinal e
    # semente própria, pareado contra a mesma verdade (auditoria do Gemini, achado 1).
    rng_noise = S.rng("B1-ruido", name, partition, replicate)
    noise_only = G.add_noise(rng_noise, signal, cell["snr"], BAND, alpha=cell["alpha"])[0] - signal

    signal_id = f"{name}|{partition}|{replicate}"
    out = dict(
        cell=cell,
        partition=partition,
        rep=replicate,
        signal_id=signal_id,
        det={},
        f0={},
    )

    for window_s in WINDOWS:
        params = D.StftParams(
            win_s=window_s,
            hop_s=0.5,
            threshold_db=min(DET_THRESHOLDS_DB),
        )
        t_frames, frames, df = D.detect(noisy, params)
        _, noise_frames, _ = D.detect(noise_only, params)
        out["det"][window_s] = {}

        for threshold_db in DET_THRESHOLDS_DB:
            min_snr_linear = 10 ** (threshold_db / 10)
            selected_frames = [
                [peak for peak in frame if peak[2] >= min_snr_linear]
                for frame in frames
            ]
            (
                records,
                n_false,
                n_true,
                n_missed,
                n_unresolved,
                n_unresolved_peaks,
            ) = D.match_truth(
                t_frames,
                selected_frames,
                truth,
                win_s=window_s,
                df_hz=df,
            )

            noise_selected = [
                [peak for peak in frame if peak[2] >= min_snr_linear]
                for frame in noise_frames
            ]
            noise_match = D.match_truth(t_frames, noise_selected, truth,
                                        win_s=window_s, df_hz=df)

            precision_count = 0
            order_counts = defaultdict(lambda: [0, 0])
            rows = []
            for frame_index, component_index, f_true, f_est, snr_linear in records:
                sample_index = min(
                    int(round(t_frames[frame_index] * G.FS)),
                    truth.t.size - 1,
                )
                track = np.asarray(truth.freqs[component_index])
                fdot = float(np.gradient(track, truth.t)[sample_index])
                modulation = fdot / (f_true * np.log(2.0))
                snr_db = 10.0 * np.log10(max(snr_linear, 1e-12))
                error_hz = f_est - f_true
                is_precise = abs(error_hz) <= 1.0 / window_s
                precision_count += int(is_precise)

                order = int(truth.orders[component_index])
                bucket = (
                    "1-5" if 1 <= order <= 5 else
                    "6-10" if 6 <= order <= 10 else
                    "11-20" if 11 <= order <= 20 else
                    "21-40" if 21 <= order <= 40 else
                    "41-80" if 41 <= order <= 80 else
                    "other"
                )
                order_counts[bucket][0] += int(is_precise)
                order_counts[bucket][1] += 1

                # Tupla compacta para reduzir memória no piloto e nas rodadas maiores:
                # frame, ordem, f_true, f_est, SNR_local_dB, df/dt, inclinação em oitavas/s.
                rows.append((
                    int(frame_index),
                    order,
                    float(f_true),
                    float(f_est),
                    float(snr_db),
                    float(fdot),
                    float(modulation),
                ))

            n_frames = len(selected_frames)
            eligible_true = max(0, n_true - n_unresolved)
            out["det"][window_s][threshold_db] = dict(
                n_true=n_true,
                n_eligible_true=eligible_true,
                n_match=len(records),
                n_missed=n_missed,
                n_unresolved=n_unresolved,
                n_false=n_false,
                n_unresolved_peaks=n_unresolved_peaks,
                n_precise=precision_count,
                n_match_ruido_puro=len(noise_match[0]),
                n_elegiveis_ruido_puro=max(0, noise_match[2] - noise_match[4]),
                n_picos_ruido_puro=sum(len(f) for f in noise_selected),
                n_frames=n_frames,
                order_counts=dict(order_counts),
                # Somente o conjunto com o menor limiar alimenta a calibração empírica.
                rows=rows if threshold_db == min(DET_THRESHOLDS_DB) else [],
            )

    # Estimador da fundamental avaliado em quadros de 0,5 s. O YIN first fica
    # apenas como comparador histórico; a seleção de limiar usa exclusivamente cal.
    filtered = F0.prefilter(noisy, F0_PREFILTER)
    frame_times, f0_frames = F0.frames(filtered, 0.5, 0.5)
    true_f0 = np.asarray([
        truth.f0[min(int(round(tc * G.FS)), truth.t.size - 1)]
        for tc in frame_times
    ])

    f0_results = {}
    for mode in ("first", "best"):
        for threshold in YIN_THRESHOLDS:
            estimates = [
                F0.yin(frame, threshold=threshold, mode=mode)[0]
                for frame in f0_frames
            ]
            f0_results[f"yin_{mode}_{threshold}"] = [
                classify_f0(value, reference, cell["profile"])
                for value, reference in zip(estimates, true_f0)
            ]

    cepstrum = [F0.cepstrum(frame, min_prominence=0.0) for frame in f0_frames]
    f0_results["cep_raw"] = [
        (float(estimate), float(prominence),
         classify_f0(estimate, reference, cell["profile"]))
        for (estimate, prominence), reference in zip(cepstrum, true_f0)
    ]
    out["f0"] = f0_results
    return out


def fit_empirical_uncertainty_table(rows, window_s):
    """Tabela de intervalos empíricos centrais de 95%, por SNR e modulação."""
    table = []
    for bin_index, (lower, upper) in enumerate(SNR_BINS):
        for modulation_class in ("plano", "modulado"):
            selected = [
                row for row in rows
                if _snr_bin(row["snr_db"]) == bin_index
                and _modulation_class(row["modulation_oct_s"]) == modulation_class
            ]
            errors = np.asarray([row["error_hz"] for row in selected], dtype=float)
            n_signals = len({row["signal_id"] for row in selected})
            entry = dict(
                snr_bin=bin_index,
                snr_low_db=lower,
                snr_high_db=upper,
                modulation=modulation_class,
                n=int(errors.size),
                n_sinais=n_signals,
                min_n=MIN_CAL_RECORDS_PER_STRATUM,
                min_sinais=MIN_CAL_SIGNALS_PER_STRATUM,
                status=(
                    "ok"
                    if errors.size >= MIN_CAL_RECORDS_PER_STRATUM
                    and n_signals >= MIN_CAL_SIGNALS_PER_STRATUM
                    else "amostra_insuficiente"
                ),
            )
            if errors.size >= MIN_CAL_RECORDS_PER_STRATUM:
                bias_hz = float(np.median(errors))
                q_low_hz = float(np.quantile(errors, QUANTILE_LOW, method="lower"))
                q_high_hz = float(np.quantile(errors, QUANTILE_HIGH, method="higher"))
                q95_centered_hz = float(np.quantile(
                    np.abs(errors - bias_hz), 0.95, method="higher"
                ))

                log_errors = np.asarray([
                    np.log(row["f_est"] / row["f_true"])
                    for row in selected
                    if row["f_est"] > 0 and row["f_true"] > 0
                ], dtype=float)
                bias_log_f = float(np.median(log_errors))
                q_low_log_f = float(np.quantile(
                    log_errors, QUANTILE_LOW, method="lower"
                ))
                q_high_log_f = float(np.quantile(
                    log_errors, QUANTILE_HIGH, method="higher"
                ))
                q95_centered_log_f = float(np.quantile(
                    np.abs(log_errors - bias_log_f), 0.95, method="higher"
                ))

                entry.update(
                    bias_mediano_hz=bias_hz,
                    q025_erro_hz=q_low_hz,
                    q975_erro_hz=q_high_hz,
                    q95_abs_erro_centrado_hz=q95_centered_hz,
                    bias_mediano_log_f=bias_log_f,
                    q025_erro_log_f=q_low_log_f,
                    q975_erro_log_f=q_high_log_f,
                    q95_abs_erro_centrado_log_f=q95_centered_log_f,
                    mediana_f_verdadeira_hz=float(np.median([
                        row["f_true"] for row in selected
                    ])),
                    orçamento_precisão_hz=PRECISION_BUDGET_FACTOR / window_s,
                    passa_orcamento_precisao=(
                        q95_centered_hz <= PRECISION_BUDGET_FACTOR / window_s
                    ),
                )
            table.append(entry)
    return table


def select_min_snr(table):
    """Escolhe em cal o menor SNR cujo estrato e todos os superiores são suportados e passam."""
    by_key = {
        (entry["snr_bin"], entry["modulation"]): entry
        for entry in table
    }
    n_bins = len(SNR_BINS)

    for candidate_bin in range(n_bins):
        tail_passes = True
        for bin_index in range(candidate_bin, n_bins):
            for modulation in ("plano", "modulado"):
                entry = by_key[(bin_index, modulation)]
                if (
                    entry["status"] != "ok"
                    or not entry.get("passa_orcamento_precisao", False)
                ):
                    tail_passes = False
                    break
            if not tail_passes:
                break
        if tail_passes:
            return float(SNR_BINS[candidate_bin][0])
    return None


def _cluster_bootstrap_interval(signal_coverages, seed, repetitions=1000):
    """IC bootstrap por sinal, preservando a dependência entre quadros/componentes."""
    values = np.asarray(list(signal_coverages.values()), dtype=float)
    if values.size < 2:
        return None
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(repetitions, values.size))
    means = values[indices].mean(axis=1)
    return [
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
    ]


def verify_empirical_uncertainty(rows, table, min_snr_db, window_s):
    """Verifica a tabela em sinais independentes; não trata quadros como independentes."""
    if min_snr_db is None:
        return dict(status="sem_limiar_snr_calibrado", n_sinais=0)

    by_key = {
        (entry["snr_bin"], entry["modulation"]): entry
        for entry in table
    }
    per_signal = defaultdict(lambda: [0, 0])
    per_stratum = defaultdict(lambda: [0, 0])
    per_stratum_hz = defaultdict(lambda: [0, 0])
    n_skipped = 0

    for row in rows:
        if row["snr_db"] < min_snr_db:
            continue
        bin_index = _snr_bin(row["snr_db"])
        modulation = _modulation_class(row["modulation_oct_s"])
        entry = by_key.get((bin_index, modulation))
        if entry is None or entry["status"] != "ok":
            n_skipped += 1
            continue

        log_error = float(np.log(row["f_est"] / row["f_true"]))
        covered_log = (
            entry["q025_erro_log_f"] <= log_error <= entry["q975_erro_log_f"]
        )
        covered_hz = (
            entry["q025_erro_hz"] <= row["error_hz"] <= entry["q975_erro_hz"]
        )
        per_signal[row["signal_id"]][0] += int(covered_log)
        per_signal[row["signal_id"]][1] += 1
        per_stratum[(bin_index, modulation)][0] += int(covered_log)
        per_stratum[(bin_index, modulation)][1] += 1
        per_stratum_hz[(bin_index, modulation)][0] += int(covered_hz)
        per_stratum_hz[(bin_index, modulation)][1] += 1

    signal_coverages = {
        signal_id: covered / total
        for signal_id, (covered, total) in per_signal.items()
        if total
    }
    if signal_coverages:
        observed = float(np.mean(list(signal_coverages.values())))
        seed = S.seed_int("B1", f"uncertainty-bootstrap-{window_s}", "ver", 0)
        ci = _cluster_bootstrap_interval(signal_coverages, seed)
    else:
        observed, ci = None, None

    strata = {
        f"{bin_index}:{modulation}": dict(
            cobertura_log_f=covered / total if total else None,
            cobertura_hz=(
                per_stratum_hz[(bin_index, modulation)][0]
                / per_stratum_hz[(bin_index, modulation)][1]
                if per_stratum_hz[(bin_index, modulation)][1] else None
            ),
            n_componentes=total,
            cobertos_log_f=covered,
        )
        for (bin_index, modulation), (covered, total) in per_stratum.items()
    }
    return dict(
        status="verificacao_descritiva_independente",
        unidade_ic="sinal sintético; bootstrap em clusters de sinal",
        n_sinais=len(signal_coverages),
        n_componentes=sum(v[1] for v in per_stratum.values()),
        n_pulados_sem_estrato_calibrado=n_skipped,
        cobertura_media_por_sinal=observed,
        ic_bootstrap_95_por_sinal=ci,
        estratos=strata,
    )



def estimate_pairwise_covariance(rows, min_snr_db):
    """Estima covariância cruzada em log-f entre componentes do mesmo quadro.

    As medianas por ordem removem vieses fixos antes dos produtos cruzados.
    A estrutura operacional candidata é diag(sigma_k^2) + c^2 11^T, PSD por
    construção. Os produtos por par são preservados como diagnóstico; qualquer
    matriz completa deve ser reavaliada/regularizada antes do Bloco 2.
    """
    selected = [row for row in rows if min_snr_db is not None and row["snr_db"] >= min_snr_db]
    if not selected:
        return dict(status="sem_dados_acima_do_limiar")

    errors_by_order = defaultdict(list)
    for row in selected:
        if row["f_true"] > 0 and row["f_est"] > 0:
            errors_by_order[row["order"]].append(float(np.log(row["f_est"] / row["f_true"])))

    bias_by_order = {
        order: float(np.median(values))
        for order, values in errors_by_order.items()
    }
    groups = defaultdict(dict)
    for row in selected:
        if row["f_true"] <= 0 or row["f_est"] <= 0:
            continue
        key = (row["signal_id"], row["frame"])
        order = int(row["order"])
        residual = float(np.log(row["f_est"] / row["f_true"])) - bias_by_order[order]
        groups[key][order] = residual

    products = defaultdict(list)
    for values in groups.values():
        orders = sorted(values)
        if len(orders) < 2:
            continue
        for i, order_i in enumerate(orders[:-1]):
            for order_j in orders[i + 1:]:
                products[(order_i, order_j)].append(values[order_i] * values[order_j])

    pair_rows = []
    for (order_i, order_j), observations in sorted(products.items()):
        if len(observations) >= 50:
            pair_rows.append(dict(
                order_i=order_i,
                order_j=order_j,
                covariance_log_f=float(np.mean(observations)),
                n_pairs=len(observations),
            ))

    if not pair_rows:
        return dict(
            status="amostra_insuficiente_para_covariancia_cruzada",
            n_sinais=len({row["signal_id"] for row in selected}),
            n_quadros_com_multiplos_componentes=sum(
                len(values) >= 2 for values in groups.values()
            ),
            pares=[],
        )

    median_covariance = float(np.median([
        row["covariance_log_f"] for row in pair_rows
    ]))
    common_variance = max(0.0, median_covariance)
    return dict(
        status="diagnostico_calibrado_em_cal",
        estrutura_candidata="diag(sigma_k^2) + c^2 * 11T",
        sigma_common_log_f=float(np.sqrt(common_variance)),
        variancia_common_log_f=float(common_variance),
        n_sinais=len({row["signal_id"] for row in selected}),
        n_quadros_com_multiplos_componentes=sum(
            len(values) >= 2 for values in groups.values()
        ),
        pares=pair_rows,
        ressalva=(
            "os produtos por par são diagnósticos; confirmar a estrutura, "
            "a positividade e a cobertura em ver antes do Bloco 2"
        ),
    )


def identifiability_order(q95_abs_log_f, max_order=2000):
    """Diagnóstico estrutural conservador: separação > 2 × raio empírico q95 em ln(f).

    Não pressupõe normalidade e não transforma detectabilidade em teto de N(t).
    """
    if q95_abs_log_f is None or not np.isfinite(q95_abs_log_f) or q95_abs_log_f < 0:
        return None
    for order in range(1, max_order + 1):
        if np.log((order + 1) / order) <= 2.0 * q95_abs_log_f:
            return order - 1
    return f">={max_order}"


def _rows_from_results(results, window_s, partition):
    rows = []
    for result in results:
        if result["partition"] != partition:
            continue
        metrics = result["det"][window_s][min(DET_THRESHOLDS_DB)]
        for frame, order, f_true, f_est, snr_db, fdot, modulation in metrics["rows"]:
            rows.append(dict(
                signal_id=result["signal_id"],
                frame=frame,
                order=order,
                f_true=f_true,
                f_est=f_est,
                error_hz=f_est - f_true,
                snr_db=snr_db,
                fdot_hz_s=fdot,
                modulation_oct_s=modulation,
            ))
    return rows


def _summarize_detection(results, window_s):
    """Resumo da detecção separado por partição (auditoria do Gemini, achado 3).

    Taxas reportadas sobre o total de componentes e sobre os resolvidos, lado a lado
    (achado 2), e taxa de associação acidental medida com ruído puro (achado 1)."""
    out = {}
    for partition in sorted({r["partition"] for r in results}):
        part = [r for r in results if r["partition"] == partition]
        window_summary = {}
        for threshold_db in DET_THRESHOLDS_DB:
            by_integrated_snr = {}
            for integrated_snr in GRID["snr"]:
                sel = [r["det"][window_s][threshold_db] for r in part
                       if r["cell"]["snr"] == integrated_snr]
                tot = lambda key: sum(item[key] for item in sel)
                n_true, n_elig, n_match = tot("n_true"), tot("n_eligible_true"), tot("n_match")
                n_frames = tot("n_frames")
                by_integrated_snr[str(integrated_snr)] = dict(
                    taxa_deteccao_sobre_total=n_match / n_true if n_true else None,
                    taxa_deteccao_sobre_resolvidos=n_match / n_elig if n_elig else None,
                    fracao_nao_resolvidos=tot("n_unresolved") / n_true if n_true else None,
                    taxa_precisa_sobre_total=tot("n_precise") / n_true if n_true else None,
                    falsos_picos_por_quadro=tot("n_false") / n_frames if n_frames else None,
                    picos_absorvidos_por_nao_resolvidos=tot("n_unresolved_peaks"),
                    taxa_associacao_acidental_ruido_puro=(
                        tot("n_match_ruido_puro") / tot("n_elegiveis_ruido_puro")
                        if tot("n_elegiveis_ruido_puro") else None),
                    picos_por_quadro_ruido_puro=(
                        tot("n_picos_ruido_puro") / n_frames if n_frames else None),
                    ic95_associacao_acidental_por_sinal=_cluster_bootstrap_interval(
                        {i: item["n_match_ruido_puro"] / item["n_elegiveis_ruido_puro"]
                         for i, item in enumerate(sel) if item["n_elegiveis_ruido_puro"]},
                        S.seed_int("B1", f"ruido-{partition}-{window_s}-{threshold_db}-{integrated_snr}", "boot", 0)),
                    n_sinais=len(sel),
                    componentes_verdadeiros=n_true,
                )
            order_totals = defaultdict(lambda: [0, 0])
            for r in part:
                for bucket, (precise, total) in r["det"][window_s][threshold_db]["order_counts"].items():
                    order_totals[bucket][0] += precise
                    order_totals[bucket][1] += total
            window_summary[str(threshold_db)] = dict(
                por_snr_integrada=by_integrated_snr,
                precisao_abs_erro_le_1_sobre_T_por_ordem={
                    b: p / t if t else None for b, (p, t) in order_totals.items()},
            )
        out[partition] = window_summary
    return out


def select_yin_best_threshold(results):
    """Escolhe o limiar do YIN best apenas em cal; indisponíveis contam como não acerto."""
    candidates = []
    for threshold in YIN_THRESHOLDS:
        cell_scores = []
        cell_availability = []
        for profile in IDENTIFIABLE_PROFILES:
            for snr in (10.0, 20.0):
                selected = [
                    result for result in results
                    if result["partition"] == "cal"
                    and result["cell"]["profile"] == profile
                    and result["cell"]["snr"] == snr
                ]
                labels = [
                    label
                    for result in selected
                    for label in result["f0"][f"yin_best_{threshold}"]
                ]
                if not labels:
                    continue
                cell_scores.append(labels.count("acerto") / len(labels))
                cell_availability.append(
                    sum(label != "indisponivel" for label in labels) / len(labels)
                )
        score = float(np.mean(cell_scores)) if cell_scores else 0.0
        availability = float(np.mean(cell_availability)) if cell_availability else 0.0
        candidates.append(dict(
            threshold=threshold,
            score_acerto_por_quadro=score,
            disponibilidade_media=availability,
        ))

    # Critério de desempate: maior disponibilidade; depois, menor limiar.
    chosen = sorted(
        candidates,
        key=lambda item: (
            item["score_acerto_por_quadro"],
            item["disponibilidade_media"],
            -item["threshold"],
        ),
        reverse=True,
    )[0]
    return chosen["threshold"], candidates


def _summarize_fundamental(results, chosen_threshold):
    present = sorted({r["partition"] for r in results})
    summary = {"por_particao": {p: {} for p in present}}
    for partition in present:
        for profile in GRID["profile"]:
            by_snr = {}
            for snr in GRID["snr"]:
                selected = [
                    result for result in results
                    if result["partition"] == partition
                    and result["cell"]["profile"] == profile
                    and result["cell"]["snr"] == snr
                ]
                entry = {}
                for key in [
                    f"yin_{mode}_{threshold}"
                    for mode in ("first", "best")
                    for threshold in YIN_THRESHOLDS
                ]:
                    labels = [label for result in selected for label in result["f0"][key]]
                    entry[key] = {
                        label: labels.count(label) / len(labels)
                        for label in sorted(set(labels))
                    } if labels else {}

                for prominence in (2.0, 4.0, 6.0):
                    labels = [
                        label if prom >= prominence else "indisponivel"
                        for result in selected
                        for _, prom, label in result["f0"]["cep_raw"]
                    ]
                    entry[f"cepstro_{prominence}"] = {
                        label: labels.count(label) / len(labels)
                        for label in sorted(set(labels))
                    } if labels else {}

                by_snr[str(snr)] = entry
            summary["por_particao"][partition][profile] = by_snr

    summary["yin_best_threshold_escolhido_em_cal"] = chosen_threshold
    summary["criterio"] = (
        "maior proporção de acertos por quadro nos perfis identificáveis e SNR integrada "
        "de 10 e 20 dB; indisponibilidade conta como não acerto; verificação somente em ver"
    )
    summary["interpretacao_ausente_ambigua"] = (
        f"{AMBIGUOUS_LABEL} é compatível com subharmônica, mas não identificável no sinal; "
        "não é contabilizado como erro"
    )
    return summary


def summarize(results):
    summary = {
        "deteccao": {},
        "incerteza": {},
        "fundamental": {},
        "identificabilidade": {},
    }

    chosen_yin_threshold, yin_candidates = select_yin_best_threshold(results)
    summary["fundamental"] = _summarize_fundamental(results, chosen_yin_threshold)
    summary["fundamental"]["candidatos_yin_best_em_cal"] = yin_candidates

    for window_s in WINDOWS:
        summary["deteccao"][str(window_s)] = _summarize_detection(results, window_s)

        cal_rows = _rows_from_results(results, window_s, "cal")
        ver_rows = _rows_from_results(results, window_s, "ver")
        table = fit_empirical_uncertainty_table(cal_rows, window_s)
        min_snr = select_min_snr(table)
        verification = verify_empirical_uncertainty(
            ver_rows, table, min_snr, window_s
        )

        eligible_q95_log = [
            item["q95_abs_erro_centrado_log_f"]
            for item in table
            if item["status"] == "ok"
            and min_snr is not None
            and item["snr_low_db"] >= min_snr
        ]
        q95_log_reference = (
            float(max(eligible_q95_log)) if eligible_q95_log else None
        )
        covariance_cal = estimate_pairwise_covariance(cal_rows, min_snr)
        covariance_ver = estimate_pairwise_covariance(ver_rows, min_snr)
        summary["incerteza"][str(window_s)] = dict(
            metodo="quantis empíricos centrais de 95%, por SNR local e modulação",
            sem_hipotese_gaussiana=True,
            limiar_minimo_snr_local_db=min_snr,
            critério_do_limiar=(
                "menor bin em que todos os bins superiores, plano e modulado, "
                "têm pelo menos MIN_CAL_RECORDS_PER_STRATUM e q95 do erro centrado <= 1/T"
            ),
            minimo_registros_por_estrato=MIN_CAL_RECORDS_PER_STRATUM,
            minimo_sinais_independentes_por_estrato=MIN_CAL_SIGNALS_PER_STRATUM,
            tabela_calibracao_cal=table,
            verificacao_ver=verification,
            covariancia_cruzada_cal=covariance_cal,
            diagnostico_covariancia_ver=covariance_ver,
            raio_q95_log_f_referencia=q95_log_reference,
            ressalva=(
                "quantis empíricos em ln(f) são a incerteza primária; não há conversão "
                "por fator normal para sigma. A tabela em Hz é mantida para o orçamento "
                "de precisão do detector."
            ),
        )
        summary["identificabilidade"][str(window_s)] = {
            f"f0={f0}|slope={slope}": (
                identifiability_order(q95_log_reference)
                if q95_log_reference is not None else None
            )
            for f0 in GRID["f0"]
            for slope in GRID["slope"]
        }

    return summary


FREEZE_SCHEMA = "SIM-MCA-001/B1/congelamento/v2"
CODE_FILES = ("block1.py", "detection.py", "fundamental.py", "generator.py", "seeds.py",
              "assignment.py", "stats.py")


def code_fingerprint():
    """SHA-256 de cada arquivo de código do laboratório que influencia a rodada."""
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    out = {}
    for name in CODE_FILES:
        with open(os.path.join(base, name), "rb") as fh:
            out[name] = hashlib.sha256(fh.read()).hexdigest()
    return out


def run_config():
    """Configuração completa da simulação, para registro no congelamento."""
    return dict(grade=GRID, janelas_s=WINDOWS, limiares_deteccao_db=DET_THRESHOLDS_DB,
                yin_limiares=YIN_THRESHOLDS, banda_hz=BAND, duracao_s=DUR,
                prefiltro_f0_hz=F0_PREFILTER, faixas_snr_local_db=SNR_BINS,
                limiar_modulacao_oct_s=MODULATION_SPLIT_OCT_S,
                quantis=(QUANTILE_LOW, QUANTILE_HIGH),
                orcamento_precisao_fator=PRECISION_BUDGET_FACTOR,
                min_registros_estrato=MIN_CAL_RECORDS_PER_STRATUM,
                min_sinais_estrato=MIN_CAL_SIGNALS_PER_STRATUM,
                tol_log2_f0=TOL_LOG2_F0, max_gate_fraction=0.45,
                meia_largura_lobulo_principal_bins=D.MAINLOBE_HALF_WIDTH_BINS)


def build_freeze(summary, window_s, det_threshold_db, decided_by, notes="", provenance=None):
    """Artefato de congelamento das regras do Bloco 1, produzido só a partir de cal.

    Registra o que a validação final (partição val) vai aplicar sem reajuste: janela,
    limiar de detecção, tabela de incerteza e SNR mínima calibradas em cal, limiar do YIN
    escolhido em cal, tolerância da fundamental e regra de pareamento. O hash SHA-256 do
    conteúdo é gravado junto (parecer da Luna sobre 434ca29).

    Proveniência (parecer da Luna sobre 05f2b07): commit de origem, SHA-256 do arquivo de
    resultados exploratórios, impressão digital do código e configuração completa. O hash
    interno só detecta alteração sem recálculo; a autenticação vem de versionar o artefato
    e o seu checksum num commit próprio, antes da rodada val."""
    if float(det_threshold_db) not in DET_THRESHOLDS_DB or float(window_s) not in WINDOWS:
        raise ValueError("janela e limiar de detecção precisam estar na grade simulada")
    unc = summary["incerteza"][str(window_s)]
    if unc["limiar_minimo_snr_local_db"] is None:
        raise ValueError("sem SNR mínima calibrada em cal para esta janela")
    body = dict(
        esquema=FREEZE_SCHEMA,
        janela_s=float(window_s),
        limiar_deteccao_db=float(det_threshold_db),
        limiar_minimo_snr_local_db=unc["limiar_minimo_snr_local_db"],
        tabela_incerteza_cal=unc["tabela_calibracao_cal"],
        yin_best_limiar=summary["fundamental"]["yin_best_threshold_escolhido_em_cal"],
        tol_log2_f0=TOL_LOG2_F0,
        regra_pareamento="porta max(2/T, |df/dt|*T/2, df_STFT/2); um-a-um; um pico por não resolvido",
        decidido_por=decided_by,
        notas=notes,
        proveniencia=dict(provenance or {}),
        codigo_sha256=code_fingerprint(),
        configuracao=run_config(),
    )
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return dict(body, sha256=digest)


def check_freeze(freeze):
    body = {k: v for k, v in freeze.items() if k != "sha256"}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if freeze.get("esquema") != FREEZE_SCHEMA or digest != freeze.get("sha256"):
        raise ValueError("congelamento inválido ou alterado depois de gerado")


def evaluate_frozen(results, freeze):
    """Validação final: aplica as regras congeladas aos sinais da partição val, sem recalibrar.

    Recusa qualquer resultado de cal ou ver. Nada é ajustado: a tabela de incerteza, a SNR
    mínima e o limiar do YIN vêm do artefato. A cobertura é a cobertura condicional aos
    componentes pareados e resolvidos dentro da porta (ver criterio_pareamento)."""
    check_freeze(freeze)
    parts = {r["partition"] for r in results}
    if parts != {"val"}:
        raise ValueError(f"a avaliação congelada aceita só a partição val; recebeu {sorted(parts)}")
    w = freeze["janela_s"]
    val_rows = _rows_from_results(results, w, "val")
    # População avaliada = saída do detector com o limiar congelado E controle de qualidade de
    # cal: SNR local ≥ max(SNR mínima de cal, limiar de detecção) (parecer da Luna, 05f2b07).
    effective_snr = max(float(freeze["limiar_minimo_snr_local_db"]),
                        float(freeze["limiar_deteccao_db"]))
    coverage = verify_empirical_uncertainty(
        val_rows, freeze["tabela_incerteza_cal"], effective_snr, w)
    code_now = code_fingerprint()
    detection = _summarize_detection(results, w)["val"][str(freeze["limiar_deteccao_db"])]
    fundamental = _summarize_fundamental(results, freeze["yin_best_limiar"])["por_particao"]["val"]
    key = f"yin_best_{freeze['yin_best_limiar']}"
    fundamental = {prof: {snr: entry.get(key, {}) for snr, entry in by_snr.items()}
                   for prof, by_snr in fundamental.items()}
    return dict(
        congelamento_sha256=freeze["sha256"],
        janela_s=w,
        snr_local_efetivo_db=effective_snr,
        populacao_avaliada=(f"componentes pareados e resolvidos com SNR local ≥ {effective_snr} dB, "
                            "isto é, aceitos pelo detector com o limiar congelado e pelo controle de "
                            "qualidade de cal"),
        codigo_igual_ao_congelado=(code_now == freeze.get("codigo_sha256")),
        arquivos_de_codigo_alterados=sorted(k for k in code_now
                                            if code_now[k] != freeze.get("codigo_sha256", {}).get(k)),
        cobertura_incerteza_val=coverage,
        deteccao_val=detection,
        fundamental_val_yin_congelado=fundamental,
        interpretacao=("quantis e cobertura condicionais a componentes pareados e resolvidos dentro "
                       "da porta de associação; não são erro irrestrito de todos os componentes"),
    )


def f_max_check():
    """Ganho da cadeia de decimação simulada (16 kHz → 2 kHz)."""
    rng = S.rng("B1", "fmax", "cal", 0)
    x = rng.normal(size=int(60 * 16000))
    y = G.decimation_chain(x, 8)
    f_in, p_in = sps.welch(x, fs=16000, nperseg=8192)
    f_out, p_out = sps.welch(y, fs=2000, nperseg=1024)
    gain_db = 10 * np.log10(p_out / np.interp(f_out, f_in, p_in))
    reference = np.median(gain_db[(f_out > 20) & (f_out < 500)])
    flat = np.abs(gain_db - reference) <= 0.5
    first_bad = f_out[(~flat) & (f_out > 20)]
    f_max = float(first_bad.min()) if first_bad.size else float(f_out[flat].max())
    return dict(
        criterio="primeira frequência acima de 20 Hz com ganho fora de ±0,5 dB da mediana 20–500 Hz",
        f_max_hz=f_max,
        ganho_ref_db=float(reference),
        nota="filtro FIR do scipy, não o filtro do MBARI; valida o procedimento, não o valor real",
    )


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=6,
                        help="réplicas por célula e por partição cal/ver")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--out", required=True)
    parser.add_argument("--particoes", nargs="+", default=list(S.EXPLORATORY_PARTITIONS),
                        choices=list(S.PARTITIONS),
                        help="'val' só na validação final, depois de congeladas as regras")
    parser.add_argument("--congelamento",
                        help="arquivo de congelamento; obrigatório com val, que roda sozinha")
    args = parser.parse_args(argv)
    if "val" in args.particoes and (args.particoes != ["val"] or not args.congelamento):
        parser.error("val roda sozinha e exige --congelamento (regras fixadas antes, só em cal)")

    if args.reps < 1 or args.workers < 1:
        parser.error("--reps e --workers devem ser positivos")

    started = time.time()
    keys = list(GRID)
    cells = [dict(zip(keys, values)) for values in itertools.product(*GRID.values())]
    jobs = [
        (cell, partition, replicate)
        for cell in cells
        for partition in args.particoes
        for replicate in range(args.reps)
    ]

    with Pool(args.workers) as pool:
        results = pool.map(run_one, jobs, chunksize=4)

    report = dict(
        bloco="B1",
        plano="SIM-MCA-001 v0.3.2 — runner revisado após a auditoria do Gemini",
        particoes=args.particoes,
        rotulo="EXPLORATORY/FEASIBILITY",
        tipo="piloto" if args.reps <= 6 else "rodada exploratória",
        grade=GRID,
        janelas_stft_s=WINDOWS,
        yin_limiares=YIN_THRESHOLDS,
        tol_log2_f0=TOL_LOG2_F0,
        limiares_deteccao_db=DET_THRESHOLDS_DB,
        prefiltro_f0_hz=F0_PREFILTER,
        faixas_snr_local_db=[dict(min_db=lo, max_db=hi) for lo, hi in SNR_BINS],
        limiar_modulacao_oct_s=MODULATION_SPLIT_OCT_S,
        replicas_por_celula_e_particao=args.reps,
        n_sinais=len(jobs),
        criterio_pareamento=(
            "regra de avaliação sintética baseada na verdade; não integra a cadeia de detecção aplicada a sinais reais. "
            "associação global um-a-um sobre todos os componentes; porta max(2/T, |df/dt|*T/2, df_STFT/2), "
            "independente do orçamento de precisão 1/T; componente não resolvido absorve no máximo um pico, "
            "com porta limitada a 45% da separação; associação acidental medida com ruído puro. "
            "Quantis e cobertura são condicionais a componentes pareados e resolvidos dentro da porta; "
            "2/T vai até o primeiro zero do lóbulo principal da Hann e não exclui energia de lóbulos laterais"
        ),
        metodo_incerteza=(
            "quantis empíricos centrais de 95% por SNR local e classe de modulação; "
            "SNR mínimo selecionado somente em cal e verificado somente em ver"
        ),
        selecao_fundamental=(
            "YIN best; limiar selecionado somente em cal nos perfis identificáveis; "
            "YIN first mantido apenas como comparador"
        ),
        versoes=dict(
            python=platform.python_version(),
            numpy=np.__version__,
            scipy=scipy.__version__,
        ),
        f_max=f_max_check(),
        resultados=(evaluate_frozen(results, json.load(open(args.congelamento, encoding="utf-8")))
                    if args.particoes == ["val"] else summarize(results)),
        tempo_s=round(time.time() - started, 1),
    )

    body = json.dumps(report, ensure_ascii=False, indent=1, sort_keys=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(body)
    print(args.out, hashlib.sha256(body.encode()).hexdigest(), f"{report['tempo_s']} s")


if __name__ == "__main__":
    sys.exit(main())
