import pytest
from hmal.bioacoustics.vocalization_mapper import map_cetacean_vocalization, classify_vocalization

def test_map_single_frequency_whale():
    result = map_cetacean_vocalization([25.0], f0_base=25.0, harmonic_order=16)
    assert result[0]["channel_ratio"] == "1/1"
    assert abs(result[0]["priority"] - 0.5) < 1e-6

def test_map_single_frequency_dolphin():
    result = map_cetacean_vocalization([1732.0], f0_base=1732.0, harmonic_order=16)
    assert result[0]["channel_ratio"] == "1/1"

def test_classify_blue_whale_infrasound():
    assert classify_vocalization(20.0, "blue_whale") == "infrassom_social"

def test_classify_dolphin_whistle():
    assert classify_vocalization(300.0) == "assobio_social"

def test_classify_dolphin_click():
    assert classify_vocalization(3000.0) == "clique_echolocalizacao"

def test_map_out_of_tolerance():
    result = map_cetacean_vocalization([50000.0], f0_base=25.0)
    # Should still map but may have warning or high error
    assert "channel_ratio" in result[0]

def test_priority_metric():
    result = map_cetacean_vocalization([18.75], f0_base=25.0)
    # 18.75/25 = 0.75 = 3/4 -> priority = 1/(3+4) = 1/7
    assert abs(result[0]["priority"] - 1/7) < 1e-6

def test_multiple_frequencies():
    freqs = [18.5, 22.3, 35.1]
    results = map_cetacean_vocalization(freqs, f0_base=25.0)
    assert len(results) == 3
    assert all("channel_ratio" in r for r in results)
