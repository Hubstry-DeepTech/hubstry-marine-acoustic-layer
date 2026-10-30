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

- nova matriz `lab/bench/matrix_v04.json`, gerada por `make_matrix.py` com semente nova, a ser sorteada e registrada no ato do congelamento (por exemplo, a partir do hash do commit de congelamento);
- a matriz da v0.3.1 continua existindo e não é sobrescrita;
- o desenvolvimento de receptores, a partir de agora, usa apenas sementes de desenvolvimento declaradas e disjuntas das matrizes de avaliação.

## 4. Relatório obrigatório

Para cada modo e cada condição de B3:
- recuperação exata, número de erros grosseiros (|erro| > 1/T) e RMS/ACRB em todos os SNR de −10 a +30 dB, inclusive 16 e 18 dB;
- os mesmos números no hold-out, quando houver ensaios de desenvolvimento na matriz;
- a referência idealizada de probabilidade de erro, ao lado da taxa observada.

## 5. Receptor a submeter

O receptor a submeter à v0.4 deve ser declarado e congelado **antes** da execução sobre a nova matriz. Candidato em avaliação: a v3 experimental (`ReceiverV3` em `lab/bench/receiver.py`). Ela faz a seleção nas 159 candidatas como a v1, refina com máximo global na janela, rejeita canais mais de 10 dB abaixo do maior pico do espectro (o primeiro lóbulo lateral da janela retangular fica em −13,3 dB) e usa no modo com piloto o estimador de mínimos quadrados da v2.

Nos testes de desenvolvimento com sementes fora de qualquer matriz de avaliação (91.000.000 e 92.000.000 em diante):
- a 16 dB, 3 erros grosseiros em 1.000 ensaios por modo, compatível com a referência idealizada;
- a 18 dB, RMS/ACRB de 1,04 (hf) e 1,07 (lf), sem erros grosseiros;
- os 158 pontos médios de B7b rejeitados nos dois modos.

Esses números são de desenvolvimento e não substituem a execução confirmatória.

## 6. Pendências antes do congelamento

1. Revisão da Luna sobre este rascunho.
2. Decisão do Guilherme sobre o receptor a submeter (v2 ou v3).
3. Geração e registro da semente da nova matriz no commit de congelamento.
4. Execução definitiva nos dois modos, com a regra agregada aplicada por `aggregate.py` com verificação de metadados.
