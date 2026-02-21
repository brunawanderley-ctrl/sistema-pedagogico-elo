#!/usr/bin/env python3
"""
PAGINA 27: SALA DE SITUACAO
Dashboard executivo — visao completa da rede em 3 minutos.
Proposta #1 da Arena de Propostas (Time Azul).
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_UNIDADES, CORES_STATUS
from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    status_conformidade, carregar_fato_aulas, carregar_horario_esperado,
    carregar_ocorrencias, carregar_frequencia_alunos, carregar_alunos,
    carregar_professores, filtrar_ate_hoje, _hoje,
    DATA_DIR, UNIDADES_NOMES,
    CONFORMIDADE_CRITICO, CONFORMIDADE_BAIXO, CONFORMIDADE_META,
    CONFORMIDADE_EXCELENTE, THRESHOLD_FREQUENCIA_LDB,
    DIAS_SEM_REGISTRO_ATENCAO, DIAS_SEM_REGISTRO_URGENTE,
)
from components import (
    cabecalho_pagina, filtro_unidade, metricas_em_colunas,
    aplicar_filtro_unidade,
)

st.set_page_config(page_title="Sala de Situação", page_icon="🏥", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

# ========== CSS ==========
st.markdown("""
<style>
    .context-bar {
        background: linear-gradient(90deg, #1a237e 0%, #283593 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        font-size: 1.05em;
    }
    .context-item {
        text-align: center;
    }
    .context-item .valor {
        font-size: 1.6em;
        font-weight: bold;
    }
    .context-item .rotulo {
        font-size: 0.8em;
        opacity: 0.85;
    }
    .saude-card {
        padding: 16px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 4px 0;
    }
    .saude-card .pct {
        font-size: 2.2em;
        font-weight: bold;
        margin: 4px 0;
    }
    .saude-card .detalhe {
        font-size: 0.85em;
        opacity: 0.9;
    }
    .alert-critical {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 15px;
        margin: 8px 0;
        border-radius: 4px;
    }
    .alert-warning {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 8px 0;
        border-radius: 4px;
    }
    .progress-container {
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        height: 28px;
        margin: 6px 0;
        position: relative;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 0.85em;
        transition: width 0.5s ease;
    }
    .progress-label {
        font-weight: 600;
        margin-bottom: 2px;
    }
    .link-card {
        background: #f5f5f5;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 4px 0;
        text-decoration: none;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)


# ========== FUNCOES INTERNAS ==========

def carregar_dados_sala():
    """Carrega todos os dados necessarios para a Sala de Situacao."""
    dados = {}
    df_aulas = carregar_fato_aulas()
    if not df_aulas.empty:
        dados['aulas'] = filtrar_ate_hoje(df_aulas)
    df_horario = carregar_horario_esperado()
    if not df_horario.empty:
        dados['horario'] = df_horario
    df_ocorr = carregar_ocorrencias()
    if not df_ocorr.empty:
        dados['ocorrencias'] = df_ocorr
    df_freq = carregar_frequencia_alunos()
    if not df_freq.empty:
        dados['frequencia'] = df_freq
    df_alunos = carregar_alunos()
    if not df_alunos.empty:
        dados['alunos'] = df_alunos
    df_profs = carregar_professores()
    if not df_profs.empty:
        dados['professores'] = df_profs
    return dados


def calcular_saude_unidade(df_aulas, df_horario, semana):
    """Calcula metricas de saude por unidade. Retorna lista de dicts."""
    resultado = []
    unidades = sorted(df_aulas['unidade'].dropna().unique())
    for un in unidades:
        df_un = df_aulas[df_aulas['unidade'] == un]
        df_hor_un = df_horario[df_horario['unidade'] == un] if not df_horario.empty else pd.DataFrame()

        aulas_registradas = len(df_un)
        aulas_esperadas = len(df_hor_un) * semana if not df_hor_un.empty else 0
        conformidade = (aulas_registradas / aulas_esperadas * 100) if aulas_esperadas > 0 else 0

        profs_registrando = df_un['professor'].nunique()
        profs_esperados = df_hor_un['professor'].nunique() if not df_hor_un.empty else profs_registrando

        # Professores sem registro na semana atual
        profs_com_registro = set()
        if 'semana_letiva' in df_un.columns:
            profs_com_registro = set(df_un[df_un['semana_letiva'] == semana]['professor'].unique())
        profs_esperados_set = set(df_hor_un['professor'].unique()) if not df_hor_un.empty else set()
        profs_sem_registro = len(profs_esperados_set - profs_com_registro)

        emoji, label = status_conformidade(conformidade)

        resultado.append({
            'unidade': un,
            'nome': UNIDADES_NOMES.get(un, un),
            'conformidade': round(conformidade, 1),
            'emoji': emoji,
            'label': label,
            'aulas_registradas': aulas_registradas,
            'profs_registrando': profs_registrando,
            'profs_esperados': profs_esperados,
            'profs_sem_registro': profs_sem_registro,
            'cor': CORES_UNIDADES.get(un, '#607D8B'),
        })
    return resultado


def calcular_metricas_gerais(df_aulas, df_horario, df_ocorr, df_freq, semana):
    """Calcula metricas gerais com delta vs semana anterior."""
    hoje = _hoje()

    # Conformidade geral
    aulas_total = len(df_aulas)
    aulas_esperadas = len(df_horario) * semana if not df_horario.empty else 0
    conformidade = (aulas_total / aulas_esperadas * 100) if aulas_esperadas > 0 else 0

    # Delta: conformidade semana anterior
    if semana > 1 and not df_horario.empty:
        aulas_esperadas_ant = len(df_horario) * (semana - 1)
        if 'semana_letiva' in df_aulas.columns:
            aulas_ate_ant = len(df_aulas[df_aulas['semana_letiva'] < semana])
        else:
            aulas_ate_ant = aulas_total  # fallback
        conf_ant = (aulas_ate_ant / aulas_esperadas_ant * 100) if aulas_esperadas_ant > 0 else 0
        delta_conf = round(conformidade - conf_ant, 1)
    else:
        delta_conf = None

    # Aulas hoje
    aulas_hoje = len(df_aulas[df_aulas['data'].dt.date == hoje.date()]) if 'data' in df_aulas.columns else 0

    # Conteudo preenchido
    if aulas_total > 0:
        com_conteudo = len(df_aulas[df_aulas['conteudo'].notna() & (df_aulas['conteudo'] != '')])
        pct_conteudo = round(com_conteudo / aulas_total * 100, 1)
    else:
        pct_conteudo = 0

    # Professores ativos
    profs_ativos = df_aulas['professor'].nunique()
    profs_total = df_horario['professor'].nunique() if not df_horario.empty else profs_ativos

    # Alunos em risco (frequencia < 75% LDB)
    if not df_freq.empty and 'pct_frequencia' in df_freq.columns:
        alunos_risco = len(df_freq[df_freq['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB]['aluno_id'].unique())
    else:
        alunos_risco = None  # N/D

    # Ocorrencias na semana
    if not df_ocorr.empty and 'data' in df_ocorr.columns:
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        ocorr_semana = len(df_ocorr[df_ocorr['data'] >= inicio_semana])
    else:
        ocorr_semana = 0

    return {
        'conformidade': round(conformidade, 1),
        'delta_conf': delta_conf,
        'aulas_hoje': aulas_hoje,
        'pct_conteudo': pct_conteudo,
        'profs_ativos': profs_ativos,
        'profs_total': profs_total,
        'alunos_risco': alunos_risco,
        'ocorr_semana': ocorr_semana,
    }


def gerar_alertas_criticos(df_aulas, df_horario, df_freq, semana):
    """Gera lista de alertas criticos ordenados por prioridade. Retorna max 10."""
    hoje = _hoje()
    alertas = []

    # --- TIPO 1: Professor silencioso (0 registros na semana atual) ---
    if not df_horario.empty and 'semana_letiva' in df_aulas.columns:
        profs_esperados = df_horario.groupby(['unidade', 'professor']).size().reset_index(name='slots')
        for _, row in profs_esperados.iterrows():
            un = row['unidade']
            prof = row['professor']
            aulas_sem = df_aulas[
                (df_aulas['professor'] == prof) &
                (df_aulas['unidade'] == un) &
                (df_aulas['semana_letiva'] == semana)
            ]
            if len(aulas_sem) == 0 and semana > 1:
                # Verifica ultimo registro
                df_prof = df_aulas[(df_aulas['professor'] == prof) & (df_aulas['unidade'] == un)]
                if df_prof.empty:
                    dias_sem = 999
                elif df_prof['data'].notna().any():
                    dias_sem = (hoje - df_prof['data'].max()).days
                else:
                    dias_sem = 999

                if dias_sem >= DIAS_SEM_REGISTRO_URGENTE:
                    nivel = 'CRITICO'
                    prioridade = 1
                elif dias_sem >= DIAS_SEM_REGISTRO_ATENCAO:
                    nivel = 'ATENCAO'
                    prioridade = 2
                else:
                    continue

                disciplinas = ', '.join(sorted(
                    df_horario[(df_horario['professor'] == prof) & (df_horario['unidade'] == un)]['disciplina'].unique()
                )[:3])

                alertas.append({
                    'nivel': nivel,
                    'prioridade': prioridade,
                    'titulo': f'Professor Silencioso — {prof}',
                    'contexto': f'{un} | {disciplinas}',
                    'problema': f'{dias_sem} dias sem registro' if dias_sem < 999 else 'Nenhum registro no ano',
                    'acao': 'Contatar professor IMEDIATAMENTE' if nivel == 'CRITICO' else 'Monitorar e conversar',
                })

    # --- TIPO 2: Turma com conformidade critica (<50%) ---
    if not df_horario.empty:
        for (un, serie), grupo_hor in df_horario.groupby(['unidade', 'serie']):
            df_turma = df_aulas[(df_aulas['unidade'] == un) & (df_aulas['serie'] == serie)]
            esperado = len(grupo_hor) * semana
            real = len(df_turma)
            conf = (real / esperado * 100) if esperado > 0 else 0
            if conf < CONFORMIDADE_CRITICO:
                alertas.append({
                    'nivel': 'CRITICO',
                    'prioridade': 3,
                    'titulo': f'Turma Critica — {serie} ({un})',
                    'contexto': f'{un} | {serie}',
                    'problema': f'Conformidade {conf:.0f}% ({real}/{esperado} aulas)',
                    'acao': 'Verificar registros de professores desta turma',
                })
            elif conf < CONFORMIDADE_BAIXO:
                alertas.append({
                    'nivel': 'ATENCAO',
                    'prioridade': 4,
                    'titulo': f'Turma em Atencao — {serie} ({un})',
                    'contexto': f'{un} | {serie}',
                    'problema': f'Conformidade {conf:.0f}% ({real}/{esperado} aulas)',
                    'acao': 'Acompanhar evolucao semanal',
                })

    # --- TIPO 3: Alunos com frequencia em risco (<75% LDB) ---
    if not df_freq.empty and 'pct_frequencia' in df_freq.columns:
        risco = df_freq[df_freq['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB]
        if not risco.empty:
            por_unidade = risco.groupby('unidade')['aluno_id'].nunique()
            for un, n_alunos in por_unidade.items():
                alertas.append({
                    'nivel': 'ATENCAO' if n_alunos < 10 else 'CRITICO',
                    'prioridade': 5,
                    'titulo': f'Frequencia em Risco — {un}',
                    'contexto': f'{un} | {n_alunos} aluno(s)',
                    'problema': f'{n_alunos} aluno(s) com frequencia abaixo de {THRESHOLD_FREQUENCIA_LDB}%',
                    'acao': 'Acionar coordenacao e familia',
                })

    # Ordenar por prioridade (CRITICO primeiro, depois ATENCAO)
    ordem_nivel = {'CRITICO': 0, 'ATENCAO': 1}
    alertas.sort(key=lambda a: (ordem_nivel.get(a['nivel'], 9), a['prioridade']))

    return alertas[:10]


def render_barra_progresso(label, valor, maximo, descricao=""):
    """Renderiza uma barra de progresso HTML."""
    if maximo <= 0:
        pct = 0
    else:
        pct = min(100, valor / maximo * 100)

    if pct >= CONFORMIDADE_META:
        cor = '#43A047'
    elif pct >= CONFORMIDADE_BAIXO:
        cor = '#FFA726'
    else:
        cor = '#E53935'

    st.markdown(f"""
    <div>
        <div class="progress-label">{label}</div>
        <div class="progress-container">
            <div class="progress-fill" style="width: {pct:.0f}%; background: {cor};">
                {valor:,} / {maximo:,} ({pct:.0f}%)
            </div>
        </div>
        <small style="color: #666;">{descricao}</small>
    </div>
    """, unsafe_allow_html=True)


# ========== MAIN ==========

def main():
    cabecalho_pagina(
        "🏥 Sala de Situacao",
        "Visao executiva — o que precisa da sua atencao AGORA"
    )

    dados = carregar_dados_sala()

    if 'aulas' not in dados:
        st.error("Dados nao carregados. Execute a extracao do SIGA primeiro.")
        return

    df_aulas = dados['aulas']
    df_horario = dados.get('horario', pd.DataFrame())
    df_ocorr = dados.get('ocorrencias', pd.DataFrame())
    df_freq = dados.get('frequencia', pd.DataFrame())

    # Filtro de unidade na sidebar
    with st.sidebar:
        filtro_un = filtro_unidade(key="pg27_un")

    # Aplicar filtro
    df_aulas_filt = aplicar_filtro_unidade(df_aulas, filtro_un)
    df_horario_filt = aplicar_filtro_unidade(df_horario, filtro_un)
    df_ocorr_filt = aplicar_filtro_unidade(df_ocorr, filtro_un) if not df_ocorr.empty else df_ocorr
    df_freq_filt = aplicar_filtro_unidade(df_freq, filtro_un) if not df_freq.empty else df_freq

    # ========== SECAO 1: CONTEXTO TEMPORAL ==========
    semana = calcular_semana_letiva()
    capitulo = calcular_capitulo_esperado(semana)
    trimestre = calcular_trimestre(semana)
    hoje = _hoje()

    st.markdown(f"""
    <div class="context-bar">
        <div class="context-item">
            <div class="valor">{semana}ª</div>
            <div class="rotulo">Semana Letiva</div>
        </div>
        <div class="context-item">
            <div class="valor">Cap {capitulo}/12</div>
            <div class="rotulo">Progressao SAE</div>
        </div>
        <div class="context-item">
            <div class="valor">{trimestre}º Tri</div>
            <div class="rotulo">Trimestre</div>
        </div>
        <div class="context-item">
            <div class="valor">{hoje.strftime('%d/%m/%Y')}</div>
            <div class="rotulo">Hoje</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ========== SECAO 2: SAUDE POR UNIDADE ==========
    st.markdown("### 🏫 Saude por Unidade")

    if filtro_un == "TODAS":
        saude = calcular_saude_unidade(df_aulas, df_horario, semana)
        if saude:
            cols = st.columns(len(saude))
            for i, s in enumerate(saude):
                with cols[i]:
                    st.markdown(f"""
                    <div class="saude-card" style="background: {s['cor']};">
                        <div><strong>{s['nome']}</strong></div>
                        <div class="pct">{s['emoji']} {s['conformidade']:.0f}%</div>
                        <div class="detalhe">
                            {s['aulas_registradas']:,} aulas registradas<br>
                            {s['profs_registrando']}/{s['profs_esperados']} professores<br>
                            {s['profs_sem_registro']} sem registro na semana
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        # Unidade unica selecionada
        saude = calcular_saude_unidade(df_aulas_filt, df_horario_filt, semana)
        if saude:
            s = saude[0]
            st.markdown(f"""
            <div class="saude-card" style="background: {s['cor']}; max-width: 400px;">
                <div><strong>{s['nome']}</strong></div>
                <div class="pct">{s['emoji']} {s['conformidade']:.0f}%</div>
                <div class="detalhe">
                    {s['aulas_registradas']:,} aulas registradas |
                    {s['profs_registrando']}/{s['profs_esperados']} professores |
                    {s['profs_sem_registro']} sem registro na semana
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ========== SECAO 3: METRICAS GERAIS COM DELTA ==========
    st.markdown("---")
    st.markdown("### 📊 Indicadores Gerais")

    m = calcular_metricas_gerais(df_aulas_filt, df_horario_filt, df_ocorr_filt, df_freq_filt, semana)

    metricas = [
        {
            'label': 'Conformidade Geral',
            'value': f"{m['conformidade']:.1f}%",
            'delta': f"{m['delta_conf']:+.1f}pp" if m['delta_conf'] is not None else None,
            'delta_color': 'normal' if m['delta_conf'] and m['delta_conf'] >= 0 else 'inverse',
            'help': 'Aulas registradas / aulas esperadas pela grade',
        },
        {
            'label': 'Aulas Hoje',
            'value': str(m['aulas_hoje']),
            'help': 'Registros lancados com data de hoje',
        },
        {
            'label': 'Conteudo Preenchido',
            'value': f"{m['pct_conteudo']:.0f}%",
            'help': 'Aulas com campo conteudo preenchido',
        },
        {
            'label': 'Professores Ativos',
            'value': f"{m['profs_ativos']}/{m['profs_total']}",
            'help': 'Professores com pelo menos 1 registro',
        },
        {
            'label': 'Alunos em Risco',
            'value': str(m['alunos_risco']) if m['alunos_risco'] is not None else 'N/D',
            'help': f"Frequencia abaixo de {THRESHOLD_FREQUENCIA_LDB}% (LDB)",
        },
        {
            'label': 'Ocorrencias na Semana',
            'value': str(m['ocorr_semana']),
            'help': 'Ocorrencias registradas na semana atual',
        },
    ]

    metricas_em_colunas(metricas)

    # ========== SECAO 4: ALERTAS CRITICOS (TOP 10) ==========
    st.markdown("---")
    st.markdown("### 🚨 Alertas Criticos (TOP 10)")

    alertas = gerar_alertas_criticos(df_aulas_filt, df_horario_filt, df_freq_filt, semana)

    if not alertas:
        st.success("Nenhum alerta critico no momento!")
    else:
        for alerta in alertas:
            if alerta['nivel'] == 'CRITICO':
                st.markdown(f"""
                <div class="alert-critical">
                    <strong>🔴 {alerta['titulo']}</strong><br>
                    <small>{alerta['contexto']}</small><br>
                    <span>{alerta['problema']}</span><br>
                    <em>Acao: {alerta['acao']}</em>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-warning">
                    <strong>🟡 {alerta['titulo']}</strong><br>
                    <small>{alerta['contexto']}</small><br>
                    <span>{alerta['problema']}</span><br>
                    <em>Acao: {alerta['acao']}</em>
                </div>
                """, unsafe_allow_html=True)

    # ========== SECAO 5: PROGRESSO SEMANAL ==========
    st.markdown("---")
    st.markdown("### 📈 Progresso Semanal")

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        aulas_reg = len(df_aulas_filt)
        aulas_esp = len(df_horario_filt) * semana if not df_horario_filt.empty else 0
        render_barra_progresso(
            "Aulas Registradas vs Esperadas",
            aulas_reg,
            max(aulas_esp, 1),
            f"Grade semanal x {semana} semanas",
        )

    with col_p2:
        if aulas_reg > 0:
            com_cont = len(df_aulas_filt[df_aulas_filt['conteudo'].notna() & (df_aulas_filt['conteudo'] != '')])
        else:
            com_cont = 0
        render_barra_progresso(
            "Conteudo Preenchido",
            com_cont,
            max(aulas_reg, 1),
            "Aulas com campo conteudo preenchido",
        )

    with col_p3:
        render_barra_progresso(
            "Progressao SAE",
            capitulo,
            12,
            f"Capitulo {capitulo} de 12 esperado na semana {semana}",
        )

    # ========== SECAO 6: ACESSO RAPIDO ==========
    st.markdown("---")
    st.markdown("### 🔗 Acesso Rapido")

    pages_dir = Path(__file__).parent
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.page_link("pages/14_🧠_Alertas_Inteligentes.py", label="🧠 Alertas Inteligentes", icon="🧠")
        st.page_link("pages/13_🚦_Semáforo_Professor.py", label="🚦 Semaforo Professor", icon="🚦")
        st.page_link("pages/23_🚨_Alerta_Precoce_ABC.py", label="🚨 Alerta Precoce ABC", icon="🚨")
    with col_l2:
        st.page_link("pages/01_📊_Quadro_Gestão.py", label="📊 Quadro de Gestao", icon="📊")
        st.page_link("pages/22_📋_Ocorrências.py", label="📋 Ocorrencias", icon="📋")
        if (pages_dir / "24_🔗_Cruzamento_SIGA_SAE.py").exists():
            st.page_link("pages/24_🔗_Cruzamento_SIGA_SAE.py", label="🔗 Cruzamento SIGA x SAE", icon="🔗")


main()
