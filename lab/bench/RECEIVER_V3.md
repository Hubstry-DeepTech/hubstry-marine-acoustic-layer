# Receptor v3 da bancada digital HMAL

**Data:** 31/10/2026 · **Critérios a que se destina:** v0.4 (`lab/BENCH_CRITERIA_v0.4-draft.md`), ainda não congelados · **Código:** `ReceiverV3` em `lab/bench/receiver.py`

## Por que existe uma v3

Os resultados definitivos sob a v0.3.1 (`lab/bench/results/REPORT_v1_v2.md`) mostraram pontos fortes complementares:

| | v1 | v2 |
|---|---|---|
| Seleção do canal com pouco sinal (16 dB, `K = 1`) | 3 a 4 erros em 1.000 | 49 a 59 erros em 1.000 |
| B4, desvio de escala com piloto | reprovado | aprovado |
| B7b, tons entre canais | 0 de 158 rejeitados | 158 de 158 |

A v3 combina a seleção da v1, um teste de dominância espectral para rejeitar tons fora do dicionário e o modo com piloto da v2.

## Algoritmo

**Sem piloto:**
1. Potência nas 159 candidatas de `H_16`, como na v1. Escolhem-se as `K` maiores.
2. Refinamento de cada uma com máximo global numa grade de passo `1/(8T)` dentro de ±`1/T`, seguido do método de Brent em torno do melhor ponto. A v1 usava só Brent em ±`1/T` e podia convergir para um lóbulo lateral.
3. Associação ao elemento mais próximo de `H_16` e tolerância `1/(2T)`, como na v1.
4. **Teste de dominância:** o canal é rejeitado (`accepted = false`) quando a potência no ponto refinado fica mais de 10 dB abaixo do maior pico do espectro, calculado por FFT com preenchimento até `8·N`.
   - O primeiro lóbulo lateral da janela retangular fica a −13,3 dB. Num tom fora de `H_16`, o refinamento a partir da candidata vizinha cai num lóbulo lateral e é rejeitado.
   - O valor de −10 dB foi fixado pela geometria da janela, antes de qualquer execução sobre matriz de avaliação.

**Com piloto:** idêntico à v2 (`lab/bench/RECEIVER_V2.md`): picos na grade fina, piloto a até 0,2% de `f0`, razões provisórias e `f0` por mínimos quadrados.

**Detecção (B7a):** não usa o decodificador e é idêntica nas três versões.

## Riscos registrados

1. **Canal verdadeiro fraco em sinais com vários tons.** O teste compara cada canal com o maior pico global. Se os tons tivessem amplitudes diferentes, um canal verdadeiro poderia ficar mais de 10 dB abaixo do maior e ser rejeitado. Nas matrizes da bancada, os tons têm amplitudes iguais. O risco existe em uso real e fica fora do escopo da v0.4.
2. **Interferência entre tons próximos** (pares de pior caso, separação de `f0/240`). A soma de dois tons pode criar um pico global acima de cada um. Com amplitudes iguais, a diferença esperada fica longe de 10 dB, mas isso precisa ser verificado na matriz inteira.
3. **Modo com piloto herdado da v2.** Mantém os riscos registrados para a v2: mais de um pico na faixa do piloto e razão provisória errada que contamina `f0`.
4. **Desempenho da v2 perto do limiar não afeta a v3 sem piloto**, mas afeta o modo com piloto. Em B4 (20 dB) isso não apareceu nos 2.000 ensaios por modo da v0.3.1.

## Transparência sobre o desenvolvimento

- A v3 foi desenhada **depois** de ver os resultados da v1 e da v2 na matriz v0.3.0. Por isso, não será avaliada nessa matriz para fins de aprovação.
- Testes de desenvolvimento já feitos: sementes de ruído a partir de 91.000.000 e 92.000.000, fora de qualquer matriz de avaliação, só `K = 1` e B7b.
- **Validação de desenvolvimento completa, antes do congelamento:** todos os ensaios (B1 a B5 e B7, 1.000 ensaios por condição), numa matriz gerada com semente de desenvolvimento declarada e ruído deslocado em 500.000.000, disjunta da matriz v0.3.0 e da futura matriz v0.4. O objetivo é testar os riscos 1 a 3 antes de congelar o receptor, não aprovar nada. Se a validação revelar falha, a correção será feita e registrada aqui antes do congelamento.
- Nenhum parâmetro numérico da v3 será ajustado depois do commit de congelamento.
