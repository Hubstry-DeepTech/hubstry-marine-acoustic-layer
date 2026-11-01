# MCA-001 — Série harmônica musical e canto B da baleia-azul

**Matriz de Correspondências Analógicas do HMAL (MCA), ficha 001** · **Versão:** 0.5 (aplica o perfil operacional HMAL das seis relações e incorpora a revisão adversarial da v0.4 e os pareceres da Luna de 01/11/2026) · **Data:** 01/11/2026 · **Estado:** protocolo de verificação em especificação; nenhuma medição foi feita e nenhum dado foi aberto para elaborá-lo. **Rótulo:** `EXPLORATORY/FEASIBILITY`.

**Documentos relacionados:**
- `lab/analogias/PERFIL_OPERACIONAL_HMAL_seis_relacoes.md`: as definições operacionais das seis relações usadas aqui. Esta ficha não as repete; aplica-as;
- `lab/sources/fontes.csv` (PR #14): fontes externas citadas pelo código Sxx;
- textos do autor: "π√f(A): Uma Álgebra Hexarrelacional de Significância para Algoritmos" (fevereiro de 2026), TICA v0.1, Morfologia Harmônica v1.0, HALE v3.0 e whitepaper GuruDev.

## 1. Finalidade

Esta ficha é o protocolo de verificação da correspondência entre a série harmônica, tal como a acústica musical a descreve, e o canto B da baleia-azul. Ela fixa os objetos, as estruturas, os parâmetros e os controles com que cada relação do perfil operacional será investigada nesse caso.

O objetivo não é mostrar que as seis relações se aplicam ao canto B. É investigar quais delas encontram instâncias mensuráveis nele, quais não encontram e sob quais condições. Das seis, quatro estão especificadas para teste (ρ₁, ρ₂, ρ₃ e ρ₄) e duas permanecem abertas (ρ₅ e ρ₆).

## 2. Relação com o pré-registro e com a Fase 1

Esta ficha não integra a hipótese H1 do pré-registro v1.3.1-draft. A Seção 3.2 desse documento exclui os harmônicos de uma mesma vocalização como evidência de relações entre unidades vocais distintas, e essa exclusão permanece. A harmonicidade do canto B é uma pergunta diferente, que só poderá ser investigada depois de registrada em emenda versionada, com motivação, data e indicação dos dados já observados, antes de qualquer medição.

A ficha também não altera a Fase 1, cujo escopo exclui frequência fundamental e harmônicos. As medições aqui especificadas pertencem à Fase 2.

## 3. Quadro teórico

### 3.1 Modalidades de analogia

A taxonomia de três modalidades vem da TICA (Seções 7.1 a 7.4), que também ancora em Gentner a distinção entre analogia heurística e funcional.

- **Analogia heurística:** um sistema conhecido orienta a exploração de outro, por semelhança de superfície, com o menor compromisso ontológico.
- **Analogia funcional:** elementos de dois sistemas desempenham papéis equivalentes em seus respectivos contextos.
- **Analogia homológica:** correspondência de estrutura entre sistemas distintos, independentemente de ancestralidade ou origem evolutiva comum. O termo não é usado no sentido da biologia evolutiva, em que homologia designa semelhança por descendência comum.

Dois conceitos do autor são distinguidos. A relação ρ₂ da Álgebra exige homomorfismo entre estruturas, com simetria apenas no isomorfismo (Definição 3.2). A analogia homológica da TICA exige isomorfismo completo, com mapeamento biunívoco (Seção 7.4). Nesta ficha, a homologia é medida pela relação ρ₂, em níveis. O nível mais alto alcançável com dados é o isomorfismo parcial (Seção 3.3), que não equivale ao isomorfismo completo da TICA, e este não é pressuposto.

Dois referenciais externos complementam a taxonomia. Mary Hesse (S23) distingue analogias positivas, negativas e neutras. Dedre Gentner (S24) sustenta que analogias consistentes preservam relações, e não apenas atributos.

### 3.2 Os dois sistemas

**Sistema de origem: a série harmônica da acústica musical.** Um som periódico de frequência fundamental `f₀` contém componentes em `fₙ = n·f₀`. As razões entre componentes são razões de inteiros: a oitava é 2:1, a quinta justa entre o segundo e o terceiro harmônicos é 3:2, e a décima segunda entre a fundamental e o terceiro harmônico é 3:1. Essas relações decorrem da periodicidade do sinal. A organização delas em escalas, consonâncias e afinações pertence à percepção e à cultura humanas.

**Sistema de destino: o canto B da baleia-azul do Pacífico Nordeste.** Trata-se de vocalização tonal, com duração de vários segundos e modulação de frequência. Na literatura, o componente mais energético é identificado como o terceiro harmônico, e sua frequência de pico a 10 s do início ficou entre 46,1 Hz (2006) e 42,6 Hz (2019) (S01). Essa identificação já pressupõe a estrutura harmônica e a atribuição de ordem que esta ficha pretende testar. Por isso, a fundamental perto de 14 a 15 Hz que dela resulta é tratada aqui como hipótese, e não como dado. Segundo o resumo de um artigo publicado, fundamental e sobretons podem ser modelados por uma série de ondículas curtas atribuídas a pulsos pneumáticos (S02, conferido apenas pelo resumo). Esse modelo é uma hipótese de produção.

### 3.3 Estruturas e parâmetros desta ficha

As definições gerais (componente, evento, estrutura ideal `𝓘_N`, atribuição `h`, escala `g`, desvio `εₖ`) estão na Seção 4 do perfil operacional. Esta ficha fixa o seguinte.

**Ordem máxima efetiva `N(t)`.** A ordem máxima depende do instante, porque a fundamental varia durante o chamado. Ela é o menor de dois limites:
- o limite de banda, `⌊f_max / g(t)⌋`, em que `f_max` é a frequência acima da qual a resposta do filtro de decimação dos arquivos de 2 kHz deixa de ser plana. O valor de `f_max` será fixado a partir da documentação do MBARI e verificado com ruído branco sintético processado pela mesma cadeia;
- o limite de identificabilidade: a maior ordem `n` para a qual a separação relativa entre ordens adjacentes, cerca de `1/n`, ainda é maior que duas vezes a incerteza relativa típica dos componentes. Acima dessa ordem, não é possível distinguir `n` de `n + 1`.

A finitude de `𝓘_N` não é exigida pela existência de `h`, que poderia ser definida em todos os naturais. Ela é necessária para definir o isomorfismo parcial e para limitar a busca de atribuições.

**Conjunto esperado de ordens `E(t)`.** É o conjunto das ordens de `1` a `N(t)` cuja posição ideal fica acima do piso de ruído local, estimado no espectro sem usar a detecção dos componentes. `E(t)` é definido antes e independentemente de `C(t)`. Assim se evita a circularidade de definir o esperado pelo que foi detectado.

**Isomorfismo parcial.** Homomorfismo aproximado (perfil, Seção 5.2) em que `h` é bijetiva entre `C(t)` e `E(t)`. O termo "parcial" registra que `E(t)` não contém todas as ordens de `𝓘_N`.

**Ajuste e incerteza.** Para cada atribuição candidata, um único ajuste ponderado de `ln f_k = ln h_k + ln g` substitui a comparação par a par das razões. Os `K(K − 1)/2` pares de componentes contêm apenas `K − 1` razões independentes, e contar pares inflaria a evidência. A modulação de frequência, comum a todos os componentes, correlaciona os erros; a matriz de covariância entra no ajuste. O teste usa qui-quadrado com `K − 1` graus de liberdade.

**Estimador independente da fundamental `f̂₀`.** Será escolhido na Fase 2, por exemplo entre estimadores baseados em autocorrelação, e calibrado com sinais sintéticos. Ele é usado para validar `g` e para a candidata de ρ₆.

## 4. Aplicação das seis relações

| Relação | Escopo | Instância nesta ficha | Estado | Grau de evidência (HALE) |
|---|---|---|---|---|
| ρ₁ Similitude | Interdomínio; intradomínio | Cada componente ↔ a posição ideal da sua ordem; cada componente ↔ o componente de mesma ordem em outro evento | Especificada | Conjecturado |
| ρ₂ Homologia | Interdomínio | `C(t)` ↔ `𝓘_N(t)`, com atribuição injetiva e mínima, ajuste único e modelo nulo | Especificada, condicionada ao modelo nulo | Conjecturado |
| ρ₃ Equivalência | Global | Eventos inteiros comparados por assinatura em contextos fixados na Seção 4.1 | Especificada | Argumentado |
| ρ₄ Simetria | Intradomínio; global | Instantes do mesmo evento e eventos distintos, por fator de escala único; séries de eventos ao longo de anos | Especificada | Conjecturado |
| ρ₅ Equilíbrio | Intradomínio | Aberta; candidatas no perfil, Seção 5.5 | Aberta | Especulado |
| ρ₆ Compensação | Intradomínio | Aberta; candidata no perfil, Seção 5.6, com fundamental fraca e terceiro harmônico forte como ponto de partida | Aberta | Especulado |

### 4.1 Contextos de ρ₃ para o canto B

Os contextos abaixo são propostos para revisão. Depois de aprovados, ficam congelados antes de qualquer medição.

1. **Ordem do componente de maior energia**, na atribuição mínima aceita por ρ₂.
2. **Padrão das ordens dos três componentes mais energéticos**, como conjunto.
3. **Classe do contorno de frequência**: descendente, plano ou ascendente, conforme a inclinação de `ln g(t)` ao longo do evento seja menor que `−s`, entre `−s` e `s`, ou maior que `s`, com `s` fixado antes da medição.
4. **Resultado do teste de homologia** no instante central do evento: aceito ou rejeitado.

Dois eventos são equivalentes quando coincidem nos quatro contextos. A relação é de equivalência por construção (perfil, Seção 5.3).

### 4.2 Observações sobre as instâncias

- **ρ₁ e ρ₂ não são independentes.** Usam a mesma atribuição e a mesma escala. Se `g` é estimado dos mesmos componentes, a aceitação de ρ₁ em todos os componentes e a aceitação de ρ₂ quase coincidem. Elas são reportadas separadamente porque respondem a perguntas diferentes, uma sobre atributos e outra sobre relações, e a dependência fica declarada.
- **ρ₄ e o declínio secular de frequência.** O terceiro harmônico do canto B da população do Pacífico Nordeste baixou de frequência entre 2006 e 2019 (S01). Perguntar se os demais componentes acompanham esse declínio pelo mesmo fator é uma instância global de ρ₄. A pergunta envolve apenas componentes do canto B: não compara chamados A e B e não forma a razão vedada pelo pré-registro.
- **ρ₆ e a fundamental fraca.** Uma série de componentes harmônicos exatos determina a fundamental mesmo quando o componente fundamental está fraco ou ausente. Com tolerância e ordens faltantes, porém, o período pode ficar ambíguo. A candidata de `Ω` no perfil mede justamente essa ambiguidade, e pode resultar subaditiva.
- **Equivalência de oitava.** Na teoria musical, alturas separadas por oitavas pertencem à mesma classe. É uma analogia neutra para o canto da baleia, e esta ficha não a pressupõe.

## 5. Analogias positivas, negativas e neutras

**Positivas (compartilhadas por razões físicas):**
- componentes em múltiplos inteiros da fundamental, enquanto o sinal for periódico;
- as razões 2:1, 3:2 e 3:1 entre os três primeiros componentes.

**Negativas (não transferíveis):**
- a organização em escalas, a consonância e a função estética, que pertencem à percepção e à cultura humanas;
- qualquer intenção musical do animal;
- a percepção do canto como sequência de notas;
- o significado comunicativo dos componentes, que pertence à zoossemiótica e exige dados de comportamento.

**Neutras (a investigar):**
- a homologia do canto B com a série ideal, avaliada contra o modelo nulo (ρ₂);
- a estabilidade da assinatura entre eventos (ρ₃);
- a preservação da estrutura sob a modulação e o declínio de frequência (ρ₄);
- as candidatas de equilíbrio e compensação (ρ₅ e ρ₆);
- a relação entre o desvio da harmonicidade ideal e o modelo de produção por pulsos pneumáticos (S02).

## 6. Decisões sobre os textos do autor

**Decididos pelo autor em 01/11/2026:**

1. **Critérios próprios do HMAL.** Os trabalhos do autor são fundamento conceitual e não precisam ser harmonizados entre si. As seis relações recebem definições operacionais próprias do HMAL, no perfil operacional, com fonte, propriedades e controles declarados.
2. **Homologia como homomorfismo.** Fica adotado o texto da Definição 3.2 da Álgebra. O próprio manuscrito não é uniforme: a fórmula da Definição 3.2 usa uma seta com til, notação usual de isomorfismo, e a demonstração do Teorema 3.1 conclui "existe um isomorfismo". A tabela do README do repositório e a docstring de `calculate_homology` usam `≅`. A função `calculate_homology` mede a cobertura de multiconjuntos de tipos de nós de código e fica registrada como heurística legada, a ser substituída na refatoração do HexaSign.
3. **Hierarquia como ordem conceitual.** O Teorema 3.1 afirma a cadeia de implicações. A Seção 15.2 reconhece que a demonstração é um esboço e pergunta: (a) se a passagem do equilíbrio para a simetria exige `Φ` bijetiva; (b) se a passagem da simetria para a equivalência exige que o grupo preserve todos os contextos; (c) se existem modelos finitos em que alguma implicação falha. Esta ficha trata a ordem como conceitual e, por usar estruturas finitas, é ela mesma um caso para a pergunta (c).

**Ainda abertos:**

4. **Operacionalização acústica de ρ₅ e ρ₆.** As definições abstratas existem (Definições 3.5 e 3.6). As candidatas acústicas estão no perfil e dependem de simulação.
5. **Pesos da norma.** A Seção 5.1 da Álgebra justifica os pesos `φ^(k−1)` por duas razões: dar mais peso às relações mais profundas e fazer a ponte com o design. Nenhuma das duas é medição. Esta ficha não agrega as dimensões.

## 7. Controles e critérios de refutação

Os critérios de cada relação estão no perfil operacional. Nesta ficha, valem ainda:

1. **Modelo nulo de homologia.** Antes de qualquer dado real, a busca de atribuições é aplicada a conjuntos de componentes inarmônicos e a conjuntos aleatórios com o mesmo número de componentes e a mesma banda do canto B. Se a taxa de falsa homologia não ficar abaixo do limite fixado, a tolerância é revista nos dados sintéticos, nunca nos dados reais.
2. **Interpretação de um resultado negativo.** Se ρ₂ for rejeitada na maioria dos instantes de eventos identificados com confiança, a física da série harmônica não fica refutada, porque ela vale para qualquer sinal periódico. O resultado indicaria que, na escala de análise adotada, o canto B não se comporta como sinal periódico estável, ou que interferem fatores ainda não controlados: erro de oitava na estimativa da fundamental, sobreposição de animais, efeitos de propagação ou da cadeia de gravação. Cada um desses fatores será examinado antes de qualquer conclusão sobre o mecanismo de produção.
3. **Identificação independente.** Nenhum critério é aplicado antes de os eventos serem identificados por procedimento independente, conforme a linha de anotação de eventos, e antes de as tolerâncias serem fixadas com sinais sintéticos.

## 8. Papel das tecnologias da Hubstry

- **GuruDev Core:** representação formal das estruturas, das atribuições e das evidências. Segundo o seu README, o validador semântico ainda está em desenvolvimento.
- **HexaSign:** cálculo do perfil das seis dimensões, depois da refatoração para estruturas relacionais com grandezas físicas. As heurísticas lexicais atuais (`src/lib/hexa-engine.ts`) permanecem experimentais e não são usadas aqui.
- **GrammAIr Flow:** revisão da clareza e da consistência terminológica dos textos, sem papel na decisão sobre a validade da correspondência.

## 9. Próximos passos

1. Revisão desta ficha e do perfil operacional pela Luna.
2. Simulação das candidatas de ρ₅ e ρ₆, e do modelo nulo de ρ₂, com sinais sintéticos.
3. Inclusão da linha de harmonicidade do canto B na proposta de emenda v1.4, com esta ficha como fundamento.
4. Conferência das fontes S02, S23 e S24 no texto primário. As referências Sxx estão no registro de fontes do PR #14, que deve ser incorporado antes desta ficha.

Generated by Claude
