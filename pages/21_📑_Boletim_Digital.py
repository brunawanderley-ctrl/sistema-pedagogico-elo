#!/usr/bin/env python3
"""
PÁGINA 21: BOLETIM DIGITAL
Visão do boletim escolar: notas por trimestre, médias, situação.
Permite visualizar como coordenador ou como se fosse o portal do aluno.

TEMPORARIAMENTE OCULTO — Notas trimestrais de 2026 ainda não disponíveis no SIGA.
Será reativado após lançamento das notas do 1º Trimestre (maio/2026).
"""

import streamlit as st

# --- PÁGINA TEMPORARIAMENTE OCULTA ---
st.set_page_config(page_title="Boletim Digital", page_icon="📑", layout="wide")
st.title("📑 Boletim Digital")
st.info(
    "**Página temporariamente desativada.**\n\n"
    "As notas trimestrais de 2026 ainda não foram lançadas no SIGA. "
    "O 1º Trimestre termina em 10/05/2026 — após o lançamento das notas, "
    "esta página será reativada com dados reais.\n\n"
    "Para consultar o histórico escolar (notas finais de anos anteriores), "
    "utilize a **Página 19 — Painel do Aluno**."
)
st.stop()
# --- FIM DO BLOQUEIO TEMPORÁRIO ---

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_UNIDADES, ORDEM_SERIES
from utils import (
    calcular_semana_letiva, calcular_trimestre, calcular_capitulo_esperado,
    carregar_notas, carregar_alunos, carregar_frequencia_alunos,
    filtrar_ate_hoje, _hoje,
    calcular_media_trimestral, calcular_frequencia_aluno,
    THRESHOLD_FREQUENCIA_LDB, PERIODOS_OPCOES,
    UNIDADES, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM,
)

st.set_page_config(page_title="Boletim Digital", page_icon="📑", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

st.markdown("""
<style>
    .boletim-header {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 100%);
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 15px;
        text-align: center;
    }
    .nota-aprovada { background: #C8E6C9; padding: 8px; border-radius: 4px; text-align: center; font-weight: bold; }
    .nota-recuperacao { background: #FFF9C4; padding: 8px; border-radius: 4px; text-align: center; font-weight: bold; }
    .nota-reprovada { background: #FFCDD2; padding: 8px; border-radius: 4px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def classificar_nota(nota):
    """Classifica nota: >= 7 aprovado, >= 5 recuperacao, < 5 reprovado."""
    if pd.isna(nota):
        return '-', '#F5F5F5'
    if nota >= 7:
        return f'{nota:.1f}', '#C8E6C9'
    elif nota >= 5:
        return f'{nota:.1f}', '#FFF9C4'
    return f'{nota:.1f}', '#FFCDD2'


def main():
    st.title("📑 Boletim Digital")
    st.markdown("**Boletim Escolar | Notas e Frequência por Trimestre**")

    hoje = _hoje()
    semana = calcular_semana_letiva(hoje)
    trimestre = calcular_trimestre(semana)

    df_notas = carregar_notas()
    df_alunos = carregar_alunos()
    df_freq = carregar_frequencia_alunos()

    if df_notas.empty:
        st.warning("⚠️ Dados de notas ainda não extraídos do SIGA.")
        st.info("""
        **Como ativar esta página:**

        1. Execute `python3 explorar_api_alunos.py` para descobrir os endpoints
        2. Os endpoints de notas são:
           - `/api/v1/diario/{id}/notas/` (P0)
           - `/api/v1/planilha_notas_faltas/` (P0)
        3. Após descobrir, a extração populará `fato_Notas.csv`

        **Colunas esperadas:**
        `aluno_id, aluno_nome, unidade, serie, turma, disciplina, avaliacao, nota, trimestre, data_avaliacao`
        """)

        # Preview simulado
        st.markdown("---")
        _mostrar_boletim_simulado(trimestre)
        return

    # ========== VISAO: COORDENADOR OU ALUNO ==========
    tab_coord, tab_turma = st.tabs(["👨‍💼 Visão Coordenação", "📋 Boletim por Turma"])

    # TAB 1: VISAO COORDENACAO
    with tab_coord:
        st.subheader("📊 Panorama de Notas")

        tem_ano = 'ano' in df_notas.columns
        tem_trimestre = 'trimestre' in df_notas.columns
        n_filtros = 3 + (1 if tem_ano else 0) + (1 if tem_trimestre else 0)
        cols_filtro = st.columns(n_filtros)
        idx = 0

        with cols_filtro[idx]:
            unidade_sel = st.selectbox("Unidade:", ['Todas'] + UNIDADES,
                format_func=lambda x: UNIDADES_NOMES.get(x, x) if x != 'Todas' else 'Todas',
                key='bol_unidade')
        idx += 1

        with cols_filtro[idx]:
            series_disp = sorted(df_notas['serie'].unique()) if 'serie' in df_notas.columns else []
            serie_sel = st.selectbox("Série:", ['Todas'] + series_disp, key='bol_serie')
        idx += 1

        # Filtro de ano (dados historicos)
        ano_sel = None
        if tem_ano:
            with cols_filtro[idx]:
                anos_disp = sorted(df_notas['ano'].dropna().unique(), reverse=True)
                ano_sel = st.selectbox("Ano:", anos_disp if anos_disp else [2025], key='bol_ano')
            idx += 1

        # Filtro de trimestre (dados trimestrais)
        tri_sel = 'Todos'
        if tem_trimestre:
            with cols_filtro[idx]:
                tri_sel = st.selectbox("Trimestre:", ['Todos', '1o', '2o', '3o'], key='bol_tri')
            idx += 1

        df = df_notas.copy()
        if unidade_sel != 'Todas' and 'unidade' in df.columns:
            df = df[df['unidade'] == unidade_sel]
        if serie_sel != 'Todas' and 'serie' in df.columns:
            df = df[df['serie'] == serie_sel]
        if ano_sel is not None and 'ano' in df.columns:
            df = df[df['ano'] == ano_sel]
        if tri_sel != 'Todos' and 'trimestre' in df.columns:
            tri_num = {'1o': 1, '2o': 2, '3o': 3}.get(tri_sel)
            df = df[df['trimestre'] == tri_num]

        if df.empty:
            st.info("Sem dados para os filtros selecionados.")
        else:
            # Metricas
            col1, col2, col3, col4 = st.columns(4)
            media = df['nota'].mean() if 'nota' in df.columns else 0
            abaixo_media = len(df[df['nota'] < 7]) if 'nota' in df.columns else 0
            total_avaliacoes = len(df)
            alunos_unicos = df['aluno_id'].nunique() if 'aluno_id' in df.columns else 0

            with col1:
                st.metric("Média Geral", f"{media:.1f}")
            with col2:
                st.metric("Avaliações", total_avaliacoes)
            with col3:
                st.metric("Abaixo de 7.0", abaixo_media)
            with col4:
                st.metric("Alunos", alunos_unicos)

            # Heatmap: Serie x Disciplina (media)
            if 'serie' in df.columns and 'disciplina' in df.columns and 'nota' in df.columns:
                pivot = df.pivot_table(index='serie', columns='disciplina', values='nota', aggfunc='mean').round(1)
                if not pivot.empty:
                    fig = px.imshow(
                        pivot, text_auto=True,
                        color_continuous_scale=['#E53935', '#FBC02D', '#43A047'],
                        range_color=[0, 10],
                        title='Média de Notas (Série x Disciplina)'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

            # Distribuicao de notas
            if 'nota' in df.columns:
                fig2 = px.histogram(
                    df, x='nota', nbins=20,
                    title='Distribuição de Notas',
                    color_discrete_sequence=['#1a237e']
                )
                fig2.add_vline(x=7, line_dash="dash", line_color="green", annotation_text="Média 7.0")
                fig2.add_vline(x=5, line_dash="dash", line_color="red", annotation_text="Recuperação")
                st.plotly_chart(fig2, use_container_width=True)

            # Ranking: disciplinas com pior media
            if 'disciplina' in df.columns and 'nota' in df.columns:
                ranking = df.groupby('disciplina')['nota'].agg(['mean', 'count']).round(1)
                ranking.columns = ['Média', 'Avaliações']
                ranking = ranking.sort_values('Média')
                st.subheader("📉 Disciplinas com Menor Média")
                st.dataframe(ranking.head(10), use_container_width=True)

    # TAB 2: BOLETIM POR TURMA
    with tab_turma:
        st.subheader("📋 Boletim de Turma")

        col_t1, col_t2 = st.columns(2)

        # Turma ou Serie (fallback quando turma nao disponivel)
        tem_turma_col = 'turma' in df_notas.columns and df_notas['turma'].notna().any()
        with col_t1:
            if tem_turma_col:
                turmas_disp = sorted(df_notas['turma'].dropna().unique())
                turma_sel = st.selectbox("Turma:", turmas_disp if turmas_disp else ['N/A'], key='bol_turma')
            else:
                series_turma = sorted(df_notas['serie'].unique()) if 'serie' in df_notas.columns else []
                turma_sel = st.selectbox("Série:", series_turma if series_turma else ['N/A'], key='bol_turma')

        with col_t2:
            if 'trimestre' in df_notas.columns:
                tri_turma = st.selectbox("Trimestre:", [1, 2, 3], index=trimestre - 1, key='bol_turma_tri')
            elif 'ano' in df_notas.columns:
                anos_turma = sorted(df_notas['ano'].dropna().unique(), reverse=True)
                ano_turma = st.selectbox("Ano:", anos_turma if anos_turma else [2025], key='bol_turma_ano')
            else:
                st.info("Sem coluna de período disponível.")

        if turma_sel == 'N/A':
            st.info("Selecione uma turma.")
        else:
            df_turma = df_notas.copy()
            if tem_turma_col:
                df_turma = df_turma[df_turma['turma'] == turma_sel]
            elif 'serie' in df_turma.columns:
                df_turma = df_turma[df_turma['serie'] == turma_sel]
            if 'trimestre' in df_turma.columns:
                df_turma = df_turma[df_turma['trimestre'] == tri_turma]
            elif 'ano' in df_turma.columns:
                df_turma = df_turma[df_turma['ano'] == ano_turma]

            if df_turma.empty:
                label_periodo = f"{tri_turma}o trimestre" if 'trimestre' in df_notas.columns else str(ano_turma) if 'ano' in df_notas.columns else ''
                st.info(f"Sem notas para {turma_sel} em {label_periodo}.")
            elif 'aluno_nome' in df_turma.columns and 'disciplina' in df_turma.columns and 'nota' in df_turma.columns:
                # Pivot: aluno x disciplina
                boletim = df_turma.pivot_table(
                    index='aluno_nome', columns='disciplina', values='nota', aggfunc='mean'
                ).round(1)
                boletim['Media'] = boletim.mean(axis=1).round(1)
                boletim = boletim.sort_values('Media', ascending=False)

                # Colorir
                def colorir_boletim(val):
                    if pd.isna(val):
                        return 'background-color: #F5F5F5'
                    if val >= 7:
                        return 'background-color: #C8E6C9'
                    elif val >= 5:
                        return 'background-color: #FFF9C4'
                    return 'background-color: #FFCDD2'

                st.dataframe(
                    boletim.style.map(colorir_boletim),
                    use_container_width=True, height=500
                )

                # Legenda e resultado
                st.markdown("""
                **Legenda:** 🟢 >= 7.0 (Aprovado) | 🟡 5.0-6.9 (Recuperação) | 🔴 < 5.0 (Reprovado)
                """)
                if 'resultado' in df_turma.columns:
                    resultados = df_turma.groupby('aluno_nome')['resultado'].first().reset_index()
                    aprovados = (resultados['resultado'] == 'A').sum()
                    total = len(resultados)
                    st.caption(f"Aprovados: {aprovados}/{total} ({aprovados/max(1,total)*100:.0f}%)")


def _mostrar_boletim_simulado(trimestre):
    """Preview simulado do boletim."""
    import numpy as np

    st.markdown("""
    <div class="boletim-header">
        <h2 style="margin:0; color:white;">COLÉGIO ELO - BOLETIM ESCOLAR 2026</h2>
        <p style="margin:5px 0 0; opacity:0.8;">SIMULAÇÃO - Execute extração para dados reais</p>
    </div>
    """, unsafe_allow_html=True)

    disciplinas = ['Matemática', 'L. Portuguesa', 'História', 'Geografia', 'Ciências', 'Inglês', 'Arte']
    alunos = ['Ana Silva', 'Bruno Costa', 'Carla Mendes', 'Diego Santos', 'Eva Lima']

    data = {}
    for disc in disciplinas:
        data[disc] = [round(np.random.uniform(4, 10), 1) for _ in alunos]

    df_sim = pd.DataFrame(data, index=alunos)
    df_sim['Media'] = df_sim.mean(axis=1).round(1)

    def colorir(val):
        if val >= 7:
            return 'background-color: #C8E6C9'
        elif val >= 5:
            return 'background-color: #FFF9C4'
        return 'background-color: #FFCDD2'

    st.dataframe(df_sim.style.map(colorir), use_container_width=True)
    st.caption(f"⚠️ Dados simulados | {trimestre}o Trimestre")


if __name__ == "__main__":
    main()
