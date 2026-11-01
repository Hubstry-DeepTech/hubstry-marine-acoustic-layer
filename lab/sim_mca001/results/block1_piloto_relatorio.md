# Bloco 1 — relatório do piloto

**Plano:** SIM-MCA-001 v0.2 · **Data:** 01/11/2026 · **Rótulo:** `EXPLORATORY/FEASIBILITY` · **Tipo:** piloto. Nenhum parâmetro foi escolhido neste piloto. Nenhum dado real foi aberto.

**Arquivo de resultados:** `block1_piloto.json` (SHA-256 `e5387e567eef78c58df91216acb704f6071d622de37a769a35335af9e71b39a2`), gerado por `python -m lab.sim_mca001.block1 --reps 6 --workers 2`, em 693 s, com Python 3.13, NumPy 2.5.3 e SciPy 1.18.1.

## 1. O que foi executado

- **1.920 sinais sintéticos** de 10 s a 2 kHz. A grade tem 160 células: quatro perfis de amplitude, fundamental inicial de 12 ou 18 Hz, inclinação de 0 ou −0,05 oitava/s, SNR integrada de −5 a 20 dB, e ruído branco ou `1/f`. Cada célula tem 6 réplicas na partição de calibração (`cal`) e 6 na de verificação (`ver`).
- **Detecção** com janelas de STFT de 0,5, 1 e 2 s, passo de 0,5 s e limiares de 6, 10 e 15 dB sobre o piso local.
- **Estimadores de `f̂₀`:** YIN com a regra original do primeiro mínimo (`first`), YIN com o menor atraso perto do mínimo global (`best`), ambos com limiares de 0,1, 0,2 e 0,3, e cepstro com proeminência mínima de 2, 4 e 6. Todos recebem o sinal após um passa-faixa de 5 a 250 Hz.
- **Testes automáticos:** os 11 testes de `tests/test_sim_mca001.py` passam. Entre eles, a comparação da decisão D1 com a busca exaustiva e a verificação do dimensionamento de Monte Carlo.

## 2. Resultados

### 2.1 O modelo de incerteza `σ_f` ainda não é adequado

O modelo `σ_f² = a/SNR_local + b·(ḟ·T)²` foi ajustado nas sementes `cal` e verificado nas `ver`. A cobertura do intervalo nominal de 95% ficou abaixo do alvo:

| Janela | Cobertura (`ver`) | Quartil de SNR local mais baixo |
|---|---|---|
| 0,5 s | 85,9% | 75% |
| 1 s | 82,4% | 65% |
| 2 s | 77,8% | 53% |

**Causa provável:** o pareamento com a verdade aceita picos até meio espaçamento harmônico, para não truncar o erro. Perto de componentes fracos, picos de ruído passam a valer como estimativas. A distribuição do erro tem, então, um núcleo gaussiano e uma cauda pesada, que o modelo não representa.

**Consequência:** o Bloco 2 não pode começar com este modelo. Um `σ_f` subestimado infla o qui-quadrado e faz ρ₁ e ρ₂ rejeitarem sinais harmônicos verdadeiros.

**Opções para a revisão:**
- (a) modelo de mistura, com núcleo gaussiano e fração de valores atípicos;
- (b) quantis empíricos do erro por faixa de SNR local, sem supor gaussianidade;
- (c) SNR local mínima para que um componente entre na busca de atribuições.

### 2.2 O limite de identificabilidade não é o limite efetivo

Com o modelo ajustado, a condição da ficha (`ln((n + 1)/n) > 2·σ_ln f`) só deixaria de valer acima da ordem 2.000 em todos os cenários.

**Por quê:** `σ_f` é aproximadamente constante em hertz. Então `σ_ln f = σ_f/(n·f₀)` e `ln((n + 1)/n) ≈ 1/n` caem juntos com a ordem. A condição se reduz a algo próximo de `f₀ > 2·σ_f`, quase independente de `n`. Só o termo de modulação cresce com a ordem, e ele é pequeno nas inclinações simuladas.

**O que limita de fato a ordem útil é a detecção:** componentes de ordem alta são fracos e não aparecem. A proposta para a revisão da ficha é que `N(t)` seja limitado pelo limite de banda e pela detecção, mantendo o critério de identificabilidade como verificação.

**Ressalva:** essa conclusão depende do modelo de incerteza, que a Seção 2.1 mostrou estar subestimado. Ela será refeita após a revisão do modelo.

### 2.3 Estimador da fundamental: o YIN com a regra original falha no caso que motiva a ficha

Os números abaixo vêm só da partição `ver` e descrevem o piloto, sem escolher estimador.

| Perfil e SNR | YIN `first` 0,2 | YIN `best` 0,2 | Cepstro, proeminência 6 |
|---|---|---|---|
| Terceiro harmônico dominante, 20 dB | 97,8% de erro | 0,5% de erro | 0,0% de erro |
| Terceiro harmônico dominante, 10 dB | 66,4% de erro | 0,6% de erro | 1,2% de erro |
| Terceiro harmônico dominante, 5 dB | 22,8% de erro (80% disponível) | 5,1% de erro (80% disponível) | 4,2% de erro (22% disponível) |
| Decrescente, 10 dB | 0,0% | 0,1% | 0,1% |
| Fundamental ausente identificável, 10 dB | 0,0% | 0,4% | 0,0% |

As taxas de erro são calculadas entre as estimativas disponíveis.

- **O YIN com a regra do primeiro mínimo fica excluído.** Quando o terceiro harmônico domina, ele devolve o período desse harmônico: a 20 dB, 56% das estimativas caem em `3f₀`. É exatamente o perfil atribuído ao canto B.
- **O YIN `best` e o cepstro acertam** ao menos 98,8% das estimativas disponíveis a partir de 10 dB. Abaixo de 5 dB, ambos ficam em grande parte indisponíveis, o que é o comportamento desejado.
- **Fundamental ausente com periodicidade ambígua** (só ordens pares; nada é contado como erro):
  - o YIN `best` devolve o período do sinal, `2f₀`, ou fica indisponível; a fundamental física aparece em no máximo 6% dos quadros;
  - o cepstro devolve a fundamental física, que não está no sinal, em 11% a 24% dos quadros.
  - Isso é uma indicação contra o cepstro, porque ele "encontra" uma periodicidade que o sinal não tem.
- **Candidato para a rodada final:** YIN `best`. A escolha do limiar será feita nas sementes `cal` da rodada final e verificada nas `ver`.

### 2.4 Detecção

- Com limiar de 10 dB, os falsos picos por quadro ficam entre 0,15 e 0,29 com janela de 0,5 s, perto de 0,5 com janela de 1 s, e entre 1 e 2,3 com janela de 2 s.
- A taxa de detecção precisa (erro até `1/T`) cresce com a SNR. É limitada pelos componentes de ordem alta, que são fracos no perfil decrescente.
- A janela de 2 s é a pior em precisão por ordem e em falsos picos. A escolha entre 0,5 e 1 s depende do modelo de incerteza revisado.

### 2.5 Procedimento de `f_max`

O procedimento funciona: com o filtro FIR do SciPy, o ganho sai da faixa de ±0,5 dB em 888,7 Hz. Esse valor vale para o filtro simulado, não para o do MBARI. O valor real de `f_max` depende da documentação do filtro de decimação dos arquivos de 2 kHz.

## 3. O que o piloto decide

Nada é congelado. O piloto indica três encaminhamentos para a revisão:

1. Revisar o modelo de incerteza antes da rodada final do Bloco 1 (Seção 2.1).
2. Excluir o YIN com a regra original e levar à rodada final o YIN `best`, com o cepstro como comparação (Seção 2.3).
3. Rever, na ficha, o papel do critério de identificabilidade na definição de `N(t)` (Seção 2.2).

Generated by Claude
