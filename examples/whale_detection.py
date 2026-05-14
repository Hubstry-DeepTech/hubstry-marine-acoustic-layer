#!/usr/bin/env python3
"""Pipeline de detecção de vocalizações de baleia-azul."""
from hmal.core import HarmonicProtocol
from hmal.bioacoustics import map_cetacean_vocalization

def detect_blue_whale(frequencies_hz):
    hp = HarmonicProtocol(f0_base=25.0, mode="whale")
    results = map_cetacean_vocalization(frequencies_hz, hp.f0_adaptive, species="blue_whale")
    mapped = [r for r in results if r.get("channel_ratio")]
    social = [r for r in results if r.get("interpretation") == "infrassom_social"]
    return {
        "total": len(frequencies_hz),
        "mapped": len(mapped),
        "social": len(social),
        "channels": list(set(r["channel_ratio"] for r in mapped))
    }

if __name__ == "__main__":
    sample = [18.5, 22.3, 27.8, 35.1, 39.9]
    stats = detect_blue_whale(sample)
    print("🐋 Detecção de Baleia-Azul — HMAL")
    print(f"  Analisadas: {stats['total']}")
    print(f"  Mapeadas: {stats['mapped']} ({stats['mapped']/stats['total']*100:.1f}%)")
    print(f"  Sociais: {stats['social']}")
    print(f"  Canais: {', '.join(stats['channels'])}")
