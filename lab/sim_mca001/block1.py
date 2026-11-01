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
import math
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
                snr_high_db=None if math.isinf(upper) else upper,
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
                bias = float(np.median(errors))
                q_low = float(np.quantile(errors, QUANTILE_LOW, method="lower"))
                q_high = float(np.quantile(errors, QUANTILE_HIGH, method="higher"))
                q95_centered = float(np.quantile(
                    np.abs(errors - bias), 0.95, method="higher"
                ))
                entry.update(
                    bias_mediano_hz=bias,
                    q025_erro_hz=q_low,
                    q975_erro_hz=q_high,
                    q95_abs_erro_centrado_hz=q95_centered,
                    sigma_equivalente_hz=(q_high - q_low) / 3.92,
                    mediana_f_verdadeira_hz=float(np.median([row["f_true"] for row in selected])),
                    sigma_equivalente_log_f=(
                        (q_high - q_low) / 3.92
                    ) / max(float(np.median([row["f_true"] for row in selected])), 1e-12),
                    orçamento_precisão_hz=PRECISION_BUDGET_FACTOR / window_s,
                    passa_orcamento_precisao=(
                        q95_centered <= PRECISION_BUDGET_FACTOR / window_s
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
            return float(SNR_BINS_DB[candidate_bin])
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

        covered = (
            entry["q025_erro_hz"] <= row["error_hz"] <= entry["q975_erro_hz"]
        )
        per_signal[row["signal_id"]][0] += int(covered)
        per_signal[row["signal_id"]][1] += 1
        per_stratum[(bin_index, modulation)][0] += int(covered)
        per_stratum[(bin_index, modulation)][1] += 1

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
            cobertura=covered / total if total else None,
            n_componentes=total,
            cobertos=covered,
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


def identifiability_order(sigma_f_hz, f0, max_order=2000):
    """Diagnóstico estrutural; não transforma detecção em teto de N(t)."""
    for order in range(1, max_order + 1):
        sigma_log_f = sigma_f_hz / (order * f0)
        if np.log((order + 1) / order) <= 2.0 * sigma_log_f:
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
    window_summary = {}
    for threshold_db in DET_THRESHOLDS_DB:
        by_integrated_snr = {}
        for integrated_snr in GRID["snr"]:
            selected = [
                result["det"][window_s][threshold_db]
                for result in results
                if result["cell"]["snr"] == integrated_snr
            ]
            n_true = sum(item["n_true"] for item in selected)
            n_eligible = sum(item["n_eligible_true"] for item in selected)
            n_match = sum(item["n_match"] for item in selected)
            n_frames = sum(item["n_frames"] for item in selected)
            n_false = sum(item["n_false"] for item in selected)
            n_unresolved = sum(item["n_unresolved"] for item in selected)
            n_unresolved_peaks = sum(item["n_unresolved_peaks"] for item in selected)
            by_integrated_snr[str(integrated_snr)] = dict(
                taxa_deteccao_em_componentes_resolvidos=(
                    n_match / n_eligible if n_eligible else None
                ),
                falsos_picos_por_quadro=n_false / n_frames if n_frames else None,
                componentes_nao_resolvidos=n_unresolved,
                picos_associados_a_componentes_nao_resolvidos=n_unresolved_peaks,
                componentes_verdadeiros=n_true,
            )

        order_totals = defaultdict(lambda: [0, 0])
        for result in results:
            metrics = result["det"][window_s][threshold_db]
            for bucket, (precise, total) in metrics["order_counts"].items():
                order_totals[bucket][0] += precise
                order_totals[bucket][1] += total

        window_summary[str(threshold_db)] = dict(
            por_snr_integrada=by_integrated_snr,
            precisao_abs_erro_le_1_sobre_T_por_ordem={
                bucket: precise / total if total else None
                for bucket, (precise, total) in order_totals.items()
            },
        )
    return window_summary


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
    summary = {"por_particao": {"cal": {}, "ver": {}}}
    for partition in S.PARTITIONS:
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

        eligible_scales = [
            item["sigma_equivalente_hz"]
            for item in table
            if item["status"] == "ok"
            and min_snr is not None
            and item["snr_low_db"] >= min_snr
        ]
        sigma_reference = (
            float(np.median(eligible_scales)) if eligible_scales else None
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
            sigma_equivalente_referencia_hz=sigma_reference,
            ressalva="sigma equivalente é escala marginal derivada da largura do intervalo; "
                     "a tabela de quantis é o objeto primário",
        )
        summary["identificabilidade"][str(window_s)] = {
            f"f0={f0}|slope={slope}": (
                identifiability_order(sigma_reference, f0)
                if sigma_reference is not None else None
            )
            for f0 in GRID["f0"]
            for slope in GRID["slope"]
        }

    return summary


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
    args = parser.parse_args(argv)

    if args.reps < 1 or args.workers < 1:
        parser.error("--reps e --workers devem ser positivos")

    started = time.time()
    keys = list(GRID)
    cells = [dict(zip(keys, values)) for values in itertools.product(*GRID.values())]
    jobs = [
        (cell, partition, replicate)
        for cell in cells
        for partition in S.PARTITIONS
        for replicate in range(args.reps)
    ]

    with Pool(args.workers) as pool:
        results = pool.map(run_one, jobs, chunksize=4)

    report = dict(
        bloco="B1",
        plano="SIM-MCA-001 v0.2 — runner revisado",
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
            "associação global um-a-um; porta max(1/T, |df/dt|*T/2, df_STFT/2), "
            "limitada a 45% da separação verdadeira mais próxima; não resolvidos separados"
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
        resultados=summarize(results),
        tempo_s=round(time.time() - started, 1),
    )

    body = json.dumps(report, ensure_ascii=False, indent=1, sort_keys=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(body)
    print(args.out, hashlib.sha256(body.encode()).hexdigest(), f"{report['tempo_s']} s")


if __name__ == "__main__":
    sys.exit(main())
