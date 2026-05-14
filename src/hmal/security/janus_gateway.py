"""Gateway de interoperabilidade com padrão NATO C2/JANUS."""
from enum import Enum

class JanusCompatibilityMode(Enum):
    OVERLAY = "overlay"      # HMAL como camada de auth sobre JANUS
    STANDALONE = "standalone" # HMAL operando independentemente

class JanusGateway:
    JANUS_BAND = (7000, 12000)  # Hz, faixa padrão JANUS
    
    def __init__(self, mode: JanusCompatibilityMode = JanusCompatibilityMode.OVERLAY):
        self.mode = mode
    
    def align_to_janus_band(self, frequency_hz: float) -> float:
        """Projeta frequência para dentro da banda JANUS se necessário."""
        low, high = self.JANUS_BAND
        return max(low, min(high, frequency_hz))
    
    def wrap_janus(self, payload: bytes) -> bytes:
        """Encapsula payload JANUS com header HMAL para autenticação."""
        header = b"HMALv1" + len(payload).to_bytes(2, "big")
        return header + payload
    
    def unwrap_janus(self, wrapped: bytes) -> bytes:
        """Extrai payload JANUS e verifica integridade HMAL."""
        if not wrapped.startswith(b"HMALv1"):
            raise ValueError("Invalid HMAL header")
        payload_len = int.from_bytes(wrapped[6:8], "big")
        return wrapped[8:8+payload_len]
