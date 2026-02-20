#!/usr/bin/env python3
"""
PAGINA 26: PAINEL UNIFICADO
Integra dados de Vagas/Matriculas (BI Bruna Marinho) com dados pedagogicos (SIGA).
Cruza matriculas, aulas registradas, ocorrencias, evasao e metas 2026.
"""

import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    carregar_fato_aulas, carregar_ocorrencias, carregar_alunos,
    carregar_horario_esperado, carregar_professores, filtrar_ate_hoje,
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    DATA_DIR, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM, ORDEM_SERIES,
)
from config_cores import CORES_UNIDADES, CORES_SERIES
from shared_domain import (
    UNIDADES_CANONICAL, METAS_2026, META_TOTAL_2026,
    traduzir_unidade_vagas_para_pedagogico,
    nome_unidade_vagas_para_canonico,
    listar_series_intersecao,
    obter_unidade,
)

st.set_page_config(page_title="Painel Unificado", page_icon="📊", layout="wide")
from auth import check_password, logout_button

if not check_password():
    st.stop()
logout_button()

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 20px; border-radius: 10px;
        text-align: center; margin: 5px 0;
    }
    .metric-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .metric-yellow { background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%); }
    .metric-red { background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }
    .metric-blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .progress-bar-container {
        background: #e0e0e0; border-radius: 10px; height: 28px;
        overflow: hidden; margin: 6px 0;
    }
    .progress-bar-fill {
        height: 100%; border-radius: 10px; display: flex;
        align-items: center; justify-content: center;
        font-weight: bold; font-size: 0.85em; color: white;
        transition: width 0.5s ease;
    }
    .info-box {
        background: #e3f2fd; border-left: 4px solid #1976D2;
        padding: 12px; margin: 8px 0; border-radius: 4px;
    }
    .alert-box {
        background: #fff3e0; border-left: 4px solid #ff9800;
        padding: 12px; margin: 8px 0; border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# VAGAS.DB - Caminho e conexao
# ============================================================
VAGAS_DB_PATH = Path("/Users/brunaviegas/Downloads/Cópia BI/output/vagas.db")
VAGAS_2025_DB_PATH = Path("/Users/brunaviegas/Downloads/Cópia BI/output/vagas_2025.db")

# Nomes canônicos das unidades para exibicao
NOMES_UNIDADES_CANONICAL = {
    cod: u.nome for cod, u in UNIDADES_CANONICAL.items()
}


def _vagas_db_disponivel() -> bool:
    """Verifica se o vagas.db esta acessivel."""
    return VAGAS_DB_PATH.exists() and VAGAS_DB_PATH.stat().st_size > 0


def _vagas_2025_disponivel() -> bool:
    """Verifica se o vagas_2025.db esta acessivel."""
    return VAGAS_2025_DB_PATH.exists() and VAGAS_2025_DB_PATH.stat().st_size > 0


# ============================================================
# CARREGAMENTO DE DADOS DO VAGAS.DB
# ============================================================

@st.cache_data(ttl=300)
def carregar_matriculas_vagas():
    """Carrega matriculas da ultima extracao do vagas.db.
    Retorna DataFrame com colunas: unidade_cod_ped, unidade_nome, segmento,
    turma, matriculados, vagas, novatos, veteranos.
    """
    if not _vagas_db_disponivel():
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(VAGAS_DB_PATH, check_same_thread=False)
        df = pd.read_sql_query("""
            SELECT unidade_codigo, unidade_nome, segmento, turma,
                   vagas, novatos, veteranos, matriculados,
                   pre_matriculados, disponiveis
            FROM vagas
            WHERE extracao_id = (SELECT MAX(id) FROM extrações)
        """, conn)
        conn.close()
    except Exception:
        return pd.DataFrame()

    if df.empty:
        return df

    # Traduzir unidade para codigo pedagogico
    df['unidade_cod_ped'] = df['unidade_codigo'].apply(
        traduzir_unidade_vagas_para_pedagogico
    )
    # Nome canonico
    df['unidade_nome_can'] = df['unidade_cod_ped'].map(NOMES_UNIDADES_CANONICAL)
    return df


@st.cache_data(ttl=300)
def carregar_matriculas_2025():
    """Carrega matriculas 2025 para calculo de evasao."""
    if not _vagas_2025_disponivel():
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(VAGAS_2025_DB_PATH, check_same_thread=False)
        df = pd.read_sql_query("""
            SELECT unidade_codigo, turma,
                   SUM(matriculados) as total_2025,
                   SUM(veteranos) as veteranos_2025,
                   SUM(novatos) as novatos_2025
            FROM vagas
            WHERE extracao_id = (SELECT MAX(id) FROM extrações)
            GROUP BY unidade_codigo, turma
        """, conn)
        conn.close()
    except Exception:
        return pd.DataFrame()
    df['unidade_cod_ped'] = df['unidade_codigo'].apply(
        traduzir_unidade_vagas_para_pedagogico
    )
    return df


@st.cache_data(ttl=300)
def carregar_matriculas_2026_evasao():
    """Carrega matriculas 2026 agrupadas por turma para calculo de evasao."""
    if not _vagas_db_disponivel():
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(VAGAS_DB_PATH, check_same_thread=False)
        df = pd.read_sql_query("""
            SELECT unidade_codigo, turma,
                   SUM(matriculados) as total_2026,
                   SUM(veteranos) as veteranos_2026,
                   SUM(novatos) as novatos_2026
            FROM vagas
            WHERE extracao_id = (SELECT MAX(id) FROM extrações)
            GROUP BY unidade_codigo, turma
        """, conn)
        conn.close()
    except Exception:
        return pd.DataFrame()
    df['unidade_cod_ped'] = df['unidade_codigo'].apply(
        traduzir_unidade_vagas_para_pedagogico
    )
    return df


@st.cache_data(ttl=300)
def carregar_ultima_extracao_vagas():
    """Retorna a data da ultima extracao do vagas.db."""
    if not _vagas_db_disponivel():
        return "N/A"
    try:
        conn = sqlite3.connect(VAGAS_DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT data_extracao FROM extrações ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            dt = datetime.fromisoformat(row[0])
            return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        pass
    return "N/A"


# ============================================================
# FUNCOES AUXILIARES
# ============================================================

import re

_PROGRESSAO_SERIE = {
    "Infantil II": "Infantil III",
    "Infantil III": "Infantil IV",
    "Infantil IV": "Infantil V",
    "Infantil V": "1\u00ba Ano",
    "1\u00ba Ano": "2\u00ba Ano",
    "2\u00ba Ano": "3\u00ba Ano",
    "3\u00ba Ano": "4\u00ba Ano",
    "4\u00ba Ano": "5\u00ba Ano",
    "5\u00ba Ano": "6\u00ba Ano",
    "6\u00ba Ano": "7\u00ba Ano",
    "7\u00ba Ano": "8\u00ba Ano",
    "8\u00ba Ano": "9\u00ba Ano",
    "9\u00ba Ano": "1\u00aa S\u00e9rie",
    "1\u00aa S\u00e9rie": "2\u00aa S\u00e9rie",
    "2\u00aa S\u00e9rie": "3\u00aa S\u00e9rie",
    "3\u00aa S\u00e9rie": "Formado",
}


def _extrair_serie_da_turma(nome_turma):
    """Extrai e padroniza a serie a partir do nome da turma do vagas.db."""
    if not nome_turma:
        return None
    nome = nome_turma.lower()

    # Infantil
    if "infantil v" in nome and "infantil vi" not in nome:
        return "Infantil V"
    if "infantil iv" in nome:
        return "Infantil IV"
    if "infantil iii" in nome:
        return "Infantil III"
    if "infantil ii" in nome:
        return "Infantil II"

    # Ensino Medio (serie)
    match = re.search(r"(\d)\s*[ºª°]?\s*s[eé]rie", nome)
    if match:
        return f"{match.group(1)}\u00aa S\u00e9rie"

    # Ensino Medio (ano + medio)
    if "médio" in nome or "medio" in nome:
        match = re.search(r"(\d)\s*[ºª°]?\s*ano", nome)
        if match:
            return f"{match.group(1)}\u00aa S\u00e9rie"

    # Fundamental (ano)
    match = re.search(r"(\d)\s*[ºª°]?\s*ano", nome)
    if match:
        return f"{match.group(1)}\u00ba Ano"

    return None


def _cor_progresso(pct):
    """Retorna cor para barra de progresso baseada no percentual."""
    if pct >= 95:
        return "#43A047"
    elif pct >= 80:
        return "#66BB6A"
    elif pct >= 60:
        return "#FFA726"
    else:
        return "#E53935"


def _render_progress_bar(valor, meta, label=""):
    """Renderiza barra de progresso HTML."""
    pct = (valor / meta * 100) if meta > 0 else 0
    pct_display = min(pct, 100)
    cor = _cor_progresso(pct)
    st.markdown(f"""
    <div style="margin-bottom: 4px; font-size: 0.9em;">
        <strong>{label}</strong> {valor:,} / {meta:,} ({pct:.1f}%)
    </div>
    <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width: {pct_display}%; background: {cor};">
            {pct:.0f}%
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGINA PRINCIPAL
# ============================================================

def main():
    st.title("📊 Painel Unificado")
    st.markdown("**Integracao Vagas/Matriculas + Pedagogico | Colegio ELO 2026**")

    # Verificacao de disponibilidade do vagas.db
    vagas_ok = _vagas_db_disponivel()
    if not vagas_ok:
        st.warning(
            "O banco de dados de Vagas/Matriculas nao foi encontrado em:\n\n"
            f"`{VAGAS_DB_PATH}`\n\n"
            "Os dados de matriculas nao serao exibidos. "
            "Dados pedagogicos continuam disponiveis."
        )

    # Carregar dados
    df_matriculas = carregar_matriculas_vagas() if vagas_ok else pd.DataFrame()
    df_aulas = carregar_fato_aulas()
    df_aulas = filtrar_ate_hoje(df_aulas) if not df_aulas.empty else df_aulas
    df_ocorrencias = carregar_ocorrencias()
    df_horario = carregar_horario_esperado()
    df_professores = carregar_professores()

    # Info de atualizacao
    ultima_vagas = carregar_ultima_extracao_vagas() if vagas_ok else "N/A"
    semana = calcular_semana_letiva()
    trimestre = calcular_trimestre(semana)

    st.markdown(f"""
    <div class="info-box">
        <strong>Semana Letiva:</strong> {semana}a |
        <strong>Trimestre:</strong> {trimestre}o |
        <strong>Ultima extracao Vagas:</strong> {ultima_vagas}
    </div>
    """, unsafe_allow_html=True)

    # ========== ABAS ==========
    tab1, tab2, tab3, tab4 = st.tabs([
        "Visao Geral por Unidade",
        "Cruzamento Matricula x Pedagogico",
        "Evasao x Desempenho",
        "Metas 2026",
    ])

    # ==============================================================
    # ABA 1 - VISAO GERAL POR UNIDADE
    # ==============================================================
    with tab1:
        _render_visao_geral(df_matriculas, df_aulas, df_ocorrencias)

    # ==============================================================
    # ABA 2 - CRUZAMENTO MATRICULA x PEDAGOGICO
    # ==============================================================
    with tab2:
        _render_cruzamento(df_matriculas, df_aulas, df_horario, df_professores)

    # ==============================================================
    # ABA 3 - EVASAO x DESEMPENHO
    # ==============================================================
    with tab3:
        _render_evasao(df_ocorrencias)

    # ==============================================================
    # ABA 4 - METAS 2026
    # ==============================================================
    with tab4:
        _render_metas(df_matriculas)


# ============================================================
# ABA 1 - VISAO GERAL POR UNIDADE
# ============================================================

def _render_visao_geral(df_matriculas, df_aulas, df_ocorrencias):
    st.header("Visao Geral por Unidade")

    # KPIs globais
    total_matriculas = int(df_matriculas['matriculados'].sum()) if not df_matriculas.empty else 0
    total_aulas = len(df_aulas) if not df_aulas.empty else 0
    total_ocorrencias = len(df_ocorrencias) if not df_ocorrencias.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card metric-blue">
            <h1 style="margin:0; font-size: 2.5em;">{total_matriculas:,}</h1>
            <p style="margin:0;">Matriculas 2026</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        pct_meta = (total_matriculas / META_TOTAL_2026 * 100) if META_TOTAL_2026 > 0 else 0
        st.markdown(f"""
        <div class="metric-card {'metric-green' if pct_meta >= 90 else 'metric-yellow' if pct_meta >= 70 else 'metric-red'}">
            <h1 style="margin:0; font-size: 2.5em;">{pct_meta:.1f}%</h1>
            <p style="margin:0;">da Meta Total ({META_TOTAL_2026:,})</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card metric-green">
            <h1 style="margin:0; font-size: 2.5em;">{total_aulas:,}</h1>
            <p style="margin:0;">Aulas Registradas</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card {'metric-yellow' if total_ocorrencias > 1000 else 'metric-green'}">
            <h1 style="margin:0; font-size: 2.5em;">{total_ocorrencias:,}</h1>
            <p style="margin:0;">Ocorrencias</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Barras de progresso de matricula por unidade
    if not df_matriculas.empty:
        st.subheader("Progresso de Matricula vs Meta 2026")
        for cod in ['BV', 'CD', 'JG', 'CDR']:
            unidade = UNIDADES_CANONICAL[cod]
            total_un = int(df_matriculas[df_matriculas['unidade_cod_ped'] == cod]['matriculados'].sum())
            meta_un = unidade.meta_2026
            _render_progress_bar(total_un, meta_un, label=f"{unidade.nome} ({cod})")

        st.markdown("<br>", unsafe_allow_html=True)

    # Tabela resumo por unidade
    st.subheader("Tabela Resumo por Unidade")
    resumo_rows = []
    for cod in ['BV', 'CD', 'JG', 'CDR']:
        unidade = UNIDADES_CANONICAL[cod]
        nome = unidade.nome

        # Matriculas
        if not df_matriculas.empty:
            matr = int(df_matriculas[df_matriculas['unidade_cod_ped'] == cod]['matriculados'].sum())
        else:
            matr = 0

        # Aulas
        if not df_aulas.empty and 'unidade' in df_aulas.columns:
            aulas_un = len(df_aulas[df_aulas['unidade'] == cod])
        else:
            aulas_un = 0

        # Professores
        if not df_aulas.empty and 'professor' in df_aulas.columns:
            profs_un = df_aulas[df_aulas['unidade'] == cod]['professor'].nunique() if 'unidade' in df_aulas.columns else 0
        else:
            profs_un = 0

        # Ocorrencias
        if not df_ocorrencias.empty and 'unidade' in df_ocorrencias.columns:
            ocorr_un = len(df_ocorrencias[df_ocorrencias['unidade'] == cod])
        else:
            ocorr_un = 0

        meta = unidade.meta_2026
        pct = (matr / meta * 100) if meta > 0 else 0

        resumo_rows.append({
            'Unidade': f"{nome} ({cod})",
            'Matriculas': matr,
            'Meta 2026': meta,
            '% Meta': f"{pct:.1f}%",
            'Aulas Registradas': aulas_un,
            'Professores Ativos': profs_un,
            'Ocorrencias': ocorr_un,
        })

    df_resumo = pd.DataFrame(resumo_rows)
    st.dataframe(df_resumo, use_container_width=True, hide_index=True)

    # Grafico comparativo
    if not df_matriculas.empty:
        st.subheader("Matriculas por Segmento e Unidade")
        df_seg = df_matriculas.groupby(['unidade_nome_can', 'segmento'])['matriculados'].sum().reset_index()
        if not df_seg.empty:
            fig = px.bar(
                df_seg, x='unidade_nome_can', y='matriculados', color='segmento',
                title='Distribuicao de Matriculas por Segmento',
                labels={'unidade_nome_can': 'Unidade', 'matriculados': 'Matriculados', 'segmento': 'Segmento'},
                barmode='stack',
                color_discrete_map={
                    'Ed. Infantil': '#a78bfa',
                    'Fund. I': '#4ade80',
                    'Fund. II': '#60a5fa',
                    'Ens. M\u00e9dio': '#fbbf24',
                },
            )
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)


# ============================================================
# ABA 2 - CRUZAMENTO MATRICULA x PEDAGOGICO
# ============================================================

def _render_cruzamento(df_matriculas, df_aulas, df_horario, df_professores):
    st.header("Cruzamento Matricula x Pedagogico")

    # Series que existem em ambos os sistemas
    series_intersecao = listar_series_intersecao()

    if df_matriculas.empty:
        st.warning("Dados de matriculas nao disponiveis. Impossivel realizar cruzamento.")
        return

    if df_aulas.empty:
        st.warning("Dados de aulas nao disponiveis. Impossivel realizar cruzamento.")
        return

    # Filtro de unidade
    opcoes_unidade = ['TODAS'] + [f"{UNIDADES_CANONICAL[c].nome} ({c})" for c in ['BV', 'CD', 'JG', 'CDR']]
    filtro_un = st.selectbox("Filtrar por Unidade", opcoes_unidade, key="cruz_un")

    cod_filtro = None
    if filtro_un != 'TODAS':
        # Extrair codigo do parentesis
        cod_filtro = filtro_un.split('(')[-1].replace(')', '').strip()

    # Extrair serie das turmas do vagas
    df_mat = df_matriculas.copy()
    df_mat['serie'] = df_mat['turma'].apply(_extrair_serie_da_turma)
    # Filtrar apenas series cobertas pelo pedagogico
    df_mat = df_mat[df_mat['serie'].isin(series_intersecao)]

    # Agrupar matriculas por unidade e serie
    mat_por_serie = df_mat.groupby(['unidade_cod_ped', 'serie']).agg(
        matriculados=('matriculados', 'sum'),
        turmas_vagas=('turma', 'nunique'),
    ).reset_index()

    # Agrupar aulas por unidade e serie
    aulas_por_serie = df_aulas.groupby(['unidade', 'serie']).agg(
        aulas=('aula_id', 'count') if 'aula_id' in df_aulas.columns else ('data', 'count'),
        professores=('professor', 'nunique'),
        disciplinas=('disciplina', 'nunique'),
    ).reset_index()
    aulas_por_serie.rename(columns={'unidade': 'unidade_cod_ped'}, inplace=True)

    # Merge
    df_cruz = mat_por_serie.merge(
        aulas_por_serie, on=['unidade_cod_ped', 'serie'], how='outer'
    )
    df_cruz['matriculados'] = df_cruz['matriculados'].fillna(0).astype(int)
    df_cruz['aulas'] = df_cruz['aulas'].fillna(0).astype(int)
    df_cruz['professores'] = df_cruz['professores'].fillna(0).astype(int)
    df_cruz['disciplinas'] = df_cruz['disciplinas'].fillna(0).astype(int)

    # Adicionar nome da unidade
    df_cruz['unidade_nome'] = df_cruz['unidade_cod_ped'].map(NOMES_UNIDADES_CANONICAL)

    # Aplicar filtro
    if cod_filtro:
        df_cruz = df_cruz[df_cruz['unidade_cod_ped'] == cod_filtro]

    if df_cruz.empty:
        st.info("Nenhum dado encontrado para os filtros selecionados.")
        return

    # Calcular ratio (aulas por aluno)
    df_cruz['aulas_por_aluno'] = df_cruz.apply(
        lambda r: round(r['aulas'] / r['matriculados'], 1) if r['matriculados'] > 0 else 0, axis=1
    )

    # Ordenar por serie
    df_cruz['ordem'] = df_cruz['serie'].apply(
        lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99
    )
    df_cruz = df_cruz.sort_values(['unidade_cod_ped', 'ordem'])

    # Tabela
    st.subheader("Por Serie: Matriculados vs Registros Pedagogicos")
    df_display = df_cruz[[
        'unidade_nome', 'serie', 'matriculados', 'aulas',
        'professores', 'disciplinas', 'aulas_por_aluno'
    ]].rename(columns={
        'unidade_nome': 'Unidade',
        'serie': 'Serie',
        'matriculados': 'Matriculados',
        'aulas': 'Aulas Registradas',
        'professores': 'Professores',
        'disciplinas': 'Disciplinas',
        'aulas_por_aluno': 'Aulas/Aluno',
    })

    # Highlight series com poucos registros
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Alertas: series com muitos alunos mas poucas aulas
    st.subheader("Alertas: Series com Baixa Cobertura Pedagogica")
    df_alerta = df_cruz[
        (df_cruz['matriculados'] > 30) & (df_cruz['aulas_por_aluno'] < 1)
    ]
    if not df_alerta.empty:
        for _, row in df_alerta.iterrows():
            st.markdown(f"""
            <div class="alert-box">
                <strong>{row['unidade_nome']} - {row['serie']}</strong>:
                {int(row['matriculados'])} alunos matriculados mas apenas
                {int(row['aulas'])} aulas registradas
                ({row['aulas_por_aluno']} aulas/aluno)
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("Nenhuma serie com baixa cobertura pedagogica identificada.")

    # Grafico de barras agrupadas
    st.subheader("Comparativo Visual")
    if cod_filtro:
        df_graf = df_cruz.copy()
    else:
        # Agregar por serie (todas as unidades)
        df_graf = df_cruz.groupby('serie').agg(
            matriculados=('matriculados', 'sum'),
            aulas=('aulas', 'sum'),
            professores=('professores', 'sum'),
        ).reset_index()
        df_graf['ordem'] = df_graf['serie'].apply(
            lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99
        )
        df_graf = df_graf.sort_values('ordem')

    # Normalizar para grafico
    df_melt = df_graf[['serie', 'matriculados', 'aulas']].melt(
        id_vars='serie', var_name='Metrica', value_name='Valor'
    )
    df_melt['Metrica'] = df_melt['Metrica'].map({
        'matriculados': 'Matriculados',
        'aulas': 'Aulas Registradas',
    })

    fig = px.bar(
        df_melt, x='serie', y='Valor', color='Metrica', barmode='group',
        title='Matriculados vs Aulas Registradas por Serie',
        labels={'serie': 'Serie', 'Valor': 'Quantidade'},
        color_discrete_map={'Matriculados': '#60a5fa', 'Aulas Registradas': '#4ade80'},
    )
    fig.update_layout(height=450, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# ABA 3 - EVASAO x DESEMPENHO
# ============================================================

def _render_evasao(df_ocorrencias):
    st.header("Evasao x Desempenho")

    df_2025 = carregar_matriculas_2025()
    df_2026 = carregar_matriculas_2026_evasao()

    if df_2025.empty or df_2026.empty:
        st.warning(
            "Dados de matriculas 2025 e/ou 2026 nao disponiveis para calculo de evasao.\n\n"
            "Certifique-se de que os arquivos `vagas.db` e `vagas_2025.db` estao em:\n\n"
            f"`{VAGAS_DB_PATH.parent}`"
        )
        # Mesmo sem evasao, mostrar ocorrencias se disponiveis
        if not df_ocorrencias.empty:
            _render_ocorrencias_resumo(df_ocorrencias)
        return

    # Calcular evasao
    df_2025_c = df_2025.copy()
    df_2026_c = df_2026.copy()

    df_2025_c['serie'] = df_2025_c['turma'].apply(_extrair_serie_da_turma)
    df_2026_c['serie'] = df_2026_c['turma'].apply(_extrair_serie_da_turma)

    df_2025_c = df_2025_c[df_2025_c['serie'].notna()]
    df_2026_c = df_2026_c[df_2026_c['serie'].notna()]

    # Agregar por unidade e serie
    ag_2025 = df_2025_c.groupby(['unidade_cod_ped', 'serie']).agg(
        total_2025=('total_2025', 'sum'),
    ).reset_index()

    ag_2026 = df_2026_c.groupby(['unidade_cod_ped', 'serie']).agg(
        total_2026=('total_2026', 'sum'),
        veteranos_2026=('veteranos_2026', 'sum'),
    ).reset_index()

    resultados = []
    for _, row25 in ag_2025.iterrows():
        un = row25['unidade_cod_ped']
        serie_2025 = row25['serie']
        serie_esperada = _PROGRESSAO_SERIE.get(serie_2025)

        if not serie_esperada or serie_esperada == 'Formado':
            continue

        alunos_2025 = row25['total_2025']

        filtro = (ag_2026['unidade_cod_ped'] == un) & (ag_2026['serie'] == serie_esperada)
        dados_26 = ag_2026[filtro]

        if len(dados_26) > 0:
            veteranos_2026 = int(dados_26['veteranos_2026'].values[0])
        else:
            veteranos_2026 = 0

        evasao = max(0, int(alunos_2025) - veteranos_2026)
        pct_evasao = (evasao / alunos_2025 * 100) if alunos_2025 > 0 else 0

        resultados.append({
            'unidade': un,
            'unidade_nome': NOMES_UNIDADES_CANONICAL.get(un, un),
            'serie_2025': serie_2025,
            'serie_2026': serie_esperada,
            'alunos_2025': int(alunos_2025),
            'veteranos_2026': veteranos_2026,
            'evasao': evasao,
            'pct_evasao': round(pct_evasao, 1),
        })

    df_evasao = pd.DataFrame(resultados)

    if df_evasao.empty:
        st.info("Sem dados de evasao para exibir.")
    else:
        # Resumo por unidade
        st.subheader("Taxa de Evasao por Unidade (2025 para 2026)")
        ev_unidade = df_evasao.groupby(['unidade', 'unidade_nome']).agg(
            alunos_2025=('alunos_2025', 'sum'),
            veteranos_2026=('veteranos_2026', 'sum'),
            evasao=('evasao', 'sum'),
        ).reset_index()
        ev_unidade['pct_evasao'] = (ev_unidade['evasao'] / ev_unidade['alunos_2025'] * 100).round(1)
        ev_unidade['pct_retencao'] = (100 - ev_unidade['pct_evasao']).round(1)

        cols_ev = st.columns(4)
        for i, (_, row) in enumerate(ev_unidade.iterrows()):
            with cols_ev[i % 4]:
                cor_classe = 'metric-green' if row['pct_evasao'] < 15 else ('metric-yellow' if row['pct_evasao'] < 25 else 'metric-red')
                st.markdown(f"""
                <div class="metric-card {cor_classe}">
                    <h2 style="margin:0;">{row['pct_evasao']}%</h2>
                    <p style="margin:0;">Evasao {row['unidade_nome']}</p>
                    <small>{row['evasao']:,} de {row['alunos_2025']:,} alunos</small>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Grafico de evasao por serie (filtrar apenas series do pedagogico)
        series_ped = SERIES_FUND_II + SERIES_EM
        df_ev_ped = df_evasao[df_evasao['serie_2025'].isin(series_ped)]

        if not df_ev_ped.empty:
            st.subheader("Evasao por Serie (apenas Fund. II e EM)")
            ev_serie = df_ev_ped.groupby('serie_2025').agg(
                alunos_2025=('alunos_2025', 'sum'),
                evasao=('evasao', 'sum'),
            ).reset_index()
            ev_serie['pct_evasao'] = (ev_serie['evasao'] / ev_serie['alunos_2025'] * 100).round(1)
            ev_serie['ordem'] = ev_serie['serie_2025'].apply(
                lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99
            )
            ev_serie = ev_serie.sort_values('ordem')

            fig = px.bar(
                ev_serie, x='serie_2025', y='pct_evasao',
                title='Taxa de Evasao por Serie (%)',
                labels={'serie_2025': 'Serie (2025)', 'pct_evasao': 'Evasao (%)'},
                color='pct_evasao',
                color_continuous_scale=['#4ade80', '#fbbf24', '#f87171'],
                range_color=[0, 40],
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # Cruzar ocorrencias x evasao
    if not df_ocorrencias.empty and not df_evasao.empty:
        st.markdown("---")
        _render_correlacao_ocorrencias_evasao(df_ocorrencias, df_evasao)

    # Resumo de ocorrencias
    if not df_ocorrencias.empty:
        st.markdown("---")
        _render_ocorrencias_resumo(df_ocorrencias)


def _render_correlacao_ocorrencias_evasao(df_ocorrencias, df_evasao):
    """Mostra correlacao entre ocorrencias e evasao por unidade."""
    st.subheader("Correlacao: Ocorrencias x Evasao")

    # Ocorrencias por unidade
    ocorr_un = df_ocorrencias.groupby('unidade').size().reset_index(name='ocorrencias')
    ocorr_un.rename(columns={'unidade': 'unidade_cod'}, inplace=True)

    # Evasao por unidade
    ev_un = df_evasao.groupby('unidade').agg(
        alunos_2025=('alunos_2025', 'sum'),
        evasao=('evasao', 'sum'),
    ).reset_index()
    ev_un['pct_evasao'] = (ev_un['evasao'] / ev_un['alunos_2025'] * 100).round(1)
    ev_un.rename(columns={'unidade': 'unidade_cod'}, inplace=True)

    # Merge
    df_corr = ocorr_un.merge(ev_un, on='unidade_cod', how='inner')
    df_corr['unidade_nome'] = df_corr['unidade_cod'].map(NOMES_UNIDADES_CANONICAL)

    if len(df_corr) < 2:
        st.info("Dados insuficientes para correlacao.")
        return

    fig = px.scatter(
        df_corr, x='ocorrencias', y='pct_evasao', text='unidade_nome',
        title='Ocorrencias vs Taxa de Evasao por Unidade',
        labels={'ocorrencias': 'Total de Ocorrencias', 'pct_evasao': 'Taxa de Evasao (%)'},
        size='alunos_2025', size_max=50,
        color='unidade_cod',
        color_discrete_map=CORES_UNIDADES,
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="info-box">
        <strong>Nota:</strong> Este grafico mostra a relacao entre o volume de ocorrencias
        disciplinares e a taxa de evasao por unidade. O tamanho do ponto indica o
        numero de alunos em 2025. Correlacao nao implica causalidade.
    </div>
    """, unsafe_allow_html=True)


def _render_ocorrencias_resumo(df_ocorrencias):
    """Exibe resumo de ocorrencias por gravidade e unidade."""
    st.subheader("Resumo de Ocorrencias por Unidade")

    if 'gravidade' in df_ocorrencias.columns and 'unidade' in df_ocorrencias.columns:
        pivot = df_ocorrencias.groupby(['unidade', 'gravidade']).size().reset_index(name='total')
        pivot_table = pivot.pivot_table(
            index='unidade', columns='gravidade', values='total', fill_value=0, aggfunc='sum'
        ).reset_index()
        pivot_table.rename(columns={'unidade': 'Unidade'}, inplace=True)

        # Adicionar total
        grav_cols = [c for c in pivot_table.columns if c != 'Unidade']
        pivot_table['Total'] = pivot_table[grav_cols].sum(axis=1)
        pivot_table = pivot_table.sort_values('Total', ascending=False)

        st.dataframe(pivot_table, use_container_width=True, hide_index=True)
    else:
        # Fallback simples
        ocorr_un = df_ocorrencias.groupby('unidade').size().reset_index(name='Total')
        ocorr_un.rename(columns={'unidade': 'Unidade'}, inplace=True)
        st.dataframe(ocorr_un, use_container_width=True, hide_index=True)


# ============================================================
# ABA 4 - METAS 2026
# ============================================================

def _render_metas(df_matriculas):
    st.header("Metas de Matricula 2026")

    if df_matriculas.empty:
        st.warning("Dados de matriculas nao disponiveis.")
        return

    # Totais por unidade
    totais = df_matriculas.groupby('unidade_cod_ped')['matriculados'].sum().to_dict()

    # Gauges por unidade
    st.subheader("Progresso vs Meta por Unidade")

    fig = go.Figure()
    unidades_info = []
    for cod in ['BV', 'CD', 'JG', 'CDR']:
        un = UNIDADES_CANONICAL[cod]
        atual = int(totais.get(cod, 0))
        meta = un.meta_2026
        pct = (atual / meta * 100) if meta > 0 else 0
        faltam = max(0, meta - atual)
        unidades_info.append({
            'codigo': cod,
            'nome': un.nome,
            'atual': atual,
            'meta': meta,
            'pct': pct,
            'faltam': faltam,
        })

    cols = st.columns(4)
    for i, info in enumerate(unidades_info):
        with cols[i]:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=info['atual'],
                delta={'reference': info['meta'], 'relative': False, 'valueformat': ',d'},
                title={'text': f"{info['nome']} ({info['codigo']})"},
                number={'valueformat': ',d'},
                gauge={
                    'axis': {'range': [0, int(info['meta'] * 1.15)]},
                    'bar': {'color': _cor_progresso(info['pct'])},
                    'steps': [
                        {'range': [0, int(info['meta'] * 0.6)], 'color': '#ffebee'},
                        {'range': [int(info['meta'] * 0.6), int(info['meta'] * 0.8)], 'color': '#fff3e0'},
                        {'range': [int(info['meta'] * 0.8), info['meta']], 'color': '#e8f5e9'},
                        {'range': [info['meta'], int(info['meta'] * 1.15)], 'color': '#c8e6c9'},
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 3},
                        'thickness': 0.75,
                        'value': info['meta'],
                    },
                },
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

    # Gauge total
    st.markdown("---")
    st.subheader("Meta Total da Rede")

    total_atual = sum(info['atual'] for info in unidades_info)
    pct_total = (total_atual / META_TOTAL_2026 * 100) if META_TOTAL_2026 > 0 else 0

    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        fig_total = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=total_atual,
            delta={'reference': META_TOTAL_2026, 'relative': False, 'valueformat': ',d'},
            title={'text': "Total da Rede ELO"},
            number={'valueformat': ',d'},
            gauge={
                'axis': {'range': [0, int(META_TOTAL_2026 * 1.15)]},
                'bar': {'color': _cor_progresso(pct_total)},
                'steps': [
                    {'range': [0, int(META_TOTAL_2026 * 0.6)], 'color': '#ffebee'},
                    {'range': [int(META_TOTAL_2026 * 0.6), int(META_TOTAL_2026 * 0.8)], 'color': '#fff3e0'},
                    {'range': [int(META_TOTAL_2026 * 0.8), META_TOTAL_2026], 'color': '#e8f5e9'},
                    {'range': [META_TOTAL_2026, int(META_TOTAL_2026 * 1.15)], 'color': '#c8e6c9'},
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': META_TOTAL_2026,
                },
            },
        ))
        fig_total.update_layout(height=350)
        st.plotly_chart(fig_total, use_container_width=True)

    with col_t2:
        faltam_total = max(0, META_TOTAL_2026 - total_atual)
        st.markdown(f"""
        <div class="metric-card {'metric-green' if pct_total >= 90 else 'metric-yellow' if pct_total >= 70 else 'metric-red'}">
            <h1 style="margin:0; font-size: 2.5em;">{pct_total:.1f}%</h1>
            <p style="margin:0;">Atingimento</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if faltam_total > 0:
            st.markdown(f"""
            <div class="metric-card metric-yellow">
                <h1 style="margin:0; font-size: 2.5em;">{faltam_total:,}</h1>
                <p style="margin:0;">Faltam para Meta</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            excedente = total_atual - META_TOTAL_2026
            st.markdown(f"""
            <div class="metric-card metric-green">
                <h1 style="margin:0; font-size: 2.5em;">+{excedente:,}</h1>
                <p style="margin:0;">Acima da Meta!</p>
            </div>
            """, unsafe_allow_html=True)

    # Projecao de atingimento
    st.markdown("---")
    st.subheader("Projecao de Atingimento")

    # Calcular tendencia baseada na variacao 2025 -> 2026
    df_2025 = carregar_matriculas_2025()

    if not df_2025.empty:
        total_2025 = int(df_2025['total_2025'].sum())
        crescimento = total_atual - total_2025
        pct_crescimento = (crescimento / total_2025 * 100) if total_2025 > 0 else 0

        # Semana atual e projecao
        semana = calcular_semana_letiva()
        semanas_restantes = max(0, 42 - semana)

        # Taxa de crescimento semanal media
        if semana > 1:
            cresc_semanal = crescimento / semana
            projecao_final = total_atual + (cresc_semanal * semanas_restantes)
        else:
            cresc_semanal = 0
            projecao_final = total_atual

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.metric(
                "Matriculas 2025", f"{total_2025:,}",
                delta=f"{crescimento:+,} ({pct_crescimento:+.1f}%)",
                delta_color="normal" if crescimento >= 0 else "inverse"
            )
        with col_p2:
            st.metric("Crescimento Semanal Medio", f"{cresc_semanal:+.0f} alunos/semana")
        with col_p3:
            projecao_pct = (projecao_final / META_TOTAL_2026 * 100) if META_TOTAL_2026 > 0 else 0
            st.metric(
                "Projecao Final (sem. 42)",
                f"{projecao_final:,.0f}",
                delta=f"{projecao_pct:.1f}% da meta",
                delta_color="normal" if projecao_final >= META_TOTAL_2026 else "inverse"
            )

        # Grafico de projecao
        semanas = list(range(1, 43))
        valores_proj = [total_2025 + cresc_semanal * s for s in semanas]

        fig_proj = go.Figure()
        # Linha de projecao
        fig_proj.add_trace(go.Scatter(
            x=semanas, y=valores_proj,
            mode='lines', name='Projecao',
            line=dict(color='#60a5fa', dash='dash', width=2),
        ))
        # Ponto atual
        fig_proj.add_trace(go.Scatter(
            x=[semana], y=[total_atual],
            mode='markers+text', name='Atual',
            marker=dict(size=14, color='#4ade80'),
            text=[f'{total_atual:,}'], textposition='top center',
        ))
        # Linha de meta
        fig_proj.add_hline(
            y=META_TOTAL_2026, line_dash='dot', line_color='red',
            annotation_text=f'Meta: {META_TOTAL_2026:,}',
        )
        fig_proj.update_layout(
            title='Projecao de Matriculas ao Longo do Ano',
            xaxis_title='Semana Letiva',
            yaxis_title='Total de Matriculas',
            height=400,
            showlegend=True,
        )
        st.plotly_chart(fig_proj, use_container_width=True)

        # Tabela por unidade
        st.subheader("Detalhamento por Unidade")
        det_rows = []
        for info in unidades_info:
            cod = info['codigo']
            # Total 2025 para esta unidade
            dados_25_un = df_2025[df_2025['unidade_cod_ped'] == cod]
            t_2025 = int(dados_25_un['total_2025'].sum()) if not dados_25_un.empty else 0
            diff = info['atual'] - t_2025
            diff_pct = (diff / t_2025 * 100) if t_2025 > 0 else 0

            det_rows.append({
                'Unidade': f"{info['nome']} ({info['codigo']})",
                'Matr. 2025': t_2025,
                'Matr. 2026': info['atual'],
                'Variacao': f"{diff:+,} ({diff_pct:+.1f}%)",
                'Meta 2026': info['meta'],
                '% Meta': f"{info['pct']:.1f}%",
                'Faltam': info['faltam'],
            })

        st.dataframe(pd.DataFrame(det_rows), use_container_width=True, hide_index=True)
    else:
        st.info(
            "Dados de 2025 nao disponiveis para calculo de projecao. "
            "Exibindo apenas o progresso atual."
        )

        # Tabela simples
        det_rows = []
        for info in unidades_info:
            det_rows.append({
                'Unidade': f"{info['nome']} ({info['codigo']})",
                'Matr. 2026': info['atual'],
                'Meta 2026': info['meta'],
                '% Meta': f"{info['pct']:.1f}%",
                'Faltam': info['faltam'],
            })
        st.dataframe(pd.DataFrame(det_rows), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
