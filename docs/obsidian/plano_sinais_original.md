# PLANO 2 — SINAIS E REDES
## Reuniões de Monitoramento de Dados | Colégio ELO | 2026
### 45 reuniões anuais | Quartas-feiras | 45–50 minutos

---

> **O que é este plano:** Reuniões quinzenais de leitura de painel, diagnóstico de indicadores e tomada de decisão baseada em evidências. Não é reunião pedagógica de conteúdo — é reunião de gestão de dados. Todo número citado vem dos arquivos do Streamlit, Power BI ou dos CSVs em `/siga_extrator/power_bi/`.

---

## ESTRUTURA GERAL

### Os 5 Eixos de Monitoramento

| Eixo | Foco | Dashboards Principais |
|------|------|-----------------------|
| **A — Conformidade Docente** | Lançamentos SIGA, alinhamento SAE, ritmo de capítulo | `08_Alertas_Conformidade`, `13_Semáforo_Professor`, `06_Visão_Professor`, `score_Professor.csv` |
| **B — Frequência e Retenção** | Presença, evasão, busca ativa, matrícula | `20_Frequência_Escolar`, `23_Alerta_Precoce_ABC`, `score_Aluno_ABC.csv` |
| **C — Desempenho Acadêmico** | Notas, aprovação, recuperação, progressão | `21_Boletim_Digital`, `05_Progressão_SAE`, `09_Comparativos`, `fato_Notas_Historico.csv` |
| **D — Clima e Ocorrências** | Disciplina, bem-estar, prevenção | `22_Ocorrências`, `14_Alertas_Inteligentes`, `fato_Ocorrencias.csv` |
| **E — Engajamento Digital** | SAE plataforma, LMS, cruzamento SIGA×SAE | `24_Cruzamento_SIGA_SAE`, `04_Material_SAE`, `fato_Engajamento_SAE.csv`, `fato_Cruzamento.csv` |

### Formato de cada reunião (45–50 min)

| Bloco | Duração | O que fazer |
|-------|---------|-------------|
| **Leitura ao vivo** | 15 min | Abrir Streamlit/Power BI, ler números, comparar com meta SMART |
| **Diagnóstico** | 10 min | O que os dados dizem? 2 hipóteses + 2 riscos nomeados |
| **Ação por unidade** | 15 min | BV → CD → JG → CDR: o que cada coordenador faz esta semana |
| **Compromissos** | 5 min | Quem faz o quê, prazo, evidência esperada (registro em `feedbacks_coordenacao.json`) |

### Metas SMART Anuais (linha de base: Semana 4 / Fev 2026)

| Eixo | Indicador | Atual | Meta Tri 1 | Meta Tri 2 | Meta Ano |
|------|-----------|-------|-----------|-----------|---------|
| A | Conformidade média | 43,7% | 60% | 70% | 75% |
| A | Professores críticos | 41 (únicos) | ≤25 | ≤15 | ≤10 |
| A | Professores no ritmo | 12,9% | 35% | 55% | 65% |
| A | Feedbacks dados | 1/107 | 30/107 | 60/107 | 100% |
| B | Frequência média | 84,7% | 87% | 89% | ≥90% |
| B | Alunos com freq >90% | 54,1% | 65% | 72% | 78% |
| B | Alunos "Freq→Família" | 563 | ≤350 | ≤200 | ≤100 |
| C | Média de notas | 8,3 | ≥8,0 | ≥8,0 | ≥8,0 |
| C | Alunos Críticos (ABC) | 14 | ≤10 | ≤5 | 0 |
| C | Alunos Atenção+Crítico | 344 | ≤250 | ≤150 | ≤80 |
| D | Ocorrências Graves | 53 (acumulado) | Reduzir 50% ritmo | Reduzir 50% | ≤20 ano |
| D | CDR graves / semana | ~9 | ≤4/sem | ≤2/sem | ≤1/sem |
| E | Cruzamentos com dados | 1.773 "Sem Dados" | 50% ativos | 70% ativos | 80%+ |
| E | Engajamento SAE med | — | baseline | 60%+ | 80%+ |

---

## CALENDÁRIO EXECUTIVO 2026

```
I TRIMESTRE:  27/jan → 10/mai  (69 dias letivos, semanas 1–15)
II TRIMESTRE: 11/mai → 12/set  (68 dias letivos, semanas 16–33, férias jul sem 23–27)
III TRIMESTRE: 14/set → 18/dez (68 dias letivos, semanas 34–47)

Feriados que afetam quartas: Carnaval (13-17/fev, mas sem quarta),
  Data Magna PE (06/mar, sexta), Corpus Christi (04/jun, quinta),
  Independência (07/set, segunda), N.S. Aparecida (12/out, segunda),
  Consciência Negra (20/nov, sexta), N.S. Conceição (08/dez, terça)

Eventos nas quartas: 28/jan Adaptação | 25/fev Encontro Famílias |
  25/mar Posse Representantes | 01/abr Páscoa ELO | 22/abr Jogos/A2.4 |
  17/jun São João ELO | 02/set Feriado Paulista (JG) |
  09/dez Rec III Tri | 16/dez Resultados
```

---

# I TRIMESTRE
## 27 de janeiro → 10 de maio de 2026
## Tema: BASELINE — Instalar Rotinas, Calibrar Alertas, Primeiras Intervenções

> **Contexto do trimestre:** Os dados do ano estão nascendo. A `fato_Aulas.csv` tem 3.188 registros acumulados mas o trimestre começa zerado em notas (`fato_Notas_2026` = 0 registros). A conformidade está em 43,7% na semana 4 — muito abaixo dos 60% que precisamos atingir até o final do trimestre. CDR é destaque positivo em conformidade (54,6%) mas alerta máximo em ocorrências graves (36 de 53 = 68% do total). JG tem a pior frequência (79,6%) e o maior risco estudantil (25%).

---

### REUNIÃO T1-E1 — ABERTURA DO MONITORAMENTO
**Data:** 28 de janeiro de 2026 (Quarta | Semana 1 | Semana de Adaptação)
**Tipo:** E1 — Painel de Abertura / Instalação do Sistema

**Dashboards a abrir:**
- `01_Quadro_Gestão.py` → visão geral todas as unidades
- `resumo_Executivo.csv` → ler semáforos por unidade
- `02_Calendário_Escolar.py` → confirmar datas críticas do trimestre

**Pauta de 45 minutos:**

*Leitura ao vivo (15 min):*
Abrir `01_Quadro_Gestão` com filtro "Semana 1". Semana de adaptação — dados ainda não representativos, mas o painel já existe. Registrar: quantos professores já lançaram aula na semana 1? Verificar `fato_Aulas.csv` — existem registros de 28/jan? Qual o total de alunos matriculados por unidade (BV=586, CD=622, JG=456, CDR=357)?

*Diagnóstico (10 min):*
Esta reunião não é de crise — é de instalação. Perguntas a responder:
1. Todos os coordenadores sabem onde acessar o Streamlit?
2. Qual a URL de produção do sistema? Está acessível para todos?
3. O `config_coordenadores.json` está correto? (BV: Bruna Vitória/Gilberto | CD: Alline/Elisângela/Vanessa | CDR: Ana Cláudia/Vanessa | JG: Lecinane/Pietro)

*Ação por unidade (15 min):*
- **BV** (Bruna Vitória + Gilberto): Revisar lista de 586 alunos matriculados. Identificar novatos que ainda não têm histórico 2025 em `fato_Notas_Historico.csv`.
- **CD** (Alline + Elisângela + Vanessa): Revisar lista de 622 alunos. CD é a unidade com maior número — atenção especial ao volume de dados.
- **JG** (Lecinane + Pietro): Revisar 456 alunos. JG já aparece com histórico de frequência problemática — coordenadores devem receber alerta sobre isso.
- **CDR** (Ana Cláudia + Vanessa): Revisar 357 alunos. CDR tem 36 ocorrências graves acumuladas de 2025 ainda abertas — verificar se são pendências de documentação ou disciplinares reais.

*Compromissos (5 min):*
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| Todos acessam Streamlit e confirmam login | Todos coordenadores | 30/jan | Print da tela aberta |
| BV revisa lista novatos sem histórico | Bruna Vitória | 04/fev | Lista no WhatsApp da gestão |
| CDR: triagem das 36 ocorrências graves | Ana Cláudia | 04/fev | Classificação: pendência doc vs disciplinar |

---

### REUNIÃO T1-02 — EIXO A: CONFORMIDADE DOCENTE
**Data:** 4 de fevereiro de 2026 (Quarta | Semana 2)
**Eixo:** A — Conformidade Docente
**Contexto:** Primeira semana completa com dados reais. `score_Professor.csv` começa a ser populado.

**Dashboards a abrir:**
- `08_Alertas_Conformidade.py` → professores com lançamento atrasado
- `13_Semáforo_Professor.py` → visão semafórica por unidade
- `06_Visão_Professor.py` → drill-down individual

**Indicadores a ler:**
- Conformidade média por unidade (meta da semana: ≥30% — início é naturalmente baixo)
- Quantos professores já lançaram ao menos 1 aula com conteúdo preenchido?
- Quais disciplinas têm 0 lançamentos? (cruzar com `resumo_Aulas_Esperadas.csv` — 521 linhas)
- Quadrante Q4 "Crítico" do `score_Professor.csv`: quem está lá?

**Questões diagnósticas:**
1. A conformidade baixa é por desconhecimento do sistema ou resistência?
2. Quais turmas não têm nenhum registro de aula nas semanas 1-2?

**Hipóteses a testar:**
- H1: Professores novos em 2026 têm menor taxa de lançamento (cruzar com `dim_Professores.csv`)
- H2: Disciplinas com menos aulas/semana (Arte=1, Filosofia=1) têm menor conformidade por menor urgência percebida

**Riscos identificados:**
- R1: Se a conformidade ficar abaixo de 20% na semana 4, o sinal SAE fica sem dados para cruzamento
- R2: Professores que não lançaram nas semanas 1-2 raramente "recuperam" o histórico retroativamente

**Ação por unidade (15 min):**
- **BV:** Listar os 10 professores com menor conformidade. Bruna Vitória agenda conversa individual com os críticos (classificação="Crítico" no `score_Professor.csv`).
- **CD:** Verificar se Alline/Elisângela/Vanessa já deram o primeiro feedback no `feedbacks_coordenacao.json`. Meta: 5 feedbacks até a próxima reunião.
- **JG:** Lecinane faz levantamento manual: quais professores de JG lançaram na semana 1?
- **CDR:** CDR tem a melhor conformidade (54,6%) — identificar o que fazem diferente e documentar para replicar.

**Compromissos:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| BV: agenda conversa com 5 professores críticos | Bruna Vitória | 11/fev | Registro em `feedbacks_coordenacao.json` |
| CDR: descrever prática de lançamento para compartilhar | Ana Cláudia/Vanessa | 11/fev | Áudio ou texto no grupo |
| JG: levantamento manual semana 1 | Lecinane | 06/fev | Lista enviada à gestão |

---

### REUNIÃO T1-03 — EIXO B: FREQUÊNCIA E RETENÇÃO
**Data:** 11 de fevereiro de 2026 (Quarta | Semana 3)
**Eixo:** B — Frequência e Retenção

**Dashboards a abrir:**
- `20_Frequência_Escolar.py` → mapa de faltas por turma
- `23_Alerta_Precoce_ABC.py` → tier dos alunos (Verde/Monitorar/Atenção/Crítico)
- `score_Aluno_ABC.csv` → filtrar flag_A="Risco" ou "Alerta"

**Indicadores a ler:**
- Frequência média por unidade (baseline semana 4: BV=90,2% | CD=83,6% | JG=79,6% | CDR=85,5%)
- Quantos alunos com flag "Frequência → Família" por unidade (total: 563 alunos)
  - BV: verificar via `score_Aluno_ABC.csv` filtro unidade+intervencao
  - JG: espera-se proporcionalmente mais — JG tem 25% em risco
- Alunos Críticos (tier=3): 14 no total — quem são? Qual turma?
- Alunos com frequência abaixo de 42,9% (caso extremo: Camila Rangel, BV, 6ºAno — 8 faltas em 4 semanas)

**Questões diagnósticas:**
1. JG tem freq 79,6% — quais turmas puxam essa média para baixo?
2. Os 563 alunos "Freq→Família" já foram contactados? Por quem?

**Hipóteses a testar:**
- H1: A maioria das faltas de JG concentra-se nas turmas de manhã (acesso ao bairro)
- H2: Alunos novatos (sem histórico 2025) têm maior taxa de evasão precoce

**Riscos identificados:**
- R1: 563 contatos com família = volume impossível sem priorização — sem triagem, ninguém liga para ninguém
- R2: Alunos com <75% de frequência já nas semanas 1-3 têm altíssima probabilidade de reprovação por falta (25% de 205 dias = 51 dias = marca atingida em março se ritmo continuar)

**Ação por unidade (15 min):**
- **BV:** Extrair lista de alunos BV com flag "Freq→Família" do `score_Aluno_ABC.csv`. Priorizar os tier=2 (Atenção) e tier=3 (Crítico). Bruna Vitória delega 1 funcionário para ligações.
- **CD:** CD tem freq 83,6% — abaixo da meta de 87%. Identificar as 3 turmas com pior frequência.
- **JG:** URGENTE. Frequência 79,6% com 25% em risco. Lecinane mapeia: é problema de turma específica ou generalizado? Abre `20_Frequência_Escolar` filtrado por JG.
- **CDR:** Verificar se os 6 alunos CDR com flag "Freq→Família" já têm contato registrado.

**Compromissos:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| JG: mapa por turma de frequência | Lecinane + Pietro | 13/fev | Print do dashboard filtrado |
| BV: lista priorizada Tier 2-3 | Bruna Vitória | 13/fev | Lista com 10 nomes + responsável por ligar |
| CD: identificar 3 turmas críticas | Alline | 13/fev | Nomes das turmas no grupo |
| Todas unidades: definir protocolo de busca ativa | Todos | 18/fev | Texto do protocolo |

---

### REUNIÃO T1-04 — EIXO C: DESEMPENHO ACADÊMICO
**Data:** 18 de fevereiro de 2026 (Quarta | Semana 4)
**Eixo:** C — Desempenho Acadêmico
**Contexto:** Semana 4 — ainda sem notas 2026 (`fato_Notas_2026` = 0 registros). Usar histórico 2025 como proxy.

**Dashboards a abrir:**
- `09_Comparativos.py` → comparativo histórico por série/disciplina
- `05_Progressão_SAE.py` → capítulo esperado=2, onde os professores estão?
- `21_Boletim_Digital.py` → boletim 2025 dos alunos atuais
- `fato_Notas_Historico.csv` → 58.268 registros históricos

**Indicadores a ler:**
- Média de notas 2025 por unidade (proxy para 2026): BV=8,1 | CD=8,2 | JG=8,4 | CDR=8,3
- Alunos Críticos (tier=3, `score_Aluno_ABC.csv`): 14 alunos — quais disciplinas têm menor nota?
- Capítulo esperado na semana 4: Capítulo 2 (conforme `dim_Progressao_SAE.csv`)
- Quantos professores estão no capítulo 2? Quantos estão adiantados/atrasados?
- `fato_Cruzamento.csv`: 1.773 registros com status — quantos "Sem Dados" vs "Alinhado"?

**Questões diagnósticas:**
1. O histórico 2025 indica quais disciplinas têm maior risco de reprovação em 2026?
2. Os 14 alunos Críticos — qual a disciplina com menor nota no histórico?

**Hipóteses a testar:**
- H1: Matemática e Língua Portuguesa concentram as menores notas históricas (5 aulas/semana = maior exposição)
- H2: Alunos que reprovaram alguma disciplina em 2025 já estão nos tier 2 ou 3 do ABC

**Riscos identificados:**
- R1: Sem notas 2026 disponíveis ainda, a janela de intervenção precoce está fechando (A1 do trimestre será em março)
- R2: Alunos com histórico de repetência têm menor taxa de engajamento SAE — cruzar com `fato_Engajamento_SAE.csv`

**Ação por unidade (15 min):**
- **BV:** Bruna Vitória + Gilberto: Identificar 5 alunos BV com pior histórico 2025 em Matemática. Estes são os candidatos a reforço preventivo.
- **CD:** Vanessa mapeia alunos CD tier=2/3 com notas <7 em Língua Portuguesa no histórico.
- **JG:** JG tem média 8,4 (melhor das unidades) — mas 25% em risco. Paradoxo: risco é de frequência, não de nota. Pietro confirma isso nos dados.
- **CDR:** CDR: verificar se alunos tier=3 (Crítico) têm disciplinas específicas com nota <5 no histórico.

**Compromissos:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| Identificar 5 candidatos a reforço preventivo por unidade | Todos coordenadores | 25/fev | Lista de 20 alunos total |
| Confirmar data da A1 (1ª Avaliação) por unidade | Gestão + coordenadores | 25/fev | Datas no calendário |
| Reexecutar extração `fato_Notas_2026` após A1 | Bruna Marinho | Após A1 | CSV atualizado |

---

### REUNIÃO T1-05 — EIXO D: CLIMA E OCORRÊNCIAS
**Data:** 25 de fevereiro de 2026 (Quarta | Semana 5 | Encontro com as Famílias)
**Eixo:** D — Clima e Ocorrências
**Contexto:** Semana do Encontro com as Famílias — excelente timing para cruzar dados de ocorrências com o que as famílias trarão.

**Dashboards a abrir:**
- `22_Ocorrências.py` → mapa de ocorrências por unidade/tipo/gravidade
- `14_Alertas_Inteligentes.py` → alertas ativos
- `fato_Ocorrencias.csv` → 5.894 registros (inclui histórico + 2026)

**Indicadores a ler — leitura ao vivo:**
Abrir `fato_Ocorrencias.csv` filtrado por 2026. Ler:
- Total por unidade 2026: BV=2.486 | CD=1.641 | JG=767 | CDR=1.000
- Ocorrências Graves: BV=11 | CD=2 | JG=4 | CDR=36 ← **CDR = 68% do total**
- Top tipos (do dataset completo): Atraso na Entrada=212 | Indisciplina=51 | Obs. Material Didático=156
- 57 alunos com flag "Comportamento → Orientação" (`score_Aluno_ABC.csv`)

**Questões diagnósticas:**
1. CDR tem 36 ocorrências graves vs 11 de BV que tem quase o dobro de alunos — o que explica?
2. As 212 ocorrências de "Atraso na Entrada" — distribuição por unidade e horário?

**Hipóteses a testar:**
- H1: Os 36 graves de CDR concentram-se em poucas turmas ou perfil de aluno específico
- H2: Atrasos são mais frequentes no turno matutino e estão correlacionados com baixa frequência

**Riscos identificados:**
- R1: CDR com 36 graves em semana 5 = ritmo projetado de ~150 graves no trimestre se não intervir
- R2: 57 alunos "Comportamento→Orientação" sem ação registrada = escalada provável

**Ação por unidade (15 min):**
- **BV:** 11 graves — identificar os alunos envolvidos. Estão entre os 57 "Comportamento→Orientação"?
- **CD:** 2 graves — manter monitoramento. Verificar se os 51 casos de Indisciplina têm padrão de turma.
- **JG:** 4 graves — Pietro verifica se envolvem os mesmos alunos da frequência crítica.
- **CDR:** URGENTE. Ana Cláudia classifica manualmente as 36 ocorrências graves: quantas são o mesmo aluno? Existe padrão de horário/dia? Ação imediata para as próximas 2 semanas.

**Aproveitando o Encontro com Famílias (mesmo dia):**
Coordenadores têm script para mencionar aos responsáveis de alunos com ocorrência:
*"Notamos que [nome] teve [N] registros este ano. Gostaríamos de conversar sobre isso."*

**Compromissos:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| CDR: classificação das 36 ocorrências graves | Ana Cláudia | 04/mar | Planilha com: aluno, tipo real, ação tomada |
| BV: cruzar 11 graves com lista "Comportamento→Orientação" | Bruna Vitória | 04/mar | Lista integrada |
| Meta CDR: ≤4 ocorrências graves/semana a partir de agora | Ana Cláudia | Contínuo | Dashboard D semana seguinte |

---

### REUNIÃO T1-06 — EIXO E: ENGAJAMENTO DIGITAL
**Data:** 4 de março de 2026 (Quarta | Semana 6)
**Eixo:** E — Engajamento Digital (SAE × SIGA)

**Dashboards a abrir:**
- `24_Cruzamento_SIGA_SAE.py` → 4 abas: Materiais | Alunos | Engajamento | Cruzamento
- `04_Material_SAE.py` → materiais por disciplina/série
- `fato_Engajamento_SAE.csv` → 1.632 registros (aluno × material × capítulo)
- `fato_Cruzamento.csv` → 1.773 registros (turma × disciplina × semana)

**Indicadores a ler:**
- `fato_Cruzamento.csv`: quantos registros com status "Alinhado" vs "Sem Dados"?
- `fato_Engajamento_SAE.csv`: média de `pct_exercicios` por disciplina e série
- `dim_Materiais_SAE.csv`: quantos materiais ativos no LMS por série?
- Capítulo dos professores (SIGA) vs capítulo dos alunos (SAE): gap médio

**Questões diagnósticas:**
1. A maioria dos 1.773 registros de cruzamento está "Sem Dados" — por que? Professores não lançam capítulo ou alunos não acessam o SAE?
2. Quais disciplinas têm melhor alinhamento SIGA×SAE?

**Hipóteses a testar:**
- H1: O gap de alinhamento é maior nas disciplinas com menos aulas/semana (Arte=1, Filosofia=1)
- H2: Alunos tier=0 (Verde) têm pct_exercicios acima de 60%; alunos tier=2/3 têm abaixo de 20%

**Riscos identificados:**
- R1: Se a base de dados SAE não crescer, a Página 24 perde relevância como ferramenta de gestão
- R2: Professores que não identificam o capítulo no SIGA tornam o cruzamento impossível

**Ação por unidade (15 min):**
- **BV:** Bruna Vitória e Gilberto: verificar quais professores BV identificam capítulo SAE nos lançamentos SIGA.
- **CD:** Alline: fazer teste — acessar o portal SAE com credenciais da coordenação e verificar o engajamento das turmas de CD.
- **JG:** Lecinane: verificar no `fato_Engajamento_SAE.csv` se há registros de alunos de JG. Alunos JG estão acessando o SAE?
- **CDR:** Verificar se os professores CDR com maior conformidade (CDR tem 54,6%) também são os que mais registram capítulo SAE.

**Compromissos:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| Orientar professores a mencionar capítulo SAE no campo conteúdo | Todos coordenadores | 11/mar | Print de 3 exemplos bem feitos |
| Verificar acesso SAE de alunos JG | Lecinane | 11/mar | Número de alunos JG no `fato_Engajamento_SAE.csv` |
| Baseline: % de exercícios SAE concluídos por série | Bruna Marinho | 11/mar | CSV atualizado |

---

### REUNIÃO T1-07 — EIXO A (SPRINT DE CONFORMIDADE)
**Data:** 11 de março de 2026 (Quarta | Semana 7)
**Eixo:** A — Conformidade Docente (2ª passagem — sprint)
**Contexto:** Segunda leitura de conformidade. Tempo suficiente para ver se as intervenções das semanas 2-6 surtiram efeito.

**Dashboards a abrir:**
- `13_Semáforo_Professor.py` → comparar com semana 2
- `08_Alertas_Conformidade.py` → quais professores ainda estão críticos?
- `06_Visão_Professor.py` → drill-down nos que saíram do crítico
- `feedbacks_coordenacao.json` → quantos feedbacks registrados até agora?

**Indicadores a ler — comparativo semana 2 vs semana 7:**
| Indicador | Sem 2 (ref) | Meta Sem 7 | Leitura Atual |
|-----------|------------|-----------|---------------|
| Conformidade BV | ~39,5% | 45%+ | ? |
| Conformidade CD | ~39,1% | 45%+ | ? |
| Conformidade JG | ~41,3% | 47%+ | ? |
| Conformidade CDR | ~54,6% | 58%+ | ? |
| Professores críticos | 41 | ≤30 | ? |
| Feedbacks dados | 1 | ≥15 | ? |

**Questões diagnósticas:**
1. Quais professores foram abordados pelos coordenadores e mudaram de comportamento?
2. Existe correlação entre o professor receber feedback e a melhoria de conformidade?

**Sprint de ação — foco cirúrgico:**
Abrir `score_Professor.csv`, filtrar `classificacao=="Crítico"`, ordenar por `unidade`. Para cada crítico:
- Está no Q4 "Crítico" (registra pouco E conteúdo fraco)?
- Ou no Q2 "Registra pouco" mas com conteúdo bom quando registra?

Os Q4 são prioridade absoluta de intervenção.

**Ação por unidade (15 min):**
- **BV:** Bruna Vitória: dos 10 professores críticos BV, quantos ainda estão críticos? Quem melhorou? Por quê?
- **CD:** Alline: verificar os 6 críticos CD — algum saiu do crítico nas últimas 5 semanas?
- **JG:** Lecinane: JG tem 6 críticos. Algum é professor de disciplina SAE? Cruzar com `dim_Progressao_SAE.csv`.
- **CDR:** CDR tem apenas 3 críticos — meta: zero críticos até a reunião E2. Plano concreto para cada um.

**Meta da sprint:** Reduzir de 41 para 25 professores críticos até a Reunião E2 (18/mar).

**Compromissos:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| BV: feedback individual para os 10 críticos BV | Bruna Vitória + Gilberto | 18/mar | 10 entradas em `feedbacks_coordenacao.json` |
| CD: feedback para os 6 críticos CD | Alline/Vanessa | 18/mar | 6 entradas JSON |
| JG: feedback para os 6 críticos JG | Lecinane/Pietro | 18/mar | 6 entradas JSON |
| CDR: feedback para os 3 críticos CDR | Ana Cláudia/Vanessa | 18/mar | 3 entradas JSON |

---

### REUNIÃO T1-E2 — REVISÃO DE MEIO DE TRIMESTRE
**Data:** 18 de março de 2026 (Quarta | Semana 8)
**Tipo:** E2 — Painel Completo (leitura de todos os eixos)

**Dashboards a abrir:**
- `01_Quadro_Gestão.py` → visão consolidada
- `15_Resumo_Semanal.py` → resumo semana 8
- `resumo_Executivo.csv` → comparar com semana 4 (baseline)
- `17_Painel_Ações.py` → compromissos cumpridos vs pendentes

**Painel Comparativo — Semana 4 vs Semana 8:**
| Eixo | Indicador | Sem 4 (baseline) | Meta Sem 8 | Leitura |
|------|-----------|-----------------|-----------|---------|
| A | Conformidade média | 43,7% | 50% | ? |
| A | Críticos | 41 únicos | ≤28 | ? |
| A | Feedbacks dados | 1 | ≥25 | ? |
| B | Freq média | 84,7% | 85,5% | ? |
| B | Flag Freq→Família | 563 | ≤500 | ? |
| C | Alunos Críticos ABC | 14 | ≤12 | ? |
| D | Graves CDR/semana | ~9 | ≤5 | ? |
| E | Cruzamentos ativos | ~0% | 15%+ | ? |

**Diagnóstico — o que os dados dizem após 7 semanas:**
Duas hipóteses a validar:
1. CDR tem conformidade melhor porque a coordenação é mais próxima dos professores (dado de feedbacks confirma?)
2. JG tem frequência pior por fatores externos ao controle da escola (acesso, perfil socioeconômico)

**Dois riscos a nomear:**
- R1: Se a conformidade não atingir 50% na semana 8, a meta de 60% no final do trimestre é matematicamente impossível sem intervenção extraordinária
- R2: Os 563 alunos com flag de frequência são um passivo que, se não reduzido antes da A1, vai gerar uma crise de aprovação em maio

**Ação por unidade (15 min):**
Cada coordenador apresenta 3 números: o que melhorou, o que piorou, o que está estagnado no seu eixo de responsabilidade desta semana.

**Meta explícita para as próximas 7 semanas:**
- Conformidade: de onde está → 60% até 10/mai
- Frequência: de onde está → 87% até 10/mai
- Feedbacks: de onde está → 50/107 até 10/mai

**Compromissos:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| Cada unidade: plano de 4 semanas para fechar gap de conformidade | Todos | 25/mar | Documento enviado à gestão |
| Reexecutar extração de dados após A1 | Bruna Marinho | Data da A1 + 2 dias | CSVs atualizados |

---

### REUNIÃO T1-09 — EIXO B: FREQUÊNCIA — BUSCA ATIVA
**Data:** 25 de março de 2026 (Quarta | Semana 9 | Posse Representantes)
**Eixo:** B — Frequência e Retenção (busca ativa)

**Dashboards a abrir:**
- `23_Alerta_Precoce_ABC.py` → alunos tier 2 e 3
- `20_Frequência_Escolar.py` → tendência das últimas 4 semanas
- `score_Aluno_ABC.csv` → filtrar `flag_A=="Risco"` e `flag_A=="Alerta"`

**Indicadores a ler:**
- Quantos alunos já ultrapassaram 25% de faltas? (limiar de reprovação)
- Tendência de frequência: está melhorando, estável ou piorando em cada unidade?
- Alunos que tinham flag "Freq→Família" na semana 4 — quantos tiveram contato com família?
- JG: a frequência de 79,6% da semana 4 melhorou? Para quanto?

**Ação urgente — busca ativa escalonada:**
Protocolo de 3 níveis baseado no `score_Aluno_ABC.csv`:
1. **Tier 1 (Monitorar, freq<90%):** Mensagem automática via SIGA
2. **Tier 2 (Atenção, freq<75%):** Ligação do coordenador
3. **Tier 3 (Crítico, freq<50%):** Reunião presencial com família + plano de frequência

**Ação por unidade:**
- **BV:** Tier 3 BV — quantos? Reunião presencial agendada para quando?
- **CD:** Verificar se os 66 alunos CD "Atenção" receberam ligação
- **JG:** JG tem 109 alunos "Monitorar" e 112 "Atenção" — quase 50% da escola. Plano emergencial.
- **CDR:** CDR tem 84 "Atenção" = 23,5% dos alunos. Verificar se correlaciona com as ocorrências graves.

**Compromissos:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| JG: plano emergencial de frequência (protocolo 3 níveis) | Lecinane + Pietro | 01/abr | Documento com nomes e ações |
| BV: reuniões famílias tier=3 agendadas | Bruna Vitória | 08/abr | Agenda com datas |
| CDR: cruzar 84 "Atenção" com lista de ocorrências graves | Ana Cláudia | 01/abr | Lista integrada |

---

### REUNIÃO T1-10 — EIXO C: DESEMPENHO PÓS-A1
**Data:** 1 de abril de 2026 (Quarta | Semana 10 | Páscoa ELO)
**Eixo:** C — Desempenho Acadêmico (após primeira avaliação)

> **Nota:** Páscoa ELO é um evento da escola, não feriado nacional. Verificar se a reunião acontece normalmente ou se precisa ser remarcada para 02/abr (quinta).

**Dashboards a abrir:**
- `21_Boletim_Digital.py` → notas A1 se já disponíveis no SIGA
- `09_Comparativos.py` → A1 2026 vs A1 2025
- `fato_Notas_2026` → verificar se já foi reextraído após A1

**Indicadores a ler:**
- Média A1 por unidade e por disciplina
- Alunos com nota <5 na A1 por disciplina (candidatos a recuperação)
- Comparativo com A1 2025: houve queda ou melhora?
- Alunos que estão simultâneamente: freq baixa + nota baixa + ocorrência (= Crítico confirmado)

**Ação por unidade:**
- Todas: atualizar tier ABC com dados de nota A1 + frequência semana 10
- Identificar candidatos a reforço antes da A2

**Compromissos:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| Reextrair `fato_Notas_2026` e `score_Aluno_ABC.csv` | Bruna Marinho | 03/abr | CSVs com notas A1 |
| Cada unidade: lista de alunos com <5 em ≥2 disciplinas | Todos coordenadores | 08/abr | Lista para intervenção |

---

### REUNIÃO T1-11 — EIXO D: OCORRÊNCIAS — CDR EM FOCO
**Data:** 8 de abril de 2026 (Quarta | Semana 11)
**Eixo:** D — Clima e Ocorrências (foco CDR)

**Dashboards a abrir:**
- `22_Ocorrências.py` → filtro CDR, gravidade=Grave
- `14_Alertas_Inteligentes.py` → alertas CDR
- `fato_Ocorrencias.csv` → filtro `unidade=="CDR"` e `gravidade=="Grave"`

**Questão central:** As 36 ocorrências graves de CDR — em 11 semanas, o número cresceu, estabilizou ou caiu?

**Leitura ao vivo:**
Calcular a taxa semanal de graves CDR. Se na semana 4 eram 36 acumuladas, qual é o número na semana 11? Meta: ≤4/semana (seria ~28 adicionais em 7 semanas = máximo 64 total).

**Ação por unidade:**
- **CDR:** Ana Cláudia apresenta os resultados da triagem dos 36 casos originais (compromisso da reunião T1-05). Quais são recorrentes? Quais foram resolvidos?
- **Demais unidades:** Aprender com o caso CDR — que padrões preventivos estão funcionando nas outras unidades?

---

### REUNIÃO T1-12 — EIXO E: SAE DIGITAL — BASELINE CONFIRMADO
**Data:** 15 de abril de 2026 (Quarta | Semana 12)
**Eixo:** E — Engajamento Digital

**Dashboards a abrir:**
- `24_Cruzamento_SIGA_SAE.py` → aba "Engajamento"
- `fato_Engajamento_SAE.csv` → 1.632 registros — houve crescimento?
- `fato_Cruzamento.csv` → status distribution: Alinhado vs Sem Dados

**Meta desta reunião:** Confirmar o baseline de engajamento SAE para o trimestre. Ao final do trimestre, este número será a referência para o Tri 2.

**Indicadores a ler:**
- % de registros "Alinhado" em `fato_Cruzamento.csv` (cruzamento semana 1 vs semana 12)
- Média de `pct_exercicios` em `fato_Engajamento_SAE.csv` por série
- Disciplinas com melhor alinhamento SAE×SIGA

---

### REUNIÃO T1-13 — CRUZAMENTO EIXOS A+C: PROFESSOR E RESULTADO
**Data:** 22 de abril de 2026 (Quarta | Semana 13 | Jogos / A2.4)
**Tipo:** Cruzamento de eixos (A × C)

> **Nota:** Jogos ELO na mesma semana — verificar horário da reunião.

**Questão central:** Existe correlação entre a conformidade do professor e o desempenho dos alunos?

**Análise de cruzamento:**
Abrir `score_Professor.csv` e `score_Aluno_ABC.csv` lado a lado.
Para cada turma: professor com `classificacao=="Excelente"` → seus alunos têm `tier` mais baixo?

**Hipóteses a confirmar:**
- H1: Turmas com professor Excelente têm média de notas ≥0,5 ponto acima das com professor Crítico
- H2: A conformidade docente tem lag de 3-4 semanas para aparecer no desempenho dos alunos

**Ação por unidade:**
Cada coordenador identifica: qual é o seu professor com maior conformidade e qual é o desempenho médio da turma dele? E o de menor conformidade?

---

### REUNIÃO T1-14 — CRUZAMENTO EIXOS B+D: FREQUÊNCIA E COMPORTAMENTO
**Data:** 29 de abril de 2026 (Quarta | Semana 14)
**Tipo:** Cruzamento de eixos (B × D)

**Questão central:** Os alunos com mais faltas são os mesmos que geram mais ocorrências?

**Análise de cruzamento:**
Cruzar `score_Aluno_ABC.csv`:
- `flag_A` (frequência) vs `flag_C` (ocorrências)
- Quantos alunos têm simultaneamente `flag_A=="Risco"` E `ocorr_graves>0`?

**Hipóteses:**
- H1: 80% dos alunos com ocorrência grave também têm frequência abaixo de 85%
- H2: O padrão atraso→indisciplina→falta é cronológico (atraso primeiro, depois indisciplina, depois evasão)

**Ação prática:**
Identificar os alunos com os dois flags simultâneos e criar um "Protocolo Duplo" — intervenção de frequência E comportamento ao mesmo tempo.

---

### REUNIÃO T1-E3 — FECHAMENTO DO TRIMESTRE
**Data:** 6 de maio de 2026 (Quarta | Semana 15)
**Tipo:** E3 — Resultados vs Metas, Planejamento Tri 2

**Dashboards a abrir:**
- `01_Quadro_Gestão.py` → todos os indicadores
- `resumo_Executivo.csv` → semáforos finais do trimestre
- `15_Resumo_Semanal.py` → resumo da semana 15
- `17_Painel_Ações.py` → auditoria de compromissos do trimestre

**Painel Final do Trimestre — Meta vs Realizado:**
| Indicador | Baseline (Sem 4) | Meta Tri 1 | Realizado |
|-----------|-----------------|-----------|-----------|
| Conformidade média | 43,7% | 60% | ? |
| Professores críticos | 41 | ≤25 | ? |
| Feedbacks dados | 1/107 | 30/107 | ? |
| Frequência média | 84,7% | 87% | ? |
| Alunos Freq→Família | 563 | ≤350 | ? |
| Alunos Críticos ABC | 14 | ≤10 | ? |
| Graves CDR/semana | ~9 | ≤4 | ? |
| Cruzamentos ativos | ~0% | 15%+ | ? |

**Diagnóstico trimestral:**
- O que funcionou? (evidências de melhora com dados)
- O que não funcionou? (metas não atingidas — por quê?)
- Quais intervenções devem ser mantidas no Tri 2?
- Quais devem ser abandonadas?

**Planejamento para o Tri 2:**
- Ajustar metas SMART com base no realizado
- Definir novos focos por unidade
- CDR: ocorrências → plano específico
- JG: frequência → plano específico

**Compromissos do fechamento:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| Relatório de fechamento Tri 1 (dados) | Bruna Marinho | 15/mai | CSV + PDF |
| Cada coordenador: "o que aprendi este trimestre" (1 página) | Todos | 13/mai | Documento |
| Plano de Tri 2 revisado | Gestão | 13/mai | Documento aprovado |

---

# II TRIMESTRE
## 11 de maio → 12 de setembro de 2026
## Tema: TRACKING — Rastrear Progresso, Ajustar Intervenções, Escalar Sucessos

> **Contexto do trimestre:** Férias de julho (sem 23-27, 02/jul–31/jul) reduzem as quartas disponíveis de 15 para 13 — será necessário usar 2 quartas de julho (não letivas) como reuniões de coordenação, OU aceitar 13 reuniões no trimestre e compensar com 1 reunião extra no Tri 3. O plano adota 13 reuniões no Tri 2 + 15 no Tri 3 + 14 no Tri 1 = 42 ao total, mais 3 ajustes. Opção prática: manter 15 reuniões no Tri 2 usando 2 quartas em julho nas semanas 23 e 24 (reunião de coordenação durante férias — comum em colégios privados).

> **Dados disponíveis no início do Tri 2:** `fato_Notas_2026` com A1 e A2 do Tri 1, `score_Aluno_ABC.csv` atualizado, conformidade acumulada de 15 semanas.

---

### REUNIÃO T2-E1 — ABERTURA DO II TRIMESTRE
**Data:** 13 de maio de 2026 (Quarta | Semana 16)
**Tipo:** E1 — Abertura com painel completo

**Dashboards a abrir:**
- `01_Quadro_Gestão.py` → semana 16
- `resumo_Executivo.csv` → comparar semana 15 (final Tri 1) com semana 16
- `09_Comparativos.py` → resultado final Tri 1 por unidade

**Pauta:**
1. Leitura dos resultados finais do Tri 1 (foram atingidas as metas?)
2. Calibrar novas metas para o Tri 2
3. Instalar monitoramento do Tri 2 — quais novos indicadores disponíveis (notas A1+A2 Tri 1 agora em `fato_Notas_2026`)
4. Identificar os alunos em risco de reprovação por nota ou frequência ao final do Tri 1

**Metas SMART para o Tri 2:**
| Eixo | Indicador | Início Tri 2 | Meta Final Tri 2 |
|------|-----------|-------------|-----------------|
| A | Conformidade média | [resultado Tri 1] | 70% |
| A | Professores no ritmo | [resultado Tri 1] | 55% |
| A | Feedbacks acumulados | [resultado Tri 1] | 60/107 |
| B | Frequência média | [resultado Tri 1] | 89% |
| B | Alunos flag Freq | [resultado Tri 1] | ≤200 |
| C | Média de notas | [resultado Tri 1] | ≥8,0 |
| C | Alunos Críticos ABC | [resultado Tri 1] | ≤5 |
| D | Graves semana | [resultado Tri 1] | ≤2/semana CDR |
| E | Cruzamentos ativos | [resultado Tri 1] | 60%+ |

---

### REUNIÃO T2-02 — EIXO B: FREQUÊNCIA PÓS-FÉRIAS DE CARNAVAL
**Data:** 20 de maio de 2026 (Quarta | Semana 17)
**Eixo:** B — Frequência e Retenção

> **Contexto:** Carnaval foi em fevereiro (13-17/fev) mas os efeitos de absenteísmo pós-período festivo ainda ressoam. A volta do Tri 2 é o momento de ver quem "não voltou" de fato.

**Indicadores a ler:**
- Alunos que foram matriculados no Tri 1 mas não aparecem no diário de chamada no início do Tri 2 (evasão silenciosa)
- Frequência semana 16-17: houve queda típica do início de trimestre?
- Atualização do `score_Aluno_ABC.csv` — quantos alunos mudaram de tier entre o final do Tri 1 e o início do Tri 2?

**Questão crítica:** Evasão silenciosa — alunos que param de ir sem comunicar à escola. Como identificar?
Cruzar: aluno presente no `dim_Alunos.csv` (2.219) mas ausente nas últimas 10 aulas de `fato_Frequencia_Aluno.csv`.

**Ação por unidade:**
- **JG:** Prioridade máxima. Se a frequência não melhorou no Tri 2, é sinal de problema estrutural.
- **CDR:** Verificar se os alunos com ocorrências graves também tiveram queda de frequência entre trimestres.

---

### REUNIÃO T2-03 — EIXO A: CONFORMIDADE — AJUSTE DE MEIO DE ANO
**Data:** 27 de maio de 2026 (Quarta | Semana 18)
**Eixo:** A — Conformidade Docente

**Contexto:** Semana 18 = quase metade do ano letivo. A conformidade de 43,7% da semana 4 deve ter evoluído. Se ainda estiver abaixo de 60%, a meta de 75% no final do ano está em sério risco.

**Dashboards a abrir:**
- `13_Semáforo_Professor.py` → evolução da conformidade semana a semana
- `25_Devolutivas.py` → feedbacks dados até agora
- `feedbacks_coordenacao.json` → auditoria completa

**Análise de evolução:**
- Professores que saíram do tier "Crítico" e para qual tier foram (Atenção/Bom/Excelente)?
- Professores "Excelente" — o que têm em comum? (disciplina, segmento, unidade, anos de casa)
- Taxa de feedback: 1 feedback em semana 4 → quanto na semana 18?

**Compromisso desta reunião:** Cada coordenador compromete-se com 5 feedbacks adicionais nas próximas 2 semanas. O `feedbacks_coordenacao.json` será auditado na reunião seguinte.

---

### REUNIÃO T2-04 — EIXO C: NOTAS A1 TRI 2 — PRIMEIROS SINAIS
**Data:** 3 de junho de 2026 (Quarta | Semana 19)
**Eixo:** C — Desempenho Acadêmico

**Dashboards a abrir:**
- `21_Boletim_Digital.py` → notas Tri 2 (se A1 Tri 2 já aconteceu)
- `05_Progressão_SAE.py` → capítulo esperado vs realizado (semana 19 = Capítulo 5/6)
- `09_Comparativos.py` → comparativo Tri 1 vs início Tri 2

**Capítulo esperado na semana 19:** Capítulo 5 (início do Tri 2 = capítulos 5-8 conforme fórmula de progressão).

**Questão de progressão:**
Abrir `dim_Progressao_SAE.csv`: na semana 19, `capitulo_esperado` deve ser 5 para todas as disciplinas Fund II e EM. Quantos professores estão no capítulo 5? Quantos ainda estão no 3 ou 4 (atrasados)?

---

### REUNIÃO T2-05 — EIXO D: CLIMA — PRÉ-FÉRIAS
**Data:** 10 de junho de 2026 (Quarta | Semana 20)
**Eixo:** D — Clima e Ocorrências

**Contexto:** 2 semanas antes das férias de julho. Histórico de escolas: o clima piora nas semanas pré-férias. Verificar se o padrão se repete no ELO.

**Indicadores a ler:**
- Taxa de ocorrências nas semanas 18-20 vs semanas 1-5 (início do ano)
- CDR: as graves estão caindo? Meta era ≤4/semana
- Alunos "Comportamento → Orientação": o número de 57 cresceu ou caiu?
- Tipos de ocorrência: atrasos aumentam pré-férias?

**Hipótese a testar:**
H1: Atrasos (212 ocorrências acumuladas) sobem nas semanas 19-22 pré-férias

---

### REUNIÃO T2-06 — EIXO E: SAE PÓS-RETORNO
**Data:** 17 de junho de 2026 (Quarta | Semana 21 | São João Instituto ELO)

> **Nota:** São João ELO no mesmo dia — verificar se a reunião acontece pela manhã antes do evento ou é remarcada.

**Eixo:** E — Engajamento Digital
**Contexto:** Metade do ano — momento de avaliar o engajamento SAE acumulado.

**Dashboards a abrir:**
- `24_Cruzamento_SIGA_SAE.py` → todas as 4 abas
- `fato_Engajamento_SAE.csv` → evolução desde o início do ano
- `fato_Cruzamento.csv` → quantos registros "Alinhado" agora?

**Meta desta reunião:** Confirmar que pelo menos 30% dos cruzamentos estão "Alinhados" (meta mínima para o meio do ano).

---

### REUNIÃO T2-07 — PAINEL DE MEIO DE ANO (antes das férias)
**Data:** 24 de junho de 2026 (Quarta | Semana 22)
**Tipo:** Reunião especial pré-férias

**Pauta em 45 minutos:**
- 10 min: Fechar todos os indicadores antes das férias (snapshot semana 22)
- 10 min: Identificar os alunos que precisam de acompanhamento DURANTE as férias (visita domiciliar, contato família)
- 10 min: Planejar o que será feito na primeira semana de retorno (agosto)
- 15 min: Comprometer cada coordenador com 1 ação concreta nas férias para os alunos críticos

---

### REUNIÃO T2-08 — RETORNO DAS FÉRIAS — MONITORAMENTO DE EVASÃO
**Data:** 5 de agosto de 2026 (Quarta | Semana 28)
**Eixo:** B — Frequência e Retenção (foco evasão pós-férias)

> **Contexto crítico:** Retorno das férias de julho é o momento de maior risco de evasão em escolas privadas. Alunos que não voltaram = potenciais cancelamentos de matrícula.

**Dashboards a abrir:**
- `20_Frequência_Escolar.py` → semana 28 (1ª semana de retorno)
- `23_Alerta_Precoce_ABC.py` → quem mudou de tier durante as férias?
- `score_Aluno_ABC.csv` → reextraído com dados pós-retorno

**Indicadores urgentes:**
- Alunos presentes na semana 22 (antes das férias) e ausentes na semana 28: evasão potencial
- Taxa de presença na 1ª semana de retorno por unidade (meta: ≥85% todos)
- Metas de matrícula: BV=1.250, CD=1.200, JG=850, CDR=800 — quantos alunos ativos hoje?

**Alerta de matrícula:**
Cruzar `dim_Alunos.csv` (2.219 alunos) com a chamada da semana 28. Alunos ausentes por 3+ dias consecutivos sem justificativa = contato imediato.

**Ação por unidade:**
- **JG:** JG tem menor frequência — o retorno das férias é crítico. Lecinane monitora diariamente a semana 28.
- **CDR:** Verificar se alunos com ocorrências graves voltaram e se o comportamento mudou.
- **BV e CD:** Monitorar alunos que estavam em tier 2/3 antes das férias — voltaram ao mesmo tier?

---

### REUNIÃO T2-09 — EIXO A: CONFORMIDADE — ACELERAÇÃO FINAL
**Data:** 12 de agosto de 2026 (Quarta | Semana 29)
**Eixo:** A — Conformidade Docente

**Contexto:** Semana 29 — faltam apenas 4 semanas para o final do Tri 2. A meta de conformidade de 70% precisa ser atingida até 12/set.

**Sprint de conformidade final do Tri 2:**
- Abrir `score_Professor.csv`, ordenar por `pct_conformidade`
- Os 20 piores: o que há em comum? (disciplina, segmento, unidade)
- Plano de ação de 3 semanas para cada um dos 20 piores

---

### REUNIÃO T2-10 — EIXO C: NOTAS — POSIÇÃO DO ALUNO NO ANO
**Data:** 19 de agosto de 2026 (Quarta | Semana 30)
**Eixo:** C — Desempenho Acadêmico

**Contexto:** Com A1 e A2 do Tri 1 e A1 do Tri 2 disponíveis, é possível calcular a trajetória de cada aluno no ano.

**Análise de risco de reprovação:**
Alunos com média ponderada abaixo de 5,0 considerando as notas disponíveis = candidatos a recuperação ou reprovação. Identificar por série e disciplina.

**Dashboards a abrir:**
- `21_Boletim_Digital.py` → notas acumuladas
- `09_Comparativos.py` → Tri 1 vs Tri 2
- `16_Inteligência_Conteúdo.py` → qualidade do conteúdo por professor

---

### REUNIÃO T2-11 — EIXO D: OCORRÊNCIAS — ANÁLISE DE PADRÃO ANUAL
**Data:** 26 de agosto de 2026 (Quarta | Semana 31)
**Eixo:** D — Clima e Ocorrências

**Análise de padrão anual:**
Com 31 semanas de dados em `fato_Ocorrencias.csv`, é possível identificar:
- Semanas com pico de ocorrências (qual semana do ano teve mais registros?)
- Alunos reincidentes (aparecem em >3 ocorrências graves)
- Tipos em crescimento (atrasos estão aumentando ou diminuindo ao longo do ano?)

**CDR — avaliação dos 7 meses:**
Meta era ≤4 graves/semana. Está sendo cumprida? Se não, por quê?

---

### REUNIÃO T2-12 — CRUZAMENTO EIXOS A+E: PROFESSOR E PLATAFORMA
**Data:** 2 de setembro de 2026 (Quarta | Semana 32 | Feriado Paulista só JG)

> **Nota:** Feriado Paulista afeta apenas JG. Reunião ocorre normalmente para BV, CD e CDR. JG participa remotamente ou via ata.

**Tipo:** Cruzamento A × E
**Questão central:** Professores com maior conformidade SIGA têm também maior alinhamento com o capítulo SAE?

**Análise:**
Cruzar `score_Professor.csv` (classificação) com `fato_Cruzamento.csv` (status de alinhamento).
- Professores "Excelente" → quantos % dos seus cruzamentos são "Alinhado"?
- Professores "Crítico" → quantos % são "Sem Dados"?

---

### REUNIÃO T2-E3 — FECHAMENTO DO II TRIMESTRE
**Data:** 9 de setembro de 2026 (Quarta | Semana 33)
**Tipo:** E3 — Resultados vs Metas, Planejamento Tri 3

**Painel comparativo completo — Início do Ano vs Final do Tri 2:**
| Indicador | Sem 4 (base) | Meta Tri 2 | Realizado |
|-----------|-------------|-----------|-----------|
| Conformidade média | 43,7% | 70% | ? |
| Professores críticos | 41 | ≤15 | ? |
| Feedbacks dados | 1 | 60/107 | ? |
| Frequência média | 84,7% | 89% | ? |
| Alunos flag Freq | 563 | ≤200 | ? |
| Alunos Críticos ABC | 14 | ≤5 | ? |
| Graves CDR acumuladas | — | ≤40 Tri 2 | ? |
| Cruzamentos ativos | ~0% | 60%+ | ? |

**Questões estratégicas para o Tri 3:**
1. Quais alunos estão em risco de reprovação por nota ao final do ano?
2. Quais professores precisam de plano de melhoria urgente no Tri 3?
3. O engajamento SAE cresceu o suficiente para ser um indicador confiável?
4. CDR resolveu o problema de ocorrências graves?

---

# III TRIMESTRE
## 14 de setembro → 18 de dezembro de 2026
## Tema: FECHAMENTO — Projetar Resultados, Últimas Intervenções, Avaliar o Ano, Planejar 2027

> **Contexto do trimestre:** O Tri 3 é o trimestre da convergência — todos os dados do ano estão disponíveis. As decisões aqui são sobre resultados finais: aprovação/reprovação, renovação de matrícula, renovação de contrato de professores, planejamento 2027. O ritmo é mais intenso porque o tempo esgota.

> **Progressão SAE no Tri 3:** Capítulos 9-12 (semanas 34+). Professores que estão no capítulo 8 ou menos na semana 34 estão atrasados para fechar o currículo no ano.

---

### REUNIÃO T3-E1 — ABERTURA DO III TRIMESTRE
**Data:** 16 de setembro de 2026 (Quarta | Semana 34)
**Tipo:** E1 — Abertura com painel de risco de fechamento de ano

**Dashboards a abrir:**
- `01_Quadro_Gestão.py` → semana 34
- `05_Progressão_SAE.py` → capítulo esperado=9, quantos professores estão lá?
- `23_Alerta_Precoce_ABC.py` → quem está em risco de reprovação ao final do ano?
- `resumo_Executivo.csv` → semáforo geral

**Foco desta reunião:** Identificar os 3 riscos principais que podem comprometer o fechamento do ano:
1. Alunos em risco de reprovação por nota (média <5 projetada)
2. Alunos em risco de reprovação por falta (>25% de faltas até a semana 34)
3. Professores que não concluirão o currículo SAE (capítulo < 9 na semana 34)

**Metas SMART para o Tri 3:**
| Eixo | Indicador | Início Tri 3 | Meta Final do Ano |
|------|-----------|-------------|-----------------|
| A | Conformidade média | [resultado Tri 2] | 75% |
| A | Feedbacks acumulados | [resultado Tri 2] | 100% (107/107) |
| B | Frequência média | [resultado Tri 2] | ≥90% |
| B | Alunos flag Freq | [resultado Tri 2] | ≤100 |
| C | Alunos reprovados | 0 projetado | ≤3% da escola |
| D | Graves acumuladas | [resultado Tri 2] | ≤20 no Tri 3 |
| E | Engajamento SAE | [resultado Tri 2] | 80%+ |

---

### REUNIÃO T3-02 — EIXO A: CONFORMIDADE — SPRINT FINAL
**Data:** 23 de setembro de 2026 (Quarta | Semana 35)
**Eixo:** A — Conformidade Docente (sprint final)

**Contexto:** Faltam 13 semanas para o final do ano. A meta é 75% de conformidade — se está abaixo de 65% agora, é hora de ação extraordinária.

**Dashboards:**
- `13_Semáforo_Professor.py` → comparar semana 34 com semana 1 (visão de evolução anual)
- `25_Devolutivas.py` → feedbacks acumulados no ano
- `feedbacks_coordenacao.json` → auditoria final

**A grande pergunta:** Quais professores que eram "Crítico" na semana 4 ainda estão em "Crítico" ou "Atenção" na semana 35? Estes são os casos que precisam de conversa de gestão, não apenas de coordenação.

**Análise de progresso individual:**
Para cada professor que permanece crítico por >30 semanas: o problema é de capacidade ou de motivação? A resposta define a intervenção (formação vs conversa de desempenho).

---

### REUNIÃO T3-03 — EIXO B: FREQUÊNCIA — PROJEÇÃO DE REPROVAÇÃO
**Data:** 30 de setembro de 2026 (Quarta | Semana 36)
**Eixo:** B — Frequência e Retenção

**Análise preditiva de frequência:**
Com dados de 36 semanas em `fato_Frequencia_Aluno.csv` (83.818 registros), calcular:
- Para cada aluno com frequência atual X%: qual será a frequência no final do ano se o ritmo continuar?
- Quantos alunos estão no "ponto de não retorno" (mesmo comparecendo 100% até dezembro, ainda ficam abaixo de 75%)?

**Ação urgente:** Alunos no ponto de não retorno → protocolo de reclassificação ou recurso (atestado médico, justificativas).

---

### REUNIÃO T3-04 — EIXO C: NOTAS — MAPA DE APROVAÇÃO
**Data:** 7 de outubro de 2026 (Quarta | Semana 37)
**Eixo:** C — Desempenho Acadêmico

**Dashboard principal:** `21_Boletim_Digital.py` com projeção de notas finais.

**Análise de projeção:**
Com as notas disponíveis (A1+A2 Tri 1 + A1+A2 Tri 2 + A1 Tri 3), calcular a nota projetada final de cada aluno em cada disciplina. Identificar:
- Alunos com projeção de reprovação em ≥2 disciplinas (candidatos a conselho de classe de reprovação)
- Alunos com projeção abaixo de 5 em 1 disciplina (candidatos a recuperação)
- Turmas com maior % projetado de reprovação

**Meta:** Zero alunos com projeção de reprovação por nota até o final do Tri 3.

---

### REUNIÃO T3-05 — EIXO D: OCORRÊNCIAS — FECHAMENTO DISCIPLINAR
**Data:** 14 de outubro de 2026 (Quarta | Semana 38)
**Eixo:** D — Clima e Ocorrências

**Análise anual de ocorrências:**
Com `fato_Ocorrencias.csv` completo do ano:
- Total acumulado por unidade e evolução trimestre a trimestre
- CDR: a meta de ≤20 graves no Tri 3 está sendo cumprida?
- Top 10 alunos com mais ocorrências no ano — precisam de relatório para o conselho de classe
- Tipos em declínio vs tipos em crescimento (o que as intervenções resolveram?)

---

### REUNIÃO T3-06 — EIXO E: ENGAJAMENTO DIGITAL — AVALIAÇÃO FINAL
**Data:** 21 de outubro de 2026 (Quarta | Semana 39)
**Eixo:** E — Engajamento Digital

**Avaliação do ano no SAE:**
- `fato_Engajamento_SAE.csv`: evolução do pct_exercicios ao longo de 39 semanas
- `fato_Cruzamento.csv`: % de registros "Alinhado" vs "Sem Dados" no final do ano
- Disciplinas que fecharam o currículo SAE com 12 capítulos
- Disciplinas que ficaram para trás

**Questão de valor:** O SAE Digital valeu o investimento? Os dados de engajamento mostram impacto no desempenho (cruzar engajamento SAE com notas)?

---

### REUNIÃO T3-07 — CRUZAMENTO A+B+C: PROFESSOR → ALUNO (VISÃO COMPLETA)
**Data:** 28 de outubro de 2026 (Quarta | Semana 40)
**Tipo:** Cruzamento triplo A × B × C

**A grande análise do ano:**
Professor com maior conformidade → seus alunos têm melhor frequência E melhores notas?

Construir uma tabela por turma:
- `pct_conformidade` do professor (de `score_Professor.csv`)
- `frequencia_media` dos alunos da turma (de `score_Aluno_ABC.csv`)
- `media_notas` dos alunos da turma (de `score_Aluno_ABC.csv`)

**Hipótese final:** A conformidade docente explica pelo menos 30% da variância nas notas dos alunos.

---

### REUNIÃO T3-08 — CRUZAMENTO B+D: FREQUÊNCIA E COMPORTAMENTO (BALANÇO ANUAL)
**Data:** 4 de novembro de 2026 (Quarta | Semana 41)
**Tipo:** Cruzamento B × D (balanço do ano)

**Análise longitudinal:**
Os alunos que tinham `flag_A=="Risco"` na semana 4 e para os quais a escola interveio — qual é o tier deles na semana 41? A intervenção funcionou?

**Grupos de controle naturais:**
- Alunos que receberam contato de família: melhoraram?
- Alunos que NÃO receberam contato: pioraram?
- Esta análise justifica (ou questiona) o protocolo de busca ativa.

---

### REUNIÃO T3-09 — EIXO A: FEEDBACKS FINAIS (META 100%)
**Data:** 11 de novembro de 2026 (Quarta | Semana 42)
**Eixo:** A — Conformidade Docente

**Meta desta reunião:** Garantir que todos os 107 professores recebam ao menos 1 feedback registrado em `feedbacks_coordenacao.json` até o final do ano.

**Auditoria:**
- Quantos professores sem nenhum feedback registrado?
- Estes são os professores "invisíveis" — nem excelentes nem críticos, ficaram no meio
- Plano de 5 semanas para cobrir os que faltam

---

### REUNIÃO T3-10 — CONSELHO DE CLASSE DIGITAL (PRÉ-CONSELHO)
**Data:** 18 de novembro de 2026 (Quarta | Semana 43)
**Tipo:** Reunião especial — Preparação para Conselho de Classe

**Dashboards a abrir — todos simultaneamente:**
- `19_Painel_Aluno.py` → drill-down aluno por aluno nos casos limítrofes
- `21_Boletim_Digital.py` → notas projetadas finais
- `23_Alerta_Precoce_ABC.py` → tier final de cada aluno
- `18_Análise_Turma.py` → turmas com maior % de risco

**Preparação do conselho:**
Para cada aluno com risco de reprovação:
- Nota projetada por disciplina
- Frequência projetada final
- Histórico de intervenções (feedbacks, contatos com família)
- Recomendação: aprovação / recuperação / reprovação

**Output desta reunião:** Lista consolidada de alunos para o conselho de classe, com dados completos de cada um, extraída dos CSVs.

---

### REUNIÃO T3-11 — EIXO B+C: FREQUÊNCIA E NOTAS — ÚLTIMAS INTERVENÇÕES
**Data:** 25 de novembro de 2026 (Quarta | Semana 44)
**Tipo:** Cruzamento B × C (urgente — últimas 3 semanas)

**Contexto:** Faltam 3 semanas para o encerramento do ano. Esta é a última chance de intervenção real.

**Alunos no limiar:**
- Frequência entre 73-75% (podem passar ou não, dependendo das próximas semanas)
- Nota entre 4,5-5,0 em alguma disciplina (recuperação ainda possível)

**Ação cirúrgica:** Para cada aluno no limiar, um plano específico de 3 semanas:
- Frequência: contato diário com família
- Nota: reforço intensivo ou prova substitutiva

---

### REUNIÃO T3-12 — CRUZAMENTO FINAL D+E: CLIMA E DIGITAL
**Data:** 2 de dezembro de 2026 (Quarta | Semana 45)
**Tipo:** Cruzamento D × E

**Questão de pesquisa:** Alunos com melhor engajamento SAE (maior pct_exercicios) têm menos ocorrências disciplinares?

**Análise:**
Cruzar `fato_Engajamento_SAE.csv` com `score_Aluno_ABC.csv` (coluna `total_ocorrencias`).
Esta correlação, se confirmada, justifica investimento ainda maior no SAE Digital para 2027.

---

### REUNIÃO T3-13 — PRÉ-FECHAMENTO: PROJEÇÃO FINAL
**Data:** 9 de dezembro de 2026 (Quarta | Semana 46 | Recuperação III Trimestre)
**Tipo:** Reunião de projeção final

**Contexto:** Semana de recuperação do Tri 3 — as notas finais ainda não estão fechadas, mas os dados de frequência já são quase definitivos.

**Indicadores finais:**
- Alunos com frequência < 75% (reprovados por falta — definitivo)
- Alunos com média projetada < 5 (reprovados por nota — quase definitivo)
- Alunos que realizarão prova final de recuperação

**Dados para a semana final:**
Esta reunião define o que a gestão precisa saber ANTES do último dia de aula.

---

### REUNIÃO T3-E3 — FECHAMENTO DO ANO / AVALIAÇÃO ANUAL
**Data:** 16 de dezembro de 2026 (Quarta | Semana 47 | Resultado III Tri / Rec Final)
**Tipo:** E3 — Fechamento Anual + Planejamento 2027

**Esta é a reunião mais importante do ano.** Duração estendida: 90 minutos.

**Parte 1 (30 min): Resultados vs Metas Anuais**

| Indicador | Sem 4 (baseline) | Meta Anual | Realizado 2026 | Delta |
|-----------|-----------------|-----------|----------------|-------|
| Conformidade média | 43,7% | 75% | ? | ? |
| Professores críticos | 41 | ≤10 | ? | ? |
| Feedbacks dados | 1/107 | 107/107 | ? | ? |
| Professores no ritmo | 12,9% | 65% | ? | ? |
| Frequência média | 84,7% | ≥90% | ? | ? |
| Alunos freq >90% | 54,1% | 78% | ? | ? |
| Alunos Verde (ABC) | 69,2% | 85%+ | ? | ? |
| Alunos Críticos (ABC) | 14 | 0 | ? | ? |
| Média de notas | 8,3 | ≥8,0 | ? | ? |
| Graves CDR/semana | ~9 | ≤1 | ? | ? |
| Cruzamentos ativos | ~0% | 80%+ | ? | ? |

**Parte 2 (20 min): O que funcionou e o que não funcionou**

Para cada eixo, 2 perguntas:
1. Qual foi a maior vitória deste eixo em 2026? (com dados)
2. Qual foi o maior fracasso? (com dados)

Sem análise qualitativa sem número. Cada afirmação é sustentada por um indicador de um CSV.

**Parte 3 (20 min): Aprendizados para 2027**

- O sistema de monitoramento (Streamlit + Power BI + CSVs) funcionou? O que melhorar?
- As 45 reuniões foram suficientes? O formato de 45 minutos foi produtivo?
- Quais indicadores faltaram? Quais indicadores não serviram para nada?
- O cruzamento SIGA×SAE gerou valor? Vale expandir em 2027?

**Parte 4 (20 min): Planejamento 2027**

- Novas metas SMART para 2027 (a partir dos resultados de 2026)
- Calendário de reuniões 2027 (mesma estrutura ou ajustar?)
- Investimentos em dados: novos CSVs a extrair, novos dashboards a criar
- Coordenadores: avaliação de desempenho baseada em indicadores (cada coordenador recebe seu "relatório do ano")

**Compromisso final:**
| Compromisso | Responsável | Prazo | Evidência |
|-------------|------------|-------|-----------|
| Relatório anual de dados 2026 (PDF) | Bruna Marinho | 23/dez | PDF enviado à gestão |
| Cada coordenador: autoavaliação com dados | Todos | 20/dez | Documento 1 página |
| Proposta de metas SMART 2027 | Gestão + Bruna Marinho | 15/jan/2027 | Documento aprovado |
| Calendário de reuniões 2027 | Gestão | 20/jan/2027 | Calendário no sistema |

---

## APÊNDICE A — PROTOCOLO DE LEITURA DE DADOS

### Como abrir e ler os dashboards em cada reunião

**Passo 1 — Inicialização (antes da reunião)**
```
cd /Users/brunaviegas/siga_extrator
streamlit run Home.py
```
Confirmar que o Streamlit está rodando na porta 8501.

**Passo 2 — Navegar para o dashboard do eixo**
Use a sidebar para navegar. A numeração das páginas:
- Eixo A: páginas 06, 08, 13, 25 (`Visão_Professor`, `Alertas_Conformidade`, `Semáforo_Professor`, `Devolutivas`)
- Eixo B: páginas 20, 23 (`Frequência_Escolar`, `Alerta_Precoce_ABC`)
- Eixo C: páginas 05, 09, 21 (`Progressão_SAE`, `Comparativos`, `Boletim_Digital`)
- Eixo D: páginas 14, 22 (`Alertas_Inteligentes`, `Ocorrências`)
- Eixo E: páginas 04, 24 (`Material_SAE`, `Cruzamento_SIGA_SAE`)
- Geral: páginas 01, 15, 17 (`Quadro_Gestão`, `Resumo_Semanal`, `Painel_Ações`)

**Passo 3 — Leitura ao vivo com o grupo**
Projetar o dashboard. O facilitador lê em voz alta os números. Outro participante anota.
Nunca ficar mais de 3 minutos em um único número — o objetivo é ritmo, não profundidade.

**Passo 4 — Registrar compromissos**
Ao final, abrir `feedbacks_coordenacao.json` e registrar diretamente no JSON:
```json
{
  "BV_NOME_PROFESSOR_semana": {
    "data": "YYYY-MM-DD",
    "coordenador": "Nome",
    "classificacao_atual": "Crítico/Atenção/Bom/Excelente",
    "feedback": "Texto do feedback",
    "acao_combinada": "O que o professor vai fazer",
    "prazo": "YYYY-MM-DD"
  }
}
```

---

## APÊNDICE B — TABELA DE METAS SMART POR EIXO

### Eixo A — Conformidade Docente
```
Meta: Conformidade 43,7% → 60% (Tri 1) → 70% (Tri 2) → 75% (Ano)
Medição: score_Professor.csv, campo pct_conformidade
Frequência: semanal (automático via extração)
Alerta: qualquer unidade abaixo da meta de -5pp por 2 semanas seguidas
```

### Eixo B — Frequência e Retenção
```
Meta: Frequência 84,7% → 87% (Tri 1) → 89% (Tri 2) → 90%+ (Ano)
Medição: score_Aluno_ABC.csv, campo pct_frequencia
Frequência: semanal (automático)
Alerta especial JG: qualquer semana com frequência < 78% = reunião emergencial
```

### Eixo C — Desempenho Acadêmico
```
Meta: Manter média ≥ 8,0, reduzir alunos Críticos de 14 → 0
Medição: score_Aluno_ABC.csv, campos media_geral e disciplinas_abaixo_5
Frequência: por avaliação (A1, A2 de cada trimestre = 6 pontos de medição)
Alerta: qualquer disciplina com média < 7,0 em qualquer unidade
```

### Eixo D — Clima e Ocorrências
```
Meta: Reduzir graves 50% por trimestre (CDR: 36 → ≤18 → ≤9 → ≤4 no ano)
Medição: fato_Ocorrencias.csv, campo gravidade=="Grave"
Frequência: semanal (automático)
Alerta CDR: qualquer semana com >4 ocorrências graves = pauta obrigatória da próxima reunião
```

### Eixo E — Engajamento Digital
```
Meta: Cruzamentos ativos 0% → 15% (Tri 1) → 60% (Tri 2) → 80% (Ano)
Medição: fato_Cruzamento.csv, campo status=="Alinhado"
Frequência: mensal (extração SAE é mais pesada)
Alerta: se engajamento médio cair abaixo de 30% após semana 20, investigar acesso SAE
```

---

## APÊNDICE C — SEMÁFORO DE INDICADORES

### Semáforo por indicador (o que significa cada cor)

| Indicador | Verde | Amarelo | Vermelho |
|-----------|-------|---------|---------|
| Conformidade | ≥70% | 50-69% | <50% |
| Frequência | ≥90% | 85-89% | <85% |
| Alunos Críticos (ABC) | 0 | 1-5 | >5 |
| Graves/semana (CDR) | ≤1 | 2-4 | >4 |
| Feedbacks | ≥70% profs | 40-69% | <40% |
| Cruzamentos ativos | ≥70% | 40-69% | <40% |

### Critérios de convocação de reunião emergencial
Qualquer condição abaixo = reunião emergencial fora do calendário:
- JG com frequência < 75% por 2 semanas consecutivas
- CDR com >6 ocorrências graves em uma semana
- Qualquer unidade com aluno tier=3 sem intervenção registrada por >2 semanas
- Conformidade geral cair > 10pp em 1 semana (indica problema de sistema, não de professor)

---

## APÊNDICE D — COORDENADORES E RESPONSABILIDADES DE DADOS

| Unidade | Coordenador | Séries | Contato dados | Foco especial |
|---------|------------|--------|---------------|---------------|
| BV | Bruna Vitória | 6º-9º Ano | `feedbacks_coordenacao.json` (BV_*) | Eixo A (maior volume de profs críticos: 24) |
| BV | Gilberto Santos | 1ª-3ª EM | `feedbacks_coordenacao.json` (BV_*) | Eixo C (EM tem mais disciplinas) |
| CD | Alline | 9ºAno + EM | `feedbacks_coordenacao.json` (CD_*) | Eixo B (CD tem freq 83,6%) |
| CD | Elisângela Luiz | 6º Ano | `feedbacks_coordenacao.json` (CD_*) | Eixo A |
| CD | Vanessa | 7º-8º Ano | `feedbacks_coordenacao.json` (CD_*) | Eixo A |
| CDR | Ana Cláudia | 9ºAno + EM | `feedbacks_coordenacao.json` (CDR_*) | Eixo D (CDR tem 68% das graves) |
| CDR | Vanessa | 6º-8º Ano | `feedbacks_coordenacao.json` (CDR_*) | Eixo D |
| JG | Lecinane | 6º-8º Ano | `feedbacks_coordenacao.json` (JG_*) | Eixo B (JG tem freq 79,6%) |
| JG | Pietro | 9ºAno + EM | `feedbacks_coordenacao.json` (JG_*) | Eixo B |

**Responsável pelos dados (extração e atualização dos CSVs):** Bruna Marinho Wanderley Viegas
- Extração semanal: `score_Professor.csv`, `score_Aluno_ABC.csv`, `resumo_Executivo.csv`
- Extração por avaliação: `fato_Notas_2026` (após cada A1 e A2 de cada trimestre)
- Extração mensal: `fato_Engajamento_SAE.csv`, `fato_Cruzamento.csv`
- Extração contínua: `fato_Ocorrencias.csv`, `fato_Frequencia_Aluno.csv`

---

## APÊNDICE E — CALENDÁRIO RESUMIDO DAS 45 REUNIÕES

### I Trimestre (15 reuniões)
| # | Data | Semana | Tipo | Eixo |
|---|------|--------|------|------|
| T1-E1 | 28/jan | 1 | Abertura | Instalação do sistema |
| T1-02 | 04/fev | 2 | Eixo | A — Conformidade |
| T1-03 | 11/fev | 3 | Eixo | B — Frequência |
| T1-04 | 18/fev | 4 | Eixo | C — Desempenho |
| T1-05 | 25/fev | 5 | Eixo | D — Ocorrências |
| T1-06 | 04/mar | 6 | Eixo | E — SAE Digital |
| T1-07 | 11/mar | 7 | Sprint | A — Conformidade (2ª) |
| T1-E2 | 18/mar | 8 | Revisão | Painel completo |
| T1-09 | 25/mar | 9 | Eixo | B — Busca ativa |
| T1-10 | 01/abr | 10 | Eixo | C — Pós-A1 |
| T1-11 | 08/abr | 11 | Eixo | D — CDR em foco |
| T1-12 | 15/abr | 12 | Eixo | E — SAE baseline |
| T1-13 | 22/abr | 13 | Cruzamento | A × C |
| T1-14 | 29/abr | 14 | Cruzamento | B × D |
| T1-E3 | 06/mai | 15 | Fechamento | Resultados Tri 1 |

### II Trimestre (15 reuniões)
| # | Data | Semana | Tipo | Eixo |
|---|------|--------|------|------|
| T2-E1 | 13/mai | 16 | Abertura | Painel Tri 2 |
| T2-02 | 20/mai | 17 | Eixo | B — Evasão pós-férias |
| T2-03 | 27/mai | 18 | Eixo | A — Ajuste meio de ano |
| T2-04 | 03/jun | 19 | Eixo | C — Notas A1 Tri 2 |
| T2-05 | 10/jun | 20 | Eixo | D — Clima pré-férias |
| T2-06 | 17/jun | 21 | Eixo | E — SAE meio de ano |
| T2-07 | 24/jun | 22 | Especial | Snapshot pré-férias |
| T2-08 | 05/ago | 28 | Urgente | B — Evasão pós-férias jul |
| T2-09 | 12/ago | 29 | Sprint | A — Conformidade final Tri 2 |
| T2-10 | 19/ago | 30 | Eixo | C — Posição no ano |
| T2-11 | 26/ago | 31 | Eixo | D — Padrão anual |
| T2-12 | 02/set | 32 | Cruzamento | A × E |
| T2-E3 | 09/set | 33 | Fechamento | Resultados Tri 2 |
| *Extra* | *Jul (TBD)* | *23-27* | *Opcional* | *Planejamento retorno* |
| *Extra* | *Jul (TBD)* | *23-27* | *Opcional* | *Metas Tri 3* |

### III Trimestre (15 reuniões)
| # | Data | Semana | Tipo | Eixo |
|---|------|--------|------|------|
| T3-E1 | 16/set | 34 | Abertura | Risco de fechamento |
| T3-02 | 23/set | 35 | Sprint | A — Conformidade final |
| T3-03 | 30/set | 36 | Eixo | B — Projeção reprovação |
| T3-04 | 07/out | 37 | Eixo | C — Mapa de aprovação |
| T3-05 | 14/out | 38 | Eixo | D — Fechamento disciplinar |
| T3-06 | 21/out | 39 | Eixo | E — Avaliação final SAE |
| T3-07 | 28/out | 40 | Cruzamento | A × B × C |
| T3-08 | 04/nov | 41 | Cruzamento | B × D |
| T3-09 | 11/nov | 42 | Sprint | A — Feedbacks finais 100% |
| T3-10 | 18/nov | 43 | Especial | Pré-conselho de classe |
| T3-11 | 25/nov | 44 | Cruzamento | B × C urgente |
| T3-12 | 02/dez | 45 | Cruzamento | D × E |
| T3-13 | 09/dez | 46 | Especial | Projeção final |
| T3-E3 | 16/dez | 47 | Fechamento | Avaliação anual + 2027 |
| *Flex* | *TBD* | — | *Reserva* | *Se necessário* |

---

*Documento gerado em 21/02/2026.*
*Dados de referência: `resumo_Executivo.csv` (Semana 4), `score_Aluno_ABC.csv` (2.021 alunos), `score_Professor.csv` (333 registros / 107 professores únicos), `fato_Ocorrencias.csv` (5.894 registros).*
*Sistema: Streamlit (27 páginas) + Power BI (DAX v2.3) + CSVs em `/Users/brunaviegas/siga_extrator/power_bi/`.*
