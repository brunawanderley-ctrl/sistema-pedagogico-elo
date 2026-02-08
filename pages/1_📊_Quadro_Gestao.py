#!/usr/bin/env python3
"""
PÁGINA 1: QUADRO DE GESTÃO À VISTA
Visão geral com métricas principais e alertas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_SERIES, CORES_UNIDADES, ORDEM_SERIES
from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    status_conformidade, carregar_fato_aulas, carregar_horario_esperado,
    carregar_calendario, filtrar_ate_hoje, _hoje, DATA_DIR
)

st.set_page_config(page_title="Quadro de Gestao", page_icon="📊", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

# CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 5px 0;
    }
    .metric-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .metric-yellow { background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%); }
    .metric-red { background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }
    .alert-critical {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .alert-warning {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

def carregar_dados():
    dados = {}
    df_aulas = carregar_fato_aulas()
    if not df_aulas.empty:
        dados['aulas'] = filtrar_ate_hoje(df_aulas)
    df_horario = carregar_horario_esperado()
    if not df_horario.empty:
        dados['horario'] = df_horario
    df_cal = carregar_calendario()
    if not df_cal.empty:
        dados['calendario'] = df_cal
    return dados

def main():
    st.title("📊 Quadro de Gestão à Vista")
    st.markdown("**Visão Geral da Rede | Atualizado em Tempo Real**")

    dados = carregar_dados()

    if 'aulas' not in dados:
        st.error("Dados não carregados. Execute a extração do SIGA primeiro.")
        return

    df_aulas = dados['aulas']
    df_horario = dados.get('horario', pd.DataFrame())

    # ========== FILTROS NO TOPO ==========
    st.markdown("---")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        unidades = ['TODAS'] + sorted(df_aulas['unidade'].dropna().unique().tolist())
        user_unit = get_user_unit()
        default_un = unidades.index(user_unit) if user_unit and user_unit in unidades else 0
        filtro_un = st.selectbox("🏫 Unidade", unidades, index=default_un)

    with col_f2:
        segmentos = ['TODOS', 'Anos Finais', 'Ensino Médio']
        filtro_seg = st.selectbox("📚 Segmento", segmentos)

    with col_f3:
        series_disp = ['TODAS'] + sorted(df_aulas['serie'].dropna().unique().tolist())
        filtro_serie = st.selectbox("🎓 Série", series_disp)

    with col_f4:
        trimestres = ['ATUAL', '1º Trimestre', '2º Trimestre', '3º Trimestre']
        filtro_tri = st.selectbox("📅 Trimestre", trimestres)

    # Aplica filtros
    df = df_aulas.copy()
    if filtro_un != 'TODAS':
        df = df[df['unidade'] == filtro_un]
    if filtro_seg == 'Anos Finais':
        df = df[df['serie'].str.contains('Ano', na=False)]
    elif filtro_seg == 'Ensino Médio':
        df = df[df['serie'].str.contains('Série|EM', na=False)]
    if filtro_serie != 'TODAS':
        df = df[df['serie'] == filtro_serie]

    # ========== MÉTRICAS PRINCIPAIS ==========
    st.markdown("---")
    st.header("🎯 Indicadores Principais")

    # Calcula semana letiva baseada na data de HOJE
    semana = calcular_semana_letiva()
    capitulo = calcular_capitulo_esperado(semana)
    trimestre = calcular_trimestre(semana)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h1 style="margin:0; font-size: 3em;">{semana}ª</h1>
            <p style="margin:0;">Semana Letiva</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card metric-green">
            <h1 style="margin:0; font-size: 3em;">{capitulo}/12</h1>
            <p style="margin:0;">Capítulo Esperado</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h1 style="margin:0; font-size: 3em;">{trimestre}º</h1>
            <p style="margin:0;">Trimestre</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        total_aulas = len(df)
        st.markdown(f"""
        <div class="metric-card metric-green">
            <h1 style="margin:0; font-size: 3em;">{total_aulas:,}</h1>
            <p style="margin:0;">Aulas Registradas</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        profs_registrando = df['professor'].nunique()
        # Total de professores esperados (do horário)
        if not df_horario.empty:
            df_hor_filtrado = df_horario.copy()
            if filtro_un != 'TODAS':
                df_hor_filtrado = df_hor_filtrado[df_hor_filtrado['unidade'] == filtro_un]
            if filtro_seg == 'Anos Finais':
                df_hor_filtrado = df_hor_filtrado[df_hor_filtrado['serie'].str.contains('Ano', na=False)]
            elif filtro_seg == 'Ensino Médio':
                df_hor_filtrado = df_hor_filtrado[df_hor_filtrado['serie'].str.contains('Série|EM', na=False)]
            profs_esperados = df_hor_filtrado['professor'].nunique()
        else:
            profs_esperados = profs_registrando

        st.markdown(f"""
        <div class="metric-card">
            <h1 style="margin:0; font-size: 2.5em;">{profs_registrando}/{profs_esperados}</h1>
            <p style="margin:0;">Professores Registrando</p>
        </div>
        """, unsafe_allow_html=True)

    # ========== CONFORMIDADE ==========
    st.markdown("---")
    st.header("📈 Taxa de Conformidade")

    if not df_horario.empty:
        # Filtra horário esperado
        df_hor = df_horario.copy()
        if filtro_un != 'TODAS':
            df_hor = df_hor[df_hor['unidade'] == filtro_un]
        if filtro_seg == 'Anos Finais':
            df_hor = df_hor[df_hor['serie'].str.contains('Ano', na=False)]
        elif filtro_seg == 'Ensino Médio':
            df_hor = df_hor[df_hor['serie'].str.contains('Série|EM', na=False)]

        aulas_semana = len(df_hor)
        aulas_esperadas = aulas_semana * semana
        conformidade = (total_aulas / aulas_esperadas * 100) if aulas_esperadas > 0 else 0

        col_c1, col_c2, col_c3 = st.columns(3)

        with col_c1:
            st.metric("Aulas/Semana (Grade)", f"{aulas_semana:,}")
        with col_c2:
            st.metric("Esperado até Agora", f"{aulas_esperadas:,}")
        with col_c3:
            delta = total_aulas - aulas_esperadas
            cor = "normal" if delta >= 0 else "inverse"
            st.metric("Conformidade", f"{conformidade:.1f}%", delta=f"{delta:+,} aulas", delta_color=cor)

        # Gauge de conformidade
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=conformidade,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Taxa de Conformidade Geral"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#4CAF50" if conformidade >= 85 else "#FF9800" if conformidade >= 70 else "#f44336"},
                'steps': [
                    {'range': [0, 50], 'color': "#ffebee"},
                    {'range': [50, 70], 'color': "#fff3e0"},
                    {'range': [70, 85], 'color': "#e8f5e9"},
                    {'range': [85, 100], 'color': "#c8e6c9"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # ========== ALERTAS ==========
    st.markdown("---")
    st.header("⚠️ Alertas Ativos")

    alertas = []

    # Alerta: Professores sem registro
    if not df_horario.empty:
        profs_esperados = set(df_horario['professor'].unique())
        profs_registrados = set(df['professor'].unique())
        profs_sem = profs_esperados - profs_registrados
        if len(profs_sem) > 0:
            alertas.append({
                'tipo': 'CRÍTICO',
                'msg': f'{len(profs_sem)} professores SEM registro no período',
                'detalhe': ', '.join(sorted(list(profs_sem))[:5]) + ('...' if len(profs_sem) > 5 else '')
            })

    # Alerta: Aulas sem conteúdo
    sem_conteudo = df[df['conteudo'].isna() | (df['conteudo'] == '')]
    if len(sem_conteudo) > 0:
        pct = len(sem_conteudo) / total_aulas * 100 if total_aulas > 0 else 0
        alertas.append({
            'tipo': 'ATENÇÃO',
            'msg': f'{len(sem_conteudo)} aulas ({pct:.0f}%) sem conteúdo registrado',
            'detalhe': 'Verifique os registros dos professores'
        })

    # Alerta: Conformidade baixa por unidade
    if not df_horario.empty:
        for un in df_aulas['unidade'].unique():
            df_un = df_aulas[df_aulas['unidade'] == un]
            df_hor_un = df_horario[df_horario['unidade'] == un]

            # Calcula semana baseada na data máxima DA UNIDADE
            if df_un['data'].notna().any():
                data_max_un = df_un['data'].max()
                semana_un = calcular_semana_letiva(data_max_un)
            else:
                semana_un = 1

            esperado_un = len(df_hor_un) * semana_un
            real_un = len(df_un)
            conf_un = (real_un / esperado_un * 100) if esperado_un > 0 else 0
            if conf_un < 70:
                alertas.append({
                    'tipo': 'CRÍTICO',
                    'msg': f'Unidade {un}: conformidade de apenas {conf_un:.0f}%',
                    'detalhe': f'{real_un} registradas de {esperado_un} esperadas (sem {semana_un})'
                })
            elif conf_un < 85:
                alertas.append({
                    'tipo': 'ATENÇÃO',
                    'msg': f'Unidade {un}: conformidade de {conf_un:.0f}%',
                    'detalhe': f'{real_un} registradas de {esperado_un} esperadas (sem {semana_un})'
                })

    if alertas:
        for alerta in alertas:
            if alerta['tipo'] == 'CRÍTICO':
                st.markdown(f"""
                <div class="alert-critical">
                    <strong>🔴 {alerta['tipo']}: {alerta['msg']}</strong><br>
                    <small>{alerta['detalhe']}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-warning">
                    <strong>🟡 {alerta['tipo']}: {alerta['msg']}</strong><br>
                    <small>{alerta['detalhe']}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ Nenhum alerta ativo no momento!")

    # ========== GRÁFICOS ==========
    st.markdown("---")
    st.header("📊 Visão Geral")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        # Por unidade
        df_un = df.groupby('unidade').size().reset_index(name='aulas')
        fig = px.pie(df_un, values='aulas', names='unidade',
                    title='Distribuição por Unidade',
                    color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        # Por série com cores corretas
        df_serie = df.groupby('serie').size().reset_index(name='aulas')
        df_serie['ordem'] = df_serie['serie'].apply(lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99)
        df_serie = df_serie.sort_values('ordem')
        fig = px.bar(df_serie, x='aulas', y='serie', orientation='h',
                    title='Aulas por Série',
                    color='serie',
                    color_discrete_map=CORES_SERIES)
        st.plotly_chart(fig, use_container_width=True)

    # Timeline
    st.subheader("📅 Evolução Temporal")
    df_dia = df.groupby(df['data'].dt.date).size().reset_index(name='aulas')
    df_dia.columns = ['Data', 'Aulas']
    fig = px.area(df_dia, x='Data', y='Aulas', title='Aulas Registradas por Dia')
    st.plotly_chart(fig, use_container_width=True)

    # ========== TABELA RESUMO ==========
    st.markdown("---")
    st.header("📋 Resumo por Unidade")

    resumo = []
    for un in sorted(df_aulas['unidade'].unique()):
        df_un = df_aulas[df_aulas['unidade'] == un]
        df_hor_un = df_horario[df_horario['unidade'] == un] if not df_horario.empty else pd.DataFrame()

        # Calcula semana baseada na data máxima DA UNIDADE
        if df_un['data'].notna().any():
            data_max_un = df_un['data'].max()
            semana_un = calcular_semana_letiva(data_max_un)
        else:
            semana_un = 1

        esperado = len(df_hor_un) * semana_un if not df_hor_un.empty else 0
        real = len(df_un)
        conf = (real / esperado * 100) if esperado > 0 else 0

        resumo.append({
            'Unidade': un,
            'Professores': df_un['professor'].nunique(),
            'Turmas': df_un['turma'].nunique(),
            'Disciplinas': df_un['disciplina'].nunique(),
            'Aulas Registradas': real,
            'Esperadas': esperado,
            'Semanas': semana_un,
            'Conformidade': f"{conf:.1f}%",
            'Status': '✅' if conf >= 85 else ('⚠️' if conf >= 70 else '🔴')
        })

    df_resumo = pd.DataFrame(resumo)
    st.dataframe(df_resumo, use_container_width=True, hide_index=True)

    # ========== RANKING DE PROFESSORES ==========
    if not df_horario.empty:
        st.markdown("---")
        st.header("🏆 Ranking de Professores")

        prof_ranking = []
        for prof in df_horario['professor'].unique():
            df_prof_hor = df_horario[df_horario['professor'] == prof]
            df_prof_aulas = df_aulas[df_aulas['professor'] == prof]
            un = df_prof_hor['unidade'].iloc[0]
            discs = ', '.join(sorted(df_prof_hor['disciplina'].unique())[:2])
            esp = len(df_prof_hor) * semana
            real_p = len(df_prof_aulas)
            conf_p = (real_p / esp * 100) if esp > 0 else 0
            nome = prof.split(' - ')[0] if ' - ' in prof else prof
            prof_ranking.append({
                'Professor': nome,
                'Unidade': un,
                'Disciplinas': discs,
                'Registrado': real_p,
                'Esperado': esp,
                'Conformidade': conf_p,
            })

        df_rank = pd.DataFrame(prof_ranking)
        df_rank = df_rank[df_rank['Esperado'] > 0]

        col_r1, col_r2 = st.columns(2)

        with col_r1:
            st.subheader("🟢 Top 5 - Mais em Dia")
            top5 = df_rank.nlargest(5, 'Conformidade')
            for _, row in top5.iterrows():
                pct = row['Conformidade']
                st.markdown(f"**{row['Professor']}** ({row['Unidade']}) - {row['Disciplinas']} | **{pct:.0f}%**")

        with col_r2:
            st.subheader("🔴 5 que Precisam de Atencao")
            bottom5 = df_rank[df_rank['Conformidade'] < 100].nsmallest(5, 'Conformidade')
            for _, row in bottom5.iterrows():
                pct = row['Conformidade']
                icon = '🔴' if pct < 60 else '🟡'
                st.markdown(f"{icon} **{row['Professor']}** ({row['Unidade']}) - {row['Disciplinas']} | **{pct:.0f}%**")

if __name__ == "__main__":
    main()
