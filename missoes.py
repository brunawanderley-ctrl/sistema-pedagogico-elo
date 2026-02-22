"""
Motor de deteccao e priorizacao de missoes semanais.
Centraliza logica de negocios separada da UI.
Cada missao tem: tipo, nivel, score, frase_humana, contexto, acoes, links.
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

CORES_MISSAO = {
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

ICONES_MISSAO = {
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

def calcular_score(missao):
    """Score 0-100. Quanto maior, mais urgente."""
    peso = PESOS_TIPO.get(missao['tipo'], 0.5)
    dias = missao.get('dias_problema', 1)
    temporal = min(2.0, 1.0 + (dias / 14))
    n_afetados = missao.get('n_afetados', 1)
    impacto = min(2.0, 1.0 + math.log10(max(n_afetados, 1) + 1) / 2)
    recorrencia = missao.get('fator_recorrencia', 1.0)
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
    missoes = []
    if df_horario.empty or semana <= 1:
        return missoes

    # Filtrar horario por unidade/series do coordenador
    mask_h = (df_horario['unidade'] == unidade) & (df_horario['serie'].isin(series))
    hor_coord = df_horario[mask_h]
    if hor_coord.empty:
        return missoes

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

        missoes.append({
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
                ('app_pages/13_🚦_Semáforo_Professor.py', '🚦 Semaforo'),
                ('app_pages/14_🧠_Alertas_Inteligentes.py', '🧠 Alertas'),
            ],
        })

    return missoes


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
    missoes = []
    if df_horario.empty or semana < 1:
        return missoes

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

        missoes.append({
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
                ('app_pages/18_🏫_Análise_Turma.py', '🏫 Analise Turma'),
                ('app_pages/13_🚦_Semáforo_Professor.py', '🚦 Semaforo'),
            ],
        })

    return missoes


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
    missoes = []
    if df_freq.empty or 'pct_frequencia' not in df_freq.columns:
        return missoes

    mask = (df_freq['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB)
    if 'unidade' in df_freq.columns:
        mask &= (df_freq['unidade'] == unidade)
    if 'serie' in df_freq.columns:
        mask &= (df_freq['serie'].isin(series))

    risco = df_freq[mask]
    if risco.empty:
        return missoes

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

            missoes.append({
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
                    ('app_pages/23_🚨_Alerta_Precoce_ABC.py', '🚨 Alerta ABC'),
                    ('app_pages/20_📊_Frequência_Escolar.py', '📊 Frequencia'),
                ],
            })

    return missoes


def _detectar_ocorrencia_grave(df_ocorr, unidade, series):
    """Tipo 7: Ocorrencias graves nos ultimos 7 dias."""
    missoes = []
    if df_ocorr.empty:
        return missoes

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
        return missoes

    n = len(graves)
    # Agrupar
    if 'aluno_nome' in graves.columns:
        nomes = ', '.join(graves['aluno_nome'].unique()[:3])
    else:
        nomes = f"{n} registro(s)"

    missoes.append({
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
            ('app_pages/22_📋_Ocorrências.py', '📋 Ocorrencias'),
        ],
    })

    return missoes


def _detectar_disciplina_orfa(df_aulas, df_horario, semana, unidade, series):
    """Tipo 8: Disciplina com zero registros desde o inicio do ano."""
    missoes = []
    if df_horario.empty or semana <= 1:
        return missoes

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
            missoes.append({
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
                    ('app_pages/14_🧠_Alertas_Inteligentes.py', '🧠 Alertas'),
                ],
            })

    return missoes


def _detectar_prof_queda(df_aulas, df_horario, semana, unidade, series):
    """Tipo 6: Professor com queda >30% de registros vs semana anterior."""
    missoes = []
    if df_horario.empty or semana <= 2:
        return missoes

    mask_h = (df_horario['unidade'] == unidade) & (df_horario['serie'].isin(series))
    hor_coord = df_horario[mask_h]
    if hor_coord.empty:
        return missoes

    mask_a = (df_aulas['unidade'] == unidade) & (df_aulas['serie'].isin(series))
    aulas_coord = df_aulas[mask_a]
    if aulas_coord.empty or 'semana_letiva' not in aulas_coord.columns:
        return missoes

    sem_atual = aulas_coord[aulas_coord['semana_letiva'] == semana]
    sem_anterior = aulas_coord[aulas_coord['semana_letiva'] == semana - 1]

    if sem_anterior.empty:
        return missoes

    reg_anterior = sem_anterior.groupby('professor').size()
    reg_atual = sem_atual.groupby('professor').size()

    for prof in reg_anterior.index:
        ant = reg_anterior[prof]
        atu = reg_atual.get(prof, 0)
        if ant == 0:
            continue
        queda_pct = (ant - atu) / ant * 100
        if queda_pct < 30:
            continue

        # Verificar recorrencia (queda 2+ semanas consecutivas)
        fator_rec = 1.0
        if semana >= 3 and 'semana_letiva' in aulas_coord.columns:
            sem_ant2 = aulas_coord[aulas_coord['semana_letiva'] == semana - 2]
            reg_ant2 = len(sem_ant2[sem_ant2['professor'] == prof])
            if reg_ant2 > ant:
                fator_rec = 1.3  # queda em 2+ semanas

        prof_info = hor_coord[hor_coord['professor'] == prof]
        discs = ', '.join(sorted(prof_info['disciplina'].unique())[:3])
        series_t = ', '.join(sorted(prof_info['serie'].unique())[:3])
        n_afetados = len(prof_info) * 30

        missoes.append({
            'tipo': 'PROF_QUEDA',
            'professor': prof,
            'disciplinas': discs,
            'series': series_t,
            'unidade': unidade,
            'dias_problema': 7,
            'n_afetados': n_afetados,
            'fator_recorrencia': fator_rec,
            'queda_pct': round(queda_pct, 0),
            'registros_semana_anterior': int(ant),
            'registros_semana_atual': int(atu),
            'o_que': (
                f"{prof} ({discs}) teve queda de {queda_pct:.0f}% nos registros. "
                f"Semana anterior: {ant} | Semana atual: {atu}."
            ),
            'por_que': (
                f"Queda abrupta pode indicar problema de acesso, licenca ou desmotivacao. "
                f"{'Queda recorrente (2+ semanas).' if fator_rec > 1 else ''}"
            ),
            'como': [
                f"Verificar com {prof} se houve mudanca de horario ou problema de acesso",
                "Se licenca medica, registrar e redistribuir turmas",
                "Se desmotivacao, agendar conversa de feedback ate sexta",
            ],
            'links': [
                ('app_pages/13_🚦_Semáforo_Professor.py', '🚦 Semaforo'),
            ],
        })

    return missoes


def _detectar_curriculo_atrasado(df_aulas, semana, unidade, series):
    """Tipo 7: Professor >1 capitulo atras do SAE esperado."""
    missoes = []
    if df_aulas.empty or semana < 4:
        return missoes

    capitulo_esperado = calcular_capitulo_esperado(semana)
    if capitulo_esperado <= 1:
        return missoes

    mask = (df_aulas['unidade'] == unidade) & (df_aulas['serie'].isin(series))
    aulas = df_aulas[mask]
    if aulas.empty:
        return missoes

    # Tentar detectar capitulo a partir do campo 'conteudo'
    import re
    cap_pattern = re.compile(r'cap(?:[ií]tulo|\.?)\s*(\d{1,2})', re.IGNORECASE)

    for (prof, disc), grupo in aulas.groupby(['professor', 'disciplina']):
        max_cap = 0
        if 'conteudo' in grupo.columns:
            conteudos = grupo['conteudo'].dropna().astype(str)
            for txt in conteudos:
                matches = cap_pattern.findall(txt)
                for m in matches:
                    max_cap = max(max_cap, int(m))

        if max_cap == 0:
            # Tentar dim_Progressao_SAE
            prog_path = DATA_DIR / "dim_Progressao_SAE.csv"
            if prog_path.exists():
                try:
                    prog_df = pd.read_csv(prog_path)
                    mask_p = (prog_df.get('professor', pd.Series()) == prof) & \
                             (prog_df.get('disciplina', pd.Series()) == disc)
                    if mask_p.any():
                        max_cap = int(prog_df[mask_p]['capitulo_atual'].max())
                except Exception:
                    pass

        if max_cap == 0:
            continue

        gap = capitulo_esperado - max_cap
        if gap <= 1:
            continue

        series_prof = ', '.join(sorted(grupo['serie'].unique())[:3])
        n_afetados = grupo['serie'].nunique() * 30

        missoes.append({
            'tipo': 'CURRICULO_ATRASADO',
            'professor': prof,
            'disciplina': disc,
            'series': series_prof,
            'unidade': unidade,
            'capitulo_atual': max_cap,
            'capitulo_esperado': capitulo_esperado,
            'gap': gap,
            'dias_problema': gap * 7,
            'n_afetados': n_afetados,
            'fator_recorrencia': 1.0,
            'o_que': (
                f"{prof} ({disc}) esta no capitulo {max_cap}, "
                f"mas o esperado e o capitulo {capitulo_esperado} ({gap} capitulos atrasado)."
            ),
            'por_que': (
                f"Atraso de {gap} capitulo(s) compromete a cobertura curricular SAE. "
                f"Alunos do {series_prof} podem nao completar o conteudo planejado."
            ),
            'como': [
                f"Conversar com {prof} sobre plano de recuperacao de ritmo",
                f"Se gap >= 3: considerar compactacao de capitulos {max_cap+1}-{capitulo_esperado}",
                "Alinhar com coordenacao pedagogica prazo realista",
            ],
            'links': [
                ('app_pages/05_📚_Progressão_SAE.py', '📚 Progressao SAE'),
            ],
        })

    return missoes


def _detectar_prof_sem_conteudo(df_aulas, df_horario, semana, unidade, series):
    """Tipo 8: Professor com >50% aulas sem campo conteudo preenchido."""
    missoes = []
    if df_aulas.empty or df_horario.empty or semana < 2:
        return missoes

    mask_a = (df_aulas['unidade'] == unidade) & (df_aulas['serie'].isin(series))
    aulas = df_aulas[mask_a]
    if aulas.empty or 'conteudo' not in aulas.columns:
        return missoes

    for prof, grupo in aulas.groupby('professor'):
        total = len(grupo)
        if total < 3:
            continue

        sem_conteudo = grupo['conteudo'].isna() | (grupo['conteudo'].astype(str).str.strip() == '')
        n_vazio = sem_conteudo.sum()
        pct_vazio = n_vazio / total * 100

        if pct_vazio < 50:
            continue

        prof_info = df_horario[
            (df_horario['unidade'] == unidade) & (df_horario['professor'] == prof)
        ]
        discs = ', '.join(sorted(prof_info['disciplina'].unique())[:3]) if not prof_info.empty else ''
        series_t = ', '.join(sorted(grupo['serie'].unique())[:3])
        n_afetados = grupo['serie'].nunique() * 30

        missoes.append({
            'tipo': 'PROF_SEM_CONTEUDO',
            'professor': prof,
            'disciplinas': discs,
            'series': series_t,
            'unidade': unidade,
            'pct_vazio': round(pct_vazio, 0),
            'aulas_sem_conteudo': int(n_vazio),
            'aulas_total': total,
            'dias_problema': 7,
            'n_afetados': n_afetados,
            'fator_recorrencia': 1.0,
            'o_que': (
                f"{prof} ({discs}) tem {pct_vazio:.0f}% das aulas sem conteudo descrito. "
                f"{n_vazio} de {total} aulas sem descricao de conteudo."
            ),
            'por_que': (
                f"Aulas sem conteudo impossibilitam rastrear cobertura curricular. "
                f"Alunos do {series_t} nao tem registro do que foi ensinado."
            ),
            'como': [
                f"Orientar {prof} sobre a importancia do registro de conteudo",
                "Mostrar exemplo de registro completo (capitulo + topico)",
                "Prazo: regularizar registros pendentes ate sexta-feira",
            ],
            'links': [
                ('app_pages/13_🚦_Semáforo_Professor.py', '🚦 Semaforo'),
                ('app_pages/05_📚_Progressão_SAE.py', '📚 Progressao SAE'),
            ],
        })

    return missoes


def _detectar_processo_deadline(unidade, config_path=None):
    """Tipo 9: Deadline de feedback proximo."""
    missoes = []
    hoje = _hoje()
    path = config_path or (DATA_DIR / "config_coordenadores.json")
    if not path.exists():
        return missoes

    with open(path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    for periodo in config.get('periodos_feedback', []):
        deadline = datetime.strptime(periodo['deadline_feedback'], '%Y-%m-%d')
        dias_restantes = (deadline - hoje).days
        if 0 < dias_restantes <= 30:
            missoes.append({
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
                    ('app_pages/12_📋_Agenda_Coordenação.py', '📋 Agenda'),
                ],
            })

    return missoes


# ========== PIPELINE PRINCIPAL ==========

def gerar_missoes(unidade, series):
    """Gera todas as missoes para um coordenador. Retorna lista ordenada por score."""
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
        todas.extend(_detectar_prof_queda(df_aulas, df_horario, semana, unidade, series))
        todas.extend(_detectar_curriculo_atrasado(df_aulas, semana, unidade, series))
        todas.extend(_detectar_prof_sem_conteudo(df_aulas, df_horario, semana, unidade, series))
    todas.extend(_detectar_aluno_frequencia(df_freq, unidade, series))
    todas.extend(_detectar_ocorrencia_grave(df_ocorr, unidade, series))
    todas.extend(_detectar_processo_deadline(unidade))

    # Calcular score e classificar
    for b in todas:
        b['score'] = calcular_score(b)
        b['nivel'] = classificar(b['score'])
        b['icone'] = ICONES_MISSAO.get(b['tipo'], '⚪')
        b['cor'] = CORES_MISSAO.get(b['tipo'], '#607D8B')

    todas.sort(key=lambda x: x['score'], reverse=True)
    return todas


# ========== PERSISTENCIA ==========

def _status_path():
    return WRITABLE_DIR / "missoes_status.json"


def carregar_status():
    """Carrega status das missoes (JSON)."""
    path = _status_path()
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def salvar_status(missao_id, status, nota=""):
    """Salva status de uma missao."""
    todos = carregar_status()
    todos[missao_id] = {
        'status': status,
        'nota': nota,
        'atualizado_em': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }
    path = _status_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def gerar_missao_id(missao):
    """Gera ID unico para a missao baseado em tipo + entidade + semana."""
    semana = calcular_semana_letiva()
    entidade = missao.get('professor', missao.get('serie', missao.get('disciplina', 'geral')))
    un = missao.get('unidade', '')
    return f"{missao['tipo']}_{un}_{entidade}_{semana}".replace(' ', '_')


def gerar_missao_fingerprint(missao):
    """Gera fingerprint estavel SEM semana — para rastreamento entre semanas.
    Formato: {tipo}_{unidade}_{entidade}"""
    entidade = missao.get('professor', missao.get('serie', missao.get('disciplina', 'geral')))
    un = missao.get('unidade', '')
    return f"{missao['tipo']}_{un}_{entidade}".replace(' ', '_')


def gerar_todas_missoes_rede():
    """Gera missoes para TODOS os coordenadores de todas as unidades.
    Usa config_coordenadores.json. Retorna dict {unidade: [missoes]}."""
    config_path = DATA_DIR / "config_coordenadores.json"
    if not config_path.exists():
        return {}

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    resultado = {}
    for coord in config.get('coordenadores', []):
        un = coord['unidade']
        series = coord.get('series', [])
        missoes = gerar_missoes(un, series)
        if un not in resultado:
            resultado[un] = []
        resultado[un].extend(missoes)

    # Deduplicar por fingerprint dentro de cada unidade
    for un in resultado:
        seen = set()
        dedup = []
        for b in resultado[un]:
            fp = gerar_missao_fingerprint(b)
            if fp not in seen:
                seen.add(fp)
                dedup.append(b)
        resultado[un] = sorted(dedup, key=lambda x: x['score'], reverse=True)

    return resultado
