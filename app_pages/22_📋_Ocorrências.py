#!/usr/bin/env python3
"""
PAGINA 22: OCORRENCIAS
Dashboard completo de ocorrencias por categoria (Disciplinar, Pedagogico, Administrativo).
CEO ve todas as unidades; Coordenador ve a sua unidade.
Filtros por categoria, gravidade, tipo, serie, periodo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import date, timedelta
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_UNIDADES, CORES_SERIES, ORDEM_SERIES
from utils import (
    calcular_semana_letiva, calcular_trimestre,
    carregar_ocorrencias, carregar_alunos, salvar_ocorrencia,
    _hoje,
    UNIDADES, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM,
)
from components import cabecalho_pagina, metricas_em_colunas
from auth import get_user_unit, get_user_role, ROLE_CEO

# ========== CSS ==========
st.markdown("""
<style>
    .ocorr-grave {
        background: #FFEBEE; border-left: 5px solid #D32F2F;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .ocorr-media {
        background: #FFF3E0; border-left: 5px solid #F57C00;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .ocorr-leve {
        background: #FFF8E1; border-left: 5px solid #FBC02D;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .ocorr-positiva {
        background: #E8F5E9; border-left: 5px solid #43A047;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .ocorr-stat {
        background: white; border: 1px solid #e0e0e0; border-radius: 10px;
        padding: 16px; text-align: center;
    }
    .ocorr-stat-valor { font-size: 1.8em; font-weight: bold; }
    .ocorr-stat-label { font-size: 0.82em; color: #666; margin-top: 4px; }
    .ocorr-insight {
        background: #E8EAF6; border-left: 4px solid #3F51B5;
        padding: 12px 16px; margin: 8px 0; border-radius: 4px;
    }
    .cat-badge {
        display: inline-block; padding: 3px 10px; border-radius: 12px;
        font-size: 0.8em; font-weight: 600; margin-right: 6px;
    }
    .cat-disciplinar { background: #FFCDD2; color: #C62828; }
    .cat-pedagogico { background: #C8E6C9; color: #2E7D32; }
    .cat-administrativo { background: #E0E0E0; color: #616161; }
</style>
""", unsafe_allow_html=True)

GRAVIDADES = ['Leve', 'Media', 'Grave']

TIPOS_OCORRENCIA = [
    'Indisciplina', 'Atraso', 'Falta de Material',
    'Agressão Verbal', 'Agressão Física', 'Uso de Celular',
    'Evasão de Aula', 'Danificação de Patrimônio', 'Bullying',
    'Desobediência', 'Registro Positivo', 'Outro',
]

PROVIDENCIAS_SUGERIDAS = {
    'Leve': ['Advertência verbal', 'Conversa com o aluno', 'Registro no diário'],
    'Media': ['Advertência escrita', 'Contato com responsável', 'Encaminhamento à coordenação'],
    'Grave': ['Suspensão', 'Reunião com responsável', 'Encaminhamento à direção', 'Ata de ocorrência'],
}


def main():
    cabecalho_pagina("Ocorrencias", "Registro e Monitoramento")

    hoje = _hoje()
    semana = calcular_semana_letiva(hoje)
    trimestre = calcular_trimestre(semana)
    role = get_user_role()
    user_unit = get_user_unit()
    is_ceo = (role == ROLE_CEO)

    df_alunos = carregar_alunos()
    df_ocorr = carregar_ocorrencias()
    tem_dados = not df_ocorr.empty

    if not tem_dados:
        tab_reg, tab_info = st.tabs(["Novo Registro", "Sobre"])
        with tab_reg:
            _tab_novo_registro(df_alunos, not df_alunos.empty)
        with tab_info:
            _mostrar_info_sistema()
        return

    # ========== FILTROS NO CORPO PRINCIPAL ==========
    st.markdown("### Filtros")
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        if is_ceo:
            unidade_opcoes = ['Todas'] + UNIDADES
            unidade_sel = st.selectbox(
                "Unidade:",
                unidade_opcoes,
                format_func=lambda x: UNIDADES_NOMES.get(x, x) if x != 'Todas' else 'Rede ELO (todas)',
                key='ocorr_un',
            )
        else:
            # Coordenador/Diretor: ve sua unidade por padrao, pode ver outras
            default_idx = UNIDADES.index(user_unit) + 1 if user_unit in UNIDADES else 0
            unidade_opcoes = ['Todas'] + UNIDADES
            unidade_sel = st.selectbox(
                "Unidade:",
                unidade_opcoes,
                index=default_idx,
                format_func=lambda x: UNIDADES_NOMES.get(x, x) if x != 'Todas' else 'Todas',
                key='ocorr_un',
            )

    with f2:
        categorias_disp = sorted(df_ocorr['categoria'].dropna().unique().tolist()) if 'categoria' in df_ocorr.columns else []
        # Default: Disciplinar + Pedagogico (excluir Administrativo que e 91% do ruido)
        default_cats = [c for c in categorias_disp if c != 'Administrativo']
        if not default_cats:
            default_cats = categorias_disp
        categoria_sel = st.multiselect("Categoria:", categorias_disp, default=default_cats, key='ocorr_cat')

    with f3:
        grav_sel = st.selectbox("Gravidade:", ['Todas'] + GRAVIDADES, key='ocorr_grav')

    with f4:
        periodo_opcoes = ['Ultimos 30 dias', 'Ultimos 7 dias', 'Este mes', 'Este trimestre', 'Ano 2026', 'Tudo']
        periodo_sel = st.selectbox("Periodo:", periodo_opcoes, key='ocorr_periodo')

    # Linha 2 de filtros
    f5, f6 = st.columns(2)
    with f5:
        series_disp = sorted(
            df_ocorr['serie'].dropna().unique().tolist(),
            key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99,
        ) if 'serie' in df_ocorr.columns else []
        serie_sel = st.selectbox("Serie:", ['Todas'] + series_disp, key='ocorr_serie')

    with f6:
        tipos_disp = sorted(df_ocorr['tipo'].dropna().unique().tolist()) if 'tipo' in df_ocorr.columns else []
        tipo_sel = st.selectbox("Tipo:", ['Todos'] + tipos_disp, key='ocorr_tipo')

    # ========== APLICAR FILTROS ==========
    df = df_ocorr.copy()

    # Unidade
    if unidade_sel != 'Todas' and 'unidade' in df.columns:
        df = df[df['unidade'] == unidade_sel]

    # Categoria
    if categoria_sel and 'categoria' in df.columns:
        df = df[df['categoria'].isin(categoria_sel)]

    # Gravidade
    if grav_sel != 'Todas' and 'gravidade' in df.columns:
        df = df[df['gravidade'] == grav_sel]

    # Periodo
    if 'data' in df.columns:
        hoje_dt = hoje.date() if hasattr(hoje, 'date') else hoje
        if periodo_sel == 'Ultimos 7 dias':
            df = df[df['data'].dt.date >= (hoje_dt - timedelta(days=7))]
        elif periodo_sel == 'Ultimos 30 dias':
            df = df[df['data'].dt.date >= (hoje_dt - timedelta(days=30))]
        elif periodo_sel == 'Este mes':
            df = df[df['data'].dt.date >= hoje_dt.replace(day=1)]
        elif periodo_sel == 'Este trimestre':
            tri_inicio = {1: 1, 2: 5, 3: 9}
            mes_ini = tri_inicio.get(trimestre, 1)
            df = df[df['data'].dt.date >= hoje_dt.replace(month=mes_ini, day=1)]
        elif periodo_sel == 'Ano 2026':
            df = df[df['data'].dt.year == 2026]
        # 'Tudo' = sem filtro

    # Serie
    if serie_sel != 'Todas' and 'serie' in df.columns:
        df = df[df['serie'] == serie_sel]

    # Tipo
    if tipo_sel != 'Todos' and 'tipo' in df.columns:
        df = df[df['tipo'] == tipo_sel]

    # ========== CONTEXTO ==========
    label_un = UNIDADES_NOMES.get(unidade_sel, 'Rede ELO') if unidade_sel != 'Todas' else 'Rede ELO'
    cats_label = ', '.join(categoria_sel) if categoria_sel else 'Todas'
    st.caption(f"**{len(df)}** ocorrencias | {label_un} | {cats_label} | {periodo_sel}")

    if df.empty:
        st.info("Nenhuma ocorrencia encontrada para os filtros selecionados.")
        st.markdown("---")
        _tab_novo_registro(df_alunos, not df_alunos.empty)
        return

    # ========== METRICAS ==========
    total = len(df)
    alunos_envolvidos = df['aluno_id'].nunique() if 'aluno_id' in df.columns else 0
    reincidentes = 0
    if 'aluno_id' in df.columns:
        contagem = df['aluno_id'].value_counts()
        reincidentes = int((contagem > 2).sum())
    graves = int(len(df[df['gravidade'] == 'Grave'])) if 'gravidade' in df.columns else 0
    medias = int(len(df[df['gravidade'] == 'Media'])) if 'gravidade' in df.columns else 0
    n_dias = max(1, df['data'].dt.date.nunique()) if 'data' in df.columns else 1
    media_dia = round(total / n_dias, 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, valor, cor in [
        (c1, 'Total', total, '#1a237e'),
        (c2, 'Alunos', alunos_envolvidos, '#1a237e'),
        (c3, 'Reincidentes (3+)', reincidentes, '#E65100'),
        (c4, 'Graves', graves, '#C62828'),
        (c5, 'Media/Dia', media_dia, '#1a237e'),
    ]:
        with col:
            st.markdown(f"""
            <div class="ocorr-stat">
                <div class="ocorr-stat-valor" style="color:{cor};">{valor}</div>
                <div class="ocorr-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ========== TABS ==========
    tab_risco, tab_geral, tab_turma, tab_comp, tab_detalhe, tab_registro = st.tabs([
        "Alunos em Risco", "Visao Geral", "Por Serie/Turma",
        "Comparativo Unidades", "Detalhamento", "Novo Registro",
    ])

    # ------ TAB: ALUNOS EM RISCO ------
    with tab_risco:
        _tab_alunos_risco(df)

    # ------ TAB: VISAO GERAL ------
    with tab_geral:
        _tab_visao_geral(df)

    # ------ TAB: POR SERIE/TURMA ------
    with tab_turma:
        _tab_por_turma(df)

    # ------ TAB: COMPARATIVO UNIDADES ------
    with tab_comp:
        _tab_comparativo(df_ocorr, categoria_sel, periodo_sel, hoje, trimestre)

    # ------ TAB: DETALHAMENTO ------
    with tab_detalhe:
        _tab_detalhamento(df)

    # ------ TAB: NOVO REGISTRO ------
    with tab_registro:
        _tab_novo_registro(df_alunos, not df_alunos.empty)


# ============================================================
# TABS
# ============================================================

def _tab_alunos_risco(df):
    """Alunos com ocorrencias que precisam de atencao — por gravidade e reincidencia."""
    st.subheader("Alunos que Precisam de Atencao")

    if 'aluno_nome' not in df.columns:
        st.info("Dados de aluno nao disponiveis.")
        return

    # Apenas Disciplinar conta para risco (Pedagogico = informativo, Administrativo = operacional)
    df_risco = df[df['categoria'] == 'Disciplinar'] if 'categoria' in df.columns else df

    if df_risco.empty:
        st.info("Nenhuma ocorrencia disciplinar para os filtros selecionados. "
                "Registros pedagogicos (atestados, atendimentos) sao informativos e nao contam para risco.")
        return

    # Ranking por aluno (so Disciplinar)
    agg_dict = {'total': ('tipo', 'count')}
    if 'gravidade' in df_risco.columns:
        agg_dict['graves'] = ('gravidade', lambda x: (x == 'Grave').sum())
        agg_dict['medias'] = ('gravidade', lambda x: (x == 'Media').sum())
    agg_dict['tipos'] = ('tipo', lambda x: ', '.join(sorted(x.unique())))
    if 'data' in df_risco.columns:
        agg_dict['ultima'] = ('data', 'max')

    ranking = df_risco.groupby('aluno_nome').agg(**agg_dict).reset_index()
    ranking = ranking.sort_values('total', ascending=False)

    # Adicionar serie/unidade/turma
    for col in ['serie', 'unidade', 'turma']:
        if col in df_risco.columns:
            info = df_risco.groupby('aluno_nome')[col].first()
            ranking = ranking.merge(info, on='aluno_nome', how='left')

    # Classificar risco considerando gravidade E quantidade
    # - CRITICO: 5+ ocorrencias OU 2+ graves
    # - ALERTA: 3-4 ocorrencias OU 1 grave OU 2+ medias
    # - ATENCAO: 2 ocorrencias OU 1 media
    has_grav = 'graves' in ranking.columns
    has_med = 'medias' in ranking.columns

    def _nivel_risco(row):
        total = row['total']
        graves = int(row.get('graves', 0)) if has_grav else 0
        medias = int(row.get('medias', 0)) if has_med else 0
        if total >= 5 or graves >= 2:
            return 'critico'
        if total >= 3 or graves >= 1 or medias >= 2:
            return 'alerta'
        if total >= 2 or medias >= 1:
            return 'atencao'
        return None

    ranking['nivel'] = ranking.apply(_nivel_risco, axis=1)
    ranking_risco = ranking[ranking['nivel'].notna()]

    criticos = ranking_risco[ranking_risco['nivel'] == 'critico']
    alerta = ranking_risco[ranking_risco['nivel'] == 'alerta']
    atencao = ranking_risco[ranking_risco['nivel'] == 'atencao']

    grupos = [
        (criticos, 'INTERVENCAO URGENTE', 'ocorr-grave'),
        (alerta, 'ALERTA', 'ocorr-media'),
        (atencao, 'ATENCAO', 'ocorr-leve'),
    ]

    total_risco = len(ranking_risco)

    if total_risco == 0:
        st.success("Nenhum aluno em risco para os filtros selecionados.")
        return

    # Insight
    if not criticos.empty:
        st.markdown(f"""
        <div class="ocorr-insight">
            <strong>{len(criticos)} aluno(s) precisam de intervencao urgente</strong> (5+ ocorrencias ou 2+ graves).
            Recomendacao: agendar conversa com responsaveis e equipe pedagogica.
        </div>
        """, unsafe_allow_html=True)

    for grupo, label, css in grupos:
        if grupo.empty:
            continue
        st.markdown(f"#### {label} ({len(grupo)} alunos)")

        for _, row in grupo.iterrows():
            serie_info = f" | {row['serie']}" if 'serie' in row.index and pd.notna(row.get('serie')) else ''
            turma_info = f" | {row['turma']}" if 'turma' in row.index and pd.notna(row.get('turma')) else ''
            un_info = f" | {UNIDADES_NOMES.get(row.get('unidade', ''), row.get('unidade', ''))}" if 'unidade' in row.index and pd.notna(row.get('unidade')) else ''
            graves_info = f" | {int(row['graves'])} grave(s)" if 'graves' in row.index and row.get('graves', 0) > 0 else ''
            medias_info = f" | {int(row['medias'])} media(s)" if 'medias' in row.index and row.get('medias', 0) > 0 else ''

            st.markdown(f"""
            <div class="{css}">
                <strong>{row['aluno_nome']}</strong>{serie_info}{turma_info}{un_info}
                <span style="float:right; font-weight:bold;">{int(row['total'])} ocorr.{graves_info}{medias_info}</span>
                <br><small>Tipos: {row['tipos']}</small>
            </div>
            """, unsafe_allow_html=True)

    # Tabela exportavel
    with st.expander("Tabela completa"):
        cols_show = [c for c in ['aluno_nome', 'total', 'graves', 'medias', 'serie', 'turma', 'unidade', 'tipos']
                     if c in ranking_risco.columns]
        st.dataframe(ranking_risco[cols_show], use_container_width=True, hide_index=True)


def _tab_visao_geral(df):
    """Panorama geral com graficos."""
    st.subheader("Panorama Geral")

    col_e, col_d = st.columns(2)

    with col_e:
        # Por tipo
        if 'tipo' in df.columns:
            tipo_counts = df['tipo'].value_counts().reset_index()
            tipo_counts.columns = ['Tipo', 'Qtd']
            fig = px.bar(
                tipo_counts.head(12), x='Qtd', y='Tipo', orientation='h',
                color='Qtd', color_continuous_scale=['#FBC02D', '#D32F2F'],
                title='Por Tipo de Ocorrencia',
            )
            fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col_d:
        # Por gravidade
        if 'gravidade' in df.columns:
            grav_counts = df['gravidade'].value_counts().reset_index()
            grav_counts.columns = ['Gravidade', 'Qtd']
            cores_grav = {'Grave': '#D32F2F', 'Media': '#F57C00', 'Leve': '#FBC02D'}
            fig2 = px.pie(
                grav_counts, values='Qtd', names='Gravidade',
                color='Gravidade', color_discrete_map=cores_grav,
                title='Por Gravidade', hole=0.4,
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

    # Timeline
    if 'data' in df.columns:
        timeline = df.groupby(df['data'].dt.date).size().reset_index()
        timeline.columns = ['Data', 'Ocorrencias']
        fig3 = px.area(
            timeline, x='Data', y='Ocorrencias',
            title='Evolucao Diaria',
            color_discrete_sequence=['#E53935'],
        )
        fig3.update_layout(height=300)
        st.plotly_chart(fig3, use_container_width=True)

    # Por dia da semana
    if 'data' in df.columns:
        col_ds, col_cat = st.columns(2)
        with col_ds:
            dias = {0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sab', 6: 'Dom'}
            df_dias = df.copy()
            df_dias['dia_semana'] = df_dias['data'].dt.dayofweek.map(dias)
            dia_counts = df_dias['dia_semana'].value_counts().reindex(
                ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'], fill_value=0
            ).reset_index()
            dia_counts.columns = ['Dia', 'Qtd']
            fig5 = px.bar(dia_counts, x='Dia', y='Qtd',
                         color_discrete_sequence=['#3F51B5'],
                         title='Por Dia da Semana')
            fig5.update_layout(height=300)
            st.plotly_chart(fig5, use_container_width=True)

        with col_cat:
            if 'categoria' in df.columns:
                cat_counts = df['categoria'].value_counts().reset_index()
                cat_counts.columns = ['Categoria', 'Qtd']
                fig6 = px.pie(
                    cat_counts, values='Qtd', names='Categoria',
                    title='Por Categoria', hole=0.4,
                    color='Categoria',
                    color_discrete_map={
                        'Disciplinar': '#E53935', 'Pedagogico': '#43A047', 'Administrativo': '#9E9E9E'
                    },
                )
                fig6.update_layout(height=300)
                st.plotly_chart(fig6, use_container_width=True)


def _tab_por_turma(df):
    """Analise por serie e turma."""
    st.subheader("Ocorrencias por Serie e Turma")

    if 'serie' not in df.columns:
        st.info("Dados de serie nao disponiveis.")
        return

    # Por serie
    serie_counts = df['serie'].value_counts().reset_index()
    serie_counts.columns = ['Serie', 'Qtd']
    serie_counts['ordem'] = serie_counts['Serie'].apply(
        lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99
    )
    serie_counts = serie_counts.sort_values('ordem')

    fig = px.bar(
        serie_counts, x='Serie', y='Qtd',
        color='Serie', color_discrete_map=CORES_SERIES,
        title='Ocorrencias por Serie',
        text='Qtd',
    )
    fig.update_layout(height=400, showlegend=False)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap serie x tipo
    if 'tipo' in df.columns:
        col_agg = 'aluno_id' if 'aluno_id' in df.columns else 'data'
        pivot = df.pivot_table(
            index='serie', columns='tipo', values=col_agg, aggfunc='count', fill_value=0
        )
        if not pivot.empty:
            # Reordenar
            series_order = [s for s in ORDEM_SERIES if s in pivot.index]
            outros = [s for s in pivot.index if s not in ORDEM_SERIES]
            pivot = pivot.reindex(series_order + outros)

            fig2 = px.imshow(
                pivot, text_auto=True,
                color_continuous_scale=['#FFFFFF', '#FBC02D', '#D32F2F'],
                title='Heatmap: Serie x Tipo',
                aspect='auto',
            )
            fig2.update_layout(height=max(300, len(pivot) * 40 + 100))
            st.plotly_chart(fig2, use_container_width=True)

    # Ranking por turma
    if 'turma' in df.columns and df['turma'].notna().any():
        st.subheader("Ranking por Turma")
        turma_stats = df.groupby('turma').agg(
            total=('tipo', 'count'),
        ).reset_index().sort_values('total', ascending=False)

        if 'gravidade' in df.columns:
            grav_turma = df.groupby('turma')['gravidade'].apply(
                lambda x: (x == 'Grave').sum()
            ).reset_index(name='graves')
            turma_stats = turma_stats.merge(grav_turma, on='turma', how='left')

        st.dataframe(turma_stats.head(20), use_container_width=True, hide_index=True)


def _tab_comparativo(df_ocorr_full, categoria_sel, periodo_sel, hoje, trimestre):
    """Comparativo entre unidades (visao CEO)."""
    st.subheader("Comparativo entre Unidades")

    # Aplicar mesmos filtros de categoria e periodo no df completo
    df = df_ocorr_full.copy()
    if categoria_sel and 'categoria' in df.columns:
        df = df[df['categoria'].isin(categoria_sel)]
    if 'data' in df.columns:
        hoje_dt = hoje.date() if hasattr(hoje, 'date') else hoje
        if periodo_sel == 'Ultimos 7 dias':
            df = df[df['data'].dt.date >= (hoje_dt - timedelta(days=7))]
        elif periodo_sel == 'Ultimos 30 dias':
            df = df[df['data'].dt.date >= (hoje_dt - timedelta(days=30))]
        elif periodo_sel == 'Este mes':
            df = df[df['data'].dt.date >= hoje_dt.replace(day=1)]
        elif periodo_sel == 'Este trimestre':
            tri_inicio = {1: 1, 2: 5, 3: 9}
            mes_ini = tri_inicio.get(trimestre, 1)
            df = df[df['data'].dt.date >= hoje_dt.replace(month=mes_ini, day=1)]
        elif periodo_sel == 'Ano 2026':
            df = df[df['data'].dt.year == 2026]

    if 'unidade' not in df.columns or df.empty:
        st.info("Dados insuficientes para comparativo.")
        return

    # Comparativo por unidade
    comp = df.groupby('unidade').agg(
        total=('tipo', 'count'),
        alunos=('aluno_id', 'nunique') if 'aluno_id' in df.columns else ('aluno_nome', 'nunique'),
    ).reset_index()

    if 'gravidade' in df.columns:
        grav_un = df.groupby('unidade')['gravidade'].apply(lambda x: (x == 'Grave').sum()).reset_index(name='graves')
        comp = comp.merge(grav_un, on='unidade', how='left')

    comp['unidade_nome'] = comp['unidade'].map(UNIDADES_NOMES)
    comp = comp.sort_values('total', ascending=False)

    # Grafico comparativo
    fig = px.bar(
        comp, x='unidade_nome', y='total',
        color='unidade', color_discrete_map=CORES_UNIDADES,
        title='Total de Ocorrencias por Unidade',
        text='total',
    )
    fig.update_layout(height=350, showlegend=False)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    # Tabela comparativa
    cols_comp = [c for c in ['unidade_nome', 'total', 'alunos', 'graves'] if c in comp.columns]
    rename = {'unidade_nome': 'Unidade', 'total': 'Total', 'alunos': 'Alunos Envolvidos', 'graves': 'Graves'}
    st.dataframe(
        comp[cols_comp].rename(columns=rename),
        use_container_width=True, hide_index=True,
    )

    # Por tipo em cada unidade
    if 'tipo' in df.columns:
        col_agg = 'aluno_id' if 'aluno_id' in df.columns else 'data'
        pivot = df.pivot_table(
            index='unidade', columns='tipo', values=col_agg, aggfunc='count', fill_value=0
        )
        if not pivot.empty:
            pivot.index = pivot.index.map(lambda x: UNIDADES_NOMES.get(x, x))
            # Selecionar top 8 tipos para nao poluir
            top_tipos = df['tipo'].value_counts().head(8).index.tolist()
            pivot_top = pivot[[c for c in top_tipos if c in pivot.columns]]
            if not pivot_top.empty:
                fig2 = px.imshow(
                    pivot_top, text_auto=True,
                    color_continuous_scale=['#FFFFFF', '#FBC02D', '#D32F2F'],
                    title='Heatmap: Unidade x Tipo (Top 8)',
                    aspect='auto',
                )
                fig2.update_layout(height=300)
                st.plotly_chart(fig2, use_container_width=True)


def _tab_detalhamento(df):
    """Lista completa com busca e exportacao."""
    st.subheader("Registro Completo")

    busca = st.text_input("Buscar:", placeholder="Nome, tipo, descricao...", key='ocorr_busca')

    df_show = df.copy()
    if busca:
        mask = pd.Series(False, index=df_show.index)
        for col in ['aluno_nome', 'tipo', 'descricao', 'responsavel', 'providencia', 'categoria']:
            if col in df_show.columns:
                mask = mask | df_show[col].astype(str).str.contains(busca, case=False, na=False)
        df_show = df_show[mask]

    cols_show = [c for c in ['data', 'aluno_nome', 'serie', 'turma', 'unidade', 'tipo',
                              'categoria', 'gravidade', 'descricao', 'providencia', 'responsavel']
                 if c in df_show.columns]

    if 'data' in df_show.columns:
        df_show = df_show.sort_values('data', ascending=False)

    if df_show.empty:
        st.info("Nenhum resultado para a busca.")
        return

    # Colorir gravidade
    if 'gravidade' in cols_show:
        def _color_grav(val):
            colors = {'Grave': 'background-color: #FFCDD2', 'Media': 'background-color: #FFE0B2', 'Leve': 'background-color: #FFF9C4'}
            return colors.get(val, '')
        styled = df_show[cols_show].style.map(_color_grav, subset=['gravidade'])
        st.dataframe(styled, use_container_width=True, hide_index=True, height=500)
    else:
        st.dataframe(df_show[cols_show] if cols_show else df_show, use_container_width=True, hide_index=True, height=500)

    st.caption(f"Total: {len(df_show)} ocorrencias")

    # Exportar
    csv_data = df_show[cols_show].to_csv(index=False) if cols_show else df_show.to_csv(index=False)
    st.download_button(
        "Exportar CSV", csv_data,
        file_name=f"ocorrencias_{_hoje().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )


def _tab_novo_registro(df_alunos, tem_alunos):
    """Formulario de registro de nova ocorrencia."""
    st.subheader("Registrar Nova Ocorrencia")

    if not tem_alunos:
        st.warning("Dados de alunos nao disponiveis. Registre manualmente.")

    with st.form("form_ocorrencia", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            data_ocorr = st.date_input("Data:", value=_hoje().date() if hasattr(_hoje(), 'date') else _hoje(), key='form_data')

            if tem_alunos:
                unidades_disp = sorted(df_alunos['unidade'].unique()) if 'unidade' in df_alunos.columns else []
                unidade_form = st.selectbox("Unidade:", unidades_disp,
                    format_func=lambda x: UNIDADES_NOMES.get(x, x), key='form_unidade')

                df_filtrado = df_alunos[df_alunos['unidade'] == unidade_form] if 'unidade' in df_alunos.columns else df_alunos
                series_disp = sorted(df_filtrado['serie'].unique()) if 'serie' in df_filtrado.columns else []
                serie_form = st.selectbox("Serie:", series_disp, key='form_serie')

                df_filtrado = df_filtrado[df_filtrado['serie'] == serie_form] if 'serie' in df_filtrado.columns else df_filtrado
                alunos_disp = df_filtrado[['aluno_id', 'aluno_nome', 'turma']].drop_duplicates().sort_values('aluno_nome')
                if not alunos_disp.empty:
                    aluno_options = {f"{r['aluno_nome']} ({r['turma']})": r for _, r in alunos_disp.iterrows()}
                    aluno_sel = st.selectbox("Aluno:", list(aluno_options.keys()), key='form_aluno')
                    aluno_info = aluno_options.get(aluno_sel, {})
                else:
                    st.warning("Nenhum aluno encontrado.")
                    aluno_info = {}
                    aluno_sel = None
            else:
                unidade_form = st.selectbox("Unidade:", UNIDADES,
                    format_func=lambda x: UNIDADES_NOMES.get(x, x), key='form_unidade')
                serie_form = st.text_input("Serie:", key='form_serie')
                aluno_nome_manual = st.text_input("Nome do Aluno:", key='form_aluno_nome')
                aluno_info = {}
                aluno_sel = aluno_nome_manual

        with col2:
            tipo_ocorr = st.selectbox("Tipo:", TIPOS_OCORRENCIA, key='form_tipo')
            gravidade = st.selectbox("Gravidade:", GRAVIDADES, key='form_gravidade')
            sugestoes = PROVIDENCIAS_SUGERIDAS.get(gravidade, [])
            providencia = st.selectbox("Providencia:", [''] + sugestoes + ['Outra...'], key='form_prov')
            if providencia == 'Outra...':
                providencia = st.text_input("Especifique:", key='form_prov_custom')
            responsavel = st.text_input("Responsavel:",
                value=st.session_state.get("user_display", ""), key='form_responsavel')

        descricao = st.text_area("Descricao:", height=100, key='form_descricao',
                                 placeholder="O que aconteceu, quando, onde...")

        submitted = st.form_submit_button("Registrar", type="primary", use_container_width=True)

        if submitted:
            if not descricao.strip():
                st.error("A descricao e obrigatoria.")
            elif not aluno_sel:
                st.error("Selecione ou informe o aluno.")
            else:
                registro = {
                    'data': pd.Timestamp(data_ocorr).strftime('%Y-%m-%d'),
                    'unidade': unidade_form,
                    'serie': serie_form if not tem_alunos else aluno_info.get('serie', serie_form),
                    'turma': aluno_info.get('turma', '') if tem_alunos else '',
                    'aluno_id': int(float(aluno_info.get('aluno_id', 0))) if tem_alunos and aluno_info else 0,
                    'aluno_nome': aluno_info.get('aluno_nome', aluno_sel) if tem_alunos and aluno_info else aluno_sel,
                    'tipo': tipo_ocorr,
                    'categoria': 'Disciplinar',
                    'gravidade': gravidade,
                    'descricao': descricao.strip().replace('\n', ' | '),
                    'responsavel': responsavel.strip(),
                    'providencia': providencia if providencia else '',
                    'registrado_por': st.session_state.get("username", "sistema"),
                }
                if salvar_ocorrencia(registro):
                    st.success(f"Ocorrencia registrada: {registro['aluno_nome']} - {tipo_ocorr}")
                    st.balloons()
                else:
                    st.error("Erro ao salvar.")


def _mostrar_info_sistema():
    """Info sobre o sistema."""
    st.markdown("""
    ## Sistema de Ocorrencias

    Permite registrar e acompanhar ocorrencias de alunos.

    ### Categorias
    | Categoria | Exemplos |
    |-----------|----------|
    | **Disciplinar** | Indisciplina, agressao, bullying, evasao |
    | **Pedagogico** | Atendimento pedagogico, falta justificada |
    | **Administrativo** | Cobranca, matricula, documentacao |

    ### Gravidades
    | Gravidade | Acao Sugerida |
    |-----------|--------------|
    | **Leve** | Advertencia verbal, conversa |
    | **Media** | Advertencia escrita, contato com responsavel |
    | **Grave** | Suspensao, reuniao, encaminhamento |

    ### Integracao
    Os dados alimentam a **dimensao B (Behavior)** do Alerta Precoce ABC.
    """)


main()
