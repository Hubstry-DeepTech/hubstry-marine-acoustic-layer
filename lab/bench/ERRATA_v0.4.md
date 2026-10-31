# Errata da v0.4

## 31/10/2026: rejeições de canal verdadeiro abaixo de 16 dB

**Afirmação errada:** "nenhuma rejeição de canal verdadeiro" pela regra de dominância de −10 dB do receptor v3, "em toda a grade de SNR".

**Onde apareceu:**
- `lab/bench/results/dev-v3-run41188079573/REPORT_V3_DEV.md`, item 1 dos riscos: corrigido no próprio arquivo, com remissão a esta errata;
- `lab/BENCH_CRITERIA_v0.4.md`, Seção 7, último item ("nenhuma rejeição de canal verdadeiro"). O arquivo é protegido pelo congelamento (`FREEZE_v0.4.json`) e **não foi alterado**: qualquer mudança nele invalidaria a verificação do congelamento. A frase é descritiva, sobre a validação de desenvolvimento, e não faz parte dos critérios de aprovação. Esta errata prevalece sobre ela;
- na mensagem de pedido de congelamento enviada à revisora (Luna), item 1.

**O que os dados mostram** (`diagnostic_rejection_rate`, B3, todas as condições, os dois modos):

| SNR integrada | Desenvolvimento (41188079573) | Confirmatória (41231673988) |
|---|---|---|
| de −10 a 14 dB | de 0 a 17 por mil, conforme a condição | de 0 a 15 por mil, conforme a condição |
| 16 dB | 0 | 1 por mil, só em lf, par mais próximo 14/15 e 15/16 |
| 18 dB ou mais | 0 | 0 |

Com sinal fraco, o maior pico do espectro tende a ser de ruído. Quando a potência no canal escolhido fica mais de 10 dB abaixo desse pico, a v3 rejeita o canal em vez de aceitar uma identificação duvidosa. É o comportamento esperado da regra, e o risco registrado em `RECEIVER_V3.md` (canal verdadeiro fraco) se materializa nesse regime.

**Origem do erro:** a conferência de desenvolvimento imprimiu as taxas de rejeição a 16 dB, a 18 dB e o máximo a partir de 20 dB, e o texto generalizou para a grade inteira.

**Efeito sobre o resultado:** nenhum. Os critérios de aprovação do B3 valem a partir de 20 dB (recuperação ≥ 99% e RMS/ACRB ≤ 1,5), onde não houve rejeição nem nas rodadas de desenvolvimento nem na confirmatória. Os dados completos estão em `diagnostic_rejection_rate` de cada `B3.json`.
