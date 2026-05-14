# -*- coding: utf-8 -*-
"""Exemplo: deteccao de vocalizacoes de baleias usando HMAL."""
from __future__ import annotations

from hmal.bioacoustics.vocalization_mapper import map_cetacean_vocalization
from hmal.core.harmonic_protocol import HarmonicProtocol


def main() -> None:
    # Frequencias observadas (Hz) de uma gravacao hipotetica
    observed = [25.0, 50.0, 75.0, 100.0, 200.0, 300.0, 450.0, 600.0]

    # Mapeamento com tolerancia padrao
    results = map_cetacean_vocalization(
        frequencies=observed,
        f0_base=25.0,
        harmonic_order=16,
        tolerance=1e-4,
        species="blue_whale",
    )

    print("=== Mapeamento Harmonico ===")
    for r in results:
        tol_mark = "OK" if r["within_tolerance"] else "EXCEDIDA"
        print(
            f"  {r['frequency_hz']:7.1f} Hz -> {r['channel_ratio']:>4s} "
            f"(err {r['error_ppm']:8.2f} ppm, {tol_mark}) "
            f"-> {r['biological_interpretation']}"
        )

    # Geracao de waveform sintetico
    protocol = HarmonicProtocol(f0_base=25.0, harmonic_order=16, mode="hybrid")
    channels = [(r["channel_a"], r["channel_b"]) for r in results[:4]]
    t, waveform = protocol.generate_waveform(channels, duration=0.1, sample_rate=48000)
    sync_w = protocol.sync_window(channels)

    print(f"\nWaveform: {len(t)} amostras, peak={waveform.max():.4f}")
    print(f"Janela de sincronia: {sync_w:.6f} s")

    # f0 adaptativo por SNR
    for snr in [0, 10, 20, 30]:
        f0 = protocol.set_adaptive_f0(snr_db=float(snr))
        print(f"  SNR={snr:2d} dB -> f0_adaptativo = {f0:.2f} Hz")


if __name__ == "__main__":
    main()
