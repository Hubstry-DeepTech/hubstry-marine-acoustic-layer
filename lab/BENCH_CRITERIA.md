# HMAL — Critérios da bancada digital de validação

**Versão:** 0.3.0-draft · **Data:** 30/10/2026 · **Estado:** aguardando nova revisão; congela no commit de aprovação, antes de qualquer execução definitiva

**Mudanças desde 0.2.0:**
- fator 12 no limite de Cramér–Rao e conversão explícita entre SNR integrado e SNR por amostra;
- matriz completa materializada, com teste de CI de reconstrução;
- piloto excluído da busca de dados;
- função otimizada pelo estimador definida, sem alegação de máxima verossimilhança conjunta para vários tons;
- regra de detecção de B7 operacional, com critério de Clopper–Pearson;
- B6 tratado como exploratório, com SNR local por banda;
- modos renomeados;
- ambiente e interfaces registrados.

**Mudanças desde 0.1.0:** amostragem de 96 kHz no modo de alta frequência; receptor especificado; piloto em B4; referência do E1 transcrita.

## 1. Objeto da validação

O objeto é o **HMAL Rational Signal Processing Core**, um subsistema de software delimitado. Ele integra cinco componentes:

1. dicionário racional `H_16` e normalização de canais (`RationalChannel`);
2. geração de formas de onda (`HarmonicProtocol.generate_waveform`);
3. janela de sincronização (`HarmonicProtocol.sync_window`);
4. receptor mínimo, especificado na Seção 4 e a implementar em `lab/bench/`;
5. relatório de verificação, comparando entrada, saída e previsão analítica.

Ficam **fora** da validação: o ajuste adaptativo de `f0` por SNR (relação sinal-ruído), a classificação biológica por faixas de frequência, os módulos de segurança, a compatibilidade JANUS, a comunicação submarina operacional e a hipótese bioacústica H1.

## 2. Ambiente de laboratório digital e interfaces

- **Ambiente:** GitHub Actions, `ubuntu-latest`, Python 3.11. Cada resultado registra o commit, a versão do sistema, do Python, do NumPy e do SciPy, as sementes e a data.
- **Interfaces sob teste:**
  - `RationalChannel(a, b)`;
  - `HarmonicProtocol(f0_base, harmonic_order=16, mode=...)`;
  - `generate_waveform(channels, duration, sample_rate, amplitudes, phase_polarities) -> (t, s)`;
  - `sync_window(channel_ratios) -> float`;
  - receptor `lab/bench/receiver.py: decode(x, fs, f0, K, pilot=False) -> list[(a, b) | "fora da tolerância"]`.
- **Ambiente relevante definido:** canal digital com ruído branco gaussiano aditivo e desvio de escala comum, o que modela um Doppler uniforme. Fundo acústico real do MBARI apenas em caráter exploratório (B6).
- **Previsões de desempenho:** as da Seção 5, registradas antes da execução.
- Aprovação nos limiares é **autoavaliação** de maturidade, sujeita a revisão independente. Não é certificação.

## 3. Modos, sinais e ruído

Os modos são parâmetros sintéticos da bancada. Não são frequências representativas de nenhuma espécie.

| Modo | `f0` | `fs` | Duração `T` | `N = fs·T` | Maior frequência (`16·f0`) | Nyquist |
|---|---|---|---|---|---|---|
| Alta frequência (AF) | 1.732 Hz | 96 kHz | 0,5 s | 48.000 | 27.712 Hz | 48 kHz |
| Baixa frequência (BF) | 25 Hz | 2 kHz | 20 s | 40.000 | 400 Hz | 1 kHz |

- **Sinal:** soma de tons de amplitudes iguais gerada por `generate_waveform`. A polaridade de fase de cada tom (0 ou π) vem da matriz. Essa limitação do gerador fica registrada no relatório.
- **Ruído:** branco, gaussiano, de média zero e variância `σ²` por amostra, em toda a banda de 0 a `fs/2`. É gerado por `numpy.random.default_rng(noise_seed)`.
- **SNR:** `η_k = A_k²/(2σ²)` é o SNR por amostra do tom `k`, com `A_k` a amplitude depois da normalização do gerador. O SNR integrado é `SNR_int,k = N·η_k`. Para cada SNR-alvo, `σ² = A_k²·N / (2·SNR_int)`.

## 4. Receptor especificado

1. **Transformada contínua:** `X(f) = Σ_n x[n]·exp(−j2πfn/fs)`, com janela retangular. A função usada no refinamento é `P(f) = |X(f)|²/N`.
2. **Seleção:** avaliar `P` nas frequências candidatas `r·f0`, com `r ∈ H_16`, e escolher as `K` maiores.
3. **Refinamento:** para cada candidata escolhida, maximizar `P(f)` pelo método de Brent no intervalo `[f_c − 1/T, f_c + 1/T]`, de forma independente para cada pico. Para `K = 1`, esse é aproximadamente o estimador de máxima verossimilhança de um tom em ruído branco. Para `K ≥ 2`, é um estimador operacional por picos, **não** uma estimativa conjunta de máxima verossimilhança.
4. **Decodificação:** associar cada frequência estimada ao elemento mais próximo de `H_16`. Aceitar quando `|f_est − r·f0| ≤ 1/(2T)`; caso contrário, marcar "fora da tolerância".
5. **Modo com piloto (B4):**
   - estimar a frequência do piloto `1/1` maximizando `P` em ±0,2% de `f0`, e usar essa estimativa como `f0`;
   - executar os passos 2 a 4 sobre as 158 candidatas restantes, **com o piloto excluído da busca**.

## 5. Previsões analíticas

- **Separação mínima.** Em `H_16`, a menor distância entre razões vizinhas é exatamente `1/240`:
  - modo AF: cerca de 7,2 Hz, ou 3,6 bins de `1/T`;
  - modo BF: 0,104 Hz, ou 2,1 bins.

  Os pares de pior caso são `1/16–1/15` e `14/15–15/16`.
- **Cramér–Rao assintótico para tom único real** (amplitude, fase e frequência desconhecidas):

  $$\sigma_{f,\mathrm{ACRB}} = \sqrt{\frac{12\,f_s^2}{(2\pi)^2\,\eta\,N(N^2-1)}},\qquad \eta = \frac{\mathrm{SNR}_{int}}{N}$$

  Referências: Kay, *Fundamentals of Statistical Signal Processing*, vol. 1, 1993; Candan e Çelebi, 2021. A expressão vale só para um tom. Para `K ≥ 2`, o erro por canal é comparado a ela apenas de forma descritiva.
- **Limiar de detecção.**
  - Com ruído apenas, `I(f) = P(f)/σ̂²` segue aproximadamente uma distribuição exponencial de média 1 em cada candidata.
  - `σ̂²` é a mediana de `P` nas frequências de Fourier `k·fs/N`, com `k = 1, …, N/2 − 1`, dividida por `ln 2`.
  - Para `M = 159` candidatas e taxa de projeto `α = 0,5%`, o limiar é `γ = −ln(1 − (1−α)^(1/M)) ≈ 10,365`.
  - **Regra de detecção:** declarar sinal presente quando `max_c I(r_c·f0) > γ`.
  - O limiar é **congelado** e não é ajustado com dados.

## 6. Ensaios e critérios de aprovação

A matriz completa está em `lab/bench/matrix.json`, versão 0.3.0, gerada por `lab/bench/make_matrix.py` com semente 20261030. Ela traz, para cada ensaio e cada modo:
- os canais;
- as polaridades de fase;
- a semente de ruído de cada um dos 1.000 ensaios.

O teste `tests/test_bench_matrix.py` verifica no CI que o arquivo versionado é idêntico ao reconstruído. B3 e B4 rodam nos **dois** modos. Os mesmos ensaios são usados em toda a grade de SNR, com números aleatórios comuns.

| Ensaio | O que verifica | Critério de aprovação |
|---|---|---|
| B1 — Dicionário | Cardinalidade, coprimalidade, unicidade e separação mínima | `\|H_16\| = 159`, `\|H_32\| = 647`, pares coprimos, sem duplicatas, `Δr_min(H_16) = 1/240` exato |
| B2 — Fidelidade espectral, sem ruído | (a) os 158 canais de dados isolados; (b) 50 conjuntos com `K = 2` e 50 com `K = 3`, separação ≥ `10/T` | (a) erro ≤ `0,01/T`; (b) erro ≤ `0,05/T` por canal |
| B3 — Recuperação sob ruído | `K = 1, 2, 3` sorteados (1.000 ensaios cada) e cada par de pior caso como condição própria (1.000 ensaios cada); `SNR_int` de −10 a +30 dB, passo de 2 dB | (a) 100% sem ruído; (b) ≥ 99% de recuperação exata do conjunto com `SNR_int ≥ 20 dB`, em todas as condições, inclusive os pares de pior caso; (c) só para `K = 1`: erro RMS ≤ 1,5·`σ_f,ACRB` com `SNR_int ≥ 16 dB` |
| B4 — Desvio de escala comum | Piloto `1/1` + `K = 1` ou `2` canais de dados; frequências multiplicadas por `(1+ε)`, `ε ∈ {−10⁻³, −5·10⁻⁴, 0, 5·10⁻⁴, 10⁻³}`; `SNR_int = 20 dB` por canal | ≥ 99% de recuperação exata em todos os valores de `ε` |
| B5 — Sincronização | `s(t + W) = s(t)` para `W = sync_window(...)`, avaliado na expressão analítica, nos conjuntos de B2; comparação com o período mínimo numérico | Diferença relativa máxima ≤ 10⁻⁹; registrar se `W` é mínimo ou múltiplo |
| B7 — Controles negativos | (a) só ruído, nos dois modos: 10.000 ensaios de calibração (sementes 0–9.999), apenas para verificação, e 10.000 de avaliação (sementes 1.000.000–1.009.999); (b) tons nos 158 pontos médios entre vizinhos de `H_16`, sem ruído | (a) limite superior unilateral de 95% de Clopper–Pearson da taxa de falso positivo na avaliação ≤ 1%, em cada modo; (b) 100% marcados "fora da tolerância" |

## 7. Ensaio exploratório com fundo real (B6)

- **Modo:** BF.
- **Sinal:** canais sintéticos injetados em trechos de gravação MBARI de 2 kHz.
- **Ruído colorido:** o fundo não é branco. Por isso, o SNR é definido **por banda**. Para cada portadora `k`, `σ²_k` é a mediana de `P` no trecho sem injeção, nos bins a até `5/T` da portadora (excluídos os bins a até `2/T` dela), dividida por `ln 2`. Então `SNR_int,k = A_k²·N / (2σ²_k)`.
- **Resultado:** curva de recuperação × SNR local, publicada integralmente.
- **Status:** **exploratório**. Não tem critério de aprovação e não entra na regra de decisão de maturidade. Sem acesso ao bucket público do MBARI, é registrado como "não executado".

## 8. Regra de decisão de maturidade

- **B1–B5 e B7 aprovados:** o relatório pode declarar, como autoavaliação, **TRL 4 do subsistema computacional**. A declaração se apoia na integração dos componentes da Seção 1, nas interfaces da Seção 2 e em resultados reproduzíveis coerentes com as previsões da Seção 5, no ambiente digital definido.
- **Algum desses ensaios reprovado:** o subsistema permanece em **TRL 3**. O relatório registra a falha, a causa provável e a correção prevista.
- A declaração vale **somente** para o subsistema da Seção 1. Não se estende à comunicação submarina, ao sistema completo nem à hipótese H1.

## 9. Ensaio paralelo da cadeia de medição (E1)

Reprodução do Blue B Call Index do MBARI, conforme o código de processamento em lote do notebook. A referência está congelada em `lab/bench/e1_reference.json`, com acesso em 30/10/2026:
- segmentos de 60 s; Welch com janela Hann de 2.000 amostras e `nfft = 2000`;
- PSD em dB calibrado (`10·log10(psd) − sens`);
- `CI = média(pico 43–44 Hz) / média(fundo 37 e 50 Hz)`, ou seja, uma razão entre níveis em dB;
- médias diárias publicadas em `Out[15]` para novembro de 2016.

**Critério:** diferença relativa ≤ 2% nas médias diárias de 01, 11 e 22/11/2016. Os demais dias são reportados sem critério. O dia 19/11 aparece como NaN em `Out[15]`. O notebook o recalcula em `In[17]`, mas não imprime o valor; por isso, ele fica sem referência numérica e fora da comparação.

## 10. Reprodutibilidade

- Código em `lab/bench/`, executado pelo CI.
- Resultados em JSON versionados, com commit, sementes, versões de bibliotecas e data.
- Os limiares e a matriz não mudam depois do congelamento. Qualquer alteração exige nova versão e registro do motivo.
- LLMs podem ajudar a escrever o código e a revisar, mas não produzem os valores das métricas.
