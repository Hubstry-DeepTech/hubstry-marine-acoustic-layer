"""Gerador de sinais sintéticos (plano SIM-MCA-001, Seção 3).

Todo sinal é gerado como forma de onda, a FS = 2 kHz, e devolve também a verdade
(frequência de cada componente em função do tempo) para avaliação.
"""
from dataclasses import dataclass, field

import numpy as np
from scipy import signal as sps

FS = 2000.0


@dataclass
class Truth:
    """Verdade de um sinal: frequências instantâneas e amplitudes por componente."""
    t: np.ndarray
    freqs: list            # lista de arrays f_k(t), em Hz
    amps: list             # amplitude de cada componente (constante)
    orders: list           # ordem harmônica verdadeira, ou None nos nulos
    f0: np.ndarray | None  # fundamental física f0(t), ou None nos nulos
    meta: dict = field(default_factory=dict)


def f0_contour(t, f0_start, slope_oct_per_s):
    """Contorno linear em log2 f: f0(t) = f0_start · 2^(slope · t)."""
    return f0_start * np.power(2.0, slope_oct_per_s * t)


def tukey_envelope(n, fs=FS, ramp_s=0.5):
    alpha = min(1.0, 2 * ramp_s * fs / n)
    return sps.windows.tukey(n, alpha)


AMPLITUDE_PROFILES = ("decrescente", "h3_dominante", "ausente_identificavel", "ausente_ambigua")


def amplitude_profile(name, orders):
    """Amplitude por ordem. Os dois perfis 'ausente_*' seguem o parecer da Luna:
    fundamental ausente com periodicidade identificável (ordens 2, 3, 4, ...) e
    fundamental ausente com periodicidade ambígua (só ordens pares)."""
    n = np.asarray(orders, dtype=float)
    if name == "decrescente":
        a = 1.0 / n
    elif name == "h3_dominante":
        a = 0.5 / n
        a[n == 1] = 0.1
        a[n == 3] = 1.0
    elif name == "ausente_identificavel":
        a = 1.0 / n
        a[n == 1] = 0.0
    elif name == "ausente_ambigua":
        a = np.where(n % 2 == 0, 1.0 / n, 0.0)
    else:
        raise ValueError(name)
    return a


def _phase(freq, fs):
    return 2 * np.pi * np.cumsum(freq) / fs


def harmonic(rng, duration=10.0, f0_start=15.0, slope=0.0, profile="decrescente",
             f_gen_max=900.0, inharm_b=0.0, tau_sim=0.0, fs=FS):
    """G1 (inharm_b = tau_sim = 0) e G2: f_n = n·f0·√(1 + b·n²)·(1 + δ_n), δ_n ~ N(0, tau_sim²)."""
    t = np.arange(int(round(duration * fs))) / fs
    f0 = f0_contour(t, f0_start, slope)
    n_max = int(np.floor(f_gen_max / f0.max()))
    orders = np.arange(1, n_max + 1)
    amps = amplitude_profile(profile, orders)
    delta = rng.normal(0.0, tau_sim, size=orders.size) if tau_sim > 0 else np.zeros(orders.size)
    env = tukey_envelope(t.size, fs)
    x = np.zeros_like(t)
    freqs, kept_amps, kept_orders = [], [], []
    for n, a, d in zip(orders, amps, delta):
        if a <= 0:
            continue
        fn = n * f0 * np.sqrt(1.0 + inharm_b * n * n) * (1.0 + d)
        if fn.max() >= 0.5 * fs:
            continue
        x += a * np.sin(_phase(fn, fs) + rng.uniform(0, 2 * np.pi))
        freqs.append(fn)
        kept_amps.append(float(a))
        kept_orders.append(int(n))
    return env * x, Truth(t, freqs, kept_amps, kept_orders, f0,
                          dict(gen="G1" if inharm_b == 0 and tau_sim == 0 else "G2",
                               f0_start=f0_start, slope=slope, profile=profile,
                               inharm_b=inharm_b, tau_sim=tau_sim))


def _near_small_ratio(fs_sorted, n_excl, eta):
    """Verdadeiro se algum par de frequências tem razão a menos de eta (em log) de m/n, m, n ≤ n_excl."""
    ratios = np.array(sorted({m / n for m in range(1, n_excl + 1) for n in range(1, n_excl + 1) if m > n}))
    lr = np.log(ratios)
    for i in range(len(fs_sorted)):
        for j in range(i + 1, len(fs_sorted)):
            if np.min(np.abs(np.log(fs_sorted[j] / fs_sorted[i]) - lr)) < eta:
                return True
    return False


def null_comodulated(rng, K, band, duration=10.0, slope=0.0, amps=None, n_excl=6, eta=0.01,
                     fs=FS, max_tries=10000):
    """G3: K componentes com frequências iniciais log-uniformes na banda, todos com a mesma
    modulação relativa (comodulação). Exclui pares com razão a menos de eta (log) de m/n,
    m, n ≤ n_excl. Coincidências com razões de ordem mais alta permanecem e entram na taxa
    de falsa homologia medida."""
    t = np.arange(int(round(duration * fs))) / fs
    lo, hi = band
    hi0 = hi / max(1.0, 2.0 ** (slope * duration)) if slope > 0 else hi
    for _ in range(max_tries):
        f_init = np.sort(np.exp(rng.uniform(np.log(lo), np.log(hi0), size=K)))
        if not _near_small_ratio(f_init, n_excl, eta):
            break
    else:
        raise RuntimeError("G3: zona de exclusão impossível de satisfazer")
    mod = np.power(2.0, slope * t)
    amps = np.ones(K) if amps is None else np.asarray(amps, float)
    env = tukey_envelope(t.size, fs)
    x = np.zeros_like(t)
    freqs = []
    for f, a in zip(f_init, amps):
        fk = f * mod
        x += a * np.sin(_phase(fk, fs) + rng.uniform(0, 2 * np.pi))
        freqs.append(fk)
    return env * x, Truth(t, freqs, list(map(float, amps)), [None] * K, None,
                          dict(gen="G3", K=K, band=band, slope=slope, n_excl=n_excl, eta=eta))


def null_independent(rng, K, band, duration=10.0, slope_sd=0.05, fm_sd=0.002, amps=None, fs=FS):
    """G4: K componentes com frequências log-uniformes na banda, cada um com inclinação própria
    (desvio-padrão slope_sd, em oitavas/s) e passeio aleatório próprio em log f (passo fm_sd por segundo)."""
    t = np.arange(int(round(duration * fs))) / fs
    lo, hi = band
    amps = np.ones(K) if amps is None else np.asarray(amps, float)
    env = tukey_envelope(t.size, fs)
    x = np.zeros_like(t)
    freqs = []
    for a in amps:
        f = np.exp(rng.uniform(np.log(lo), np.log(hi)))
        walk = np.cumsum(rng.normal(0, fm_sd / np.sqrt(fs), size=t.size))
        fk = f * np.power(2.0, rng.normal(0, slope_sd) * t + walk)
        fk = np.clip(fk, 1.0, 0.49 * fs)
        x += a * np.sin(_phase(fk, fs) + rng.uniform(0, 2 * np.pi))
        freqs.append(fk)
    return env * x, Truth(t, freqs, list(map(float, amps)), [None] * K, None,
                          dict(gen="G4", K=K, band=band, slope_sd=slope_sd, fm_sd=fm_sd))


def colored_noise(rng, n, alpha=0.0):
    """Ruído gaussiano com espectro de potência ∝ 1/f^alpha (alpha = 0: branco)."""
    w = rng.normal(size=n)
    if alpha == 0:
        return w
    spec = np.fft.rfft(w)
    f = np.fft.rfftfreq(n)
    f[0] = f[1]
    spec *= f ** (-alpha / 2.0)
    out = np.fft.irfft(spec, n)
    return out / out.std()


def band_energy(x, band, fs=FS):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(x.size, 1 / fs)
    m = (f >= band[0]) & (f <= band[1])
    return float(np.sum(np.abs(spec[m]) ** 2))


def add_noise(rng, x, snr_db, band, alpha=0.0, fs=FS):
    """Convenção SNR_integrated: energia do sinal sobre energia do ruído, ambas integradas no
    evento e na banda de análise `band`."""
    noise = colored_noise(rng, x.size, alpha)
    scale = np.sqrt(band_energy(x, band, fs) / (band_energy(noise, band, fs) * 10 ** (snr_db / 10)))
    return x + scale * noise, scale


def decimation_chain(x16k, factor=8):
    """Cadeia de decimação simulada (FIR de fase zero). Não é o filtro do MBARI:
    serve para verificar o procedimento de fixação de f_max."""
    return sps.decimate(x16k, factor, ftype="fir", zero_phase=True)


def overlap(x1, x2, lag_samples, gain=1.0):
    """Sobreposição de dois animais: soma com defasagem."""
    y = x1.copy()
    y[lag_samples:] += gain * x2[: x1.size - lag_samples]
    return y


def multipath(x, delay_s, gain, fs=FS):
    d = int(round(delay_s * fs))
    y = x.copy()
    y[d:] += gain * x[: x.size - d]
    return y
