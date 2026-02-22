#!/usr/bin/env python3
"""
SISTEMA PEDAGOGICO INTEGRADO - COLEGIO ELO 2026
Plataforma Unificada: SIGA + SAE + PEEX Command Center

Entry point unico com st.navigation. Organiza paginas por secoes e role.
Substitui tanto o antigo Sistema_Pedagogico.py quanto o PEEX_Command_Center.py.

Uso:
    streamlit run Sistema_Pedagogico.py
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Sistema Pedagogico ELO 2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS unificado (merge de ambos apps)
st.markdown("""
<style>
    @media (max-width: 768px) {
        .stColumns > div { min-width: 100% !important; }
        .ceo-header, .briefing-header { padding: 16px !important; }
        .ceo-header h2, .briefing-header h2 { font-size: 1.3em !important; }
        .scorecard { padding: 12px !important; }
        .scorecard div[style*="font-size:2.2em"] { font-size: 1.6em !important; }
        .kpi-card { padding: 10px !important; }
        .kpi-value { font-size: 1.5em !important; }
        .missao-card-urgente, .missao-card-importante, .missao-card-monitorar { padding: 12px 14px !important; }
        button { min-height: 44px !important; }
    }
    .main > div { padding-top: 1rem; }
    h1 { color: #1a237e; text-align: center; }
    h2 { color: #303f9f; border-bottom: 2px solid #303f9f; padding-bottom: 8px; }
    h3 { color: #3f51b5; }
    .info-box {
        background: #e3f2fd; border-left: 4px solid #2196f3;
        padding: 15px; margin: 10px 0; border-radius: 4px;
    }
    .success-box {
        background: #e8f5e9; border-left: 4px solid #4caf50;
        padding: 15px; margin: 10px 0; border-radius: 4px;
    }
    .warning-box {
        background: #fff3e0; border-left: 4px solid #ff9800;
        padding: 15px; margin: 10px 0; border-radius: 4px;
    }
    .highlight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 25px; border-radius: 12px;
        text-align: center; margin: 10px 0;
    }
    .saude-card {
        padding: 20px; border-radius: 12px; text-align: center; margin: 5px 0;
        color: white; min-height: 120px;
    }
    .saude-verde { background: linear-gradient(135deg, #43A047, #66BB6A); }
    .saude-amarelo { background: linear-gradient(135deg, #F9A825, #FDD835); color: #333; }
    .saude-vermelho { background: linear-gradient(135deg, #E53935, #EF5350); }
</style>
""", unsafe_allow_html=True)

from auth import check_password, logout_button, get_user_role

if not check_password():
    st.stop()
logout_button()

role = get_user_role()

# ========== REGISTRO DE PAGINAS POR SECAO ==========

sections = {}

# Helper
def P(path, title, icon="📄"):
    return st.Page(path, title=title, icon=icon)


if role == 'ceo':
    sections["Painel"] = [
        P("app_pages/home.py", "Home", "🏠"),
        P("app_pages/onboarding.py", "Onboarding", "🎓"),
        P("app_pages/glossario.py", "Glossario", "📖"),
    ]
    sections["Acompanhamento"] = [
        P("app_pages/01_📊_Quadro_Gestão.py", "Quadro Gestao", "📊"),
        P("app_pages/02_🎯_Prioridades_da_Semana.py", "Prioridades SIGA", "🎯"),
        P("app_pages/13_🚦_Semáforo_Professor.py", "Semaforo Professor", "🚦"),
        P("app_pages/08_⚠️_Alertas_Conformidade.py", "Alertas Conformidade", "⚠️"),
        P("app_pages/14_🧠_Alertas_Inteligentes.py", "Alertas Inteligentes", "🧠"),
    ]
    sections["Professores"] = [
        P("app_pages/06_👨‍🏫_Visão_Professor.py", "Visao Professor", "👨‍🏫"),
        P("app_pages/11_🖨️_Material_Professor.py", "Material Professor", "🖨️"),
        P("peex_pages/08_meus_professores.py", "Meus Professores", "👥"),
        P("peex_pages/12_espelho_coordenador.py", "Espelho Coordenador", "🪞"),
        P("app_pages/25_💬_Devolutivas.py", "Devolutivas", "💬"),
    ]
    sections["Alunos"] = [
        P("app_pages/19_🎓_Painel_Aluno.py", "Painel Aluno", "🎓"),
        P("app_pages/20_📊_Frequência_Escolar.py", "Frequencia Escolar", "📊"),
        P("app_pages/23_🚨_Alerta_Precoce_ABC.py", "Alerta Precoce ABC", "🚨"),
        P("app_pages/22_📋_Ocorrências.py", "Ocorrencias", "📋"),
        P("peex_pages/09_meus_alunos.py", "Meus Alunos", "🎒"),
    ]
    sections["Curriculo e SAE"] = [
        P("app_pages/03_📚_Estrutura_Curricular.py", "Estrutura Curricular", "📚"),
        P("app_pages/04_📖_Material_SAE.py", "Material SAE", "📖"),
        P("app_pages/05_📈_Progressão_SAE.py", "Progressao SAE", "📈"),
        P("app_pages/24_🔗_Cruzamento_SIGA_SAE.py", "Cruzamento SIGA SAE", "🔗"),
        P("app_pages/16_🔬_Inteligência_Conteúdo.py", "Inteligencia Conteudo", "🔬"),
    ]
    sections["Inteligencia PEEX"] = [
        P("peex_pages/00_centro_inteligencia.py", "Centro de Inteligencia", "🧠"),
        P("peex_pages/preparador_reuniao.py", "Preparador de Reuniao", "🎤"),
        P("peex_pages/10_peex_adaptativo.py", "PEEX Adaptativo", "📋"),
        P("peex_pages/14_gerador_peex_rede.py", "Gerador Rede", "🌐"),
        P("peex_pages/02_simulador.py", "Simulador", "🔮"),
        P("peex_pages/propostas_concorrentes.py", "Arena de Propostas", "⚔️"),
        P("peex_pages/genealogia.py", "Genealogia da Proposta", "🌳"),
        P("peex_pages/calendario_peex.py", "Calendario PEEX", "📅"),
    ]
    sections["Reunioes PEEX"] = [
        P("peex_pages/15_gerador_peex_unidade.py", "Pauta Reuniao", "📃"),
        P("peex_pages/07_plano_acao.py", "Plano de Acao", "📝"),
    ]
    sections["Estrategia"] = [
        P("peex_pages/00_comando_ceo.py", "Comando CEO", "🏢"),
        P("peex_pages/03_scorecard_diretores.py", "Scorecard", "📊"),
        P("peex_pages/04_ranking_rede.py", "Rankings", "🏆"),
        P("peex_pages/05_memoria.py", "Memoria", "💉"),
        P("peex_pages/20_sinais_vitais.py", "Sinais Vitais", "💓"),
        P("peex_pages/21_escalacoes.py", "Escalacoes", "🔺"),
        P("peex_pages/22_compromissos.py", "Compromissos", "🤝"),
    ]
    sections["Relatorios"] = [
        P("app_pages/15_📄_Resumo_Semanal.py", "Resumo Semanal", "📄"),
        P("app_pages/26_📊_Painel_Unificado.py", "Painel Unificado", "📊"),
        P("peex_pages/16_briefing_pdf.py", "Briefing PDF", "📄"),
        P("peex_pages/13_polinizacao.py", "Polinizacao", "🌸"),
    ]
    sections["Referencia"] = [
        P("app_pages/09_🔄_Comparativos.py", "Comparativos", "🔄"),
        P("app_pages/10_📋_Detalhamento_Aulas.py", "Detalhamento Aulas", "📋"),
        P("app_pages/07_📝_Instrumentos_Avaliativos.py", "Instrumentos", "📝"),
        P("app_pages/21_📑_Boletim_Digital.py", "Boletim", "📑"),
        P("app_pages/18_🏫_Análise_Turma.py", "Analise Turma", "🏫"),
        P("app_pages/28_📅_Calendário_Escolar.py", "Calendario Escolar", "📅"),
        P("app_pages/12_📋_Agenda_Coordenação.py", "Agenda Coordenacao", "📋"),
        P("app_pages/17_🎯_Painel_Ações.py", "Painel Acoes", "🎯"),
        P("peex_pages/11_ritmo_semanal.py", "Ritmo Semanal", "📅"),
    ]

elif role == 'diretor':
    sections["Painel"] = [
        P("app_pages/home.py", "Home", "🏠"),
        P("app_pages/onboarding.py", "Onboarding", "🎓"),
        P("app_pages/glossario.py", "Glossario", "📖"),
    ]
    sections["Acompanhamento"] = [
        P("app_pages/01_📊_Quadro_Gestão.py", "Quadro Gestao", "📊"),
        P("app_pages/02_🎯_Prioridades_da_Semana.py", "Prioridades SIGA", "🎯"),
        P("app_pages/13_🚦_Semáforo_Professor.py", "Semaforo Professor", "🚦"),
        P("app_pages/08_⚠️_Alertas_Conformidade.py", "Alertas Conformidade", "⚠️"),
        P("app_pages/14_🧠_Alertas_Inteligentes.py", "Alertas Inteligentes", "🧠"),
    ]
    sections["Professores"] = [
        P("app_pages/06_👨‍🏫_Visão_Professor.py", "Visao Professor", "👨‍🏫"),
        P("app_pages/11_🖨️_Material_Professor.py", "Material Professor", "🖨️"),
        P("peex_pages/08_meus_professores.py", "Meus Professores", "👥"),
        P("peex_pages/12_espelho_coordenador.py", "Espelho Coordenador", "🪞"),
        P("app_pages/25_💬_Devolutivas.py", "Devolutivas", "💬"),
    ]
    sections["Alunos"] = [
        P("app_pages/19_🎓_Painel_Aluno.py", "Painel Aluno", "🎓"),
        P("app_pages/20_📊_Frequência_Escolar.py", "Frequencia Escolar", "📊"),
        P("app_pages/23_🚨_Alerta_Precoce_ABC.py", "Alerta Precoce ABC", "🚨"),
        P("app_pages/22_📋_Ocorrências.py", "Ocorrencias", "📋"),
        P("peex_pages/09_meus_alunos.py", "Meus Alunos", "🎒"),
    ]
    sections["Curriculo e SAE"] = [
        P("app_pages/03_📚_Estrutura_Curricular.py", "Estrutura Curricular", "📚"),
        P("app_pages/05_📈_Progressão_SAE.py", "Progressao SAE", "📈"),
        P("app_pages/24_🔗_Cruzamento_SIGA_SAE.py", "Cruzamento SIGA SAE", "🔗"),
    ]
    sections["Reunioes"] = [
        P("peex_pages/07_plano_acao.py", "Plano de Acao", "📝"),
        P("peex_pages/15_gerador_peex_unidade.py", "Pauta Unidade", "📃"),
    ]
    sections["Estrategia"] = [
        P("peex_pages/03_scorecard_diretores.py", "Scorecard", "📊"),
        P("peex_pages/20_sinais_vitais.py", "Sinais Vitais", "💓"),
        P("peex_pages/21_escalacoes.py", "Escalacoes", "🔺"),
        P("peex_pages/22_compromissos.py", "Compromissos", "🤝"),
        P("peex_pages/05_memoria.py", "Memoria", "💉"),
    ]
    sections["Relatorios"] = [
        P("app_pages/15_📄_Resumo_Semanal.py", "Resumo Semanal", "📄"),
        P("peex_pages/16_briefing_pdf.py", "Briefing PDF", "📄"),
        P("peex_pages/04_ranking_rede.py", "Rankings", "🏆"),
        P("app_pages/26_📊_Painel_Unificado.py", "Painel Unificado", "📊"),
    ]

elif role == 'professor':
    sections["Meu Espaco"] = [
        P("app_pages/home.py", "Home", "🏠"),
        P("peex_pages/17_espelho_professor.py", "Meu Espelho", "🪞"),
        P("peex_pages/18_minhas_turmas.py", "Minhas Turmas", "📚"),
        P("peex_pages/19_meu_progresso.py", "Meu Progresso", "📈"),
        P("app_pages/glossario.py", "Glossario", "📖"),
    ]

else:
    # Coordenador / Viewer
    sections["Painel"] = [
        P("app_pages/home.py", "Home", "🏠"),
        P("app_pages/onboarding.py", "Onboarding", "🎓"),
        P("app_pages/glossario.py", "Glossario", "📖"),
    ]
    sections["Acompanhamento"] = [
        P("app_pages/01_📊_Quadro_Gestão.py", "Quadro Gestao", "📊"),
        P("app_pages/02_🎯_Prioridades_da_Semana.py", "Prioridades SIGA", "🎯"),
        P("app_pages/13_🚦_Semáforo_Professor.py", "Semaforo Professor", "🚦"),
        P("app_pages/08_⚠️_Alertas_Conformidade.py", "Alertas Conformidade", "⚠️"),
        P("app_pages/14_🧠_Alertas_Inteligentes.py", "Alertas Inteligentes", "🧠"),
    ]
    sections["Professores"] = [
        P("app_pages/06_👨‍🏫_Visão_Professor.py", "Visao Professor", "👨‍🏫"),
        P("app_pages/11_🖨️_Material_Professor.py", "Material Professor", "🖨️"),
        P("peex_pages/08_meus_professores.py", "Meus Professores", "👥"),
        P("peex_pages/12_espelho_coordenador.py", "Meu Espelho", "🪞"),
        P("app_pages/25_💬_Devolutivas.py", "Devolutivas", "💬"),
    ]
    sections["Alunos"] = [
        P("app_pages/19_🎓_Painel_Aluno.py", "Painel Aluno", "🎓"),
        P("app_pages/20_📊_Frequência_Escolar.py", "Frequencia Escolar", "📊"),
        P("app_pages/23_🚨_Alerta_Precoce_ABC.py", "Alerta Precoce ABC", "🚨"),
        P("app_pages/22_📋_Ocorrências.py", "Ocorrencias", "📋"),
        P("peex_pages/09_meus_alunos.py", "Meus Alunos", "🎒"),
    ]
    sections["Curriculo e SAE"] = [
        P("app_pages/03_📚_Estrutura_Curricular.py", "Estrutura Curricular", "📚"),
        P("app_pages/05_📈_Progressão_SAE.py", "Progressao SAE", "📈"),
        P("app_pages/24_🔗_Cruzamento_SIGA_SAE.py", "Cruzamento SIGA SAE", "🔗"),
    ]
    sections["Reunioes PEEX"] = [
        P("peex_pages/15_gerador_peex_unidade.py", "Pauta Reuniao", "📃"),
        P("peex_pages/07_plano_acao.py", "Plano de Acao", "📝"),
    ]
    sections["Relatorios"] = [
        P("app_pages/15_📄_Resumo_Semanal.py", "Resumo Semanal", "📄"),
        P("peex_pages/16_briefing_pdf.py", "Briefing PDF", "📄"),
        P("peex_pages/13_polinizacao.py", "Polinizacao", "🌸"),
        P("peex_pages/04_ranking_rede.py", "Rankings", "🏆"),
    ]

pg = st.navigation(sections)
pg.run()
