def classify_vocalization(frequency_hz: float, species: str = None) -> str:
    if frequency_hz < 50: return "infrassom_social"
    elif frequency_hz < 500: return "assobio_social"
    elif frequency_hz < 5000: return "clique_echolocalizacao"
    else: return "ultrassom_alta_resolucao"

def map_cetacean_vocalization(frequencies, f0_base=25.0, harmonic_order=16):
    results = []
    for f in frequencies:
        ratio = f / f0_base
        best = min(((a,b) for a in range(1,harmonic_order+1) for b in range(1,harmonic_order+1)), 
                   key=lambda x: abs(x[0]/x[1] - ratio))
        results.append({'frequency_hz': f, 'channel_ratio': f"{best[0]}/{best[1]}", 
                        'priority': 1/(best[0]+best[1]), 'interpretation': classify_vocalization(f)})
    return results
