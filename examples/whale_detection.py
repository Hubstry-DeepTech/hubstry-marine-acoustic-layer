#!/usr/bin/env python3
"""
Exemplo: Pipeline de detecção de vocalizações de baleia-azul.
Uso: python examples/whale_detection.py
"""
from hmal.core import HarmonicProtocol
from hmal.bioacoustics import map_cetacean_vocalization, classify_vocalization

def detect_blue_whale_vocalizations(frequencies_hz: list[float]) -> dict:
    """
    Detecta e classifica vocalizações de baleia-azul.
    
    Args:
        frequencies_hz: Lista de frequências observadas (Hz)
    
    Returns:
        Dict com estatísticas de detecção
    """
    hp = HarmonicProtocol(f0_base=25.0, mode="whale")
    results = map_cetacean_vocalization(frequencies_hz, hp.f0_adaptive, species="blue_whale")
    
    # Estatísticas
    mapped = [r for r in results if r.get("channel_ratio") is not None]
    social_calls = [r for r in results if r.get("interpretation") == "infrassom_social"]
    
    return {
        "total_detected": len(frequencies_hz),
        "successfully_mapped": len(mapped),
        "social_calls": len(social_calls),
        "avg_error_ppm": sum(r["error_ppm"] for r in mapped) / len(mapped) if mapped else None,
        "channels_used": list(set(r["channel_ratio"] for r in mapped))
    }

if __name__ == "__main__":
    # Dados simulados de vocalização
    sample_frequencies = [18.5, 22.3, 27.8, 35.1, 39.9]
    stats = detect_blue_whale_vocalizations(sample_frequencies)
    
    print("🐋 Detecção de Baleia-Azul — HMAL")
    print(f"  Frequências analisadas: {stats['total_detected']}")
    print(f"  Mapeadas com sucesso: {stats['successfully_mapped']} ({stats['successfully_mapped']/stats['total_detected']*100:.1f}%)")
    print(f"  Chamados sociais: {stats['social_calls']}")
    print(f"  Erro médio: {stats['avg_error_ppm']:.1f} ppm")
    print(f"  Canais utilizados: {', '.join(stats['channels_used'])}")
