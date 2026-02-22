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
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_SERIES, CORES_UNIDADES, ORDEM_SERIES
from utils import (
    calcular_semana_letiva, carregar_fato_aulas, carregar_horario_esperado,
    filtrar_ate_hoje, filtrar_por_periodo, PERIODOS_OPCOES, _hoje,
    SERIES_FUND_II, SERIES_EM,
    CONFORMIDADE_BAIXO, CONFORMIDADE_META,
)
from components import (
    filtro_periodo, aplicar_filtro_segmento, cabecalho_pagina,
)


def main():
    cabecalho_pagina("🔄 Análise Comparativa", "Compare unidades, professores e séries")

    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()

    if df_aulas.empty or df_horario.empty:
        st.error("Dados não carregados.")
        return

    df_aulas = filtrar_ate_hoje(df_aulas)

    periodo_sel = filtro_periodo(key="pg09_periodo")
    df_aulas = filtrar_por_periodo(df_aulas, periodo_sel)

    # Calcula semana baseada na ultima data de registro
    if df_aulas['data'].notna().any():
        semana = calcular_semana_letiva(df_aulas['data'].max())
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
                'Status': '✅' if conf >= CONFORMIDADE_META else ('⚠️' if conf >= CONFORMIDADE_BAIXO else '🔴')
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
            fig.add_hline(y=CONFORMIDADE_META, line_dash="dash", line_color="green",
                         annotation_text=f"Meta {CONFORMIDADE_META}%")
            st.plotly_chart(fig, use_container_width=True)

        # Ranking
        st.subheader("🏆 Ranking de Unidades")
        df_rank = df_comp.sort_values('Conf_Num', ascending=False)
        for i, row in df_rank.iterrows():
            pos = list(df_rank['Unidade']).index(row['Unidade']) + 1
            st.markdown(f"**{pos}º** {row['Unidade']} - {row['Conformidade']} {row['Status']}")

    # ========== TAB 2: MESMA DISCIPLINA ==========
    with tab2:
        st.header("👨‍🏫 Comparativo por Disciplina e Série")

        st.markdown("Selecione a disciplina e a série para comparar todas as turmas da rede.")

        # Filtros: disciplina e série
        col_d1, col_d2 = st.columns(2)

        with col_d1:
            disciplinas = sorted(df_aulas['disciplina'].dropna().unique())
            disc_sel = st.selectbox("Disciplina:", disciplinas)

        df_disc = df_aulas[df_aulas['disciplina'] == disc_sel]

        with col_d2:
            series_disc = sorted(df_disc['serie'].dropna().unique(),
                                key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99)
            serie_sel = st.selectbox("Série:", ['Todas'] + series_disc, key='serie_disc')

        if serie_sel != 'Todas':
            df_disc = df_disc[df_disc['serie'] == serie_sel]

        if len(df_disc) > 0:
            hor_slots = df_horario.groupby(['unidade', 'serie', 'disciplina']).size()

            # Agrupa por turma (cada turma = 1 linha)
            turma_comp = []
            for _, row in df_disc.groupby(['turma', 'professor', 'unidade', 'serie']).agg(
                aulas=('data', 'count'),
                conteudos=('conteudo', lambda x: list(x.dropna().unique())),
                ultima_data=('data', 'max'),
            ).reset_index().iterrows():
                slot_key = (row['unidade'], row['serie'], disc_sel)
                esperado_turma = hor_slots.get(slot_key, 0) * semana
                conf = (row['aulas'] / esperado_turma * 100) if esperado_turma > 0 else 0
                conteudos_list = row['conteudos']
                ultimo = conteudos_list[-1] if conteudos_list else '-'

                turma_comp.append({
                    'Unidade': row['unidade'],
                    'Série': row['serie'],
                    'Turma': row['turma'],
                    'Professor': row['professor'],
                    'Aulas': row['aulas'],
                    'Esperadas': esperado_turma,
                    'Conformidade': f'{conf:.0f}%',
                    'Conf_Num': conf,
                    'Conteúdos Únicos': len(conteudos_list),
                    'Último Conteúdo': ultimo[:60] + '...' if len(str(ultimo)) > 60 else ultimo,
                })

            df_turmas = pd.DataFrame(turma_comp)
            if not df_turmas.empty:
                df_turmas = df_turmas.sort_values(['Série', 'Unidade', 'Turma'])

                # Tabela
                df_show = df_turmas.drop(columns=['Conf_Num'])
                st.dataframe(df_show, use_container_width=True, hide_index=True)

                # Gráfico: aulas por turma, cor = unidade
                _titulo = f'{disc_sel} — {serie_sel}' if serie_sel != 'Todas' else f'{disc_sel} — Todas as Séries'
                fig = px.bar(df_turmas, x='Turma', y='Aulas',
                            color='Unidade',
                            color_discrete_map=CORES_UNIDADES,
                            title=f'{_titulo}: Aulas por Turma',
                            hover_data=['Professor', 'Série', 'Conformidade'])
                st.plotly_chart(fig, use_container_width=True)

                # Conformidade por turma
                fig2 = px.bar(df_turmas, x='Turma', y='Conf_Num',
                             color='Unidade',
                             color_discrete_map=CORES_UNIDADES,
                             title=f'{_titulo}: Conformidade por Turma',
                             hover_data=['Professor', 'Série'])
                fig2.add_hline(y=CONFORMIDADE_META, line_dash="dash", line_color="green",
                              annotation_text=f"Meta {CONFORMIDADE_META}%")
                fig2.update_yaxes(title_text="Conformidade (%)")
                st.plotly_chart(fig2, use_container_width=True)

                # Comparativo de conteúdo entre turmas da mesma série
                st.subheader("📋 Conteúdo por Turma")
                for serie in sorted(df_turmas['Série'].unique(),
                                   key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99):
                    df_serie_t = df_turmas[df_turmas['Série'] == serie]
                    with st.expander(f"**{serie}** — {len(df_serie_t)} turmas", expanded=serie_sel != 'Todas'):
                        for _, r in df_serie_t.iterrows():
                            status = '✅' if r['Conf_Num'] >= CONFORMIDADE_META else ('⚠️' if r['Conf_Num'] >= CONFORMIDADE_BAIXO else '🔴')
                            st.markdown(
                                f"{status} **{r['Turma']}** ({r['Unidade']}) — {r['Professor']}: "
                                f"{r['Aulas']} aulas, {r['Conteúdos Únicos']} conteúdos — _{r['Último Conteúdo']}_"
                            )

                # Alerta de discrepância
                if len(df_turmas) > 1:
                    max_conf = df_turmas['Conf_Num'].max()
                    min_conf = df_turmas['Conf_Num'].min()
                    if max_conf - min_conf > 30:
                        melhor = df_turmas.loc[df_turmas['Conf_Num'].idxmax()]
                        pior = df_turmas.loc[df_turmas['Conf_Num'].idxmin()]
                        st.warning(
                            f"⚠️ **Discrepância de {max_conf - min_conf:.0f}pp** entre turmas.\n\n"
                            f"- Melhor: {melhor['Turma']} ({melhor['Unidade']}) — {melhor['Conformidade']}\n"
                            f"- Menor: {pior['Turma']} ({pior['Unidade']}) — {pior['Conformidade']}"
                        )
            else:
                st.info("Nenhum registro encontrado.")
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
            df_series['ordem'] = df_series['Série'].apply(
                lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99)
            df_series = df_series.sort_values('ordem')

        # Gráfico com cores por série
        fig = px.bar(df_series, x='Série', y='Conformidade',
                    title='Conformidade por Série',
                    color='Série',
                    color_discrete_map=CORES_SERIES)
        fig.add_hline(y=CONFORMIDADE_META, line_dash="dash", line_color="green",
                     annotation_text=f"Meta {CONFORMIDADE_META}%")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Tabela
        df_series['Conformidade'] = df_series['Conformidade'].apply(lambda x: f'{x:.1f}%')
        df_series_show = df_series.drop(columns=['ordem'], errors='ignore')
        st.dataframe(df_series_show, use_container_width=True, hide_index=True)

        # Comparativo Anos Finais vs Ensino Médio
        st.subheader("📊 Anos Finais vs Ensino Médio")

        df_fund = df_aulas[df_aulas['serie'].isin(SERIES_FUND_II)]
        df_em = df_aulas[df_aulas['serie'].isin(SERIES_EM)]

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

main()
