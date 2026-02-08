#!/usr/bin/env python3
"""
PAGINA 7: INSTRUMENTOS AVALIATIVOS
Trilhas, avaliacoes, simulados, tarefas - com filtro de periodo e rankings
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    carregar_fato_aulas, filtrar_ate_hoje, filtrar_por_periodo,
    calcular_semana_letiva, calcular_trimestre, _hoje,
    PERIODOS_OPCOES, SERIES_FUND_II, SERIES_EM,
)
from config_cores import CORES_UNIDADES, CORES_SERIES, ORDEM_SERIES

st.set_page_config(page_title="Instrumentos Avaliativos", page_icon="📝", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()


def busca_instrumento(texto, palavras):
    if pd.isna(texto):
        return False
    texto_lower = str(texto).lower()
    return any(p in texto_lower for p in palavras)


def main():
    st.title("📝 Instrumentos Avaliativos")
    st.markdown("**Rankings, tarefas, avaliações e projetos - com filtro de período**")

    df = carregar_fato_aulas()
    if df.empty:
        st.error("Dados não carregados.")
        return

    df = filtrar_ate_hoje(df)
    hoje = _hoje()
    semana_atual = calcular_semana_letiva(hoje)
    trimestre = calcular_trimestre(semana_atual)

    # ========== FILTROS GLOBAIS ==========
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        periodo_sel = st.selectbox("Período:", PERIODOS_OPCOES, key='periodo_instr')

    with col_f2:
        opcoes_un = ['TODAS'] + sorted(df['unidade'].dropna().unique().tolist())
        user_unit = get_user_unit()
        default_un = opcoes_un.index(user_unit) if user_unit and user_unit in opcoes_un else 0
        un_sel = st.selectbox("Unidade:", opcoes_un, index=default_un)

    with col_f3:
        segmento = st.radio("Segmento:", ['Todos', 'Fund II', 'EM'], horizontal=True)

    with col_f4:
        disciplinas = ['TODAS'] + sorted(df['disciplina'].dropna().unique().tolist())
        disc_sel = st.selectbox("Disciplina:", disciplinas)

    # Aplica filtros
    df_f = filtrar_por_periodo(df, periodo_sel)
    if un_sel != 'TODAS':
        df_f = df_f[df_f['unidade'] == un_sel]
    if segmento == 'Fund II':
        df_f = df_f[df_f['serie'].isin(SERIES_FUND_II)]
    elif segmento == 'EM':
        df_f = df_f[df_f['serie'].isin(SERIES_EM)]
    if disc_sel != 'TODAS':
        df_f = df_f[df_f['disciplina'] == disc_sel]

    # Indica periodo ativo
    st.caption(f"Mostrando: **{periodo_sel}** | {len(df_f):,} registros")

    # ========== DETECÇÃO DE INSTRUMENTOS ==========
    df_f['tem_tarefa'] = df_f['tarefa'].notna() & ~df_f['tarefa'].isin(['.', ',', '-', ''])
    df_f['tipo_instrumento'] = 'Aula Regular'

    mask_trilha = df_f['conteudo'].apply(lambda x: busca_instrumento(x, ['trilha', 'digital', 'portal sae', 'oda']))
    mask_avaliacao = df_f['conteudo'].apply(lambda x: busca_instrumento(x, ['avaliação', 'avaliaç', 'prova', 'teste']))
    mask_simulado = df_f['conteudo'].apply(lambda x: busca_instrumento(x, ['simulado', 'enem']))
    mask_projeto = df_f['conteudo'].apply(lambda x: busca_instrumento(x, ['projeto', 'trabalho', 'seminário', 'apresentação']))
    mask_correcao = df_f['conteudo'].apply(lambda x: busca_instrumento(x, ['correção', 'correcao', 'gabarito', 'revisão']))

    df_f.loc[mask_trilha, 'tipo_instrumento'] = 'Trilha Digital'
    df_f.loc[mask_avaliacao, 'tipo_instrumento'] = 'Avaliação'
    df_f.loc[mask_simulado, 'tipo_instrumento'] = 'Simulado'
    df_f.loc[mask_projeto, 'tipo_instrumento'] = 'Projeto/Trabalho'
    df_f.loc[mask_correcao, 'tipo_instrumento'] = 'Correção/Revisão'

    # ========== METRICAS PRINCIPAIS ==========
    st.markdown("---")

    total = len(df_f)
    com_tarefa = df_f['tem_tarefa'].sum()
    pct_tarefa = (com_tarefa / total * 100) if total > 0 else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total Aulas", f"{total:,}")
    with col2:
        st.metric("Com Tarefa", f"{com_tarefa:,}", delta=f"{pct_tarefa:.0f}%")
    with col3:
        st.metric("Trilhas", mask_trilha.sum())
    with col4:
        st.metric("Avaliações", mask_avaliacao.sum())
    with col5:
        st.metric("Simulados", mask_simulado.sum())
    with col6:
        st.metric("Projetos", mask_projeto.sum())

    # ========== TABS ==========
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Rankings",
        "📊 Distribuição",
        "📅 Calendário de Avaliações",
        "📋 Detalhamento",
        "📈 Evolução"
    ])

    # ========== TAB 1: RANKINGS ==========
    with tab1:
        st.header("🏆 Rankings de Professores")

        visao = st.radio("Visão do Ranking:", ['Tarefas', 'Avaliações', 'Trilhas', 'Projetos', 'Score Geral'],
                         horizontal=True)

        if visao == 'Tarefas':
            st.subheader("Professores que Mais Registram Tarefas")
            df_tarefa = df_f[df_f['tem_tarefa']]
            if len(df_tarefa) > 0:
                ranking = df_tarefa.groupby(['professor', 'unidade']).agg(
                    tarefas=('tarefa', 'count'),
                    disciplinas=('disciplina', 'nunique'),
                    turmas=('turma', 'nunique'),
                ).reset_index().sort_values('tarefas', ascending=False)

                # Top 15
                top = ranking.head(15)
                st.dataframe(top.rename(columns={
                    'professor': 'Professor', 'unidade': 'Unidade',
                    'tarefas': 'Tarefas', 'disciplinas': 'Disciplinas', 'turmas': 'Turmas',
                }), use_container_width=True, hide_index=True)

                fig = px.bar(top, x='professor', y='tarefas', color='unidade',
                            color_discrete_map=CORES_UNIDADES,
                            title=f'Top 15 - Tarefas Registradas ({periodo_sel})')
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

                # Bottom 10 (quem menos registra)
                st.subheader("⚠️ Professores com Menos Tarefas")
                bottom = ranking.tail(10).sort_values('tarefas')
                st.dataframe(bottom.rename(columns={
                    'professor': 'Professor', 'unidade': 'Unidade',
                    'tarefas': 'Tarefas', 'disciplinas': 'Disciplinas', 'turmas': 'Turmas',
                }), use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma tarefa registrada no período selecionado.")

        elif visao == 'Avaliações':
            st.subheader("Menções a Avaliações por Professor")
            df_aval = df_f[mask_avaliacao]
            if len(df_aval) > 0:
                ranking = df_aval.groupby(['professor', 'unidade']).size().reset_index(name='mencoes')
                ranking = ranking.sort_values('mencoes', ascending=False)
                st.dataframe(ranking.head(15).rename(columns={
                    'professor': 'Professor', 'unidade': 'Unidade', 'mencoes': 'Menções a Avaliação',
                }), use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma menção a avaliação no período.")

        elif visao == 'Trilhas':
            st.subheader("Uso de Trilhas Digitais SAE")
            df_trilha = df_f[mask_trilha]
            if len(df_trilha) > 0:
                ranking = df_trilha.groupby(['professor', 'unidade', 'disciplina']).size().reset_index(name='mencoes')
                ranking = ranking.sort_values('mencoes', ascending=False)
                st.dataframe(ranking.head(15).rename(columns={
                    'professor': 'Professor', 'unidade': 'Unidade',
                    'disciplina': 'Disciplina', 'mencoes': 'Menções a Trilhas',
                }), use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma menção a trilhas no período.")

        elif visao == 'Projetos':
            st.subheader("Projetos e Trabalhos")
            df_proj = df_f[mask_projeto]
            if len(df_proj) > 0:
                ranking = df_proj.groupby(['professor', 'unidade']).size().reset_index(name='projetos')
                ranking = ranking.sort_values('projetos', ascending=False)
                st.dataframe(ranking.head(15).rename(columns={
                    'professor': 'Professor', 'unidade': 'Unidade', 'projetos': 'Projetos',
                }), use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma menção a projetos no período.")

        else:  # Score Geral
            st.subheader("Score Geral de Instrumentos Avaliativos")
            st.markdown("Score = Tarefas (40pts) + Avaliações (25pts) + Trilhas (20pts) + Projetos (15pts)")

            scores = []
            for prof in df_f['professor'].dropna().unique():
                df_p = df_f[df_f['professor'] == prof]
                un = df_p['unidade'].iloc[0]
                total_p = len(df_p)
                if total_p == 0:
                    continue

                n_tarefa = df_p['tem_tarefa'].sum()
                n_aval = df_p['conteudo'].apply(lambda x: busca_instrumento(x, ['avaliação', 'avaliaç', 'prova', 'teste'])).sum()
                n_trilha = df_p['conteudo'].apply(lambda x: busca_instrumento(x, ['trilha', 'digital', 'portal sae'])).sum()
                n_proj = df_p['conteudo'].apply(lambda x: busca_instrumento(x, ['projeto', 'trabalho', 'seminário'])).sum()

                # Score normalizado
                score_tarefa = min(40, (n_tarefa / total_p) * 40)
                score_aval = min(25, (n_aval / total_p) * 100)
                score_trilha = min(20, (n_trilha / total_p) * 100)
                score_proj = min(15, (n_proj / total_p) * 60)

                scores.append({
                    'Professor': prof,
                    'Unidade': un,
                    'Aulas': total_p,
                    'Tarefas': n_tarefa,
                    'Avaliações': n_aval,
                    'Trilhas': n_trilha,
                    'Projetos': n_proj,
                    'Score': round(score_tarefa + score_aval + score_trilha + score_proj),
                })

            df_scores = pd.DataFrame(scores).sort_values('Score', ascending=False)
            st.dataframe(df_scores.head(20), use_container_width=True, hide_index=True)

    # ========== TAB 2: DISTRIBUICAO ==========
    with tab2:
        st.header("📊 Distribuição de Instrumentos")

        # Por tipo
        tipo_counts = df_f['tipo_instrumento'].value_counts().reset_index()
        tipo_counts.columns = ['Tipo', 'Quantidade']

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(tipo_counts, values='Quantidade', names='Tipo',
                        title=f'Tipos de Atividade ({periodo_sel})')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Taxa de tarefa por unidade
            tarefa_un = df_f.groupby('unidade').agg(
                total=('conteudo', 'count'),
                com_tarefa=('tem_tarefa', 'sum'),
            ).reset_index()
            tarefa_un['pct'] = (tarefa_un['com_tarefa'] / tarefa_un['total'] * 100).round(1)

            fig = px.bar(tarefa_un, x='unidade', y='pct', color='unidade',
                        color_discrete_map=CORES_UNIDADES,
                        title='% de Aulas com Tarefa por Unidade')
            fig.add_hline(y=50, line_dash="dash", line_color="green", annotation_text="Meta 50%")
            st.plotly_chart(fig, use_container_width=True)

        # Por serie
        st.subheader("Taxa de Tarefa por Série")
        tarefa_serie = df_f.groupby('serie').agg(
            total=('conteudo', 'count'),
            com_tarefa=('tem_tarefa', 'sum'),
        ).reset_index()
        tarefa_serie['pct'] = (tarefa_serie['com_tarefa'] / tarefa_serie['total'] * 100).round(1)
        tarefa_serie['ordem'] = tarefa_serie['serie'].apply(
            lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99)
        tarefa_serie = tarefa_serie.sort_values('ordem')

        fig = px.bar(tarefa_serie, x='serie', y='pct', color='serie',
                    color_discrete_map=CORES_SERIES,
                    title='% de Aulas com Tarefa por Série')
        fig.add_hline(y=50, line_dash="dash", line_color="green")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Por disciplina
        st.subheader("Taxa de Tarefa por Disciplina")
        tarefa_disc = df_f.groupby('disciplina').agg(
            total=('conteudo', 'count'),
            com_tarefa=('tem_tarefa', 'sum'),
        ).reset_index()
        tarefa_disc['pct'] = (tarefa_disc['com_tarefa'] / tarefa_disc['total'] * 100).round(1)
        tarefa_disc = tarefa_disc.sort_values('pct', ascending=False)

        fig = px.bar(tarefa_disc, x='disciplina', y='pct',
                    title='% de Aulas com Tarefa por Disciplina',
                    color_discrete_sequence=['#1976D2'])
        fig.add_hline(y=50, line_dash="dash", line_color="green")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # ========== TAB 3: CALENDARIO ==========
    with tab3:
        st.header("📅 Calendário de Avaliações 2026")

        calendario = pd.DataFrame({
            'Trimestre': ['1o', '1o', '1o', '1o', '2o', '2o', '2o', '3o', '3o', '3o', '3o'],
            'Avaliação': ['A1.1-A1.2', 'A1.3-A1.4', 'A1.5-A2', 'Simulado + Rec',
                         'A1', 'A2', 'Simulado + Rec',
                         'A1', 'A2', 'Final', 'Simulado'],
            'Semanas': ['7-8', '8', '11-12', '13-14', '19-20', '24-25', '27-28', '32-33', '37-38', '40', '41'],
            'Período': ['09-13/Mar', '16-20/Mar', '06-17/Abr', '20/Abr-08/Mai',
                       '15-26/Jun', '03-14/Ago', '24-28/Ago',
                       '28/Set-09/Out', '02-13/Nov', '30/Nov-04/Dez', '07-11/Dez'],
            'Conteúdo SAE': ['Caps 1-2', 'Cap 3', 'Caps 4-6', '1o Tri completo',
                            'Caps 7-8', 'Cap 9', '2o Tri completo',
                            'Caps 10-11', 'Cap 12', 'Ano completo', 'Ano completo']
        })

        # Destaca a avaliacao atual
        st.dataframe(calendario, use_container_width=True, hide_index=True)

        # Proxima avaliacao
        avaliacoes_semanas = [(7, 'A1.1-A1.2'), (8, 'A1.3-A1.4'), (11, 'A1.5-A2'), (13, 'Simulado + Rec'),
                              (19, 'A1'), (24, 'A2'), (27, 'Simulado + Rec'),
                              (32, 'A1'), (37, 'A2'), (40, 'Final'), (41, 'Simulado')]

        prox = None
        for sem, nome in avaliacoes_semanas:
            if sem > semana_atual:
                prox = (sem, nome)
                break

        if prox:
            dias_ate = (prox[0] - semana_atual) * 7
            st.info(f"Próxima avaliação: **{prox[1]}** (Semana {prox[0]}, ~{dias_ate} dias)")

    # ========== TAB 4: DETALHAMENTO ==========
    with tab4:
        st.header("📋 Detalhamento de Registros")

        tipo_det = st.selectbox("Tipo de instrumento:", [
            'Todos', 'Aula Regular', 'Trilha Digital', 'Avaliação',
            'Simulado', 'Projeto/Trabalho', 'Correção/Revisão', 'Com Tarefa'
        ])

        df_det = df_f.copy()
        if tipo_det == 'Com Tarefa':
            df_det = df_det[df_det['tem_tarefa']]
        elif tipo_det != 'Todos':
            df_det = df_det[df_det['tipo_instrumento'] == tipo_det]

        df_det = df_det.sort_values('data', ascending=False)

        colunas = ['data', 'unidade', 'serie', 'disciplina', 'professor', 'conteudo', 'tarefa']
        df_show = df_det[colunas].copy()
        df_show['data'] = df_show['data'].dt.strftime('%d/%m/%Y')

        st.caption(f"{len(df_det):,} registros encontrados")
        st.dataframe(df_show.head(100), use_container_width=True, hide_index=True, height=500)

    # ========== TAB 5: EVOLUCAO ==========
    with tab5:
        st.header("📈 Evolução Semanal")

        evolucao = df.copy()
        evolucao = filtrar_ate_hoje(evolucao)
        evolucao['tem_tarefa'] = evolucao['tarefa'].notna() & ~evolucao['tarefa'].isin(['.', ',', '-', ''])

        semanal = evolucao.groupby('semana_letiva').agg(
            total=('conteudo', 'count'),
            com_tarefa=('tem_tarefa', 'sum'),
        ).reset_index()
        semanal['pct_tarefa'] = (semanal['com_tarefa'] / semanal['total'] * 100).round(1)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=semanal['semana_letiva'], y=semanal['total'],
            name='Total Aulas', marker_color='#90CAF9',
        ))
        fig.add_trace(go.Bar(
            x=semanal['semana_letiva'], y=semanal['com_tarefa'],
            name='Com Tarefa', marker_color='#1976D2',
        ))
        fig.add_trace(go.Scatter(
            x=semanal['semana_letiva'], y=semanal['pct_tarefa'],
            name='% Tarefa', yaxis='y2',
            line=dict(color='#E53935', width=3),
            mode='lines+markers',
        ))
        fig.update_layout(
            title='Aulas e Tarefas por Semana Letiva',
            xaxis_title='Semana', yaxis_title='Quantidade',
            yaxis2=dict(title='% com Tarefa', overlaying='y', side='right', range=[0, 100]),
            barmode='overlay', height=450,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Evolucao por unidade
        if un_sel == 'TODAS':
            st.subheader("Evolução por Unidade")
            sem_un = evolucao.groupby(['semana_letiva', 'unidade']).agg(
                com_tarefa=('tem_tarefa', 'sum'),
                total=('conteudo', 'count'),
            ).reset_index()
            sem_un['pct'] = (sem_un['com_tarefa'] / sem_un['total'] * 100).round(1)

            fig = px.line(sem_un, x='semana_letiva', y='pct', color='unidade',
                         color_discrete_map=CORES_UNIDADES,
                         title='% de Aulas com Tarefa por Unidade/Semana',
                         labels={'semana_letiva': 'Semana', 'pct': '% Tarefa'})
            fig.add_hline(y=50, line_dash="dash", line_color="green")
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
