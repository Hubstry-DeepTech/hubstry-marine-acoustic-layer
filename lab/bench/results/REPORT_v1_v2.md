# Relatório comparativo dos receptores v1 e v2 sob os critérios v0.3.1

**Data:** 31/10/2026 · **Critérios:** `lab/BENCH_CRITERIA.md` v0.3.1 (congelados) · **Matriz:** v0.3.0 · 1.000 ensaios por condição

| Execução | Receptor | Commit | Diretório |
|---|---|---|---|
| 41120505952 | v1 | `4ba2c05` | `v1-run41120505952/` |
| 41131667005 | v2 (com dados por ensaio) | `a691855` | `v2-run41131667005/` |

A execução 41121711705 (v2, `972beb6`, em `v2-run41121711705/`) é anterior à de número 41131667005 e deu o mesmo veredito.

## 1. Veredito por ensaio e modo

| Ensaio | v1 hf | v1 lf | v2 hf | v2 lf |
|---|---|---|---|---|
| B1 | aprovado | aprovado | aprovado | aprovado |
| B2 | aprovado | aprovado | aprovado | aprovado |
| B3 | **reprovado** (c) | **reprovado** (c) | **reprovado** (c) | **reprovado** (c) |
| B4 | **reprovado** | **reprovado** | aprovado | aprovado |
| B5 | aprovado | aprovado | aprovado | aprovado |
| B7 | **reprovado** (b) | **reprovado** (b) | aprovado | aprovado |

**Regra agregada da v0.3.1:** TRL 3 (nível de maturidade tecnológica 3) para os dois receptores.
- **v2:** `aggregate.py` aplicado sobre os dois modos devolve "TRL 3: B3/hf, B3/lf".
- **v1:** o agregador devolve `INCONSISTENT_RUNS` só porque a execução da v1 é anterior à gravação do campo `receiver` nos metadados. O commit e a versão de critérios e matriz coincidem entre os modos. O veredito por modo, registrado em cada `summary.json`, é TRL 3.

## 2. B3: onde está a falha

Os critérios (a) e (b) passam em todas as condições, nos dois receptores e nos dois modos. Falha só o critério (c): com um canal (`K = 1`), erro RMS (raiz do erro quadrático médio) ≤ 1,5·ACRB (limite de Cramér–Rao assintótico) a partir de 16 dB.

| `K = 1` | Recuperação a 16 dB | Erros a 16 dB | RMS/ACRB a 16 dB | RMS/ACRB a 18 dB | RMS/ACRB a 20 dB | RMS/ACRB a 30 dB |
|---|---|---|---|---|---|---|
| v1 hf | 0,997 | 3 | 2.159 | 1,03 | 1,02 | 1,002 |
| v1 lf | 0,996 | 4 | 1.172 | 1,03 | 1,02 | 1,008 |
| v2 hf | 0,941 | 59 | 34.347 | 1,03 | 1,02 | 1,002 |
| v2 lf | 0,951 | 49 | 27.956 | 5.271 (2 erros) | 1,02 | 1,008 |

**Leitura:**
- Sem erros de canal, os dois receptores operam no limite teórico: o RMS/ACRB fica entre 1,00 e 1,03.
- Um único canal trocado em 1.000 ensaios leva o RMS a milhares de vezes a ACRB. O critério (c) mede, de fato, a taxa de troca de canal, e não a eficiência da estimativa.
- A v1 erra perto da referência idealizada de detecção M-ária, que prevê cerca de 2 erros em 1.000 a 16 dB. A v2 erra de 12 a 20 vezes mais na mesma faixa. A busca de picos na grade fina, sem a seleção nas 159 candidatas, perde desempenho em SNR (razão sinal-ruído) baixa.
- A taxa no hold-out da v2 (ensaios a partir do índice 20) acompanha a taxa integral, por exemplo 0,943 contra 0,941 em `k1`/hf a 16 dB. Não há sinal de sobreajuste aos ensaios de desenvolvimento.
- Nenhuma falha da v2 ocorre a partir de 20 dB (`failures_snr_ge20` vazio em todas as condições).

## 3. B4 e B7: o que a v2 corrigiu

| | v1 hf | v1 lf | v2 hf | v2 lf |
|---|---|---|---|---|
| B4, recuperação mínima, `k1` | 0,958 | 0,964 | 1,000 | 1,000 |
| B4, recuperação mínima, `k2` | 0,919 | 0,929 | 1,000 | 1,000 |
| B7b, pontos médios rejeitados (de 158) | 0 | 0 | 158 | 158 |
| B7a, limite superior Clopper–Pearson 95% (avaliação) | 0,58% | 0,70% | 0,58% | 0,70% |

O B7a é idêntico nos dois receptores porque o teste de detecção não usa o decodificador.

## 4. Consequências para a v0.4

1. Os pontos fortes são complementares:
   - a v1 seleciona o canal certo em SNR baixa, porém falha em B4 e em B7b;
   - a v2 resolve B4 e B7b, porém troca mais canais a 16 dB.
2. Essa combinação motiva o receptor v3, escolhido para a v0.4. A v3 faz a seleção da v1, rejeita picos mais de 10 dB abaixo do maior e usa o estimador de mínimos quadrados da v2 no modo com piloto.
3. Os dados confirmam o diagnóstico do rascunho v0.4: a 20 dB ou mais, os dois receptores passam no critério (c) nesta matriz. A aprovação, porém, só vale numa execução com matriz e sementes novas, com o receptor v3 congelado antes.
