# PEEX 2026 — EQUIPE A: AUDITORIA E MELHORIAS DO BI PEDAGÓGICO
## Colégio ELO | Sistema Streamlit 27 Páginas | Fevereiro 2026

**Produzido por:** Equipe A — Especialistas em Dashboards Educacionais e UX de Dados
**Data:** 21/02/2026
**Base de análise:** Leitura direta do código-fonte de todas as 27 páginas + utils.py (668 linhas)
**Contexto crítico:** 43,7% conformidade, 1/107 feedbacks, 41 professores críticos, semáforo vermelho em todas as 4 unidades

---

## PARTE 1: AUDITORIA DAS 27 PÁGINAS

### Metodologia de Avaliação

Cada página foi avaliada em três dimensões:
- **Nota (1-5) para reunião de 30 min** — o quanto ela se encaixa no fluxo real de uma coordenação
- **Status atual** — o que já funciona
- **Gap crítico** — o que impede o coordenador de tomar uma decisão ali mesmo

---

### PG 01 — Quadro de Gestão à Vista
**Nota para reunião: 3/5**

**Status atual:** Carrega `carregar_fato_aulas()` + `carregar_horario_esperado()`, calcula `calcular_semana_letiva()` e `calcular_capitulo_esperado()`, exibe 5 métricas em cards coloridos (semana, capítulo, trimestre, aulas registradas, professores registrando). Possui gauge de conformidade via `go.Indicator` com steps verde/laranja/vermelho. Gera alertas dinâmicos de disciplinas sem registro, unidades com conformidade baixa e aulas sem conteúdo.

**O que falta:**
- Não mostra delta temporal: conformidade esta semana vs semana passada. O coordenador não sabe se está melhorando ou piorando.
- Os 5 cards superiores são informativos mas não clicáveis — não levam a lugar nenhum.
- O alerta de "disciplinas sem registro" lista 5 exemplos, mas não diz o nome do professor responsável.
- Não há nenhuma indicação de "próxima reunião PEEX" ou countdown.
- O gauge de conformidade usa toda a largura de tela mas transmite uma única informação — desperdício de espaço em tela de reunião.
- Filtro de `segmento` é "Anos Finais / Ensino Médio" mas não existe filtro de coordenador — Bruna Vitória só precisa de 6º-9º, Gilberto só precisa de EM.

**Proposta de melhoria:**
Transformar em "página-capa da reunião". Adicionar coluna lateral fixa com: próxima reunião PEEX (data e tipo), professores que NÃO registraram HOJE (lista com nome + telefone), e um botão "Gerar Pauta da Reunião" que abre pg 15. O gauge pode ser reduzido à metade e ao lado exibir comparativo semana anterior como seta para cima/baixo.

---

### PG 02 — Calendário Escolar
**Nota para reunião: 2/5**

**Status atual:** Visualização do calendário 2026 com os 205 dias letivos, 7 sábados letivos e trimestres. Provavelmente usa `carregar_calendario()` e `dim_Calendario.csv` (327 dias).

**O que falta:**
- Não contextualiza "quantos dias letivos restam no trimestre atual".
- Não destaca a data da próxima reunião PEEX.
- Não mostra semana letiva atual em destaque.
- Irrelevante para a maior parte das reuniões de coordenação (útil só no início do ano e em planejamento de período).

**Proposta de melhoria:**
Transformar em widget de contexto embutido em outras páginas, não página standalone. Ou adicionar uma visão "contador de semanas restantes no trimestre" com progresso de capítulos esperados. Isso tornaria a página útil durante as reuniões.

---

### PG 03 — Estrutura Curricular
**Nota para reunião: 2/5**

**Status atual:** Provavelmente exibe a grade de disciplinas por série/unidade. Usa `carregar_disciplinas()`, `dim_Disciplinas.csv` (35 disciplinas com disciplina_id e grupo).

**O que falta:**
- Pouca relevância operacional em reunião — é uma página de referência cadastral.
- Não cruza com dados reais de conformidade por disciplina.
- Não identifica quais disciplinas têm mais problemas de registro na semana atual.

**Proposta de melhoria:**
Adicionar coluna de "saúde atual" ao lado de cada disciplina: taxa de conformidade da semana + professor responsável + dias desde último registro. Isso transforma uma página estática em radar de problemas por disciplina.

---

### PG 04 — Material SAE
**Nota para reunião: 2/5**

**Status atual:** Exibe `dim_Materiais_SAE.csv` — materiais disponíveis no portal SAE Digital por série/disciplina. Usa `carregar_materiais_sae()`.

**O que falta:**
- Não conecta o material disponível com o que está sendo ensinado (`fato_Aulas.conteudo`).
- Não indica se o professor está usando o material SAE ou ensinando conteúdo diferente.
- Não mostra engajamento dos alunos no material (`fato_Engajamento_SAE.csv`).

**Proposta de melhoria:**
Cruzar `dim_Materiais_SAE` com `fato_Aulas.conteudo` via regex de capítulo (já existe em pg 16: `CAP_PATTERNS`). Mostrar: "Material SAE disponível: Cap 3 / Professor registrou: Cap 2 (1 capítulo atrás)". Isso gera dado acionável para reunião.

---

### PG 05 — Progressão SAE
**Nota para reunião: 4/5**

**Status atual:** Cruza `fato_Aulas` com `dim_Progressao_SAE.csv` via `progressao_key`. Usa `estimar_capitulo_real()` com regex para extrair capítulo dos conteúdos registrados. Mostra capítulo esperado (`calcular_capitulo_esperado(semana)`) vs estimativa do capítulo real. Tem filtros de unidade, segmento, série e período.

**O que falta:**
- O match de 88,2% da `dim_Progressao_SAE` significa que 11,8% dos registros não cruza — esse gap precisa aparecer como warning visível.
- A função `estimar_capitulo_real()` usa regex mas não valida se o texto é só "." ou "," (conteúdo vazio disfarçado). Já pg 16 trata isso com `extrair_capitulo()` que checa `texto in ('.', '', ',')` — pg 05 deveria usar a mesma lógica.
- Não há visualização por professor: qual professor de Matemática do 7º Ano BV está mais atrasado?
- Não há barra de progresso visual "semana 4 de 15 do trimestre, capítulo 1 de 4 esperados neste trimestre".

**Proposta de melhoria:**
Adicionar heatmap de atraso curricular: eixo X = disciplinas, eixo Y = séries, cor = diferença (capítulo esperado - capítulo real). Isso dá ao coordenador uma visão instantânea de quais turmas estão mais defasadas antes da reunião começar.

---

### PG 06 — Visão do Professor
**Nota para reunião: 3/5**

**Status atual:** Gera ficha individual de professor com calendário de encontros, total de aulas esperadas no ano, metas por trimestre. Tem CSS de impressão (`@media print`) para "material imprimível". Usa `FERIADOS_2026` hardcoded. Função `calcular_encontros_disciplina()` considera feriados.

**O que falta:**
- É uma página de planejamento, não de acompanhamento — não mostra o que o professor JÁ registrou vs o que deveria ter registrado até hoje.
- O material imprimível não inclui os alertas reais do professor (se ele está em vermelho no semáforo).
- Não há campo para o coordenador anotar observações sobre aquele professor antes da devolutiva.
- `FERIADOS_2026` está hardcoded na pg 06 mas não está em `utils.py` — viola a fonte única de verdade.

**Proposta de melhoria:**
Integrar com pg 13 (Semáforo) e pg 25 (Devolutivas). A ficha impressa do professor deveria mostrar: conformidade atual, último registro, capítulo atual vs esperado, e espaço para anotação do coordenador. Isso transforma a página em ferramenta de preparo para a devolutiva.

---

### PG 07 — Instrumentos Avaliativos
**Nota para reunião: 2/5**

**Status atual:** Provavelmente analisa tipos de instrumentos avaliativos registrados nos conteúdos de aula. Usa classificação similar à de pg 16 (`KEYWORDS_AVALIACAO`, `KEYWORDS_PRATICA` etc.).

**O que falta:**
- Sem os dados de notas de 2026 (pg 21 está desativada, `fato_Notas_2026` = 0 registros), essa página tem utilidade limitada até maio/2026.
- Não conecta instrumento com resultado do aluno.
- Pouco acionável em reunião de 30 minutos.

**Proposta de melhoria:**
Adiar revisão completa para após lançamento das notas do 1º Trimestre (10/05/2026). Por ora, mostrar pelo menos a distribuição de tipos de aula registrados (Expositiva / Prática / Avaliativa / Vazio) usando `classificar_tipo_aula()` de pg 16 como referência.

---

### PG 08 — Alertas e Conformidade
**Nota para reunião: 3/5**

**Status atual:** Lista alertas ativos em tabela com `Status/Tipo/Detalhe/Ação`. Calcula conformidade por unidade usando data máxima de cada unidade (correto). Filtra por unidade, segmento, período. Tem `st.download_button` para exportar CSV. Calcula conformidade por professor com `for prof in df_aulas_filt['professor'].unique()`.

**O que falta:**
- O cálculo de conformidade por professor (linhas 258-281) itera sobre todos os professores com loop Python — em bases grandes (1.901 aulas, 107 professores) isso é lento. Deveria usar `groupby` vectorizado.
- A tabela de alertas não tem ordenação por prioridade visível — críticos e atenção ficam misturados.
- Não há botão "Marcar como resolvido" para os alertas.
- O critério "Disciplinas sem registro" gera um alerta por combinação unidade+série+disciplina, podendo gerar dezenas de alertas para o mesmo professor — o coordenador se perde.
- Tabela de "Critérios de Alerta" no topo da página é redundante e ocupa espaço que poderia ser usado pelos alertas ativos.

**Proposta de melhoria:**
Agrupar alertas por professor (não por slot). Um professor com 5 turmas sem registro vira 1 alerta com badge "5 turmas" em vez de 5 alertas separados. Adicionar coluna "Responsável pela ação" (nome do coordenador) e status (Novo / Em acompanhamento / Resolvido) com persistência em JSON — similar ao que pg 17 já faz com `ACOES_FILE`.

---

### PG 09 — Comparativos
**Nota para reunião: 4/5**

**Status atual:** Três tabs: "Entre Unidades", "Mesma Disciplina", "Entre Séries". Tab 1 calcula conformidade por unidade com data máxima individual (evita distorção por unidade com menos dados). Tab 2 permite ver todos os professores de uma mesma disciplina lado a lado.

**O que falta:**
- Não há comparativo temporal: unidade X esta semana vs semana passada — só consegue ver snapshot atual.
- Tab "Mesma Disciplina" é a mais valiosa para reunião de rede (todos os professores de Matemática dos 4 unidades) mas não aparece em destaque.
- Não exibe ranking: "qual unidade melhorou mais esta semana?"
- Não há comparativo de progressão SAE entre unidades.

**Proposta de melhoria:**
Adicionar tab "Evolução Semanal" com gráfico de linha por unidade nas últimas 4 semanas — usando `df_aulas.groupby(['unidade', 'semana_letiva']).size()`. Isso responde à pergunta mais frequente na reunião de rede: "estamos melhorando ou piorando em relação à semana passada?"

---

### PG 10 — Detalhamento de Aulas
**Nota para reunião: 2/5**

**Status atual:** Tabela detalhada de `fato_Aulas.csv` com todas as colunas. Permite busca e filtragem granular.

**O que falta:**
- Muito granular para uma reunião de 30 min — é ferramenta de auditoria, não de gestão.
- Não há highlight visual de registros problemáticos (conteúdo vazio, data muito antiga).
- Útil para coordenador que quer investigar um professor específico pós-reunião.

**Proposta de melhoria:**
Adicionar filtro "Mostrar apenas problemáticos" que filtra `conteudo.isin(['.', ',', '-', '']) | conteudo.isna()`. Adicionar coluna calculada "Qualidade do Registro" usando `calcular_score_qualidade()` de pg 16. Isso torna a página útil como drill-down a partir de alertas.

---

### PG 11 — Material do Professor
**Nota para reunião: 2/5**

**Status atual:** Provavelmente gera material de referência para o professor (sequência de capítulos, datas, etc.). Usa dados de `dim_Progressao_SAE` e `dim_Horario_Esperado`.

**O que falta:**
- Sem integração com dados reais de registro — não mostra gap.
- Pouco acionável em reunião de coordenação (é voltado ao professor, não ao coordenador).

**Proposta de melhoria:**
Integrar com pg 13 para que o material gerado para o professor inclua seu status atual no semáforo. Gerar uma versão "Contexto pré-devolutiva" que o coordenador imprime antes de chamar o professor.

---

### PG 12 — Agenda da Coordenação
**Nota para reunião: 4/5**

**Status atual:** Gestão de feedbacks/observações de aula por coordenador. Tem `CONFIG_FILE` (`config_coordenadores.json`) e persistência JSON. Inclui botão para atualizar dados do SIGA via `subprocess.run(["python3", atualizar_siga.py])`. Detecta ambiente cloud com `is_cloud()`. Sidebar com "Última atualização" via `ultima_atualizacao()`.

**O que falta:**
- O botão de atualização do SIGA na sidebar é ótimo mas funciona apenas localmente (`not is_cloud()`). No deploy no Render, o coordenador não consegue atualizar os dados.
- Não há visão de "quem ainda não recebeu feedback este trimestre" — crucial dado que apenas 1/107 professores recebeu feedback.
- A agenda não mostra alertas dos professores que têm visita agendada: seria útil ver "Visita com Prof. X amanhã → ele está em VERMELHO no semáforo".
- Não integra com pg 25 (Devolutivas) — agenda e ficha de devolutiva são desconexas.

**Proposta de melhoria:**
Criar painel "Pendências de Feedback" que lista todos os professores que não receberam devolutiva este trimestre (carregando `devolutivas.json` de pg 25). Badge numérico: "87 professores sem feedback". Link direto para iniciar devolutiva a partir da agenda.

---

### PG 13 — Semáforo do Professor
**Nota para reunião: 5/5** — MELHOR PÁGINA PARA REUNIÃO

**Status atual:** Calcula métricas por professor via `calcular_metricas_professor()`: taxa de registro, taxa de conteúdo, taxa de tarefa, dias sem registro. Classifica em verde/amarelo/vermelho/cinza. Mostra cards resumo (n_verde, n_amarelo, n_vermelho+n_cinza, % saúde da rede). Exibe matriz por unidade com gráfico de barras empilhado. Tabela detalhada ordenada por prioridade (vermelho primeiro). Filtro de cor (Crítico / Atenção / OK / Sem dados). Critério verde: `taxa_registro >= 80 AND taxa_conteudo >= 60`.

**O que falta:**
- A tabela final mostra colunas "Cor" (texto) e "Status" (emoji) — redundantes. Ocupa espaço.
- "Dias Sem Registro" pode ser 0 mesmo para professor em vermelho (registrou aulas antigas mas não esta semana).
- Não há link direto "Iniciar Devolutiva" na linha do professor vermelho.
- Não há histórico: o professor estava vermelho na semana passada também? É tendência ou acontecimento pontual?
- O critério de cor é hardcoded na função (`>= 80` e `>= 60`) — deveria ser configurável por `CONFORMIDADE_META` e `CONTEUDO_VAZIO_ALERTA` de utils.py.

**Proposta de melhoria:**
Adicionar coluna "Tendência" com seta: comparando taxa de registro da semana atual vs semana anterior via `df_aulas.groupby(['professor', 'semana_letiva']).size()`. Adicionar botão "Chamar para reunião" que cria entrada em `acoes_coordenacao.json` (já existe em pg 17). Isso fecha o loop: semáforo → ação → acompanhamento.

---

### PG 14 — Alertas Inteligentes
**Nota para reunião: 4/5**

**Status atual:** Detecta 5 tipos de alerta via `detectar_alertas()`: VERMELHO (Professor Silencioso), AMARELO (Registro em Queda — queda >30% vs semana anterior), LARANJA (Currículo Atrasado — <50% conformidade), AZUL (Frequência Pendente — >5 dias sem registro), ROSA (Disciplina Órfã — zero registros). Calcula `calcular_score_risco()` por professor. Tem filtros de unidade, segmento, período e cor de alerta.

**O que falta:**
- O Alerta VERMELHO (Professor Silencioso) usa `semana_atual` de `calcular_semana_letiva()` — sem parâmetros, usa `_hoje()`. Mas `_hoje()` retorna `datetime.now()`, e no início da semana (segunda-feira) ainda há poucos registros — gera falso positivo nos primeiros 2 dias da semana.
- O Alerta AMARELO compara semana N-1 com N-2, não semana atual com N-1 — detecta queda com 1 semana de atraso.
- O Score de Risco (`calcular_score_risco`) está implementado mas não é exibido na tela principal — fica escondido.
- Não há ação direta na tela: o coordenador vê os alertas mas precisa ir manualmente para pg 25 iniciar devolutiva.
- `detectar_alertas()` tem `@st.cache_data(ttl=300)` mas recebe DataFrames como argumento — pode ter comportamento inesperado com caching de objetos mutáveis.

**Proposta de melhoria:**
Exibir o Score de Risco como métrica principal ao lado do tipo de alerta. Adicionar botão "Registrar Providência" inline que salva em `acoes_coordenacao.json`. Corrigir falso positivo do alerta VERMELHO adicionando tolerância de 2 dias no início da semana: `if dias_sem < 2: continue`.

---

### PG 15 — Resumo Semanal
**Nota para reunião: 5/5** — IMPRESCINDÍVEL PARA O INÍCIO DE CADA REUNIÃO

**Status atual:** Gera duas versões de relatório: `gerar_resumo_texto()` (formato WhatsApp com emojis e bold) e `gerar_resumo_reuniao()` (formato tabular detalhado). Calcula métricas por unidade: conformidade, aulas total, aulas na semana, profs ativos, profs sem registro, taxa de conteúdo. Lista disciplinas sem registro na semana. Inclui seção de "Pontos de Atenção" automáticos.

**O que falta:**
- O relatório de texto usa `'\n'.join(linhas)` sem distinção de negrito HTML — no Streamlit aparece como texto plano (os asteriscos do WhatsApp aparecem literalmente).
- `gerar_resumo_reuniao()` gera texto sem HTML — mas a página provavelmente usa `st.text_area()` para exibir, não `st.markdown()` — desperdiça formatação.
- Não há geração de PDF — é o que mais falta para reunião presencial.
- "Pontos de Atenção" repete os alertas já visíveis no topo — poderia ser a seção mais útil mas está no final, depois de todo o scroll.
- O parâmetro `feriados_impacto=15` em `calcular_encontros_disciplina()` de pg 06 é hardcoded mas poderia ser derivado de `dim_Calendario.csv` que já tem os dias letivos.

**Proposta de melhoria:**
Reposicionar "Pontos de Atenção" para o topo do relatório. Adicionar `st.download_button` com relatório em .txt já existe em outras páginas — replicar aqui. Para PDF: usar `fpdf2` ou `reportlab` (já disponíveis no Python) gerando um arquivo com logo do ELO, tabela de métricas e lista de alertas — exatamente o documento que o coordenador leva impresso para a reunião.

---

### PG 16 — Inteligência de Conteúdo
**Nota para reunião: 3/5**

**Status atual:** Analisa `fato_Aulas.conteudo` com regex (`CAP_PATTERNS`) e NLP simples. Funções: `extrair_capitulo()`, `classificar_tipo_aula()`, `calcular_score_qualidade()`. Detecta capítulos mencionados nos registros, classifica tipo de aula (Avaliativa / Projeto / Prática / Leitura / Expositiva / Vazio / Outro). Usa `KEYWORDS_*` para classificação.

**O que falta:**
- `calcular_score_qualidade()` está definida mas a lógica de score não é mostrada na documentação lida — o resultado pode ser opaco para o coordenador ("score 67 — por quê?").
- `CAP_PATTERNS` inclui "Unidade" e "Módulo" como equivalentes de capítulo — pode gerar falso positivo em escolas que usam "Unidade 1" para algo diferente do capítulo SAE.
- A pg 16 e a pg 05 têm funções `extrair_capitulo()` duplicadas com lógicas ligeiramente diferentes — viola DRY. Deveria haver uma única `extrair_capitulo()` em `utils.py`.
- Não há análise de qualidade ao longo do tempo — o score de qualidade está melhorando ou piorando semana a semana?

**Proposta de melhoria:**
Consolidar `extrair_capitulo()` em `utils.py` para uso unificado. Adicionar gráfico de evolução do score de qualidade por semana letiva. Exibir "Top 10 registros mais ricos" (maior score) como exemplos positivos para compartilhar na reunião — reconhecimento de boas práticas.

---

### PG 17 — Painel de Ações
**Nota para reunião: 4/5**

**Status atual:** Gera diagnóstico automático por professor via `diagnosticar_professor()`. Calcula prioridade (0=ok, 1=atenção, 2=urgente, 3=crítico) baseado em conformidade, conteúdo vazio, dias sem registro. Usa `ACOES_FILE = WRITABLE_DIR / "acoes_coordenacao.json"` para persistência. Tem `DIA_REUNIAO_SEMANAL = 3` (quinta-feira). `carregar_config_coords()` lê `CONFIG_FILE`.

**O que falta:**
- `DIA_REUNIAO_SEMANAL = 3` está hardcoded — pode não ser quinta para todas as unidades (CD pode ter segunda, JG pode ter terça).
- O diagnóstico por professor usa loop Python sobre todos os professores — mesmo problema de performance de pg 08. Para 107 professores com 1.901 registros, pode ser lento.
- Não há visão de "checklist da reunião de hoje": quais ações foram definidas na última reunião? Foram executadas?
- Os arquivos `acoes_coordenacao.json` e `config_coordenadores.json` são globais (sem distinção por unidade) — o coordenador BV vê as ações do coordenador CDR.

**Proposta de melhoria:**
Separar `ACOES_FILE` por unidade: `f"acoes_{unidade}.json"`. Adicionar seção "Ações Abertas da Última Reunião" que lista o que ficou pendente e permite marcar como concluído — cria continuidade entre reuniões, eliminando o esquecimento de combinados.

---

### PG 18 — Análise por Turma
**Nota para reunião: 4/5**

**Status atual:** Calcula `calcular_saude_turma()` com score 0-100 por disciplina (60% conformidade + 40% qualidade de conteúdo). Usa regex para extrair capítulo via `CAP_PATTERNS`. Permite selecionar unidade, série e ver todas as disciplinas daquela turma em uma visão cross-disciplina.

**O que falta:**
- `calcular_saude_turma()` tem `@st.cache_data(ttl=300)` mas recebe objetos DataFrame como parâmetros — o Streamlit pode não cachear corretamente se o DataFrame mudar.
- Não há comparativo com outras turmas da mesma série em outras unidades — qual 7º Ano está indo melhor: BV ou CD?
- Não mostra frequência média da turma ao lado do score de saúde.
- Não indica quantos alunos da turma estão no tier 2 ou 3 do sistema ABC (pg 23).

**Proposta de melhoria:**
Adicionar coluna "Alunos em Risco ABC" usando `score_Aluno_ABC.csv` (já existe em `power_bi/`). Isso conecta a visão de turma (saúde do ensino) com a visão de aluno (risco de fracasso). É o dado que o coordenador mais precisa para priorizar qual turma discutir na reunião.

---

### PG 19 — Painel do Aluno
**Nota para reunião: 4/5**

**Status atual:** Perfil 360° do aluno: notas via `carregar_notas()`, frequência via `carregar_frequencia_alunos()`, ocorrências via `carregar_ocorrencias()`, aulas da turma via `carregar_fato_aulas()`. Radar de desempenho via `go.Scatterpolar`. Funções: `calcular_media_trimestral()`, `calcular_frequencia_aluno()`, `status_frequencia()`.

**O que falta:**
- Depende de `dim_Alunos.csv` (2.219 alunos) — se não extraído, exibe warning e para. A extração de alunos do SIGA é processo separado e pode estar desatualizada.
- Não mostra o score ABC do aluno (pg 23 calcula mas pg 19 não consome `score_Aluno_ABC.csv`).
- Não há botão "Registrar Ocorrência" direto do perfil do aluno — o coordenador precisa ir para pg 22.
- O radar de desempenho usa `go.Scatterpolar` com eixos de notas por disciplina — mas se notas de 2026 ainda não existem (`fato_Notas_2026` = 0 registros), o radar fica vazio ou usa dados históricos sem indicar claramente isso.

**Proposta de melhoria:**
Adicionar badge de "Tier ABC" no topo do perfil (Tier 0=Verde, 1=Amarelo, 2=Laranja, 3=Vermelho). Adicionar botão "Registrar Ocorrência" que pré-preenche `aluno_id`, `aluno_nome`, `unidade` e `serie` e abre pg 22 — elimina retrabalho.

---

### PG 20 — Frequência Escolar
**Nota para reunião: 4/5**

**Status atual:** Usa `carregar_frequencia_alunos()` que lê `fato_Frequencia_Aluno.csv` (20.805 registros, 1.268 alunos). Fallback para `carregar_frequencia_historico()` se arquivo não existe. Detecta fonte dos dados com badge visual ("Dados reais de frequência 2026" ou aviso de histórico). Filtros: unidade, segmento, série, disciplina, turma. `_color_freq()` colore células da tabela. Threshold LDB: `THRESHOLD_FREQUENCIA_LDB = 75`.

**O que falta:**
- JG está em 79,6% de frequência média — isso está abaixo dos 85% de excelência mas acima do mínimo LDB. A página não destaca esse número de forma diferenciada para JG.
- Não há visão temporal: a frequência está caindo ou estabilizando? Qual semana foi pior?
- Não há listagem de "alunos com falta em 3+ disciplinas na mesma semana" — sinal forte de evasão iminente.
- Filtro de disciplina lista todas as disciplinas — em reunião de coordenação, o filtro mais útil seria "Mostrar apenas alunos abaixo de 75%".

**Proposta de melhoria:**
Adicionar tab "Risco de Reprovação" que lista apenas alunos com `pct_frequencia < THRESHOLD_FREQUENCIA_LDB`, ordenados pelo percentual (pior primeiro), com coluna "Faltas restantes antes de reprovar" calculada como: `(total_aulas_previstas * 0.25) - faltas_atuais`. Isso é o dado que o coordenador precisa levar para contatar a família.

---

### PG 21 — Boletim Digital
**Nota para reunião: N/A — PÁGINA DESATIVADA**

**Status atual:** Desativada com `st.stop()`. Mensagem: "Notas trimestrais de 2026 ainda não foram lançadas. O 1º Trimestre termina em 10/05/2026."

**O que falta:**
- Nada a fazer até 10/05/2026.
- Quando reativar, garantir que usa dados de `fato_Notas_2026` e não confunde com `fato_Notas_Historico.csv`.

**Proposta de melhoria:**
Criar uma versão "placeholder" que mostra notas históricas de anos anteriores como referência, com aviso claro "dados de 2025". Isso permitiria ao coordenador comparar "aluno X teve 4.2 em Matemática em 2025 — está no perfil de risco" mesmo antes das notas de 2026.

---

### PG 22 — Ocorrências Disciplinares
**Nota para reunião: 4/5**

**Status atual:** 6 tabs quando há dados: "Novo Registro", "Alunos em Risco", "Visão Geral", "Por Turma", "Por Aluno", "Detalhamento". Filtros na sidebar: período, unidade (multi-select via `filtro_unidade_multi`), segmento, tipo. `TIPOS_OCORRENCIA` com 12 tipos. `GRAVIDADES = ['Leve', 'Media', 'Grave']` (sem acento em Media — conforme documentação). `PROVIDENCIAS_SUGERIDAS` por gravidade. Dados: 4.948 ocorrências (BV=2136, CD=1397, CDR=805, JG=610). CDR tem 68% das graves (mencionado no contexto).

**O que falta:**
- A tab "Alunos em Risco" é a mais valiosa para reunião mas não aparece em primeiro lugar — "Novo Registro" fica na frente e tem menos relevância gerencial.
- Não há visão "CDR tem 68% das ocorrências graves" destacada na tela — é o insight mais crítico mas está enterrado nos dados.
- Não há correlação com frequência: alunos com muitas ocorrências tendem a ter frequência baixa?
- O formulário de "Novo Registro" pede `aluno_id` mas alunos do SIGA têm IDs numéricos — o coordenador pode não saber o ID do aluno de cabeça.

**Proposta de melhoria:**
Reordenar tabs: primeiro "Alunos em Risco", depois "Por Turma" e "Visão Geral". Adicionar no topo da página um card destacado: "CDR: X% das ocorrências graves nesta semana" com comparativo da semana anterior. Usar busca por nome no formulário de registro (não por ID) com autocomplete via `dim_Alunos.csv`.

---

### PG 23 — Alerta Precoce ABC
**Nota para reunião: 5/5** — MELHOR FERRAMENTA DE INTERVENÇÃO

**Status atual:** Framework A (Attendance) + B (Behavior) + C (Coursework). `calcular_score_abc()` retorna flags, tier (0-3) e score (0-100). Thresholds: A={risco:85, critico:75}, B={risco:2, critico:5}, C={risco:5.0, critico:3.0}. Tier 3 = 3 flags simultâneas = intervenção intensiva. Pesos: A=30%, B=30%, C=40%.

**O que falta:**
- Os thresholds estão hardcoded em `ABC_THRESHOLDS` — deveriam ser configuráveis por segmento (EM pode ter critérios diferentes do Fundamental).
- Tier 3 com 3 flags simultâneas é correto mas há casos de aluno com score 95/100 em apenas uma dimensão que pode ser mais urgente que um aluno com score 40/100 em 3 dimensões — o tier não captura isso.
- Não há histórico de tier: o aluno estava em Tier 2 no mês passado e agora está em Tier 3? Essa progressão é o sinal mais importante.
- Falta "plano de ação sugerido" por tier: Tier 3 → quem acionar (família? direção? psicólogo?).
- `score_Aluno_ABC.csv` existe em `power_bi/` mas outras páginas (pg 18, pg 19) não consomem esse arquivo.

**Proposta de melhoria:**
Adicionar campo "Intervenção Registrada" por aluno, persistido em JSON, que o coordenador preenche após a reunião. Isso cria o loop: identificar (ABC) → intervir (registro) → monitorar (ABC na semana seguinte). Conectar `score_Aluno_ABC.csv` com pg 19 e pg 18.

---

### PG 24 — Cruzamento SIGA x SAE
**Nota para reunião: 3/5**

**Status atual:** 4 abas de cruzamento entre dados SIGA (fato_Aulas) e SAE Digital (dim_Materiais_SAE, dim_Alunos_SAE, fato_Engajamento_SAE). Match de alunos por nome normalizado + série + unidade (~85% esperado). Detecta capítulo via regex `cap(?:ítulo|\.?)\s*(\d{1,2})` nos conteúdos do SIGA.

**O que falta:**
- `fato_Engajamento_SAE.csv` ainda está marcado como "novo - rodar extrair_sae_digital.py" — pode estar vazio ou incompleto.
- O cruzamento professor SIGA x material SAE é o dado mais estratégico: professor registrou Cap 3 no SIGA mas alunos estão fazendo exercícios de Cap 2 no SAE — isso indica que o professor avançou mas os alunos não.
- Não há score de engajamento agregado por turma para levar à reunião.

**Proposta de melhoria:**
Criar uma métrica composta: "Alinhamento Docente-Discente" = correlação entre capítulo registrado pelo professor (SIGA) e progresso dos alunos no material (SAE). Professores com alta taxa de registro mas alunos com baixo engajamento SAE são um problema diferente de professores com baixo registro.

---

### PG 25 — Devolutivas Personalizadas
**Nota para reunião: 5/5** — FERRAMENTA CENTRAL DO PEEX

**Status atual:** Modelo 3C's + SBI + Feedforward. `_calcular_metricas_professor()` calcula taxa de registro, taxa de conteúdo, taxa de tarefa, séries, disciplinas, dias sem registro para contextualizar a devolutiva. Persistência em `devolutivas.json`. Sidebar com seleção de unidade e professor. CSS com classes `.ccc-comecar`, `.ccc-cessar`, `.ccc-continuar`, `.ccc-feedforward`, `.ccc-combinados`, `.ccc-sbi`.

**O que falta:**
- Apenas 1/107 professores recebeu feedback — o sistema existe mas não está sendo usado. Problema de adoção, não de funcionalidade.
- `devolutivas.json` é arquivo local sem backup na nuvem — se o coordenador trocar de máquina, perde o histórico.
- Não há visualização "Histórico de Devolutivas do Professor X" — para ver se os combinados da última reunião foram cumpridos.
- Não há template de devolutiva pré-preenchido com os alertas do professor (pg 14 detecta o problema, pg 25 não consome esses dados automaticamente).
- Sem integração com pg 12 (Agenda) — não sabe se há visita agendada para aquele professor.

**Proposta de melhoria:**
Criar "Contexto Automático da Devolutiva": ao selecionar o professor, a página carrega automaticamente: semáforo atual (pg 13), alertas ativos (pg 14), última devolutiva registrada (pg 25 histórico) e próxima visita agendada (pg 12). O coordenador entra na reunião já preparado, sem precisar navegar por 4 páginas diferentes.

---

### PG 26 — Painel Unificado
**Nota para reunião: 4/5**

**Status atual:** Integra `vagas.db` (SQLite de `/Users/brunaviegas/Downloads/Cópia BI/output/`) com dados pedagógicos do SIGA. `METAS_2026` por unidade (BV=1250, CD=1200, JG=850, CDR=800). Usa `shared_domain.py` com `UNIDADES_CANONICAL`, `traduzir_unidade_vagas_para_pedagogico()`. Carrega matrículas 2026 e 2025 para cálculo de evasão.

**O que falta:**
- `VAGAS_DB_PATH = Path("/Users/brunaviegas/Downloads/Cópia BI/output/vagas.db")` — caminho hardcoded na máquina local. No deploy no Render, isso quebra silenciosamente.
- Não há correlação direta: alunos com muitas faltas têm maior probabilidade de evasão? Esse cruzamento seria a killer feature do painel unificado.
- Não há destaque para "alunos pré-matriculados em risco" — alunos que entraram recentemente e já têm sinais de abandono.

**Proposta de melhoria:**
Usar variável de ambiente `VAGAS_DB_PATH` em vez de caminho hardcoded. Adicionar seção "Risco de Evasão" que cruza frequência abaixo de LDB com status de matrícula — o coordenador vê quais alunos estão pagando mas não aparecendo.

---

### PG 27 — Sala de Situação
**Nota para reunião: 5/5** — MELHOR PÁGINA EXECUTIVA

**Status atual:** `calcular_saude_unidade()` calcula conformidade, profs_registrando, profs_esperados, profs_sem_registro na semana atual. `calcular_metricas_gerais()` calcula delta de conformidade vs semana anterior (correto!), aulas hoje, pct_conteudo, alunos_risco. `gerar_alertas_criticos()` gera máximo 10 alertas priorizados por tipo (professor silencioso → turma crítica → frequência em risco). `render_barra_progresso()` com cores semáforo.

**O que falta:**
- `gerar_alertas_criticos()` limita a 10 alertas mas não há indicação de quantos foram omitidos — o coordenador pode pensar que são apenas 10 problemas quando há 50.
- A "context bar" do topo (CSS `.context-bar`) usa HTML puro que pode não renderizar em alguns navegadores móveis.
- Não há botão "Iniciar Reunião" que bloqueia o foco na tela atual (modo apresentação).
- Os alertas de frequência são "por unidade" (não por aluno) — perder especificidade.
- A função `_hoje()` em utils.py retorna `datetime(2026, 2, 5)` se o ano < 2026. Mas em 21/02/2026 ela retorna `datetime.now()` corretamente. OK.

**Proposta de melhoria:**
Adicionar contador "X alertas adicionais não exibidos" quando houver mais de 10. Criar "Modo Reunião" que expande os alertas em tela cheia, esconde sidebar e navbar, e adiciona botões de ação inline. Pg 27 é a que mais se aproxima do ideal — merece virar o ponto de entrada padrão para reuniões.

---

## PARTE 2: TOP 10 MELHORIAS PRIORITÁRIAS

### Ranking por Impacto × Facilidade de Implementação

---

### MELHORIA #1 — Histórico de Conformidade Semanal (Tendência)
**Prioridade: CRÍTICA | Esforço: P (Pequeno)**

**Problema que resolve:**
Atualmente, o sistema só mostra snapshots do momento atual. O coordenador na reunião não sabe se a situação melhorou ou piorou em relação à semana passada. A única exceção é `calcular_metricas_gerais()` em pg 27 que já calcula delta de conformidade — mas está limitada a essa página.

**Páginas afetadas:** 01, 09, 13, 15, 27

**O que mudar:**
Em `utils.py`, criar função `calcular_historico_semanal(df_aulas, df_horario, n_semanas=4)`:
```python
def calcular_historico_semanal(df_aulas, df_horario, n_semanas=4):
    semana_atual = calcular_semana_letiva()
    resultado = []
    for s in range(max(1, semana_atual - n_semanas + 1), semana_atual + 1):
        df_s = df_aulas[df_aulas['semana_letiva'] <= s] if 'semana_letiva' in df_aulas.columns else df_aulas
        esperado = len(df_horario) * s
        conf = (len(df_s) / esperado * 100) if esperado > 0 else 0
        resultado.append({'semana': s, 'conformidade': round(conf, 1)})
    return pd.DataFrame(resultado)
```
Usar em pg 01, 15 e 27 com `plotly.express.line` mostrando últimas 4 semanas. Adicionar seta de tendência em pg 13 (semáforo) na coluna do professor.

**Mockup ASCII:**
```
Conformidade das Últimas 4 Semanas (Rede)
  100% |
   80% |      .....*
   60% |  *...*
   40% |
        Sem1  Sem2  Sem3  Sem4(atual)

  Tendência: +8.3% vs semana anterior  [seta para cima verde]
```

---

### MELHORIA #2 — Modo Reunião (Fullscreen com Navegação Guiada)
**Prioridade: CRÍTICA | Esforço: M (Médio)**

**Problema que resolve:**
Em uma reunião de 30 minutos com o coordenador compartilhando tela, navegar por 27 páginas desperdiça tempo. O coordenador precisa de uma visão que mostre tudo que importa sem sair da tela.

**Páginas afetadas:** Nova página (Página 28) ou reformulação de pg 27

**O que mudar:**
Criar pg 28 com URL `28_🎯_Modo_Reuniao.py`. A página detecta o tipo de reunião via selectbox no topo (Unidade/Rede) e monta automaticamente o briefing. Detalhado na Parte 3 deste documento.

---

### MELHORIA #3 — Exportação PDF para Reunião
**Prioridade: ALTA | Esforço: M (Médio)**

**Problema que resolve:**
O coordenador precisa de um documento para levar impresso para a reunião (ou compartilhar no grupo do WhatsApp antes). Pg 15 gera texto mas não PDF.

**Páginas afetadas:** 15, 27

**O que mudar:**
Em pg 15, adicionar botão "Gerar PDF da Reunião" usando `fpdf2` (biblioteca Python):
```python
from fpdf import FPDF

def gerar_pdf_reuniao(semana, cap_esperado, trimestre, df_metricas, alertas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"REUNIÃO PEEX — Semana {semana}", ln=True, align="C")
    pdf.set_font("Helvetica", size=10)
    # Tabela de métricas por unidade
    for _, row in df_metricas.iterrows():
        pdf.cell(0, 8, f"{row['nome']}: {row['conformidade']:.0f}%", ln=True)
    # Alertas críticos
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "ALERTAS CRÍTICOS:", ln=True)
    for a in alertas:
        pdf.cell(0, 8, f"[{a['nivel']}] {a['titulo']}: {a['problema']}", ln=True)
    return bytes(pdf.output())
```
Exibir com `st.download_button("Baixar PDF da Reunião", gerar_pdf_reuniao(...), "reuniao_semana_X.pdf", "application/pdf")`.

---

### MELHORIA #4 — Agrupamento de Alertas por Professor (Deduplicação)
**Prioridade: ALTA | Esforço: P (Pequeno)**

**Problema que resolve:**
Um professor que leciona para 7 turmas sem registrar gera 7+ alertas separados em pg 08 e pg 14. O coordenador se perde em uma lista de 30 alertas que são na verdade 5 professores.

**Páginas afetadas:** 08, 14, 27

**O que mudar:**
Em `detectar_alertas()` de pg 14, após criar o DataFrame de alertas, agrupar por professor:
```python
# Agrupa alertas do mesmo professor
if not df_alertas.empty and 'professor' in df_alertas.columns:
    df_alertas_grouped = df_alertas.groupby(['professor', 'unidade']).agg(
        tipos=('tipo', lambda x: ', '.join(sorted(set(x)))),
        n_turmas=('disciplinas', 'count'),
        pior_tipo=('tipo', lambda x: x.mode()[0]),
        detalhes=('detalhe', lambda x: ' | '.join(x.tolist()[:3]))
    ).reset_index()
```
Exibir na pg 08 como "Prof. X (BV): 3 turmas sem registro, 2 turmas com currículo atrasado" em uma linha única com badge de contagem.

---

### MELHORIA #5 — Ação Direta nos Alertas (Loop de Fechamento)
**Prioridade: ALTA | Esforço: M (Médio)**

**Problema que resolve:**
O coordenador vê o alerta, mas não tem como registrar o que fez sobre ele sem sair da página. Isso faz com que as ações fiquem apenas na memória ou em anotações físicas — e se perdem.

**Páginas afetadas:** 14, 27, 08

**O que mudar:**
Adicionar em cada alerta uma linha de ação inline:
```python
with st.expander(f"[{alerta['nivel']}] {alerta['titulo']}", expanded=False):
    st.write(alerta['problema'])
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        acao_texto = st.text_input("Providência tomada:", key=f"acao_{i}")
    with col2:
        responsavel = st.selectbox("Responsável:", ["Bruna Vitória", "Gilberto", ...], key=f"resp_{i}")
    with col3:
        if st.button("Salvar", key=f"save_{i}"):
            salvar_acao(alerta, acao_texto, responsavel)  # persiste em acoes_{unidade}.json
            st.success("Registrado!")
```
Usar `acoes_coordenacao.json` de pg 17 como backend de persistência.

---

### MELHORIA #6 — Dashboard de "Quem Não Recebeu Feedback"
**Prioridade: ALTA | Esforço: P (Pequeno)**

**Problema que resolve:**
Apenas 1/107 professores recebeu feedback em 2026. Não há visibilidade sobre quem está pendente. O coordenador não sabe por onde começar.

**Páginas afetadas:** 12, 25

**O que mudar:**
Em pg 12 (Agenda), adicionar seção "Pendências de Feedback":
```python
devolutivas = carregar_devolutivas()  # importar função de pg 25
profs_com_feedback = set(d['professor'] for d in devolutivas if d.get('unidade') == filtro_un)
profs_todos = set(df_aulas[df_aulas['unidade'] == filtro_un]['professor'].unique())
profs_sem_feedback = profs_todos - profs_com_feedback

st.metric("Professores sem feedback este trimestre", len(profs_sem_feedback))
# Lista ordenada por prioridade (vermelho primeiro)
df_pendentes = df_semaforo[df_semaforo['Professor_Raw'].isin(profs_sem_feedback)]
df_pendentes = df_pendentes.sort_values('_ordem')
st.dataframe(df_pendentes[['Professor', 'Cor', 'Taxa Registro', 'Dias Sem Registro']])
```

---

### MELHORIA #7 — Faltas Restantes Antes de Reprovar (Frequência)
**Prioridade: ALTA | Esforço: P (Pequeno)**

**Problema que resolve:**
A pg 20 mostra percentual de frequência mas não traduz isso em linguagem acionável. O coordenador precisa saber "quantas faltas esse aluno ainda pode ter antes de reprovar?" para decidir se liga para a família hoje ou pode esperar.

**Páginas afetadas:** 20, 23

**O que mudar:**
Em pg 20, adicionar coluna calculada:
```python
# Total de aulas previstas no ano por disciplina (usa dim_Horario_Esperado)
# Para calcular, precisamos saber: aulas_semana_disciplina * 47 semanas = total_previsto
SEMANAS_TOTAL = 47  # semanas letivas no ano
aulas_previstas = df_horario.groupby(['unidade', 'serie', 'disciplina']).size() * SEMANAS_TOTAL
# Faltas atuais
# Limite de faltas = total_previsto * 0.25 (LDB 75%)
# Faltas restantes = (total_previsto * 0.25) - faltas_atuais
df['faltas_restantes'] = ((df['total_aulas'] / (df['total_aulas'] / df['pct_frequencia'] * 100) * SEMANAS_TOTAL / semana_atual) * 0.25 - (df['total_aulas'] - df['presencas'])).round(0)
df['faltas_restantes'] = df['faltas_restantes'].clip(lower=0).astype(int)
```
Exibir com cor: verde (>20 faltas restantes), amarelo (5-20), vermelho (<5).

---

### MELHORIA #8 — Comparativo Semana vs Semana por Unidade
**Prioridade: MÉDIA | Esforço: P (Pequeno)**

**Problema que resolve:**
Na reunião de rede, a pergunta mais frequente é "cada unidade melhorou em relação à última semana?" Hoje não há essa visão em nenhuma página de forma direta.

**Páginas afetadas:** 09, 15

**O que mudar:**
Em pg 09, tab "Entre Unidades", adicionar coluna "Delta vs Semana Anterior":
```python
for un in ['BV', 'CD', 'JG', 'CDR']:
    df_un = df_aulas[df_aulas['unidade'] == un]
    aulas_sem_atual = len(df_un[df_un['semana_letiva'] == semana]) if 'semana_letiva' in df_un.columns else 0
    aulas_sem_ant = len(df_un[df_un['semana_letiva'] == semana - 1]) if 'semana_letiva' in df_un.columns else 0
    delta = aulas_sem_atual - aulas_sem_ant
    delta_pct = (delta / aulas_sem_ant * 100) if aulas_sem_ant > 0 else 0
    comparativo.append({..., 'Delta Semana': f"{delta:+d} ({delta_pct:+.0f}%)"})
```
Colorir verde se delta positivo, vermelho se negativo.

---

### MELHORIA #9 — Busca por Nome de Aluno no Registro de Ocorrência
**Prioridade: MÉDIA | Esforço: P (Pequeno)**

**Problema que resolve:**
O formulário de nova ocorrência em pg 22 requer `aluno_id` numérico do SIGA. O coordenador não sabe o ID de cabeça — precisa ir à pg 19, buscar o aluno, anotar o ID e voltar. Isso aumenta a fricção do registro e explica por que as ocorrências são sub-registradas.

**Páginas afetadas:** 22

**O que mudar:**
Substituir campo de ID por busca textual:
```python
# Em _tab_novo_registro()
if tem_alunos:
    busca_aluno = st.text_input("Buscar aluno por nome:", key="busca_nome_aluno")
    if busca_aluno:
        df_match = df_alunos[df_alunos['aluno_nome'].str.contains(busca_aluno, case=False, na=False)]
        if not df_match.empty:
            opcoes = [f"{row['aluno_nome']} ({row['serie']}, {row['turma']}, {row['unidade']})"
                      for _, row in df_match.head(10).iterrows()]
            sel = st.selectbox("Selecionar aluno:", opcoes, key="sel_aluno_ocorr")
            # Extrai aluno_id do aluno selecionado
```

---

### MELHORIA #10 — Notificação WhatsApp com Resumo Semanal
**Prioridade: MÉDIA | Esforço: G (Grande)**

**Problema que resolve:**
O resumo semanal existe (pg 15) mas precisa ser acessado manualmente. Se o coordenador não abrir o sistema na manhã da reunião, não vê o resumo. Uma mensagem automática toda segunda-feira antes da reunião garantiria que todos chegam informados.

**Páginas afetadas:** 15, scheduler.py

**O que mudar:**
O arquivo `scheduler.py` já existe em `/Users/brunaviegas/siga_extrator/`. Adicionar task semanal:
```python
# Em scheduler.py
import requests

def enviar_resumo_whatsapp(semana, texto_resumo):
    """Envia resumo via API WhatsApp Business ou Evolution API."""
    # Configurar em st.secrets['whatsapp']['api_url'] e ['token']
    grupos_peex = st.secrets.get('whatsapp', {}).get('grupos_peex', [])
    for grupo_id in grupos_peex:
        requests.post(
            f"{api_url}/sendText",
            json={"chatId": grupo_id, "text": texto_resumo},
            headers={"Authorization": f"Bearer {token}"}
        )
```
Triggerar via `schedule.every().monday.at("07:30").do(enviar_resumo_whatsapp)`.

---

## PARTE 3: PÁGINA "MODO REUNIÃO"

### Proposta Completa: Página 28 — Modo Reunião PEEX

**Arquivo:** `pages/28_🎯_Modo_Reunião.py`

**Conceito:** Uma única página que condensa tudo que o coordenador precisa nos primeiros 5 minutos de qualquer reunião PEEX. Sem rolagem desnecessária. Sem navegação entre páginas. Com botões de ação diretos.

---

### Layout Detalhado (Mockup ASCII)

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║  🎯 MODO REUNIÃO PEEX | Semana 4 · Cap. 1/12 · 1º Trimestre · 21/02/2026      ║
║  Tipo: [Unidade v] | Unidade: [BV - Boa Viagem v] | Coordenador: Bruna Vitória ║
╚══════════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────────┐
│ SAÚDE DA UNIDADE                                                                 │
│  Conformidade   Profs OK  Profs Atenção  Profs Crítico  Alunos Risco   Trend    │
│  ████ 43.7%      12 🟢      18 🟡          8 🔴          47 ⚠️       ↑ +3%    │
└──────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐ ┌────────────────────────────────────────────┐
│ ALERTAS CRÍTICOS (3)            │ │ PROFESSORES EM VERMELHO (8)                │
│                                 │ │                                            │
│ 🔴 Prof. João Silva             │ │ 🔴 João Silva - Matemática 6ºAno - 7d     │
│    Matemática | 7 dias sem reg  │ │    [Chamar] [Devolutiva] [WhatsApp]        │
│    [Registrar Providência]      │ │                                            │
│                                 │ │ 🔴 Maria Santos - Port. 7ºAno - 12d      │
│ 🔴 Arte - 8ºAno                 │ │    [Chamar] [Devolutiva] [WhatsApp]        │
│    0 registros no ano           │ │                                            │
│    [Verificar Professor]        │ │ 🟡 Carlos Lima - Inglês 9ºAno - 4d        │
│                                 │ │    [Chamar] [Devolutiva] [WhatsApp]        │
│ ⚠️ 6ºAno: conformidade 38%     │ │                                            │
│    [Ver Turma]                  │ │                    [Ver todos os 8...]     │
└─────────────────────────────────┘ └────────────────────────────────────────────┘

┌─────────────────────────────────┐ ┌────────────────────────────────────────────┐
│ ALUNOS EM RISCO ABC (Tier 2+)  │ │ AGENDA DE COMBINADOS DA ÚLTIMA REUNIÃO    │
│                                 │ │                                            │
│ Tier 3 (Crítico): 4 alunos     │ │ ✅ Ligar para família do João F. - FEITO  │
│ Tier 2 (Atenção): 18 alunos    │ │ ⏳ Observar aula de Port. 6ºAno - PEND.  │
│                                 │ │ ❌ Devolutiva Prof. Maria S. - ATRASADO  │
│ [Ver lista completa]            │ │                                            │
│                                 │ │ [Marcar como feito] [Adicionar novo]       │
└─────────────────────────────────┘ └────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│ PAUTA AUTOMÁTICA DA REUNIÃO                                                      │
│                                                                                  │
│ 1. Conformidade: 43.7% (↑3% vs sem. anterior)                                  │
│    → Foco: Prof. João Silva (7d) e Maria Santos (12d)                           │
│                                                                                  │
│ 2. Frequência: 82.3% na BV | JG em 79.6% (abaixo da meta 85%)                 │
│    → 4 alunos com menos de 5 faltas antes de reprovar                          │
│                                                                                  │
│ 3. Ocorrências: 18 esta semana | 3 graves (ver CDR)                            │
│    → 2 alunos com score ABC Tier 3                                              │
│                                                                                  │
│ 4. Progressão SAE: Cap 1 esperado | 67% das turmas no ritmo                   │
│    → 3 turmas com >1 capítulo de atraso                                        │
│                                                                                  │
│ [Exportar Pauta PDF] [Copiar para WhatsApp] [Imprimir]                          │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

### Dados a Puxar

```python
# Carregar em paralelo com st.cache_data
df_aulas = carregar_fato_aulas()          # conformidade, professores
df_horario = carregar_horario_esperado()  # grade esperada
df_freq = carregar_frequencia_alunos()    # frequência alunos
df_ocorr = carregar_ocorrencias()         # ocorrências
df_alunos = carregar_alunos()             # dados alunos
df_prog = carregar_progressao_sae()       # progressão SAE
score_abc = pd.read_csv(DATA_DIR / "score_Aluno_ABC.csv")  # já existe

# De pg 25 (Devolutivas):
devolutivas = carregar_devolutivas()
# De pg 17 (Painel de Ações):
acoes_pendentes = carregar_acoes()
# De pg 13 (Semáforo):
df_semaforo = calcular_metricas_professor(df_aulas, df_horario, semana)
```

---

### Filtros Necessários

1. **Tipo de reunião:** Unidade / Rede
   - Se "Unidade": filtro de unidade (selectbox) + coordenador responsável auto-detectado via `get_user_unit()`
   - Se "Rede": mostra visão consolidada de todas as 4 unidades

2. **Semana de referência:** por padrão = semana atual via `calcular_semana_letiva()`. Permite selecionar semana passada para "pós-mortem".

3. **Segmento:** Anos Finais / EM / Ambos — filtra a visão de professores e alunos.

---

### Fluxo de Navegação

```
Coordenador abre pg 28
    │
    ├─ Seleciona Tipo: UNIDADE
    │       │
    │       ├─ Unidade auto-detectada (get_user_unit())
    │       ├─ Carrega métricas em <3 segundos
    │       └─ Exibe layout completo
    │
    ├─ Seleciona Tipo: REDE
    │       │
    │       ├─ Carrega métricas de BV + CD + JG + CDR
    │       └─ Exibe comparativo lado a lado
    │
    ├─ Clica "Chamar" em professor vermelho
    │       └─ Abre modal com dados do professor + botão "Registrar Providência"
    │
    ├─ Clica "Devolutiva"
    │       └─ Navega para pg 25 com professor pré-selecionado (via session_state)
    │
    ├─ Clica "Exportar Pauta PDF"
    │       └─ Gera PDF com fpdf2 e st.download_button
    │
    └─ Clica "Marcar como feito" em combinado
            └─ Atualiza acoes_coordenacao.json e re-renderiza
```

---

### Ações Diretas da Tela

| Ação | Destino | Dado gerado |
|------|---------|-------------|
| Registrar Providência | Modal inline | Salva em `acoes_{unidade}.json` |
| Iniciar Devolutiva | pg 25 com professor pré-carregado | `st.session_state['prof_selecionado']` |
| Ver Lista de Alunos ABC | pg 23 com filtro de tier | `st.session_state['tier_filtro']` |
| Exportar Pauta PDF | Download | `.pdf` via fpdf2 |
| Copiar para WhatsApp | Clipboard | Texto formatado da pg 15 |
| Marcar combinado como feito | Inline | Atualiza `acoes_pendentes.json` |

---

## PARTE 4: FLUXOS DE DECISÃO NO DASHBOARD

### Fluxo 1 — Professor Não Registra

**Situação:** Na reunião semanal, coordenador quer saber quem não registrou esta semana.

```
INÍCIO: Abrir pg 27 (Sala de Situação) ou pg 28 (Modo Reunião)
    │
    ├─ Verificar: Seção "ALERTAS CRÍTICOS" → Tipo "Professor Silencioso"
    │
    ├─ Clicar no alerta para ver detalhes
    │       └─ Quantos dias sem registro?
    │           ├─ 1-3 dias → ATENÇÃO: monitorar (não agir ainda)
    │           ├─ 4-6 dias → URGENTE: contato por WhatsApp hoje
    │           └─ 7+ dias → CRÍTICO: ligar agora + registrar providência
    │
    ├─ Para investigar mais: ir para pg 13 (Semáforo do Professor)
    │       └─ Filtrar: "🔴 Crítico" → ver Taxa Registro + Dias Sem Registro
    │
    ├─ Para entender o histórico: ir para pg 10 (Detalhamento de Aulas)
    │       └─ Filtrar por professor → ver últimas aulas registradas
    │
    └─ AÇÃO: ir para pg 25 (Devolutivas) → selecionar professor → preencher SBI:
               Situação: "Semana X sem registro"
               Comportamento: "0 aulas lançadas de Y esperadas"
               Impacto: "Alunos sem conteúdo registrado, conformidade em Z%"

DECISÃO POSSÍVEL:
  → Professor com problema técnico → verificar acesso ao SIGA
  → Professor sobrecarregado → redistribuir turmas
  → Professor resistente → escalar para direção
  → Professor ausente (licença?) → verificar substituto
```

---

### Fluxo 2 — Aluno Faltando

**Situação:** Professora relatou que um aluno específico falta muito às suas aulas.

```
INÍCIO: Abrir pg 20 (Frequência Escolar)
    │
    ├─ Filtrar: Unidade → Série → Turma → Disciplina
    ├─ Ordenar por pct_frequencia (crescente)
    │       └─ Ver alunos abaixo de 75% (threshold LDB)
    │
    ├─ Clicar no aluno → ir para pg 19 (Painel do Aluno)
    │       ├─ Verificar: frequência em TODAS as disciplinas
    │       │   ├─ Falta só em 1 disciplina → pode ser conflito com professor
    │       │   └─ Falta em várias → padrão de absenteísmo
    │       ├─ Verificar: histórico de ocorrências (pg 22 integrada)
    │       └─ Verificar: score ABC (pg 23)
    │           ├─ Flag A isolada (só frequência) → problema logístico/familiar
    │           ├─ Flags A+B (frequência + comportamento) → problema socioemocional
    │           └─ Flags A+B+C (tudo) → TIER 3 → intervenção intensiva urgente
    │
    ├─ Calcular: quantas faltas restantes antes de reprovar?
    │       (usar fórmula de Melhoria #7)
    │
    └─ AÇÃO:
         < 5 faltas restantes → contato imediato com família
         5-10 faltas restantes → reunião com família esta semana
         > 10 faltas restantes → monitorar semanalmente

DOCUMENTAÇÃO: pg 22 → Novo Registro → Tipo: "Falta de Material" ou criar tipo "Absenteísmo"
```

---

### Fluxo 3 — Turma com Problema de Desempenho

**Situação:** Coordenadora percebe que uma turma está mal em várias disciplinas.

```
INÍCIO: Abrir pg 18 (Análise por Turma)
    │
    ├─ Selecionar: Unidade + Série
    ├─ Ver: Score de Saúde da Turma (0-100)
    │       └─ Quais disciplinas puxam o score para baixo?
    │           ├─ Disciplina com score < 50 → problema sério
    │           └─ Disciplina com conteúdo vazio > 40% → qualidade do registro ruim
    │
    ├─ Ir para pg 05 (Progressão SAE)
    │       └─ Filtrar pela mesma série
    │           └─ Qual capítulo estão ensinando vs qual deveriam estar?
    │               ├─ 0 capítulos de atraso → problema de qualidade, não de ritmo
    │               └─ 1+ capítulos de atraso → professor não avançou o currículo
    │
    ├─ Ir para pg 23 (ABC) → filtrar por série
    │       └─ Quantos alunos da turma estão em Tier 2+?
    │           └─ Se > 30% da turma em risco → problema sistêmico (não individual)
    │
    └─ AÇÃO:
         Score turma < 50% → reunião de área (todos os professores da turma)
         Score turma 50-70% → devolutiva individual para professor mais fraco
         Atraso curricular > 2 caps → plano de recuperação curricular com pg 06 (Visão Professor)

PERGUNTA CHAVE: o problema é do professor (1 disciplina ruim) ou da turma (todas as disciplinas)?
```

---

### Fluxo 4 — Conformidade de Unidade Baixa

**Situação:** Na reunião de rede, uma unidade está com conformidade muito abaixo das outras.

```
INÍCIO: Abrir pg 09 (Comparativos), Tab "Entre Unidades"
    │
    ├─ Identificar: qual unidade tem menor conformidade?
    │       └─ Ver delta vs semana anterior (com Melhoria #8 implementada)
    │           ├─ Queda = problema novo esta semana
    │           └─ Estável e baixo = problema crônico
    │
    ├─ Drill-down: ir para pg 13 (Semáforo) → filtrar pela unidade problemática
    │       └─ Quantos professores em vermelho?
    │           ├─ 1-2 professores → problema individual
    │           └─ 5+ professores → problema sistêmico da unidade
    │
    ├─ Contexto histórico: pg 09 Tab "Mesma Disciplina"
    │       └─ A Matemática da unidade X vs outras unidades
    │           └─ Se todas as disciplinas de X estão baixas → problema de cultura/gestão
    │
    └─ DECISÃO:
         Problema individual → devolutiva focada (pg 25)
         Problema sistêmico → reunião de unidade com coordenação + direção
         Problema de dados → verificar se extração do SIGA está funcionando para aquela unidade

NOTA: Períodos API por unidade são diferentes (BV=80, CD=78, JG=79, CDR=77).
Se uma unidade subitamente tem menos dados, verificar se o período correto está sendo usado na extração.
```

---

### Fluxo 5 — Professor com Conteúdo Vazio

**Situação:** Professor registra que "deu aula" mas o campo conteúdo está vazio ou com "." ou "conteúdo do livro".

```
INÍCIO: Abrir pg 16 (Inteligência de Conteúdo)
    │
    ├─ Ver: Taxa de registros vazios por professor
    │       └─ Filtrar: tipo de aula = "Vazio"
    │           └─ Quais professores têm > 30% de registros vazios?
    │               (threshold: CONTEUDO_VAZIO_ALERTA = 30% em utils.py)
    │
    ├─ Analisar: são registros realmente vazios ou são "."/","/"-"?
    │       └─ pg 10 (Detalhamento) → filtrar por professor → ver campo conteúdo
    │
    ├─ Verificar: professor avança na progressão SAE?
    │       └─ pg 05 → filtrar pelo professor
    │           ├─ Capítulo avança = professor está registrando algo (mesmo que vazio)
    │           └─ Capítulo não avança = professor não registra conteúdo real
    │
    └─ AÇÃO:
         Registros com "." → orientar sobre preenchimento (não é sabotagem, é preguiça)
         Registros vazios recorrentes → incluir na devolutiva: pg 25, seção "Cessar"
         > 50% vazios → CONTEUDO_VAZIO_CRITICO threshold → alerta automático pg 08

SCRIPT DE DEVOLUTIVA SUGERIDO:
  Situação: "Nas últimas 3 semanas, X de Y registros estão com campo conteúdo vazio"
  Comportamento: "O sistema mostra pontos, vírgulas ou campo em branco"
  Impacto: "Coordenação não consegue verificar progressão curricular; família não sabe o que foi ensinado"
  Feedforward: "Na próxima semana, registrar pelo menos: disciplina + capítulo + atividade principal"
```

---

### Fluxo 6 — Preparar Devolutiva de Professor

**Situação:** Coordenadora tem reunião com professor em 30 minutos e precisa se preparar com dados.

```
INÍCIO: Abrir pg 25 (Devolutivas) → sidebar: selecionar unidade + professor
    │
    ├─ Ver métricas automáticas carregadas por _calcular_metricas_professor():
    │   - aulas_registradas vs aulas_esperadas
    │   - taxa_registro, taxa_conteudo, taxa_tarefa
    │   - dias_sem_registro (último registro)
    │   - séries e disciplinas
    │
    ├─ COMPLEMENTAR com dados de outras páginas (abertura manual hoje):
    │   ├─ pg 13: semáforo do professor (verde/amarelo/vermelho + histórico)
    │   ├─ pg 14: alertas ativos (tipo + prioridade)
    │   ├─ pg 05: capítulo atual vs esperado nas disciplinas dele
    │   └─ pg 25: última devolutiva registrada (histórico)
    │
    ├─ Preencher estrutura SBI:
    │   - Situação: contexto concreto do dado
    │   - Comportamento: o que foi observado nos dados
    │   - Impacto: consequência para alunos/escola
    │
    ├─ Preencher 3C's:
    │   - Continuar: o que está bem (reconhecer explicitamente)
    │   - Começar: o que precisa implementar
    │   - Cessar: o que está gerando problema
    │
    └─ Registrar Combinados:
         - Meta mensurável (ex: "registrar conteúdo em 80% das aulas por 2 semanas")
         - Prazo específico (próxima reunião = data)
         - Responsável pelo acompanhamento

NOTA: Com Melhoria #6 implementada, pg 25 carregaria automaticamente o semáforo e os alertas do professor sem precisar navegar.
```

---

### Fluxo 7 — Análise de Progressão SAE na Reunião de Rede

**Situação:** Na reunião de rede, verificar se todas as unidades estão no mesmo capítulo.

```
INÍCIO: Abrir pg 05 (Progressão SAE)
    │
    ├─ Filtrar: "Ano Completo" + "Rede Toda" (sem filtro de unidade)
    ├─ Ver: Capítulo esperado = calcular_capitulo_esperado(semana_atual)
    │       Semana 4 → Capítulo esperado = 1
    │
    ├─ Comparar por unidade:
    │   └─ Qual unidade está mais avançada? Qual está mais atrasada?
    │       └─ Diferença > 1 capítulo entre unidades = problema de alinhamento
    │
    ├─ Comparar por disciplina:
    │   └─ Quais disciplinas estão mais atrasadas?
    │       └─ Disciplinas com atraso consistente em todas as unidades = problema de grade horária
    │
    ├─ Verificar série mais crítica:
    │   └─ Qual série tem mais capítulos de atraso?
    │       └─ 9º Ano → impacto no vestibular/SSA
    │
    └─ AÇÃO:
         Unidade adiantada = verificar se está pulando conteúdos (qualidade do ensino)
         Unidade atrasada = plano de recuperação curricular com datas específicas
         Disciplina atrasada em todas as unidades = reunião de área nacional SAE

PONTO DE ATENÇÃO: A função estimar_capitulo_real() em pg 05 usa regex que pode não capturar
todos os formatos de registro. Professores que escrevem "capítulo três" (por extenso) não são detectados.
```

---

### Fluxo 8 — Turma com Muitas Ocorrências

**Situação:** Coordenadora recebe relatos de que o clima de uma turma está deteriorado.

```
INÍCIO: Abrir pg 22 (Ocorrências) → Tab "Por Turma"
    │
    ├─ Filtrar: unidade + período (últimas 2 semanas)
    ├─ Ver: ranking de turmas por número de ocorrências
    │       └─ Qual turma tem mais ocorrências?
    │
    ├─ Analisar distribuição por tipo:
    │   ├─ Predominância de "Indisciplina" → problema de gestão de sala
    │   ├─ Predominância de "Bullying" → problema de convivência
    │   ├─ Predominância de "Uso de Celular" → problema de política escolar
    │   └─ Muitos "Registro Positivo" = turma saudável (bom sinal!)
    │
    ├─ Cruzar com Tab "Alunos em Risco":
    │   └─ Os mesmos alunos aparecem em múltiplas ocorrências?
    │       ├─ 1 aluno = 50% das ocorrências → problema individual
    │       └─ Ocorrências distribuídas = problema de clima de turma
    │
    ├─ Cruzar com pg 20 (Frequência):
    │   └─ Turma com muitas ocorrências tem frequência mais baixa?
    │       └─ Correlação positiva = alunos "difíceis" faltam mais → fuga da escola
    │
    └─ AÇÃO:
         1 aluno problemático → intervenção individual (pg 19 + pg 23 + família)
         Múltiplos alunos → intervenção de turma (assembleia, acordo de convivência)
         Professor específico com muitas ocorrências → observação de aula (pg 12 Agenda)
         CDR: 68% das ocorrências graves → reunião específica com coordenação CDR

GRAVIDADES em pg 22: ['Leve', 'Media', 'Grave'] — 'Media' SEM acento (padrão do CSV).
Não modificar para 'Média' pois quebrará filtros existentes.
```

---

## PARTE 5: O QUE FALTA NO SISTEMA

### Funcionalidades Não Existentes Que Fariam Diferença

---

### F1 — Comparação Temporal Semana vs Semana (CRÍTICO)

**Por que falta:**
O sistema captura snapshots mas não salva o estado de cada semana como série temporal. Quando a extração roda (`atualizar_siga.py`), sobrescreve `fato_Aulas.csv` sem preservar histórico semanal.

**O que faria diferença:**
Gráfico de linha mostrando conformidade das últimas 8 semanas por unidade. Permite ver tendências e responder "estamos melhorando?" na reunião em 10 segundos.

**Como implementar:**
1. Modificar `atualizar_siga.py` para salvar snapshot semanal: `fato_Aulas_sem_{semana}.csv` em `/power_bi/historico/`
2. Criar `carregar_historico_semanal()` em `utils.py` que lê todos os arquivos de histórico e concatena
3. Adicionar em pg 09 tab "Evolução Temporal" com `plotly.express.line`

**Esforço:** M | **Impacto:** CRÍTICO

---

### F2 — Exportação PDF Automatizada para Reunião (ALTO)

**Por que falta:**
Pg 15 gera texto para WhatsApp mas não PDF. Para reunião presencial, o coordenador precisa de documento impresso ou compartilhável por email/Teams.

**O que faria diferença:**
Botão "Gerar PDF desta Reunião" que produz um documento de 2 páginas com: cabeçalho ELO, semana/trimestre, tabela de métricas por unidade, lista de alertas críticos, lista de professores para contato, e espaço para anotações.

**Como implementar:**
Instalar `fpdf2` (`pip install fpdf2`). Criar `gerar_pdf_reuniao()` em pg 15 (detalhado em Melhoria #3). Adicionar logo do ELO em base64 no cabeçalho.

**Esforço:** M | **Impacto:** ALTO

---

### F3 — Notificações Push / WhatsApp Automático

**Por que falta:**
O `scheduler.py` existe e já roda extrações automáticas. Mas não envia notificações. O coordenador só vê os dados se abrir o sistema.

**O que faria diferença:**
- Toda segunda-feira 07:30: "Resumo da Semana X — [unidade] — conformidade Y%"
- Quando professor atinge 7 dias sem registro: alerta imediato no WhatsApp do coordenador responsável
- Quando aluno cruza threshold de frequência (<75%): notificação automática

**Como implementar:**
Integrar `scheduler.py` com Evolution API (self-hosted) ou WhatsApp Business API. Criar `config_whatsapp.json` com grupos por unidade/coordenador. Adicionar 3 tasks no scheduler: resumo semanal, alerta professor silencioso, alerta frequência.

**Esforço:** G | **Impacto:** ALTO

---

### F4 — Observação de Aula Estruturada (Protocolo Digital)

**Por que falta:**
Pg 12 (Agenda) agenda visitas de observação mas não tem formulário de observação. O coordenador vai à sala de aula com papel e caneta, e o registro fica desconectado do sistema.

**O que faria diferença:**
Formulário de observação de aula com: checklist de domínio pedagógico (gestão de sala, qualidade das perguntas, engajamento dos alunos, alinhamento curricular, uso do material SAE), campo de evidências textuais e pontuação automática. Os dados alimentam o contexto da devolutiva em pg 25.

**Como implementar:**
Criar pg 12b ou aba adicional em pg 12 com `st.form()`. Persistir em `observacoes_{unidade}.json`. Conectar com pg 25: ao abrir devolutiva de um professor, mostrar as observações de aula registradas.

**Esforço:** M | **Impacto:** ALTO

---

### F5 — Mapa de Calor de Risco (Heatmap Aluno × Disciplina)

**Por que falta:**
pg 23 (ABC) mostra lista de alunos em risco, mas não mostra padrões visuais: "qual disciplina tem mais alunos em risco? Em qual série isso se concentra?"

**O que faria diferença:**
Heatmap `plotly.graph_objects.Heatmap` com eixos aluno (linhas) × disciplina (colunas) e cor = score de risco (0-100). O coordenador vê em 5 segundos quais disciplinas/alunos formam um cluster de risco.

**Como implementar:**
Em pg 23, após calcular `calcular_score_abc()` para cada aluno, pivotar o DataFrame:
```python
pivot = df_risco.pivot_table(
    values='score', index='aluno_nome', columns='disciplina',
    aggfunc='first', fill_value=0
)
fig = go.Figure(go.Heatmap(
    z=pivot.values, x=pivot.columns, y=pivot.index,
    colorscale=[[0, 'green'], [0.5, 'yellow'], [1, 'red']]
))
```

**Esforço:** P | **Impacto:** ALTO

---

### F6 — Integração com Calendário de Reuniões (Google Calendar / Outlook)

**Por que falta:**
As 45 reuniões PEEX de 2026 estão documentadas em `PLANO_REUNIOES_PEDAGOGICAS_2026.md` mas não estão no sistema. O dashboard não sabe quando é a próxima reunião.

**O que faria diferença:**
O sistema calcula automaticamente "próxima reunião PEEX: em X dias" e pré-carrega os dados relevantes. Na véspera da reunião, envia resumo automático por WhatsApp.

**Como implementar:**
Criar `dim_Reunioes_PEEX.csv` com as 45 datas, tipo (Unidade/Rede), tema e coordenadores responsáveis. Em pg 01 e pg 28, calcular dias até próxima reunião. Integrar com notificação de pg 25 (F3).

**Esforço:** P | **Impacto:** MÉDIO

---

### F7 — Análise de Sentimento dos Conteúdos Registrados

**Por que falta:**
Pg 16 classifica tipo de aula mas não analisa se o conteúdo registrado é rico ou superficial. "Exercícios" pode ser um registro rico ("Resolução de problemas de equações de 2º grau Cap. 3 pg. 45-52") ou pobre ("exercícios do livro").

**O que faria diferença:**
Score de profundidade do registro: 0 = vazio, 1 = palavra única, 2 = tipo de atividade, 3 = capítulo mencionado, 4 = página ou atividade específica, 5 = objetivo de aprendizagem claro. Professores com score médio alto = exemplos de boa prática para compartilhar nas reuniões.

**Como implementar:**
Melhorar `calcular_score_qualidade()` em pg 16 com critérios explícitos:
```python
def calcular_score_qualidade(texto):
    if pd.isna(texto) or texto in ('.', '', ',', '-'):
        return 0
    texto = str(texto).strip()
    score = 1  # base: tem algo
    if len(texto) > 10: score += 1
    if extrair_capitulo(texto): score += 1  # mencionou capítulo
    if any(k in texto.lower() for k in ['pág', 'pg.', 'atividade', 'exercício']): score += 1
    if len(texto) > 50: score += 1  # descrição detalhada
    return min(score, 5)
```

**Esforço:** P | **Impacto:** MÉDIO

---

### F8 — Banco de Evidências de Boas Práticas

**Por que falta:**
Os conteúdos de maior qualidade (score 4-5 em pg 16) existem nos dados mas não são surfaced. Não há mecanismo para o coordenador marcar um registro como "exemplo positivo" para compartilhar na reunião.

**O que faria diferença:**
Galeria de "Melhores Registros da Semana" em pg 15 (Resumo Semanal): 5 exemplos de conteúdos bem registrados, com professor e disciplina — para reconhecimento público na reunião. Muda a dinâmica de "cobrar quem errou" para "celebrar quem acertou".

**Como implementar:**
Em pg 15, adicionar seção:
```python
# Top 5 conteúdos mais ricos da semana (score >= 4)
df_top = df_sem.copy()
df_top['score_qualidade'] = df_top['conteudo'].apply(calcular_score_qualidade)
df_top = df_top[df_top['score_qualidade'] >= 4].nlargest(5, 'score_qualidade')
if not df_top.empty:
    st.subheader("Destaques da Semana")
    for _, row in df_top.iterrows():
        st.markdown(f"**{row['professor']}** ({row['disciplina']}, {row['serie']}): {row['conteudo']}")
```

**Esforço:** P | **Impacto:** ALTO (mudança cultural)

---

### F9 — Correlação Frequência × Desempenho × Ocorrências

**Por que falta:**
Os três datasets existem (`fato_Frequencia_Aluno.csv`, `fato_Notas_Historico.csv`, `fato_Ocorrencias.csv`) mas nenhuma página os cruza sistematicamente para responder: "alunos com baixa frequência tiram notas mais baixas? Alunos com ocorrências têm mais faltas?"

**O que faria diferença:**
Scatter plot interativo em pg 26 (Painel Unificado): eixo X = frequência média, eixo Y = média de notas, tamanho do ponto = número de ocorrências. Permite ao coordenador ver clusters: alunos com perfil (baixa freq + baixas notas + muitas ocorrências) = Tier 3 ABC confirmado por múltiplas fontes.

**Como implementar:**
Em pg 26 ou pg 23, cruzar os três DataFrames por `aluno_id`:
```python
df_abc = df_alunos[['aluno_id', 'aluno_nome', 'serie', 'unidade']].copy()
df_abc = df_abc.merge(
    df_freq.groupby('aluno_id')['pct_frequencia'].mean().reset_index(),
    on='aluno_id', how='left'
)
df_abc = df_abc.merge(
    df_notas.groupby('aluno_id')['nota'].mean().reset_index().rename(columns={'nota': 'media_notas'}),
    on='aluno_id', how='left'
)
df_abc = df_abc.merge(
    df_ocorr.groupby('aluno_id').size().reset_index(name='n_ocorrencias'),
    on='aluno_id', how='left'
)
```

**Esforço:** M | **Impacto:** ALTO

---

### F10 — Dashboard para Pais (Portal Simplificado)

**Por que falta:**
O sistema é voltado para coordenação e professores. Mas pais de alunos em risco ABC precisam ser acionados — e hoje isso é feito por telefone, sem evidências concretas para mostrar.

**O que faria diferença:**
Página simples com senha por aluno: frequência atual, notas (quando disponíveis), ocorrências recentes, e mensagem do coordenador. O coordenador envia o link com a senha para o responsável por WhatsApp antes da reunião de família — chegam informados.

**Como implementar:**
Criar `pages/29_👨‍👩‍👧_Portal_Familia.py` com autenticação separada via `aluno_id` como senha. Exibir apenas dados do aluno correspondente. Usar `status_frequencia()` e `calcular_score_abc()` para linguagem simplificada: "Situação: Atenção Necessária" em vez de "Tier 2".

**Esforço:** M | **Impacto:** ALTO (engajamento familiar)

---

### F11 — Módulo de Metas e Acompanhamento de OKRs

**Por que falta:**
Cada coordenador tem metas pedagógicas (conformidade 80%, feedback para todos os professores, etc.) mas o sistema não rastreia progresso em relação a essas metas. Pg 17 tem ações pontuais, mas não OKRs trimestrais.

**O que faria diferença:**
Na reunião de abertura do trimestre, coordenador define 3 OKRs com metas numéricas. O sistema mostra progress bar de cada OKR na pg 28 (Modo Reunião): "Meta: 80% conformidade | Atual: 43.7% | Progresso: 54% da meta". Isso transforma o dashboard de ferramenta de monitoramento em ferramenta de gestão por resultados.

**Como implementar:**
Criar `okrs_{unidade}_{trimestre}.json` com estrutura:
```json
[
  {"objetivo": "Conformidade de registro", "meta": 80, "metrica": "conformidade_pct", "prazo": "2026-05-10"},
  {"objetivo": "Professores com feedback", "meta": 80, "metrica": "pct_profs_com_feedback", "prazo": "2026-05-10"}
]
```
Calcular valor atual de cada métrica no momento em que a página carrega.

**Esforço:** M | **Impacto:** ALTO

---

### F12 — Reconhecimento e Gamificação para Professores

**Por que falta:**
O sistema é exclusivamente voltado a identificar problemas. Não há nenhum mecanismo de reconhecimento para professores que estão indo bem. Isso cria uma percepção negativa: "o dashboard só serve para me cobrar".

**O que faria diferença:**
Badge semanal automático: "Professor Exemplar da Semana" — professor com maior taxa de conformidade + maior qualidade de conteúdo + sem alertas. Exibir no início da reunião. Enviar mensagem de parabéns por WhatsApp automaticamente.

**Como implementar:**
Em pg 15, após calcular métricas dos professores, identificar:
```python
df_destaque = df_semaforo[df_semaforo['Cor'] == 'verde'].copy()
df_destaque['score_total'] = df_destaque['Taxa Registro'] * 0.6 + df_destaque['Taxa Conteudo'] * 0.4
prof_exemplar = df_destaque.nlargest(1, 'score_total').iloc[0]
st.success(f"Professor(a) da Semana: {prof_exemplar['Professor']} — {prof_exemplar['Taxa Registro']:.0f}% de conformidade!")
```
Enviar via `scheduler.py` para grupo WhatsApp da unidade.

**Esforço:** P | **Impacto:** MÉDIO (mas alto para cultura)

---

## APÊNDICE: PROBLEMAS TÉCNICOS ENCONTRADOS NO CÓDIGO

### Bug #1 — Função extrair_capitulo() Duplicada
**Onde:** `pages/16_🔬_Inteligência_Conteúdo.py` (linha 48) e `pages/18_🏫_Análise_Turma.py` (linha 40)
**Problema:** Duas implementações independentes com lógicas ligeiramente diferentes. pg 18 não checa `texto in ('.', '', ',')`.
**Correção:** Mover para `utils.py` como função canônica e importar nas duas páginas.

### Bug #2 — FERIADOS_2026 Hardcoded Fora do utils.py
**Onde:** `pages/06_👨‍🏫_Visão_Professor.py` (linha 54)
**Problema:** Viola o princípio de fonte única de verdade. Se um feriado mudar, precisa ser atualizado em dois lugares.
**Correção:** Mover `FERIADOS_2026` para `utils.py` ou derivar de `dim_Calendario.csv` (que já tem coluna `letivo`).

### Bug #3 — Caminho Hardcoded do vagas.db
**Onde:** `pages/26_📊_Painel_Unificado.py` (linha 79)
**Código:** `VAGAS_DB_PATH = Path("/Users/brunaviegas/Downloads/Cópia BI/output/vagas.db")`
**Problema:** Quebra no deploy no Render e em qualquer outra máquina.
**Correção:** `VAGAS_DB_PATH = Path(os.environ.get('VAGAS_DB_PATH', '/Users/brunaviegas/Downloads/Cópia BI/output/vagas.db'))`

### Bug #4 — st.cache_data com DataFrames Mutáveis
**Onde:** `pages/14_🧠_Alertas_Inteligentes.py` (linha 105) e `pages/18_🏫_Análise_Turma.py` (linha 52)
**Problema:** `@st.cache_data(ttl=300)` com DataFrames como parâmetros pode ter comportamento imprevisível se o DataFrame for modificado in-place antes de ser passado.
**Correção:** Passar apenas parâmetros primitivos (semana, unidade como strings) ou usar `@st.cache_data(hash_funcs={pd.DataFrame: lambda df: df.shape})`.

### Bug #5 — DIA_REUNIAO_SEMANAL Hardcoded
**Onde:** `pages/17_🎯_Painel_Ações.py` (linha 41)
**Código:** `DIA_REUNIAO_SEMANAL = 3  # Quinta-feira`
**Problema:** Diferentes unidades podem ter reunião em dias diferentes.
**Correção:** Mover para `config_coordenadores.json` com estrutura por unidade: `{"BV": {"dia_reuniao": 3}, "CD": {"dia_reuniao": 1}}`.

### Bug #6 — Loop Python para Calcular Conformidade por Professor
**Onde:** `pages/08_⚠️_Alertas_Conformidade.py` (linhas 258-281) e `pages/13_🚦_Semáforo_Professor.py` (linhas 75-138)
**Problema:** Loop `for prof in df_aulas_filt['professor'].unique()` com sub-consultas ao DataFrame por professor — O(n×m) em vez de O(n log n) com groupby. Em 107 professores × 1.901 aulas pode ser lento.
**Correção:** Usar `df_aulas.groupby(['professor', 'unidade', 'serie', 'disciplina']).size()` para calcular todos os professores de uma vez com merge no df_horario.

### Bug #7 — _hoje() Retorna Data Fixa Desnecessariamente
**Onde:** `utils.py` (linha 614)
**Código:** `if hoje.year < 2026: return datetime(2026, 2, 5)`
**Problema:** Comportamento de simulação que não se aplica mais em 2026. Pode confundir debugging.
**Correção:** Remover o fallback ou mudar para `datetime(2026, 1, 26)` (início do ano letivo) como fallback mais seguro.

---

## SUMÁRIO EXECUTIVO PARA A EQUIPE

### O Que o Sistema Faz Bem
1. **pg 13 (Semáforo)** e **pg 27 (Sala de Situação)** são ferramentas genuinamente úteis para reunião — usá-las como ponto de entrada padrão.
2. **pg 15 (Resumo Semanal)** gera um relatório completo que pode abrir qualquer reunião em 5 minutos.
3. **pg 23 (ABC)** tem o framework de alerta precoce mais sofisticado do sistema — mas está sendo sub-utilizado porque não conecta com ação direta.
4. **utils.py** é bem organizado: todas as constantes de threshold (`CONFORMIDADE_*`, `THRESHOLD_FREQUENCIA_LDB`) estão centralizadas e documentadas.
5. O sistema de `status_conformidade()` e `status_frequencia()` produz labels consistentes em todo o sistema.

### O Que Mais Impede o Uso em Reunião
1. **Sem histórico temporal** — não é possível ver se a situação está melhorando.
2. **Alertas não agrupados** — 1 professor problemático gera 7+ alertas separados.
3. **Sem loop de fechamento** — nenhuma página fecha o ciclo "detectar → agir → monitorar".
4. **Sem PDF** — coordenador não tem documento para levar para reunião presencial.
5. **27 páginas** sem um ponto de entrada claro — o coordenador novo não sabe por onde começar.

### Prioridade de Implementação

| Sprint | Melhorias | Esforço Total | Impacto |
|--------|-----------|---------------|---------|
| Sprint 1 (1 semana) | #1 Histórico semanal + #4 Agrupamento alertas + #6 Dashboard feedback | P+P+P | CRÍTICO |
| Sprint 2 (1 semana) | #7 Faltas restantes + #8 Comparativo semana + #9 Busca aluno | P+P+P | ALTO |
| Sprint 3 (2 semanas) | #2 Modo Reunião (pg 28) + #3 PDF | M+M | CRÍTICO |
| Sprint 4 (2 semanas) | #5 Ações inline + F1 Heatmap risco + F8 Boas práticas | M+P+P | ALTO |
| Sprint 5 (3 semanas) | #10 WhatsApp + F4 Observação de aula + F11 OKRs | G+M+M | ALTO |

---

*Documento gerado pela Equipe A — Análise baseada no código-fonte real de 27 páginas + utils.py (668 linhas) + dados de produção do Colégio ELO (fevereiro 2026).*

*Versão: 1.0 | Data: 21/02/2026*
