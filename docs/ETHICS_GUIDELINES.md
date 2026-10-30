# HMAL - Diretrizes Eticas

## 1. Principios Fundamentais

O HMAL (Hubstry Marine Acoustic Layer) opera sob um principio de **nao-interferencia**: a pesquisa e a operação atualmente documentadas concentram-se em processamento e analise passiva de dados acusticos.

A versao atual do software pode gerar vetores digitais de sinais sinteticos para simulacao computacional. Isso nao significa que o repositorio controle transdutores, realize emissao submarina ou esteja autorizado para reproducao acustica no ambiente marinho. Qualquer conversao D/A, reproducao amplificada, emissao ativa ou experimento de campo exige avaliacao etica, autorizacoes e validacao de seguranca acustica proprias.

## 2. Limites de Exposicao Sonora

### 2.1 Limites NOAA (NMFS)

| Especie/Grupo | Banda (Hz)   | Limite (dB re 1 uPa) |
|---------------|--------------|----------------------|
| Baleia-azul   | 10-100       | 180 (impulso) / 120 (continuo) |
| Baleia-comum  | 10-200       | 180 (impulso) / 120 (continuo) |
| Golfinho      | 2.000-20.000 | 190 (impulso) / 140 (continuo) |
| Foca          | 500-5.000    | 185 (impulso) / 130 (continuo) |

Os valores acima sao referencias documentais herdadas de versoes anteriores e **nao constituem limites operacionais validados pelo HMAL**, autorizacao de emissao ou demonstracao de conformidade. Antes de qualquer uso que envolva emissao, os criterios aplicaveis devem ser confirmados diretamente nas orientacoes regulatorias vigentes e por profissional competente em bioacustica/acustica submarina.

### 2.2 Regra de Seguranca

Qualquer modulo futuro que exporte sinais para reproducao ou conversao D/A devera passar por avaliacao de seguranca acustica e incluir mecanismos tecnicos de limitacao validados antes de qualquer teste com transdutor. A exigencia historica de atenuacao de 40 dB mencionada em versoes anteriores nao foi validada como criterio suficiente de seguranca e nao deve ser usada como prova de conformidade.

## 3. Uso Dual e Restricoes

### 3.1 Usos Vedados e Limites para Uso de Defesa

As diretrizes atuais vedam o uso do HMAL para:

- **Sonar ativo**: Geracao de pulsos acusticos direcionados a fauna marinha.
- **Dispersao acustica**: Criacao de barreiras sonoras para afastar mamiferos marinhos.
- **Pesca acustica**: Uso de sinais harmonicos para atrair ou confundir cardumes.
- **Rastreamento para dano e monitoramento irregular**: Uso do HMAL para localizar, rastrear ou seguir cetaceos e outros mamiferos marinhos com fins de caca, captura, perseguicao ou molestamento, ou para monitoramento realizado sem as autorizacoes ambientais exigidas, conforme a clausula etica do arquivo `LICENSE`. No Brasil, a Lei 7.643/1987 proibe a pesca e qualquer forma de molestamento intencional de cetaceos em aguas jurisdicionais brasileiras.

Estas diretrizes **nao estabelecem uma proibicao generica de todo uso militar ou de defesa**. Isso nao significa que tais usos estejam autorizados: o arquivo `LICENSE` exige autorizacao previa e expressa do licenciante para produtos ou integracoes comerciais/de defesa. Qualquer proposta desse tipo tambem depende de avaliacao etica, juridica e de seguranca independente. Nenhum uso de defesa e concedido automaticamente pelo acesso ao repositorio; as atividades vedadas acima permanecem vedadas.

### 3.2 Aplicacoes Permitidas

- Analise passiva de gravacoes bioacusticas.
- Pesquisa cientifica com aprovacao de comite de etica, quando aplicavel.
- Monitoramento ambiental em parques marinhos (exclusivamente passivo e mediante autorizacoes aplicaveis).
- Educacao e divulgacao cientifica.

### 3.3 Verificacao de Licenca

O licenciamento do software e definido pelo arquivo `LICENSE` na raiz do repositorio: **Business Source License 1.1 (BSL 1.1)**, com concessao adicional para pesquisa academica, educacao e conservacao sob **CC BY 4.0**. Usos comerciais, SaaS e integracoes/produtos de defesa exigem autorizacao explicita do licenciante, conforme o texto da licenca. Esta secao etica acrescenta limites de uso; ela **nao substitui** o arquivo `LICENSE` nem concede direitos adicionais. O acesso ao codigo nao equivale a autorizacao para uso comercial ou de defesa. As atividades vedadas na Secao 3.1 continuam vedadas independentemente de autorizacao comercial.

## 4. Requisitos de Auditoria

### 4.1 Registro de Atividades

Todo acesso a dados de vocalizacoes deve ser registrado em log estruturado contendo:
- Timestamp UTC (ISO 8601).
- Identificador do operador.
- Especie alvo e regiao geografica.
- Parametros de analise utilizados (f0_base, harmonic_order, tolerance).
- Hash SHA-256 do arquivo de audio processado.

### 4.2 Revisao Periodica

Revisoes periodicas de governanca devem considerar:
- Logs de uso para identificar padroes de uso indevido.
- Pull requests que modifiquem modulos de geracao de sinais.
- Novas dependencias externas quanto a licencas e seguranca.

### 4.3 Divulgacao Responsavel

Vulnerabilidades de seguranca descobertas no HMAL devem ser reportadas pelo contato do responsavel do projeto: `guilhermemachado.ceo@hubstry.dev`. A divulgacao publica deve considerar riscos a usuarios, terceiros e ao ambiente marinho.

## 5. Marcos Normativos a Avaliar

A depender da atividade, jurisdicao, especie e contexto operacional, podem ser relevantes:

- **MARPOL** Annex V (prevencao de poluicao por lixo de navios; nao e, por si, norma geral de ruido submarino).
- **Marine Mammal Protection Act** (EUA).
- **Habitats Directive** (Diretiva 92/43/CEE, Uniao Europeia).
- **Lei de Biodiversidade** (Lei 13.123/2015, Brasil), quando houver acesso a patrimonio genetico/conhecimento tradicional associado nos termos de sua aplicabilidade.
- **CITES** Appendix I, quando houver atividades sujeitas ao regime de comercio internacional de especies listadas.

Esta lista e indicativa, nao exaustiva e nao constitui parecer juridico, declaracao de aplicabilidade ou certificacao de conformidade do HMAL. A aplicabilidade deve ser avaliada para cada atividade por profissionais competentes.

## 6. Referencias

1. NOAA NMFS. "Technical Guidance for Assessing the Effects of Anthropogenic Sound on Marine Mammal Hearing." NOAA Technical Memorandum NMFS-OPR-64, 2018.
2. Southall, B.L. et al. "Marine Mammal Noise Exposure Criteria." Aquatic Mammals, 2019.
3. ISO 18405:2017. "Underwater acoustics - Terminology."
4. IUCN. "Guidelines for Minimising Acoustic Disturbance to Marine Mammals from Seismic Surveys."