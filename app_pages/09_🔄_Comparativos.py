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

        # Aplica filtro de segmento (mapeia labels customizados para padrao)
        _seg_map = {
            'Todos': 'Todos',
            'Anos Finais (6º-9º)': 'Anos Finais',
            'Ensino Médio (1ª-3ª)': 'Ensino Medio',
        }
        _seg_norm = _seg_map.get(segmento, segmento)
        df_seg = aplicar_filtro_segmento(df_aulas.copy(), _seg_norm)
        df_hor_seg = aplicar_filtro_segmento(df_horario.copy(), _seg_norm)

        with col_s2:
            # Seletor de disciplina (filtrado pelo segmento)
            disciplinas = sorted(df_seg['disciplina'].dropna().unique())
            disc_sel = st.selectbox("Selecione a disciplina:", disciplinas)

        # Visão: por professor (agregado) ou por turma (detalhado)
        visao = st.radio("Visão:", ['Por Professor', 'Por Turma do Professor'],
                        horizontal=True, key='visao_disc')

        # Filtra
        df_disc = df_seg[df_seg['disciplina'] == disc_sel]
        df_hor_disc = df_hor_seg[df_hor_seg['disciplina'] == disc_sel]

        if len(df_disc) > 0:
            # Pre-calcula slots do horário por (unidade, serie, disciplina) com contagem
            hor_slots = df_hor_seg.groupby(['unidade', 'serie', 'disciplina']).size()

            if visao == 'Por Professor':
                # === VISÃO AGREGADA POR PROFESSOR ===
                profs_comp = []
                for prof in df_disc['professor'].unique():
                    df_prof = df_disc[df_disc['professor'] == prof]

                    unidades = ', '.join(df_prof['unidade'].unique())
                    turmas = df_prof['turma'].nunique()
                    aulas = len(df_prof)

                    prof_slots = set(df_prof.groupby(['unidade', 'serie', 'disciplina']).size().index)
                    aulas_sem_prof = sum(
                        hor_slots.get(slot, 0) for slot in prof_slots
                    )
                    esperado = aulas_sem_prof * semana

                    conteudos = df_prof['conteudo'].dropna().unique()
                    ultimo_conteudo = conteudos[-1] if len(conteudos) > 0 else '-'

                    conf = (aulas / esperado * 100) if esperado > 0 else 0

                    profs_comp.append({
                        'Professor': prof,
                        'Unidades': unidades,
                        'Turmas': turmas,
                        'Aulas Registradas': aulas,
                        'Esperadas': esperado,
                        'Conformidade': f'{conf:.0f}%',
                        'Último Conteúdo': ultimo_conteudo[:50] + '...' if len(str(ultimo_conteudo)) > 50 else ultimo_conteudo
                    })

                df_profs = pd.DataFrame(profs_comp)
                st.dataframe(df_profs, use_container_width=True, hide_index=True)

                fig = px.bar(df_profs, x='Professor', y='Aulas Registradas',
                            title=f'Aulas Registradas - {disc_sel}',
                            color='Unidades',
                            color_discrete_map=CORES_UNIDADES)
                st.plotly_chart(fig, use_container_width=True)

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
                # === VISÃO POR TURMA DO PROFESSOR ===
                turma_comp = []
                for _, row in df_disc.groupby(['professor', 'turma', 'unidade', 'serie']).agg(
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
                        'Professor': row['professor'],
                        'Turma': row['turma'],
                        'Série': row['serie'],
                        'Unidade': row['unidade'],
                        'Aulas': row['aulas'],
                        'Esperadas': esperado_turma,
                        'Conformidade': f'{conf:.0f}%',
                        'Conteúdos Únicos': len(conteudos_list),
                        'Último Conteúdo': ultimo[:60] + '...' if len(str(ultimo)) > 60 else ultimo,
                    })

                df_turmas = pd.DataFrame(turma_comp)
                if not df_turmas.empty:
                    df_turmas = df_turmas.sort_values(['Professor', 'Série', 'Turma'])
                    st.dataframe(df_turmas, use_container_width=True, hide_index=True)

                    # Gráfico por turma
                    fig = px.bar(df_turmas, x='Turma', y='Aulas',
                                color='Professor',
                                title=f'{disc_sel} — Aulas por Turma',
                                barmode='group')
                    st.plotly_chart(fig, use_container_width=True)

                    # Comparativo de conteúdo entre turmas da mesma série
                    st.subheader("📋 Conteúdo por Turma")
                    for serie in sorted(df_turmas['Série'].unique()):
                        df_serie_t = df_turmas[df_turmas['Série'] == serie]
                        if len(df_serie_t) > 1:
                            st.markdown(f"**{serie}** — {len(df_serie_t)} turmas")
                            for _, r in df_serie_t.iterrows():
                                st.markdown(f"- {r['Turma']} ({r['Professor']}): {r['Aulas']} aulas, {r['Conteúdos Únicos']} conteúdos — _{r['Último Conteúdo']}_")
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
