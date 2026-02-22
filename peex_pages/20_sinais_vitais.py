"""
PEEX — Sinais Vitais (Diretor)
Semaforo da unidade com 5 indicadores + tendencia + posicao vs rede.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit, get_user_role, ROLE_DIRETOR, ROLE_CEO
from utils import (
    calcular_semana_letiva, DATA_DIR, UNIDADES_NOMES,
    CONFORMIDADE_META, CONFORMIDADE_BAIXO, CONFORMIDADE_CRITICO,
)
from components import cabecalho_pagina
from peex_utils import calcular_indice_elo


# ========== CSS ==========

st.markdown("""
<style>
    .semaforo-card {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 16px;
    }
    .sem-verde { background: linear-gradient(135deg, #2e7d32, #43a047); }
    .sem-amarelo { background: linear-gradient(135deg, #e65100, #ff9800); }
    .sem-vermelho { background: linear-gradient(135deg, #b71c1c, #e53935); }
    .indicador-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        margin: 6px 0;
        border-radius: 8px;
        background: #fafafa;
    }
    .indicador-nome { flex: 1; font-weight: bold; }
    .indicador-valor { font-size: 1.2em; font-weight: bold; min-width: 60px; text-align: right; }
    .indicador-bar-bg {
        flex: 2;
        height: 10px;
        background: #e0e0e0;
        border-radius: 5px;
        overflow: hidden;
    }
    .indicador-bar-fill { height: 100%; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role not in (ROLE_CEO, ROLE_DIRETOR):
    st.stop()


# ========== MAIN ==========

cabecalho_pagina("Sinais Vitais", "Saude da sua unidade em tempo real")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)

resumo_path = DATA_DIR / "resumo_Executivo.csv"
if not resumo_path.exists():
    st.warning("Dados nao disponiveis. Execute a extracao do SIGA.")
    st.stop()

resumo_df = pd.read_csv(resumo_path)
row = resumo_df[resumo_df['unidade'] == user_unit]
total_row = resumo_df[resumo_df['unidade'] == 'TOTAL']

if row.empty:
    st.warning(f"Dados da unidade {user_unit} nao encontrados.")
    st.stop()

r = row.iloc[0]
ie = calcular_indice_elo(r)

# Semaforo
conf = r.get('pct_conformidade_media', 0)
if conf >= CONFORMIDADE_META:
    cor_sem = 'sem-verde'
    status_txt = 'SAUDAVEL'
elif conf >= CONFORMIDADE_BAIXO:
    cor_sem = 'sem-amarelo'
    status_txt = 'ATENCAO'
else:
    cor_sem = 'sem-vermelho'
    status_txt = 'CRITICO'

st.markdown(f"""
<div class="semaforo-card {cor_sem}">
    <div style="font-size:0.9em; opacity:0.85;">{nome_un}</div>
    <div style="font-size:3em; font-weight:bold;">{status_txt}</div>
    <div style="font-size:1.2em;">IE: {ie:.0f}/100 | Conformidade: {conf:.0f}%</div>
</div>
""", unsafe_allow_html=True)


# Indicadores detalhados
st.markdown("### 5 Indicadores")

indicadores = [
    ('Conformidade', 'pct_conformidade_media', False, 100),
    ('Frequencia Media', 'frequencia_media', False, 100),
    ('Prof. no Ritmo SAE', 'pct_prof_no_ritmo', False, 100),
    ('Alunos em Risco', 'pct_alunos_risco', True, 50),
    ('Ocorrencias Graves', 'ocorr_graves', True, 100),
]

for nome, campo, inverso, vmax in indicadores:
    val = r.get(campo, 0)
    media_rede = total_row.iloc[0].get(campo, 0) if not total_row.empty else 0

    if inverso:
        pct = max(0, min(100, (1 - val / max(vmax, 1)) * 100))
        cor = '#2e7d32' if val < media_rede else '#c62828'
    else:
        pct = max(0, min(100, val / max(vmax, 1) * 100))
        cor = '#2e7d32' if val >= media_rede else '#c62828'

    delta_txt = ""
    if media_rede:
        delta = val - media_rede
        sinal = '+' if delta > 0 else ''
        delta_txt = f" (rede: {media_rede:.0f}, delta: {sinal}{delta:.0f})"

    st.markdown(f"""
    <div class="indicador-row">
        <div class="indicador-nome">{nome}</div>
        <div class="indicador-bar-bg">
            <div class="indicador-bar-fill" style="width:{pct:.0f}%; background:{cor};"></div>
        </div>
        <div class="indicador-valor" style="color:{cor};">{val:.0f}</div>
    </div>
    """, unsafe_allow_html=True)
    if delta_txt:
        st.caption(delta_txt)
