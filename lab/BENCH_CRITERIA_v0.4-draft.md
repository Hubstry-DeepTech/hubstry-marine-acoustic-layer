# HMAL — Critérios da bancada digital, proposta de revisão v0.4

**Versão:** 0.4.0-draft · **Data:** 30/10/2026 · **Estado:** rascunho para revisão; **não** congelado e **não** aplicável a nenhuma execução até aprovação e congelamento formais

Este documento propõe mudanças sobre `lab/BENCH_CRITERIA.md` v0.3.1. Tudo o que não é citado aqui permanece idêntico à v0.3.1.

## 1. Resultado preservado sob a v0.3.1

A revisão não altera retroativamente nenhum resultado. Sob os critérios congelados v0.3.1:

- execução `41121711705` (receptor v2, commit `972beb6`): B1, B2, B4, B5 e B7 aprovados nos modos hf e lf; **B3 reprovado nos dois modos**, apenas pelo critério B3(c);
- regra agregada: **TRL 3** (`lab/bench/results/v2-run41121711705/aggregate.json`).

Esse registro permanece válido e será citado em qualquer apresentação, ao lado de qualquer resultado posterior.

## 2. Mudança proposta: B3(c) a partir de 20 dB

**Texto v0.3.1:** só para `K = 1`, erro RMS ≤ 1,5·`σ_f,ACRB` com `SNR_int ≥ 16 dB`.

**Texto proposto v0.4:** só para `K = 1`, erro RMS ≤ 1,5·`σ_f,ACRB` com `SNR_int ≥ 20 dB`. Os resultados de 10 a 18 dB continuam calculados e publicados como diagnóstico, sem critério de aprovação.

### 2.1 Por que a mudança (registro pós-resultado)

- **A revisão ocorreu depois de ver os resultados da v0.3.1.** Ela é declarada como correção pós-hoc.
- **Erro de especificação:** o corte de 16 dB foi fixado por uma estimativa incorreta do regime de limiar. A ACRB (limite de Cramér–Rao assintótico) descreve o erro local em torno do pico correto. Ela não inclui erros de ambiguidade, quando o estimador escolhe um canal errado entre as 159 candidatas. Um único erro desse tipo domina o RMS. O B3(c) da v0.3.1 misturava, portanto, eficiência de estimação e acerto de classificação.
- **Referência idealizada:** no modelo de detecção não coerente M-ária com sinais ortogonais (M = 159), a probabilidade de escolher o canal errado é de cerca de 2,3 × 10⁻³ a 16 dB, 9,8 × 10⁻⁶ a 18 dB e 1,1 × 10⁻⁹ a 20 dB, conferida de forma independente pela Luna. O dicionário `H_16` não é exatamente ortogonal: a correlação máxima entre canais é de 8,4% (hf) e 12,7% (lf). Por isso, esses valores são uma **referência sob modelo idealizado**, não um limite universal de qualquer receptor.
- **Componente do receptor:** a 16 dB, a v1 errou de 3 a 4 vezes em 1.000 ensaios, perto da referência idealizada. A v2 errou de 49 a 59 vezes. Parte da reprovação da v2 é, portanto, desempenho do receptor, e isso fica registrado.
- **Escolha de 20 dB:** é conservadora e coincide com o corte do critério B3(b). É o regime em que a referência idealizada prevê erros de ambiguidade desprezíveis em 1.000 ensaios. Não é apresentado como limite universal do HMAL.

## 3. Validação confirmatória com sementes novas

O corte de 20 dB foi escolhido depois de observar a matriz oficial. Por isso, uma aprovação sob a v0.4 só vale com **sementes nunca usadas** no desenvolvimento de receptores nem na escolha do corte:

- nova matriz `lab/bench/matrix_v04.json`, gerada por `make_matrix.py --version 0.4.0 --seed S --noise-offset O`;
- a semente `S` e o deslocamento `O` das sementes de ruído são sorteados com `secrets` (gerador criptográfico do Python) **antes** do commit de congelamento e registrados nele. Não se deriva a semente do hash do próprio commit, porque isso seria circular;
- `O` é escolhido acima de 1.000.000.000, de modo que todas as sementes de ruído (B3, B4 e B7) fiquem disjuntas da matriz v0.3.0 e das sementes de desenvolvimento (91.000.000 a 93.000.000 e a faixa de 500.000.000). Um teste automático (`tests/test_bench_tools.py`) verifica a disjunção e a reconstrução idêntica da matriz;
- a matriz da v0.3.1 continua existindo e não é sobrescrita;
- o desenvolvimento de receptores, a partir de agora, usa apenas sementes de desenvolvimento declaradas e disjuntas das matrizes de avaliação.

## 4. Relatório obrigatório

Para cada modo e cada condição de B3:
- recuperação exata, número de erros grosseiros (|erro| > 1/T) e RMS/ACRB em todos os SNR de −10 a +30 dB, inclusive 16 e 18 dB;
- os mesmos números no hold-out, quando houver ensaios de desenvolvimento na matriz;
- a referência idealizada de probabilidade de erro, ao lado da taxa observada, calculada por `lab/bench/ideal_pe.py` (o script registra seu próprio hash; com `M = 159`: 2,26 × 10⁻³ a 16 dB, 9,83 × 10⁻⁶ a 18 dB e 1,09 × 10⁻⁹ a 20 dB);
- para `K = 1`, em toda a grade de SNR, duas métricas separadas, como diagnóstico complementar sem efeito na decisão:
  - taxa de erro de identificação de canal, P(canal incorreto | SNR);
  - RMS condicionado à identificação correta, dividido pela ACRB.

  O RMS global continua sendo o critério B3(c) e continua publicado, porque mostra o efeito conjunto das duas falhas. O RMS condicional nunca substitui a taxa de erro de identificação, pois excluiria justamente os ensaios que revelam as falhas mais graves.

## 5. Receptor a submeter

O receptor a submeter à v0.4 deve ser declarado e congelado **antes** da execução sobre a nova matriz. Receptor escolhido por Guilherme Machado em 31/10/2026: a v3 (`ReceiverV3` em `lab/bench/receiver.py`). Ela faz a seleção nas 159 candidatas como a v1, refina com máximo global na janela, rejeita canais mais de 10 dB abaixo do maior pico do espectro (o primeiro lóbulo lateral da janela retangular fica em −13,3 dB) e usa no modo com piloto o estimador de mínimos quadrados da v2.

Nos testes de desenvolvimento com sementes fora de qualquer matriz de avaliação (91.000.000 e 92.000.000 em diante):
- a 16 dB, 3 erros grosseiros em 1.000 ensaios por modo, compatível com a referência idealizada;
- a 18 dB, RMS/ACRB de 1,04 (hf) e 1,07 (lf), sem erros grosseiros;
- os 158 pontos médios de B7b rejeitados nos dois modos.

Esses testes cobrem só `K = 1` e B7b. Os demais ensaios (B2, B3 com `K = 2` e `3`, B4 com piloto) ainda não foram verificados para a v3; os riscos estão em `lab/bench/RECEIVER_V3.md`. Esses números são de desenvolvimento e não substituem a execução confirmatória.

Comparação v1 × v2 sob a v0.3.1, com os dados por ensaio: `lab/bench/results/REPORT_v1_v2.md`.

## 6. Protocolo de congelamento

1. Validação de desenvolvimento completa da v3 numa matriz com semente declarada, disjunta da oficial (`lab/bench/RECEIVER_V3.md`). Ela serve para descobrir falhas antes do congelamento, não para aprovar.
2. Revisão da Luna sobre o código da bancada (`run_bench.py`, `make_matrix.py`, `aggregate.py`, `receiver.py`, `ideal_pe.py`, `bench.yml`) e sobre o resultado da validação de desenvolvimento.
3. Sorteio de `S` e `O` com `secrets`, geração de `matrix_v04.json` e registro do SHA-256 da matriz.
4. **Commit de congelamento** contendo, ao mesmo tempo:
   - este documento renomeado para `lab/BENCH_CRITERIA_v0.4.md`, com estado "congelado";
   - `matrix_v04.json`;
   - `lab/bench/FREEZE_v0.4.json`, gerado por `freeze.py create`, com receptor, versão dos critérios, arquivo, SHA-256, semente e deslocamento da matriz, o SHA-256 de cada arquivo protegido (critérios, receptor, runner, agregador, junção, resolvedor, gerador da matriz, `freeze.py`, `constraints.txt`, gerador de sinais `harmonic_protocol.py` e `bench.yml`) e o ambiente esperado (Python 3.11.17, NumPy e SciPy fixados em `constraints.txt`, glibc).

   O congelamento é verificado por código, e não só registrado: `freeze.verify_freeze()` roda em `resolve_run.py` antes da execução, inclusive conferindo o ambiente em uso, e em `aggregate.py` antes de qualquer conclusão de TRL, conferindo também os metadados de cada modo. Qualquer divergência impede a execução ou leva a INCONSISTENT_RUNS.
5. O workflow da bancada dispara só pelo commit que cria `matrix_v04.json`. As execuções partem exatamente desse commit; nada é alterado durante a rodada. Cada modo roda em seis partes paralelas (B1, B2, B4, B5 e B7 numa parte; cada condição do B3 numa parte), juntadas por `merge_parts.py`, que exige configuração idêntica em todas as partes e cada ensaio e condição exatamente uma vez. A divisão não altera ensaios, limiares, matriz nem receptor.
6. `aggregate.py` só emite conclusão de TRL quando commit, receptor, versão de critérios, arquivo e SHA-256 da matriz e corte do B3(c) coincidem nos dois modos.

Nenhuma declaração de TRL 4 antes da execução confirmatória e da agregação.

## 7. Estado do código (31/10/2026, após a revisão técnica da Luna)

- `run_bench.py`:
  - opções `--receiver v3`, `--criteria 0.4.0` (matriz `matrix_v04.json`, B3(c) a partir de 20 dB), `--matrix` (só desenvolvimento, nunca definitiva) e `--out`;
  - grava nos metadados `matrix_file`, `matrix_sha256`, `matrix_seed`, `noise_seed_offset` e `b3c_min_snr_db`;
  - separa, em todas as condições de B3, três taxas: identificação incorreta (canal aceito com razão errada), rejeição ou perda (canal verdadeiro não aceito) e falha total de recuperação;
  - para `K = 1`, grava o erro de frequência de cada ensaio, o que permite recalcular de forma independente o RMS global e o RMS entre os ensaios com identificação correta e canal aceito;
  - os critérios v0.3.1 continuam executáveis sem alteração.
- `make_matrix.py`: com os valores padrão, reconstrói a matriz v0.3.0 idêntica. Uma matriz não marcada como desenvolvimento exige semente fora das já usadas (20261030, 20261031, 777001) e deslocamento de ruído ≥ 1.000.000.000.
- `aggregate.py`:
  - compara o bloco de metadados de cada artefato com o `summary.json` do seu diretório, e o veredito de cada artefato com o do resumo;
  - exige, conforme a versão de critérios, os campos obrigatórios e os valores esperados (`matrix_v04.json` e 20 dB na v0.4);
  - na v0.4, confere o SHA-256 da matriz e o receptor com `FREEZE_v0.4.json`;
  - sem congelamento registrado, não emite conclusão.
- `bench.yml` e `resolve_run.py`:
  - a rodada confirmatória só parte do push do commit de congelamento, com receptor e critérios lidos de `FREEZE_v0.4.json`;
  - o disparo manual exige semente de desenvolvimento, gera a matriz com deslocamento abaixo de 1.000.000.000, copia a matriz para o artefato e sempre marca a execução como não definitiva;
  - não há caminho manual para uma rodada definitiva.
- `tests/test_bench_integrity.py`: testes para cada um desses casos.
- Após a revisão de congelamento da Luna (31/10/2026): `permissions: contents: read` no `bench.yml`; `freeze.py` com verificação executável do congelamento; `constraints.txt` (NumPy 2.4.6, SciPy 1.17.1) e Python 3.11.17 fixados no workflow; `compare_runs.py` para equivalência automatizada entre rodadas; testes negativos em `tests/test_bench_freeze.py`.
- `merge_parts.py` e `tests/test_bench_merge.py` (31/10/2026): execução dividida em partes paralelas, porque a validação de desenvolvimento levou 5 h 04 min no modo hf, perto do limite de 340 min por job. A data da execução saiu do bloco `env`, que passa a identificar só a configuração; ela fica em `date_utc` de cada artefato e do resumo.
- Validação de desenvolvimento da v3 (`lab/bench/results/dev-v3-run41188079573/REPORT_V3_DEV.md`): seis ensaios aprovados nos dois modos, nenhuma rejeição de canal verdadeiro; não definitiva.

## 8. Pendências

1. Validação de desenvolvimento completa da v3 (passo 1 da Seção 6).
2. Revisão da Luna sobre o código e sobre essa validação.
3. Aprovação do Guilherme para o commit de congelamento.
Decisão de receptor: v3, tomada por Guilherme Machado em 31/10/2026.
