# Validação de desenvolvimento do receptor v3 (não confirmatória)

**Data:** 31/10/2026 · **Execução:** GitHub Actions 41188079573, disparo manual · **Código:** commit `d90f986` · **Critérios aplicados:** 0.4.0 (rascunho, não congelado) · **Matriz:** desenvolvimento, semente 20261031, deslocamento de ruído 500.000.000, SHA-256 `81fc0e6b…` (arquivo `matrix_dev.json`, idêntico nos dois modos) · **Estado:** NÃO DEFINITIVO

Esta rodada serve para descobrir falhas da v3 antes do congelamento (`lab/bench/RECEIVER_V3.md`). Ela **não** sustenta nenhuma declaração de maturidade. A matriz é disjunta da matriz v0.3.0 e da futura matriz confirmatória v0.4, que terá deslocamento de ruído ≥ 1.000.000.000.

## Agregação

- `aggregate.json`: agregador atual (`c462408`) aplicado a estes artefatos: **NÃO DEFINITIVO**, sem problemas de consistência.
- `aggregate_ci_d90f986.json`: saída do agregador no próprio workflow, no commit `d90f986`. Ele devolvia INCONSISTENT_RUNS para rodadas de desenvolvimento por causa do arquivo de matriz e da ausência de congelamento. Esse comportamento foi corrigido depois, por recomendação da Luna. Os vereditos por ensaio são os mesmos nas duas saídas.

## Vereditos por ensaio (critérios 0.4.0 aplicados a esta matriz)

| Ensaio | hf | lf |
|---|---|---|
| B1 | aprovado | aprovado |
| B2 | aprovado | aprovado |
| B3 | aprovado | aprovado |
| B4 | aprovado | aprovado |
| B5 | aprovado | aprovado |
| B7 | aprovado | aprovado |

## Riscos da v3 testados (RECEIVER_V3.md)

1. **Canal verdadeiro rejeitado pela regra de dominância de −10 dB:** **errata de 31/10/2026, ver `lab/bench/ERRATA_v0.4.md`.** A versão anterior deste item dizia "nenhuma rejeição em toda a grade de SNR", e isso estava errado. As taxas de rejeição variaram de 0 a 1,7%, conforme a condição, nos níveis de SNR (razão sinal-ruído) abaixo de 16 dB: nesse regime, o maior pico do espectro costuma ser ruído, e o canal fica mais de 10 dB abaixo dele. A partir de 16 dB não houve nenhuma rejeição. A conferência original olhou só 16 dB, 18 dB e o máximo a partir de 20 dB; a grade inteira não foi examinada. As falhas a 16 e 18 dB são todas identificações incorretas.
2. **Pares de pior caso (`f0/240` de separação):** recuperação de 99,2% a 99,5% a 16 dB e de 99,9% a 100% a 18 dB; 100% a partir de 20 dB.
3. **Modo com piloto (B4):** 100% de recuperação em `k1` e `k2`, nos cinco desvios de escala e nos dois modos.
4. **Tons entre canais (B7b):** 158 de 158 rejeitados nos dois modos. Falsos alarmes (B7a): limite superior de Clopper–Pearson a 95% de 0,64% (hf) e 0,60% (lf).

## Perto do limiar, com um canal

| | Identificações incorretas a 16 dB | a 18 dB | RMS/ACRB a 16 dB | RMS condicional/ACRB a 16 dB | a 20 dB | a 30 dB |
|---|---|---|---|---|---|---|
| hf | 5 em 1.000 | 0 | 2.088 | 1,06 | 1,04 | 1,03 |
| lf | 0 em 1.000 | 0 | 1,06 | 1,06 | 1,03 | 1,02 |

O RMS condicional é calculado só entre os ensaios com identificação correta e canal aceito.

- A referência idealizada (`ideal_pe.py`, `M = 159`, canais ortogonais) prevê cerca de 2,3 erros em 1.000 a 16 dB. Os 5 erros em hf e 0 em lf são da mesma ordem. Os canais de `H_16` não são perfeitamente ortogonais, e por isso a referência serve de comparação, não de limite.
- Como na v1, uma única identificação incorreta a 16 dB leva o RMS global a milhares de vezes a ACRB (limite de Cramér–Rao assintótico). É por isso que o B3(c) da v0.4 vale a partir de 20 dB.
- Sem erros de identificação, o erro de frequência fica entre 1,02 e 1,06 vez o limite teórico.

## Comparação com as versões anteriores (matrizes diferentes; só indicativa)

| Erros de identificação a 16 dB, 1 canal | hf | lf |
|---|---|---|
| v1 (matriz v0.3.0) | 3 | 4 |
| v2 (matriz v0.3.0) | 59 | 49 |
| v3 (matriz de desenvolvimento) | 5 | 0 |

A v3 recupera a seleção de canal da v1 com pouco sinal e mantém os acertos da v2 em B4 e B7b.

## Tempo de execução

O job hf levou 5 h 04 min, perto do limite de 340 min do GitHub Actions; o lf, 4 h 42 min. A rodada confirmatória será dividida em jobs paralelos por ensaio e por condição do B3, com uma etapa de junção verificada antes do agregador. Essa mudança não altera ensaios, limiares nem receptor, e será revisada antes do congelamento.

## Conclusão de desenvolvimento

Nenhuma falha encontrada nos riscos registrados. Não há motivo de engenharia para alterar a v3 antes do congelamento.

Esta conclusão não é um resultado de maturidade. A avaliação confirmatória depende do congelamento da v0.4 com matriz e sementes novas e da agregação da execução definitiva.
