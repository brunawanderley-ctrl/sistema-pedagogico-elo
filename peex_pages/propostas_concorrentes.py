"""
PEEX — Arena de Propostas Concorrentes (CEO)
CEO digita uma pergunta estrategica e o sistema gera 2-3 propostas
concorrentes para avaliacao comparativa e decisao.
"""

import json
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_role, ROLE_CEO
from utils import DATA_DIR, WRITABLE_DIR, UNIDADES_NOMES, calcular_semana_letiva
from llm_engine import AnalistaELO, _llm_disponivel


# ========== CSS ==========

st.markdown("""
<style>
    .arena-header {
        background: linear-gradient(135deg, #1a237e 0%, #4a148c 50%, #00695c 100%);
        color: white;
        padding: 28px;
        border-radius: 14px;
        margin-bottom: 24px;
    }
    .arena-header h2 { color: white; margin: 0 0 8px 0; }
    .arena-header .subtitle { opacity: 0.8; font-size: 0.95em; }
    .proposta-card {
        padding: 20px;
        border-radius: 12px;
        margin: 8px 0;
        min-height: 320px;
    }
    .proposta-conservadora {
        background: linear-gradient(180deg, #e3f2fd 0%, #bbdefb 100%);
        border-top: 4px solid #1565c0;
    }
    .proposta-inovadora {
        background: linear-gradient(180deg, #f3e5f5 0%, #e1bee7 100%);
        border-top: 4px solid #7b1fa2;
    }
    .proposta-dados {
        background: linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 100%);
        border-top: 4px solid #2e7d32;
    }
    .proposta-nome {
        font-size: 1.15em;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .proposta-resumo {
        font-size: 0.95em;
        margin-bottom: 12px;
        line-height: 1.5;
    }
    .proposta-pro {
        color: #2e7d32;
        font-size: 0.9em;
        margin: 2px 0;
    }
    .proposta-contra {
        color: #c62828;
        font-size: 0.9em;
        margin: 2px 0;
    }
    .proposta-meta {
        font-size: 0.85em;
        color: #444;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid rgba(0,0,0,0.1);
    }
    .historico-item {
        background: #f5f5f5;
        border-left: 3px solid #1a237e;
        padding: 10px 16px;
        margin: 6px 0;
        border-radius: 4px;
        font-size: 0.9em;
    }
    .origem-box {
        background: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.85em;
        color: #666;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role != ROLE_CEO:
    st.warning("Acesso restrito a CEO.")
    st.stop()


# ========== HEADER ==========

semana = calcular_semana_letiva()

st.markdown("""
<div class="arena-header">
    <h2>Arena de Propostas</h2>
    <div class="subtitle">
        Digite uma pergunta estrategica. O sistema gera 2-3 propostas concorrentes
        para que voce compare, avalie e decida.
    </div>
</div>
""", unsafe_allow_html=True)


# ========== SESSION STATE ==========

if "arena_historico" not in st.session_state:
    st.session_state["arena_historico"] = []

if "arena_propostas" not in st.session_state:
    st.session_state["arena_propostas"] = None

if "arena_escolha" not in st.session_state:
    st.session_state["arena_escolha"] = None


# ========== DADOS ==========

resumo_path = DATA_DIR / "resumo_Executivo.csv"
resumo_df = pd.read_csv(resumo_path) if resumo_path.exists() else pd.DataFrame()

dados_rede = {}
if not resumo_df.empty:
    for _, row in resumo_df.iterrows():
        dados_rede[row.get("unidade", "")] = row.to_dict()


# ========== INPUT ==========

st.markdown("### Pergunta Estrategica")

pergunta = st.text_area(
    "O que voce quer decidir?",
    placeholder="Ex: Devemos priorizar frequencia ou conformidade no II Trimestre?",
    height=100,
    key="arena_pergunta",
)

col_btn, col_status = st.columns([1, 3])
with col_btn:
    submeter = st.button("Gerar Propostas", type="primary")
with col_status:
    if _llm_disponivel():
        st.caption("Motor IA ativo — propostas personalizadas")
    else:
        st.caption("Motor IA indisponivel — propostas via template")


# ========== GERACAO ==========

if submeter and pergunta.strip():
    with st.spinner("Gerando propostas concorrentes..."):
        analista = AnalistaELO()
        propostas = analista.competir_propostas(dados_rede, pergunta.strip())

    st.session_state["arena_propostas"] = propostas
    st.session_state["arena_escolha"] = None

    # Registrar no historico
    registro = {
        "pergunta": pergunta.strip(),
        "data": datetime.now().isoformat(),
        "semana": semana,
        "n_propostas": len(propostas) if propostas else 0,
        "fonte": "llm" if _llm_disponivel() else "template",
        "escolha": None,
    }
    historico = st.session_state["arena_historico"]
    historico.insert(0, registro)
    # Manter apenas as ultimas 20
    st.session_state["arena_historico"] = historico[:20]

elif submeter:
    st.warning("Digite uma pergunta antes de gerar propostas.")


# ========== EXIBICAO DE PROPOSTAS ==========

propostas = st.session_state.get("arena_propostas")

if propostas and len(propostas) > 0:
    st.markdown("---")
    st.markdown("### Propostas Concorrentes")

    # Estilos por posicao
    estilos = [
        {"classe": "proposta-conservadora", "emoji": "Conservadora", "cor_titulo": "#1565c0"},
        {"classe": "proposta-inovadora", "emoji": "Inovadora", "cor_titulo": "#7b1fa2"},
        {"classe": "proposta-dados", "emoji": "Baseada em Dados", "cor_titulo": "#2e7d32"},
    ]

    cols = st.columns(min(len(propostas), 3))

    for i, prop in enumerate(propostas[:3]):
        estilo = estilos[i] if i < len(estilos) else estilos[0]
        nome = prop.get("nome", f"Proposta {i+1}")
        resumo = prop.get("resumo", "")
        pros = prop.get("pros", [])
        contras = prop.get("contras", [])
        impacto = prop.get("impacto", "N/A")
        prazo = prop.get("prazo", "N/A")

        pros_html = "".join(
            f'<div class="proposta-pro">+ {p}</div>' for p in pros
        )
        contras_html = "".join(
            f'<div class="proposta-contra">- {c}</div>' for c in contras
        )

        with cols[i]:
            st.markdown(f"""
            <div class="proposta-card {estilo['classe']}">
                <div style="font-size:0.8em; color:{estilo['cor_titulo']}; font-weight:bold; margin-bottom:4px;">
                    {estilo['emoji']}
                </div>
                <div class="proposta-nome">{nome}</div>
                <div class="proposta-resumo">{resumo}</div>
                {pros_html}
                {contras_html}
                <div class="proposta-meta">
                    <strong>Impacto:</strong> {impacto}<br>
                    <strong>Prazo:</strong> {prazo}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Selecao pelo CEO
    st.markdown("---")
    st.markdown("### Sua Decisao")

    nomes_propostas = [p.get("nome", f"Proposta {i+1}") for i, p in enumerate(propostas[:3])]
    escolha = st.radio(
        "Qual proposta voce prefere?",
        options=nomes_propostas,
        index=None,
        key="arena_radio",
        horizontal=True,
    )

    if escolha:
        st.session_state["arena_escolha"] = escolha
        # Atualizar historico com a escolha
        historico = st.session_state.get("arena_historico", [])
        if historico:
            historico[0]["escolha"] = escolha
        st.success(f"Proposta selecionada: **{escolha}**")
        st.caption("Decisao registrada nesta sessao. Utilize como referencia nas proximas reunioes.")

    # Origem
    with st.expander("Origem das propostas"):
        st.markdown("""
        <div class="origem-box">
            Propostas geradas com base nos dados atuais (resumo_Executivo.csv) +
            documentos PEEX originais (docs/obsidian/). Cada proposta representa uma
            abordagem distinta: <strong>Conservadora</strong> (menor risco),
            <strong>Inovadora</strong> (maior impacto) e
            <strong>Baseada em Dados</strong> (o que os indicadores sugerem).
        </div>
        """, unsafe_allow_html=True)
        if _llm_disponivel():
            st.caption("Fonte: Claude API (LLM) com contexto dos documentos PEEX")
        else:
            st.caption("Fonte: Templates internos (API Claude nao configurada)")


# ========== HISTORICO ==========

st.markdown("---")
st.markdown("### Historico de Perguntas")

historico = st.session_state.get("arena_historico", [])
ultimas = historico[:5]

if ultimas:
    for h in ultimas:
        data_fmt = h.get("data", "")[:16].replace("T", " ")
        escolha_txt = f" | Escolha: {h['escolha']}" if h.get("escolha") else ""
        fonte_txt = "IA" if h.get("fonte") == "llm" else "Template"
        st.markdown(f"""
        <div class="historico-item">
            <strong>Sem {h.get('semana', '?')}</strong> ({data_fmt}) — {fonte_txt}{escolha_txt}<br>
            {h.get('pergunta', '')}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Nenhuma pergunta registrada nesta sessao. Faca sua primeira pergunta acima!")
