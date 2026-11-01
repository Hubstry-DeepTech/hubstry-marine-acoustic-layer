# MCA-001 — Série harmônica musical e canto B da baleia-azul

**Matriz de Correspondências Analógicas do HMAL (MCA), ficha 001** · **Versão:** 0.1 (especificação para revisão da Luna e aprovação do Guilherme) · **Data:** 01/11/2026 · **Estado:** especificação conceitual; nenhuma medição foi feita e nenhum dado foi aberto para elaborá-la. **Rótulo:** `EXPLORATORY/FEASIBILITY`.

**Fontes das definições:** as seis relações de significância vêm do manuscrito da Álgebra Hexarrelacional de Significância (π√f(A)), de Guilherme Gonçalves Machado, conforme o README e o módulo `core/relations.py` do repositório `marcabru-tech/algebra-hexarrelacional` (commit `085f753`). As demais fontes citadas pelo código Sxx estão em `lab/sources/fontes.csv`.

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

**Sistema de destino: o canto B da baleia-azul do Pacífico Nordeste.** Trata-se de vocalização tonal com fundamental em torno de 15 Hz e modulação de frequência ao longo de 10 a 20 s. O terceiro harmônico concentra a maior energia e é o componente usualmente medido (S01). Um modelo publicado propõe que fundamental e sobretons resultem de uma série de pulsos pneumáticos (S02). Esse modelo é uma hipótese de produção, e não uma observação direta do mecanismo.

### 3.3 Representação como estruturas relacionais

Os dois sistemas são representados como estruturas relacionais no sentido da teoria dos conjuntos.

- **Estrutura ideal:** `𝓗 = ⟨ℕ⁺, r⟩`, em que cada elemento `n` é a ordem de um harmônico e `r(m, n) = m/n` é a razão entre componentes.
- **Estrutura observada no instante t:** `𝓑(t) = ⟨C(t), r̂_t⟩`, em que `C(t) = {c₁, …, c_K}` é o conjunto de componentes espectrais detectados, com frequências `f_k(t)`, e `r̂_t(c_j, c_k) = f_j(t)/f_k(t)`.

Uma atribuição de ordens é uma função `h: C(t) → ℕ⁺` que associa a cada componente observado uma ordem harmônica. A tolerância de comparação, `δ`, deriva da resolução e da incerteza de estimação de frequência, e será fixada antes de qualquer medição, a partir de sinais sintéticos.

## 4. As seis relações aplicadas aos dois sistemas

As relações são tratadas como seis dimensões independentes de um perfil de correspondência. Elas não são agregadas em um escore único, e a norma ponderada pela razão áurea não é usada nesta ficha (Seção 6).

| Relação | Definição no manuscrito | Instância nesta ficha | Grandeza medível | Classe de Hesse |
|---|---|---|---|---|
| ρ₁ Similitude | `d(φ(x), φ(y)) < ε`; reflexiva, simétrica, não transitiva | Proximidade de cada componente observado à posição ideal `h(c_k)·f₀(t)`, componente por componente, sem considerar as relações entre componentes | Desvio relativo `εₙ(t) = (fₙ(t) − n·f₀(t)) / (n·f₀(t))`, comparado à tolerância | Positiva: a física de sinais periódicos prevê a proximidade |
| ρ₂ Homologia | Existência de `h` entre as estruturas; reflexiva, transitiva, não simétrica | Existência de uma atribuição `h` que preserve todas as razões entre pares: `|r̂_t(c_j, c_k) − h(c_j)/h(c_k)| ≤ δ` | Fração de pares preservados e maior desvio entre pares, por instante e por evento | Positiva para a estrutura; neutra para sua estabilidade |
| ρ₃ Equivalência | `∀C: C[x] ≃ C[y]`; relação de equivalência | Igualdade da descrição estrutural em todos os contextos de análise: a mesma atribuição `h` vale em todos os segmentos do canto, em todos os eventos e em todos os dias | Proporção de contextos em que a atribuição se mantém; partição dos eventos em classes de mesma estrutura | Neutra |
| ρ₄ Simetria | `∃T ∈ 𝒢: T(x) = y`; órbita de um grupo de transformações | Invariância das razões sob o grupo de mudanças de escala de frequência, `T_a(f) = a·f`, que na música corresponde à transposição | Variação de `εₙ` em função de `f₀(t)` durante a modulação do canto e entre eventos | Neutra |
| ρ₅ Equilíbrio | `Φ(x) + Φ(y) = 0`; simétrica, não reflexiva, não transitiva | Candidata: cancelamento de desvios de sinal oposto entre componentes, com `Φ = εₙ` | Soma dos desvios de pares de componentes | Neutra; exige cautela, porque artefatos de estimação espectral também podem produzir desvios de sinais opostos |
| ρ₆ Compensação | A deficiência de um é o excesso do outro, e a combinação produz valor maior que a soma das partes | Candidata: a fundamental do canto B é fraca e o terceiro harmônico é forte; a frequência fundamental só é identificável pelo conjunto dos componentes, e não por um componente isolado de ordem desconhecida | Comparação entre a identificação e a precisão de `f₀` obtidas por cada componente isolado e pelo conjunto | Neutra |

Algumas instâncias pedem esclarecimento:

- **ρ₂ e a não simetria.** A atribuição `h` leva um conjunto finito de componentes observados a uma estrutura ideal infinita. Por isso, ela é um homomorfismo injetivo, e não um isomorfismo, e a relação é naturalmente não simétrica: a estrutura observada se insere na ideal, mas o inverso não ocorre. Essa leitura coincide com a implementação de `calculate_homology`, que mede a inserção de uma estrutura na outra (Seção 6, ponto 1).
- **ρ₃ e a equivalência de oitava.** Na teoria musical, a equivalência de oitava é o exemplo clássico de relação de equivalência: alturas separadas por oitavas pertencem à mesma classe. Sua relevância para o canto da baleia é uma analogia neutra, e esta ficha não a pressupõe.
- **ρ₄ e o declínio secular de frequência.** O canto B da população do Pacífico Nordeste vem baixando de frequência há décadas (S01). Perguntar se as razões internas se preservam nesse declínio é uma instância natural da simetria por escala. Essa pergunta envolve apenas componentes do canto B. Ela não compara chamados A e B e não forma a razão vedada pelo pré-registro.
- **ρ₆ e a fundamental ausente.** Em acústica musical, uma série de harmônicos especifica a fundamental mesmo quando o componente fundamental está ausente ou fraco. É o que a literatura de percepção chama de fundamental ausente, ou altura virtual. A ficha usa apenas a parte física desse fenômeno, a identificabilidade de `f₀` a partir do conjunto, sem qualquer inferência sobre a percepção do animal.

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

## 6. Pontos a resolver no manuscrito antes da medição

1. **A notação de ρ₂.** A definição simbólica usa `≅`, que indica isomorfismo. Um isomorfismo tem inversa e tornaria a relação simétrica, o que contradiz a propriedade declarada de não simetria. A implementação mede inserção de uma estrutura na outra, compatível com um homomorfismo injetivo. Propõe-se ajustar a notação para `h: Struct(x) ↪ Struct(y)`.
2. **A hierarquia cumulativa.** O manuscrito afirma que cada relação implica todas as anteriores. Com as definições formais, essa implicação não vale em geral. Uma transformação de grupo (ρ₄) não garante substitutibilidade em todos os contextos (ρ₃). O cancelamento de potenciais (ρ₅) não garante pertinência à mesma órbita (ρ₄). Nesta ficha, as seis relações são tratadas como dimensões independentes. A hierarquia pode ser mantida como ordem conceitual de exigência, desde que não seja usada como implicação lógica.
3. **A definição formal de ρ₆.** A expressão "valor maior que a soma das partes" exige especificar o valor medido e a operação de soma. A instância proposta na Seção 4 é uma candidata, a ser confirmada pelo autor da teoria.
4. **A ponderação pela razão áurea.** Os pesos `φ^(k−1)` da norma `f(A)` são uma escolha teórica, e não um resultado de medição. Em uso científico, esta ficha apresenta o perfil das seis dimensões sem agregação.

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
2. Resposta do autor da teoria aos quatro pontos da Seção 6.
3. Inclusão da linha de harmonicidade do canto B na proposta de emenda v1.4, com esta ficha como fundamento teórico.
4. Registro das fontes S23 e S24 em estado `texto_primario` antes da submissão de qualquer texto derivado.

Generated by Claude
