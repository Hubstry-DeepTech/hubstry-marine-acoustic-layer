"""Referência idealizada de erro de identificação de canal (lab/BENCH_CRITERIA_v0.4-draft.md, Seção 2.1).

Modelo: detecção não coerente M-ária com sinais ortogonais de mesma energia em ruído branco gaussiano.
Escolhe-se o canal com maior envoltória; erra-se quando alguma das M-1 envoltórias de ruído supera a do canal
verdadeiro. Com r a envoltória normalizada do canal verdadeiro (Rice, parâmetro a = sqrt(2·Es/N0)):

    P_e = ∫_0^∞ r·exp(-(r² + a²)/2)·I0(a·r)·[1 - (1 - exp(-r²/2))^(M-1)] dr

Correspondência com a bancada: SNR_int = A²N/(2σ²) = Es/σ², com Es = A²N/2 e densidade espectral bilateral
N0/2 = σ²; logo Es/N0 = SNR_int/2.

Limitação: o dicionário H_16 não é ortogonal (correlação máxima entre canais de 8,4% em hf e 12,7% em lf),
e o receptor refina a frequência em vez de testar só as candidatas. O valor é uma referência sob modelo
idealizado, não um limite de qualquer receptor.

Uso: python lab/bench/ideal_pe.py [--m 159] [--snr 10 12 14 16 18 20 22]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import integrate, special


def ideal_pe(snr_int_db: float, m: int = 159) -> float:
    es_n0 = 10 ** (snr_int_db / 10) / 2
    a = np.sqrt(2 * es_n0)

    def f(r: float) -> float:
        # i0e(x) = exp(-x)·I0(x): exp(-(r²+a²)/2)·I0(a r) = exp(-(r-a)²/2)·i0e(a r)
        rice = r * np.exp(-((r - a) ** 2) / 2) * special.i0e(a * r)
        # 1 - (1 - e^{-r²/2})^{m-1}, calculado sem cancelamento
        miss = -np.expm1((m - 1) * np.log1p(-np.exp(-r * r / 2))) if r > 0 else 1.0
        return rice * miss

    val, _ = integrate.quad(f, 0, a + 40, points=[a], limit=500, epsabs=0, epsrel=1e-10)
    return float(val)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=159)
    ap.add_argument("--snr", type=float, nargs="+", default=[10, 12, 14, 16, 18, 20, 22])
    a = ap.parse_args()
    rows = {f"{s:g}": ideal_pe(s, a.m) for s in a.snr}
    out = {
        "model": "M-ary noncoherent orthogonal, equal energy, AWGN; Es/N0 = SNR_int/2",
        "M": a.m,
        "pe_by_snr_int_db": rows,
        "expected_errors_per_1000": {k: 1000 * v for k, v in rows.items()},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
