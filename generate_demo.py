#!/usr/bin/env python3
# generate_demo.py - Cria examples/demo.py sem problemas de encoding
code = '''#!/usr/bin/env python3
"""Demo interativo do HMAL ? para pitch t?cnico e onboarding."""
from hmal.core import HarmonicProtocol, RationalChannel
from hmal.bioacoustics import map_cetacean_vocalization

def main():
    print("?? HMAL Demo ? Hubstry Marine Acoustic Layer v0.1.0")
    print("=" * 60)
    
    print("\\n?? Modo Baleia-Azul (f? = 25 Hz)")
    hp_whale = HarmonicProtocol(f0_base=25.0, mode="whale")
    for f in [18.5, 22.3, 35.1]:
        r = map_cetacean_vocalization([f], hp_whale.f0_adaptive)[0]
        print(f"  {f:5.1f} Hz -> {r['channel_ratio']:>4} | P={r['priority']:.3f} | {r['interpretation']}")
    
    print("\\n?? Modo Golfinho (f? = 1732 Hz)")
    hp_dolphin = HarmonicProtocol(f0_base=1732.0, mode="dolphin")
    for f in [4500, 8200, 12000]:
        r = map_cetacean_vocalization([f], hp_dolphin.f0_adaptive)[0]
        print(f"  {f:5.0f} Hz -> {r['channel_ratio']:>4} | P={r['priority']:.3f} | {r['interpretation']}")
    
    print("\\n?? Autentica??o H-Challenge (~200 B)")
    from hmal.security import HChallengeResponse
    hcr = HChallengeResponse(b"demo_2026")
    ch = hcr.generate_challenge()
    resp = hcr.compute_response(ch)
    print(f"  Challenge: {ch['channels']}")
    print(f"  Verified: {hcr.verify_response(ch, resp)}")
    
    print("\\n" + "=" * 60)
    print("? Demo conclu?da")

if __name__ == "__main__":
    main()
'''
with open("examples/demo.py", "w", encoding="utf-8") as f:
    f.write(code)
print("OK: examples/demo.py criado")
