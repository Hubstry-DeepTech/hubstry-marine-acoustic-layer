# HMAL — Resumo executivo para a reunião COPPE/UFRJ

**Hubstry Marine Acoustic Layer | 30/10/2026 | Protocolo exploratório v1.3.1-draft**

## Pergunta

O HMAL investiga se a razão entre a mesma grandeza acústica medida em duas unidades vocais distintas pode ser descrita de modo informativo por um dicionário finito de razões racionais reduzidas (`H_N`). Harmônicos de uma mesma vocalização são excluídos como evidência: são esperados pela física de sinais periódicos.

## Protótipo e limites

O protótipo projeta uma medida/frequência observada sobre o elemento mais próximo de `H_N`, calcula erro de projeção e a métrica interna `P(a/b)=1/(a+b)`. Isso demonstra uma implementação computacional, não que cetáceos selecionem essas razões, que o mapeamento melhore a detecção ou que o HMAL seja um protocolo de comunicação submarina validado.

## Viabilidade dos dados — ordem e prazos pré-fixados

1. **Pacífico Nordeste, MBARI A/B — até 02/11/2026:** A é pulsado e B tonal; presumivelmente NO-GO, salvo justificativa física independente que torne as medidas comparáveis.
2. **Chagos, unidades 2/3 — até 04/11/2026:** ambas são descritas como tons puros, mas o depósito Zenodo disponível não contém áudio original nem medidas dessas unidades. Exige gravações autorizadas e termos verificados.
3. **Atlântico Norte, partes A/B — até 05/11/2026:** áudio, metadados, rótulos e acesso precisam ser verificados.

Sem confirmação até o prazo, o candidato é NO-GO nesta versão. Se nenhum passar, H1 será registrada como `H1_NOT_OPERATIONALIZABLE_THIS_PHASE`, sem substituição pós-hoc.

## Limite inferencial

Com uma única combinação população/variante × par vocal × temporada, `n_eff=1`. Blocos, dias e eventos repetidos melhoram a precisão, mas não criam replicação biológica independente. Portanto, esta fase não produz teste confirmatório nem valor-p biológico para H1. A comparação `H_16` versus `D_log` para uma razão isolada é geométrica/descritiva. Cramér–Rao é limite inferior sob pressupostos, não erro garantido.

## Aplicação de engenharia de curto prazo — H3

H3 investiga um possível escore de QA para apoiar a revisão de detecções do PAMGuard, distinguindo verdadeiros positivos de falsos positivos/transientes com rótulos independentes. O Guia de Monitoramento da Biota Marinha do IBAMA (2018) inclui procedimentos de Monitoramento Acústico Passivo no contexto de pesquisas sísmicas marítimas e medidas de mitigação associadas a licenças. Isso indica um contexto de aplicação potencial, não prova de demanda, conformidade ou superioridade. O HMAL não substitui PAMGuard, especialistas ou procedimentos oficiais. Fontes: [Guia IBAMA 2018](https://www.gov.br/ibama/pt-br/centrais-de-conteudo/arquivos/arquivos-pdf/2018-11-01-ibama-guia-de-monitoramento-da-biota-marinha-outubro-pdf) · [diretrizes técnicas](https://www.gov.br/ibama/pt-br/assuntos/laf/procedimentos-e-servicos/arquivos/petroleo-e-gas/diretrizes).

## Fase 2 e interlocução buscada

A fase confirmatória exige múltiplas unidades biológicas independentes, medidas comparáveis, dados/rótulos verificáveis, modelo nulo biologicamente fundamentado, simulação de poder e novo pré-registro com hash próprio. Buscamos interlocução da COPPE/UFRJ para avaliar mensuração vocal, replicação, modelos nulos e estimação em sinais submarinos.

**Resultado apresentado:** protocolo exploratório/viabilidade, pares pré-registrados, prazos de decisão e limites explícitos — não confirmação biológica nem validação em campo.