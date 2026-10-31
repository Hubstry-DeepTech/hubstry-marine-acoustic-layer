# HMAL Lab: plano da interface pública (front-end)

**Versão:** 0.2 · **Data:** 31/10/2026 · **Estado:** aprovado pela Luna com complementos; Fase 0 implementada no ramo `docs/frontend-plan` (PR #8), aguardando revisão; evidências da v0.3.1 integradas ao `main` pelo PR #9

## 1. Objetivo

Publicar uma página que mostre, a qualquer avaliador, o que o HMAL (Hubstry Marine Acoustic Layer, camada acústica marinha da Hubstry) já demonstrou. O foco é o processo seletivo da Incubadora de Empresas da COPPE/UFRJ (Instituto Alberto Luiz Coimbra de Pós-Graduação e Pesquisa de Engenharia da Universidade Federal do Rio de Janeiro), com entrevista em 06/11/2026.

A página deve:

- exibir os resultados da bancada digital e do experimento E1 com dados reais;
- ligar cada número ao commit, à execução do GitHub Actions e à versão dos critérios que o produziram;
- servir de primeiro projeto do laboratório digital da Hubstry.

## 2. Princípios de integridade

1. **Só publica o que está no ramo `main`.** O site lê os JSON versionados no repositório. Nenhum número é digitado à mão no código da página.
2. **Proveniência em cada resultado:** commit, identificador da execução, versão dos critérios, versão da matriz e data em UTC (Tempo Universal Coordenado).
3. **TRL (Technology Readiness Level, nível de maturidade tecnológica) exatamente como o `aggregate.py` declara.** O TRL 3 da v0.3.1 continua visível ao lado de qualquer resultado posterior. Reprovações (v1 e v2 no B3) também aparecem.
4. **Sem "ao vivo" enquanto não houver dado ao vivo.** Os dados do E1 são históricos (MBARI, Monterey Bay Aquarium Research Institute, novembro de 2016) e aparecem rotulados assim.
5. **Ética visível:** link para a cláusula da licença que veda o uso para caça, captura ou perseguição de mamíferos marinhos.
6. **Maturidade sempre por componente, nunca "HMAL — TRL n".** Núcleo computacional de processamento racional: avaliação de TRL conforme a versão de critérios indicada. Comunicação acústica submarina: sem validação física da cadeia completa. Hipótese H1: hipótese científica em aberto, à qual TRL não se aplica.
7. **Dois commits por resultado.** `experiment_commit` é o código que executou o experimento; `publication_commit` é o commit do `main` que contém os resultados publicados. O tipo de execução é registrado: GitHub Actions, com o identificador da execução, ou execução manual numa VM, com data, ambiente e hashes, como no E1. Não se exige identificador de execução que não exista.
8. **Status exato do agregador**, inclusive `INCONSISTENT_RUNS` (caso da v1) e `INCOMPLETO`. A página não esconde a diferença entre a avaliação por modo e a conclusão conjunta.
9. **Dados históricos rotulados como históricos.** O E1 é a reprodução de um índice sobre gravações de novembro de 2016, não observação de baleias em tempo real. O índice CI (Call Index, índice de chamado) é uma razão de níveis espectrais e não conta vocalizações individuais.
10. **Privacidade sem afirmação absoluta.** Texto da página: "Sem formulários, cookies de rastreamento ou perfilamento. A hospedagem e os serviços de infraestrutura podem realizar registros técnicos de segurança, conforme suas políticas de privacidade." O GitHub Pages registra endereços IP dos visitantes para fins de segurança.
11. **Licenças separadas e atribuição completa.** Dados do MBARI: atribuição, link para a licença CC BY 4.0 e indicação de que foram processados e visualizados pela Hubstry. Software HMAL: BSL 1.1 (Business Source License) com concessão adicional, identificada à parte.

## 3. Escopo por fase

### Fase 0: antes de 06/11 (estimativa de 1 a 2 dias de trabalho)

| Seção | Conteúdo | Fonte dos dados |
|---|---|---|
| Início | responde em poucos segundos: o que é o HMAL (projeto de pesquisa e engenharia de processamento acústico que investiga estruturas harmônicas racionais e suas possíveis aplicações); o que já demonstrou (reprodução de um índice acústico do MBARI em três dias de gravações históricas e bancada digital com aprovações e reprovações documentadas); o que ainda não demonstrou (comunicação acústica submarina operacional, validação biológica da hipótese H1, aplicação comercial validada); maturidade por componente | `docs/SPECIFICATION.md` (texto revisado à mão, sem números) |
| Bancada digital | tabela de vereditos B1 a B7 por modo; curva de recuperação × SNR (razão sinal-ruído) por condição; curva RMS/ACRB (erro RMS, raiz do erro quadrático médio, sobre o limite de Cramér–Rao assintótico); comparação v1 × v2 | `lab/bench/results/*/` |
| E1, baleia-azul | série diária do índice de chamado B; espectrogramas dos três dias de critério; comparação com a referência do MBARI e tolerância de 2% | `lab/bench/results/e1/` |
| Metodologia | resumo de critérios, pré-registro, hold-out, correção pós-hoc da v0.4; links para os documentos | `lab/*.md` |
| Ética e licença | cláusula ética; dados CC BY 4.0 (Creative Commons Atribuição 4.0) do MBARI com crédito | `LICENSE`, `docs/ETHICS_GUIDELINES.md` |

Se a rodada definitiva da v0.4 terminar antes da entrevista, ela entra na mesma seção, ao lado da v0.3.1, só depois do merge no `main`.

**Pré-requisito:** as evidências da v0.3.1 (resultados v1 e v2, relatório, manifesto de proveniência e estado congelado dos critérios) precisam estar no `main`, pelo PR #9. Enquanto uma evidência não estiver no `main`, o build falha ou oculta a seção correspondente; ele nunca busca dados em ramos de desenvolvimento. O pré-registro aparece com o estado que o próprio documento declara (hoje `1.3.1-draft`, candidato a congelamento de nível 1).

**Fora da Fase 0:** demonstração interativa, versão inglesa completa, painel automático e animações.

### Fase 1: depois da entrevista

- Demonstração interativa do dicionário harmônico `H_16`. O visitante escolhe razões e SNR, o navegador sintetiza o sinal, calcula o espectro e mostra a decodificação. É uma reimplementação didática em JavaScript, rotulada como tal e não como o receptor oficial.
- Versão em inglês.

### Fase 2: painel periódico com dados reais

- Um job agendado do GitHub Actions processa um dia recente do arquivo público do MBARI e publica o índice no site. A frequência é diária, conforme a defasagem real de publicação do arquivo, que precisa ser verificada antes.
- O rótulo será "atualizado diariamente com defasagem de N dias", nunca "ao vivo".

### Fase 3

- Integração ao site do laboratório digital da Hubstry, com outras linhas de pesquisa.

## 4. Arquitetura

- **Site estático, sem servidor de aplicação e sem banco de dados.** O custo é zero e não há superfície de ataque além da hospedagem.
- **Pipeline de dados:** `site/build_data.py` lê `lab/bench/results/MANIFEST.json` e os resultados versionados e gera `site/public/data/*.json` reduzidos, com esquema validado e bloco de proveniência (caminho do JSON, SHA-256, `experiment_commit`, `publication_commit`, tipo e identificador de execução). O status de maturidade vem da execução do próprio `aggregate.py` sobre os artefatos; a regra não é duplicada em JavaScript.
- **Front-end:** HTML, CSS e TypeScript com Vite (ferramenta de build); gráficos com Observable Plot (biblioteca de visualização baseada em D3). Sem framework pesado.
- **Hospedagem:** GitHub Pages pelo workflow `pages.yml`, disparado por push no `main` que altere `site/`, `lab/bench/results/`, os critérios (`lab/BENCH_CRITERIA*.md`), o pré-registro, a especificação, as diretrizes éticas ou a licença. Endereço: `hmal.hubstry.dev`. O domínio é verificado na organização do GitHub antes de criar o CNAME (registro de nome canônico) na Cloudflare, para evitar sequestro de subdomínio; o HTTPS é ativado depois. A estrutura nasce preparada para internacionalização.
- **Analytics:** opcional na Fase 0. Se entrar, Cloudflare Web Analytics por snippet, sem cookies e sem proxy da Cloudflare, acompanhado da nota de privacidade do princípio 10, em linha com a LGPD (Lei Geral de Proteção de Dados).
- **Acessibilidade e desempenho:** contraste AA (WCAG, Web Content Accessibility Guidelines), tema claro e escuro, leitura em celular, texto alternativo e tabela acessível com os dados principais de cada gráfico, navegação por teclado, carregamento abaixo de 1 MB sem os espectrogramas (PNG convertidos para WebP e carregados sob demanda; originais mantidos no repositório).

## 5. Critérios de aceite

1. Todo número exibido é rastreável a um JSON no `main`, com caminho, SHA-256, `experiment_commit`, `publication_commit` e tipo de execução.
2. O status de maturidade exibido é o que o `aggregate.py` produz ao ser executado no build sobre os artefatos, inclusive `INCONSISTENT_RUNS`; a regra não é reimplementada em JavaScript.
3. O build falha, com testes para cada caso, diante de: dado sem proveniência; SHA-256 divergente do manifesto; metadados divergentes entre modos; agregado incompleto; execução não definitiva apresentada como definitiva.
4. Lighthouse (auditoria do Google Chrome): acessibilidade ≥ 95 e desempenho ≥ 90 no celular, com verificação manual de teclado e leitor de tela.
5. Revisão documental da Luna sobre os textos; auditoria técnica independente do GLM-5.3 sobre o pipeline de dados.
6. Merge manual pelo Guilherme como barreira de publicação.

## 6. Riscos

| Risco | Mitigação |
|---|---|
| Página parecer mais madura que o projeto | princípios 3 e 4; textos revisados pela Luna |
| Divergência entre o site e o repositório | dados gerados no build a partir do `main`; teste de consistência |
| Prazo da entrevista | Fase 0 mínima; demonstração interativa só na Fase 1 |
| Espectrogramas pesados (cerca de 0,5 MB cada) | conversão para WebP e carregamento sob demanda |

## 7. Decisões tomadas (parecer da Luna, 31/10/2026)

| Decisão | Escolha |
|---|---|
| Hospedagem | GitHub Pages |
| Endereço | `hmal.hubstry.dev` |
| Comparação v1 × v2 | na Fase 0, com a ressalva do agregador legado para a v1 e o agregado TRL 3 da v2 sob a v0.3.1 |
| Inglês | Fase 1; a Fase 0 sai em português |
| Analytics | opcional na Fase 0 |
