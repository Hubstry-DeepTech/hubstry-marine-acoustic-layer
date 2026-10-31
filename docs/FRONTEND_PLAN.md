# HMAL Lab: plano da interface pública (front-end)

**Versão:** 0.1 · **Data:** 31/10/2026 · **Estado:** proposta para revisão da Luna; nada foi implementado

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

## 3. Escopo por fase

### Fase 0: antes de 06/11 (estimativa de 1 a 2 dias de trabalho)

| Seção | Conteúdo | Fonte dos dados |
|---|---|---|
| Início | o que é o HMAL em três frases; maturidade por componente; links para repositório e licença | `docs/SPECIFICATION.md` (texto revisado à mão, sem números) |
| Bancada digital | tabela de vereditos B1 a B7 por modo; curva de recuperação × SNR (razão sinal-ruído) por condição; curva RMS/ACRB (erro RMS, raiz do erro quadrático médio, sobre o limite de Cramér–Rao assintótico); comparação v1 × v2 | `lab/bench/results/*/` |
| E1, baleia-azul | série diária do índice de chamado B; espectrogramas dos três dias de critério; comparação com a referência do MBARI e tolerância de 2% | `lab/bench/results/e1/` |
| Metodologia | resumo de critérios, pré-registro, hold-out, correção pós-hoc da v0.4; links para os documentos | `lab/*.md` |
| Ética e licença | cláusula ética; dados CC BY 4.0 (Creative Commons Atribuição 4.0) do MBARI com crédito | `LICENSE`, `docs/ETHICS_GUIDELINES.md` |

Se a rodada definitiva da v0.4 terminar antes da entrevista, ela entra na mesma seção, ao lado da v0.3.1, só depois do merge no `main`.

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
- **Pipeline de dados:** `site/build_data.py` lê os resultados versionados e gera `site/public/data/*.json` reduzidos, com um esquema validado e o bloco de proveniência. O build falha se faltar proveniência ou se o veredito não bater com o `aggregate.py`.
- **Front-end:** HTML, CSS e TypeScript com Vite (ferramenta de build); gráficos com Observable Plot (biblioteca de visualização baseada em D3). Sem framework pesado.
- **Hospedagem:** GitHub Pages pelo workflow `pages.yml`, disparado por push no `main` que altere `site/` ou `lab/bench/results/`. Endereço proposto: `hmal.hubstry.dev`, com DNS (Domain Name System) na Cloudflare.
- **Analytics:** Cloudflare Web Analytics, sem cookies, compatível com a LGPD (Lei Geral de Proteção de Dados). Sem formulário e sem coleta de dados pessoais.
- **Acessibilidade e desempenho:** contraste AA (WCAG, Web Content Accessibility Guidelines), tema claro e escuro, leitura em celular, texto alternativo nos gráficos, carregamento abaixo de 1 MB sem os espectrogramas.

## 5. Critérios de aceite

1. Todo número exibido é rastreável até um JSON no `main`, e o JSON até o commit e a execução.
2. O TRL exibido é idêntico ao campo `trl_rule` do agregado correspondente.
3. O build falha diante de dado sem proveniência ou com veredito divergente, e há teste para isso.
4. Lighthouse (auditoria do Google Chrome): acessibilidade ≥ 95 e desempenho ≥ 90 no celular.
5. Revisão da Luna sobre os textos; auditoria independente do GLM-5.3 sobre o pipeline de dados.
6. Merge manual pelo Guilherme.

## 6. Riscos

| Risco | Mitigação |
|---|---|
| Página parecer mais madura que o projeto | princípios 3 e 4; textos revisados pela Luna |
| Divergência entre o site e o repositório | dados gerados no build a partir do `main`; teste de consistência |
| Prazo da entrevista | Fase 0 mínima; demonstração interativa só na Fase 1 |
| Espectrogramas pesados (cerca de 0,5 MB cada) | conversão para WebP e carregamento sob demanda |

## 7. Decisões pedidas

1. **Hospedagem:** GitHub Pages ou Cloudflare Pages. A proposta é GitHub Pages, pela proximidade com o repositório.
2. **Endereço:** `hmal.hubstry.dev` ou uma seção em `hubstry.dev/hmal`.
3. **Comparação v1 × v2:** mostrar já na Fase 0. A proposta é sim, por transparência.
4. **Inglês:** na Fase 0 ou só na Fase 1.
