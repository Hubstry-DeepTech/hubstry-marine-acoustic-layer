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
MODULATION_SPLIT_OCT_S = 0.01  # só para ler o piloto v2 (diag_cobertura.py)
# Estratos de excursão de frequência na janela, em unidades de 1/T: e = |df/dt|·T².
# Substituem a classe binária plano/modulado (achado 4 da auditoria do Gemini): o erro em Hz
# depende da excursão do próprio componente, que cresce com a ordem sob modulação.
EXCURSION_EDGES_BINS = (0.5, 2.0)
EXCURSION_CLASSES = ("baixa", "media", "alta")
# Classes em que o orçamento de precisão 1/T é exigido na escolha da SNR mínima. Na classe
# "alta" (excursão >= 2/T) o erro é dominado pela própria modulação: os quantis são calibrados
# e usados, mas o orçamento 1/T não se aplica (proposta, aguarda a Luna).
BUDGET_CLASSES = ("baixa", "media")

# Critérios de aceite fixados pela Luna em 02/11/2026, antes da rodada final (SIM-MCA-001
# v0.3.5). São registrados no congelamento e aplicados sem ajuste depois de ver o resultado.
COVERAGE_CRITERIA = dict(
    nominal=0.95,
    limite_inferior_ic_media_por_sinal_min=0.93,
    cobertura_por_faixa_de_ordem_min=0.92,
    componentes_min_por_faixa=200,
)
MIN_CAL_RECORDS_PER_STRATUM = 200
MIN_CAL_SIGNALS_PER_STRATUM = 50
QUANTILE_LOW = 0.025
QUANTILE_HIGH = 0.975
PRECISION_BUDGET_FACTOR = 1.0
AMBIGUOUS_LABEL = "subarmonica_compativel_nao_identificavel"
IDENTIFIABLE_PROFILES = ("decrescente", "h3_dominante", "ausente_identificavel")
# Critério do estimador independente (Luna, 02/11/2026). O perfil "ausente_ambigua" não entra
# no denominador: lá a fundamental física não é identificável no sinal.
YIN_CRITERIA = dict(
    estimador="yin_best",
    p95_erro_relativo_abs_max=0.01,
    disponibilidade_min=0.994,
    snr_min_db=10.0,
    perfis=IDENTIFIABLE_PROFILES,
)


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
    """Classe binária do piloto v2; mantida só para reler aquele resultado."""
    return "plano" if abs(slope_oct_s) < MODULATION_SPLIT_OCT_S else "modulado"


def _excursion_class(fdot_hz_s, window_s):
    """Excursão de frequência do componente dentro da janela, em unidades de 1/T."""
    excursion = abs(float(fdot_hz_s)) * float(window_s) ** 2
    if excursion < EXCURSION_EDGES_BINS[0]:
        return "baixa"
    if excursion < EXCURSION_EDGES_BINS[1]:
        return "media"
    return "alta"


def log_interval_from_hz(f_est, q025_hz, q975_hz):
    """Intervalo do resíduo ln(f_est/f_true) obtido dos quantis do erro e = f_est − f_true.

    Parte da frequência estimada, porque a verdadeira é desconhecida em dados reais
    (parecer da Luna sobre o piloto v2): e ∈ [q025, q975] ⇔ f_true ∈ [f_est − q975,
    f_est − q025] ⇔ ln(f_est/f_true) ∈ [ln(f_est/(f_est − q025)), ln(f_est/(f_est − q975))].
    Devolve None quando f_est − q975 <= 0 (intervalo indefinido em ln f)."""
    lower_true = f_est - q975_hz
    upper_true = f_est - q025_hz
    if lower_true <= 0 or upper_true <= 0:
        return None
    return (float(np.log(f_est / upper_true)), float(np.log(f_est / lower_true)))


def _order_band(order):
    return "1-3" if order <= 3 else "4-10" if order <= 10 else "11-30" if order <= 30 else "31+"


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
                # registros guardados em todos os limiares: o pareamento é refeito em cada
                # limiar, então a população de cada um é a saída real do detector naquele
                # limiar (revisão do GLM-5.3 sobre 45aa863)
                rows=rows,
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
            if mode == "best":
                # estimativa e referência por quadro, para os critérios de erro relativo e
                # disponibilidade (None = indisponível)
                f0_results[f"yin_best_{threshold}_raw"] = [
                    [float(value) if np.isfinite(value) else None, float(reference)]
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
    """Tabela de intervalos empíricos centrais de 95% do erro em Hz, por SNR local e excursão.

    A incerteza primária é o erro e = f_est − f_true em Hz, cuja escala é aproximadamente
    constante entre ordens (diagnóstico do piloto v2). O intervalo em ln f de cada componente
    sai de log_interval_from_hz, a partir de f_est, sem hipótese gaussiana."""
    table = []
    for bin_index, (lower, upper) in enumerate(SNR_BINS):
        for excursion_class in EXCURSION_CLASSES:
            selected = [
                row for row in rows
                if _snr_bin(row["snr_db"]) == bin_index
                and _excursion_class(row["fdot_hz_s"], window_s) == excursion_class
            ]
            errors = np.asarray([row["error_hz"] for row in selected], dtype=float)
            n_signals = len({row["signal_id"] for row in selected})
            entry = dict(
                snr_bin=bin_index,
                snr_low_db=lower,
                snr_high_db=upper,
                excursao=excursion_class,
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
                q95_centered_hz = float(np.quantile(
                    np.abs(errors - bias_hz), 0.95, method="higher"
                ))
                budget_hz = PRECISION_BUDGET_FACTOR / window_s
                entry.update(
                    bias_mediano_hz=bias_hz,
                    q025_erro_hz=float(np.quantile(errors, QUANTILE_LOW, method="lower")),
                    q975_erro_hz=float(np.quantile(errors, QUANTILE_HIGH, method="higher")),
                    q95_abs_erro_centrado_hz=q95_centered_hz,
                    orcamento_precisao_hz=budget_hz,
                    orcamento_exigido=excursion_class in BUDGET_CLASSES,
                    passa_orcamento_precisao=q95_centered_hz <= budget_hz,
                )
            table.append(entry)
    return table


def _usable(entry):
    return entry is not None and entry["status"] == "ok"


def select_min_snr(table):
    """Escolhe em cal o menor bin de SNR a partir do qual, em todos os bins superiores, as
    classes de excursão com orçamento exigido têm amostra suficiente e q95 centrado <= 1/T.

    A classe "alta" não entra no critério; seus componentes só são usados nos estratos com
    amostra suficiente (e excluídos, com contagem, nos demais)."""
    by_key = {(entry["snr_bin"], entry["excursao"]): entry for entry in table}
    n_bins = len(SNR_BINS)
    for candidate_bin in range(n_bins):
        tail_passes = all(
            _usable(by_key.get((bin_index, excursion)))
            and by_key[(bin_index, excursion)].get("passa_orcamento_precisao", False)
            for bin_index in range(candidate_bin, n_bins)
            for excursion in BUDGET_CLASSES
        )
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


def verify_empirical_uncertainty(rows, table, min_snr_db, window_s, partition="ver"):
    """Verifica a tabela em sinais independentes; não trata quadros como independentes.

    A cobertura é medida em Hz e, para cada componente, também no intervalo em ln f obtido
    de f_est (log_interval_from_hz). As duas coincidem quando o intervalo em ln f é definido;
    a discordância é contada como verificação da transformação. A cobertura é reportada
    por sinal (unidade do IC), por faixa de ordem e por estrato."""
    if min_snr_db is None:
        return dict(status="sem_limiar_snr_calibrado", n_sinais=0)

    by_key = {(entry["snr_bin"], entry["excursao"]): entry for entry in table}
    per_signal = defaultdict(lambda: [0, 0])
    per_stratum = defaultdict(lambda: [0, 0])
    per_order = defaultdict(lambda: [0, 0])
    per_excursion = defaultdict(lambda: [0, 0])
    skipped = defaultdict(int)
    undefined_log = 0
    log_disagreement = 0

    for row in rows:
        if row["snr_db"] < min_snr_db:
            continue
        key = (_snr_bin(row["snr_db"]), _excursion_class(row["fdot_hz_s"], window_s))
        entry = by_key.get(key)
        if not _usable(entry):
            skipped[key[1]] += 1
            continue
        covered = entry["q025_erro_hz"] <= row["error_hz"] <= entry["q975_erro_hz"]
        interval = log_interval_from_hz(row["f_est"], entry["q025_erro_hz"], entry["q975_erro_hz"])
        if interval is None:
            undefined_log += 1
        else:
            residual = float(np.log(row["f_est"] / row["f_true"]))
            if (interval[0] <= residual <= interval[1]) != covered:
                log_disagreement += 1
        for bucket, k in ((per_signal, row["signal_id"]), (per_stratum, key),
                          (per_order, _order_band(int(row["order"]))),
                          (per_excursion, key[1])):
            bucket[k][0] += int(covered)
            bucket[k][1] += 1

    signal_coverages = {
        signal_id: covered / total
        for signal_id, (covered, total) in per_signal.items()
        if total
    }
    if signal_coverages:
        observed = float(np.mean(list(signal_coverages.values())))
        seed = S.seed_int("B1", f"uncertainty-bootstrap-{window_s}", partition, 0)
        ci = _cluster_bootstrap_interval(signal_coverages, seed)
    else:
        observed, ci = None, None

    return dict(
        status="verificacao_descritiva_independente",
        unidade_ic="sinal sintético; bootstrap em clusters de sinal",
        n_sinais=len(signal_coverages),
        n_componentes=sum(v[1] for v in per_stratum.values()),
        n_pulados_sem_estrato_calibrado=int(sum(skipped.values())),
        pulados_por_excursao=dict(skipped),
        intervalo_log_f_indefinido=undefined_log,
        discordancias_hz_log_f=log_disagreement,
        cobertura_media_por_sinal=observed,
        ic_bootstrap_95_por_sinal=ci,
        cobertura_por_faixa_de_ordem={
            band: dict(cobertura=c / n, n_componentes=n)
            for band, (c, n) in sorted(per_order.items())
        },
        # cada classe de excursão tem cobertura medida e reportada; a classe sem nenhum
        # estrato calibrado acima da SNR mínima fica registrada como não avaliável
        cobertura_por_excursao={
            klass: (
                dict(status="avaliada", cobertura=per_excursion[klass][0] / per_excursion[klass][1],
                     n_componentes=per_excursion[klass][1], pulados=skipped.get(klass, 0))
                if per_excursion[klass][1]
                else dict(status="nao_avaliavel", n_componentes=0, pulados=skipped.get(klass, 0))
            )
            for klass in EXCURSION_CLASSES
        },
        estratos={
            f"{b}:{e}": dict(cobertura_hz=c / n if n else None, n_componentes=n, cobertos=c)
            for (b, e), (c, n) in sorted(per_stratum.items())
        },
    )


def evaluate_coverage_criterion(verification, criteria=None):
    """Aplica o critério de cobertura fixado antes da rodada final, sem ajuste posterior.

    Aprovado só se o limite inferior do IC bootstrap (reamostragem de sinais inteiros) da
    cobertura média por sinal e a cobertura de cada faixa de ordem avaliável atingem os
    mínimos. Faixas com menos componentes que o mínimo são registradas como não avaliáveis;
    se nenhuma faixa é avaliável, o resultado é não avaliável."""
    criteria = COVERAGE_CRITERIA if criteria is None else criteria
    ci = verification.get("ic_bootstrap_95_por_sinal")
    if verification.get("status") != "verificacao_descritiva_independente" or not ci:
        return dict(veredito="nao_avaliavel", motivo="sem verificação ou sem IC por sinal",
                    criterios=criteria)
    bands = {}
    for band, item in verification.get("cobertura_por_faixa_de_ordem", {}).items():
        if item["n_componentes"] < criteria["componentes_min_por_faixa"]:
            bands[band] = dict(item, status="nao_avaliavel")
        else:
            bands[band] = dict(item, status=(
                "aprovada" if item["cobertura"] >= criteria["cobertura_por_faixa_de_ordem_min"]
                else "reprovada"))
    evaluable = [b for b in bands.values() if b["status"] != "nao_avaliavel"]
    signal_ok = ci[0] >= criteria["limite_inferior_ic_media_por_sinal_min"]
    if not evaluable:
        verdict = "nao_avaliavel"
    elif signal_ok and all(b["status"] == "aprovada" for b in evaluable):
        verdict = "aprovado"
    else:
        verdict = "reprovado"
    return dict(
        veredito=verdict,
        limite_inferior_ic_media_por_sinal=ci[0],
        media_por_sinal_aprovada=signal_ok,
        faixas_de_ordem=bands,
        classes_de_excursao=verification.get("cobertura_por_excursao"),
        criterios=criteria,
    )


def evaluate_yin_criterion(results, threshold, partition, criteria=None):
    """Aplica o critério do YIN best fixado antes da rodada final.

    Denominador: quadros dos perfis identificáveis com SNR integrada >= snr_min_db. O perfil
    "ausente_ambigua" fica fora, por não ter fundamental identificável. Erro: percentil 95 do
    erro relativo absoluto |f̂0/f0 − 1| entre as estimativas disponíveis. Disponibilidade:
    fração de quadros com estimativa."""
    criteria = YIN_CRITERIA if criteria is None else criteria
    key = f"yin_best_{threshold}_raw"
    by_cell = defaultdict(lambda: [0, []])
    for result in results:
        cell = result["cell"]
        if (result["partition"] != partition or cell["profile"] not in criteria["perfis"]
                or cell["snr"] < criteria["snr_min_db"]):
            continue
        bucket = by_cell[(cell["profile"], cell["snr"])]
        for estimate, reference in result["f0"][key]:
            bucket[0] += 1
            if estimate is not None:
                bucket[1].append(abs(estimate / reference - 1.0))
    total = sum(v[0] for v in by_cell.values())
    errors = [e for v in by_cell.values() for e in v[1]]
    if total == 0:
        return dict(veredito="nao_avaliavel", motivo="sem quadros elegíveis", criterios=criteria)
    availability = len(errors) / total
    p95 = float(np.quantile(errors, 0.95, method="higher")) if errors else None
    ok = (p95 is not None and p95 <= criteria["p95_erro_relativo_abs_max"]
          and availability >= criteria["disponibilidade_min"])
    return dict(
        veredito="aprovado" if ok else "reprovado",
        limiar=threshold,
        particao=partition,
        n_quadros=total,
        disponibilidade=availability,
        p95_erro_relativo_abs=p95,
        por_perfil_e_snr={
            f"{profile}|{snr}": dict(
                n_quadros=n,
                disponibilidade=len(errs) / n if n else None,
                p95_erro_relativo_abs=(float(np.quantile(errs, 0.95, method="higher"))
                                       if errs else None),
            )
            for (profile, snr), (n, errs) in sorted(by_cell.items())
        },
        criterios=criteria,
        ressalva=("SNR do critério = SNR integrada da célula, porque a fundamental é estimada "
                  "no sinal inteiro do quadro; não demonstra a fundamental física do canto B"),
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
    """Critério antigo, com raio constante em ln f. Mantido só para reler o piloto v2:
    a condição exata, com intervalo em Hz, é identifiability_by_scenario."""
    if q95_abs_log_f is None or not np.isfinite(q95_abs_log_f) or q95_abs_log_f < 0:
        return None
    for order in range(1, max_order + 1):
        if np.log((order + 1) / order) <= 2.0 * q95_abs_log_f:
            return order - 1
    return f">={max_order}"


def identifiability_by_scenario(table, min_snr_db, window_s, f0_hz, slope_oct_s,
                                duration_s=None, f_max_hz=None):
    """Maior ordem n tal que os intervalos de componentes vizinhos não se sobrepõem até n.

    Com e = f_est − f_true ∈ [q025, q975], o componente k é observado em
    [k·f0 + q025_k, k·f0 + q975_k]. Os componentes n e n + 1 ficam separados quando
    f0 > q975_n − q025_{n+1} (parecer da Luna sobre o piloto v2; com quantis simétricos de
    raio r, vale f0 > 2r). Cada componente usa o estrato da sua excursão; como a SNR local de
    cada componente não é conhecida antes, usa-se o pior caso entre os bins de SNR elegíveis
    (>= min_snr_db, amostra suficiente): maior q975 para n e menor q025 para n + 1.
    Pior caso também no tempo: a separação usa a menor fundamental do sinal e a excursão,
    a maior. O teto é o limite de banda, ⌊f_max/f0_min⌋."""
    duration_s = DUR if duration_s is None else duration_s
    f_max_hz = BAND[1] if f_max_hz is None else f_max_hz
    if min_snr_db is None:
        return dict(status="sem_limiar_snr_calibrado")
    f0_end = f0_hz * 2.0 ** (slope_oct_s * duration_s)
    f0_min, f0_max = min(f0_hz, f0_end), max(f0_hz, f0_end)
    band_limit = int(np.floor(f_max_hz / f0_min))

    eligible = defaultdict(list)
    for entry in table:
        if _usable(entry) and entry["snr_low_db"] >= min_snr_db:
            eligible[entry["excursao"]].append(entry)

    def bounds(order):
        fdot = order * f0_max * abs(slope_oct_s) * np.log(2.0)
        entries = eligible.get(_excursion_class(fdot, window_s), [])
        if not entries:
            return None
        return (min(e["q025_erro_hz"] for e in entries), max(e["q975_erro_hz"] for e in entries))

    # ordem_identificavel = maior N tal que todos os pares vizinhos entre 1 e N estão separados
    worst_margin = None
    if bounds(1) is None:
        return dict(status="estrato_sem_calibracao", ordem_identificavel=0,
                    limite_de_banda=band_limit, f0_min_hz=f0_min)
    for order in range(1, band_limit):
        b_n, b_next = bounds(order), bounds(order + 1)
        if b_next is None:
            return dict(status="estrato_sem_calibracao", ordem_identificavel=order,
                        limite_de_banda=band_limit, f0_min_hz=f0_min,
                        menor_folga_hz=worst_margin)
        margin = f0_min - (b_n[1] - b_next[0])
        worst_margin = margin if worst_margin is None else min(worst_margin, margin)
        if margin <= 0:
            return dict(status="sobreposicao", ordem_identificavel=order,
                        limite_de_banda=band_limit, f0_min_hz=f0_min,
                        menor_folga_hz=worst_margin)
    return dict(status="identificavel_ate_o_limite_de_banda", ordem_identificavel=band_limit,
                limite_de_banda=band_limit, f0_min_hz=f0_min, menor_folga_hz=worst_margin)


def _rows_from_results(results, window_s, partition, threshold_db=None):
    rows = []
    for result in results:
        if result["partition"] != partition:
            continue
        metrics = result["det"][window_s][
            min(DET_THRESHOLDS_DB) if threshold_db is None else float(threshold_db)]
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
    if any(r["partition"] == "ver" for r in results):
        summary["fundamental"]["criterio_yin_ver_descritivo"] = evaluate_yin_criterion(
            results, chosen_yin_threshold, "ver")

    for window_s in WINDOWS:
        summary["deteccao"][str(window_s)] = _summarize_detection(results, window_s)

        cal_rows = _rows_from_results(results, window_s, "cal")
        ver_rows = _rows_from_results(results, window_s, "ver")
        table = fit_empirical_uncertainty_table(cal_rows, window_s)
        min_snr = select_min_snr(table)
        verification = verify_empirical_uncertainty(
            ver_rows, table, min_snr, window_s
        )
        # tabela e SNR mínima calibradas em cal para cada limiar de detecção, com o pareamento
        # feito naquele limiar; build_freeze usa a do limiar escolhido
        per_threshold = {}
        for thr in DET_THRESHOLDS_DB:
            t_thr = fit_empirical_uncertainty_table(
                _rows_from_results(results, window_s, "cal", thr), window_s)
            per_threshold[str(thr)] = dict(tabela_calibracao_cal=t_thr,
                                           limiar_minimo_snr_local_db=select_min_snr(t_thr))

        covariance_cal = estimate_pairwise_covariance(cal_rows, min_snr)
        covariance_ver = estimate_pairwise_covariance(ver_rows, min_snr)
        summary["incerteza"][str(window_s)] = dict(
            por_limiar_deteccao=per_threshold,
            metodo=("quantis empíricos centrais de 95% do erro em Hz, por SNR local e excursão "
                    "de frequência na janela; intervalo em ln f obtido de f_est"),
            sem_hipotese_gaussiana=True,
            limiar_minimo_snr_local_db=min_snr,
            critério_do_limiar=(
                "menor bin em que todos os bins superiores, nas classes de excursão baixa e média, "
                "têm pelo menos MIN_CAL_RECORDS_PER_STRATUM registros e MIN_CAL_SIGNALS_PER_STRATUM "
                "sinais e q95 do erro centrado <= 1/T; a classe alta é calibrada sem orçamento"
            ),
            bordas_excursao_em_1_sobre_T=EXCURSION_EDGES_BINS,
            minimo_registros_por_estrato=MIN_CAL_RECORDS_PER_STRATUM,
            minimo_sinais_independentes_por_estrato=MIN_CAL_SIGNALS_PER_STRATUM,
            tabela_calibracao_cal=table,
            verificacao_ver=verification,
            covariancia_cruzada_cal=covariance_cal,
            diagnostico_covariancia_ver=covariance_ver,
            ressalva=(
                "a covariância cruzada ainda é estimada em ln f com vieses por ordem; o alinhamento "
                "das escalas entre os quantis em Hz e a matriz Sigma é a validação seguinte"
            ),
        )
        summary["incerteza"][str(window_s)]["criterio_cobertura_ver_descritivo"] = (
            evaluate_coverage_criterion(verification))
        summary["identificabilidade"][str(window_s)] = {
            f"f0={f0}|slope={slope}": identifiability_by_scenario(
                table, min_snr, window_s, f0, slope)
            for f0 in GRID["f0"]
            for slope in GRID["slope"]
        }

    return summary


FREEZE_SCHEMA = "SIM-MCA-001/B1/congelamento/v3"
CODE_FILES = ("block1.py", "detection.py", "fundamental.py", "generator.py", "seeds.py",
              "assignment.py", "stats.py", "congelar_b1.py")


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
                bordas_excursao_em_1_sobre_T=EXCURSION_EDGES_BINS,
                classes_com_orcamento=BUDGET_CLASSES,
                quantis=(QUANTILE_LOW, QUANTILE_HIGH),
                orcamento_precisao_fator=PRECISION_BUDGET_FACTOR,
                min_registros_estrato=MIN_CAL_RECORDS_PER_STRATUM,
                min_sinais_estrato=MIN_CAL_SIGNALS_PER_STRATUM,
                tol_log2_f0=TOL_LOG2_F0, max_gate_fraction=D.MAX_GATE_FRACTION,
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
    unc = summary["incerteza"][str(window_s)]["por_limiar_deteccao"][str(float(det_threshold_db))]
    if unc["limiar_minimo_snr_local_db"] is None:
        raise ValueError("sem SNR mínima calibrada em cal para esta janela e este limiar")
    body = dict(
        esquema=FREEZE_SCHEMA,
        janela_s=float(window_s),
        limiar_deteccao_db=float(det_threshold_db),
        limiar_minimo_snr_local_db=unc["limiar_minimo_snr_local_db"],
        tabela_incerteza_cal=unc["tabela_calibracao_cal"],
        yin_best_limiar=summary["fundamental"]["yin_best_threshold_escolhido_em_cal"],
        tol_log2_f0=TOL_LOG2_F0,
        criterios_aceite=dict(cobertura=COVERAGE_CRITERIA, yin=YIN_CRITERIA,
                              classes_de_excursao=dict(bordas_em_1_sobre_T=EXCURSION_EDGES_BINS,
                                                       classes_com_orcamento=BUDGET_CLASSES),
                              fixados_por="Luna, 02/11/2026, antes da rodada final"),
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
    val_rows = _rows_from_results(results, w, "val", freeze["limiar_deteccao_db"])
    # População avaliada = saída do detector com o limiar congelado E controle de qualidade de
    # cal: SNR local ≥ max(SNR mínima de cal, limiar de detecção) (parecer da Luna, 05f2b07).
    effective_snr = max(float(freeze["limiar_minimo_snr_local_db"]),
                        float(freeze["limiar_deteccao_db"]))
    coverage = verify_empirical_uncertainty(
        val_rows, freeze["tabela_incerteza_cal"], effective_snr, w, partition="val")
    code_now = code_fingerprint()
    changed = sorted(k for k in set(code_now) | set(freeze.get("codigo_sha256", {}))
                     if code_now.get(k) != freeze.get("codigo_sha256", {}).get(k))
    if changed:
        # política fail closed (revisão da Luna sobre 2260df5): validação congelada não roda
        # com código diferente do congelado
        raise ValueError(f"código diferente do congelado em {changed}; validação recusada")
    detection = _summarize_detection(results, w)["val"][str(freeze["limiar_deteccao_db"])]
    fundamental = _summarize_fundamental(results, freeze["yin_best_limiar"])["por_particao"]["val"]
    key = f"yin_best_{freeze['yin_best_limiar']}"
    fundamental = {prof: {snr: entry.get(key, {}) for snr, entry in by_snr.items()}
                   for prof, by_snr in fundamental.items()}
    criteria = freeze["criterios_aceite"]
    coverage_verdict = evaluate_coverage_criterion(coverage, criteria["cobertura"])
    yin_verdict = evaluate_yin_criterion(results, freeze["yin_best_limiar"], "val",
                                         dict(criteria["yin"], perfis=tuple(criteria["yin"]["perfis"])))
    return dict(
        congelamento_sha256=freeze["sha256"],
        janela_s=w,
        veredito_cobertura=coverage_verdict,
        veredito_yin=yin_verdict,
        snr_local_efetivo_db=effective_snr,
        populacao_avaliada=(f"componentes pareados e resolvidos pelo detector com o limiar congelado de "
                            f"{freeze['limiar_deteccao_db']} dB (pareamento refeito nesse limiar) e com "
                            f"SNR local ≥ {effective_snr} dB, controle de qualidade calibrado em cal no "
                            "mesmo limiar"),
        codigo_igual_ao_congelado=True,
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
        nota=("filtro FIR do scipy da cadeia sintética de referência; não é filtro de fonte real "
              "nem de arquivo MBARI (NO-GO); valida o procedimento"),
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
    parser.add_argument("--offset-replica", type=int, default=0,
                        help="índice da primeira réplica; a rodada final usa sementes inéditas "
                             "(o piloto consumiu as réplicas 0 a 5 de cal e ver)")
    parser.add_argument("--congelamento",
                        help="arquivo de congelamento; obrigatório com val, que roda sozinha")
    args = parser.parse_args(argv)
    if "val" in args.particoes and (args.particoes != ["val"] or not args.congelamento):
        parser.error("val roda sozinha e exige --congelamento (regras fixadas antes, só em cal)")

    if args.reps < 1 or args.workers < 1 or args.offset_replica < 0:
        parser.error("--reps e --workers devem ser positivos e --offset-replica, não negativo")

    started = time.time()
    keys = list(GRID)
    cells = [dict(zip(keys, values)) for values in itertools.product(*GRID.values())]
    jobs = [
        (cell, partition, replicate)
        for cell in cells
        for partition in args.particoes
        for replicate in range(args.offset_replica, args.offset_replica + args.reps)
    ]

    with Pool(args.workers) as pool:
        results = pool.map(run_one, jobs, chunksize=4)

    report = dict(
        bloco="B1",
        plano="SIM-MCA-001 v0.3.5 — incerteza em Hz por excursão; identificabilidade exata",
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
        bordas_excursao_em_1_sobre_T=EXCURSION_EDGES_BINS,
        replicas_por_celula_e_particao=args.reps,
        deslocamento_de_replica=args.offset_replica,
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
            "quantis empíricos centrais de 95% do erro em Hz, por SNR local e excursão de frequência "
            "na janela; intervalo em ln f a partir de f_est; SNR mínima selecionada somente em cal "
            "e verificada somente em ver"
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
