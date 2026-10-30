# Pré-Registro Exploratório: Relações entre Medidas Acústicas Comparáveis de Unidades Vocais Distintas no HMAL

**ID do Protocolo:** `HMAL-PREREG-2026-001`  
**Versão:** `1.3.1-draft`  
**Status:** CANDIDATO A CONGELAMENTO NÍVEL 1 — protocolo exploratório e de viabilidade. Nível 1 autoriza apenas análise de viabilidade/estimativa exploratória; não autoriza inferência confirmatória. Nível 2 exige protocolo confirmatório futuro, com versão e hash próprios.  
**Data da revisão:** 30/10/2026  
**Autor:** Guilherme Gonçalves Machado (Hubstry Deep Tech)  
**Repositório alvo:** `Hubstry-DeepTech/hubstry-marine-acoustic-layer`  
**Operador:** `guilhermemachado.ceo@hubstry.dev`  
**Semente global de reprodutibilidade (`MASTER_SEED`):** `20261106`  
**Gerador:** `numpy.random.Generator(numpy.random.PCG64(20261106))`

> **Aviso de validade:** esta versão incorpora a auditoria adversarial v1.2. O protocolo separa dois níveis: **Nível 1**, congelamento exploratório/viabilidade, e **Nível 2**, desenho confirmatório futuro. A análise atual pode estimar medidas apenas quando o par vocal passar por critérios pré-especificados de acesso, identificação e comparabilidade física. Com uma única população × par vocal × temporada, `n_eff = 1`: não há confirmação estatística de H1. O Nível 1 não implica confirmação, nem dispensa replicação biológica, simulação de poder ou modelo nulo biologicamente justificado para a fase 2.

---

## 1. Motivação e pergunta científica

A implementação original de `map_cetacean_vocalization()` projeta uma frequência observada sobre o elemento mais próximo de um dicionário finito de razões racionais. Como qualquer valor positivo dentro do suporte pode ser aproximado por algum elemento de um dicionário suficientemente denso, uma taxa elevada de encaixe, isoladamente, não demonstra estrutura biológica especial.

A auditoria anterior identificou circularidade em comparar picos secundários com o fundamental estimado do próprio chamado. Esta versão mantém a proibição: componentes harmônicos de uma mesma vocalização não são evidência de relações especiais entre unidades vocais distintas.

A auditoria adversarial identificou um segundo problema: em uma população e temporada, a razão entre duas unidades vocais pode ser praticamente constante. Repetir sua estimação em muitos blocos de áudio melhora a precisão da estimativa, mas não cria novas replicações biológicas. Portanto, blocos não podem ser tratados como replicações independentes para testar uma hipótese sobre uma população.

**Pergunta exploratória nesta versão:** qual é a razão estimada entre uma mesma grandeza acústica, medida em duas unidades vocais distintas e identificadas independentemente, dentro de uma população/variante e temporada previamente delimitadas? Em que medida a posição dessa razão no dicionário `H_N` difere da posição em um dicionário geométrico competidor de igual cardinalidade?

**Pergunta confirmatória de fase futura:** em múltiplas unidades de replicação biológica independentes — por exemplo, combinações população × par de unidades vocais comparáveis × temporada, com dependência entre temporadas e populações modelada — as razões observadas apresentam aderência ao dicionário racional maior do que a esperada sob um modelo nulo biologicamente plausível e definido antes da análise?

A análise atual poderá estimar uma razão em um único contexto biológico somente se o primeiro par elegível na lista fixa da Seção 2.1 passar por todos os critérios de viabilidade; caso contrário, registrará o no-go sem substituição posterior. Nesse cenário, `n_eff = 1` para inferência sobre a população/temporada: não haverá teste confirmatório de H1, mesmo que existam muitos eventos ou blocos de gravação.

O pré-registro não presume que a hipótese seja verdadeira. Resultados descritivos, negativos ou inconclusivos serão relatados sem alteração retrospectiva da hipótese, do conjunto de dados ou dos critérios de análise.

## 2. Escopo, população e fontes de dados

### 2.1 População-alvo e comparabilidade das variáveis

- **Espécie inicial:** baleia-azul (*Balaenoptera musculus*).
- **Populações/variantes candidatas:** Pacífico Nordeste (MBARI), Chagos (unidades 2/3) e Atlântico Norte (partes/unidades A/B), todas condicionadas às fontes, ao acesso, à identificação independente e à comparabilidade descritos no registro ordenado abaixo.
- **Fonte candidata prioritária para áudio e processamento:** MBARI Pacific Sound, bucket `pacific-sound-2khz`.
- **Registro de pares vocais candidatos:** a seleção seguirá, sem reordenação pós-hoc, a lista fixa abaixo. A prioridade do dataset para processamento não equivale à prioridade científica do par para H1.

**Regra geral de comparabilidade:** a razão só poderá ser formada entre medidas da mesma grandeza física operacionalmente definida. Frequência fundamental de componente tonal (`f0`, Hz), frequência de pico de unidade tonal (`f_peak`, Hz) e taxa de repetição de pulsos (`PRR`, pulsos/s) não serão intercambiadas apenas por terem dimensão temporal inversa. A escolha do par será feita por documentação acústica, acesso e critérios de identificação independentes de `H_N`, `D_log` e de qualquer resultado de projeção.

#### Registro prévio e ordenado de pares candidatos

| Ordem | População/canto e par | Variável candidata | Fonte de caracterização | Estado inicial e regra de decisão | Prazo final de decisão |
|---|---|---|---|---|---|
| 1 | Pacífico Nordeste — chamado A / chamado B (MBARI) | A: taxa de repetição de pulsos (`PRR`); B: frequência fundamental tonal (`f0`) | Lewis et al. (2018), [DOI 10.1111/mms.12458](https://doi.org/10.1111/mms.12458); documentação [MBARI Blue B Call Index](https://docs.mbari.org/pacific-sound/notebooks/bluewhales/classify/blueB/PacificSoundBlueBCallIndex/) | **Presumivelmente NO-GO** para a razão A/B: A é descrito como pulsado e B como tonal. Só poderá passar se uma justificativa física independente, publicada e operacionalizável antes da projeção em `H_N` demonstrar que há uma mesma grandeza mensurável nos dois. Não dividir `PRR` por `f0` por conveniência dimensional. | **02/11/2026** (até 23:59, horário de Brasília). Sem justificativa independente documentada até o prazo: NO-GO nesta versão. |
| 2 | Chagos — unidade 2 / unidade 3 do canto | Frequência de pico de unidade tonal pura (`f_peak`, Hz) em cada unidade | Leroy et al. (2021), [Scientific Reports, DOI 10.1038/s41598-021-88062-5](https://doi.org/10.1038/s41598-021-88062-5) | **Candidato condicional de melhor comparabilidade tonal.** O artigo descreve as unidades 2 e 3 como tons puros; a unidade 3 pode estar ausente. O dataset Zenodo de Jancovich & Rogers (2026), [DOI 10.5281/zenodo.22654272](https://doi.org/10.5281/zenodo.22654272), não contém áudio original e reporta medidas das subunidades 1 e 2 da primeira unidade, não das unidades 2 e 3. Só será GO se gravações originais contendo ambas as unidades forem obtidas por acesso autorizado, documentado e com termos de uso verificados. As médias publicadas por Leroy et al. não substituem áudio/eventos individuais nem constituem dataset para esta análise. | **04/11/2026** (até 23:59, horário de Brasília). Sem áudio autorizado de ambas as unidades e termos de uso verificados até o prazo: NO-GO nesta versão. |
| 3 | Atlântico Norte — parte/unidade tonal A / parte/unidade tonal B da sequência | Frequência fundamental/instantânea da componente tonal (`f0`, Hz), com resumo por unidade definido antes da análise | Mellinger & Clark (2003), [PubMed record](https://pubmed.ncbi.nlm.nih.gov/12942988/) | **Reserva condicional, acesso não verificado.** A descrição publicada caracteriza A como tonal de frequência aproximadamente constante e B como tonal modulado em frequência. Só será elegível se uma fonte de áudio acessível e seus metadados permitirem identificar ambas as unidades e estimar a mesma variável `f0` com método compatível. Não presumir disponibilidade, licença ou rótulos. | **05/11/2026** (até 23:59, horário de Brasília). Sem áudio, metadados, identificação e termos de uso verificados até o prazo: NO-GO nesta versão. |

A ordem acima e os prazos da última coluna são fixos. Cada decisão GO/NO-GO deverá ser registrada com data, evidência consultada e justificativa até o prazo específico do candidato. A ausência de resposta de instituição, autorização pendente ou acesso não concluído até o prazo equivale a NO-GO nesta versão; não haverá extensão informal nem espera indefinida. Se um candidato passar, a seleção se encerra nele; candidatos posteriores não poderão substituí-lo após a inspeção de resultados. A elegibilidade será decidida por critérios de acesso, caracterização acústica, mensuração e identificação, **sem consultar o erro de projeção em `H_N`, `D_log`, `\Delta(q)` ou a prioridade `P(a/b)`**. O primeiro par que satisfizer todos os critérios documentados poderá ser usado para a estimativa exploratória. A falha de um candidato leva apenas ao próximo candidato já listado; não autoriza inserir novos pares depois de inspecionar os resultados. Se nenhum dos três passar, H1 será declarada **não operacionalizável nesta fase**. Não haverá substituição pós-hoc.

O índice convencional do chamado B do MBARI quantifica ocorrência/intensidade por energia em bandas associadas ao chamado; ele não identifica, por si só, eventos A/B nem fornece automaticamente a frequência fundamental. O pico do terceiro harmônico usado no índice não será rotulado como `f0` (ver documentação MBARI acima).

### 2.2 Critério de viabilidade (go/no-go)

A decisão de cada candidato deverá ser registrada até o prazo individual da Seção 2.1: MBARI A/B até 02/11/2026; Chagos unidades 2/3 até 04/11/2026; Atlântico Norte A/B até 05/11/2026 (todos até 23:59, horário de Brasília). Pendências de autorização ou respostas institucionais não prorrogam esses prazos. A análise exploratória de estimação de H1 só poderá ocorrer para o primeiro par elegível da lista pré-registrada na Seção 2.1 e somente se:

1. houver áudio acessível e versionado para o período escolhido;
2. houver critérios reproduzíveis para identificar cada tipo vocal, independentes da aderência a `H_N`;
3. a variável acústica de cada unidade vocal estiver operacionalmente definida e for comparável entre as unidades que formarão a razão;
4. for possível estimar uma única medida por evento, sem usar picos harmônicos do mesmo evento como observações independentes;
5. os blocos/dias piloto e os blocos/dias de avaliação descritiva estiverem identificados e separados previamente;
6. a proveniência, os IDs/datas, a estação/sensor e as condições de gravação estiverem registrados.

**Critério de inferência:** a análise confirmatória de H1 exige múltiplas unidades de replicação biológica independentes, e não apenas múltiplos eventos ou blocos. A unidade proposta é a combinação de população/variante vocal × par de unidades vocais comparáveis × temporada. A independência de temporadas deve ser avaliada considerando autocorrelação temporal; song types dentro de uma mesma população não serão considerados independentes automaticamente. O número de replicações necessário deverá ser determinado por simulação de poder baseada na variabilidade entre unidades biológicas, antes da fase confirmatória.

Se houver apenas uma população, um par vocal e uma temporada, `n_eff = 1`: o resultado será exclusivamente uma estimativa exploratória de `q`, sua incerteza e a comparação geométrica dos dicionários. Não será calculado valor-p biológico, não será declarada confirmação e os blocos não serão usados como substitutos de replicações biológicas.

Os pares serão avaliados exclusivamente na ordem pré-registrada da Seção 2.1. Se um candidato falhar, passa-se apenas ao próximo candidato já listado. Se todos falharem em acesso, identificação ou comparabilidade, H1 será marcada como **não operacionalizável nesta fase**, sem inclusão de um novo par. Se algum par passar na mensuração, mas houver apenas uma unidade de replicação biológica, H1 será marcada como **estimável, porém não confirmatória**. Não se substituirá silenciosamente espécie, população, unidade vocal, variável ou dataset.

### 2.3 Escopo excluído desta versão

- Golfinhos, odontocetos e assobios FM não integram o escopo desta versão.
- Harmônicos e sobretons de uma mesma vocalização não constituem evidência confirmatória de relações entre unidades distintas.
- Sinais sintéticos servem à calibração e aos testes do estimador, não à confirmação de hipótese biológica.
- O índice B do MBARI é baseline de monitoramento, não classificador A/B, estimador automático de `f0` ou validação do mapeamento racional.
- Repetições de bloco, dia ou evento em uma mesma população/temporada não serão tratadas automaticamente como replicações biológicas independentes.

## 3. Definições matemáticas

### 3.1 Dicionário de razões racionais reduzidas (`H_N`)

Para uma ordem inteira `N >= 1`, define-se:

$$
H_N = \left\{q=\frac{a}{b}\;\middle|\;a,b\in\{1,2,\ldots,N\},\;\gcd(a,b)=1\right\}.
$$

O conjunto contém razões positivas ordenadas, incluindo valores menores e maiores que 1. Portanto, **não será denominado sequência ou conjunto de frações de Farey**, cuja definição usual restringe as frações ao intervalo de 0 a 1. Neste protocolo, `H_N` será chamado de **dicionário finito de razões racionais reduzidas**.

Sua cardinalidade é:

$$
|H_N|=2\sum_{k=1}^{N}\varphi(k)-1,
$$

onde `\varphi(k)` é a função totiente de Euler. Valores de referência:

- `|H_4| = 11`;
- `|H_8| = 43`;
- `|H_16| = 159`;
- `|H_32| = 647`.

A referência geométrica padrão desta versão utilizará `N=16`, logo `|H_16|=159`. Outras ordens, se calculadas, serão análises secundárias de sensibilidade. `N=16` não representa a definição de um teste biológico confirmatório nesta versão.

A métrica de prioridade definida no projeto é:

$$
P(a/b)=\frac{1}{a+b}.
$$

`P` será tratada como uma convenção matemática interna do HMAL. Não será apresentada como propriedade biológica, preferência acústica ou vantagem energética demonstrada sem evidência independente.

### 3.2 Grandezas acústicas comparáveis e razão entre unidades distintas

Para cada evento vocal elegível `e`, será extraída uma única medida primária `x_e`, definida de acordo com a natureza física da unidade vocal:

- para uma unidade tonal: frequência fundamental de um trecho tonal estável, `f0` em Hz;
- para uma unidade pulsada: taxa de repetição de pulsos, `PRR` em pulsos/s, se essa for a variável escolhida e validada;
- outras variáveis exigem definição física, algoritmo de estimação e justificativa próprios, congelados antes da análise.

Uma razão `q` só será formada entre duas unidades vocais quando ambas fornecerem a **mesma grandeza física operacional** ou quando houver uma hipótese mecanística independente que justifique a razão entre grandezas distintas. Não se denominará `f0` a taxa de repetição de pulsos. Em particular, a razão entre `f0` de uma unidade tonal B e `PRR` de uma unidade pulsada A não será calculada nesta versão sem justificativa independente.

Para uma unidade de replicação biológica `r`, definida como combinação população/variante × par de unidades vocais comparáveis × temporada, serão estimadas medidas agregadas:

$$
\tilde x_{1,r}=\operatorname{median}\{x_e:e\in U_1,r\},\qquad
\tilde x_{2,r}=\operatorname{median}\{x_e:e\in U_2,r\}.
$$

Se — e somente se — `x` representar a mesma grandeza nas duas unidades, a razão estimada será:

$$
\hat q_r=\frac{\tilde x_{1,r}}{\tilde x_{2,r}}.
$$

Os blocos, dias, sequências e eventos dentro de `r` são subamostras/níveis de observação que contribuem para estimar `\hat q_r`; não são replicações biológicas independentes para inferência sobre a hipótese. Com uma única combinação `r`, o tamanho amostral biológico efetivo é `n_eff=1`, independentemente do número de blocos.

Não será utilizado um `f_0` populacional fixo para normalizar todas as observações. Todas as medidas serão associadas aos metadados de população, variante vocal, unidade, data, estação/sensor, implantação e método de estimação.

### 3.3 Erro relativo de projeção

Para `q>0` e um dicionário discreto `D`:

$$
\hat q(q;D)=\arg\min_{r\in D}|r-q|,
$$

$$
\varepsilon_{ppm}(q;D)=10^6\frac{|\hat q(q;D)-q|}{q}.
$$

O erro será calculado descritivamente para `H_16` e para o dicionário competidor `D_log`, definidos na Seção 5. Valores `q` fora do suporte `[1/16,16]` serão registrados como `OUT_OF_SUPPORT`, sem truncamento ou projeção artificial para a borda; sua elegibilidade/exclusão deverá ser contabilizada no fluxo de eventos segundo regra congelada antes da análise confirmatória. A regra de desempate, caso existam dois elementos equidistantes, deverá ser determinística e registrada no código antes da análise confirmatória.

## 4. Hierarquia observacional e unidade de replicação biológica

### 4.1 Hierarquia observacional

A estrutura dos dados será tratada hierarquicamente:

- **Quadros STFT:** observações internas do estimador; nunca serão tratados como `n` independente.
- **Evento/chamado:** unidade de mensuração da variável acústica.
- **Sequência vocal:** agrupamento de eventos relacionados, quando identificável.
- **Bloco de gravação/dia:** subamostra operacional dentro de uma implantação e temporada.
- **Implantação/deployment:** agrupamento espacial/temporal.
- **População/variante vocal × par de unidades comparáveis × temporada:** unidade proposta de replicação biológica para a inferência de fase futura, sujeita a justificativa de independência.

Quadros adjacentes com 75% de sobreposição são dependentes e não serão usados diretamente em testes estatísticos, permutações ou cálculo de tamanho amostral como se fossem eventos independentes.

### 4.2 Precisão da estimativa não é replicação biológica

Blocos adicionais dentro de uma mesma população, par de unidades vocais e temporada podem melhorar a precisão de `\hat q_r`, desde que a dependência seja modelada. Contudo, eles continuam medindo o mesmo parâmetro populacional/contextual e não aumentam o número de replicações biológicas independentes.

A incerteza de `\hat q_r` será estimada por procedimento que respeite o agrupamento (por exemplo, reamostragem em clusters definidos previamente ou modelo hierárquico), e não por tratar quadros STFT, eventos correlacionados ou dias autocorrelacionados como observações iid. O método exato será especificado no piloto e congelado antes de qualquer análise confirmatória.

### 4.3 Unidade de inferência e tamanho amostral efetivo

A unidade de inferência futura será `r = população/variante vocal × par de unidades vocais comparáveis × temporada`, após avaliação da independência biológica. A replicação deverá abranger mais de uma população/variante e/ou temporadas adicionais com modelagem explícita da autocorrelação. Múltiplos song types em uma mesma população podem compartilhar mecanismos e história vocal; não serão considerados independentes sem justificativa.

Para o dataset atual do Pacífico Nordeste, caso só haja uma população, um par de unidades comparáveis e uma temporada analisável, `n_eff=1`. O protocolo permitirá estimar e descrever `\hat q_r`, mas não realizar teste confirmatório de H1. O número necessário de unidades biológicas para a fase confirmatória será definido por simulação de poder, não pelo número bruto de arquivos, eventos ou blocos.

### 4.4 Exclusões de qualidade

Critérios de exclusão de evento (por exemplo, clipping, saturação, baixa relação sinal-ruído, sobreposição de fontes ou impossibilidade de identificar a unidade vocal) serão aplicados antes da agregação, conforme regras congeladas e registradas. Nenhum evento será excluído por apresentar resultado favorável ou desfavorável a `H_16` ou `D_log`.

## 5. Modelos nulos e dicionários competidores

Serão mantidas quatro famílias de modelos para referência geométrica e análises de sensibilidade. **Nenhuma delas constitui, isoladamente, hipótese nula biológica confirmatória nesta versão.** Os resultados não poderão ser selecionados retrospectivamente por favorecerem o HMAL.

### 5.1 `H0,grid` — dicionário competidor de mesma cardinalidade (referência geométrica)

Para cada razão estimada `q`, compara-se o dicionário `H_16` com um competidor logaritmicamente espaçado `D_log` com exatamente 159 pontos no mesmo suporte:

$$
[u_{min},u_{max}]=[1/16,16].
$$

$$
D_{log}=\left\{\exp\left(\ln u_{min}+\frac{j}{158}\ln\frac{u_{max}}{u_{min}}\right):j=0,1,\ldots,158\right\}.
$$

Define-se a diferença geométrica:

$$
\Delta(q)=\varepsilon_{ppm}(q;D_{log})-\varepsilon_{ppm}(q;H_{16}).
$$

Valores positivos indicam que `H_16` tem menor erro de projeção **naquele valor de q**. Esta comparação controla a cardinalidade global e o suporte dos dicionários, mas, para um único `q`, o resultado depende da densidade local e da posição de `q` em relação aos pontos dos dois dicionários. Portanto, `\Delta(q)` é uma **medida descritiva de geometria**, não um teste de que uma população biológica selecionou ou prefere razões racionais.

A comparação `H_16` versus `D_log` não fornece, isoladamente, uma distribuição nula biológica. Uma referência local baseada em razões `q_rand` só poderá ser calculada como diagnóstico exploratório se o intervalo plausível `W` e sua distribuição (por exemplo, log-uniforme em `W`) forem definidos com base em informação externa independente dos valores confirmatórios. Não se escolherá `W` depois de observar `q`. A quantidade `P(\Delta(Q_{rand})\geq\Delta(q_{obs}))`, caso calculada, será rotulada **referência geométrica local exploratória**, e não valor-p confirmatório da hipótese biológica.

O dicionário linear `D_lin`, também com 159 pontos no mesmo suporte, será análise secundária de sensibilidade.

### 5.2 `H0,unif` — razões/frequências uniformes no suporte (secundário)

Serão geradas realizações uniformes no suporte previamente definido. Este modelo é uma análise secundária; sua interpretação como ruído espectral uniforme é limitada e não será considerada o teste decisivo da hipótese.

### 5.3 `H0,log` — razões log-uniformes no suporte (secundário)

Serão geradas realizações para as quais `ln(q)` é uniforme em `[ln(1/16), ln(16)]`. Este modelo é uma análise secundária de sensibilidade para uma distribuição uniforme em escala logarítmica.

### 5.4 `H0,perm` — permutação de rótulos de unidades vocais (exploratória)

Se e somente se houver justificativa de permutabilidade, a permutação ocorrerá no nível de **eventos vocais identificados**, nunca no nível de quadros STFT. Os rótulos/tipos vocais poderão ser permutados apenas dentro de estratos definidos antes da análise, preservando a estrutura de agrupamento e os totais por estrato.

A permutabilidade de A/B não pode ser presumida: tipos vocais distintos podem ter processos de produção, ocorrência, duração e distribuição temporal diferentes. Se os rótulos não forem intercambiáveis sob a hipótese nula, `H0,perm` será omitido ou apresentado apenas como ilustração de sensibilidade, sem interpretação inferencial. Não se permutarão quadros, picos simultâneos ou janelas sobrepostas.

### 5.5 Simulações Monte Carlo

Quando utilizadas, as realizações Monte Carlo usarão `MASTER_SEED=20261106`, com sub-sementes derivadas de forma determinística por modelo/estrato. O número de realizações será registrado antes da execução. Resultados de `H0,unif`, `H0,log`, `D_lin` e `H0,perm` serão identificados como secundários/sensibilidade e não serão usados para escolher a hipótese nula que favoreça o HMAL.

## 6. Hipóteses e estado inferencial

### 6.1 H1 — hipótese de pesquisa; estimável exploratoriamente, não confirmatória nesta amostra

**Enunciado para investigação:** em unidades de replicação biológica independentes `r` — população/variante vocal × par de unidades vocais comparáveis × temporada — a razão `q_r` entre medidas acústicas da mesma grandeza pode apresentar erro de projeção menor em `H_16` do que em um dicionário competidor `D_log` de mesma cardinalidade e suporte.

**Condição de comparabilidade:** H1 não será operacionalizada como razão entre `f0` de uma unidade tonal e taxa de repetição de pulsos de uma unidade pulsada sem justificativa física independente e hipótese específica. A identificação de chamados A e B, por si só, não satisfaz essa condição.

**Estado da amostra atual:** se o conjunto do Pacífico Nordeste fornecer apenas uma combinação população/variante × par vocal × temporada, haverá somente uma razão biológica estimada (`n_eff=1`). Os blocos de gravação serão usados para estimar a precisão dessa razão, não como replicações para um teste de sinal ou teste de hipótese. Nesse caso, H1 será reportada apenas como estimativa exploratória e `\Delta(\hat q_r)` será uma comparação geométrica descritiva.

**Hipótese confirmatória de fase futura:** em múltiplas unidades `r` biologicamente independentes, a distribuição dos `\Delta(q_r)` será comparada com uma hipótese nula biologicamente plausível, especificada e justificada antes da coleta/abertura confirmatória. O desenho deverá definir a distribuição nula de `q`, o procedimento inferencial, a dependência entre populações e temporadas e o tamanho amostral por simulação de poder. `H0,grid` sozinho não substitui esse modelo nulo biológico.

Não será calculado valor-p por tratar blocos dentro de uma mesma população/temporada como replicações independentes. Não se declarará confirmação com base em um único `q`, em múltiplos dias de gravação ou em uma diferença pontual de densidade entre `H_16` e `D_log`.

### 6.2 Precisão, Cramér–Rao e critério de identificabilidade

A tolerância `\eta` **não integra a estatística contínua `\Delta(q)`** e não será usada como limiar para transformar cada bloco em sucesso/fracasso no teste de H1. Nesta versão, ela tem apenas papel instrumental: determinar se a incerteza da razão estimada permite distinguir as projeções mais próximas de `H_16` e `D_log`.

Definam-se:

$$
r_H(q)=\arg\min_{r\in H_{16}}|r-q|,\qquad r_D(q)=\arg\min_{r\in D_{log}}|r-q|,
$$

$$
g(q)=10^6\frac{|r_H(q)-r_D(q)|}{q}\quad\text{ppm}.
$$

Seja `U_{95}(q)` a incerteza relativa de 95% da razão, obtida por calibração do pipeline completo e procedimento de propagação validado. O critério operacional de identificabilidade será:

$$
U_{95}(q)<\frac{g(q)}{2}.
$$

Se a condição não for satisfeita, a observação será marcada como `INSTRUMENTALLY_UNDER_RESOLVED` para a comparação entre os dois dicionários. Além disso, a incerteza de `\Delta(q)` deverá ser propagada sobre a distribuição calibrada de `q`; se a região de incerteza de `\Delta` incluir zero, não haverá discriminação instrumental entre os dicionários. O critério de identificabilidade não é, por si só, teste de hipótese biológica.

**Cramér–Rao e convenção de SNR.** O limite de Cramér–Rao depende do modelo de sinal, da parametrização, do número de amostras, da taxa de amostragem, dos parâmetros conhecidos/desconhecidos e da definição de SNR. Não será reutilizada como universal a expressão da versão 1.1.0-draft nem serão mantidos os exemplos numéricos de `1 s → 6.980 ppm` e `4 s → 1.740 ppm`.

Para uma senoide complexa isolada em ruído gaussiano branco, sob o modelo clássico de frequência desconhecida e SNR definido por amostra, Rife & Boorstyn (1974) derivam um limite cuja variância é proporcional a `1/[SNR_sample × N(N^2-1)]`; portanto, a `SNR_sample` fixa, o desvio-padrão escala aproximadamente com `N^{-3/2}` (com fatores de escala que dependem da convenção de frequência e do modelo real/complexo). Se for mantido fixo o SNR integrado, que cresce aproximadamente com `N × SNR_sample` sob hipóteses usuais, a expressão pode ser reescrita com dependência aparente em `1/T`; isso não equivale a manter fixo o SNR por amostra. Ver Rife & Boorstyn (1974), DOI `10.1109/TIT.1974.1055282`. A fórmula exata aplicável ao sinal acústico real e ao estimador usado deverá ser derivada para sua parametrização; não será inferida apenas pela duração da janela.

O pipeline deverá distinguir e registrar, sem intercambiá-los:

1. `SNR_sample`: razão entre a potência média do sinal e a variância de ruído por amostra no domínio temporal, estimada no trecho de análise. Para uma senoide real ideal de amplitude `A` em ruído branco de variância `\sigma_n^2`, uma convenção usual é `SNR_sample = (A^2/2)/\sigma_n^2`; a convenção exata adotada deverá ser registrada;
2. `SNR_integrated`: SNR de observação baseado na energia do sinal ao longo da janela, definida como `E_signal / sigma_n^2`, em que `sigma_n^2` é a variância de ruído por amostra (ou a variância equivalente após ponderação pela janela). Para um tom estável em ruído branco independente, cresce aproximadamente como `N × SNR_sample`. Não deve ser confundido com `sum(signal^2)/sum(noise^2)` no mesmo trecho, que estima uma razão média de potências e não cresce automaticamente com `N`;
3. `SNR_bin` ou `SNR_frame`: razão entre potência do pico/componente e estimativa do piso espectral local no espectrograma. Esse indicador é dependente da resolução espectral, da janela, da largura de banda do bin e do estimador do piso de ruído.

O valor de `SNR_frame` ou `SNR_bin` não poderá ser inserido na fórmula de Cramér–Rao derivada para `SNR_sample` ou `SNR_integrated` sem transformação e justificativa. A expressão de conversão, banda de ruído, janela e pressupostos deverão ser documentados. Para uma unidade pulsada, o limite de frequência de uma senoide não será automaticamente aplicado à taxa de repetição de pulsos; será necessário um modelo de estimação próprio.

O limite de Cramér–Rao é um limite inferior sob os pressupostos do modelo, não um erro real garantido. Em áudio submarino com ruído colorido, multipercurso, modulação, reverberação ou fontes sobrepostas, a adequação do modelo deve ser avaliada. A calibração sintética do pipeline completo, com frequências/variáveis conhecidas e ruído representativo, é obrigatória.

A incerteza da razão agregada não será obtida aplicando diretamente o limite de uma senoide à mediana de eventos nem dividindo automaticamente por `sqrt(n)`. A propagação deverá respeitar a dependência entre eventos, sequências, dias e implantações, por simulação do pipeline completo ou método estatístico validado.

`\eta_primary` será apenas um rótulo para a incerteza relativa operacional calibrada usada no critério de identificabilidade. Ela não entra em `\Delta(q)` contínuo nem constitui uma segunda hipótese. Se não houver definição defensável do modelo de sinal, convenção de SNR e calibração, `U_{95}(q)` será marcado como não disponível e a comparação será `INSTRUMENTALLY_UNDER_RESOLVED` ou não avaliada.

Uma referência local `q_rand` poderá ser explorada apenas quando o suporte `W` tiver sido estabelecido externamente e antes de observar os resultados confirmatórios. Sem tal fundamento, não haverá cálculo de probabilidade local. Mesmo quando disponível, essa referência descreverá a geometria dos dicionários em torno de um intervalo plausível; não substituirá replicação biológica nem produzirá, isoladamente, evidência confirmatória.

### 6.3 H2 — registro descritivo do canal projetado e da prioridade (não inferencial)

A antiga hipótese de concentração/proporção em canais de alta prioridade fica **retirada** nesta versão. Com uma única razão estimada (`n_eff=1`), uma proporção de razões em canais de alta prioridade seria apenas 0 ou 1 e não representa uma frequência populacional estimável.

Para cada `\hat q_r` exploratória que seja legitimamente calculável, registrar somente:

1. o valor observado `\hat q_r` e sua incerteza;
2. o elemento mais próximo `q^* = a^*/b^*` em `H_16`, com regra determinística de desempate;
3. a métrica interna `P(a^*/b^*) = 1/(a^*+b^*)`;
4. o erro de projeção em ppm e a condição de identificabilidade instrumental.

Esse registro é um descritor matemático do mapeamento HMAL, não uma proporção, concentração biológica, preferência acústica ou teste estatístico. Não serão calculados odds ratios, testes de proporção ou p-valores para H2 nesta fase. O descritor não poderá ser usado para resgatar H1 nem para alegar validação biológica.

### 6.4 H3 — utilidade como filtro de controle de qualidade para detecções PAMGuard (engenharia secundária)

H3 será mantida apenas como hipótese de engenharia: avaliar se um escore de QA calculado sobre detecções do PAMGuard ajuda a distinguir detecções rotuladas como verdadeiros positivos de falsos positivos/transientes, em conjunto de avaliação com rótulos independentes.

H3 não é evidência da hipótese bioacústica H1. O escore não poderá usar como prova de organização biológica os harmônicos de uma mesma vocalização. A avaliação deverá separar treino/validação/teste por gravação, dia ou implantação, evitando que janelas do mesmo evento ou gravação apareçam em partições diferentes. AUC e intervalos de confiança serão reportados como métricas de engenharia. O valor AUC > 0,65 poderá ser mantido como meta exploratória, não como prova científica da hipótese H1.

### 6.5 Sub-hipóteses removidas

As antigas H1a (f0 populacional fixo) e H1b (fundamental adaptativo por quadro STFT) são removidas como sub-hipóteses confirmatórias. Elas investigavam variantes de normalização de picos do mesmo chamado e não respondem à pergunta revisada sobre relações entre unidades vocais distintas. Comparações entre estimadores poderão ser realizadas apenas como validação técnica exploratória, sem inferência sobre H1.

## 7. Parâmetros de processamento e extração

### 7.1 Escopo de processamento

O processamento desta versão será restrito à baleia-azul. A configuração de odontocetos (500–48.000 Hz) da versão anterior está fora do escopo e poderá constar de protocolo posterior. Chamados A/B do Pacífico Nordeste são apenas candidatos; sua comparabilidade física deverá ser demonstrada antes de formar uma razão.

### 7.2 Definição da variável e estimação por evento

Antes do piloto, deverá ser definida a variável de cada unidade vocal:

- unidade tonal: `f0` de trecho tonal estável;
- unidade pulsada: `PRR` ou outra medida temporal explicitamente definida, sem renomeá-la `f0`;
- grandezas diferentes não serão divididas entre si sem modelo físico e hipótese específicos.

A medida será estimada uma vez por evento elegível, a partir de segmento estável e algoritmo congelado no piloto. O estimador e a segmentação devem ser apropriados à natureza do sinal (tonal ou pulsado). A STFT pode apoiar localização/inspeção de componentes, mas os quadros serão agregados dentro do evento e nunca tratados como unidades experimentais independentes.

A configuração anterior de janela de 1 s, 75% de sobreposição, zero-padding 4x e interpolação parabólica poderá ser mantida para inspeção exploratória, mas não será automaticamente considerada adequada à inferência em baixa frequência. A duração da janela/segmento deverá ser compatível com o evento, com a estabilidade da grandeza e com a identificabilidade instrumental.

### 7.3 Convenção de SNR e calibração de ruído

O protocolo não fixa ainda um limiar universal de `10 dB`. No piloto, deverá ser documentado qual SNR é calculado, por meio de qual fórmula, em qual domínio, sobre qual janela e com qual estimativa de ruído. No mínimo, distinguir:

- SNR por amostra no domínio temporal (`SNR_sample`);
- SNR integrado no trecho (`SNR_integrated`);
- SNR de pico/bin/quadro no domínio espectral (`SNR_bin`/`SNR_frame`).

O limiar de seleção/qualidade, se utilizado, será definido por calibração independente e não poderá ser tratado como entrada intercambiável de uma expressão de Cramér–Rao. O relatório registrará taxa de amostragem, janela, duração efetiva, banda de ruído, janela espectral e método de estimativa do piso de ruído.

### 7.4 Sobreposição, eventos e clipping

A sobreposição STFT poderá ser usada para melhorar a continuidade da estimativa dentro de um evento. Ela não aumenta o tamanho amostral. A medida de cada evento será agregada por uma regra única congelada (por exemplo, mediana dos quadros válidos de trecho tonal estável).

Eventos com clipping/saturação serão excluídos ou sinalizados conforme regra congelada antes da análise. Clipping é distorção não linear que pode introduzir conteúdo espectral artificial; clipping simétrico frequentemente produz harmônicos ímpares, mas não se afirmará que todo clipping produz exclusivamente harmônicos ímpares.

### 7.5 Sinais sintéticos de calibração

`DS-00-SYNTH` será mantido com `MASTER_SEED=20261106` para teste de recuperação do estimador e calibração instrumental. Os estratos S1, S3, S4 e S5 serão preservados conforme suas definições no artefato de calibração correspondente; S5 será identificado como controle de erro Tipo I. As definições operacionais de cada estrato, frequências/variáveis, SNR por convenção, duração, ruído e métricas deverão ser referenciadas explicitamente antes do congelamento.

O estrato S2 que avalia recuperação de relações 2/1, 3/1 e 4/1 dentro de um mesmo sinal não será usado como evidência confirmatória nem como resultado de suporte à hipótese biológica. Se mantido, será exclusivamente teste unitário do estimador, fora de todas as métricas inferenciais e conclusões sobre H1/H2.

## 8. Plano de análise, estimativa e futura inferência

### 8.1 Análise desta versão: estimativa exploratória

Para um único contexto população/variante × par vocal comparável × temporada, serão reportados:

- número de eventos elegíveis por unidade vocal;
- número de sequências, blocos, dias e implantações;
- estimativas agregadas das medidas acústicas e sua incerteza;
- `\hat q_r`, apenas se as grandezas forem comparáveis;
- `\varepsilon_{ppm}(\hat q_r;H_{16})`, `\varepsilon_{ppm}(\hat q_r;D_{log})` e `\Delta(\hat q_r)` como descritores de geometria;
- resultado do critério instrumental, se `U_{95}(q)` estiver validamente calibrado;
- limitações de acesso, classificação e cobertura temporal.

Não será calculado teste de sinal, Mann–Whitney, odds ratio, bootstrap ou permutação que trate blocos/dias/eventos de uma mesma unidade biológica como replicações independentes. Não será reportado valor-p de H1 para `n_eff=1`. Os intervalos de incerteza apresentados deverão ser intervalos de estimação de `q` sob um procedimento de dependência documentado, não intervalos de inferência populacional entre replicações biológicas.

### 8.2 Desenho confirmatório de fase futura

A confirmação de H1 exigirá múltiplas unidades `r` biologicamente independentes, com variável acústica comparável e identificação independente das unidades vocais. O número de unidades será definido por simulação de poder que incorpore variabilidade entre populações/variantes/temporadas e autocorrelação temporal. O desenho deverá especificar previamente:

1. população, variante e par de unidades vocais em cada `r`;
2. grandeza física idêntica ou justificativa para qualquer razão entre grandezas distintas;
3. distribuição nula biologicamente plausível de `q` ou de `\Delta(q)`, estabelecida sem usar os resultados confirmatórios;
4. hipótese nula, teste, estatística, nível `alpha`, tamanho de efeito mínimo e método de intervalo de confiança;
5. tratamento de dependência dentro de população, temporada, implantação e sequência;
6. número de unidades independentes e simulação de poder;
7. regra de identificabilidade instrumental e tolerância, se usada.

`H_16` versus `D_log` é uma comparação de geometria com igual cardinalidade e suporte. Por si só, não especifica a distribuição de razões que seria esperada ao acaso em uma população biológica. Um modelo `q_rand` local só poderá ser parte do teste confirmatório se seu suporte e distribuição forem derivados de dados externos independentes e congelados previamente. A proposta de usar uma distribuição log-uniforme em vizinhança local poderá ser avaliada como sensibilidade, mas não será tratada automaticamente como nulo válido nem como p-valor biológico.

### 8.3 Análises secundárias e H2/H3

`N=4`, `N=8`, `N=32`, `D_lin`, `H0,unif`, `H0,log` e `H0,perm` serão análises secundárias/descritivas. Não poderão substituir retrospectivamente o resultado principal nem ser selecionadas por produzirem resultados mais favoráveis.

H2 será apenas o registro descritivo do elemento `q^*` em `H_16` e de seu valor `P(a^*/b^*)`, sem proporção ou inferência. H3 será avaliada separadamente como hipótese de engenharia de QA, com separação de dados por gravação/dia/implantação. H3 não constitui evidência da hipótese bioacústica H1.

Não haverá a família confirmatória de 64 testes da versão anterior. Uma família secundária submetida a inferência formal deverá ter sua composição e correção de multiplicidade especificadas em protocolo próprio, antes da análise. Caso contrário, os resultados serão apresentados sem alegação confirmatória.

## 9. Separação exploratória/confirmatória, falsificação e relato

### 9.1 Separação temporal dos dados

Antes do congelamento, registrar em manifesto:

- IDs/intervalos de datas destinados ao piloto exploratório;
- IDs/intervalos de datas destinados à análise confirmatória;
- estação/sensor, implantação e população correspondentes;
- critério de exclusão de blocos e eventos;
- versão e checksum dos arquivos.

Para uma fase confirmatória futura, os dias do piloto não poderão integrar o conjunto confirmatório. Os dados confirmatórios futuros não serão usados para escolher janelas, tolerâncias, limiares de SNR, classificadores, parâmetros ou modelos nulos. Se a separação não puder ser estabelecida, toda a análise será rotulada como exploratória e um novo conjunto confirmatório será necessário.

### 9.2 Regras para afirmações sobre tendências de frequência

Nenhuma afirmação de tendência crescente ou decrescente será feita sem identificar explicitamente:

1. espécie, população e variante vocal;
2. unidade vocal específica (por exemplo, chamado A, chamado B ou subunidade identificada);
3. variável medida e unidade (frequência acústica em Hz, taxa de ocorrência/contagem de chamados ou outra métrica);
4. período coberto;
5. fonte de dados, versão e método de estimação.

Frequência de ocorrência de chamados não será confundida com frequência acústica em hertz. Não se generalizará uma tendência local para toda a espécie sem evidência adequada.

### 9.3 Compromisso com resultados negativos e inconclusivos

Na amostra atual com `n_eff=1`, o resultado de H1 será apresentado como estimativa exploratória, sem declaração de confirmação ou refutação estatística. Ausência de significância não será alegada quando nenhum teste confirmatório válido tiver sido executado.

Na fase confirmatória futura, se o teste pré-especificado não atingir os critérios de efeito e incerteza, o relatório distinguirá entre: (a) suporte à hipótese; (b) não rejeição da hipótese nula; (c) evidência compatível com efeito menor que o mínimo relevante, se houver precisão adequada; e (d) resultado inconclusivo por insuficiência de resolução, amostra ou identificação. `p >= alpha` não será usado como sinônimo automático de refutação.

O descritor H2 e a hipótese de engenharia H3 serão relatados separadamente, sem serem usados para compensar ausência de evidência para H1.

### 9.4 Proibição de pós-seleção

É proibido:

- excluir eventos ou arquivos após observar o erro de projeção em `H_16` ou `D_log`;
- ajustar manualmente frequências fundamentais para melhorar encaixe em `H_N`;
- alterar o conjunto de dados, os dias, a unidade experimental, a tolerância ou o modelo nulo após consultar os resultados confirmatórios;
- selecionar retrospectivamente `N`, tolerância ou modelo nulo favorável;
- contar quadros STFT, picos do mesmo evento ou harmônicos intrachamado como replicações independentes.

Exclusões por qualidade só serão permitidas com base em critérios técnicos definidos antes da análise e serão registradas no log de auditoria.

### 9.5 Congelamento por hash e proveniência

**Nível 1 — exploratório:** após cumprir a Seção 10.1, congelar a versão exploratória v1.3.1 e seu manifesto aplicável. Registrar separadamente `L1_EXPLORATORY_PROTOCOL_SHA256`, `L1_EXPLORATORY_MANIFEST_SHA256` e o hash dos scripts usados. Os resultados devem carregar o rótulo `EXPLORATORY/FEASIBILITY`; esse hash não autoriza inferência confirmatória.

**Nível 2 — confirmatório:** antes de qualquer abertura/análise confirmatória, emitir protocolo/versão própria e manifesto confirmatório, calculando `L2_CONFIRMATORY_PROTOCOL_SHA256`, `L2_CONFIRMATORY_MANIFEST_SHA256` e hashes dos scripts. O congelamento Nível 2 é independente do Nível 1; o hash exploratório não poderá ser reaproveitado como confirmação.

Qualquer alteração após o congelamento de cada nível exigirá nova versão/emenda, hash próprio, data, motivação e indicação explícita se os dados correspondentes já foram observados.

## 10. Congelamentos em dois níveis e checklists de go/no-go

Esta versão separa o congelamento de um **protocolo exploratório/viabilidade (Nível 1)** do congelamento futuro de um **protocolo confirmatório (Nível 2)**. O cumprimento do Nível 1 não autoriza inferência confirmatória nem converte uma estimativa com `n_eff=1` em evidência populacional.

### 10.1 Nível 1 — congelamento exploratório e de viabilidade (v1.3.1)

O Nível 1 pode ser congelado para pré-especificar a ordem dos candidatos, o procedimento de go/no-go e as análises estritamente exploratórias. Não exige que já exista replicação biológica suficiente para H1 confirmatória. Para congelar e executar a avaliação exploratória, devem estar concluídos e documentados:

**A. Seleção prévia do par vocal**

- [ ] A ordem dos candidatos da Seção 2.1 está fixa e não foi alterada após inspeção dos resultados de projeção.
- [ ] O go/no-go de cada candidato foi registrado usando documentação acústica, acesso, identificação e comparabilidade, sem consultar `H_N`, `D_log`, `\Delta(q)` ou `P(a/b)`.
- [ ] Cada decisão foi registrada até o prazo individual: MBARI A/B até 02/11/2026; Chagos unidades 2/3 até 04/11/2026; Atlântico Norte A/B até 05/11/2026 (23:59, horário de Brasília).
- [ ] Ausência de autorização, resposta ou acesso concluído até o prazo foi classificada como NO-GO nesta versão; não houve extensão informal ou espera indefinida.
- [ ] Ao obter o primeiro GO, a seleção foi encerrada; nenhum candidato posterior foi usado como substituto após observação de resultados.
- [ ] O chamado A/B do MBARI não é tratado como par comparável sem justificativa física independente; o estado presumido de no-go está explicitado.
- [ ] Chagos unidades 2/3 só pode avançar com áudio autorizado contendo ambas as unidades; o Zenodo 10.5281/zenodo.22654272 não é tratado como fonte desse áudio.
- [ ] O par Atlântico Norte A/B só pode avançar mediante fonte de áudio, acesso/termos de uso e identificação das duas unidades efetivamente verificados.
- [ ] Se nenhum candidato passar, o resultado será `H1_NOT_OPERATIONALIZABLE_THIS_PHASE`; nenhum par novo será introduzido nesta versão.

**Regra condicional para os blocos B, C e D:** se todos os candidatos da Seção 2.1 forem NO-GO nos respectivos prazos, marcar cada item aplicável dos blocos B, C e D como `N/A — nenhum candidato elegível; H1_NOT_OPERATIONALIZABLE_THIS_PHASE`, registrando a razão. Isso não impede o congelamento do Nível 1 como protocolo de viabilidade. Os registros de busca, evidência e decisão de cada candidato continuam obrigatórios no bloco A. Se pelo menos um candidato passar, B, C e D deixam de ser N/A e os requisitos pertinentes ao candidato selecionado devem ser cumpridos. O bloco E é sempre obrigatório.

**B. Mensuração e comparabilidade**

- [ ] Para o candidato que passar, a variável medida em cada unidade está definida por escrito (`f0`, `f_peak`, `PRR` ou outra), com unidade, algoritmo, segmento de análise e justificativa física.
- [ ] As duas medidas usadas em `q` representam a mesma grandeza operacional ou há justificativa física independente, escrita antes da projeção em `H_N`.
- [ ] A identificação de eventos/unidades é independente do mapeamento HMAL.
- [ ] Há no máximo uma medida agregada por evento conforme regra definida; quadros STFT e picos intrachamado não são unidades independentes.
- [ ] A segmentação, regra de agregação, exclusões de qualidade e tratamento de unidade ausente estão definidos para o piloto.

**C. SNR, resolução e calibração exploratória**

- [ ] A convenção de SNR usada em cada métrica está identificada como `SNR_sample`, `SNR_integrated` ou `SNR_bin/frame`, com fórmula, janela, banda e estimativa de ruído.
- [ ] A expressão de Cramér–Rao, quando utilizada, corresponde ao modelo de sinal, ao estimador e à convenção de SNR; não é tratada como erro real garantido.
- [ ] O protocolo de calibração com `DS-00-SYNTH`, `MASTER_SEED=20261106`, S1, S3, S4 e S5 está especificado; S5 continua sendo controle de erro Tipo I.
- [ ] `U95(q)` só é reportado se a calibração do pipeline e a propagação de incerteza forem executadas e documentadas; caso contrário, será `NOT_ESTIMATED` e não haverá alegação de identificabilidade.
- [ ] O descritor H2 limita-se a `q^*`, `P(a^*/b^*)`, erro de projeção e estado instrumental; não calcula proporção ou teste de concentração.

**D. Dados e proveniência**

- [ ] Para qualquer áudio usado, o acesso, termos/licença, versão, data de obtenção e proveniência estão verificados e registrados.
- [ ] IDs/intervalos de datas do piloto e da avaliação descritiva estão definidos sem sobreposição; se não houver conjunto descritivo separado, todo resultado será rotulado como piloto exploratório.
- [ ] Estação/sensor, implantação, metadados, taxa de amostragem, duração, checksums e critérios de inclusão/exclusão estão registrados.
- [ ] `MASTER_SEED`, versão do código, parâmetros, manifesto SHA-256 e log de auditoria estão preservados.

**E. Escopo e comunicação dos resultados**

- [ ] O Nível 1 está rotulado como exploratório/viabilidade, sem valor-p biológico ou confirmação de H1 para `n_eff=1`.
- [ ] H3 permanece hipótese secundária de engenharia e não é apresentada como evidência bioacústica.
- [ ] A documentação distingue explicitamente no-go de dados, não operacionalizabilidade, estimativa exploratória e inconclusão instrumental.

Ao concluir A–E — ou, quando todos os candidatos forem NO-GO, ao concluir A e E e marcar justificadamente B, C e D como `N/A` — o operador poderá congelar o protocolo exploratório v1.3.1 com o rótulo `FREEZE_LEVEL_1_EXPLORATORY`. Nesse caso, o resultado será `H1_NOT_OPERATIONALIZABLE_THIS_PHASE`; não haverá estimativa de `q`, análise H1 com áudio nem inferência biológica nesta fase.

### 10.2 Nível 2 — congelamento confirmatório futuro (novo protocolo/versão)

O Nível 2 será especificado em versão própria, com data e hash independentes. Não é requisito para congelar o protocolo exploratório v1.3.1 e não pode ser declarado concluído por cumprir apenas a checklist do Nível 1.

Antes de qualquer análise confirmatória, deverão ser concluídos:

- [ ] Múltiplas unidades de replicação biológica independentes, definidas e justificadas (população/variante × par de unidades comparáveis × temporada); a dependência entre populações, variantes e temporadas será modelada.
- [ ] Simulação de poder com parâmetros e variabilidade biologicamente fundamentados para determinar o número de unidades independentes.
- [ ] Modelo nulo biológico primário, com distribuição de `q`/`\Delta(q)` justificada por evidência externa independente, suporte e parâmetros congelados antes dos dados confirmatórios.
- [ ] Estatística primária, regra de decisão, tamanho de efeito mínimo, `alpha`, intervalo de confiança e família de testes pré-especificados; análises secundárias e correção de multiplicidade definidas separadamente.
- [ ] Procedimento inferencial reproduzível que respeite a hierarquia de eventos, sequências, dias, implantações, populações e temporadas.
- [ ] Dataset confirmatório com acesso/termos verificados, amostragem independente do piloto e manifestos/checksums congelados.
- [ ] Método de mensuração, convenção de SNR, calibração, tolerância/identificabilidade e todos os critérios de exclusão congelados antes da abertura dos dados confirmatórios.
- [ ] Novo arquivo de protocolo ou emenda versionada, com `L2_CONFIRMATORY_PROTOCOL_SHA256`, `L2_CONFIRMATORY_MANIFEST_SHA256` e hash dos scripts/análise correspondentes.

Não será reutilizado o hash do Nível 1 como se fosse congelamento confirmatório. Qualquer alteração depois do congelamento de cada nível exige versão/emenda, data, justificativa e indicação explícita se os dados daquele nível já foram observados.

### 10.3 Resultado para a reunião da COPPE/UFRJ

Até a reunião, o resultado defensável é o protocolo exploratório pré-especificado, a lista ordenada de candidatos, os critérios de go/no-go, a matriz de proveniência e os limites do que os dados permitem estimar. Não apresentar valores de H1 como confirmação. Se nenhum par passar, apresentar a não operacionalizabilidade nesta fase como resultado de viabilidade, juntamente com o requisito de dados para a fase 2.

## 11. Registro de alterações desta versão

Em relação à versão 1.2.0-draft:

1. Foi incluído registro fixo e ordenado de três pares candidatos, com critérios de elegibilidade e regra de go/no-go decididos sem consultar a projeção em `H_N`, `D_log`, `\Delta(q)` ou `P(a/b)`.
2. O par Pacífico Nordeste A/B foi classificado como presumivelmente não comparável (`PRR` pulsada versus `f0` tonal), salvo justificativa física independente anterior à análise.
3. Chagos unidades 2/3 foram incluídas como candidato tonal condicional, distinguindo a caracterização de Leroy et al. (2021) da indisponibilidade do áudio original no dataset Zenodo de Jancovich & Rogers (2026).
4. Atlântico Norte A/B foi incluído como reserva condicional, com acesso a áudio e identificação ainda não verificados.
5. A antiga H2 de proporção/concentração foi retirada e substituída pelo registro descritivo do elemento mais próximo de `H_16` e de `P(a/b)` para uma única razão.
6. A checklist foi dividida em Nível 1 exploratório/viabilidade e Nível 2 confirmatório futuro, com requisitos, versões e hashes separados.
7. **v1.3.1:** foram acrescentados prazos finais de decisão por candidato (MBARI 02/11/2026, Chagos 04/11/2026 e Atlântico Norte 05/11/2026, todos às 23:59 em Brasília), com NO-GO automático se os requisitos não forem demonstrados até cada prazo.
8. **v1.3.1:** a checklist do Nível 1 permite marcar os blocos B, C e D como `N/A — nenhum candidato elegível` quando todos os pares forem NO-GO, registrando `H1_NOT_OPERATIONALIZABLE_THIS_PHASE`, sem impedir o congelamento exploratório.
9. **v1.3.1:** o título foi alterado para “Relações entre Medidas Acústicas Comparáveis de Unidades Vocais Distintas”, evitando pressupor que todas as variáveis mensuradas sejam frequências fundamentais.

**Estado final:** versão 1.3.1-draft, candidata a congelamento do Nível 1. O Nível 1 autoriza somente protocolo exploratório/viabilidade após os critérios da Seção 10.1; não autoriza inferência confirmatória. O Nível 2 depende de replicação biológica independente, simulação de poder, modelo nulo biologicamente fundamentado, mensuração comparável e congelamento/hash separados.