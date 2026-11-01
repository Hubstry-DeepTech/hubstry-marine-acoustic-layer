# lab/sim_mca001 — simulações sintéticas da ficha MCA-001

Implementa o plano `lab/analogias/SIM-MCA-001_plano_simulacoes.md`. Rótulo de todos os
resultados: `EXPLORATORY/FEASIBILITY`. Nenhum dado real é lido por este código.

| Arquivo | Conteúdo |
|---|---|
| `seeds.py` | Sementes determinísticas por bloco, cenário, partição (`cal` ou `ver`) e réplica |
| `generator.py` | Gerador G1 a G4, ruído com convenção `SNR_integrated`, interferências e cadeia de decimação |
| `detection.py` | Detecção de componentes por STFT, sem hipótese sobre a fundamental |
| `fundamental.py` | Estimadores independentes de `f̂₀`: YIN e cepstro, com pré-filtro passa-faixa |
| `assignment.py` | Mínimos quadrados generalizados, busca de atribuições e conjunto `H*` |
| `stats.py` | Valor-p empírico, Clopper–Pearson e dimensionamento do critério de aceite |
| `block1.py` | Bloco 1: detecção, incerteza e estimador da fundamental |
| `results/` | Saídas JSON e relatórios |

Testes automáticos: `pytest tests/test_sim_mca001.py`.

Piloto do Bloco 1 (cerca de 15 minutos com dois núcleos):

```bash
python -m lab.sim_mca001.block1 --reps 6 --workers 2 --out lab/sim_mca001/results/block1_piloto.json
```
