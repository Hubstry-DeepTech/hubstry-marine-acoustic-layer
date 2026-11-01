# Perfil operacional HMAL das seis relações de significância

**Versão:** 0.1.3 (incorpora os pareceres da Luna sobre a v0.1, a v0.1.1 e a v0.1.2) · **Data:** 01/11/2026 · **Estado:** especificação; nenhuma medição foi feita. **Rótulo:** `EXPLORATORY/FEASIBILITY`.

## 1. Natureza deste documento

Este documento estabelece critérios operacionais próprios do HMAL (Hubstry Marine Acoustic Layer, camada acústica marinha da Hubstry) para as seis relações de significância: similitude (ρ₁), homologia (ρ₂), equivalência (ρ₃), simetria (ρ₄), equilíbrio (ρ₅) e compensação (ρ₆).

O documento não revisa, não valida e não harmoniza a teoria geral das seis relações. Os trabalhos do autor que a fundamentam têm objetos, propósitos e níveis de formalização próprios, e não precisam coincidir entre si. Aqui, o que se faz é uma adaptação declarada ao domínio acústico, com quatro compromissos:

- cada critério indica de qual texto do autor vem a sua inspiração;
- cada critério declara as propriedades que de fato garante (reflexividade, simetria, transitividade);
- cada critério tem controle e critério de refutação próprios;
- os critérios são fixados antes de qualquer medição.

O objetivo não é demonstrar que as seis relações funcionam porque foram definidas na teoria. É investigar quais delas encontram instâncias mensuráveis em sinais acústicos marinhos, quais não encontram, e sob quais condições.

## 2. Arquitetura em três níveis

1. **Fundamento conceitual:** os trabalhos do autor fornecem conceitos, definições abstratas e hipóteses.
   - "π√f(A): Uma Álgebra Hexarrelacional de Significância para Algoritmos" (fevereiro de 2026): definições abstratas das seis relações (Definições 3.1 a 3.6).
   - Whitepaper GuruDev, Seção 2.8: relações de concordância e a noção de escopo.
   - TICA, Seções 7.1 a 7.4: modalidades de analogia heurística, funcional e homológica.
   - Morfologia Harmônica: critérios de refutação por postulado e Procrustes Harmônico.
   - HALE, Seção 9.4: graus de evidência.
2. **Definições operacionais do HMAL:** este documento.
3. **Protocolo de verificação:** cada ficha da Matriz de Correspondências Analógicas (MCA) aplica estas definições a uma correspondência concreta, com dados, tolerâncias numéricas e controles. A primeira é a MCA-001.

## 3. Dois eixos de classificação

Cada relação é investigada segundo dois eixos independentes. O primeiro eixo vem da Álgebra; o segundo, da Seção 2.8 do whitepaper GuruDev. O segundo eixo complementa o primeiro e não redefine as relações.

**Eixo 1 — natureza da relação:** proximidade (ρ₁), preservação estrutural (ρ₂), substituibilidade contextual (ρ₃), transformação de grupo (ρ₄), anulação de potenciais (ρ₅), complementaridade com emergência (ρ₆).

**Eixo 2 — escopo da concordância:**
- **intradomínio:** elementos de um mesmo domínio, como dois eventos do mesmo tipo de chamado;
- **interdomínio:** elementos de domínios distintos, como componentes observados e ordens de uma estrutura ideal;
- **global:** estruturas ou domínios considerados como um todo.

| Relação | Intradomínio | Interdomínio | Global |
|---|---|---|---|
| ρ₁ Similitude | componente de um evento ↔ componente de mesma ordem em outro evento | componente observado ↔ posição ideal da sua ordem | — |
| ρ₂ Homologia | — | estrutura observada ↔ estrutura ideal | — |
| ρ₃ Equivalência | — | — | evento ↔ evento, como totalidades, em contextos fixados |
| ρ₄ Simetria | evento ↔ evento, ou instante ↔ instante | — | séries de eventos ao longo de anos |
| ρ₅ Equilíbrio | pares de componentes, ou estados ao longo do tempo | — | — |
| ρ₆ Compensação | componentes ↔ conjunto de componentes | — | — |

## 4. Objetos comuns

As definições abaixo valem para todas as fichas acústicas.

- **Componente espectral `c`:** pico do espectro com frequência `f`, incerteza `σ_f` e amplitude `A`, obtido por um procedimento de detecção que não usa nenhuma hipótese sobre a frequência fundamental.
- **Evento `e`:** trecho identificado como uma vocalização por procedimento de anotação independente (linha de anotação de eventos do HMAL). Um evento é representado pelos conjuntos de componentes `C(t)` nos instantes de análise.
- **Estrutura harmônica ideal `𝓘_N`:** estrutura de duas espécies, `⟨{1, …, N}, ℚ⁺, r⟩`, em que `r(m, n) = m/n`. Ela representa apenas o valor das razões entre ordens. O símbolo evita a colisão com o `H_N` do dicionário de comunicação do HMAL e com o `ℋ` do HALE.
- **Atribuição de ordens `h`:** função de `C(t)` em `{1, …, N}`. Por definição, ela é injetiva (componentes distintos recebem ordens distintas) e mínima (o máximo divisor comum das ordens atribuídas é 1). Se `h` preserva as razões, `2·h` também preserva, com escala pela metade. A minimalidade escolhe a atribuição primitiva entre as atribuições proporcionais. Ela não identifica a fundamental física: um sinal com componentes apenas em `2f₀` e `4f₀` recebe a atribuição mínima `(1, 2)`, com escala `2f₀`, embora a fundamental física seja `f₀`. A identificação da fundamental física depende do estimador independente `f̂₀`.
- **Conjunto de atribuições de melhor ajuste `H*`:** o conjunto das atribuições injetivas e mínimas cuja estatística de ajuste fica a uma distância de no máximo `Δ_T` da menor estatística encontrada. São as atribuições admissíveis dentro da margem `Δ_T`, e não atribuições igualmente ótimas. A variabilidade da estatística de ajuste depende do número de componentes `K`, da incerteza e do ruído; por isso, um único `Δ_T` absoluto pode gerar conjuntos `H*` de tamanhos muito diferentes. As simulações sintéticas testam se um valor único basta. Se não bastar, `Δ_T` passa a ser uma tabela por estratos de `K` e de condição de sinal. Em qualquer caso, a regra inteira é fixada antes da medição com dados reais. `H*` é calculado para todo instante em que haja ao menos dois componentes, independentemente do teste de homologia. Quando `H*` tem um único elemento, ele é chamado `h*`. Quando nenhuma atribuição é calculável, o instante recebe o estado "não estimável".
- **Escala `g`:** dado `h`, `ln g` é estimado por mínimos quadrados generalizados no modelo `ln f_k = ln h_k + ln g + e_k`, com a matriz de covariância completa `Σ` dos logaritmos das frequências: `ln ĝ = 1ᵀΣ⁻¹(y − ln h) / 1ᵀΣ⁻¹1`, em que `y` é o vetor dos `ln f_k`. Quando os erros são independentes, `Σ` é diagonal e o estimador se reduz aos mínimos quadrados ponderados com pesos `1/(σ_k/f_k)²`. O mesmo estimador é usado em todas as relações.
- **Estimador independente da fundamental `f̂₀`:** procedimento que estima a fundamental sem usar `h` nem os componentes detectados como tais, por exemplo a partir da autocorrelação do sinal. É usado para definir tudo o que precisa ser independente da busca de atribuições: a ordem máxima efetiva, o conjunto esperado de ordens e a validação da escala `g`. Nos intervalos em que `f̂₀` não for confiável, segundo critério fixado antes da medição, as classificações que dependem dele ficam indisponíveis.
- **Desvio relativo `εₖ`:** `εₖ = f_k / (h_k · g) − 1`. Para desvios pequenos, `|ln(1 + εₖ)| ≈ |εₖ|`, com erro da ordem de `εₖ²/2`.

## 5. Fichas operacionais

Cada ficha tem os sete campos propostos pela Luna (definição HMAL, objeto, operador, métrica, tolerância, controle e refutação, estado), mais a fonte conceitual, as propriedades garantidas e o grau de evidência. O grau de evidência segue a tabela do HALE (Seção 9.4): estabelecido, demonstrado em simulação, conjecturado, argumentado ou especulado.

### 5.1 ρ₁ — Similitude

| Campo | Conteúdo |
|---|---|
| Fonte conceitual | Álgebra, Definição 3.1: `d(φ(x), φ(y)) < ε`. Gentner: semelhança de atributos. Whitepaper GuruDev, Seção 2.8, para o escopo intradomínio |
| Definição HMAL | Um componente é similar à posição ideal da sua ordem quando o desvio logarítmico entre os dois está dentro da tolerância do próprio componente |
| Objeto | Componente `c_k` e a posição ideal `h_k · g` (interdomínio); ou dois componentes de mesma ordem em eventos distintos (intradomínio) |
| Operador | `φ = ln f`; `d` = diferença absoluta |
| Métrica | Resíduo `r_k = ln f_k − ln h_k − ln g₍₋ₖ₎`, em que `g₍₋ₖ₎` é a escala estimada sem o componente `k`, e desvio normalizado `u_k = r_k / √Var(r_k)`, com `Var(r_k) = Var(ln f_k) + Var(ln g₍₋ₖ₎) − 2·Cov(ln f_k, ln g₍₋ₖ₎)`. O termo de covariância é obtido de `Σ` e não se anula quando os erros são correlacionados pela modulação comum. Fração de componentes com `|u_k| ≤ z` |
| Tolerância | `|u_k| ≤ z`, com `z` fixado antes da medição por calibração com sinais sintéticos |
| Propriedades | Reflexiva, simétrica, não transitiva, como na Definição 3.1 |
| Controle e refutação | Sinais sintéticos com inarmonicidade conhecida, para verificar que o critério a detecta. Refutação: a fração de componentes similares não difere da obtida em substitutos inarmônicos com o mesmo número de componentes e a mesma banda |
| Dependência declarada | ρ₁ e ρ₂ usam a mesma atribuição, escolhida com todos os componentes, inclusive o que ρ₁ avalia. Deixar o componente fora só da estimação da escala reduz, mas não elimina, a sua influência. ρ₁ é, portanto, um diagnóstico de proximidade condicionado à atribuição, e o procedimento completo é calibrado com sinais sintéticos. Quando `H*` tem mais de um elemento, ρ₁ é calculada para cada atribuição `h ∈ H*`, com a respectiva escala sem o próprio componente, e o resultado é reportado como o intervalo dos valores obtidos. A aprovação é conservadora: o critério precisa ser satisfeito em todas as atribuições admissíveis. Assim, a escolha entre atribuições quase ótimas não decide o resultado. Com um único elemento em `H*`, o cálculo é o mesmo. ρ₁ avalia atributos, componente por componente; ρ₂ avalia relações, no conjunto |
| Estado | Especificada |
| Grau de evidência | A proximidade dos componentes de um sinal periódico às posições ideais é **estabelecida** pela física. Que o canto B se comporte assim é **conjecturado** |

### 5.2 ρ₂ — Homologia

| Campo | Conteúdo |
|---|---|
| Fonte conceitual | Álgebra, Definição 3.2: homomorfismo entre estruturas, com simetria apenas no isomorfismo. TICA, Seção 7.4: a analogia homológica por isomorfismo completo é o caso máximo. Whitepaper GuruDev, Seção 2.8: concordância entre elementos de conjuntos distintos |
| Definição HMAL | A estrutura observada é homóloga à ideal quando existe uma atribuição `h` injetiva e mínima com a qual o modelo `ln f_k = ln h_k + ln g` se ajusta aos componentes dentro da incerteza |
| Objeto | `C(t)` e `𝓘_N` (interdomínio) |
| Operador | Busca exaustiva das atribuições injetivas e mínimas, com ajuste ponderado para cada uma |
| Métrica | Estatística qui-quadrado do melhor ajuste, com `K − 1` graus de liberdade nominais (`K` componentes, um parâmetro livre), reportada como estatística descritiva; cobertura do conjunto esperado de ordens |
| Tolerância e significância | O qui-quadrado do melhor ajuste é reportado como estatística descritiva. Como a atribuição é escolhida entre muitas candidatas, o valor-p nominal com `K − 1` graus de liberdade não vale depois da busca. A significância é calculada pela distribuição empírica do qui-quadrado do melhor ajuste nos sinais nulos, gerados e processados pelo procedimento completo: mesma detecção, mesma busca, mesma minimalidade. Como um qui-quadrado menor indica ajuste melhor, a evidência contra o modelo nulo está na cauda inferior: `p_emp = (1 + Σ_b 𝟙(T_b ≤ T_obs)) / (B + 1)`, em que `T_obs` é a estatística observada e `T_b` a de cada um dos `B` sinais nulos. O número `B`, o nível de significância `α` e a regra de aprovação são fixados antes da medição. **Nulos compostos:** as duas famílias de nulos (inarmônicos e aleatórios) são avaliadas em separado, cada uma com seu `p_emp`, e ρ₂ só é aceita se `max(p_inarmônico, p_aleatório) ≤ α`. Assim, um resultado favorável contra uma família não encobre falsa homologia frequente na outra. **Unidade de decisão:** a decisão primária é tomada por evento, no instante central do evento, definido pela anotação independente. Estatísticas ao longo do tempo do evento são exploratórias. Se uma estatística temporal vier a ser usada para decidir, a sua distribuição nula precisa ser calibrada sobre sinais nulos completos, que reproduzam a multiplicidade de instantes e a dependência temporal. Quando a modulação de frequência introduz erros correlacionados entre componentes, a matriz de covariância entra no ajuste |
| Níveis | **Mergulho exato:** todas as razões preservadas sem erro; referência teórica apenas. **Homomorfismo aproximado:** o ajuste passa no teste. **Cobertura parcial:** o ajuste passa depois de excluir componentes por regra fixada antes da medição; a fração mantida é reportada como escore, e não como prova. **Isomorfismo parcial:** homomorfismo aproximado bijetivo entre `C(t)` e um conjunto esperado de ordens definido sem usar a detecção (ver a ficha MCA) |
| Propriedades | Reflexiva e transitiva (composição de homomorfismos); não simétrica, porque a estrutura observada é finita e a ideal contém ordens não observadas. Coerente com o texto da Definição 3.2 |
| Controle e refutação | Modelo nulo obrigatório: conjuntos de componentes inarmônicos e conjuntos aleatórios com o mesmo `K` e a mesma banda, e também com relação sinal-ruído, distribuição de amplitudes, modulação de frequência e ruído comparáveis aos dos eventos, para que o modelo nulo não seja artificialmente fácil de rejeitar. Todos passam pelo procedimento completo, a partir do sinal, e não a partir de picos ideais. A taxa com que esses conjuntos passam no teste é a taxa de falsa homologia. Se ela não ficar abaixo de um limite fixado antes da medição, a tolerância não é informativa e o critério não pode ser aplicado. Refutação: a taxa de homologia nos dados não supera a taxa de falsa homologia |
| Estado | Especificada, condicionada ao modelo nulo |
| Grau de evidência | **Conjecturado** para o canto B |

Nota sobre o manuscrito: o texto da Definição 3.2 diz "homomorfismo", mas a fórmula usa uma seta com til, notação usual de isomorfismo, e a demonstração do Teorema 3.1 conclui "existe um isomorfismo". Este perfil adota o texto da definição.

### 5.3 ρ₃ — Equivalência

| Campo | Conteúdo |
|---|---|
| Fonte conceitual | Álgebra, Definição 3.3: `∀C ∈ 𝒞: C[x] ≃ C[y]`, substituibilidade em todo contexto. Whitepaper GuruDev, Seção 2.8: concordância entre conjuntos tomados como um todo |
| Definição HMAL | Dois eventos são equivalentes quando produzem a mesma assinatura em todos os contextos de análise do conjunto `𝒞`, fixado antes da medição |
| Objeto | Eventos inteiros (global) |
| Operador | Cada contexto é uma função `C_i` que leva um evento a uma saída discreta, com discretização fixada antes da medição. A assinatura é `S(e) = (C₁(e), …, C_m(e))`. Dois eventos são equivalentes quando `S(e) = S(e')` |
| Métrica | Partição dos eventos em classes de equivalência; número e tamanho das classes; estabilidade da classe de cada evento sob reamostragem |
| Tolerância | Embutida na discretização de cada contexto |
| Propriedades | Reflexiva, simétrica e transitiva por construção: a igualdade de saídas de uma função é sempre uma relação de equivalência. A partição em classes é, portanto, bem definida. A equivalência é relativa ao conjunto finito `𝒞` de contextos do HMAL, e não substituibilidade universal em todo contexto concebível, como na Definição 3.3 da Álgebra. Essa limitação fica declarada |
| Contextos candidatos | A fixar na ficha MCA, antes de qualquer medição. Exemplos: ordem do componente de maior energia; padrão das ordens dos três componentes mais fortes; classe do contorno de frequência (descendente, plano, ascendente, por limiar de inclinação); resultado do teste de homologia |
| Distinção em relação a ρ₄ | Dois eventos com a mesma assinatura que não são cópias escaladas um do outro são equivalentes e não simétricos. Duas cópias escaladas em que o ruído apagou um componente podem ter assinaturas diferentes: são simétricas e não equivalentes |
| Controle e refutação | Eventos perto dos limiares de discretização podem mudar de classe. A estabilidade é avaliada por reamostragem. Refutação: as classes não são estáveis, ou a partição não difere da obtida com assinaturas embaralhadas entre eventos |
| Estado | Especificada na forma; os contextos dependem de cada ficha |
| Grau de evidência | **Argumentado**: a construção é matemática; sua utilidade para eventos reais não foi testada |

### 5.4 ρ₄ — Simetria

| Campo | Conteúdo |
|---|---|
| Fonte conceitual | Álgebra, Definição 3.4: pertinência à mesma órbita sob um grupo de transformações. Morfologia Harmônica: Procrustes Harmônico, a transposição como remoção de simetria. HALE: canonicidade e invariância de escala (Definição 3.10 e Teorema 3.4) |
| Definição HMAL | Dois eventos, ou dois instantes do mesmo evento, são simétricos quando um é cópia do outro por um único fator de escala de frequência, dentro da incerteza |
| Objeto | Pares de eventos ou de instantes (intradomínio); séries de eventos ao longo de anos (global) |
| Operador | Grupo `𝒢 = {T_a : f ↦ a·f, a > 0}`. No domínio logarítmico, `T_a` é uma translação. Sobre as `K_c` ordens comuns, `d_k = ln f'_k − ln f_k`. A covariância de `d` é `V_d = Σ' + Σ − C − Cᵀ`, em que `C` é a covariância cruzada entre os dois eventos. `C = 0` só quando a independência entre os eventos for declarada e justificada, por exemplo eventos sem sobreposição temporal e com estimação separada; caso contrário, `C` é estimada. O fator é estimado pelo mesmo estimador de mínimos quadrados generalizados da Seção 4: `ln â = 1ᵀV_d⁻¹d / 1ᵀV_d⁻¹1`. É o Procrustes Harmônico restrito à translação em log-frequência |
| Métrica | Modelo único, ajustado por mínimos quadrados generalizados: `d_k = ln a + β·(k − k̄) + e_k`, com `e ~ N(0, V_d + τ²·I)`. O parâmetro `β` é a tendência dos resíduos com a ordem. O parâmetro `τ` é a dispersão residual além do ruído de medição já contido em `V_d`, isto é, o desvio da simetria que não depende da ordem. Também são reportados os resíduos `r_k = d_k − ln â` e o qui-quadrado com `K_c − 1` graus de liberdade, como estatísticas descritivas |
| Tolerância | Teste de equivalência, e não ausência de diferença significativa. Duas margens são fixadas antes da medição, por calibração com sinais sintéticos: `m_r`, para a dispersão dos resíduos, e `m_t`, para a inclinação dos resíduos em função da ordem `k`. A simetria é aceita quando duas condições valem ao mesmo tempo. Primeira: o limite superior do intervalo de confiança unilateral de 95% de `τ` fica abaixo de `m_r`. Esse limite é obtido por verossimilhança perfilada; com poucas ordens comuns, usa-se bootstrap paramétrico com número de réplicas fixado antes. Segunda: o intervalo de confiança de 90% de `β`, calculado com a covariância `V_d + τ̂²·I`, fica inteiramente dentro de `[−m_t, m_t]`, o que equivale a dois testes unilaterais (TOST, Two One-Sided Tests) a 5%. A ausência de tendência significativa não basta. Este é o método primário. As simulações podem compará-lo com alternativas, mas o método final é fixado antes da medição com dados reais |
| Propriedades | Sem tolerância, a relação de órbita é de equivalência, como na Álgebra. Com tolerância, a versão medida é reflexiva e simétrica, mas não transitiva. Isso fica declarado |
| Controle e refutação | Sinais sintéticos escalados com e sem inarmonicidade dependente da ordem, e com ruído correlacionado, para medir o poder do teste de equivalência. Refutação: a inclinação dos resíduos com a ordem fica fora da margem `m_t`, ou a dispersão excede `m_r`; ou seja, a estrutura não se preserva sob a mudança de escala |
| Estado | Especificada |
| Grau de evidência | **Conjecturado** |

### 5.5 ρ₅ — Equilíbrio

| Campo | Conteúdo |
|---|---|
| Fonte conceitual | Álgebra, Definição 3.5: `Φ(x) + Φ(y) = 0`, e a versão dinâmica com derivada temporal nula. Whitepaper GuruDev, Seção 2.3: "proporção e distribuição harmônica entre sistemas" |
| Linhas candidatas | **Equilíbrio relacional:** pares de componentes com potenciais complementares que se anulam. **Equilíbrio dinâmico:** estacionariedade de uma função de estado ao longo de uma janela, por exemplo a razão de energia entre duas ordens durante o chamado. As duas linhas são hipóteses distintas e terão funções `Φ` e testes próprios |
| Armadilha registrada | Se `Φ` for o resíduo de um ajuste de mínimos quadrados com intercepto, a soma ponderada dos resíduos é zero por construção. Um "equilíbrio" assim seria artefato do método. A função `Φ` precisa ser definida independentemente de qualquer ajuste |
| Requisitos para fechar | Função `Φ` independente do ajuste; pareamento fixado antes da medição; tolerância; modelo nulo |
| Propriedades | Simétrica, não reflexiva, não transitiva, como na Definição 3.5 |
| Estado | Aberta |
| Grau de evidência | **Especulado** |

### 5.6 ρ₆ — Compensação

| Campo | Conteúdo |
|---|---|
| Fonte conceitual | Álgebra, Definição 3.6: complementaridade, `Δ(x) = −Δ(y)`, e emergência, `Ω(x ⊕ y) > Ω(x) + Ω(y)`, com `Δ: S → ℝⁿ`, `Ω: S → ℝ` e `⊕` como composição. Whitepaper GuruDev, Seção 2.3: "suprir lacunas funcionais" |
| Pergunta HMAL | A combinação de componentes espectrais fornece informação sobre a fundamental que não se obtém de cada componente isolado? |
| Candidata a `Δ` | Desvio da energia de cada componente em relação à média ponderada do evento. No canto B, a fundamental fraca teria `Δ` negativo e o terceiro harmônico forte, positivo |
| Candidata a `Ω` | Informação sobre a fundamental medida pela redução de hipóteses. Fixa-se uma grade de hipóteses de fundamental `𝓕₀` numa banda declarada. Para um conjunto `S` de componentes, `𝓕(S)` é o subconjunto das hipóteses compatíveis com todos os componentes de `S`, isto é, para as quais cada componente fica perto de algum múltiplo inteiro, dentro da tolerância. Define-se `Ω(S) = log₂(|𝓕₀| / |𝓕(S)|)`. A operação `⊕` é a união dos conjuntos de componentes |
| Condição de emergência | `Ω(x ⊕ y) > Ω(x) + Ω(y)` equivale a `|𝓕(x ∪ y)| · |𝓕₀| < |𝓕(x)| · |𝓕(y)|`: as restrições combinadas eliminam mais hipóteses do que eliminariam se fossem independentes |
| Ressalvas | A quantidade de hipóteses eliminadas depende da resolução da grade `𝓕₀`. A grade, a banda e a distribuição prévia (hipóteses equiprováveis) são declaradas, e a sensibilidade de `Ω` à resolução é testada. A candidata a `Δ`, definida como desvio em relação à média, tem soma ponderada zero por construção: componentes acima e abaixo da média sempre existem. Observar sinais opostos não demonstra complementaridade; a complementaridade exigirá um critério que não seja satisfeito por qualquer distribuição de energia. A informação de Fisher de componentes independentes é aditiva e, por isso, não serve como `Ω`. Para uma série harmônica verdadeira, as hipóteses compatíveis com dois componentes incluem a fundamental e seus submúltiplos, e a interseção pode ser maior do que a esperada ao acaso. Se a simulação mostrar que a série harmônica é subaditiva nesse `Ω`, isso será um resultado informativo, e não uma falha. A validação de `Ω` exige o estimador independente `f̂₀` |
| Estado | Aberta, com candidata especificada para simulação |
| Grau de evidência | **Especulado** |

## 6. Regras gerais

1. **Sem agregação.** As seis dimensões são reportadas separadamente. Não se calcula escore único, e a norma ponderada pela razão áurea não é usada.
2. **Sem hierarquia lógica.** A ordem ρ₁ a ρ₆ é uma ordem conceitual de exigência. Não se pressupõe que uma relação implique outra, nem que sejam independentes. A Álgebra, no Teorema 3.1, afirma a cadeia de implicações. Na Seção 15.2, o próprio manuscrito reconhece que a demonstração é um esboço e pergunta, entre outros pontos, se existem modelos finitos em que alguma implicação falha. As fichas da MCA são exatamente esses modelos finitos, e o perfil das seis relações pode ser reportado como diagnóstico descritivo dessa pergunta.
3. **Dependências declaradas.** ρ₁ e ρ₂ compartilham `h` e `g`. ρ₃ pode usar o resultado de ρ₂ como contexto. Essas dependências são registradas em cada ficha.
4. **Fixação prévia.** Tolerâncias, contextos, pareamentos e níveis de significância são fixados antes de qualquer medição e registrados na ficha MCA correspondente.
5. **Harmônicos de uma mesma vocalização** continuam excluídos como evidência da hipótese H1 do pré-registro, que trata de relações entre unidades vocais distintas.

Generated by Claude
