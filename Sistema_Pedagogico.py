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
import pandas as pd
import subprocess
import os
from datetime import datetime
from pathlib import Path
from auth import check_password, logout_button
from utils import (
    DATA_DIR, is_cloud, ultima_atualizacao,
    carregar_fato_aulas, carregar_horario_esperado, carregar_calendario, carregar_progressao_sae,
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre, filtrar_ate_hoje, _hoje, UNIDADES_NOMES
)


# Configuração da página (DEVE ser a primeira chamada Streamlit)
st.set_page_config(
    page_title="Sistema Pedagógico ELO 2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========== HEALTH CHECK: SCHEDULER EXTERNO ==========
def _ler_health_scheduler():
    """Le o health check do scheduler externo (scheduler_standalone.py)."""
    health_file = Path(__file__).parent / "scheduler_health.json"
    if not health_file.exists():
        return {}
    try:
        import json
        with open(health_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

# ========== SESSION STATE: INICIALIZAÇÃO DE VARIÁVEIS COMUNS ==========
if 'semana_atual' not in st.session_state:
    st.session_state.semana_atual = calcular_semana_letiva()
if 'capitulo_esperado' not in st.session_state:
    st.session_state.capitulo_esperado = calcular_capitulo_esperado(st.session_state.semana_atual)
if 'trimestre_atual' not in st.session_state:
    st.session_state.trimestre_atual = calcular_trimestre(st.session_state.semana_atual)

# Autenticação - bloqueia acesso sem login
if not check_password():
    st.stop()

# ========== SIDEBAR: LOGOUT + ATUALIZAÇÃO DE DADOS ==========
logout_button()
_aulas_path = DATA_DIR / "fato_Aulas.csv"

with st.sidebar:
    st.subheader("Atualizar Dados")
    st.caption(f"Ultima atualizacao: {ultima_atualizacao()}")

    # Botao de atualizacao manual (funciona local E no Render)
    _tem_senha = bool(os.environ.get("SIGA_SENHA"))
    if not _tem_senha:
        try:
            _tem_senha = bool(st.secrets.get("siga", {}).get("senha"))
        except (FileNotFoundError, AttributeError):
            pass

    if _tem_senha:
        if not is_cloud():
            # Local: roda via subprocess (como antes)
            if st.button("Atualizar Diario de Classe", type="primary", key="btn_atualizar_home"):
                _script_path = Path(__file__).parent / "atualizar_siga.py"
                _env = os.environ.copy()
                try:
                    _env["SIGA_SENHA"] = st.secrets["siga"]["senha"]
                except (KeyError, FileNotFoundError):
                    pass
                with st.spinner("Atualizando dados do SIGA..."):
                    _result = subprocess.run(
                        ["python3", str(_script_path)],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=str(Path(__file__).parent),
                        env=_env,
                    )
                if _result.returncode == 0:
                    st.success("Dados atualizados com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro na atualizacao:")
                    st.code(_result.stderr or _result.stdout, language="text")
        else:
            # Render/Cloud: roda via subprocess (mesmo que local)
            if st.button("Atualizar Diario de Classe", type="primary", key="btn_atualizar_home"):
                _script_path = Path(__file__).parent / "atualizar_siga.py"
                _env = os.environ.copy()
                with st.spinner("Atualizando dados do SIGA..."):
                    _result = subprocess.run(
                        ["python3", str(_script_path)],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=str(Path(__file__).parent),
                        env=_env,
                    )
                if _result.returncode == 0:
                    st.success("Dados atualizados com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro na atualizacao:")
                    st.code(_result.stderr or _result.stdout, language="text")
    else:
        st.info("Configure SIGA_SENHA para habilitar atualizacoes.")

    # Status do scheduler externo (le health check de scheduler_standalone.py)
    _health = _ler_health_scheduler()
    if _health.get("last_run"):
        try:
            _last_dt = datetime.fromisoformat(_health["last_run"])
            _last_str = _last_dt.strftime("%d/%m %H:%M")
            if _health.get("ok"):
                st.caption(f"Ultima extracao: {_last_str} ({_health.get('total', 0)} aulas)")
            else:
                st.caption(f"Ultima extracao: {_last_str} (ERRO: {_health.get('erro', '?')})")
        except (ValueError, TypeError):
            st.caption(f"Ultima extracao: {_health['last_run']}")
    st.caption("Scheduler: Externo (8h, 12h, 18h, 20h)")

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
            <p>Relatórios individuais por professor para impressão em lote.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>🚦 13. Semáforo do Professor</h3>
            <p>Visão matricial rápida: quem precisa de atenção HOJE. <strong>NOVO!</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col3b:
        st.markdown("""
        <div class="page-link">
            <h3>📋 12. Agenda da Coordenação</h3>
            <p>Observação de aulas, feedback, acompanhamento de professores.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="page-link">
            <h3>🧠 14. Alertas Inteligentes</h3>
            <p>5 tipos de alerta + Score de Risco do Professor. <strong>NOVO!</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # Quarta linha
    col4a, col4b = st.columns(2)
    with col4a:
        st.markdown("""
        <div class="page-link">
            <h3>📄 15. Resumo Semanal</h3>
            <p>Relatório para reuniões e WhatsApp. Exportável! <strong>NOVO!</strong></p>
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
    st.header("🏥 Saúde da Rede")

    df_aulas = carregar_fato_aulas()
    df_aulas = filtrar_ate_hoje(df_aulas)
    df_horario = carregar_horario_esperado()
    df_cal = carregar_calendario()
    df_prog = carregar_progressao_sae()

    if not df_aulas.empty and not df_horario.empty:
        semana = calcular_semana_letiva()
        capitulo = calcular_capitulo_esperado(semana)
        trimestre = calcular_trimestre(semana)

        # Context bar
        st.markdown(f"**Semana {semana}** | Capítulo esperado: {capitulo}/12 | {trimestre}o Trimestre")

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
            st.metric("Grade Horária", f"{len(df_horario):,}/sem")
        with col_s3:
            if not df_cal.empty:
                letivos = len(df_cal[df_cal['eh_letivo'] == 1])
                st.metric("Dias Letivos", f"{letivos}")
            else:
                st.metric("Calendário", "N/A")
        with col_s4:
            if not df_prog.empty:
                st.metric("Progressão SAE", f"{len(df_prog):,}")
            else:
                st.metric("Progressão SAE", "N/A")

        # ========== PONTOS DE ATENCAO HOJE ==========
        st.markdown("---")
        st.header("📌 Pontos de Atenção Hoje")

        from auth import get_user_unit
        user_unit = get_user_unit()
        hoje = _hoje()

        pontos = []

        # 1. Disciplinas sem nenhum registro
        slots_esp = set(df_horario.groupby(['unidade', 'serie', 'disciplina']).size().index)
        slots_real = set(df_aulas.groupby(['unidade', 'serie', 'disciplina']).size().index)
        slots_sem = slots_esp - slots_real
        if user_unit:
            slots_sem_un = [s for s in slots_sem if s[0] == user_unit]
        else:
            slots_sem_un = list(slots_sem)
        if len(slots_sem_un) > 0:
            exemplos = [f"{d} ({s})" for u, s, d in sorted(slots_sem_un)[:4]]
            pontos.append(('🔴', f'{len(slots_sem_un)} disciplinas sem NENHUM registro', ', '.join(exemplos)))

        # 2. Professores com baixa conformidade na unidade do usuario
        df_un_user = df_aulas if not user_unit else df_aulas[df_aulas['unidade'] == user_unit]
        df_hor_user = df_horario if not user_unit else df_horario[df_horario['unidade'] == user_unit]
        profs_baixos = []
        for prof, df_p in df_un_user.groupby('professor'):
            un_p = df_p['unidade'].iloc[0]
            esp = 0
            for s in df_p['serie'].unique():
                for d in df_p['disciplina'].unique():
                    esp += len(df_hor_user[
                        (df_hor_user['unidade'] == un_p) &
                        (df_hor_user['serie'] == s) &
                        (df_hor_user['disciplina'] == d)
                    ]) * semana
            if esp > 0:
                conf_p = len(df_p) / esp * 100
                if conf_p < 60:
                    profs_baixos.append((prof, conf_p))
        if profs_baixos:
            profs_baixos.sort(key=lambda x: x[1])
            nomes = [f"{p} ({c:.0f}%)" for p, c in profs_baixos[:3]]
            pontos.append(('🟡', f'{len(profs_baixos)} professores abaixo de 60%', ', '.join(nomes)))

        # 3. Aulas recentes sem conteudo
        df_recente = df_un_user[df_un_user['data'] >= (hoje - pd.Timedelta(days=7))]
        if not df_recente.empty:
            sem_cont = df_recente[df_recente['conteudo'].isna() | (df_recente['conteudo'] == '')]
            if len(sem_cont) > 0:
                pct_vazio = len(sem_cont) / len(df_recente) * 100
                if pct_vazio > 20:
                    pontos.append(('🟡', f'{len(sem_cont)} aulas sem conteúdo nos últimos 7 dias ({pct_vazio:.0f}%)',
                                   'Verificar registros dos professores'))

        # 4. Info positiva
        if not profs_baixos and len(slots_sem_un) == 0:
            pontos.append(('🟢', 'Tudo em ordem!', 'Todos os professores registrando e todas disciplinas cobertas'))

        # Render pontos
        for emoji, msg, detalhe in pontos:
            if emoji == '🔴':
                bg = '#FFEBEE'
                border = '#E53935'
            elif emoji == '🟡':
                bg = '#FFF8E1'
                border = '#FFA726'
            else:
                bg = '#E8F5E9'
                border = '#43A047'
            st.markdown(f"""
            <div style="background:{bg}; border-left:4px solid {border}; padding:12px 16px; margin:8px 0; border-radius:4px;">
                <strong>{emoji} {msg}</strong><br>
                <small style="color:#666;">{detalhe}</small>
            </div>
            """, unsafe_allow_html=True)

        if user_unit:
            st.caption(f"Mostrando alertas para: {UNIDADES_NOMES.get(user_unit, user_unit)}")

    else:
        st.warning("Dados não carregados. Execute a extração do SIGA para ver a saúde da rede.")

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
