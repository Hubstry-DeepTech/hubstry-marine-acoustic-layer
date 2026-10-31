# Receptor v2 da bancada digital HMAL

**Data:** 30/10/2026 · **Critérios aplicados:** `lab/BENCH_CRITERIA.md` v0.3.1, **sem alteração** de ensaios, limiares, matriz ou sementes

## Por que existe uma v2

O receptor é o sistema sob teste. Os critérios de aprovação continuam congelados. O teste de fumaça da v1 (6 ensaios por condição, sem valor definitivo) indicou dois modos de falha. A v1 também foi submetida à execução definitiva, e seu resultado entra no relatório junto com o da v2.

| Falha observada na v1 | Causa | Correção na v2 |
|---|---|---|
| B4: canais de razão alta perdidos com desvio de escala | O erro de estimativa do piloto `1/1` é multiplicado pela razão `r` do canal: 0,1 bin no piloto vira cerca de 1,5 bin em `15/1` | `f0` final estimado por mínimos quadrados com o piloto e todos os canais decodificados; os canais de razão alta passam a dar a maior precisão |
| B7b: tons entre dois canais aceitos como canais | A seleção avalia só as frequências candidatas, e o refinamento local converge para um lóbulo lateral perto da candidata | Os picos do espectro são localizados **antes** da associação ao dicionário; um tom fora de `H_16` gera um pico fora da tolerância |

## Algoritmo

1. **Espectro em grade fina:** `P(f) = |X(f)|²/N` com janela retangular, calculado pela FFT com preenchimento de zeros até `8·N` pontos (passo `1/(8T)`).
2. **Picos:** escolher os `K` maiores máximos locais (`K + 1` no modo com piloto).
3. **Refinamento:** maximizar `P(f)` pelo método de Brent em ±`1/(8T)` em torno de cada pico da grade.
4. **Sem piloto:** associar cada frequência ao elemento mais próximo de `H_16` (com `f0` nominal) e aceitar quando `|f_est − r·f0| ≤ 1/(2T)`.
5. **Com piloto:**
   - o pico a até 0,2% de `f0` é o piloto;
   - os demais recebem razões provisórias pelo elemento de `H_16 \ {1/1}` mais próximo de `f/f_piloto`;
   - `f0_LS = (f_piloto + Σ r_i·f_i) / (1 + Σ r_i²)`, a solução de mínimos quadrados de `f_i = r_i·f0`;
   - associação final e tolerância com `f0_LS`, com o piloto excluído do dicionário de dados.

A v1 e a v2 são **algoritmos diferentes**, avaliados pelos mesmos critérios de aceite; a v2 não é outra implementação da especificação da v1.

O teste de detecção B7a não usa o decodificador. Ele continua idêntico ao da v1: estatística nas 159 candidatas, `σ̂²` pela mediana e limiar `γ ≈ 10,365`.

## Transparência sobre o desenvolvimento

As verificações de desenvolvimento da v2 usaram, em cada modo:
- B4: ensaios de índice 0 a 29 de `k1` e de `k2` (sementes `noise_seed` correspondentes em `matrix.json`), com SNR integrado de 20 dB e os cinco valores de ε;
- B3: ensaios de índice 0 a 19 de `k1`, `k2`, `k3` e de cada par de pior caso, com SNR integrado de 20, 24 e 30 dB (pares de pior caso: 20 e 30 dB);
- B7b: os 158 pontos médios.

O relatório apresenta, além do resultado integral, a taxa de recuperação só nos ensaios **não usados no desenvolvimento** (B3 a partir do índice 20; B4 a partir do índice 30). O B7b não tem conjunto independente: seu resultado vale como teste de regressão, não como validação cega. As mudanças são estruturais (ordem das etapas e estimador de escala), e nenhum parâmetro numérico foi ajustado a esses resultados. O passo de grade `1/(8T)` e a faixa de ±0,2% do piloto já constavam da v1. Ainda assim, essa sobreposição fica registrada. Numa próxima iteração, o desenvolvimento deve usar sementes fora da matriz.

## Interface efetiva e decisões registradas após a auditoria do GLM-5.3 (30/10/2026)

- **Interface efetiva:** `Receiver(fs, duration, f0)` / `ReceiverV2(fs, duration, f0)` e o método `decode(x, K, pilot=False) -> dict`, com `channels` = lista de `{f_est, ratio: [a, b] | None, accepted}`, além de `f0_used` (e `f0_pilot` na v2). Difere da forma resumida da Seção 2 dos critérios: `fs`, `f0` e a duração `T` (necessária para a tolerância `1/(2T)`) vão no construtor, e "fora da tolerância" corresponde a `accepted = false`. A semântica é a mesma.
- **Decisão de aprovação:** segue os critérios congelados, sobre os 1.000 ensaios de cada condição. A taxa no hold-out (B3 a partir do índice 20; B4 a partir do 30) é reportada ao lado e não altera a decisão. Uma divergência entre as duas taxas será apontada no relatório.
- **Riscos registrados fora das condições congeladas:** se houver mais de um pico na faixa de ±0,2%, o piloto é o mais próximo de `f0` nominal (no modo AF, um lóbulo lateral do piloto cabe nessa faixa; nos ensaios B4, com amplitudes iguais e 20 dB, ele não entra entre os `K+1` maiores picos); a busca de picos ignora os bins de DC e Nyquist; uma razão provisória errada contamina `f0_LS` e pode derrubar todos os canais do ensaio.
