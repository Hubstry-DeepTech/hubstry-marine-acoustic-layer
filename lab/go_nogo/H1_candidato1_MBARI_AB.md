# Registro de GO/NO-GO — candidato 1 de H1: Pacífico Nordeste, chamados A e B (MBARI)

**Pré-registro:** `lab/PREREGISTRATION.md`, versão 1.3.1-draft, Seções 2.1, 2.2, 3.2 e 10.1 · **Prazo do candidato:** 02/11/2026, 23:59, horário de Brasília · **Data do registro:** 01/11/2026 · **Decisão:** **NO-GO nesta versão** · **Estado:** rascunho para revisão da Luna; a decisão vale quando o Guilherme fizer o merge antes do prazo.

## 1. A regra aplicada

O pré-registro classifica o par A/B como "presumivelmente NO-GO". Ele só passa se houver uma justificativa física independente, publicada e operacionalizável, anterior a qualquer projeção no dicionário `H_N`, mostrando que existe uma mesma grandeza mensurável nos dois chamados. A Seção 3.2 admite uma única alternativa: uma hipótese mecanística independente que justifique a razão entre grandezas distintas. O pré-registro também proíbe dividir a taxa de repetição de pulsos (`PRR`) pela frequência fundamental (`f0`) por conveniência dimensional. Sem essa justificativa documentada até o prazo, o resultado é NO-GO nesta versão.

A decisão foi tomada só com documentação acústica, acesso, identificação e comparabilidade. Não foram consultados `H_N`, `D_log`, `Δ(q)` nem `P(a/b)`, e nenhum áudio foi aberto.

## 2. Evidência consultada

Os códigos `Sxx` e `Cxx` remetem ao registro de fontes (`lab/sources/`, PR #14).

| Fonte | O que sustenta | Conferência |
|---|---|---|
| Lewis e Širović (2018), S06 | Caracterização usada pelo pré-registro: A pulsado (`PRR`) e B tonal (`f0`) | Fonte do pré-registro |
| Documentação MBARI Blue B Call Index | O índice do chamado B mede energia em bandas e o pico do terceiro harmônico; não identifica eventos A/B nem fornece `f0` | Fonte do pré-registro |
| Rice et al. (2022), S01, C01 a C03 | No chamado A, mede-se a frequência de pico média do sobretom dominante; no B, o pico do terceiro harmônico. A modulação de amplitude do chamado A pode deslocar a frequência medida no sobretom sem mudança da portadora | Texto integral |
| McDonald et al. (2001), S03, C05 | A componente de 90 Hz do chamado A não é harmônico da energia perto de 16 Hz | Texto integral |
| Moore (1999), S09, C06 | Segundo relato secundário, afirmaria o contrário: 90 Hz seria o quinto harmônico de uma fundamental perto de 18 Hz | Pendente de conferência integral; não é usada como evidência independente |
| Dziak et al. (2017), S02, C04 | Modelo de produção do chamado B por pulsos pneumáticos; é modelo proposto | Só o resumo |

## 3. Justificativa

1. **Fundamento suficiente: falta a justificativa exigida.** Até o prazo, não foi apresentada justificativa física independente para tratar `PRR` do chamado A e `f0` do chamado B como a mesma grandeza (Seção 2.1). Também não foi apresentada hipótese mecanística publicada que justifique a razão entre essas grandezas diferentes (Seção 3.2). Isso basta para o NO-GO. Não é preciso demonstrar que uma relação entre elas não possa existir. Ter a mesma dimensão inversa do tempo não torna as grandezas comparáveis.
2. **A alternativa examinada também não cumpre a regra.** A Luna propôs considerar a frequência de pico de um componente espectral em cada chamado, seguindo a medição de Rice et al. (2022). A proposta é razoável como pergunta, mas não atende ao critério:
   - Rice et al. empregam regras de seleção específicas para cada chamado: o sobretom dominante em A e o terceiro harmônico em B, este por concentrar normalmente mais energia e ser registrado de forma mais consistente. As duas medidas são expressas em Hz, mas o artigo analisa os chamados em separado, não estabelece equivalência física entre as componentes selecionadas e não propõe razão entre elas;
   - no chamado A, a modulação de amplitude é um possível fator de confusão. Rice et al. indicam que ela pode explicar parte da mudança medida no sobretom sem mudança da portadora, e sugerem medir as duas grandezas para investigar isso; não demonstram que ocorra (C03);
   - a natureza da componente de 90 Hz do chamado A é tema de divergência: McDonald et al. (2001) afirmam que ela não é harmônico da energia perto de 16 Hz (C05). A posição contrária atribuída a Moore (1999) ainda não foi conferida no texto integral (C06). A divergência é contexto, e não fundamento do NO-GO.
3. **Adotá-la agora seria uma alteração pós-especificação, com risco de seleção.** As médias publicadas de A e de B por ano foram lidas pela equipe durante esta avaliação. Não houve consulta a `H_N`, `D_log`, `Δ(q)` ou `P(a/b)`, e a razão não foi calculada. Mas definir agora a variável, depois dessa exposição, introduziria risco de escolha pós-hoc. Esse risco precisa ser declarado e controlado numa emenda, e não absorvido numa decisão de prazo.
4. **Trocar a variável exige emenda.** O pré-registro proíbe substituir variável sem versão e emenda. A troca de `PRR` por frequência de pico no chamado A não pode ser feita por decisão de prazo.

## 4. Divergência registrada

Em 01/11/2026, a Luna recomendou primeiro suspender o NO-GO e fazer uma auditoria de viabilidade com o áudio do MBARI, avaliando a frequência de pico como variável comum. O Claude recomendou o NO-GO pelos motivos da Seção 3. Depois de revisar o registro, a Luna concordou com o NO-GO nesta versão. Ela esclareceu que a auditoria dos áudios era uma proposta de investigação exploratória, e não justificativa para aprovar o par. Segundo ela, essa auditoria pode embasar uma emenda futura, mas não substituir retroativamente a variável registrada. A divergência está resolvida. A decisão final é do Guilherme, pelo merge antes do prazo.

## 5. Consequências

- **Alcance:** o NO-GO não refuta H1. Ele significa que este par, com as variáveis e a justificativa hoje registradas, não é operacionalizável nesta versão.
- **Seleção:** passa-se ao candidato 2, Chagos, unidades 2 e 3, com prazo em 04/11/2026, 23:59. Nenhum par novo é incluído.
- **Se os três candidatos forem NO-GO:** o resultado será `H1_NOT_OPERATIONALIZABLE_THIS_PHASE`, conforme a Seção 10.1. Os blocos B, C e D da checklist ficam `N/A`, e o Nível 1 pode ser congelado como protocolo de viabilidade.
- **Para uma emenda futura (v1.4):** a rota da frequência de pico fica registrada como candidata. A emenda deve:
  - declarar que as médias publicadas já são conhecidas;
  - fixar antes qual componente medir em cada chamado;
  - testar, com sinais sintéticos, o viés da modulação de amplitude no pico do chamado A;
  - usar dados de anos não consultados na escolha.
- **Exploração futura, fora desta decisão:** investigar nos áudios a portadora, o sobretom dominante e a modulação de amplitude de A e os componentes de B, com critérios definidos antes. O resultado pode embasar a emenda, mas não altera esta decisão de elegibilidade.

## 6. Checklist do Nível 1, bloco A, para este candidato

- [x] Decisão registrada antes do prazo individual.
- [x] Decisão tomada sem consultar `H_N`, `D_log`, `Δ(q)` ou `P(a/b)`.
- [x] O par A/B do MBARI não foi tratado como comparável sem justificativa física independente.
- [x] Nenhum candidato posterior foi usado como substituto após observação de resultados.

Generated by Claude
