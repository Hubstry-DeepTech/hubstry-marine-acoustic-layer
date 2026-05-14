# Hubstry Marine Acoustic Layer (HMAL)

> Protocolo de comunicação acústica subaquática baseado em séries harmônicas racionais

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL_1.1-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-2_passed-green)](tests/)

## 🌊 Visão

Adaptação do protocolo Hubstry IoT (HPG 1.0) para o meio aquático, utilizando séries harmônicas racionais como base para:

- **Bioacústica científica**: mapeamento de vocalizações cetáceas para canais racionais a/b
- **Monitoramento ambiental**: sensores subaquáticos para conservação marinha
- **Comunicação segura**: autenticação leve (~200 B) + anti-jamming harmônico + gateway JANUS

## 🚀 Instalação Rápida

```bash
git clone https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer.git
cd hubstry-marine-acoustic-layer
python -m pip install numpy scipy ply pytest
python -m pytest tests/ -v
from hmal.core import HarmonicProtocol, RationalChannel
hp = HarmonicProtocol(f0_base=25.0, mode="whale")
channel = RationalChannel(3, 4)
print(f"Frequência: {channel.frequency(hp.f0_adaptive)} Hz")
# Saída: Frequência: 18.75 Hz
📚 Documentação
Arquivo
Descrição
docs/SPECIFICATION.md
Especificação técnica do protocolo
docs/DEPLOYMENT.md
Guia de implantação em sensores/ROVs
docs/ETHICS_GUIDELINES.md
Diretrizes éticas: não-interferência com cetáceos
docs/ZENODO_PAPER/manuscript.md
Paper para submissão ao Zenodo
⚖️ Licença
Dados e paper: CC-BY-4.0 (aberto para ciência)
Código de segurança: BSL-1.1 (uso comercial requer autorização)
Código core: MIT (para pesquisa e desenvolvimento)
📬 Contato
Autor: Guilherme Gonçalves Machado
Email: guilhermemachado.ceo@hubstry.dev
ORCID: 0009-0008-1083-0784
Site: hubstry.dev
© 2026 Hubstry Deep Tech — Rio de Janeiro, Brasil
