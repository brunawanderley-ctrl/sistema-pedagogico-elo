# PEEX Command Center — Guia Completo de Uso

**Colegio ELO 2026 | Programa ELO de Excelencia**

---

## O que e o PEEX?

PEEX = **Programa ELO de Excelencia**. E um sistema de gestao pedagogica inteligente que transforma dados brutos do SIGA (sistema academico) em **decisoes concretas** para cada nivel da escola.

O PEEX Command Center e a ferramenta onde tudo acontece: uma aplicacao web que cada pessoa da equipe acessa com seu login, vendo exatamente o que precisa para sua funcao.

**Analogia**: Pense no PEEX como o "painel de controle" de um aviao. O piloto (CEO) ve todos os instrumentos. O copiloto (Diretor) ve os essenciais. O engenheiro de voo (Coordenador) monitora os sistemas. E cada passageiro (Professor) acompanha seu proprio voo.

---

## Como acessar

1. Abra o navegador e acesse o endereco do sistema (ex: `http://localhost:8515`)
2. Digite seu **usuario** e **senha**
3. O sistema reconhece seu perfil e mostra apenas as paginas relevantes

### Contas de acesso

| Login | Perfil | Unidade | Senha |
|-------|--------|---------|-------|
| `bruna` | CEO | Rede | `EloAdmin2026!` |
| `bv` | Coordenador | Boa Viagem | `EloBV2026` |
| `candeias` | Coordenador | Candeias | `EloCD2026` |
| `janga` | Coordenador | Janga | `EloJG2026` |
| `cordeiro` | Coordenador | Cordeiro | `EloCDR2026` |
| `dir_bv` | Diretor | Boa Viagem | `EloDirBV2026` |
| `dir_cd` | Diretor | Candeias | `EloDirCD2026` |
| `dir_jg` | Diretor | Janga | `EloDirJG2026` |
| `dir_cdr` | Diretor | Cordeiro | `EloDirCDR2026` |
| `prof_demo` | Professor | Boa Viagem | `EloProf2026` |

---

## Os 4 Perfis

### CEO (Bruna)
Ve **toda a rede** — 4 unidades, todos os indicadores, rankings, simulacoes. Tem 15 paginas disponiveis. E quem toma decisoes estrategicas e acompanha a saude geral da rede.

### Diretor
Ve a **estrategia da sua unidade** + visao parcial da rede. Tem 9 paginas. Recebe escalacoes dos coordenadores e define compromissos.

### Coordenador
Ve a **operacao diaria** — seus professores, seus alunos, ritmo semanal, plano de acao. Tem 11 paginas. E o "guardiao PEEX" que age diretamente.

### Professor
Ve **apenas seus proprios dados** — score, turmas, progresso. Tem 3 paginas. Nunca ve dados de colegas. Transparencia sem exposicao.

---

## Conceitos-chave

### Indice ELO (IE)

O IE e a "nota de saude" de cada unidade, de 0 a 100. Combina 6 indicadores com pesos diferentes:

| Indicador | Peso | O que mede |
|-----------|------|------------|
| Conformidade media | 25% | % de aulas registradas no SIGA |
| Frequencia media | 20% | % de presenca dos alunos |
| Profs no ritmo SAE | 20% | % de professores alinhados ao curriculo |
| Alunos com freq >90% | 15% | % de alunos com presenca excelente |
| Alunos em risco | 10% | % de alunos em situacao critica (quanto menor, melhor) |
| Ocorrencias graves | 10% | Total de ocorrencias graves (quanto menor, melhor) |

**Exemplo**: Uma unidade com 75% de conformidade, 88% de frequencia, 40% no ritmo SAE, 60% com freq>90%, 15% de alunos risco e 20 ocorrencias graves teria um IE de aproximadamente 67/100.

---

### Batalhas

"Batalha" e o nome que damos a cada **problema detectado automaticamente** pelo sistema. O PEEX analisa os dados toda madrugada e identifica 9 tipos de batalha:

| Tipo | O que detecta | Exemplo |
|------|---------------|---------|
| PROF_SILENCIOSO | Professor que parou de registrar aulas | "Prof. Silva nao registra ha 12 dias" |
| DISCIPLINA_ORFA | Disciplina sem nenhum registro no ano | "Filosofia 7A: zero aulas registradas" |
| TURMA_CRITICA | Turma abaixo da meta de conformidade | "8B esta com 35% de conformidade" |
| ALUNO_FREQUENCIA | Aluno com frequencia abaixo de 75% | "15 alunos abaixo do limiar LDB" |
| ALUNO_OCORRENCIA | Aluno com ocorrencias graves recorrentes | "3 ocorrencias graves em 2 semanas" |
| PROF_QUEDA | Professor que caiu mais de 30% de uma semana para outra | "Prof. Santos caiu de 80% para 45%" |
| CURRICULO_ATRASADO | Professor mais de 1 capitulo atras do SAE | "Prof. Lima esta no Cap 3, deveria estar no Cap 5" |
| PROF_SEM_CONTEUDO | Aulas registradas sem descricao de conteudo | "60% das aulas sem campo conteudo" |
| PROCESSO_DEADLINE | Prazo de feedback se aproximando | "Faltam 5 dias para o prazo de observacao" |

Cada batalha tem um **nivel de urgencia**:
- **URGENTE** — Agir hoje
- **IMPORTANTE** — Agir esta semana
- **MONITORAR** — Acompanhar, sem acao imediata

---

### Estrelas de Evolucao

Cada unidade ganha de 0 a 3 estrelas por indicador, por semana:

| Estrelas | Criterio |
|----------|----------|
| 0 | Piorou ou estagnou por 2+ semanas |
| 1 | Estavel (variacao menor que 1 ponto percentual) |
| 2 | Melhorou de 1 a 3 pontos percentuais |
| 3 | Melhorou mais de 3pp OU atingiu a meta |

Sao 5 indicadores, entao o maximo por semana e **15 estrelas**. As estrelas **acumulam** durante o trimestre (nunca se perde estrelas ja conquistadas). Isso gera o **Ranking de Evolucao**.

---

### Escalacao

Quando um problema persiste, ele "escala" para niveis superiores. E um protocolo automatico:

| Nivel | Nome | Quando acontece | Quem age |
|-------|------|-----------------|----------|
| 1 | Informar | Alerta amarelo por 2+ semanas | Coordenador toma ciencia |
| 2 | Pedir apoio | Alerta vermelho confirmado | Diretor participa da proxima reuniao FOCO |
| 3 | Intervencao direta | Prof critico apos 3+ feedbacks / Aluno tier 3 por 4+ sem | Conversa de desempenho / Reuniao com familia |
| 4 | Crise institucional | Evasao >5% / Incidente grave / Conformidade <30% | Plano de crise em 48h |

---

### Fases do Ano

O ano letivo e dividido em 3 fases, cada uma com prioridades diferentes:

#### Fase 1 — SOBREVIVENCIA (Semanas 1-15 | 27/jan a 10/mai)
**Cor: Vermelho** | Foco: garantir o basico

| Prioridade | Meta | Onde estava |
|-----------|------|-------------|
| Registro SIGA | 70% | 43.7% |
| Feedback coordenacao | 40 feedbacks | 1 |
| Presenca alunos | 88% | 84.7% |

#### Fase 2 — CONSOLIDACAO (Semanas 16-33 | 11/mai a 12/set)
**Cor: Laranja** | Foco: alinhar curriculo e aprofundar

| Prioridade | Meta | Onde estava |
|-----------|------|-------------|
| Alinhamento SAE | 55% no ritmo | 12.9% |
| Observacao de aula | 250 observacoes | 0 |
| Intervencao academica | Reduzir alunos risco para 120 | 344 |

#### Fase 3 — EXCELENCIA (Semanas 34-47 | 14/set a 18/dez)
**Cor: Verde** | Foco: qualidade e planejamento 2027

| Prioridade | Meta | Onde estava |
|-----------|------|-------------|
| Avaliacao formativa | 80% com exit ticket | 0% |
| Cobertura curricular | 65% no ritmo | 12.9% |
| Planejamento 2027 | 4 unidades com plano | 0 |

---

### Estacoes (Tom do Sistema)

O sistema ajusta seu tom de comunicacao conforme a "estacao" do ano letivo:

| Estacao | Semanas | Tom |
|---------|---------|-----|
| Plantio | 1-6 | Acolhedor, orientador |
| Crescimento | 7-20 | Desafiador, motivador |
| Dormencia | 21-27 | Reflexivo, planejador (ferias) |
| Florescimento | 28-38 | Celebratorio, intenso |
| Colheita | 39-47 | Estrategico, prospectivo |

---

### Nudges Comportamentais

O sistema usa 5 tecnicas de psicologia comportamental para motivar acao:

| Tecnica | Como funciona | Exemplo |
|---------|---------------|---------|
| **Aversao a perda** | Mostra o que voce PERDE se nao agir | "Se nao agir hoje, perdera visibilidade sobre 45 alunos" |
| **Prova social** | Mostra que outros ja fizeram | "23 de 28 coordenadores ja resolveram isso na 1a semana" |
| **Efeito default** | Plano ja vem pronto, so executar | "Seu plano de acao ja foi gerado. Basta executar." |
| **Compromisso** | Pede para registrar uma meta | "Registre: vou resolver ate sexta. Quem registra cumpre 2x mais." |
| **Identidade** | Reforça o papel do coordenador | "Coordenadores PEEX sao guardioes. Nenhum aluno fica invisivel." |

---

### Rankings

Existem 4 rankings que comparam as 4 unidades:

| Ranking | O que mede | Criterio |
|---------|-----------|----------|
| **Saude** | Estado atual | Indice ELO (IE) |
| **Evolucao** | Melhoria ao longo do tempo | Estrelas acumuladas no trimestre |
| **Generosidade** | Colaboracao entre unidades | Pontos por visitas, mentorias, praticas compartilhadas |
| **Solo** | Registro e dados | Completude e qualidade dos lancamentos |

**Pontos de Generosidade:**

| Acao | Pontos |
|------|--------|
| Visita a outra unidade | 15 |
| Pareamento com resultado positivo | 10 |
| Mentoria ativa entre professores | 8 |
| Pratica compartilhada no feed | 5 |
| Adotou pratica de outra unidade | 4 |
| Material didatico compartilhado | 3 |
| Feedback construtivo registrado | 2 |

---

## As 4 Unidades

| Unidade | Codigo | Foco especial | Coordenadores |
|---------|--------|---------------|---------------|
| **Boa Viagem** | BV | Referencia — meta 80% conformidade | Bruna Vitoria (6-9o), Gilberto (EM) |
| **Candeias** | CD | Equilibrio — 3 coordenadoras | Alline, Elisangela, Vanessa |
| **Janga** | JG | Frequencia — 25% alunos em risco | Lecinane, Pietro |
| **Cordeiro** | CDR | Ocorrencias — 68% das graves da rede | Ana Claudia, Vanessa |

---

## Calendario de Reunioes PEEX

O ano tem **45 reunioes programadas** em 2 tipos:

- **RR (Reuniao de Rede)**: 10x/ano — todas as unidades juntas
- **RU (Reuniao de Unidade)**: 35x/ano — cada unidade separada

### Formatos de Reuniao

| Formato | Nome | Duracao | Quando usar |
|---------|------|---------|-------------|
| F | FLASH | 30 min | Check rapido semanal — foco em dados |
| FO | FOCO | 45 min | Aprofundamento em 1-2 temas |
| C | CRISE | 60 min | Situacao emergencial |
| E | ESTRATEGICA | 90 min | Balanco trimestral, planejamento |

### Reunioes do 1o Trimestre (exemplo)

| Semana | Tipo | Formato | Titulo |
|--------|------|---------|--------|
| 2 | Rede | Estrategica 90min | Choque de Realidade |
| 3 | Unidade | Flash 30min | Check registro |
| 4 | Unidade | Flash 30min | Check registro + Dossie |
| 5 | Unidade | Flash 30min | Pre-Encontro Familias |
| 6 | Rede | Foco 45min | Primeiro Balanco + Feedback |
| 7 | Unidade | Flash 30min | Registro + Feedback |
| 8 | Unidade | Flash 30min | Check feedback + Contrato |
| 9 | Unidade | Flash 30min | Pre-Pascoa |
| 10 | Rede | Foco 45min | Revisao Mid-Tri + Presenca |
| 11 | Unidade | Flash 30min | Busca ativa + Clima |
| 13 | Unidade | Foco 45min | Inclusao/PEI + Escalacao |
| 14 | Unidade | Flash 30min | Feedback individual |
| 15 | Rede | Estrategica 90min | Encerramento I Tri |

---

## Mapa de Paginas — O que cada uma faz

### Paginas da CEO (15 paginas)

#### Zona Consciencia — "O que esta acontecendo na rede?"

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Comando CEO** | Dashboard geral: narrativa IA, 3 decisoes do dia, heatmap de saude, IE da rede, calendario PEEX | Todo dia de manha (5 min) |
| **Prioridades** | Batalhas priorizadas por score, com prescricoes e nudges | Antes de qualquer reuniao |
| **Scorecard** | Scorecard detalhado de cada unidade: IE, conformidade, frequencia, professores criticos, batalhas | Reunioes de rede |
| **Simulador** | "E se eu transferir um professor?" — simula impacto de intervencoes no IE | Decisoes estrategicas |
| **Rankings** | 4 rankings: Saude, Evolucao, Generosidade, Solo | Reunioes de rede, celebracoes |
| **Memoria** | Vacinas institucionais: crises passadas + intervencoes + resultados. Alerta quando dados atuais casam com crise anterior | Quando algo parece familiar |

#### Zona Reuniao — "Como preparar a proxima reuniao?"

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **PEEX Rede** | Gera pauta automatica para reuniao de rede com dados consolidados | Antes da reuniao de rede (10x/ano) |
| **PEEX Adaptativo** | Gera pauta para reuniao de unidade com 5 atos do Ritual de Floresta | Antes de cada reuniao de unidade |
| **Plano de Acao** | 3-5 acoes concretas geradas das batalhas, com responsavel + prazo + status | Toda segunda-feira |
| **Briefing PDF** | Resumo imprimivel de tudo: batalhas + pauta + plano de acao | Para levar impresso na reuniao |

#### Zona Operacao — "Como estao os coordenadores?"

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Espelho Coordenador** | 360 graus de cada coordenador: batalhas resolvidas, tempo de resposta, feedbacks | Acompanhamento quinzenal |
| **Polinizacao** | Feed de boas praticas compartilhadas entre unidades | Quando quiser celebrar ou replicar |

#### Zona Estrategia — "O que precisa da minha atencao?"

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Sinais Vitais** | Semaforo da unidade (5 indicadores) + tendencia + posicao vs rede | Monitoramento semanal |
| **Escalacoes** | Batalhas que subiram de nivel (coordenador nao resolveu) | Quando o sistema notifica |
| **Compromissos** | Compromissos registrados em reuniao + acompanhamento | Pos-reuniao |

---

### Paginas do Diretor (9 paginas)

| Pagina | O que mostra |
|--------|-------------|
| **Painel Diretor** | Dashboard da unidade (mesmo layout do CEO, filtrado) |
| **Scorecard** | Scorecard da propria unidade vs rede |
| **Sinais Vitais** | Semaforo da unidade |
| **Escalacoes** | Batalhas escaladas dos coordenadores |
| **Compromissos** | Compromissos e encaminhamentos |
| **Memoria** | Vacinas institucionais |
| **Prioridades** | Batalhas priorizadas |
| **Rankings** | Posicao da unidade nos 4 rankings |
| **Briefing PDF** | Resumo imprimivel |

---

### Paginas do Coordenador (11 paginas)

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Prioridades** | Batalhas da sua unidade, priorizadas | Todo dia de manha |
| **Meus Professores** | Professores agrupados por saude (verde/amarelo/vermelho) com prescricoes individuais | Planejamento de feedbacks |
| **Meus Alunos** | Alunos em 3 tiers (A/B/C) com frequencia e ocorrencias | Busca ativa, intervencoes |
| **Ritmo Semanal** | Visao dia a dia: quem registrou SEG, TER, QUA, QUI, SEX | Monitoramento diario |
| **Plano de Acao** | 3-5 acoes da semana com status | Toda segunda + acompanhamento |
| **PEEX Adaptativo** | Pauta da proxima reuniao (5 atos) | Preparacao da reuniao |
| **Pauta Reuniao** | Gerador de pauta para reuniao de unidade | Antes de cada reuniao |
| **Meu Espelho** | Auto-avaliacao: % batalhas resolvidas, tempo de resposta | Reflexao pessoal |
| **Polinizacao** | Feed de praticas: compartilhar e adotar ideias | Quando quiser trocar experiencias |
| **Rankings** | Posicao da unidade nos rankings | Motivacao |
| **Briefing PDF** | Resumo imprimivel | Para reunioes presenciais |

---

### Paginas do Professor (3 paginas)

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Meu Espelho** | Seu score decomposto: Registro (35%) + Conteudo (25%) + Tarefa (15%) + Recencia (25%). Comparativo anonimo com a media. Caminho de melhoria. | A qualquer momento |
| **Minhas Turmas** | Conformidade e conteudo por turma/disciplina | Para ver como estao suas turmas |
| **Meu Progresso** | Evolucao do score ao longo das semanas + conquistas desbloqueadas | Motivacao pessoal |

**Importante**: O professor NUNCA ve dados de outros professores. Apenas a media anonima para comparacao.

---

## Ritual de Floresta — A Reuniao PEEX

Toda reuniao de unidade segue a estrutura dos **5 Atos do Ritual de Floresta**:

### Ato 1 — Raizes (5 min)
Check-in: como esta a energia da equipe? Momento humano antes dos dados.

### Ato 2 — Solo (10 min)
Dados da semana: batalhas, conformidade, frequencia. O "chao" sobre o qual se trabalha.

### Ato 3 — Micelio (10 min)
Conexoes: quem precisa de ajuda? Quem pode ajudar? A "rede subterranea" de colaboracao.

### Ato 4 — Sementes (10 min)
3 compromissos concretos para a proxima semana. Cada um com responsavel e prazo.

### Ato 5 — Chuva (5 min)
Celebrar 1 conquista da semana. **NUNCA terminar com problema.** Sempre com algo positivo.

---

## Os 6 Robos IA

O sistema roda automaticamente 6 "robos" que processam dados e geram informacoes:

| Robo | Quando roda | O que faz |
|------|-------------|-----------|
| **VIGILIA** | 4x por dia (2h, 8h, 14h, 20h) | Detecta batalhas, gera scorecards |
| **ESTRATEGISTA** | Domingo 22h | Gera narrativa CEO, 3 decisoes, ranking, heatmap |
| **CONSELHEIRO** | Segunda 5h | Gera pauta da reuniao, perguntas, rituais |
| **COMPARADOR** | Segunda 5h30 | Calcula estrelas, rankings, compara unidades |
| **PREDITOR** | Sexta 20h | Projeta tendencias, gera alertas preventivos |
| **RETROALIMENTADOR** | A cada 6h | Verifica se acoes foram executadas, escala se nao |

Voce nao precisa fazer nada — os robos rodam sozinhos. Os resultados aparecem automaticamente nas paginas.

---

## Metas SMART do Ano

| Eixo | Indicador | Inicio | Meta 1oTri | Meta 2oTri | Meta Ano |
|------|-----------|--------|------------|------------|----------|
| Conformidade | % media de lancamento | 43.7% | 70% | 78% | 80% |
| Conformidade | Professores criticos | 41 | 20 | 10 | 5 |
| Conformidade | % profs no ritmo SAE | 12.9% | 35% | 55% | 65% |
| Frequencia | % frequencia media | 84.7% | 88% | 89% | 90% |
| Frequencia | % alunos freq >90% | 54.1% | 65% | 72% | 78% |
| Frequencia | % alunos em risco | 18.4% | 15% | 12% | 10% |
| Desempenho | Media de notas | 8.3 | 8.0 | 8.0 | 8.0 |
| Clima | Ocorrencias graves | 53 | 26 | 13 | 20 |

---

## Marcos do 1o Trimestre (checklist)

- [ ] Conformidade >= 70%
- [ ] 40+ feedbacks registrados
- [ ] Frequencia JG >= 85%
- [ ] CDR <= 4 ocorrencias graves/semana
- [ ] Todos os 41 professores criticos contatados
- [ ] Protocolo de Busca Ativa funcionando
- [ ] PMV (Painel de Monitoramento da Vigilia) enviado toda segunda sem falha

---

## Fluxo Semanal Sugerido

### Segunda-feira
1. Abra o **Comando CEO** (ou Prioridades, se coordenador)
2. Leia a narrativa gerada pelo ESTRATEGISTA
3. Veja as 3 decisoes sugeridas
4. Abra o **Plano de Acao** e confirme as acoes da semana
5. Prepare a pauta da reuniao no **PEEX Adaptativo**

### Terca a Quinta
1. Acompanhe o **Ritmo Semanal** — quem registrou hoje?
2. Execute as acoes do plano
3. Marque como "em andamento" ou "resolvida"
4. Use **Meus Professores** para feedbacks individuais

### Sexta-feira
1. Revise o **Espelho Coordenador** — como foi sua semana?
2. Celebre conquistas no **Feed de Polinizacao**
3. O PREDITOR gera projecoes para a proxima semana

### Antes de cada reuniao
1. Abra **PEEX Adaptativo** ou **PEEX Rede** (conforme o tipo)
2. Revise a pauta gerada
3. Exporte **Briefing PDF** se quiser levar impresso
4. Adicione notas pessoais

---

## Glossario Rapido

| Termo | Significado |
|-------|-------------|
| **IE** | Indice ELO — nota de saude da unidade (0-100) |
| **Batalha** | Problema detectado automaticamente pelo sistema |
| **Estrela** | Ponto de evolucao por indicador (0-3 por semana) |
| **Escalacao** | Problema que subiu de nivel por nao ser resolvido |
| **Nudge** | Mensagem motivacional baseada em psicologia comportamental |
| **Conformidade** | % de aulas registradas no SIGA |
| **Ritmo SAE** | Alinhamento do professor com o curriculo esperado |
| **Tier A/B/C** | Classificacao de alunos por risco (A=saudavel, C=critico) |
| **SIGA** | Sistema academico (lancamento de aulas, notas, frequencia) |
| **SAE** | Material didatico + plataforma digital |
| **RR** | Reuniao de Rede (10x/ano) |
| **RU** | Reuniao de Unidade (35x/ano) |
| **FLASH** | Reuniao rapida de 30 min |
| **FOCO** | Reuniao de 45 min com aprofundamento |
| **Polinizacao** | Compartilhamento de boas praticas entre unidades |
| **Micorrizica** | Pareamento automatico de professores para colaboracao |
| **Vacina** | Registro de crise passada para prevencao futura |
| **PMV** | Painel de Monitoramento da Vigilia (relatorio automatico) |

---

## Perguntas Frequentes

**P: Com que frequencia os dados atualizam?**
R: O robo VIGILIA roda 4x por dia. Os dados que voce ve tem no maximo 6 horas de atraso.

**P: O professor pode ver dados de outros professores?**
R: Nao. O professor so ve seus proprios dados e a media anonima da unidade.

**P: O que fazer quando uma batalha aparece como URGENTE?**
R: Agir no mesmo dia. Abra a batalha, leia a prescricao, e execute a acao sugerida. Marque como "em andamento" no Plano de Acao.

**P: Como funciona o ranking de Generosidade?**
R: Acumula pontos por acoes de colaboracao: visitas entre unidades (+15), mentorias (+8), praticas compartilhadas (+5), etc.

**P: Posso editar a pauta gerada?**
R: Sim. A pauta e uma sugestao baseada nos dados. Voce pode adicionar notas e ajustar antes da reuniao.

**P: O que acontece se eu nao resolver uma batalha?**
R: Apos 2 semanas, ela escala para o nivel seguinte. No nivel 3, o diretor e chamado para intervir. No nivel 4, vira crise institucional.

**P: O simulador realmente preve o futuro?**
R: O simulador estima impacto baseado em medias historicas. Nao e uma previsao exata, mas uma ferramenta de apoio a decisao.

---

*Documento gerado em 21/02/2026 — PEEX Command Center v1.0*
