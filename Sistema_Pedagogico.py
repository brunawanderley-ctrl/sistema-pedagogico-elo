#!/usr/bin/env python3
"""
SISTEMA PEDAGÓGICO INTEGRADO - COLÉGIO ELO 2026
Plataforma de Acompanhamento: SIGA + SAE

Sistema multi-página para coordenação pedagógica com:
- Material de referência completo
- Dashboards de acompanhamento
- Material imprimível para professores
"""

import streamlit as st
import subprocess
import os
from datetime import datetime
from pathlib import Path
from auth import check_password, logout_button
from utils import DATA_DIR, is_cloud, ultima_atualizacao, carregar_fato_aulas, carregar_horario_esperado, carregar_calendario, carregar_progressao_sae

# Configuração da página (DEVE ser a primeira chamada Streamlit)
st.set_page_config(
    page_title="Sistema Pedagógico ELO 2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Autenticação - bloqueia acesso sem login
if not check_password():
    st.stop()

# ========== SIDEBAR: LOGOUT + ATUALIZAÇÃO DE DADOS ==========
logout_button()
_aulas_path = DATA_DIR / "fato_Aulas.csv"

with st.sidebar:
    st.subheader("Atualizar Dados")
    st.caption(f"Ultima atualizacao: {ultima_atualizacao()}")

    if not is_cloud():
        if st.button("Atualizar Diario de Classe", type="primary", key="btn_atualizar_home"):
            _script_path = Path(__file__).parent / "atualizar_siga.py"
            with st.spinner("Atualizando dados do SIGA..."):
                _result = subprocess.run(
                    ["python3", str(_script_path)],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(Path(__file__).parent),
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

# CSS customizado
st.markdown("""
<style>
    .main > div { padding-top: 1rem; }
    h1 { color: #1a237e; text-align: center; }
    h2 { color: #303f9f; border-bottom: 2px solid #303f9f; padding-bottom: 8px; }
    h3 { color: #3f51b5; }
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .warning-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .highlight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin: 10px 0;
    }
    .page-link {
        background: #f5f5f5;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #3f51b5;
    }
    .page-link:hover {
        background: #e8eaf6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    aulas_path = _aulas_path

    st.title("📚 Sistema Pedagógico Integrado")
    st.markdown("### Colégio ELO - Planejamento 2026 | SIGA + SAE")

    st.markdown("---")

    # Introdução
    st.markdown("""
    <div class="highlight-card">
        <h2 style="color: white; border: none;">Bem-vindo ao Sistema de Gestão Pedagógica</h2>
        <p>Este sistema integra os dados do <strong>SIGA</strong> (Sistema de Gestão Acadêmica)
        com a estrutura curricular do <strong>SAE Digital</strong> para acompanhamento em tempo real.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navegação por páginas
    st.header("📑 Navegação do Sistema")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="page-link">
            <h3>📊 1. Quadro de Gestão à Vista</h3>
            <p>Visão geral com métricas principais, alertas e status atual da rede.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>📅 2. Calendário Escolar</h3>
            <p>Trimestres, feriados, recessos, semanas especiais e marcos de avaliação.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>📚 3. Estrutura Curricular</h3>
            <p>Carga horária por disciplina, comparativo entre unidades, Anos Finais e Ensino Médio.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>📖 4. Material SAE</h3>
            <p>Estrutura dos livros, seções, metodologia Design Thinking, explicações para coordenação.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>📈 5. Progressão SAE</h3>
            <p>Ritmo esperado, capítulos por semana, onde está vs onde deveria estar.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="page-link">
            <h3>👨‍🏫 6. Visão do Professor</h3>
            <p>Calendário individual, encontros no ano, metas por trimestre. <strong>Imprimível!</strong></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>📝 7. Instrumentos Avaliativos</h3>
            <p>Trilhas, avaliações, simulados - quem usou, quando, onde.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>⚠️ 8. Alertas e Conformidade</h3>
            <p>Monitoramento de registros, professores sem aulas, atrasos.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>🔄 9. Comparativos</h3>
            <p>Entre unidades, entre professores da mesma disciplina, entre séries.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>📋 10. Detalhamento de Aulas</h3>
            <p>Quem registrou, o quê, onde, quando. Visão completa dos registros.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Instruções
    st.header("🧭 Como Usar Este Sistema")

    st.markdown("""
    <div class="info-box">
        <strong>👈 Use o menu lateral (sidebar)</strong> para navegar entre as páginas.<br><br>
        Cada página contém:
        <ul>
            <li><strong>Informações de referência</strong> - Tabelas e explicações do material SAE</li>
            <li><strong>Dados em tempo real</strong> - Extraídos do SIGA</li>
            <li><strong>Comparativos</strong> - Entre unidades, professores, séries</li>
            <li><strong>Material imprimível</strong> - Para entregar aos professores</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Status atual
    st.header("📊 Status Atual do Sistema")

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()
    df_cal = carregar_calendario()
    df_prog = carregar_progressao_sae()

    with col_s1:
        if not df_aulas.empty:
            st.metric("✅ Aulas no SIGA", f"{len(df_aulas):,}")
        else:
            st.metric("❌ Aulas no SIGA", "Nao carregado")

    with col_s2:
        if not df_horario.empty:
            st.metric("✅ Grade Horaria", f"{len(df_horario):,}/semana")
        else:
            st.metric("❌ Grade Horaria", "Nao carregado")

    with col_s3:
        if not df_cal.empty:
            st.metric("✅ Calendario", f"{len(df_cal)} dias")
        else:
            st.metric("❌ Calendario", "Nao carregado")

    with col_s4:
        if not df_prog.empty:
            st.metric("✅ Progressao SAE", f"{len(df_prog):,} registros")
        else:
            st.metric("❌ Progressao SAE", "Nao carregado")

    # Rodapé
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        Sistema Pedagógico Integrado - Colégio ELO 2026<br>
        SIGA + SAE Digital | Última atualização: {datetime.now().strftime("%d/%m/%Y %H:%M")}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
