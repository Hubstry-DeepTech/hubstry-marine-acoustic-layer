#!/usr/bin/env python3
"""
Demo interativo do HMAL — para pitch técnico e onboarding.
Execução: python examples/demo.py
"""
from hmal.core import HarmonicProtocol, RationalChannel
from hmal.bioacoustics import map_cetacean_vocalization

def main():
    print("🌊 HMAL Demo — Hubstry Marine Acoustic Layer v0.1.0")
    print("=" * 60)
    
    # Modo baleia
    print("\n🐋 Modo Baleia-Azul (f₀ = 25 Hz)")
    hp_whale = HarmonicProtocol(f0_base=25.0, mode="whale")
    vocals_whale = [18.5, 22.3, 35.1]
    for f in vocals_whale:
        result = map_cetacean_vocalization([f], hp_whale.f0_adaptive)[0]
        print(f"  {f:5.1f} Hz -> {result['channel_ratio']:>4} | P={result['priority']:.3f} | {result['interpretation']}")
    
    # Modo golfinho
    print("\n🐬 Modo Golfinho (f₀ = 1732 Hz)")
    hp_dolphin = HarmonicProtocol(f0_base=1732.0, mode="dolphin")
    vocals_dolphin = [4500, 8200, 12000]
    for f in vocals_dolphin:
        result = map_cetacean_vocalization([f], hp_dolphin.f0_adaptive)[0]
        print(f"  {f:5.0f} Hz -> {result['channel_ratio']:>4} | P={result['priority']:.3f} | {result['interpretation']}")
    
    # Security demo
    print("\n🔐 Autenticação H-Challenge (~200 B)")
    from hmal.security import HChallengeResponse
    hcr = HChallengeResponse(b"demo_seed_2026")
    challenge = hcr.generate_challenge()
    print(f"  Challenge: {challenge['channels']}")
    response = hcr.compute_response(challenge)
    print(f"  Response size: {len(response)} bytes")
    print(f"  Verified: {hcr.verify_response(challenge, response)}")
    
    print("\n" + "=" * 60)
    print("✅ Demo concluída — pronto para campo e investidores")

if __name__ == "__main__":
    main()
