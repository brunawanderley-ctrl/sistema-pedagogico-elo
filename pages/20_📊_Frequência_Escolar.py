#!/usr/bin/env python3
"""
PAGINA 20: FREQUENCIA ESCOLAR
Dashboard de frequencia individual dos alunos com dados REAIS de chamada 2026.
Monitoramento do limite LDB de 75% para aprovacao.
Alertas de alunos em risco de reprovacao por faltas.
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
    carregar_frequencia_alunos, carregar_frequencia_historico,
    carregar_frequencia_detalhada, carregar_alunos,
    status_frequencia,
    THRESHOLD_FREQUENCIA_LDB,
    UNIDADES, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM,
    _hoje,
)
from components import (
    cabecalho_pagina, metricas_em_colunas, botao_download_csv,
    filtro_unidade, filtro_segmento, filtro_serie,
    aplicar_filtro_unidade, aplicar_filtro_segmento, aplicar_filtro_serie,
)

st.set_page_config(page_title="Frequencia Escolar", page_icon="📊", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

# ========== CSS ==========
st.markdown("""
<style>
    .freq-badge-verde { background: #C8E6C9; color: #2E7D32; padding: 4px 10px;
        border-radius: 12px; font-weight: 600; font-size: 0.85em; }
    .freq-badge-amarelo { background: #FFF9C4; color: #F57F17; padding: 4px 10px;
        border-radius: 12px; font-weight: 600; font-size: 0.85em; }
    .freq-badge-vermelho { background: #FFCDD2; color: #C62828; padding: 4px 10px;
        border-radius: 12px; font-weight: 600; font-size: 0.85em; }
    .risco-card {
        background: #FFEBEE; border-left: 5px solid #D32F2F;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .ok-card {
        background: #E8F5E9; border-left: 5px solid #43A047;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .fonte-badge {
        background: #E3F2FD; color: #1565C0; padding: 6px 14px;
        border-radius: 16px; font-weight: 600; font-size: 0.9em;
        display: inline-block; margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


def _color_freq(val):
    """Retorna cor de fundo condicional para pct_frequencia."""
    if pd.isna(val):
        return ''
    if val >= 85:
        return 'background-color: #C8E6C9'  # verde
    elif val >= 70:
        return 'background-color: #FFF9C4'  # amarelo
    return 'background-color: #FFCDD2'  # vermelho


def main():
    cabecalho_pagina(
        "📊 Frequencia Escolar",
        "Monitoramento de Presenca | Limite LDB: 75%",
    )

    hoje = _hoje()
    semana = calcular_semana_letiva(hoje)
    trimestre = calcular_trimestre(semana)

    # ========== CARREGAR DADOS ==========
    df_freq = carregar_frequencia_alunos()

    if df_freq.empty:
        st.warning("Dados de frequencia ainda nao disponiveis.")
        st.info("Nenhuma fonte de dados de frequencia encontrada "
                "(nem fato_Frequencia_Aluno.csv nem historico com faltas).")
        return

    # Detectar fonte dos dados
    is_2026 = 'fonte' in df_freq.columns and (df_freq['fonte'] == '2026_chamada').any()
    is_historico = 'fonte' in df_freq.columns and (df_freq['fonte'] == 'historico').any()

    if is_2026:
        st.markdown(
            '<span class="fonte-badge">Dados reais de frequencia 2026 (chamada diaria)</span>',
            unsafe_allow_html=True,
        )
    elif is_historico:
        st.info("Dados derivados do historico de notas (faltas/carga horaria por disciplina/ano). "
                "Para frequencia diaria, aguarde a extracao do fato_Frequencia_Aluno.csv.")

    # ========== FILTROS ==========
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        unidade_sel = filtro_unidade(todas_label='TODAS', key='freq_un')
    with col_f2:
        segmento_sel = filtro_segmento(key='freq_seg')

    # Preparar series disponiveis ANTES do filtro de serie
    series_disp = sorted(
        df_freq['serie'].dropna().unique().tolist(),
        key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99,
    ) if 'serie' in df_freq.columns else []

    with col_f3:
        serie_sel = filtro_serie(series_disponiveis=series_disp, key='freq_serie')

    # Disciplinas disponiveis
    disc_disp = sorted(df_freq['disciplina'].dropna().unique().tolist()) if 'disciplina' in df_freq.columns else []
    with col_f4:
        disc_sel = st.selectbox("Disciplina", ['Todas'] + disc_disp, key='freq_disc')

    # Aplicar filtros
    df = df_freq.copy()
    df = aplicar_filtro_unidade(df, unidade_sel, todas_label='TODAS')
    df = aplicar_filtro_segmento(df, segmento_sel)
    df = aplicar_filtro_serie(df, serie_sel)
    if disc_sel != 'Todas' and 'disciplina' in df.columns:
        df = df[df['disciplina'] == disc_sel]

    # Filtro de turma (dinâmico, com base nos filtros anteriores)
    turmas_disp = sorted(df['turma'].dropna().unique().tolist()) if 'turma' in df.columns else []
    if turmas_disp:
        turma_sel = st.selectbox("Turma", ['Todas'] + turmas_disp, key='freq_turma')
        if turma_sel != 'Todas' and 'turma' in df.columns:
            df = df[df['turma'] == turma_sel]

    if df.empty:
        st.info("Nenhum dado de frequencia para os filtros selecionados.")
        return

    # ========== CALCULAR METRICAS GLOBAIS ==========
    # Media geral por aluno (media de todas as disciplinas)
    group_aluno_cols = [c for c in ['aluno_id', 'aluno_nome', 'unidade', 'serie', 'turma'] if c in df.columns]
    if 'aluno_id' in df.columns:
        agg_dict = {'total_aulas': ('total_aulas', 'sum')}
        if 'presencas' in df.columns:
            agg_dict['presencas'] = ('presencas', 'sum')
        if 'faltas' in df.columns:
            agg_dict['faltas'] = ('faltas', 'sum')
        if 'justificadas' in df.columns:
            agg_dict['justificadas'] = ('justificadas', 'sum')
        freq_geral = df.groupby(group_aluno_cols).agg(**agg_dict).reset_index()
        if 'presencas' in freq_geral.columns:
            freq_geral['pct_frequencia'] = (freq_geral['presencas'] / freq_geral['total_aulas'].clip(lower=1) * 100).round(1)
    else:
        freq_geral = df.copy()

    total_alunos = freq_geral['aluno_id'].nunique() if 'aluno_id' in freq_geral.columns else len(freq_geral)
    media_geral = freq_geral['pct_frequencia'].mean() if 'pct_frequencia' in freq_geral.columns else 0
    total_faltas = int(df['faltas'].sum()) if 'faltas' in df.columns else 0
    total_justificadas = int(df['justificadas'].sum()) if 'justificadas' in df.columns else 0
    em_risco = len(freq_geral[freq_geral['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB]) if 'pct_frequencia' in freq_geral.columns else 0

    # ========== METRICAS ==========
    metricas_em_colunas([
        {'label': 'Total Alunos', 'value': f"{total_alunos:,}".replace(',', '.')},
        {'label': '% Frequencia Media', 'value': f"{media_geral:.1f}%"},
        {'label': 'Total Faltas', 'value': f"{total_faltas:,}".replace(',', '.'),
         'delta': f"{em_risco} aluno(s) <{THRESHOLD_FREQUENCIA_LDB}%", 'delta_color': 'inverse'},
        {'label': 'Faltas Justificadas', 'value': f"{total_justificadas:,}".replace(',', '.')},
    ])

    st.markdown("---")

    # ========== TABS ==========
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Visao Geral", "Alunos em Risco", "Por Serie/Disciplina",
        "Top 20 Faltas", "Tabela Completa"
    ])

    # ------ TAB 1: VISAO GERAL ------
    with tab1:
        st.subheader("Distribuicao de Frequencia por Unidade")

        if 'unidade' in df.columns and 'pct_frequencia' in df.columns:
            # Agregar por aluno por unidade para box plot
            df_box = df.groupby(['aluno_id', 'unidade']).agg(
                pct_frequencia=('pct_frequencia', 'mean'),
            ).reset_index() if 'aluno_id' in df.columns else df

            fig_box = px.box(
                df_box, x='unidade', y='pct_frequencia',
                color='unidade', color_discrete_map=CORES_UNIDADES,
                title='Frequencia por Unidade',
                labels={'pct_frequencia': '% Frequencia', 'unidade': 'Unidade'},
                category_orders={'unidade': [u for u in ['BV', 'CD', 'JG', 'CDR'] if u in df_box['unidade'].unique()]},
            )
            fig_box.add_hline(y=THRESHOLD_FREQUENCIA_LDB, line_dash="dash", line_color="red",
                              annotation_text=f"LDB {THRESHOLD_FREQUENCIA_LDB}%")
            fig_box.add_hline(y=85, line_dash="dot", line_color="orange", annotation_text="Atencao 85%")
            fig_box.update_layout(showlegend=False, height=450)
            st.plotly_chart(fig_box, use_container_width=True)

        # Histograma geral
        if 'pct_frequencia' in freq_geral.columns and len(freq_geral) > 0:
            fig_hist = px.histogram(
                freq_geral, x='pct_frequencia', nbins=25,
                title='Distribuicao da Frequencia dos Alunos',
                labels={'pct_frequencia': '% Frequencia', 'count': 'Qtd Alunos'},
                color_discrete_sequence=['#1a237e'],
            )
            fig_hist.add_vline(x=THRESHOLD_FREQUENCIA_LDB, line_dash="dash", line_color="red",
                               annotation_text=f"LDB {THRESHOLD_FREQUENCIA_LDB}%")
            fig_hist.add_vline(x=85, line_dash="dot", line_color="orange", annotation_text="Atencao 85%")
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)

        # Media por unidade - barras
        if 'unidade' in freq_geral.columns:
            media_un = freq_geral.groupby('unidade')['pct_frequencia'].mean().reset_index()
            media_un = media_un.sort_values('pct_frequencia', ascending=False)
            media_un['unidade_nome'] = media_un['unidade'].map(UNIDADES_NOMES)

            fig_bar = px.bar(
                media_un, x='unidade_nome', y='pct_frequencia',
                color='unidade', color_discrete_map=CORES_UNIDADES,
                title='Frequencia Media por Unidade',
                labels={'pct_frequencia': '% Frequencia', 'unidade_nome': 'Unidade'},
                text=media_un['pct_frequencia'].round(1).astype(str) + '%',
            )
            fig_bar.add_hline(y=THRESHOLD_FREQUENCIA_LDB, line_dash="dash", line_color="red")
            fig_bar.update_layout(showlegend=False, height=350, yaxis_range=[60, 100])
            fig_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)

    # ------ TAB 2: ALUNOS EM RISCO ------
    with tab2:
        st.subheader(f"Alunos com Frequencia Abaixo de {THRESHOLD_FREQUENCIA_LDB}%")

        risco = freq_geral[freq_geral['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB].sort_values('pct_frequencia') if 'pct_frequencia' in freq_geral.columns else pd.DataFrame()

        if risco.empty:
            st.success(f"Nenhum aluno com frequencia abaixo de {THRESHOLD_FREQUENCIA_LDB}%!")
        else:
            st.error(f"{len(risco)} aluno(s) em risco de reprovacao por faltas!")

            # Cards de alunos em risco
            for _, row in risco.head(30).iterrows():
                pct = row['pct_frequencia']
                nome = row.get('aluno_nome', 'N/A')
                total = row.get('total_aulas', 0)
                n_faltas = row.get('faltas', 0)
                n_just = row.get('justificadas', 0)
                serie_info = f" | {row['serie']}" if 'serie' in row.index and pd.notna(row.get('serie')) else ''
                turma_info = f" | {row['turma']}" if 'turma' in row.index and pd.notna(row.get('turma')) else ''
                unidade_info = f" | {UNIDADES_NOMES.get(row.get('unidade', ''), row.get('unidade', ''))}" if 'unidade' in row.index and pd.notna(row.get('unidade')) else ''

                st.markdown(f"""
                <div class="risco-card">
                    <strong>{nome}</strong>{serie_info}{turma_info}{unidade_info}
                    <span style="float: right; font-size: 1.2em; font-weight: bold; color: #D32F2F;">{pct:.1f}%</span>
                    <br><small>{int(total)} aulas | {int(n_faltas)} faltas | {int(n_just)} justificadas</small>
                </div>
                """, unsafe_allow_html=True)

            if len(risco) > 30:
                st.caption(f"Exibindo 30 de {len(risco)} alunos em risco. Veja a tabela completa na aba 'Tabela Completa'.")

            with st.expander("Tabela completa de alunos em risco"):
                cols_risco = [c for c in ['aluno_nome', 'serie', 'turma', 'unidade', 'total_aulas',
                                          'presencas', 'faltas', 'justificadas', 'pct_frequencia']
                              if c in risco.columns]
                st.dataframe(risco[cols_risco], use_container_width=True, hide_index=True)

        # Alunos em atencao (75-85%)
        atencao = freq_geral[
            (freq_geral['pct_frequencia'] >= THRESHOLD_FREQUENCIA_LDB) &
            (freq_geral['pct_frequencia'] < 85)
        ].sort_values('pct_frequencia') if 'pct_frequencia' in freq_geral.columns else pd.DataFrame()

        if not atencao.empty:
            st.markdown("---")
            st.subheader(f"Alunos em Atencao ({THRESHOLD_FREQUENCIA_LDB}%-85%)")
            st.warning(f"{len(atencao)} aluno(s) com frequencia entre {THRESHOLD_FREQUENCIA_LDB}% e 85%.")
            cols_at = [c for c in ['aluno_nome', 'serie', 'turma', 'unidade',
                                   'total_aulas', 'presencas', 'faltas', 'pct_frequencia']
                       if c in atencao.columns]
            st.dataframe(atencao[cols_at], use_container_width=True, hide_index=True)

    # ------ TAB 3: POR SERIE/DISCIPLINA ------
    with tab3:
        st.subheader("Frequencia por Serie")

        if 'serie' in df.columns and 'pct_frequencia' in df.columns:
            # Media por serie
            media_serie = df.groupby('serie')['pct_frequencia'].mean().reset_index()
            # Ordenar conforme ORDEM_SERIES
            media_serie['ordem'] = media_serie['serie'].apply(
                lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99
            )
            media_serie = media_serie.sort_values('ordem')

            fig_serie = px.bar(
                media_serie, x='serie', y='pct_frequencia',
                color='serie', color_discrete_map=CORES_SERIES,
                title='Frequencia Media por Serie',
                labels={'pct_frequencia': '% Frequencia', 'serie': 'Serie'},
                text=media_serie['pct_frequencia'].round(1).astype(str) + '%',
                category_orders={'serie': [s for s in ORDEM_SERIES if s in media_serie['serie'].values]},
            )
            fig_serie.add_hline(y=THRESHOLD_FREQUENCIA_LDB, line_dash="dash", line_color="red",
                                annotation_text=f"LDB {THRESHOLD_FREQUENCIA_LDB}%")
            fig_serie.update_layout(showlegend=False, height=400, yaxis_range=[60, 100])
            fig_serie.update_traces(textposition='outside')
            st.plotly_chart(fig_serie, use_container_width=True)

        # Heatmap serie x disciplina
        if 'disciplina' in df.columns and 'serie' in df.columns and 'pct_frequencia' in df.columns:
            st.subheader("Heatmap: Frequencia (Serie x Disciplina)")
            pivot = df.pivot_table(
                index='serie', columns='disciplina', values='pct_frequencia', aggfunc='mean'
            ).round(1)
            if not pivot.empty:
                # Reordenar series
                series_order = [s for s in ORDEM_SERIES if s in pivot.index]
                pivot = pivot.reindex(series_order)

                fig_heat = px.imshow(
                    pivot, text_auto=True,
                    color_continuous_scale=['#E53935', '#FBC02D', '#43A047'],
                    range_color=[60, 100],
                    title='Frequencia Media (Serie x Disciplina)',
                    aspect='auto',
                )
                fig_heat.update_layout(height=max(350, len(pivot) * 50 + 150))
                st.plotly_chart(fig_heat, use_container_width=True)

        # Alunos em risco por serie
        if 'aluno_id' in freq_geral.columns and 'serie' in freq_geral.columns:
            st.subheader("Alunos em Risco por Serie")
            risco_serie = freq_geral[freq_geral['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB]
            if not risco_serie.empty:
                risco_count = risco_serie.groupby('serie')['aluno_id'].nunique().reset_index()
                risco_count.columns = ['serie', 'alunos_risco']
                total_count = freq_geral.groupby('serie')['aluno_id'].nunique().reset_index()
                total_count.columns = ['serie', 'total_alunos']
                risco_count = risco_count.merge(total_count, on='serie', how='left')
                risco_count['pct_risco'] = (risco_count['alunos_risco'] / risco_count['total_alunos'].clip(lower=1) * 100).round(1)
                # Ordenar
                risco_count['ordem'] = risco_count['serie'].apply(
                    lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99
                )
                risco_count = risco_count.sort_values('ordem').drop(columns='ordem')
                st.dataframe(risco_count, use_container_width=True, hide_index=True)
            else:
                st.success("Nenhum aluno em risco em nenhuma serie!")

    # ------ TAB 4: TOP 20 FALTAS ------
    with tab4:
        st.subheader("Top 20 Alunos com Mais Faltas")

        if 'faltas' in freq_geral.columns and 'aluno_nome' in freq_geral.columns:
            top_faltas = freq_geral.nlargest(20, 'faltas').copy()
            top_faltas['label'] = top_faltas['aluno_nome'].str[:35]
            if 'serie' in top_faltas.columns:
                top_faltas['label'] = top_faltas['label'] + ' (' + top_faltas['serie'].fillna('') + ')'

            fig_top = px.bar(
                top_faltas.sort_values('faltas'),
                x='faltas', y='label', orientation='h',
                color='pct_frequencia' if 'pct_frequencia' in top_faltas.columns else None,
                color_continuous_scale=['#E53935', '#FBC02D', '#43A047'],
                range_color=[60, 100],
                title='Top 20 Alunos com Mais Faltas',
                labels={'faltas': 'Total de Faltas', 'label': 'Aluno'},
                text='faltas',
            )
            fig_top.update_layout(
                height=max(500, len(top_faltas) * 30 + 100),
                yaxis_title='',
                coloraxis_colorbar_title='% Freq',
            )
            fig_top.update_traces(textposition='outside')
            st.plotly_chart(fig_top, use_container_width=True)

            # Tabela
            cols_top = [c for c in ['aluno_nome', 'serie', 'turma', 'unidade',
                                    'total_aulas', 'presencas', 'faltas', 'justificadas',
                                    'pct_frequencia'] if c in top_faltas.columns]
            st.dataframe(top_faltas[cols_top], use_container_width=True, hide_index=True)
        else:
            st.info("Dados de faltas nao disponiveis para este filtro.")

    # ------ TAB 5: TABELA COMPLETA ------
    with tab5:
        st.subheader("Detalhamento Completo por Aluno")

        busca = st.text_input("Buscar aluno:", placeholder="Digite o nome do aluno...", key='freq_busca')

        # Usar df (por disciplina) para detalhamento completo
        df_show = df.copy()
        if busca and 'aluno_nome' in df_show.columns:
            df_show = df_show[df_show['aluno_nome'].str.contains(busca, case=False, na=False)]

        if df_show.empty:
            st.info("Nenhum resultado encontrado para a busca.")
        else:
            # Adicionar coluna Status
            if 'pct_frequencia' in df_show.columns:
                df_show = df_show.sort_values('pct_frequencia')
                df_show['Status'] = df_show['pct_frequencia'].apply(
                    lambda x: f"{status_frequencia(x)[0]} {status_frequencia(x)[1]}"
                )

            cols_display = [c for c in ['aluno_nome', 'serie', 'turma', 'unidade', 'disciplina',
                                         'total_aulas', 'presencas', 'faltas', 'justificadas',
                                         'pct_frequencia', 'Status'] if c in df_show.columns]

            # Aplicar cores condicionais
            if 'pct_frequencia' in cols_display:
                styled = df_show[cols_display].style.map(
                    _color_freq, subset=['pct_frequencia']
                )
                st.dataframe(styled, use_container_width=True, hide_index=True, height=600)
            else:
                st.dataframe(df_show[cols_display] if cols_display else df_show,
                             use_container_width=True, hide_index=True, height=600)

            st.caption(
                f"Total: {df_show['aluno_id'].nunique() if 'aluno_id' in df_show.columns else len(df_show)} alunos | "
                f"{len(df_show)} registros (aluno x disciplina) | "
                f"Limite LDB: {THRESHOLD_FREQUENCIA_LDB}%"
            )

            # Download
            st.markdown("---")
            botao_download_csv(
                df_show[cols_display] if cols_display else df_show,
                nome_arquivo='frequencia_escolar_2026',
                label='Download Frequencia (CSV)',
                key='freq_download',
            )

        # Detalhamento individual por aluno
        st.markdown("---")
        st.subheader("Detalhamento por Aluno")
        alunos_lista = sorted(df['aluno_nome'].dropna().unique()) if 'aluno_nome' in df.columns else []
        if alunos_lista:
            aluno_det = st.selectbox("Selecionar aluno:", [''] + alunos_lista, key='freq_det_aluno')
            if aluno_det:
                df_aluno = df[df['aluno_nome'] == aluno_det]
                cols_det = [c for c in ['disciplina', 'total_aulas', 'presencas', 'faltas',
                                        'justificadas', 'pct_frequencia'] if c in df_aluno.columns]
                if cols_det:
                    det = df_aluno[cols_det].sort_values('pct_frequencia')
                    styled_det = det.style.map(_color_freq, subset=['pct_frequencia']) if 'pct_frequencia' in cols_det else det.style
                    st.dataframe(styled_det, use_container_width=True, hide_index=True)

                    # Resumo do aluno
                    if 'pct_frequencia' in df_aluno.columns:
                        media_aluno = df_aluno['pct_frequencia'].mean()
                        total_f = int(df_aluno['faltas'].sum()) if 'faltas' in df_aluno.columns else 0
                        total_j = int(df_aluno['justificadas'].sum()) if 'justificadas' in df_aluno.columns else 0
                        emoji, label = status_frequencia(media_aluno)
                        st.markdown(
                            f"**Frequencia media geral:** {media_aluno:.1f}% {emoji} {label} | "
                            f"**Faltas:** {total_f} | **Justificadas:** {total_j}"
                        )


if __name__ == "__main__":
    main()
