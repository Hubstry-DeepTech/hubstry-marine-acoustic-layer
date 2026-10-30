# Especificação Técnica: HMAL v0.1.0

> Hubstry Marine Acoustic Layer — Protocolo de comunicação acústica subaquática baseado em séries harmônicas racionais

**Versão**: 0.1.0-alpha | **Status**: maturidade avaliada por componente (ver tabela abaixo) | **Licença**: BSL-1.1 + CC-BY-4.0


| Linha | Avaliação atual | Meta |
|---|---|---|
| Núcleo computacional racional (`H_N`, canais, formas de onda, sincronização) | Prova de conceito implementada e testada: TRL 3 | TRL 4 do subsistema, conforme `lab/BENCH_CRITERIA.md` |
| Comunicação acústica submarina | Arquitetura e módulos experimentais, sem cadeia física testada | Bancada eletroacústica (*breadboard*) em parceria |
| Hipótese bioacústica H1 | Protocolo exploratório pré-registrado; TRL não se aplica a hipótese científica | Avaliação científica com replicação independente |
| H3 — controle de qualidade de detecções PAMGuard | Aplicação de engenharia em investigação | Benchmark com rótulos independentes |

---

## 1. Visão Geral

O HMAL adapta o protocolo HPG 1.0 (Harmonic Protocol Grid) para o meio aquático, utilizando séries harmônicas racionais como espaço de canais nativo. Se vocalizações de cetáceos guardam relações informativas com esse formalismo é uma pergunta de pesquisa em aberto, tratada no pré-registro (`lab/PREREGISTRATION.md`), e não uma premissa do protocolo.

### Casos de Uso
| Caso | Descrição | Prioridade |
|------|-----------|------------|
| Bioacústica científica | Mapeamento de vocalizações cetáceas para análise comportamental | Alta |
| Monitoramento ambiental | Sensores subaquáticos para conservação e detecção de impacto antrópico | Alta |
| Comunicação segura offshore | Autenticação leve para ROVs, dutos e UUVs | Média |
| Interface homem-cetáceo | Protótipo de decodificação semântica de vocalizações | Baixa (futuro) |

---

## 2. Arquitetura

### 2.1 Pilha de Protocolo (Adaptação OSI)
```
┌─────────────────────────┐
│ Aplicação               │ ← GuruDev bridge (opcional)
├─────────────────────────┤
│ Segurança (HSL)         │ ← H-Challenge/Response (~200 B)
├─────────────────────────┤
│ Rede (NET)              │ ← Roteamento por grade de profundidade
├─────────────────────────┤
│ Controle de Acesso (MAC)│ ← Channel hopping harmônico determinístico
├─────────────────────────┤
│ Física (PHY-M)          │ ← Geração de waveform s(t) = Σ A·sin(2π·a/b·f₀·t+φ)
└─────────────────────────┘
```

### 2.2 Parâmetros Principais
| Parâmetro | Valor Padrão | Descrição |
|-----------|-------------|-----------|
| `f0_base` | 25.0 Hz | Frequência fundamental de referência |
| `harmonic_order` | 16 | Ordem N do conjunto H_N (4, 8, 16, 32) |
| `mode` | "hybrid" | whale/dolphin/hybrid (ajusta f₀ adaptativo) |
| `tolerance` | 1e-4 | Tolerância para matching racional (100 ppm) |
| `phase_polarity` | true | Codifica direção via φ ∈ {0, π} |

---

## 3. API Reference

### 3.1 Core: `HarmonicProtocol`
```python
class HarmonicProtocol:
    def __init__(self, f0_base: float, harmonic_order: int = 16, mode: str = "hybrid")
    @property
    def f0_adaptive(self) -> float  # Retorna f₀ ajustado por modo
    def generate_waveform(self, channels: list, duration: float, sample_rate: int = 48000) -> tuple
    def sync_window(self, channel_ratios: list) -> float  # Calcula T_sync
```

### 3.2 Core: `RationalChannel`
```python
@dataclass(frozen=True)
class RationalChannel:
    a: int  # Numerador
    b: int  # Denominador
    @property
    def priority(self) -> float  # P(a/b) = 1/(a+b)
    def frequency(self, f0: float) -> float  # f = (a/b) · f₀
```

### 3.3 Bioacoustics: `map_cetacean_vocalization`
```python
def map_cetacean_vocalization(
    frequencies: list[float],
    f0_base: float = 25.0,
    harmonic_order: int = 16,
    tolerance: float = 1e-4,
    species: str = None
) -> list[dict]:
    """
    Mapeia frequências observadas para canais harmônicos a/b ∈ H_N.
    
    Retorna lista de dicts com:
    - frequency_hz: frequência original
    - channel_ratio: string "a/b"
    - priority: métrica P(a/b)
    - biological_interpretation: classificação heurística
    - error_ppm: erro de aproximação em partes por milhão
    """
```

### 3.4 Security: `HChallengeResponse`
```python
class HChallengeResponse:
    def __init__(self, secret_seed: bytes)
    def generate_challenge(self, n_channels: int = 3) -> dict
    def compute_response(self, challenge: dict) -> bytes  # ~16 B HMAC
    def verify_response(self, challenge: dict, response: bytes) -> bool
```

---

## 4. Integração com Padrões Existentes

### 4.1 Compatibilidade com JANUS (STANAG 4748) — especificação conceitual
> Modo descrito em nível de projeto; ainda não testado com modems acústicos reais.

- Faixa JANUS: 7–12 kHz
- HMAL mapeia canais a/b dentro desta faixa quando `mode="janus_overlay"`
- Autenticação HSL ocorre antes do payload JANUS padrão
- Compatibilidade: `JanusCompatibilityMode.OVERLAY` (padrão) ou `STANDALONE`

### 4.2 Ponte com GuruDev Core (planejada)
> Módulo `hmal.gurudev` ainda não incluído neste repositório.

```python
from hmal.gurudev import ontology_bridge
semantic_vector = ontology_bridge.map_vocalization_to_ontology(mapped_channel)
# Retorna vetor R⁶ hexarrelacional + casos gramaticais
```

---

## 5. Limitações Conhecidas

| Limitação | Impacto | Mitigação |
|-----------|---------|-----------|
| Desk-study (sem validação em campo) | Resultados preliminares | Parceria com laboratórios oceanográficos para TRL 4–6 |
| Classificação biológica heurística | Precisão limitada | Treinar ML com dados rotulados por especialistas |
| H_N limitado a N=32 | Trade-off resolução vs. computação | Otimizar para ARM Cortex-M4 em dispositivos embarcados |
| Propagação em águas rasas não modelada | Perda de precisão em estuários | Implementar modelo Bellhop-lite em fase futura |

---

## 6. Roadmap Técnico

| Período | Marco | Estado em 30/10/2026 |
|---|---|---|
| mai/2026 | Expansão de testes (43 testes) | Concluído |
| jun/2026 | Integração contínua (Python 3.11–3.13, CodeQL) | Concluído |
| out/2026 | Pré-registro exploratório, matriz de dados e critérios da bancada digital | Em revisão |
| nov/2026 | Decisões *go/no-go* de viabilidade (02, 04 e 05/11) e bancada digital B1–B7 | Planejado |
| 06/11/2026 | Apresentação à COPPE/UFRJ | Agendado |
| 2027 | Bancada eletroacústica em tanque e validação com parceiro oceanográfico | A definir com parceria |
| 2027 | Submissão de artigo em bioacústica | Condicionada aos resultados |


---

*Documento criado em maio de 2026; roteiro atualizado em 30/10/2026.*
