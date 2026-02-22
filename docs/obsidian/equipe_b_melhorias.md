# PEEX 2026 — EQUIPE B: MANIFESTO E REDESIGN DO BI PEDAGÓGICO
## Uma Crítica Fundamentada e uma Visão de Transformação

**Documento rival produzido pela Equipe B**
**Data:** 21/02/2026
**Base de análise:** Leitura direta das 27 páginas em `/Users/brunaviegas/siga_extrator/pages/` e `utils.py` (668 linhas)

---

## AVISO ANTES DE COMEÇAR

Este documento não é uma lista de sugestões educadas. É uma crítica honesta baseada em código real, em dados reais do Colégio ELO, e em princípios de design que fazem a diferença entre um sistema que as pessoas usam e um sistema que existe para ninguém usar. Se alguma afirmação dói, é porque o diagnóstico está correto.

---

# PARTE 1: MANIFESTO — O DASHBOARD ESTÁ ERRADO

## 1.1 O Problema Fundamental: Confusão entre Relatório e Sistema de Decisão

O BI Pedagógico do Colégio ELO foi construído como se o objetivo fosse *mostrar dados*. O objetivo real é *provocar decisões*. São dois produtos completamente diferentes, e confundi-los é o erro que explica por que 43,7% de conformidade continua sendo 43,7% mesmo depois de meses de desenvolvimento.

Um relatório responde à pergunta: "o que aconteceu?"
Um sistema de decisão responde à pergunta: "o que eu faço agora?"

As 27 páginas atuais respondem quase exclusivamente à primeira pergunta. A segunda é deixada inteiramente para o coordenador resolver por conta própria, em 30 minutos de reunião, sem estrutura, sem tempo, sem histórico de decisões anteriores.

## 1.2 O Diagnóstico de 27 Páginas

Após leitura linha a linha do código, a Equipe B classifica as 27 páginas em quatro categorias:

### CATEGORIA A — Páginas de Alta Decisão (deveriam ser a entrada do sistema)
Estas páginas têm lógica de diagnóstico real e geram listas de ação. O problema é que estão enterradas no meio da navegação:

- **Página 13 — Semáforo do Professor:** A função `calcular_metricas_professor()` calcula taxa de registro e taxa de conteúdo por professor. Isto é ouro. Está na página 13 de 27.
- **Página 14 — Alertas Inteligentes:** Cinco tipos de alerta com prioridade. A constante `TIPOS_ALERTA` com `prioridade: 1` (professor silencioso) até `prioridade: 5` (disciplina órfã) é exatamente o que o coordenador precisa na abertura da reunião. Está na página 14 de 27.
- **Página 17 — Painel de Ações:** A função `diagnosticar_professor()` gera diagnóstico completo com prioridades 0 a 3. Esta deveria ser a Home do sistema. Está na página 17 de 27.
- **Página 27 — Sala de Situação:** Visão executiva da rede. Criada como "proposta do Time Azul". Está na página 27 de 27 — a última página, onde praticamente ninguém chega.

### CATEGORIA B — Páginas de Suporte Legítimo (precisam existir, mas não na navegação principal)
Páginas que têm valor para análise profunda mas não para a rotina de reunião:

- **Página 5 — Progressão SAE:** A função `estimar_capitulo_real()` e o cruzamento com `dim_Progressao_SAE` são análises importantes, mas são detalhe técnico, não ponto de partida.
- **Página 9 — Comparativos:** Comparativo entre unidades é relevante, mas apenas quando já se sabe qual problema investigar.
- **Página 16 — Inteligência de Conteúdo:** Os `CAP_PATTERNS` para regex de capítulo e a função `classificar_tipo_aula()` são análises sofisticadas, mas são de auditoria, não de reunião semanal.
- **Página 18 — Análise por Turma:** A função `calcular_saude_turma()` é boa. Está no lugar errado.
- **Páginas 20, 21, 22, 23 — Frequência, Boletim, Ocorrências, ABC:** Banco de dados bem estruturado. Acesso correto é "clique para aprofundar", não "navegue até lá".

### CATEGORIA C — Páginas que Ninguém Usa em Reunião (desperdício de manutenção)
Páginas que existem por completude técnica mas não têm função numa reunião de coordenação de 30 minutos:

- **Página 2 — Calendário Escolar:** `dim_Calendario.csv` tem 327 dias. A página mostra o calendário. Mas o coordenador já sabe o calendário. Esta informação é referência, não dashboard.
- **Página 3 — Estrutura Curricular:** Carga horária por série. Dado estático. Não muda semana a semana. Pertence a um manual, não a um dashboard operacional.
- **Página 4 — Material SAE:** A página 4 é literalmente uma descrição textual da metodologia Design Thinking do livro SAE. Isso é documentação interna, não BI.
- **Página 6 — Visão do Professor:** "MATERIAL IMPRIMÍVEL para entregar ao professor" — o próprio docstring do arquivo confirma que a função é gerar um PDF para dar ao professor. Isso é uma funcionalidade de impressão, não uma página de dashboard operacional.
- **Página 11 — Material Imprimível:** Mesmo problema da Página 6, explicitado no nome: `🖨️`. Um sistema de decisão não deveria precisar de impressão como funcionalidade central.

### CATEGORIA D — Páginas com Potencial Não Realizado (design certo, implementação incompleta)
- **Página 12 — Agenda da Coordenação:** Tem autenticação por coordenador, tem `feedbacks_coordenacao.json`, tem `config_coordenadores.json`, tem a lógica de `DIA_REUNIAO_SEMANAL = 3`. Mas o registro de decisões é um JSON plano, sem histórico estruturado, sem follow-up automatizado, sem conexão com os alertas da Página 14.
- **Página 15 — Resumo Semanal:** A função `gerar_resumo_texto()` gera texto para WhatsApp com formatação `*NEGRITO*`. Boa ideia. Mas é manual — o coordenador precisa navegar até lá, clicar, copiar e colar. O sistema não envia nada automaticamente.
- **Página 25 — Devolutivas:** O modelo SBI + 3 C's + Feedforward é pedagogicamente correto. Mas o `DEVOLUTIVAS_FILE` é um JSON local, desconectado das métricas automáticas. O dado de "1/107 feedbacks" não é falha do coordenador — é falha do design.

## 1.3 O Problema da Navegação Numérica

A navegação atual é uma lista numerada de 01 a 27, apresentada como menu lateral do Streamlit. Isso significa:

1. O coordenador precisa saber de antemão qual número corresponde a qual função
2. Não há hierarquia visual — Página 1 (Quadro de Gestão) tem o mesmo peso visual que Página 4 (documentação SAE)
3. Não há ponto de entrada contextual — o sistema abre sempre na mesma Home, independente de qual unidade o coordenador representa ou do que aconteceu na semana
4. Não há notificação de estado — nada no menu indica que existem alertas críticos sem que o coordenador navegue até a Página 14
5. A numeração cria uma ilusão de que a ordem importa — que é preciso passar pela Página 1 para chegar à Página 14

**O coordenador de Boa Viagem (Bruna Vitória, 6º-9º Ano) não tem tempo para descobrir qual das 27 páginas é a mais relevante para ela hoje.** O sistema deveria saber isso e apresentar primeiro.

## 1.4 O que está sobrando

Com base na análise, estas páginas podem ser eliminadas ou fundidas sem perda de valor operacional:

| Página | Diagnóstico | Destino proposto |
|--------|-------------|-----------------|
| 02 — Calendário | Referência estática | Modal de "contexto da semana" na Home |
| 03 — Estrutura Curricular | Dado de configuração | Seção de configuração administrativa |
| 04 — Material SAE | Documentação | Wiki/Notion, não dashboard |
| 06 — Visão Professor | Impressão | Botão "gerar PDF" em Pg 13 |
| 08 — Alertas Conformidade | Duplica Pg 14 | Fundir com Pg 14 |
| 11 — Material Imprimível | Impressão | Botão "gerar PDF" em Pg 13 |
| 10 — Detalhamento Aulas | Tabela raw | Modal de detalhe a partir de Pg 13 |

**Resultado: de 27 páginas para 15 páginas com densidade de informação muito maior por página.**

## 1.5 O que está faltando

O que existe no código mas não aparece como deveria:

1. **Não existe uma "decisão" registrada no sistema.** `acoes_coordenacao.json` existe na Página 17 com `salvar_acoes()`, mas não há follow-up automático, não há comparação "o que prometemos semana passada vs o que aconteceu".

2. **Não existe distinção de papel.** O sistema tem `get_user_role()` em `auth.py`, mas todas as páginas mostram tudo para todos. Bruna Vitória (coordenadora BV, Anos Finais) entra e vê dados de CDR também, misturados. O filtro é sempre manual.

3. **Não existe temporal como contexto.** A Página 1 (Quadro de Gestão) carrega `filtrar_ate_hoje(df_aulas)` — ela sabe a semana atual. Mas ela não compara com a semana anterior. Não há linha de tendência de curto prazo. O sistema mostra "43,7% de conformidade" sem dizer se isso está melhorando ou piorando.

4. **Não existe loop de feedback entre professores e dados.** Os dados do SIGA entram, são analisados, e o coordenador decide em reunião. Mas o professor não sabe que está no vermelho do semáforo até que o coordenador fale. O sistema poderia enviar uma notificação automática ao professor antes mesmo da reunião.

5. **Não existe priorização multi-critério.** Página 14 lista alertas por tipo. Mas um professor pode ter ao mesmo tempo: conformidade baixa + currículo atrasado + ocorrências na turma. Esses sinais deveriam ser somados em um score único que determine a ordem de pauta da reunião.

## 1.6 Princípios de Design para um Dashboard de Decisão

A Equipe B adota os seguintes princípios, que não estão implementados no sistema atual:

**Princípio 1 — Contexto Antes de Dados**
O sistema deve saber quem está acessando, de qual unidade, em qual semana do ano, e apresentar o contexto imediatamente. "Semana 4, Capítulo 1 esperado, 3 alertas críticos em BV" deve aparecer antes de qualquer gráfico.

**Princípio 2 — Ação é o produto, dado é o insumo**
Cada visualização deve terminar com uma chamada à ação ou uma decisão possível. Um gráfico de barras de conformidade sem o botão "registrar intervenção" é dados, não decisão.

**Princípio 3 — 3 cliques até a decisão**
Da abertura do sistema até o registro de uma intervenção: máximo 3 cliques. Hoje são pelo menos 7 (login + Home + navegar para Pg 14 + navegar para Pg 17 + selecionar professor + selecionar tipo de ação + salvar).

**Princípio 4 — Urgência visível sem clique**
Alertas críticos devem ser visíveis na Home sem que o coordenador precise navegar para encontrá-los. O badge vermelho no menu lateral é insuficiente — é necessário que a Home já mostre "3 professores em estado crítico" com link direto para cada um.

**Princípio 5 — Memória institucional**
O sistema deve lembrar o que foi decidido na semana anterior e cobrar resultados automaticamente. Hoje, cada reunião começa do zero.

**Princípio 6 — Configuração é invisível**
O coordenador não deveria nunca precisar selecionar "unidade: BV" porque o sistema já sabe que ela é coordenadora de BV. O `get_user_unit()` existe em `auth.py` mas não é usado como contexto padrão em todas as páginas.

---

# PARTE 2: REDESIGN — A VISÃO DO SISTEMA

## 2.1 Da Hierarquia Plana à Hierarquia de Decisão

O sistema atual tem hierarquia plana: 27 páginas de mesmo nível. O redesign propõe 4 camadas:

```
CAMADA 0: CONTEXTO AUTOMÁTICO (sem clique)
    → Semana letiva atual | Capítulo esperado | Trimestre
    → Alertas críticos da unidade do usuário
    → Score ELO da unidade (ver Parte 4)

CAMADA 1: HOME — PARA ONDE OLHAR AGORA (1 clique)
    → Mapa de calor dos professores (semáforo 4x4)
    → Top 5 situações que precisam de ação esta semana
    → Pauta automática da próxima reunião

CAMADA 2: DETALHE DO PROBLEMA (2 cliques)
    → Perfil do professor/aluno específico
    → Histórico do problema (está piorando ou melhorando?)
    → Sugestão de intervenção com base em dados

CAMADA 3: REGISTRO DA AÇÃO (3 cliques)
    → Registrar devolutiva com contexto automático
    → Definir prazo e critério de sucesso
    → Follow-up automático programado
```

## 2.2 Reorganização das 27 Páginas

### SEÇÃO 1: HOJE (3 páginas)
**Substitui:** Páginas 1, 13, 14, 27
```
HOME_SALA_DE_SITUAÇÃO    ← fusão de Pg 1 + Pg 27
ALERTA_SEMAFORO          ← fusão de Pg 13 + Pg 14 (reformatada)
PAUTA_DA_REUNIÃO         ← nova (gerada automaticamente)
```

### SEÇÃO 2: PROFESSORES (4 páginas)
**Substitui:** Páginas 5, 6, 9, 16, 17, 18
```
DIAGNÓSTICO_PROFESSOR    ← fusão de Pg 17 + Pg 6 (sem impressão)
PROGRESSÃO_CONTEÚDO      ← fusão de Pg 5 + Pg 16
ANÁLISE_TURMA            ← Pg 18 (refinada)
COMPARATIVO_REDE         ← Pg 9 (reformatada, sem as 3 abas soltas)
```

### SEÇÃO 3: ALUNOS (4 páginas)
**Substitui:** Páginas 19, 20, 21, 22, 23
```
PAINEL_ALUNO_360         ← fusão de Pg 19 + Pg 21
FREQUÊNCIA_RISCO         ← Pg 20 + ABC (Pg 23)
OCORRÊNCIAS              ← Pg 22 (mantida, já é boa)
CRUZAMENTO_SAE           ← Pg 24 (mantida)
```

### SEÇÃO 4: AÇÕES E MEMÓRIA (3 páginas)
**Substitui:** Páginas 12, 15, 17, 25
```
DEVOLUTIVAS              ← Pg 25 (com dados automáticos)
AGENDA_HISTÓRICO         ← Pg 12 + histórico de decisões de Pg 17
RESUMO_EXPORTAÇÃO        ← Pg 15 (com envio automático)
```

### SEÇÃO 5: CONTEXTO E REFERÊNCIA (2 páginas, não no menu principal)
**Substitui:** Páginas 2, 3, 4, 7, 8, 10, 11, 26
```
CONFIGURAÇÃO             ← Pg 3 + Pg 8 (critérios)
PAINEL_UNIFICADO         ← Pg 26 (vagas + pedagógico)
```

**Total: 15 páginas funcionais + 2 de contexto = 17 páginas, não 27.**

## 2.3 Mapa de Navegação Ideal

```
┌─────────────────────────────────────────────────────────┐
│  COLÉGIO ELO — BI PEDAGÓGICO          [BV] Sem 4 Cap 1  │
│  Bruna Vitória — Coordenadora 6º-9º Ano                 │
│                                                         │
│  ⚠️ 3 ALERTAS CRÍTICOS ESTA SEMANA                      │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│  HOJE                                                  │
│  ├── Home / Sala de Situação   [Score ELO: 67 ⚠️]     │
│  ├── Semáforo + Alertas        [3 vermelhos]           │
│  └── Pauta da Reunião          [gerada automaticamente] │
├────────────────────────────────────────────────────────┤
│  PROFESSORES                                           │
│  ├── Diagnóstico Individual    [selecionar professor]  │
│  ├── Progressão de Conteúdo    [cap. real vs esperado] │
│  ├── Análise por Turma         [visão cross-disciplina]│
│  └── Comparativo Rede          [BV vs CD vs JG vs CDR] │
├────────────────────────────────────────────────────────┤
│  ALUNOS                                                │
│  ├── Painel 360 do Aluno       [busca por nome]        │
│  ├── Frequência e Risco ABC    [lista de risco]        │
│  ├── Ocorrências               [dashboard comportament]│
│  └── Cruzamento SIGA x SAE    [engajamento digital]   │
├────────────────────────────────────────────────────────┤
│  AÇÕES                                                 │
│  ├── Devolutivas               [ficha com dados auto]  │
│  ├── Agenda e Histórico        [memória institucional] │
│  └── Resumo / Exportação       [WhatsApp + PDF]        │
└────────────────────────────────────────────────────────┘
```

## 2.4 O Conceito de "3 Cliques até a Decisão"

**Situação atual (contagem real):**
```
[Login] → [Pg 1 Home] → [sidebar: Pg 14] → [selecionar unidade BV] →
[ver alertas] → [sidebar: Pg 17] → [selecionar professor] →
[clicar em ação] → [salvar]
= 8 passos, 6 seleções manuais, tempo estimado: 4-7 minutos
```

**Situação proposta:**
```
[Login] → [Home já filtrada para BV, mostra 3 alertas críticos] →
[clicar no professor em vermelho] → [perfil completo + botão "registrar devolutiva"]
= 3 passos, 0 seleções manuais, tempo estimado: 45 segundos
```

A diferença é que o sistema conhece o usuário. `get_user_unit()` já retorna `'BV'` para Bruna Vitória. Isso deveria ser o contexto padrão de **toda** a experiência, não um filtro que ela precisa aplicar manualmente em cada página.

---

# PARTE 3: AS 10 MUDANÇAS QUE TRANSFORMAM O DASHBOARD

## Mudança 1: A Home como Sala de Guerra, Não como Relatório

### Estado Atual
Página 1 carrega `carregar_fato_aulas()` + `filtrar_ate_hoje()` e exibe métricas gerais com `st.metric()`. O coordenador vê números agregados. A primeira informação é "total de aulas registradas: 1.901". Isso não aciona nenhuma decisão.

### Problema
A Home atual responde "quanto" mas não "onde está o problema" e não "o que fazer". É um painel de CEO para uma pessoa que precisa agir como gestora operacional nos próximos 30 minutos.

### Transformação
A Home deve abrir com três zonas imediatas, sem scroll:

```
┌────────────────────────────────────────────────────────────────┐
│  BOM DIA, BRUNA VITÓRIA                    Semana 4 | Cap 1   │
│  6º ao 9º Ano — Boa Viagem                 21/02/2026 07:14   │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  SCORE ELO BV: 67/100  ⚠️  (-3 vs semana passada)       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  AÇÃO IMEDIATA (3 situações):                                  │
│  🔴 Prof. João — 0 registros há 4 dias     [ver perfil]       │
│  🟠 6º Ano Mat — Cap. 0 (esperado: Cap. 1) [ver turma]        │
│  🟡 7º Ano — Prof. Ana caiu 40% esta semana [ver devolutiva]  │
│                                                                │
│  PRÓXIMA REUNIÃO: Quinta-feira 26/02       [ver pauta]        │
└────────────────────────────────────────────────────────────────┘
```

### Impacto na Reunião
O coordenador chega na reunião já sabendo os 3 pontos de pauta prioritários. Não precisa de 15 minutos para "contextualizar". Começa em 30 segundos.

---

## Mudança 2: Semáforo como Mapa, Não como Lista

### Estado Atual
Página 13 (`calcular_metricas_professor()`) calcula cores por professor mas exibe em cards HTML individuais usando `st.markdown()`. Para ver todos os professores, o coordenador faz scroll numa lista longa.

### Problema
107 professores em 4 unidades em formato de lista = impossível ter visão global. O objetivo do semáforo é "ver quem está em vermelho em 5 segundos" (o próprio docstring da Pg 13 diz isso). Mas o design não permite.

### Transformação
Grade matricial 2D com professores nas linhas e semanas nas colunas — cor = semáforo. Permite ver tendência + status atual ao mesmo tempo:

```
┌──────────────────────────────────────────────────────────────┐
│  SEMÁFORO — BOA VIAGEM | 6º-9º Ano                          │
│                                                              │
│  PROFESSOR         S1   S2   S3  S4(atual)  TREND           │
│  ─────────────────────────────────────────────────────────  │
│  Ana Paula         🟢   🟢   🟡   🔴         ↘ ATENCAO      │
│  Carlos Henrique   🟢   🟢   🟢   🟢         → OK            │
│  Fernanda Lima     🟡   🔴   🔴   🔴         ↘ CRITICO       │
│  João Marcos       🟢   🟢   🟡   🟡         → MONITORAR     │
│                                                              │
│  [clique no nome = perfil completo + histórico + devolutiva] │
└──────────────────────────────────────────────────────────────┘
```

### Implementação Técnica
A função `calcular_metricas_professor()` da Pg 13 já calcula as métricas por semana. Falta apenas acumular por semana (não só "semana atual") e renderizar como heatmap com `plotly.graph_objects.Heatmap`. Os dados já existem em `fato_Aulas.csv`.

### Impacto na Reunião
De "qual professor precisa de atenção?" (resposta: precisa ler a lista) para "Fernanda Lima está vermelha há 3 semanas" (resposta: 2 segundos de visualização).

---

## Mudança 3: Alerta Inteligente com Score Único (Não 5 Tipos Separados)

### Estado Atual
Página 14 tem 5 tipos de alerta (VERMELHO=professor silencioso, AMARELO=registro em queda, LARANJA=currículo atrasado, AZUL=frequência pendente, ROSA=disciplina órfã). Cada tipo tem `prioridade` de 1 a 5. Mas o sistema exibe os tipos separadamente, como abas ou seções independentes.

### Problema
Um professor pode estar simultaneamente: silencioso (prioridade 1) + currículo atrasado (prioridade 3) + disciplina órfã (prioridade 5). O sistema mostra esse professor em três seções diferentes. O coordenador precisa fazer a conta mentalmente de que é o mesmo professor com três problemas sobrepostos. Em 30 minutos de reunião, essa conta não acontece.

### Transformação
Score de risco composto por professor, ordenado automaticamente:

```
RANKING DE ATENÇÃO — SEMANA 4 — BOA VIAGEM

#1  FERNANDA LIMA          Score: 89/100  CRÍTICO
    ├── 🔴 Sem registro há 6 dias (+40 pts)
    ├── 🟠 Cap. 0 vs esperado Cap. 1 (+30 pts)
    └── 🩷 Biologia órfã na semana (+19 pts)
    [AÇÃO SUGERIDA: Reunião urgente — pauta já disponível]

#2  ANA PAULA              Score: 52/100  ATENÇÃO
    ├── 🟡 Registro caiu 40% vs semana anterior (+35 pts)
    └── 🔵 5 dias sem lançar frequência (+17 pts)
    [AÇÃO SUGERIDA: Conversa de acompanhamento]

#3  JOÃO MARCOS            Score: 23/100  MONITORAR
    └── 🟡 Conformidade 78% (meta: 85%) (+23 pts)
    [AÇÃO SUGERIDA: Feedback positivo + orientação]
```

### Implementação Técnica
A lógica de prioridade já existe na Pg 14 (`'prioridade': 1` até `5`). A transformação é somar os scores ponderados e ordernar o resultado em um único DataFrame, não em seções separadas. Modificação em `calcular_score_risco_professor()` (nova função em `utils.py`).

### Impacto na Reunião
A pauta da reunião é o próprio ranking. O #1 é o primeiro assunto. Sem discussão sobre "por onde começar".

---

## Mudança 4: Pauta Automática como Produto Principal

### Estado Atual
Página 15 (`gerar_resumo_texto()`) gera texto para WhatsApp manualmente. Página 17 (`ACOES_FILE = WRITABLE_DIR / "acoes_coordenacao.json"`) tem registro de ações. Mas não existe uma "pauta" — existe um texto genérico de situação + uma lista de ações sem conexão entre si.

### Problema
A pauta da reunião é o artefato mais importante da semana. Hoje ela não existe como dado do sistema — ela existe na cabeça do coordenador ou num papel. O sistema gera dados para que o coordenador construa a pauta manualmente.

### Transformação
Botão único: "GERAR PAUTA DA SEMANA 4". O sistema produz:

```
PAUTA — REUNIÃO SEMANAL COLÉGIO ELO BV
Quinta-feira, 26/02/2026 | 14h00 | Semana 4 | Capítulo esperado: 1

────────────────────────────────────────
1. SITUAÇÕES CRÍTICAS (15 min)
────────────────────────────────────────
[CRÍTICO] Fernanda Lima — 6 dias sem registro
  Dados: fato_Aulas.csv | Última aula: 15/02/2026
  Histórico: estava OK nas semanas 1-2, começou a cair na semana 3
  Intervenção semana passada: "Conversa de acompanhamento" (registrado 13/02)
  Resultado: NÃO RESOLVIDO (situação piorou)
  Ação proposta: Reunião formal + plano de ação documentado

────────────────────────────────────────
2. SITUAÇÕES DE ATENÇÃO (10 min)
────────────────────────────────────────
[ATENÇÃO] Ana Paula — queda de 40% no registro
  ...

────────────────────────────────────────
3. FOLLOW-UP DA SEMANA PASSADA (5 min)
────────────────────────────────────────
[PENDENTE] João Marcos — meta de 85% conformidade
  Prometido em 14/02: atingir 85% até esta semana
  Resultado atual: 82% (ainda abaixo)
  ...

────────────────────────────────────────
TEMPO TOTAL ESTIMADO: 30 minutos
Próxima atualização: 28/02/2026 (Semana 5)
```

### Implementação Técnica
Combinar `diagnosticar_professor()` (Pg 17) + `carregar_acoes()` (Pg 17) + `calcular_metricas_professor()` (Pg 13) em uma nova função `gerar_pauta_semanal()`. Os dados existem. A lógica de conexão entre eles ainda não foi escrita.

### Impacto na Reunião
Elimina os primeiros 15 minutos de "contextualização" que hoje são gastos tentando entender o que aconteceu na semana. A reunião começa diretamente na decisão.

---

## Mudança 5: Devolutiva com Dados Automáticos Pré-Carregados

### Estado Atual
Página 25 (`DEVOLUTIVAS_FILE = WRITABLE_DIR / 'devolutivas.json'`) tem o modelo SBI + 3 C's + Feedforward. A função `_calcular_metricas_professor()` calcula métricas do professor para "contexto da devolutiva". Mas o formulário abre vazio — o coordenador preenche tudo manualmente.

### Problema
Com 107 professores e 45 reuniões por ano, o coordenador tem potencialmente 107 fichas de devolutiva para preencher. Se cada uma leva 10 minutos pra preencher do zero, são 17,8 horas só de digitação. O resultado é 1/107 feedbacks — o sistema gera atrito suficiente para que o coordenador simplesmente não use.

### Transformação
Quando o coordenador clica em "Registrar Devolutiva" para Fernanda Lima, o sistema abre a ficha **pré-preenchida** com:

```
DEVOLUTIVA — FERNANDA LIMA — 21/02/2026

[DADOS AUTOMÁTICOS — extraídos de fato_Aulas.csv]
Conformidade atual: 31% (meta: 85%) — CRÍTICO
Último registro: 15/02/2026 (6 dias atrás)
Capítulo estimado: 0 (esperado: 1) — atraso de 1 capítulo
Tipo de aulas mais frequente: Expositiva (classificar_tipo_aula — Pg 16)
Turmas afetadas: 8º A, 8º B, 9º A

[HISTÓRICO DE DEVOLUTIVAS]
Última devolutiva: 13/02/2026 — "Conversa de acompanhamento"
Compromisso firmado: "Atingir 75% de conformidade até semana 4"
Status do compromisso: NÃO CUMPRIDO (atual: 31%)

[SBI — preencher]
Situação: ...
Comportamento: ...
Impacto: ...

[3 C's — preencher]
Continuar: ...
Começar: ...
Cessar: ...
```

### Implementação Técnica
A função `_calcular_metricas_professor()` na Pg 25 já existe. A mudança é: ao abrir a Pg 25 com `professor=X` como parâmetro de URL, ela carrega automaticamente as métricas e os histórico de devolutivas anteriores. Adicionar `st.query_params` para aceitar professor pré-selecionado.

### Impacto na Reunião
De 10 minutos por devolutiva para 2 minutos. Meta de 107 feedbacks/ano se torna viável.

---

## Mudança 6: Score ABC de Aluno na Tela do Professor

### Estado Atual
Página 23 (Sistema ABC de Alerta Precoce) e Página 19 (Painel do Aluno) são páginas separadas, acessadas por caminhos independentes. O professor de Matemática do 8º Ano não sabe, ao olhar o semáforo da Pg 13, se o problema de conformidade dele está correlacionado com problemas de frequência dos alunos.

### Problema
O dado mais importante é a interseção: professor com conformidade baixa + turma com frequência baixa = problema estrutural, não apenas de registro. Hoje esse cruzamento não aparece em lugar nenhum como visualização integrada.

### Transformação
No perfil do professor (Pg 13 → click), mostrar:

```
FERNANDA LIMA — Biologia | 8º A, 8º B, 9º A — BV

Conformidade: 31% ⚠️
Capítulo real: 0 | Esperado: 1

TURMAS AFETADAS:
┌──────────┬─────────────┬───────────────┬──────────────┐
│ Turma    │ Freq. Média │ Em risco LDB  │ Ocorrências  │
├──────────┼─────────────┼───────────────┼──────────────┤
│ 8º A     │ 82%         │ 2 alunos      │ 3 esta semana│
│ 8º B     │ 91%         │ 0 alunos      │ 1 esta semana│
│ 9º A     │ 78%         │ 4 alunos ⚠️   │ 5 esta semana│
└──────────┴─────────────┴───────────────┴──────────────┘

INTERPRETAÇÃO: 9º A tem frequência baixa E o professor
não está registrando. O problema pode ser maior do que
parece nos dados de conformidade.
```

### Implementação Técnica
Cruzar `fato_Aulas.csv` + `fato_Frequencia_Aluno.csv` + `fato_Ocorrencias.csv` por (unidade, serie, turma). As três tabelas já existem. Falta a query de cruzamento e a visualização integrada.

### Impacto na Reunião
O coordenador para de discutir "o professor não está registrando" e começa a discutir "o 9º A tem um problema de engajamento que precisamos investigar junto — tanto o professor quanto os alunos".

---

## Mudança 7: Filtros Salvos e Contexto Persistente

### Estado Atual
Cada página tem seu próprio conjunto de filtros independentes. `barra_filtros_padrao()` em `components.py` é chamada em quase todas as páginas com prefixos diferentes (`key_prefix="pg01_"`, `key_prefix="pg05_"` etc.). Isso significa que filtrar "BV" na Pg 1 não carrega "BV" automaticamente na Pg 5.

### Problema
O coordenador de BV (Bruna Vitória) aplica o filtro "BV" em cada página que acessa. Em uma sessão de reunião de 30 minutos onde ela navega por 8-10 páginas, ela seleciona "BV" pelo menos 8-10 vezes. São 2-3 minutos de fricção pura.

### Transformação
`st.session_state` com contexto global:

```python
# Em auth.py — após login bem-sucedido:
if 'contexto_usuario' not in st.session_state:
    st.session_state.contexto_usuario = {
        'unidade': get_user_unit(),          # 'BV'
        'segmento': get_user_segment(),      # 'FUND_II'
        'ultima_pagina': None,
        'filtros_salvos': {},
    }

# Em components.py — barra_filtros_padrao():
def barra_filtros_padrao(...):
    # Lê contexto global como padrão
    contexto = st.session_state.get('contexto_usuario', {})
    unidade_default = contexto.get('unidade', 'TODAS')
    # Salva mudanças de volta ao contexto
    ...
```

### Impacto na Reunião
Zero tempo gasto em filtros. O sistema sabe quem é o usuário e para qual unidade mostrar dados.

---

## Mudança 8: Histórico de Decisões como Banco de Dados Real

### Estado Atual
`acoes_coordenacao.json` (Pg 17) e `devolutivas.json` (Pg 25) e `feedbacks_coordenacao.json` (Pg 12) são três JSONs separados, sem schema comum, sem índice cruzado por professor, sem histórico temporal estruturado.

### Problema
Não existe memória institucional. Se a coordenadora registrou uma intervenção para João Marcos na semana 2, esse registro não aparece automaticamente quando ela abre o perfil de João Marcos na semana 4. O passado não informa o presente.

### Transformação
Unificar em `fato_Intervencoes.csv` com schema:

```
data | coordenadora | professor | tipo_intervencao |
    alerta_gatilho | descricao | compromisso_firmado |
    prazo_verificacao | status (pendente/cumprido/nao_cumprido)
```

Carregar esse arquivo em `utils.py` com `carregar_intervencoes()` e exibir no perfil do professor, na pauta automática, e no histórico da Pg 12.

### Impacto na Reunião
"João Marcos foi monitorado nas semanas 2 e 3, ambas as vezes com o compromisso de atingir 85% de conformidade. Não cumpriu. Na semana 4, escalamos para reunião formal." — essa narrativa emerge dos dados automaticamente.

---

## Mudança 9: Progressão SAE com Alarme de Desvio Real

### Estado Atual
Página 5 usa `estimar_capitulo_real()` com regex `cap[íi]?t?u?l?o?\.?\s*(\d{1,2})` nos conteúdos dos registros. E `calcular_capitulo_esperado(semana)` em `utils.py` define o capítulo esperado por semana via SWITCH. O gap entre real e esperado é calculado mas exibido apenas como número numa tabela.

### Problema
Na semana 4, o capítulo esperado é 1. Se Fernanda Lima está no capítulo 0 (sem registro), o sistema mostra "desvio: -1". Mas isso não comunica urgência. Um desvio de -1 no começo do ano é diferente de um desvio de -1 no fim do trimestre — no segundo caso, o acúmulo pode ser irrecuperável.

### Transformação
Projeção de fim de trimestre com base na velocidade atual:

```
PROGRESSÃO — BIOLOGIA | 8º ANO | BV

Cap. esperado hoje (Sem 4): 1
Cap. real estimado: 0  ← extraído dos conteúdos (Pg 5)
Desvio atual: -1 capítulo

PROJEÇÃO FIM DE TRIMESTRE (Semana 15):
  Velocidade atual: 0 cap/semana
  Cap. projetado sem correção: 0 (esperado: 4)
  ⚠️ RISCO: Termine o 1º Trimestre com 4 capítulos de atraso
  Para recuperar: precisaria cobrir 4 caps em 11 semanas
  = 2.7 caps por semana — INVIÁVEL

  RECOMENDAÇÃO: Iniciar plano de recuperação esta semana.
  Mínimo viável: completar Cap. 1 E Cap. 2 até Semana 8.
```

### Implementação Técnica
Adicionar em `utils.py`:
```python
def projetar_capitulo_fim_trimestre(cap_real, semana_atual, semana_fim_trimestre=15):
    semanas_restantes = semana_fim_trimestre - semana_atual
    cap_esperado_fim = calcular_capitulo_esperado(semana_fim_trimestre)
    if semana_atual > 1:
        velocidade = cap_real / semana_atual
    else:
        velocidade = 0
    cap_projetado = cap_real + (velocidade * semanas_restantes)
    deficit = cap_esperado_fim - cap_projetado
    return {
        'cap_projetado': round(cap_projetado, 1),
        'cap_esperado_fim': cap_esperado_fim,
        'deficit': round(deficit, 1),
        'recuperavel': deficit <= semanas_restantes * 0.5,
    }
```

### Impacto na Reunião
A discussão muda de "está atrasado" para "se não agirmos agora, terminamos o trimestre com 4 capítulos de atraso e não há como recuperar". Urgência com evidência.

---

## Mudança 10: WhatsApp Automático como Canal, Não como Feature

### Estado Atual
Página 15 (`gerar_resumo_texto()`) formata o resumo com `*NEGRITO*` do WhatsApp. Mas o coordenador precisa: navegar até a Pg 15 → clicar em "gerar" → copiar o texto → abrir o WhatsApp → colar → enviar. São 6 passos manuais.

### Problema
Se o fluxo tem 6 passos, o coordenador faz isso raramente. O WhatsApp deveria ser um canal de saída automático do sistema, não um destino manual.

### Transformação
Integração via WhatsApp Business API ou, para MVP, via link `wa.me` pré-formatado:

```python
def gerar_link_whatsapp(texto_resumo, numero_grupo):
    """Gera link wa.me com texto codificado para envio direto."""
    import urllib.parse
    texto_encoded = urllib.parse.quote(texto_resumo)
    return f"https://wa.me/{numero_grupo}?text={texto_encoded}"
```

Botão na Home: "Enviar resumo para grupo BV-Coord" → abre WhatsApp com mensagem pré-formatada. Um clique.

Para a versão mais avançada: webhook para Evolution API (WhatsApp API self-hosted) que envia automaticamente toda sexta-feira às 17h.

### Impacto na Reunião
Toda a equipe de coordenação recebe o resumo semanal automaticamente, sem depender de uma pessoa lembrar de enviar.

---

# PARTE 4: "ÍNDICE ELO" — IMPLEMENTAÇÃO NO DASHBOARD

## 4.1 O Problema da Métrica Única

Hoje o sistema tem dezenas de métricas: conformidade de registro, taxa de conteúdo, capítulo real vs esperado, frequência de alunos, ocorrências, feedbacks dados. Para o coordenador com 30 minutos de reunião, isso é excesso de informação sem síntese.

O "Índice ELO" resolve isso: um número de 0 a 100 por unidade/segmento que resume a saúde pedagógica da semana. Não para simplificar a complexidade — para criar um ponto de entrada. O Índice ELO é o título da página. Os dados por trás são o conteúdo.

## 4.2 Fórmula do Índice ELO

```
ÍNDICE ELO = (
    Conformidade_Registro  × 0.30   (% aulas registradas / esperadas)
  + Qualidade_Conteúdo     × 0.20   (% registros com conteúdo não-vazio)
  + Progressao_Curriculo   × 0.25   (cap. real / cap. esperado, max 1.0)
  + Frequencia_Alunos      × 0.15   (% alunos com freq > 75% LDB)
  + Engajamento_SAE        × 0.10   (% alunos com atividade SAE na semana)
)

Onde cada componente é normalizado de 0 a 100.
```

### Fontes de cada componente:
- `Conformidade_Registro`: calculado em `calcular_metricas_professor()` — Pg 13
- `Qualidade_Conteúdo`: `taxa_conteudo` — mesmo lugar
- `Progressao_Curriculo`: `estimar_capitulo_real()` / `calcular_capitulo_esperado()` — Pg 5 + utils.py
- `Frequencia_Alunos`: `fato_Frequencia_Aluno.csv` + `calcular_frequencia_aluno()` — utils.py
- `Engajamento_SAE`: `fato_Engajamento_SAE.csv` — Pg 24

O peso de Engajamento SAE começa em 0.10 porque `fato_Engajamento_SAE.csv` ainda tem dados incompletos (match de ~85% esperado). Quando o `extrair_sae_digital.py` estiver completo, pode subir para 0.15.

## 4.3 Implementação em utils.py

```python
def calcular_indice_elo(unidade, semana, df_aulas, df_horario,
                        df_freq=None, df_engaj_sae=None):
    """
    Calcula Índice ELO (0-100) para uma unidade na semana atual.
    Retorna dict com score total e detalhe por componente.
    """
    # 1. Conformidade de Registro
    df_un = df_aulas[df_aulas['unidade'] == unidade]
    df_hor_un = df_horario[df_horario['unidade'] == unidade]
    esperado = len(df_hor_un) * semana
    realizado = len(df_un)
    conformidade = min(100, (realizado / esperado * 100)) if esperado > 0 else 0

    # 2. Qualidade de Conteúdo
    com_conteudo = df_un['conteudo'].notna() & (df_un['conteudo'].str.strip() != '')
    qualidade = (com_conteudo.sum() / len(df_un) * 100) if len(df_un) > 0 else 0

    # 3. Progressão Curricular
    cap_esperado = calcular_capitulo_esperado(semana)
    caps_reais = []
    for prof, df_prof in df_un.groupby('professor'):
        cap_real = estimar_capitulo_medio(df_prof['conteudo'].tolist())
        if cap_real is not None:
            caps_reais.append(cap_real / cap_esperado)
    progressao = min(100, (sum(caps_reais) / len(caps_reais) * 100)) if caps_reais else 50

    # 4. Frequência Alunos
    freq_score = 75  # default quando não disponível
    if df_freq is not None and not df_freq.empty:
        df_freq_un = df_freq[df_freq['unidade'] == unidade]
        alunos_ok = (df_freq_un['frequencia_pct'] >= THRESHOLD_FREQUENCIA_LDB).sum()
        freq_score = (alunos_ok / len(df_freq_un) * 100) if len(df_freq_un) > 0 else 75

    # 5. Engajamento SAE
    sae_score = 60  # default quando não disponível
    if df_engaj_sae is not None and not df_engaj_sae.empty:
        df_sae_un = df_engaj_sae[df_engaj_sae['unidade'] == unidade]
        ativos = (df_sae_un['atividades_semana'] > 0).sum()
        sae_score = (ativos / len(df_sae_un) * 100) if len(df_sae_un) > 0 else 60

    # Score final ponderado
    score = (
        conformidade * 0.30
        + qualidade * 0.20
        + progressao * 0.25
        + freq_score * 0.15
        + sae_score * 0.10
    )

    return {
        'score': round(score, 1),
        'conformidade': round(conformidade, 1),
        'qualidade': round(qualidade, 1),
        'progressao': round(progressao, 1),
        'frequencia': round(freq_score, 1),
        'sae': round(sae_score, 1),
    }
```

## 4.4 Visualização: Gauge + Trend + Comparativo

### Gauge na Home (sem scroll):
```
┌──────────────────────────────────────────────────────────┐
│  ÍNDICE ELO — BOA VIAGEM             Semana 4            │
│                                                          │
│         0    25    50    75    100                        │
│         ├────┼─────┼──────●─────┼────┤                   │
│         🔴   🟠    🟡    ╪    🟢                          │
│                          67                              │
│                    ⚠️ ATENÇÃO                            │
│                                                          │
│  Semana passada: 70 (-3)  │  Meta: 85                   │
└──────────────────────────────────────────────────────────┘
```

### Decomposição (ao clicar no gauge):
```
ÍNDICE ELO BV: 67/100 ← ONDE ESTÁ PERDENDO PONTOS?

Conformidade Registro:   58% × 0.30 = 17.4 pts  ⚠️ (-8 vs meta)
Qualidade Conteúdo:      71% × 0.20 = 14.2 pts  🟡
Progressão Curricular:   85% × 0.25 = 21.3 pts  ✅
Frequência Alunos:       89% × 0.15 = 13.4 pts  ✅
Engajamento SAE:         10% × 0.10 =  1.0 pts  🔴 (dados incompletos)
                                      ─────────
                         TOTAL:       67.3/100

DIAGNÓSTICO: O principal problema é Conformidade de Registro
(component que mais pesa: 30%). Priorizar ação sobre os
professores com semáforo vermelho (3 identificados).
```

### Comparativo entre Unidades:
```
ÍNDICE ELO — REDE COMPLETA | Semana 4

BV   ████████████████████░░░░░░  67  ⚠️
CD   ██████████████████████████  85  ✅
JG   █████████████░░░░░░░░░░░░░  51  🔴  ← FOCO URGENTE
CDR  ████████████████████░░░░░░  68  ⚠️

Meta: ──────────────────────────── 85
```

## 4.5 Como o Índice ELO aparece na Home

O Índice ELO é a primeira coisa visível. Não é escondido na lateral ou atrás de scroll. É o título operacional do dia:

```
BOM DIA, BRUNA VITÓRIA
ÍNDICE ELO — BOA VIAGEM: 67/100 ⚠️  (-3 vs semana passada)
```

E a primeira pergunta que o sistema responde automaticamente é: "por que 67 e não 85?"

---

# PARTE 5: AUTOMAÇÃO PARA REUNIÃO

## 5.1 Geração Automática de Pauta

A pauta automática funciona como uma nova função em `utils.py`:

```python
def gerar_pauta_reuniao(unidade, semana, df_aulas, df_horario,
                        df_intervencoes, max_criticos=3, max_atencao=3):
    """
    Gera pauta estruturada para reunião semanal.
    Retorna dict com seções, tempo estimado e follow-ups.
    """
    pauta = {
        'meta': {'unidade': unidade, 'semana': semana,
                 'data_reuniao': proxima_quinta(),
                 'tempo_total_min': 30},
        'criticos': [],      # Até max_criticos professores
        'atencao': [],       # Até max_atencao professores
        'follow_ups': [],    # Compromissos da semana anterior
        'positivos': [],     # Destaques positivos (1-2)
    }
    # Calcular scores e preencher seções...
    return pauta
```

**Regra de ouro:** A pauta nunca tem mais de 7 itens. Acima disso, o coordenador paralisa. A função descarta automaticamente os menos urgentes e os move para uma fila de "próxima semana".

## 5.2 Dossie Digital — Substituindo o PMV Impresso

O "Plano de Melhoria de Vida" (PMV) impresso atual é substituído por um dossie digital gerado on-demand:

**Conteúdo do dossie (para cada professor em pauta):**
1. Cronologia de conformidade das últimas 4 semanas (gráfico de linha)
2. Lista de aulas registradas vs esperadas (tabela simples)
3. Amostras dos últimos 3 conteúdos registrados (os textos reais)
4. Histórico de devolutivas anteriores com resultados
5. Comparativo: esse professor vs media da mesma disciplina na rede

**Geração:** botão "Exportar dossie de João Marcos (PDF)" → gera via `reportlab` ou `weasyprint` a partir do HTML Streamlit.

**Alternativa leve:** exportar como texto markdown estruturado que pode ser colado no WhatsApp ou impresso em 30 segundos.

## 5.3 Registro de Decisões e Follow-up

Durante a reunião, enquanto os itens de pauta são discutidos:

```
[DURANTE A REUNIÃO — MODO RÁPIDO]

Professor: Fernanda Lima
Decisão tomada: Reunião formal com gestão
Compromisso da professora: Zerar backlog de registro até Semana 6
Prazo de verificação: Semana 5 (28/02)
Quem acompanha: Bruna Vitória
[SALVAR — 1 clique]
```

Na semana seguinte, o sistema abre automaticamente com o follow-up em destaque:

```
FOLLOW-UP SEMANA PASSADA (verificar antes da reunião):
Fernanda Lima — prometeu regularizar registros até hoje
Status atual: 45% conformidade (subiu de 31%, mas ainda abaixo dos 85%)
→ Compromisso PARCIALMENTE CUMPRIDO — decidir se prorroga ou escala
```

## 5.4 WhatsApp e Telegram como Canal de Alertas Preventivos

**Fluxo proposto (implementável com Evolution API ou Bot Telegram):**

```
Segunda-feira 07:00 — ALERTA AUTOMÁTICO para o coordenador:
"Bom dia! Semana 4 começando.
Índice ELO BV: 67 ⚠️ (-3 vs semana passada)
Atenção: João Marcos não registrou nenhuma aula ainda hoje.
Fernanda Lima: última aula registrada há 6 dias.
Pauta completa: [link direto para Pg 15]"

Quarta-feira 17:00 — LEMBRETE DE PAUTA:
"Reunião amanhã às 14h.
Pauta automática já gerada: 3 críticos, 2 atenção, 1 follow-up.
[link direto para pauta]"

Sexta-feira 17:30 — RESUMO SEMANAL:
"Semana 4 encerrada.
Índice ELO BV: 71 (+4 vs início da semana)
Intervenções registradas: 3
Compromissos firmados: 2 (acompanhar na semana 5)
[resumo completo]"
```

**Implementação MVP (sem API externa):**
Botão "Enviar para WhatsApp" na Home → abre `wa.me?text=...` com o texto pré-formatado. Um clique. Zero infraestrutura adicional.

## 5.5 PDF/Relatório Pós-Reunião

Após a reunião, o coordenador clica em "Fechar reunião":

```python
def gerar_relatorio_pos_reuniao(pauta_executada, decisoes_tomadas, duracao_min):
    """Gera relatório estruturado da reunião realizada."""
    relatorio = {
        'data': datetime.now().isoformat(),
        'duracao': duracao_min,
        'presentes': decisoes_tomadas.get('presentes', []),
        'itens_discutidos': len(pauta_executada),
        'decisoes': decisoes_tomadas,
        'proximos_passos': extrair_follow_ups(decisoes_tomadas),
        'indice_elo': calcular_indice_elo(...)
    }
    return relatorio
```

O relatório é salvo em `fato_Intervencoes.csv` e pode ser exportado como PDF ou enviado automaticamente para o grupo de WhatsApp.

---

# PARTE 6: EXPERIÊNCIA DO COORDENADOR

## 6.1 Persona: Bruna Vitória Nascimento

**Dados reais do contexto:**
- Coordenadora de 6º, 7º, 8º e 9º Ano da Unidade Boa Viagem
- Supervisiona uma parte dos 107 professores da rede ELO
- Participa de 45 reuniões/ano (menos de 1 por semana letiva)
- Tem 30 minutos por reunião
- Não é técnica — sua formação é pedagógica, não em análise de dados
- Acessa o sistema em diferentes momentos: segunda cedo para planejamento, quarta para preparar pauta, quinta na reunião

**O que ela precisa:**
- Saber em 30 segundos quais são os problemas mais urgentes desta semana
- Ter histórico de conversas com professores ao alcance durante a reunião
- Registrar decisões sem precisar de uma ferramenta separada (Word, papel)
- Compartilhar informações com a equipe sem copiar/colar de uma tela para outra
- Confiar nos dados — hoje, com 43,7% de conformidade, ela sabe que os dados estão incompletos e desconta mentalmente

**O que ela não precisa:**
- Ver o calendário escolar (ela já sabe o calendário)
- Entender como funciona a API do SIGA
- Selecionar filtros em cada página que acessa
- Navegar 27 páginas para encontrar a informação relevante

## 6.2 Jornada Atual vs Jornada Ideal

### Segunda-feira, 07:15 — Preparação Semanal

**Jornada Atual:**
```
07:15 — Abre o Streamlit
07:17 — Navega até Pg 1 (Quadro de Gestão)
07:18 — Seleciona filtro "BV" + "Fundamental II"
07:20 — Vê métricas agregadas. Conformidade: 67%.
         Pensa: "Quem está puxando esse número para baixo?"
07:21 — Navega até Pg 13 (Semáforo)
07:22 — Seleciona filtro "BV" novamente
07:24 — Encontra 3 professores vermelhos
07:25 — Não sabe se esses professores estiveram vermelhos semana passada também
07:26 — Navega até Pg 14 (Alertas Inteligentes)
07:27 — Seleciona filtro "BV" novamente (terceira vez)
07:30 — Encontra lista de alertas. Tenta mentalmente identificar quais são os
         mais urgentes entre os diferentes tipos.
07:35 — Copia informações manualmente para o bloco de notas
         (TOTAL: 20 minutos, ainda não tomou nenhuma decisão)
```

**Jornada Ideal:**
```
07:15 — Abre o Streamlit. Login já lembra BV como unidade padrão.
07:15 — Home já mostra: "Índice ELO BV: 67 ⚠️ | 3 ações urgentes"
07:16 — Vê os 3 professores ordenados por urgência, com motivo e histórico
07:17 — Clica em Fernanda Lima. Vê perfil completo + histórico
07:18 — Clica em "Adicionar à pauta". Fernanda Lima aparece como #1 na pauta
07:19 — Repete para os outros 2 professores.
07:20 — Pauta está pronta. Envia para grupo WhatsApp (1 clique)
         (TOTAL: 5 minutos, 3 decisões tomadas)
```

### Quinta-feira, 14h00 — A Reunião

**Jornada Atual:**
```
14:00 — Abre laptop na reunião
14:02 — Navega até Pg 13 para mostrar o semáforo para os presentes
14:05 — Semáforo não filtra por coordenador automaticamente
14:06 — Aplica filtro BV + Fundamental II
14:07 — Discute Fernanda Lima. Precisa de dados de contexto.
14:09 — Abre nova aba, vai para Pg 5 (Progressão SAE)
14:10 — Seleciona filtro BV + Biologia + 8º Ano
14:12 — Encontra o dado de capítulo real. Volta para a discussão.
14:15 — Quer registrar a decisão. Vai para Pg 17 (Painel de Ações)
14:16 — Seleciona professor Fernanda Lima (terceira seleção manual)
14:18 — Registra ação. Volta para discussão.
14:20 — Passou 20 minutos no primeiro item. Ainda tem 2 professores na pauta.
14:25 — Encerra a reunião com os outros dois pontos sem resolver
         (TOTAL: 25 minutos, 1 de 3 itens resolvido)
```

**Jornada Ideal:**
```
14:00 — Abre o modo "Reunião" (tela cheia, sem sidebar)
14:00 — Pauta já aberta: "Item 1: Fernanda Lima — CRÍTICO"
14:01 — Dados do perfil completo visíveis: conformidade, capítulo, histórico
14:05 — Decisão tomada. Clica "Registrar decisão" → preenche 2 campos
14:06 — Item 1 encerrado. Sistema avança automaticamente para Item 2
14:10 — Item 2 resolvido
14:15 — Item 3 resolvido
14:18 — Clica "Fechar reunião". Sistema gera ata automática e envia para grupo
         (TOTAL: 18 minutos, 3 de 3 itens resolvidos, ata enviada)
```

## 6.3 Pain Points Específicos por Página

| Página | Pain Point Real | Solução |
|--------|-----------------|---------|
| 01 — Home | Métricas agregadas sem ponto de ação | Substituir por Score ELO + Top 3 ações |
| 12 — Agenda | Feedbacks salvos em JSON desconectado | Fundir com `fato_Intervencoes.csv` |
| 13 — Semáforo | Lista longa com scroll, sem histórico | Grade matricial com tendência temporal |
| 14 — Alertas | 5 tipos separados, sem score integrado | Score único + ranking de urgência |
| 15 — Resumo | Texto manual para copiar/colar | Link WhatsApp com 1 clique |
| 17 — Ações | Três JSONs desconectados | Banco de dados unificado de intervenções |
| 25 — Devolutivas | Formulário vazio, dados não auto-carregam | Pré-preenchimento automático com contexto |

## 6.4 Como o Sistema se Adapta ao Usuário

### Perfil automático por login:
```python
# Em auth.py — após check_password():
PERFIS_USUARIOS = {
    'bruna.vitoria': {
        'unidade': 'BV',
        'segmentos': ['FUND_II'],
        'role': 'coord_pedagogica',
    },
    'gilberto': {
        'unidade': 'BV',
        'segmentos': ['EM'],
        'role': 'coord_pedagogica',
    },
    # Direção ELO: vê TODAS as unidades
    'direcao': {
        'unidade': None,
        'segmentos': None,
        'role': 'direcao',
    }
}
```

### Filtros como memória:
`st.session_state` persiste os filtros durante toda a sessão. Se Bruna Vitória mudar de "Fundamental II" para "Ensino Médio" na Pg 5, o sistema pergunta: "Você quer ver EM por padrão nesta sessão?" — e lembra a resposta.

### Histórico de navegação:
O sistema aprende quais páginas são mais acessadas por cada usuário e reordena o menu automaticamente. Se Bruna Vitória sempre vai direto para Pg 13 → Pg 17, o sistema sugere "Atalho: Semáforo → Ações" como opção rápida na Home.

---

# PARTE 7: ROADMAP DE IMPLEMENTAÇÃO

## FASE 0 — O QUE PODE SER FEITO SEM CÓDIGO (Imediato, 0 dias)

Estas mudanças são organizacionais e de nomenclatura, não de código:

### Renomear as páginas
A mudança mais impactante possível sem uma linha de código: renomear os arquivos de páginas para refletir função, não número:

```
ANTES                           DEPOIS
01_📊_Quadro_Gestão.py    →  01_🏠_HOME.py
13_🚦_Semáforo_Professor.py →  02_🚦_SEMÁFORO.py
14_🧠_Alertas_Inteligentes.py→  03_⚠️_ALERTAS.py
17_🎯_Painel_Ações.py     →  04_✅_AÇÕES.py
25_💬_Devolutivas.py      →  05_💬_DEVOLUTIVAS.py
```

Páginas movidas para o final (raramente acessadas em reunião):
```
02_📅_Calendário_Escolar.py → 20_📅_REFERÊNCIA_Calendário.py
03_📚_Estrutura_Curricular.py→ 21_📚_REFERÊNCIA_Curricular.py
04_📖_Material_SAE.py       → 22_📖_REFERÊNCIA_SAE.py
```

O menu lateral do Streamlit já ordena por número. Renomear é suficiente para mudar a hierarquia de navegação.

### Configurar unidade padrão por usuário
O arquivo `auth.py` já tem `get_user_unit()`. A mudança é chamar essa função em `components.py` como padrão de todos os filtros. Custo: 5-10 linhas de código. Benefício: elimina a necessidade de selecionar unidade manualmente em cada página.

### Criar atalhos diretos entre páginas
Adicionar botões de navegação cruzada nas páginas existentes:
- Na Pg 13 (Semáforo): botão "Registrar ação sobre este professor" → abre Pg 17 com professor pré-selecionado via `st.query_params`
- Na Pg 14 (Alertas): botão "Ver devolutiva" → abre Pg 25 com professor pré-selecionado
- Na Pg 17 (Ações): botão "Ver perfil completo" → abre Pg 13 filtrado

---

## FASE 1 — Quick Wins (2 semanas)

### Semana 1:

**Tarefa 1.1 — Contexto persistente de usuário**
```python
# Em components.py — barra_filtros_padrao():
def barra_filtros_padrao(series_disponiveis, key_prefix=""):
    contexto = st.session_state.get('contexto_usuario', {})
    unidade_default = contexto.get('unidade', 'TODAS')
    # ... resto da função usa unidade_default
```
Estimativa: 2 horas. Elimina o principal atrito de uso.

**Tarefa 1.2 — Score de risco composto na Pg 14**
Combinar os 5 tipos de alerta em score único + ranking. Modifica apenas `main()` da Pg 14.
Estimativa: 4 horas.

**Tarefa 1.3 — Link WhatsApp com 1 clique na Pg 15**
Adicionar `gerar_link_whatsapp()` em `utils.py` e botão na Pg 15.
Estimativa: 1 hora.

### Semana 2:

**Tarefa 1.4 — Grade matricial no Semáforo (Pg 13)**
Substituir cards HTML por `plotly.graph_objects.Heatmap` com semanas × professores.
Dados já disponíveis em `fato_Aulas.csv`.
Estimativa: 6 horas.

**Tarefa 1.5 — Pré-preenchimento automático de devolutivas (Pg 25)**
Aceitar `st.query_params['professor']` e pré-carregar métricas via `_calcular_metricas_professor()`.
Estimativa: 3 horas.

**Tarefa 1.6 — Renomear e reorganizar páginas**
Conforme Fase 0, renomear arquivos e verificar imports.
Estimativa: 2 horas.

**RESULTADO DA FASE 1:**
- 0 alterações de banco de dados
- 0 novas dependências
- Eliminação de ~70% do atrito de navegação
- Score de urgência disponível para a reunião

---

## FASE 2 — Funcionalidades Novas (4 semanas)

### Semana 3-4:

**Tarefa 2.1 — Índice ELO**
Implementar `calcular_indice_elo()` em `utils.py` + visualização gauge na Home.
Estimativa: 8 horas.

**Tarefa 2.2 — Pauta Automática**
Implementar `gerar_pauta_reuniao()` em `utils.py` + nova página `03_PAUTA.py`.
Estimativa: 12 horas.

**Tarefa 2.3 — Banco de Intervenções Unificado**
Criar `fato_Intervencoes.csv` com schema definido. Migrar dados de `acoes_coordenacao.json` + `devolutivas.json` + `feedbacks_coordenacao.json`.
Estimativa: 8 horas.

### Semana 5-6:

**Tarefa 2.4 — Histórico temporal no Semáforo**
Calcular score de professor por semana (não só semana atual) e mostrar tendência.
Requer acumular `calcular_metricas_professor()` historicamente.
Estimativa: 10 horas.

**Tarefa 2.5 — Projeção de Capítulo Fim de Trimestre**
Implementar `projetar_capitulo_fim_trimestre()` em `utils.py` + exibição na Pg 5.
Estimativa: 6 horas.

**Tarefa 2.6 — Follow-up automático na Home**
Comparar intervenções registradas com dados atuais e exibir status de follow-up.
Estimativa: 8 horas.

**RESULTADO DA FASE 2:**
- Índice ELO funcionando por unidade
- Pauta automática gerada toda semana
- Histórico de decisões consultável
- Sistema com memória institucional real

---

## FASE 3 — Transformação Completa (8 semanas)

### Semana 7-10:

**Tarefa 3.1 — Modo Reunião**
Interface alternativa (tela cheia, sem sidebar, navegação linear) ativada por `?modo=reuniao` na URL. Facilita uso durante a reunião presencial.
Estimativa: 20 horas.

**Tarefa 3.2 — Dossie Digital PDF**
Geração de PDF por professor com gráficos de conformidade, amostras de conteúdo, histórico de devolutivas.
Requer: `reportlab` ou `weasyprint`.
Estimativa: 16 horas.

**Tarefa 3.3 — Integração SAE completa**
Finalizar `extrair_sae_digital.py` + incluir `Engajamento_SAE` no Índice ELO com peso real.
Estimativa: 20 horas (dependente de estabilidade da API SAE).

### Semana 11-14:

**Tarefa 3.4 — Alertas proativos (WhatsApp/Telegram)**
Implementar `alertas_automaticos.py` com agendamento (APScheduler ou cron) para envio automático segunda 07h + quarta 17h + sexta 17h30.
Estimativa: 24 horas + configuração de infraestrutura.

**Tarefa 3.5 — Fusão e reorganização final de páginas**
Eliminar páginas redundantes (02, 03, 04, 06, 08, 10, 11), fundir as funcionalidades relevantes nas páginas principais.
Estimativa: 30 horas (refatoração + testes).

**Tarefa 3.6 — Adaptação por perfil de usuário**
Sistema de aprendizado de preferências via `st.session_state` + arquivo de preferências por usuário.
Estimativa: 16 horas.

**RESULTADO DA FASE 3:**
- De 27 páginas para 15 páginas mais densas
- Sistema que se adapta ao usuário, não o contrário
- Alertas preventivos chegam ao coordenador antes de ele precisar acessar o sistema
- Memória institucional completa com histórico de 45 reuniões/ano
- Dossie digital substitui qualquer material impresso

---

## Tabela Resumo do Roadmap

| Fase | Duração | Custo (horas dev) | Impacto Principal |
|------|---------|-------------------|-------------------|
| 0 | Imediato | 0 | Reorganização visual, sem código |
| 1 | 2 semanas | ~18h | Elimina 70% do atrito de navegação |
| 2 | 4 semanas | ~52h | Índice ELO + pauta automática + memória |
| 3 | 8 semanas | ~126h | Transformação completa, 27→15 páginas |

**Total Fase 1+2:** 70 horas de desenvolvimento = aproximadamente 4-5 semanas de trabalho parcial (10h/semana). A maioria das mudanças não altera a base de dados existente — apenas reorganiza como os dados já disponíveis são apresentados.

---

## EPÍLOGO: POR QUE A EQUIPE B GANHA ESSA DISPUTA

A Equipe A provavelmente listará melhorias técnicas: mais gráficos, mais métricas, melhores visualizações, mais dados integrados. São melhorias válidas e importantes.

Mas a Equipe B aposta em algo diferente: **a reunião de quinta-feira às 14h é o produto final do sistema, não o dashboard.**

Tudo o que construímos, todo dado extraído do SIGA, toda normalização de disciplinas feita em `normalizacao.py`, todo alerta calculado em `calcular_metricas_professor()` — só tem valor se resultar em uma decisão tomada nessa reunião de 30 minutos.

Hoje, com 43,7% de conformidade e 1/107 feedbacks, o sistema está provando que os dados chegam mas as decisões não acontecem. Não porque os coordenadores são negligentes. Porque o design do sistema coloca a carga de síntese e priorização sobre o humano, quando deveria ser o contrário.

O sistema não pode ser mais inteligente que o coordenador. Mas pode ser mais organizado. Pode lembrar o que foi prometido semana passada. Pode calcular automaticamente quem precisa de atenção. Pode preparar a reunião antes que o coordenador chegue.

Isso é um sistema de decisão. O que existe hoje é um repositório de dados com interface gráfica.

A diferença entre esses dois produtos é a diferença entre 43,7% de conformidade e 85% de conformidade.

---

*Documento produzido pela Equipe B — PEEX 2026*
*Base de código analisado: `/Users/brunaviegas/siga_extrator/pages/` (27 arquivos) + `utils.py` (668 linhas)*
*Data: 21/02/2026*
