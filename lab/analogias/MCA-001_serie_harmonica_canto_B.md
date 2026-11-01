# MCA-001 — Série harmônica musical e canto B da baleia-azul

**Matriz de Correspondências Analógicas do HMAL (MCA), ficha 001** · **Versão:** 0.3 (incorpora as decisões do autor da teoria e o parecer da Luna sobre a v0.2, ambos de 01/11/2026) · **Data:** 01/11/2026 · **Estado:** especificação conceitual; nenhuma medição foi feita e nenhum dado foi aberto para elaborá-la. **Rótulo:** `EXPLORATORY/FEASIBILITY`.

**Fontes das definições:** as seis relações de significância vêm do manuscrito "π√f(A): Uma Álgebra Hexa Relacional de Significância para Algoritmos" (fevereiro de 2026), de Guilherme Gonçalves Machado, Seções 3.2 a 3.7, conferidas no texto integral, e do módulo `core/relations.py` do repositório `marcabru-tech/algebra-hexarrelacional` (commit `085f753`). As demais fontes citadas pelo código Sxx estão em `lab/sources/fontes.csv`.

## 1. Finalidade

Esta ficha especifica como a correspondência entre a série harmônica, tal como a acústica musical a descreve, e o canto B da baleia-azul pode ser examinada pelas seis relações de significância do HexaSign. A ficha também estabelece o que pode ser medido, o que permanece hipotético e o que a correspondência não autoriza concluir.

A ficha cumpre dois propósitos complementares.

O primeiro é científico: oferecer um quadro teórico explícito para a linha exploratória de harmonicidade do canto B, proposta como parte da emenda v1.4 do pré-registro.

O segundo é metodológico: submeter as seis relações, até aqui estimadas por heurísticas lexicais em textos e por cobertura de estruturas sintáticas em código, a um domínio em que suas instâncias podem ser definidas sobre grandezas físicas mensuráveis, com tolerâncias derivadas da resolução instrumental.

## 2. Relação com o pré-registro e com a Fase 1

Esta ficha não integra a hipótese H1 do pré-registro v1.3.1-draft. A Seção 3.2 desse documento exclui expressamente os harmônicos de uma mesma vocalização como evidência de relações entre unidades vocais distintas, e essa exclusão permanece. A harmonicidade do canto B é uma pergunta diferente, que só poderá ser investigada depois de registrada em emenda versionada, com motivação, data e indicação dos dados já observados, antes de qualquer medição.

A ficha também não altera a Fase 1, cujo escopo exclui frequência fundamental e harmônicos. As medições aqui especificadas pertencem à Fase 2.

## 3. Quadro teórico

### 3.1 Modalidades de analogia

O HMAL adota uma taxonomia de trabalho com três modalidades. Ela não corresponde a uma classificação consolidada na literatura e é definida aqui para uso consistente no projeto.

- **Analogia heurística:** um sistema conhecido é usado para formular perguntas sobre outro, sem pretensão de correspondência demonstrada.
- **Analogia funcional:** componentes de dois sistemas desempenham papéis comparáveis em seus respectivos contextos.
- **Analogia homológica, ou homologia estrutural:** entendida neste estudo como correspondência entre as relações constitutivas de sistemas distintos, independentemente de ancestralidade ou origem evolutiva comum. O termo não é usado no sentido da biologia evolutiva, em que homologia designa semelhança por descendência comum.

Dois referenciais complementam essa taxonomia sem se confundir com ela. Mary Hesse (S23) distingue analogias positivas, que são propriedades sabidamente compartilhadas, negativas, que são propriedades sabidamente distintas, e neutras, ainda não examinadas. Dedre Gentner (S24) sustenta que uma analogia consistente preserva relações entre elementos, e não apenas atributos superficiais, e que sistemas de relações interligadas pesam mais do que relações isoladas.

### 3.2 Os dois sistemas

**Sistema de origem: a série harmônica da acústica musical.** Um som periódico de frequência fundamental `f₀` contém componentes em `fₙ = n·f₀`, com `n = 1, 2, 3, …`. As razões entre componentes são razões de números inteiros; a oitava corresponde a 2:1, a quinta justa a 3:2, e a décima segunda, entre a fundamental e o terceiro harmônico, a 3:1. Essas relações são consequência da periodicidade do sinal, e não de uma escolha perceptiva ou cultural. A organização dessas relações em escalas, consonâncias e afinações já pertence à percepção e à cultura humanas.

**Sistema de destino: o canto B da baleia-azul do Pacífico Nordeste.** Trata-se de vocalização tonal, com duração de vários segundos e modulação de frequência ao longo do chamado. O terceiro harmônico concentra a maior energia e é o componente usualmente medido. Sua frequência de pico, medida a 10 s do início, ficou entre 46,1 Hz (2006) e 42,6 Hz (2019), o que situa a fundamental perto de 15 Hz (S01). Segundo o resumo de um artigo publicado, fundamental e sobretons podem ser modelados por uma série de ondículas curtas, atribuídas a pulsos pneumáticos (S02, conferido apenas pelo resumo). Esse modelo é uma hipótese de produção, e não uma observação direta do mecanismo.

### 3.3 Representação como estruturas relacionais finitas

Os dois sistemas são representados como estruturas relacionais finitas, no sentido da teoria dos conjuntos.

- **Estrutura ideal de comparação:** `𝓗_N = ⟨{1, …, N}, r⟩`, em que cada elemento `n` é a ordem de um harmônico e `r(m, n) = m/n`. A ordem máxima `N` é fixada pela banda analisada: com arquivos de 2 kHz e análise até 990 Hz, `N = ⌊990 / f₀⌋`. A restrição a um conjunto finito é necessária, porque nenhuma correspondência bijetiva pode existir entre um conjunto finito de componentes observados e o conjunto infinito dos números naturais.
- **Estrutura observada no instante t:** `𝓑(t) = ⟨C(t), r̂_t⟩`, em que `C(t) = {c₁, …, c_K}` é o conjunto de componentes espectrais detectados, com frequências `f_k(t)` e incertezas `σ_k(t)`, e `r̂_t(c_j, c_k) = f_j(t)/f_k(t)`.

Uma **atribuição de ordens** é uma função `h: C(t) → {1, …, N}`. A atribuição é exigida injetiva por definição: componentes distintos recebem ordens distintas. A injetividade não decorre da cardinalidade dos conjuntos. Ela é uma condição do procedimento, e uma atribuição que associe dois componentes à mesma ordem é rejeitada.

A **tolerância** de comparação para uma razão entre os componentes `c_j` e `c_k` deriva da propagação das incertezas de frequência: `δ_jk = z · r̂_jk · √((σ_j/f_j)² + (σ_k/f_k)²)`, com o fator `z` e o método de estimação de `σ` fixados antes de qualquer medição, por calibração com sinais sintéticos.

Três níveis de correspondência estrutural são distinguidos:
- **homomorfismo exato:** todas as razões entre pares são preservadas, sem tolerância. Serve apenas como referência teórica, porque medições com ruído não o alcançam;
- **homomorfismo aproximado:** todas as razões entre pares são preservadas dentro de `δ_jk`;
- **cobertura parcial:** apenas uma fração dos pares satisfaz o critério. A fração é um escore de correspondência, e não prova da existência de um homomorfismo.

O isomorfismo, caso máximo da homologia, corresponde a um homomorfismo aproximado em que todas as ordens de `{1, …, N}` com energia acima do limiar de detecção têm componente observado.

## 4. As seis relações aplicadas aos dois sistemas

As seis relações são reportadas separadamente, como dimensões conceituais do perfil de correspondência. Não se pressupõe implicação lógica geral entre elas, nem independência matemática ou estatística. ρ₁ e ρ₂, por exemplo, usam a mesma atribuição `h` e a mesma estimativa de `f₀`, e seus resultados não são independentes. As dimensões não são agregadas em um escore único, e a norma ponderada pela razão áurea não é usada nesta ficha (Seção 6).

| Relação | Definição no manuscrito | Instância nesta ficha | Grandeza medível | Estado |
|---|---|---|---|---|
| ρ₁ Similitude | `d(φ(x), φ(y)) < ε`; reflexiva, simétrica, não transitiva | `x` é um componente observado `c_k`; `y` é o elemento ideal `h(c_k)·f₀(t)`; `φ` é o logaritmo da frequência; `d` é a diferença absoluta. A relação vale quando o desvio está dentro da tolerância | `|ln f_k − ln(h(c_k)·f₀)|`, aproximadamente o desvio relativo `εₙ(t)` | Especificada |
| ρ₂ Homologia | Homomorfismo `h` entre as estruturas; reflexiva, transitiva, não simétrica | Existência de uma atribuição injetiva `h` que preserve as razões entre pares, nos três níveis da Seção 3.3 | Nível alcançado; fração de pares preservados; maior desvio normalizado `|r̂_jk − h_j/h_k| / δ_jk` | Especificada |
| ρ₃ Equivalência | `∀C: C[x] ≃ C[y]`; relação de equivalência | Dois instantes ou eventos são equivalentes quando, nas ordens presentes em ambos, as atribuições coincidem e as razões são preservadas. Exige ao menos três ordens comuns. Componentes ausentes não violam a relação, mas reduzem a cobertura, que é reportada | Proporção de pares de contextos equivalentes; número de ordens comuns; partição dos eventos em classes | Especificada, com regra de ausências |
| ρ₄ Simetria | `∃T ∈ 𝒢: T(x) = y`; órbita de um grupo de transformações | Hipótese empírica: os componentes observados em dois instantes ou eventos relacionam-se por um mesmo fator de escala `a`, com `f_k' ≈ a·f_k` para todas as ordens comuns. A invariância das razões sob `T_a` é propriedade matemática da transformação; o que se testa é se os dados se comportam assim | Estimativa de `ln a` por mínimos quadrados nas ordens comuns; dispersão dos resíduos comparada com a incerteza | Especificada |
| ρ₅ Equilíbrio | `Φ(x) + Φ(y) = 0`; simétrica, não reflexiva, não transitiva | Questão aberta. Uma candidata seria o pareamento de ordens adjacentes, com `Φ` igual ao desvio relativo normalizado, mas o pareamento, a normalização e a tolerância não estão definidos, e artefatos de estimação espectral também produzem desvios de sinais opostos | Não definida | Aberta |
| ρ₆ Compensação | Complementaridade `Δ(x) = −Δ(y)` e emergência `Ω(x ⊕ y) > Ω(x) + Ω(y)` | Questão aberta. A distribuição de energia do canto B, com fundamental fraca e terceiro harmônico forte, e a identificabilidade de `f₀` pelo conjunto dos componentes são pontos de partida. Nenhum deles demonstra, por si, complementaridade ou superaditividade | Exigiria uma função quantitativa `Ω`, por exemplo uma medida de informação sobre `f₀`, comparada entre componentes isolados e conjunto | Aberta |

Algumas instâncias pedem esclarecimento:

- **ρ₂ e a implementação existente.** O README do repositório usa uma seta com til na notação de ρ₂. A docstring de `calculate_homology` usa `≅` e descreve a operação como isomorfismo estrutural. A função calcula a cobertura direcional de multiconjuntos de tipos de nós de árvores sintáticas de código. Ela não constrói nem verifica um homomorfismo entre estruturas relacionais. Fica registrada como aproximação heurística legada, a ser substituída na refatoração do HexaSign.
- **ρ₃ e a equivalência de oitava.** Na teoria musical, a equivalência de oitava é o exemplo clássico de relação de equivalência: alturas separadas por oitavas pertencem à mesma classe. Sua relevância para o canto da baleia é uma analogia neutra, e esta ficha não a pressupõe.
- **ρ₄ e o declínio secular de frequência.** O terceiro harmônico do canto B da população do Pacífico Nordeste baixou de frequência entre 2006 e 2019 (S01). Perguntar se os demais componentes acompanham esse declínio pelo mesmo fator de escala é uma instância natural da simetria. A pergunta envolve apenas componentes do canto B. Ela não compara chamados A e B e não forma a razão vedada pelo pré-registro.
- **ρ₆ e a fundamental ausente.** Em acústica, uma série de harmônicos especifica a fundamental mesmo quando o componente fundamental está fraco ou ausente. A ficha usa apenas a parte física desse fenômeno, sem inferência sobre a percepção do animal, e o registra como ponto de partida para formalizar ρ₆, e não como instância já especificada.

## 5. Analogias positivas, negativas e neutras

**Positivas (compartilhadas por razões físicas):**
- componentes em múltiplos inteiros da fundamental, enquanto o sinal for periódico;
- as razões 2:1, 3:2 e 3:1 entre os três primeiros componentes.

**Negativas (não transferíveis):**
- a organização em escalas, a consonância e a função estética, que pertencem à percepção e à cultura humanas;
- qualquer intenção musical do animal;
- a percepção do canto como sequência de notas;
- o significado comunicativo dos componentes, que pertence ao domínio da zoossemiótica e exige dados de comportamento.

**Neutras (a investigar):**
- a estabilidade da estrutura harmônica ao longo do canto e entre eventos (ρ₃);
- a invariância das razões sob a modulação e o declínio de frequência (ρ₄);
- as instâncias candidatas de equilíbrio e compensação (ρ₅ e ρ₆);
- a relação entre o desvio da harmonicidade ideal e o modelo de produção por pulsos pneumáticos (S02).

## 6. Decisões sobre o manuscrito e pontos ainda abertos

**Decididos pelo autor da teoria em 01/11/2026:**

1. **Homologia como homomorfismo.** A Definição 3.2 do manuscrito já define `h` como homomorfismo e declara a simetria apenas no caso de isomorfismo. Outros textos do autor usam formulações mais fortes: a tabela do README do repositório e a docstring do código usam `≅`, e a TICA (Seção 7.4) fala em "mapeamento biunívoco que preserva todas as relações". Fica adotada a definição do manuscrito: a homologia é um homomorfismo, medido como grau de preservação das relações, e o isomorfismo é o caso máximo. A notação recomendada é `h: Struct(x) → Struct(y)`, ou `↪` quando o homomorfismo for injetivo, e os textos que usam `≅` serão harmonizados.
2. **Hierarquia como ordem conceitual.** O manuscrito afirma que cada relação implica todas as anteriores. Com as definições formais, essa implicação não vale em geral, e o próprio manuscrito admite exceções. A Seção 3.6 diz que o equilíbrio "não exige que os elementos sejam transformáveis um no outro", o que nega a passagem de ρ₅ para ρ₄. Fica adotado que a hierarquia é uma ordem conceitual de exigência, e não uma implicação lógica. As seis relações são reportadas separadamente, sem implicação lógica geral entre elas e sem pressupor independência matemática ou estatística.

**Ainda abertos:**

3. **A definição formal de ρ₅ e ρ₆.** A Definição 3.6 do manuscrito tem duas partes: complementaridade, `Δ(x) = −Δ(y)`, e emergência, `Ω(x ⊕ y) > Ω(x) + Ω(y)`. As funções `Δ`, `Ω` e a operação `⊕` não estão especificadas. A Definição 3.5 exige escolher a função `Φ` e o pareamento dos elementos. Nesta ficha, ρ₅ e ρ₆ permanecem questões abertas (Seção 4).
4. **A ponderação pela razão áurea.** O manuscrito (Seção 5.1) justifica os pesos `φ^(k−1)` por razões estéticas e de design, e não por medição. Em uso científico, esta ficha apresenta o perfil das seis dimensões sem agregação.

## 7. Critérios de falsificação

A correspondência estrutural deve ser considerada enfraquecida se:
- os desvios `εₙ` excederem sistematicamente a tolerância `δ`, depois de descontados os efeitos de modulação de frequência, resolução espectral e sobreposição de fontes;
- nenhuma atribuição `h` preservar as razões entre pares na maioria dos instantes de eventos identificados com confiança.

Esses resultados não refutariam a física da série harmônica, que vale para qualquer sinal periódico. Indicariam que o canto B não se comporta como sinal periódico estável na escala de análise adotada, o que é em si um resultado informativo sobre o mecanismo de produção.

A simetria por escala (ρ₄) é enfraquecida se os desvios relativos variarem sistematicamente com `f₀`, além da incerteza de estimação.

Nenhum desses critérios será aplicado antes de os eventos serem identificados por procedimento independente, conforme a linha de anotação de eventos, e antes de as tolerâncias serem fixadas com sinais sintéticos.

## 8. Papel das tecnologias da Hubstry

- **GuruDev Core:** representação formal das duas estruturas, das atribuições e das evidências. O validador semântico ainda está em desenvolvimento, segundo seu README.
- **HexaSign:** cálculo do perfil das seis dimensões. Exige implementar estimadores das seis relações sobre estruturas relacionais com grandezas físicas, distintos das heurísticas lexicais atuais (`src/lib/hexa-engine.ts`), que permanecem experimentais.
- **GrammAIr Flow:** revisão da clareza e da consistência terminológica dos textos, sem papel na decisão sobre a validade da correspondência.

## 9. Próximos passos

1. Revisão desta ficha pela Luna.
2. Formalização de ρ₅ e ρ₆ pelo autor da teoria (Seção 6, ponto 3).
3. Inclusão da linha de harmonicidade do canto B na proposta de emenda v1.4, com esta ficha como fundamento teórico.
4. Conferência das fontes S02, S23 e S24 no texto primário antes da submissão de qualquer texto derivado. As referências Sxx estão no registro de fontes do PR #14, que deve ser incorporado antes desta ficha.

Generated by Claude
