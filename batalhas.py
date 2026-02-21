"""
Motor de deteccao e priorizacao de batalhas semanais.
Centraliza logica de negocios separada da UI.
Cada batalha tem: tipo, nivel, score, frase_humana, contexto, acoes, links.
"""

import math
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado, _hoje,
    carregar_fato_aulas, carregar_horario_esperado,
    carregar_ocorrencias, carregar_frequencia_alunos,
    carregar_alunos, filtrar_ate_hoje,
    UNIDADES_NOMES, CONFORMIDADE_CRITICO, CONFORMIDADE_BAIXO,
    THRESHOLD_FREQUENCIA_LDB, DIAS_SEM_REGISTRO_URGENTE,
    DIAS_SEM_REGISTRO_ATENCAO, WRITABLE_DIR, DATA_DIR,
)


# ========== PESOS POR TIPO ==========

PESOS_TIPO = {
    'PROF_SILENCIOSO': 1.0,
    'DISCIPLINA_ORFA': 0.95,
    'TURMA_CRITICA': 0.9,
    'ALUNO_FREQUENCIA': 0.85,
    'ALUNO_OCORRENCIA': 0.8,
    'PROF_QUEDA': 0.7,
    'CURRICULO_ATRASADO': 0.6,
    'PROF_SEM_CONTEUDO': 0.5,
    'PROCESSO_DEADLINE': 0.4,
}

CORES_BATALHA = {
    'PROF_SILENCIOSO': '#F44336',
    'PROF_QUEDA': '#FFA000',
    'PROF_SEM_CONTEUDO': '#7B1FA2',
    'TURMA_CRITICA': '#E65100',
    'CURRICULO_ATRASADO': '#FF6D00',
    'ALUNO_FREQUENCIA': '#1565C0',
    'ALUNO_OCORRENCIA': '#AD1457',
    'DISCIPLINA_ORFA': '#78909C',
    'PROCESSO_DEADLINE': '#5C6BC0',
}

ICONES_BATALHA = {
    'PROF_SILENCIOSO': '🔴',
    'PROF_QUEDA': '🟡',
    'PROF_SEM_CONTEUDO': '📄',
    'TURMA_CRITICA': '⚠️',
    'CURRICULO_ATRASADO': '🟠',
    'ALUNO_FREQUENCIA': '🔵',
    'ALUNO_OCORRENCIA': '🆘',
    'DISCIPLINA_ORFA': '👻',
    'PROCESSO_DEADLINE': '⏰',
}


# ========== SCORE ==========

def calcular_score(batalha):
    """Score 0-100. Quanto maior, mais urgente."""
    peso = PESOS_TIPO.get(batalha['tipo'], 0.5)
    dias = batalha.get('dias_problema', 1)
    temporal = min(2.0, 1.0 + (dias / 14))
    n_afetados = batalha.get('n_afetados', 1)
    impacto = min(2.0, 1.0 + math.log10(max(n_afetados, 1) + 1) / 2)
    recorrencia = batalha.get('fator_recorrencia', 1.0)
    raw = peso * temporal * impacto * recorrencia * 25
    return min(100, max(0, round(raw, 1)))


def classificar(score):
    if score >= 70:
        return 'URGENTE'
    elif score >= 40:
        return 'IMPORTANTE'
    return 'MONITORAR'


# ========== DETECTORES ==========

def _detectar_prof_silencioso(df_aulas, df_horario, semana, unidade, series):
    """Tipo 1: Professor com 0 registros na semana atual."""
    hoje = _hoje()
    batalhas = []
    if df_horario.empty or semana <= 1:
        return batalhas

    # Filtrar horario por unidade/series do coordenador
    mask_h = (df_horario['unidade'] == unidade) & (df_horario['serie'].isin(series))
    hor_coord = df_horario[mask_h]
    if hor_coord.empty:
        return batalhas

    # Professores esperados (com series do coordenador)
    profs_esperados = hor_coord.groupby('professor').agg(
        disciplinas=('disciplina', lambda x: sorted(x.unique())),
        series_prof=('serie', lambda x: sorted(x.unique())),
        slots=('disciplina', 'count'),
    ).reset_index()

    # Aulas na semana atual
    mask_a = (df_aulas['unidade'] == unidade) & (df_aulas['serie'].isin(series))
    if 'semana_letiva' in df_aulas.columns:
        aulas_sem = df_aulas[mask_a & (df_aulas['semana_letiva'] == semana)]
    else:
        aulas_sem = pd.DataFrame()

    profs_com_registro = set(aulas_sem['professor'].unique()) if not aulas_sem.empty else set()

    for _, row in profs_esperados.iterrows():
        prof = row['professor']
        if prof in profs_com_registro:
            continue

        # Calcular dias sem registro
        df_prof = df_aulas[(df_aulas['professor'] == prof) & (df_aulas['unidade'] == unidade)]
        if df_prof.empty or df_prof['data'].isna().all():
            dias_sem = (hoje - datetime(2026, 1, 26)).days
            ultima_data = None
        else:
            ultima_data = df_prof['data'].max()
            dias_sem = (hoje - ultima_data).days

        if dias_sem < DIAS_SEM_REGISTRO_ATENCAO:
            continue

        discs = ', '.join(row['disciplinas'][:3])
        series_t = ', '.join(row['series_prof'][:3])

        # Contar alunos afetados
        n_afetados = row['slots'] * 30  # estimativa ~30 alunos por turma

        batalhas.append({
            'tipo': 'PROF_SILENCIOSO',
            'professor': prof,
            'disciplinas': discs,
            'series': series_t,
            'unidade': unidade,
            'dias_problema': dias_sem,
            'ultima_data': ultima_data.strftime('%d/%m') if ultima_data else 'nunca',
            'n_afetados': n_afetados,
            'fator_recorrencia': 1.0,
            'o_que': (
                f"{prof} ({discs}) nao registrou nenhuma aula esta semana. "
                f"{'Ultimo registro: ' + ultima_data.strftime('%d/%m') + ' (' + str(dias_sem) + ' dias atras).' if ultima_data else 'Nenhum registro no ano.'}"
            ),
            'por_que': (
                f"~{n_afetados} alunos do {series_t} estao sem acompanhamento em {discs}. "
                f"{'Sao ' + str(dias_sem) + ' dias consecutivos sem registro.' if dias_sem > 7 else ''}"
            ),
            'como': _acoes_prof_silencioso(prof, dias_sem),
            'links': [
                ('pages/13_🚦_Semáforo_Professor.py', '🚦 Semaforo'),
                ('pages/14_🧠_Alertas_Inteligentes.py', '🧠 Alertas'),
            ],
        })

    return batalhas


def _acoes_prof_silencioso(prof, dias):
    acoes = [f"Ligar para {prof} ou ir ate a sala"]
    if dias >= DIAS_SEM_REGISTRO_URGENTE:
        acoes.append("Se nao atender, enviar mensagem formal")
        acoes.append("Escalar para a direcao se sem resposta ate quarta")
    else:
        acoes.append("Perguntar se ha dificuldade de acesso ao SIGA")
        acoes.append("Combinar prazo para regularizacao (ate sexta)")
    return acoes


def _detectar_turma_critica(df_aulas, df_horario, semana, unidade, series):
    """Tipo 4: Turma com conformidade abaixo do critico."""
    batalhas = []
    if df_horario.empty or semana < 1:
        return batalhas

    for serie in series:
        hor_turma = df_horario[(df_horario['unidade'] == unidade) & (df_horario['serie'] == serie)]
        if hor_turma.empty:
            continue

        aulas_turma = df_aulas[(df_aulas['unidade'] == unidade) & (df_aulas['serie'] == serie)]
        esperado = len(hor_turma) * semana
        real = len(aulas_turma)
        conf = (real / esperado * 100) if esperado > 0 else 0

        if conf >= CONFORMIDADE_BAIXO:
            continue

        # Professores sem registro nesta turma
        profs_esperados = set(hor_turma['professor'].unique())
        profs_com = set(aulas_turma['professor'].unique()) if not aulas_turma.empty else set()
        profs_sem = profs_esperados - profs_com
        lista_sem = ', '.join(sorted(profs_sem)[:4])
        n_profs_sem = len(profs_sem)

        n_afetados = len(hor_turma) * 30  # estimativa

        nivel = 'CRITICO' if conf < CONFORMIDADE_CRITICO else 'ATENCAO'

        batalhas.append({
            'tipo': 'TURMA_CRITICA',
            'serie': serie,
            'unidade': unidade,
            'conformidade': round(conf, 0),
            'aulas_registradas': real,
            'aulas_esperadas': esperado,
            'dias_problema': semana * 5,  # dias uteis
            'n_afetados': n_afetados,
            'fator_recorrencia': 1.0,
            'o_que': (
                f"{serie} ({UNIDADES_NOMES.get(unidade, unidade)}) com apenas {conf:.0f}% de conformidade. "
                f"{real} de {esperado} aulas registradas ate a semana {semana}."
            ),
            'por_que': (
                f"{'~' + str(n_afetados) + ' alunos com cobertura curricular incompleta. ' if n_afetados > 0 else ''}"
                f"{n_profs_sem} professor(es) sem registro: {lista_sem}."
                if n_profs_sem > 0 else
                f"Conformidade abaixo da meta. Verificar se ha registros pendentes."
            ),
            'como': _acoes_turma_critica(n_profs_sem, lista_sem, serie),
            'links': [
                ('pages/18_🏫_Análise_Turma.py', '🏫 Analise Turma'),
                ('pages/13_🚦_Semáforo_Professor.py', '🚦 Semaforo'),
            ],
        })

    return batalhas


def _acoes_turma_critica(n_profs_sem, lista_sem, serie):
    acoes = []
    if n_profs_sem > 3:
        acoes.append(f"Agendar reuniao URGENTE com equipe do {serie}")
    elif n_profs_sem > 0:
        acoes.append(f"Contatar individualmente: {lista_sem}")
    acoes.append("Verificar se ha problema de acesso ao SIGA")
    acoes.append("Prazo: todos com registro ate sexta-feira")
    return acoes


def _detectar_aluno_frequencia(df_freq, unidade, series):
    """Tipo 6: Alunos com frequencia abaixo de 75% (LDB)."""
    batalhas = []
    if df_freq.empty or 'pct_frequencia' not in df_freq.columns:
        return batalhas

    mask = (df_freq['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB)
    if 'unidade' in df_freq.columns:
        mask &= (df_freq['unidade'] == unidade)
    if 'serie' in df_freq.columns:
        mask &= (df_freq['serie'].isin(series))

    risco = df_freq[mask]
    if risco.empty:
        return batalhas

    # Agrupar por serie
    if 'serie' in risco.columns and 'aluno_id' in risco.columns:
        por_serie = risco.groupby('serie').agg(
            n_alunos=('aluno_id', 'nunique'),
            freq_min=('pct_frequencia', 'min'),
        ).reset_index()

        for _, row in por_serie.iterrows():
            serie = row['serie']
            n = row['n_alunos']
            freq_min = row['freq_min']

            # Nomes dos alunos mais criticos
            alunos_serie = risco[risco['serie'] == serie]
            if 'aluno_nome' in alunos_serie.columns:
                top_risco = alunos_serie.drop_duplicates('aluno_id').nsmallest(3, 'pct_frequencia')
                nomes = ', '.join(
                    f"{r['aluno_nome']} ({r['pct_frequencia']:.0f}%)"
                    for _, r in top_risco.iterrows()
                )
            else:
                nomes = f"{n} aluno(s)"

            batalhas.append({
                'tipo': 'ALUNO_FREQUENCIA',
                'serie': serie,
                'unidade': unidade,
                'n_alunos': n,
                'dias_problema': 7,
                'n_afetados': n,
                'fator_recorrencia': 1.0,
                'o_que': (
                    f"{n} aluno(s) do {serie} com frequencia abaixo de 75% (limite LDB). "
                    f"Mais criticos: {nomes}."
                ),
                'por_que': (
                    f"Abaixo de 75%, risco de reprovacao por infrequencia (LDB art. 24, VI). "
                    f"{'Situacao critica: aluno com ' + str(round(freq_min)) + '%.' if freq_min < 60 else ''}"
                ),
                'como': [
                    "Encaminhar lista para orientacao educacional HOJE",
                    "Solicitar contato com as familias",
                    "Registrar no SIGA a intervencao realizada",
                    "Acompanhar frequencia na proxima semana",
                ],
                'links': [
                    ('pages/23_🚨_Alerta_Precoce_ABC.py', '🚨 Alerta ABC'),
                    ('pages/20_📊_Frequência_Escolar.py', '📊 Frequencia'),
                ],
            })

    return batalhas


def _detectar_ocorrencia_grave(df_ocorr, unidade, series):
    """Tipo 7: Ocorrencias graves nos ultimos 7 dias."""
    batalhas = []
    if df_ocorr.empty:
        return batalhas

    hoje = _hoje()
    inicio_semana = hoje - timedelta(days=7)

    mask = (df_ocorr['unidade'] == unidade) if 'unidade' in df_ocorr.columns else pd.Series(True, index=df_ocorr.index)
    if 'serie' in df_ocorr.columns:
        mask &= df_ocorr['serie'].isin(series)
    if 'data' in df_ocorr.columns:
        mask &= df_ocorr['data'] >= inicio_semana
    if 'gravidade' in df_ocorr.columns:
        mask &= df_ocorr['gravidade'] == 'Grave'

    graves = df_ocorr[mask]
    if graves.empty:
        return batalhas

    n = len(graves)
    # Agrupar
    if 'aluno_nome' in graves.columns:
        nomes = ', '.join(graves['aluno_nome'].unique()[:3])
    else:
        nomes = f"{n} registro(s)"

    batalhas.append({
        'tipo': 'ALUNO_OCORRENCIA',
        'unidade': unidade,
        'n_ocorrencias': n,
        'dias_problema': 3,
        'n_afetados': graves['aluno_id'].nunique() if 'aluno_id' in graves.columns else n,
        'fator_recorrencia': 1.0,
        'o_que': f"{n} ocorrencia(s) grave(s) nos ultimos 7 dias. Alunos: {nomes}.",
        'por_que': "Ocorrencias graves exigem intervencao imediata e registro de providencia.",
        'como': [
            "Verificar providencia de cada ocorrencia",
            "Convocar familia/responsavel se necessario",
            "Registrar acompanhamento no SIGA",
        ],
        'links': [
            ('pages/22_📋_Ocorrências.py', '📋 Ocorrencias'),
        ],
    })

    return batalhas


def _detectar_disciplina_orfa(df_aulas, df_horario, semana, unidade, series):
    """Tipo 8: Disciplina com zero registros desde o inicio do ano."""
    batalhas = []
    if df_horario.empty or semana <= 1:
        return batalhas

    mask_h = (df_horario['unidade'] == unidade) & (df_horario['serie'].isin(series))
    hor = df_horario[mask_h]

    for (serie, disc), grupo in hor.groupby(['serie', 'disciplina']):
        aulas_disc = df_aulas[
            (df_aulas['unidade'] == unidade) &
            (df_aulas['serie'] == serie) &
            (df_aulas['disciplina'] == disc)
        ]
        if len(aulas_disc) == 0:
            n_slots = len(grupo)
            batalhas.append({
                'tipo': 'DISCIPLINA_ORFA',
                'disciplina': disc,
                'serie': serie,
                'unidade': unidade,
                'dias_problema': semana * 5,
                'n_afetados': n_slots * 30,
                'fator_recorrencia': 1.0,
                'o_que': (
                    f"{disc} no {serie} ({UNIDADES_NOMES.get(unidade, unidade)}) "
                    f"nao tem NENHUM registro desde o inicio do ano. Ja se passaram {semana} semanas."
                ),
                'por_que': (
                    f"Alunos estao sem nenhuma aula de {disc} registrada. "
                    f"Possivel causa: professor nao designado ou problema de login."
                ),
                'como': [
                    f"Verificar com secretaria se ha professor para {disc} no {serie}",
                    "Se houver, contatar o professor sobre os registros",
                    "Se nao houver, escalar para direcao (pendencia critica)",
                ],
                'links': [
                    ('pages/14_🧠_Alertas_Inteligentes.py', '🧠 Alertas'),
                ],
            })

    return batalhas


def _detectar_processo_deadline(unidade, config_path=None):
    """Tipo 9: Deadline de feedback proximo."""
    batalhas = []
    hoje = _hoje()
    path = config_path or (DATA_DIR / "config_coordenadores.json")
    if not path.exists():
        return batalhas

    with open(path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    for periodo in config.get('periodos_feedback', []):
        deadline = datetime.strptime(periodo['deadline_feedback'], '%Y-%m-%d')
        dias_restantes = (deadline - hoje).days
        if 0 < dias_restantes <= 30:
            batalhas.append({
                'tipo': 'PROCESSO_DEADLINE',
                'bimestre': periodo['nome'],
                'deadline': periodo['deadline_feedback'],
                'unidade': unidade,
                'dias_problema': max(1, 30 - dias_restantes),
                'dias_restantes': dias_restantes,
                'n_afetados': 5,
                'fator_recorrencia': 1.0,
                'o_que': (
                    f"Deadline do {periodo['nome']}: {deadline.strftime('%d/%m/%Y')} "
                    f"({dias_restantes} dias restantes). Verifique feedbacks pendentes."
                ),
                'por_que': (
                    "Cada professor deve receber 1 observacao de aula + 1 reuniao de feedback por bimestre. "
                    f"{'URGENTE: menos de 2 semanas!' if dias_restantes <= 14 else ''}"
                ),
                'como': [
                    "Verificar agenda e reservar horarios para feedbacks",
                    "Priorizar professores com alertas ativos",
                    "Usar material da Agenda de Coordenacao (pagina 12)",
                ],
                'links': [
                    ('pages/12_📋_Agenda_Coordenação.py', '📋 Agenda'),
                ],
            })

    return batalhas


# ========== PIPELINE PRINCIPAL ==========

def gerar_batalhas(unidade, series):
    """Gera todas as batalhas para um coordenador. Retorna lista ordenada por score."""
    df_aulas = carregar_fato_aulas()
    if not df_aulas.empty:
        df_aulas = filtrar_ate_hoje(df_aulas)
    df_horario = carregar_horario_esperado()
    df_freq = carregar_frequencia_alunos()
    df_ocorr = carregar_ocorrencias()
    semana = calcular_semana_letiva()

    todas = []
    if not df_aulas.empty:
        todas.extend(_detectar_prof_silencioso(df_aulas, df_horario, semana, unidade, series))
        todas.extend(_detectar_turma_critica(df_aulas, df_horario, semana, unidade, series))
        todas.extend(_detectar_disciplina_orfa(df_aulas, df_horario, semana, unidade, series))
    todas.extend(_detectar_aluno_frequencia(df_freq, unidade, series))
    todas.extend(_detectar_ocorrencia_grave(df_ocorr, unidade, series))
    todas.extend(_detectar_processo_deadline(unidade))

    # Calcular score e classificar
    for b in todas:
        b['score'] = calcular_score(b)
        b['nivel'] = classificar(b['score'])
        b['icone'] = ICONES_BATALHA.get(b['tipo'], '⚪')
        b['cor'] = CORES_BATALHA.get(b['tipo'], '#607D8B')

    todas.sort(key=lambda x: x['score'], reverse=True)
    return todas


# ========== PERSISTENCIA ==========

def _status_path():
    return WRITABLE_DIR / "batalhas_status.json"


def carregar_status():
    """Carrega status das batalhas (JSON)."""
    path = _status_path()
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def salvar_status(batalha_id, status, nota=""):
    """Salva status de uma batalha."""
    todos = carregar_status()
    todos[batalha_id] = {
        'status': status,
        'nota': nota,
        'atualizado_em': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }
    path = _status_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def gerar_batalha_id(batalha):
    """Gera ID unico para a batalha baseado em tipo + entidade + semana."""
    semana = calcular_semana_letiva()
    entidade = batalha.get('professor', batalha.get('serie', batalha.get('disciplina', 'geral')))
    un = batalha.get('unidade', '')
    return f"{batalha['tipo']}_{un}_{entidade}_{semana}".replace(' ', '_')
