---
title: "Errata e nota de revisão — Mapeamento Harmônico Racional de Vocalizações Cetáceas: Protocolo HMAL e Aplicações em Bioacústica Subaquática"
subtitle: "Versão 1.0.1 do preprint (substitui a leitura da versão 1.0.0 nos pontos indicados)"
author: "Guilherme Gonçalves Machado — Hubstry Deep Tech, Rio de Janeiro, Brasil — ORCID 0009-0008-1083-0784"
date: "01 de novembro de 2026"
lang: pt-BR
---

# 1. Natureza desta versão

Esta versão 1.0.1 é uma errata da versão 1.0.0 do preprint, depositada no Zenodo em 14 de maio de 2026 (DOI da versão 1.0.0: https://doi.org/10.5281/zenodo.20184616).

A versão 1.0.1 é depositada como nova versão do mesmo registro e contém dois arquivos: esta nota de errata e o PDF integral da versão 1.0.0, sem alterações. O manuscrito não foi reescrito. Nos pontos listados abaixo, a leitura correta passa a ser a desta nota. Os demais pontos devem ser lidos com as ressalvas da Seção 4.

As correções resultam de uma auditoria interna do projeto, realizada entre outubro e novembro de 2026. A auditoria reconstruiu o HMAL (Hubstry Marine Acoustic Layer, camada acústica marinha da Hubstry) sobre bases verificáveis:

- pré-registro com regras de decisão fixadas antes da análise;
- bancada digital com critérios congelados por resumo criptográfico;
- reprodução independente de um índice bioacústico publicado;
- registro versionado de fontes, ainda em revisão.

A auditoria mostrou que parte dos resultados empíricos da versão 1.0.0 não tem sustentação verificável. Esses resultados são aqui retirados, e não apenas corrigidos.

# 2. Resultados retirados

## 2.1 Percentuais de cobertura em H₁₆ (Resumo; Tabela 1; Tabela 2; Seção 4.4; Seção 6)

A versão 1.0.0 afirma que mais de 87% das frequências fundamentais de baleias-azuis e mais de 84% das de golfinhos-nariz-de-garrafa podem ser aproximadas por elementos de H₁₆ com erro relativo inferior a 200 ppm (partes por milhão). Também apresenta percentuais por classe vocal (Tabela 2) e uma medida de robustez superior a 78% (Seção 4.4). Todos esses resultados são retirados, pelas três razões seguintes.

**a) A origem dos dados não está estabelecida.** A própria versão 1.0.0, na caixa "Pendente de verificação" da Seção 3.1, declara que os tamanhos de amostra (n ≈ 1.247 e n ≈ 3.891) são estimativas obtidas durante processamento computacional. Declara também que eles não foram confirmados por consulta direta aos repositórios NOAA PMEL e OBIS-SEAMAP, conforme o protocolo de acesso de cada repositório. Sem acesso documentado aos arquivos de áudio, sem a lista dos segmentos analisados e sem o código executado sobre eles, os percentuais não podem ser atribuídos a dados medidos. Pelo mesmo motivo, a afirmação de que um conjunto de dados foi publicado sob CC BY 4.0 no Zenodo (Seção 5) fica suspensa até a publicação de um depósito com DOI próprio.

**b) Não há modelo nulo.** Uma taxa de encaixe só tem significado quando comparada com a taxa esperada ao acaso, que depende do intervalo de frequências, da distribuição de referência e da tolerância. A versão 1.0.0 não apresenta essa comparação. O conjunto H₁₆ contém 159 razões distintas, 79 delas no intervalo de 0,4 a 1,6. Como referência ilustrativa, sob distribuição log-uniforme nesse intervalo e tolerância relativa de 200 ppm, a união dos intervalos de aceitação cobre cerca de 2,25% do domínio. O valor foi obtido por cálculo direto e confirmado por simulação com 200 mil sorteios. Ele caracteriza apenas esse modelo nulo e não constitui uma taxa universal de encaixe ao acaso. Ainda assim, mostra que um resultado de 87% exigiria dados rastreáveis, procedimento documentado e comparação explícita com um modelo nulo justificado.

**c) A tolerância de 200 ppm não está fundamentada.** Dois problemas aparecem na Seção 3.2:

- A tolerância é justificada pela diferença mínima perceptível (JND, just-noticeable difference) de Tursiops truncatus, de 0,2% a 0,4%. Esse valor foi medido em golfinhos-nariz-de-garrafa, na faixa de quilohertz, e não se aplica a frequências de 25 Hz nem a vocalizações de outra espécie. Além disso, um limiar de percepção animal não equivale à incerteza de um estimador espectral aplicado a gravações. A JND citada, portanto, não fundamenta a tolerância adotada.
- A resolução espectral declarada, de cerca de 3,9 Hz, corresponde a cerca de 156.000 ppm de uma frequência de 25 Hz, e não a 156 ppm. Uma tolerância de 200 ppm em 25 Hz equivale a 0,005 Hz, cerca de 780 vezes menos que o espaçamento declarado. Estimadores que interpolam entre pontos do espectro podem, em princípio, alcançar precisão menor que esse espaçamento. Isso, porém, exigiria especificar o método e calibrá-lo com sinais sintéticos em condições equivalentes de relação sinal-ruído, modulação, janela e duração. Na ausência dessa demonstração, a tolerância de 200 ppm não está validada.

## 2.2 Conclusão (Seção 6)

A frase "Demonstramos que vocalizações de baleias-azuis e golfinhos-nariz-de-garrafa podem ser representadas" em H₁₆ é retirada, pelas razões da Seção 2.1 desta errata.

# 3. Afirmações corrigidas

## 3.1 Cardinalidade de H_N (Seção 2.1, Equação 1; Tabela 3)

A versão 1.0.0 informa |H₁₆| = 255 e |H₃₂| = 1.023, com crescimento da ordem de N²/ln N. Com a definição da própria Equação 1, H_N = {a/b : 1 ≤ a, b ≤ N, mdc(a, b) = 1}, os valores corretos são |H₁₆| = 159 e |H₃₂| = 647. O crescimento é assintoticamente (6/π²)·N². Os valores foram conferidos por contagem exaustiva em código. O registro relacionado HPG 1.0 (DOI 10.5281/zenodo.18652888) contém o mesmo tipo de erro (|H₁₆| = 80, que conta apenas as frações menores ou iguais a 1) e será corrigido em versão própria.

## 3.2 Estrutura harmônica das vocalizações (Seção 1)

A versão 1.0.0 afirma que a estrutura harmônica dos cantos "não é acidental" e "maximiza a eficiência energética". Componentes em múltiplos inteiros de uma frequência fundamental são consequência física de qualquer sinal periódico. Por isso, harmônicos de uma mesma vocalização não constituem evidência de organização biológica especial. A afirmação é retirada. A hipótese de vantagem de propagação, se mantida, exigirá formulação e teste próprios.

## 3.3 Modos normais de propagação (Seção 2.3)

A versão 1.0.0 afirma que os modos normais de propagação acústica subaquática "são, por construção, séries harmônicas" e que os canais (a/b)·f₀ correspondem a modos normais reais. A afirmação é incorreta. Em um guia de onda oceânico, os modos normais são componentes do campo acústico obtidos da equação de Helmholtz. Eles dependem da geometria, das condições de contorno e do perfil de velocidade do som, e não são múltiplos racionais de uma frequência fundamental do canal. A afirmação é retirada, junto com a qualificação de H_N como espaço de canais "fisicamente nativo" ao meio.

## 3.4 Período de sincronização (Seção 2.3, Equação 4)

A versão 1.0.0 define T_sync = mmc(b₁, …, b_K)/f₀ (Equação 4) e afirma que, para denominadores b_k ≤ 16 e até quatro canais simultâneos, T_sync permanece inferior a 2,8 s com f₀ = 25 Hz. A afirmação é falsa. Com a própria Equação 4 e denominadores 11, 13, 15 e 16, T_sync = 34.320/25 = 1.372,8 s, ou cerca de 22 minutos e 53 segundos.

A Equação 4 permanece válida: mmc(b₁, …, b_K)/f₀ é um período comum a todos os canais, isto é, um instante em que todos se realinham. Para frequências f_k = (a_k/b_k)·f₀, com cada fração reduzida, o menor período comum é mmc(b₁, …, b_K)/(mdc(a₁, …, a_K)·f₀). Os dois coincidem quando o máximo divisor comum dos numeradores é 1, e o valor da Equação 4 é um múltiplo inteiro do menor período nos demais casos.

O termo "codas", usado na comparação com ritmos de vocalização, designa padrões rítmicos de cliques de cachalotes, e não vocalizações de baleias-azuis.

## 3.5 Métrica de prioridade e adequação bioacústica (Resumo; Seção 5.1; Tabela 3)

A afirmação de que a função de prioridade P(a/b) = 1/(a + b) "correlaciona-se com harmônicos biologicamente relevantes" passa a ser uma hipótese não testada. A própria Seção 4.2 da versão 1.0.0 já a tratava assim. O mesmo vale para:

- a associação entre estresse e deslocamento de P(a/b) (Seção 5.1);
- a qualificação "fit bioacústico nativo" (Tabela 3).

P(a/b) permanece apenas como função de pontuação de engenharia, que ordena canais por complexidade racional. O termo "métrica", usado na versão 1.0.0, não deve ser lido no sentido matemático estrito.

## 3.6 Referência de exposição acústica (Seção 5.4)

A versão 1.0.0 apresenta como "limiar de segurança" uma emissão restrita a 180 dB re 1 µPa a 1 m, atribuída a NMFS-OPR-55. A referência é retirada, por três razões:

- Um valor a 1 m da fonte é um nível de fonte. A orientação técnica do NMFS (National Marine Fisheries Service, Serviço Nacional de Pesca Marinha dos Estados Unidos) trata de níveis recebidos pelos animais e de critérios de exposição auditiva, que são grandezas diferentes.
- A orientação citada foi atualizada em outubro de 2024 (versão 3.0, NMFS-OPR-71).
- A orientação atual diferencia critérios por grupo auditivo e por tipo de fonte, com métricas de exposição próprias.

Nenhum valor substituto é apresentado nesta nota. Um critério de exposição só poderá ser indicado com identificação do grupo auditivo, do tipo de fonte, da ponderação em frequência e da métrica aplicável.

# 4. O que permanece da versão 1.0.0

Permanecem como proposta de engenharia, sem validação empírica:

- a definição do protocolo, com o dicionário H_N como conjunto de canais de comunicação;
- a função de pontuação P(a/b) como critério de prioridade de canais;
- a definição de T_sync, com os valores corrigidos acima.

As seções de capacidade de canal (Seção 3.3), integração semântica (Seção 5.2) e segurança (Seção 5.3) não foram reavaliadas nesta errata e devem ser lidas como proposta conceitual.

# 5. Estado atual do projeto

O HMAL prossegue com procedimentos verificáveis, documentados no repositório público do projeto. Os links abaixo apontam para os artefatos no commit `8d6091f` da branch principal, de 01/11/2026:

- **Pré-registro exploratório, versão 1.3.1-draft, ainda não congelado.** Lista ordenada e fixa de pares vocais candidatos, com prazos de decisão. Exige grandezas físicas comparáveis e identificação independente dos eventos. Proíbe usar harmônicos de uma mesma vocalização como evidência de relações entre unidades vocais distintas. Exige modelo nulo para qualquer afirmação de encaixe em H_N. Arquivo: https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer/blob/8d6091f1c613aa8bb0267705f7de1470bc69923a/lab/PREREGISTRATION.md
- **Bancada digital do protocolo de comunicação.** Ensaios com sinais sintéticos, sob critérios congelados na versão 0.4.0, com manifesto de congelamento por SHA-256 (https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer/blob/8d6091f1c613aa8bb0267705f7de1470bc69923a/lab/bench/FREEZE_v0.4.json). A execução confirmatória no GitHub Actions (https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer/actions/runs/41231673988) resultou no nível 4 de maturidade tecnológica (TRL 4), em autoavaliação, restrito ao subsistema computacional. Não há validação em campo nem em meio aquático. Relatório: https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer/blob/8d6091f1c613aa8bb0267705f7de1470bc69923a/lab/bench/results/v04-run41231673988/REPORT_V04.md; errata dos critérios: https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer/blob/8d6091f1c613aa8bb0267705f7de1470bc69923a/lab/bench/ERRATA_v0.4.md
- **Ensaio E1.** Reimplementação independente do cálculo do índice de canto B de baleia-azul publicado pelo MBARI (Monterey Bay Aquarium Research Institute), com dados públicos sob CC BY 4.0. O resultado é concordância numérica com os valores publicados, e não replicação de um resultado biológico. Resultado: https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer/blob/8d6091f1c613aa8bb0267705f7de1470bc69923a/lab/bench/results/e1/E1.json

Os resultados enumerados nesta seção não utilizam os percentuais retirados nesta nota.

# 6. Declaração

O autor agradece a revisão interna que identificou os problemas aqui corrigidos. Os resultados empíricos retirados nesta errata não foram verificados contra os dados originais antes da publicação. As versões seguintes do projeto adotam como regra que nenhum resultado empírico é publicado sem dados rastreáveis, código executável e verificação independente.
