"""Estimadores independentes da fundamental f̂0 (plano, Seção 4, item 3; decisão D4).

Só estimadores que não pressupõem estrutura harmônica: autocorrelação normalizada
(família YIN) e cepstro. Cada estimativa vem com uma medida de confiança; abaixo do
critério de confiabilidade, a saída é NaN (indisponível).
"""
import numpy as np
from scipy import signal as sps

from .generator import FS


def frames(x, win_s, hop_s, fs=FS):
    n, h = int(round(win_s * fs)), int(round(hop_s * fs))
    starts = np.arange(0, x.size - n + 1, h)
    return (starts + n / 2) / fs, [x[s:s + n] for s in starts]


def prefilter(x, band=(5.0, 250.0), fs=FS):
    """Passa-faixa aplicado antes dos estimadores de f0. Não pressupõe estrutura harmônica:
    só limita o ruído de banda larga."""
    sos = sps.butter(4, band, btype="bandpass", fs=fs, output="sos")
    return sps.sosfiltfilt(sos, x)


def yin(frame, fmin=8.0, fmax=40.0, threshold=0.15, mode="first", fs=FS):
    """Diferença média cumulativa normalizada (YIN). Devolve (f0, confiança = 1 − d'(τ)).

    mode="first": primeiro mínimo abaixo do limiar (regra original do YIN).
    mode="best": menor τ cujo d' fica a até 0,05 do mínimo global da faixa; confiável se
    esse mínimo ficar abaixo do limiar."""
    n = frame.size
    tmin, tmax = int(fs / fmax), int(fs / fmin)
    if 2 * tmax >= n:
        raise ValueError("janela curta demais para fmin")
    w = n - tmax - 2
    x0 = frame[:w]
    d = np.array([np.sum((x0 - frame[tau:tau + w]) ** 2) for tau in range(tmax + 2)])
    cm = np.cumsum(d[1:])
    dp = np.ones_like(d)
    dp[1:] = d[1:] * np.arange(1, d.size) / np.where(cm > 0, cm, 1)
    seg = dp[tmin:tmax + 1]
    if mode == "best":
        if seg.min() >= threshold:
            return np.nan, float(1 - seg.min())
        cand = np.where(seg <= seg.min() + 0.05)[0]
    else:
        cand = np.where(seg < threshold)[0]
    if cand.size == 0:
        return np.nan, float(1 - seg.min())
    tau = cand[0] + tmin
    while tau + 1 <= tmax and dp[tau + 1] < dp[tau]:
        tau += 1
    a, b, c = dp[tau - 1], dp[tau], dp[tau + 1]
    den = a - 2 * b + c
    # interpolação parabólica só num mínimo local estrito no interior da faixa; o
    # deslocamento fica limitado a meia amostra (auditoria do Gemini, achado 6)
    if tmin < tau < tmax and b <= a and b <= c and den > 0:
        shift = float(np.clip(0.5 * (a - c) / den, -0.5, 0.5))
    else:
        shift = 0.0
    return fs / (tau + shift), float(1 - b)


def cepstrum(frame, fmin=8.0, fmax=40.0, min_prominence=4.0, fs=FS):
    """Cepstro real. Devolve (f0, proeminência do pico sobre a mediana); NaN abaixo do mínimo."""
    w = frame * np.hanning(frame.size)
    spec = np.abs(np.fft.rfft(w, 4 * frame.size)) + 1e-12
    ceps = np.fft.irfft(np.log(spec))
    qmin, qmax = int(fs / fmax), int(fs / fmin)
    seg = ceps[qmin:qmax + 1]
    i = int(np.argmax(seg))
    prom = float((seg[i] - np.median(seg)) / (np.median(np.abs(seg - np.median(seg))) + 1e-12))
    if prom < min_prominence:
        return np.nan, prom
    q = i + qmin
    if 0 < i < seg.size - 1:
        a, b, c = seg[i - 1], seg[i], seg[i + 1]
        den = a - 2 * b + c
        q += 0.5 * (a - c) / den if den < 0 else 0.0
    return fs / q, prom


def track(x, method="yin", win_s=0.5, hop_s=0.5, fs=FS, **kw):
    t, fr = frames(x, win_s, hop_s, fs)
    fn = yin if method == "yin" else cepstrum
    out = [fn(f, fs=fs, **kw) for f in fr]
    return t, np.array([o[0] for o in out]), np.array([o[1] for o in out])
