#!/usr/bin/env python3
"""
PAGINA 19: PAINEL DO ALUNO
Perfil individual do aluno: notas, frequencia, ocorrencias, evolucao.
Dashboard 360 graus por aluno com radar de desempenho.
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
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    carregar_alunos, carregar_notas, carregar_frequencia_alunos,
    carregar_ocorrencias, carregar_fato_aulas, filtrar_ate_hoje, _hoje,
    calcular_media_trimestral, calcular_frequencia_aluno,
    status_frequencia, THRESHOLD_FREQUENCIA_LDB,
    UNIDADES, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM, PERIODOS_OPCOES,
    filtrar_por_periodo,
)

st.set_page_config(page_title="Painel do Aluno", page_icon="🎓", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

st.markdown("""
<style>
    .aluno-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 15px;
    }
    .nota-card {
        background: white; border: 1px solid #E0E0E0; padding: 12px;
        border-radius: 8px; text-align: center; margin: 4px;
    }
    .nota-alta { border-left: 4px solid #43A047; }
    .nota-media { border-left: 4px solid #FBC02D; }
    .nota-baixa { border-left: 4px solid #E53935; }
    .freq-ok { color: #43A047; font-weight: bold; }
    .freq-risco { color: #E53935; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("🎓 Painel do Aluno")
    st.markdown("**Visão 360 graus do desempenho individual**")

    hoje = _hoje()
    semana = calcular_semana_letiva(hoje)
    trimestre = calcular_trimestre(semana)

    # Carregar dados
    df_alunos = carregar_alunos()
    df_notas = carregar_notas()
    df_freq = carregar_frequencia_alunos()
    df_ocorr = carregar_ocorrencias()
    df_aulas = carregar_fato_aulas()
    if not df_aulas.empty:
        df_aulas = filtrar_ate_hoje(df_aulas)

    # Verificar se temos dados de alunos
    tem_dados_alunos = not df_alunos.empty
    tem_notas = not df_notas.empty
    tem_freq = not df_freq.empty
    tem_ocorr = not df_ocorr.empty

    if not tem_dados_alunos:
        st.warning("⚠️ Dados de alunos ainda não extraídos do SIGA.")
        st.info("""
        **Para ativar esta página, execute:**

        ```bash
        python3 explorar_api_alunos.py
        ```

        Isso vai descobrir os endpoints da API SIGA para notas, frequência e ocorrências.
        Depois, execute a extração completa para popular os dados.

        **Endpoints necessários:**
        - `/api/v1/diario/{id}/alunos/lista/` → dim_Alunos.csv
        - `/api/v1/diario/{id}/notas/` → fato_Notas.csv
        - `/api/v1/diario/diario_aula/{id}/chamada/` → fato_Frequencia_Aluno.csv
        - `/api/v1/ocorrencia/ocorrencia/lista/` → fato_Ocorrencias.csv
        """)

        # Mostrar preview com dados simulados
        st.markdown("---")
        st.subheader("📋 Preview do Painel (dados simulados)")
        _mostrar_preview_simulado(trimestre, semana)
        return

    # ========== FILTROS ==========
    col_f1, col_f2, col_f3 = st.columns([2, 2, 3])

    with col_f1:
        unidade_selecionada = st.selectbox(
            "Unidade:",
            ['Todas'] + UNIDADES,
            format_func=lambda x: UNIDADES_NOMES.get(x, x) if x != 'Todas' else 'Todas'
        )

    # Filtrar alunos por unidade
    df_alunos_filtrado = df_alunos.copy()
    if unidade_selecionada != 'Todas' and 'unidade' in df_alunos.columns:
        df_alunos_filtrado = df_alunos_filtrado[df_alunos_filtrado['unidade'] == unidade_selecionada]

    with col_f2:
        series_disponiveis = sorted(df_alunos_filtrado['serie'].unique()) if 'serie' in df_alunos_filtrado.columns else []
        serie_sel = st.selectbox("Série:", ['Todas'] + series_disponiveis)

    if serie_sel != 'Todas' and 'serie' in df_alunos_filtrado.columns:
        df_alunos_filtrado = df_alunos_filtrado[df_alunos_filtrado['serie'] == serie_sel]

    with col_f3:
        alunos_lista = sorted(df_alunos_filtrado['aluno_nome'].unique()) if 'aluno_nome' in df_alunos_filtrado.columns else []
        aluno_sel = st.selectbox("Aluno:", alunos_lista if alunos_lista else ['Nenhum aluno'])

    if not alunos_lista:
        st.info("Nenhum aluno encontrado com os filtros selecionados.")
        return

    # Obter ID do aluno
    aluno_info = df_alunos_filtrado[df_alunos_filtrado['aluno_nome'] == aluno_sel].iloc[0] if 'aluno_nome' in df_alunos_filtrado.columns else None
    if aluno_info is None:
        return

    aluno_id = aluno_info.get('aluno_id', None)

    # ========== HEADER DO ALUNO ==========
    st.markdown(f"""
    <div class="aluno-header">
        <h2 style="margin:0; color:white;">👤 {aluno_sel}</h2>
        <p style="margin:5px 0 0; opacity:0.8;">
            {aluno_info.get('serie', '')} | {UNIDADES_NOMES.get(str(aluno_info.get('unidade', '')), '')} |
            Turma: {aluno_info.get('turma', 'N/A')} |
            Matrícula: {aluno_info.get('matricula', 'N/A')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ========== FILTRO DE ANO (dados historicos) ==========
    ano_sel = None
    if tem_notas and 'ano' in df_notas.columns:
        anos_disp = sorted(df_notas['ano'].dropna().unique(), reverse=True)
        if anos_disp:
            ano_sel = st.selectbox("Ano letivo:", anos_disp, key='painel_ano')

    # ========== METRICAS RESUMO ==========
    col1, col2, col3, col4 = st.columns(4)

    # Media geral
    if tem_notas and aluno_id is not None:
        notas_aluno = df_notas[df_notas['aluno_id'] == aluno_id] if 'aluno_id' in df_notas.columns else pd.DataFrame()
        if ano_sel is not None and 'ano' in notas_aluno.columns:
            notas_aluno = notas_aluno[notas_aluno['ano'] == ano_sel]
        media_geral = notas_aluno['nota'].mean() if 'nota' in notas_aluno.columns and not notas_aluno.empty else 0
    else:
        notas_aluno = pd.DataFrame()
        media_geral = 0

    with col1:
        cor = "#43A047" if media_geral >= 7 else "#FBC02D" if media_geral >= 5 else "#E53935"
        st.metric("Média Geral", f"{media_geral:.1f}", delta=None)

    # Frequencia geral
    if tem_freq and aluno_id is not None:
        freq_aluno = calcular_frequencia_aluno(df_freq, aluno_id)
        pct_freq = freq_aluno['pct_frequencia'].mean() if not freq_aluno.empty else 0
    else:
        freq_aluno = pd.DataFrame()
        pct_freq = 0

    with col2:
        emoji_freq, label_freq = status_frequencia(pct_freq) if pct_freq > 0 else ('⬜', 'N/A')
        st.metric("Frequência", f"{pct_freq:.1f}%", delta=f"{emoji_freq} {label_freq}")

    # Ocorrencias
    if tem_ocorr and aluno_id is not None:
        ocorr_aluno = df_ocorr[df_ocorr['aluno_id'] == aluno_id] if 'aluno_id' in df_ocorr.columns else pd.DataFrame()
        total_ocorr = len(ocorr_aluno)
    else:
        ocorr_aluno = pd.DataFrame()
        total_ocorr = 0

    with col3:
        st.metric("Ocorrências", total_ocorr)

    with col4:
        st.metric("Semana Letiva", f"{semana}a", delta=f"{trimestre}o Trimestre")

    # ========== TABS ==========
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Notas", "📅 Frequência", "📋 Ocorrências", "📈 Evolução", "🕸️ Radar"
    ])

    # TAB 1: NOTAS
    with tab1:
        st.subheader("📊 Notas por Disciplina")

        if not notas_aluno.empty and 'disciplina' in notas_aluno.columns:
            # Notas por disciplina e trimestre
            if 'trimestre' in notas_aluno.columns:
                pivot = notas_aluno.pivot_table(
                    index='disciplina', columns='trimestre', values='nota', aggfunc='mean'
                ).round(1)
                pivot.columns = [f"{int(c)}o Tri" for c in pivot.columns]
                pivot['Media'] = pivot.mean(axis=1).round(1)

                # Colorir
                def colorir_nota(val):
                    if pd.isna(val):
                        return 'background-color: #F5F5F5'
                    if val >= 7:
                        return 'background-color: #C8E6C9'
                    elif val >= 5:
                        return 'background-color: #FFF9C4'
                    return 'background-color: #FFCDD2'

                st.dataframe(pivot.style.map(colorir_nota), use_container_width=True)
            else:
                medias = notas_aluno.groupby('disciplina')['nota'].mean().round(1).sort_values(ascending=False)
                fig = px.bar(
                    x=medias.values, y=medias.index, orientation='h',
                    color=medias.values,
                    color_continuous_scale=['#E53935', '#FBC02D', '#43A047'],
                    range_color=[0, 10],
                    title='Média por Disciplina'
                )
                fig.update_layout(yaxis_title='', xaxis_title='Média', height=400)
                st.plotly_chart(fig, use_container_width=True)

            # Detalhamento por avaliacao
            with st.expander("Ver detalhamento por avaliação"):
                cols_show = [c for c in ['disciplina', 'avaliacao', 'nota', 'trimestre', 'ano', 'resultado', 'faltas', 'data_avaliacao'] if c in notas_aluno.columns]
                sort_cols = [c for c in ['disciplina', 'ano'] if c in notas_aluno.columns] or cols_show[:1]
                st.dataframe(notas_aluno[cols_show].sort_values(sort_cols), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma nota registrada para este aluno.")

    # TAB 2: FREQUENCIA
    with tab2:
        st.subheader("📅 Frequência por Disciplina")

        if not freq_aluno.empty:
            # Gauge de frequencia geral
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pct_freq,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Frequência Geral"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': '#1a237e'},
                    'steps': [
                        {'range': [0, 75], 'color': '#FFCDD2'},
                        {'range': [75, 90], 'color': '#FFF9C4'},
                        {'range': [90, 100], 'color': '#C8E6C9'},
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 4},
                        'thickness': 0.75,
                        'value': THRESHOLD_FREQUENCIA_LDB,
                    },
                }
            ))
            fig_gauge.update_layout(height=250)
            st.plotly_chart(fig_gauge, use_container_width=True)

            # Tabela por disciplina
            freq_display = freq_aluno.copy()
            if 'pct_frequencia' in freq_display.columns:
                freq_display['Status'] = freq_display['pct_frequencia'].apply(
                    lambda x: status_frequencia(x)[0] + ' ' + status_frequencia(x)[1]
                )
                freq_display = freq_display.rename(columns={
                    'total_aulas': 'Aulas', 'presencas': 'Presenças',
                    'pct_frequencia': '% Frequência'
                })
                cols_show = [c for c in ['disciplina', 'Aulas', 'Presenças', '% Frequência', 'Status'] if c in freq_display.columns]
                st.dataframe(freq_display[cols_show] if cols_show else freq_display, use_container_width=True, hide_index=True)

                # Alertas de risco
                em_risco = freq_aluno[freq_aluno['pct_frequencia'] < THRESHOLD_FREQUENCIA_LDB]
                if not em_risco.empty:
                    st.error(f"🔴 ALERTA: Aluno com frequência abaixo de {THRESHOLD_FREQUENCIA_LDB}% em {len(em_risco)} disciplina(s)!")
                    for _, row in em_risco.iterrows():
                        st.markdown(f"  - **{row.get('disciplina', '?')}**: {row['pct_frequencia']:.1f}%")
        else:
            st.info("Dados de frequência individual ainda não disponíveis.")

    # TAB 3: OCORRENCIAS
    with tab3:
        st.subheader("📋 Ocorrências Disciplinares")

        if not ocorr_aluno.empty:
            # Timeline
            cols_show = [c for c in ['data', 'tipo', 'descricao', 'responsavel', 'providencia'] if c in ocorr_aluno.columns]
            st.dataframe(
                ocorr_aluno[cols_show].sort_values('data', ascending=False) if 'data' in ocorr_aluno.columns else ocorr_aluno,
                use_container_width=True, hide_index=True
            )

            # Distribuicao por tipo
            if 'tipo' in ocorr_aluno.columns:
                fig = px.pie(ocorr_aluno, names='tipo', title='Distribuição por Tipo')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("Nenhuma ocorrência registrada para este aluno.")

    # TAB 4: EVOLUCAO
    with tab4:
        st.subheader("📈 Evolução ao Longo do Tempo")

        if not notas_aluno.empty and 'trimestre' in notas_aluno.columns and 'disciplina' in notas_aluno.columns:
            evolucao = notas_aluno.groupby(['trimestre', 'disciplina'])['nota'].mean().reset_index()
            fig = px.line(
                evolucao, x='trimestre', y='nota', color='disciplina',
                markers=True, title='Evolução das Médias por Trimestre'
            )
            fig.update_layout(xaxis_title='Trimestre', yaxis_title='Média', yaxis_range=[0, 10])
            fig.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="Meta 7.0")
            fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Mínimo 5.0")
            st.plotly_chart(fig, use_container_width=True)
        elif not notas_aluno.empty and 'ano' in notas_aluno.columns and 'disciplina' in notas_aluno.columns:
            # Dados historicos: evolucao por ano
            notas_todos_anos = df_notas[df_notas['aluno_id'] == aluno_id] if 'aluno_id' in df_notas.columns else pd.DataFrame()
            if not notas_todos_anos.empty:
                evolucao = notas_todos_anos.groupby(['ano', 'disciplina'])['nota'].mean().reset_index()
                fig = px.line(
                    evolucao, x='ano', y='nota', color='disciplina',
                    markers=True, title='Evolução das Médias por Ano'
                )
                fig.update_layout(xaxis_title='Ano', yaxis_title='Média', yaxis_range=[0, 10])
                fig.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="Meta 7.0")
                fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Mínimo 5.0")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Dados insuficientes para evolução temporal.")
        else:
            st.info("Dados insuficientes para evolução temporal.")

    # TAB 5: RADAR
    with tab5:
        st.subheader("🕸️ Radar de Desempenho")

        if not notas_aluno.empty and 'disciplina' in notas_aluno.columns:
            medias = notas_aluno.groupby('disciplina')['nota'].mean()
            if len(medias) >= 3:
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=medias.values.tolist() + [medias.values[0]],
                    theta=medias.index.tolist() + [medias.index[0]],
                    fill='toself',
                    name='Aluno',
                    fillcolor='rgba(26, 35, 126, 0.2)',
                    line_color='#1a237e',
                ))
                # Linha de referencia (media 7)
                fig.add_trace(go.Scatterpolar(
                    r=[7] * (len(medias) + 1),
                    theta=medias.index.tolist() + [medias.index[0]],
                    name='Meta (7.0)',
                    line=dict(color='green', dash='dash'),
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                    title='Desempenho por Disciplina',
                    height=500,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Necessário ao menos 3 disciplinas para o radar.")
        else:
            st.info("Notas não disponíveis para gerar radar.")


def _mostrar_preview_simulado(trimestre, semana):
    """Mostra preview com dados simulados para demonstrar o layout."""
    import numpy as np

    disciplinas = ['Matematica', 'Portugues', 'Historia', 'Geografia', 'Ciencias', 'Ingles']
    notas_sim = [np.random.uniform(5, 10) for _ in disciplinas]

    st.markdown("""
    <div class="aluno-header">
        <h2 style="margin:0; color:white;">👤 Aluno Exemplo (SIMULADO)</h2>
        <p style="margin:5px 0 0; opacity:0.8;">7o Ano | Boa Viagem | Turma A | Mat: 1-00000</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Média Geral", "7.8")
    with col2:
        st.metric("Frequência", "92.3%", delta="✅ Excelente")
    with col3:
        st.metric("Ocorrências", "1")
    with col4:
        st.metric("Semana Letiva", f"{semana}a", delta=f"{trimestre}o Tri")

    # Radar simulado
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=notas_sim + [notas_sim[0]],
        theta=disciplinas + [disciplinas[0]],
        fill='toself', name='Aluno',
        fillcolor='rgba(26, 35, 126, 0.2)', line_color='#1a237e',
    ))
    fig.add_trace(go.Scatterpolar(
        r=[7] * (len(disciplinas) + 1),
        theta=disciplinas + [disciplinas[0]],
        name='Meta (7.0)', line=dict(color='green', dash='dash'),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        title='Radar de Desempenho (SIMULADO)',
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption("⚠️ Dados simulados para demonstração. Execute a extração para dados reais.")


if __name__ == "__main__":
    main()
