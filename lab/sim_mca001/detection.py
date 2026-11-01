"""Detecção de componentes sem hipótese sobre a fundamental (plano, Seção 4, item 1)."""
from dataclasses import dataclass

import numpy as np
from scipy import signal as sps
from scipy.ndimage import median_filter

from .generator import FS


@dataclass
class StftParams:
    win_s: float = 1.0
    hop_s: float = 0.5
    zero_pad: int = 4
    floor_bins_hz: float = 20.0   # largura da mediana móvel do piso de ruído, em Hz
    threshold_db: float = 6.0     # pico precisa ficar este tanto acima do piso local
    f_lo: float = 5.0
    f_hi: float = 900.0


def stft_power(x, p: StftParams, fs=FS):
    nper = int(round(p.win_s * fs))
    hop = int(round(p.hop_s * fs))
    nfft = nper * p.zero_pad
    f, t, Z = sps.stft(x, fs=fs, window="hann", nperseg=nper, noverlap=nper - hop, nfft=nfft,
                       boundary=None, padded=False)
    return f, t, np.abs(Z) ** 2


def detect(x, p: StftParams = StftParams(), fs=FS):
    """Devolve, para cada quadro, os picos (f, potência, SNR local linear) e a grade de tempos.

    Frequência refinada por interpolação parabólica do log da potência.
    """
    f, t, P = stft_power(x, p, fs)
    df = f[1] - f[0]
    w = max(3, int(round(p.floor_bins_hz / df)) | 1)
    floor = median_filter(P, size=(w, 1), mode="nearest")
    lp = np.log(P + 1e-300)
    thr = 10 ** (p.threshold_db / 10)
    band = (f >= p.f_lo) & (f <= p.f_hi)
    frames = []
    for j in range(P.shape[1]):
        col, lcol, fl = P[:, j], lp[:, j], floor[:, j]
        k = np.where(band[1:-1] & (col[1:-1] > col[:-2]) & (col[1:-1] >= col[2:])
                     & (col[1:-1] > thr * fl[1:-1]))[0] + 1
        # máximo local também na vizinhança de ±zero_pad posições (±1 posição sem preenchimento),
        # para não contar ondulações do preenchimento com zeros como picos distintos
        r = p.zero_pad
        k = [i for i in k if col[i] >= col[max(0, i - r):i + r + 1].max()]
        peaks = []
        for i in k:
            a, b, c = lcol[i - 1], lcol[i], lcol[i + 1]
            den = a - 2 * b + c
            d = 0.5 * (a - c) / den if den < 0 else 0.0
            peaks.append((f[i] + d * df, float(np.exp(b - 0.25 * (a - c) * d)), float(col[i] / fl[i])))
        frames.append(peaks)
    return t, frames, df


def match_truth(t_frames, frames, truth, tol_hz):
    """Pareia picos detectados com componentes verdadeiros no centro de cada quadro.

    Devolve uma lista de registros (quadro, índice do componente, f_verdadeira, f_estimada,
    SNR local) e o número de picos não pareados (falsos)."""
    rec, false_peaks, n_true = [], 0, 0
    for j, (tc, peaks) in enumerate(zip(t_frames, frames)):
        idx = min(int(round(tc * FS)), truth.t.size - 1)
        ftrue = np.array([fk[idx] for fk in truth.freqs])
        n_true += ftrue.size
        used = set()
        for fe, amp, snr in peaks:
            d = np.abs(ftrue - fe)
            k = int(np.argmin(d)) if d.size else -1
            if k >= 0 and d[k] <= tol_hz and k not in used:
                used.add(k)
                rec.append((j, k, float(ftrue[k]), float(fe), snr))
            else:
                false_peaks += 1
    return rec, false_peaks, n_true
