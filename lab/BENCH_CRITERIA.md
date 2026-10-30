# HMAL — Critérios da bancada digital de validação

**Versão:** 0.1.0-draft · **Data:** 30/10/2026 · **Estado:** aguardando aprovação; congela no commit de aprovação, antes de qualquer execução definitiva

## 1. Objeto da validação

O objeto é o **HMAL Rational Signal Processing Core**, um subsistema de software delimitado. Ele integra cinco componentes:

1. dicionário racional `H_N` e normalização de canais (`RationalChannel`);
2. geração de formas de onda (`HarmonicProtocol.generate_waveform`);
3. janela de sincronização (`HarmonicProtocol.sync_window`);
4. receptor mínimo, a construir: estimação espectral e recuperação dos canais;
5. relatório de verificação, comparando entrada, saída e previsão analítica.

Ficam **fora** da validação: o ajuste adaptativo de `f0` por SNR (relação sinal-ruído), a classificação biológica por faixas de frequência, os módulos de segurança, a compatibilidade JANUS, a comunicação submarina operacional e a hipótese bioacústica H1.

## 2. Previsões analíticas fixadas antes dos ensaios

- **Separação mínima entre canais.** Para dois elementos vizinhos de `H_N` com denominadores `b1` e `b2`, a distância entre as razões é de pelo menos `1/(b1·b2)`. Em `H_16`, a separação mínima é `Δr_min = 1/240`. Em frequência, `Δf_min = f0/240`: cerca de 7,2 Hz para `f0 = 1732 Hz` e 0,10 Hz para `f0 = 25 Hz`.
- **Duração mínima de observação.** A resolução espectral é de aproximadamente `1/T`. A recuperação sem ambiguidade exige `T ≥ 2/Δf_min`: cerca de 0,28 s no modo golfinho e 19,2 s no modo baleia.
- **Limite de Cramér–Rao.** Para um tom em ruído branco gaussiano, o desvio-padrão mínimo de um estimador não enviesado de frequência é `σ_CRB = sqrt(6·fs² / ((2π)²·SNR·N·(N²−1)))`, com `N` amostras, taxa `fs` e `SNR = A²/(2σ²)` para um tom real de amplitude `A` em ruído de variância `σ²` (Kay, *Fundamentals of Statistical Signal Processing*, vol. 1, 1993).
- **Probabilidade prevista de acerto.** Acima do limiar de SNR, a recuperação correta de um canal ocorre quando `|erro| < Δf/2`. A previsão é `P ≈ erf(Δf / (2·√2·σ))`.
- **Invariância à escala.** As razões entre canais simultâneos não mudam quando todas as frequências são multiplicadas por `(1+ε)`, como num desvio Doppler comum. Com dois ou mais canais, o receptor que usa razões entre canais deve ser imune a esse desvio.

## 3. Ensaios e critérios de aprovação

Condições padrão: `fs = 48 kHz` no modo golfinho e `fs = 2 kHz` no modo baleia. Sementes aleatórias fixas. Pelo menos 1.000 repetições por condição nos ensaios com ruído.

| Ensaio | O que verifica | Critério de aprovação |
|---|---|---|
| B1 — Dicionário | Cardinalidade, coprimalidade, unicidade e separação mínima de `H_16` e `H_32` | `\|H_16\| = 159`, `\|H_32\| = 647`, todos os pares coprimos, sem duplicatas, `Δr_min(H_16) = 1/240` exato |
| B2 — Fidelidade espectral | Frequências presentes no sinal gerado × frequências previstas, sem ruído | Erro de cada pico ≤ 1% de `1/T` |
| B3 — Recuperação sob ruído | Taxa de recuperação exata do conjunto de canais (K = 1, 2, 3), de −10 a +30 dB | (a) 100% sem ruído; (b) ≥ 99% com SNR integrado por canal ≥ 20 dB; (c) erro RMS de frequência ≤ 1,5·`σ_CRB` na região acima do limiar; (d) limiar de 50% de acerto a até ±3 dB da previsão analítica |
| B4 — Desvio de escala | Recuperação com todas as frequências deslocadas por `(1+ε)`, `\|ε\| ≤ 10⁻³` | Com K ≥ 2 e SNR ≥ 20 dB: ≥ 99% |
| B5 — Sincronização | `s(t + W) = s(t)` para `W = sync_window(...)`; comparação com o período mínimo numérico | Diferença relativa máxima ≤ 10⁻⁹; registrar se `W` é mínimo ou múltiplo do mínimo |
| B6 — Fundo acústico real | Canais sintéticos injetados em trechos de gravação MBARI de 2 kHz, modo baleia, `T ≥ 20 s` | ≥ 95% de recuperação com SNR integrado ≥ 20 dB; curva completa publicada |
| B7 — Controles negativos | (a) entrada só com ruído; (b) tons a meio caminho entre vizinhos de `H_N` | (a) falsos positivos ≤ 1% no limiar de detecção escolhido; (b) ≥ 99% sinalizados como fora da tolerância |

O ensaio B6 depende de acesso ao bucket público do MBARI. Ele roda no GitHub Actions. A falta de acesso é registrada como "não executado", nunca como aprovação.

## 4. Regra de decisão de maturidade

- **B1–B5 e B7 aprovados:** o relatório pode declarar **TRL 4 do subsistema computacional**, validado em ambiente de laboratório digital com resultados reproduzíveis e coerentes com as previsões analíticas. B6 aprovado reforça a declaração com fundo acústico real.
- **Algum desses ensaios reprovado:** o subsistema permanece em **TRL 3**. O relatório registra a falha, a causa provável e a correção prevista.
- A declaração vale **somente** para o subsistema da Seção 1. Não se estende à comunicação submarina, ao sistema completo nem à hipótese H1.

## 5. Ensaio paralelo da cadeia de medição (E1)

Reproduzir o Blue B Call Index do MBARI para dias de novembro de 2016, seguindo o código de processamento em lote do notebook: segmentos de 60 s, Welch com janela Hann de 1 s e `nfft = 2000`, pico em 43–44 Hz e fundo em 37 e 50 Hz.

Antes da execução, os valores de referência publicados no notebook serão transcritos para `lab/bench/e1_reference.json`, com a data de acesso. O critério de aprovação é uma diferença relativa ≤ 2% em cada média diária comparada. O domínio da razão (linear ou dB) é o do código de referência e fica registrado.

## 6. Reprodutibilidade

- Código em `lab/bench/`, executado pelo CI.
- Resultados em JSON versionados, com commit, sementes, versões de bibliotecas e data.
- Os limiares desta página não mudam depois do congelamento. Qualquer alteração exige nova versão e registro do motivo.
- LLMs podem ajudar a escrever o código e a revisar, mas não produzem os valores das métricas.
