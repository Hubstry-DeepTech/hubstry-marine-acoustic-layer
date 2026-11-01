# Registro de GO/NO-GO — candidato 1 de H1: Pacífico Nordeste, chamados A e B (MBARI)

**Pré-registro:** `lab/PREREGISTRATION.md`, versão 1.3.1-draft, Seções 2.1, 2.2 e 10.1 · **Prazo do candidato:** 02/11/2026, 23:59, horário de Brasília · **Data do registro:** 01/11/2026 · **Decisão:** **NO-GO nesta versão** · **Estado:** rascunho para revisão da Luna; a decisão vale quando o Guilherme fizer o merge antes do prazo.

## 1. A regra aplicada

O pré-registro classifica o par A/B como "presumivelmente NO-GO". Ele só passa se houver uma justificativa física independente, publicada e operacionalizável, anterior a qualquer projeção no dicionário `H_N`, mostrando que existe uma mesma grandeza mensurável nos dois chamados. O pré-registro também proíbe dividir a taxa de repetição de pulsos (`PRR`) pela frequência fundamental (`f0`) por conveniência dimensional. Sem essa justificativa documentada até o prazo, o resultado é NO-GO nesta versão.

A decisão foi tomada só com documentação acústica, acesso, identificação e comparabilidade. Não foram consultados `H_N`, `D_log`, `Δ(q)` nem `P(a/b)`, e nenhum áudio foi aberto.

## 2. Evidência consultada

Os códigos `Sxx` e `Cxx` remetem ao registro de fontes (`lab/sources/`, PR #14).

| Fonte | O que sustenta | Conferência |
|---|---|---|
| Lewis e Širović (2018), S06 | Caracterização usada pelo pré-registro: A pulsado (`PRR`) e B tonal (`f0`) | Fonte do pré-registro |
| Documentação MBARI Blue B Call Index | O índice do chamado B mede energia em bandas e o pico do terceiro harmônico; não identifica eventos A/B nem fornece `f0` | Fonte do pré-registro |
| Rice et al. (2022), S01, C01 a C03 | No chamado A, mede-se a frequência de pico média do sobretom dominante; no B, o pico do terceiro harmônico. A modulação de amplitude do chamado A pode deslocar a frequência medida no sobretom sem mudança da portadora | Texto integral |
| McDonald et al. (2001), S03, C05 | A componente de 90 Hz do chamado A não é harmônico da energia perto de 16 Hz | Texto integral |
| Moore (1999), S09, C06 | Afirma o contrário: 90 Hz seria o quinto harmônico de uma fundamental perto de 18 Hz | Pendente; registrada como divergência |
| Dziak et al. (2017), S02, C04 | Modelo de produção do chamado B por pulsos pneumáticos; é modelo proposto | Só o resumo |

## 3. Justificativa

1. **A operacionalização registrada não é comparável.** `PRR` do chamado A (pulsos por segundo) e `f0` do chamado B (frequência de um componente tonal) são grandezas diferentes. Ter a mesma dimensão inversa do tempo não as torna comparáveis.
2. **A alternativa examinada também não cumpre a regra.** A Luna propôs considerar a frequência de pico de um componente espectral em cada chamado, seguindo a medição de Rice et al. (2022). A proposta é razoável como pergunta, mas não atende ao critério:
   - Rice et al. medem os dois chamados em separado e não afirmam que o pico do sobretom dominante de A e o terceiro harmônico de B sejam a mesma grandeza física;
   - a escolha de qual componente de cada chamado comparar é arbitrária, e cada escolha produz uma razão diferente;
   - no chamado A, o pico medido pode ser deslocado pela modulação de amplitude (C03), e há divergência publicada sobre a natureza harmônica da componente de 90 Hz (C05 contra C06).
3. **Adotá-la agora contaminaria a decisão.** As médias publicadas de A e de B por ano já foram lidas pela equipe durante esta avaliação. Definir agora uma variável cuja razão pode ser calculada com esses números contraria a exigência de decidir a elegibilidade sem consultar a projeção. A razão não foi calculada.
4. **Trocar a variável exige emenda.** O pré-registro proíbe substituir variável sem versão e emenda. A troca de `PRR` por frequência de pico no chamado A não pode ser feita por decisão de prazo.

## 4. Divergência registrada

A Luna recomendou, em 01/11/2026, suspender o NO-GO e fazer uma auditoria de viabilidade com o áudio do MBARI, avaliando a frequência de pico como variável comum. O Claude recomendou o NO-GO pelos motivos da Seção 3. Até a data deste registro, a Luna não havia respondido a essa contra-argumentação. A decisão final é do Guilherme. Este registro é proposto para revisão da Luna antes do merge.

## 5. Consequências

- **Seleção:** passa-se ao candidato 2, Chagos, unidades 2 e 3, com prazo em 04/11/2026, 23:59. Nenhum par novo é incluído.
- **Se os três candidatos forem NO-GO:** o resultado será `H1_NOT_OPERATIONALIZABLE_THIS_PHASE`, conforme a Seção 10.1. Os blocos B, C e D da checklist ficam `N/A`, e o Nível 1 pode ser congelado como protocolo de viabilidade.
- **Para uma emenda futura (v1.4):** a rota da frequência de pico fica registrada como candidata. A emenda deve:
  - declarar que as médias publicadas já são conhecidas;
  - fixar antes qual componente medir em cada chamado;
  - testar, com sinais sintéticos, o viés da modulação de amplitude no pico do chamado A;
  - usar dados de anos não consultados na escolha.

## 6. Checklist do Nível 1, bloco A, para este candidato

- [x] Decisão registrada antes do prazo individual.
- [x] Decisão tomada sem consultar `H_N`, `D_log`, `Δ(q)` ou `P(a/b)`.
- [x] O par A/B do MBARI não foi tratado como comparável sem justificativa física independente.
- [x] Nenhum candidato posterior foi usado como substituto após observação de resultados.

Generated by Claude
