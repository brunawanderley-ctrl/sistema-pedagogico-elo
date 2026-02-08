#!/usr/bin/env python3
"""
PÁGINA 12: AGENDA DA COORDENAÇÃO
Acompanhamento de professores, observação de aulas e feedback
Com gestão por coordenador e deadlines bimestrais
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import math
import json
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import DATA_DIR, is_cloud, ultima_atualizacao, calcular_semana_letiva, calcular_capitulo_esperado, carregar_fato_aulas

st.set_page_config(page_title="Agenda Coordenacao", page_icon="📋", layout="wide")
from auth import check_password, logout_button
if not check_password():
    st.stop()
logout_button()

# ========== SIDEBAR: ATUALIZAÇÃO DE DADOS (topo) ==========
with st.sidebar:
    st.subheader("Atualizar Dados")
    st.caption(f"Ultima atualizacao: {ultima_atualizacao()}")

    if not is_cloud():
        if st.button("Atualizar Diario de Classe", type="primary", key="btn_atualizar_agenda"):
            _script_dir = Path(__file__).parent.parent
            _script_path = _script_dir / "atualizar_siga.py"
            with st.spinner("Atualizando dados do SIGA..."):
                _result = subprocess.run(
                    ["python3", str(_script_path)],
                    capture_output=True, text=True, timeout=300,
                    cwd=str(_script_dir),
                )
            if _result.returncode == 0:
                st.success("Dados atualizados com sucesso!")
                st.rerun()
            else:
                st.error("Erro na atualizacao:")
                st.code(_result.stderr or _result.stdout, language="text")
    else:
        st.info("Atualizacao de dados disponivel apenas localmente.")
    st.markdown("---")

st.markdown("""
<style>
    .agenda-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
    }
    .deadline-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .progress-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .feedback-pendente {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .feedback-realizado {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .observacao-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .alerta-deadline {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    @media print {
        .no-print { display: none; }
    }
</style>
""", unsafe_allow_html=True)

FEEDBACK_FILE = DATA_DIR / "feedbacks_coordenacao.json"
CONFIG_FILE = DATA_DIR / "config_coordenadores.json"

def carregar_config():
    """Carrega configuração de coordenadores."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"coordenadores": [], "periodos_feedback": []}

def salvar_config(config):
    """Salva configuração de coordenadores."""
    config['atualizado_em'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def carregar_feedbacks():
    """Carrega feedbacks salvos."""
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_feedbacks(feedbacks):
    """Salva feedbacks."""
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(feedbacks, f, ensure_ascii=False, indent=2)

def get_bimestre_atual(hoje):
    """Retorna o bimestre atual e info."""
    config = carregar_config()
    periodos = config.get('periodos_feedback', [])

    for periodo in periodos:
        inicio = datetime.strptime(periodo['inicio'], '%Y-%m-%d')
        fim = datetime.strptime(periodo['fim'], '%Y-%m-%d')
        if inicio <= hoje <= fim:
            return periodo

    # Se não encontrou, retorna o primeiro
    if periodos:
        return periodos[0]
    return {
        "bimestre": 1,
        "nome": "1º Bimestre",
        "inicio": "2026-01-26",
        "fim": "2026-03-31",
        "deadline_feedback": "2026-04-10"
    }

def filtrar_series(serie_texto, series_coordenador):
    """Verifica se a série está na lista do coordenador."""
    for s in series_coordenador:
        if s.lower() in serie_texto.lower():
            return True
        # Trata variações
        if "6" in s and "6" in serie_texto:
            return True
        if "7" in s and "7" in serie_texto:
            return True
        if "8" in s and "8" in serie_texto:
            return True
        if "9" in s and "9" in serie_texto:
            return True
        if "1ª" in s and ("1ª" in serie_texto or "1a" in serie_texto.lower()):
            return True
        if "2ª" in s and ("2ª" in serie_texto or "2a" in serie_texto.lower()):
            return True
        if "3ª" in s and ("3ª" in serie_texto or "3a" in serie_texto.lower()):
            return True
    return False

def main():
    st.title("📋 Agenda da Coordenação Pedagógica")

    # Carrega configurações
    config = carregar_config()
    feedbacks = carregar_feedbacks()

    # Define "hoje"
    hoje = datetime.now()
    if hoje.year < 2026:
        hoje = datetime(2026, 2, 5)

    bimestre_info = get_bimestre_atual(hoje)
    deadline = datetime.strptime(bimestre_info['deadline_feedback'], '%Y-%m-%d')
    dias_restantes = (deadline - hoje).days

    # ========== INTRODUÇÃO E PROTOCOLO ==========
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0 0 15px 0; border: none;">🎯 Protocolo de Acompanhamento Pedagógico</h2>
        <p style="font-size: 1.1em; margin-bottom: 15px;">
            Como coordenador(a) pedagógico(a), você tem duas responsabilidades principais com cada professor sob sua supervisão:
        </p>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                <h3 style="color: #90caf9; margin: 0;">🔍 1. Observação de Aula</h3>
                <p style="margin: 10px 0 0 0;">Assistir pelo menos <strong>1 aula completa</strong> de cada professor a cada <strong>2 meses</strong> (bimestre).</p>
            </div>
            <div style="flex: 1; min-width: 200px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                <h3 style="color: #a5d6a7; margin: 0;">💬 2. Reunião de Feedback</h3>
                <p style="margin: 10px 0 0 0;">Realizar <strong>1 reunião individual</strong> com cada professor a cada <strong>2 meses</strong> para dar feedback sobre a observação.</p>
            </div>
        </div>
        <p style="margin-top: 15px; font-style: italic; opacity: 0.9;">
            📌 Meta anual: <strong>4 observações + 4 feedbacks</strong> por professor (1 por bimestre)
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ========== QUADRO VISUAL DE PRAZO ==========
    cor_alerta = "#c62828" if dias_restantes <= 7 else ("#ff9800" if dias_restantes <= 14 else "#43a047")
    emoji_alerta = "🚨" if dias_restantes <= 7 else ("⚠️" if dias_restantes <= 14 else "✅")

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {cor_alerta}dd 0%, {cor_alerta} 100%); color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
            <div>
                <h3 style="color: white; margin: 0; opacity: 0.9;">{emoji_alerta} PRAZO ATUAL</h3>
                <p style="font-size: 2.5em; font-weight: bold; margin: 5px 0;">{dias_restantes} dias</p>
                <p style="margin: 0;">até o deadline</p>
            </div>
            <div style="border-left: 2px solid rgba(255,255,255,0.3); padding-left: 20px;">
                <p style="margin: 0; opacity: 0.9;">📅 Período de Análise</p>
                <p style="font-size: 1.3em; font-weight: bold; margin: 5px 0;">{bimestre_info['nome']}</p>
                <p style="margin: 0;">{bimestre_info['inicio']} a {bimestre_info['fim']}</p>
            </div>
            <div style="border-left: 2px solid rgba(255,255,255,0.3); padding-left: 20px;">
                <p style="margin: 0; opacity: 0.9;">⏰ Deadline para Feedbacks</p>
                <p style="font-size: 1.3em; font-weight: bold; margin: 5px 0;">{deadline.strftime('%d/%m/%Y')}</p>
                <p style="margin: 0;">Todos os feedbacks devem estar registrados</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mensagem de alerta se próximo do deadline
    if dias_restantes <= 7:
        st.error(f"🚨 **URGENTE:** Faltam apenas {dias_restantes} dias para o deadline! Finalize todos os feedbacks pendentes.")
    elif dias_restantes <= 14:
        st.warning(f"⚠️ **ATENÇÃO:** O deadline está próximo ({dias_restantes} dias). Verifique seus feedbacks pendentes.")

    st.markdown("---")

    # Carrega dados
    df_aulas = carregar_fato_aulas()

    if df_aulas.empty:
        st.error("Dados nao carregados. Execute a extracao do SIGA primeiro.")
        return

    df_aulas = df_aulas[df_aulas['data'] <= hoje].copy()

    semana_atual = calcular_semana_letiva(hoje)
    capitulo_esperado = calcular_capitulo_esperado(semana_atual)

    # ========== SELEÇÃO INICIAL: UNIDADE E COORDENADOR ==========
    st.markdown("---")

    col_sel1, col_sel2, col_sel3 = st.columns(3)

    with col_sel1:
        unidades = sorted(df_aulas['unidade'].dropna().unique())
        opcoes_unidade = ["TODAS"] + unidades
        unidade_sel = st.selectbox("🏫 Unidade:", opcoes_unidade, key='un_principal')

    # Filtra coordenadores da unidade (ou todos)
    if unidade_sel == "TODAS":
        coordenadores_un = config.get('coordenadores', [])
    else:
        coordenadores_un = [c for c in config.get('coordenadores', []) if c['unidade'] == unidade_sel]

    nomes_coord = [f"{c['nome']} ({c['unidade']})" if unidade_sel == "TODAS" else c['nome'] for c in coordenadores_un]

    with col_sel2:
        if nomes_coord:
            opcoes_coord = ["TODOS"] + nomes_coord
            coord_sel = st.selectbox("👤 Coordenador(a):", opcoes_coord)

            if coord_sel == "TODOS":
                coord_info = {
                    'nome': 'TODOS',
                    'unidade': unidade_sel,
                    'series': ["6º Ano", "7º Ano", "8º Ano", "9º Ano", "1ª Série", "2ª Série", "3ª Série"]
                }
            else:
                # Remove o sufixo (unidade) se existir
                coord_nome = coord_sel.split(" (")[0] if " (" in coord_sel else coord_sel
                coord_info = next((c for c in coordenadores_un if c['nome'] == coord_nome), None)
        else:
            st.warning("Nenhum coordenador cadastrado")
            coord_sel = None
            coord_info = None

    with col_sel3:
        if coord_info:
            if coord_sel == "TODOS" and unidade_sel == "TODAS":
                st.info(f"📚 Visualizando: Todas as unidades e séries")
            elif coord_sel == "TODOS":
                st.info(f"📚 Visualizando: Todas as séries de {unidade_sel}")
            else:
                st.info(f"📚 Séries: {', '.join(coord_info['series'])}")

    # ========== DASHBOARD INICIAL COM MÉTRICAS ==========
    st.markdown("---")

    # Cards de período e deadline
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)

    with col_d1:
        st.markdown(f"""
        <div class="agenda-card">
            <h3 style="color: white; margin: 0;">📅 {bimestre_info['nome']}</h3>
            <p style="margin: 5px 0;">Período de Análise</p>
            <small>{bimestre_info['inicio']} a {bimestre_info['fim']}</small>
        </div>
        """, unsafe_allow_html=True)

    with col_d2:
        cor_deadline = "alerta-deadline" if dias_restantes <= 7 else "deadline-card"
        st.markdown(f"""
        <div class="{'deadline-card' if dias_restantes > 7 else 'alerta-deadline'}">
            <h3 style="{'color: white;' if dias_restantes > 7 else 'color: #c62828;'} margin: 0;">⏰ Deadline</h3>
            <p style="margin: 5px 0; font-size: 1.5em; font-weight: bold;">{deadline.strftime('%d/%m/%Y')}</p>
            <small>{dias_restantes} dias restantes</small>
        </div>
        """, unsafe_allow_html=True)

    # Calcula progresso de feedbacks
    if coord_info:
        # Filtra por unidade (ou todas)
        if unidade_sel == "TODAS":
            df_coord = df_aulas.copy()
        else:
            df_coord = df_aulas[df_aulas['unidade'] == unidade_sel].copy()

        # Filtra por séries do coordenador
        df_coord = df_coord[df_coord['serie'].apply(lambda x: filtrar_series(str(x), coord_info['series']) if pd.notna(x) else False)]
        professores_coord = df_coord['professor'].dropna().unique()
        total_profs = len(professores_coord)

        # Conta feedbacks realizados
        feedbacks_realizados = 0
        for prof in professores_coord:
            # Se TODAS unidades, precisa verificar em qual unidade o professor está
            if unidade_sel == "TODAS":
                prof_un = df_aulas[df_aulas['professor'] == prof]['unidade'].iloc[0] if len(df_aulas[df_aulas['professor'] == prof]) > 0 else ""
                prof_key = f"{prof_un}_{prof}_{bimestre_info['bimestre']}"
            else:
                prof_key = f"{unidade_sel}_{prof}_{bimestre_info['bimestre']}"

            if prof_key in feedbacks and feedbacks[prof_key].get('feedback_realizado'):
                feedbacks_realizados += 1

        pct_completo = (feedbacks_realizados / total_profs * 100) if total_profs > 0 else 0

        with col_d3:
            st.markdown(f"""
            <div class="progress-card">
                <h3 style="color: white; margin: 0;">📊 Progresso</h3>
                <p style="margin: 5px 0; font-size: 2em; font-weight: bold;">{pct_completo:.0f}%</p>
                <small>{feedbacks_realizados}/{total_profs} feedbacks</small>
            </div>
            """, unsafe_allow_html=True)

        with col_d4:
            st.metric("👨‍🏫 Professores", total_profs)
            st.metric("📚 Capítulo Esperado", f"{capitulo_esperado}/12")

        # Se "TODOS" selecionado, mostra resumo por coordenador
        if coord_sel == "TODOS" and len(coordenadores_un) > 0:
            st.markdown("---")
            if unidade_sel == "TODAS":
                st.subheader("📊 Resumo por Coordenador - Todas as Unidades")
            else:
                st.subheader(f"📊 Resumo por Coordenador - {unidade_sel}")

            # Agrupa por unidade se "TODAS" selecionado
            if unidade_sel == "TODAS":
                for un in unidades:
                    coords_un = [c for c in coordenadores_un if c['unidade'] == un]
                    if coords_un:
                        st.markdown(f"**🏫 {un}**")
                        cols_coord = st.columns(len(coords_un))
                        for i, c in enumerate(coords_un):
                            df_c = df_aulas[df_aulas['unidade'] == un].copy()
                            df_c = df_c[df_c['serie'].apply(lambda x: filtrar_series(str(x), c['series']) if pd.notna(x) else False)]
                            profs_c = df_c['professor'].dropna().unique()
                            total_c = len(profs_c)

                            fb_done_c = 0
                            for p in profs_c:
                                pk = f"{un}_{p}_{bimestre_info['bimestre']}"
                                if pk in feedbacks and feedbacks[pk].get('feedback_realizado'):
                                    fb_done_c += 1

                            pct_c = (fb_done_c / total_c * 100) if total_c > 0 else 0
                            status_c = "✅" if pct_c >= 100 else ("🟡" if pct_c >= 50 else "🔴")

                            with cols_coord[i]:
                                st.markdown(f"""
                                <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px;">
                                    <p style="margin: 0; font-weight: bold;">{c['nome']}</p>
                                    <p style="font-size: 1.5em; margin: 5px 0;">{status_c} {pct_c:.0f}%</p>
                                    <small>{fb_done_c}/{total_c} feedbacks</small><br>
                                    <small style="color: #666;">{', '.join(c['series'])}</small>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                cols_coord = st.columns(len(coordenadores_un))
                for i, c in enumerate(coordenadores_un):
                    df_c = df_aulas[df_aulas['unidade'] == unidade_sel].copy()
                    df_c = df_c[df_c['serie'].apply(lambda x: filtrar_series(str(x), c['series']) if pd.notna(x) else False)]
                    profs_c = df_c['professor'].dropna().unique()
                    total_c = len(profs_c)

                    fb_done_c = 0
                    for p in profs_c:
                        pk = f"{unidade_sel}_{p}_{bimestre_info['bimestre']}"
                        if pk in feedbacks and feedbacks[pk].get('feedback_realizado'):
                            fb_done_c += 1

                    pct_c = (fb_done_c / total_c * 100) if total_c > 0 else 0
                    status_c = "✅" if pct_c >= 100 else ("🟡" if pct_c >= 50 else "🔴")

                    with cols_coord[i]:
                        st.markdown(f"""
                        <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; text-align: center;">
                            <p style="margin: 0; font-weight: bold;">{c['nome']}</p>
                            <p style="font-size: 1.5em; margin: 5px 0;">{status_c} {pct_c:.0f}%</p>
                            <small>{fb_done_c}/{total_c} feedbacks</small><br>
                            <small style="color: #666;">{', '.join(c['series'])}</small>
                        </div>
                        """, unsafe_allow_html=True)

    else:
        with col_d3:
            st.info("Selecione um coordenador")
        with col_d4:
            st.metric("📅 Semana", f"{semana_atual}ª")

    # ========== TABS ==========
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Meus Professores",
        "👨‍🏫 Detalhamento",
        "📝 Registrar Feedback",
        "📅 Agenda Completa",
        "⚙️ Configurações"
    ])

    # ========== TAB 1: MEUS PROFESSORES ==========
    with tab1:
        if coord_sel == "TODOS" and unidade_sel == "TODAS":
            st.header("📊 Todos os Professores - Todas as Unidades")
        elif coord_sel == "TODOS":
            st.header(f"📊 Todos os Professores - {unidade_sel}")
        else:
            st.header(f"📊 Professores - {coord_sel if coord_sel else 'Selecione coordenador'}")

        if coord_info:
            # Lista professores do coordenador
            resumo_profs = []
            for prof in sorted(professores_coord):
                df_prof = df_coord[df_coord['professor'] == prof]
                aulas_registradas = len(df_prof)

                # Unidade do professor
                prof_unidade = df_prof['unidade'].iloc[0] if len(df_prof) > 0 else '-'

                # Último conteúdo
                conteudos = df_prof[df_prof['conteudo'].notna()]['conteudo']
                ultimo_conteudo = str(conteudos.iloc[-1])[:40] + '...' if len(conteudos) > 0 else '-'

                # Status do feedback
                prof_key = f"{prof_unidade}_{prof}_{bimestre_info['bimestre']}"
                fb_info = feedbacks.get(prof_key, {})
                status_obs = '✅' if fb_info.get('observacao_realizada') else '⏳'
                status_fb = '✅' if fb_info.get('feedback_realizado') else '⏳'

                dados_prof = {
                    'Professor': prof,
                    'Séries': ', '.join(df_prof['serie'].dropna().unique())[:25],
                    'Aulas': aulas_registradas,
                    'Último Conteúdo': ultimo_conteudo,
                    'Observação': status_obs,
                    'Feedback': status_fb
                }

                # Adiciona coluna de unidade se "TODAS" selecionado
                if unidade_sel == "TODAS":
                    dados_prof = {'Unidade': prof_unidade, **dados_prof}

                resumo_profs.append(dados_prof)

            df_resumo = pd.DataFrame(resumo_profs)

            # Filtro de status
            filtro_status = st.radio("Filtrar:", ['Todos', 'Pendentes', 'Concluídos'], horizontal=True)

            if filtro_status == 'Pendentes':
                df_resumo = df_resumo[(df_resumo['Observação'] == '⏳') | (df_resumo['Feedback'] == '⏳')]
            elif filtro_status == 'Concluídos':
                df_resumo = df_resumo[(df_resumo['Observação'] == '✅') & (df_resumo['Feedback'] == '✅')]

            st.dataframe(df_resumo, use_container_width=True, hide_index=True)

            # Alerta de pendências
            pendentes = len(df_resumo[(df_resumo['Feedback'] == '⏳')])
            if pendentes > 0 and dias_restantes <= 14:
                st.markdown(f"""
                <div class="alerta-deadline">
                    <strong>⚠️ ATENÇÃO:</strong> {pendentes} feedbacks pendentes e apenas {dias_restantes} dias até o deadline!
                </div>
                """, unsafe_allow_html=True)

        else:
            st.warning("Selecione uma unidade e coordenador para ver os professores.")

    # ========== TAB 2: DETALHAMENTO ==========
    with tab2:
        st.header("👨‍🏫 Detalhamento do Professor")

        if coord_info and len(professores_coord) > 0:
            prof_det = st.selectbox("Selecione o professor:", sorted(professores_coord), key='prof_det')

            if prof_det:
                df_prof = df_coord[df_coord['professor'] == prof_det]

                # Encontra o coordenador responsável por este professor (pelas séries)
                coord_responsavel = coord_sel
                if coord_sel == "TODOS":
                    series_prof = df_prof['serie'].dropna().unique()
                    for c in coordenadores_un:
                        for s in series_prof:
                            if filtrar_series(str(s), c['series']):
                                coord_responsavel = c['nome']
                                break

                # Card do professor
                st.markdown(f"""
                <div class="agenda-card">
                    <h2 style="color: white; margin: 0;">{prof_det}</h2>
                    <p>Coordenador(a): {coord_responsavel} | Aulas: {len(df_prof)}</p>
                    <p>Séries: {', '.join(df_prof['serie'].dropna().unique())}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("---")

                # Conteúdos e tarefas
                st.subheader("📝 Conteúdos e Tarefas Registrados")

                df_conteudos = df_prof[['data', 'disciplina', 'turma', 'conteudo', 'tarefa']].copy()
                df_conteudos = df_conteudos[df_conteudos['conteudo'].notna() | df_conteudos['tarefa'].notna()]
                df_conteudos = df_conteudos.sort_values('data', ascending=False)
                df_conteudos['data'] = df_conteudos['data'].dt.strftime('%d/%m/%Y')

                if len(df_conteudos) > 0:
                    st.dataframe(df_conteudos, use_container_width=True, hide_index=True, height=300)
                else:
                    st.warning("Nenhum conteúdo registrado.")

                # Material para impressão
                st.markdown("---")
                st.subheader("🖨️ Material para Feedback")

                material = f"""
================================================================================
           RELATÓRIO PARA REUNIÃO DE FEEDBACK - COLÉGIO ELO 2026
================================================================================

PROFESSOR: {prof_det}
COORDENADOR(A): {coord_responsavel}
UNIDADE: {unidade_sel}
PERÍODO: {bimestre_info['nome']} ({bimestre_info['inicio']} a {bimestre_info['fim']})
DEADLINE: {bimestre_info['deadline_feedback']}

--------------------------------------------------------------------------------
                         SITUAÇÃO ATUAL
--------------------------------------------------------------------------------

Semana Letiva: {semana_atual}ª
Capítulo Esperado: {capitulo_esperado} de 12
Aulas Registradas: {len(df_prof)}
Aulas com Conteúdo: {len(df_prof[df_prof['conteudo'].notna()])}

--------------------------------------------------------------------------------
                    ÚLTIMOS CONTEÚDOS REGISTRADOS
--------------------------------------------------------------------------------
"""
                ultimos = df_prof[df_prof['conteudo'].notna()].tail(10)
                for _, row in ultimos.iterrows():
                    data_str = row['data'].strftime('%d/%m') if pd.notna(row['data']) else '-'
                    conteudo_str = str(row['conteudo'])[:60] if pd.notna(row['conteudo']) else '-'
                    material += f"\n{data_str}: {conteudo_str}"

                material += f"""

--------------------------------------------------------------------------------
                    CHECKLIST DE FEEDBACK
--------------------------------------------------------------------------------

[ ] Progressão está de acordo com capítulo {capitulo_esperado}?
[ ] Conteúdos detalhados?
[ ] Tarefas atribuídas?
[ ] Dificuldades com turmas?

--------------------------------------------------------------------------------
                       REGISTRO
--------------------------------------------------------------------------------

Data Observação: ___/___/______
Data Feedback: ___/___/______

Notas:
_______________________________________________________________________________
_______________________________________________________________________________

Assinaturas:
Coordenação: _________________________
Professor: ___________________________

================================================================================
"""

                st.download_button(
                    "📥 Baixar Material (TXT)",
                    material,
                    f"feedback_{prof_det.replace(' ', '_')}_{bimestre_info['bimestre']}bim.txt",
                    "text/plain"
                )
        else:
            st.warning("Selecione coordenador para ver professores.")

    # ========== TAB 3: REGISTRAR FEEDBACK ==========
    with tab3:
        st.header("📝 Registrar Feedback")

        if coord_info and len(professores_coord) > 0:
            prof_fb = st.selectbox("Professor:", sorted(professores_coord), key='prof_fb')

            if prof_fb:
                # Encontra o coordenador responsável
                coord_responsavel = coord_sel
                if coord_sel == "TODOS":
                    df_prof_fb = df_coord[df_coord['professor'] == prof_fb]
                    series_prof = df_prof_fb['serie'].dropna().unique()
                    for c in coordenadores_un:
                        for s in series_prof:
                            if filtrar_series(str(s), c['series']):
                                coord_responsavel = c['nome']
                                break

                prof_key = f"{unidade_sel}_{prof_fb}_{bimestre_info['bimestre']}"
                fb_atual = feedbacks.get(prof_key, {})

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("🔍 Observação de Aula")
                    obs_realizada = st.checkbox("Observação realizada", value=fb_atual.get('observacao_realizada', False))
                    data_obs = st.date_input("Data:", value=hoje, key='data_obs')
                    notas_obs = st.text_area("Notas:", value=fb_atual.get('notas_observacao', ''), height=100, key='notas_obs')

                with col2:
                    st.subheader("💬 Feedback")
                    fb_realizado = st.checkbox("Feedback realizado", value=fb_atual.get('feedback_realizado', False))
                    data_fb = st.date_input("Data:", value=hoje, key='data_fb')
                    notas_fb = st.text_area("Combinados:", value=fb_atual.get('notas_feedback', ''), height=100, key='notas_fb')

                st.markdown("---")

                col_av1, col_av2, col_av3 = st.columns(3)
                with col_av1:
                    aval_prog = st.selectbox("Progressão:", ['Adequada', 'Atenção', 'Crítica'],
                                            index=['Adequada', 'Atenção', 'Crítica'].index(fb_atual.get('aval_progressao', 'Adequada')))
                with col_av2:
                    aval_reg = st.selectbox("Registros:", ['Adequada', 'Atenção', 'Crítica'],
                                           index=['Adequada', 'Atenção', 'Crítica'].index(fb_atual.get('aval_registros', 'Adequada')))
                with col_av3:
                    aval_geral = st.selectbox("Geral:", ['Excelente', 'Bom', 'Regular', 'Precisa Melhorar'],
                                             index=['Excelente', 'Bom', 'Regular', 'Precisa Melhorar'].index(fb_atual.get('aval_geral', 'Bom')))

                if st.button("💾 Salvar", type="primary"):
                    feedbacks[prof_key] = {
                        'professor': prof_fb,
                        'coordenador': coord_responsavel,
                        'unidade': unidade_sel,
                        'bimestre': bimestre_info['bimestre'],
                        'observacao_realizada': obs_realizada,
                        'data_observacao': data_obs.strftime('%d/%m/%Y'),
                        'notas_observacao': notas_obs,
                        'feedback_realizado': fb_realizado,
                        'data_feedback': data_fb.strftime('%d/%m/%Y'),
                        'notas_feedback': notas_fb,
                        'aval_progressao': aval_prog,
                        'aval_registros': aval_reg,
                        'aval_geral': aval_geral,
                        'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M')
                    }
                    salvar_feedbacks(feedbacks)
                    st.success("✅ Salvo!")
                    st.rerun()
        else:
            st.warning("Selecione coordenador.")

    # ========== TAB 4: AGENDA COMPLETA ==========
    with tab4:
        st.header("📅 Visão Geral - Todos os Coordenadores")

        # Resumo por coordenador
        resumo_geral = []
        for coord in config.get('coordenadores', []):
            df_c = df_aulas[df_aulas['unidade'] == coord['unidade']].copy()
            df_c = df_c[df_c['serie'].apply(lambda x: filtrar_series(str(x), coord['series']) if pd.notna(x) else False)]
            profs = df_c['professor'].dropna().unique()
            total_p = len(profs)

            # Conta feedbacks
            fb_done = 0
            for p in profs:
                pk = f"{coord['unidade']}_{p}_{bimestre_info['bimestre']}"
                if pk in feedbacks and feedbacks[pk].get('feedback_realizado'):
                    fb_done += 1

            pct = (fb_done / total_p * 100) if total_p > 0 else 0

            resumo_geral.append({
                'Coordenador': coord['nome'],
                'Unidade': coord['unidade'],
                'Séries': ', '.join(coord['series']),
                'Professores': total_p,
                'Feedbacks': f"{fb_done}/{total_p}",
                'Progresso': f"{pct:.0f}%",
                'Status': '✅' if pct >= 100 else ('🟡' if pct >= 50 else '🔴')
            })

        df_geral = pd.DataFrame(resumo_geral)
        st.dataframe(df_geral, use_container_width=True, hide_index=True)

        # Gráfico de progresso
        st.subheader("📊 Progresso por Coordenador")
        df_geral['Pct'] = df_geral['Progresso'].str.replace('%', '').astype(float)

        import plotly.express as px
        fig = px.bar(df_geral, x='Coordenador', y='Pct', color='Unidade',
                    title=f'Progresso de Feedbacks - {bimestre_info["nome"]}')
        fig.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="Meta 100%")
        st.plotly_chart(fig, use_container_width=True)

    # ========== TAB 5: CONFIGURAÇÕES ==========
    with tab5:
        st.header("⚙️ Configuração de Coordenadores")

        st.markdown("""
        <div class="observacao-box">
            <strong>📝 Instruções:</strong> Edite os coordenadores e suas séries abaixo.
            Clique em "Salvar Configurações" após as alterações.
        </div>
        """, unsafe_allow_html=True)

        # Exibe configuração atual
        st.subheader("👥 Coordenadores Atuais")

        coords_atual = config.get('coordenadores', [])
        df_coords = pd.DataFrame(coords_atual) if coords_atual else pd.DataFrame(columns=['nome', 'unidade', 'series'])

        # Editor de dados
        edited_df = st.data_editor(
            df_coords,
            column_config={
                "nome": st.column_config.TextColumn("Nome do Coordenador", width="medium"),
                "unidade": st.column_config.SelectboxColumn("Unidade", options=["BV", "CD", "CDR", "JG"], width="small"),
                "series": st.column_config.ListColumn("Séries", width="large")
            },
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Adicionar novo coordenador (formulário simples)
        st.subheader("➕ Adicionar/Editar Coordenador")

        col1, col2 = st.columns(2)
        with col1:
            novo_nome = st.text_input("Nome:")
            nova_unidade = st.selectbox("Unidade:", ["BV", "CD", "CDR", "JG"], key='nova_un')

        with col2:
            series_options = ["6º Ano", "7º Ano", "8º Ano", "9º Ano", "1ª Série", "2ª Série", "3ª Série"]
            novas_series = st.multiselect("Séries:", series_options)

        if st.button("➕ Adicionar Coordenador"):
            if novo_nome and nova_unidade and novas_series:
                coords_atual.append({
                    "nome": novo_nome,
                    "unidade": nova_unidade,
                    "series": novas_series
                })
                config['coordenadores'] = coords_atual
                salvar_config(config)
                st.success(f"✅ {novo_nome} adicionado!")
                st.rerun()
            else:
                st.error("Preencha todos os campos.")

        st.markdown("---")

        # Salvar alterações do editor
        if st.button("💾 Salvar Todas as Configurações", type="primary"):
            # Converte de volta para lista de dicts
            novos_coords = edited_df.to_dict('records')
            config['coordenadores'] = novos_coords
            salvar_config(config)
            st.success("✅ Configurações salvas!")
            st.rerun()

        # Exibe última atualização
        st.caption(f"Última atualização: {config.get('atualizado_em', 'N/A')}")


if __name__ == "__main__":
    main()
