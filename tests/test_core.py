"""Testes do modulo core."""
from __future__ import annotations
import numpy as np
import pytest
from hmal.core.harmonic_protocol import HarmonicProtocol, RationalChannel, _lcm_list


class TestRationalChannel:
    def test_creation(self):
        ch = RationalChannel(3, 2)
        assert ch.a == 3
        assert ch.b == 2

    def test_auto_reduce(self):
        ch = RationalChannel(4, 2)
        assert ch.a == 2
        assert ch.b == 1

    def test_priority(self):
        ch = RationalChannel(1, 1)
        assert ch.priority == pytest.approx(0.5)

    def test_frequency(self):
        ch = RationalChannel(3, 2)
        assert ch.frequency(100.0) == pytest.approx(150.0)

    def test_invalid_range(self):
        with pytest.raises(ValueError):
            RationalChannel(0, 1)
        with pytest.raises(ValueError):
            RationalChannel(1, 0)


class TestLcmList:
    def test_basic(self):
        assert _lcm_list([2, 3, 4]) == 12

    def test_single(self):
        assert _lcm_list([7]) == 7

    def test_empty(self):
        assert _lcm_list([]) == 1


class TestHarmonicProtocol:
    def test_creation(self):
        hp = HarmonicProtocol(f0_base=25.0)
        assert hp.f0_base == 25.0
        assert hp.harmonic_order == 16

    def test_invalid_f0(self):
        with pytest.raises(ValueError):
            HarmonicProtocol(f0_base=-10.0)


class TestWaveform:
    def test_shape(self):
        hp = HarmonicProtocol(f0_base=25.0)
        t, s = hp.generate_waveform([(1, 1)], duration=0.01, sample_rate=48000)
        assert t.ndim == 1
        assert s.ndim == 1
        assert len(t) == len(s)

    def test_normalization(self):
        hp = HarmonicProtocol(f0_base=25.0)
        t, s = hp.generate_waveform([(1, 1), (2, 1)], duration=0.01)
        assert np.max(np.abs(s)) == pytest.approx(1.0)

    def test_empty_channels_raises(self):
        hp = HarmonicProtocol(f0_base=25.0)
        with pytest.raises(ValueError):
            hp.generate_waveform([], duration=0.01)

    def test_duration_raises(self):
        hp = HarmonicProtocol(f0_base=25.0)
        with pytest.raises(ValueError):
            hp.generate_waveform([(1, 1)], duration=0.0)


class TestSyncWindow:
    def test_basic(self):
        hp = HarmonicProtocol(f0_base=25.0)
        sw = hp.sync_window([(1, 2), (1, 3)])
        assert sw == pytest.approx(6.0 / 25.0)

    def test_empty_raises(self):
        hp = HarmonicProtocol(f0_base=25.0)
        with pytest.raises(ValueError):
            hp.sync_window([])


class TestAdaptiveF0:
    def test_returns_float(self):
        hp = HarmonicProtocol(f0_base=25.0, mode="hybrid")
        f0 = hp.set_adaptive_f0(snr_db=15.0)
        assert isinstance(f0, float)
        assert f0 > 25.0

    def test_snr_zero(self):
        hp = HarmonicProtocol(f0_base=25.0, mode="hybrid")
        f0 = hp.set_adaptive_f0(snr_db=0.0)
        assert f0 == pytest.approx(25.0)

    def test_snr_high(self):
        hp = HarmonicProtocol(f0_base=25.0, mode="hybrid")
        f0_low = hp.set_adaptive_f0(snr_db=5.0)
        f0_high = hp.set_adaptive_f0(snr_db=25.0)
        assert f0_high > f0_low

    def test_non_hybrid_mode(self):
        hp = HarmonicProtocol(f0_base=50.0, mode="custom")
        f0 = hp.set_adaptive_f0(snr_db=20.0)
        assert f0 == 50.0
