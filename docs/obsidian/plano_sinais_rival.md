# PLANO RIVAL — DECISÃO ANTES DO DADO
## Reuniões de Monitoramento por Dados | Colégio ELO | 2026
### 45 reuniões formais + Rituais Rápidos + Alertas Automatizados

---

> **Filosofia deste plano:** O melhor sistema de dados é aquele que as pessoas USAM, não o mais completo. Este plano prioriza DECISÃO sobre LEITURA. Cada reunião termina com uma lista de ações concretas e um responsável. Se não há ação, a reunião não deveria existir.

> **Princípio central:** Indicadores LEAD (que preveem) valem mais que indicadores LAG (que confirmam). Não esperamos a reunião para descobrir uma crise — o sistema avisa antes.

---

# SEÇÃO 1 — PARECER CRÍTICO DO PLANO EXISTENTE

## 1.1 Pontos Fortes (o que funciona e deve ser mantido)

O plano "Sinais e Redes" é um documento impressionante em profundidade e coerência. Reconheço os seguintes méritos:

**1. Estrutura de 5 eixos bem definida.** A divisão em Conformidade (A), Frequência (B), Desempenho (C), Clima (D) e Engajamento Digital (E) é lógica, cobre as dimensões essenciais e evita sobreposição conceitual. Cada eixo tem dashboards mapeados, indicadores claros e metas SMART. Isso é raro em escolas.

**2. Metas SMART com baseline real.** Usar dados da Semana 4 como baseline (conformidade 43,7%, frequência 84,7%, 14 alunos críticos, etc.) e projetar metas trimestrais e anuais é excelente prática. Muitos planos escolares definem metas sem saber de onde partem.

**3. Compromissos por unidade com prazo e evidência.** Cada reunião termina com uma tabela de compromissos que inclui responsável, prazo e evidência esperada. Isso é o mínimo para accountability e o plano entrega isso de forma consistente.

**4. Hipóteses e riscos nomeados.** A prática de formular 2 hipóteses e 2 riscos por reunião transforma a leitura de dados em investigação. Isso evita a leitura passiva de números.

**5. Uso inteligente do calendário escolar.** O plano identifica conflitos com eventos (Páscoa ELO, Jogos, São João, feriados) e propõe alternativas. Isso demonstra conhecimento operacional da escola.

**6. Cruzamentos temáticos.** As reuniões de cruzamento (A x C, B x D, D x E) no final de cada trimestre são sofisticadas e podem revelar correlações que análises isoladas perdem.

**7. Apêndices operacionais.** O protocolo de leitura de dados (Apêndice A), os semáforos (Apêndice C) e o mapeamento de coordenadores (Apêndice D) são recursos práticos que facilitam a execução.

---

## 1.2 Pontos Fracos (onde o plano falha ou arrisca falhar)

### FRAQUEZA 1: Síndrome do "Abrir Dashboard"
**Diagnóstico:** Cada reunião lista 3 a 5 dashboards para abrir. Em 45 reuniões, são mais de 150 aberturas de dashboard ao longo do ano. Isso cria dois problemas:
- **Dependência técnica:** Se o Streamlit cair, se o CSV estiver desatualizado, se a internet falhar — a reunião para. Não há Plano B.
- **Teatro de indicadores:** 15 minutos de "leitura ao vivo" com projetor pode virar um ritual de contemplação de números sem conexão com ação. O coordenador que não entende o dashboard fica passivo, esperando que alguém interprete para ele.

**Risco real:** A reunião T1-E1 pede para abrir 3 dashboards na semana de adaptação, quando a escola tem zero dados significativos. Abrir dashboard com dados vazios ensina os coordenadores que os painéis nem sempre são úteis — péssima primeira impressão.

### FRAQUEZA 2: Volume sem priorização
**Diagnóstico:** O plano trata todos os 5 eixos com peso igual a cada trimestre. São 3 passagens por eixo por trimestre (eixo puro + cruzamento + revisão). Mas os dados reais mostram que os problemas não são simétricos:
- JG tem crise de frequência (79,6%) — precisa de atenção semanal, não quinzenal.
- CDR tem crise de ocorrências graves (68% do total) — precisa de intervenção diária, não de esperar a reunião da semana 11.
- O Eixo E (SAE Digital) tem dados esparsos ("1.773 Sem Dados") — dedicar o mesmo tempo a ele que ao Eixo B é desproporcional.

**Risco real:** O coordenador de JG espera 2 semanas para discutir frequência enquanto alunos acumulam faltas todos os dias.

### FRAQUEZA 3: Reunião única serve para tudo
**Diagnóstico:** O formato é sempre 45 minutos = 15 (leitura) + 10 (diagnóstico) + 15 (ação) + 5 (compromissos). Mas uma reunião de abertura de trimestre tem necessidades diferentes de uma reunião de sprint de conformidade ou de um pré-conselho de classe. O formato rígido pode:
- Desperdiçar 15 min de leitura quando o dado já foi visto por todos via alerta automático.
- Comprimir a ação em 15 min quando o tema exige 30 min de planejamento.

### FRAQUEZA 4: Ausência de alertas automatizados
**Diagnóstico:** O plano depende 100% da reunião para que os coordenadores tomem conhecimento dos dados. Não há menção a:
- Notificações automáticas (WhatsApp, e-mail, Telegram) quando um indicador cruza o limiar vermelho.
- Relatórios automáticos semanais enviados antes da reunião para que todos cheguem preparados.
- Alertas em tempo real quando um aluno acumula X faltas consecutivas.

**Risco real:** Entre a reunião T1-03 (frequência, 11/fev) e a T1-09 (busca ativa, 25/mar), passam-se 6 semanas sem discussão formal de frequência. Nesse intervalo, um aluno com 3 faltas/semana acumula 18 faltas — quase 9% do limite anual.

### FRAQUEZA 5: Paralisia por profundidade
**Diagnóstico:** Algumas reuniões propõem análises que exigem nível de analista de dados, não de coordenador pedagógico:
- "Cruzar `score_Professor.csv` com `fato_Cruzamento.csv` (status de alinhamento)" — o coordenador sabe fazer isso?
- "Construir tabela por turma com pct_conformidade, frequencia_media e media_notas" — quem constrói? Na hora?
- "Calcular: para cada aluno com frequência atual X%, qual será a frequência no final do ano se o ritmo continuar?" — isso é uma projeção estatística.

**Risco real:** O coordenador que não domina dados fica dependente de Bruna Marinho para fazer todas as análises. Se ela não preparar antes, a reunião empaca. Bruna Marinho vira gargalo.

### FRAQUEZA 6: 45 reuniões podem ser demais
**Diagnóstico:** 45 quartas-feiras de 45-50 minutos = 34 horas do ano dedicadas apenas a leitura de dados. Para 9 coordenadores que já têm rotina pedagógica intensa, isso pode ser percebido como burocracia. O plano não diferencia:
- Semana normal (tudo estável) de semana de crise (indicador vermelho).
- Algumas reuniões poderiam ser substituídas por um "boletim semanal" escrito, lido em 5 minutos, com resposta assíncrona.

### FRAQUEZA 7: Falta protocolo de escalação
**Diagnóstico:** O plano define o que os coordenadores fazem, mas não define quando um problema escala para a direção. Não há resposta para:
- Se a conformidade cair 15pp em 2 semanas, quem a direção convoca?
- Se um aluno tier=3 não melhora após 4 semanas de intervenção, o que acontece?
- Se um professor crítico ignora 3 feedbacks seguidos, qual é o próximo passo?

### FRAQUEZA 8: O Tri 2 e Tri 3 são menos detalhados
**Diagnóstico:** O Tri 1 tem 15 reuniões minuciosamente detalhadas (pautas completas, ações por unidade, compromissos). A partir do Tri 2, as reuniões ficam progressivamente mais genéricas ("Ação por unidade: JG prioridade máxima"). Isso sugere que o plano foi escrito com energia decrescente ou que assume que o padrão do Tri 1 se replica automaticamente — o que raramente acontece.

---

## 1.3 Omissões Relevantes

| O que falta | Por que importa |
|-------------|-----------------|
| **Indicadores de retenção/matrícula** | O plano cita metas de matrícula (BV=1.250, CD=1.200, JG=850, CDR=800) mas não monitora cancelamentos semanais. Perder 5 alunos/mês por unidade = 240 alunos/ano = 12% de evasão. |
| **Indicadores de satisfação** | Nenhuma métrica de percepção de família ou aluno. Dados de ocorrência são proxy ruim para clima escolar. |
| **Indicador de carga do coordenador** | 563 alunos "Freq->Família" divididos por 9 coordenadores = 63 famílias para ligar por coordenador. Isso é viável? O plano não dimensiona a carga de trabalho gerada pelas intervenções. |
| **Plano de contingência técnico** | Se o Streamlit/SQLite/CSV corromper, qual é o plano B para a reunião? |
| **Formação dos coordenadores em dados** | Como garantir que todos entendam o dashboard? Treinamento está fora do plano. |
| **Indicadores de processo** | O plano mede resultados (conformidade, frequência) mas não mede o processo de gestão: % de compromissos cumpridos, tempo médio entre alerta e ação, taxa de resposta a feedbacks. |

---

## 1.4 Riscos Técnicos

| Risco | Probabilidade | Impacto | Mitigação proposta pelo plano |
|-------|--------------|---------|-------------------------------|
| Streamlit fora do ar na hora da reunião | Média | Alto (reunião perde a pauta) | Nenhuma |
| CSV desatualizado (extração não rodou) | Média | Alto (dados da semana passada) | Menciona "reexecutar extração" mas sem automação |
| Coordenador não sabe filtrar dashboard | Alta | Médio (fica passivo) | Apêndice A com passos, mas sem treinamento |
| `fato_Notas_2026` vazio até A1 (~março) | Certa | Médio (reunião C sem dados novos) | Usa histórico 2025 como proxy — bom |
| `fato_Engajamento_SAE` com poucos dados | Alta | Baixo (eixo E fica fraco) | Aceitável no Tri 1 |
| Bruna Marinho ausente/sobrecarregada | Média | Crítico (toda extração para) | Nenhuma — ponto único de falha |

---

# SEÇÃO 2 — PROPOSTA RIVAL: DECISÃO ANTES DO DADO

## 2.0 Filosofia de Gestão

O plano existente pergunta: "O que os dados dizem?"
Este plano pergunta: **"O que precisamos DECIDIR, e qual dado nos ajuda a decidir?"**

A diferença é sutil mas fundamental:
- No plano existente, a reunião começa abrindo o dashboard e lendo números.
- Neste plano, a reunião começa com a **pergunta da semana** e usa o dado apenas para responder.

### Os 3 Princípios

**Princípio 1: Dado é munição, não espetáculo.**
Ninguém precisa ver 5 dashboards para decidir que o professor João precisa de feedback. O coordenador precisa de UMA informação: "João lançou 12% das aulas esperadas esta semana." O resto é contexto opcional.

**Princípio 2: Alerta antes da reunião, ação na reunião.**
Toda informação crítica chega ao coordenador ANTES da reunião (via boletim semanal automático). A reunião é para DECIDIR o que fazer, não para DESCOBRIR o que aconteceu.

**Princípio 3: Simplicidade escala, complexidade para.**
Um coordenador que entende 3 números essenciais age melhor do que um que vê 15 indicadores e não sabe por onde começar.

---

## 2.1 Estrutura do Sistema

### 3 Camadas de Monitoramento

| Camada | Frequência | Quem participa | Duração | O que produz |
|--------|-----------|----------------|---------|-------------|
| **Camada 1: Alerta Automático** | Diário/contínuo | Sistema -> Coordenador | 0 min (push notification) | Notificação no WhatsApp/e-mail |
| **Camada 2: Ritual Rápido** | 2x por semana (seg+qui) | Coordenador + equipe da unidade | 10 min | 1 decisão por unidade |
| **Camada 3: Reunião Formal** | Semanal (quartas) | Todos coordenadores + gestão | 30-50 min (variável) | Lista de ações com prazo |

### Tipos de Reunião Formal (Camada 3)

| Tipo | Duração | Frequência | Quando usar |
|------|---------|-----------|-------------|
| **FLASH** | 30 min | Semanas normais (~28/ano) | Indicadores estáveis, sem vermelho |
| **FOCO** | 45 min | Semanas de atenção (~12/ano) | 1+ indicador amarelo, precisa de plano |
| **CRISE** | 60 min | Quando necessário (~3-5/ano) | Indicador vermelho confirmado, escalação |
| **ESTRATÉGICA** | 90 min | 3x/ano (abertura/meio/fim) | Fechamento de trimestre, planejamento |

**Diferença crucial:** O plano existente trata todas as 45 reuniões com o mesmo formato de 45 min. Este plano adapta a duração à gravidade da semana. Semana tranquila = 30 min. Semana de crise = 60 min. Isso respeita o tempo do coordenador e aumenta a intensidade quando necessário.

---

## 2.2 Os 7 Indicadores Essenciais (vs 15+ do plano existente)

Cada coordenador monitora no máximo 7 números por semana. São eles:

| # | Indicador | Fonte | O que responde | Lead/Lag |
|---|-----------|-------|---------------|----------|
| 1 | **Taxa de lançamento semanal** | `fato_Aulas.csv` | "Quantos % dos professores lançaram esta semana?" | LEAD |
| 2 | **Alunos ausentes hoje** | `fato_Frequencia_Aluno.csv` | "Quantos alunos faltaram hoje? Quais são reincidentes?" | LEAD |
| 3 | **Alunos no limiar de frequência** | `score_Aluno_ABC.csv` | "Quantos estão entre 75-80% e podem cair para reprovação?" | LEAD |
| 4 | **Ocorrências graves da semana** | `fato_Ocorrencias.csv` | "Quantas graves esta semana? Quem?" | LEAD |
| 5 | **Professores sem lançamento em 2+ semanas** | `score_Professor.csv` | "Quem sumiu do sistema?" | LEAD |
| 6 | **Gap de capítulo SAE** | `dim_Progressao_SAE.csv` | "Quantos professores estão 2+ capítulos atrás?" | LEAD |
| 7 | **Alunos tier 2/3 sem intervenção** | `score_Aluno_ABC.csv` | "Quantos alunos em risco sem ação registrada?" | LEAD |

**Nota:** Os indicadores LAG (notas, conformidade acumulada, frequência média) são importantes mas só entram nas reuniões ESTRATÉGICAS trimestrais. No dia a dia, o coordenador precisa de indicadores LEAD que permitem PREVENIR.

---

## 2.3 O Boletim Semanal de 1 Página (enviado antes da reunião)

Toda segunda-feira às 7h, cada coordenador recebe no WhatsApp/e-mail um boletim de 1 página com os 7 indicadores da sua unidade. Formato:

```
╔══════════════════════════════════════════════╗
║   BOLETIM SEMANAL — [UNIDADE] — Semana [N]  ║
╠══════════════════════════════════════════════╣
║                                              ║
║  LANÇAMENTOS ESTA SEMANA:  72% (↑ de 65%)   ║
║  ├─ Meta: 80%                                ║
║  └─ Professores zerados: João, Maria, Pedro  ║
║                                              ║
║  FREQUÊNCIA HOJE (segunda): 87%              ║
║  ├─ Alunos ausentes: 76 de 586              ║
║  └─ Reincidentes (3+ faltas seg): 12 nomes  ║
║                                              ║
║  ALUNOS NO LIMIAR (75-80%): 23 alunos       ║
║  ├─ Risco de reprovação se ritmo continuar   ║
║  └─ Top 5: [nomes]                          ║
║                                              ║
║  OCORRÊNCIAS GRAVES SEMANA: 2               ║
║  ├─ [Nome] — [tipo] — [data]                ║
║  └─ [Nome] — [tipo] — [data]                ║
║                                              ║
║  PROFESSORES SUMIDOS (2+ sem sem lançamento):║
║  └─ 3 professores: [nomes]                  ║
║                                              ║
║  GAP SAE: 4 professores 2+ caps atrás       ║
║  └─ [nomes e disciplinas]                   ║
║                                              ║
║  ALUNOS EM RISCO SEM AÇÃO: 8 alunos         ║
║  └─ Tier 2: 6 | Tier 3: 2 (ver lista)      ║
║                                              ║
║  VEREDICTO DA SEMANA: 🟡 ATENÇÃO            ║
║  Motivo: 3 professores sumidos + 2 graves    ║
║                                              ║
╚══════════════════════════════════════════════╝
```

**Por que isso muda o jogo:** O coordenador chega na reunião de quarta JÁ SABENDO o que aconteceu. A reunião gasta zero tempo lendo dados e 100% do tempo decidindo ações.

**Geração do boletim:** Script Python automático (`gerar_boletim_semanal.py`) que lê os CSVs e gera texto formatado. Bruna Marinho configura uma vez; roda sozinho via cron/agendador.

---

## 2.4 Rituais Rápidos (Camada 2)

### Ritual de Segunda — "Pulso" (10 min)
**Quando:** Toda segunda-feira, 7h30, logo após receber o boletim.
**Quem:** Coordenador + secretaria da unidade (presencial, na própria unidade).
**Pauta fixa:**
1. Ler o boletim semanal (2 min)
2. Há algum aluno tier 3 que precisa de ligação HOJE? (3 min)
3. Há algum professor que precisa de conversa HOJE? (3 min)
4. Registrar 1 ação no caderno/WhatsApp (2 min)

**Regra:** Se o boletim mostra tudo verde, o ritual de segunda é cancelado. Só acontece se houver amarelo ou vermelho.

### Ritual de Quinta — "Checkpoint" (10 min)
**Quando:** Toda quinta-feira, 15h.
**Quem:** Coordenador sozinho (autoavaliação).
**Pauta fixa:**
1. A ação de segunda foi cumprida? (Sim/Não)
2. Algum aluno novo entrou em risco esta semana?
3. Preciso levar algo para a reunião de quarta?

**Regra:** Não gera documento. É um momento de reflexão individual. O coordenador que não fizer, não é cobrado — mas aquele que fizer vai chegar mais preparado na quarta.

---

## 2.5 Calendário das 45 Reuniões Formais

### Convenções
- **[F]** = FLASH (30 min) — semana normal
- **[FO]** = FOCO (45 min) — atenção necessária
- **[C]** = CRISE (60 min) — se indicador vermelho (pode ser rebaixada para FOCO se tudo estável)
- **[E]** = ESTRATÉGICA (90 min) — abertura/fechamento de trimestre

### TRIMESTRE 1 — INSTALAR E CALIBRAR (27/jan - 10/mai, 15 reuniões)

**Tema:** Instalar o sistema, calibrar os alertas, primeiras intervenções. O Tri 1 é o trimestre da paciência informada — os dados estão nascendo, mas já podemos agir sobre frequência e conformidade.

---

#### R01 [E] — 28/jan — Semana 1 — INSTALAÇÃO DO SISTEMA
**Duração:** 90 min (única reunião de instalação do ano)
**Semana de adaptação — poucos dados, muito alinhamento.**

**Parte 1 — Treinamento Relâmpago (30 min):**
Cada coordenador recebe um notebook/tablet com o Streamlit aberto. Em vez de projetar na tela e ler, cada um navega por conta própria com um roteiro impresso:
1. Abra a página 01 (Quadro de Gestão). Encontre sua unidade. Qual o número de alunos?
2. Abra a página 13 (Semáforo Professor). Encontre um professor da sua unidade. Qual a classificação dele?
3. Abra a página 23 (Alerta Precoce). Encontre um aluno tier 2. Qual o nome?

**Regra:** Se o coordenador conseguir completar as 3 tarefas em 10 minutos, ele está pronto. Se não, precisa de tutoria individual na semana seguinte.

**Parte 2 — Contrato de Dados (20 min):**
Apresentar o Boletim Semanal de 1 Página (modelo impresso). Explicar:
- Toda segunda-feira às 7h vocês recebem isto no WhatsApp.
- Os 7 indicadores que vocês vão acompanhar o ano todo.
- O semáforo (verde/amarelo/vermelho) e o que cada cor significa para a sua unidade.

**Parte 3 — Diagnóstico Inicial por Unidade (30 min):**
Cada dupla/trio de coordenadores responde, usando os dados da semana 1:
- BV (Bruna Vitória + Gilberto): Quantos alunos matriculados? Quantos professores? Há novatos sem histórico 2025?
- CD (Alline + Elisângela + Vanessa): Mesmo exercício. CD é a maior unidade — atenção ao volume.
- JG (Lecinane + Pietro): O histórico de 2025 já mostra frequência problemática. Vocês sabem quais turmas?
- CDR (Ana Cláudia + Vanessa): 36 ocorrências graves em 2025 — são pendências documentais ou disciplinares reais?

**Parte 4 — Primeiros Compromissos (10 min):**

| Compromisso | Responsável | Prazo | Evidência |
|------------|------------|-------|-----------|
| Completar as 3 tarefas de navegação no Streamlit | Todos os coordenadores | 30/jan | Print ou confirmação verbal |
| Configurar recebimento do boletim semanal no WhatsApp | Bruna Marinho + coordenadores | 03/fev | Primeiro boletim recebido |
| CDR: classificar 36 ocorrências graves 2025 (documental vs disciplinar) | Ana Cláudia | 04/fev | Planilha classificada |
| JG: listar turmas com freq <80% em 2025 | Lecinane | 04/fev | Lista de turmas |

---

#### R02 [FO] — 04/fev — Semana 2 — CONFORMIDADE: PRIMEIROS SINAIS
**Pergunta da semana:** "Quantos professores lançaram ao menos 1 aula na semana 1? Quem não lançou?"

**Preparação (ANTES da reunião):** Boletim semanal enviado na segunda (02/fev). Os coordenadores chegam sabendo quais professores não lançaram.

**Pauta (45 min):**

*Decisão 1 (15 min): Professores zerados*
- Abrir lista de professores com zero lançamentos (do boletim). Não precisa de dashboard — a lista é suficiente.
- Para cada professor zerado: é desconhecimento do sistema ou resistência?
- Ação imediata: coordenador agenda conversa individual com cada professor zerado da sua unidade até sexta-feira.

*Decisão 2 (15 min): Protocolo de lançamento*
- CDR tem 54,6% de conformidade — melhor que as demais. O que CDR faz diferente?
- Ana Cláudia/Vanessa (CDR) apresentam em 5 minutos a rotina de cobrança que usam.
- As demais unidades decidem: vão adotar a mesma prática ou adaptá-la?

*Decisão 3 (10 min): Frequência precoce*
- Semana 2 — dados de frequência começam a aparecer. JG já mostra sinais? Algum aluno com 3+ faltas na primeira semana?
- Se sim: coordenador de JG (Lecinane) liga para a família HOJE, não espera a reunião de frequência.

*Compromissos (5 min):*

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Conversa individual com cada professor zerado | Cada coordenador | 07/fev |
| CDR: documentar rotina de cobrança (1 página) | Ana Cláudia | 07/fev |
| JG: ligar para famílias de alunos com 3+ faltas na semana 1 | Lecinane | 06/fev |

---

#### R03 [FO] — 11/fev — Semana 3 — FREQUÊNCIA: MAPA DE RISCO
**Pergunta da semana:** "Quais alunos estão faltando de forma reincidente? Quais turmas concentram as faltas?"

**Pauta (45 min):**

*Decisão 1 (20 min): Triagem de frequência por turma*
- O boletim mostra a frequência por unidade. Agora o drill-down: quais TURMAS puxam a média para baixo?
- JG (79,6%): Lecinane abre `20_Frequência_Escolar.py` filtrado por JG e identifica as 3 piores turmas.
- CD (83,6%): Alline faz o mesmo para CD.
- Resultado: cada coordenador sai com uma lista de no máximo 3 turmas prioritárias.

*Decisão 2 (15 min): Protocolo de busca ativa (criar agora)*
- 563 alunos com flag "Freq->Família" é inviável. Priorizar:
  - **Nível 1 (Urgente):** Alunos com <70% de frequência nas semanas 1-3 = ligação imediata do coordenador.
  - **Nível 2 (Atenção):** Alunos com 70-80% = mensagem padronizada via secretaria.
  - **Nível 3 (Monitorar):** Alunos com 80-90% = acompanhar no boletim, agir se piorar.
- Estimar volume: Nível 1 deve ter no máximo 30-50 alunos. Nível 2, ~150. Nível 3, ~350.
- Dividir ligações: cada coordenador fica com no máximo 5-8 ligações de Nível 1 por semana.

*Decisão 3 (5 min): Caso extremo*
- Camila Rangel (BV, 6o Ano, 42,9% de frequência) — 8 faltas em 4 semanas. Se o ritmo continuar, estará com menos de 30% em março.
- Bruna Vitória: reunião presencial com a família ATÉ sexta.

*Compromissos (5 min):*

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Escrever protocolo de busca ativa (3 níveis) | Lecinane (rascunho) + todos (revisão) | 14/fev |
| JG: identificar 3 turmas com pior frequência | Lecinane + Pietro | 13/fev |
| BV: reunião com família de Camila Rangel | Bruna Vitória | 14/fev |
| CD: listar alunos Nível 1 (<70% freq) | Alline | 13/fev |

---

#### R04 [F] — 18/fev — Semana 4 — CONFORMIDADE: CHECKPOINT
**Pergunta da semana:** "Os professores zerados da semana 2 lançaram algo? A conversa do coordenador funcionou?"

**Pauta (30 min — reunião FLASH):**

*Decisão única (20 min): Avaliação do impacto das conversas*
- Cada coordenador reporta: "Conversei com X professores zerados. Resultado: Y lançaram, Z ainda não."
- Para os que ainda não lançaram: a razão é técnica (não sabe usar o sistema) ou comportamental (não quer)?
  - Técnica: agendar tutoria individual (Bruna Marinho disponível para 15 min por professor).
  - Comportamental: registrar em `feedbacks_coordenacao.json` e definir prazo final (2 semanas).

*Próximos passos (10 min):*
- Confirmar baseline da Semana 4 (dados reais): conformidade, frequência, ocorrências, alunos por tier.
- Este é o ponto zero oficial do monitoramento.

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Tutoria individual para professores com dificuldade técnica | Bruna Marinho | 25/fev |
| Registrar feedback formal para professores que recusam lançar | Cada coordenador | 25/fev |

---

#### R05 [FO] — 25/fev — Semana 5 — OCORRÊNCIAS: CDR EM FOCO + ENCONTRO FAMÍLIAS
**Pergunta da semana:** "CDR tem 36 ocorrências graves — concentram-se em quais alunos? O que estamos fazendo?"

**Contexto:** Dia do Encontro com Famílias — oportunidade de ouro para ação imediata.

**Pauta (45 min):**

*Decisão 1 (20 min): Anatomia das 36 graves de CDR*
- Ana Cláudia apresenta a classificação das 36 ocorrências (compromisso da R01):
  - Quantas envolvem o mesmo aluno? (concentração vs dispersão)
  - Quantas são violência/bullying vs indisciplina "comum"?
  - Existe padrão de horário/dia/turma?
- Definir: os 5 alunos com mais ocorrências graves de CDR terão reunião com família HOJE (Encontro com Famílias).

*Decisão 2 (15 min): Ocorrências nas outras unidades*
- BV tem 11 graves — são os mesmos alunos que estão com frequência baixa?
- JG tem 4 graves — baixo volume, mas cruzar com a frequência problemática.
- CD tem 2 graves — exemplar. O que fazem diferente?

*Decisão 3 (10 min): Script para o Encontro com Famílias*
- Coordenadores preparam fala para famílias de alunos com ocorrências: direta, empática, baseada em dados.
- Modelo: "Seu filho teve [N] registros de [tipo] este ano. Gostaríamos de construir um plano juntos para melhorar isso."

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| CDR: reunião com 5 famílias de alunos com mais graves | Ana Cláudia + Vanessa | 25/fev (hoje) |
| Meta CDR: máximo 4 ocorrências graves/semana a partir de agora | Ana Cláudia | Contínuo |
| BV: cruzar 11 graves com frequência dos mesmos alunos | Bruna Vitória | 28/fev |

---

#### R06 [F] — 04/mar — Semana 6 — PROGRESSÃO SAE + ENGAJAMENTO DIGITAL
**Pergunta da semana:** "Estamos no capítulo certo? Os alunos estão acessando o SAE?"

**Pauta (30 min — FLASH):**

*Decisão 1 (15 min): Capítulo esperado vs real*
- Semana 6 = capítulo esperado 2. Quantos professores estão no capítulo 2? Quantos no 1 ainda? Quantos no 0?
- Professores com capítulo 0 na semana 6 = NÃO estão usando o SAE. Entram na lista de prioridade.
- Ação: coordenador pergunta ao professor — "Você sabe qual capítulo deveria estar trabalhando?"

*Decisão 2 (15 min): Engajamento SAE dos alunos*
- `fato_Engajamento_SAE.csv`: quantos alunos acessaram a plataforma? Quantos fizeram exercícios?
- Se <30% dos alunos acessaram: o problema é de acesso (login não funciona) ou de uso (ninguém cobrou)?
- Ação prática: cada coordenador escolhe 1 turma-piloto para verificar login e acesso SAE na próxima semana.

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Verificar acesso SAE de 1 turma-piloto por unidade | Cada coordenador | 11/mar |
| Orientar professores sobre capítulo esperado (cap 2) | Cada coordenador | 11/mar |

---

#### R07 [FO] — 11/mar — Semana 7 — SPRINT DE CONFORMIDADE
**Pergunta da semana:** "Quantos dos 25 professores críticos (meta) já saíram do vermelho? Quantos restam?"

**Pauta (45 min):**

*Decisão 1 (25 min): Revisão professor a professor dos críticos*
- Na semana 4, havia 25 professores críticos (confirmados após baseline). Listar:
  - BV: 10 críticos — quantos receberam feedback? Quantos melhoraram?
  - CD: 6 críticos — status?
  - JG: 6 críticos — status?
  - CDR: 3 críticos — meta: zero até fim de março.
- Para cada professor que permanece crítico: o que muda agora? Intensificar feedback? Conversa de gestão?

*Decisão 2 (15 min): Correlação feedback-melhoria*
- Dos professores que receberam feedback, quantos melhoraram conformidade em 2+ semanas?
- Se a correlação é baixa: o feedback não está funcionando. Precisamos mudar a abordagem.
- Se a correlação é alta: mais feedbacks = mais melhoria. Aumentar ritmo.

*Compromissos (5 min):*

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Feedback registrado em JSON para TODOS os críticos restantes | Cada coordenador | 18/mar |
| CDR: plano individual para os 3 (ou menos) críticos restantes | Ana Cláudia | 18/mar |
| Coordenadores com <5 feedbacks registrados: meta de +5 até 18/mar | Todos | 18/mar |

---

#### R08 [E] — 18/mar — Semana 8 — REVISÃO DE MEIO DE TRIMESTRE
**Tipo:** ESTRATÉGICA (90 min)
**Pergunta da semana:** "Estamos no caminho para atingir as metas do Tri 1? O que precisa mudar?"

**Parte 1 — Painel Comparativo (20 min):**

| Indicador | Baseline (Sem 4) | Meta Tri 1 | Atual (Sem 8) | Tendência |
|-----------|-----------------|-----------|---------------|-----------|
| Conformidade média | 43,7% | 60% | ? | ↑↓→ |
| Professores críticos | 25 (confirmados) | ≤15 | ? | ↑↓→ |
| Frequência média | 84,7% | 87% | ? | ↑↓→ |
| Alunos limiar (<80%) | ~370 | ≤250 | ? | ↑↓→ |
| Graves CDR/semana | ~9 | ≤4 | ? | ↑↓→ |
| Feedbacks dados | 1 | ≥25 | ? | ↑↓→ |
| Compromissos cumpridos (7 reuniões) | — | ≥70% | ? | — |

**Nota importante:** Indicador novo — "Compromissos cumpridos". Auditar: das ações combinadas nas reuniões R01 a R07, quantas foram efetivamente realizadas? Se a taxa é <50%, o problema não é de dados — é de execução.

**Parte 2 — Diagnóstico por Unidade (30 min, 7 min cada):**
Cada coordenador apresenta em 7 minutos:
1. O que melhorou na minha unidade (com dado).
2. O que piorou (com dado).
3. O que estou fazendo diferente nas próximas 7 semanas.

**Parte 3 — Recalibrar Metas (20 min):**
- Se a conformidade está em 48% na semana 8, a meta de 60% no final do Tri 1 é viável? (Precisa subir 12pp em 7 semanas = ~1,7pp/semana. Possível se mantiver ritmo.)
- Se a frequência de JG ainda está <80%, considerar plano emergencial específico para JG (ver Seção 3: Escalação).

**Parte 4 — Plano de 7 Semanas até o Fechamento (20 min):**
Cada coordenador sai com 3 ações priorizadas para as próximas 7 semanas. Não mais que 3. Foco.

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Documento "Plano 7 semanas" de cada unidade (1 página) | Cada coordenador | 25/mar |
| Reexecutar extração completa após A1 | Bruna Marinho | Pós-A1 |
| Auditoria de compromissos das 7 primeiras reuniões | Bruna Marinho | 25/mar |

---

#### R09 [FO] — 25/mar — Semana 9 — FREQUÊNCIA: BUSCA ATIVA EM ESCALA
**Pergunta da semana:** "O protocolo de busca ativa de 3 níveis está funcionando? Quantas famílias foram contatadas?"

**Pauta (45 min):**

*Decisão 1 (20 min): Auditoria da busca ativa*
- Na R03, criamos o protocolo de 3 níveis. 6 semanas depois: quantos contatos foram feitos?
  - Nível 1 (Urgente, <70%): esperava-se 30-50 alunos. Quantos foram contatados? Resultado?
  - Nível 2 (Atenção, 70-80%): esperava-se ~150 mensagens. Foram enviadas?
  - Nível 3 (Monitorar, 80-90%): estão sendo acompanhados nos boletins?
- Se o volume é inviável: reduzir para Nível 1 apenas. Melhor ligar para 30 com qualidade do que mandar 500 mensagens genéricas.

*Decisão 2 (15 min): Tendência de frequência — 9 semanas de dados*
- Com 9 semanas, já dá para ver tendência. A frequência está subindo, estável ou caindo por unidade?
- JG: se continua <80% após 9 semanas de intervenção, escalar para direção (ver Protocolo de Escalação, Seção 3).

*Decisão 3 (10 min): Previsão de reprovação por falta*
- Alunos com <70% de frequência na semana 9: se mantiverem o ritmo, estarão com <65% no final do ano. São candidatos a reprovação por falta.
- Quantos são? Lista nominal para cada coordenador.

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Relatório de busca ativa: contatos feitos e resultados | Cada coordenador | 01/abr |
| JG: se freq <80% → escalar para direção com relatório de dados | Lecinane + Bruna Marinho | 01/abr |
| Lista de alunos em risco de reprovação por falta | Bruna Marinho (extração) | 28/mar |

---

#### R10 [FO] — 01/abr — Semana 10 — DESEMPENHO: PRIMEIRAS NOTAS (PÓS-A1)
**Pergunta da semana:** "As notas da A1 confirmam ou desmentem os riscos que os indicadores LEAD apontavam?"

**Nota:** Páscoa ELO nesta semana — confirmar horário. Se inviável, remarcar para 02/abr.

**Pauta (45 min):**

*Decisão 1 (20 min): Leitura das notas A1*
- Se `fato_Notas_2026` já foi extraído: média A1 por unidade e disciplina.
- Os 14 alunos tier 3 (Crítico) do ABC — confirmados pelas notas? Ou as notas revelam novos riscos?
- Cruzar: alunos com frequência baixa + nota baixa na A1 = candidatos a intervenção DUPLA.

*Decisão 2 (15 min): Candidatos a reforço*
- Cada coordenador identifica 5 alunos da sua unidade que precisam de reforço ANTES da A2.
- Disciplinas mais críticas: provavelmente Matemática e Língua Portuguesa (maior carga horária = maior peso).

*Decisão 3 (10 min): Progressão SAE semana 10*
- Capítulo esperado: 3. Quantos professores estão alinhados?
- Professores com capítulo 1 ou 0 na semana 10 = estão perdendo o currículo. Intervenção urgente.

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Lista de 5 alunos para reforço por unidade (20 total) | Cada coordenador | 08/abr |
| Reextrair `fato_Notas_2026` se não feito ainda | Bruna Marinho | 03/abr |
| Contato com professores com capítulo <2 na semana 10 | Cada coordenador | 08/abr |

---

#### R11 [F] — 08/abr — Semana 11 — OCORRÊNCIAS: TENDÊNCIA
**Pergunta da semana:** "As graves de CDR estão caindo? As intervenções funcionaram?"

**Pauta (30 min — FLASH):**

*Decisão única (20 min):*
- CDR: acumulado de graves nas semanas 5-11 vs semanas 1-4. Ritmo caiu?
  - Se sim: documentar o que funcionou (para replicar).
  - Se não: escalar para direção (ver Protocolo de Escalação).
- Outras unidades: tendência de ocorrências gerais. Atrasos (212 acumulados na sem 4) — estão crescendo ou estabilizando?
- Alunos "Comportamento->Orientação" (57 na sem 4): quantos receberam orientação de fato?

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| CDR: relatório de tendência de graves para a direção | Ana Cláudia | 15/abr |
| Cada unidade: status dos alunos "Comportamento->Orientação" | Cada coordenador | 15/abr |

---

#### R12 [F] — 15/abr — Semana 12 — SAE: BASELINE CONFIRMADO
**Pergunta da semana:** "Qual é o nosso baseline real de engajamento SAE após 12 semanas?"

**Pauta (30 min — FLASH):**

*Decisão 1 (15 min):*
- `fato_Cruzamento.csv`: % de "Alinhado" vs "Sem Dados" — este é o baseline real.
- Se >70% ainda é "Sem Dados": o cruzamento SIGA x SAE não está gerando valor. Considerar simplificar o monitoramento do Eixo E (menos reuniões, mais diagnóstico de causa-raiz).

*Decisão 2 (15 min):*
- Engajamento médio dos alunos no SAE (`pct_exercicios`). Se <20%: o problema é de ADOÇÃO, não de monitoramento.
- Ação prática: cada coordenador verifica em 1 turma se os alunos sabem que o SAE existe e como acessar.

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Diagnóstico de adoção SAE: alunos sabem acessar? (1 turma por unidade) | Cada coordenador | 22/abr |
| Definir: o Eixo E merece reunião dedicada ou vira item de pauta nas reuniões gerais? | Gestão | 22/abr |

---

#### R13 [FO] — 22/abr — Semana 13 — CRUZAMENTO: PROFESSOR x RESULTADO
**Pergunta da semana:** "Existe evidência de que professor com melhor conformidade tem alunos com melhores resultados?"

**Nota:** Jogos ELO nesta semana — confirmar horário.

**Pauta (45 min):**

*Análise principal (30 min):*
- Bruna Marinho prepara ANTES da reunião uma tabela simples (impressa):
  | Professor | Conformidade | Turma | Freq média turma | Nota média A1 |
  |-----------|-------------|-------|-----------------|---------------|
  (Top 10 melhores e 10 piores em conformidade)
- O grupo analisa: os alunos dos professores excelentes estão melhor? Pior? Sem diferença?
- Se SIM (correlação): a conformidade é uma CAUSA, não só um indicador. Intensificar.
- Se NÃO (sem correlação): a conformidade mede burocracia, não qualidade. Repensar o indicador.

*Próximos passos (15 min):*
- Definir se a conformidade continua como indicador #1 ou se precisa ser complementada com indicador de qualidade (ex: conteúdo do lançamento, não apenas se lançou).

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Tabela professor x resultado (preparada antes da reunião) | Bruna Marinho | 20/abr |
| Revisão do conceito de conformidade se sem correlação | Gestão + Bruna Marinho | 29/abr |

---

#### R14 [FO] — 29/abr — Semana 14 — CRUZAMENTO: FREQUÊNCIA x COMPORTAMENTO
**Pergunta da semana:** "Os alunos que mais faltam são os mesmos que mais geram ocorrências? O padrão atraso->indisciplina->falta é real?"

**Pauta (45 min):**

*Análise principal (25 min):*
- Bruna Marinho prepara tabela cruzada (antes da reunião):
  | Aluno | Freq % | Ocorr graves | Ocorr leves | Tier ABC | Intervenção feita? |
  (Apenas alunos com flag_A="Risco" OU ocorr_graves > 0)
- Verificar H1: 80% dos alunos com ocorrência grave também têm freq <85%?
- Se confirmado: criar "Protocolo Duplo" — intervenção simultânea de frequência E comportamento para estes alunos.

*Definição do Protocolo Duplo (20 min):*
- Aluno com risco de freq + ocorrência grave = reunião com família + plano individualizado + acompanhamento semanal por 4 semanas.
- Volume estimado: 20-30 alunos em toda a rede. Cada coordenador fica com 2-5 casos.
- É viável? Se não: priorizar os 10 mais graves.

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Tabela cruzada freq x comportamento (antes da reunião) | Bruna Marinho | 27/abr |
| "Protocolo Duplo" escrito (1 página) | Lecinane (rascunho, validado por todos) | 06/mai |
| Identificar os 10 alunos prioritários para Protocolo Duplo | Cada coordenador: 2-3 nomes | 06/mai |

---

#### R15 [E] — 06/mai — Semana 15 — FECHAMENTO DO I TRIMESTRE
**Tipo:** ESTRATÉGICA (90 min)
**Pergunta da semana:** "O que conseguimos no Tri 1? O que falhou? O que muda no Tri 2?"

**Parte 1 — Resultados vs Metas (25 min):**

| Indicador | Baseline (Sem 4) | Meta Tri 1 | Realizado | Veredicto |
|-----------|-----------------|-----------|-----------|-----------|
| Conformidade média | 43,7% | 60% | ? | Atingiu / Não atingiu |
| Professores críticos | 25 | ≤15 | ? | ↑↓→ |
| Frequência média | 84,7% | 87% | ? | ↑↓→ |
| Alunos limiar (<80%) | ~370 | ≤250 | ? | ↑↓→ |
| Graves CDR/semana | ~9 | ≤4 | ? | ↑↓→ |
| Feedbacks dados | 1 | ≥25 | ? | ↑↓→ |
| Compromissos cumpridos | — | ≥70% | ? | — |
| Busca ativa: contatos feitos | 0 | ≥80% Nível 1 | ? | — |

**Parte 2 — Retrospectiva (25 min):**
Cada coordenador responde (3 min cada, total 27 min para 9 coordenadores):
1. "A reunião/ritual que mais me ajudou foi..."
2. "O indicador que mais me ajudou a tomar decisão foi..."
3. "O que eu mudaria para o Tri 2 é..."

**Parte 3 — Calibrar Metas Tri 2 (20 min):**
Ajustar metas com base no realizado. Se a conformidade atingiu 55% (não 60%), a meta do Tri 2 é 65% (não 70%). Metas inalcançáveis desmotivam.

**Parte 4 — Reformulação (20 min):**
- Algum ritual/reunião deve ser eliminado?
- O boletim semanal está sendo lido? Útil? Precisa mudar?
- O Eixo E (SAE) merece reunião própria no Tri 2 ou vira item de pauta?

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Relatório de fechamento Tri 1 (1 página por eixo + resumo) | Bruna Marinho | 13/mai |
| Cada coordenador: autoavaliação de 1 parágrafo | Todos | 13/mai |
| Metas SMART revisadas para Tri 2 (documento final) | Gestão + Bruna Marinho | 13/mai |

---

### TRIMESTRE 2 — RASTREAR E INTENSIFICAR (11/mai - 12/set, 15 reuniões)

**Tema:** Os dados já são robustos. O sistema está calibrado. Agora o foco é rastrear o impacto das intervenções e intensificar onde não funcionou. Férias em julho (sem 23-27) = usar 2 quartas de julho para planejamento.

---

#### R16 [E] — 13/mai — Semana 16 — ABERTURA DO II TRIMESTRE
**Tipo:** ESTRATÉGICA (90 min)

**Parte 1 (30 min): Painel de abertura com metas revisadas**
- Ler os resultados finais do Tri 1 (relatório de Bruna Marinho).
- Apresentar metas recalibradas do Tri 2.
- Identificar os alunos que mudaram de tier entre Tri 1 e início Tri 2 (melhoraram? pioraram?).

**Parte 2 (30 min): Novos dados disponíveis**
- `fato_Notas_2026` agora tem A1+A2 do Tri 1. Pela primeira vez temos notas reais.
- Quais alunos reprovaram a A1 E a A2? Estes são os de maior risco no ano.
- Quais disciplinas têm as menores médias?

**Parte 3 (30 min): Planejamento de 18 semanas**
- O Tri 2 inclui férias (sem 23-27). Planejamento real: 13 semanas de aula + 5 de férias.
- Cada coordenador define seus 3 focos para o Tri 2 (máximo 3 — disciplina é importante).
- Definir: usar 2 quartas de julho para reuniões de planejamento do retorno? (Recomendo sim.)

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Metas SMART Tri 2 aprovadas | Gestão | 15/mai |
| Cada coordenador: 3 focos do Tri 2 (1 parágrafo) | Todos | 20/mai |
| Atualizar boletim semanal com notas A1+A2 Tri 1 | Bruna Marinho | 20/mai |

---

#### R17 [FO] — 20/mai — Sem 17 — EVASÃO SILENCIOSA + FREQUÊNCIA
**Pergunta:** "Algum aluno que estava no Tri 1 não apareceu no Tri 2?"
- Cruzar dim_Alunos com chamada da semana 16-17. Ausentes sem justificativa = contato imediato.
- JG: a frequência subiu no Tri 2 ou estagnou? Se estagnou = problema estrutural (não é de intervenção pontual).

#### R18 [FO] — 27/mai — Sem 18 — CONFORMIDADE MEIO DE ANO
**Pergunta:** "Na metade do ano letivo, a conformidade está na trajetória para 70%?"
- Evolução semanal da conformidade. Se <55%: intervenção extraordinária (ver Escalação).
- Feedbacks acumulados: quantos dos 107 professores já receberam ao menos 1?

#### R19 [F] — 03/jun — Sem 19 — NOTAS A1 TRI 2 (PRIMEIROS SINAIS)
**Pergunta:** "As notas A1 do Tri 2 estão melhores ou piores que as do Tri 1?"
- Capítulo esperado: 5-6. Gap de progressão SAE.
- Alunos que reprovaram A1 em ambos os trimestres = risco crítico no ano.

#### R20 [FO] — 10/jun — Sem 20 — CLIMA PRÉ-FÉRIAS
**Pergunta:** "O clima está piorando com a proximidade das férias? Atrasos e indisciplina subiram?"
- Tendência de ocorrências semanas 18-20 vs 1-5. Padrão sazonal?
- CDR: meta de ≤4 graves/semana — está sendo cumprida após 20 semanas?

#### R21 [F] — 17/jun — Sem 21 — ENGAJAMENTO SAE + BALANÇO DIGITAL
**Nota:** São João ELO — confirmar horário.
**Pergunta:** "O engajamento SAE cresceu ou ficou no mesmo patamar do Tri 1?"
- Se estagnou: o Eixo E passa a ser item de pauta (3 min) e não reunião própria no Tri 3.
- Se cresceu: investigar o que impulsionou (cobrança do professor? turma-piloto?).

#### R22 [FO] — 24/jun — Sem 22 — SNAPSHOT PRÉ-FÉRIAS
**Pergunta:** "Que alunos precisam de acompanhamento DURANTE as férias?"
- Lista de alunos tier 2/3 que podem evadir nas férias.
- Cada coordenador sai com no máximo 5 nomes para ligar durante julho.
- Compromisso: cada coordenador faz 1 contato por semana durante as férias (5 ligações total).

#### R23 [F] — 08/jul — Sem 24 (FÉRIAS) — PLANEJAMENTO DO RETORNO
**Reunião durante férias — comum em escolas privadas. Opcional, mas recomendada.**
**Pergunta:** "O que precisa estar pronto na semana do retorno?"
- Planejar a semana 28 (retorno): protocolo de acolhimento, verificação de evasão, checklist de dados.
- 30 minutos bastam. Pode ser por videoconferência.

#### R24 [F] — 15/jul — Sem 25 (FÉRIAS) — METAS DO TRI 3
**Também durante férias — pode ser videoconferência.**
**Pergunta:** "Quais são as metas realistas para o último trimestre?"
- Com 33 semanas de dados, projetar: quais metas anuais são alcançáveis e quais precisam ser revisadas?

#### R25 [FO] — 05/ago — Sem 28 — RETORNO DAS FÉRIAS: EVASÃO
**Pergunta crítica:** "Quantos alunos NÃO voltaram?"
- Comparar presença semana 22 (antes das férias) com semana 28 (retorno).
- Alunos ausentes por 3+ dias consecutivos = contato imediato.
- Meta de matrícula: BV=1.250, CD=1.200, JG=850, CDR=800. Quantos ativos HOJE?
- JG: monitoramento diário na semana do retorno.

#### R26 [FO] — 12/ago — Sem 29 — CONFORMIDADE: SPRINT FINAL TRI 2
**Pergunta:** "Faltam 4 semanas. A conformidade atinge 70%?"
- Sprint: lista dos 20 piores professores em conformidade. Plano de 3 semanas para cada.
- Professores que receberam 3+ feedbacks e não melhoraram → escalar para direção.

#### R27 [FO] — 19/ago — Sem 30 — POSIÇÃO DO ALUNO NO ANO
**Pergunta:** "Qual é a projeção de aprovação/reprovação de cada aluno?"
- Com notas de Tri 1 + A1 Tri 2: projetar nota final.
- Alunos com projeção <5 em 2+ disciplinas: candidatos a conselho de classe.
- Priorizar os 20 alunos mais críticos da rede.

#### R28 [F] — 26/ago — Sem 31 — OCORRÊNCIAS: PADRÃO ANUAL
**Pergunta:** "Com 31 semanas de dados, existe um padrão sazonal nas ocorrências?"
- Picos de ocorrência: quais semanas do ano? Pré-férias? Retorno?
- Alunos reincidentes (>3 graves no ano): quantos são? Precisam de relatório para conselho.

#### R29 [FO] — 02/set — Sem 32 — CRUZAMENTO: PROFESSOR x PLATAFORMA
**Nota:** Feriado Paulista (JG). JG participa remotamente.
**Pergunta:** "Professores com melhor conformidade SIGA também usam melhor o SAE?"
- Se sim: a conformidade é proxy de engajamento pedagógico geral. Bom sinal.
- Se não: são competências distintas. Tratar separadamente.

#### R30 [E] — 09/set — Sem 33 — FECHAMENTO DO II TRIMESTRE
**Tipo:** ESTRATÉGICA (90 min)
**Mesmo formato da R15 — adaptado para Tri 2.**
- Resultados vs Metas Tri 2.
- Retrospectiva dos coordenadores.
- Metas calibradas para o Tri 3 (último trimestre).
- Decisão: o Tri 3 é o trimestre do FECHAMENTO — quais alunos são prioridade absoluta?

---

### TRIMESTRE 3 — FECHAR E PROJETAR (14/set - 18/dez, 15 reuniões)

**Tema:** Convergência. Todos os dados do ano estão disponíveis. As decisões são sobre resultados finais: aprovação, reprovação, renovação de matrícula, avaliação de professores, planejamento 2027.

---

#### R31 [E] — 16/set — Sem 34 — ABERTURA DO III TRIMESTRE: RISCO DE FECHAMENTO
**Tipo:** ESTRATÉGICA (90 min)
**Foco:** Identificar os 3 maiores riscos de fechamento do ano.
- Alunos em risco de reprovação por nota (projeção <5).
- Alunos em risco de reprovação por falta (projeção <75%).
- Professores que não concluirão o currículo SAE (capítulo <9 na semana 34).
- Metas SMART para o Tri 3 (últimas metas do ano).

#### R32 [FO] — 23/set — Sem 35 — CONFORMIDADE: SPRINT FINAL DO ANO
**Pergunta:** "Quais professores AINDA estão críticos após 35 semanas? Por quê?"
- Professores críticos por 30+ semanas: o problema é capacidade ou motivação?
- Capacidade → formação imediata (Bruna Marinho oferece tutoria).
- Motivação → conversa de desempenho com direção (Escalação Nível 3).

#### R33 [FO] — 30/set — Sem 36 — PROJEÇÃO FINAL DE FREQUÊNCIA
**Pergunta:** "Quantos alunos serão reprovados por falta se o ritmo atual continuar?"
- Cálculo: para cada aluno com freq atual X%, projetar freq final.
- "Ponto de não retorno": alunos que, mesmo com 100% de presença até dezembro, ficam <75%.
- Ação: protocolo de reclassificação ou recurso (atestados, justificativas).

#### R34 [FO] — 07/out — Sem 37 — MAPA DE APROVAÇÃO
**Pergunta:** "Quais alunos precisam de quanto em cada disciplina para passar?"
- Projeção de nota final: com A1+A2 de Tri 1 e 2, + A1 Tri 3, calcular nota mínima necessária na A2 Tri 3.
- Turmas com maior % projetado de reprovação.
- Priorizar candidatos a recuperação.

#### R35 [F] — 14/out — Sem 38 — OCORRÊNCIAS: FECHAMENTO DISCIPLINAR
**Pergunta:** "Quais alunos terão relatório disciplinar no conselho de classe?"
- Top 10 alunos com mais ocorrências no ano.
- CDR: balanço anual de ocorrências graves vs meta.
- Preparar relatório individualizado para o conselho.

#### R36 [F] — 21/out — Sem 39 — SAE: AVALIAÇÃO FINAL DO ANO
**Pergunta:** "O SAE Digital valeu o investimento? Os dados mostram impacto?"
- Cruzar engajamento SAE com notas finais projetadas. Correlação?
- Se sim: expandir SAE em 2027. Se não: reavaliar investimento.
- Quais disciplinas fecharam os 12 capítulos? Quais ficaram para trás?

#### R37 [FO] — 28/out — Sem 40 — CRUZAMENTO TRIPLO: CONFORMIDADE x FREQ x NOTAS
**A grande análise do ano.**
- Tabela por turma: conformidade do professor x frequência x notas dos alunos.
- Hipótese final: a conformidade explica os resultados? Ou é só burocracia?
- Resultado alimenta a decisão sobre manter/reformular o indicador em 2027.

#### R38 [FO] — 04/nov — Sem 41 — EFICÁCIA DAS INTERVENÇÕES
**Pergunta:** "As intervenções do ano (busca ativa, feedbacks, protocolo duplo) funcionaram?"
- Alunos que receberam busca ativa: tier na sem 4 vs tier na sem 41. Melhoraram?
- Professores que receberam feedback: conformidade antes vs depois.
- Se a intervenção funcionou: manter em 2027. Se não: mudar abordagem.

#### R39 [FO] — 11/nov — Sem 42 — FEEDBACKS: META 100%
**Pergunta:** "Todos os 107 professores receberam ao menos 1 feedback registrado?"
- Professores "invisíveis" (zero feedback no ano): quem são? Por que passaram despercebidos?
- Plano de 5 semanas para cobrir os que faltam.
- Meta: 107/107 até 16/dez.

#### R40 [E] — 18/nov — Sem 43 — PRÉ-CONSELHO DE CLASSE
**Tipo:** ESTRATÉGICA (90 min) — Preparação para o Conselho de Classe

**Esta é a reunião mais operacional do ano.** Output: lista consolidada de alunos para o conselho.

Para cada aluno com risco de reprovação:
- Nota projetada por disciplina (com nota mínima necessária na A2 Tri 3).
- Frequência projetada final.
- Histórico de intervenções no ano (feedbacks, contatos, protocolo duplo).
- Recomendação: aprovação / recuperação / reprovação.
- Dados impressos em ficha individual para o conselho.

| Compromisso | Responsável | Prazo |
|------------|------------|-------|
| Fichas individuais dos alunos em risco (impressas) | Bruna Marinho + coordenadores | 24/nov |
| Lista final de alunos para o conselho de classe | Cada coordenador | 24/nov |

#### R41 [C] — 25/nov — Sem 44 — ÚLTIMAS INTERVENÇÕES (URGENTE)
**Tipo:** CRISE (60 min) — se houver alunos no limiar. FLASH (30 min) se não.
**Pergunta:** "Faltam 3 semanas. Quem ainda pode ser salvo?"
- Alunos com frequência 73-75% (podem passar se não faltarem mais).
- Alunos com nota 4,5-5,0 (podem passar com a A2 Tri 3 ou recuperação).
- Para cada: plano cirúrgico de 3 semanas (contato diário com família + reforço intensivo).

#### R42 [F] — 02/dez — Sem 45 — CRUZAMENTO FINAL: CLIMA x DIGITAL
**Pergunta:** "Alunos com melhor engajamento SAE têm menos ocorrências?"
- Se correlação positiva: argumento para expandir SAE em 2027.
- Última reunião de análise do ano. A partir daqui, é só fechamento.

#### R43 [FO] — 09/dez — Sem 46 — PROJEÇÃO FINAL + RECUPERAÇÃO
**Nota:** Semana de recuperação do Tri 3.
**Pergunta:** "Quais são os números definitivos (ou quase) do ano?"
- Frequência <75% (reprovação por falta — definitivo).
- Notas <5 após recuperação (reprovação por nota — quase definitivo).
- Preparar dados para o relatório anual.

#### R44 [FO] — 16/dez — Sem 47 — RESULTADO FINAL + AVALIAÇÃO DO ANO
**Tipo:** ESTRATÉGICA expandida (120 min) — última reunião do ano.

**Parte 1 (30 min): Resultados Finais vs Metas Anuais**

| Indicador | Baseline (Sem 4) | Meta Anual | Realizado 2026 | Delta |
|-----------|-----------------|-----------|----------------|-------|
| Conformidade média | 43,7% | 75% | ? | ? |
| Professores críticos | 25 | ≤10 | ? | ? |
| Feedbacks dados | 1/107 | 107/107 | ? | ? |
| Frequência média | 84,7% | ≥90% | ? | ? |
| Alunos freq >90% | 54,1% | 78% | ? | ? |
| Alunos Verde (ABC) | 69,2% | 85%+ | ? | ? |
| Alunos reprovados | — | ≤3% | ? | ? |
| Graves CDR total | 36 (acumulado sem 4) | ≤20 no ano | ? | ? |
| Cruzamentos SAE ativos | ~0% | 80%+ | ? | ? |
| Compromissos cumpridos (45 reuniões) | — | ≥75% | ? | ? |

**Parte 2 (30 min): O que funcionou / O que não funcionou**
Para cada eixo: 1 vitória + 1 fracasso, ambos com dados.
Para o sistema de monitoramento: O boletim semanal foi útil? Os rituais rápidos funcionaram? As reuniões FLASH foram suficientes ou precisavam de mais tempo?

**Parte 3 (30 min): Avaliação do Coordenador**
Cada coordenador recebe seu "relatório do ano":
- Quantos feedbacks deu?
- Quantas intervenções de busca ativa fez?
- Quantos compromissos de reunião cumpriu?
- Como os indicadores da sua unidade evoluíram de janeiro a dezembro?

**Parte 4 (30 min): Planejamento 2027**
- Novas metas SMART (a partir dos resultados de 2026).
- O que muda no sistema de monitoramento (mais Flash? menos reuniões? outro formato?).
- Investimentos: novos dashboards, automações, treinamentos.
- Decisão sobre o SAE Digital 2027.

#### R45 [RESERVA] — Data flexível — REUNIÃO DE CONTINGÊNCIA
**Usada apenas se alguma quarta-feira foi cancelada por evento/feriado ao longo do ano.** Se não usada, vira uma reunião de "retrospectiva livre" na última semana de aula.

---

# SEÇÃO 3 — SISTEMA DE ALERTAS E ESCALAÇÃO

## 3.1 Alertas Automatizados (Camada 1)

Alertas que não dependem de reunião. Funcionam via script automático + notificação no WhatsApp/e-mail do coordenador.

### Alertas Diários (verificados todo dia útil às 19h)

| # | Alerta | Condição | Destinatário | Ação esperada |
|---|--------|----------|-------------|---------------|
| A1 | **Aluno 3+ faltas consecutivas** | 3 dias seguidos sem presença registrada | Coordenador da turma | Ligar para família no dia seguinte |
| A2 | **Professor sem lançamento em 5+ dias úteis** | Nenhum registro em `fato_Aulas` nos últimos 5 dias | Coordenador da unidade | Conversa com o professor na manhã seguinte |
| A3 | **Ocorrência grave registrada** | Qualquer entrada com gravidade="Grave" em `fato_Ocorrencias` | Coordenador da unidade + Direção | Ciência imediata; ação conforme gravidade |

### Alertas Semanais (verificados toda segunda às 7h, no boletim)

| # | Alerta | Condição | Destinatário | Ação esperada |
|---|--------|----------|-------------|---------------|
| A4 | **Turma com freq <80% na semana** | Média de presença da turma <80% na semana anterior | Coordenador da turma | Investigar causa; contato com representante de turma |
| A5 | **Professor com conformidade <30%** | `pct_conformidade` <30% acumulado | Coordenador da unidade | Feedback registrado obrigatório |
| A6 | **Aluno mudou para tier 3 (Crítico)** | Tier ABC mudou de 2 para 3 | Coordenador da turma | Reunião com família em até 5 dias úteis |
| A7 | **CDR: >4 graves na semana** | Contagem de graves CDR na semana >4 | Ana Cláudia + Direção | Análise imediata; plano de ação em 48h |

### Alertas Mensais (verificados na primeira segunda do mês)

| # | Alerta | Condição | Destinatário | Ação esperada |
|---|--------|----------|-------------|---------------|
| A8 | **Gap SAE >2 capítulos** | Professor 2+ capítulos atrás do esperado | Coordenador | Conversa sobre ritmo de progressão |
| A9 | **Evasão silenciosa** | Aluno presente no `dim_Alunos` mas sem presença em 15+ dias | Coordenador + Secretaria | Contato com família; verificar status de matrícula |
| A10 | **Conformidade geral <meta-10pp** | Conformidade da rede 10+ pontos percentuais abaixo da meta do trimestre | Direção + Todos coordenadores | Reunião CRISE na próxima quarta |

### Implementação Técnica dos Alertas

```
Script: alertas_automaticos.py
Localização: /Users/brunaviegas/siga_extrator/power_bi/
Dependências: score_Aluno_ABC.csv, score_Professor.csv, fato_Ocorrencias.csv, fato_Aulas.csv
Execução: cron diário 19h (alertas diários) + cron segunda 6h (alertas semanais)
Saída: mensagem formatada enviada via API WhatsApp Business ou Telegram Bot
Fallback: se API falhar, gera arquivo .txt e envia por e-mail
```

**Plano B quando o Streamlit cai:**
- Os alertas não dependem do Streamlit — leem diretamente os CSVs.
- O boletim semanal também não depende do Streamlit — é gerado por script independente.
- Se o Streamlit cair na hora da reunião: o coordenador já tem o boletim semanal em mãos. A reunião acontece com base no boletim impresso + CSVs abertos no Excel/Google Sheets.
- Bruna Marinho mantém um backup dos CSVs no Google Drive (atualizado semanalmente). Qualquer coordenador pode acessar pelo celular.

---

## 3.2 Protocolo de Escalação

### Quando o problema sai do coordenador e vai para a direção?

| Nível | Quando escalar | Quem escala | Para quem | O que a direção faz |
|-------|---------------|-------------|-----------|---------------------|
| **Nível 1 — Informar** | Indicador amarelo por 2+ semanas seguidas | Coordenador | Direção (por e-mail/WhatsApp) | Toma ciência. Nenhuma ação imediata. |
| **Nível 2 — Pedir apoio** | Indicador vermelho confirmado OU coordenador sem capacidade de resolver sozinho | Coordenador + Bruna Marinho | Direção (reunião de 15 min) | Direção participa da próxima reunião FOCO para definir ação conjunta. |
| **Nível 3 — Intervenção direta** | Professor crítico após 3+ feedbacks sem melhora OU aluno tier 3 sem melhora após 4 semanas de intervenção OU freq de unidade <75% por 3+ semanas | Coordenador + Bruna Marinho (com relatório de dados) | Direção (reunião formal de 30 min) | Direção assume: conversa de desempenho com professor / reunião com família do aluno / plano de crise para unidade. |
| **Nível 4 — Crise institucional** | Evasão >5% em qualquer unidade no mês OU incidente grave (violência, risco à segurança) OU conformidade geral <30% | Direção (acionada automaticamente pelo alerta A10 ou pelo coordenador) | Gestão executiva / Mantenedora | Reunião extraordinária. Plano de crise em 48h. Possível comunicação aos pais. |

### Fluxo Visual de Escalação

```
INDICADOR AMARELO → Coordenador monitora (2 semanas)
          ↓ (não melhorou)
INDICADOR VERMELHO → Coordenador + Bruna Marinho preparam relatório
          ↓ (relatório pronto)
REUNIÃO COM DIREÇÃO (15-30 min) → Direção decide ação
          ↓ (ação definida)
ACOMPANHAMENTO SEMANAL → Volta para verde/amarelo?
          ↓ (não)
INTERVENÇÃO DIRETA DA DIREÇÃO → Conversa formal / plano de crise
```

### Regras de Ouro da Escalação

1. **Nunca escalar sem dado.** O coordenador que escala deve trazer o número, o período, a tendência e o que já tentou.
2. **Nunca escalar por desconforto, só por evidência.** "Eu acho que o professor João não está bem" não é escalação. "O professor João tem 15% de conformidade há 6 semanas e não respondeu a 3 feedbacks" é escalação.
3. **A direção não resolve — a direção decide.** O papel da direção na escalação é DECIDIR (manter, intensificar, mudar abordagem, desligar), não executar. A execução volta para o coordenador com o respaldo da decisão.
4. **Escalar é sinal de maturidade, não de fraqueza.** O coordenador que escala está reconhecendo os limites da sua autoridade. O que NÃO escala e o problema piora é pior.

---

## 3.3 Gatilhos Específicos por Unidade

| Unidade | Gatilho de escalação imediata | Motivo |
|---------|------------------------------|--------|
| **JG** | Frequência semanal <75% | JG já tem a pior frequência da rede (79,6%). Abaixo de 75% é crise. |
| **CDR** | >6 ocorrências graves em 1 semana | CDR concentra 68% das graves. >6/semana indica descontrole. |
| **BV** | >5 professores críticos sem feedback em 2+ semanas | BV tem o maior volume de profs críticos (10). Sem feedback = sem gestão. |
| **CD** | Evasão >3 alunos/semana | CD é a maior unidade (622 alunos). Evasão silenciosa é o maior risco. |

---

# SEÇÃO 4 — PAINEL MÍNIMO VIÁVEL (O QUE CADA COORDENADOR VÊ TODA SEMANA)

## 4.1 Filosofia do Painel Mínimo

O plano existente propõe abrir 3-5 dashboards por reunião (150+ aberturas no ano). Este plano propõe o oposto: **1 página que substitui 15 minutos de navegação em dashboards**.

O Painel Mínimo Viável (PMV) é gerado automaticamente, enviado antes da reunião, e contém apenas o que o coordenador PRECISA saber para DECIDIR naquela semana. Não é um dashboard interativo — é uma folha de papel (ou PDF) que pode ser impressa e lida em 3 minutos.

**Regra:** Se o coordenador precisa abrir o Streamlit para entender o PMV, o PMV falhou.

---

## 4.2 Layout do Painel Mínimo Viável (1 página A4)

```
┌─────────────────────────────────────────────────────────────────────┐
│                 COLÉGIO ELO — [UNIDADE] — SEMANA [N]               │
│                     [Data] | Trimestre [N] | [Tema]                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ╔═══════════════════════════════════════════════════════════╗      │
│  ║  VEREDICTO DA SEMANA:  🟢 VERDE  /  🟡 ATENÇÃO  /  🔴 CRISE  ║ │
│  ╚═══════════════════════════════════════════════════════════╝      │
│                                                                     │
│  ┌──────────────── PROFESSORES ────────────────────────┐           │
│  │ Lançaram esta semana: ██████████░░ 72% (meta: 80%)  │           │
│  │ Zerados (nada lançado): 4 profs → João, Maria...    │           │
│  │ Críticos persistentes: 3 profs (>4 sem sem lançar)  │           │
│  │ Feedbacks dados este mês: 8/[total profs unidade]   │           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                     │
│  ┌──────────────── ALUNOS ─────────────────────────────┐           │
│  │ Frequência da semana: 88,2% (meta: 90%)  ↑ de 86%  │           │
│  │ Faltaram 3+ dias esta semana: 12 alunos → [nomes]  │           │
│  │ No limiar (73-80%): 18 alunos → [top 5 nomes]      │           │
│  │ Tier 3 (Crítico): 2 alunos → Carlos 6ºA, Ana 8ºB   │           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                     │
│  ┌──────────────── OCORRÊNCIAS ────────────────────────┐           │
│  │ Total da semana: 23 (Leves:18 | Médias:4 | Graves:1)│           │
│  │ Grave: Pedro Silva, 7ºA — Agressão — 12/mar        │           │
│  │ Reincidentes (3+ no mês): Lucas 8ºB (5x), Ana 6ºA  │           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                     │
│  ┌──────────────── PROGRESSÃO SAE ─────────────────────┐           │
│  │ Capítulo esperado: 4 | Profs alinhados: 65%         │           │
│  │ Atrasados 2+ caps: 3 profs → [nomes e disciplinas]  │           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                     │
│  ┌──────────────── AÇÕES PENDENTES ────────────────────┐           │
│  │ ⬜ Ligar para família de Carlos (tier 3) — prazo 14/mar│        │
│  │ ⬜ Feedback para prof. João (crítico) — prazo 15/mar │           │
│  │ ✅ Reunião com família de Ana — feita 10/mar        │           │
│  │ ⬜ Verificar acesso SAE turma 7ºB — prazo 18/mar    │           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                     │
│  ┌──────────────── COMPARATIVO COM A REDE ─────────────┐           │
│  │        BV     CD     JG     CDR   |  REDE           │           │
│  │ Conf:  52%    48%    50%    58%   |  52%             │           │
│  │ Freq:  89%    85%    80%    86%   |  85%             │           │
│  │ Grav:   1      0      0      3   |   4              │           │
│  │        ▲      ▲      ▼      ▲   |                   │           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                     │
│  Próxima reunião: Quarta [data] — Tipo: [FLASH/FOCO/CRISE]        │
│  Pergunta da semana: "[pergunta que será discutida]"               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4.3 Especificação Técnica do PMV

### Geração
- **Script:** `gerar_pmv_semanal.py`
- **Inputs:** `score_Professor.csv`, `score_Aluno_ABC.csv`, `fato_Ocorrencias.csv`, `dim_Progressao_SAE.csv`, `fato_Aulas.csv`
- **Output:** 4 PDFs (1 por unidade) + 1 PDF consolidado (rede)
- **Execução:** Toda segunda-feira às 6h (antes do boletim WhatsApp das 7h)
- **Distribuição:** PDF enviado por e-mail e WhatsApp; versão impressa disponível na sala dos coordenadores

### Lógica do Veredicto Semanal

```python
def calcular_veredicto(indicadores_unidade):
    vermelhos = 0
    amarelos = 0

    # Frequência
    if indicadores_unidade['freq_semanal'] < 80:
        vermelhos += 1
    elif indicadores_unidade['freq_semanal'] < 85:
        amarelos += 1

    # Conformidade
    if indicadores_unidade['conformidade'] < meta_trimestre - 15:
        vermelhos += 1
    elif indicadores_unidade['conformidade'] < meta_trimestre - 5:
        amarelos += 1

    # Ocorrências graves
    if indicadores_unidade['graves_semana'] > 4:
        vermelhos += 1
    elif indicadores_unidade['graves_semana'] > 2:
        amarelos += 1

    # Alunos tier 3 sem intervenção
    if indicadores_unidade['tier3_sem_acao'] > 0:
        amarelos += 1
    if indicadores_unidade['tier3_sem_acao'] > 3:
        vermelhos += 1

    if vermelhos >= 1:
        return "CRISE"
    elif amarelos >= 2:
        return "ATENÇÃO"
    else:
        return "VERDE"
```

### Frequência de Atualização dos Dados

| Dado | Atualização | Responsável | Fallback se não atualizar |
|------|------------|-------------|---------------------------|
| `fato_Aulas.csv` | Automática diária (extração SIGA) | Script automatizado | Usar último CSV disponível |
| `score_Professor.csv` | Semanal (sexta à noite) | Script + revisão Bruna Marinho | Usar semana anterior |
| `score_Aluno_ABC.csv` | Semanal (sexta à noite) | Script + revisão Bruna Marinho | Usar semana anterior |
| `fato_Ocorrencias.csv` | Automática diária (extração SIGA) | Script automatizado | Usar último CSV disponível |
| `dim_Progressao_SAE.csv` | Mensal | Bruna Marinho | Usar mês anterior |
| `fato_Notas_2026` | Por avaliação (6x/ano) | Bruna Marinho | Sem fallback — dado crítico |

---

## 4.4 O que o PMV substitui (e o que NÃO substitui)

### O PMV SUBSTITUI:
- Os 15 minutos de "leitura ao vivo" de dashboards no início da reunião.
- A necessidade de projetar o Streamlit na reunião (o PMV já traz os números).
- A dependência do Streamlit para que a reunião funcione.
- A ansiedade do coordenador que não sabe navegar no dashboard.

### O PMV NÃO SUBSTITUI:
- O drill-down quando um indicador precisa de investigação profunda (ex: "quais turmas puxam a frequência de JG para baixo?"). Para isso, abrir o Streamlit na reunião — mas só quando necessário, não como ritual obrigatório.
- A análise de cruzamento trimestral (reuniões ESTRATÉGICAS). Essas precisam de tabelas preparadas por Bruna Marinho.
- O `feedbacks_coordenacao.json` como registro de ações.

---

## 4.5 Treinamento dos Coordenadores

### Sessão Única de Treinamento (90 min — antes da R01 ou integrado à R01)

| Módulo | Duração | Conteúdo |
|--------|---------|----------|
| **Leitura do PMV** | 20 min | Como ler o Painel Mínimo Viável. Exercício: "Olhe o PMV da semana passada de outra unidade. O que você faria como coordenador?" |
| **Navegação no Streamlit** | 30 min | As 3 tarefas básicas: encontrar professor, encontrar aluno, encontrar turma. Cada coordenador faz no seu computador/tablet. |
| **Registro de feedback** | 20 min | Como preencher o `feedbacks_coordenacao.json`. Demonstração + prática com caso fictício. |
| **Protocolo de escalação** | 20 min | Quando escalar? Como escalar? O que trazer? Simulação de 2 cenários. |

**Material de apoio:** Cartão plastificado (tamanho A5) com:
- Frente: "Os 7 indicadores que eu acompanho" (com semáforos e limiares)
- Verso: "Protocolo de escalação" (4 níveis resumidos)

O coordenador mantém o cartão na mesa. Consulta quando precisar. Não precisa decorar.

---

# RESUMO EXECUTIVO — POR QUE ESTE PLANO É DIFERENTE

| Aspecto | Plano Existente ("Sinais e Redes") | Este Plano ("Decisão Antes do Dado") |
|---------|-----------------------------------|--------------------------------------|
| **Filosofia** | "O que os dados dizem?" | "O que precisamos decidir?" |
| **Frequência de informação** | Quinzenal (na reunião) | Contínua (alertas) + diária (rituais) + semanal (reunião) |
| **Dependência do Streamlit** | Total (reunião depende do dashboard aberto) | Parcial (PMV funciona sem Streamlit) |
| **Formato de reunião** | Fixo (45 min, sempre) | Variável (30-90 min, conforme gravidade) |
| **Indicadores por coordenador** | 15+ (todos os eixos) | 7 essenciais (com drill-down sob demanda) |
| **Linguagem dos indicadores** | Técnica ("pct_conformidade", "tier ABC") | Simples ("Quantos professores lançaram?", "Quantos alunos faltaram?") |
| **Alertas automatizados** | Nenhum | 10 alertas (3 diários, 4 semanais, 3 mensais) |
| **Protocolo de escalação** | Mencionado no Apêndice C (4 critérios genéricos) | Protocolo completo com 4 níveis, gatilhos por unidade, regras de ouro |
| **Plano B (Streamlit cai)** | Nenhum | Boletim impresso + CSVs no Google Drive + Excel |
| **Formação do coordenador** | Apêndice A (roteiro escrito) | Sessão prática de 90 min + cartão plastificado de referência |
| **Priorização de crises** | Todas unidades tratadas igual | JG (frequência), CDR (ocorrências), BV (volume de profs) com gatilhos específicos |
| **O que cada reunião produz** | Lista de compromissos | Lista de DECISÕES com responsável e prazo |
| **Meta de compromissos cumpridos** | Não medida | Meta explícita: ≥75% de cumprimento |

---

## Nota Final

Este plano não pretende substituir integralmente o "Sinais e Redes". O plano existente tem méritos significativos — especialmente as metas SMART, os cruzamentos de eixos e o mapeamento detalhado de dashboards. O que este plano rival oferece é uma **camada de operacionalidade** que transforma a leitura de dados em decisão e ação.

O ideal seria uma fusão: a profundidade analítica do plano existente com a simplicidade operacional deste. O melhor plano não é o mais completo — é o que os coordenadores realmente usam, toda semana, sem precisar de ajuda para interpretar.

**O dado que não vira decisão é desperdício. A reunião que não vira ação é teatro.**

---

*Documento gerado em 21/02/2026.*
*Dados de referência: mesma base do plano existente — `resumo_Executivo.csv` (Semana 4), `score_Aluno_ABC.csv` (2.021 alunos), `score_Professor.csv` (107 professores), `fato_Ocorrencias.csv` (5.894 registros).*
*Infraestrutura: Streamlit (23 páginas pedagógicas) + Power BI (DAX v2.3) + CSVs em `/siga_extrator/power_bi/` + Alertas automatizados (novo) + PMV semanal (novo).*
