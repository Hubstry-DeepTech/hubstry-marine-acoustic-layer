"""Testes estendidos do modulo security."""
from __future__ import annotations
import pytest
from hmal.security.h_challenge import HChallengeResponse
from math import gcd


@pytest.fixture
def auth():
    return HChallengeResponse(secret_seed=b"test-seed-123")


class TestChallengeGcd:
    def test_all_channels_coprime(self, auth):
        for _ in range(50):
            ch = auth.generate_challenge(n_channels=4)
            for a, b in ch["channels"]:
                assert gcd(a, b) == 1, f"canal ({a},{b}) nao coprimo"

    def test_channel_count(self, auth):
        ch = auth.generate_challenge(n_channels=8)
        assert len(ch["channels"]) == 8

    def test_valid_verify(self, auth):
        ch = auth.generate_challenge(n_channels=4)
        resp = auth.compute_response(ch)
        assert auth.verify_response(ch, resp) is True


class TestNonceUniqueness:
    def test_no_collision(self, auth):
        nonces = set()
        for _ in range(100):
            ch = auth.generate_challenge(n_channels=4)
            n = ch["nonce"]
            assert n not in nonces, f"nonce duplicado: {n}"
            nonces.add(n)

    def test_nonce_type(self, auth):
        ch = auth.generate_challenge(n_channels=4)
        assert isinstance(ch["nonce"], str)
        assert len(ch["nonce"]) > 0
