"""Autenticacao leve H-Challenge/Response (~200 bytes).
Seguranca: usa secrets.randbelow.
"""
import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from math import gcd


@dataclass
class HChallengeResponse:
    secret_seed: bytes

    def generate_challenge(self, n_channels: int = 3) -> dict:
        nonce = os.urandom(4)
        channels = []
        attempts = 0
        while len(channels) < n_channels:
            a = secrets.randbelow(15) + 1
            b = secrets.randbelow(15) + 1
            if gcd(a, b) == 1:
                channels.append((a, b))
            attempts += 1
            if attempts > 1000:
                raise RuntimeError("Falha ao gerar canais validos.")
        return {"nonce": nonce.hex(), "channels": channels}

    def compute_response(self, challenge: dict) -> bytes:
        data = challenge["nonce"].encode() + str(challenge["channels"]).encode()
        return hashlib.sha256(self.secret_seed + data).digest()[:16]

    def verify_response(self, challenge: dict, response: bytes) -> bool:
        expected = self.compute_response(challenge)
        return hmac.compare_digest(expected, response)
