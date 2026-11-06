# Bloco 1 — relatório do piloto v2 e auditoria

**Plano:** SIM-MCA-001 v0.3.1 · **Data:** 01/11/2026 · **Rótulo:** `EXPLORATORY/FEASIBILITY` · **Tipo:** piloto. Nenhum parâmetro foi congelado e nenhum dado real foi aberto.

**Arquivo de resultados:** `block1_piloto_v2.json` (SHA-256 `2382d4733e01f96acfe0bae34e21054745020a1228230c31d3097a5da2c09e47`). Foi gerado pelo runner revisado pela Luna (commit `a9cf3d1`), com `--reps 6 --workers 2`, em 4.033 s. São 1.920 sinais, metade na partição `cal` e metade na `ver`.

## 1. Correção da busca de atribuições (condição da Luna para o Bloco 2)

A Luna mostrou que a busca rápida da decisão D1 não era completa. Confirmei o problema: em 3.000 casos sorteados, a heurística por arredondamento errou o mínimo em 622. As falhas se concentram nos ajustes ruins, típicos dos sinais nulos.

A busca foi substituída por uma busca exata, por ramificação e poda (`assignment.exact_search`). A descrição e a verificação estão no plano, Seção 4. Em resumo:
- coincidiu com a busca exaustiva no mínimo e no conjunto `H*` inteiro, nos mesmos 3.000 casos;
- custa de 7 a 12 ms por busca, em mediana, na escala do canto B;
- dois testes automáticos registram a completude da busca exata e a incompletude da heurística.

A suíte do repositório passa (156 testes).

**Proteções e verificação reproduzível (parecer da Luna sobre o piloto v2).**
- A fatoração `UᵀDU` agora falha explicitamente se algum dos `K − 1` primeiros pivôs for não positivo, se o último não for nulo dentro da tolerância, ou se a reconstrução `UᵀDU` se afastar de `M` em mais de 10⁻⁶ relativo. Antes, um pivô intermediário pequeno era zerado em silêncio.
- A cota inicial passou a usar a mesma aritmética da busca. A bateria mal condicionada revelou que, com `Σ` de número de condição até ~10¹⁰, a diferença de arredondamento entre `vᵀMv` direto e a soma fatorada chegava a 6·10⁻⁵ relativo. Isso fazia a busca podar a própria semente ótima em 2 de 500 casos. O conjunto `H*` é decidido no fim pelo valor direto.
- O script `verify_d1.py` reproduz as baterias. Resultado (`results/verify_d1.json`):

| Bateria | Casos | Mínimo igual ao exaustivo | `H*` igual ao exaustivo | Tempo mediano |
|---|---|---|---|---|
| Geral (K 2 a 6, N = 12) | 3.000 | 3.000 | 3.000 | 1,2 ms |
| Mal condicionada (condição até ~10¹⁰) | 500 | 500 | 500 | 3,0 ms |
| Escala operacional (N 60 a 70, K 4 a 6) | 21 | 21 | 21 | 13 ms |

- **Limite não coberto:** `K ≥ 7` com `N ≥ 60`. A comparação exaustiva passa de 3,8·10⁸ combinações e fica inviável.
- A docstring de `assignment.py` foi atualizada. Dois testes novos verificam a fatoração e uma versão reduzida das baterias.

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

Verifiquei isso com `diag_cobertura.py`, aplicando a tabela de calibração do piloto a 160 sinais da partição `ver`, um por célula.

**Correção (parecer da Luna):** esses 160 sinais não são novos. As sementes são determinísticas, e a réplica 0 de cada célula já fazia parte da verificação do piloto. O diagnóstico é uma reanálise de parte da partição `ver`, e a escolha da janela de 1 s foi feita olhando esses resultados. Por isso, os números abaixo são exploratórios e não confirmam a cobertura. A confirmação exige uma nova partição de verificação, com sementes inéditas, gerada depois de registrar a janela, o limiar, as regras dos quantis e o critério de cobertura.

| Janela | Ordens 1 a 3 | 4 a 10 | 11 a 30 | 31 ou mais | Média por sinal |
|---|---|---|---|---|---|
| 0,5 s, quantis em `ln f` | 74,2% | 95,0% | 99,3% | 99,5% | 84,0% |
| 0,5 s, quantis em Hz | 97,9% | 96,6% | 95,1% | 92,0% | 90,2% |
| 1 s, quantis em `ln f` | 78,7% | 95,8% | 99,7% | 100% | 81,7% |
| 1 s, quantis em Hz | 98,5% | 96,5% | 92,7% | 93,9% | 95,2% (exploratório) |

- Os sinais com poucos componentes têm, proporcionalmente, mais ordens baixas, e por isso puxam a média por sinal para baixo.
- Com quantis em Hz e janela de 1 s, a cobertura fica perto de 95% em todas as faixas de ordem e em todos os fatores da grade: entre 93,7% e 96,0% por perfil, fundamental, inclinação, SNR integrada e cor do ruído.
- Com janela de 0,5 s, ainda sobra dependência da SNR integrada (81,8% a −5 dB e 96,8% a 20 dB). A SNR local não a captura sozinha nessa janela.

**Proposta para a revisão:**
- tabular os quantis do erro em Hz, por SNR local e modulação;
- obter o intervalo em `ln f` de cada componente por transformação exata dos quantis em Hz, sem supor gaussianidade. **Correção (parecer da Luna):** em dados reais, a frequência verdadeira é desconhecida, e a transformação precisa partir da frequência estimada. Com `e = f_est − f_true` e quantis `q₀₂₅` e `q₉₇₅`, vale `f_true ∈ [f_est − q₉₇₅, f_est − q₀₂₅]`. O resíduo `ln(f_est/f_true)` fica, então, em `[ln(f_est/(f_est − q₀₂₅)), ln(f_est/(f_est − q₉₇₅))]`, desde que `f_est − q₉₇₅ > 0`. A forma com `f_k` verdadeira, usada no diagnóstico, vale só na simulação;
- levar a janela de 1 s, com limiar de 15 dB, como candidata da rodada final.

### 2.3 Identificabilidade: o limite finito vem do mesmo artefato

O runner v2 calcula o limite de identificabilidade com um raio constante em `ln f`. Os valores foram de 71 (janela de 0,5 s), 151 (1 s) e 206 (2 s) ordens.

**Correção (parecer da Luna):** a derivação que eu tinha feito usava a aproximação logarítmica e não era exata. Com intervalo de erro aditivo em Hz, os intervalos de dois harmônicos adjacentes não se sobrepõem quando `(n + 1)·f₀ − r_Hz > n·f₀ + r_Hz`, isto é, quando `f₀ > 2·r_Hz`. Essa condição exata não depende de `n`. O limite `2,9·r_Hz` que eu havia indicado é só uma condição suficiente e conservadora.

Duas ressalvas da Luna também procedem:
- com quantis assimétricos, a condição usa os extremos efetivos dos intervalos, e não um raio simétrico;
- a dependência da ordem pode voltar não só pela modulação, mas também pela diferença de SNR local entre harmônicos vizinhos, que caem em estratos diferentes e têm intervalos diferentes.

A condição de `N(t)` será reescrita com os extremos dos intervalos em Hz de componentes adjacentes, cada um no seu estrato. A nova fórmula aguarda aprovação.

### 2.4 Estimador da fundamental

O limiar do YIN `best` escolhido em `cal` foi 0,3, pelo critério de acertos nos perfis identificáveis a 10 e 20 dB. Na partição `ver`:
- a 10 e 20 dB, o erro entre as estimativas disponíveis ficou em até 1,2%, com disponibilidade de 99% a 100%;
- a 5 dB, no perfil de terceiro harmônico dominante, o erro subiu para 7,4%, contra 5,1% com o limiar 0,2.

O critério de seleção não controla o erro abaixo de 10 dB. Proponho acrescentar um teto para a taxa de erro entre as estimativas disponíveis, fixado antes da rodada final. Pela decisão da Luna, o limiar 0,2 não será promovido com base nessa comparação, que vem da partição `ver`. O 0,3 fica provisório. Antes da rodada final, serão fixados por SNR e perfil: o teto de erro, a disponibilidade mínima e a regra de indisponibilidade abaixo da SNR mínima, contando os quadros agrupados por sinal. A escolha final será feita em `cal` e verificada em sementes inéditas.

No caso ambíguo (só ordens pares), o YIN `best` 0,3 devolveu o período do sinal ou ficou indisponível em 88% a 100% dos quadros. A saída compatível com a subarmônica ficou em até 7%, sem ser contada como erro.

### 2.5 Detecção

- Com limiar de 10 dB e janela de 1 s, a taxa de detecção dos componentes resolvidos foi de 17% a 0 dB, 56% a 10 dB e 90% a 20 dB. Os falsos picos ficaram entre 0,5 e 0,9 por quadro.
- Com janela de 0,5 s, há menos falsos picos (0,15 a 0,55 por quadro), mas a detecção é menor (67% a 20 dB).
- Na janela de 1 s, 27% dos componentes ficaram "não resolvidos". São sobretudo ordens altas com modulação, cuja excursão de frequência na janela passa de 45% da separação entre componentes.

## 3. Situação

| Item | Estado |
|---|---|
| Busca exata de atribuições | Fatoração protegida e verificação reproduzível (`verify_d1.py`); aguarda aprovação definitiva |
| Matriz `Σ` | Código implementa diagonal mais modo comum; plano v0.3.1 apresenta as opções (a) e (b); aguarda decisão |
| Incerteza por quantis em Hz | Aceita pela Luna como candidata; transformação para `ln f` corrigida para partir de `f_est`; confirmação exige sementes inéditas |
| Rodada final do Bloco 1 | Em espera, até essas decisões |
| Bloco 2 | Bloqueado |
| Dados reais | Bloqueados |

Generated by Claude
