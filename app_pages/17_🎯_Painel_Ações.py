#!/usr/bin/env python3
"""
PAGINA 17: PAINEL DE ACOES DA COORDENACAO
Centro de comando: acoes automaticas, prioridades, checklist semanal.
Gera lista de intervencoes baseada nos dados reais.
"""

import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
    filtrar_por_periodo, PERIODOS_OPCOES,
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    _hoje, DATA_DIR, WRITABLE_DIR, SERIES_FUND_II, SERIES_EM, UNIDADES_NOMES,
    CONFORMIDADE_CRITICO, CONFORMIDADE_BAIXO, CONFORMIDADE_META,
    CONTEUDO_VAZIO_ALERTA, CONTEUDO_VAZIO_CRITICO,
    DIAS_SEM_REGISTRO_ATENCAO, DIAS_SEM_REGISTRO_URGENTE,
)
from config_cores import CORES_SERIES, CORES_UNIDADES, ORDEM_SERIES

from auth import get_user_unit

# ========== FUNCOES DE DIAGNOSTICO ==========

CONFIG_FILE = WRITABLE_DIR / "config_coordenadores.json"
ACOES_FILE = WRITABLE_DIR / "acoes_coordenacao.json"

# Dia da semana para reuniao semanal (0=Segunda, 3=Quinta, 6=Domingo)
DIA_REUNIAO_SEMANAL = 3


def carregar_config_coords():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass
    return {"coordenadores": [], "periodos_feedback": []}


def carregar_acoes():
    if ACOES_FILE.exists():
        try:
            with open(ACOES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass
    return {}


def salvar_acoes(acoes):
    with open(ACOES_FILE, 'w', encoding='utf-8') as f:
        json.dump(acoes, f, ensure_ascii=False, indent=2)


def diagnosticar_professor(df_prof, df_horario, semana, prof_nome, unidade):
    """Gera diagnostico completo de um professor."""
    alertas = []
    prioridade = 0  # 0=ok, 1=atencao, 2=urgente, 3=critico

    total_aulas = len(df_prof)

    # 1. Conformidade de registro
    series_prof = df_prof['serie'].dropna().unique()
    discs_prof = df_prof['disciplina'].dropna().unique()

    slots = 0
    for serie in series_prof:
        for disc in discs_prof:
            slot_count = len(df_horario[
                (df_horario['unidade'] == unidade) &
                (df_horario['serie'] == serie) &
                (df_horario['disciplina'] == disc)
            ])
            slots += slot_count

    esperado = slots * semana
    conformidade = (total_aulas / esperado * 100) if esperado > 0 else 0

    if conformidade < CONFORMIDADE_CRITICO:
        alertas.append(('critico', f'Conformidade crítica: {conformidade:.0f}% ({total_aulas}/{esperado})'))
        prioridade = max(prioridade, 3)
    elif conformidade < CONFORMIDADE_BAIXO:
        alertas.append(('urgente', f'Conformidade baixa: {conformidade:.0f}%'))
        prioridade = max(prioridade, 2)
    elif conformidade < CONFORMIDADE_META:
        alertas.append(('atencao', f'Conformidade abaixo da meta: {conformidade:.0f}%'))
        prioridade = max(prioridade, 1)

    # 2. Qualidade de conteudo
    vazios = len(df_prof[df_prof['conteudo'].isin(['.', ',', '-', '']) | df_prof['conteudo'].isna()])
    pct_vazio = (vazios / total_aulas * 100) if total_aulas > 0 else 0

    if pct_vazio > CONTEUDO_VAZIO_CRITICO:
        alertas.append(('critico', f'{pct_vazio:.0f}% dos registros sem conteúdo'))
        prioridade = max(prioridade, 3)
    elif pct_vazio > CONTEUDO_VAZIO_ALERTA:
        alertas.append(('urgente', f'{pct_vazio:.0f}% dos registros sem conteúdo'))
        prioridade = max(prioridade, 2)

    # 3. Dias sem registro
    if df_prof['data'].notna().any():
        ultimo_registro = df_prof['data'].max()
        dias_sem = (_hoje() - ultimo_registro).days
        if dias_sem > DIAS_SEM_REGISTRO_URGENTE:
            alertas.append(('urgente', f'{dias_sem} dias sem registrar aulas'))
            prioridade = max(prioridade, 2)
        elif dias_sem > DIAS_SEM_REGISTRO_ATENCAO:
            alertas.append(('atencao', f'{dias_sem} dias sem registro'))
            prioridade = max(prioridade, 1)
    else:
        alertas.append(('critico', 'Nenhum registro de aula'))
        prioridade = max(prioridade, 3)

    # 4. Tarefa atribuida
    sem_tarefa = df_prof['tarefa'].isna() | df_prof['tarefa'].isin(['.', ',', '-', ''])
    pct_sem_tarefa = (sem_tarefa.sum() / total_aulas * 100) if total_aulas > 0 else 0
    if pct_sem_tarefa > 80:
        alertas.append(('atencao', f'{pct_sem_tarefa:.0f}% das aulas sem tarefa'))
        prioridade = max(prioridade, 1)

    return {
        'professor': prof_nome,
        'unidade': unidade,
        'conformidade': conformidade,
        'pct_vazio': pct_vazio,
        'prioridade': prioridade,
        'alertas': alertas,
        'total_aulas': total_aulas,
        'series': ', '.join(series_prof),
    }


@st.cache_data(ttl=300)
def gerar_diagnosticos_todos(df_aulas, df_horario, semana):
    """Gera diagnostico para todos os professores (cached)."""
    diagnosticos = []
    for prof in df_aulas['professor'].dropna().unique():
        df_prof = df_aulas[df_aulas['professor'] == prof]
        un_prof = df_prof['unidade'].iloc[0]
        diag = diagnosticar_professor(df_prof, df_horario, semana, prof, un_prof)
        diagnosticos.append(diag)
    diagnosticos.sort(key=lambda x: (-x['prioridade'], -x['pct_vazio']))
    return diagnosticos


def gerar_acao_recomendada(diag):
    """Gera acao recomendada para o coordenador baseada no diagnostico."""
    p = diag['prioridade']
    if p == 3:
        return f"URGENTE: Conversa individual com {diag['professor']} sobre registros"
    elif p == 2:
        return f"Verificar registros de {diag['professor']} e agendar feedback"
    elif p == 1:
        return f"Acompanhar {diag['professor']} na próxima semana"
    return f"{diag['professor']} - OK, manter acompanhamento"


def main():
    st.title("🎯 Painel de Ações da Coordenação")
    st.markdown("**Centro de comando: diagnóstico automático, prioridades e checklist**")

    df = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()

    if df.empty:
        st.error("Dados não carregados.")
        return

    df = filtrar_ate_hoje(df)

    # Filtro de periodo (selectbox sera renderizado abaixo nos filtros)
    periodo_sel = st.session_state.get('periodo_17', PERIODOS_OPCOES[0])
    df = filtrar_por_periodo(df, periodo_sel)

    hoje = _hoje()
    semana = calcular_semana_letiva(hoje)
    cap_esperado = calcular_capitulo_esperado(semana)
    trimestre = calcular_trimestre(semana)

    config = carregar_config_coords()
    acoes_salvas = carregar_acoes()

    # ========== FILTROS ==========
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        opcoes_un = ['TODAS'] + sorted(df['unidade'].dropna().unique().tolist())
        user_unit = get_user_unit()
        default_un = opcoes_un.index(user_unit) if user_unit and user_unit in opcoes_un else 0
        un_sel = st.selectbox("Unidade:", opcoes_un, index=default_un)

    with col_f2:
        st.selectbox("Período:", PERIODOS_OPCOES, key='periodo_17')

    with col_f3:
        segmento = st.radio("Segmento:", ['Todos', 'Fund II', 'EM'], horizontal=True)

    # Aplica filtros
    df_f = df.copy()
    if un_sel != 'TODAS':
        df_f = df_f[df_f['unidade'] == un_sel]
    if segmento == 'Fund II':
        df_f = df_f[df_f['serie'].isin(SERIES_FUND_II)]
    elif segmento == 'EM':
        df_f = df_f[df_f['serie'].isin(SERIES_EM)]

    # ========== BANNER DE CONTEXTO ==========
    dias_ate_fim_tri = {
        1: (datetime(2026, 5, 8) - hoje).days,
        2: (datetime(2026, 8, 28) - hoje).days,
        3: (datetime(2026, 12, 18) - hoje).days,
    }
    dias_fim = dias_ate_fim_tri.get(trimestre, 0)

    cor_banner = '#43A047' if dias_fim > 30 else ('#F57C00' if dias_fim > 14 else '#E53935')

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {cor_banner}dd 0%, {cor_banner} 100%); color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div style="text-align: center;">
                <p style="margin: 0; opacity: 0.9;">Semana Letiva</p>
                <p style="font-size: 2em; font-weight: bold; margin: 0;">{semana}a</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; opacity: 0.9;">Trimestre</p>
                <p style="font-size: 2em; font-weight: bold; margin: 0;">{trimestre}o</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; opacity: 0.9;">Cap. Esperado</p>
                <p style="font-size: 2em; font-weight: bold; margin: 0;">{cap_esperado}/12</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; opacity: 0.9;">Dias até Fim do Tri</p>
                <p style="font-size: 2em; font-weight: bold; margin: 0;">{max(0, dias_fim)}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ========== DIAGNOSTICO AUTOMATICO ==========
    st.markdown("---")

    # Roda diagnostico para todos os professores (cached)
    diagnosticos = gerar_diagnosticos_todos(df_f, df_horario, semana)

    # ========== METRICAS RESUMO ==========
    criticos = sum(1 for d in diagnosticos if d['prioridade'] == 3)
    urgentes = sum(1 for d in diagnosticos if d['prioridade'] == 2)
    atencao = sum(1 for d in diagnosticos if d['prioridade'] == 1)
    ok = sum(1 for d in diagnosticos if d['prioridade'] == 0)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style="background: #ffebee; border-left: 4px solid #E53935; padding: 15px; border-radius: 5px; text-align: center;">
            <p style="margin: 0; color: #E53935; font-weight: bold;">CRÍTICOS</p>
            <p style="font-size: 2.5em; margin: 0; color: #E53935;">{criticos}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: #fff3e0; border-left: 4px solid #F57C00; padding: 15px; border-radius: 5px; text-align: center;">
            <p style="margin: 0; color: #F57C00; font-weight: bold;">URGENTES</p>
            <p style="font-size: 2.5em; margin: 0; color: #F57C00;">{urgentes}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background: #fff8e1; border-left: 4px solid #FBC02D; padding: 15px; border-radius: 5px; text-align: center;">
            <p style="margin: 0; color: #F9A825; font-weight: bold;">ATENÇÃO</p>
            <p style="font-size: 2.5em; margin: 0; color: #F9A825;">{atencao}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div style="background: #e8f5e9; border-left: 4px solid #43A047; padding: 15px; border-radius: 5px; text-align: center;">
            <p style="margin: 0; color: #43A047; font-weight: bold;">OK</p>
            <p style="font-size: 2.5em; margin: 0; color: #43A047;">{ok}</p>
        </div>
        """, unsafe_allow_html=True)

    # ========== TABS ==========
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚨 Ações Prioritárias",
        "📋 Checklist Semanal",
        "📊 Visão Geral",
        "📝 Notas e Registro"
    ])

    # ========== TAB 1: ACOES PRIORITARIAS ==========
    with tab1:
        st.header("🚨 Top 10 Ações Prioritárias")

        st.markdown("""
        Lista gerada automaticamente baseada em: **conformidade**, **qualidade de conteúdo**,
        **dias sem registro** e **tarefas atribuídas**. Foque nos críticos primeiro.
        """)

        top_acoes = [d for d in diagnosticos if d['prioridade'] >= 1][:10]

        if not top_acoes:
            st.success("Nenhuma ação prioritária no momento. Todos os professores estão OK!")
        else:
            for i, diag in enumerate(top_acoes, 1):
                prioridade_cor = {3: '#E53935', 2: '#F57C00', 1: '#FBC02D'}
                prioridade_label = {3: 'CRÍTICO', 2: 'URGENTE', 1: 'ATENÇÃO'}
                prioridade_emoji = {3: '🔴', 2: '🟠', 1: '🟡'}

                cor = prioridade_cor.get(diag['prioridade'], '#9E9E9E')
                label = prioridade_label.get(diag['prioridade'], 'INFO')
                emoji = prioridade_emoji.get(diag['prioridade'], 'ℹ️')

                acao = gerar_acao_recomendada(diag)

                # Monta lista de alertas
                alertas_html = ''.join(
                    f'<li style="color: #555;">{a[1]}</li>' for a in diag['alertas']
                )

                # Check se ja foi marcado como resolvido
                acao_key = f"{diag['unidade']}_{diag['professor']}_sem{semana}"
                resolvido = acoes_salvas.get(acao_key, {}).get('resolvido', False)
                opacidade = '0.5' if resolvido else '1'

                st.markdown(f"""
                <div style="background: white; border-left: 5px solid {cor}; padding: 15px; margin: 8px 0; border-radius: 5px; opacity: {opacidade}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="background: {cor}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; font-weight: bold;">{label}</span>
                            <strong style="margin-left: 10px; font-size: 1.1em;">{emoji} #{i} - {diag['professor']}</strong>
                            <span style="color: #666; margin-left: 10px;">({diag['unidade']} | {diag['series']})</span>
                        </div>
                        <div style="text-align: right; color: #666;">
                            <small>Conformidade: {diag['conformidade']:.0f}% | Aulas: {diag['total_aulas']}</small>
                        </div>
                    </div>
                    <p style="margin: 8px 0 5px 0; font-weight: bold; color: #333;">➡️ {acao}</p>
                    <ul style="margin: 5px 0; padding-left: 20px;">{alertas_html}</ul>
                </div>
                """, unsafe_allow_html=True)

                # Botao para marcar como resolvido
                col_acao1, col_acao2 = st.columns([4, 1])
                with col_acao2:
                    if st.checkbox("Resolvido", value=resolvido, key=f"check_{acao_key}"):
                        if not resolvido:
                            acoes_salvas[acao_key] = {
                                'resolvido': True,
                                'data': hoje.strftime('%Y-%m-%d'),
                                'professor': diag['professor'],
                            }
                            salvar_acoes(acoes_salvas)

    # ========== TAB 2: CHECKLIST SEMANAL ==========
    with tab2:
        st.header(f"📋 Checklist - Semana {semana}")

        st.markdown("""
        Checklist automático para acompanhamento semanal da coordenação.
        Marque os itens conforme for completando.
        """)

        checklist_key = f"checklist_sem{semana}"
        checklist_salvo = acoes_salvas.get(checklist_key, {})

        items = [
            ("verificar_registros", "Verificar se todos os professores registraram aulas da semana"),
            ("contatar_ausentes", f"Contatar professores sem registro há mais de 3 dias"),
            ("revisar_conteudo", "Revisar qualidade dos conteúdos registrados (amostrar 5 professores)"),
            ("conferir_progressao", f"Conferir se professores estão no capítulo {cap_esperado} ou próximo"),
            ("verificar_tarefas", "Verificar se tarefas estão sendo atribuídas regularmente"),
            ("preparar_resumo", "Preparar resumo semanal para reunião de quinta-feira"),
            ("agendar_feedbacks", "Verificar feedbacks pendentes e agendar próximos"),
        ]

        # Adicionar items especificos do trimestre
        if semana in (7, 8):
            items.append(("verificar_a1", "Verificar aplicação das avaliações A1.1-A1.4"))
        elif semana in (11, 12):
            items.append(("verificar_a2", "Verificar aplicação das avaliações A1.5-A2"))
        elif semana in (13, 14):
            items.append(("verificar_simulado", "Verificar aplicação do Simulado + Recuperação"))

        for item_key, item_text in items:
            checked = checklist_salvo.get(item_key, False)
            new_val = st.checkbox(item_text, value=checked, key=f"cl_{item_key}")
            if new_val != checked:
                if checklist_key not in acoes_salvas:
                    acoes_salvas[checklist_key] = {}
                acoes_salvas[checklist_key][item_key] = new_val
                salvar_acoes(acoes_salvas)

        # Progresso
        total_items = len(items)
        done_items = sum(1 for k, _ in items if checklist_salvo.get(k, False))
        pct_done = (done_items / total_items * 100) if total_items > 0 else 0

        st.progress(pct_done / 100)
        st.caption(f"{done_items}/{total_items} itens completados ({pct_done:.0f}%)")

        # Eventos da semana
        st.markdown("---")
        st.subheader("📅 Eventos desta Semana")

        eventos = []
        if semana in (7, 8):
            eventos.append("📝 Semana de Avaliações A1.1-A1.4")
        if semana in (11, 12):
            eventos.append("📝 Semana de Avaliações A1.5-A2")
        if semana in (13, 14):
            eventos.append("📋 Simulado + Recuperação 1o Trimestre")
        if semana % 4 == 0:
            eventos.append("📊 Reunião mensal de coordenação")

        if hoje.weekday() == DIA_REUNIAO_SEMANAL:  # Quinta-feira
            eventos.append("🗓️ Reunião semanal de acompanhamento (hoje)")
        elif hoje.weekday() < DIA_REUNIAO_SEMANAL:
            dias_quinta = DIA_REUNIAO_SEMANAL - hoje.weekday()
            eventos.append(f"🗓️ Reunião semanal em {dias_quinta} dia(s)")

        if eventos:
            for ev in eventos:
                st.markdown(f"- {ev}")
        else:
            st.info("Semana regular, sem eventos especiais.")

    # ========== TAB 3: VISAO GERAL ==========
    with tab3:
        st.header("📊 Visão Geral - Todos os Professores")

        # Tabela completa
        dados_tabela = []
        for diag in diagnosticos:
            prioridade_emoji = {3: '🔴', 2: '🟠', 1: '🟡', 0: '🟢'}
            dados_tabela.append({
                'Status': prioridade_emoji.get(diag['prioridade'], '⚪'),
                'Professor': diag['professor'],
                'Unidade': diag['unidade'],
                'Séries': diag['series'],
                'Aulas': diag['total_aulas'],
                'Conformidade': f"{diag['conformidade']:.0f}%",
                '% Vazio': f"{diag['pct_vazio']:.0f}%",
                'Alertas': len(diag['alertas']),
            })

        df_tabela = pd.DataFrame(dados_tabela)

        # Filtro de prioridade
        filtro_prio = st.radio("Filtrar:", ['Todos', 'Críticos', 'Urgentes', 'Atenção', 'OK'], horizontal=True)

        if filtro_prio == 'Críticos':
            df_tabela = df_tabela[df_tabela['Status'] == '🔴']
        elif filtro_prio == 'Urgentes':
            df_tabela = df_tabela[df_tabela['Status'] == '🟠']
        elif filtro_prio == 'Atenção':
            df_tabela = df_tabela[df_tabela['Status'] == '🟡']
        elif filtro_prio == 'OK':
            df_tabela = df_tabela[df_tabela['Status'] == '🟢']

        st.dataframe(df_tabela, use_container_width=True, hide_index=True, height=500)

        # Distribuicao de prioridades
        st.subheader("Distribuição de Prioridades")

        prio_counts = pd.DataFrame({
            'Prioridade': ['Crítico', 'Urgente', 'Atenção', 'OK'],
            'Quantidade': [criticos, urgentes, atencao, ok],
            'Cor': ['#E53935', '#F57C00', '#FBC02D', '#43A047'],
        })

        fig = px.bar(prio_counts, x='Prioridade', y='Quantidade',
                    color='Prioridade',
                    color_discrete_map={
                        'Crítico': '#E53935', 'Urgente': '#F57C00',
                        'Atenção': '#FBC02D', 'OK': '#43A047'
                    },
                    title='Professores por Nível de Prioridade')
        st.plotly_chart(fig, use_container_width=True)

        # Scatter: Conformidade vs % Vazio
        st.subheader("Conformidade vs Qualidade de Conteúdo")

        scatter_data = pd.DataFrame([{
            'Professor': d['professor'],
            'Unidade': d['unidade'],
            'Conformidade': d['conformidade'],
            'Pct Vazio': d['pct_vazio'],
            'Prioridade': {3: 'Crítico', 2: 'Urgente', 1: 'Atenção', 0: 'OK'}[d['prioridade']],
        } for d in diagnosticos])

        fig = px.scatter(
            scatter_data, x='Conformidade', y='Pct Vazio',
            color='Unidade', color_discrete_map=CORES_UNIDADES,
            hover_data=['Professor', 'Prioridade'],
            title='Conformidade (%) vs Registros Vazios (%)',
            labels={'Pct Vazio': '% Registros Vazios', 'Conformidade': '% Conformidade'},
        )
        fig.add_hline(y=CONTEUDO_VAZIO_ALERTA, line_dash="dash", line_color="red", annotation_text=f"Limite {CONTEUDO_VAZIO_ALERTA}% vazios")
        fig.add_vline(x=CONFORMIDADE_META, line_dash="dash", line_color="green", annotation_text=f"Meta {CONFORMIDADE_META}%")
        st.plotly_chart(fig, use_container_width=True)

    # ========== TAB 4: NOTAS E REGISTRO ==========
    with tab4:
        st.header("📝 Notas da Coordenação")

        st.markdown("""
        Registre observações, decisões e acompanhamentos da semana.
        Estas notas ficam salvas e podem ser consultadas depois.
        """)

        nota_key = f"notas_sem{semana}"
        notas_atuais = acoes_salvas.get(nota_key, {})

        # Notas da semana
        nota_texto = st.text_area(
            f"Notas - Semana {semana}:",
            value=notas_atuais.get('texto', ''),
            height=200,
            placeholder="Registre aqui suas observações da semana...\n\nExemplo:\n- Conversei com Prof. X sobre registro de conteúdo\n- Agendar feedback com Prof. Y\n- Turma Z precisa de atenção especial em Matemática"
        )

        if st.button("💾 Salvar Notas", type="primary"):
            acoes_salvas[nota_key] = {
                'texto': nota_texto,
                'data': hoje.strftime('%Y-%m-%d'),
            }
            salvar_acoes(acoes_salvas)
            st.success("Notas salvas!")

        # Historico de notas
        st.markdown("---")
        st.subheader("📚 Histórico de Notas")

        notas_anteriores = []
        for k, v in sorted(acoes_salvas.items(), reverse=True):
            if k.startswith('notas_sem') and v.get('texto'):
                sem_num = k.replace('notas_sem', '')
                notas_anteriores.append({
                    'semana': sem_num,
                    'data': v.get('data', ''),
                    'texto': v['texto'],
                })

        if notas_anteriores:
            for nota in notas_anteriores[:5]:
                with st.expander(f"Semana {nota['semana']} ({nota['data']})"):
                    st.markdown(nota['texto'])
        else:
            st.info("Nenhuma nota anterior registrada.")

        # Exportar relatorio semanal
        st.markdown("---")
        st.subheader("📄 Exportar Relatório Semanal")

        if st.button("Gerar Relatório"):
            relatorio = f"""
================================================================================
      RELATÓRIO SEMANAL DA COORDENAÇÃO - COLÉGIO ELO 2026
================================================================================

Semana Letiva: {semana}a | {trimestre}o Trimestre
Capítulo Esperado: {cap_esperado}/12
Data: {hoje.strftime('%d/%m/%Y')}

================================================================================
                         RESUMO DE PRIORIDADES
================================================================================

Professores Críticos: {criticos}
Professores Urgentes: {urgentes}
Professores Atenção:  {atencao}
Professores OK:       {ok}
Total:                {len(diagnosticos)}

================================================================================
                    TOP AÇÕES PRIORITÁRIAS
================================================================================
"""
            for i, diag in enumerate([d for d in diagnosticos if d['prioridade'] >= 2][:5], 1):
                acao = gerar_acao_recomendada(diag)
                relatorio += f"\n{i}. [{diag['unidade']}] {acao}"
                for a in diag['alertas']:
                    relatorio += f"\n   - {a[1]}"

            relatorio += f"""

================================================================================
                      NOTAS DA SEMANA
================================================================================
{nota_texto or '(nenhuma nota registrada)'}

================================================================================
"""

            st.download_button(
                "📥 Baixar Relatório (TXT)",
                relatorio,
                f"relatorio_semana_{semana}.txt",
                "text/plain"
            )


main()
