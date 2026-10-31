"""Receptor mínimo da bancada digital HMAL, conforme lab/BENCH_CRITERIA.md (v0.3.1, Seção 4)."""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import gcd, log

import numpy as np
from scipy.optimize import minimize_scalar

N_ORDER = 16
PILOT = Fraction(1, 1)


@lru_cache(maxsize=None)
def h_n(n: int = N_ORDER) -> tuple[Fraction, ...]:
    return tuple(sorted({Fraction(a, b) for a in range(1, n + 1) for b in range(1, n + 1) if gcd(a, b) == 1}))


def detection_threshold(alpha: float = 0.005, m: int | None = None) -> float:
    """Limiar gamma = -ln(1 - (1 - alpha)^(1/M)) (Seção 5)."""
    m = len(h_n()) if m is None else m
    return -log(1.0 - (1.0 - alpha) ** (1.0 / m))


def power_at(x: np.ndarray, f: float, fs: float) -> float:
    """P(f) = |X(f)|^2 / N, com X(f) = sum_n x[n] exp(-j 2 pi f n / fs) e janela retangular."""
    n = np.arange(x.size)
    X = np.dot(x, np.exp(-2j * np.pi * f * n / fs))
    return float(abs(X) ** 2 / x.size)


class Receiver:
    def __init__(self, fs: float, duration: float, f0: float) -> None:
        self.fs = float(fs)
        self.T = float(duration)
        self.N = int(round(fs * duration))
        self.f0 = float(f0)
        self.n = np.arange(self.N)
        self.ratios = h_n()

    # --- passos 1 e 2: potência nas candidatas -------------------------------------------
    def _steering(self, freqs: np.ndarray) -> np.ndarray:
        return np.exp(-2j * np.pi * np.outer(freqs, self.n) / self.fs)

    def candidate_powers(self, x: np.ndarray, f0: float, ratios) -> np.ndarray:
        key = (f0, tuple(ratios))
        if key == getattr(self, "_cache_key", None):
            E = self._cache_E
        else:
            E = self._steering(np.array([float(r) * f0 for r in ratios]))
            if f0 == self.f0:  # matriz das candidatas nominais é reutilizada (não muda o cálculo)
                self._cache_key, self._cache_E = key, E
        X = E @ x
        return np.abs(X) ** 2 / self.N

    # --- passo 3: refinamento por Brent ----------------------------------------------------
    def refine(self, x: np.ndarray, fc: float, half_width: float | None = None) -> float:
        hw = 1.0 / self.T if half_width is None else half_width
        y = x * np.exp(-2j * np.pi * fc * self.n / self.fs)  # desloca fc para 0; P(fc + d) inalterado

        def neg_p(d: float) -> float:
            X = np.dot(y, np.exp(-2j * np.pi * d * self.n / self.fs))
            return -(X.real * X.real + X.imag * X.imag) / self.N

        res = minimize_scalar(neg_p, bounds=(-hw, hw), method="bounded", options={"xatol": 1e-5 / self.T})
        return fc + float(res.x)

    # --- passo 4: decodificação ------------------------------------------------------------
    def associate(self, f_est: float, f0: float, ratios) -> dict:
        r = min(ratios, key=lambda q: abs(float(q) * f0 - f_est))
        dist = abs(float(r) * f0 - f_est)
        return {"f_est": f_est, "ratio": [r.numerator, r.denominator], "accepted": dist <= 1.0 / (2.0 * self.T)}

    def decode(self, x: np.ndarray, K: int, pilot: bool = False) -> dict:
        f0 = self.f0
        ratios = self.ratios
        out: dict = {"f0_used": f0}
        if pilot:
            f0 = self.estimate_pilot(x)
            ratios = tuple(r for r in self.ratios if r != PILOT)
            out["f0_used"] = f0
        p = self.candidate_powers(x, f0, ratios)
        top = np.argsort(p)[::-1][:K]
        decoded = []
        for idx in sorted(top, key=lambda i: float(ratios[i])):
            f_est = self.refine(x, float(ratios[idx]) * f0)
            decoded.append(self.associate(f_est, f0, ratios))
        out["channels"] = decoded
        return out

    # --- passo 5: piloto ---------------------------------------------------------------------
    def estimate_pilot(self, x: np.ndarray, rel_range: float = 0.002) -> float:
        lo, hi = self.f0 * (1 - rel_range), self.f0 * (1 + rel_range)
        step = 1.0 / (8.0 * self.T)
        grid = np.arange(lo, hi + step / 2, step)
        p = np.abs(self._steering(grid) @ x) ** 2 / self.N
        best = float(grid[int(np.argmax(p))])
        f = self.refine(x, best, half_width=step)
        return min(max(f, lo), hi)

    # --- detecção (B7) -----------------------------------------------------------------------
    def noise_variance(self, x: np.ndarray) -> float:
        Xk = np.fft.rfft(x)[1 : self.N // 2]
        return float(np.median(np.abs(Xk) ** 2 / self.N) / log(2.0))


class ReceiverV2(Receiver):
    """Receptor v2 (lab/bench/RECEIVER_V2.md): busca de picos antes da associação ao dicionário.

    Mudanças em relação à v1, sem alterar critérios, matriz ou limiares:
    1. Os K maiores picos locais do espectro (grade de passo 1/(8T)) são localizados primeiro e
       refinados por Brent em +-1/(8T); só então cada pico é associado ao elemento mais próximo
       de H_16 e testado contra a tolerância 1/(2T). Um tom fora do dicionário produz um pico
       fora da tolerância, em vez de vazar para a candidata vizinha.
    2. Modo com piloto: o pico a até 0,2% de f0 é o piloto; os demais picos recebem razões
       provisórias por f/f_piloto; f0 final é estimado por mínimos quadrados com o piloto e todos
       os canais; a associação e a tolerância usam esse f0.
    """

    GRID = 8  # pontos por bin de 1/T

    def _peaks(self, x: np.ndarray, n_peaks: int) -> list[float]:
        M = self.GRID * self.N
        P = np.abs(np.fft.rfft(x, n=M)) ** 2 / self.N
        df = self.fs / M
        k = np.arange(1, P.size - 1)
        is_max = (P[k] > P[k - 1]) & (P[k] >= P[k + 1])
        idx = k[is_max]
        top = idx[np.argsort(P[idx])[::-1][:n_peaks]]
        step = 1.0 / (self.GRID * self.T)
        return [self.refine(x, float(i) * df, half_width=step) for i in top]

    def decode(self, x: np.ndarray, K: int, pilot: bool = False) -> dict:
        if not pilot:
            f_est = sorted(self._peaks(x, K))
            return {"f0_used": self.f0, "channels": [self.associate(f, self.f0, self.ratios) for f in f_est]}
        data = tuple(r for r in self.ratios if r != PILOT)
        peaks = self._peaks(x, K + 1)
        lo, hi = self.f0 * 0.998, self.f0 * 1.002
        in_range = [f for f in peaks if lo <= f <= hi]
        if not in_range:
            return {"f0_used": self.f0, "f0_pilot": None, "channels": [{"f_est": f, "ratio": None, "accepted": False} for f in peaks[:K]]}
        f_pilot = min(in_range, key=lambda f: abs(f - self.f0))
        others = sorted(f for f in peaks if f != f_pilot)[:K]
        prov = [min(data, key=lambda q: abs(float(q) - f / f_pilot)) for f in others]
        num = f_pilot + sum(float(r) * f for r, f in zip(prov, others))
        den = 1.0 + sum(float(r) ** 2 for r in prov)
        f0_ls = num / den
        return {"f0_used": f0_ls, "f0_pilot": f_pilot, "channels": [self.associate(f, f0_ls, data) for f in others]}


class ReceiverV3(ReceiverV2):
    """Receptor v3 (lab/bench/RECEIVER_V3.md): seleção nas candidatas (como a v1), refinamento com máximo
    global na janela e teste de dominância espectral; modo com piloto igual à v2.

    Motivação: a v2 busca picos no espectro inteiro e, perto do limiar (16-18 dB), às vezes escolhe um pico de
    ruído longe do tom, o que gera erros enormes e reprova B3(c). A v1 não tem esse problema, mas aceita tons
    fora do dicionário (B7b). A v3 restringe a busca às candidatas e rejeita o canal quando a potência no ponto
    refinado está mais de 10 dB abaixo do maior pico do espectro (o primeiro lóbulo lateral da janela
    retangular fica em -13,3 dB; tons verdadeiros com amplitudes iguais ficam no mesmo nível do maior pico).
    """

    DOMINANCE_DB = -10.0

    def _refine_global(self, x: np.ndarray, fc: float) -> float:
        hw, step = 1.0 / self.T, 1.0 / (self.GRID * self.T)
        offsets = np.arange(-hw, hw + step / 2, step)
        p = np.abs(self._steering(fc + offsets) @ x) ** 2 / self.N
        best = fc + float(offsets[int(np.argmax(p))])
        a, b = max(fc - hw, best - step), min(fc + hw, best + step)
        f = Receiver.refine(self, x, (a + b) / 2, (b - a) / 2)
        return f if power_at(x, f, self.fs) >= power_at(x, best, self.fs) else best

    def decode(self, x: np.ndarray, K: int, pilot: bool = False) -> dict:
        if pilot:
            return ReceiverV2.decode(self, x, K, pilot=True)
        p = self.candidate_powers(x, self.f0, self.ratios)
        top = np.argsort(p)[::-1][:K]
        pmax = float(np.max(np.abs(np.fft.rfft(x, n=self.GRID * self.N)) ** 2) / self.N)
        floor = pmax * 10 ** (self.DOMINANCE_DB / 10)
        out = []
        for idx in sorted(top, key=lambda i: float(self.ratios[i])):
            f = self._refine_global(x, float(self.ratios[idx]) * self.f0)
            ch = self.associate(f, self.f0, self.ratios)
            pf = power_at(x, f, self.fs)
            ch["dominance_db"] = float(10 * np.log10(pf / pmax)) if pf > 0 else -np.inf
            if pf < floor:
                ch["accepted"] = False
            out.append(ch)
        return {"f0_used": self.f0, "channels": out}
