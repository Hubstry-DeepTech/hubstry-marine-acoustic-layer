"""Testes do modulo bioacoustics."""
from __future__ import annotations
import warnings
import pytest
from hmal.bioacoustics.vocalization_mapper import (
    _build_hn,
    classify_vocalization,
    map_cetacean_vocalization,
)
from math import gcd


class TestBuildHn:
    def test_basic_size(self):
        pairs = _build_hn(4)
        assert len(pairs) > 0

    def test_all_coprime(self):
        for n in range(2, 10):
            for a, b in _build_hn(n):
                assert gcd(a, b) == 1, f"gcd({a},{b}) != 1"

    def test_no_duplicates(self):
        seen = set()
        for a, b in _build_hn(8):
            key = (a, b)
            assert key not in seen, f"duplicata: {key}"
            seen.add(key)

    def test_order_one(self):
        pairs = _build_hn(1)
        assert pairs == [(1, 1)]


class TestClassify:
    def test_infrasound_whale(self):
        assert classify_vocalization(15.0, "blue_whale") == "infrassom_social"

    def test_infrasound_nav(self):
        assert classify_vocalization(30.0, "unknown") == "infrassom_navegacao"

    def test_whistle(self):
        assert classify_vocalization(300.0) == "assobio_social"

    def test_click(self):
        assert classify_vocalization(2000.0) == "clique_echolocalizacao"

    def test_ultrasound(self):
        assert classify_vocalization(10000.0) == "ultrassom_alta_resolucao"


class TestMapVocalization:
    def test_basic_mapping(self):
        results = map_cetacean_vocalization([25.0, 50.0], f0_base=25.0)
        assert len(results) == 2
        assert results[0]["channel_ratio"] == "1/1"
        assert results[1]["channel_ratio"] == "2/1"

    def test_error_ppm_present(self):
        results = map_cetacean_vocalization([100.0], f0_base=25.0)
        assert "error_ppm" in results[0]
        assert isinstance(results[0]["error_ppm"], float)

    def test_error_ppm_exact_match(self):
        results = map_cetacean_vocalization([75.0], f0_base=25.0)
        assert results[0]["error_ppm"] == 0.0

    def test_tolerance_within(self):
        results = map_cetacean_vocalization([50.0], f0_base=25.0, tolerance=1e-3)
        assert results[0]["within_tolerance"] is True

    def test_tolerance_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            results = map_cetacean_vocalization(
                [9999.0], f0_base=25.0, harmonic_order=4, tolerance=1e-6
            )
            assert len(w) >= 1
            assert any("ppm" in str(x.message).lower() for x in w)

    def test_biological_interpretation_present(self):
        results = map_cetacean_vocalization(
            [25.0], f0_base=25.0, species="blue_whale"
        )
        assert "biological_interpretation" in results[0]

    def test_negative_frequency_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            results = map_cetacean_vocalization([-5.0], f0_base=25.0)
            assert len(results) == 0
            assert len(w) >= 1

    def test_invalid_f0_raises(self):
        with pytest.raises(ValueError):
            map_cetacean_vocalization([100.0], f0_base=0.0)

    def test_invalid_order_raises(self):
        with pytest.raises(ValueError):
            map_cetacean_vocalization([100.0], f0_base=25.0, harmonic_order=0)
