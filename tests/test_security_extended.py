import pytest
from hmal.security import HChallengeResponse, JanusGateway, JanusCompatibilityMode

def test_hcr_generate_challenge():
    hcr = HChallengeResponse(b"seed_test_123")
    challenge = hcr.generate_challenge()
    assert "nonce" in challenge
    assert "channels" in challenge
    assert len(challenge["channels"]) >= 1

def test_hcr_full_cycle():
    hcr = HChallengeResponse(b"seed_test_123")
    challenge = hcr.generate_challenge()
    response = hcr.compute_response(challenge)
    assert hcr.verify_response(challenge, response) is True

def test_hcr_tamper_detection():
    hcr = HChallengeResponse(b"seed_test_123")
    challenge = hcr.generate_challenge()
    response = hcr.compute_response(challenge)
    tampered = bytes([b ^ 0xFF for b in response])
    assert hcr.verify_response(challenge, tampered) is False

def test_janus_gateway_modes():
    gw_overlay = JanusGateway(JanusCompatibilityMode.OVERLAY)
    gw_standalone = JanusGateway(JanusCompatibilityMode.STANDALONE)
    assert gw_overlay.mode == JanusCompatibilityMode.OVERLAY
    assert gw_standalone.mode == JanusCompatibilityMode.STANDALONE

def test_janus_band_clamp():
    gw = JanusGateway()
    assert gw.align_to_janus_band(5000) == 7000
    assert gw.align_to_janus_band(9500) == 9500
    assert gw.align_to_janus_band(15000) == 12000

def test_janus_wrap_unwrap():
    gw = JanusGateway()
    original = b"JANUS_PAYLOAD_TEST_123"
    wrapped = gw.wrap_janus(original)
    assert wrapped.startswith(b"HMALv1")
    assert gw.unwrap_janus(wrapped) == original

def test_janus_invalid_header():
    gw = JanusGateway()
    with pytest.raises(ValueError):
        gw.unwrap_janus(b"INVALID_HEADER" + b"\x00\x10" + b"payload")
