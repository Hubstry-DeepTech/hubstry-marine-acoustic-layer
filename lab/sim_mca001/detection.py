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
    """Pareia detecções e componentes verdadeiros com associação um-a-um.

    Se tol_hz for fornecido, usa-o como limite fixo (compatibilidade dos testes).
    No runner, win_s é obrigatório e a porta de associação é:

        max(1 / T, |df/dt| * T / 2, df_STFT / 2)

    A porta é limitada a 45% da separação do componente verdadeiro mais próximo.
    Quando a excursão necessária excede esse limite, o componente é marcado como
    não resolvido, em vez de forçar um pareamento ou contar o pico como falso.

    Retorna:
      registros, picos_falsos, componentes_verdadeiros, componentes_perdidos,
      componentes_não_resolvidos, picos_associados_a_componentes_não_resolvidos.

    Cada registro tem (quadro, índice_componente, f_verdadeira, f_estimada, SNR_local).
    """
    if tol_hz is None and (win_s is None or win_s <= 0):
        raise ValueError("win_s positivo é obrigatório quando tol_hz não é fornecido")
    if max_gate_fraction <= 0 or max_gate_fraction >= 0.5:
        raise ValueError("max_gate_fraction deve estar entre 0 e 0.5")

    records = []
    false_peaks = 0
    n_true = 0
    n_missed = 0
    n_unresolved_truth = 0
    n_unresolved_peaks = 0

    for frame_index, (frame_time, peaks) in enumerate(zip(t_frames, frames)):
        sample_index = int(np.clip(round(frame_time * fs), 0, truth.t.size - 1))
        true_freqs = np.asarray([track[sample_index] for track in truth.freqs], dtype=float)
        detected_freqs = np.asarray([peak[0] for peak in peaks], dtype=float)
        detected_snr = np.asarray([peak[2] for peak in peaks], dtype=float)
        n_true += true_freqs.size

        if true_freqs.size == 0:
            false_peaks += detected_freqs.size
            continue

        raw_gates = np.empty(true_freqs.size, dtype=float)
        ambiguous = np.zeros(true_freqs.size, dtype=bool)

        for k, track in enumerate(truth.freqs):
            if tol_hz is not None:
                raw_gate = float(tol_hz)
            else:
                fdot = abs(_truth_slope_hz_s(np.asarray(track), truth, sample_index))
                raw_gate = max(1.0 / win_s, 0.5 * fdot * win_s, 0.5 * (df_hz or 0.0))

            if true_freqs.size > 1:
                separations = np.abs(true_freqs[k] - np.delete(true_freqs, k))
                nearest = float(np.min(separations))
                cap = max_gate_fraction * nearest
                raw_gates[k] = raw_gate
                if raw_gate >= cap:
                    ambiguous[k] = True
            else:
                raw_gates[k] = raw_gate

        n_unresolved_truth += int(ambiguous.sum())
        eligible = np.flatnonzero(~ambiguous)

        # Deteções próximas de componentes não resolvidos não são falsos positivos.
        unresolved_detection = np.zeros(detected_freqs.size, dtype=bool)
        for k in np.flatnonzero(ambiguous):
            unresolved_detection |= (
                np.abs(detected_freqs - true_freqs[k]) <= raw_gates[k]
            )
        n_unresolved_peaks += int(unresolved_detection.sum())

        matched_truth = set()
        matched_detection = set()

        if eligible.size and detected_freqs.size:
            gates = raw_gates[eligible].copy()
            if tol_hz is None and true_freqs.size > 1:
                for pos, k in enumerate(eligible):
                    nearest = np.min(np.abs(true_freqs[k] - np.delete(true_freqs, k)))
                    gates[pos] = min(gates[pos], max_gate_fraction * nearest)

            distance = np.abs(true_freqs[eligible, None] - detected_freqs[None, :])
            invalid_cost = 1e9
            cost = np.where(distance <= gates[:, None], distance, invalid_cost + distance)
            row_index, col_index = linear_sum_assignment(cost)

            for row, col in zip(row_index, col_index):
                if distance[row, col] > gates[row]:
                    continue
                k = int(eligible[row])
                matched_truth.add(k)
                matched_detection.add(int(col))
                records.append((
                    frame_index,
                    k,
                    float(true_freqs[k]),
                    float(detected_freqs[col]),
                    float(detected_snr[col]),
                ))

        n_missed += int(eligible.size - len(matched_truth))
        false_peaks += sum(
            1 for i in range(detected_freqs.size)
            if i not in matched_detection and not unresolved_detection[i]
        )

    return (
        records,
        int(false_peaks),
        int(n_true),
        int(n_missed),
        int(n_unresolved_truth),
        int(n_unresolved_peaks),
    )
