"""
Configuracao do PEEX/PEDS 2026 — Programa de Excelencia.
Fonte unica de verdade para fases, prioridades, reunioes, metas, eixos e escalacao.
Extraido de: PEEX_2026_PLANO_DEFINITIVO.md
"""

# ========== FASES E PRIORIDADES ==========

FASES = {
    1: {
        'nome': 'SOBREVIVENCIA',
        'semanas': (1, 15),
        'periodo': '27/jan - 10/mai',
        'dias_letivos': 69,
        'cor': '#c62828',
        'prioridades': [
            {'id': 'P1', 'nome': 'Registro SIGA', 'baseline': 43.7, 'meta': 70,
             'indicador': 'pct_conformidade_media', 'unidade_medida': '%'},
            {'id': 'P2', 'nome': 'Feedback coordenacao', 'baseline': 1, 'meta': 40,
             'indicador': 'feedbacks_dados', 'unidade_medida': '/107'},
            {'id': 'P3', 'nome': 'Presenca alunos', 'baseline': 84.7, 'meta': 88,
             'indicador': 'frequencia_media', 'unidade_medida': '%'},
        ],
    },
    2: {
        'nome': 'CONSOLIDACAO',
        'semanas': (16, 33),
        'periodo': '11/mai - 12/set',
        'dias_letivos': 68,
        'cor': '#e65100',
        'prioridades': [
            {'id': 'P4', 'nome': 'Alinhamento SAE', 'baseline': 12.9, 'meta': 55,
             'indicador': 'pct_prof_no_ritmo', 'unidade_medida': '%'},
            {'id': 'P5', 'nome': 'Observacao de aula', 'baseline': 0, 'meta': 250,
             'indicador': 'observacoes_aula', 'unidade_medida': ' obs'},
            {'id': 'P6', 'nome': 'Intervencao academica', 'baseline': 344, 'meta': 120,
             'indicador': 'alunos_atencao_critico', 'unidade_medida': ' alunos'},
        ],
    },
    3: {
        'nome': 'EXCELENCIA',
        'semanas': (34, 47),
        'periodo': '14/set - 18/dez',
        'dias_letivos': 68,
        'cor': '#2e7d32',
        'prioridades': [
            {'id': 'P7', 'nome': 'Avaliacao formativa', 'baseline': 0, 'meta': 80,
             'indicador': 'pct_exit_ticket', 'unidade_medida': '%'},
            {'id': 'P8', 'nome': 'Cobertura curricular', 'baseline': 12.9, 'meta': 65,
             'indicador': 'pct_prof_no_ritmo', 'unidade_medida': '%'},
            {'id': 'P9', 'nome': 'Planejamento 2027', 'baseline': 0, 'meta': 4,
             'indicador': 'unidades_com_plano', 'unidade_medida': ' unid'},
        ],
    },
}


def fase_atual(semana):
    """Retorna numero da fase (1, 2 ou 3) e dict da fase."""
    for n, fase in FASES.items():
        ini, fim = fase['semanas']
        if ini <= semana <= fim:
            return n, fase
    return 1, FASES[1]


# ========== 5 EIXOS DE CONTEXTO ==========

EIXOS = [
    {
        'id': 'A', 'nome': 'Conformidade', 'icone': 'A',
        'foco': 'Lancamentos, alinhamento SAE, ritmo',
        'cor': '#1565C0',
        'dashboards': ['08_Alertas_Conformidade', '13_Semaforo_Professor'],
        'csvs': ['score_Professor.csv'],
    },
    {
        'id': 'B', 'nome': 'Frequencia', 'icone': 'B',
        'foco': 'Presenca, evasao, busca ativa',
        'cor': '#2E7D32',
        'dashboards': ['20_Frequencia_Escolar', '23_Alerta_Precoce_ABC'],
        'csvs': ['score_Aluno_ABC.csv'],
    },
    {
        'id': 'C', 'nome': 'Desempenho', 'icone': 'C',
        'foco': 'Notas, aprovacao, progressao',
        'cor': '#E65100',
        'dashboards': ['21_Boletim_Digital', '05_Progressao_SAE'],
        'csvs': ['fato_Notas_Historico.csv'],
    },
    {
        'id': 'D', 'nome': 'Clima', 'icone': 'D',
        'foco': 'Ocorrencias, disciplina',
        'cor': '#AD1457',
        'dashboards': ['22_Ocorrencias', '14_Alertas_Inteligentes'],
        'csvs': ['fato_Ocorrencias.csv'],
    },
    {
        'id': 'E', 'nome': 'Engajamento Digital', 'icone': 'E',
        'foco': 'SAE plataforma, cruzamento SIGA x SAE',
        'cor': '#7B1FA2',
        'dashboards': ['24_Cruzamento_SIGA_SAE'],
        'csvs': ['fato_Engajamento_SAE.csv'],
    },
]


# ========== 7 INDICADORES LEAD ==========

INDICADORES_LEAD = [
    {
        'id': 'L1', 'nome': 'Taxa de lancamento semanal',
        'pergunta': 'Quantos % dos professores lancaram esta semana?',
        'fonte': 'fato_Aulas.csv',
        'indicador_resumo': 'pct_conformidade_media',
        'meta_tri1': 70, 'meta_ano': 80,
        'cor': '#1565C0',
    },
    {
        'id': 'L2', 'nome': 'Alunos ausentes hoje',
        'pergunta': 'Quantos faltaram? Quais sao reincidentes?',
        'fonte': 'fato_Frequencia_Aluno.csv',
        'indicador_resumo': None,
        'meta_tri1': None, 'meta_ano': None,
        'cor': '#2E7D32',
    },
    {
        'id': 'L3', 'nome': 'Alunos no limiar (75-80%)',
        'pergunta': 'Quantos podem cair para reprovacao?',
        'fonte': 'score_Aluno_ABC.csv',
        'indicador_resumo': None,
        'meta_tri1': 300, 'meta_ano': 80,
        'cor': '#F57C00',
    },
    {
        'id': 'L4', 'nome': 'Ocorrencias graves da semana',
        'pergunta': 'Quantas graves? Quem?',
        'fonte': 'fato_Ocorrencias.csv',
        'indicador_resumo': 'ocorr_graves',
        'meta_tri1': 4, 'meta_ano': 1,
        'cor': '#C62828',
    },
    {
        'id': 'L5', 'nome': 'Professores sem lancamento 2+ sem',
        'pergunta': 'Quem sumiu do sistema?',
        'fonte': 'score_Professor.csv',
        'indicador_resumo': 'professores_criticos',
        'meta_tri1': 20, 'meta_ano': 5,
        'cor': '#4A148C',
    },
    {
        'id': 'L6', 'nome': 'Gap de capitulo SAE',
        'pergunta': 'Quantos profs estao 2+ capitulos atras?',
        'fonte': 'dim_Progressao_SAE.csv',
        'indicador_resumo': 'pct_prof_no_ritmo',
        'meta_tri1': 35, 'meta_ano': 65,
        'cor': '#00695C',
    },
    {
        'id': 'L7', 'nome': 'Alunos tier 2/3 sem intervencao',
        'pergunta': 'Quantos em risco sem acao registrada?',
        'fonte': 'score_Aluno_ABC.csv',
        'indicador_resumo': None,
        'meta_tri1': None, 'meta_ano': None,
        'cor': '#BF360C',
    },
]


# ========== CALENDARIO DE 45 REUNIOES ==========

REUNIOES = [
    # I Trimestre — 13 reuniões
    {'id': 1,  'cod': 'RR1',  'data': '2026-02-02', 'semana': 2,  'tipo_reuniao': 'RR', 'formato': 'E',
     'titulo': 'Choque de Realidade', 'foco': 'Registro como prioridade #1'},
    {'id': 2,  'cod': 'RU1',  'data': '2026-02-09', 'semana': 3,  'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Check registro', 'foco': 'Lista nominal: quem registrou, quem nao. Visita corpo a corpo.'},
    {'id': 3,  'cod': 'RU2',  'data': '2026-02-16', 'semana': 4,  'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Check registro + Dossie', 'foco': 'Dossie atualizado. Se lista nao diminuiu, mudar metodo.'},
    {'id': 4,  'cod': 'RU3',  'data': '2026-02-23', 'semana': 5,  'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Pre-Encontro Familias', 'foco': '5 alunos em maior risco: conversa com familia ANTES do Encontro.'},
    {'id': 5,  'cod': 'RR2',  'data': '2026-03-02', 'semana': 6,  'tipo_reuniao': 'RR', 'formato': 'FO',
     'titulo': 'Primeiro Balanco + Feedback', 'foco': 'Conformidade Sem 2 vs Sem 6. Inicio foco Feedback.'},
    {'id': 6,  'cod': 'RU4',  'data': '2026-03-09', 'semana': 7,  'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Registro + Feedback', 'foco': 'Primeiras "Conversas de 10 min" com professores.'},
    {'id': 7,  'cod': 'RU5',  'data': '2026-03-16', 'semana': 8,  'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Check feedback + Contrato', 'foco': 'Contrato de Pratica Docente. Plano B se <53.7%.'},
    {'id': 8,  'cod': 'RU6',  'data': '2026-03-23', 'semana': 9,  'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Pre-Pascoa', 'foco': 'Registros antes do feriado. Nenhum professor sai sem atualizar.'},
    {'id': 9,  'cod': 'RR3',  'data': '2026-03-30', 'semana': 10, 'tipo_reuniao': 'RR', 'formato': 'FO',
     'titulo': 'Revisao Mid-Tri + Presenca', 'foco': 'Protocolo Busca Ativa 3 niveis. Plano B se nao +10pp.'},
    {'id': 10, 'cod': 'RU7',  'data': '2026-04-06', 'semana': 11, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Busca ativa + Clima', 'foco': 'Termometro de Clima por Turma. Busca ativa JG/CDR.'},
    {'id': 11, 'cod': 'RU8',  'data': '2026-04-20', 'semana': 13, 'tipo_reuniao': 'RU', 'formato': 'FO',
     'titulo': 'Inclusao/PEI + Escalacao', 'foco': 'Mapa de Barreiras. Escalacao CDR se graves nao diminuiram.'},
    {'id': 12, 'cod': 'RU9',  'data': '2026-04-27', 'semana': 14, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Feedback individual', 'foco': 'Quem evoluiu (celebrar). Quem nao (conversa franca). Prep encerramento.'},
    {'id': 13, 'cod': 'RR4',  'data': '2026-05-04', 'semana': 15, 'tipo_reuniao': 'RR', 'formato': 'E',
     'titulo': 'Encerramento I Tri', 'foco': 'Balanco completo + Prioridades II Tri + Celebracao.'},

    # II Trimestre — 13 reuniões + 4 RR = 17 total (ids 14-30)
    {'id': 14, 'cod': 'RR5',  'data': '2026-05-11', 'semana': 16, 'tipo_reuniao': 'RR', 'formato': 'E',
     'titulo': 'Abertura II Tri', 'foco': 'Alinhamento SAE + Inicio observacoes de aula.'},
    {'id': 15, 'cod': 'RU10', 'data': '2026-05-18', 'semana': 17, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Conversas de Ritmo SAE', 'foco': 'Protocolo de Ritmo: capitulo atual vs esperado por professor.'},
    {'id': 16, 'cod': 'RU11', 'data': '2026-05-25', 'semana': 18, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Avaliacao formativa', 'foco': 'Check SAE + Rubrica de Devolutiva ELO.'},
    {'id': 17, 'cod': 'RU12', 'data': '2026-06-01', 'semana': 19, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Ciclos tematicos', 'foco': 'Observacao de aula: 1 dimensao por ciclo de 3 semanas.'},
    {'id': 18, 'cod': 'RU13', 'data': '2026-06-08', 'semana': 20, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Contratos + Familias', 'foco': 'Revisao Contratos de Pratica. Comunicacao pre-ferias.'},
    {'id': 19, 'cod': 'RR6',  'data': '2026-06-15', 'semana': 21, 'tipo_reuniao': 'RR', 'formato': 'FO',
     'titulo': 'Pre-ferias', 'foco': 'Balanco 5 semanas II Tri. Boletim Narrativo piloto. Comunicacao familias.'},
    {'id': 20, 'cod': 'RU14', 'data': '2026-06-22', 'semana': 22, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Ultima antes ferias', 'foco': 'Alunos risco pre-ferias. Profs em gap SAE. Boletim Narrativo piloto.'},
    # Férias sem 23-27
    {'id': 21, 'cod': 'RR7',  'data': '2026-08-03', 'semana': 28, 'tipo_reuniao': 'RR', 'formato': 'FO',
     'titulo': 'Retorno ferias', 'foco': 'Quem voltou? Dashboard presenca 1o dia. 6 semanas ate fim II Tri.'},
    {'id': 22, 'cod': 'RU15', 'data': '2026-08-10', 'semana': 29, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Reativacao rotinas', 'foco': 'Check presenca retorno. Reativar rotina de registro.'},
    {'id': 23, 'cod': 'RU16', 'data': '2026-08-17', 'semana': 30, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Pre-simulado', 'foco': 'Observacoes intensivas. Preparacao Simulado 22/08.'},
    {'id': 24, 'cod': 'RU17', 'data': '2026-08-24', 'semana': 31, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Analise Simulado', 'foco': 'Resultados Simulado 22/08. Turmas abaixo do esperado.'},
    {'id': 25, 'cod': 'RU18', 'data': '2026-08-31', 'semana': 32, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Tecnologia SAE', 'foco': 'Engajamento digital. Design experiencias hibridas Caps 7-8.'},
    {'id': 26, 'cod': 'RR8',  'data': '2026-09-08', 'semana': 33, 'tipo_reuniao': 'RR', 'formato': 'E',
     'titulo': 'Encerramento II Tri', 'foco': 'Balanco I vs II Tri. Grafico evolucao. Prioridades III Tri.'},

    # III Trimestre — 15 reuniões (ids 27-45)
    {'id': 27, 'cod': 'RR9',  'data': '2026-09-14', 'semana': 34, 'tipo_reuniao': 'RR', 'formato': 'E',
     'titulo': 'Abertura III Tri', 'foco': 'Avaliacao formativa + Ticket de Saida + Cobertura curricular.'},
    {'id': 28, 'cod': 'RU19', 'data': '2026-09-21', 'semana': 35, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Cobertura + Tickets', 'foco': 'Garantia cobertura curricular. Alinhamento SSA 3a Serie.'},
    {'id': 29, 'cod': 'RU20', 'data': '2026-09-28', 'semana': 36, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Check tickets + SAE', 'foco': 'Ritmo SAE Caps 9-10. Professores usando Ticket de Saida.'},
    {'id': 30, 'cod': 'RU21', 'data': '2026-10-05', 'semana': 37, 'tipo_reuniao': 'RU', 'formato': 'FO',
     'titulo': 'Revisao Mid-Tri III', 'foco': 'Profs 2+ caps atrasados = plano emergencial de compactacao.'},
    {'id': 31, 'cod': 'RU22', 'data': '2026-10-19', 'semana': 39, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Cultura de escola', 'foco': 'Manifesto ELO. Observacoes focadas. Validacao com alunos.'},
    {'id': 32, 'cod': 'RU23', 'data': '2026-10-26', 'semana': 40, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Check triplice III Tri', 'foco': 'Conformidade + Frequencia + Notas. Visao integrada.'},
    {'id': 33, 'cod': 'RU24', 'data': '2026-11-03', 'semana': 41, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Inclusao: PEIs + Adaptacoes', 'foco': 'Revisao PEIs. Catalogo de Adaptacoes ELO.'},
    {'id': 34, 'cod': 'RU25', 'data': '2026-11-09', 'semana': 42, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Familias: Pacto Encerramento', 'foco': 'Engajamento familiar. Avaliacao Boletim Narrativo.'},
    {'id': 35, 'cod': 'RU26', 'data': '2026-11-16', 'semana': 43, 'tipo_reuniao': 'RU', 'formato': 'FO',
     'titulo': 'Transicoes: Passagem', 'foco': 'Protocolo de Passagem Pedagogica. 9o -> 1a Serie EM.'},
    {'id': 36, 'cod': 'RU27', 'data': '2026-11-23', 'semana': 44, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Feedback anual', 'foco': 'Cartas de Crescimento. Avaliacao Contratos de Pratica.'},
    {'id': 37, 'cod': 'RU28', 'data': '2026-11-30', 'semana': 45, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Pares pedagogicos', 'foco': 'Formacao para 2027. Cada professor escolhe 1 par.'},
    {'id': 38, 'cod': 'RU29', 'data': '2026-12-01', 'semana': 45, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Recuperacao final', 'foco': 'Plano de recuperacao dos alunos em risco final.'},
    {'id': 39, 'cod': 'RU30', 'data': '2026-12-07', 'semana': 46, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Encerramento operacional', 'foco': 'Notas fechadas. Documentacao completa.'},
    {'id': 40, 'cod': 'RU31', 'data': '2026-12-14', 'semana': 47, 'tipo_reuniao': 'RU', 'formato': 'F',
     'titulo': 'Fechamento', 'foco': 'Ultimo check do ano. Tudo documentado.'},
    {'id': 45, 'cod': 'RR10', 'data': '2026-12-07', 'semana': 46, 'tipo_reuniao': 'RR', 'formato': 'E',
     'titulo': 'Encerramento Anual', 'foco': 'Balanco completo + Aprendizados + Planejamento 2027 + Reconhecimento.'},
]


FORMATOS_REUNIAO = {
    'F':  {'nome': 'FLASH',       'duracao': 30, 'cor': '#43A047', 'icone': '⚡'},
    'FO': {'nome': 'FOCO',        'duracao': 45, 'cor': '#FFA000', 'icone': '🔍'},
    'C':  {'nome': 'CRISE',       'duracao': 60, 'cor': '#C62828', 'icone': '🚨'},
    'E':  {'nome': 'ESTRATEGICA', 'duracao': 90, 'cor': '#1565C0', 'icone': '🎯'},
}


# ========== ROTEIROS DIFERENCIADOS (da Sintese Final Sec 2.3) ==========

ROTEIROS = {
    'FLASH': {
        'quando': 'Tudo verde, sem urgencias',
        'duracao': '15-20 min',
        'saida_obrigatoria': '1 nome + 1 acao + 1 prazo',
        'blocos': [
            {'tempo': '0-3 min', 'nome': 'Check-in', 'script': 'Como esta a energia da equipe? Uma palavra por pessoa.',
             'pagina': None},
            {'tempo': '3-8 min', 'nome': 'Numeros-chave', 'script': 'Conformidade, frequencia, missoes. So os numeros, sem debate.',
             'pagina': '00_centro_inteligencia'},
            {'tempo': '8-13 min', 'nome': 'Foco unico', 'script': 'Qual e O problema da semana? Um so. Quem resolve? Ate quando?',
             'pagina': 'preparador_reuniao'},
            {'tempo': '13-18 min', 'nome': 'Compromisso', 'script': 'Cada diretor registra 1 compromisso. Nome, acao, prazo. Pronto.',
             'pagina': '07_plano_acao'},
            {'tempo': '18-20 min', 'nome': 'Celebracao', 'script': 'Qual foi a melhor coisa que aconteceu esta semana? Terminamos positivo.',
             'pagina': None},
        ],
    },
    'FOCO': {
        'quando': '1+ indicador amarelo',
        'duracao': '30-45 min',
        'saida_obrigatoria': 'Diagnostico + plano de 2 semanas com responsaveis',
        'blocos': [
            {'tempo': '0-5 min', 'nome': 'Raizes', 'script': 'Ancoragem: como voces estao? Roda rapida. Depois, o foco de hoje.',
             'pagina': None},
            {'tempo': '5-15 min', 'nome': 'Diagnostico', 'script': 'Vamos entender POR QUE este indicador esta amarelo. Dados na tela. Cada unidade explica seu contexto.',
             'pagina': '00_centro_inteligencia'},
            {'tempo': '15-25 min', 'nome': 'Plano de Acao', 'script': 'O que cada unidade vai fazer nas proximas 2 semanas? Seja especifico: quem, o que, ate quando.',
             'pagina': '07_plano_acao'},
            {'tempo': '25-35 min', 'nome': 'Polinizacao', 'script': 'Quem ja resolveu isso? Compartilhe a estrategia. Quem precisa, anote.',
             'pagina': '13_polinizacao'},
            {'tempo': '35-45 min', 'nome': 'Compromissos + Chuva', 'script': 'Registrem os compromissos. Prazo: 2 semanas. Revisaremos na proxima FOCO. Celebracao: 1 conquista cada.',
             'pagina': '22_compromissos'},
        ],
    },
    'CRISE': {
        'quando': 'Vermelho confirmado em 1+ indicador',
        'duracao': '45-60 min',
        'saida_obrigatoria': 'Declaracao de crise + responsavel unico + plano 48h',
        'blocos': [
            {'tempo': '0-5 min', 'nome': 'Declaracao', 'script': 'Estamos em modo CRISE. Isso nao e panico, e foco. Vou apresentar os dados e precisamos de um plano em 48 horas.',
             'pagina': None},
            {'tempo': '5-15 min', 'nome': 'Dados Criticos', 'script': 'Os numeros que nos trouxeram aqui. Sem julgamento, so fatos. Cada unidade afetada apresenta.',
             'pagina': '20_sinais_vitais'},
            {'tempo': '15-30 min', 'nome': '5 Porques', 'script': 'Vamos aplicar os 5 Porques. Por que este indicador esta vermelho? Por que isso aconteceu? Por que nao foi detectado antes? Por que a acao anterior nao funcionou? Qual e a causa raiz?',
             'pagina': 'preparador_reuniao'},
            {'tempo': '30-45 min', 'nome': 'Plano 48h', 'script': 'Responsavel unico para este problema. O que vai ser feito em 48 horas. Sem delegacao excessiva, uma pessoa dona do problema.',
             'pagina': '07_plano_acao'},
            {'tempo': '45-55 min', 'nome': 'Escala e Suporte', 'script': 'O que o responsavel precisa de mim (CEO) e da rede? Vou liberar o que for necessario. Proximo check: amanha as 17h.',
             'pagina': '21_escalacoes'},
            {'tempo': '55-60 min', 'nome': 'Encerramento', 'script': 'Crise nao e fracasso, e oportunidade de mostrar quem somos. Vamos resolver juntos.',
             'pagina': None},
        ],
        'protocolos_unidade': {
            'JG': 'Pietro + secretaria ligam no mesmo dia. Lecinane vai pessoalmente. Foco: frequencia.',
            'CDR': 'Mapa de calor de ocorrencias. 3 turmas-foco. Presenca fisica da coordenacao 5 dias consecutivos.',
            'BV': 'Bruna Vitoria + Gilberto dividem lista. 5 min com cada professor envolvido em 48h.',
            'CD': '15+ dias sem presenca = verificar matricula ativa. Alline/Elisangela/Vanessa: 1 turma cada.',
        },
    },
    'ESTRATEGICA': {
        'quando': 'Inicio, meio ou fim de trimestre',
        'duracao': '60-90 min',
        'saida_obrigatoria': 'Balanco completo + 3 metas proximo periodo + celebracao formal',
        'blocos': [
            {'tempo': '0-10 min', 'nome': 'Raizes Profundas', 'script': 'Antes dos numeros: como foi este periodo para voces? O que aprendemos? Roda de 2 min cada.',
             'pagina': None},
            {'tempo': '10-30 min', 'nome': 'Balanco Completo', 'script': 'Vamos revisar cada eixo: Conformidade, Frequencia, Desempenho, Clima, Engajamento. Grafico de evolucao do trimestre inteiro.',
             'pagina': '00_centro_inteligencia'},
            {'tempo': '30-45 min', 'nome': 'Metas vs Realidade', 'script': 'Quais metas atingimos? Quais nao? POR QUE? Sem desculpas, com aprendizados.',
             'pagina': '02_simulador'},
            {'tempo': '45-60 min', 'nome': 'Proximo Periodo', 'script': '3 prioridades para o proximo trimestre. Cada unidade propoe as suas. Rede consolida.',
             'pagina': '10_peex_adaptativo'},
            {'tempo': '60-75 min', 'nome': 'Reconhecimento', 'script': 'Estrelas do trimestre. Quem mais evoluiu. Quem mais ajudou. Quem mais se superou. Certificado simbolico.',
             'pagina': '04_ranking_rede'},
            {'tempo': '75-90 min', 'nome': 'Celebracao', 'script': 'Fechamos o ciclo. Momento de gratidao. Cada pessoa diz 1 coisa que agradece. Foto da equipe.',
             'pagina': None},
        ],
    },
}


# ========== DETECAO AUTOMATICA DE FORMATO ==========

def detectar_formato_reuniao(missoes_rede, resumo_df=None, semana=None):
    """Detecta o formato correto de reuniao baseado nos indicadores atuais.

    Prioridade:
    1. Inicio/meio/fim de tri -> ESTRATEGICA
    2. Vermelho confirmado -> CRISE
    3. 1+ amarelo -> FOCO
    4. Tudo verde -> FLASH

    Args:
        missoes_rede: dict unidade -> lista de missoes
        resumo_df: DataFrame do resumo executivo (opcional)
        semana: semana letiva (opcional, para detectar transicao de tri)

    Returns:
        str: 'FLASH', 'FOCO', 'CRISE' ou 'ESTRATEGICA'
    """
    import pandas as pd

    # 1. Verificar transicao de trimestre
    if semana:
        semanas_estrategicas = {1, 2, 15, 16, 33, 34, 46, 47}
        if semana in semanas_estrategicas:
            return 'ESTRATEGICA'

    # 2. Contar urgentes
    total_urgentes = sum(
        len([m for m in ms if m.get('nivel') == 'URGENTE'])
        for ms in missoes_rede.values()
    ) if missoes_rede else 0

    # 3. Verificar conformidade critica
    tem_vermelho = False
    tem_amarelo = False
    if resumo_df is not None and not resumo_df.empty:
        unidades = resumo_df[resumo_df['unidade'] != 'TOTAL']
        for _, row in unidades.iterrows():
            conf = row.get('pct_conformidade_media', 0)
            if conf < 40:
                tem_vermelho = True
            elif conf < 60:
                tem_amarelo = True

    if total_urgentes >= 5 or tem_vermelho:
        return 'CRISE'
    if total_urgentes >= 3 or tem_amarelo:
        return 'FOCO'
    return 'FLASH'


def proxima_reuniao(semana):
    """Retorna a proxima reuniao (ou reuniao da semana atual)."""
    for r in REUNIOES:
        if r['semana'] >= semana:
            return r
    return REUNIOES[-1]


def reunioes_do_trimestre(trimestre):
    """Retorna reunioes de um trimestre especifico."""
    fase = FASES.get(trimestre, FASES[1])
    ini, fim = fase['semanas']
    return [r for r in REUNIOES if ini <= r['semana'] <= fim]


def reuniao_anterior(semana):
    """Retorna a reuniao mais recente (passada)."""
    passadas = [r for r in REUNIOES if r['semana'] < semana]
    return passadas[-1] if passadas else None


# ========== METAS SMART ==========

METAS_SMART = [
    {'eixo': 'A', 'indicador': 'Conformidade media', 'baseline': 43.7,
     'meta_tri1': 70, 'meta_tri2': 78, 'meta_ano': 80, 'unidade': '%', 'campo_resumo': 'pct_conformidade_media'},
    {'eixo': 'A', 'indicador': 'Professores criticos', 'baseline': 41,
     'meta_tri1': 20, 'meta_tri2': 10, 'meta_ano': 5, 'unidade': '', 'campo_resumo': 'professores_criticos',
     'inverso': True},
    {'eixo': 'A', 'indicador': 'Profs no ritmo SAE', 'baseline': 12.9,
     'meta_tri1': 35, 'meta_tri2': 55, 'meta_ano': 65, 'unidade': '%', 'campo_resumo': 'pct_prof_no_ritmo'},
    {'eixo': 'B', 'indicador': 'Frequencia media', 'baseline': 84.7,
     'meta_tri1': 88, 'meta_tri2': 89, 'meta_ano': 90, 'unidade': '%', 'campo_resumo': 'frequencia_media'},
    {'eixo': 'B', 'indicador': 'Alunos freq >90%', 'baseline': 54.1,
     'meta_tri1': 65, 'meta_tri2': 72, 'meta_ano': 78, 'unidade': '%', 'campo_resumo': 'pct_freq_acima_90'},
    {'eixo': 'B', 'indicador': 'Alunos em risco', 'baseline': 18.4,
     'meta_tri1': 15, 'meta_tri2': 12, 'meta_ano': 10, 'unidade': '%', 'campo_resumo': 'pct_alunos_risco',
     'inverso': True},
    {'eixo': 'C', 'indicador': 'Media de notas', 'baseline': 8.3,
     'meta_tri1': 8.0, 'meta_tri2': 8.0, 'meta_ano': 8.0, 'unidade': '', 'campo_resumo': 'media_notas'},
    {'eixo': 'D', 'indicador': 'Ocorrencias graves', 'baseline': 53,
     'meta_tri1': 26, 'meta_tri2': 13, 'meta_ano': 20, 'unidade': '', 'campo_resumo': 'ocorr_graves',
     'inverso': True},
]


# ========== DIFERENCIACAO POR UNIDADE ==========

DIFERENCIACAO_UNIDADE = {
    'BV': {
        'foco': 'Referencia — meta 80% conformidade em 4 semanas',
        'cor': '#1976D2',
        'coordenadores': 'Bruna Vitoria (6-9o), Gilberto (EM)',
        'escalacao': '>5 professores criticos sem feedback em 2+ semanas',
    },
    'CD': {
        'foco': 'Equilibrio — 3 coordenadoras dividem carga',
        'cor': '#388E3C',
        'coordenadores': 'Alline, Elisangela, Vanessa',
        'escalacao': 'Evasao >3 alunos/semana',
    },
    'JG': {
        'foco': 'Frequencia — 79,6%, 25% alunos em risco',
        'cor': '#F57C00',
        'coordenadores': 'Lecinane, Pietro',
        'escalacao': 'Frequencia semanal <75%',
    },
    'CDR': {
        'foco': 'Ocorrencias — 36 de 53 graves da rede (68%)',
        'cor': '#7B1FA2',
        'coordenadores': 'Ana Claudia, Vanessa',
        'escalacao': '>6 ocorrencias graves em 1 semana',
    },
}


# ========== ESCALACAO ==========

NIVEIS_ESCALACAO = [
    {'nivel': 1, 'nome': 'Informar', 'quando': 'Amarelo por 2+ semanas',
     'acao_direcao': 'Toma ciencia. Nenhuma acao.', 'cor': '#FFA000'},
    {'nivel': 2, 'nome': 'Pedir apoio', 'quando': 'Vermelho confirmado OU coordenador sem capacidade',
     'acao_direcao': 'Participa da proxima FOCO.', 'cor': '#E65100'},
    {'nivel': 3, 'nome': 'Intervencao direta', 'quando': 'Prof critico 3+ feedbacks / Aluno tier 3 4+ sem / Freq <75% 3+ sem',
     'acao_direcao': 'Conversa de desempenho / Reuniao familia / Plano de crise.', 'cor': '#C62828'},
    {'nivel': 4, 'nome': 'Crise institucional', 'quando': 'Evasao >5% / Incidente grave / Conformidade <30%',
     'acao_direcao': 'Plano de crise em 48h.', 'cor': '#880E4F'},
]


# ========== MARCOS TRIMESTRAIS (CHECKLIST) ==========

MARCOS = {
    1: [
        'Conformidade >=70%',
        '40+ feedbacks registrados',
        'Frequencia JG >=85%',
        'CDR graves <=4/semana',
        'Todos os 41 professores criticos contatados',
        'Protocolo de Busca Ativa funcionando',
        'PMV enviado toda segunda sem falha',
    ],
    2: [
        '55%+ professores no ritmo SAE',
        '250+ observacoes de aula realizadas',
        'Plano individual para cada aluno tier 2/3',
        'Rubrica de Devolutiva em uso',
        'Boletim Narrativo pilotado em 8 turmas',
        'Zero professores criticos persistentes (>20 sem)',
    ],
    3: [
        'Conformidade >=80%',
        '107/107 professores com ao menos 1 feedback',
        'Frequencia >=90%',
        'Ticket de Saida semanal por 80%+ profs',
        'Caps 1-12 cobertos em todas as disciplinas',
        'Protocolo de Passagem preenchido 100%',
        'Pares Pedagogicos definidos para 2027',
        'Planejamento 2027 com 3 prioridades por unidade',
    ],
}
