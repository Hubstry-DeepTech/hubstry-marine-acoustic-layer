<p align="center">
  <a href="https://doi.org/10.5281/zenodo.20184616">
    <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.20184616.svg" alt="DOI">
  </a>
  <br>
  <strong>Hubstry Marine Acoustic Layer (HMAL)</strong>
  <br>
  <em>Protocolo de comunicação subaquática baseado em séries harmônicas racionais</em>
</p>

---

## Visão Geral

O **Hubstry Marine Acoustic Layer (HMAL)** é um protocolo de comunicação acústica subaquática adaptado do **HPG 1.0** (*Harmonic Protocol Grid*, DOI: [10.5281/zenodo.18652888](https://doi.org/10.5281/zenodo.18652888)) para o meio aquático. O HMAL utiliza séries harmônicas racionais como espaço de canais nativo, operando como *overlay* sobre o padrão NATO C2/JANUS, com autenticação leve e anti-jamming harmônico determinístico.

O HMAL é parte do ecossistema **Hubstry**, integrando-se ao **GuruDev Core** (DOI: [10.5281/zenodo.19772798](https://doi.org/10.5281/zenodo.19772798)) para análise semântica de vocalizações cetáceas.

### Publicação

O paper de referência do HMAL v1.0.0 está publicado no Zenodo:

> **Mapeamento Harmônico Racional de Vocalizações Cetáceas: Protocolo HMAL e Aplicações em Bioacústica Subaquática**
> Guilherme Gonçalves Machado (2026). Hubstry Deep Tech.
> DOI: [10.5281/zenodo.20184616](https://doi.org/10.5281/zenodo.20184616)

---

## Arquitetura do Ecossistema Hubstry

- **HPG 1.0** ([10.5281/zenodo.18652888](https://doi.org/10.5281/zenodo.18652888)): base matemática — séries harmônicas racionais como espaço de canais.
- **GuruDev Core** ([10.5281/zenodo.19772798](https://doi.org/10.5281/zenodo.19772798)): linguagem de programação ontológica — análise semântica, interoperabilidade entre semioses.
- **HMAL** ([10.5281/zenodo.20184616](https://doi.org/10.5281/zenodo.20184616)): adaptação do HPG 1.0 para o meio aquático — protocolo de comunicação subaquática.

---

## Fundamentação Teórica

### Séries Harmônicas Racionais

O conjunto harmônico de ordem *N* é definido como:

> H_N = { a/b | 1 <= a,b <= N, mdc(a,b) = 1 }

Cada elemento *a/b* define um canal de frequência *f = (a/b) · f₀*, onde *f₀* é a frequência fundamental adaptativa ao contexto de aplicação.

### Métrica de Prioridade

> P(a/b) = 1 / (a + b)

Canais com menor soma *a + b* correspondem a harmônicos de baixa ordem — os mais relevantes biologicamente por sua eficiência energética e robustez à atenuação diferencial do canal aquático.

### Espécies de Referência

| Espécie | *f₀* | Faixa Vocal | Amostra |
|---------|------|-------------|---------|
| Baleia-azul (*Balaenoptera musculus*) | 25 Hz | 10–40 Hz (infrassom) | n ≈ 1 247 |
| Golfinho-nariz-de-garrafa (*Tursiops truncatus*) | 1 732 Hz | 200 Hz–150 kHz | n ≈ 3 891 |

> **Nota**: os valores de *n* são estimativas de *desk-study* pendentes de confirmação direta com os repositórios NOAA PMEL e OBIS-SEAMAP. Consulte a Seção 3.1 do paper ([DOI: 10.5281/zenodo.20184616](https://doi.org/10.5281/zenodo.20184616)) para detalhes.

---

## Resultados Principais

- **Cobertura H₁₆**: >87% das frequências fundamentais de baleias-azuis e >84% das de golfinhos mapeadas com erro < 200 ppm.
- **Cobertura H₃₂**: >94% (baleias) e >91% (golfinhos).
- **Canais de alta prioridade** (P > 0,1): concentram >68% das vocalizações biologicamente significativas.
- **Handshake HSL**: ~200 B de *overhead*, latência < 2,1 s, taxa de falha < 1,2%.
- **Capacidade de canal**: ~26,6 kbps (teórico, B = 4 kHz, SNR = 20 dB).

---

## Protocolo HMAL

### Funcionamento

O HMAL opera como *overlay* sobre o padrão NATO C2/JANUS (7–12 kHz):

1. **Autenticação leve**: handshake HSL de ~200 bytes (vs. TLS > 1 KB).
2. **Channel hopping** harmônico determinístico: mudança de *a/b* para *c/d* em O(1) — vantagem sobre FHSS pseudoaleatório.
3. **Verificação espectral de razões**: rejeição de sinal *multipath* distorcido que não satisfaz *a/b ∈ H_N*.
4. **Rotação de chave LFSR**: determinística, sem troca de chave — ambos os lados avançam o mesmo LFSR independentemente.

### Comparação com Protocolos Existentes

| Protocolo | Autenticação | Anti-jamming | Espaço de Canais | Adaptação Bioacústica |
|-----------|-------------|--------------|------------------|----------------------|
| **HMAL (H₁₆)** | ~200 B | Harm. determinístico | 255 canais rac. | Nativa |
| NATO C2/JANUS | Nenhuma | Nenhum | FSK 7–12 kHz fixo | Arbitrária |
| EvoLogics USBL | > 1 KB (TLS) | Parcial (DSSS) | OFDM proprietário | Arbitrária |
| WHOI Micro-modem | Nenhuma | Nenhum | FSK/PSK fixo | Arbitrária |

---

## Integração com GuruDev Core

O HMAL opera na **camada de transporte** (captura, autenticação e roteamento de sinais acústicos). A **camada semântica** é fornecida pelo GuruDev Core (DOI: [10.5281/zenodo.19772798](https://doi.org/10.5281/zenodo.19772798)):

1. **Captura**: hidrofone autentica via HSL, encaminha sinal para processamento.
2. **Decomposição espectral**: FFT e mapeamento de componentes para canais H_N.
3. **Interpretação ontológica**: GuruDev recebe a sequência de canais e aplica 7 níveis de interpretação semântica.
4. **GuruMatrix 5D**: rastreamento por categoria aristotélica, nível semântico e perfil de delegação quântica.
5. **Alexandria**: vocalização cetácea como 26ª linguagem no *LanguageAnalyzer*, com perfil hexarrelacional próprio.

> O resultado não é tradução direta — é mapeamento ontológico: identificação de estruturas funcionais análogas entre a semiose cetácea e semioses humanas computacionais.

---

## Ética e Governança Dual-Use

O HMAL adota o **Princípio de Não-Interferência** como fronteira ética inviolável:

- Emissão ativa restrita a < 180 dB re 1 µPa @ 1 m (limiar NOAA NMFS-OPR-55).
- Faixas críticas de vocalização (40 Hz baleias, 8–16 kHz golfinhos) excluídas do *channel hopping* por padrão.
- Logs imutáveis de emissão para auditoria (IBAMA, NOAA, IMO).
- Uso dual militar: exclusivamente comunicações táticas. Nenhuma aplicação em sistemas de armas.

---

## Datasets e Reprodutibilidade

- **Baleias-azuis**: NOAA PMEL — Pacific Ocean Acoustics Group. Acesso: <https://www.pmel.noaa.gov/acoustics/>
- **Golfinhos**: OBIS-SEAMAP — repositório DolphinBank. Acesso: <https://seamap.env.duke.edu/>
- **Paper e código**: disponíveis no Zenodo — DOI: [10.5281/zenodo.20184616](https://doi.org/10.5281/zenodo.20184616)

---

## Licença

Este projeto é distribuído sob a licença **CC-BY-4.0** (Creative Commons Atribuição 4.0 Internacional).

---

## Autor

**Guilherme Gonçalves Machado**
Hubstry Deep Tech — Rio de Janeiro, Brasil
ORCID: [0009-0008-1083-0784](https://orcid.org/0009-0008-1083-0784)
E-mail: guilhermemachado.ceo@hubstry.dev
Web: <https://hubstry.dev>

---

## Como Citar

```bibtex
@misc{machado2026hmal,
  author       = {Machado, Guilherme Gonçalves},
  title        = {Mapeamento Harmônico Racional de Vocalizações Cetáceas:
                  Protocolo HMAL e Aplicações em Bioacústica Subaquática},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20184616},
  version      = {1.0.0}
}
| Recurso | DOI | Link |
|---------|-----|------|
| **HPG 1.0** (base matemática) | 10.5281/zenodo.18652888 | [Zenodo](https://doi.org/10.5281/zenodo.18652888) |
| **GuruDev Core** (ontologia) | 10.5281/zenodo.19772798 | [Zenodo](https://doi.org/10.5281/zenodo.19772798) |
| **Semiografia** | 10.5281/zenodo.19546051 | [Zenodo](https://doi.org/10.5281/zenodo.19546051) |
| **HMAL** (este trabalho) | 10.5281/zenodo.20184616 | [Zenodo](https://doi.org/10.5281/zenodo.20184616) |
