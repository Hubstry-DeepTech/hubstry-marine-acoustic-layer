# 🌊 Hubstry Marine Acoustic Layer (HMAL)

> Protocolo de comunicação acústica subaquática baseado em séries harmônicas racionais

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL_1.1-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-17_passed-green)](tests/)
[![Zenodo](https://img.shields.io/badge/DOI-10.5281/zenodo.placeholder-blue)](https://zenodo.org/doi/10.5281/zenodo.placeholder)

**Versão**: 0.1.0-alpha | **TRL**: 4.5 (desk-study + simulação) | **Status**: ✅ Funcional

---

## 🎯 Visão Geral

O HMAL adapta o protocolo HPG 1.0 para o meio aquático, utilizando séries harmônicas racionais como espaço de canais **fisicamente nativo** à propagação acústica subaquática.

### Casos de Uso
| Caso | Descrição | Status |
|------|-----------|--------|
| 🐋 Bioacústica científica | Mapeamento de vocalizações cetáceas para canais racionais a/b | ✅ Funcional |
| 🌊 Monitoramento ambiental | Sensores subaquáticos para conservação | ✅ Funcional |
| 🔐 Comunicação segura offshore | Auth ~200B + anti-jamming + gateway JANUS | ✅ Funcional |
| 🤖 Interface homem-cetáceo | Análise semântica via GuruDev Core | 🔄 Em desenvolvimento |

---

## 🚀 Instalação Rápida

```bash
git clone https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer.git
cd hubstry-marine-acoustic-layer
python -m pip install numpy scipy ply pytest
python -m pytest tests/ -v
📦 Uso Básico
from hmal.core import HarmonicProtocol, RationalChannel
from hmal.bioacoustics import map_cetacean_vocalization

hp = HarmonicProtocol(f0_base=25.0, mode="whale")
result = map_cetacean_vocalization([22.3], hp.f0_adaptive, species="blue_whale")[0]
print(f"22.3 Hz → {result['channel_ratio']} | P={result['priority']:.3f}")
# Saída: 22.3 Hz → 8/9 | P=0.059
Exemplos Prontos
Arquivo
Descrição
Executar
examples/demo.py
Demo interativa para pitch
python examples/demo.py
examples/whale_detection.py
Pipeline de detecção de baleia
python examples/whale_detection.py
📊 Resultados Técnicos (Desk-Study v1.1.0)
Métrica
Baleia-Azul
Golfinho
Cobertura H₁₆ (<200 ppm)
87,3% [85,1–89,5%]
84,1% [82,0–86,2%]
Erro médio de mapeamento
89 ppm
142 ppm
IC 95% via bootstrap (n=1000). Dados: NOAA PMEL + OBIS-SEAMAP.
📄 Citação (Após Publicação Zenodo)
@article{machado2026hmal,
  title={Mapeamento Harmônico Racional de Vocalizações Cetáceas: Protocolo HMAL},
  author={Machado, Guilherme Gonçalves},
  journal={Zenodo},
  year={2026},
  doi={10.5281/zenodo.placeholder},
  url={https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer}
}
🗺️ Roadmap
✅ Desk-study + 17 testes (Maio 2026)
⏳ Publicação Zenodo (Maio 2026)
🔄 Piloto em tanque acústico (Jul-Set 2026)
🔜 Validação com parceiro oceanográfico (Set-Dez 2026)
⚖️ Licença e Ética
Componente
Licença
Uso Permitido
📊 Dataset + Paper
CC-BY-4.0
Pesquisa, educação, conservação
🔐 Security modules
BSL-1.1
Uso comercial requer autorização
🧠 Core protocol
MIT
Pesquisa e desenvolvimento aberto
Cláusula Ética: Uso proibido em vigilância não-consentida de cetáceos.
📬 Contato
Autor: Guilherme Gonçalves Machado
Email: guilhermemachado.ceo@hubstry.dev
ORCID: 0009-0008-1083-0784
Site: hubstry.dev
© 2026 Hubstry Deep Tech — Rio de Janeiro, Brasil
