"""Protocolo Harmonico HMAL -- Core."""
from __future__ import annotations
from dataclasses import dataclass
from math import gcd, lcm as math_lcm
from functools import reduce
import numpy as np


def _lcm_list(values: list[int]) -> int:
    return reduce(math_lcm, values, 1)


@dataclass(frozen=True)
class RationalChannel:
    a: int
    b: int
    def __post_init__(self) -> None:
        if self.a < 1 or self.b < 1:
            raise ValueError("a e b devem ser >= 1")
        g = gcd(self.a, self.b)
        if g > 1:
            object.__setattr__(self, "a", self.a // g)
            object.__setattr__(self, "b", self.b // g)
    @property
    def priority(self) -> float:
        return 1.0 / (self.a + self.b)
    def frequency(self, f0: float) -> float:
        return (self.a / self.b) * f0
    def __repr__(self) -> str:
        return f"RationalChannel({self.a}/{self.b})"


class HarmonicProtocol:
    _F0_DEFAULTS = {"whale": 25.0, "dolphin": 1732.0}

    def __init__(self, f0_base: float, harmonic_order: int = 16, mode: str = "hybrid") -> None:
        if f0_base <= 0:
            raise ValueError(f"f0_base deve ser positivo; recebido: {f0_base}")
        self.f0_base = f0_base
        self.harmonic_order = harmonic_order
        self.mode = mode
        self._f0_adaptive = self._F0_DEFAULTS.get(mode, f0_base)

    @property
    def f0_adaptive(self) -> float:
        return self._f0_adaptive

    def set_adaptive_f0(self, snr_db: float | None = None) -> float:
        if self.mode != "hybrid" or snr_db is None:
            return self._f0_adaptive
        import math
        snr_clamped = max(0.0, min(30.0, snr_db))
        log_f0 = math.log(25.0) + (snr_clamped / 30.0) * math.log(1732.0 / 25.0)
        self._f0_adaptive = math.exp(log_f0)
        return self._f0_adaptive

    def generate_waveform(self, channels: list[tuple[int, int]], duration: float,
                          sample_rate: int = 48000, amplitudes: list[float] | None = None,
                          phase_polarities: list[int] | None = None) -> tuple[np.ndarray, np.ndarray]:
        if not channels:
            raise ValueError("channels nao pode ser vazio.")
        if duration <= 0:
            raise ValueError("duration deve ser positivo")
        n = len(channels)
        amps = amplitudes or [1.0] * n
        phases = phase_polarities or [0] * n
        if len(amps) != n:
            raise ValueError(f"amplitudes deve ter {n} elementos.")
        if len(phases) != n:
            raise ValueError(f"phase_polarities deve ter {n} elementos.")
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        s = np.zeros_like(t)
        for (a, b), amp, phi in zip(channels, amps, phases):
            freq = (a / b) * self._f0_adaptive
            phase_rad = 0.0 if phi == 0 else np.pi
            s += amp * np.sin(2 * np.pi * freq * t + phase_rad)
        max_val = np.max(np.abs(s))
        if max_val > 0:
            s = s / max_val
        return t, s

    def sync_window(self, channel_ratios: list[tuple[int, int]]) -> float:
        if not channel_ratios:
            raise ValueError("channel_ratios nao pode ser vazio.")
        denominators = [b for (_, b) in channel_ratios]
        lcm_b = _lcm_list(denominators)
        return lcm_b / self._f0_adaptive
