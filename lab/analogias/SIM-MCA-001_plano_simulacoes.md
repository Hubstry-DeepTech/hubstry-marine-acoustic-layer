# SIM-MCA-001 — Plano de simulações sintéticas da ficha MCA-001

**Versão:** 0.3.1 (incorpora o parecer da Luna sobre a v0.1, a revisão do Bloco 1 e o parecer sobre o piloto v2: busca exata com fatoração protegida e verificação reproduzível; opções para `Σ`) · **Data:** 01/11/2026 · **Estado:** em execução: piloto v2 do Bloco 1. Bloco 2 bloqueado até a aprovação da busca exata e de `Σ`. Nenhum dado real foi aberto. **Rótulo de todos os resultados:** `EXPLORATORY/FEASIBILITY`.

**Documentos de referência:**
- `lab/analogias/MCA-001_serie_harmonica_canto_B.md` (v0.5.4): a ficha cujos critérios estas simulações calibram;
- `lab/analogias/PERFIL_OPERACIONAL_HMAL_seis_relacoes.md` (v0.1.4): as definições operacionais das relações;
- `lab/PREREGISTRATION.md` (v1.3.1-draft): tem precedência em qualquer conflito.

## 1. Objetivo

As simulações têm dois objetivos.

1. **Verificar o comportamento dos critérios.** Com sinais de estrutura conhecida, medir se cada critério aceita o que deve aceitar e rejeita o que deve rejeitar, e com que frequência erra.
2. **Fixar os parâmetros em aberto.** A ficha e o perfil deixam vários valores para calibração com sinais sintéticos. As simulações produzem esses valores, que serão congelados antes de qualquer dado real (Seção 8).

As simulações não testam se o canto B é harmônico. Elas testam se o instrumento de medida funciona. Um resultado de simulação vale, no máximo, como grau **demonstrado em simulação** da tabela do HALE, e apenas para as propriedades do método.

## 2. Princípios

1. **Cadeia completa a partir da forma de onda.** Todo sinal sintético é gerado como forma de onda, passa pela mesma detecção de componentes, pelo mesmo estimador da fundamental e pela mesma busca de atribuições. Nenhuma etapa recebe picos ideais.
2. **Mesma taxa de amostragem dos dados previstos.** Os sinais são gerados a 2 kHz, a taxa dos arquivos decimados do MBARI (Monterey Bay Aquarium Research Institute). Uma variante passa por decimação a partir de 16 kHz, para simular o filtro de decimação.
3. **Parâmetros de literatura, não de dados.** As faixas de frequência, duração e modulação vêm de valores publicados (S01) e são deliberadamente amplas. Nenhum arquivo do MBARI é aberto para ajustá-las.
4. **Sementes determinísticas.** Cada sinal tem semente derivada de `SHA-256("SIM-MCA-001" | bloco | cenário | réplica)`. Esse espaço é separado do `MASTER_SEED` do pré-registro, que pertence ao conjunto `DS-00-SYNTH`.
5. **Calibração em um conjunto, verificação em outro.** Para cada parâmetro calibrado, as sementes usadas para escolher o valor são distintas das usadas para verificar o seu desempenho. Sem isso, as taxas de erro reportadas ficariam otimistas.

## 3. Gerador de sinais

### 3.1 Sinal harmônico de referência (G1)

`x(t) = Σₙ aₙ(t) · sin(2π · n · ∫₀ᵗ f₀(u) du + φₙ)`, para `n` de 1 até a última ordem abaixo de `f_max`.

- **Contorno da fundamental `f₀(t)`:** linear ou exponencial em `log f`, com inclinação em oitavas por segundo numa grade que inclui o plano e o descendente.
- **Perfil de amplitudes por ordem:** quatro perfis fixos. (a) Decrescente com a ordem. (b) Terceiro harmônico dominante e fundamental fraca, o caso que motiva a ficha. (c) Fundamental ausente com periodicidade identificável: ordens 2, 3, 4 e seguintes, cujo período continua sendo `1/f₀`. (d) Fundamental ausente com periodicidade ambígua: só ordens pares. Nesse caso, o sinal é periódico em `1/(2f₀)` e a fundamental física não é identificável a partir dele. Por determinação da Luna, a saída do estimador em (d) é classificada como período do sinal (`2f₀`), fundamental física ou outra, e não é contada como erro.
- **Envoltória temporal:** subida e descida suaves, para evitar transientes de borda.
- **Fases `φₙ`:** sorteadas uniformemente.

### 3.2 Desvios controlados da harmonicidade (G2)

- **Inarmonicidade dependente da ordem:** `fₙ = n · f₀ · √(1 + b · n²)`, com `b` numa grade que inclui zero. Serve ao poder de ρ₁, de ρ₂ e da tendência `β` de ρ₄.
- **Desvios independentes da ordem:** `fₙ = n · f₀ · (1 + δₙ)`, com `δₙ` sorteado com desvio-padrão `τ_sim`. Serve à dispersão `τ` de ρ₄.
- **Desvios heterocedásticos e correlacionados:** `δₙ` com variância crescente com a ordem, ou com correlação entre ordens vizinhas. Testam a hipótese `τ²·I` do perfil (Seção 5.4).

### 3.3 Famílias nulas de ρ₂ (G3 e G4)

O perfil exige duas famílias, avaliadas em separado.

- **G3 — inarmônico comodulado.** `K` componentes cujas frequências iniciais são sorteadas de forma independente com distribuição log-uniforme na banda `[f_lo, f_hi]`. Todos seguem a mesma modulação relativa de frequência do G1, `f_k(t) = f_k(0) · 2^(s·t)`. É a família mais difícil de rejeitar, porque preserva a comodulação, que também é propriedade dos sinais harmônicos.
  - **Zona de exclusão (formalização exigida pela Luna):** o sorteio é rejeitado e refeito se algum par `i < j` satisfizer `|ln(f_j/f_i) − ln(m/n)| < η` para alguma razão `m/n > 1` com `m, n ≤ n_excl`.
  - **Valores:** `n_excl = 6` e `η = 3·σ̃`, em que `σ̃` é a incerteza típica de `ln f` fixada no Bloco 1 para a condição de SNR do cenário.
  - **Por que `n_excl` pequeno:** com `n_excl` igual à ordem máxima `N`, as razões `m/n` cobririam a banda de forma quase densa e nenhum sorteio passaria. A exclusão remove só as coincidências com razões de inteiros pequenos, que tornariam o nulo trivialmente harmônico. As coincidências com razões de ordem mais alta permanecem e fazem parte da taxa de falsa homologia medida, como devem.
- **G4 — aleatório independente.** `K` componentes com frequências sorteadas uniformemente em log na mesma banda, cada um com modulação própria e independente.

Nas duas famílias, o número de componentes, a banda, a distribuição de amplitudes, a relação sinal-ruído, a duração e o ruído reproduzem os do cenário harmônico com que são comparadas.

### 3.4 Ruído e interferências

- **Ruído:** gaussiano branco e ruído colorido com espectro `1/f^α`, com `α` numa grade declarada.
- **Sobreposição de animais:** soma de dois sinais G1 com fundamentais distintas e defasagem temporal.
- **Propagação:** cópia atrasada e atenuada do próprio sinal (multipercurso simples).
- **Cadeia de gravação:** filtro de decimação e erro comum de relógio, isto é, um fator multiplicativo único em todas as frequências.

### 3.5 Convenção de SNR

A relação sinal-ruído (SNR, signal-to-noise ratio) é declarada como `SNR_integrated`, uma das três convenções do pré-registro: energia do sinal sobre energia do ruído, integradas no evento e na banda de análise. Os resultados são também reportados em `SNR_bin/frame` estimada, para permitir a comparação com os dados reais.

## 4. Cadeia de processamento sob teste

1. **Detecção de componentes.** Espectrograma por STFT (Short-Time Fourier Transform, transformada de Fourier de tempo curto), com janela e passo fixados no Bloco 1. Picos locais acima de um limiar sobre o piso de ruído local. Frequência refinada por interpolação parabólica do pico. A detecção não usa nenhuma hipótese sobre a fundamental.
2. **Incerteza e covariância `Σ`.** A incerteza é descrita por quantis empíricos do erro em `ln f`, por estrato de SNR local e de modulação, com SNR local mínima como controle de qualidade (decisão da Luna sobre o piloto). Picos falsos são contados à parte e não entram na distribuição do erro.
   - **Matriz operacional `Σ` (pendente; condição para o Bloco 2).** A Luna constatou que o código implementa `Σ = diag(s_k²) + c²·11ᵀ` (modo comum), e não a matriz geral `S·R·S` que a v0.3 descrevia. Há duas opções para decisão:
     - **(a) Diagonal mais modo comum.** É o que está implementado. É semidefinida positiva por construção, tem um único parâmetro de correlação e é bem condicionada. Como o termo comum não altera o `χ²`, em ρ₂ ela equivale, na prática, à matriz diagonal.
     - **(b) Correlação geral `R`.** Estimada em `cal` a partir dos pares de ordens. Exige regularização (por exemplo, contração em direção a (a)), projeção para a matriz semidefinida positiva mais próxima, controle do número de condição e regra para pares com amostra insuficiente.
     - **Recomendação:** (a), salvo se a verificação em `ver` mostrar correlação não comum relevante entre ordens. Em qualquer caso, a escolha será verificada em sementes inéditas, com positividade e condicionamento declarados.
     - **Por que isso não reintroduz a hipótese gaussiana:** em ρ₂, `χ²` é só uma forma quadrática que ordena as atribuições, e a significância vem da distribuição nula empírica. Em ρ₁, a tolerância usa diretamente os quantis empíricos.
   - **A componente comum da correlação não afeta ρ₂:** um termo `c²·11ᵀ` é absorvido pela escala (ver abaixo). A parte de `R` que pesa em ρ₂ é a correlação que não é comum a todos os componentes.
3. **Estimador independente `f̂₀`.** Candidatos: autocorrelação normalizada (família YIN) e cepstro. Estimadores por soma de harmônicos ficam fora, porque pressupõem a estrutura harmônica que ρ₂ testa e tornariam `E(t)` dependente dessa hipótese.
4. **Ordem máxima `N(t)` e conjunto esperado `E(t)`.** Como na ficha, Seção 3.4.
5. **Busca de atribuições e `H*`.** Ajuste por mínimos quadrados generalizados para cada atribuição injetiva e mínima, e conjunto `H*` pela margem `Δ_T`.
6. **Relações.** ρ₁, ρ₂, ρ₃ e ρ₄ exatamente como no perfil v0.1.4.

**Decisão D1 (aprovada condicionalmente; busca refeita após a revisão do Bloco 1).** Se `g > 0`, a ordem crescente das frequências impõe ordem crescente das ordens atribuídas. A busca é restrita às atribuições crescentes e mínimas, igualmente para dados e nulos.

**Contraexemplo da Luna.** A primeira versão enumerava as atribuições consistentes com arredondamento e acrescentava perturbações de ±1. A Luna mostrou que essa busca não é completa: num caso, ela parou em χ² = 2.900,87, com `(4, 5, 7, 9)`, enquanto a busca exaustiva achou χ² = 1.917,24, com `(5, 6, 8, 10)`. Reproduzi o problema: em 3.000 casos sorteados, a heurística errou o mínimo em 622. As falhas se concentram nos ajustes ruins, justamente os dos sinais nulos. O teste anterior passava porque só usava sinais quase harmônicos. Um teste que passa não demonstrava a completude.

**Busca exata adotada (`assignment.exact_search`).** Ramificação e poda, no estilo da decodificação em esfera.
- Com a escala ótima eliminada, `χ²(h) = vᵀMv`, em que `v = y − ln h` e `M = Σ⁻¹ − Σ⁻¹11ᵀΣ⁻¹/(1ᵀΣ⁻¹1)`, semidefinida.
- A decomposição `M = UᵀDU` escreve `χ²` como soma de termos não negativos, `d_k·(v_k + Σ_{j>k} U_kj·v_j)²`, em que cada termo depende só das ordens `k` em diante.
- A busca fixa as ordens da maior para a menor. A soma parcial é uma cota inferior de `χ²`. Assim, cada ordem só percorre o intervalo em que a cota não excede `T_min + Δ_T`. Nenhuma atribuição dentro desse raio é descartada.
- A cota inicial é finita: a melhor entre `(1, …, K)` e o resultado da heurística.

**Verificação.**
- Em 3.000 casos sorteados, com covariância não diagonal, ajustes bons e ruins e `Δ_T` de 0, 1 e 5, a busca exata coincidiu com a exaustiva no mínimo e no conjunto `H*` inteiro, sem nenhuma diferença.
- Os testes automáticos `test_exact_search_matches_exhaustive_including_poor_fits` e `test_rounding_heuristic_is_not_complete` registram as duas coisas.
- Custo em escala do canto B, com nulos aleatórios: mediana de 7 a 12 ms por busca para `K` de 6 a 10 e `N` de 60 a 70; máximo de 0,18 s.

**Efeito da restrição monótona.** Em 400 nulos aleatórios, a busca exaustiva sem a restrição de ordem achou `χ²` menor que a busca monótona uma única vez. A restrição é parte da definição da estatística e vale igualmente para dados e nulos. Por isso não compromete a validade de `p_emp`, mas fica registrada.

**Propriedade verificada nos testes:** um termo comum de covariância `c²·11ᵀ`, que representa a comodulação, não altera o qui-quadrado do ajuste, porque é absorvido pela escala. Ele aumenta apenas a variância de `ln g`. Portanto, a comodulação afeta ρ₁ e a incerteza da escala, mas não a estatística de ρ₂.

## 5. Blocos de simulação

### Bloco 1 — Detecção, incerteza e estimador da fundamental

**Pergunta:** a cadeia mede frequências com a incerteza que declara, e o estimador independente acerta a fundamental?

- Taxa de detecção e de falsos picos por SNR, perfil de amplitude e taxa de modulação.
- Viés e dispersão de `ln f_k`; comparação com a `σ_f` declarada.
- Erro de `f̂₀`, taxa de erro de oitava e de fator 3, e o critério de confiabilidade de `f̂₀`, nos três cenários determinados pela Luna: fundamental presente; fundamental ausente com periodicidade identificável; fundamental ausente com periodicidade ambígua. No terceiro, a saída esperada é indisponibilidade ou o período do sinal, e nada é contado como erro.
- Verificação de `f_max` com ruído branco processado pela cadeia de decimação.
- Verificação do limite de identificabilidade: acima da ordem prevista por `ln((n + 1)/n) > 2σ`, a taxa de atribuição errada de ordem adjacente deve subir.

**Fixa:** janela e passo da STFT, limiar de detecção, modelo de `σ_f` e de `Σ`, estimador `f̂₀` e o seu critério de confiabilidade, `f_max`.

### Bloco 2 — Similitude e homologia (ρ₁ e ρ₂)

**Pergunta:** com que frequência sinais não harmônicos passam como homólogos, e com que poder os harmônicos são reconhecidos?

- Taxa de falsa homologia em G3 e em G4, separadamente, por estrato de `K` e de SNR.
- Poder contra G1 e contra G2 com inarmonicidade crescente.
- **Calibração de `p_emp`:** sob cada família nula, a fração de casos com `p_emp ≤ α` não pode exceder `α`, dentro do erro de Monte Carlo.
- **Calibração de `Δ_T`:** tamanho de `H*` por estrato de `K`. Se um valor único gerar tamanhos muito diferentes entre estratos, `Δ_T` vira tabela, como prevê o perfil.
- ρ₁ em todas as atribuições de `H*`: tamanho do intervalo de sensibilidade e frequência com que a aprovação conservadora muda o resultado.
- Fatores de confusão da ficha (Seção 7, item 2): erro de oitava, sobreposição de animais, multipercurso e cadeia de gravação, cada um com o seu efeito sobre a decisão de ρ₂.

**Fixa:** `Δ_T` (valor ou tabela), `z` de ρ₁, `B`, `α`, limite aceitável de falsa homologia.

### Bloco 3 — Equivalência (ρ₃)

**Pergunta:** a assinatura de quatro contextos é estável para o mesmo gerador e diferente para geradores diferentes?

- Estabilidade: dois eventos do mesmo gerador, com ruído independente, devem receber a mesma assinatura com probabilidade alta.
- Discriminação: eventos de perfis de amplitude ou contornos diferentes devem receber assinaturas diferentes.
- Fração de eventos "não avaliáveis para ρ₃" por SNR, para fixar a cobertura mínima sem descartar a maioria dos eventos.
- Limiar `s` da classe de contorno e número mínimo de quadros.

**Fixa:** cobertura mínima, `s`, número mínimo de quadros.

### Bloco 4 — Simetria (ρ₄)

**Pergunta:** o teste de equivalência tem o tamanho e o poder declarados?

- Tamanho do TOST (Two One-Sided Tests): com `|β|` exatamente na margem `m_t`, a taxa de aceitação não pode exceder 5%.
- Cobertura real do intervalo de 90% de `β` com `τ̂` estimado dos mesmos dados, comparada com bootstrap paramétrico, sobretudo com poucas ordens comuns e com `τ` perto de zero.
- Cobertura do limite superior de `τ` por verossimilhança perfilada.
- Robustez à violação de `τ²·I`: desvios heterocedásticos e correlacionados (Seção 3.2).
- Covariância cruzada: erro comum de relógio entre dois eventos, para verificar que ele afeta `ln a` e não `β`; e o efeito de tomar `C = 0` indevidamente.

**Fixa:** `m_r`, `m_t`, o método final do intervalo de `β` e o número de réplicas do bootstrap.

**Decisão D2 (aprovada parcialmente).** Para `m_t`, vale o critério físico: na maior ordem identificável `N`, a tendência acumulada `|β| · (N − 1)` fica abaixo de metade da separação entre ordens adjacentes, `½ · ln((N + 1)/N)`. A Luna o aceitou como condição suficiente e conservadora. Para `m_r`, a derivação será probabilística e própria, a ser proposta no Bloco 4: por exemplo, o maior `τ` para o qual a probabilidade de um componente cair mais perto da ordem vizinha que da sua fica abaixo de um nível fixado. Os testes de fronteira usam `|β| = m_t` e também `τ = m_r`.

### Bloco 5 — Candidatas de ρ₆ (exploratório)

**Pergunta:** a candidata `Ω` mostra emergência na série harmônica, ou é subaditiva?

- `Ω(x ∪ y)` contra `Ω(x) + Ω(y)` para pares de componentes de G1, G3 e G4.
- Sensibilidade à resolução da grade `𝓕₀` e à banda declarada.
- Demonstração da armadilha registrada no perfil: a candidata `Δ` definida como desvio da média tem soma ponderada nula para qualquer gerador.

ρ₅ continua aberta. Sem uma função `Φ` definida independentemente de qualquer ajuste, não há o que simular.

**Fixa:** nada. O resultado alimenta a decisão de manter, reformular ou abandonar as candidatas.

## 6. Tamanhos de Monte Carlo e critérios de aceite

- Cada taxa de erro é estimada com intervalo de Clopper–Pearson de 95%, como no plano da Fase 1.
- **Piloto:** até 2.000 réplicas por cenário. Serve para medir custos e localizar problemas, e não para aceitar parâmetros.
- **Validação final das taxas de erro tipo I** (falsa homologia, tamanho do TOST, calibração de `p_emp`): 6.000 réplicas por cenário.
- **Critério de aceite:** o limite superior **unilateral** de 95% de Clopper–Pearson não excede o nível nominal mais 1 ponto percentual.
- **Por que 6.000:** a Luna mostrou que, com 2.000 réplicas e intervalo bilateral, um teste exatamente calibrado seria aprovado só cerca de metade das vezes. O cálculo binomial exato (`stats.pass_probability`, verificado em teste automático) dá, para um teste calibrado em 5%: 61% de aprovação com 2.000 réplicas, 93% com 5.000 e 96% com 6.000. Entre 5.700 e 6.300 réplicas, a probabilidade fica sempre acima de 95%.
- Poder e estabilidade: pelo menos 500 réplicas por cenário.
- Número de nulos `B` dentro de cada `p_emp`: candidato 999, a confirmar no Bloco 2 pelo custo de processamento.
- Se o critério falhar, o parâmetro é recalibrado nas sementes de calibração e verificado de novo em sementes de verificação novas.
- **Separação obrigatória:** nenhum parâmetro é escolhido e avaliado nas mesmas sementes. A partição `cal` ou `ver` faz parte da semente de cada sinal (`seeds.py`), e os relatórios indicam de qual partição vem cada número.

## 7. Implementação e reprodutibilidade

- **Local no repositório:** `lab/sim_mca001/`, novo diretório. Nenhum arquivo protegido pelo `FREEZE_v0.4.json` é alterado.
- **Linguagem:** Python, com NumPy e SciPy em versões fixadas num `constraints` próprio.
- **Testes automáticos antes de qualquer bloco:**
  - sinal G1 sem ruído recupera `h` exata e qui-quadrado próximo de zero;
  - sinal com componentes só em `2f₀` e `4f₀` recebe a atribuição mínima `(1, 2)`, como declara o perfil;
  - a fórmula de `p_emp` dá `1/(B + 1)` quando nenhum nulo supera o observado;
  - mínimos quadrados generalizados com `Σ` diagonal coincidem com mínimos quadrados ponderados.
- **Saídas:** um arquivo JSON por bloco, com parâmetros, sementes, versões e resultados; um manifesto SHA-256; um relatório por bloco.
- **Execução:** piloto pequeno de cada bloco numa máquina local, para medir o custo. As rodadas completas, se o custo exigir, vão para a VM da Hubstry na GCP (Google Cloud Platform), sem alterar o código.

## 8. Tabela de parâmetros a congelar

| Parâmetro | Onde é usado | Bloco que o fixa |
|---|---|---|
| Janela e passo da STFT, limiar de detecção | Detecção | 1 |
| Modelo de `σ_f` e `Σ` | Todas as relações | 1 |
| Estimador `f̂₀` e critério de confiabilidade | `N(t)`, `E(t)`, ρ₆ | 1 |
| `f_max` | `N(t)` | 1 |
| `Δ_T` (valor ou tabela por `K`) | `H*`, ρ₁, ρ₃ | 2 |
| `z` | ρ₁ | 2 |
| `B`, `α`, limite de falsa homologia | ρ₂ | 2 |
| Cobertura mínima, `s`, quadros mínimos | ρ₃ | 3 |
| `m_r`, `m_t`, método do intervalo de `β` | ρ₄ | 4 |

Ao fim dos Blocos 1 a 4, esta tabela é preenchida, revisada pela Luna e registrada na ficha MCA-001 como versão própria, com hash. Só então a ficha pode ser proposta para a emenda v1.4 do pré-registro.

## 9. Ordem de execução

1. Testes automáticos e gerador (Seções 3 e 7).
2. Bloco 1, porque todos os outros dependem de `σ_f`, `Σ` e `f̂₀`.
3. Bloco 2.
4. Bloco 4.
5. Bloco 3, que usa `H*` e o resultado de ρ₂.
6. Bloco 5, exploratório.

## 10. Decisões pedidas à revisão

Parecer da Luna sobre a v0.1:

| Decisão | Estado |
|---|---|
| D1 — atribuições crescentes | Aprovada condicionalmente. A heurística por arredondamento falhou na revisão independente da Luna; foi substituída por busca exata, verificada contra a exaustiva (Seção 4). Aguarda nova aprovação |
| D2 — margens físicas | Aprovada para `m_t`; `m_r` com derivação probabilística própria no Bloco 4 |
| D3 — famílias G3 e G4 | Aprovadas; distribuição e zona de exclusão de G3 formalizadas na Seção 3.3 |
| D4 — fundamental independente | Aprovada |
| D5 — Monte Carlo | Aprovada para piloto; validação final com 6.000 réplicas e critério unilateral (Seção 6) |

## 11. O que estas simulações não fazem

- Não abrem dados do MBARI nem de outra fonte real.
- Não dizem nada sobre o canto B. Um critério bem calibrado em simulação pode ainda falhar com dados reais, por fatores não simulados.
- Não tocam a hipótese H1 do pré-registro nem o par de chamados A e B.

Generated by Claude
