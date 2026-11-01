# lab/sim_mca001 — simulações sintéticas da ficha MCA-001

Implementa o plano SIM-MCA-001. Todos os resultados têm rótulo
EXPLORATORY/FEASIBILITY. Nenhum dado real é lido por este código.

| Arquivo | Conteúdo |
|---|---|
| seeds.py | Sementes determinísticas por bloco, cenário, partição cal/ver e réplica |
| generator.py | Gerador G1 a G4, ruído com convenção SNR_integrated, interferências e decimação |
| detection.py | STFT, detecção sem hipótese sobre a fundamental e pareamento sintético um-a-um |
| fundamental.py | Estimadores independentes de f0: YIN e cepstro |
| assignment.py | Mínimos quadrados generalizados, busca de atribuições e conjunto H* |
| stats.py | Valor-p empírico, Clopper–Pearson e dimensionamento do critério de aceite |
| block1.py | Bloco 1: detecção, incerteza empírica e estimador da fundamental |
| results/ | Saídas JSON e relatórios |

## Revisões do runner do Bloco 1

- Picos falsos são contabilizados separadamente de erros de localização.
- O pareamento é global e um-a-um; a tolerância depende da resolução STFT e da excursão de frequência na janela, não do espaçamento harmônico.
- Componentes sem separação suficiente são marcados como não resolvidos, sem serem forçados a falsos positivos.
- A incerteza usa quantis empíricos centrais de 95% por SNR local e modulação, em Hz e em ln(f), sem hipótese gaussiana; nenhum fator 3,92 converte largura de intervalo em desvio-padrão.
- A identificabilidade é um diagnóstico separado, por comparação da separação logarítmica entre ordens com duas vezes o raio empírico q95 em ln(f).
- O limiar mínimo de SNR é escolhido exclusivamente na partição cal e verificado na partição ver.
- YIN best é o candidato; o limiar é selecionado em cal. YIN first permanece somente como comparador.
- A covariância cruzada é estimada em cal por produtos entre resíduos log-f de componentes pareados no mesmo quadro; a estrutura comum é tratada como candidata e verificada em ver.
- A saída sub-harmônica do cenário ambíguo é identificada como não identificável, não como erro.
- O limite de identificabilidade é reportado separadamente da detectabilidade; a detecção informa quais componentes entram em C(t) e E(t), não redefine o teto estrutural N(t).

Testes automáticos:

```bash
pytest tests/test_sim_mca001.py
```

Piloto:

```bash
python -m lab.sim_mca001.block1 --reps 6 --workers 2 --out lab/sim_mca001/results/block1_piloto_v2.json
```
