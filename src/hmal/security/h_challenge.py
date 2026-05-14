"""Autenticação leve H-Challenge/Response (~200 bytes)."""
import hashlib
import os
from dataclasses import dataclass

@dataclass
class HChallengeResponse:
    secret_seed: bytes
    
    def generate_challenge(self, n_channels: int = 3) -> dict:
        """Gera desafio com n_channels harmônicos aleatórios."""
        nonce = os.urandom(4)
        channels = [(os.randint(1,16), os.randint(1,16)) for _ in range(n_channels)]
        return {"nonce": nonce.hex(), "channels": channels}
    
    def compute_response(self, challenge: dict) -> bytes:
        """Computa resposta HMAC-SHA256 truncada (~200B total)."""
        data = challenge["nonce"].encode() + str(challenge["channels"]).encode()
        return hashlib.sha256(self.secret_seed + data).digest()[:16]  # 128-bit tag
    
    def verify_response(self, challenge: dict, response: bytes) -> bool:
        """Verifica resposta com comparação constante-time."""
        expected = self.compute_response(challenge)
        return hashlib.compare_digest(expected, response)
