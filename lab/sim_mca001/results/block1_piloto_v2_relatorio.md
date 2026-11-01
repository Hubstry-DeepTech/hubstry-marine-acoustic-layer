# Bloco 1 — relatório do piloto v2 e auditoria

**Plano:** SIM-MCA-001 v0.3 · **Data:** 01/11/2026 · **Rótulo:** `EXPLORATORY/FEASIBILITY` · **Tipo:** piloto. Nenhum parâmetro foi congelado e nenhum dado real foi aberto.

**Arquivo de resultados:** `block1_piloto_v2.json` (SHA-256 `2382d4733e01f96acfe0bae34e21054745020a1228230c31d3097a5da2c09e47`). Foi gerado pelo runner revisado pela Luna (commit `a9cf3d1`), com `--reps 6 --workers 2`, em 4.033 s. São 1.920 sinais, metade na partição `cal` e metade na `ver`.

## 1. Correção da busca de atribuições (condição da Luna para o Bloco 2)

A Luna mostrou que a busca rápida da decisão D1 não era completa. Confirmei o problema: em 3.000 casos sorteados, a heurística por arredondamento errou o mínimo em 622. As falhas se concentram nos ajustes ruins, típicos dos sinais nulos.

A busca foi substituída por uma busca exata, por ramificação e poda (`assignment.exact_search`). A descrição e a verificação estão no plano, Seção 4. Em resumo:
- coincidiu com a busca exaustiva no mínimo e no conjunto `H*` inteiro, nos mesmos 3.000 casos;
- custa de 7 a 12 ms por busca, em mediana, na escala do canto B;
- dois testes automáticos registram a completude da busca exata e a incompletude da heurística.

A suíte do repositório passa (154 testes).

## 2. Resultados do piloto v2

### 2.1 Incerteza: a cobertura agregada está correta, mas a cobertura por sinal não

Com os quantis empíricos em `ln f`, a cobertura por estrato de SNR local e modulação ficou entre 94,6% e 95,4%, nas três janelas.

A média da cobertura **por sinal**, porém, ficou bem abaixo de 95%:

| Janela | Limiar de SNR local (escolhido em `cal`) | Cobertura média por sinal (`ver`) | IC bootstrap de 95% |
|---|---|---|---|
| 0,5 s | 10 dB | 84,3% | 83,4% a 85,2% |
| 1 s | 15 dB | 81,6% | 80,2% a 82,9% |
| 2 s | 20 dB | 85,3% | 83,8% a 86,7% |

### 2.2 Diagnóstico: o quantil em `ln f` agregado sobre todas as ordens

O erro de frequência tem escala aproximadamente constante em **hertz**, e não em `ln f`. Como `ln(f_est/f_true) ≈ erro_Hz/f`, o mesmo erro em hertz vira um erro grande em `ln f` nas ordens baixas e pequeno nas altas.

Um quantil de `ln f` agregado sobre todas as ordens fica, então, estreito demais para as ordens baixas e largo demais para as altas. A cobertura agregada sai certa porque as ordens altas são maioria.

Verifiquei isso com `diag_cobertura.py`: 160 sinais novos da partição `ver`, um por célula, com a tabela de calibração do piloto.

| Janela | Ordens 1 a 3 | 4 a 10 | 11 a 30 | 31 ou mais | Média por sinal |
|---|---|---|---|---|---|
| 0,5 s, quantis em `ln f` | 74,2% | 95,0% | 99,3% | 99,5% | 84,0% |
| 0,5 s, quantis em Hz | 97,9% | 96,6% | 95,1% | 92,0% | 90,2% |
| 1 s, quantis em `ln f` | 78,7% | 95,8% | 99,7% | 100% | 81,7% |
| 1 s, quantis em Hz | 98,5% | 96,5% | 92,7% | 93,9% | **95,2%** |

- Os sinais com poucos componentes têm, proporcionalmente, mais ordens baixas, e por isso puxam a média por sinal para baixo.
- Com quantis em Hz e janela de 1 s, a cobertura fica perto de 95% em todas as faixas de ordem e em todos os fatores da grade: entre 93,7% e 96,0% por perfil, fundamental, inclinação, SNR integrada e cor do ruído.
- Com janela de 0,5 s, ainda sobra dependência da SNR integrada (81,8% a −5 dB e 96,8% a 20 dB). A SNR local não a captura sozinha nessa janela.

**Proposta para a revisão:**
- tabular os quantis do erro em Hz, por SNR local e modulação;
- obter o intervalo em `ln f` de cada componente por transformação exata, `[ln(1 + q₀₂₅/f_k), ln(1 + q₉₇₅/f_k)]`. Isso não supõe gaussianidade: é a mesma quantidade empírica, levada ao domínio do ajuste;
- levar a janela de 1 s, com limiar de 15 dB, como candidata da rodada final.

### 2.3 Identificabilidade: o limite finito vem do mesmo artefato

O runner v2 calcula o limite de identificabilidade com um raio constante em `ln f`. Os valores foram de 71 (janela de 0,5 s), 151 (1 s) e 206 (2 s) ordens.

Com o raio em Hz, que é o que de fato descreve o erro, a condição `ln((n + 1)/n) > 2·r_Hz/(n·f₀)` equivale a `n·ln(1 + 1/n) > 2·r_Hz/f₀`. O lado esquerdo fica entre `ln 2` e 1 para qualquer `n`. Então a condição deixa de depender da ordem:
- vale para todas as ordens se `f₀ > 2·r_Hz/ln 2 ≈ 2,9·r_Hz`;
- falha para todas se `f₀ < 2·r_Hz`.

O limite continua estrutural, como decidiu a Luna. Mas, com erro constante em hertz, ele se torna um limite sobre `f₀`, e não sobre `n`. Só o termo de modulação, que cresce com a ordem, pode reintroduzir dependência de `n`. Isso deve ser verificado no estrato modulado.

### 2.4 Estimador da fundamental

O limiar do YIN `best` escolhido em `cal` foi 0,3, pelo critério de acertos nos perfis identificáveis a 10 e 20 dB. Na partição `ver`:
- a 10 e 20 dB, o erro entre as estimativas disponíveis ficou em até 1,2%, com disponibilidade de 99% a 100%;
- a 5 dB, no perfil de terceiro harmônico dominante, o erro subiu para 7,4%, contra 5,1% com o limiar 0,2.

O critério de seleção não controla o erro abaixo de 10 dB. Proponho acrescentar um teto para a taxa de erro entre as estimativas disponíveis, fixado antes da rodada final.

No caso ambíguo (só ordens pares), o YIN `best` 0,3 devolveu o período do sinal ou ficou indisponível em 88% a 100% dos quadros. A saída compatível com a subarmônica ficou em até 7%, sem ser contada como erro.

### 2.5 Detecção

- Com limiar de 10 dB e janela de 1 s, a taxa de detecção dos componentes resolvidos foi de 17% a 0 dB, 56% a 10 dB e 90% a 20 dB. Os falsos picos ficaram entre 0,5 e 0,9 por quadro.
- Com janela de 0,5 s, há menos falsos picos (0,15 a 0,55 por quadro), mas a detecção é menor (67% a 20 dB).
- Na janela de 1 s, 27% dos componentes ficaram "não resolvidos". São sobretudo ordens altas com modulação, cuja excursão de frequência na janela passa de 45% da separação entre componentes.

## 3. Situação

| Item | Estado |
|---|---|
| Busca exata de atribuições | Implementada e verificada; aguarda aprovação da Luna |
| Matriz `Σ` | Proposta no plano, Seção 4; aguarda aprovação |
| Incerteza por quantis em Hz | Proposta, com diagnóstico (Seção 2.2); aguarda aprovação |
| Rodada final do Bloco 1 | Em espera, até essas decisões |
| Bloco 2 | Bloqueado |
| Dados reais | Bloqueados |

Generated by Claude
