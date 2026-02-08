#!/usr/bin/env python3
"""
PAGINA 20: FREQUENCIA ESCOLAR
Dashboard de frequencia individual dos alunos.
Monitoramento do limite LDB de 75% para aprovacao.
Alertas de alunos em risco de reprovacao por faltas.
Suporta dados diretos (fato_Frequencia_Aluno) e derivados (historico de notas).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_UNIDADES, CORES_SERIES, ORDEM_SERIES
from utils import (
    calcular_semana_letiva, calcular_trimestre,
    carregar_frequencia_alunos, carregar_alunos, carregar_fato_aulas,
    filtrar_ate_hoje, filtrar_por_periodo, _hoje,
    calcular_frequencia_aluno, status_frequencia,
    THRESHOLD_FREQUENCIA_LDB, PERIODOS_OPCOES,
    UNIDADES, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM,
)

st.set_page_config(page_title="Frequencia Escolar", page_icon="📊", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

st.markdown("""
<style>
    .risco-card {
        background: #FFEBEE; border-left: 5px solid #D32F2F;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .ok-card {
        background: #E8F5E9; border-left: 5px solid #43A047;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("📊 Frequencia Escolar")
    st.markdown("**Monitoramento de Presenca | Limite LDB: 75%**")

    hoje = _hoje()
    semana = calcular_semana_letiva(hoje)
    trimestre = calcular_trimestre(semana)

    df_freq = carregar_frequencia_alunos()
    df_alunos = carregar_alunos()

    if df_freq.empty:
        st.warning("Dados de frequencia individual ainda nao disponiveis.")
        st.info("Nenhuma fonte de dados de frequencia encontrada (nem fato_Frequencia_Aluno.csv nem historico com faltas).")

        # Mostrar informacoes do fato_Aulas (frequencia da AULA, nao do aluno)
        df_aulas = carregar_fato_aulas()
        if not df_aulas.empty:
            df_aulas = filtrar_ate_hoje(df_aulas)
            st.markdown("---")
            st.subheader("Frequencia de Registro por Aula (dados disponiveis)")
            st.caption("Nota: Esta e a frequencia de REGISTRO das aulas pelo professor, nao a frequencia individual do aluno.")

            if 'frequencia' in df_aulas.columns:
                freq_counts = df_aulas['frequencia'].value_counts()
                fig = px.pie(values=freq_counts.values, names=freq_counts.index,
                            title='Status de Frequencia dos Registros de Aula',
                            color_discrete_sequence=['#43A047', '#FBC02D', '#E53935', '#9E9E9E'])
                st.plotly_chart(fig, use_container_width=True)

                col1, col2, col3 = st.columns(3)
                concluidas = freq_counts.get('CONCLUIDA', 0)
                programadas = freq_counts.get('PROGRAMADA', 0)
                atrasadas = freq_counts.get('ATRASADA', 0)
                with col1:
                    st.metric("Aulas com Chamada", concluidas)
                with col2:
                    st.metric("Programadas", programadas)
                with col3:
                    st.metric("Atrasadas", atrasadas)
        return

    # Detectar fonte dos dados
    is_historico = 'fonte' in df_freq.columns and (df_freq['fonte'] == 'historico').any()
    tem_ano = 'ano' in df_freq.columns
    tem_presente = 'presente' in df_freq.columns

    if is_historico:
        st.info("Dados derivados do historico de notas (faltas/carga horaria por disciplina/ano). "
                "Para frequencia diaria, aguarde a extracao do endpoint de chamada do SIGA.")

    # ========== FILTROS ==========
    n_filtros = 2 + (1 if tem_ano else 0) + (1 if not is_historico else 0)
    cols_filtro = st.columns(n_filtros)
    idx = 0

    with cols_filtro[idx]:
        unidade_sel = st.selectbox("Unidade:", ['Todas'] + UNIDADES,
            format_func=lambda x: UNIDADES_NOMES.get(x, x) if x != 'Todas' else 'Todas',
            key='freq_unidade')
    idx += 1

    with cols_filtro[idx]:
        segmento_sel = st.selectbox("Segmento:", ['Todos', 'Anos Finais', 'Ensino Medio'],
            key='freq_segmento')
    idx += 1

    ano_sel = None
    if tem_ano:
        with cols_filtro[idx]:
            anos_disp = sorted(df_freq['ano'].dropna().unique(), reverse=True)
            ano_sel = st.selectbox("Ano:", anos_disp if anos_disp else [2025], key='freq_ano')
        idx += 1

    if not is_historico and idx < n_filtros:
        with cols_filtro[idx]:
            periodo_sel = st.selectbox("Periodo:", PERIODOS_OPCOES, key='freq_periodo')

    # Aplicar filtros
    df = df_freq.copy()
    if unidade_sel != 'Todas' and 'unidade' in df.columns:
        df = df[df['unidade'] == unidade_sel]
    if segmento_sel == 'Anos Finais' and 'serie' in df.columns:
        df = df[df['serie'].isin(SERIES_FUND_II)]
    elif segmento_sel == 'Ensino Medio' and 'serie' in df.columns:
        df = df[df['serie'].isin(SERIES_EM)]
    if ano_sel is not None and 'ano' in df.columns:
        df = df[df['ano'] == ano_sel]
    if not is_historico:
        df = filtrar_por_periodo(df, periodo_sel)

    if df.empty:
        st.info("Nenhum dado de frequencia para os filtros selecionados.")
        return

    # ========== CALCULAR FREQUENCIA ==========
    if is_historico or 'pct_frequencia' in df.columns:
        # Dados do historico ja tem pct_frequencia por disciplina
        freq_por_aluno = df.copy()
        # Media geral por aluno (todas disciplinas do ano)
        group_cols = ['aluno_id'] if 'aluno_id' in df.columns else []
        if 'aluno_nome' in df.columns:
            group_cols.append('aluno_nome')
        extra_cols = [c for c in ['unidade', 'serie', 'turma'] if c in df.columns]

        if group_cols:
            freq_geral = df.groupby(group_cols).agg(
                total_aulas=('total_aulas', 'sum'),
                presencas=('presencas', 'sum'),
                faltas_total=('faltas', 'sum') if 'faltas' in df.columns else ('total_aulas', 'count'),
            ).reset_index()
            freq_geral['pct_frequencia'] = (freq_geral['presencas'] / freq_geral['total_aulas'].clip(lower=1) * 100).round(1)
            # Trazer unidade/serie do primeiro registro do aluno
            if extra_cols and 'aluno_id' in df.columns:
                extras = df.groupby('aluno_id')[extra_cols].first().reset_index()
                freq_geral = freq_geral.merge(extras, on='aluno_id', how='left')
        else:
            freq_geral = df.copy()
    else:
        # Dados diretos com coluna 'presente'
        freq_por_aluno = calcular_frequencia_aluno(df)
        if freq_por_aluno.empty:
            st.info("Dados insuficientes para calcular frequencia.")
            return
        if 'aluno_nome' in freq_por_aluno.columns:
            freq_geral = freq_por_aluno.groupby('aluno_nome').agg(
                total_aulas=('total_aulas', 'sum'),
                presencas=('presencas', 'sum'),
            ).reset_index()
            freq_geral['pct_frequencia'] = (freq_geral['presencas'] / freq_geral['total_aulas'].clip(lower=1) * 100).round(1)
        else:
            freq_geral = freq_por_aluno.copy()

    # ========== METRICAS ==========
    col1, col2, col3, col4 = st.columns(4)

    media_geral = freq_geral['pct_frequencia'].mean() if 'pct_frequencia' in freq_geral.columns else 0
    em_risco = len(freq_geral[freq_geral['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB]) if 'pct_frequencia' in freq_geral.columns else 0
    total_alunos = freq_geral['aluno_id'].nunique() if 'aluno_id' in freq_geral.columns else len(freq_geral)
    atencao = len(freq_geral[(freq_geral['pct_frequencia'] >= THRESHOLD_FREQUENCIA_LDB) & (freq_geral['pct_frequencia'] < 85)]) if 'pct_frequencia' in freq_geral.columns else 0

    with col1:
        st.metric("Media Geral", f"{media_geral:.1f}%")
    with col2:
        st.metric("Total Alunos", total_alunos)
    with col3:
        st.metric("Em Risco (<75%)", em_risco, delta=f"{'ALERTA' if em_risco > 0 else 'OK'}")
    with col4:
        st.metric("Atencao (75-85%)", atencao)

    # ========== TABS ==========
    tab1, tab2, tab3, tab4 = st.tabs([
        "Alunos em Risco", "Visao Geral", "Por Serie", "Detalhamento"
    ])

    # TAB 1: ALUNOS EM RISCO
    with tab1:
        st.subheader(f"Alunos com Frequencia Abaixo de {THRESHOLD_FREQUENCIA_LDB}%")

        risco = freq_geral[freq_geral['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB].sort_values('pct_frequencia') if 'pct_frequencia' in freq_geral.columns else pd.DataFrame()

        if risco.empty:
            st.success(f"Nenhum aluno com frequencia abaixo de {THRESHOLD_FREQUENCIA_LDB}%!")
        else:
            st.error(f"{len(risco)} aluno(s) em risco de reprovacao por faltas!")

            for _, row in risco.iterrows():
                pct = row['pct_frequencia']
                nome = row.get('aluno_nome', 'N/A')
                total = row.get('total_aulas', 0)
                faltas = total - row.get('presencas', 0)
                serie_info = f" | {row['serie']}" if 'serie' in row.index and pd.notna(row.get('serie')) else ''
                unidade_info = f" | {UNIDADES_NOMES.get(row.get('unidade', ''), row.get('unidade', ''))}" if 'unidade' in row.index and pd.notna(row.get('unidade')) else ''

                st.markdown(f"""
                <div class="risco-card">
                    <strong>{nome}</strong>{serie_info}{unidade_info}
                    <span style="float: right; font-size: 1.2em; font-weight: bold; color: #D32F2F;">{pct:.1f}%</span>
                    <br><small>{int(total)} aulas | {int(faltas)} faltas</small>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("Ver tabela completa"):
                cols_show = [c for c in ['aluno_nome', 'serie', 'unidade', 'total_aulas', 'presencas', 'pct_frequencia'] if c in risco.columns]
                st.dataframe(risco[cols_show], use_container_width=True, hide_index=True)

    # TAB 2: VISAO GERAL
    with tab2:
        st.subheader("Distribuicao de Frequencia")

        if 'pct_frequencia' in freq_geral.columns and len(freq_geral) > 0:
            fig = px.histogram(
                freq_geral, x='pct_frequencia', nbins=20,
                title='Distribuicao da Frequencia dos Alunos',
                labels={'pct_frequencia': '% Frequencia'},
                color_discrete_sequence=['#1a237e']
            )
            fig.add_vline(x=THRESHOLD_FREQUENCIA_LDB, line_dash="dash", line_color="red",
                         annotation_text=f"LDB {THRESHOLD_FREQUENCIA_LDB}%")
            fig.add_vline(x=90, line_dash="dash", line_color="green", annotation_text="Meta 90%")
            st.plotly_chart(fig, use_container_width=True)

            # Box plot por unidade
            if 'unidade' in freq_por_aluno.columns and freq_por_aluno['unidade'].nunique() > 1:
                fig2 = px.box(
                    freq_por_aluno, x='unidade', y='pct_frequencia',
                    color='unidade', color_discrete_map=CORES_UNIDADES,
                    title='Frequencia por Unidade'
                )
                fig2.add_hline(y=THRESHOLD_FREQUENCIA_LDB, line_dash="dash", line_color="red")
                st.plotly_chart(fig2, use_container_width=True)

            # Evolucao por ano (se historico com multiplos anos)
            if is_historico and 'ano' in df_freq.columns:
                # Mostrar evolucao sem filtro de ano
                df_all = df_freq.copy()
                if unidade_sel != 'Todas' and 'unidade' in df_all.columns:
                    df_all = df_all[df_all['unidade'] == unidade_sel]
                if segmento_sel == 'Anos Finais' and 'serie' in df_all.columns:
                    df_all = df_all[df_all['serie'].isin(SERIES_FUND_II)]
                elif segmento_sel == 'Ensino Medio' and 'serie' in df_all.columns:
                    df_all = df_all[df_all['serie'].isin(SERIES_EM)]
                # Media por ano
                anos_com_dados = df_all.groupby('ano')['pct_frequencia'].agg(['mean', 'count']).reset_index()
                anos_com_dados = anos_com_dados[anos_com_dados['count'] >= 10]  # minimo de registros
                if len(anos_com_dados) > 1:
                    fig3 = px.line(
                        anos_com_dados, x='ano', y='mean', markers=True,
                        title='Evolucao da Frequencia Media por Ano',
                        labels={'mean': '% Frequencia Media', 'ano': 'Ano'}
                    )
                    fig3.add_hline(y=THRESHOLD_FREQUENCIA_LDB, line_dash="dash", line_color="red",
                                  annotation_text="LDB 75%")
                    fig3.update_layout(yaxis_range=[60, 100])
                    st.plotly_chart(fig3, use_container_width=True)

    # TAB 3: POR SERIE
    with tab3:
        st.subheader("Frequencia por Serie")

        if 'serie' in freq_por_aluno.columns and 'pct_frequencia' in freq_por_aluno.columns:
            media_serie = freq_por_aluno.groupby('serie')['pct_frequencia'].mean().reset_index()
            media_serie = media_serie.sort_values('pct_frequencia')

            fig = px.bar(
                media_serie, x='pct_frequencia', y='serie', orientation='h',
                color='pct_frequencia',
                color_continuous_scale=['#E53935', '#FBC02D', '#43A047'],
                range_color=[60, 100],
                title='Media de Frequencia por Serie'
            )
            fig.add_vline(x=THRESHOLD_FREQUENCIA_LDB, line_dash="dash", line_color="red")
            fig.update_layout(yaxis_title='', xaxis_title='% Frequencia', height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Heatmap serie x disciplina
            if 'disciplina' in freq_por_aluno.columns:
                pivot = freq_por_aluno.pivot_table(
                    index='serie', columns='disciplina', values='pct_frequencia', aggfunc='mean'
                ).round(1)
                if not pivot.empty:
                    fig3 = px.imshow(
                        pivot, text_auto=True,
                        color_continuous_scale=['#E53935', '#FBC02D', '#43A047'],
                        range_color=[60, 100],
                        title='Heatmap: Frequencia Media (Serie x Disciplina)'
                    )
                    fig3.update_layout(height=400)
                    st.plotly_chart(fig3, use_container_width=True)

            # Alunos em risco por serie
            if 'aluno_id' in freq_por_aluno.columns:
                risco_serie = freq_por_aluno[freq_por_aluno['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB]
                if not risco_serie.empty:
                    risco_count = risco_serie.groupby('serie')['aluno_id'].nunique().reset_index()
                    risco_count.columns = ['serie', 'alunos_risco']
                    total_count = freq_por_aluno.groupby('serie')['aluno_id'].nunique().reset_index()
                    total_count.columns = ['serie', 'total_alunos']
                    risco_count = risco_count.merge(total_count, on='serie', how='left')
                    risco_count['pct_risco'] = (risco_count['alunos_risco'] / risco_count['total_alunos'].clip(lower=1) * 100).round(1)
                    st.subheader("Alunos em Risco por Serie")
                    st.dataframe(risco_count.sort_values('pct_risco', ascending=False),
                                use_container_width=True, hide_index=True)

    # TAB 4: DETALHAMENTO
    with tab4:
        st.subheader("Detalhamento Completo")

        busca = st.text_input("Buscar aluno:", placeholder="Digite o nome do aluno...", key='freq_busca')

        df_show = freq_geral.copy()
        if busca and 'aluno_nome' in df_show.columns:
            df_show = df_show[df_show['aluno_nome'].str.contains(busca, case=False, na=False)]

        if 'pct_frequencia' in df_show.columns:
            df_show['Status'] = df_show['pct_frequencia'].apply(
                lambda x: f"{status_frequencia(x)[0]} {status_frequencia(x)[1]}"
            )
            df_show = df_show.sort_values('pct_frequencia')

        # Selecionar colunas relevantes para exibicao
        cols_display = [c for c in ['aluno_nome', 'serie', 'unidade', 'turma', 'total_aulas',
                                     'presencas', 'pct_frequencia', 'Status'] if c in df_show.columns]
        if cols_display:
            st.dataframe(df_show[cols_display], use_container_width=True, hide_index=True, height=500)
        else:
            st.dataframe(df_show, use_container_width=True, hide_index=True, height=500)

        st.caption(f"Total: {total_alunos} alunos | Limite LDB: {THRESHOLD_FREQUENCIA_LDB}%"
                   + (" | Fonte: Historico de Notas" if is_historico else ""))

        # Detalhamento por disciplina para aluno selecionado
        if is_historico and 'aluno_nome' in df.columns:
            st.markdown("---")
            alunos_lista = sorted(df['aluno_nome'].dropna().unique())
            if alunos_lista:
                aluno_det = st.selectbox("Detalhar aluno:", [''] + alunos_lista, key='freq_det_aluno')
                if aluno_det:
                    df_aluno_det = df[df['aluno_nome'] == aluno_det]
                    cols_det = [c for c in ['disciplina', 'carga_horaria', 'faltas', 'pct_frequencia'] if c in df_aluno_det.columns]
                    if cols_det:
                        det = df_aluno_det[cols_det].sort_values('pct_frequencia')
                        def _color_freq(val):
                            if pd.isna(val):
                                return ''
                            if val >= 90:
                                return 'background-color: #C8E6C9'
                            elif val >= THRESHOLD_FREQUENCIA_LDB:
                                return 'background-color: #FFF9C4'
                            return 'background-color: #FFCDD2'
                        styled = det.style.map(_color_freq, subset=['pct_frequencia']) if 'pct_frequencia' in cols_det else det.style
                        st.dataframe(styled, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
