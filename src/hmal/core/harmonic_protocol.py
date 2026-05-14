from dataclasses import dataclass
from math import gcd
import numpy as np

@dataclass(frozen=True)
class RationalChannel:
    a: int
    b: int
    def __post_init__(self):
        g = gcd(self.a, self.b)
        if g > 1:
            object.__setattr__(self, 'a', self.a // g)
            object.__setattr__(self, 'b', self.b // g)
    @property
    def priority(self): return 1.0 / (self.a + self.b)
    def frequency(self, f0: float) -> float: return (self.a / self.b) * f0

class HarmonicProtocol:
    def __init__(self, f0_base: float, harmonic_order: int = 16, mode: str = "hybrid"):
        self.f0_base = f0_base
        self.mode = mode
        self.f0_adaptive = 25.0 if mode == "whale" else (1732.0 if mode == "dolphin" else f0_base)
