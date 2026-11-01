# HMAL Lab — Fase 1: caracterização acústica básica

**Versão:** 0.1 (rascunho para revisão da Luna e aprovação do Guilherme) · **Data:** 01/11/2026 · **Estado:** plano técnico; nenhuma linha de implementação foi escrita e nenhum dado novo foi baixado ou observado para elaborá-lo.

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

## 2. Escopo

### 2.1 Incluído

1. **Pipeline em Python, fora do navegador.**
   - Lê os arquivos WAV (Waveform Audio File Format) diários do conjunto público Pacific Ocean Sound Recordings, do MBARI (Monterey Bay Aquarium Research Institute), na versão decimada a 2 kHz.
   - Confere o SHA-256 de cada arquivo.
   - Recorta trechos por regra fixa (Seção 3).
   - Produz os dados de cada trecho em arquivos versionados.
2. **Ficha de caracterização** de cada trecho e de qualquer intervalo selecionado, com os parâmetros da Seção 4.
3. **Forma de onda** em pressão acústica (pascal), representada por envoltória de mínimos e máximos.
4. **Espectrograma** em densidade espectral de potência, em dB re 1 µPa²/Hz (decibéis em relação a um micropascal ao quadrado por hertz).
5. **Seleção de intervalo:**
   - por arraste sobre o gráfico;
   - por campos numéricos de início e fim, para uso com teclado.
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

A fase também não toca nenhum arquivo protegido por `FREEZE_v0.4.json` nem altera a bancada digital.

### 2.3 Relação com o pré-registro

A Seção 2.1 do pré-registro determina que a elegibilidade dos pares candidatos de H1 seja decidida sem consultar o erro de projeção em H_N. Como a Fase 1 não calcula projeções, ela não interfere nessa regra.

Ainda assim, a ficha de caracterização não será utilizada como evidência para nenhuma decisão GO/NO-GO de H1. Essas decisões continuam regidas exclusivamente pelos critérios e prazos do pré-registro.

Para não abrir dados novos antes da separação exigida pela Seção 9.1 do pré-registro, a Fase 1 utiliza apenas os três dias já observados no ensaio E1: 01, 11 e 22 de novembro de 2016. Esses dias ficam registrados como exploratórios e, conforme a mesma seção, não poderão integrar um conjunto confirmatório futuro.

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
  - O rótulo na página será "trecho de maior índice do canto B no dia", nunca "canto de baleia identificado".
- **Trecho B, nível de referência mais baixo:**
  - Usa o minuto válido de menor índice B no mesmo dia, com o mesmo recorte.
  - Serve como contraste descritivo, e não como "ruído de fundo" no sentido estatístico.

São válidos os minutos com menos de 1% de amostras ausentes, a mesma regra do E1.

Se um trecho ultrapassar o início ou o fim do arquivo, desloca-se o recorte para dentro do dia, e o deslocamento é registrado. Empates são resolvidos pelo minuto mais antigo.

O total é de seis trechos e 12 minutos de áudio, uma quantidade pequena o bastante para ser verificada integralmente.

## 4. Parâmetros da ficha de caracterização

Todos os níveis usam a sensibilidade nominal do hidrofone declarada pelo MBARI, que é a mesma do E1: −168,8 dB re 1 V/µPa antes de 14/06/2017. O fator de tensão 3 também segue o E1.

A pressão em micropascal é obtida por `p = 3·x / 10^(S/20)`, em que `x` é a amostra normalizada e `S` a sensibilidade.

Essa conversão não é uma calibração independente. A página deverá dizer isso no acordeão de método, em atendimento à decisão 3 da proposta da Luna: não apresentar uma estimativa como medição física calibrada.

| Parâmetro | Definição operacional | Unidade |
|---|---|---|
| Origem | Bucket, chave do arquivo, SHA-256, sensor (MARS), data e hora UTC (Tempo Universal Coordenado) de início e fim, deslocamento em amostras, sensibilidade usada, licença | — |
| Duração | Número de amostras dividido pela taxa de amostragem | s |
| Nível de pressão sonora eficaz de banda larga | Valor RMS (raiz do valor quadrático médio) da pressão após remoção da média do intervalo; `20·log10(p_rms / 1 µPa)` | dB re 1 µPa, 0–1.000 Hz |
| Nível na banda de 10 a 990 Hz | Integral do espectro médio entre 10 e 990 Hz, sem filtragem no tempo, para não introduzir a atenuação parcial de um filtro perto do corte | dB re 1 µPa |
| Nível de pico | Maior valor absoluto da pressão após remoção da média; `20·log10(p_pico / 1 µPa)` | dB re 1 µPa |
| Espectro médio | Método de Welch, janela Hann de 2.000 amostras, nfft 2.000 (resolução de 1 Hz), sobreposição de 50%, média no domínio linear | dB re 1 µPa²/Hz |
| Percentis espectrais | Percentis 5, 50 e 95 da densidade espectral de cada frequência ao longo dos quadros do intervalo | dB re 1 µPa²/Hz |
| Frequência dominante | Frequência de maior densidade no espectro médio entre 10 e 990 Hz, informada só quando a proeminência (diferença em relação à mediana da banda) for de pelo menos 6 dB; abaixo disso, a ficha diz "sem componente dominante" | Hz, resolução de 1 Hz |
| Amostras ausentes | Fração de amostras exatamente iguais a zero (regra do E1) | % |
| Saturação | Fração de amostras com valor absoluto igual ou superior a 0,999 da escala máxima | % |

Algumas definições exigem cuidado na apresentação:
- A frequência dominante é a região de maior energia no intervalo, e não a frequência fundamental. A página repetirá essa distinção, lembrando que a fundamental nem sempre é a componente de maior energia.
- O limiar de 6 dB de proeminência é instrumental. Ele evita apontar uma flutuação estatística do ruído como componente e é verificado por simulação (Seção 6, critério S2). Não é um critério biológico.
- O intervalo mínimo selecionável é de 10 s, que corresponde a 19 quadros de Welch. Com essa duração, a flutuação da média espectral em ruído branco fica muito abaixo do limiar de proeminência.

## 5. Arquitetura e entregáveis

1. **Módulo `lab/char/characterize.py`:**
   - lê o WAV, confere o SHA-256 e aplica a regra da Seção 3.2;
   - grava em `lab/char/results/c1/`:
     - `C1.json`: ficha completa, origem, ambiente e parâmetros;
     - `<trecho>.env.json`: envoltória de mínimos e máximos em blocos de 50 ms e valor quadrático médio por bloco, que permitem calcular o nível eficaz de banda larga e o nível de pico de qualquer intervalo com granularidade de 50 ms;
     - `<trecho>.psd.bin`: matriz de densidade espectral por quadro, de 0 a 1.000 Hz, em inteiros de 16 bits com passo de 0,01 dB e deslocamento declarado no cabeçalho do `C1.json`. São 239 quadros por 1.001 frequências, em torno de 480 kB por trecho, carregados só quando o trecho é aberto.
2. **Workflow `.github/workflows/characterize.yml`:**
   - acionamento manual;
   - ações fixadas por SHA;
   - ambiente fixado por arquivo de restrições;
   - baixa os três WAV por HTTPS anônimo, executa o módulo duas vezes e compara as saídas byte a byte;
   - publica os resultados como artefato.

   A execução no GitHub Actions substitui a execução manual em máquina virtual usada no E1. Com isso, a proveniência passa a ter tipo `github_actions` e identificador de execução.
3. **Manifesto:** novo conjunto `c1` em `lab/bench/results/MANIFEST.json`, com SHA-256 de todos os arquivos, conferido pelo `site/build_data.py` como já ocorre com os demais conjuntos.
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

### 6.1 Verificação com sinais sintéticos (pytest, semente fixa)

| Código | Teste | Critério |
|---|---|---|
| S1 | Tom de 50,0 Hz com amplitude conhecida, 120 s | Nível eficaz de banda larga, nível na banda de 10 a 990 Hz e nível de pico a até ±0,1 dB do valor teórico; frequência dominante = 50 Hz |
| S2 | Ruído branco gaussiano de variância conhecida, 100 sementes, intervalos de 10 s e de 120 s | Mediana da densidade espectral a até ±0,5 dB do valor teórico; nenhuma frequência dominante falsa nas 100 sementes |
| S3 | Tom de 80 Hz somado ao ruído do S2 com proeminência teórica de 10 dB | Frequência dominante = 80 Hz em todas as sementes |
| S4 | Sequência de zeros e amostras saturadas inseridas em posições conhecidas | Frações de amostras ausentes e saturadas exatas |
| S5 | Pulso tonal iniciado em 30,00 s | Início detectado na envoltória com erro de no máximo 50 ms e no espectrograma com erro de no máximo 0,5 s |
| S6 | Conversão de unidades | Para uma tensão conhecida e a sensibilidade de −168,8 dB re 1 V/µPa, a pressão calculada coincide com o valor analítico com erro relativo inferior a 10⁻⁹ |

### 6.2 Verificação com os dados reais

| Código | Teste | Critério |
|---|---|---|
| R1 | Integridade de origem | Os SHA-256 dos três WAV coincidem com os registrados no E1; qualquer divergência interrompe a execução |
| R2 | Coerência entre domínios (teorema de Parseval) | Para cada trecho, o nível eficaz de banda larga calculado no tempo e a integral do espectro médio entre 0 e 1.000 Hz diferem em no máximo 0,5 dB |
| R3 | Reprodutibilidade | Duas execuções no mesmo workflow produzem arquivos byte a byte idênticos |
| R4 | Regra de seleção | Os inícios dos seis trechos coincidem com os calculados independentemente a partir das séries `series_<dia>.json` publicadas |

### 6.3 Verificação da página

| Código | Teste | Critério |
|---|---|---|
| P1 | Concordância entre Python e página | Para 20 intervalos determinísticos por trecho, os valores da ficha calculados no navegador coincidem com os do Python a até 0,05 dB, com a mesma frequência dominante ou a mesma ausência dela |
| P2 | Manifesto | O build falha se qualquer arquivo do conjunto `c1` divergir do SHA-256 registrado |
| P3 | Privacidade e robustez | Nenhuma requisição externa, nenhum erro de console e nenhuma rolagem horizontal em 390 px de largura |
| P4 | Acessibilidade | A seleção de intervalo funciona só com teclado; o espectrograma tem descrição textual equivalente; os estados não dependem só de cor |
| P5 | Escopo | Nenhuma tela exibe frequência fundamental, harmônicos, espécie ou canal H₁₆; um teste confere que o módulo da Fase 1 não importa o protocolo harmônico |

### 6.4 Verificação editorial e de governança

| Código | Critério |
|---|---|
| E1 | Cada novo painel tem tese visível e os dois acordeões, com texto aprovado pela Luna na versão 1.3 do editorial |
| E2 | A página informa que os níveis usam a sensibilidade nominal do MBARI e que não constituem calibração independente |
| E3 | Nenhum arquivo protegido por `FREEZE_v0.4.json` foi alterado, conforme verificação do `freeze.py` no build |

## 7. Limitações declaradas

1. A sensibilidade nominal é tratada como plana em toda a banda. A resposta em frequência real do sistema de gravação não é corrigida, porque não está documentada no conjunto de dados consultado.
2. Os arquivos de 2 kHz são versões decimadas do registro original. Conteúdo acima de 1.000 Hz não existe nesses arquivos, e a página dirá isso.
3. O trecho de maior índice B indica maior energia relativa na banda do terceiro harmônico do canto B. Isso não equivale a detecção confirmada de um chamado nem a identificação de indivíduo ou população.
4. Seis trechos de três dias não descrevem a paisagem sonora do local nem sua variação sazonal. Servem para demonstrar o método, e não para tirar conclusões ambientais.
5. A ficha descreve o intervalo como um todo. Fontes simultâneas, como uma embarcação e um animal, aparecem somadas no espectro, sem separação.

## 8. Cronograma proposto

| Data | Etapa |
|---|---|
| 01/11 | Revisão deste plano pela Luna e aprovação do Guilherme |
| 01–02/11 | Módulo, testes sintéticos (S1–S6) e workflow; PR em rascunho |
| 02/11 | Execução do workflow; conferência de R1–R4; o artefato é baixado pelo Guilherme |
| 02–03/11 | Editorial v1.3, seção 5.2, para revisão da Luna; implementação na página e P1–P5 |
| 03–04/11 | Revisão final da Luna e merge pelo Guilherme |

Se o cronograma não se cumprir até 04/11, a seção não será publicada antes da entrevista de 06/11. A página atual permanece como está, e a Fase 1 é apresentada como trabalho em andamento, com este plano como evidência.

A declaração de TRL 4 do subsistema computacional não depende desta fase.

## 9. Decisões solicitadas

1. Aprovar o escopo das Seções 2 e 3, em especial o uso exclusivo dos três dias do E1 e a regra fixa de seleção dos trechos.
2. Aprovar os parâmetros da ficha (Seção 4), incluindo o limiar instrumental de 6 dB de proeminência e o intervalo mínimo de 10 s.
3. Aprovar os critérios de aceite da Seção 6 como condição de conclusão da fase.
4. Autorizar a execução no GitHub Actions como forma de proveniência desta fase.

Generated by Claude
