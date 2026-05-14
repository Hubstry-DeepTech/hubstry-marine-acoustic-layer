# Hubstry Marine Acoustic Layer (HMAL)

> Protocolo de comunicação acústica subaquática baseado em séries harmônicas racionais

[![CI](https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer/actions/workflows/ci.yml/badge.svg)](https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer/actions)
[![License: BSL 1.1](https://img.shields.io/badge/License-BSL_1.1-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

## Visão

Adaptação do protocolo Hubstry IoT para meio aquático:

- **Bioacústica científica**: mapeamento vocalizações para canais racionais a/b
- **Monitoramento ambiental**: sensores para conservação marinha
- **Comunicação segura**: autenticação leve + anti-jamming + gateway JANUS

## Instalação

```bash
git clone https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer.git
cd hubstry-marine-acoustic-layer
python -m pip install numpy scipy ply pytest
python -m pytest tests/ -v
```

## Uso

```python
from hmal.core import HarmonicProtocol, RationalChannel

hp = HarmonicProtocol(25.0, mode="whale")
ch = RationalChannel(3, 4)
print(ch.frequency(hp.f0_adaptive))
```

## Contato

Guilherme G. Machado | guilhermemachado.ceo@hubstry.dev | ORCID: 0009-0008-1083-0784

© 2026 Hubstry Deep Tech — Rio de Janeiro, Brasil
