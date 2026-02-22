"""
PEEX — Genealogia da Proposta
Arvore intelectual do PEEX: rastreamento de ~40 conceitos desde os planos
originais ate a implementacao, com status e localizacao no codigo.
"""

import json
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_role, ROLE_CEO
from utils import WRITABLE_DIR


# ========== CONCEITOS PEEX ==========

CONCEITOS_PEEX = [
    {"conceito": "Indice ELO (IE)", "origem": "Plano Pedagogico Original", "sintese": "Adotado com pesos ajustados", "status": "implementado", "arquivo": "peex_utils.py:calcular_indice_elo"},
    {"conceito": "Ritual de Floresta (5 atos)", "origem": "Competidor B", "sintese": "Adotado integralmente", "status": "implementado", "arquivo": "engine.py:_gerar_rituais"},
    {"conceito": "Nudges Comportamentais", "origem": "Plano Sinais Original", "sintese": "5 mecanismos mantidos", "status": "implementado", "arquivo": "narrativa.py:gerar_nudge_comportamental"},
    {"conceito": "4 Formatos de Reuniao (FLASH/FOCO/CRISE/ESTRATEGICA)", "origem": "Sintese Final", "sintese": "Definido na Sintese", "status": "implementado", "arquivo": "peex_config.py:FORMATOS_REUNIAO"},
    {"conceito": "Escalacao 4 niveis", "origem": "Plano Sinais Original", "sintese": "Mantido com ajustes", "status": "implementado", "arquivo": "peex_config.py:NIVEIS_ESCALACAO"},
    {"conceito": "Diferenciacao por Unidade", "origem": "Plano Pedagogico Original", "sintese": "4 perfis distintos", "status": "implementado", "arquivo": "peex_config.py:DIFERENCIACAO_UNIDADE"},
    {"conceito": "Metas SMART trimestrais", "origem": "Plano Definitivo", "sintese": "8 metas com baseline", "status": "implementado", "arquivo": "peex_config.py:METAS_SMART"},
    {"conceito": "Estrelas da Semana", "origem": "Competidor A", "sintese": "3 rankings: evolucao, saude, generosidade", "status": "implementado", "arquivo": "estrelas.py"},
    {"conceito": "7 Robos Orquestradores", "origem": "Plano Sinais Original + Competidor B", "sintese": "Vigilia+Estrategista+Conselheiro+Comparador+Preditor+Retro+Preparador", "status": "implementado", "arquivo": "engine.py"},
    {"conceito": "Robo ANALISTA (LLM)", "origem": "Plano novo (CEO request)", "sintese": "Narrativa enriquecida com IA", "status": "novo", "arquivo": "llm_engine.py:executar_analista"},
    {"conceito": "Guardiao da Floresta (metafora)", "origem": "Competidor B", "sintese": "Identidade central do PEEX", "status": "implementado", "arquivo": "narrativa.py"},
    {"conceito": "Roteiros FLASH/FOCO/CRISE/ESTRATEGICA", "origem": "Sintese Final Sec 2.3", "sintese": "4 protocolos com scripts minuto-a-minuto", "status": "parcial", "arquivo": "peex_config.py:ROTEIROS"},
    {"conceito": "Crise por Unidade (protocolos)", "origem": "Sintese Final", "sintese": "JG=frequencia, CDR=ocorrencias, BV=referencia, CD=evasao", "status": "parcial", "arquivo": "peex_config.py"},
    {"conceito": "5 Porques (workflow crise)", "origem": "Competidor A", "sintese": "Interativo para reunioes CRISE", "status": "faltando", "arquivo": "preparador_reuniao.py"},
    {"conceito": "Boletim Narrativo", "origem": "Plano Pedagogico Rival", "sintese": "Piloto 8 turmas no II Tri", "status": "faltando", "arquivo": "N/A"},
    {"conceito": "Ticket de Saida semanal", "origem": "Plano Pedagogico Original", "sintese": "Meta: 80% profs III Tri", "status": "faltando", "arquivo": "N/A"},
    {"conceito": "Contratos de Pratica Docente", "origem": "Plano Sinais Rival", "sintese": "Revisados trimestralmente", "status": "faltando", "arquivo": "N/A"},
    {"conceito": "Observacao de Aula (250 meta)", "origem": "Plano Definitivo", "sintese": "II Tri: 1 dimensao/ciclo 3 sem", "status": "faltando", "arquivo": "N/A"},
    {"conceito": "Arena de Propostas Concorrentes", "origem": "Plano novo (CEO request)", "sintese": "CEO decide entre alternativas", "status": "novo", "arquivo": "peex_pages/propostas_concorrentes.py"},
    {"conceito": "Polinizacao (insights cruzados)", "origem": "Competidor B", "sintese": "Troca de praticas entre unidades", "status": "implementado", "arquivo": "peex_pages/13_polinizacao.py"},
    {"conceito": "Protocolo de Busca Ativa (3 niveis)", "origem": "Sintese Final", "sintese": "Unidade->Orientacao->Familia", "status": "parcial", "arquivo": "missoes.py"},
    {"conceito": "PMV (Panorama de Missoes e Vigilancia)", "origem": "Plano Definitivo", "sintese": "Enviado toda segunda", "status": "implementado", "arquivo": "peex_pages/16_briefing_pdf.py"},
    {"conceito": "Simulador de Cenarios", "origem": "Competidor A", "sintese": "What-if para indicadores", "status": "implementado", "arquivo": "peex_pages/02_simulador.py"},
    {"conceito": "Espelho do Coordenador", "origem": "Plano Sinais Original", "sintese": "Dashboard individual do coord", "status": "implementado", "arquivo": "peex_pages/12_espelho_coordenador.py"},
    {"conceito": "Espelho do Professor", "origem": "Plano Sinais Rival", "sintese": "Visao individual do prof", "status": "implementado", "arquivo": "peex_pages/17_espelho_professor.py"},
    {"conceito": "Sistema de Missoes (Vigilia)", "origem": "Competidor B", "sintese": "URGENTE/IMPORTANTE/MONITORAR", "status": "implementado", "arquivo": "missoes.py"},
    {"conceito": "Passagem Pedagogica (9o->1aEM)", "origem": "Plano Definitivo", "sintese": "III Tri: protocolo completo", "status": "faltando", "arquivo": "N/A"},
    {"conceito": "Pares Pedagogicos 2027", "origem": "Plano Definitivo", "sintese": "Cada prof escolhe 1 par", "status": "faltando", "arquivo": "N/A"},
    {"conceito": "Catalogo de Adaptacoes ELO", "origem": "Sintese Final", "sintese": "Inclusao + PEIs", "status": "faltando", "arquivo": "N/A"},
    {"conceito": "Comunicacao com Familias", "origem": "Plano Pedagogico Rival", "sintese": "Pre-ferias + Encontros", "status": "faltando", "arquivo": "N/A"},
    {"conceito": "Alerta Precoce ABC", "origem": "Plano Sinais Original", "sintese": "Score A/B/C por aluno", "status": "implementado", "arquivo": "app_pages/23_Alerta_Precoce_ABC.py"},
]


# ========== CSS ==========

st.markdown("""
<style>
    .gen-header {
        background: linear-gradient(135deg, #1a237e 0%, #311b92 100%);
        color: white;
        padding: 28px;
        border-radius: 14px;
        margin-bottom: 24px;
    }
    .gen-header h2 { color: white; margin: 0 0 8px 0; }
    .gen-header .subtitle { opacity: 0.8; font-size: 0.95em; }
    .arvore-container {
        background: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        overflow-x: auto;
    }
    .arvore-flow {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        flex-wrap: nowrap;
        min-width: 700px;
    }
    .arvore-node {
        padding: 16px 20px;
        border-radius: 10px;
        text-align: center;
        min-width: 140px;
        color: white;
        font-weight: bold;
        font-size: 0.9em;
    }
    .arvore-node-sm {
        font-size: 0.75em;
        opacity: 0.85;
        font-weight: normal;
        margin-top: 4px;
    }
    .arvore-arrow {
        font-size: 1.8em;
        color: #9e9e9e;
        margin: 0 8px;
    }
    .node-planos { background: linear-gradient(135deg, #1565c0, #1976d2); }
    .node-compet { background: linear-gradient(135deg, #7b1fa2, #9c27b0); }
    .node-sintese { background: linear-gradient(135deg, #e65100, #ff9800); }
    .node-impl { background: linear-gradient(135deg, #2e7d32, #43a047); }
    .stat-card {
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 12px;
    }
    .stat-value { font-size: 2em; font-weight: bold; }
    .stat-label { font-size: 0.85em; opacity: 0.85; margin-top: 4px; }
    .stat-verde { background: linear-gradient(135deg, #2e7d32, #43a047); }
    .stat-amarelo { background: linear-gradient(135deg, #e65100, #ff9800); }
    .stat-vermelho { background: linear-gradient(135deg, #c62828, #e53935); }
    .stat-azul { background: linear-gradient(135deg, #1565c0, #1976d2); }
    .conceito-row {
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 8px;
        border-left: 4px solid #e0e0e0;
        background: #fafafa;
    }
    .conceito-impl { border-left-color: #43a047; background: #f1f8e9; }
    .conceito-parcial { border-left-color: #ff9800; background: #fff8e1; }
    .conceito-faltando { border-left-color: #e53935; background: #fbe9e7; }
    .conceito-novo { border-left-color: #1976d2; background: #e3f2fd; }
    .conceito-nome { font-weight: bold; font-size: 0.95em; }
    .conceito-meta { font-size: 0.8em; color: #666; margin-top: 4px; }
    .badge-status {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75em;
        font-weight: bold;
        color: white;
    }
    .badge-implementado { background: #43a047; }
    .badge-parcial { background: #ff9800; }
    .badge-faltando { background: #e53935; }
    .badge-novo { background: #1976d2; }
    .progress-container {
        background: #e0e0e0;
        border-radius: 8px;
        height: 20px;
        overflow: hidden;
        margin-top: 12px;
    }
    .progress-fill {
        height: 100%;
        border-radius: 8px;
        display: flex;
    }
    .progress-seg {
        height: 100%;
        transition: width 0.3s;
    }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role != ROLE_CEO:
    st.stop()


# ========== HEADER ==========

st.markdown("""
<div class="gen-header">
    <h2>Genealogia da Proposta PEEX</h2>
    <div class="subtitle">
        Arvore intelectual completa: dos 4 planos originais ate a implementacao.
        Rastreamento de cada conceito, sua origem e status atual.
    </div>
</div>
""", unsafe_allow_html=True)


# ========== ARVORE VISUAL ==========

st.markdown("### Fluxo de Construcao do PEEX")

st.markdown("""
<div class="arvore-container">
    <div class="arvore-flow">
        <div class="arvore-node node-planos">
            4 Planos Originais
            <div class="arvore-node-sm">Pedagogico + Sinais<br>+ Rivais (2 versoes)</div>
        </div>
        <div class="arvore-arrow">&rarr;</div>
        <div class="arvore-node node-compet">
            2 Competidores
            <div class="arvore-node-sm">Comp. A + Comp. B<br>IA-generated</div>
        </div>
        <div class="arvore-arrow">&rarr;</div>
        <div class="arvore-node node-sintese">
            Sintese Final
            <div class="arvore-node-sm">Melhor de cada<br>plano combinado</div>
        </div>
        <div class="arvore-arrow">&rarr;</div>
        <div class="arvore-node node-impl">
            Implementacao
            <div class="arvore-node-sm">Codigo + Sistema<br>PEEX ativo</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ========== ESTATISTICAS ==========

st.markdown("---")
st.markdown("### Status de Implementacao")

# Tentar carregar auditoria pre-gerada
audit_path = WRITABLE_DIR / "audit_peex_gap.json"
audit_data = None
if audit_path.exists():
    try:
        with open(audit_path, "r", encoding="utf-8") as f:
            audit_data = json.load(f)
    except (json.JSONDecodeError, IOError):
        pass

# Contagens
total = len(CONCEITOS_PEEX)
n_impl = sum(1 for c in CONCEITOS_PEEX if c["status"] == "implementado")
n_parcial = sum(1 for c in CONCEITOS_PEEX if c["status"] == "parcial")
n_faltando = sum(1 for c in CONCEITOS_PEEX if c["status"] == "faltando")
n_novo = sum(1 for c in CONCEITOS_PEEX if c["status"] == "novo")

pct_impl = (n_impl / total * 100) if total else 0
pct_parcial = (n_parcial / total * 100) if total else 0
pct_faltando = (n_faltando / total * 100) if total else 0
pct_novo = (n_novo / total * 100) if total else 0

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="stat-card stat-verde">
        <div class="stat-value">{n_impl}</div>
        <div class="stat-label">Implementados ({pct_impl:.0f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card stat-amarelo">
        <div class="stat-value">{n_parcial}</div>
        <div class="stat-label">Parciais ({pct_parcial:.0f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card stat-vermelho">
        <div class="stat-value">{n_faltando}</div>
        <div class="stat-label">Faltando ({pct_faltando:.0f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-card stat-azul">
        <div class="stat-value">{n_novo}</div>
        <div class="stat-label">Novos ({pct_novo:.0f}%)</div>
    </div>
    """, unsafe_allow_html=True)

# Barra de progresso segmentada
st.markdown(f"""
<div class="progress-container">
    <div class="progress-fill">
        <div class="progress-seg" style="width:{pct_impl}%; background:#43a047;"></div>
        <div class="progress-seg" style="width:{pct_parcial}%; background:#ff9800;"></div>
        <div class="progress-seg" style="width:{pct_novo}%; background:#1976d2;"></div>
        <div class="progress-seg" style="width:{pct_faltando}%; background:#e53935;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption(f"Total: {total} conceitos rastreados")

if audit_data:
    st.caption(f"Ultima auditoria: {audit_data.get('gerado_em', 'N/A')[:19].replace('T', ' ')}")


# ========== FILTRO ==========

st.markdown("---")
st.markdown("### Conceitos Rastreados")

filtro_status = st.radio(
    "Filtrar por status:",
    ["Todos", "Implementado", "Parcial", "Faltando", "Novo"],
    horizontal=True,
)

# Aplicar filtro
if filtro_status == "Todos":
    conceitos_filtrados = CONCEITOS_PEEX
else:
    status_map = {
        "Implementado": "implementado",
        "Parcial": "parcial",
        "Faltando": "faltando",
        "Novo": "novo",
    }
    status_filtro = status_map.get(filtro_status, "implementado")
    conceitos_filtrados = [c for c in CONCEITOS_PEEX if c["status"] == status_filtro]

st.caption(f"Exibindo {len(conceitos_filtrados)} de {total} conceitos")


# ========== TABELA DE CONCEITOS ==========

for conceito in conceitos_filtrados:
    status = conceito["status"]
    classe_row = {
        "implementado": "conceito-impl",
        "parcial": "conceito-parcial",
        "faltando": "conceito-faltando",
        "novo": "conceito-novo",
    }.get(status, "")

    badge_classe = {
        "implementado": "badge-implementado",
        "parcial": "badge-parcial",
        "faltando": "badge-faltando",
        "novo": "badge-novo",
    }.get(status, "badge-implementado")

    status_label = status.capitalize()

    st.markdown(f"""
    <div class="conceito-row {classe_row}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="conceito-nome">{conceito['conceito']}</span>
            <span class="badge-status {badge_classe}">{status_label}</span>
        </div>
        <div class="conceito-meta">
            <strong>Origem:</strong> {conceito['origem']} |
            <strong>Sintese:</strong> {conceito['sintese']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Detalhes expandiveis
    with st.expander(f"Detalhes: {conceito['conceito']}", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Conceito:** {conceito['conceito']}")
            st.markdown(f"**Origem:** {conceito['origem']}")
            st.markdown(f"**Status:** {status_label}")
        with col_b:
            st.markdown(f"**Sintese:** {conceito['sintese']}")
            arquivo = conceito["arquivo"]
            if arquivo != "N/A":
                st.markdown(f"**Arquivo:** `{arquivo}`")
            else:
                st.markdown("**Arquivo:** Nao implementado ainda")


# ========== ORIGENS AGRUPADAS ==========

st.markdown("---")
st.markdown("### Conceitos por Origem")

origens = {}
for c in CONCEITOS_PEEX:
    origem = c["origem"]
    if origem not in origens:
        origens[origem] = []
    origens[origem].append(c)

for origem, conceitos_origem in sorted(origens.items(), key=lambda x: -len(x[1])):
    n_total = len(conceitos_origem)
    n_ok = sum(1 for c in conceitos_origem if c["status"] == "implementado")
    n_parc = sum(1 for c in conceitos_origem if c["status"] == "parcial")

    with st.expander(f"{origem} ({n_total} conceitos, {n_ok} implementados, {n_parc} parciais)"):
        for c in conceitos_origem:
            badge = {
                "implementado": "badge-implementado",
                "parcial": "badge-parcial",
                "faltando": "badge-faltando",
                "novo": "badge-novo",
            }.get(c["status"], "")
            st.markdown(
                f'<span class="badge-status {badge}">{c["status"]}</span> '
                f'**{c["conceito"]}** — {c["sintese"]}',
                unsafe_allow_html=True,
            )
