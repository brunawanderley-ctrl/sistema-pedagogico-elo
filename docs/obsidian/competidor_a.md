# COMPETIDOR A — PROPOSTA PEDS 2026
## Colégio ELO | Sistema de Excelência Pedagógica por Segmento
### Foco: Anos Finais (6º-9º) e Ensino Médio (1ª-3ª Série) | Dashboard 26 Páginas | Dados Reais Semana 4

> **Premissa desta proposta:** O Plano Definitivo é o melhor documento já produzido para o ELO. Esta proposta não o descarta — ela resolve o que o plano deixou incompleto: a **diferenciação por segmento** (Anos Finais vs. EM), o **mapeamento operacional do dashboard de 26 páginas**, e **cinco mecanismos inovadores** que o plano simplesmente não tem.

> **O que esta proposta faz diferente:** Trata 6º-9º Ano e 1ª-3ª EM como escolas distintas dentro da mesma escola. Mapeia cada uma das 26 páginas do Streamlit para cada tipo de reunião. Propõe intervenções específicas que os dados da Semana 4 exigem e que o Plano Definitivo não respondeu com granularidade suficiente.

---

# PARTE 1 — DIAGNÓSTICO POR SEGMENTO

## 1.1 Anos Finais (6º-9º Ano) — O Que os Dados Revelam

### Perfil do Segmento
Os Anos Finais concentram a maior parte dos alunos ELO. Nas 4 unidades, os alunos do 6º ao 9º Ano compõem aproximadamente 65-70% do total (estimativa: ~1.310 alunos), com professores de disciplinas especializadas — diferente dos Anos Iniciais onde um único professor comanda a turma. Isso cria uma **fragmentação natural de responsabilidade**: nenhum professor "dono" de turma, cada um vendo os alunos 1-5 vezes por semana.

### Problemas Específicos dos Anos Finais

**1. Conformidade abaixo de 40% é estruturalmente ligada ao volume de registros esperados.**
Um professor de Matemática com 5 turmas de 6º-9º Ano precisa registrar 5 diários por dia útil. Se o SIGA exige preenchimento manual sem auto-preenchimento, isso soma 25 registros semanais. Com 43,7% de conformidade geral — e considerando que os Anos Finais têm mais professores por turma — o gargalo de lançamento é maior neste segmento do que no EM.

**2. 78% dos professores no Q2 ("Registra Pouco") é um problema de rotina, não de resistência.**
A classificação Q2 (baixa conformidade, não zero) indica professores que tentam, mas não sustentam. Isso é diferente do professor que recusa. A intervenção para Q2 é de **simplificação do processo**, não de pressão. A proposta aqui diverge do Plano Definitivo: o foco deve ser em reduzir fricção antes de aumentar cobrança.

**3. JG com 25% em risco e 79,6% de frequência concentra principalmente os Anos Finais.**
A evasão gradual no Brasil começa exatamente no 6º Ano — ruptura com o ciclo de alfabetização, múltiplos professores, disciplinas abstratas. JG precisa de uma intervenção desenhada para o 6º e 7º Ano especificamente, não para o segmento todo.

**4. CDR com 36 ocorrências graves (68% da rede) está distribuída em pouquíssimas turmas.**
36 ocorrências graves em 4 semanas, na menor unidade da rede (357 alunos), aponta para concentração: provavelmente 3-5 turmas respondem por 80%+ desses registros. Identificar as turmas e os alunos reincidentes é a ação mais urgente do segmento — e o dashboard tem a ferramenta exata para isso (`22_Ocorrencias.py`).

**5. 12,9% dos professores no ritmo SAE = quase ninguém está alinhado curriculamente.**
Em Semana 4, o capítulo esperado é o 1. Com 12,9% no ritmo, a maioria dos professores ainda nem começou a usar o SAE ativamente. Isso não é problema de alinhamento — é problema de adoção. A hipótese: professores de Anos Finais, especialmente nas disciplinas com 4-5 aulas/semana (Português e Matemática), têm mais material SAE para administrar e mais resistência ao currículo externo.

### Padrões nos Anos Finais

**Padrão A — Professores de disciplinas "menores" (Arte, Filosofia, Ed. Física) têm conformidade sistematicamente menor.**
Com apenas 1-2 aulas por semana, o professor de Arte visita cada turma uma vez. O SIGA fica "esquecido" porque não há rotina diária que force o acesso. Intervenção diferente: configurar alerta semanal personalizado para esses professores, não cobrança diária.

**Padrão B — O 9º Ano é o elo entre os segmentos.**
O 9º Ano de Anos Finais já tem perfil parcialmente adolescente — mais ocorrências, mais faltas voluntárias, mais pressão por preparação para o EM. Em BV (Bruna Vitória cuida de 6º-9º), há uma oportunidade de criar uma "passagem pedagógica" formal entre o 9º Ano e a 1ª Série que o plano atual toca apenas superficialmente.

**Padrão C — 528 alunos flagados "Freq→Família" são majoritariamente dos Anos Finais.**
Adolescentes do 6º-9º Ano desenvolvem padrões de evasão gradual que os pais não percebem até ser tarde. A estratégia de contato familiar para esse perfil é diferente do EM — pais de alunos de Anos Finais ainda têm alta responsabilidade legal e emocional; pais de alunos de EM já tendem a dar mais autonomia.

### Oportunidades nos Anos Finais

**Oportunidade 1 — Dashboard como espelho de turma.**
As páginas `19_Painel_Aluno.py` a `26_Dashboard_Unificado.py` permitem que o coordenador veja, turma a turma, o panorama completo. Para os Anos Finais, onde cada professor não tem visão sistêmica, o coordenador pode usar o dashboard para criar um **"mapa de saúde de turma"** que os professores conselheiros recebem mensalmente.

**Oportunidade 2 — Alinhamento SAE no 6º-7º Ano como laboratório.**
O 6º Ano é onde o SAE tem maior potencial de impacto — alunos ainda formando hábitos de estudo, material estruturado, professores com 3 aulas/semana (volume gerenciável). Criar um piloto de alinhamento SAE focado nas turmas de 6º Ano de BV ou CD pode gerar dados de impacto que justificam expansão.

**Oportunidade 3 — Bruna Vitória (BV) como referência de modelo.**
BV tem a maior conformidade (39,5%) e a melhor frequência (90,2%) da rede, apesar de ser a maior unidade. Bruna Vitória como coordenadora de 6º-9º tem perfil para ser a "professora dos coordenadores" — o modelo que os outros aprendem visitando.

---

## 1.2 Ensino Médio (1ª-3ª Série) — O Que os Dados Revelam

### Perfil do Segmento
O EM no ELO representa aproximadamente 30-35% dos alunos (estimativa: ~710 alunos). Mas concentra desafios únicos:
- SSA (Sistema de Seleção Avaliativa) para 3ª Série: pressão por preparação para vestibular/ENEM
- Alunos mais maduros com maior agência sobre presença e engajamento
- Coordenação em BV separada (Gilberto Santos cuida exclusivamente do EM)
- O EM do ELO é TEEN 2: 9º Ano + 1ª, 2ª e 3ª EM compartilham material SAE

### Problemas Específicos do EM

**1. O EM é o segmento mais invisível nos dados.**
O Plano Definitivo menciona "SSA para 3ª Série EM" uma vez (Semana 35). Não há qualquer análise de desempenho específica por série do EM, nenhuma proposta de diferenciação entre 1ª, 2ª e 3ª Série, nenhum reconhecimento de que um coordenador que cuida só do EM (Gilberto em BV) tem um trabalho radicalmente diferente de quem cuida de 6º-9º Ano.

**2. Conformidade baixa no EM pode ter causa diferente.**
Professores de EM frequentemente são mais especializados e mais resistentes a "supervisão pedagógica". Um professor de Física do 3º Ano com 20 anos de experiência pode entender o SIGA como burocracia, não como ferramenta pedagógica. A abordagem de "sentar junto e registrar" funciona para o 6º Ano; para o EM, a entrada precisa ser pelo **resultado do aluno**, não pelo processo do professor.

**3. A pressão por ENEM/vestibular cria conflito com o currículo SAE.**
Com 12,9% dos professores no ritmo SAE, e sendo o EM o segmento com maior pressão externa por resultado de prova, professores de 3ª Série provavelmente pulam ou compactam capítulos para "dar o conteúdo do ENEM". Isso não é resistência — é racionalidade mal informada. O SAE tem alinhamento com ENEM; a tarefa é mostrar isso, não cobrar.

**4. Gilberto Santos (BV/EM) aparece zero vezes no Plano Definitivo.**
O coordenador de Ensino Médio da maior unidade da rede é completamente invisível no plano. Ele não tem roteiro diferenciado, não tem metas específicas para o segmento, não tem reuniões pensadas para as particularidades do EM. Esta proposta corrige isso.

**5. Alunos de EM têm padrão de frequência diferente.**
Faltas no EM frequentemente são estratégicas — aluno que calculou quantas faltas pode ter sem reprovar. O limiar legal de 75% de presença mínima é mais bem conhecido por alunos do EM do que do 6º Ano. O mecanismo de alerta precisa considerar isso: alunos com exatamente 76-80% de presença no EM são **deliberadamente beirando o limite**, o que exige conversa diferente da que se tem com um aluno de 7º Ano que simplesmente faltou.

### Padrões no EM

**Padrão D — A 3ª Série EM precisa de protocolo próprio de acompanhamento acadêmico.**
Com SSA e ENEM, o 3º Ano tem pressão de resultado que nenhuma outra série tem. O boletim narrativo (previsto para piloto no II Tri) precisa ter versão especial para o 3º Ano — mais focado em competências ENEM, menos em descritores do currículo regular.

**Padrão E — Professores de EM frequentemente ministram aulas em múltiplas unidades.**
Um professor de Biologia pode dar aulas em BV e CD. Seu registro de conformidade aparece fragmentado nas duas unidades. O Plano Definitivo não menciona isso. O dashboard precisa de uma visão "por professor" que consolide todas as suas turmas, independente de unidade.

**Padrão F — O EM tem o mais alto potencial de cruzamento SIGA×SAE.**
Alunos do EM no SAE Digital têm acesso a trilhas de estudo, simulados ENEM, banco de questões. O cruzamento entre engajamento SAE (fato_Engajamento_SAE.csv) e desempenho em avaliações (fato_Notas_Historico.csv) é especialmente poderoso para o 3º Ano: qual aluno está usando o SAE Digital e correlaciona com melhores notas?

### Oportunidades no EM

**Oportunidade 4 — Simulados como momento de análise pedagógica.**
Os sábados letivos de 22/08 e 29/08 são simulados. Para o EM, esses simulados são o momento mais rico de dados do ano: o que os alunos sabem, o que não sabem, onde o currículo precisa de reforço. O Plano Definitivo menciona os simulados mas não propõe uma metodologia de análise pedagógica — apenas "analise os resultados".

**Oportunidade 5 — Gilberto Santos como especialista de EM para a rede.**
Se BV é a unidade referência de Anos Finais (Bruna Vitória), BV pode ser também a referência de EM com Gilberto como modelo. Um coordenador dedicado exclusivamente ao EM tem a possibilidade de criar protocolos de preparação para vestibular que CD, JG e CDR (que não têm coordenador exclusivo de EM) podem replicar.

**Oportunidade 6 — Protagonismo estudantil no EM como motor de frequência.**
Alunos do EM que se sentem protagonistas faltam menos. Criar mecanismos de escuta ativa — pesquisa de clima, conselho de representantes, projetos interdisciplinares com escolha temática — pode movimentar o indicador de frequência mais do que qualquer campanha de cobrança de pais.

---

## 1.3 As Diferenças Cruciais que Exigem Abordagens Radicalmente Diferentes

| Dimensão | Anos Finais (6º-9º) | Ensino Médio (1ª-3ª) |
|----------|--------------------|-----------------------|
| **Coordenador em BV** | Bruna Vitória (6º-9º) | Gilberto Santos (1ª-3ª EM) |
| **Pressão externa** | Nenhuma (currículo livre) | SSA (3ª Série) + ENEM |
| **Perfil do aluno** | Adolescente em formação identitária | Adolescente com projeto de futuro |
| **Relação família** | Alta interferência parental | Autonomia crescente |
| **SAE** | TEEN 1 (4 volumes, 12 caps) | TEEN 2 (9º+EM, 4 volumes, 12 caps) |
| **Causa da falta** | Desinvestimento precoce / problema familiar | Estratégica / engajamento baixo |
| **Causa da baixa conformidade** | Fricção técnica + rotina fragmentada | Resistência cultural + disputa de prioridades |
| **Melhor ponto de entrada** | Aluno (dado de presença gera urgência) | Resultado (dado de nota gera relevância) |
| **Instrumento mais efetivo** | Busca ativa de família | Projeto de carreira + mentoria de professor |
| **Risco maior** | Evasão silenciosa | Reprovação por nota + abandono no III Tri |
| **Dashboard — página âncora** | `23_Alerta_Precoce_ABC.py` | `21_Boletim_Digital.py` + `24_Cruzamento_SIGA_SAE.py` |
| **Frequência de reunião ideal** | Semanal (muitas variáveis) | Quinzenal de dados + semanal de ação |
| **Formato de feedback ao professor** | "Seu aluno tal faltou 5 dias" | "Sua turma de 3º Ano está no Cap. 3, deveria estar no 5" |
| **Indicador principal** | Frequência + ocorrências | Progressão SAE + desempenho em simulados |
| **Intervenção mais urgente 2026** | JG: busca ativa massiva | Todas as unidades: adoção SAE Digital |

---

# PARTE 2 — PROPOSTA PARA ANOS FINAIS

## 2.1 Filosofia do Programa para Anos Finais

**"A turma tem dono, mesmo quando tem 8 professores."**

O maior problema dos Anos Finais não é conformidade — é responsabilidade difusa. Nenhum professor se sente "dono" da trajetória do aluno porque cada um o vê 1-5 vezes por semana. O coordenador é o único que vê o aluno inteiro.

A proposta para Anos Finais tem dois eixos:
1. **Tornar o coordenador o integrador de trajetória** — usando o dashboard para construir a visão longitudinal que nenhum professor individual tem
2. **Criar um professor conselheiro por turma** — com 30 minutos mensais de análise de painel de turma

## 2.2 Modelo de Reunião Semanal — Coordenadores de Anos Finais

### Reunião de Unidade para Anos Finais: "Formato TRIPÉ"
**Duração:** 30 minutos | **Frequência:** Semanal (segunda, 7h30)
**Quem participa:** Coordenador(es) de Anos Finais + eventual professor convidado

| Bloco | Tempo | Conteúdo | Página do Dashboard |
|-------|-------|----------|---------------------|
| **Tripé 1: Presença** | 10 min | Quem faltou? Há reincidência? Família contactada? | `20_Frequencia_Escolar.py`, `23_Alerta_Precoce_ABC.py` |
| **Tripé 2: Registro** | 10 min | Professores que não lançaram essa semana. Lista nominal. Próxima ação. | `08_Alertas_Conformidade.py`, `13_Semaforo_Professor.py` |
| **Tripé 3: Ação** | 10 min | Uma ação, um responsável, um prazo. Checar ação da semana anterior. | `10_Painel_Unificado.py` |

**Regras do Tripé:**
- O coordenador **não prepara** nada — o PMV chega pronto às 7h
- O foco é sempre: **quais nomes**, não quais percentuais
- A reunião termina com uma lista de no máximo 3 nomes: 1 professor + 1 aluno + 1 família para ação desta semana
- Se todos os três estão verdes: reunião dura 10 minutos

## 2.3 Roteiros das 4 Reuniões-Tipo para Anos Finais

---

### REUNIÃO-TIPO 1: SEMANA NORMAL (verde)
**Quando usar:** Conformidade >=70%, frequência >=88%, sem novos Tier 3, sem graves
**Duração:** 15-20 minutos

**Roteiro:**

```
[0-3 min] PMV na tela — coordenador abre página 09_Resumo_Semanal.py
          Verifica: todos os indicadores verdes?

[3-8 min] Progressão SAE — abre 05_Progressao_SAE.py
          Pergunta: "Alguém 2+ capítulos atrás?"
          Se sim: anota nome para conversa informal (não é emergência)
          Se não: celebra em 30 segundos e segue

[8-12 min] Frequência — abre 20_Frequencia_Escolar.py
           Filtra pela unidade. Aluno beirando 80%? Nomeia 1 para monitoramento
           Se nenhum crítico: encerra esse bloco

[12-16 min] Ação da Semana
           "Esta semana vou conversar com [professor X] sobre SAE"
           Registra no Formulário de 1 Linha

[16-20 min] Celebração rápida
           "O 7º Ano A teve 96% de frequência esta semana. Vou mandar uma mensagem
           para a Sra. [professora conselheira]."
```

**Indicador de sucesso:** Reunião terminou sem angústia. Coordenador saiu com 1 ação.

---

### REUNIÃO-TIPO 2: ALERTA (amarelo)
**Quando usar:** 1-2 indicadores em amarelo (conformidade entre 55-70%, frequência 83-88%, 1-2 novos Tier 2, graves estáveis)
**Duração:** 30-35 minutos

**Roteiro:**

```
[0-5 min] PMV na tela — página 09_Resumo_Semanal.py
          "O veredicto de hoje é ATENÇÃO. Vamos entender por quê."
          Identificar qual indicador puxou o amarelo

[5-15 min] FOCO no indicador amarelo
           SE é conformidade:
             → Abre 08_Alertas_Conformidade.py
             → Filtra "professores sem lançamento nos últimos 7 dias"
             → Lista nominal: quem são? É a primeira vez ou reincidência?
             → Protocolo: professores de 1ª vez = conversa informal
                          professores de 2ª+ semana = feedback formal

           SE é frequência:
             → Abre 20_Frequencia_Escolar.py → aba "por turma"
             → Qual turma puxou para baixo? É padrão de 1 aluno ou toda a turma?
             → Se 1 aluno: Tier ABC 23_Alerta_Precoce_ABC.py — já é Tier 3?
             → Se turma inteira: investigar evento externo (feriado prolongado, jogo)

           SE é ocorrências:
             → Abre 22_Ocorrencias.py
             → Quais turmas, quais alunos, que tipo (Leve/Media/Grave)?
             → Padrão: mesmo aluno em múltiplas ocorrências = reunião familiar urgente

[15-25 min] Plano de Ação dos Próximos 7 Dias
           NOME 1: [professor] → [ação específica] → responsável → prazo
           NOME 2: [aluno] → [ação específica] → responsável → prazo
           NOME 3: [família se necessário] → [ação] → responsável → prazo

[25-30 min] Hipótese e Risco
           "Por que está amarelo? Nossa hipótese: [X]"
           "O que acontece se ficar amarelo por 2 semanas? Risco: [Y]"
           Define: se em 7 dias não melhorou, convoca reunião CRISE
```

**Indicador de sucesso:** Coordenador tem 3 nomes e 3 ações com prazo. Sabe exatamente quando vai virar CRISE.

---

### REUNIÃO-TIPO 3: CRISE (vermelho)
**Quando usar:** 1+ indicador vermelho por 2+ semanas, Tier 3 novo sem resposta, graves em escalada, conformidade <50%
**Duração:** 45-60 minutos | **Participantes extras:** Direção convocada

**Roteiro:**

```
[0-5 min] Protocolo de Abertura
          Coordenador abre 10_Painel_Unificado.py
          Apresenta: "Estamos em CRISE. Eis o que os dados mostram."
          Regra: sem drama, sem acusação. Só dados.

[5-15 min] Diagnóstico de Causa-Raiz
          Abertura do 14_Alertas_Inteligentes.py
          Cruzamento: quais professores têm baixa conformidade E turmas com baixa freq?
          Cruzamento: quais alunos têm freq baixa E ocorrências recentes?
          Abertura do 24_Cruzamento_SIGA_SAE.py se relevante
          PERGUNTA CENTRAL: "Qual é a causa-raiz deste indicador estar vermelho?"

[15-30 min] Lista de Nomes Completa
          Professores críticos: lista nominal + histórico de feedbacks
          Alunos Tier 3: lista nominal + última intervenção registrada
          Famílias não contactadas: lista nominal + prazo

[30-45 min] Plano de Crise (48h)
          O que acontece HOJE: quem faz o quê antes de amanhã às 17h?
          O que acontece EM 48h: reuniões, ligações, visitas
          O que acontece EM 1 SEMANA: verificação com data marcada
          Responsável por cada ação: nome, não cargo
          Escalação necessária? Nível 2 ou 3?

[45-60 min] Comunicação e Limites
          O que comunicar para professores (o quê, por quem, quando)?
          O que comunicar para pais dos alunos críticos?
          O que NÃO comunicar (preservar privacidade, evitar pânico)?
          Data da próxima reunião: daqui a 7 dias para checar evolução
```

**Especificidades por unidade:**

- **JG em CRISE de frequência:** Protocolo de Busca Ativa Nível 1 para TODOS os alunos abaixo de 75%. Pietro + secretaria ligam no mesmo dia. Lecinane vai pessoalmente a endereços dos 5 casos mais graves se necessário.
- **CDR em CRISE de ocorrências:** Mapa de calor das 36 graves nas páginas `22_Ocorrencias.py`. Identificar as 3 turmas-foco. Presença física do coordenador nessas turmas por 5 dias consecutivos.
- **BV em CRISE de conformidade:** 23 professores sem registro = Bruna Vitória e Gilberto dividem lista (ela Anos Finais, ele EM). Cada um agenda 5 minutos com cada professor em 48h.
- **CD em CRISE de evasão:** Alunos com 15+ dias sem presença em qualquer registro = verificar matrícula ativa. Secretaria acadêmica + coordenação juntas.

**Indicador de sucesso:** Direção está informada e comprometida. Cada ação tem nome e prazo. Próxima reunião marcada.

---

### REUNIÃO-TIPO 4: ESTRATÉGICA (abertura/encerramento de trimestre)
**Quando usar:** Início e fim de cada trimestre | Duração: 60-90 minutos
**Participantes:** Coordenadores de Anos Finais de TODAS as unidades + Direção

**Roteiro da Abertura de Trimestre:**

```
[0-10 min] Painel de Rede — página 07_Visão_Geral.py
           Comparativo de todas as unidades no último trimestre
           Quais unidades evoluíram? Quais regredirão?
           Celebração com dados: "BV subiu de 39,5% para X%"

[10-30 min] Análise de Padrões — páginas 17_Dashboard_Analytics.py + 18_Power_BI.py
           Cruzamento A x C: conformidade e resultado de alunos
           Cruzamento B x D: frequência e comportamento
           PERGUNTA: "Qual é o padrão que mais explica nossos resultados?"

[30-50 min] Definição das 3 Prioridades do Trimestre
           Para Anos Finais especificamente:
           I Tri: Registro SIGA + Busca Ativa JG + Mapa de ocorrências CDR
           II Tri: Alinhamento SAE + Observação de aula + Intervenção acadêmica
           III Tri: Avaliação formativa + Cobertura curricular + Passagem 9º→EM

[50-70 min] Diferenciação por Unidade
           BV: o que a Bruna Vitória precisa de diferente das outras 3 unidades?
           CD: o que Alline/Elisangela/Vanessa precisam de diferente?
           JG: o que Lecinane/Pietro precisam de diferente?
           CDR: o que Ana Cláudia/Vanessa precisam de diferente?

[70-90 min] Compromissos e Instrumentos
           1 instrumento construído durante a reunião (não como pré-trabalho)
           1 compromisso verificável por unidade
           Data da próxima reunião estratégica
```

**Roteiro do Encerramento de Trimestre:**

```
[0-15 min] Balanço — todos os indicadores
           Comparativo baseline vs meta vs resultado real
           PERGUNTA: "Atingimos o que prometemos?"

[15-30 min] O que funcionou e o que não funcionou
           Sem julgamento de valor. Análise de causalidade.
           "O que fizemos que mais moveu os indicadores?"

[30-50 min] Aprendizados que viram processo
           Qual intervenção foi tão efetiva que deve virar protocolo permanente?
           Qual ferramenta do dashboard foi mais usada e deve ser padrão?

[50-70 min] Planejamento do próximo trimestre
           Prioridades + metas + responsáveis

[70-80 min] Reconhecimento com dados
           Professor que mais evoluiu
           Turma com maior recuperação
           Coordenador com mais feedbacks registrados
```

---

## 2.4 Como Lidar com as 4 Unidades Diferenciadas em Anos Finais

### BV — Modelo de Referência
**Problema atual:** Conformidade 39,5% apesar de ser a "melhor" unidade. Significa que mesmo a referência precisa crescer 30+ pontos.
**Estratégia:** BV implementa as inovações primeiro. É o laboratório. O que funcionar em BV vira protocolo para a rede.
**Intervenção específica:** Bruna Vitória cria o "Professor Conselheiro" — um professor por turma que recebe o painel mensal de alunos. Começa com 4 turmas piloto no I Tri.
**Meta diferenciada:** 80% de conformidade em 6 semanas (meta mais agressiva justificada por ser referência).
**Dashboard âncora:** `15_Resumo_Semanal_Coord.py` + `05_Progressao_SAE.py`

### CD — Gestão por Divisão
**Problema atual:** 3 coordenadoras com 622 alunos. Risco de sobreposição e lacunas.
**Estratégia:** Divisão clara de portfólio. Alline = Matemática e Ciências. Elisangela = Linguagens. Vanessa = História/Geo/Arte/Filosofia/EM. Cada uma responsável pelos professores e alunos de suas disciplinas.
**Intervenção específica:** Dashboard filtrado por área — cada coordenadora vê só seus professores no `13_Semaforo_Professor.py`.
**Meta diferenciada:** Reduzir de 39,1% para 65% em conformidade (crescimento mais modesto dado a divisão de coordenação).
**Dashboard âncora:** `08_Alertas_Conformidade.py` (filtrado por disciplina)

### JG — Operação de Resgate
**Problema atual:** 79,6% de frequência, 25% dos alunos em risco. É a situação mais crítica da rede.
**Estratégia:** As primeiras 8 semanas do I Tri em JG são EXCLUSIVAMENTE sobre presença. Nenhuma pauta nova entra enquanto a frequência não passar de 82%.
**Intervenção específica:** Pietro assume exclusivamente o rastreamento de alunos ausentes. Lecinane assume exclusivamente o acompanhamento de professores. Divisão cirúrgica.
**Operação "Bom Dia JG":** Segunda, quarta e sexta, Pietro e Lecinane ficam na porta às 7h. Aluno presente = verificação no SIGA imediata. Aluno ausente = ligação antes das 9h.
**Meta diferenciada:** 83% em 4 semanas, 86% em 8 semanas. Meta progressiva porque a realidade é a pior.
**Dashboard âncora:** `20_Frequencia_Escolar.py` (todos os dias, não só segunda)

### CDR — Operação Clima
**Problema atual:** 36 de 53 ocorrências graves em 4 semanas. 357 alunos. É uma unidade pequena com problema enorme.
**Estratégia:** Identificar as 3-5 turmas que concentram as 36 graves. Toda energia nas próximas 8 semanas vai para essas turmas.
**Intervenção específica:** Ana Cláudia e Vanessa fazem presença física nas 3 turmas mais críticas por 3 semanas consecutivas. Observação não-punitiva + entrevistas com alunos.
**Hipótese a testar:** As graves de CDR são de um grupo pequeno de alunos reincidentes. Se isso for verdade, 5-6 alunos respondem por 80% das graves. Intervenção cirúrgica.
**Meta diferenciada:** De 36 graves em 4 semanas para <=15 no I Tri inteiro. Agressivo e necessário.
**Dashboard âncora:** `22_Ocorrencias.py` + `14_Alertas_Inteligentes.py`

---

## 2.5 Propostas Inovadoras Exclusivas para Anos Finais

### INOVAÇÃO AF-1: "O Conselho de Turma Digital"
**O que é:** Uma vez por mês, o coordenador de Anos Finais realiza um "Conselho de Turma" virtual de 20 minutos usando o dashboard. Convoca os 2-3 professores mais presentes naquela turma (ex: professor conselheiro + Matemática + Português) e abre o `19_Painel_Aluno.py` na turma específica.

**Formato:**
```
[0-5 min] Painel geral da turma — frequência, notas médias, ocorrências
[5-12 min] Alunos de atenção — quem precisa de ação ESTA semana?
[12-18 min] Divisão de responsabilidade — cada professor "adota" 1 aluno para acompanhamento semanal
[18-20 min] Registro — 1 ação por professor, com prazo
```

**Por que é melhor que o plano atual:** O Plano Definitivo propõe feedback do coordenador para o professor, mas nunca promove encontro entre professores da mesma turma. O Conselho de Turma Digital cria responsabilidade coletiva sem adicionar carga excessiva.

### INOVAÇÃO AF-2: "Padrão de Lançamento por Dia da Semana"
**O que é:** Análise no dashboard de qual dia da semana cada professor mais lança aulas. Professores têm ritmos diferentes — alguns lançam na sexta, outros no domingo, outros no dia seguinte.

**Implementação técnica:** Cruzar `fato_Aulas.csv` com `dim_Calendario.csv` para identificar o "dia preferido de lançamento" de cada professor. Configurar o alerta A2 para respeitar esse padrão — se o professor costuma lançar na sexta, o alerta dispara se a sexta passou sem lançamento, não na terça.

**Resultado esperado:** Reduzir falsos positivos nos alertas, aumentar a relevância das notificações e, consequentemente, aumentar a taxa de resposta dos professores.

### INOVAÇÃO AF-3: "Triagem de 10 Segundos" para o Coordenador
**O que é:** Uma página simplificada no dashboard (pode ser uma aba nova no `09_Resumo_Semanal.py`) com apenas 3 semáforos:
- PROFESSORES: verde/amarelo/vermelho
- ALUNOS: verde/amarelo/vermelho
- CLIMA: verde/amarelo/vermelho

**Quando usada:** Toda manhã, antes de qualquer outra tarefa. Se tudo verde: 10 segundos e fecha. Se há amarelo/vermelho: abre a página detalhada correspondente.

**Impacto:** Coordenadores sobrecarregados abrem o dashboard raramente porque "é muito para ver". Uma triagem de 10 segundos cria hábito de abertura diária sem aumentar a carga cognitiva.

### INOVAÇÃO AF-4: "Semana de Adoção" para Professores Q2
**O que é:** Uma vez por trimestre, os 10 professores com menor conformidade são convidados (não obrigados) para uma "Semana de Adoção" onde um professor de referência (Q4, conformidade alta) os acompanha durante 5 dias.

**Formato:**
- Dia 1: Professor referência mostra como faz seu lançamento em 3 minutos
- Dia 2-4: Ambos lançam no mesmo horário (intervalo do almoço ou saída)
- Dia 5: Professor Q2 faz sozinho, professor referência está disponível se precisar

**Por que funciona:** Aprendizagem por modelagem entre pares, não por instrução de cima para baixo. O professor Q2 não é tratado como problema — é tratado como alguém que precisa de suporte de colega.

---

# PARTE 3 — PROPOSTA PARA ENSINO MÉDIO

## 3.1 Filosofia do Programa para EM

**"Resultado é argumento, currículo é meio, vestibular é consequência."**

No Ensino Médio, a conformidade de registro e o alinhamento SAE não são fins — são meios para um resultado que o aluno compreende: passar no vestibular, ter base para o ENEM, construir projeto de vida. A estratégia para o EM precisa conectar cada prática docente a esse resultado compreensível pelo aluno.

O coordenador de EM não "cobra" o professor. Ele **negocia em nome do aluno**: "Eu sei que você pode dar o conteúdo que quiser, e sei que você conhece o ENEM melhor do que o livro. Mas 87% dos seus alunos têm nota abaixo de 7 em Matemática. O capítulo 3 do SAE cobre exatamente essa lacuna. O que precisamos para avançar?"

## 3.2 Papel Específico do Coordenador de EM (Gilberto Santos — BV)

**O que o Plano Definitivo não faz:** Menciona Gilberto exatamente 1 vez (no quadro de coordenadores). Não tem nenhuma reunião desenhada especificamente para o EM, nenhuma proposta de diferenciação de pauta, nenhum indicador específico do segmento.

**O que esta proposta faz:**

Gilberto Santos tem uma posição única na rede ELO: é o único coordenador dedicado exclusivamente ao Ensino Médio. Isso o torna:
1. O especialista de EM da rede (mesmo que BV seja sua unidade)
2. O modelo para as outras unidades que não têm coordenador exclusivo de EM
3. O ponto de convergência entre Anos Finais (que Bruna Vitória atende) e EM

**Responsabilidades específicas do Coordenador de EM:**
- Acompanhar o ritmo SAE com foco em alinhamento ENEM (não só cumprimento de capítulo)
- Monitorar as turmas de 3ª Série com protocolo de SSA
- Coordenar simulados ENEM internos (proposta nova — ver INOVAÇÃO EM-1)
- Criar e manter o "Diário de Carreira" dos alunos de 3ª Série (proposta nova — ver INOVAÇÃO EM-2)
- Ser referência para os coordenadores de CD, JG e CDR em questões de EM

## 3.3 Modelo de Reunião Semanal para EM

### Reunião Semanal de EM: "Formato COMPASS"
**Duração:** 30 minutos | **Frequência:** Semanal (terça, 12h — horário de almoço, mais adequado para professores de EM que frequentemente chegam tarde)
**Quem participa:** Coordenador de EM + eventual professor de 3ª Série convidado

| Bloco | Tempo | Conteúdo | Página do Dashboard |
|-------|-------|----------|---------------------|
| **C — Currículo** | 8 min | Ritmo SAE vs. esperado. Quem está atrasado? Qual capítulo é ENEM-crítico? | `05_Progressao_SAE.py` |
| **O — Ocorrências** | 5 min | Novas ocorrências no EM. Padrão de comportamento. | `22_Ocorrencias.py` |
| **M — Métricas de Aprendizagem** | 8 min | Notas recentes. Quem está abaixo de 7? Há padrão por disciplina? | `21_Boletim_Digital.py` |
| **P — Presença** | 4 min | Frequência por turma de EM. Alunos beirando o limite estratégico. | `20_Frequencia_Escolar.py` |
| **A — Ação** | 5 min | 1 ação para esta semana. Check da ação anterior. | `10_Painel_Unificado.py` |
| **SS — SAE Digital** | (quinzenal) | Cruzamento SIGA×SAE — quem está usando e qual impacto? | `24_Cruzamento_SIGA_SAE.py` |

**Diferença do formato de Anos Finais:**
- O COMPASS começa por **currículo** (não por presença), porque no EM o dado mais crítico é o alinhamento com ENEM
- A presença aparece no final porque no EM o padrão é diferente — a maioria das faltas são estratégicas, não de evasão
- O SAE Digital é revisado quinzenalmente (não semanalmente) porque o engajamento digital demora mais para mostrar variação

## 3.4 Roteiros das 4 Reuniões-Tipo para EM

---

### EM-REUNIÃO TIPO 1: SEMANA NORMAL (verde no EM)
**Quando usar:** Currículo no ritmo, freq >=85%, notas estáveis, sem graves
**Duração:** 20 minutos

```
[0-5 min] COMPASS rápido — todos os 5 indicadores no verde?
          Abre 09_Resumo_Semanal.py filtrado para séries de EM
          Se verde: "Ótimo. Foco desta semana é SAE Digital."

[5-12 min] Verificação de Progressão SAE
          Abre 05_Progressao_SAE.py filtrado por TEEN 2 (9º+EM)
          Capítulo esperado vs. capítulo real por disciplina
          Atenção especial: professores de Matemática e Português (5 aulas/semana)
          estão no ritmo? São os mais críticos para ENEM.

[12-18 min] Engajamento SAE Digital (quinzenal)
          Abre 24_Cruzamento_SIGA_SAE.py
          Quais alunos de 3ª Série usaram o SAE Digital esta semana?
          Correlação com notas do boletim?

[18-20 min] Ação e Registro
          1 mensagem de reconhecimento para professor no ritmo SAE
          1 nota no Formulário de 1 Linha
```

---

### EM-REUNIÃO TIPO 2: ALERTA (amarelo no EM)
**Quando usar:** Currículo 2+ semanas atrasado, notas da turma caíram, frequência <83%, aluno de 3ª Série em Tier 2
**Duração:** 35-40 minutos

```
[0-5 min] COMPASS — identificar qual "letra" está amarela
          Abre 10_Painel_Unificado.py
          "Estamos em atenção por causa de [C/O/M/P/A]"

[5-20 min] Análise da causa

          SE currículo atrasado (C):
          → Abre 05_Progressao_SAE.py
          → "Professor X está no Cap. 3. Deveria estar no 5. É a 1ª semana ou é padrão?"
          → Se 1ª semana: "Conversa de Ritmo" informal (10 min no intervalo)
          → Se padrão (3+ semanas): Feedback formal com plano de compactação
          → Diferencial EM: "Capítulo X cobre competência ENEM Y. Qual é sua estratégia?"

          SE notas caíram (M):
          → Abre 21_Boletim_Digital.py filtrado por série
          → "Quais disciplinas caíram? É uma turma ou o segmento todo?"
          → Se uma turma: investigar o professor
          → Se segmento: investigar evento externo (simulado, etc.)

          SE frequência beirando limite (P):
          → Abre 20_Frequencia_Escolar.py
          → Identificar alunos com 76-80% (DELIBERADAMENTE no limite)
          → Protocolo EM: conversa com O PRÓPRIO ALUNO (não com a família)
            "Você sabe que tem X% de presença. O que está acontecendo?"

[20-35 min] Plano de Ação
          Professores: conversa de ritmo agendada para esta semana
          Alunos: conversa com o próprio aluno (abordagem de protagonismo)
          Se 3ª Série: verificar se o atraso afeta conteúdo ENEM crítico

[35-40 min] Hipótese e Escalação
          "Nossa hipótese para o amarelo é [X]"
          "Precisamos escalar? Nível 1 (informar direção) ou resolvemos internamente?"
```

---

### EM-REUNIÃO TIPO 3: CRISE (vermelho no EM)
**Quando usar:** 3ª Série com desempenho crítico, reprovações em série, frequência <80%, 3+ professores sem lançamento, ocorrências graves
**Duração:** 60 minutos | **Participantes extras:** Direção + eventual professor convocado

```
[0-10 min] Mapeamento da crise
           Abre 07_Visão_Geral.py — ver EM em perspectiva de rede
           Qual unidade está em crise? É isolado ou é rede?
           Abre 14_Alertas_Inteligentes.py — cruzamentos inteligentes
           "Professores com baixa conformidade têm turmas com notas abaixo?"

[10-25 min] Análise cirúrgica
           Se crise de notas na 3ª Série:
           → Abre 21_Boletim_Digital.py + 24_Cruzamento_SIGA_SAE.py
           → "Quais alunos estão em risco real de reprovação?"
           → "Esses alunos estão usando o SAE Digital?"
           → Plano de recuperação individual: professor + coordenador + família

           Se crise de ocorrências no EM:
           → Abre 22_Ocorrencias.py filtrado por séries EM
           → No EM, ocorrências graves frequentemente são de natureza diferente
             (uso de celular, questões de saúde mental, conflitos entre pares)
           → Acionar protocolo de encaminhamento: não é só punição
           → Integrar SAE Pulso (se disponível) para diagnóstico de clima

[25-45 min] Plano de Crise com perspectiva de EM
           Alunos críticos: CONVERSA DIRETA com o aluno, não só com família
             (autonomia e protagonismo são valores do EM)
           Professores: reunião tripartite — prof + coord + representante dos alunos
           3ª Série em crise: plano de preparação intensiva para SSA
             (não esperar pelo III Tri — começar no II Tri)

[45-60 min] Comunicação
           O que comunicar para professores?
           O que comunicar para os próprios alunos? (diferencial EM)
           O que comunicar para famílias?
           Próxima reunião em 5 dias úteis
```

---

### EM-REUNIÃO TIPO 4: ESTRATÉGICA (trimestral)
**Quando usar:** Abertura e encerramento de trimestre
**Duração:** 60-75 minutos | **Diferencial:** Inclui representante de alunos de 3ª Série

```
[0-10 min] Resultados do trimestre anterior no EM especificamente
           Comparativo de séries: 1ª vs 2ª vs 3ª
           Abre 17_Dashboard_Analytics.py com filtro EM

[10-25 min] Análise de alinhamento curricular com ENEM
           "Quais competências do ENEM cobrimos nos capítulos 1-4?"
           "Quais deixamos de cobrir? Por quê?"
           "O ritmo SAE permite cobrir as competências críticas antes de dezembro?"
           Referência: 12 caps ÷ 3 trimestres = 4 caps/tri
           Caps 1-4 (I Tri) → Caps 5-8 (II Tri) → Caps 9-12 (III Tri)

[25-40 min] Prioridades diferenciadas por série
           1ª Série EM: foco em transição do 9º Ano, hábitos de estudo
           2ª Série EM: foco em consolidação curricular, SAE intensivo
           3ª Série EM: foco em simulados, análise de resultado, projeto de carreira

[40-55 min] Voz dos alunos (exclusivo para reuniões estratégicas do EM)
           Representante de turma de 3ª Série apresenta 3 pontos:
           1. O que está funcionando
           2. O que precisa melhorar
           3. O que precisamos que os professores façam diferente
           Coordenador registra e apresenta na próxima Reunião de Rede

[55-75 min] Instrumentos e compromissos
           Revisão do Contrato de Prática para professores de EM
           Meta específica para o próximo trimestre por série
           Planejamento de simulado interno (se II ou III Tri)
```

---

## 3.5 Métricas Específicas para o EM

As métricas do Plano Definitivo são genéricas. Para o EM, estas métricas são mais relevantes:

| Indicador EM | Fonte | Meta I Tri | Meta Ano |
|-------------|-------|-----------|---------|
| % professores de EM no ritmo SAE (TEEN 2) | dim_Progressao_SAE.csv | 35% | 65% |
| % alunos 3ª Série com nota >=7 em Português e Matemática | fato_Notas_2026 (quando disponível) | 60% | 75% |
| Frequência média do EM | fato_Frequencia_Aluno.csv | 86% | 89% |
| Alunos 3ª Série usando SAE Digital semanalmente | fato_Engajamento_SAE.csv | 40% | 70% |
| % professores de EM com pelo menos 1 feedback trimestral | feedbacks_coordenacao.json | 50% | 100% |
| Ocorrências graves no EM | fato_Ocorrencias.csv | <=3/mês | <=1/mês |
| Alunos reprovados por nota 3ª Série | fato_Notas_Historico.csv | <5% | <3% |

---

# PARTE 4 — USO COMPLETO DO DASHBOARD: MAPA DE 26 PÁGINAS

## 4.1 Classificação das 26 Páginas por Frequência de Uso

### GRUPO A — Uso Diário (coordenador abre todo dia útil)
| Página | Nome | Quando abre | Tempo médio |
|--------|------|------------|-------------|
| 09 | Resumo_Semanal.py | Toda segunda 7h - diagnóstico rápido | 3-5 min |
| 23 | Alerta_Precoce_ABC.py | Toda segunda + qualquer alerta A1 | 5-8 min |
| 08 | Alertas_Conformidade.py | Toda segunda + antes de cada feedback | 3-5 min |

### GRUPO B — Uso Semanal (abertura nas reuniões e rituais rápidos)
| Página | Nome | Quando abre | Tempo médio |
|--------|------|------------|-------------|
| 10 | Painel_Unificado.py | Reunião semanal - visão geral | 5 min |
| 13 | Semaforo_Professor.py | Reunião semanal - classificação professores | 5 min |
| 20 | Frequencia_Escolar.py | Reunião semanal - bloco Presença/PRESENÇA | 5-8 min |
| 22 | Ocorrencias.py | Reunião semanal - bloco Clima | 5 min |
| 05 | Progressao_SAE.py | Reunião semanal - bloco Currículo (EM) / Registro+ (AF) | 5 min |

### GRUPO C — Uso Quinzenal (análises mais profundas, reuniões de Alerta)
| Página | Nome | Quando abre | Tempo médio |
|--------|------|------------|-------------|
| 14 | Alertas_Inteligentes.py | Reuniões de Alerta e Crise - cruzamentos | 10-15 min |
| 15 | Resumo_Semanal_Coord.py | Quinzenal - check de feedbacks registrados | 5 min |
| 16 | Devolutivas.py | Quando há feedback a fazer ou verificar | 5-10 min |
| 19 | Painel_Aluno.py | Conselhos de Turma Digital (mensais) | 10-15 min |
| 21 | Boletim_Digital.py | Análise de notas (quinzenal no EM) | 8-12 min |
| 24 | Cruzamento_SIGA_SAE.py | Quinzenal (EM) / Mensal (AF) | 10-15 min |

### GRUPO D — Uso Mensal (reuniões estratégicas, análises de rede)
| Página | Nome | Quando abre | Tempo médio |
|--------|------|------------|-------------|
| 07 | Visão_Geral.py | Reuniões de Rede e trimestrais | 10-15 min |
| 17 | Dashboard_Analytics.py | Reuniões estratégicas - cruzamentos | 15-20 min |
| 18 | Power_BI.py | Reuniões estratégicas - análise avançada | 15-20 min |
| 25 | Relatorio_Familia.py | Antes de contatos com família (alunos críticos) | 10 min |
| 26 | Dashboard_Unificado.py | Encerramento de trimestre | 20-30 min |

### GRUPO E — Uso Trimestral (instrumentos de planejamento)
| Página | Nome | Quando abre | Tempo médio |
|--------|------|------------|-------------|
| 01 | Quadro_Gestao.py | Abertura e encerramento de trimestre | 15 min |
| 02 | Calendario.py | Planejamento de reuniões e eventos | 10 min |
| 03 | Estrutura.py | Onboarding de novos coordenadores | 15 min |
| 04 | Material_SAE.py | Planejamento curricular no início de trimestre | 15 min |
| 06 | Agenda.py | Planejamento semanal (coordenadores organizados) | 5 min |
| 11 | Material_Professor.py | Planejamento de formação de professores | 10 min |
| 12 | Agenda_Professor.py | Verificação de carga horária e conflitos | 10 min |

---

## 4.2 Fluxo de Decisão: "Se X está vermelho, abra Y, decida Z"

### FLUXO 1 — Conformidade Vermelha (<50%)
```
GATILHO: PMV segunda mostra conformidade <50%

PASSO 1: Abre 08_Alertas_Conformidade.py
         Filtra por "sem lançamento nos últimos 7 dias"
         → Quantos professores? É a mesma lista da semana passada?

PASSO 2: Se lista CRESCEU → situação piorando → vai para Reunião CRISE
         Se lista IGUAL → situação estagnada → Reunião ALERTA com foco em novas estratégias
         Se lista DIMINUIU → situação melhorando → Reunião NORMAL, celebra quem saiu da lista

PASSO 3: Abre 13_Semaforo_Professor.py
         Filtra por "Crítico"
         → Quem está Crítico há 3+ semanas? Esses são candidatos a escalação Nível 2

PASSO 4: Para cada professor Crítico 3+ semanas → Formulário de 1 Linha
         → Houve conversa registrada? Se não: ESTA SEMANA
         → Se sim e não melhorou: Formulário de 1 Linha + escalação Nível 2

DECISÃO Z: "Professor [Nome] está Crítico por [N] semanas.
           Já tive [X] conversas. Próximo passo: [escalação Nível 2/Reunião com direção]"
```

### FLUXO 2 — Frequência Vermelha (<80%)
```
GATILHO: PMV segunda mostra frequência unidade <80% OU aluno específico com 3+ faltas consecutivas

PASSO 1: Abre 20_Frequencia_Escolar.py
         Aba "por turma": qual turma puxou para baixo?
         Aba "por aluno": quem são os reincidentes?

PASSO 2: Abre 23_Alerta_Precoce_ABC.py
         Filtro Tier 3: há novos Tier 3 esta semana?
         → Se sim: protocolo de busca ativa Nível 1 HOJE (não amanhã)

PASSO 3: Para Anos Finais (AF):
         → Liga para família do aluno em até 24h
         → Registra em 25_Relatorio_Familia.py: data do contato, o que foi dito, compromisso da família

         Para EM:
         → PRIMEIRO: conversa com o próprio aluno
         → Abordagem: "Percebi que você faltou X dias. O que está acontecendo?"
         → Só liga para família se aluno não responder ou situação for grave

PASSO 4: Se turma inteira com freq <80% (não aluno isolado):
         → Hipótese 1: evento externo (verificar dim_Calendario.csv — havia evento?)
         → Hipótese 2: problema de clima da turma → abre 22_Ocorrencias.py (há pico de ocorrências?)
         → Hipótese 3: problema com professor específico → cruza com conformidade do professor

DECISÃO Z: "A frequência de [turma] caiu por [causa identificada].
           Ação: [busca ativa / contato família / investigação de clima].
           Responsável: [Pietro/Lecinane/Gilberto/etc]. Prazo: [data]"
```

### FLUXO 3 — Ocorrências Graves em Escalada (CDR / qualquer unidade)
```
GATILHO: Alerta A7 (CDR >4 graves em 1 semana) OU Alerta A3 (ocorrência grave nova)

PASSO 1: Abre 22_Ocorrencias.py imediatamente
         Filtro "Graves" + filtro unidade + filtro "esta semana"
         → Quantas? Quem? Que tipo?

PASSO 2: Identificar padrão:
         → Mesmo aluno em múltiplas ocorrências: protocolo de aluno reincidente
         → Mesmo horário: investigar contexto (aula específica? recreio? saída?)
         → Mesma turma: investigar clima da turma

PASSO 3: Cruzar com 14_Alertas_Inteligentes.py
         → O aluno tem frequência baixa ALÉM das ocorrências? → Tier ABC provavelmente 3
         → O professor da turma tem baixa conformidade SIGA? → Pode haver subnotificação

PASSO 4: Para CDR especificamente (36 graves em 4 semanas):
         → Criar mapa de calor manual: data × turma × aluno
         → Hipótese: 5-6 alunos respondem por 70%+ das graves?
         → Se sim: intervenção cirúrgica nos 5-6 alunos, não no segmento todo

DECISÃO Z: "O padrão das graves em CDR é [padrão identificado].
           A intervenção prioritária é [ação cirúrgica / mudança de protocolo / reunião família].
           Responsável: [Ana Cláudia / Vanessa]. Em 48h."
```

### FLUXO 4 — Gap SAE Crítico (EM, 3ª Série)
```
GATILHO: Alerta A8 (professor 2+ capítulos atrás) OU verificação quinzenal

PASSO 1: Abre 05_Progressao_SAE.py
         Filtro "TEEN 2" (9º Ano + EM)
         → Capítulo esperado vs capítulo real por professor e disciplina
         → Qual professor está mais atrasado?

PASSO 2: Identificar se o atraso é crítico para ENEM:
         → Matemática 3ª Série: qualquer atraso é ENEM-crítico
         → Português 3ª Série: qualquer atraso é ENEM-crítico
         → Outras disciplinas: verificar competências ENEM do capítulo atrasado

PASSO 3: Conversa de Ritmo (não cobrança):
         "Professor, vi que você está no Cap. [X]. Deveria estar no [Y].
          Quero entender: o que aconteceu? Você optou por ir mais devagar
          ou houve algum imprevisto?"

PASSO 4: Plano de compactação:
         → O que pode ser coberto mais rapidamente sem perda de qualidade?
         → O que é inegociável (ENEM) e deve ser priorizado?
         → Meta: chegar ao capítulo correto em no máximo 3 semanas

DECISÃO Z: "Professor [Nome] está [N] capítulos atrás em [disciplina].
           Plano de compactação: cobrir caps [X-Y] em [N] semanas,
           priorizando competências ENEM [lista]. Revisão em [data]."
```

---

## 4.3 Navegação do Coordenador: Antes, Durante e Depois da Reunião

### ANTES DA REUNIÃO (segunda, 7h00-7h15)
```
ROTINA PRÉ-REUNIÃO (15 minutos, executável no celular):

1. Abrir e-mail/WhatsApp: chegou o PMV? (gerado automaticamente às 7h)
   → Ler o "Veredicto": VERDE / ATENÇÃO / CRISE

2. Se VERDE: não precisa abrir o Streamlit. Reunião será NORMAL (15-20 min)

3. Se ATENÇÃO: abrir 08_Alertas_Conformidade.py + 23_Alerta_Precoce_ABC.py
   → Identificar os nomes (não os percentuais)
   → Anotar os 3 nomes para a reunião (professor + aluno + ação pendente)

4. Se CRISE: abrir 10_Painel_Unificado.py + 14_Alertas_Inteligentes.py
   → Convocar direção antes da reunião
   → Preparar lista completa de nomes e histórico de intervenções

5. Verificar check binário: a ação da semana passada foi cumprida?
   → Planilha de compromissos — 30 segundos
```

### DURANTE A REUNIÃO
```
REGRAS DE NAVEGAÇÃO EM REUNIÃO:

Regra 1: Uma tela por vez. Não navegar entre páginas enquanto alguém fala.
Regra 2: Mostrar nomes, não gráficos. Gráficos são para análise, nomes são para decisão.
Regra 3: "Agora vamos olhar [página X] porque precisamos decidir [Y]" — sempre explicar
         para que serve cada abertura de tela.
Regra 4: Não deixar a tela aberta enquanto debate acontece. Fecha o Streamlit, olha para
         as pessoas, discute. Reabre quando for registrar a decisão.
Regra 5: O último ato da reunião é registrar as ações em 10_Painel_Unificado.py ou no
         Formulário de 1 Linha.

SEQUÊNCIA DE PÁGINAS POR TIPO DE REUNIÃO:

NORMAL:  09 → 05 → 20 → (fecha) → Formulário 1 Linha
ALERTA:  09 → [página do indicador amarelo] → 14 → (fecha) → Formulário 1 Linha
CRISE:   10 → 14 → [páginas específicas] → 22/20/08 → 25 → Formulário 1 Linha
ESTRAT:  07 → 17 → [páginas de análise] → 26 → 01 → Formulário 1 Linha
```

### DEPOIS DA REUNIÃO (segunda, 8h00-8h30)
```
ROTINA PÓS-REUNIÃO (30 minutos, imprescindível):

1. Registrar ações no Formulário de 1 Linha (5 min)
   → Quem, o quê, até quando

2. Enviar mensagem para cada professor/aluno/família listado (15 min)
   → Modelo: "Olá [Nome], vou passar por aí hoje [ou na terça] para conversarmos
      rapidamente sobre [assunto específico]. Pode ser às [horário]?"
   → NÃO enviar mensagem genérica. Personalizar com o dado específico.

3. Atualizar painel público da unidade (5 min)
   → % conformidade desta semana
   → Professor destaque da semana

4. Planejar o Checkpoint de quinta (5 min)
   → O que vou verificar na quinta? A ação de segunda foi cumprida?
   → Qual dado preciso olhar de novo?
```

---

## 4.4 Propostas de Novas Visualizações no Dashboard

### NOVA VISUALIZAÇÃO 1 — "Triagem 3-Semáforos" (nova aba em 09_Resumo_Semanal.py)
Três círculos coloridos grandes: PROFESSORES | ALUNOS | CLIMA
Lógica automática:
- VERDE: todos indicadores acima das metas
- AMARELO: 1-2 indicadores abaixo das metas mas acima do limiar de crise
- VERMELHO: qualquer indicador no limiar de crise

**Impacto:** Primeira tela que o coordenador vê. Decisão em 10 segundos sobre qual tipo de reunião acontece hoje.

### NOVA VISUALIZAÇÃO 2 — "Evolução Semanal de Professores" (nova aba em 13_Semaforo_Professor.py)
Gráfico de barras mostrando, para cada professor:
- Lançamentos por semana (sparkline das últimas 6 semanas)
- Tendência: melhorando, estagnado ou piorando
- Badge: "1ª semana como Crítico" / "3ª semana como Crítico" (urgência crescente)

**Impacto:** Diferencia o professor que acabou de entrar em Crítico (intervenção leve) do que está Crítico há meses (escalação necessária).

### NOVA VISUALIZAÇÃO 3 — "Mapa de Calor de Ocorrências" (nova aba em 22_Ocorrencias.py)
Matriz turma × semana com intensidade de cor proporcional ao número de ocorrências.
Permite ver em 30 segundos: qual turma tem mais concentração, em quais semanas houve pico.

**Especialmente crítico para CDR:** As 36 graves provavelmente formam um padrão visível nessa matriz.

### NOVA VISUALIZAÇÃO 4 — "Ritmo ENEM" (nova aba em 05_Progressao_SAE.py, apenas EM)
Para turmas de EM, mostrar além do capítulo SAE:
- Competências ENEM cobertas nos capítulos já avançados
- Competências ENEM ainda não cobertas e em qual capítulo estão
- Projeção: "Se o professor mantiver este ritmo, vai cobrir [X%] das competências ENEM até dezembro"

**Impacto:** Transforma o SAE de "obrigação curricular" em "ferramenta de ENEM". Aumenta adesão de professores de 3ª Série.

### NOVA VISUALIZAÇÃO 5 — "Radar de Turma" (nova funcionalidade em 19_Painel_Aluno.py)
Para cada turma, um gráfico radar com 5 eixos:
- Frequência média
- Nota média
- Ocorrências (invertido — menos = melhor)
- Engajamento SAE
- Conformidade dos professores que atendem a turma

**Uso no Conselho de Turma Digital:** Em 30 segundos, todos os presentes entendem o "perfil" da turma sem precisar navegar por 5 páginas diferentes.

---

# PARTE 5 — PROPOSTAS INOVADORAS: O QUE O PLANO DEFINITIVO NÃO FAZ

## 5.1 O Que o Plano Definitivo Deixou de Resolver

O Plano Definitivo é excelente em estrutura, cadência e accountability. Mas tem 6 lacunas críticas que esta proposta preenche:

**Lacuna 1:** Não diferencia Anos Finais de EM em nenhum dos 45 formatos de reunião.
**Lacuna 2:** Não mapeia sistematicamente as 26 páginas do dashboard — fica vago sobre "usar o Streamlit".
**Lacuna 3:** Não tem mecanismo de protagonismo estudantil (o aluno é objeto, não sujeito).
**Lacuna 4:** Não propõe nada sobre desenvolvimento profissional baseado em pares (professor→professor).
**Lacuna 5:** Não trata Gilberto Santos (coordenador de EM de BV) como figura estratégica.
**Lacuna 6:** Não tem estratégia de engajamento do SAE Digital diferenciada por segmento.

---

## 5.2 INOVAÇÃO 1 — Simulado ENEM Interno (EM, exclusivo)

**O que é:** Um simulado interno estruturado com a mesma arquitetura do ENEM — 4 cadernos (Linguagens, Ciências Humanas, Ciências da Natureza, Matemática), com questões selecionadas do banco SAE Digital.

**Quando:** 3 simulados no ano:
- 1º Simulado: Semana 12 (fins de março) — diagnóstico, sem correção pública
- 2º Simulado: Semana 30 (agosto) — os sábados letivos de 22/08 e 29/08 são o momento natural
- 3º Simulado: Semana 42 (novembro) — preparação final

**Como funciona tecnicamente:**
```
1. Banco de questões: extraído do SAE Digital via API avl-activity-bff.arcotech.io
2. Seleção automática: 10 questões por competência ENEM, distribuídas por dificuldade
3. Aplicação: presencial, mesmo horário em todas as unidades
4. Análise: fato_Notas_Historico.csv + nova tabela fato_Simulados (a criar)
5. Dashboard: nova aba em 21_Boletim_Digital.py mostrando evolução ENEM por aluno
```

**Análise pós-simulado (proposta de reunião):**
```
REUNIÃO ANÁLISE DE SIMULADO (45 min, apenas EM, após cada simulado)

[0-10 min] Resultados por turma — quais competências mais baixas?
[10-25 min] Cruzamento: alunos com SAE Digital engajado vs desengajado — há diferença?
[25-35 min] Planejamento de reforço: quais capítulos SAE cobrem as competências mais fracas?
[35-45 min] Devolutiva para alunos: como apresentar os resultados de forma motivadora?
```

**Por que o Plano Definitivo não tem isso:** Menciona simulados mas apenas como evento no calendário. Não propõe metodologia de análise pedagógica dos resultados.

---

## 5.3 INOVAÇÃO 2 — "Diário de Carreira" para 3ª Série EM

**O que é:** Um documento digital simples (1 página, atualizado trimestralmente) para cada aluno de 3ª Série, mantido pelo coordenador de EM, com:
- Nota média atual por disciplina
- Gap em relação à profissão/curso desejado (se declarado)
- Engajamento SAE Digital
- 1 força e 1 área de desenvolvimento identificadas pelo professor
- Próximo passo concreto (o que o aluno vai fazer este trimestre)

**Ferramenta:** `fato_Notas_Historico.csv` + `fato_Engajamento_SAE.csv` + formulário simples
**Responsável:** Coordenador de EM (Gilberto em BV; coordenadores secundários em CD, JG, CDR)
**Entregável:** O aluno recebe seu Diário no início de cada trimestre. Discute com o coordenador em 10 minutos.

**Por que funciona:** Alunos de 3ª Série respondem a "seu futuro está em risco" diferente de alunos de 6º Ano. O Diário de Carreira conecta o dado pedagógico (nota baixa em Matemática) ao dado de vida (quer fazer Engenharia). Cria urgência real sem ameaça.

---

## 5.4 INOVAÇÃO 3 — "Semana do Colega" (programa de mentoria entre professores)

**O que é:** Uma vez por trimestre, cada professor de Q4 (excelente) é "emparelhado" com um professor de Q2 (registra pouco, mas não zero). Durante 1 semana, eles trocam:
- 1 visita cruzada de 10 minutos (cada um observa o outro em 1 aula)
- 1 conversa de 15 minutos sobre o que observou
- 1 intenção de mudança de cada um

**Regras:**
- É voluntário para ambos (nenhum é forçado)
- O Q2 não é identificado publicamente como "fraco" — é "colega para crescer junto"
- O feedback é entre pares, não do coordenador para o professor
- O coordenador apenas facilita os emparelhamentos e registra a participação

**Por que supera o Plano Definitivo:** O plano propõe observações de aula (coordenador→professor), que têm valor mas criam hierarquia e ansiedade. A "Semana do Colega" cria aprendizagem horizontal — o professor aprende mais facilmente de outro professor do que do coordenador.

**Dashboard:** `13_Semaforo_Professor.py` para identificar os pares. `15_Resumo_Semanal_Coord.py` para registrar a participação.

---

## 5.5 INOVAÇÃO 4 — "Conselho de Alunos Digital" (EM + 9º Ano)

**O que é:** Uma reunião mensal de 20 minutos entre o coordenador e 2 representantes de cada turma de 9º Ano e EM. O coordenador apresenta:
- 3 dados da turma (frequência, notas gerais, engajamento SAE) — anonimizados
- 1 desafio que precisa da visão dos alunos
- 1 conquista para celebrar

**Os alunos respondem:**
- O que está impedindo que os colegas venham?
- O que poderia melhorar nas aulas?
- O que eles mesmos podem fazer?

**Por que é inovador:** O Plano Definitivo trata os alunos exclusivamente como objetos de monitoramento — presença, nota, Tier ABC. O Conselho de Alunos Digital os torna fontes de informação e agentes de solução. Um aluno que participou do conselho e sugeriu algo que foi implementado se torna embaixador do engajamento da turma.

**Ferramenta:** `19_Painel_Aluno.py` + `26_Dashboard_Unificado.py` (versão simplificada para mostrar aos alunos)

---

## 5.6 INOVAÇÃO 5 — "Badge System" de Reconhecimento (gamificação leve)

**O que é:** Um sistema simples de badges (não pontos, não ranking) para professores, baseado em marcos reais:

| Badge | Critério | Impacto |
|-------|----------|---------|
| Consistente | 4 semanas consecutivas com 100% de lançamento | Reconhecimento no painel público |
| Alinhado | Professor atingiu capítulo esperado no SAE por 4 semanas | Menção na Reunião de Rede |
| Impacto | Turma do professor saiu do Tier 2 para Tier 1 no ABC | Carta de reconhecimento da direção |
| Parceiro | Participou de 1 "Semana do Colega" | Badge no perfil do professor |
| Referência | Recebeu 3+ pedidos de observação de colegas | Apresentação no Mercado de Práticas |

**Implementação técnica:** Nova coluna em `dim_Professores.csv` com badges atribuídos. Exibição em `13_Semaforo_Professor.py` (aba nova) e no painel público.

**Por que supera o Plano Definitivo:** O plano tem "Celebração com Dados" nas Reuniões de Rede, mas é pontual. O Badge System cria reconhecimento contínuo, visível e verificável. O professor não precisa esperar a Reunião de Rede mensal para ser reconhecido — o badge aparece na próxima segunda.

---

## 5.7 INOVAÇÃO 6 — "Operação Presença JG" (intervenção específica de unidade)

**O que é:** Um protocolo intensivo de 6 semanas para JG, que tem a pior frequência da rede (79,6%). Vai além do que o Plano Definitivo propõe para JG.

**Semanas 1-2: Diagnóstico cirúrgico**
- Pietro e Lecinane identificam, no `20_Frequencia_Escolar.py` + `23_Alerta_Precoce_ABC.py`, os 50 alunos com menor frequência
- Para cada um: turma, série, padrão de falta (dias específicos? Após eventos? Segunda/sexta?)
- Hipótese a testar: há um cluster de alunos que faltam no mesmo dia = causa comum (trabalho, transporte, etc.)

**Semanas 3-4: Contato massivo**
- Secretaria + coordenação ligam para as famílias dos 50 alunos em 5 dias úteis
- Script de conversa: "Seu filho faltou X dias. Precisamos entender. Não é punição. É cuidado."
- Registrar motivo em formulário simples (transporte/trabalho/saúde/desengajamento/outro)

**Semanas 5-6: Intervenção por motivo**
- Transporte: mapear se há padrão de endereço → proposta de van coletiva?
- Trabalho: mapear se há alunos trabalhando informalmente → conversa sobre horário
- Desengajamento: encaminhar para Conselho de Alunos Digital
- Saúde: encaminhar para equipe de suporte

**Dashboard:** `23_Alerta_Precoce_ABC.py` atualizado diariamente. `25_Relatorio_Familia.py` para registrar contatos.
**Meta:** Em 6 semanas, sair de 79,6% para 83% — crescimento de 3,4pp em 6 semanas é ambicioso mas atingível com intervenção intensiva.

---

## 5.8 INOVAÇÃO 7 — Integração SIGA × SAE com Análise Preditiva Simples

**O que é:** Usar os dados já disponíveis (`fato_Cruzamento.csv`, `fato_Engajamento_SAE.csv`) para criar um modelo simples de predição: "Qual aluno tem mais risco de reprovar no final do ano?"

**Variáveis preditoras (todas já disponíveis):**
- Frequência acumulada (fato_Frequencia_Aluno.csv)
- Tier ABC atual (score_Aluno_ABC.csv)
- Engajamento SAE Digital (fato_Engajamento_SAE.csv)
- Ocorrências (fato_Ocorrencias.csv)
- Histórico de notas trimestres anteriores (fato_Notas_Historico.csv)

**Modelo:** Não precisa ser ML sofisticado. Uma pontuação simples (1-10) com pesos definidos pelo coordenador de acordo com a realidade da escola.

**Exemplo de fórmula:**
```
Score_Risco = (Freq_peso × (100 - Freq_atual%))
            + (ABC_peso × Tier_numerico)
            + (SAE_peso × (100 - SAE_engajamento%))
            + (Ocorr_peso × qtd_ocorrencias_graves)

Peso sugerido I Tri: Freq=40%, ABC=30%, SAE=10%, Ocorr=20%
```

**Resultado:** Uma lista ordenada dos alunos com maior risco, atualizada semanalmente. O coordenador não precisa fazer análise qualitativa para identificar quem precisa de atenção — o sistema rankeia.

**Dashboard:** Nova aba em `23_Alerta_Precoce_ABC.py` chamada "Predição de Risco" com a lista ordenada.

**Por que supera o Plano Definitivo:** O plano usa Tier ABC (baseado principalmente em frequência e notas). O Score de Risco integra QUATRO fontes de dado — muito mais poderoso para identificar antecipadamente quem vai reprovar ou evadir.

---

## 5.9 Crítica Direta ao Plano Definitivo: O Que Ele Faz de Fraco

Com respeito genuíno ao trabalho investido, estes são os pontos onde o Plano Definitivo pode melhorar:

### CRÍTICA 1: A "Filosofia" é excelente, mas os roteiros são genéricos
As partes de Filosofia (Seções 1.1 a 1.8) são as melhores do documento. Mas quando chegamos aos roteiros das reuniões (RR1 a RR10, RU1 a RU28), eles são uniformes. RU7 e RU23 têm essencialmente o mesmo formato. A variação entre reuniões não reflete a evolução real que o programa deve gerar.

**Solução desta proposta:** Os 4 roteiros-tipo por segmento são calibrados para situações reais diferentes, não para etapas de um calendário.

### CRÍTICA 2: Ensino Médio é invisível
846 linhas. Gilberto Santos aparece uma vez. A 3ª Série com SSA aparece uma vez. Não há nada sobre ENEM, sobre protagonismo estudantil no EM, sobre a diferença entre coordenar um aluno de 6º Ano e um de 3ª Série.

**Solução desta proposta:** A Parte 3 inteira é dedicada ao EM com o mesmo nível de detalhe dos Anos Finais.

### CRÍTICA 3: O Dashboard é citado mas não é operacionalizado
O Plano Definitivo menciona páginas do Streamlit nas seções de Sinais e Redes, mas nunca diz: "No bloco X da reunião Y, abra a página Z e busque a informação W para tomar a decisão V." O dashboard fica como ferramenta genérica.

**Solução desta proposta:** A Parte 4 mapeia cada uma das 26 páginas com frequência, duração de uso e fluxos de decisão específicos.

### CRÍTICA 4: Nenhum mecanismo de desenvolvimento horizontal de professores
O plano propõe desenvolvimento profissional como top-down (coordenador treina/observa professor). Isso tem valor limitado porque os professores tendem a performar para observações e voltar ao padrão depois. A aprendizagem mais efetiva acontece entre pares.

**Solução desta proposta:** A "Semana do Colega" (INOVAÇÃO 3) cria aprendizagem horizontal voluntária.

### CRÍTICA 5: Zero protagonismo estudantil
Em 846 linhas sobre como melhorar a escola, os alunos aparecem como objetos de monitoramento (Tier ABC, Alerta Precoce) e nunca como agentes de melhoria. Isso é especialmente problemático para o EM.

**Solução desta proposta:** O "Conselho de Alunos Digital" (INOVAÇÃO 4) integra os alunos como fontes de diagnóstico e agentes de solução.

---

# PARTE 6 — IMPLEMENTAÇÃO FASEADA: COMO COMEÇAR ESTA SEMANA

## 6.1 Cronograma de Implantação por Semana

### SEMANA 1 (imediata): O Mínimo Viável
**AF (Bruna Vitória, BV):**
- Configurar o "Formato TRIPÉ" para a reunião semanal de segunda
- Abrir `08_Alertas_Conformidade.py` + `23_Alerta_Precoce_ABC.py` antes de cada reunião
- Iniciar a lista de badges (apenas rastrear — não comunicar ainda)

**EM (Gilberto Santos, BV):**
- Configurar o "Formato COMPASS" para a reunião de terça
- Abrir `05_Progressao_SAE.py` como primeira tela — mudança de foco de frequência para currículo

**JG (Pietro + Lecinane):**
- Iniciar "Operação Presença JG" — identificar os 50 alunos com menor frequência
- Pietro assume exclusivamente rastreamento. Lecinane assume exclusivamente professores.

**CDR (Ana Cláudia + Vanessa):**
- Criar mapa de calor das 36 ocorrências graves: quais 3 turmas concentram mais?
- Presença física nas 3 turmas prioritárias por 2 semanas

### SEMANAS 2-4: Estabilização
- Implementar PMV automático (gerar_pmv_semanal.py) para todas as unidades
- Iniciar Formulário de 1 Linha em todas as unidades
- Realizar primeiro "Conselho de Turma Digital" em BV como piloto (turma do 7º Ano A)
- Comunicar o Badge System para os professores

### SEMANAS 5-8: Expansão
- Expandir "Conselho de Turma Digital" para todas as turmas de BV (AF)
- Iniciar "Semana do Colega" no I Tri — primeiro grupo de emparelhamentos
- Iniciar Diário de Carreira para alunos de 3ª Série (piloto BV, Gilberto conduz)
- Verificar JG: a frequência subiu de 79,6%? Se sim, celebrar e manter. Se não, escalar.

### I TRI ENCERRAMENTO: Primeira avaliação
- Medir todos os indicadores do Plano Definitivo
- MAIS: medir o que só esta proposta rastreia:
  - Quantos Conselhos de Turma Digital realizados?
  - Quantos pares participaram da Semana do Colega?
  - Evolução da frequência JG com a Operação Presença?
  - Mapa de ocorrências CDR: os padrões estão quebrados?
  - Quantos alunos de 3ª Série têm Diário de Carreira?

---

## 6.2 Tabela de Responsabilidades por Inovação

| Inovação | Responsável Principal | Suporte | Prazo para Início |
|----------|----------------------|---------|------------------|
| Formato TRIPÉ (AF) | Coordenadores de AF | Bruna Marinho (dados) | Semana 1 |
| Formato COMPASS (EM) | Gilberto Santos | Coordenadores EM outros | Semana 1 |
| Operação Presença JG | Pietro (rastreamento) + Lecinane (profs) | Direção JG | Semana 1 |
| Mapa Ocorrências CDR | Ana Cláudia + Vanessa | Bruna Marinho (dados) | Semana 1 |
| Conselho de Turma Digital | Bruna Vitória (piloto BV) | Coordenadores outros | Semana 4 |
| Semana do Colega | Coordenadores de unidade | Bruna Marinho (emparelhamentos) | Semana 6 |
| Simulado ENEM Interno | Gilberto Santos + Bruna Marinho | SAE Digital API | Semana 12 |
| Diário de Carreira 3ª Série | Gilberto Santos (piloto) | Professores de 3ª Série BV | Semana 3 |
| Badge System | Bruna Marinho (dados) | Coordenadores (comunicação) | Semana 2 |
| Conselho de Alunos Digital | Coordenadores de EM | Representantes de turma | Semana 8 |
| Score de Risco (predição) | Bruna Marinho (modelagem) | Coordenadores (validação) | Semana 5 |
| Triagem 3-Semáforos (dashboard) | Bruna Marinho | — | Semana 2 |
| Mapa de Calor Ocorrências (dashboard) | Bruna Marinho | — | Semana 3 |
| Ritmo ENEM (dashboard) | Bruna Marinho | Gilberto Santos (curadoria ENEM) | Semana 6 |
| Radar de Turma (dashboard) | Bruna Marinho | — | Semana 8 |

---

## 6.3 Indicadores Adicionais que Esta Proposta Rastreia (além dos do Plano Definitivo)

| Indicador Novo | Fonte | Frequência | Meta I Tri |
|---------------|-------|-----------|-----------|
| Conselhos de Turma Digital realizados | Formulário 1 Linha | Mensal | 4 por unidade |
| Pares "Semana do Colega" completados | Novo registro | Trimestral | 10 pares na rede |
| Alunos JG com diagnóstico de causa de falta | Formulário Operação JG | Quinzenal | 50 alunos mapeados |
| Turmas CDR com <2 graves/semana | fato_Ocorrencias.csv | Semanal | 80% das turmas |
| Alunos 3ª Série com Diário de Carreira ativo | Novo registro | Trimestral | 100% dos alunos 3ª Série BV |
| Professores com badge "Consistente" | dim_Professores.csv | Mensal | 20% da rede |
| Alunos de EM que participaram do Conselho | Novo registro | Mensal | 100% das turmas EM |
| Alunos com Score de Risco > 7 (alto risco) | Score_Risco calculado | Semanal | Reduzir de X para X-20% |

---

# CONCLUSÃO — POR QUE ESTA PROPOSTA É MELHOR

## O que esta proposta mantém do Plano Definitivo
- Filosofia "Impacto Concentrado" e "Decisão Antes do Dado" — excelente, mantida integralmente
- Estrutura de 45 reuniões (10 RR + 35 RU) — mantida
- 3 prioridades por trimestre — mantida
- PMV semanal automático — mantida e operacionalizada
- Sistema de escalação em 4 níveis — mantido
- 7 indicadores LEAD + 5 eixos de contexto — mantidos
- Accountability com check binário — mantido
- Celebração com dados — mantida

## O que esta proposta adiciona
1. **Diferenciação completa AF vs EM** — Anos Finais e Ensino Médio têm filosofias, formatos, métricas e inovações diferentes
2. **Mapa operacional das 26 páginas** — o coordenador sabe exatamente qual página abrir em qual momento
3. **4 fluxos de decisão detalhados** — "Se X vermelho → abre Y → decide Z"
4. **Rotina pré e pós reunião** — o que o coordenador faz antes e depois, não só durante
5. **Gilberto Santos como figura estratégica** — coordenador de EM de BV com papel de referência para a rede
6. **7 inovações que o plano não tem** — Simulado ENEM, Diário de Carreira, Semana do Colega, Conselho de Alunos, Badge System, Operação Presença JG, Score de Risco
7. **5 novas visualizações de dashboard** — Triagem 3-Semáforos, Evolução Semanal, Mapa de Calor, Ritmo ENEM, Radar de Turma
8. **Cronograma de implantação semana a semana** — sabe o que fazer hoje, não só no ano

## A Aposta Central desta Proposta

O Plano Definitivo trata todos os professores, todos os alunos e todas as unidades com o mesmo protocolo. Esta proposta aposta no contrário: **quanto mais específica a intervenção, mais potente ela é**.

CDR não precisa de mais reuniões — precisa de um coordenador fisicamente presente nas 3 turmas mais críticas por 3 semanas.

JG não precisa de pauta nova — precisa de Pietro na porta todos os dias e das 50 famílias ligadas em uma semana.

A 3ª Série EM de BV não precisa de mais conformidade SIGA — precisa de um professor de Física que entenda que o capítulo 7 do SAE cobre a competência ENEM de eletromagnetismo que 73% dos seus alunos erraram no simulado.

Gilberto Santos não precisa de uma reunião genérica de rede — precisa de um roteiro que reconheça que ele é o único coordenador exclusivo de EM da rede, com alunos que têm projeto de vida, pressão de vestibular e capacidade de protagonismo que nenhum aluno de 6º Ano ainda tem.

**Este é o argumento desta proposta:** o Plano Definitivo é o melhor plano estrutural já feito para o ELO. Mas estrutura sem especificidade é arquitetura sem ocupação. Esta proposta ocupa o espaço que o plano abriu.

---

*COMPETIDOR A — PROPOSTA PEDS 2026*
*Colégio ELO | Fevereiro de 2026*
*Baseada nos dados reais da Semana 4 + 26 páginas do Dashboard Streamlit*
*Complemento ao PEDS_2026_PLANO_DEFINITIVO.md — não substitui, especializa*
