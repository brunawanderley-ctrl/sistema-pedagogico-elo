#!/usr/bin/env python3
"""
PAGINA 22: OCORRENCIAS DISCIPLINARES
Dashboard de ocorrencias/incidentes de alunos.
Monitoramento de comportamento, tipos de ocorrencia, turmas criticas.
Inclui sistema de registro manual com armazenamento em CSV.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import date, datetime
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_UNIDADES, CORES_SERIES, ORDEM_SERIES
from utils import (
    calcular_semana_letiva, calcular_trimestre,
    carregar_ocorrencias, carregar_alunos, salvar_ocorrencia,
    filtrar_ate_hoje, filtrar_por_periodo, _hoje,
    PERIODOS_OPCOES, UNIDADES, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM,
)

st.set_page_config(page_title="Ocorrências", page_icon="📋", layout="wide")
from auth import check_password, logout_button, get_user_unit, get_user_role
if not check_password():
    st.stop()
logout_button()

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
</style>
""", unsafe_allow_html=True)

# Tipos e gravidades padrao
TIPOS_OCORRENCIA = [
    'Indisciplina',
    'Atraso',
    'Falta de Material',
    'Agressão Verbal',
    'Agressão Física',
    'Uso de Celular',
    'Evasão de Aula',
    'Danificação de Patrimônio',
    'Bullying',
    'Desobediência',
    'Registro Positivo',
    'Outro',
]

GRAVIDADES = ['Leve', 'Media', 'Grave']

PROVIDENCIAS_SUGERIDAS = {
    'Leve': ['Advertência verbal', 'Conversa com o aluno', 'Registro no diário'],
    'Media': ['Advertência escrita', 'Contato com responsável', 'Encaminhamento à coordenação'],
    'Grave': ['Suspensão', 'Reunião com responsável', 'Encaminhamento à direção', 'Ata de ocorrência'],
}


def main():
    st.title("📋 Ocorrências Disciplinares")
    st.markdown("**Registro e Monitoramento de Comportamento**")

    hoje = _hoje()
    semana = calcular_semana_letiva(hoje)
    trimestre = calcular_trimestre(semana)

    df_alunos = carregar_alunos()
    df_ocorr = carregar_ocorrencias()

    tem_dados = not df_ocorr.empty
    tem_alunos = not df_alunos.empty

    # ========== TABS PRINCIPAIS ==========
    if tem_dados:
        tab_registro, tab_risco, tab_geral, tab_turma, tab_aluno, tab_detalhe = st.tabs([
            "Novo Registro", "Alunos em Risco", "Visão Geral",
            "Por Turma", "Por Aluno", "Detalhamento"
        ])
    else:
        tab_registro, tab_info = st.tabs(["Novo Registro", "Sobre"])

    # ========== TAB: NOVO REGISTRO ==========
    with tab_registro:
        _tab_novo_registro(df_alunos, tem_alunos)

    if tem_dados:
        # Filtros globais na sidebar
        with st.sidebar:
            st.markdown("---")
            st.subheader("Filtros Ocorrências")

            # Filtro de periodo
            if 'data' in df_ocorr.columns:
                data_min = df_ocorr['data'].min()
                data_max = df_ocorr['data'].max()
                periodo_range = st.date_input(
                    "Período:", value=(data_min, data_max),
                    min_value=data_min, max_value=data_max,
                    key='ocorr_periodo')

            unidade_sel = st.selectbox("Unidade:", ['Todas'] + UNIDADES,
                format_func=lambda x: UNIDADES_NOMES.get(x, x) if x != 'Todas' else 'Todas',
                key='ocorr_unidade')

            segmento_sel = st.selectbox("Segmento:", ['Todos', 'Anos Finais', 'Ensino Médio'],
                key='ocorr_segmento')

            tipos_disp = sorted(df_ocorr['tipo'].unique()) if 'tipo' in df_ocorr.columns else []
            tipo_sel = st.selectbox("Tipo:", ['Todos'] + tipos_disp, key='ocorr_tipo')

            grav_sel = st.selectbox("Gravidade:", ['Todas'] + GRAVIDADES, key='ocorr_grav')

            categorias_disp = sorted(df_ocorr['categoria'].unique().tolist()) if 'categoria' in df_ocorr.columns else []
            cat_sel = st.selectbox("Categoria:", ['Todas'] + categorias_disp,
                index=(['Todas'] + categorias_disp).index('Disciplinar') if 'Disciplinar' in categorias_disp else 0,
                key='ocorr_cat')

        # Aplicar filtros
        df = df_ocorr.copy()
        if 'data' in df.columns and isinstance(periodo_range, tuple) and len(periodo_range) == 2:
            df = df[(df['data'].dt.date >= periodo_range[0]) & (df['data'].dt.date <= periodo_range[1])]
        if unidade_sel != 'Todas' and 'unidade' in df.columns:
            df = df[df['unidade'] == unidade_sel]
        if segmento_sel == 'Anos Finais' and 'serie' in df.columns:
            df = df[df['serie'].isin(SERIES_FUND_II)]
        elif segmento_sel == 'Ensino Médio' and 'serie' in df.columns:
            df = df[df['serie'].isin(SERIES_EM)]
        if tipo_sel != 'Todos' and 'tipo' in df.columns:
            df = df[df['tipo'] == tipo_sel]
        if grav_sel != 'Todas' and 'gravidade' in df.columns:
            df = df[df['gravidade'] == grav_sel]
        if cat_sel != 'Todas' and 'categoria' in df.columns:
            df = df[df['categoria'] == cat_sel]

        if df.empty:
            with tab_risco:
                st.info("Nenhuma ocorrência para os filtros selecionados.")
            with tab_geral:
                st.info("Nenhuma ocorrência para os filtros selecionados.")
        else:
            # ========== METRICAS (acima das tabs) ==========
            _mostrar_metricas(df, tab_risco)

            # ========== TAB: ALUNOS EM RISCO ==========
            with tab_risco:
                _tab_alunos_risco(df)

            # ========== TAB: VISAO GERAL ==========
            with tab_geral:
                _tab_visao_geral(df)

            # ========== TAB: POR TURMA ==========
            with tab_turma:
                _tab_por_turma(df)

            # ========== TAB: POR ALUNO ==========
            with tab_aluno:
                _tab_por_aluno(df)

            # ========== TAB: DETALHAMENTO ==========
            with tab_detalhe:
                _tab_detalhamento(df)
    else:
        with tab_info:
            _mostrar_info_sistema()


def _tab_novo_registro(df_alunos, tem_alunos):
    """Tab de registro de nova ocorrencia."""
    st.subheader("Registrar Nova Ocorrência")

    if not tem_alunos:
        st.warning("Dados de alunos não disponíveis. Registre manualmente.")

    with st.form("form_ocorrencia", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            data_ocorr = st.date_input("Data:", value=_hoje().date() if hasattr(_hoje(), 'date') else _hoje(), key='form_data')

            if tem_alunos:
                # Filtrar por unidade primeiro
                unidades_disp = sorted(df_alunos['unidade'].unique()) if 'unidade' in df_alunos.columns else []
                unidade_form = st.selectbox("Unidade:", unidades_disp,
                    format_func=lambda x: UNIDADES_NOMES.get(x, x),
                    key='form_unidade')

                df_filtrado = df_alunos[df_alunos['unidade'] == unidade_form] if 'unidade' in df_alunos.columns else df_alunos

                # Filtrar por serie
                series_disp = sorted(df_filtrado['serie'].unique()) if 'serie' in df_filtrado.columns else []
                serie_form = st.selectbox("Série:", series_disp, key='form_serie')

                df_filtrado = df_filtrado[df_filtrado['serie'] == serie_form] if 'serie' in df_filtrado.columns else df_filtrado

                # Selecionar aluno
                alunos_disp = df_filtrado[['aluno_id', 'aluno_nome', 'turma']].drop_duplicates().sort_values('aluno_nome')
                if not alunos_disp.empty:
                    aluno_options = {f"{r['aluno_nome']} ({r['turma']})": r for _, r in alunos_disp.iterrows()}
                    aluno_sel = st.selectbox("Aluno:", list(aluno_options.keys()), key='form_aluno')
                    aluno_info = aluno_options.get(aluno_sel, {})
                else:
                    st.warning("Nenhum aluno encontrado para esta série.")
                    aluno_info = {}
                    aluno_sel = None
            else:
                unidade_form = st.selectbox("Unidade:", UNIDADES,
                    format_func=lambda x: UNIDADES_NOMES.get(x, x), key='form_unidade')
                serie_form = st.text_input("Série:", key='form_serie')
                aluno_nome_manual = st.text_input("Nome do Aluno:", key='form_aluno_nome')
                aluno_info = {}
                aluno_sel = aluno_nome_manual

        with col2:
            tipo_ocorr = st.selectbox("Tipo de Ocorrência:", TIPOS_OCORRENCIA, key='form_tipo')
            gravidade = st.selectbox("Gravidade:", GRAVIDADES, key='form_gravidade')

            # Sugestoes de providencia baseadas na gravidade
            sugestoes = PROVIDENCIAS_SUGERIDAS.get(gravidade, [])
            providencia = st.selectbox("Providência:", [''] + sugestoes + ['Outra...'], key='form_prov')
            if providencia == 'Outra...':
                providencia = st.text_input("Especifique a providência:", key='form_prov_custom')

            responsavel = st.text_input("Responsável pelo registro:",
                value=st.session_state.get("user_display", ""), key='form_responsavel')

        descricao = st.text_area("Descrição da ocorrência:", height=100, key='form_descricao',
                                 placeholder="Descreva o que aconteceu, quando, onde e as circunstâncias...")

        submitted = st.form_submit_button("Registrar Ocorrência", type="primary", use_container_width=True)

        if submitted:
            # Validar campos obrigatorios
            if not descricao.strip():
                st.error("A descrição é obrigatória.")
            elif not aluno_sel:
                st.error("Selecione ou informe o aluno.")
            else:
                # Montar registro
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
                    st.success(f"Ocorrência registrada com sucesso! ({registro['aluno_nome']} - {tipo_ocorr})")
                    st.balloons()
                else:
                    st.error("Erro ao salvar a ocorrência.")

    # Ultimos registros
    df_recentes = carregar_ocorrencias()
    if not df_recentes.empty:
        st.markdown("---")
        st.subheader("Últimos Registros")
        cols_show = [c for c in ['data', 'aluno_nome', 'serie', 'tipo', 'categoria', 'gravidade', 'descricao', 'responsavel']
                     if c in df_recentes.columns]
        if 'data' in df_recentes.columns:
            df_recentes = df_recentes.sort_values('data', ascending=False)
        st.dataframe(df_recentes[cols_show].head(10) if cols_show else df_recentes.head(10),
                     use_container_width=True, hide_index=True)
        st.caption(f"Total de ocorrências registradas: {len(df_recentes)}")


def _mostrar_metricas(df, container):
    """Mostra metricas resumo."""
    with container:
        col1, col2, col3, col4, col5 = st.columns(5)

        total = len(df)
        alunos_envolvidos = df['aluno_id'].nunique() if 'aluno_id' in df.columns else df['aluno_nome'].nunique() if 'aluno_nome' in df.columns else 0
        reincidentes = 0
        if 'aluno_id' in df.columns:
            contagem = df['aluno_id'].value_counts()
            reincidentes = (contagem > 1).sum()
        graves = len(df[df['gravidade'] == 'Grave']) if 'gravidade' in df.columns else 0
        media_dia = total / max(1, df['data'].dt.date.nunique()) if 'data' in df.columns else 0

        with col1:
            st.metric("Total Ocorrências", total)
        with col2:
            st.metric("Alunos Envolvidos", alunos_envolvidos)
        with col3:
            st.metric("Reincidentes", reincidentes)
        with col4:
            st.metric("Graves", graves)
        with col5:
            st.metric("Média/Dia", f"{media_dia:.1f}")


def _tab_alunos_risco(df):
    """Tab de alunos com mais ocorrencias (precisam de intervencao)."""
    st.subheader("Alunos que Precisam de Atenção")

    if 'aluno_nome' not in df.columns:
        st.info("Coluna aluno_nome não disponível.")
        return

    # Alunos com mais ocorrencias
    ranking = df.groupby(['aluno_nome']).agg(
        total=('tipo', 'count'),
        graves=('gravidade', lambda x: (x == 'Grave').sum()) if 'gravidade' in df.columns else ('tipo', 'count'),
        tipos=('tipo', lambda x: ', '.join(sorted(x.unique()))),
    ).reset_index().sort_values('total', ascending=False)

    # Adicionar info de serie/unidade
    extras = ['serie', 'unidade', 'turma']
    for col in extras:
        if col in df.columns:
            info = df.groupby('aluno_nome')[col].first()
            ranking = ranking.merge(info, on='aluno_nome', how='left')

    # Separar por gravidade
    criticos = ranking[ranking['total'] >= 5]
    alerta = ranking[(ranking['total'] >= 3) & (ranking['total'] < 5)]
    atencao = ranking[(ranking['total'] >= 2) & (ranking['total'] < 3)]

    for grupo, label, css in [(criticos, 'INTERVENÇÃO URGENTE (5+ ocorrências)', 'ocorr-grave'),
                               (alerta, 'ALERTA (3-4 ocorrências)', 'ocorr-media'),
                               (atencao, 'ATENÇÃO (2 ocorrências)', 'ocorr-leve')]:
        if grupo.empty:
            continue
        st.markdown(f"### {label} ({len(grupo)} alunos)")
        for _, row in grupo.iterrows():
            serie_info = f" | {row['serie']}" if 'serie' in row.index and pd.notna(row.get('serie')) else ''
            unidade_info = f" | {UNIDADES_NOMES.get(row.get('unidade', ''), row.get('unidade', ''))}" if 'unidade' in row.index and pd.notna(row.get('unidade')) else ''
            graves_info = f" | {int(row['graves'])} grave(s)" if 'graves' in row.index and row['graves'] > 0 else ''

            st.markdown(f"""
            <div class="{css}">
                <strong>{row['aluno_nome']}</strong>{serie_info}{unidade_info}
                <span style="float: right; font-weight: bold;">{int(row['total'])} ocorrências{graves_info}</span>
                <br><small>Tipos: {row['tipos']}</small>
            </div>
            """, unsafe_allow_html=True)

    if criticos.empty and alerta.empty and atencao.empty:
        st.success("Nenhum aluno com ocorrências reincidentes!")


def _tab_visao_geral(df):
    """Tab de visao geral das ocorrencias."""
    st.subheader("Panorama Geral")

    col_e, col_d = st.columns(2)

    with col_e:
        if 'tipo' in df.columns:
            tipo_counts = df['tipo'].value_counts().reset_index()
            tipo_counts.columns = ['Tipo', 'Quantidade']
            fig = px.pie(tipo_counts, values='Quantidade', names='Tipo',
                        title='Distribuição por Tipo',
                        color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)

    with col_d:
        if 'gravidade' in df.columns:
            grav_counts = df['gravidade'].value_counts().reset_index()
            grav_counts.columns = ['Gravidade', 'Quantidade']
            fig2 = px.bar(grav_counts, x='Gravidade', y='Quantidade',
                         color='Gravidade',
                         color_discrete_map={'Grave': '#D32F2F', 'Media': '#F57C00', 'Leve': '#FBC02D'},
                         title='Distribuição por Gravidade')
            st.plotly_chart(fig2, use_container_width=True)

    # Timeline
    if 'data' in df.columns:
        timeline = df.groupby(df['data'].dt.date).size().reset_index()
        timeline.columns = ['Data', 'Ocorrências']
        fig3 = px.line(timeline, x='Data', y='Ocorrências', markers=True,
                      title='Ocorrências ao Longo do Tempo')
        fig3.update_traces(line_color='#E53935')
        st.plotly_chart(fig3, use_container_width=True)

    # Por unidade
    if 'unidade' in df.columns and df['unidade'].nunique() > 1:
        uni_counts = df['unidade'].value_counts().reset_index()
        uni_counts.columns = ['Unidade', 'Quantidade']
        uni_counts['Unidade_Nome'] = uni_counts['Unidade'].map(UNIDADES_NOMES).fillna(uni_counts['Unidade'])
        fig4 = px.bar(uni_counts, x='Unidade_Nome', y='Quantidade',
                     color='Unidade', color_discrete_map=CORES_UNIDADES,
                     title='Ocorrências por Unidade')
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # Por dia da semana
    if 'data' in df.columns:
        dias = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
        df_dias = df.copy()
        df_dias['dia_semana'] = df_dias['data'].dt.dayofweek.map(dias)
        dia_counts = df_dias['dia_semana'].value_counts().reindex(
            ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'], fill_value=0
        ).reset_index()
        dia_counts.columns = ['Dia', 'Ocorrências']
        fig5 = px.bar(dia_counts, x='Dia', y='Ocorrências',
                     color_discrete_sequence=['#1a237e'],
                     title='Ocorrências por Dia da Semana')
        st.plotly_chart(fig5, use_container_width=True)


def _tab_por_turma(df):
    """Tab de analise por turma."""
    st.subheader("Ocorrências por Turma/Série")

    if 'serie' in df.columns:
        serie_counts = df['serie'].value_counts().reset_index()
        serie_counts.columns = ['Série', 'Ocorrências']
        fig = px.bar(serie_counts, x='Série', y='Ocorrências',
                    color='Ocorrências',
                    color_continuous_scale=['#FBC02D', '#D32F2F'],
                    title='Ocorrências por Série')
        st.plotly_chart(fig, use_container_width=True)

    if 'turma' in df.columns and df['turma'].notna().any():
        turma_counts = df['turma'].value_counts().reset_index()
        turma_counts.columns = ['Turma', 'Ocorrências']
        st.subheader("Ranking por Turma")
        st.dataframe(turma_counts.head(20), use_container_width=True, hide_index=True)

    # Heatmap serie x tipo
    if 'serie' in df.columns and 'tipo' in df.columns:
        col_agg = 'aluno_id' if 'aluno_id' in df.columns else 'data'
        pivot = df.pivot_table(index='serie', columns='tipo', values=col_agg,
                              aggfunc='count', fill_value=0)
        if not pivot.empty and len(pivot) > 0:
            fig3 = px.imshow(
                pivot, text_auto=True,
                color_continuous_scale=['#FFFFFF', '#FBC02D', '#D32F2F'],
                title='Heatmap: Ocorrências (Série x Tipo)'
            )
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)

    # Heatmap serie x gravidade
    if 'serie' in df.columns and 'gravidade' in df.columns:
        col_agg = 'aluno_id' if 'aluno_id' in df.columns else 'data'
        pivot2 = df.pivot_table(index='serie', columns='gravidade', values=col_agg,
                               aggfunc='count', fill_value=0)
        for g in GRAVIDADES:
            if g not in pivot2.columns:
                pivot2[g] = 0
        pivot2 = pivot2[GRAVIDADES]
        if not pivot2.empty:
            fig4 = px.imshow(
                pivot2, text_auto=True,
                color_continuous_scale=['#E8F5E9', '#FFF9C4', '#FFCDD2'],
                title='Heatmap: Ocorrências (Série x Gravidade)'
            )
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)


def _tab_por_aluno(df):
    """Tab de ranking por aluno."""
    st.subheader("Alunos com Mais Ocorrências")

    col_nome = 'aluno_nome' if 'aluno_nome' in df.columns else 'aluno_id' if 'aluno_id' in df.columns else None
    if not col_nome:
        st.info("Dados de aluno não disponíveis.")
        return

    ranking = df[col_nome].value_counts().reset_index()
    ranking.columns = ['Aluno', 'Ocorrências']

    # Top 20
    fig = px.bar(
        ranking.head(20), x='Ocorrências', y='Aluno', orientation='h',
        color='Ocorrências',
        color_continuous_scale=['#FBC02D', '#F57C00', '#D32F2F'],
        title='Top 20 Alunos com Mais Ocorrências'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Detalhar aluno especifico
    st.markdown("---")
    aluno_det = st.selectbox("Detalhar aluno:", [''] + ranking['Aluno'].tolist(), key='ocorr_det_aluno')
    if aluno_det:
        df_aluno = df[df[col_nome] == aluno_det].sort_values('data', ascending=False) if 'data' in df.columns else df[df[col_nome] == aluno_det]
        cols_det = [c for c in ['data', 'tipo', 'gravidade', 'descricao', 'providencia', 'responsavel'] if c in df_aluno.columns]

        # Resumo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Ocorrências", len(df_aluno))
        with col2:
            graves = len(df_aluno[df_aluno['gravidade'] == 'Grave']) if 'gravidade' in df_aluno.columns else 0
            st.metric("Graves", graves)
        with col3:
            if 'tipo' in df_aluno.columns:
                tipo_mais = df_aluno['tipo'].mode().iloc[0] if not df_aluno['tipo'].mode().empty else '-'
                st.metric("Tipo mais Frequente", tipo_mais)

        st.dataframe(df_aluno[cols_det] if cols_det else df_aluno, use_container_width=True, hide_index=True)


def _tab_detalhamento(df):
    """Tab de lista completa com busca."""
    st.subheader("Registro Completo")

    busca = st.text_input("Buscar:", placeholder="Nome do aluno, tipo de ocorrência...", key='ocorr_busca')

    df_show = df.copy()
    if busca:
        mask = pd.Series(False, index=df_show.index)
        for col in ['aluno_nome', 'tipo', 'descricao', 'responsavel', 'providencia']:
            if col in df_show.columns:
                mask = mask | df_show[col].astype(str).str.contains(busca, case=False, na=False)
        df_show = df_show[mask]

    cols_show = [c for c in ['data', 'aluno_nome', 'serie', 'turma', 'unidade', 'tipo',
                              'categoria', 'gravidade', 'descricao', 'providencia', 'responsavel']
                 if c in df_show.columns]

    if 'data' in df_show.columns:
        df_show = df_show.sort_values('data', ascending=False)

    # Colorir gravidade
    if 'gravidade' in df_show.columns:
        def _color_grav(val):
            colors = {'Grave': 'background-color: #FFCDD2', 'Media': 'background-color: #FFE0B2', 'Leve': 'background-color: #FFF9C4'}
            return colors.get(val, '')
        styled = df_show[cols_show].style.map(_color_grav, subset=['gravidade']) if cols_show else df_show.style
        st.dataframe(styled, use_container_width=True, hide_index=True, height=500)
    else:
        st.dataframe(df_show[cols_show] if cols_show else df_show, use_container_width=True, hide_index=True, height=500)

    st.caption(f"Total: {len(df_show)} ocorrências")

    # Exportar
    if not df_show.empty:
        csv_data = df_show[cols_show].to_csv(index=False) if cols_show else df_show.to_csv(index=False)
        st.download_button(
            "Exportar CSV",
            csv_data,
            file_name=f"ocorrencias_{_hoje().strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )


def _mostrar_info_sistema():
    """Informacoes sobre o sistema de ocorrencias."""
    st.markdown("""
    ## Sistema de Registro de Ocorrências

    Este sistema permite o registro e acompanhamento de ocorrências disciplinares
    dos alunos do Colégio ELO.

    ### Tipos de Ocorrência
    | Tipo | Descrição |
    |------|-----------|
    | Indisciplina | Comportamento inadequado em sala |
    | Atraso | Chegada após o horário |
    | Falta de Material | Não trouxe material necessário |
    | Agressão Verbal/Física | Conflitos entre alunos |
    | Uso de Celular | Uso indevido durante a aula |
    | Evasão de Aula | Saída sem autorização |
    | Bullying | Intimidação/assédio entre alunos |
    | Registro Positivo | Destaque por bom comportamento |

    ### Níveis de Gravidade
    | Gravidade | Providência Sugerida |
    |-----------|---------------------|
    | **Leve** | Advertência verbal, conversa com aluno |
    | **Média** | Advertência escrita, contato com responsável |
    | **Grave** | Suspensão, reunião com responsável, encaminhamento |

    ### Integração com ABC
    Os dados de ocorrências alimentam a **dimensão B (Behavior)** do
    Sistema ABC de Alerta Precoce (Página 23), contribuindo para
    identificar alunos em risco.

    ### Dados
    - As ocorrências são salvas em `fato_Ocorrencias.csv`
    - Cada registro inclui data, aluno, tipo, gravidade e descrição
    - Os dados podem ser exportados em CSV para relatórios
    """)


if __name__ == "__main__":
    main()
