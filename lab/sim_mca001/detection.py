"""Detecção de componentes sem hipótese sobre a fundamental.

A avaliação sintética separa três resultados: componente localizado, pico falso e
componente não resolvido. O pareamento usa uma atribuição global um-a-um e uma
janela de associação limitada pela resolução temporal e pela excursão de frequência
durante a janela STFT; não usa espaçamento harmônico como tolerância.
"""
from dataclasses import dataclass

import numpy as np
from scipy import signal as sps
from scipy.ndimage import median_filter
from scipy.optimize import linear_sum_assignment

from .generator import FS


@dataclass
class StftParams:
    win_s: float = 1.0
    hop_s: float = 0.5
    zero_pad: int = 4
    floor_bins_hz: float = 20.0
    threshold_db: float = 6.0
    f_lo: float = 5.0
    f_hi: float = 900.0


def stft_power(x, p: StftParams, fs=FS):
    nper = int(round(p.win_s * fs))
    hop = int(round(p.hop_s * fs))
    nfft = nper * p.zero_pad
    f, t, Z = sps.stft(
        x,
        fs=fs,
        window="hann",
        nperseg=nper,
        noverlap=nper - hop,
        nfft=nfft,
        boundary=None,
        padded=False,
    )
    return f, t, np.abs(Z) ** 2


def detect(x, p: StftParams = StftParams(), fs=FS):
    """Devolve, por quadro, picos (frequência, potência e SNR local linear)."""
    f, t, P = stft_power(x, p, fs)
    df = f[1] - f[0]
    width = max(3, int(round(p.floor_bins_hz / df)) | 1)
    floor = median_filter(P, size=(width, 1), mode="nearest")
    log_power = np.log(P + 1e-300)
    threshold = 10 ** (p.threshold_db / 10)
    band = (f >= p.f_lo) & (f <= p.f_hi)
    frames = []

    for j in range(P.shape[1]):
        col = P[:, j]
        local = np.where(
            band[1:-1]
            & (col[1:-1] > col[:-2])
            & (col[1:-1] >= col[2:])
            & (col[1:-1] > threshold * floor[1:-1, j])
        )[0] + 1

        # Evita contar lóbulos do preenchimento com zeros como picos distintos.
        radius = p.zero_pad
        local = [
            i for i in local
            if col[i] >= col[max(0, i - radius): i + radius + 1].max()
        ]

        peaks = []
        for i in local:
            a, b, c = log_power[i - 1, j], log_power[i, j], log_power[i + 1, j]
            denominator = a - 2 * b + c
            shift = 0.5 * (a - c) / denominator if denominator < 0 else 0.0
            peak_power = float(np.exp(b - 0.25 * (a - c) * shift))
            peaks.append((float(f[i] + shift * df), peak_power,
                          float(col[i] / max(floor[i, j], 1e-300))))
        frames.append(peaks)

    return t, frames, float(df)


def _truth_slope_hz_s(track, truth, index):
    """Derivada local da frequência verdadeira, em Hz/s."""
    if track.size < 2:
        return 0.0
    slope = np.gradient(track, truth.t)
    return float(slope[index])


MAINLOBE_HALF_WIDTH_BINS = 2.0  # meia largura do lóbulo principal da janela de Hann, em 1/T


def match_truth(
    t_frames,
    frames,
    truth,
    tol_hz=None,
    *,
    win_s=None,
    df_hz=None,
    fs=FS,
    max_gate_fraction=0.45,
):
    """Pareia detecções e componentes verdadeiros com associação global um-a-um.

    Porta de associação (independente do orçamento de precisão 1/T; parecer da Luna e
    auditoria do Gemini sobre o piloto v2):

        porta_k = max(2/T, |df_k/dt| · T / 2, df_STFT / 2)

    - 2/T é a meia largura do lóbulo principal da janela de Hann: um pico fora dela não é
      produzido pelo lóbulo principal daquele componente. O orçamento de precisão (1/T) é
      medido depois, sobre os pareados, e não coincide com a porta;
    - |df/dt|·T/2 é a excursão de frequência do componente na janela;
    - df_STFT/2 é metade do passo da grade de frequências.

    Se a porta atinge 45% da separação ao componente verdadeiro mais próximo, o componente
    é "não resolvido". Todos os componentes, resolvidos ou não, entram numa única associação
    um-a-um. Assim:
    - cada pico é contado uma única vez: registro (componente resolvido), pico de componente
      não resolvido (no máximo um por componente) ou pico falso;
    - cada componente resolvido é pareado ou perdido.

    Identidades garantidas por quadro e no total:
        registros + perdidos + não_resolvidos = componentes_verdadeiros
        registros + picos_de_não_resolvidos + falsos = picos_detectados

    Se tol_hz for fornecido, ele substitui a porta (uso em testes).

    Retorna: registros, picos_falsos, componentes_verdadeiros, componentes_perdidos,
    componentes_não_resolvidos, picos_associados_a_componentes_não_resolvidos.
    Cada registro: (quadro, índice_componente, f_verdadeira, f_estimada, SNR_local).
    """
    if tol_hz is None and (win_s is None or win_s <= 0):
        raise ValueError("win_s positivo é obrigatório quando tol_hz não é fornecido")
    if max_gate_fraction <= 0 or max_gate_fraction >= 0.5:
        raise ValueError("max_gate_fraction deve estar entre 0 e 0.5")

    records = []
    false_peaks = n_true = n_missed = n_unresolved_truth = n_unresolved_peaks = 0

    for frame_index, (frame_time, peaks) in enumerate(zip(t_frames, frames)):
        sample_index = int(np.clip(round(frame_time * fs), 0, truth.t.size - 1))
        true_freqs = np.asarray([track[sample_index] for track in truth.freqs], dtype=float)
        detected_freqs = np.asarray([peak[0] for peak in peaks], dtype=float)
        detected_snr = np.asarray([peak[2] for peak in peaks], dtype=float)
        K = true_freqs.size
        n_true += K
        if K == 0:
            false_peaks += detected_freqs.size
            continue

        gates = np.empty(K)
        ambiguous = np.zeros(K, dtype=bool)
        for k, track in enumerate(truth.freqs):
            if tol_hz is not None:
                gate = float(tol_hz)
            else:
                fdot = abs(_truth_slope_hz_s(np.asarray(track), truth, sample_index))
                gate = max(MAINLOBE_HALF_WIDTH_BINS / win_s, 0.5 * fdot * win_s,
                           0.5 * (df_hz or 0.0))
            if K > 1:
                nearest = float(np.min(np.abs(true_freqs[k] - np.delete(true_freqs, k))))
                cap = max_gate_fraction * nearest
                if gate >= cap:
                    ambiguous[k] = True
                    if tol_hz is None:
                        gate = cap  # o pico absorvido não pode invadir o vizinho
            gates[k] = gate
        n_unresolved_truth += int(ambiguous.sum())

        matched_truth, matched_det = set(), set()
        if detected_freqs.size:
            distance = np.abs(true_freqs[:, None] - detected_freqs[None, :])
            cost = np.where(distance <= gates[:, None], distance, 1e9 + distance)
            rows, cols = linear_sum_assignment(cost)
            for r, c in zip(rows, cols):
                if distance[r, c] > gates[r]:
                    continue
                matched_truth.add(int(r))
                matched_det.add(int(c))
                if ambiguous[r]:
                    n_unresolved_peaks += 1
                else:
                    records.append((frame_index, int(r), float(true_freqs[r]),
                                    float(detected_freqs[c]), float(detected_snr[c])))
        n_missed += int(sum(1 for k in range(K) if not ambiguous[k] and k not in matched_truth))
        false_peaks += int(detected_freqs.size - len(matched_det))

    return (records, int(false_peaks), int(n_true), int(n_missed),
            int(n_unresolved_truth), int(n_unresolved_peaks))
