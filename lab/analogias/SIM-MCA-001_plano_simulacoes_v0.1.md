# SIM-MCA-001 — Plano de simulações sintéticas da ficha MCA-001

**Versão:** 0.1 · **Data:** 01/11/2026 · **Estado:** plano para revisão da Luna; nenhuma linha de código de simulação foi escrita e nenhum dado real foi aberto. **Rótulo de todos os resultados:** `EXPLORATORY/FEASIBILITY`.

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
- **Perfil de amplitudes por ordem:** três perfis fixos. (a) decrescente com a ordem; (b) terceiro harmônico dominante e fundamental fraca; (c) fundamental ausente. O perfil (b) é o caso que motiva a ficha; o (c) testa o erro de oitava.
- **Envoltória temporal:** subida e descida suaves, para evitar transientes de borda.
- **Fases `φₙ`:** sorteadas uniformemente.

### 3.2 Desvios controlados da harmonicidade (G2)

- **Inarmonicidade dependente da ordem:** `fₙ = n · f₀ · √(1 + b · n²)`, com `b` numa grade que inclui zero. Serve ao poder de ρ₁, de ρ₂ e da tendência `β` de ρ₄.
- **Desvios independentes da ordem:** `fₙ = n · f₀ · (1 + δₙ)`, com `δₙ` sorteado com desvio-padrão `τ_sim`. Serve à dispersão `τ` de ρ₄.
- **Desvios heterocedásticos e correlacionados:** `δₙ` com variância crescente com a ordem, ou com correlação entre ordens vizinhas. Testam a hipótese `τ²·I` do perfil (Seção 5.4).

### 3.3 Famílias nulas de ρ₂ (G3 e G4)

O perfil exige duas famílias, avaliadas em separado.

- **G3 — inarmônico comodulado.** `K` componentes com razões não inteiras sorteadas na mesma banda, todos seguindo a mesma modulação relativa de frequência do G1. É a família mais difícil de rejeitar, porque preserva a comodulação, que também é propriedade dos sinais harmônicos. Para impedir razões acidentalmente próximas de inteiros pequenos, o sorteio exclui uma vizinhança declarada em torno de cada razão `m/n` com `m, n ≤ N`.
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
2. **Incerteza `σ_f` e covariância `Σ`.** Calibradas empiricamente no Bloco 1, como função da SNR do componente e da taxa de modulação. A covariância entre componentes do mesmo quadro vem da comodulação e é estimada nas simulações.
3. **Estimador independente `f̂₀`.** Candidatos: autocorrelação normalizada (família YIN) e cepstro. Estimadores por soma de harmônicos ficam fora, porque pressupõem a estrutura harmônica que ρ₂ testa e tornariam `E(t)` dependente dessa hipótese.
4. **Ordem máxima `N(t)` e conjunto esperado `E(t)`.** Como na ficha, Seção 3.4.
5. **Busca de atribuições e `H*`.** Ajuste por mínimos quadrados generalizados para cada atribuição injetiva e mínima, e conjunto `H*` pela margem `Δ_T`.
6. **Relações.** ρ₁, ρ₂, ρ₃ e ρ₄ exatamente como no perfil v0.1.4.

**Ponto para decisão (D1).** Se `g > 0`, a ordem crescente das frequências impõe ordem crescente das ordens atribuídas. Uma atribuição não monótona só se ajusta dentro da tolerância se dois componentes estiverem praticamente na mesma frequência. Proponho declarar no perfil que `h` é monótona crescente. Isso reduz a busca de todas as funções injetivas para as `C(N, K)` combinações, sem perder nenhuma atribuição plausível.

## 5. Blocos de simulação

### Bloco 1 — Detecção, incerteza e estimador da fundamental

**Pergunta:** a cadeia mede frequências com a incerteza que declara, e o estimador independente acerta a fundamental?

- Taxa de detecção e de falsos picos por SNR, perfil de amplitude e taxa de modulação.
- Viés e dispersão de `ln f_k`; comparação com a `σ_f` declarada.
- Erro de `f̂₀` e taxa de erro de oitava, com e sem fundamental, e o critério de confiabilidade de `f̂₀`.
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

**Ponto para decisão (D2).** As margens precisam de um critério de relevância, e não apenas de calibração estatística. Proponho um critério físico: na maior ordem identificável `N`, a tendência acumulada `|β| · (N − 1)` deve ficar abaixo de metade da separação entre ordens adjacentes, `½ · ln((N + 1)/N)`. Abaixo disso, a tendência não chega a confundir ordens vizinhas. Critério análogo para `m_r`. A simulação mede então o poder com essas margens.

### Bloco 5 — Candidatas de ρ₆ (exploratório)

**Pergunta:** a candidata `Ω` mostra emergência na série harmônica, ou é subaditiva?

- `Ω(x ∪ y)` contra `Ω(x) + Ω(y)` para pares de componentes de G1, G3 e G4.
- Sensibilidade à resolução da grade `𝓕₀` e à banda declarada.
- Demonstração da armadilha registrada no perfil: a candidata `Δ` definida como desvio da média tem soma ponderada nula para qualquer gerador.

ρ₅ continua aberta. Sem uma função `Φ` definida independentemente de qualquer ajuste, não há o que simular.

**Fixa:** nada. O resultado alimenta a decisão de manter, reformular ou abandonar as candidatas.

## 6. Tamanhos de Monte Carlo e critérios de aceite

- Cada taxa de erro é estimada com intervalo de Clopper–Pearson de 95%, como no plano da Fase 1.
- Taxas de erro tipo I (falsa homologia, tamanho do TOST, calibração de `p_emp`): pelo menos 2.000 réplicas por cenário, o que dá meia-largura de cerca de 1 ponto percentual perto de 5%.
- Poder e estabilidade: pelo menos 500 réplicas por cenário.
- Número de nulos `B` dentro de cada `p_emp`: candidato 999, a confirmar no Bloco 2 pelo custo de processamento.
- **Critério de aceite de cada taxa de erro tipo I:** o limite superior do intervalo de Clopper–Pearson não excede o nível nominal mais 1 ponto percentual. Se exceder, o parâmetro é recalibrado no conjunto de calibração e verificado de novo em sementes novas.

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

- **D1:** declarar `h` monótona crescente no perfil (Seção 4).
- **D2:** critério físico para as margens `m_t` e `m_r` (Bloco 4).
- **D3:** definição das duas famílias nulas, em especial a exclusão de razões próximas de inteiros pequenos em G3 (Seção 3.3).
- **D4:** exclusão dos estimadores de `f̂₀` por soma de harmônicos (Seção 4).
- **D5:** tamanhos de Monte Carlo e critério de aceite (Seção 6).

## 11. O que estas simulações não fazem

- Não abrem dados do MBARI nem de outra fonte real.
- Não dizem nada sobre o canto B. Um critério bem calibrado em simulação pode ainda falhar com dados reais, por fatores não simulados.
- Não tocam a hipótese H1 do pré-registro nem o par de chamados A e B.

Generated by Claude
