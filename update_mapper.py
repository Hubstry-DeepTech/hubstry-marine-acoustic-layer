#!/usr/bin/env python3
# update_mapper.py - Atualiza vocalization_mapper.py com suporte a species
content = '''def classify_vocalization(frequency_hz: float, species: str = None) -> str:
    if frequency_hz < 50:
        return "infrassom_social" if (species or "").lower() in ("blue_whale", "fin_whale") else "infrassom_navegacao"
    elif frequency_hz < 500:
        return "assobio_social"
    elif frequency_hz < 5000:
        return "clique_echolocalizacao"
    else:
        return "ultrassom_alta_resolucao"

def map_cetacean_vocalization(frequencies, f0_base=25.0, harmonic_order=16, species: str = None):
    results = []
    for f in frequencies:
        ratio = f / f0_base
        best = min(((a,b) for a in range(1,harmonic_order+1) for b in range(1,harmonic_order+1)), 
                   key=lambda x: abs(x[0]/x[1] - ratio))
        results.append({
            'frequency_hz': f,
            'channel_ratio': f"{best[0]}/{best[1]}", 
            'priority': 1/(best[0]+best[1]),
            'interpretation': classify_vocalization(f, species)
        })
    return results
'''
with open('src/hmal/bioacoustics/vocalization_mapper.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("? vocalization_mapper.py atualizado")
