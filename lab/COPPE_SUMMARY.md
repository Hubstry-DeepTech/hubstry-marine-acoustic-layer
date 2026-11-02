# HMAL — Resumo executivo para a reunião COPPE/UFRJ

**Hubstry Marine Acoustic Layer | 01/11/2026 | Protocolo exploratório v1.3.2-draft** (versão anterior: 30/10/2026, v1.3.1-draft)

## Pergunta

O HMAL investiga se a razão entre a mesma grandeza acústica medida em duas unidades vocais distintas pode ser descrita de modo informativo por um dicionário finito de razões racionais reduzidas (`H_N`). Harmônicos de uma mesma vocalização são excluídos como evidência: são esperados pela física de sinais periódicos.

## Protótipo e limites

O protótipo projeta uma medida/frequência observada sobre o elemento mais próximo de `H_N`, calcula erro de projeção e a métrica interna `P(a/b)=1/(a+b)`. Isso demonstra uma implementação computacional, não que cetáceos selecionem essas razões, que o mapeamento melhore a detecção ou que o HMAL seja um protocolo de comunicação submarina validado.

## Viabilidade dos dados (pré-registro v1.3.2-draft)

1. **Pacífico Nordeste, MBARI A/B — NO-GO registrado em 01/11/2026** (`lab/go_nogo/H1_candidato1_MBARI_AB.md`): A é pulsado e B tonal; não há justificativa física nem hipótese mecanística independente que torne as medidas comparáveis.
2. **Chagos e Atlântico Norte — retirados na emenda 1.3.2**, antes de qualquer acesso a dados. Foram registrados sem verificação prévia da origem dos dados, das condições de acesso e do prazo de liberação. As gravações de Chagos vêm da estação HA08 da CTBTO, de acesso controlado. O Atlântico Norte não tem gravações com rótulos independentes das partes A e B.

**Resultado desta fase:** `H1_NOT_OPERATIONALIZABLE_THIS_PHASE`, sem substituição pós-hoc. A emenda criou uma regra: nenhum candidato futuro é registrado sem verificação documentada de acesso. O acesso aos dados da CTBTO e de outras fontes passa a ser o plano de dados da fase 2.

## Limite inferencial

Com uma única combinação população/variante × par vocal × temporada, `n_eff=1`. Blocos, dias e eventos repetidos melhoram a precisão, mas não criam replicação biológica independente. Portanto, esta fase não produz teste confirmatório nem valor-p biológico para H1. A comparação `H_16` versus `D_log` para uma razão isolada é geométrica/descritiva. Cramér–Rao é limite inferior sob pressupostos, não erro garantido.

## Aplicação de engenharia de curto prazo — H3

H3 investiga um possível escore de QA para apoiar a revisão de detecções do PAMGuard, distinguindo verdadeiros positivos de falsos positivos/transientes com rótulos independentes. O Guia de Monitoramento da Biota Marinha do IBAMA (2018) inclui procedimentos de Monitoramento Acústico Passivo no contexto de pesquisas sísmicas marítimas e medidas de mitigação associadas a licenças. Isso indica um contexto de aplicação potencial, não prova de demanda, conformidade ou superioridade. O HMAL não substitui PAMGuard, especialistas ou procedimentos oficiais. Fontes: [Guia IBAMA 2018](https://www.gov.br/ibama/pt-br/centrais-de-conteudo/arquivos/arquivos-pdf/2018-11-01-ibama-guia-de-monitoramento-da-biota-marinha-outubro-pdf) · [diretrizes técnicas](https://www.gov.br/ibama/pt-br/assuntos/laf/procedimentos-e-servicos/arquivos/petroleo-e-gas/diretrizes).

## Fase 2 e interlocução buscada

A fase confirmatória exige múltiplas unidades biológicas independentes, medidas comparáveis, dados/rótulos verificáveis, modelo nulo biologicamente fundamentado, simulação de poder e novo pré-registro com hash próprio. Buscamos interlocução da COPPE/UFRJ para avaliar mensuração vocal, replicação, modelos nulos e estimação em sinais submarinos.

**Resultado apresentado:** protocolo exploratório e de viabilidade; NO-GO registrado do único candidato com dados públicos (MBARI A/B); H1 não operacionalizável nesta fase; emenda que retirou os candidatos sem acesso verificado e separou prospecção de fontes de candidatura; limites explícitos. Não é confirmação biológica nem validação em campo. A fase 2 começa por uma carteira de dados com acesso efetivamente verificado.