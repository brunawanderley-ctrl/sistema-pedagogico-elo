---
tipo: guia
status: ativo
owner: Bruna Viegas
criacao: 2026-02-21
tags: [peex, command-center, guia, operacional, reunioes, batalhas, rankings]
---

# PEEX Command Center — Guia Completo de Uso

> **Acesso:** `streamlit run PEEX_Command_Center.py` (porta 8515)
> **O que e:** Ferramenta de gestao pedagogica inteligente do Colegio ELO 2026
> **Para quem:** CEO, Diretores, Coordenadores e Professores

---

## 1. O que e o PEEX?

**PEEX = Programa ELO de Excelencia**

E o sistema que transforma dados brutos do SIGA (sistema academico da escola) em **decisoes concretas** para cada pessoa da equipe. Em vez de olhar planilhas, voce abre o PEEX e ve:

- O que esta funcionando e o que nao esta
- O que fazer primeiro (e por que)
- Como a sua unidade se compara com as outras
- Qual pauta levar para a proxima reuniao

> **Analogia:** O PEEX e como o "painel de um aviao". A CEO (piloto) ve todos os instrumentos. O Diretor (copiloto) ve os essenciais. O Coordenador (engenheiro de voo) monitora os sistemas. O Professor (passageiro) acompanha seu proprio voo.

---

## 2. Como acessar

1. Abra o navegador
2. Acesse o endereco do sistema
3. Digite usuario e senha
4. O sistema reconhece seu perfil e mostra **apenas as paginas da sua funcao**

### Contas de acesso

| Login | Quem e | Unidade | Perfil | Senha |
|-------|--------|---------|--------|-------|
| `bruna` | Bruna Viegas (CEO) | Toda a rede | CEO | `EloAdmin2026!` |
| `bv` | Coordenacao Boa Viagem | BV | Coordenador | `EloBV2026` |
| `candeias` | Coordenacao Candeias | CD | Coordenador | `EloCD2026` |
| `janga` | Coordenacao Janga | JG | Coordenador | `EloJG2026` |
| `cordeiro` | Coordenacao Cordeiro | CDR | Coordenador | `EloCDR2026` |
| `dir_bv` | Diretor(a) BV | BV | Diretor | `EloDirBV2026` |
| `dir_cd` | Diretor(a) CD | CD | Diretor | `EloDirCD2026` |
| `dir_jg` | Diretor(a) JG | JG | Diretor | `EloDirJG2026` |
| `dir_cdr` | Diretor(a) CDR | CDR | Diretor | `EloDirCDR2026` |
| `prof_demo` | Professor demonstracao | BV | Professor | `EloProf2026` |

> **O que e "perfil"?** E o nivel de acesso. Cada perfil ve paginas diferentes. Um coordenador nao ve o que o CEO ve, e vice-versa. Isso garante que cada pessoa ve exatamente o que precisa.

---

## 3. Os 4 Perfis (quem ve o que)

### CEO
**Quem:** Bruna Viegas
**Quantas paginas:** 15
**O que ve:** Toda a rede — 4 unidades, todos os indicadores, rankings, simulacoes, vacinas, pautas de reuniao de rede.
**Para que serve:** Tomar decisoes estrategicas e acompanhar a saude geral.

### Diretor
**Quem:** Diretor de cada unidade
**Quantas paginas:** 9
**O que ve:** Estrategia da sua unidade + visao parcial da rede. Recebe escalacoes dos coordenadores.
**Para que serve:** Intervir quando o coordenador nao consegue resolver sozinho.

### Coordenador
**Quem:** Coordenadores pedagogicos de cada unidade
**Quantas paginas:** 11
**O que ve:** Operacao diaria — seus professores, seus alunos, ritmo semanal, plano de acao, pauta de reuniao.
**Para que serve:** Agir diretamente nas batalhas do dia a dia. E o "guardiao PEEX".

### Professor
**Quem:** Cada professor individualmente
**Quantas paginas:** 3
**O que ve:** Apenas seus proprios dados — score, turmas, progresso. **Nunca ve dados de colegas.**
**Para que serve:** Transparencia sem exposicao. O professor sabe como esta e o que pode melhorar.

> **O que e "guardiao PEEX"?** E o apelido do coordenador no sistema. A ideia e que o coordenador e a pessoa que "guarda" a aprendizagem — nenhum aluno fica invisivel quando o guardiao age.

---

## 4. Glossario — Todos os termos do sistema

Antes de ver as paginas, aqui esta cada termo que aparece no PEEX:

### Termos de dados

| Termo | O que significa | Exemplo pratico |
|-------|----------------|-----------------|
| **Conformidade** | Percentual de aulas que o professor registrou no SIGA em relacao ao esperado | "Prof. Silva tem 75% de conformidade" = registrou 75% das aulas que deveria |
| **Frequencia** | Percentual de presenca dos alunos nas aulas | "Turma 8B tem 82% de frequencia" = em media, 82% dos alunos comparecem |
| **Ritmo SAE** | Se o professor esta alinhado com o curriculo (material didatico SAE) | "Prof. Lima esta no Cap 3 mas deveria estar no Cap 5" = atrasado |
| **Ocorrencia** | Registro de evento disciplinar (advertencia, suspensao, etc.) | "CDR tem 36 ocorrencias graves" |
| **Desempenho** | Notas dos alunos | "Media de notas da rede: 8.3" |
| **SIGA** | Sistema academico onde professores lancam aulas, notas e frequencia | E o sistema que a escola ja usa |
| **SAE** | Sistema de material didatico + plataforma digital | Livros, exercicios online, conteudo digital |

> **Conformidade e frequencia sao a mesma coisa?** Nao! Conformidade e do **professor** (ele registrou a aula?). Frequencia e do **aluno** (ele veio na aula?).

### Termos do PEEX

| Termo | O que significa | Para que serve |
|-------|----------------|----------------|
| **IE (Indice ELO)** | Nota de saude da unidade de 0 a 100. Combina 6 indicadores. | Comparar unidades com um unico numero. "BV esta com IE 72." |
| **Batalha** | Problema detectado automaticamente pelo sistema | O PEEX analisa os dados e identifica 9 tipos de problema. Cada um vira uma "batalha" que precisa ser resolvida. |
| **Estrela** | Ponto de evolucao semanal (0 a 3 por indicador) | Mede se a unidade esta melhorando, estagnada ou piorando. Acumula no trimestre. |
| **Escalacao** | Quando um problema persiste e sobe para o nivel acima | Se o coordenador nao resolve em 2 semanas, o diretor e chamado. Se continua, vira crise. |
| **Nudge** | Mensagem motivacional baseada em psicologia | "23 de 28 coordenadores ja resolveram isso" — usa tecnicas como prova social e aversao a perda. |
| **Fase** | Periodo do ano com prioridades especificas | Fase 1 (Sobrevivencia), Fase 2 (Consolidacao), Fase 3 (Excelencia). |
| **Estacao** | Tom de comunicacao do sistema conforme o periodo | Plantio (acolhedor), Crescimento (desafiador), Dormencia (reflexivo), Florescimento (intenso), Colheita (estrategico). |
| **Vacina** | Registro de crise passada para prevencao futura | "Em 2025 houve queda pos-ferias. Intervencao X resolveu." Se o padrao se repetir, o sistema alerta. |
| **Polinizacao** | Compartilhamento de boas praticas entre unidades | Feed tipo rede social onde coordenadores postam o que funcionou. |
| **Micorrizica** | Pareamento automatico de professores | O sistema sugere pares de professores que podem se ajudar (mesma disciplina, series complementares). |
| **Ritual de Floresta** | Estrutura em 5 atos para reunioes PEEX | Raizes → Solo → Micelio → Sementes → Chuva. Todo reuniao segue essa ordem. |

> **Por que "batalha"?** Porque cada problema e algo a ser "vencido" — nao e so um dado, e um convite a acao. O sistema diz "aqui esta o problema, aqui esta o que fazer."

> **Por que "estrela"?** Porque reconhece evolucao, nao apenas resultado. Uma unidade que saiu de 40% para 55% pode ter mais estrelas que uma que esta em 80% estagnada.

### Termos de reuniao

| Termo | O que significa | Quando acontece |
|-------|----------------|-----------------|
| **RR (Reuniao de Rede)** | Reuniao com todas as unidades juntas | 10x por ano (CEO + Diretores + Coordenadores) |
| **RU (Reuniao de Unidade)** | Reuniao da equipe de uma unidade | 35x por ano (semanalmente) |
| **FLASH** | Reuniao rapida de 30 min | Check semanal focado em dados |
| **FOCO** | Reuniao de 45 min com aprofundamento | 1-2 temas que precisam de mais tempo |
| **CRISE** | Reuniao emergencial de 60 min | Quando algo grave acontece |
| **ESTRATEGICA** | Reuniao de 90 min para planejamento | Abertura/encerramento de trimestre |

> **Quem decide o formato?** O calendario ja define. A pauta e gerada automaticamente pelo sistema com base nos dados da semana.

### Termos de classificacao

| Termo | O que significa | Criterio |
|-------|----------------|----------|
| **Tier A (aluno)** | Aluno saudavel | Frequencia >= 85% e menos de 2 ocorrencias |
| **Tier B (aluno)** | Aluno em atencao | Frequencia >= 75% e menos de 5 ocorrencias |
| **Tier C (aluno)** | Aluno em risco | Abaixo dos criterios de A e B |
| **Verde (professor)** | Professor saudavel | Conformidade >= 70% |
| **Amarelo (professor)** | Professor em atencao | Conformidade entre 40% e 70% |
| **Vermelho (professor)** | Professor critico | Conformidade < 40% |
| **URGENTE (batalha)** | Agir HOJE | Score alto de urgencia |
| **IMPORTANTE (batalha)** | Agir ESTA SEMANA | Score medio |
| **MONITORAR (batalha)** | Acompanhar | Score baixo, mas vale observar |

---

## 5. Como funciona o Indice ELO (IE)

O IE e a "nota de saude" de cada unidade. Vai de 0 a 100 e combina 6 indicadores:

| Indicador | Peso | O que mede | Bom e... |
|-----------|------|------------|----------|
| Conformidade media | 25% | % aulas registradas no SIGA | Alto (mais registro = melhor) |
| Frequencia media | 20% | % presenca dos alunos | Alto (mais presenca = melhor) |
| Profs no ritmo SAE | 20% | % professores alinhados ao curriculo | Alto (mais alinhados = melhor) |
| Alunos com freq >90% | 15% | % alunos com presenca excelente | Alto (mais alunos = melhor) |
| Alunos em risco | 10% | % alunos em situacao critica | **Baixo** (menos risco = melhor) |
| Ocorrencias graves | 10% | Total de ocorrencias graves | **Baixo** (menos ocorrencias = melhor) |

> **Atenção:** Nos ultimos 2 indicadores, quanto MENOR o valor, MELHOR a nota. O sistema inverte automaticamente.

**Exemplo pratico:**
- BV: 75% conformidade, 88% frequencia, 40% ritmo SAE, 60% freq>90%, 15% risco, 20 ocorrencias → **IE ≈ 67/100**
- Se BV subir conformidade de 75% para 85%, o IE sobe ~2.5 pontos (porque conformidade pesa 25%).

---

## 6. As 9 Batalhas (problemas detectados)

O PEEX analisa os dados automaticamente e identifica problemas. Cada problema e uma "batalha":

| # | Tipo | O que detecta | Exemplo | O que fazer |
|---|------|---------------|---------|-------------|
| 1 | **PROF_SILENCIOSO** | Professor parou de registrar | "Prof. Silva: 12 dias sem registro" | Conversa individual imediata |
| 2 | **DISCIPLINA_ORFA** | Disciplina sem nenhum registro no ano | "Filosofia 7A: zero aulas" | Verificar se ha professor designado |
| 3 | **TURMA_CRITICA** | Turma abaixo da meta | "8B: 35% conformidade" | Priorizar professores dessa turma |
| 4 | **ALUNO_FREQUENCIA** | Aluno com presenca < 75% (risco LDB) | "15 alunos abaixo do limiar" | Busca ativa + contato com familia |
| 5 | **ALUNO_OCORRENCIA** | Ocorrencias graves recorrentes | "3 graves em 2 semanas" | Intervencao + familia |
| 6 | **PROF_QUEDA** | Queda > 30% de uma semana pra outra | "De 80% para 45%" | Verificar se houve problema |
| 7 | **CURRICULO_ATRASADO** | Professor > 1 capitulo atras do SAE | "Cap 3, deveria Cap 5" | Plano de recuperacao curricular |
| 8 | **PROF_SEM_CONTEUDO** | > 50% das aulas sem conteudo | "60% sem descricao" | Orientar sobre registro completo |
| 9 | **PROCESSO_DEADLINE** | Prazo de feedback se aproximando | "5 dias para o prazo" | Reservar horarios na agenda |

> **Como o sistema prioriza?** Cada batalha recebe um "score" numerico baseado em gravidade, quantidade de afetados, e ha quanto tempo persiste. As de score mais alto aparecem primeiro.

> **O que acontece se eu nao resolver?** Apos 2 semanas, a batalha escala. Nivel 1 → 2 → 3 → 4 (crise). O diretor e notificado. Ver secao de Escalacao.

---

## 7. Estrelas de Evolucao

As estrelas medem se a unidade esta **melhorando** (nao apenas o estado atual).

### Como ganha estrelas (por indicador, por semana)

| Estrelas | Criterio |
|----------|----------|
| 0 estrelas | Piorou ou estagnou por 2+ semanas |
| 1 estrela | Estavel (variacao < 1 ponto percentual) |
| 2 estrelas | Melhorou de 1 a 3 pontos percentuais |
| 3 estrelas | Melhorou > 3pp OU atingiu a meta |

### 5 indicadores avaliados

1. Conformidade media
2. Frequencia media
3. Professores no ritmo SAE
4. Alunos em risco (invertido — cair e bom)
5. Ocorrencias graves (invertido — cair e bom)

**Maximo por semana:** 5 indicadores x 3 estrelas = **15 estrelas**

> **As estrelas acumulam!** Se voce ganhou 12 estrelas na semana 3 e 10 na semana 4, tem 22 estrelas no trimestre. Nunca perde estrelas ja conquistadas.

> **Por que isso importa?** Uma unidade que comecou mal mas esta melhorando rapido acumula MAIS estrelas que uma que comecou bem mas estagnou. Reconhece esforco, nao apenas resultado.

---

## 8. Escalacao — Quando o problema sobe de nivel

| Nivel | Nome | Quando | Quem age | O que acontece |
|-------|------|--------|----------|----------------|
| 1 | **Informar** | Alerta amarelo por 2+ semanas | Coordenador | Toma ciencia, sem acao do diretor |
| 2 | **Pedir apoio** | Alerta vermelho confirmado | Diretor participa da reuniao FOCO | Apoio na estrategia |
| 3 | **Intervencao direta** | Prof critico apos 3+ feedbacks / Aluno tier C por 4+ sem | Conversa de desempenho + Reuniao com familia | Acoes formais |
| 4 | **Crise institucional** | Evasao > 5% / Incidente grave / Conformidade < 30% | Plano de crise em 48h | CEO + Diretor atuam juntos |

> **Quem decide a escalacao?** O sistema sugere automaticamente, mas a decisao final e humana. O coordenador pode pedir apoio antes do sistema sugerir.

---

## 9. As 3 Fases do Ano

O ano letivo e dividido em 3 fases, cada uma com foco diferente:

### Fase 1 — SOBREVIVENCIA (Semanas 1-15 | jan-mai)
**Cor:** Vermelho | **Tom:** "Garantir o basico"

| Prioridade | O que e | De onde partimos | Meta |
|-----------|---------|------------------|------|
| Registro SIGA | % de aulas registradas | 43.7% | 70% |
| Feedback coordenacao | Feedbacks dados a professores | 1 | 40 |
| Presenca alunos | % de frequencia | 84.7% | 88% |

> **Por que "sobrevivencia"?** Porque se os professores nao registram e os alunos nao vem, nada mais funciona. Primeiro, garantir que os dados existem.

### Fase 2 — CONSOLIDACAO (Semanas 16-33 | mai-set)
**Cor:** Laranja | **Tom:** "Aprofundar e alinhar"

| Prioridade | O que e | De onde partimos | Meta |
|-----------|---------|------------------|------|
| Alinhamento SAE | % profs no ritmo | 12.9% | 55% |
| Observacao de aula | Observacoes realizadas | 0 | 250 |
| Intervencao academica | Alunos em atencao/critico | 344 | 120 |

> **Por que "consolidacao"?** Porque o basico ja funciona. Agora e hora de alinhar o curriculo e aprofundar o acompanhamento.

### Fase 3 — EXCELENCIA (Semanas 34-47 | set-dez)
**Cor:** Verde | **Tom:** "Qualidade e futuro"

| Prioridade | O que e | De onde partimos | Meta |
|-----------|---------|------------------|------|
| Avaliacao formativa | % profs com exit ticket | 0% | 80% |
| Cobertura curricular | % profs no ritmo | 12.9% | 65% |
| Planejamento 2027 | Unidades com plano | 0 | 4 |

> **O que e "exit ticket"?** E uma mini-avaliacao no final da aula (2-3 perguntas) para verificar se os alunos aprenderam. E parte da avaliacao formativa.

---

## 10. Estacoes (o tom do sistema)

O sistema muda seu tom de comunicacao conforme o momento do ano:

| Estacao | Semanas | Tom | Como o sistema fala |
|---------|---------|-----|---------------------|
| Plantio | 1-6 | Acolhedor, orientador | "Estamos plantando as bases. Cada registro e uma semente." |
| Crescimento | 7-20 | Desafiador, motivador | "Hora de crescer. Voce consegue mais." |
| Dormencia | 21-27 | Reflexivo, planejador | "Pausa para reflexao. O que aprendemos ate aqui?" |
| Florescimento | 28-38 | Celebratorio, intenso | "Os resultados estao aparecendo. Celebre e intensifique." |
| Colheita | 39-47 | Estrategico, prospectivo | "O que levamos para 2027? Qual o legado?" |

> **A dormencia coincide com as ferias?** Sim! Semanas 23-27 (julho) sao ferias. O sistema entra em modo reflexivo.

---

## 11. Os 4 Rankings

As unidades competem de forma saudavel em 4 rankings:

| Ranking | O que mede | Como pontua | Para que serve |
|---------|-----------|-------------|----------------|
| **Saude** | Estado atual | Indice ELO (IE) | Quem esta melhor AGORA |
| **Evolucao** | Melhoria ao longo do tempo | Estrelas acumuladas | Quem esta MELHORANDO mais |
| **Generosidade** | Colaboracao entre unidades | Pontos por acoes colaborativas | Quem AJUDA mais |
| **Solo** | Qualidade dos dados | Completude dos registros | Quem tem os DADOS mais completos |

### Pontos de Generosidade

| Acao | Pontos | O que conta |
|------|--------|-------------|
| Visita a outra unidade | +15 | Coordenador/professor visitou pessoalmente |
| Pareamento com resultado | +10 | Dois professores pareados e houve melhoria |
| Mentoria ativa | +8 | Professor ajudando colega de outra unidade |
| Pratica compartilhada | +5 | Postou no feed de Polinizacao |
| Adotou pratica | +4 | Adotou ideia de outra unidade |
| Material compartilhado | +3 | Compartilhou material didatico |
| Feedback construtivo | +2 | Deu feedback registrado a colega |

> **Por que ranking de Generosidade?** Porque queremos que as unidades se AJUDEM, nao apenas compitam. Ganha mais quem colabora mais.

---

## 12. Nudges Comportamentais (5 tecnicas)

O sistema usa tecnicas de psicologia para motivar acao:

| Tecnica | Como funciona | Exemplo no PEEX |
|---------|---------------|-----------------|
| **Aversao a perda** | Mostra o que voce PERDE se nao agir | "Se nao agir hoje, perdera visibilidade sobre 45 alunos" |
| **Prova social** | Mostra que outros ja fizeram | "23 de 28 coordenadores ja resolveram isso na 1a semana" |
| **Efeito default** | Plano ja vem pronto, so executar | "Seu plano de acao ja foi gerado. Basta confirmar." |
| **Compromisso** | Pede para registrar uma meta | "Registre: vou resolver ate sexta. Quem registra cumpre 2x mais." |
| **Identidade** | Reforça o papel do coordenador | "Coordenadores PEEX sao guardioes. Nenhum aluno fica invisivel." |

> **O que e "nudge"?** E um "empurraozinho" — uma mensagem que aparece no momento certo para incentivar a acao. Nao e obrigacao, e motivacao.

---

## 13. Ritual de Floresta — Como fazer a reuniao PEEX

Toda reuniao de unidade segue 5 atos:

### Ato 1 — Raizes (5 min)
**O que fazer:** Check-in. Como esta a energia da equipe?
**Por que:** Momento humano antes dos dados. Ninguem absorve informacao estressado.

### Ato 2 — Solo (10 min)
**O que fazer:** Apresentar os dados da semana: batalhas, conformidade, frequencia.
**Por que:** O "solo" e a base sobre a qual tudo cresce. Dados sao o chao.

### Ato 3 — Micelio (10 min)
**O que fazer:** Quem precisa de ajuda? Quem pode ajudar?
**Por que:** "Micelio" e a rede invisivel que conecta as arvores. Aqui conectamos as pessoas.

### Ato 4 — Sementes (10 min)
**O que fazer:** Definir 3 compromissos concretos para a proxima semana. Com responsavel e prazo.
**Por que:** Sem compromisso concreto, a reuniao nao gera acao.

### Ato 5 — Chuva (5 min)
**O que fazer:** Celebrar 1 conquista da semana.
**REGRA DE OURO: NUNCA terminar com problema. Sempre com algo positivo.**

> **Micelio = rede de fungos?** Sim! Na natureza, os micorrizas conectam arvores por baixo da terra, permitindo que compartilhem nutrientes. No PEEX, e a rede de colaboracao entre professores e equipes.

---

## 14. Calendario de Reunioes

O ano tem **45 reunioes** programadas:
- **10 Reunioes de Rede (RR)** — todas as unidades juntas
- **35 Reunioes de Unidade (RU)** — cada unidade separada

### Formatos

| Sigla | Nome | Duracao | Quando usar |
|-------|------|---------|-------------|
| **F** | FLASH | 30 min | Check semanal rapido — dados e acoes |
| **FO** | FOCO | 45 min | Aprofundamento em 1-2 temas |
| **C** | CRISE | 60 min | Emergencia (nao planejada) |
| **E** | ESTRATEGICA | 90 min | Balanco trimestral, planejamento |

### Exemplo: Reunioes do 1o Trimestre

| Sem | Tipo | Formato | Titulo | Foco |
|-----|------|---------|--------|------|
| 2 | Rede | Estrategica 90min | Choque de Realidade | Registro como prioridade #1 |
| 3 | Unidade | Flash 30min | Check registro | Lista nominal: quem registrou, quem nao |
| 4 | Unidade | Flash 30min | Check registro + Dossie | Dossie atualizado |
| 5 | Unidade | Flash 30min | Pre-Encontro Familias | 5 alunos em maior risco |
| 6 | Rede | Foco 45min | Primeiro Balanco + Feedback | Conformidade Sem 2 vs Sem 6 |
| 7 | Unidade | Flash 30min | Registro + Feedback | Primeiras conversas de 10 min |
| 8 | Unidade | Flash 30min | Check feedback + Contrato | Contrato de Pratica Docente |
| 9 | Unidade | Flash 30min | Pre-Pascoa | Nenhum professor sai sem atualizar |
| 10 | Rede | Foco 45min | Revisao Mid-Tri + Presenca | Busca Ativa 3 niveis |
| 11 | Unidade | Flash 30min | Busca ativa + Clima | Termometro de Clima |
| 13 | Unidade | Foco 45min | Inclusao/PEI + Escalacao | Mapa de Barreiras |
| 14 | Unidade | Flash 30min | Feedback individual | Celebrar + conversa franca |
| 15 | Rede | Estrategica 90min | Encerramento I Tri | Balanco + prioridades II Tri |

> **Quem prepara a pauta?** O sistema gera automaticamente com base nos dados da semana. O coordenador revisa, ajusta e exporta.

---

## 15. As 4 Unidades

| Unidade | Codigo | Foco especial | Coordenadores | Gatilho de escalacao |
|---------|--------|---------------|---------------|----------------------|
| **Boa Viagem** | BV | Referencia — meta 80% conformidade | Bruna Vitoria (6-9o), Gilberto (EM) | >5 profs criticos sem feedback em 2+ sem |
| **Candeias** | CD | Equilibrio — 3 coordenadoras | Alline, Elisangela, Vanessa | Evasao >3 alunos/semana |
| **Janga** | JG | Frequencia — 25% alunos em risco | Lecinane, Pietro | Frequencia semanal <75% |
| **Cordeiro** | CDR | Ocorrencias — 68% das graves da rede | Ana Claudia, Vanessa | >6 ocorrencias graves em 1 semana |

> **Por que cada unidade tem foco diferente?** Porque cada uma tem um desafio principal. BV precisa manter a excelencia. JG precisa resolver frequencia. CDR precisa reduzir ocorrencias. O sistema adapta as batalhas e nudges para cada realidade.

---

## 16. Mapa de Paginas — O que cada uma faz

### Para a CEO (15 paginas)

#### Zona Consciencia — "O que esta acontecendo?"

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Comando CEO** | Dashboard geral: narrativa da IA, 3 decisoes do dia, heatmap, IE, calendario | Todo dia de manha (5 min) |
| **Prioridades** | Batalhas priorizadas por score com prescricoes | Antes de qualquer reuniao |
| **Scorecard** | Scorecard detalhado de cada unidade (8 metricas) | Reunioes de rede |
| **Simulador** | "E se eu transferir um professor?" — simula impacto no IE | Decisoes estrategicas |
| **Rankings** | 4 rankings: Saude, Evolucao, Generosidade, Solo | Reunioes de rede, celebracoes |
| **Memoria** | Vacinas: crises anteriores + o que funcionou | Quando algo parece familiar |

> **O que e "heatmap"?** E um mapa de calor — uma grade colorida que mostra, de um relance, quais unidades/series estao bem (verde) ou mal (vermelho).

> **O que e "narrativa da IA"?** O robo ESTRATEGISTA analisa todos os dados e escreve um resumo em linguagem natural. Ex: "BV manteve conformidade em 72%. JG caiu 3pp em frequencia — merece atencao. CDR reduziu ocorrencias pela 2a semana — celebrar."

#### Zona Reuniao — "Como preparar a proxima reuniao?"

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **PEEX Rede** | Pauta automatica para reuniao de rede | Antes da reuniao de rede (10x/ano) |
| **PEEX Adaptativo** | Pauta para reuniao de unidade (5 atos) | Antes de cada reuniao (35x/ano) |
| **Plano de Acao** | 3-5 acoes concretas com responsavel + prazo + status | Toda segunda-feira |
| **Briefing PDF** | Resumo imprimivel | Para levar na reuniao |

> **O que e "PEEX Adaptativo"?** A pauta da reuniao se adapta aos dados. Se tem batalhas urgentes, o Ato 2 (Solo) mostra elas. Se tem celebracoes, o Ato 5 (Chuva) destaca. Nao e uma pauta fixa.

#### Zona Operacao — "Como estao os coordenadores?"

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Espelho Coordenador** | 360 graus: batalhas resolvidas, tempo de resposta, feedbacks | Quinzenal |
| **Polinizacao** | Feed de boas praticas entre unidades | Celebrar e replicar |

#### Zona Estrategia — "O que precisa da minha atencao?"

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Sinais Vitais** | Semaforo da unidade (5 indicadores) + tendencia | Semanal |
| **Escalacoes** | Batalhas que subiram de nivel | Quando o sistema notifica |
| **Compromissos** | Compromissos registrados em reuniao + status | Pos-reuniao |

---

### Para o Diretor (9 paginas)

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Painel Diretor** | Dashboard da unidade | Diario |
| **Scorecard** | Metricas da unidade vs rede | Semanal |
| **Sinais Vitais** | Semaforo + tendencia | Semanal |
| **Escalacoes** | Batalhas que subiram do coordenador | Quando notificado |
| **Compromissos** | Encaminhamentos | Pos-reuniao |
| **Memoria** | Vacinas e historico | Quando necessario |
| **Prioridades** | Batalhas priorizadas | Antes de reunioes |
| **Rankings** | Posicao da unidade | Motivacao |
| **Briefing PDF** | Resumo imprimivel | Para reunioes |

---

### Para o Coordenador (11 paginas)

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Prioridades** | Batalhas da unidade, priorizadas | Todo dia de manha |
| **Meus Professores** | Professores agrupados: verde/amarelo/vermelho + prescricoes | Planejamento de feedbacks |
| **Meus Alunos** | Alunos em 3 tiers (A/B/C) com frequencia e ocorrencias | Busca ativa |
| **Ritmo Semanal** | Dia a dia: quem registrou SEG, TER, QUA, QUI, SEX | Monitoramento diario |
| **Plano de Acao** | 3-5 acoes com status | Segunda + acompanhamento |
| **PEEX Adaptativo** | Pauta da proxima reuniao (5 atos) | Preparacao da reuniao |
| **Pauta Reuniao** | Gerador de pauta com export TXT/WhatsApp | Antes da reuniao |
| **Meu Espelho** | Auto-avaliacao: % batalhas resolvidas, tempo de resposta | Reflexao |
| **Polinizacao** | Feed de praticas | Trocar experiencias |
| **Rankings** | Posicao da unidade | Motivacao |
| **Briefing PDF** | Resumo imprimivel | Para reunioes |

> **O que e "prescricao"?** E a sugestao especifica de acao para cada professor. Ex: "Prof. Silva (vermelho): conversa individual urgente. Foco em registro de aulas — ultima aula em 12 dias. Sugerir meta de 3 registros/semana."

> **O que e "Busca Ativa"?** E o protocolo de ir atras do aluno que esta faltando. O PEEX identifica quem, e o coordenador aciona familia + orientacao.

---

### Para o Professor (3 paginas)

| Pagina | O que mostra | Quando usar |
|--------|-------------|-------------|
| **Meu Espelho** | Seu score decomposto + comparativo anonimo + caminho de melhoria | A qualquer momento |
| **Minhas Turmas** | Conformidade e conteudo por turma | Para ver suas turmas |
| **Meu Progresso** | Evolucao semanal + conquistas desbloqueadas | Motivacao |

#### Como funciona o Score do Professor

| Componente | Peso | O que mede |
|-----------|------|------------|
| Registro | 35% | % de aulas registradas no SIGA |
| Conteudo | 25% | % de aulas com descricao de conteudo |
| Tarefa | 15% | % de aulas com tarefa/atividade |
| Recencia | 25% | Quao recente foi o ultimo registro |

> **O professor ve dados de colegas?** NUNCA. Ele ve: "Seu score: 68. Media da unidade: 72. Media da rede: 70." Sem nomes, sem ranking, sem exposicao.

> **O que sao "conquistas"?** Badges desbloqueados automaticamente. Exemplos: "Primeiro Passo" (1o registro), "Constante" (4 semanas seguidas), "Detalhista" (100% com conteudo), "Cobertura Total" (todas turmas registradas).

---

## 17. Os 6 Robos IA

Rodam automaticamente, sem precisar fazer nada:

| Robo | Quando roda | O que faz | Resultado |
|------|-------------|-----------|-----------|
| **VIGILIA** | 4x/dia (2h, 8h, 14h, 20h) | Detecta batalhas, gera scorecards | Batalhas atualizadas |
| **ESTRATEGISTA** | Domingo 22h | Narrativa CEO, 3 decisoes, heatmap | Briefing de segunda |
| **CONSELHEIRO** | Segunda 5h | Pauta da reuniao, perguntas, rituais | Pauta pronta |
| **COMPARADOR** | Segunda 5h30 | Estrelas, rankings, comparativo | Rankings atualizados |
| **PREDITOR** | Sexta 20h | Projeta tendencias, alertas preventivos | "Se continuar assim, em 3 semanas..." |
| **RETROALIMENTADOR** | A cada 6h | Verifica se acoes foram executadas | Escala se coordenador nao agiu |

> **Preciso ligar os robos?** Nao. Eles rodam sozinhos via scheduler (agendador automatico). Voce so ve os resultados nas paginas.

> **O PREDITOR realmente preve o futuro?** Ele usa tendencias recentes (ultimas 4+ semanas) para projetar o que pode acontecer. Nao e magica — e matematica simples (regressao linear). Serve como alerta, nao como certeza.

---

## 18. Metas SMART do Ano

| Eixo | Indicador | Inicio | Meta 1oTri | Meta 2oTri | Meta Ano |
|------|-----------|--------|------------|------------|----------|
| Conformidade | % media lancamento | 43.7% | 70% | 78% | 80% |
| Conformidade | Profs criticos | 41 | 20 | 10 | 5 |
| Conformidade | % profs ritmo SAE | 12.9% | 35% | 55% | 65% |
| Frequencia | % frequencia media | 84.7% | 88% | 89% | 90% |
| Frequencia | % alunos freq >90% | 54.1% | 65% | 72% | 78% |
| Frequencia | % alunos em risco | 18.4% | 15% | 12% | 10% |
| Desempenho | Media de notas | 8.3 | 8.0 | 8.0 | 8.0 |
| Clima | Ocorrencias graves | 53 | 26 | 13 | 20 |

> **O que e "SMART"?** Specific (especifico), Measurable (mensuravel), Achievable (alcancavel), Relevant (relevante), Time-bound (com prazo). Toda meta tem numero, fonte de dado e prazo.

---

## 19. Marcos do 1o Trimestre (checklist)

- [ ] Conformidade >= 70%
- [ ] 40+ feedbacks registrados
- [ ] Frequencia JG >= 85%
- [ ] CDR <= 4 ocorrencias graves/semana
- [ ] Todos os 41 professores criticos contatados
- [ ] Protocolo de Busca Ativa funcionando
- [ ] PMV enviado toda segunda sem falha

> **O que e PMV?** Painel de Monitoramento da Vigilia — o relatorio automatico que o robo VIGILIA gera. E enviado toda segunda de manha.

---

## 20. Fluxo Semanal Sugerido

### Segunda-feira (15 min)
1. Abra **Comando CEO** (ou **Prioridades**, se coordenador)
2. Leia a narrativa / veja as batalhas
3. Abra o **Plano de Acao** — confirme as acoes da semana
4. Prepare a pauta da reuniao no **PEEX Adaptativo**

### Terca a Quinta (5 min/dia)
1. Veja o **Ritmo Semanal** — quem registrou hoje?
2. Execute as acoes do plano
3. Atualize status: "em andamento" ou "resolvida"
4. Use **Meus Professores** para feedbacks individuais

### Sexta-feira (10 min)
1. Revise o **Espelho Coordenador** — como foi sua semana?
2. Celebre conquistas no **Feed de Polinizacao**
3. O PREDITOR gera projecoes para a proxima semana

### Antes de cada reuniao
1. Abra **PEEX Adaptativo** ou **PEEX Rede**
2. Revise a pauta gerada
3. Exporte **Briefing PDF** se quiser levar impresso
4. Adicione notas pessoais

---

## 21. Perguntas Frequentes

**P: Com que frequencia os dados atualizam?**
R: O robo VIGILIA roda 4x por dia. Os dados tem no maximo 6 horas de atraso.

**P: O professor pode ver dados de outros professores?**
R: Nao. So ve seus proprios dados e a media anonima.

**P: O que fazer quando uma batalha aparece como URGENTE?**
R: Agir no mesmo dia. Abra a batalha, leia a prescricao, execute a acao. Marque como "em andamento".

**P: Posso editar a pauta gerada?**
R: Sim. A pauta e sugestao. Adicione notas, ajuste e exporte.

**P: O que acontece se eu nao resolver uma batalha?**
R: Apos 2 semanas, escala. Nivel 1 → 2 → 3 → 4 (crise). O diretor e notificado.

**P: O simulador realmente preve o futuro?**
R: Estima impacto baseado em medias historicas. E apoio a decisao, nao certeza.

**P: Posso acessar pelo celular?**
R: Sim. O sistema e responsivo — cards empilham em tela pequena, botoes sao grandes o suficiente para toque.

**P: E se os dados do SIGA estiverem errados?**
R: O sistema reflete o que esta no SIGA. Se o professor registrou errado, o PEEX mostra errado. A qualidade dos dados depende da qualidade do registro.

---

## Links Relacionados

- [[PEEX 2026 - Plano Definitivo]] — Plano original com 45 reunioes
- [[PEEX 2026 - Sintese Final]] — Documento principal que combina todas as propostas

---

*Guia criado em 21/02/2026 — PEEX Command Center v1.0*
*22 paginas | 4 perfis | 6 robos IA | 9 tipos de batalha | 45 reunioes programadas*
