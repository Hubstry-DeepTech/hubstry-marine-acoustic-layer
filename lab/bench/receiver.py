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
