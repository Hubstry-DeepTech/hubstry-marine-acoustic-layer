# HMAL - Diretrizes Eticas

## 1. Principios Fundamentais

O HMAL (Hubstry Marine Acoustic Layer) opera sob um principio de **nao-interferencia**:
toda saida acustica e exclusivamente analitica e jamais deve ser transmitida ao ambiente marinho.
Nenhuma funcionalidade deste software gera sinais acusticos reproduziveis em frequencias audiveis
por cetaceos, focas ou outras especies marinhas.

## 2. Limites de Exposicao Sonora

### 2.1 Limites NOAA (NMFS)

| Especie/Grupo | Banda (Hz)   | Limite (dB re 1 uPa) |
|---------------|--------------|----------------------|
| Baleia-azul   | 10-100       | 180 (impulso) / 120 (continuo) |
| Baleia-comum  | 10-200       | 180 (impulso) / 120 (continuo) |
| Golfinho      | 2.000-20.000 | 190 (impulso) / 140 (continuo) |
| Foca          | 500-5.000    | 185 (impulso) / 130 (continuo) |

Estes limites sao derivados das publicacoes do National Marine Fisheries Service (NMFS) e
do Office of Naval Research (ONR). O HMAL utiliza estes limiares apenas como referencia
analitica para classificacao de vocalizacoes gravadas, nunca para calibrar emissoes.

### 2.2 Regra de Seguranca

Qualquer modulo que gere dados acusticos para reproducao DEVE incluir um filtro passivo que
atenue a saida em pelo menos 40 dB nas bandas 10-200 Hz e 2.000-20.000 Hz antes de qualquer
conversao D/A. Este filtro nao pode ser desabilitado via API.

## 3. Uso Dual e Restricoes

### 3.1 Aplicacoes Proibidas

O HMAL e proibido de ser utilizado para:

- **Sonar ativo**: Geracao de pulsos acusticos direcionados a fauna marinha.
- **Dispersao acustica**: Criacao de barreiras sonoras para afastar mamiferos marinhos.
- **Pesca acustica**: Uso de sinais harmonicos para atrair ou confundir cardumes.
- **Militar**: Integracao com sistemas de guerra anti-submarino (ASW) ou deteccao de torpedos.

### 3.2 Aplicacoes Permitidas

- Analise passiva de gravacoes bioacusticas.
- Pesquisa cientifica com aprovacao de comite de etica.
- Monitoramento ambiental em parques marinhos (exclusivamente passivo).
- Educacao e divulgacao cientifica.

### 3.3 Verificacao de Licenca

O HMAL utiliza a licenca GPL-3.0-only com clausula adicional de uso etico. Distribuicoes
binarias devem incluir uma copia deste documento. O codigo fonte nao pode ser incorporado
em produtos com fins militares ou de exploracao comercial de recursos marinhos sem autorizacao
explicita do conselho de etica do projeto.

## 4. Requisitos de Auditoria

### 4.1 Registro de Atividades

Todo acesso a dados de vocalizacoes deve ser registrado em log estruturado contendo:
- Timestamp UTC (ISO 8601).
- Identificador do operador.
- Especie alvo e regiao geografica.
- Parametros de analise utilizados (f0_base, harmonic_order, tolerance).
- Hash SHA-256 do arquivo de audio processado.

### 4.2 Revisao Periodica

O conselho de etica do HMAL realiza revisoes trimestrais de:
- Logs de uso para identificar padroes de uso indevido.
- Pull requests que modifiquem modulos de geracao de sinais.
- Novas dependencias externas quanto a licencas e seguranca.

### 4.3 Divulgacao Responsavel

Vulnerabilidades de seguranca descobertas no HMAL devem ser reportadas via canal privado
(guilhermemachado@hubstry.onmicrosoft.com) seguindo a politica de divulgacao responsavel
com prazo minimo de 90 dias antes da divulgacao publica.

## 5. Conformidade Legal

O HMAL deve estar em conformidade com:

- **MARPOL** Annex V (poluicao acustica marinha, IMO).
- **Lei dos Mamiferos Marinhos** (Marine Mammal Protection Act, EUA).
- **Habitats Directive** (Directiva 92/43/CEE, Uniao Europeia).
- **Lei de Biodiversidade** (Lei 13.123/2015, Brasil).
- **CITES** Appendix I para especies criticas.

O descumprimento destas normas e de responsabilidade exclusiva do operador, mas o HMAL
deve fornecer mecanismos tecnico-organizacionais que facilitem a conformidade.

## 6. Referencias

1. NOAA NMFS. "Technical Guidance for Assessing the Effects of Anthropogenic Sound on Marine
   Mammal Hearing." NOAA Technical Memorandum NMFS-OPR-64, 2018.
2. Southall, B.L. et al. "Marine Mammal Noise Exposure Criteria." Aquatic Mammals, 2019.
3. ISO 18405:2017. "Underwater acoustics - Terminology."
4. IUCN. "Guidelines for Minimising Acoustic Disturbance to Marine Mammals from Seismic Surveys."
