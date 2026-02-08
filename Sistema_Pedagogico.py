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
from utils import (
    DATA_DIR, is_cloud, ultima_atualizacao,
    carregar_fato_aulas, carregar_horario_esperado, carregar_calendario, carregar_progressao_sae,
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre, UNIDADES_NOMES
)

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
    .saude-card {
        padding: 20px; border-radius: 12px; text-align: center; margin: 5px 0;
        color: white; min-height: 120px;
    }
    .saude-verde { background: linear-gradient(135deg, #43A047, #66BB6A); }
    .saude-amarelo { background: linear-gradient(135deg, #F9A825, #FDD835); color: #333; }
    .saude-vermelho { background: linear-gradient(135deg, #E53935, #EF5350); }
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

    # Terceira linha de paginas
    col3a, col3b = st.columns(2)

    with col3a:
        st.markdown("""
        <div class="page-link">
            <h3>🖨️ 11. Material do Professor</h3>
            <p>Relatorios individuais por professor para impressao em lote.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>🚦 13. Semaforo do Professor</h3>
            <p>Visao matricial rapida: quem precisa de atencao HOJE. <strong>NOVO!</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col3b:
        st.markdown("""
        <div class="page-link">
            <h3>📋 12. Agenda da Coordenacao</h3>
            <p>Observacao de aulas, feedback, acompanhamento de professores.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>🧠 14. Alertas Inteligentes</h3>
            <p>5 tipos de alerta + Score de Risco do Professor. <strong>NOVO!</strong></p>
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

    # Saude da Rede
    st.header("🏥 Saude da Rede")

    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()
    df_cal = carregar_calendario()
    df_prog = carregar_progressao_sae()

    if not df_aulas.empty and not df_horario.empty:
        semana = calcular_semana_letiva()
        capitulo = calcular_capitulo_esperado(semana)
        trimestre = calcular_trimestre(semana)

        # Context bar
        st.markdown(f"**Semana {semana}** | Capitulo esperado: {capitulo}/12 | {trimestre}o Trimestre")

        # Health cards per unit
        unidades = sorted(df_horario['unidade'].unique())
        cols_un = st.columns(len(unidades))

        for i, un in enumerate(unidades):
            df_un = df_aulas[df_aulas['unidade'] == un]
            df_hor_un = df_horario[df_horario['unidade'] == un]
            if df_un['data'].notna().any():
                semana_un = calcular_semana_letiva(df_un['data'].max())
            else:
                semana_un = 1
            esperado = len(df_hor_un) * semana_un
            real = len(df_un)
            conf = (real / esperado * 100) if esperado > 0 else 0
            profs = df_un['professor'].nunique()

            if conf >= 85:
                css = 'saude-verde'
            elif conf >= 70:
                css = 'saude-amarelo'
            else:
                css = 'saude-vermelho'

            nome_un = UNIDADES_NOMES.get(un, un)

            with cols_un[i]:
                st.markdown(f"""
                <div class="saude-card {css}">
                    <h2 style="margin:0; border:none; color:inherit;">{conf:.0f}%</h2>
                    <p style="margin:0; font-size:1.1em; font-weight:bold;">{nome_un}</p>
                    <small>{real} aulas | {profs} profs</small>
                </div>
                """, unsafe_allow_html=True)

        # Data status row
        st.markdown("")
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Aulas Registradas", f"{len(df_aulas):,}")
        with col_s2:
            st.metric("Grade Horaria", f"{len(df_horario):,}/sem")
        with col_s3:
            if not df_cal.empty:
                letivos = len(df_cal[df_cal['eh_letivo'] == 1])
                st.metric("Dias Letivos", f"{letivos}")
            else:
                st.metric("Calendario", "N/A")
        with col_s4:
            if not df_prog.empty:
                st.metric("Progressao SAE", f"{len(df_prog):,}")
            else:
                st.metric("Progressao SAE", "N/A")
    else:
        st.warning("Dados nao carregados. Execute a extracao do SIGA para ver a saude da rede.")

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
