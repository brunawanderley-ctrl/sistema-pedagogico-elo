#!/usr/bin/env python3
"""
PÁGINA 9: COMPARATIVOS
Entre unidades, professores da mesma disciplina, séries
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import math
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_SERIES, CORES_UNIDADES, ORDEM_SERIES

st.set_page_config(page_title="Comparativos", page_icon="🔄", layout="wide")
from auth import check_password, logout_button
if not check_password():
    st.stop()
logout_button()

DATA_DIR = Path(__file__).parent.parent / "power_bi"

def calcular_semana_letiva(data_ref=None):
    """Calcula semana letiva baseada em data de referência."""
    inicio = datetime(2026, 1, 26)
    if data_ref is None:
        return 1
    if isinstance(data_ref, str):
        data_ref = datetime.strptime(data_ref, '%Y-%m-%d')
    return max(1, (data_ref - inicio).days // 7 + 1)

def main():
    st.title("🔄 Análise Comparativa")
    st.markdown("**Compare unidades, professores e séries**")

    aulas_path = DATA_DIR / "fato_Aulas.csv"
    horario_path = DATA_DIR / "dim_Horario_Esperado.csv"

    if not aulas_path.exists() or not horario_path.exists():
        st.error("Dados não carregados.")
        return

    df_aulas = pd.read_csv(aulas_path)
    df_aulas['data'] = pd.to_datetime(df_aulas['data'], errors='coerce')
    df_horario = pd.read_csv(horario_path)

    # Define "hoje" - se estamos em 2025, simula 05/02/2026
    hoje = datetime.now()
    if hoje.year < 2026:
        hoje = datetime(2026, 2, 5)

    # Filtra apenas até HOJE
    df_aulas = df_aulas[df_aulas['data'] <= hoje]

    # Calcula semana baseada na última data de registro
    if df_aulas['data'].notna().any():
        data_max = df_aulas['data'].max()
        semana = calcular_semana_letiva(data_max)
    else:
        semana = 1

    # Tabs de comparação
    tab1, tab2, tab3 = st.tabs(["🏫 Entre Unidades", "👨‍🏫 Mesma Disciplina", "📚 Entre Séries"])

    # ========== TAB 1: ENTRE UNIDADES ==========
    with tab1:
        st.header("🏫 Comparativo Entre Unidades")

        # Tabela comparativa (usando data máxima de cada unidade)
        comparativo = []
        for un in ['BV', 'CD', 'JG', 'CDR']:
            df_un = df_aulas[df_aulas['unidade'] == un]
            df_hor_un = df_horario[df_horario['unidade'] == un]

            # Calcula semana baseada na data máxima DA UNIDADE
            if len(df_un) > 0 and df_un['data'].notna().any():
                data_max_un = df_un['data'].max()
                semana_un = calcular_semana_letiva(data_max_un)
            else:
                semana_un = 1

            esperado = len(df_hor_un) * semana_un
            realizado = len(df_un)
            conf = (realizado / esperado * 100) if esperado > 0 else 0

            comparativo.append({
                'Unidade': un,
                'Professores': df_un['professor'].nunique(),
                'Turmas': df_un['turma'].nunique(),
                'Disciplinas': df_un['disciplina'].nunique(),
                'Semanas': semana_un,
                'Aulas Esperadas': esperado,
                'Aulas Registradas': realizado,
                'Conformidade': f'{conf:.1f}%',
                'Status': '✅' if conf >= 85 else ('⚠️' if conf >= 70 else '🔴')
            })

        df_comp = pd.DataFrame(comparativo)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(df_comp, x='Unidade', y=['Aulas Esperadas', 'Aulas Registradas'],
                        title='Esperado vs Registrado por Unidade',
                        barmode='group')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Extrai valor numérico da conformidade
            df_comp['Conf_Num'] = df_comp['Conformidade'].str.replace('%', '').astype(float)
            fig = px.bar(df_comp, x='Unidade', y='Conf_Num',
                        title='Taxa de Conformidade por Unidade',
                        color='Conf_Num', color_continuous_scale='RdYlGn',
                        range_color=[0, 100])
            fig.add_hline(y=85, line_dash="dash", line_color="green",
                         annotation_text="Meta 85%")
            st.plotly_chart(fig, use_container_width=True)

        # Ranking
        st.subheader("🏆 Ranking de Unidades")
        df_rank = df_comp.sort_values('Conf_Num', ascending=False)
        for i, row in df_rank.iterrows():
            pos = list(df_rank['Unidade']).index(row['Unidade']) + 1
            st.markdown(f"**{pos}º** {row['Unidade']} - {row['Conformidade']} {row['Status']}")

    # ========== TAB 2: MESMA DISCIPLINA ==========
    with tab2:
        st.header("👨‍🏫 Professores da Mesma Disciplina")

        st.markdown("""
        Compare o desempenho de professores que lecionam a mesma disciplina
        para identificar discrepâncias e melhores práticas.
        """)

        # Filtro de segmento
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            segmento = st.radio("Segmento:", ['Todos', 'Anos Finais (6º-9º)', 'Ensino Médio (1ª-3ª)'],
                               horizontal=True, key='seg_prof')

        # Aplica filtro de segmento
        df_seg = df_aulas.copy()
        df_hor_seg = df_horario.copy()

        if segmento == 'Anos Finais (6º-9º)':
            df_seg = df_seg[df_seg['serie'].str.contains('Ano', na=False)]
            df_hor_seg = df_hor_seg[df_hor_seg['serie'].str.contains('Ano', na=False)]
        elif segmento == 'Ensino Médio (1ª-3ª)':
            df_seg = df_seg[df_seg['serie'].str.contains('Série|EM', na=False)]
            df_hor_seg = df_hor_seg[df_hor_seg['serie'].str.contains('Série|EM', na=False)]

        with col_s2:
            # Seletor de disciplina (filtrado pelo segmento)
            disciplinas = sorted(df_seg['disciplina'].dropna().unique())
            disc_sel = st.selectbox("Selecione a disciplina:", disciplinas)

        # Filtra
        df_disc = df_seg[df_seg['disciplina'] == disc_sel]
        df_hor_disc = df_hor_seg[df_hor_seg['disciplina'] == disc_sel]

        if len(df_disc) > 0:
            # Agrupa por professor
            profs_comp = []
            for prof in df_disc['professor'].unique():
                df_prof = df_disc[df_disc['professor'] == prof]
                df_hor_prof = df_hor_disc[df_hor_disc['professor'] == prof]

                unidades = ', '.join(df_prof['unidade'].unique())
                turmas = df_prof['turma'].nunique()
                aulas = len(df_prof)
                esperado = len(df_hor_prof) * semana

                # Conteúdos únicos
                conteudos = df_prof['conteudo'].dropna().unique()
                ultimo_conteudo = conteudos[-1] if len(conteudos) > 0 else '-'

                profs_comp.append({
                    'Professor': prof,
                    'Unidades': unidades,
                    'Turmas': turmas,
                    'Aulas Registradas': aulas,
                    'Esperadas': esperado,
                    'Último Conteúdo': ultimo_conteudo[:50] + '...' if len(str(ultimo_conteudo)) > 50 else ultimo_conteudo
                })

            df_profs = pd.DataFrame(profs_comp)
            st.dataframe(df_profs, use_container_width=True, hide_index=True)

            # Gráfico
            fig = px.bar(df_profs, x='Professor', y='Aulas Registradas',
                        title=f'Aulas Registradas - {disc_sel}',
                        color='Unidades')
            st.plotly_chart(fig, use_container_width=True)

            # Alerta de discrepância
            if len(df_profs) > 1:
                max_aulas = df_profs['Aulas Registradas'].max()
                min_aulas = df_profs['Aulas Registradas'].min()
                diff_pct = (max_aulas - min_aulas) / max_aulas * 100 if max_aulas > 0 else 0

                if diff_pct > 30:
                    st.warning(f"""
                    ⚠️ **Discrepância detectada:** Diferença de {diff_pct:.0f}% entre professores.
                    - Mais aulas: {df_profs.loc[df_profs['Aulas Registradas'].idxmax(), 'Professor']} ({max_aulas})
                    - Menos aulas: {df_profs.loc[df_profs['Aulas Registradas'].idxmin(), 'Professor']} ({min_aulas})
                    """)
        else:
            st.info("Nenhum registro encontrado para esta disciplina.")

    # ========== TAB 3: ENTRE SÉRIES ==========
    with tab3:
        st.header("📚 Comparativo Entre Séries")

        # Agrupa por série
        series_comp = []
        for serie in df_aulas['serie'].dropna().unique():
            df_serie = df_aulas[df_aulas['serie'] == serie]
            df_hor_serie = df_horario[df_horario['serie'] == serie]

            esperado = len(df_hor_serie) * semana
            realizado = len(df_serie)
            conf = (realizado / esperado * 100) if esperado > 0 else 0

            series_comp.append({
                'Série': serie,
                'Turmas': df_serie['turma'].nunique(),
                'Professores': df_serie['professor'].nunique(),
                'Disciplinas': df_serie['disciplina'].nunique(),
                'Aulas': realizado,
                'Conformidade': conf
            })

        df_series = pd.DataFrame(series_comp)
        if not df_series.empty:
            df_series = df_series.sort_values('Conformidade', ascending=False)

        # Gráfico
        fig = px.bar(df_series, x='Série', y='Conformidade',
                    title='Conformidade por Série',
                    color='Conformidade', color_continuous_scale='RdYlGn',
                    range_color=[0, 100])
        fig.add_hline(y=85, line_dash="dash", line_color="green")
        st.plotly_chart(fig, use_container_width=True)

        # Tabela
        df_series['Conformidade'] = df_series['Conformidade'].apply(lambda x: f'{x:.1f}%')
        st.dataframe(df_series, use_container_width=True, hide_index=True)

        # Comparativo Anos Finais vs Ensino Médio
        st.subheader("📊 Anos Finais vs Ensino Médio")

        df_fund = df_aulas[df_aulas['serie'].str.contains('Ano', na=False)]
        df_em = df_aulas[df_aulas['serie'].str.contains('Série|EM', na=False)]

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Anos Finais", f"{len(df_fund):,} aulas",
                     delta=f"{df_fund['professor'].nunique()} professores")

        with col2:
            st.metric("Ensino Médio", f"{len(df_em):,} aulas",
                     delta=f"{df_em['professor'].nunique()} professores")

        # Gráfico de comparação
        segmentos = pd.DataFrame({
            'Segmento': ['Anos Finais', 'Ensino Médio'],
            'Aulas': [len(df_fund), len(df_em)],
            'Professores': [df_fund['professor'].nunique(), df_em['professor'].nunique()],
            'Turmas': [df_fund['turma'].nunique(), df_em['turma'].nunique()]
        })

        fig = px.bar(segmentos, x='Segmento', y=['Aulas', 'Professores', 'Turmas'],
                    title='Comparativo por Segmento', barmode='group')
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
