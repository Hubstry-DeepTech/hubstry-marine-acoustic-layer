# HMAL Lab — Rascunho editorial v1

**Versão:** 1.0-rascunho · **Data:** 01/11/2026 · **Estado:** para revisão de Luna e aprovação de Guilherme Machado; nenhum texto foi aplicado à página

## Como ler este rascunho

Cada seção da página recebe três camadas de texto:

- **Tese:** visível logo abaixo do título; expressa a ideia central da seção.
- **Como interpretar esta informação?:** acordeão com o contexto conceitual e a orientação de leitura.
- **Método e limitações:** acordeão com critérios, condições de medição e ressalvas, quando a seção exigir.

As siglas aparecem por extenso na primeira ocorrência de cada seção, porque o visitante pode chegar diretamente a qualquer uma delas pelo menu. Os números citados abaixo são os registrados nos arquivos versionados; na página, eles continuarão sendo lidos dos dados, e não digitados no texto, salvo os parâmetros fixos dos critérios.

---

## 1. Abertura

**Tese.** O HMAL (Hubstry Marine Acoustic Layer, camada acústica marinha da Hubstry) constitui um ambiente digital de pesquisa dedicado ao estudo de sinais acústicos marinhos e de estruturas harmônicas racionais, no qual dados públicos, métodos computacionais reproduzíveis e procedimentos formais de validação são articulados de modo que cada resultado apresentado possa ser rastreado até o arquivo, o código e o critério que o sustentam.

**Como interpretar esta informação?** A página não apresenta um produto acabado, mas o estado verificável de uma pesquisa em andamento. Os resultados aqui reunidos foram produzidos por execuções automatizadas e registrados com identificadores que permitem a qualquer leitor conferir sua origem, de modo que a confiança depositada em cada número decorre da possibilidade de verificá-lo, e não da autoridade de quem o apresenta.

### 1.1. O que é, o que já demonstrou e o que ainda não demonstrou

**Tese.** A apresentação distingue explicitamente as evidências obtidas em condições controladas das hipóteses e das aplicações que ainda dependem de validação com dados ou equipamentos em ambiente real, porque a confusão entre essas categorias comprometeria a credibilidade científica de todo o conjunto.

**Como interpretar esta informação?** O que o HMAL já demonstrou refere-se a dois tipos de evidência: a reprodução numérica de um índice acústico publicado por uma instituição de pesquisa oceanográfica, a partir das mesmas gravações históricas, e o desempenho de um subsistema computacional em uma bancada digital com sinais sintéticos. O que ainda não foi demonstrado inclui a comunicação acústica submarina em operação, a validação biológica da hipótese de pesquisa sobre vocalizações de cetáceos e qualquer aplicação comercial validada; essas lacunas são apresentadas como parte do estado da pesquisa, e não omitidas.

---

## 2. Régua dos 159 canais do dicionário H₁₆

**Tese.** A régua representa o conjunto de razões racionais que o HMAL utiliza como espaço de canais, tornando visível a estrutura matemática da proposta, sem que essa representação deva ser confundida com a comprovação de 159 canais físicos independentes de transmissão no oceano.

**Como interpretar esta informação?** O dicionário H₁₆ reúne todas as frações irredutíveis a/b em que a e b variam de 1 a 16, o que resulta em 159 razões distintas; cada razão, multiplicada por uma frequência de base, define a frequência de um canal. Na régua, as razões estão dispostas em escala logarítmica, e a altura de cada traço diminui à medida que a razão se torna mais complexa, de modo que razões simples, como 1/1, 3/2 e 2/1, aparecem mais destacadas. A concentração de traços em torno de 1/1 indica a região em que os canais ficam mais próximos entre si e, portanto, mais difíceis de distinguir na presença de ruído.

**Método e limitações.** A menor distância entre duas razões vizinhas do dicionário é 1/240, valor que condiciona a resolução necessária para separar canais adjacentes e que orienta os ensaios de pior caso da bancada digital. A régua descreve a organização conceitual do espaço de canais; a viabilidade desses canais em um meio acústico real, sujeito a reflexões, atenuação e variações de propagação, permanece objeto de investigação.

---

## 3. Maturidade por componente

**Tese.** A maturidade tecnológica deve ser atribuída separadamente a cada componente do HMAL, de acordo com as evidências efetivamente disponíveis, porque apresentar o projeto inteiro em um único estágio sugeriria um grau de desenvolvimento que as partes ainda não demonstraram em conjunto.

**Como interpretar esta informação?** O TRL (Technology Readiness Level, nível de maturidade tecnológica) é uma escala de nove níveis que descreve o avanço de uma tecnologia desde a formulação de princípios até a operação comprovada. No HMAL, o núcleo computacional de processamento racional possui avaliação própria, obtida em bancada digital e vinculada a uma versão específica de critérios; a comunicação acústica submarina ainda não teve sua cadeia física validada; e a hipótese sobre vocalizações de cetáceos, por se tratar de uma pergunta científica, não comporta classificação em TRL.

**Método e limitações.** A avaliação do núcleo computacional é uma autoavaliação baseada em critérios congelados antes da execução e verificados por código, e não uma certificação emitida por terceiros; ela vale para o subsistema e para as condições sintéticas da bancada, e não para o desempenho do HMAL em ambiente marinho.

---

## 4. Bancada digital

**Tese.** A bancada digital permite avaliar o comportamento do núcleo computacional em experimentos controlados, nos quais as condições de execução são definidas previamente, de modo a verificar a recuperação dos sinais, a ocorrência de erros e a consistência dos resultados sob critérios estabelecidos antes de cada rodada.

**Como interpretar esta informação?** Em cada ensaio, o sistema gera um sinal sintético composto por um ou mais canais do dicionário, acrescenta ruído em níveis controlados e verifica se o receptor identifica corretamente os canais transmitidos. Os ensaios são executados em dois modos: um de alta frequência (hf), com frequência de base de 1.732 Hz, e outro de baixa frequência (lf), com frequência de base de 25 Hz, faixa próxima à de vocalizações de grandes baleias. O nível de maturidade só é declarado por um programa agregador, e apenas quando todos os ensaios obrigatórios são aprovados nos dois modos.

**Método e limitações.** Os critérios de cada versão são registrados e congelados antes da execução definitiva, e a matriz de ensaios utiliza sementes aleatórias sorteadas após esse congelamento, o que impede que os parâmetros sejam ajustados aos resultados. O ruído empregado é branco e gaussiano, e os sinais têm amplitudes iguais entre canais; efeitos de propagação real, como multipercurso e efeito Doppler, não são simulados.

### 4.1. Execuções definitivas

**Tese.** Cada execução definitiva corresponde a uma versão do receptor avaliada sob uma versão específica de critérios, e seu status é aquele declarado pelo agregador, inclusive quando a conclusão é desfavorável ou quando a execução não permite conclusão.

**Como interpretar esta informação?** O selo de cada linha reproduz exatamente a conclusão do agregador. Uma execução classificada como inconsistente não foi reprovada nem aprovada: o agregador apenas se recusou a emitir conclusão porque os metadados registrados não permitiam verificar a coerência entre os dois modos. Nesses casos, a página informa separadamente a avaliação obtida a partir dos vereditos de cada modo, sem atribuí-la ao agregador.

### 4.2. Veredito por ensaio e modo

**Tese.** O conjunto de ensaios verifica propriedades distintas do sistema, e a aprovação depende de todas elas simultaneamente, porque um receptor que acerta canais com ruído, mas aceita tons inexistentes ou se perde diante de pequenas variações de escala, não seria confiável.

**Como interpretar esta informação?** Os seis ensaios obrigatórios avaliam, respectivamente: a correção matemática do dicionário (B1); a precisão de frequência sem ruído (B2); a recuperação dos canais com ruído (B3); a tolerância a desvios na frequência de base, com auxílio de um canal piloto (B4); a periodicidade dos sinais gerados (B5); e a capacidade de evitar falsos alarmes e de rejeitar tons que não pertencem ao dicionário (B7). A comparação entre versões mostra como alterações no receptor afetaram cada propriedade, inclusive quando a correção de uma falha introduziu outra.

### 4.3. Recuperação dos canais com ruído (B3)

**Tese.** A capacidade de recuperar os canais transmitidos deve ser interpretada em relação à quantidade de ruído presente, porque é essa relação que indica as condições nas quais o método mantém seu desempenho e aquelas nas quais ele deixa de ser confiável.

**Como interpretar esta informação?** A relação sinal-ruído (SNR, do inglês Signal-to-Noise Ratio) expressa, em decibéis, quanto a energia do sinal supera a do ruído ao longo da janela analisada; valores mais altos indicam condições mais favoráveis. O gráfico mostra a fração de ensaios em que o receptor identificou exatamente os canais transmitidos, para cada nível de SNR e para cada condição, desde um único canal até os pares de canais mais próximos do dicionário. A transição observada entre aproximadamente 10 e 18 dB corresponde à faixa em que o ruído deixa de mascarar o sinal; a partir de 20 dB, o critério exige recuperação de pelo menos 99% em todas as condições.

**Método e limitações.** Cada ponto resulta de mil ensaios independentes. Abaixo do limiar, as falhas podem ser de dois tipos — a identificação de um canal errado ou a rejeição de um canal verdadeiro —, e essa distinção está registrada nos arquivos de resultado e na errata da versão 0.4 dos critérios.

### 4.4. Erro de frequência com um canal

**Tese.** A diferença entre a frequência transmitida e a frequência estimada pelo receptor permite avaliar a precisão com que o sistema caracteriza o sinal, desde que se distingam os erros locais de estimação dos erros causados pela escolha de um canal incorreto.

**Como interpretar esta informação?** O gráfico compara o erro quadrático médio (RMS, do inglês root mean square) das estimativas de frequência com o limite de Cramér–Rao assintótico (ACRB, do inglês asymptotic Cramér–Rao bound), que expressa a menor imprecisão teoricamente alcançável por um estimador nas mesmas condições. Uma razão próxima de 1 indica que o receptor opera perto do limite teórico. Os saltos para valores da ordem de milhares não refletem imprecisão gradual: decorrem de poucos ensaios em que o receptor escolheu um canal errado, o que desloca a estimativa por uma distância muito maior do que a imprecisão local.

**Método e limitações.** O critério exige razão de até 1,5 a partir de 16 dB na versão 0.3.1 dos critérios e a partir de 20 dB na versão 0.4. A mudança foi motivada pela constatação, registrada antes da nova rodada, de que o critério anterior misturava precisão de estimação e acerto de classificação; por esse motivo, a versão 0.4 foi avaliada em uma matriz nova, com sementes sorteadas após o congelamento.

### 4.5. Perto do limiar: comparação entre receptores

**Tese.** A comparação entre versões do receptor na faixa próxima ao limiar evidencia se as alterações introduzidas produziram melhorias mensuráveis na situação em que o sistema é mais exigido.

**Como interpretar esta informação?** As curvas mostram a fração de ensaios com recuperação exata de um único canal entre 8 e 22 dB. Diferenças de algumas unidades por mil, nessa faixa, correspondem a diferenças relevantes de robustez, porque cada troca de canal compromete integralmente a informação transmitida naquele ensaio.

### 4.6. Desvio de escala (B4) e falsos alarmes (B7)

**Tese.** Os ensaios B4 e B7 verificam se o receptor mantém a identificação correta quando a frequência de base sofre pequenos desvios e se ele evita declarar a presença de canais que não foram transmitidos.

**Como interpretar esta informação?** No B4, a frequência de base é deslocada em até 0,1%, e o receptor deve corrigir esse desvio com auxílio de um canal piloto, mantendo recuperação de pelo menos 99%. No B7, o receptor analisa ruído puro e deve declarar falsamente a presença de sinal em no máximo 1% dos casos, com nível de confiança de 95%; além disso, deve rejeitar 158 tons posicionados exatamente entre canais vizinhos, que não pertencem ao dicionário.

### 4.7. Proveniência

**Tese.** Cada resultado está associado à versão do código que o produziu, ao identificador da execução, aos arquivos de entrada e de saída e ao commit que o publicou, o que permite sua verificação independente por qualquer leitor.

**Como interpretar esta informação?** O código de verificação SHA-256 (Secure Hash Algorithm de 256 bits, algoritmo de resumo criptográfico) funciona como uma impressão digital do arquivo: qualquer alteração, ainda que mínima, produz um código diferente. A página confere esses códigos durante sua construção e recusa a publicação quando algum deles diverge do manifesto registrado. A distinção entre o commit do experimento e o commit de publicação separa o código que efetivamente executou o ensaio da versão do repositório na qual o resultado passou a ser exibido.

---

## 5. Baleia-azul: reprodução de um índice do MBARI (E1)

**Tese.** O experimento E1 demonstra que o pipeline do HMAL reproduz, a partir das mesmas gravações históricas, um índice acústico publicado pelo MBARI (Monterey Bay Aquarium Research Institute, instituto de pesquisa oceanográfica da Califórnia), com diferença relativa inferior a uma parte em cem milhões nos três dias avaliados, o que estabelece a correção do processamento de dados reais antes de qualquer análise original.

**Como interpretar esta informação?** As gravações foram obtidas pelo hidrofone do observatório submarino MARS (Monterey Accelerated Research System), na baía de Monterey, em novembro de 2016; não se trata, portanto, de dados recebidos em tempo real. O Blue B Call Index compara a intensidade espectral na faixa de 43 a 44 Hz, associada ao canto B da baleia-azul, com a intensidade em faixas vizinhas de referência; valores mais elevados indicam maior presença de canto no período analisado. Reproduzir esse índice com precisão significa que a leitura dos arquivos, a calibração e o cálculo espectral do HMAL coincidem com os do instituto que o publicou.

**Método e limitações.** O índice indica a presença de canto em uma faixa de frequência, mas não conta vocalizações individuais nem identifica animais. A reprodução cobre três dias de critério, definidos antes da execução, e a tolerância aceita era de 2%. Os dados pertencem ao MBARI, sob licença CC BY 4.0 (Creative Commons Atribuição 4.0), e foram processados e visualizados pela Hubstry.

### 5.1. Espectrograma e índice minuto a minuto

**Tese.** O espectrograma permite observar como a energia sonora se distribui entre as frequências e como essa distribuição se modifica ao longo do dia, enquanto a série minuto a minuto mostra a variação do índice ao longo das mesmas 24 horas.

**Como interpretar esta informação?** No espectrograma, o eixo horizontal representa o tempo, o eixo vertical representa a frequência, e as cores indicam o nível espectral calibrado, em decibéis relativos a 1 micropascal ao quadrado por hertz; tons mais claros correspondem a maior energia. As linhas horizontais destacam a faixa do canto B e as faixas de referência utilizadas pelo índice. Períodos em que a faixa do canto se destaca em relação às vizinhas coincidem com elevações do índice na série temporal abaixo do espectrograma.

---

## 6. Método e documentos

**Tese.** A pesquisa explicita seus critérios, protocolos e registros antes de apresentar resultados, de modo que a avaliação de cada conclusão possa considerar não apenas o que foi obtido, mas também as regras que foram fixadas previamente para obtê-lo.

**Como interpretar esta informação?** Os critérios da bancada definem os ensaios, os limiares de aprovação e a regra de maturidade; o pré-registro descreve a hipótese científica e o protocolo exploratório antes da coleta de evidências; o relatório comparativo e o relatório da rodada confirmatória apresentam os resultados e suas limitações; o registro de congelamento guarda a impressão digital de cada arquivo que define o experimento; e a errata documenta as correções feitas após a publicação. O estado de cada documento é exibido conforme declarado no próprio documento.

---

## 7. Execução e integridade (nova seção de observabilidade)

**Tese.** A seção apresenta a infraestrutura que executa e registra os experimentos, permitindo verificar se as execuções foram concluídas, se os arquivos publicados correspondem aos registrados e se cada resultado pode ser associado ao contexto que o produziu.

**Como interpretar esta informação?** A observabilidade disponível no HMAL refere-se ao processo de produção das evidências, e não ao funcionamento contínuo de um serviço. Para cada conjunto de resultados, a seção indica o tipo de execução, o identificador da execução automatizada quando existente, a conclusão do agregador, o número de arquivos conferidos e a verificação do congelamento dos critérios. Uma verificação bem-sucedida significa que nenhum arquivo protegido foi alterado depois de congelado e que o ambiente de execução corresponde ao registrado.

**Método e limitações.** A página é estática e não possui monitoramento de disponibilidade, registros de eventos em tempo real, indicadores de consumo de recursos ou alertas próprios; essas dimensões não são apresentadas porque não há dados que as sustentem. Os registros detalhados de cada execução permanecem no GitHub Actions, com prazo de retenção definido pela plataforma.

---

## 8. Ética e licenças

**Tese.** A pesquisa explicita a origem dos dados, as condições de uso do software e dos registros acústicos e os cuidados necessários para evitar aplicações que possam prejudicar os animais estudados.

**Como interpretar esta informação?** A licença do software proíbe utilizá-lo para localizar, rastrear ou seguir cetáceos e outros mamíferos marinhos com fins de caça, captura, perseguição ou molestamento, bem como para monitorá-los sem as autorizações ambientais exigidas por lei. O software e os dados obedecem a licenças distintas: o HMAL está sob a Business Source License 1.1, com concessão adicional para uso acadêmico e de conservação, e os registros do MBARI estão sob a licença CC BY 4.0, que exige atribuição da fonte.

### 8.1. Privacidade

**Tese.** A página não utiliza formulários, cookies de rastreamento ou mecanismos de perfilamento, embora a hospedagem e os serviços de infraestrutura possam manter registros técnicos de segurança segundo suas próprias políticas de privacidade.

---

## Decisões pedidas

1. Aprovação do padrão de três camadas (tese visível, "Como interpretar esta informação?" e "Método e limitações").
2. Aprovação ou correção de cada tese e de cada texto acima.
3. Inclusão da seção 7, restrita às informações de execução e integridade que já existem.
4. Pontos a conferir na revisão: a menção à proximidade entre a faixa lf e as vocalizações de grandes baleias (seção 4) e a associação da faixa de 43 a 44 Hz ao canto B (seção 5), tal como descrita pelo MBARI.
