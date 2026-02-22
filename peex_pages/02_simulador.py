"""
PEEX — Simulador de Cenarios (CEO)
CEO seleciona intervencao e ve impacto estimado nos indicadores.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_role, ROLE_CEO
from utils import DATA_DIR, UNIDADES_NOMES, calcular_semana_letiva
from components import cabecalho_pagina
from peex_utils import calcular_indice_elo


# ========== CSS ==========

st.markdown("""
<style>
    .sim-card {
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        text-align: center;
    }
    .sim-antes { background: linear-gradient(135deg, #e0e0e0, #f5f5f5); }
    .sim-depois { background: linear-gradient(135deg, #e8f5e9, #c8e6c9); }
    .sim-valor { font-size: 2.2em; font-weight: bold; }
    .sim-label { font-size: 0.85em; color: #666; }
    .sim-delta { font-size: 1.1em; font-weight: bold; }
    .sim-delta-pos { color: #2e7d32; }
    .sim-delta-neg { color: #c62828; }
    .sim-intervencao {
        padding: 14px 18px;
        margin: 6px 0;
        border-radius: 8px;
        border-left: 4px solid #1a237e;
        background: #e8eaf6;
    }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role != ROLE_CEO:
    st.warning("Acesso restrito a CEO.")
    st.stop()


# ========== INTERVENCOES ==========

INTERVENCOES = [
    {
        'id': 'transferir_prof',
        'nome': 'Transferir professor entre unidades',
        'descricao': 'Move um professor de alto desempenho para unidade com dificuldade',
        'impacto': {
            'pct_conformidade_media': 5,
            'frequencia_media': 1,
            'pct_prof_no_ritmo': 8,
        },
        'risco': 'A unidade de origem pode perder desempenho.',
    },
    {
        'id': 'reforco_escolar',
        'nome': 'Programa de reforco escolar',
        'descricao': 'Aulas extras para alunos em risco de frequencia/nota',
        'impacto': {
            'frequencia_media': 3,
            'pct_alunos_risco': -5,
        },
        'risco': 'Custo adicional de horas-aula.',
    },
    {
        'id': 'formacao_docente',
        'nome': 'Formacao docente intensiva',
        'descricao': 'Workshop para professores com baixo registro/conformidade',
        'impacto': {
            'pct_conformidade_media': 8,
            'pct_prof_no_ritmo': 10,
        },
        'risco': 'Professores fora de sala durante formacao.',
    },
    {
        'id': 'busca_ativa',
        'nome': 'Busca ativa de alunos',
        'descricao': 'Equipe dedicada a contatar familias de alunos infrequentes',
        'impacto': {
            'frequencia_media': 4,
            'pct_alunos_risco': -8,
        },
        'risco': 'Demanda tempo da equipe de orientacao.',
    },
    {
        'id': 'mentoria_coord',
        'nome': 'Mentoria entre coordenadores',
        'descricao': 'Coordenador experiente acompanha coordenador com dificuldade',
        'impacto': {
            'pct_conformidade_media': 3,
            'frequencia_media': 2,
        },
        'risco': 'Depende de disponibilidade.',
    },
]


# ========== MAIN ==========

cabecalho_pagina("Simulador de Cenarios", "Estime o impacto de intervencoes nos indicadores")

semana = calcular_semana_letiva()

resumo_path = DATA_DIR / "resumo_Executivo.csv"
if not resumo_path.exists():
    st.warning("Dados nao disponiveis. Execute a extracao do SIGA.")
    st.stop()

resumo_df = pd.read_csv(resumo_path)

# Selecionar unidade
unidade = st.selectbox(
    "Unidade alvo",
    ['BV', 'CD', 'JG', 'CDR'],
    format_func=lambda x: UNIDADES_NOMES.get(x, x),
)

row = resumo_df[resumo_df['unidade'] == unidade]
if row.empty:
    st.warning(f"Dados da unidade {unidade} nao encontrados.")
    st.stop()

r = row.iloc[0]
ie_atual = calcular_indice_elo(r)

# Selecionar intervencoes
st.markdown("### Selecione Intervencoes")
intervencoes_selecionadas = []

for interv in INTERVENCOES:
    with st.expander(f"{interv['nome']}"):
        st.markdown(f"**{interv['descricao']}**")
        st.caption(f"Risco: {interv['risco']}")

        impactos_txt = []
        for campo, delta in interv['impacto'].items():
            nome_campo = campo.replace('pct_', '').replace('_', ' ').title()
            sinal = '+' if delta > 0 else ''
            impactos_txt.append(f"{nome_campo}: {sinal}{delta}pp")
        st.markdown("Impacto estimado: " + " | ".join(impactos_txt))

        if st.checkbox("Aplicar", key=f"sim_{interv['id']}"):
            intervencoes_selecionadas.append(interv)

# Calcular cenario
st.markdown("---")
st.markdown("### Resultado da Simulacao")

if not intervencoes_selecionadas:
    st.info("Selecione pelo menos uma intervencao para simular.")
else:
    # Calcular impacto combinado
    impacto_total = {}
    for interv in intervencoes_selecionadas:
        for campo, delta in interv['impacto'].items():
            impacto_total[campo] = impacto_total.get(campo, 0) + delta

    # Criar cenario "depois"
    r_depois = dict(r)
    for campo, delta in impacto_total.items():
        val_antes = r_depois.get(campo, 0) or 0
        r_depois[campo] = max(0, min(100, val_antes + delta))

    ie_depois = calcular_indice_elo(r_depois)
    delta_ie = ie_depois - ie_atual

    # Before / After
    col_antes, col_seta, col_depois = st.columns([2, 1, 2])

    with col_antes:
        st.markdown(f"""
        <div class="sim-card sim-antes">
            <div class="sim-label">ANTES</div>
            <div class="sim-valor">{ie_atual:.0f}</div>
            <div class="sim-label">Indice ELO</div>
        </div>
        """, unsafe_allow_html=True)

    with col_seta:
        cor_delta = 'sim-delta-pos' if delta_ie > 0 else 'sim-delta-neg'
        sinal = '+' if delta_ie > 0 else ''
        st.markdown(f"""
        <div style="text-align:center; padding-top: 30px;">
            <div class="sim-delta {cor_delta}">{sinal}{delta_ie:.1f}</div>
            <div style="font-size:2em;">→</div>
        </div>
        """, unsafe_allow_html=True)

    with col_depois:
        st.markdown(f"""
        <div class="sim-card sim-depois">
            <div class="sim-label">DEPOIS</div>
            <div class="sim-valor">{ie_depois:.0f}</div>
            <div class="sim-label">Indice ELO</div>
        </div>
        """, unsafe_allow_html=True)

    # Detalhamento por indicador
    st.markdown("### Detalhamento por Indicador")
    for campo, delta in impacto_total.items():
        val_antes = r.get(campo, 0) or 0
        val_depois = max(0, min(100, val_antes + delta))
        nome = campo.replace('pct_', '').replace('_', ' ').title()
        sinal = '+' if delta > 0 else ''
        cor = '#2e7d32' if delta > 0 else '#c62828'

        st.markdown(f"""
        <div class="sim-intervencao">
            <strong>{nome}</strong>:
            {val_antes:.0f}% → {val_depois:.0f}%
            <span style="color:{cor}; font-weight:bold;">({sinal}{delta}pp)</span>
        </div>
        """, unsafe_allow_html=True)

    # Intervencoes aplicadas
    st.markdown("### Intervencoes Aplicadas")
    for interv in intervencoes_selecionadas:
        st.markdown(f"- **{interv['nome']}**: {interv['descricao']}")
