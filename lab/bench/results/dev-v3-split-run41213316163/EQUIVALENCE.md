# Equivalência entre a rodada inteira e a rodada dividida (desenvolvimento, não confirmatória)

**Data:** 31/10/2026

| | Rodada inteira | Rodada dividida |
|---|---|---|
| Execução | 41188079573 | 41213316163 |
| Commit | `d90f986` | `c08f8d6` |
| Estrutura | um job por modo | seis partes paralelas por modo, juntadas por `merge_parts.py` |
| Job mais longo | 5 h 04 min (hf) | 1 h 12 min (lf, condição k3 do B3) |
| Matriz | `matrix_dev.json`, semente 20261031, deslocamento 500.000.000 | idêntica, byte a byte |

**Comparação:** para cada modo (hf e lf) e cada ensaio (B1, B2, B3, B4, B5 e B7), o conteúdo do artefato é **idêntico**. A comparação exclui só o bloco de configuração (`env`), a data e os campos de junção (`conditions`, `merged_from`). Isso inclui os erros de frequência de cada ensaio, as taxas por SNR (razão sinal-ruído) e as métricas diagnósticas.

No bloco de configuração, a única diferença é o commit. A data saiu do bloco a partir de `c08f8d6`.

**Agregador:** NÃO DEFINITIVO nas duas rodadas, como deve ser numa rodada de desenvolvimento.

**Verificação automatizada:** `python lab/bench/compare_runs.py lab/bench/results/dev-v3-run41188079573 lab/bench/results/dev-v3-split-run41213316163` → "idênticos após normalização (12 de 12)". O teste `test_dev_runs_split_and_unsplit_are_equivalent` repete essa comparação na CI. Os arquivos JSON não são idênticos byte a byte, por causa dos metadados citados; os resultados científicos são.

**Conclusão:** a divisão em partes não altera nenhum resultado. Ela muda só o tempo de execução e acrescenta a verificação da junção.

Depois desta rodada, o `bench.yml` passou a fixar as actions por SHA, a mesma prática do `pages.yml`. Essa mudança não afeta o código da bancada.
