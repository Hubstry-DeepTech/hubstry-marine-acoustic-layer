# Rodada confirmatória da v0.4: resultado

**Data:** 31/10/2026 · **Execução:** GitHub Actions 41231673988, disparada pelo push do commit de congelamento `a2361a5` · **Critérios:** `lab/BENCH_CRITERIA_v0.4.md` (0.4.0, congelados) · **Receptor:** v3 · **Matriz:** `matrix_v04.json`, semente 1538468226, deslocamento de ruído 4.440.967.960, SHA-256 `f1174c3d…` · **Ambiente:** Python 3.11.17, NumPy 2.4.6, SciPy 1.17.1, glibc 2.43

## Veredito do agregador

> **TRL 4 (autoavaliação) do subsistema computacional sob os critérios 0.4.0: B1-B5 e B7 aprovados nos modos hf e lf.**

- Agregação no próprio workflow (`aggregate.json`) e repetida localmente no commit `a2361a5`: mesmo veredito, lista de problemas vazia.
- `freeze.py verify`: "congelamento íntegro". O bloco de configuração dos dois modos registra o mesmo commit, receptor, critérios, matriz (arquivo, SHA-256, semente e deslocamento) e ambiente congelados, com execução definitiva.
- Cada modo foi executado em seis partes paralelas e juntado por `merge_parts.py`.

**Alcance:** autoavaliação do subsistema computacional na bancada digital sintética, sob critérios congelados e matriz nova. **Não** demonstra comunicação acústica submarina em operação, cadeia física ou validação biológica da hipótese H1, e não é um TRL do HMAL como um todo. O TRL 3 sob a v0.3.1 (`REPORT_v1_v2.md`) continua registrado.

## Vereditos por ensaio

| Ensaio | hf | lf |
|---|---|---|
| B1 dicionário | aprovado | aprovado |
| B2 precisão sem ruído | aprovado | aprovado |
| B3 recuperação com ruído | aprovado | aprovado |
| B4 desvio de escala com piloto | aprovado | aprovado |
| B5 periodicidade | aprovado | aprovado |
| B7 falsos alarmes e tons entre canais | aprovado | aprovado |

## Números principais

| | hf | lf |
|---|---|---|
| B2, maior erro com 1 tom / limite | 0,0028 / 0,02 Hz | 0,00019 / 0,0005 Hz |
| B2, maior erro com 2 e 3 tons / limite | 0,023 / 0,1 Hz | 0,00071 / 0,0025 Hz |
| B3, recuperação a partir de 20 dB, todas as condições | 100% | 100% |
| B3(c), RMS/ACRB máximo a partir de 20 dB (limite 1,5) | 1,032 | 1,014 |
| B3, identificações incorretas a 16 dB, 1 canal | 4 em 1.000 | 2 em 1.000 |
| B3, identificações incorretas a 16 dB, 2 e 3 canais e pares mais próximos | de 2 a 8 em 1.000 | de 4 a 5 em 1.000 |
| B4, menor recuperação (`k1`, `k2`, cinco desvios) | 100% | 100% |
| B5, maior diferença relativa (limite 10⁻⁹) | 3,3 × 10⁻¹² | 3,5 × 10⁻¹² |
| B7a, falsos alarmes em 10.000 / limite superior a 95% (limite 1%) | 45 / 0,58% | 42 / 0,54% |
| B7b, tons entre canais rejeitados | 158 de 158 | 158 de 158 |

## Abaixo do corte de 20 dB (diagnóstico, sem efeito na decisão)

- A 16 dB com 1 canal, as identificações incorretas (4 e 2 em 1.000) são da mesma ordem da referência idealizada (cerca de 2,3 em 1.000, `ideal_pe.py`). Uma única troca de canal leva o RMS global a cerca de mil vezes a ACRB (limite de Cramér–Rao assintótico). Esse é o motivo do corte de 20 dB, decidido e documentado antes desta rodada.
- Rejeições de canal verdadeiro pela regra de −10 dB: de 0 a 15 por mil abaixo de 16 dB; 1 em 1.000 a 16 dB (lf, par 14/15 e 15/16); nenhuma a partir de 18 dB. Ver `lab/bench/ERRATA_v0.4.md`.
- Sem troca de canal, o erro de frequência fica entre 1,005 e 1,04 vez o limite teórico, de 18 a 30 dB.

## Limitações registradas

- Sinais sintéticos com tons de amplitudes iguais; o risco da regra de dominância com amplitudes desiguais continua em aberto (`RECEIVER_V3.md`).
- Ruído branco gaussiano, sem canal acústico real, multipercurso ou efeito Doppler.
- A v3 foi desenhada depois de ver os resultados da v0.3.1. Isso foi compensado com matriz e sementes novas, sorteadas só depois do congelamento do receptor e dos critérios.
