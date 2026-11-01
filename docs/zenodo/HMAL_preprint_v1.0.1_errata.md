---
title: "Errata e nota de revisão — Mapeamento Harmônico Racional de Vocalizações Cetáceas: Protocolo HMAL e Aplicações em Bioacústica Subaquática"
subtitle: "Versão 1.0.1 do preprint (substitui a leitura da versão 1.0.0 nos pontos indicados)"
author: "Guilherme Gonçalves Machado — Hubstry Deep Tech, Rio de Janeiro, Brasil — ORCID 0009-0008-1083-0784"
date: "01 de novembro de 2026"
lang: pt-BR
---

# 1. Natureza desta versão

Esta versão 1.0.1 é uma errata da versão 1.0.0 do preprint, depositada no Zenodo em 14 de maio de 2026. O texto da versão 1.0.0 permanece disponível no histórico de versões do registro, para fins de rastreabilidade. Nos pontos listados abaixo, a leitura correta passa a ser a desta errata.

As correções resultam de uma auditoria interna do projeto, realizada entre outubro e novembro de 2026. A auditoria reconstruiu o HMAL (Hubstry Marine Acoustic Layer, camada acústica marinha da Hubstry) sobre bases verificáveis:

- pré-registro com regras de decisão fixadas antes da análise;
- bancada digital com critérios congelados por resumo criptográfico;
- reprodução independente de um índice bioacústico publicado;
- registro versionado de fontes.

A auditoria mostrou que parte dos resultados empíricos da versão 1.0.0 não tem sustentação verificável. Esses resultados são aqui retirados, e não apenas corrigidos.

# 2. Resultados retirados

## 2.1 Percentuais de cobertura em H₁₆ (Resumo; Tabela 1; Tabela 2; Seção 4.4; Seção 6)

A versão 1.0.0 afirma que mais de 87% das frequências fundamentais de baleias-azuis e mais de 84% das de golfinhos-nariz-de-garrafa podem ser aproximadas por elementos de H₁₆ com erro relativo inferior a 200 ppm (partes por milhão). Também apresenta percentuais por classe vocal (Tabela 2) e uma medida de robustez superior a 78% (Seção 4.4). Todos esses resultados são retirados, pelas três razões seguintes.

**a) A origem dos dados não está estabelecida.** A própria versão 1.0.0, na caixa "Pendente de verificação" da Seção 3.1, declara que os tamanhos de amostra (n ≈ 1.247 e n ≈ 3.891) são estimativas obtidas durante processamento computacional. Declara também que eles não foram confirmados por consulta direta aos repositórios NOAA PMEL e OBIS-SEAMAP, conforme o protocolo de acesso de cada repositório. Sem acesso documentado aos arquivos de áudio, sem a lista dos segmentos analisados e sem o código executado sobre eles, os percentuais não podem ser atribuídos a dados medidos. Pelo mesmo motivo, a afirmação de que um conjunto de dados foi publicado sob CC BY 4.0 no Zenodo (Seção 5) fica suspensa até a publicação de um depósito com DOI próprio.

**b) Não há modelo nulo.** O dicionário H₁₆ é denso. Uma frequência qualquer pode ser aproximada por algum de seus elementos, de modo que uma taxa alta de encaixe não demonstra, por si, estrutura biológica. Como referência, calculamos a cobertura esperada ao acaso. Razões sorteadas com distribuição log-uniforme entre 0,4 e 1,6, com a mesma tolerância de 200 ppm, caem dentro dela em cerca de 2,2% dos casos (simulação com 200 mil sorteios). Um resultado de 87% seria extraordinário e exigiria dados rastreáveis, procedimento documentado e comparação explícita com o acaso.

**c) A justificativa da tolerância é inconsistente.** Dois problemas aparecem na Seção 3.2:

- A tolerância de 200 ppm (0,02%) é justificada pela diferença mínima perceptível (JND, just-noticeable difference) de Tursiops truncatus, de 0,2% a 0,4%. Esse valor é de 10 a 20 vezes maior que a tolerância adotada.
- A resolução espectral declarada, de cerca de 3,9 Hz, corresponde a cerca de 15,6% de uma frequência de 25 Hz, isto é, cerca de 156.000 ppm, e não 156 ppm. Com essa resolução, não é possível estimar frequências com precisão de 200 ppm.

## 2.2 Conclusão (Seção 6)

A frase "Demonstramos que vocalizações de baleias-azuis e golfinhos-nariz-de-garrafa podem ser representadas" em H₁₆ é retirada, pelas razões da Seção 2.1 desta errata.

# 3. Afirmações corrigidas

## 3.1 Cardinalidade de H_N (Seção 2.1, Equação 1; Tabela 3)

A versão 1.0.0 informa |H₁₆| = 255 e |H₃₂| = 1.023, com crescimento da ordem de N²/ln N. Com a definição da própria Equação 1, H_N = {a/b : 1 ≤ a, b ≤ N, mdc(a, b) = 1}, os valores corretos são |H₁₆| = 159 e |H₃₂| = 647. O crescimento é assintoticamente (6/π²)·N². Os valores foram conferidos por contagem exaustiva em código. O registro relacionado HPG 1.0 (DOI 10.5281/zenodo.18652888) contém o mesmo tipo de erro (|H₁₆| = 80, que conta apenas as frações menores ou iguais a 1) e será corrigido em versão própria.

## 3.2 Estrutura harmônica das vocalizações (Seção 1)

A versão 1.0.0 afirma que a estrutura harmônica dos cantos "não é acidental" e "maximiza a eficiência energética". Componentes em múltiplos inteiros de uma frequência fundamental são consequência física de qualquer sinal periódico. Por isso, harmônicos de uma mesma vocalização não constituem evidência de organização biológica especial. A afirmação é retirada. A hipótese de vantagem de propagação, se mantida, exigirá formulação e teste próprios.

## 3.3 Modos normais de propagação (Seção 2.3)

A versão 1.0.0 afirma que os modos normais de propagação acústica subaquática "são, por construção, séries harmônicas" e que os canais (a/b)·f₀ correspondem a modos normais reais. A afirmação é incorreta. Em um guia de onda oceânico, os modos normais são decomposições espaciais do campo acústico, com frequências de corte determinadas pela geometria e pelo perfil de velocidade do som. Eles não são múltiplos racionais de uma frequência fundamental do canal. A afirmação é retirada, junto com a qualificação de H_N como espaço de canais "fisicamente nativo" ao meio.

## 3.4 Período de sincronização (Seção 2.3)

A versão 1.0.0 afirma que, para denominadores b_k ≤ 16 e até quatro canais simultâneos, T_sync permanece inferior a 2,8 s com f₀ = 25 Hz. A afirmação é falsa. Com denominadores 11, 13, 15 e 16, T_sync = mmc(11, 13, 15, 16)/25 Hz = 1.372,8 s. O termo "codas", usado na comparação com ritmos de vocalização, designa padrões rítmicos de cliques de cachalotes, e não vocalizações de baleias-azuis.

## 3.5 Métrica de prioridade e adequação bioacústica (Resumo; Seção 5.1; Tabela 3)

A afirmação de que a métrica de prioridade P(a/b) = 1/(a + b) "correlaciona-se com harmônicos biologicamente relevantes" passa a ser uma hipótese não testada. A própria Seção 4.2 da versão 1.0.0 já a tratava assim. O mesmo vale para:

- a associação entre estresse e deslocamento de P(a/b) (Seção 5.1);
- a qualificação "fit bioacústico nativo" (Tabela 3).

P(a/b) permanece válida apenas como métrica de engenharia, de complexidade racional, para priorizar canais do protocolo.

## 3.6 Limiar de emissão (Seção 5.4)

O limiar de 180 dB re 1 µPa a 1 m, atribuído a NMFS-OPR-55, será conferido contra a versão vigente da orientação técnica do NMFS (National Marine Fisheries Service, Serviço Nacional de Pesca Marinha dos Estados Unidos). Essa orientação trabalha com limiares duplos de nível de exposição sonora e de pico. Até a conferência, o valor não deve ser usado como referência de segurança.

# 4. O que permanece da versão 1.0.0

Permanecem como proposta de engenharia, sem validação empírica:

- a definição do protocolo, com o dicionário H_N como conjunto de canais de comunicação;
- a métrica P(a/b) como critério de prioridade;
- a definição de T_sync, com os valores corrigidos acima.

As seções de capacidade de canal (Seção 3.3), integração semântica (Seção 5.2) e segurança (Seção 5.3) não foram reavaliadas nesta errata e devem ser lidas como proposta conceitual.

# 5. Estado atual do projeto

O HMAL prossegue com procedimentos verificáveis, documentados no repositório público https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer e na página https://hmal.hubstry.dev. Os principais são:

- **Pré-registro exploratório (v1.3.1).** Lista ordenada e fixa de pares vocais candidatos, com prazos de decisão. Exige grandezas físicas comparáveis e identificação independente dos eventos. Proíbe usar harmônicos de uma mesma vocalização como evidência de relações entre unidades vocais distintas. Exige modelo nulo para qualquer afirmação de encaixe em H_N.
- **Bancada digital do protocolo de comunicação.** Ensaios com sinais sintéticos, sob critérios congelados (versão 0.4.0) e execução confirmatória no GitHub Actions (execução 41231673988). O resultado é o nível 4 de maturidade tecnológica (TRL 4), em autoavaliação, restrito ao subsistema computacional. Não há validação em campo nem em meio aquático.
- **Ensaio E1.** Reprodução numérica do índice de canto B de baleia-azul publicado pelo MBARI (Monterey Bay Aquarium Research Institute), com dados públicos sob CC BY 4.0. É concordância numérica, não validação biológica.

Nenhum resultado do estado atual depende dos percentuais retirados nesta errata.

# 6. Declaração

O autor agradece a revisão interna que identificou os problemas aqui corrigidos. Os resultados empíricos retirados nesta errata não foram verificados contra os dados originais antes da publicação. As versões seguintes do projeto adotam como regra que nenhum resultado empírico é publicado sem dados rastreáveis, código executável e verificação independente.
