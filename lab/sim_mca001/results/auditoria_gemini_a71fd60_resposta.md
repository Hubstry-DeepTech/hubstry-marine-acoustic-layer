# Resposta à auditoria independente do commit `a71fd60`

**Data:** 01/11/2026 · **Auditor:** Gemini 4 Argon (High), pelo Antigravity CLI, em cópia descartável do repositório, com `--sandbox` · **Triagem e correções:** Claude · **Rótulo:** `EXPLORATORY/FEASIBILITY`

A Luna decidiu corrigir primeiro os três bloqueios P0, depois a calibração da incerteza, e só então rodar a validação com sementes inéditas. Nada foi congelado.

## Triagem

| # | Achado | Gravidade | Situação |
|---|---|---|---|
| 1 | A porta de pareamento coincidia com o orçamento de precisão `1/T`: o critério de precisão ficava automaticamente verdadeiro e os quantis saíam truncados | Bloqueante | Corrigido |
| 2 | Picos absorvidos por componentes não resolvidos sem pareamento um-a-um, com possível dupla contagem; detecção calculada só sobre os resolvidos | Bloqueante | Corrigido |
| 3 | Resumo de detecção misturava `cal` e `ver`; a partição `ver` já orientou escolhas | Bloqueante | Corrigido; criada a partição `val` |
| 4 | Sob modulação, o erro não é constante em Hz; identificabilidade ignora `f₀` e inclinação; escalas de quantil e de variância em `Σ` não estão alinhadas | Importante | Pendente para 03/11 (recalibração da incerteza), conforme a Luna |
| 5 | Folga numérica da busca exata em casos quase harmônicos com `Σ` muito mal condicionada | Importante | Corrigido |
| 6 | Interpolação do YIN nas bordas da faixa; corte de frequência do gerador G2 | Menor | Corrigido |
| 7 | Lacunas de testes | Importante | Seis testes propostos, adaptados e incorporados, mais dois |

## Correções

**1 e 2. Pareamento e contabilidade (`detection.match_truth`).**
- **Porta de associação:** `max(2/T, |df/dt|·T/2, df_STFT/2)`. O termo `2/T` é a meia largura do lóbulo principal da janela de Hann. Ele tem justificativa própria e é o dobro do orçamento de precisão `1/T`, que agora é medido sobre os pares sem coincidir com a porta.
- **Associação única:** todos os componentes entram numa só associação um-a-um. Um componente não resolvido absorve no máximo um pico, e a porta dele fica limitada a 45% da separação ao vizinho.
- **Identidades garantidas e testadas:**
  - `registros + perdidos + não resolvidos = componentes`;
  - `registros + picos absorvidos + falsos = picos detectados`.
- **Controle com ruído puro:** cada sinal ganha uma realização de ruído puro, com a mesma escala e semente própria, pareada contra a mesma verdade. A taxa de associação acidental passa a ser reportada.
- **Taxas lado a lado:** a detecção é reportada sobre o total de componentes e sobre os resolvidos, junto com a fração de não resolvidos.

**3. Partições (`seeds.py`, `block1.py`).**
- O resumo de detecção é separado por partição.
- Foi criada a partição `val`, para a validação final com sementes inéditas. O runner só a executa com `--particoes val`, depois de congeladas as regras. Um teste verifica que ela não roda por padrão.
- Outro teste verifica que nada escolhido em `cal` muda quando a partição `ver` muda.

**5. Busca exata (`assignment.py`).**
- A folga da poda ganhou um termo absoluto proporcional ao erro da fatoração: `K²·‖UᵀDU − M‖·(max|y| + ln N)²`.
- Os valores finais de `χ²` passaram a ser calculados por branqueamento de Cholesky com projeção explícita (`chi2_whitened`), sem formar `Σ⁻¹`. A referência exaustiva de `verify_d1.py` usa o mesmo cálculo.
- No caso extremo apontado pelo Gemini (quase harmônico, número de condição de `Σ` de 10⁷ a 10⁹), a diferença de `χ²` entre a busca e a referência caiu de cerca de 10⁻⁵ para 10⁻¹⁰ relativo. O conjunto `H*` ficou idêntico nos 30 casos.
- `verify_d1.py` foi refeito com o código novo: 3.000/3.000 casos gerais, 500/500 mal condicionados e 21/21 na escala operacional, com mínimo e `H*` iguais à busca exaustiva.

**6.** O YIN só interpola num mínimo local estrito no interior da faixa, com deslocamento limitado a meia amostra. O gerador G2 respeita `f_gen_max`.

**7.** A suíte do repositório passa com 164 testes.

## Primeiro sinal do controle com ruído puro (verificação rápida, não é resultado)

Seis sinais da partição `cal`, perfil decrescente, `f₀ = 12 Hz`, janela de 1 s:

| Limiar de detecção | Associação acidental com ruído puro | Falsos picos por quadro (20 dB) |
|---|---|---|
| 6 dB | 20% a 22% | 7,1 |
| 10 dB | cerca de 1% | 0,26 |
| 15 dB | 0% | 0 |

Com limiar de 6 dB, cerca de um em cada cinco componentes receberia um pico de ruído dentro da porta mesmo sem sinal. O controle oferece um critério independente para descartar limiares baixos. A amostra é mínima e serve só para mostrar que o controle funciona.

## O que continua pendente

- Recalibração da incerteza em função da excursão de frequência na janela, e alinhamento das escalas de quantil e de `Σ` (achado 4), prevista para 03/11.
- Teto de erro e disponibilidade mínima do YIN, por decisão da Luna.
- Rodada de validação na partição `val`, prevista para 04/11.

## Revisão da Luna sobre `434ca29` e ajustes

A Luna considerou o P0-2 corrigido e o P0-1 corrigido em grande parte. Apontou que o P0-3 continuava pendente e pediu ajustes numéricos na D1. Todos foram aplicados.

- **Interpretação condicional dos quantis (P0-1).** Os quantis e a cobertura são condicionais aos componentes pareados e resolvidos dentro da porta. Não descrevem o erro irrestrito de todos os componentes. A porta `2/T` vai até o primeiro zero do lóbulo principal da Hann e não exclui a energia dos lóbulos laterais. Isso consta do `criterio_pareamento` do runner e do resultado da validação congelada.
- **Partição `val` (P0-3).** Antes, `summarize()` só usava `cal` e `ver`, e uma execução com `val` não validaria nada. Agora há três peças:
  - **Congelamento:** `congelar_b1.py` gera `block1_freeze.json` a partir de uma rodada exploratória. O arquivo registra a janela, o limiar de detecção, a tabela de incerteza e a SNR mínima de `cal`, o limiar do YIN de `cal`, a regra de pareamento e quem decidiu, com SHA-256.
  - **Avaliação congelada:** `evaluate_frozen()` aplica o congelamento só a sinais de `val`, sem recalibrar. Recusa mistura com `cal` ou `ver` e recusa congelamento adulterado.
  - **Proteção no runner:** com `val`, o runner exige `--congelamento` e roda `val` sozinha.
  - **Teste:** `test_val_partition_evaluates_frozen_rules_without_refitting`.
- **Controle com ruído puro.** O resumo traz intervalo de confiança bootstrap por sinal e o número de sinais. Um teste novo cobre as contagens e a agregação. Os números de 20%, 1% e 0% continuam exploratórios.
- **D1 numérica.**
  - `_residual_form()` passou a formar `M` por Cholesky, `Wᵀ(I − aaᵀ/aᵀa)W`, sem inverter `Σ`.
  - `search()` devolve o mesmo `χ²` que decidiu `H*`, verificado por teste.
  - `verify_d1.py`, refeito com o código novo: ver `verify_d1.json`. A afirmação de completude fica restrita ao domínio e às tolerâncias documentadas.
- **CI.**
  - O commit `434ca29` tem execução registrada: testes em Python 3.11, 3.12 e 3.13 e CodeQL, todos com sucesso.
  - O `ci.yml` passou a medir também a cobertura de `lab/sim_mca001`. O `ci.yml` não está protegido pelo `FREEZE_v0.4.json`.

Generated by Claude
