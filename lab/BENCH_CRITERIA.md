# HMAL — Critérios da bancada digital de validação

**Versão:** 0.2.0-draft · **Data:** 30/10/2026 · **Estado:** aguardando nova revisão; congela no commit de aprovação, antes de qualquer execução definitiva

**Mudanças desde 0.1.0:** taxa de amostragem do modo golfinho elevada para 96 kHz (Nyquist); receptor e estimador especificados; piloto definido para o ensaio de escala; critério de Cramér–Rao restrito a tom único; limiar de detecção derivado analiticamente e congelado; matriz de ensaios versionada; referência do E1 transcrita.

## 1. Objeto da validação

O objeto é o **HMAL Rational Signal Processing Core**, um subsistema de software delimitado. Ele integra cinco componentes:

1. dicionário racional `H_16` e normalização de canais (`RationalChannel`);
2. geração de formas de onda (`HarmonicProtocol.generate_waveform`);
3. janela de sincronização (`HarmonicProtocol.sync_window`);
4. receptor mínimo, especificado na Seção 3 e a implementar em `lab/bench/`;
5. relatório de verificação, comparando entrada, saída e previsão analítica.

Ficam **fora** da validação: o ajuste adaptativo de `f0` por SNR (relação sinal-ruído), a classificação biológica por faixas de frequência, os módulos de segurança, a compatibilidade JANUS, a comunicação submarina operacional e a hipótese bioacústica H1.

## 2. Modos, sinais e ruído

| Modo | `f0` | `fs` | Duração `T` | Maior frequência (`16·f0`) | Nyquist |
|---|---|---|---|---|---|
| Golfinho | 1.732 Hz | 96 kHz | 0,5 s | 27.712 Hz | 48 kHz |
| Baleia | 25 Hz | 2 kHz | 20 s | 400 Hz | 1 kHz |

- **Sinal:** soma de tons de amplitudes iguais gerada por `generate_waveform`. A fase de cada tom é sorteada em {0, π}, que é o que o gerador aceita. Essa limitação fica registrada no relatório.
- **Ruído:** branco, gaussiano, de média zero e variância `σ²` por amostra, em toda a banda de 0 a `fs/2`.
- **SNR integrado por canal:** `SNR_int,k = A_k²·N / (2σ²)`, com `A_k` a amplitude do tom `k` depois da normalização do gerador e `N = fs·T` amostras. Para cada SNR-alvo, `σ²` é calculado por essa fórmula.

## 3. Receptor especificado

Com `f0` nominal e o número `K` de canais conhecidos:

1. **Periodograma** com janela retangular e preenchimento com zeros até `16·N` pontos.
2. **Seleção:** avaliar o periodograma nas 159 frequências candidatas `r·f0`, com `r ∈ H_16`, e escolher as `K` maiores.
3. **Refinamento:** maximizar o periodograma (método de Brent) em ±`1/T` em torno de cada candidata escolhida. Para um tom em ruído branco, esse máximo é aproximadamente o estimador de máxima verossimilhança.
4. **Decodificação:** associar cada frequência estimada ao elemento mais próximo de `H_16`. Aceitar quando `|f_est − r·f0| ≤ 1/(2T)`; caso contrário, marcar "fora da tolerância".
5. **Modo com piloto (B4):** o canal `1/1` é transmitido como piloto. O receptor estima primeiro a frequência do piloto em ±0,2% de `f0`, usa essa estimativa como `f0` e então executa os passos 2 a 4 sobre os canais de dados.

## 4. Previsões analíticas

- **Separação mínima.** Em `H_16`, a menor distância entre razões vizinhas é exatamente `1/240`: cerca de 7,2 Hz (3,6 bins de `1/T`) no modo golfinho e 0,104 Hz (2,1 bins) no modo baleia. Os pares de pior caso são `1/16–1/15` e `14/15–15/16`.
- **Cramér–Rao para tom único.** `σ_CRB = sqrt(6·fs² / ((2π)²·SNR·N·(N²−1)))`, com `SNR = A²/(2σ²)` (Kay, *Fundamentals of Statistical Signal Processing*, vol. 1, 1993). A expressão vale só para um tom. Para `K ≥ 2`, o erro por canal é reportado em comparação com ela apenas de forma descritiva.
- **Limiar de detecção.** Com ruído apenas, o periodograma normalizado `I(f) = P(f)/σ̂²` segue aproximadamente uma distribuição exponencial de média 1 em cada candidata. `σ̂²` é estimado pela mediana do periodograma dividida por `ln 2`. Para `M = 159` candidatas e taxa-alvo de falso positivo `α = 1%`, o limiar é `γ = −ln(1 − (1−α)^(1/M))`, cerca de 9,67. Esse valor é **congelado** e não é ajustado com dados.

## 5. Ensaios e critérios de aprovação

A matriz completa está em `lab/bench/matrix.json`, gerada de forma determinística por `lab/bench/make_matrix.py` (semente 20261030). Ela inclui os conjuntos de canais, os pares de pior caso, as grades de SNR e de escala e as faixas de sementes.

| Ensaio | O que verifica | Critério de aprovação |
|---|---|---|
| B1 — Dicionário | Cardinalidade, coprimalidade, unicidade e separação mínima | `\|H_16\| = 159`, `\|H_32\| = 647`, pares coprimos, sem duplicatas, `Δr_min(H_16) = 1/240` exato |
| B2 — Fidelidade espectral, sem ruído | (a) os 158 canais de dados isolados; (b) 50 conjuntos com `K = 2` e 50 com `K = 3`, separação ≥ `10/T`, em cada modo | (a) erro ≤ `0,01/T`; (b) erro ≤ `0,05/T` por canal |
| B3 — Recuperação sob ruído | `K = 1, 2, 3`; `SNR_int` de −10 a +30 dB, passo de 2 dB; 1.000 ensaios por condição; `K = 2` inclui os pares de pior caso | (a) 100% sem ruído; (b) ≥ 99% de recuperação exata do conjunto com `SNR_int ≥ 20 dB`; (c) só para `K = 1`: erro RMS ≤ 1,5·`σ_CRB` com `SNR_int ≥ 16 dB` |
| B4 — Desvio de escala comum | Piloto `1/1` + `K = 1` ou `2` canais; todas as frequências multiplicadas por `(1+ε)`, `ε ∈ {−10⁻³, −5·10⁻⁴, 0, 5·10⁻⁴, 10⁻³}`; `SNR_int = 20 dB` | ≥ 99% de recuperação exata em todos os valores de `ε` |
| B5 — Sincronização | `s(t + W) = s(t)` para `W = sync_window(...)`, avaliado na expressão analítica do sinal, nos conjuntos de B2; comparação com o período mínimo numérico | Diferença relativa máxima ≤ 10⁻⁹; registrar se `W` é o período mínimo ou um múltiplo dele |
| B6 — Fundo acústico real | Modo baleia; canais injetados em trechos de gravação MBARI de 2 kHz; `σ²` medido no próprio trecho | ≥ 95% de recuperação com `SNR_int ≥ 20 dB`; curva completa publicada; registrar que o fundo não é branco |
| B7 — Controles negativos | (a) só ruído, com o limiar `γ` congelado: 10.000 ensaios de calibração (sementes 0–9.999), apenas para verificação, e 10.000 de avaliação (sementes 1.000.000–1.009.999); (b) tons nos 158 pontos médios entre vizinhos de `H_16`, sem ruído | (a) falsos positivos ≤ 1,3% na avaliação (1% mais a margem de amostragem); (b) 100% marcados "fora da tolerância" |

O ensaio B6 depende de acesso ao bucket público do MBARI e roda no GitHub Actions. Sem acesso, ele é registrado como "não executado", nunca como aprovado.

## 6. Regra de decisão de maturidade

- **B1–B5 e B7 aprovados:** o relatório pode declarar **TRL 4 do subsistema computacional**, validado em ambiente de laboratório digital com resultados reproduzíveis e coerentes com as previsões analíticas. B6 aprovado reforça a declaração com fundo acústico real.
- **Algum desses ensaios reprovado:** o subsistema permanece em **TRL 3**. O relatório registra a falha, a causa provável e a correção prevista.
- A declaração vale **somente** para o subsistema da Seção 1. Não se estende à comunicação submarina, ao sistema completo nem à hipótese H1.

## 7. Ensaio paralelo da cadeia de medição (E1)

Reprodução do Blue B Call Index do MBARI, conforme o código de processamento em lote do notebook. A referência está congelada em `lab/bench/e1_reference.json`, com acesso em 30/10/2026:
- segmentos de 60 s; Welch com janela Hann de 2.000 amostras e `nfft = 2000`;
- PSD em dB calibrado (`10·log10(psd) − sens`);
- `CI = média(pico 43–44 Hz) / média(fundo 37 e 50 Hz)`, ou seja, uma razão entre níveis em dB, não entre potências lineares;
- médias diárias publicadas para novembro de 2016.

**Critério:** diferença relativa ≤ 2% nas médias diárias de 01, 11 e 22/11/2016. Os demais dias são reportados sem critério. O dia 19/11 é excluído, porque o valor publicado é NaN (dados ausentes).

## 8. Reprodutibilidade

- Código em `lab/bench/`, executado pelo CI.
- Resultados em JSON versionados, com commit, sementes, versões de bibliotecas e data.
- Os limiares e a matriz não mudam depois do congelamento. Qualquer alteração exige nova versão e registro do motivo.
- LLMs podem ajudar a escrever o código e a revisar, mas não produzem os valores das métricas.
