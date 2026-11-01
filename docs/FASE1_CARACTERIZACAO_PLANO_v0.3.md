# HMAL Lab — Fase 1: caracterização acústica básica

**Versão:** 0.3 (incorpora os pareceres técnicos da Luna sobre a v0.1 e a v0.2; aguarda aprovação de implementação) · **Data:** 01/11/2026 · **Estado:** plano técnico; nenhuma linha de implementação foi escrita e nenhum dado novo foi baixado ou observado para elaborá-lo. **Rótulo de todos os resultados desta fase:** `EXPLORATORY/FEASIBILITY`.

**Documentos relacionados:**
- `lab/PREREGISTRATION.md` (v1.3.1-draft), que tem precedência sobre este plano em qualquer conflito;
- `lab/DATASETS.md`;
- `lab/bench/e1_mbari.py` e `lab/bench/e1_reference.json`;
- `docs/EDITORIAL_HMAL_LAB_v1.md` (v1.2);
- proposta de evolução da Luna (Fase 0 a Fase 5).

## 1. Objetivo e tese da fase

A Fase 1 tem por objetivo permitir que um registro acústico real seja examinado na HMAL Lab por meio de três elementos:
- uma ficha de caracterização com parâmetros, unidades, referências de medição e origem identificados;
- a forma de onda;
- o espectrograma.

O leitor poderá selecionar um intervalo da gravação e consultar os mesmos parâmetros calculados apenas para esse intervalo. A fase não pretende interpretar biologicamente o som. Seu propósito é demonstrar que o HMAL consegue extrair, apresentar e explicar corretamente características elementares de uma gravação real, com procedimentos determinísticos, verificáveis e documentados.

Essa demonstração constitui a base metodológica das fases seguintes. O critério de aceite proposto pela Luna para a visualização básica orienta todo o plano: "um registro pode ser examinado com parâmetros, unidades e origem identificados".

A Fase 1 não altera nem amplia a declaração de TRL 4 (nível de maturidade tecnológica 4) do subsistema computacional. Seu resultado é uma demonstração própria de capacidade de análise e apresentação de dados reais.

## 2. Escopo

### 2.1 Incluído

1. **Pipeline em Python, fora do navegador.**
   - Lê os arquivos WAV (Waveform Audio File Format) diários do conjunto público Pacific Ocean Sound Recordings, do MBARI (Monterey Bay Aquarium Research Institute), na versão decimada a 2 kHz.
   - Confere o SHA-256 de cada arquivo.
   - Recorta trechos por regra fixa (Seção 3).
   - Produz os dados de cada trecho em arquivos versionados.
2. **Ficha de caracterização** de cada trecho e de cada intervalo selecionado, com os parâmetros da Seção 4.
3. **Forma de onda** em pressão acústica (pascal), representada por envoltória de mínimos e máximos.
4. **Espectrograma** em densidade espectral de potência, em dB re 1 µPa²/Hz (decibéis em relação a um micropascal ao quadrado por hertz).
5. **Seleção de intervalo:**
   - por arraste sobre o gráfico;
   - por campos numéricos de início e fim, para uso com teclado;
   - com as regras de alinhamento da Seção 4.2.
6. **Testes:**
   - sinais sintéticos de valor conhecido;
   - conferência cruzada entre o cálculo em Python e o cálculo da página;
   - conferência de proveniência.
7. **Blocos editoriais** no padrão de três camadas: tese, "Como interpretar esta informação?" e "Método e limitações". Eles entram como versão 1.3 do documento editorial e passam por nova revisão.

### 2.2 Excluído desta fase

Os itens abaixo não serão implementados nem sugeridos pela interface nesta fase:
- estimativa de frequência fundamental;
- detecção ou contagem de harmônicos;
- relação entre componentes (Fase 2);
- assinatura espectral e temporal;
- comparação entre registros (Fase 3);
- classificação de fontes ou espécies (Fase 4);
- qualquer relação com o protocolo harmônico ou com o dicionário H₁₆ (Fase 5).

O código da Fase 1 não importará `src/hmal/core/harmonic_protocol.py` e não calculará projeções em H_N, `D_log`, `Δ(q)` nem `P(a/b)`.

As medições não serão produzidas nem alteradas por modelos de inteligência artificial. Os cálculos de pressão, nível, densidade espectral e frequência dominante são determinísticos.

A fase também não toca nenhum arquivo protegido por `FREEZE_v0.4.json` nem altera a bancada digital.

### 2.3 Relação com o pré-registro

A Seção 2.1 do pré-registro determina que a elegibilidade dos pares candidatos de H1 seja decidida sem consultar o erro de projeção em H_N. Como a Fase 1 não calcula projeções, ela não interfere nessa regra.

Ainda assim, a ficha de caracterização não será utilizada como evidência para nenhuma decisão GO/NO-GO de H1, e não poderá ser usada para alterar retrospectivamente os critérios dessas decisões. Elas continuam regidas exclusivamente pelos critérios e prazos do pré-registro; o prazo do par MBARI A/B é 02/11/2026, às 23:59, horário de Brasília.

Para não abrir dados novos antes da separação exigida pela Seção 9.1 do pré-registro, a Fase 1 utiliza apenas os três dias já observados no ensaio E1: 01, 11 e 22 de novembro de 2016. Esses dias ficam registrados como exploratórios e, conforme a mesma seção, não poderão integrar um conjunto confirmatório futuro. O rótulo `EXPLORATORY/FEASIBILITY` acompanha os seis trechos nos metadados, no manifesto, nos arquivos produzidos e na interface.

## 3. Dados e seleção dos trechos

### 3.1 Fonte

- **Conjunto:** Pacific Ocean Sound Recordings, bucket `pacific-sound-2khz` (AWS Open Data).
- **Arquivos:** os mesmos três WAV diários do E1, com SHA-256 já registrados em `lab/bench/results/e1/E1.json`. O pipeline recusa qualquer arquivo cujo resumo divirja desses valores.
- **Taxa de amostragem:** 2.000 Hz.
- **Formato:** PCM (Pulse-Code Modulation) de 24 bits, um canal.
- **Licença:** CC BY 4.0, com a atribuição exigida pelo MBARI.
- O código dos notebooks do MBARI, sob GPL, não é copiado; o pipeline reimplementa apenas as convenções de calibração já documentadas no E1.

### 3.2 Regra fixa de seleção

A regra é declarada antes de qualquer processamento e não admite escolha visual. Em cada um dos três dias, são extraídos dois trechos de 120 s:

- **Trecho A, maior índice do canto B:**
  - Usa o minuto de maior índice B (CI) entre os minutos válidos da série já publicada `series_<dia>.json`.
  - O trecho começa 30 s antes do início desse minuto.
  - O rótulo na página será "trecho de maior índice do canto B no dia", nunca "canto de baleia identificado". O índice mede uma característica espectral associada ao canto B, não a identificação de uma vocalização.
- **Trecho B, menor índice do canto B:**
  - Usa o minuto válido de menor índice B no mesmo dia, com o mesmo recorte.
  - Serve como contraste descritivo, e não como "ruído de fundo" no sentido estatístico.

São válidos os minutos com menos de 1% de amostras nulas, a mesma regra do E1.

Se um trecho ultrapassar o início ou o fim do arquivo, desloca-se o recorte para dentro do dia, e o deslocamento é registrado. Empates são resolvidos pelo minuto mais antigo.

O total é de seis trechos e 12 minutos de áudio, uma quantidade pequena o bastante para ser verificada integralmente.

Os trechos são exemplos escolhidos pelos extremos de um índice já conhecido, e não uma amostra representativa da paisagem acústica do local. A interface dirá isso expressamente.

## 4. Parâmetros da ficha de caracterização

### 4.1 Cadeia de unidades

A conversão segue quatro passos, todos explícitos na página:
1. A leitura do arquivo WAV fornece uma amostra normalizada, adimensional, entre −1 e 1.
2. A multiplicação pelo fator 3 produz a tensão em volts, segundo a convenção do E1 e do exemplo de processamento do MBARI.
3. A sensibilidade nominal do hidrofone converte a tensão em pressão: `p[µPa] = V / 10^(S/20)`, com S = −168,8 dB re 1 V/µPa para gravações anteriores a 14/06/2017. O MBARI informa que esse valor foi medido a 26 Hz.
4. Para a forma de onda em pascal, divide-se a pressão em micropascal por 10⁶.

Essa conversão não é uma calibração independente. A sensibilidade nominal é tratada como plana em toda a banda, sem correção da resposta real em frequência do sistema de gravação. A página dirá isso no acordeão de método, em atendimento à decisão 3 da proposta da Luna: não apresentar uma estimativa como medição física calibrada.

### 4.2 Grade temporal e seleção de intervalos

O navegador recebe espectros já calculados, e não o arquivo WAV completo. Para que a página reproduza exatamente o cálculo de referência do Python, a seleção obedece a regras fixas:

- Início e fim do intervalo ficam alinhados a uma grade de 0,5 s, tanto no arraste quanto nos campos numéricos.
- Depois do ajuste, a página mostra o intervalo efetivamente usado.
- O cálculo espectral usa somente as janelas de Welch inteiramente contidas no intervalo. Cada janela tem 1 s (2.000 amostras) e começa a cada 0,5 s. Um intervalo [a, b] alinhado contém `(b − a − 1)/0,5 + 1` janelas.
- A duração mínima é de 10 s, o que equivale a 19 janelas.
- Os parâmetros do domínio do tempo usam blocos de 50 ms. Como 0,5 s é múltiplo de 50 ms, todo intervalo alinhado é composto de blocos completos.

### 4.3 Parâmetros

| Parâmetro | Definição operacional | Unidade |
|---|---|---|
| Origem | Bucket, chave do arquivo, SHA-256, sensor (MARS), data e hora UTC (Tempo Universal Coordenado) de início e fim, deslocamento em amostras, sensibilidade usada, licença, rótulo `EXPLORATORY/FEASIBILITY` | — |
| Duração | Número de amostras do intervalo dividido pela taxa de amostragem | s |
| Nível de pressão sonora eficaz de banda larga | Valor RMS (raiz do valor quadrático médio) da pressão após remoção da média do intervalo; `20·log10(p_rms / 1 µPa)` | dB re 1 µPa, 0–1.000 Hz |
| Nível na banda de 10 a 990 Hz | Integral do espectro médio entre 10 e 990 Hz | dB re 1 µPa |
| Nível de pico | Maior valor absoluto da pressão após remoção da média do intervalo; `20·log10(p_pico / 1 µPa)` | dB re 1 µPa |
| Espectro médio | Método de Welch, janela Hann de 2.000 amostras, nfft 2.000 (resolução de 1 Hz), sobreposição de 50%, remoção da média de cada janela (padrão do SciPy), espectro unilateral em densidade, média no domínio linear | dB re 1 µPa²/Hz |
| Percentis espectrais | Percentis 5, 50 e 95 da densidade espectral de cada frequência ao longo das janelas do intervalo | dB re 1 µPa²/Hz |
| Frequência dominante (indicador espectral) | Frequência de maior densidade no espectro médio entre 10 e 990 Hz, informada só quando a proeminência (diferença em relação à mediana da banda) for de pelo menos 6 dB; abaixo disso, a ficha diz "sem componente dominante" | Hz, resolução de 1 Hz |
| Proporção de amostras nulas | Percentual de valores digitais exatamente iguais a zero, usado como indicador operacional de ausência de dados, conforme a convenção do E1. Um zero isolado pode ser uma amostra acústica legítima | % |
| Saturação | Fração de amostras com valor absoluto igual ou superior a 0,999 da escala máxima | % |

Algumas definições exigem cuidado na apresentação:
- **Frequência dominante:** é um indicador espectral, a região de maior energia no intervalo. Não é a frequência fundamental, não identifica uma fonte sonora e não indica um tom biológico. A página repetirá essa distinção, lembrando que a fundamental nem sempre é a componente de maior energia.
- **Limiar de 6 dB:** é uma regra instrumental de apresentação, e não um critério biológico. O teste S2 verifica que ele não aponta componentes em ruído branco. Isso não demonstra que o mesmo limiar distingue corretamente componentes tonais em ruído oceânico colorido, e a página dirá isso.
- **Nível de banda larga e espectro médio:** não são numericamente equivalentes. A remoção da média de cada janela no método de Welch descarta conteúdo abaixo de cerca de 1 Hz, que o nível de banda larga inclui. Em ruído colorido simulado, a diferença chegou a 2,7 dB. Por isso a verificação de coerência entre os domínios (R2) compara estimadores equivalentes.

## 5. Arquitetura e entregáveis

1. **Módulo `lab/char/characterize.py`:**
   - lê o WAV, confere o SHA-256 e aplica a regra da Seção 3.2;
   - grava em `lab/char/results/c1/` dois tipos de arquivo:
     - **conteúdo científico determinístico**, comparado byte a byte entre execuções:
       - `c1_results.json`: fichas dos seis trechos, parâmetros de processamento, regra de seleção, rótulo `EXPLORATORY/FEASIBILITY`;
       - `<trecho>.env.json`: um registro a cada bloco de 50 ms, com número de amostras, soma das amostras, soma dos quadrados, mínimo e máximo, em pressão (µPa). Com esses cinco valores, a página calcula a média do intervalo, o nível eficaz após remover essa média e o nível de pico (`max(|máx − média|, |mín − média|)`), de forma exata para intervalos compostos de blocos completos;
       - `<trecho>.psd.bin`: matriz de densidade espectral por janela, de 0 a 1.000 Hz, em inteiros de 16 bits com passo de 0,01 dB e deslocamento declarado no `c1_results.json`. São 239 janelas por 1.001 frequências, cerca de 480 kB por trecho, carregados só quando o trecho é aberto;
     - **metadados de execução**, fora da comparação byte a byte:
       - `c1_run.json`: data e hora, identificador do workflow e da execução, imagem do executor, versões de Python, NumPy, SciPy, soundfile e libsndfile, sistema e arquitetura.
2. **Workflow `.github/workflows/characterize.yml`:**
   - acionamento manual;
   - executor `ubuntu-24.04`, não `ubuntu-latest`, cujo rótulo migra para o Ubuntu 26.04 em novembro de 2026;
   - processamento dentro de um contêiner Python fixado por digest, com o digest registrado neste plano na implementação;
   - dependências completas, inclusive transitivas, instaladas com `pip --require-hashes`;
   - ações fixadas por SHA;
   - baixa os três WAV por HTTPS anônimo e confere o SHA-256;
   - executa o módulo duas vezes e compara byte a byte apenas os arquivos de conteúdo científico;
   - publica os resultados como artefato.

   A execução no GitHub Actions substitui a execução manual em máquina virtual usada no E1. Com isso, a proveniência passa a ter tipo `github_actions` e identificador de execução.
3. **Incorporação ao repositório:** o artefato tem prazo de retenção (90 dias por padrão) e não substitui a proveniência versionada. O procedimento é:
   1. o workflow produz o artefato;
   2. o Guilherme baixa e inspeciona os resultados;
   3. os arquivos aprovados entram na branch do PR;
   4. um manifesto próprio, `lab/char/results/MANIFEST.json`, registra o conjunto `c1`, com o SHA-256 de cada arquivo, o identificador da execução e o rótulo `EXPLORATORY/FEASIBILITY`;
   5. o `site/build_data.py` verifica esse manifesto antes de cada publicação.

   O manifesto da bancada (`lab/bench/results/MANIFEST.json`) não é alterado. Lá, cada conjunto é tratado como execução da bancada, os caminhos são resolvidos dentro de `lab/bench/results` e o agregador é chamado para os modos hf e lf. Por isso, o `site/build_data.py` ganha uma verificação separada para o manifesto de caracterização, que confere caminhos seguros dentro de `lab/char/results`, resumos SHA-256 e cobertura dos arquivos obrigatórios, sem chamar o agregador da bancada. Os dados entram no `site.json` em um campo próprio.
4. **Página:**
   - nova seção "Caracterização acústica", depois do E1;
   - seletor de trecho, espectrograma desenhado em canvas a partir do `.psd.bin`, forma de onda e ficha;
   - o cálculo da ficha para um intervalo selecionado repete na página as mesmas fórmulas do Python, sobre os mesmos dados;
   - nenhuma requisição externa.
5. **Editorial v1.3:**
   - seção 5.2, com tese e acordeões para a ficha, a forma de onda e o espectrograma;
   - submetida à Luna antes da implementação na página.

## 6. Critérios de aceite

A Fase 1 só será considerada concluída quando todos os critérios abaixo forem atendidos, verificados em teste automatizado ou em registro de execução, conforme indicado.

### 6.1 Verificação com sinais sintéticos (pytest, sementes determinísticas)

| Código | Teste | Critério |
|---|---|---|
| S1 | Tom de 50,0 Hz com amplitude conhecida, 120 s | Nível eficaz de banda larga, nível na banda de 10 a 990 Hz e nível de pico a até ±0,1 dB do valor teórico; frequência dominante = 50 Hz |
| S2 | Ruído branco gaussiano de variância conhecida, 1.000 sementes, intervalos de 10 s e de 120 s | Mediana da densidade espectral a até ±0,5 dB do valor teórico; limite superior unilateral exato de Clopper–Pearson a 95% para a proporção de frequências dominantes falsas de no máximo 1%, em cada duração. Com zero falsos em 1.000, o limite fica em cerca de 0,3% |
| S3 | Tom de 80 Hz somado ao ruído do S2 com proeminência teórica de 10 dB | Frequência dominante = 80 Hz em todas as sementes |
| S4 | Sequência de zeros e amostras saturadas inseridas em posições conhecidas | Proporções de amostras nulas e saturadas exatas |
| S5 | Pulso tonal de 80 Hz iniciado em 30,00 s, sobre ruído branco gaussiano, em sinal de 60 s. A relação sinal-ruído é de 20 dB na banda de 0 a 1.000 Hz: potência do tom (A²/2) dividida pela variância do ruído | Algoritmo fixado antes da implementação. Na envoltória, o nível de cada bloco de 50 ms é `L_i = 20·log10(p_RMS,i / 1 µPa)`, e `L_ref` é a mediana de `L_i` nos blocos dos primeiros 10 s; o início é o primeiro bloco com `L_i ≥ L_ref + 10 dB`. No espectrograma, a densidade em 80 Hz de cada janela é convertida para dB re 1 µPa²/Hz, e a referência é a mediana desses valores nas janelas dos primeiros 10 s; o início é a primeira janela que alcança a referência + 10 dB, datada pelo seu instante inicial. Erro máximo de 50 ms na envoltória e de 0,5 s no espectrograma |
| S6 | Conversão de unidades | Para uma amostra normalizada conhecida, os valores intermediários (tensão em V, pressão em µPa e em Pa) coincidem com os analíticos, com erro relativo inferior a 10⁻⁹ em cada passo |
| S7 | Serialização do `.psd.bin` | Para matrizes espectrais sintéticas que cobrem a faixa de valores esperada, a reconstrução a partir dos inteiros de 16 bits tem erro máximo de 0,005 dB (metade do passo de 0,01 dB), e nenhum valor satura; a serialização recusa valores fora da faixa representável, em vez de truncá-los |

### 6.2 Verificação com os dados reais

| Código | Teste | Critério |
|---|---|---|
| R1 | Integridade de origem | Os SHA-256 dos três WAV coincidem com os registrados no E1; qualquer divergência interrompe a execução |
| R2 | Coerência entre domínios (teorema de Parseval) para a representação de Welch | Para cada trecho, comparam-se dois estimadores sob o mesmo procedimento: a média, entre as janelas, da potência de cada janela de 1 s após remoção da sua média e aplicação da janela Hann, normalizada pela soma dos quadrados da janela; e a integral da densidade espectral unilateral de 0 a 1.000 Hz, calculada como soma discreta dos valores de todos os bins, de 0 Hz a 1.000 Hz inclusive, multiplicados pela resolução de 1 Hz, sem regra trapezoidal. A normalização unilateral é a do SciPy, que não dobra os bins de 0 Hz e de Nyquist. Diferença máxima de 0,01 dB. Em teste prévio com ruído colorido simulado, a diferença foi da ordem de 10⁻¹⁴ dB. O nível de banda larga não entra nesta comparação |
| R3 | Reprodutibilidade | Duas execuções no mesmo workflow produzem arquivos de conteúdo científico byte a byte idênticos; `c1_run.json` fica fora da comparação |
| R4 | Regra de seleção | Os inícios dos seis trechos coincidem com os calculados independentemente a partir das séries `series_<dia>.json` publicadas |

### 6.3 Verificação da página

| Código | Teste | Critério |
|---|---|---|
| P1 | Concordância entre Python e página | Para 20 intervalos determinísticos por trecho, com limites na grade de 0,5 s, os valores da ficha calculados no navegador coincidem com os do Python a até 0,05 dB, com a mesma frequência dominante ou a mesma ausência dela |
| P2 | Manifesto | O build falha se qualquer arquivo do conjunto `c1` divergir do SHA-256 registrado em `lab/char/results/MANIFEST.json`, ou se o manifesto da bancada for alterado por esta fase |
| P3 | Privacidade e robustez | Nenhuma requisição externa, nenhum erro de console e nenhuma rolagem horizontal em 390 px de largura |
| P4 | Acessibilidade | A seleção de intervalo funciona só com teclado, sem depender do arraste; o espectrograma tem descrição textual equivalente; os estados não dependem só de cor |
| P5 | Escopo | Nenhuma tela exibe frequência fundamental, harmônicos, espécie ou canal H₁₆; um teste confere que o módulo da Fase 1 não importa o protocolo harmônico |

### 6.4 Verificação de governança

Os códigos passam de E1–E3 para G1–G3, porque "E1" já identifica o ensaio do índice do MBARI.

| Código | Critério |
|---|---|
| G1 | Cada novo painel tem tese visível e os dois acordeões, com texto aprovado pela Luna na versão 1.3 do editorial |
| G2 | A página informa a cadeia de unidades, que os níveis usam a sensibilidade nominal do MBARI e que não constituem calibração independente |
| G3 | Nenhum arquivo protegido por `FREEZE_v0.4.json` foi alterado, conforme verificação do `freeze.py` no build |

## 7. Limitações declaradas

1. A sensibilidade nominal, medida a 26 Hz, é tratada como plana em toda a banda. A resposta em frequência real do sistema de gravação não é corrigida, porque não está documentada no conjunto de dados consultado.
2. Os arquivos de 2 kHz são versões decimadas do registro original. Conteúdo acima de 1.000 Hz não pode ser recuperado nem analisado a partir desses arquivos, e a página dirá isso.
3. O trecho de maior índice B indica maior energia relativa na banda do terceiro harmônico do canto B. Isso não equivale a detecção confirmada de um chamado nem a identificação de indivíduo ou população.
4. Seis trechos escolhidos pelos extremos de um índice, em três dias, não descrevem a paisagem sonora do local nem sua variação sazonal. Servem para demonstrar o método, e não para tirar conclusões ambientais.
5. A ficha descreve o intervalo como um todo. Fontes simultâneas, como uma embarcação e um animal, aparecem somadas no espectro, sem separação.
6. O limiar de proeminência foi verificado apenas em ruído branco. Seu comportamento em ruído oceânico colorido não é garantido.

## 8. Cronograma proposto

| Data | Etapa |
|---|---|
| 01/11 | Revisão final deste plano v0.2 pela Luna e aprovação do Guilherme |
| 02/11 | Módulo, testes sintéticos (S1–S7) e workflow; PR em rascunho |
| 02–03/11 | Execução do workflow; conferência de R1–R4; o artefato é baixado e inspecionado pelo Guilherme |
| 03/11 | Editorial v1.3, seção 5.2, para revisão da Luna; implementação na página e P1–P5 |
| 04/11 | Revisão final da Luna e merge pelo Guilherme |

A precisão metodológica tem prioridade sobre o cronograma. Se os critérios não estiverem implementados e verificados até 04/11, a seção não será publicada antes da entrevista de 06/11. A página atual permanece como está, e a Fase 1 é apresentada como trabalho em andamento, com este plano como evidência.

## 9. Alterações em relação às versões anteriores

### 9.1 Da v0.2 para a v0.3

| Pendência do parecer da Luna sobre a v0.2 | Onde foi incorporada |
|---|---|
| Manifesto de caracterização independente do manifesto da bancada | Seção 5, item 3 |
| S5 com nível RMS em dB, mediana de referência e banda da relação sinal-ruído | Critério S5 |
| R2 com soma discreta dos bins e tratamento de 0 Hz e Nyquist | Critério R2 |
| Redação da limitação sobre conteúdo acima de 1.000 Hz | Limitação 2 |
| Teste de serialização do `.psd.bin` | Critério S7 |

### 9.2 Da v0.1 para a v0.2

| Pendência do parecer da Luna | Onde foi incorporada |
|---|---|
| 1. Seleção em passos de 0,5 s, alinhada às janelas de Welch | Seção 4.2; critério P1 |
| 2. Envoltória com contagem, soma, soma dos quadrados, mínimo e máximo por bloco de 50 ms | Seção 5, item 1 |
| 3. R2 comparando estimadores equivalentes | Critério R2; nota na Seção 4.3 |
| 4. S2 com 1.000 sementes e limite de Clopper–Pearson | Critério S2 |
| 5. "Proporção de amostras nulas" | Seções 3.2 e 4.3; critério S4 |
| 6. Algoritmo de início do S5 e unidades intermediárias do S6 | Critérios S5 e S6; Seção 4.1 |
| 7. Metadados de execução separados do conteúdo científico | Seção 5, item 1; critério R3 |
| 8. Ambiente fixado e incorporação do artefato ao manifesto | Seção 5, itens 2 e 3 |
| 9. E1–E3 renomeados para G1–G3 | Seção 6.4 |
| Rótulo `EXPLORATORY/FEASIBILITY` | Cabeçalho; Seções 2.3, 3 e 5 |
| "Frequência dominante" como indicador espectral | Seção 4.3; limitação 6 |

Duas verificações numéricas foram feitas ao preparar esta versão, com dados simulados e sem dados reais:
- **S2:** zero falsos em 1.000 sementes, nas duas durações. A maior proeminência foi de 4,37 dB em 10 s e de 1,38 dB em 120 s.
- **R2:** em ruído colorido simulado, os estimadores equivalentes diferiram em cerca de 10⁻¹⁴ dB. Já o valor eficaz global diferiu em 2,7 dB da integral de Welch, o que confirma a correção apontada pela Luna.

## 10. Decisões solicitadas

1. Confirmar que os ajustes da Seção 9.1 atendem ao parecer técnico sobre a v0.2.
2. Autorizar o início da implementação no PR #13, ou em PR próprio a partir dele.

Generated by Claude
