<p align="center">
  <strong>Hubstry Marine Acoustic Layer (HMAL)</strong><br>
  <em>Pesquisa aplicada em bioacústica marinha: razões racionais, dados públicos reais e engenharia reproduzível</em>
</p>

---

**Versão:** `0.1.0-alpha` · **Fase:** pesquisa exploratória com pré-registro · **Instituição:** Hubstry Deep Tech — Rio de Janeiro, Brasil · **Contato:** guilhermemachado.ceo@hubstry.dev

## Visão geral

O HMAL é um programa de pesquisa e engenharia da Hubstry Deep Tech sobre a estrutura acústica de vocalizações de cetáceos. A pergunta central é original: a razão entre a mesma grandeza acústica, medida em duas unidades vocais distintas, pode ser descrita de forma informativa por um dicionário finito de razões racionais reduzidas (`H_N`)?

A pesquisa começa com baleias-azuis, cujas vocalizações são estereotipadas, de baixa frequência e amplamente documentadas em bases públicas. O projeto combina três frentes:

1. **Ciência:** uma hipótese bioacústica testável, com pré-registro, critérios de decisão e prazos fixados antes da análise.
2. **Dados:** um mapa de fontes públicas reais (MBARI, NOAA, Chagos, IBAMA) com licença, proveniência e adequação documentadas.
3. **Engenharia:** uma biblioteca Python testada e uma linha de aplicação em controle de qualidade para Monitoramento Acústico Passivo (MAP).

## O que já está entregue

| Entrega | Onde |
|---|---|
| Biblioteca Python `hmal` com dicionário `H_N`, projeção de medidas, erro em ppm (partes por milhão) e métrica interna `P(a/b)` | `src/hmal/` |
| 43 testes automatizados, executados em integração contínua (CI) nas versões 3.11, 3.12 e 3.13 do Python, com análise de segurança CodeQL | `tests/`, `.github/workflows/` |
| Pré-registro exploratório com hipóteses, pares vocais candidatos, regras de decisão *go/no-go* e prazos | `lab/PREREGISTRATION.md` |
| Matriz de dados públicos com licença, acesso e limitações de cada fonte | `lab/DATASETS.md` |
| Resumo executivo para a reunião com a COPPE/UFRJ | `lab/COPPE_SUMMARY.md` |
| Diretrizes éticas e de uso dual | `docs/ETHICS_GUIDELINES.md` |
| Publicação de referência com DOI | [Zenodo 10.5281/zenodo.20184616](https://doi.org/10.5281/zenodo.20184616) |

## A pergunta científica

O conjunto usado pelo projeto é:

$$
H_N = \left\{\frac{a}{b} \mid 1\leq a,b\leq N,\;\gcd(a,b)=1\right\}.
$$

Ele inclui razões menores e maiores que 1. Com pares ordenados coprimos, `|H_16| = 159` e `|H_32| = 647`.

O desenho evita a armadilha mais comum da área. Harmônicos de uma mesma vocalização seguem razões inteiras por pura física de sinais periódicos, então não contam como evidência. A hipótese só é testada entre unidades vocais distintas, identificadas de forma independente, com grandezas fisicamente comparáveis. O dicionário `H_N` é comparado com um dicionário concorrente de mesmo tamanho em escala logarítmica (`D_log`), para separar estrutura real de efeito de densidade.

## Rigor metodológico

O projeto adota práticas de pesquisa confirmatória desde a fase exploratória:

- **Pré-registro com prazos:** cada par vocal candidato tem data-limite de viabilidade (02/11, 04/11 e 05/11/2026). Sem dados elegíveis no prazo, o resultado é registrado como inconclusivo, sem troca de hipótese depois de ver os dados.
- **Unidade de replicação explícita:** uma população × par vocal × temporada equivale a uma unidade independente (`n_eff=1`). A fase atual mede viabilidade e precisão. A fase confirmatória exige múltiplas populações.
- **Limite teórico de precisão:** a estimação de frequência é referida ao limite de Cramér–Rao, que fixa a menor variância possível sob ruído.
- **Proveniência:** toda fonte é registrada com licença, versão, data de acesso e checksum.

## Aplicação de engenharia: controle de qualidade em MAP

A hipótese H3 investiga um escore de controle de qualidade para apoiar a revisão de detecções do PAMGuard, software livre de detecção acústica de cetáceos. O objetivo é separar detecções verdadeiras de falsos positivos e ruídos transientes.

O contexto de aplicação é concreto no Brasil. O Guia de Monitoramento da Biota Marinha do IBAMA (Instituto Brasileiro do Meio Ambiente e dos Recursos Naturais Renováveis), de 2018, inclui o MAP entre as medidas de mitigação exigidas no licenciamento de pesquisas sísmicas marítimas. Uma ferramenta que reduza o tempo de revisão humana atende a uma etapa real desse fluxo. A proposta é complementar o PAMGuard e os especialistas, não substituí-los.

## Roteiro

| Fase | Objetivo | Estado |
|---|---|---|
| 1 — Viabilidade | Confirmar pares vocais mensuráveis em dados públicos; medir precisão | Em andamento (prazos até 05/11/2026) |
| 2 — Observatório público | Painel com dados diários reais do MBARI (espectrograma, Blue B Call Index, proveniência) no Hubstry Digital Research Lab | Planejado |
| 3 — Confirmatória | Múltiplas populações, modelo nulo biológico, simulação de poder estatístico, novo pré-registro | Requer parceria acadêmica |
| 4 — Engenharia de canal | Testar sinais sintéticos em canais acústicos submarinos medidos (Watermark, Underwater Acoustic Channel Library) | Futuro |

## Parceria buscada

Buscamos interlocução com a COPPE/UFRJ (Instituto Alberto Luiz Coimbra de Pós-Graduação e Pesquisa de Engenharia) em quatro temas: mensuração de vocalizações, desenho de replicação, modelos nulos e estimação de parâmetros em sinais submarinos.

## Maturidade e escopo

O HMAL está em fase de pesquisa e protótipo. Os resultados de mapeamento são exploratórios até a conclusão do pré-registro. Os módulos de protocolo e segurança (`src/hmal/core`, `src/hmal/security`) são experimentais e ainda não passaram por teste em campo nem por auditoria criptográfica. A versão 1.0.0 da publicação no Zenodo traz estimativas de desk-study (estudo teórico, sem dados de campo), hoje em revisão sob o pré-registro.

## Ética e licença

A pesquisa atual é exclusivamente passiva: análise de gravações existentes, sem emissão sonora no mar. As diretrizes éticas vedam sonar ativo, dispersão acústica de fauna, pesca acústica e vigilância de cetáceos ou monitoramento não consentido de mamíferos marinhos. Detalhes em [`docs/ETHICS_GUIDELINES.md`](docs/ETHICS_GUIDELINES.md).

Licença: **Business Source License 1.1** ([`LICENSE`](LICENSE)), com concessão sob CC BY 4.0 para pesquisa acadêmica, educação e conservação. Usos comerciais, SaaS (software como serviço) e de defesa dependem de autorização expressa do licenciante.

## Referências e dados

- Machado, G. G. (2026). *Mapeamento Harmônico Racional de Vocalizações Cetáceas: Protocolo HMAL e Aplicações em Bioacústica Subaquática* (v1.0.0). [Zenodo, DOI 10.5281/zenodo.20184616](https://doi.org/10.5281/zenodo.20184616).
- MBARI, [Pacific Sound — dados 2 kHz](https://docs.mbari.org/pacific-sound/notebooks/data/PacificSound2kHz/).
- MBARI, [Blue B Call Index](https://docs.mbari.org/pacific-sound/notebooks/bluewhales/classify/blueB/PacificSoundBlueBCallIndex/).
- MBARI, [Blue A Call Classification](https://docs.mbari.org/pacific-sound/notebooks/bluewhales/classify/blueA/PacificSoundClassifyBlueA/).
- Leroy et al. (2021), [canto de baleias-azuis-pigmeias de Chagos](https://doi.org/10.1038/s41598-021-88062-5).
- Jancovich & Rogers (2026), [dados derivados de Chagos — Zenodo](https://doi.org/10.5281/zenodo.22654272).
- Mellinger & Clark (2003), [vocalizações de baleias-azuis no Atlântico Norte](https://pubmed.ncbi.nlm.nih.gov/12942988/).
- FFI, [Watermark benchmark](https://www.ffi.no/en/research/watermark).
- Li et al. (2026), [Underwater Acoustic Channel Library — arXiv:2609.03207](https://arxiv.org/abs/2609.03207).
- IBAMA, [Guia de Monitoramento da Biota Marinha — 2018](https://www.gov.br/ibama/pt-br/centrais-de-conteudo/arquivos/arquivos-pdf/2018-11-01-ibama-guia-de-monitoramento-da-biota-marinha-outubro-pdf).

## Citação

Cite a versão do software, a data de acesso e o identificador de commit utilizados.

## Responsável

**Guilherme Gonçalves Machado**  
Hubstry Deep Tech — Rio de Janeiro, Brasil  
ORCID: [0009-0008-1083-0784](https://orcid.org/0009-0008-1083-0784)  
E-mail: guilhermemachado.ceo@hubstry.dev
