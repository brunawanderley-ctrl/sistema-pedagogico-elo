"""
PEEX — Scorecard Diretores (CEO)
Visao detalhada dos scorecards de todas as unidades para a CEO.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_role, ROLE_CEO, ROLE_DIRETOR
from utils import (
    calcular_semana_letiva, DATA_DIR, UNIDADES_NOMES,
    CONFORMIDADE_META, CONFORMIDADE_BAIXO,
)
from components import cabecalho_pagina
from engine import carregar_scorecard_diretor, carregar_missoes_pregeradas
from peex_utils import calcular_indice_elo


# ========== CSS ==========

st.markdown("""
<style>
    .sc-card {
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 6px solid;
    }
    .sc-verde { background: #e8f5e9; border-left-color: #43a047; }
    .sc-amarelo { background: #fff8e1; border-left-color: #ffa000; }
    .sc-vermelho { background: #ffebee; border-left-color: #e53935; }
    .sc-titulo { font-size: 1.3em; font-weight: bold; margin-bottom: 10px; }
    .sc-metricas {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        margin-top: 10px;
    }
    .sc-metrica {
        text-align: center;
        min-width: 80px;
    }
    .sc-metrica-valor { font-size: 1.5em; font-weight: bold; }
    .sc-metrica-label { font-size: 0.75em; color: #666; }
    .sc-missao-top {
        background: rgba(0,0,0,0.05);
        padding: 8px 12px;
        border-radius: 6px;
        margin-top: 8px;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role not in (ROLE_CEO, ROLE_DIRETOR):
    st.warning("Acesso restrito a CEO e Diretores.")
    st.stop()


# ========== MAIN ==========

cabecalho_pagina("Scorecard Diretores", "Panorama detalhado de cada unidade")

semana = calcular_semana_letiva()

resumo_path = DATA_DIR / "resumo_Executivo.csv"
if not resumo_path.exists():
    st.warning("Dados nao disponiveis. Execute a extracao do SIGA.")
    st.stop()

resumo_df = pd.read_csv(resumo_path)

# Gerar scorecard detalhado por unidade
for un_code in ['BV', 'CD', 'JG', 'CDR']:
    nome_un = UNIDADES_NOMES.get(un_code, un_code)
    sc = carregar_scorecard_diretor(un_code)
    row = resumo_df[resumo_df['unidade'] == un_code]

    if row.empty:
        continue

    r = row.iloc[0]
    ie = calcular_indice_elo(r)
    conf = r.get('pct_conformidade_media', 0)

    # Classificar
    if conf >= CONFORMIDADE_META:
        card_class = 'sc-card sc-verde'
        status = 'SAUDAVEL'
    elif conf >= CONFORMIDADE_BAIXO:
        card_class = 'sc-card sc-amarelo'
        status = 'ATENCAO'
    else:
        card_class = 'sc-card sc-vermelho'
        status = 'CRITICO'

    # Missoes
    missoes = carregar_missoes_pregeradas(un_code)
    n_missoes = len(missoes)
    n_urgentes = len([b for b in missoes if b.get('nivel') == 'URGENTE'])
    top_missao = missoes[0].get('o_que', '')[:80] if missoes else 'Nenhuma'

    st.markdown(f"""
    <div class="{card_class}">
        <div class="sc-titulo">{nome_un} — {status}</div>
        <div class="sc-metricas">
            <div class="sc-metrica">
                <div class="sc-metrica-valor">{ie:.0f}</div>
                <div class="sc-metrica-label">IE</div>
            </div>
            <div class="sc-metrica">
                <div class="sc-metrica-valor">{conf:.0f}%</div>
                <div class="sc-metrica-label">Conformidade</div>
            </div>
            <div class="sc-metrica">
                <div class="sc-metrica-valor">{r.get('frequencia_media', 0):.0f}%</div>
                <div class="sc-metrica-label">Frequencia</div>
            </div>
            <div class="sc-metrica">
                <div class="sc-metrica-valor">{sc.get('total_professores', int(r.get('total_professores', 0)))}</div>
                <div class="sc-metrica-label">Professores</div>
            </div>
            <div class="sc-metrica">
                <div class="sc-metrica-valor">{sc.get('professores_criticos', int(r.get('professores_criticos', 0)))}</div>
                <div class="sc-metrica-label">Prof Criticos</div>
            </div>
            <div class="sc-metrica">
                <div class="sc-metrica-valor">{n_missoes}</div>
                <div class="sc-metrica-label">Missoes</div>
            </div>
            <div class="sc-metrica">
                <div class="sc-metrica-valor" style="color:#c62828;">{n_urgentes}</div>
                <div class="sc-metrica-label">Urgentes</div>
            </div>
            <div class="sc-metrica">
                <div class="sc-metrica-valor">{r.get('pct_alunos_risco', 0):.0f}%</div>
                <div class="sc-metrica-label">Alunos Risco</div>
            </div>
        </div>
        <div class="sc-missao-top">Top missao: {top_missao}</div>
    </div>
    """, unsafe_allow_html=True)

# Tabela comparativa
st.markdown("---")
st.markdown("### Tabela Comparativa")

dados_tabela = []
for un_code in ['BV', 'CD', 'JG', 'CDR']:
    row = resumo_df[resumo_df['unidade'] == un_code]
    if not row.empty:
        r = row.iloc[0]
        ie = calcular_indice_elo(r)
        missoes = carregar_missoes_pregeradas(un_code)
        dados_tabela.append({
            'Unidade': UNIDADES_NOMES.get(un_code, un_code),
            'IE': round(ie, 1),
            'Conformidade': f"{r.get('pct_conformidade_media', 0):.0f}%",
            'Frequencia': f"{r.get('frequencia_media', 0):.0f}%",
            'Prof Ritmo': f"{r.get('pct_prof_no_ritmo', 0):.0f}%",
            'Alunos Risco': f"{r.get('pct_alunos_risco', 0):.0f}%",
            'Missoes': len(missoes),
        })

if dados_tabela:
    st.dataframe(pd.DataFrame(dados_tabela), use_container_width=True, hide_index=True)
