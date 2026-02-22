#!/usr/bin/env python3
"""
PÁGINA 10: DETALHAMENTO DE AULAS
Quem registrou, o quê, onde, quando - visão completa
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import carregar_fato_aulas, _hoje, ORDEM_SERIES, SERIES_FUND_II, SERIES_EM
from components import (
    filtro_unidade, filtro_segmento,
    filtro_serie as comp_filtro_serie,
    aplicar_filtro_unidade, aplicar_filtro_segmento, aplicar_filtro_serie,
    cabecalho_pagina, metricas_em_colunas, botao_download_csv,
)

from auth import get_user_unit

def main():
    cabecalho_pagina("📋 Detalhamento de Aulas", "Visão completa dos registros: quem, o quê, onde, quando")

    df = carregar_fato_aulas()

    if df.empty:
        st.warning("Dados não carregados. Execute a extração do SIGA primeiro.")
        return

    # ========== FILTROS NO TOPO ==========
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        filtro_un = filtro_unidade(key="pg10_un")

    with col2:
        filtro_seg = filtro_segmento(todos_label="TODOS", key="pg10_seg")

    # Aplica filtro de segmento primeiro
    df_seg = aplicar_filtro_segmento(df.copy(), filtro_seg)

    with col3:
        df_for_series = df_seg[df_seg['unidade'] == filtro_un] if filtro_un != 'TODAS' else df_seg
        series_disp_list = sorted(
            df_for_series['serie'].dropna().unique().tolist(),
            key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99,
        )
        filtro_serie = comp_filtro_serie(
            series_disp_list, todas_label="TODAS", key="pg10_serie",
        )

    with col4:
        if filtro_un != 'TODAS':
            disc_disp = ['TODAS'] + sorted(df_seg[df_seg['unidade'] == filtro_un]['disciplina'].dropna().unique().tolist())
        else:
            disc_disp = ['TODAS'] + sorted(df_seg['disciplina'].dropna().unique().tolist())
        filtro_disc = st.selectbox("📖 Disciplina", disc_disp)

    with col5:
        if filtro_un != 'TODAS':
            profs_disp = ['TODOS'] + sorted(df_seg[df_seg['unidade'] == filtro_un]['professor'].dropna().unique().tolist())
        else:
            profs_disp = ['TODOS'] + sorted(df_seg['professor'].dropna().unique().tolist())
        filtro_prof = st.selectbox("👨‍🏫 Professor", profs_disp)

    # Segunda linha de filtros
    col6, col7, col8, col9 = st.columns(4)

    with col6:
        turmas_disp = ['TODAS'] + sorted(df_seg['turma'].dropna().unique().tolist())
        filtro_turma = st.selectbox("🎓 Turma", turmas_disp)

    with col7:
        # Período - por padrão mostra apenas até HOJE
        data_min = df_seg['data'].min()
        data_max = df_seg['data'].max()

        hoje = _hoje()

        if pd.notna(data_min) and pd.notna(data_max):
            # Por padrão, mostra apenas ATÉ HOJE (não inclui futuros)
            data_fim_padrao = min(data_max.date(), hoje.date())
            filtro_data = st.date_input("📅 Período",
                                        value=(data_min.date(), data_fim_padrao),
                                        min_value=data_min.date(),
                                        max_value=data_max.date())
        else:
            filtro_data = None

    with col8:
        # Filtro de situação
        situacoes = ['TODAS'] + sorted(df_seg['situacao'].dropna().unique().tolist())
        filtro_situacao = st.selectbox("📌 Situação", situacoes,
                                       help="PROGRAMADA = agendada, MINISTRADA = efetivamente dada")

    with col9:
        # Com/sem conteúdo
        filtro_conteudo = st.selectbox("📝 Conteúdo", ['TODOS', 'Com conteúdo', 'Sem conteúdo'])

    # Terceira linha extra - filtro de tarefas
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)

    with col_t1:
        filtro_tarefa = st.selectbox("📋 Tarefa", ['TODOS', 'Com tarefa', 'Sem tarefa'])

    # Terceira linha - ordenação
    col10, col11, col12, col13 = st.columns(4)

    with col10:
        # Ordenação
        ordenar = st.selectbox("🔃 Ordenar por", ['Data (recente)', 'Data (antiga)',
                                                  'Unidade', 'Professor', 'Disciplina'])

    # Aplica filtros (começa do df_seg que já tem o filtro de segmento)
    df_filtrado = aplicar_filtro_unidade(df_seg.copy(), filtro_un)
    df_filtrado = aplicar_filtro_serie(df_filtrado, filtro_serie, todas_label="TODAS")
    if filtro_disc != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['disciplina'] == filtro_disc]
    if filtro_prof != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['professor'] == filtro_prof]
    if filtro_turma != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['turma'] == filtro_turma]
    if filtro_data and len(filtro_data) == 2:
        df_filtrado = df_filtrado[
            (df_filtrado['data'].dt.date >= filtro_data[0]) &
            (df_filtrado['data'].dt.date <= filtro_data[1])
        ]
    if filtro_conteudo == 'Com conteúdo':
        df_filtrado = df_filtrado[df_filtrado['conteudo'].notna() & (df_filtrado['conteudo'] != '')]
    elif filtro_conteudo == 'Sem conteúdo':
        df_filtrado = df_filtrado[df_filtrado['conteudo'].isna() | (df_filtrado['conteudo'] == '')]

    # Filtro por tarefa
    if filtro_tarefa == 'Com tarefa':
        df_filtrado = df_filtrado[df_filtrado['tarefa'].notna() & (df_filtrado['tarefa'] != '')]
    elif filtro_tarefa == 'Sem tarefa':
        df_filtrado = df_filtrado[df_filtrado['tarefa'].isna() | (df_filtrado['tarefa'] == '')]

    # Filtro por situação
    if filtro_situacao != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['situacao'] == filtro_situacao]

    # Ordenação
    if ordenar == 'Data (recente)':
        df_filtrado = df_filtrado.sort_values('data', ascending=False)
    elif ordenar == 'Data (antiga)':
        df_filtrado = df_filtrado.sort_values('data', ascending=True)
    elif ordenar == 'Unidade':
        df_filtrado = df_filtrado.sort_values(['unidade', 'data'], ascending=[True, False])
    elif ordenar == 'Professor':
        df_filtrado = df_filtrado.sort_values(['professor', 'data'], ascending=[True, False])
    elif ordenar == 'Disciplina':
        df_filtrado = df_filtrado.sort_values(['disciplina', 'data'], ascending=[True, False])

    # ========== MÉTRICAS ==========
    st.markdown("---")

    com_conteudo = df_filtrado[df_filtrado['conteudo'].notna() & (df_filtrado['conteudo'] != '')].shape[0]
    pct = (com_conteudo / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0

    metricas_em_colunas([
        {'label': 'Total de Aulas', 'value': f"{len(df_filtrado):,}"},
        {'label': 'Professores', 'value': df_filtrado['professor'].nunique()},
        {'label': 'Turmas', 'value': df_filtrado['turma'].nunique()},
        {'label': 'Disciplinas', 'value': df_filtrado['disciplina'].nunique()},
        {'label': 'Com Conteúdo', 'value': f"{pct:.0f}%"},
    ])

    # Segunda linha de métricas
    col_m6, col_m7, col_m8, col_m9, col_m10 = st.columns(5)

    with col_m6:
        com_tarefa = df_filtrado[df_filtrado['tarefa'].notna() & (df_filtrado['tarefa'] != '')].shape[0]
        pct_tarefa = (com_tarefa / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
        st.metric("Com Tarefa", f"{pct_tarefa:.0f}%")

    with col_m7:
        st.metric("Total c/ Tarefa", f"{com_tarefa:,}")

    # ========== TABELA DETALHADA ==========
    st.markdown("---")
    st.subheader(f"📊 Registros ({len(df_filtrado):,} aulas)")

    # Seleção de colunas
    colunas_disponiveis = ['data', 'unidade', 'serie', 'turma', 'disciplina',
                           'professor', 'numero_aula', 'conteudo', 'tarefa', 'situacao']
    colunas_selecionadas = st.multiselect(
        "Colunas a exibir:",
        colunas_disponiveis,
        default=['data', 'unidade', 'disciplina', 'professor', 'conteudo', 'tarefa']
    )

    if not colunas_selecionadas:
        colunas_selecionadas = colunas_disponiveis

    # Prepara visualização
    df_show = df_filtrado[colunas_selecionadas].copy()

    # Formata data
    if 'data' in df_show.columns:
        df_show['data'] = df_show['data'].dt.strftime('%d/%m/%Y')

    # Renomeia colunas
    rename_map = {
        'data': 'Data',
        'unidade': 'Unidade',
        'serie': 'Série',
        'turma': 'Turma',
        'disciplina': 'Disciplina',
        'professor': 'Professor',
        'numero_aula': 'Nº Aula',
        'conteudo': 'Conteúdo',
        'tarefa': 'Tarefa',
        'situacao': 'Situação'
    }
    df_show = df_show.rename(columns=rename_map)

    # Paginação
    LINHAS_POR_PAGINA = 50
    total_registros = len(df_show)
    total_paginas = max(1, (total_registros + LINHAS_POR_PAGINA - 1) // LINHAS_POR_PAGINA)

    if 'pagina_detalhamento' not in st.session_state:
        st.session_state.pagina_detalhamento = 1
    # Reset se filtros mudaram e página ficou fora do range
    if st.session_state.pagina_detalhamento > total_paginas:
        st.session_state.pagina_detalhamento = 1

    col_pag1, col_pag2, col_pag3, col_pag4, col_pag5 = st.columns([1, 1, 2, 1, 1])
    with col_pag1:
        if st.button("⏮ Primeira", disabled=st.session_state.pagina_detalhamento <= 1):
            st.session_state.pagina_detalhamento = 1
            st.rerun()
    with col_pag2:
        if st.button("◀ Anterior", disabled=st.session_state.pagina_detalhamento <= 1):
            st.session_state.pagina_detalhamento -= 1
            st.rerun()
    with col_pag3:
        st.markdown(f"<div style='text-align:center;padding:8px'>Página **{st.session_state.pagina_detalhamento}** de **{total_paginas}** ({total_registros:,} registros)</div>", unsafe_allow_html=True)
    with col_pag4:
        if st.button("Próxima ▶", disabled=st.session_state.pagina_detalhamento >= total_paginas):
            st.session_state.pagina_detalhamento += 1
            st.rerun()
    with col_pag5:
        if st.button("Última ⏭", disabled=st.session_state.pagina_detalhamento >= total_paginas):
            st.session_state.pagina_detalhamento = total_paginas
            st.rerun()

    inicio = (st.session_state.pagina_detalhamento - 1) * LINHAS_POR_PAGINA
    fim = inicio + LINHAS_POR_PAGINA
    st.dataframe(df_show.iloc[inicio:fim], use_container_width=True, hide_index=True, height=500)

    # ========== DOWNLOAD ==========
    st.markdown("---")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        botao_download_csv(
            df_filtrado,
            "aulas_detalhadas",
            label="📥 Download Completo (CSV)",
            key="pg10_dl_completo",
        )

    with col_d2:
        # Download dos filtrados visíveis (página atual)
        botao_download_csv(
            df_show.iloc[inicio:fim],
            "aulas_filtradas",
            label="📥 Download Exibido (CSV)",
            key="pg10_dl_exibido",
        )

    # ========== ANÁLISE RÁPIDA ==========
    st.markdown("---")
    st.header("📊 Análise Rápida dos Dados Filtrados")

    col_a1, col_a2 = st.columns(2)

    with col_a1:
        st.subheader("Top 10 Professores (mais aulas)")
        top_profs = df_filtrado.groupby('professor').size().reset_index(name='aulas')
        top_profs = top_profs.nlargest(10, 'aulas')
        st.dataframe(top_profs, use_container_width=True, hide_index=True)

    with col_a2:
        st.subheader("Aulas por Dia da Semana")
        if 'data' in df_filtrado.columns and df_filtrado['data'].notna().any():
            df_filtrado['dia_semana'] = df_filtrado['data'].dt.day_name()
            dias = df_filtrado.groupby('dia_semana').size().reset_index(name='aulas')
            ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            nomes = {'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
                    'Thursday': 'Quinta', 'Friday': 'Sexta'}
            dias['dia_semana'] = dias['dia_semana'].map(nomes)
            dias = dias.dropna()
            st.dataframe(dias, use_container_width=True, hide_index=True)

    # ========== BUSCA DE CONTEÚDO E TAREFAS ==========
    st.markdown("---")
    st.header("🔍 Busca por Conteúdo e Tarefas")

    # Filtros dedicados para a busca
    st.markdown("**Filtros da Busca:**")
    cb1, cb2, cb3, cb4, cb5 = st.columns(5)

    with cb1:
        un_busca = filtro_unidade(key="pg10_busca_un")

    with cb2:
        seg_busca = filtro_segmento(todos_label="TODOS", key="pg10_busca_seg")

    # Aplica filtro de segmento e unidade para popular série/turma
    df_busca_base = aplicar_filtro_unidade(df.copy(), un_busca)
    df_busca_base = aplicar_filtro_segmento(df_busca_base, seg_busca)

    with cb3:
        serie_busca_opts = ['TODAS'] + sorted(df_busca_base['serie'].dropna().unique().tolist(), key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99)
        serie_busca = st.selectbox("📚 Série", serie_busca_opts, key='busca_serie')

    if serie_busca != 'TODAS':
        df_busca_base = df_busca_base[df_busca_base['serie'] == serie_busca]

    with cb4:
        turma_busca_opts = ['TODAS'] + sorted(df_busca_base['turma'].dropna().unique().tolist())
        turma_busca = st.selectbox("🎓 Turma", turma_busca_opts, key='busca_turma')

    with cb5:
        qtd_busca = st.selectbox("📄 Exibir", ['10', '20', '50', '100', 'Todos'], key='busca_qtd')

    # Aplica filtros restantes
    if turma_busca != 'TODAS':
        df_busca_base = df_busca_base[df_busca_base['turma'] == turma_busca]

    # Quantidade
    limite_busca = len(df_busca_base) if qtd_busca == 'Todos' else int(qtd_busca)

    # Função para gerar texto imprimível
    def gerar_texto_impressao(df_imp, titulo, campo):
        texto = f"{'='*80}\n"
        texto += f"  {titulo.upper()} - COLÉGIO ELO 2026\n"
        texto += f"  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        if un_busca != 'TODAS':
            texto += f"  Unidade: {un_busca}\n"
        if serie_busca != 'TODAS':
            texto += f"  Série: {serie_busca}\n"
        if turma_busca != 'TODAS':
            texto += f"  Turma: {turma_busca}\n"
        texto += f"  Total: {len(df_imp)} registros\n"
        texto += f"{'='*80}\n\n"
        for _, row in df_imp.iterrows():
            data_str = row['data'].strftime('%d/%m/%Y') if pd.notna(row['data']) else '-'
            texto += f"[{data_str}] {row.get('unidade','-')} | {row.get('disciplina','-')} | {row.get('professor','-')}\n"
            if row.get('turma'):
                texto += f"  Turma: {row['turma']}\n"
            conteudo_val = str(row.get(campo, '') or '')
            if conteudo_val:
                texto += f"  {campo.capitalize()}: {conteudo_val}\n"
            texto += f"{'-'*60}\n"
        return texto

    tab_busca0, tab_busca1, tab_busca2, tab_busca3 = st.tabs(["🔍 Busca Geral", "📝 Só Conteúdo", "📋 Só Tarefa", "📊 Últimas Tarefas"])

    with tab_busca0:
        termo_geral = st.text_input("Buscar em conteúdo E tarefa ao mesmo tempo:",
                                    placeholder="Ex: trilha, equação, célula, revolução...")

        if termo_geral:
            mask_cont = df_busca_base['conteudo'].str.contains(termo_geral, case=False, na=False)
            mask_tar = df_busca_base['tarefa'].str.contains(termo_geral, case=False, na=False)
            df_busca_geral = df_busca_base[mask_cont | mask_tar].copy()
            df_busca_geral = df_busca_geral.sort_values('data', ascending=False)

            if len(df_busca_geral) > 0:
                # Métricas
                n_cont = mask_cont.sum()
                n_tar = mask_tar.sum()
                n_profs = df_busca_geral['professor'].nunique()
                st.success(f"Encontrados {len(df_busca_geral)} registros com '{termo_geral}' | {n_cont} em conteúdo, {n_tar} em tarefa | {n_profs} professores | Exibindo {min(limite_busca, len(df_busca_geral))}")

                df_geral_show = df_busca_geral[['data', 'unidade', 'serie', 'turma', 'disciplina', 'professor', 'conteudo', 'tarefa']].head(limite_busca).copy()
                df_geral_show['data'] = df_geral_show['data'].dt.strftime('%d/%m/%Y')
                df_geral_show = df_geral_show.rename(columns={
                    'data': 'Data', 'unidade': 'Unidade', 'serie': 'Série', 'turma': 'Turma',
                    'disciplina': 'Disciplina', 'professor': 'Professor',
                    'conteudo': 'Conteúdo', 'tarefa': 'Tarefa'
                })

                st.dataframe(df_geral_show, use_container_width=True, hide_index=True)

                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    csv_geral = df_geral_show.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Download CSV", csv_geral,
                                       f"busca_geral_{datetime.now().strftime('%Y%m%d')}.csv",
                                       "text/csv", key='dl_busca_geral')
                with col_g2:
                    # Texto imprimível com ambos os campos
                    texto = f"{'='*80}\n"
                    texto += f"  BUSCA GERAL: '{termo_geral.upper()}' - COLÉGIO ELO 2026\n"
                    texto += f"  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                    if un_busca != 'TODAS':
                        texto += f"  Unidade: {un_busca}\n"
                    if serie_busca != 'TODAS':
                        texto += f"  Série: {serie_busca}\n"
                    if turma_busca != 'TODAS':
                        texto += f"  Turma: {turma_busca}\n"
                    texto += f"  Total: {len(df_busca_geral)} registros | {n_profs} professores\n"
                    texto += f"{'='*80}\n\n"
                    for _, row in df_busca_geral.head(limite_busca).iterrows():
                        data_str = row['data'].strftime('%d/%m/%Y') if pd.notna(row['data']) else '-'
                        texto += f"[{data_str}] {row.get('unidade','-')} | {row.get('disciplina','-')} | {row.get('professor','-')}\n"
                        if row.get('turma'):
                            texto += f"  Turma: {row['turma']}\n"
                        cont_val = str(row.get('conteudo', '') or '')
                        tar_val = str(row.get('tarefa', '') or '')
                        if cont_val:
                            texto += f"  Conteúdo: {cont_val}\n"
                        if tar_val:
                            texto += f"  Tarefa: {tar_val}\n"
                        texto += f"{'-'*60}\n"
                    st.download_button("🖨️ Imprimir (TXT)", texto.encode('utf-8'),
                                       f"impressao_geral_{datetime.now().strftime('%Y%m%d')}.txt",
                                       "text/plain", key='imp_busca_geral')
            else:
                st.info(f"Nenhum registro encontrado com '{termo_geral}'.")

    with tab_busca1:
        termo_busca = st.text_input("Buscar apenas no campo conteúdo:",
                                    placeholder="Ex: equação, célula, revolução...")

        if termo_busca:
            df_busca = df_busca_base[df_busca_base['conteudo'].str.contains(termo_busca, case=False, na=False)]
            df_busca = df_busca.sort_values('data', ascending=False)

            if len(df_busca) > 0:
                st.success(f"Encontrados {len(df_busca)} registros com '{termo_busca}' | {df_busca['professor'].nunique()} professores | Exibindo {min(limite_busca, len(df_busca))}")

                df_busca_show = df_busca[['data', 'unidade', 'serie', 'turma', 'disciplina', 'professor', 'conteudo']].head(limite_busca).copy()
                df_busca_show['data'] = df_busca_show['data'].dt.strftime('%d/%m/%Y')
                df_busca_show = df_busca_show.rename(columns={
                    'data': 'Data', 'unidade': 'Unidade', 'serie': 'Série', 'turma': 'Turma',
                    'disciplina': 'Disciplina', 'professor': 'Professor', 'conteudo': 'Conteúdo'
                })

                st.dataframe(df_busca_show, use_container_width=True, hide_index=True)

                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    csv_cont = df_busca_show.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Download CSV", csv_cont,
                                       f"busca_conteudo_{datetime.now().strftime('%Y%m%d')}.csv",
                                       "text/csv", key='dl_busca_cont')
                with col_act2:
                    texto_imp = gerar_texto_impressao(df_busca.head(limite_busca), f"Busca de Conteúdo: '{termo_busca}'", 'conteudo')
                    st.download_button("🖨️ Imprimir (TXT)", texto_imp.encode('utf-8'),
                                       f"impressao_conteudo_{datetime.now().strftime('%Y%m%d')}.txt",
                                       "text/plain", key='imp_busca_cont')
            else:
                st.info(f"Nenhum registro encontrado com '{termo_busca}'.")

    with tab_busca2:
        termo_tarefa = st.text_input("Digite um termo para buscar nas tarefas registradas:",
                                     placeholder="Ex: exercício, página, estudar...")

        if termo_tarefa:
            df_busca_tarefa = df_busca_base[df_busca_base['tarefa'].str.contains(termo_tarefa, case=False, na=False)]
            df_busca_tarefa = df_busca_tarefa.sort_values('data', ascending=False)

            if len(df_busca_tarefa) > 0:
                st.success(f"Encontradas {len(df_busca_tarefa)} tarefas com '{termo_tarefa}' | Exibindo {min(limite_busca, len(df_busca_tarefa))}")

                df_tarefa_show = df_busca_tarefa[['data', 'unidade', 'serie', 'turma', 'disciplina', 'professor', 'tarefa']].head(limite_busca).copy()
                df_tarefa_show['data'] = df_tarefa_show['data'].dt.strftime('%d/%m/%Y')
                df_tarefa_show = df_tarefa_show.rename(columns={
                    'data': 'Data', 'unidade': 'Unidade', 'serie': 'Série', 'turma': 'Turma',
                    'disciplina': 'Disciplina', 'professor': 'Professor', 'tarefa': 'Tarefa'
                })

                st.dataframe(df_tarefa_show, use_container_width=True, hide_index=True)

                col_act3, col_act4 = st.columns(2)
                with col_act3:
                    csv_tar = df_tarefa_show.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Download CSV", csv_tar,
                                       f"busca_tarefa_{datetime.now().strftime('%Y%m%d')}.csv",
                                       "text/csv", key='dl_busca_tar')
                with col_act4:
                    texto_imp_t = gerar_texto_impressao(df_busca_tarefa.head(limite_busca), f"Busca de Tarefa: '{termo_tarefa}'", 'tarefa')
                    st.download_button("🖨️ Imprimir (TXT)", texto_imp_t.encode('utf-8'),
                                       f"impressao_tarefa_{datetime.now().strftime('%Y%m%d')}.txt",
                                       "text/plain", key='imp_busca_tar')
            else:
                st.info(f"Nenhuma tarefa encontrada com '{termo_tarefa}'.")

    with tab_busca3:
        st.subheader("📋 Últimas Tarefas Registradas")

        df_tarefas = df_busca_base[df_busca_base['tarefa'].notna() & (df_busca_base['tarefa'] != '')]
        df_tarefas = df_tarefas.sort_values('data', ascending=False)

        if len(df_tarefas) > 0:
            st.info(f"Total de {len(df_tarefas)} aulas com tarefas | Exibindo {min(limite_busca, len(df_tarefas))}")

            df_tarefas_show = df_tarefas[['data', 'unidade', 'serie', 'turma', 'disciplina', 'professor', 'tarefa']].head(limite_busca).copy()
            df_tarefas_show['data'] = df_tarefas_show['data'].dt.strftime('%d/%m/%Y')
            df_tarefas_show = df_tarefas_show.rename(columns={
                'data': 'Data', 'unidade': 'Unidade', 'serie': 'Série', 'turma': 'Turma',
                'disciplina': 'Disciplina', 'professor': 'Professor', 'tarefa': 'Tarefa'
            })

            st.dataframe(df_tarefas_show, use_container_width=True, hide_index=True, height=400)

            col_act5, col_act6 = st.columns(2)
            with col_act5:
                csv_tarefas = df_tarefas_show.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Download CSV", csv_tarefas,
                                   f"tarefas_{datetime.now().strftime('%Y%m%d')}.csv",
                                   "text/csv", key='dl_ultimas_tar')
            with col_act6:
                texto_imp_u = gerar_texto_impressao(df_tarefas.head(limite_busca), "Últimas Tarefas Registradas", 'tarefa')
                st.download_button("🖨️ Imprimir (TXT)", texto_imp_u.encode('utf-8'),
                                   f"impressao_ultimas_tarefas_{datetime.now().strftime('%Y%m%d')}.txt",
                                   "text/plain", key='imp_ultimas_tar')
        else:
            st.info("Nenhuma tarefa registrada nos dados filtrados.")

main()
