import pytest
from hmal.core.harmonic_protocol import RationalChannel, HarmonicProtocol

def test_rational_normalization():
    ch = RationalChannel(6, 8)
    assert ch.a == 3 and ch.b == 4

def test_priority():
    ch = RationalChannel(3, 4)
    assert abs(ch.priority - 1/7) < 1e-6
