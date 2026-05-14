"""Mapeamento de vocalizacoes cetaceas para canais harmonicos racionais H_N."""
from __future__ import annotations
import warnings
from math import gcd
from functools import lru_cache


@lru_cache(maxsize=None)
def _build_hn(harmonic_order: int) -> list[tuple[int, int]]:
    return [(a, b) for a in range(1, harmonic_order + 1)
            for b in range(1, harmonic_order + 1) if gcd(a, b) == 1]


def classify_vocalization(frequency_hz: float, species: str | None = None) -> str:
    species_lower = (species or "").lower()
    whale_species = {"blue_whale", "fin_whale", "humpback_whale", "sei_whale"}
    if frequency_hz < 50:
        return "infrassom_social" if species_lower in whale_species else "infrassom_navegacao"
    elif frequency_hz < 500:
        return "assobio_social"
    elif frequency_hz < 5000:
        return "clique_echolocalizacao"
    else:
        return "ultrassom_alta_resolucao"


def map_cetacean_vocalization(
    frequencies: list[float],
    f0_base: float = 25.0,
    harmonic_order: int = 16,
    tolerance: float = 1e-4,
    species: str | None = None,
) -> list[dict]:
    if f0_base <= 0:
        raise ValueError(f"f0_base deve ser positivo; recebido: {f0_base}")
    if harmonic_order < 1:
        raise ValueError(f"harmonic_order deve ser >= 1; recebido: {harmonic_order}")
    candidates = _build_hn(harmonic_order)
    if not candidates:
        raise RuntimeError(f"H_{harmonic_order} esta vazio.")
    tolerance_ppm = tolerance * 1_000_000
    results = []
    for f_obs in frequencies:
        if f_obs <= 0:
            warnings.warn(f"Frequencia nao-positiva ignorada: {f_obs} Hz", UserWarning, stacklevel=2)
            continue
        ratio = f_obs / f0_base
        best_a, best_b = min(candidates, key=lambda ab: abs(ab[0] / ab[1] - ratio))
        error_ppm = abs(best_a / best_b - ratio) / ratio * 1_000_000
        within_tolerance = error_ppm < tolerance_ppm
        if not within_tolerance:
            warnings.warn(
                f"Frequencia {f_obs:.2f} Hz mapeada para {best_a}/{best_b} "
                f"com erro {error_ppm:.1f} ppm > tolerancia {tolerance_ppm:.0f} ppm.",
                UserWarning, stacklevel=2)
        results.append({
            "frequency_hz": f_obs, "channel_ratio": f"{best_a}/{best_b}",
            "channel_a": best_a, "channel_b": best_b,
            "priority": 1.0 / (best_a + best_b),
            "error_ppm": round(error_ppm, 2), "within_tolerance": within_tolerance,
            "biological_interpretation": classify_vocalization(f_obs, species),
        })
    return results
