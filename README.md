<p align="center">
  <strong>Hubstry Marine Acoustic Layer (HMAL)</strong><br>
  <em>Protótipo de pesquisa para mapeamento de medidas acústicas e investigação de razões racionais em bioacústica marinha</em>
</p>

---

## Estado do projeto

**Versão do software:** `0.1.0-alpha`  
**Estado científico:** hipótese exploratória; protocolo de viabilidade em preparação  
**Instituição responsável:** Hubstry Deep Tech — Rio de Janeiro, Brasil  
**Contato:** guilhermemachado.ceo@hubstry.dev

O HMAL é um projeto experimental da Hubstry que investiga se medidas acústicas comparáveis, extraídas de unidades vocais distintas, podem ser descritas de modo informativo por um dicionário finito de razões racionais reduzidas (`H_N`). A pesquisa começa com vocalizações de baleias-azuis.

**O HMAL ainda não é um protocolo de comunicação submarina validado.** O repositório contém um protótipo computacional e módulos experimentais, mas não demonstra interoperabilidade acústica em campo, comunicação bidirecional funcional, segurança criptográfica validada, desempenho anti-jamming ou conformidade regulatória.

## Pergunta de pesquisa

A pergunta exploratória é se a razão entre a mesma grandeza acústica medida em duas unidades vocais distintas e identificadas independentemente pode ser descrita por um dicionário finito de razões racionais com propriedades descritivas úteis.

Harmônicos e sobretons de uma mesma vocalização não são considerados evidência de organização especial: sua presença em sinais periódicos é esperada pela física de produção e propagação sonora. A hipótese exige unidades vocais distintas, variáveis fisicamente comparáveis e controles adequados.

O pré-registro associado é `lab/PREREGISTRATION.md` (versão de trabalho v1.3.1-draft). Enquanto não houver congelamento documentado e dados elegíveis, resultados de mapeamento serão tratados como exploratórios, sem confirmação estatística ou biológica.

## O que o protótipo implementa

O código atual inclui componentes preliminares para:

- construção de um dicionário finito de razões racionais coprimas `H_N`;
- projeção de uma frequência observada sobre o elemento mais próximo do dicionário;
- cálculo de erro de aproximação e de uma métrica interna de prioridade `P(a/b)=1/(a+b)`;
- geração de sinais sintéticos por soma de componentes senoidais;
- módulos experimentais de gateway e desafio–resposta.

Esses componentes demonstram implementação de software, não validação científica ou operacional. A classificação de vocalizações presente no protótipo é heurística e não deve ser interpretada como identificação biológica validada por especialistas.

### Definição de `H_N`

O conjunto usado pelo protótipo é:

$$
H_N = \left\{\frac{a}{b} \mid 1\leq a,b\leq N,\;\gcd(a,b)=1\right\}.
$$

A definição inclui razões menores e maiores que 1; portanto, não deve ser chamada simplesmente de sequência de Farey. Para a implementação com pares ordenados coprimos, as cardinalidades são `|H_16| = 159` e `|H_32| = 647`.

A métrica `P(a/b)=1/(a+b)` é um escore interno definido pelo projeto. Não há demonstração empírica de que ela represente prioridade biológica, eficiência energética ou robustez acústica em cetáceos.

## Plano de validação

A validação foi separada em trilhas que respondem a perguntas diferentes:

1. **Hipótese bioacústica:** avaliar a viabilidade de medir a mesma grandeza física em unidades vocais distintas, começando com baleias-azuis. Com uma única combinação população × par vocal × temporada, a razão estimada tem `n_eff=1` e não permite confirmação estatística populacional.
2. **Processamento acústico:** reproduzir métodos convencionais em gravações reais, documentando dados, rótulos, calibração, proveniência e limitações de detecção.
3. **Comunicação submarina:** em fase posterior, testar sinais sintéticos em canais medidos no mar e compará-los com benchmarks existentes. Isso não será confundido com validação da hipótese bioacústica.

A matriz de dados e recursos está em `lab/DATASETS.md` (rascunho). O acesso público a um registro ou arquivo não implica licença irrestrita, autorização comercial ou adequação à hipótese específica.

## Aplicação potencial de engenharia: QA para monitoramento acústico passivo

Uma hipótese secundária de engenharia (H3) investiga se um escore de controle de qualidade pode apoiar a revisão de detecções geradas por ferramentas como PAMGuard, distinguindo detecções verdadeiras de falsos positivos ou transientes com rótulos independentes.

Esse caso de uso pode ser relevante para fluxos de Monitoramento Acústico Passivo (MAP) em pesquisas sísmicas marítimas. O Guia de Monitoramento da Biota Marinha do IBAMA (2018) inclui procedimentos de MAP no contexto das medidas de mitigação e das condicionantes de licenças de pesquisa sísmica. Isso representa contexto de aplicação potencial, não validação do HMAL, prova de demanda comercial ou conformidade regulatória. O HMAL não substitui PAMGuard, especialistas, observadores ou procedimentos oficiais.

Fontes: [Guia de Monitoramento da Biota Marinha — IBAMA 2018](https://www.gov.br/ibama/pt-br/centrais-de-conteudo/arquivos/arquivos-pdf/2018-11-01-ibama-guia-de-monitoramento-da-biota-marinha-outubro-pdf) · [Diretrizes técnicas do IBAMA](https://www.gov.br/ibama/pt-br/assuntos/laf/procedimentos-e-servicos/arquivos/petroleo-e-gas/diretrizes).

## Limitações e alegações não sustentadas

As seguintes alegações não devem ser interpretadas como resultados validados e foram retiradas desta apresentação principal até que exista evidência reproduzível e independente:

- percentuais de cobertura de `H_16`/`H_32` em vocalizações de baleias ou golfinhos;
- concentração de vocalizações biologicamente significativas em canais de alta prioridade;
- overhead, latência ou taxa de falha do handshake como desempenho medido;
- capacidade de 26,6 kbps como capacidade demonstrada do sistema;
- autenticação criptográfica segura, anti-replay validado ou resistência a jamming;
- interoperabilidade real com JANUS ou outros modems acústicos;
- interpretação semântica de vocalizações cetáceas.

Sinais sintéticos não substituem testes com gravações reais. Uma saída de mapeamento para `H_N` não prova que a vocalização foi produzida, organizada ou selecionada biologicamente segundo razões racionais.

## Segurança, ética e uso dual

Os módulos de segurança e gateway são experimentais e não foram submetidos a auditoria criptográfica independente. Não devem ser usados para proteger sistemas operacionais, infraestrutura crítica ou operações reais.

A pesquisa nesta fase concentra-se em análise de dados acústicos e validação computacional. Qualquer emissão acústica ativa, experimento com animais, coleta de campo ou uso operacional exigirá avaliação ética, autorizações, análise de impacto e validação técnica apropriadas. As diretrizes éticas vigentes proíbem sonar ativo, dispersão acústica de fauna, pesca acústica, integração com sistemas ASW ou detecção de torpedos e vigilância de cetáceos ou monitoramento não consentido de mamíferos marinhos. A licença exige autorização prévia e expressa para usos comerciais ou de defesa; essa autorização não afasta as proibições éticas específicas. O projeto não reivindica conformidade regulatória.

## Licença e uso

Consulte os arquivos [`LICENSE`](LICENSE) e [`docs/ETHICS_GUIDELINES.md`](docs/ETHICS_GUIDELINES.md). A licença atual do repositório é **Business Source License 1.1**, com uma concessão adicional para usos acadêmicos e de conservação sob CC BY 4.0; usos comerciais, SaaS ou de defesa exigem autorização explícita do licenciante. As diretrizes éticas vedam sonar ativo, dispersão acústica de fauna, pesca acústica e vigilância de cetáceos ou monitoramento não consentido de mamíferos marinhos. Elas não estabelecem uma proibição genérica de todo uso militar/de defesa, mas nenhuma aplicação desse tipo é autorizada automaticamente pelo acesso ao repositório. Isso não equivale a uma licença CC BY irrestrita para todos os usos.

## Referências e recursos

- Machado, G. G. (2026). *Mapeamento Harmônico Racional de Vocalizações Cetáceas: Protocolo HMAL e Aplicações em Bioacústica Subaquática* (versão 1.0.0). [Zenodo, DOI 10.5281/zenodo.20184616](https://doi.org/10.5281/zenodo.20184616). **Nota de versão:** a publicação 1.0.0 contém estimativas preliminares de desk-study; essas estimativas estão em revisão à luz do pré-registro exploratório atual e não devem ser interpretadas como resultados empíricos confirmados.
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

Para citar o software, indique a versão efetivamente utilizada, a data de acesso e o identificador de commit. Não atribua aos artigos citados resultados experimentais que não tenham sido produzidos pelo HMAL.

## Responsável

**Guilherme Gonçalves Machado**  
Hubstry Deep Tech — Rio de Janeiro, Brasil  
ORCID: [0009-0008-1083-0784](https://orcid.org/0009-0008-1083-0784)  
E-mail: guilhermemachado.ceo@hubstry.dev