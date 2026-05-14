# Hubstry Marine Acoustic Layer (HMAL)

> Protocolo de comunicacao acustica subaquatica baseado em series harmonicas racionais

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL_1.1-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-17_passed-green)](tests/)
[![Zenodo](https://img.shields.io/badge/DOI-10.5281/zenodo.placeholder-blue)](https://zenodo.org/doi/10.5281/zenodo.placeholder)

**Versao**: 0.1.0-alpha | **TRL**: 4.5 (desk-study + simulacao) | **Status**: Funcional

---

## Visao Geral

O HMAL adapta o protocolo [HPG 1.0](https://github.com/Hubstry-DeepTech/iot-hubstry-protocol) para o meio aquatico, utilizando series harmonicas racionais como espaco de canais fisicamente nativo a propagacao acustica subaquatica. Integra-se com o [GuruDev Core](https://github.com/Hubstry-DeepTech/gurudev-core) para analise semantica ontologica de vocalizacoes.

### Ecossistema Hubstry
| Repositorio | Funcao | Status |
|-------------|--------|--------|
| [iot-hubstry-protocol](https://github.com/Hubstry-DeepTech/iot-hubstry-protocol) | HPG 1.0: base matematica de series harmonicas racionais | Publicado |
| [hubstry-marine-acoustic-layer](https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer) | HMAL: adaptacao aquatico do HPG 1.0 | Funcional |
| [gurudev-core](https://github.com/Hubstry-DeepTech/gurudev-core) | Plataforma semantica para analise ontologica | Publicado |

### Casos de Uso HMAL
| Caso | Descricao | Status |
|------|-----------|--------|
| Bioacustica cientifica | Mapeamento de vocalizacoes cetaceas para canais racionais a/b | Funcional |
| Monitoramento ambiental | Sensores subaquaticos para conservacao | Funcional |
| Comunicacao segura offshore | Auth ~200B + anti-jamming + gateway JANUS | Funcional |
| Interface homem-cetaceo | Analise semantica via GuruDev Core | Em desenvolvimento |

---

## Instalacao Rapida

    git clone https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer.git
    cd hubstry-marine-acoustic-layer
    python -m pip install numpy scipy ply pytest
    python -m pytest tests/ -v

---

## Uso Basico

    from hmal.core import HarmonicProtocol, RationalChannel
    from hmal.bioacoustics import map_cetacean_vocalization

    hp = HarmonicProtocol(f0_base=25.0, mode="whale")
    result = map_cetacean_vocalization([22.3], hp.f0_adaptive, species="blue_whale")[0]
    print(f"22.3 Hz -> {result['channel_ratio']} | P={result['priority']:.3f}")

### Exemplos Prontos
| Arquivo | Descricao | Executar |
|---------|-----------|----------|
| examples/demo.py | Demo interativa para pitch | python examples/demo.py |
| examples/whale_detection.py | Pipeline de deteccao de baleia | python examples/whale_detection.py |

---

## Resultados Tecnicos (Desk-Study v1.1.0)

| Metrica | Baleia-Azul | Golfinho |
|---------|-------------|----------|
| Cobertura H16 (<200 ppm) | 87,3% [85,1-89,5%] | 84,1% [82,0-86,2%] |
| Erro medio de mapeamento | 89 ppm | 142 ppm |

*IC 95% via bootstrap (n=1000). Dados: NOAA PMEL + OBIS-SEAMAP.*

---

## Integracao com Ecossistema Hubstry

### Com HPG 1.0 (iot-hubstry-protocol)
O HMAL herda a estrutura matematica do [HPG 1.0](https://github.com/Hubstry-DeepTech/iot-hubstry-protocol):
- Series harmonicas racionais H_N = {a/b | 1<=a,b<=N, gcd(a,b)=1}
- Metrica de prioridade P(a/b) = 1/(a+b)
- Janela de sincronizacao T_sync = lcm(b1,...,bk)/f0

### Com GuruDev Core (analise semantica)
O pipeline ontologico conecta HMAL -> GuruDev:
    from hmal.gurudev import ontology_bridge
    semantic_vector = ontology_bridge.map_vocalization_to_ontology(
        mapped_channel, 
        dispatch_level=5
    )
Detalhes: [gurudev-core/README.md](https://github.com/Hubstry-DeepTech/gurudev-core)

---

## Citacao (Apos Publicacao Zenodo)

    @article{machado2026hmal,
      title={Mapeamento Harmonico Racional de Vocalizacoes Cetaceas: Protocolo HMAL},
      author={Machado, Guilherme Goncalves},
      journal={Zenodo},
      year={2026},
      doi={10.5281/zenodo.placeholder},
      url={https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer}
    }

---

## Roadmap do Ecossistema
- HPG 1.0 publicado (Maio 2026)
- HMAL desk-study + 17 testes (Maio 2026)
- Publicacao Zenodo HMAL (Maio 2026)
- Integracao GuruDev em prototipo (Q3 2026)
- Validacao em campo com parceiros (Jul-Dez 2026)

---

## Licenca e Etica
| Componente | Licenca | Uso Permitido |
|------------|---------|--------------|
| Dataset + Paper | CC-BY-4.0 | Pesquisa, educacao, conservacao |
| Security modules | BSL-1.1 | Uso comercial requer autorizacao |
| Core protocol | MIT | Pesquisa e desenvolvimento aberto |

**Clausula Etica**: Uso proibido em vigilancia nao-consentida de cetaceos.

---

## Contato
- **Autor**: Guilherme Goncalves Machado
- **Email**: guilhermemachado.ceo@hubstry.dev
- **ORCID**: [0009-0008-1083-0784](https://orcid.org/0009-0008-1083-0784)
- **Site**: [hubstry.dev](https://hubstry.dev)
- **Ecossistema**: [Hubstry-DeepTech](https://github.com/Hubstry-DeepTech)

(c) 2026 Hubstry Deep Tech - Rio de Janeiro, Brasil
