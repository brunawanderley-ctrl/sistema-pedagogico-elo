"""
PEEX — Meus Alunos (Coordenador)
ABC scoring + tiers + alertas por aluno.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit
from utils import (
    calcular_semana_letiva, DATA_DIR,
    UNIDADES_NOMES,
)
from components import cabecalho_pagina


# ========== CSS ==========

st.markdown("""
<style>
    .aluno-card {
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 6px;
        border-left: 4px solid;
    }
    .aluno-a { background: #e8f5e9; border-left-color: #43a047; }
    .aluno-b { background: #fff8e1; border-left-color: #ffa000; }
    .aluno-c { background: #ffebee; border-left-color: #e53935; }
    .aluno-nome { font-weight: bold; }
    .aluno-meta { font-size: 0.85em; color: #666; }
    .tier-resumo {
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ========== MAIN ==========

cabecalho_pagina("Meus Alunos", "Classificacao ABC + alertas de risco")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)

# Tentar carregar dados de alunos
alunos_path = DATA_DIR / "dim_Alunos.csv"
freq_path = DATA_DIR / "fato_Frequencia_Aluno.csv"
ocorr_path = DATA_DIR / "fato_Ocorrencias.csv"

if not alunos_path.exists():
    st.warning("Dados de alunos nao disponiveis. Execute a extracao do SIGA.")
    st.stop()

alunos_df = pd.read_csv(alunos_path)

# Filtrar por unidade
if 'unidade' in alunos_df.columns:
    alunos_un = alunos_df[alunos_df['unidade'] == user_unit].copy()
else:
    alunos_un = alunos_df.copy()

if alunos_un.empty:
    st.warning(f"Nenhum aluno encontrado para {nome_un}.")
    st.stop()

# Carregar frequencia se disponivel
freq_df = pd.DataFrame()
if freq_path.exists():
    freq_df = pd.read_csv(freq_path)
    if 'unidade' in freq_df.columns:
        freq_df = freq_df[freq_df['unidade'] == user_unit]

# Carregar ocorrencias se disponivel
ocorr_df = pd.DataFrame()
if ocorr_path.exists():
    ocorr_df = pd.read_csv(ocorr_path)
    if 'unidade' in ocorr_df.columns:
        ocorr_df = ocorr_df[ocorr_df['unidade'] == user_unit]

# Calcular score ABC por aluno
# A = sem risco, B = atencao, C = risco
alunos_un['frequencia'] = 100.0
alunos_un['n_ocorrencias'] = 0
alunos_un['ocorr_graves'] = 0

# --- Frequencia: agregar presenca bruta por aluno_id ---
if not freq_df.empty and 'aluno_id' in freq_df.columns and 'presenca' in freq_df.columns:
    f = freq_df.copy()
    f['_presente'] = f['presenca'].isin(['P'])
    f['_justificada'] = f['presenca'].isin(['J'])
    f['_registrada'] = f['presenca'].isin(['P', 'F', 'J'])
    freq_agg = f.groupby('aluno_id').agg(
        presencas=('_presente', 'sum'),
        justificadas=('_justificada', 'sum'),
        total_aulas=('_registrada', 'sum'),
    ).reset_index()
    freq_agg['pct_freq'] = (
        (freq_agg['presencas'] + freq_agg['justificadas'])
        / freq_agg['total_aulas'].clip(lower=1) * 100
    ).round(1)
    # Merge com alunos
    alunos_un = alunos_un.merge(
        freq_agg[['aluno_id', 'pct_freq', 'total_aulas']],
        on='aluno_id', how='left',
    )
    # Só atualizar freq se tiver pelo menos 5 chamadas (evitar falsos positivos)
    mask_valido = alunos_un['total_aulas'].fillna(0) >= 5
    alunos_un.loc[mask_valido, 'frequencia'] = alunos_un.loc[mask_valido, 'pct_freq'].fillna(100)
    alunos_un.drop(columns=['pct_freq', 'total_aulas'], inplace=True, errors='ignore')

# --- Ocorrencias: contar por aluno_id (so Disciplinar — Pedagogico e informativo) ---
if not ocorr_df.empty and 'aluno_id' in ocorr_df.columns:
    oc = ocorr_df.copy()
    if 'categoria' in oc.columns:
        oc = oc[oc['categoria'] == 'Disciplinar']
    ocorr_agg = oc.groupby('aluno_id').agg(
        n_ocorr=('aluno_id', 'count'),
    ).reset_index()
    if 'gravidade' in oc.columns:
        grav_agg = oc.groupby('aluno_id')['gravidade'].apply(
            lambda x: (x == 'Grave').sum()
        ).reset_index(name='n_graves')
        ocorr_agg = ocorr_agg.merge(grav_agg, on='aluno_id', how='left')
    alunos_un = alunos_un.merge(ocorr_agg, on='aluno_id', how='left')
    alunos_un['n_ocorrencias'] = alunos_un['n_ocorr'].fillna(0).astype(int)
    alunos_un['ocorr_graves'] = alunos_un['n_graves'].fillna(0).astype(int) if 'n_graves' in alunos_un.columns else 0
    alunos_un.drop(columns=['n_ocorr', 'n_graves'], inplace=True, errors='ignore')

# Score ABC
def calcular_tier(row):
    freq = row.get('frequencia', 100)
    ocorr = int(row.get('n_ocorrencias', 0))
    graves = int(row.get('ocorr_graves', 0))
    if freq < 75 or ocorr >= 5 or graves >= 2:
        return 'C'
    elif freq < 85 or ocorr >= 2 or graves >= 1:
        return 'B'
    return 'A'

alunos_un['tier'] = alunos_un.apply(calcular_tier, axis=1)

# Contagem por tier
tier_a = alunos_un[alunos_un['tier'] == 'A']
tier_b = alunos_un[alunos_un['tier'] == 'B']
tier_c = alunos_un[alunos_un['tier'] == 'C']

# Resumo
st.markdown(f"**{nome_un}** | {len(alunos_un)} alunos")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="tier-resumo" style="background: linear-gradient(135deg, #2e7d32, #43a047);">
        <div style="font-size:2em;">{len(tier_a)}</div>
        <div>Tier A (Saudavel)</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="tier-resumo" style="background: linear-gradient(135deg, #e65100, #ff9800);">
        <div style="font-size:2em;">{len(tier_b)}</div>
        <div>Tier B (Atencao)</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="tier-resumo" style="background: linear-gradient(135deg, #b71c1c, #e53935);">
        <div style="font-size:2em;">{len(tier_c)}</div>
        <div>Tier C (Risco)</div>
    </div>
    """, unsafe_allow_html=True)

# Filtros
st.markdown("---")
filtro_tier = st.radio("Filtrar por Tier:", ['Todos', 'C (Risco)', 'B (Atencao)', 'A (Saudavel)'], horizontal=True)
filtro_serie = st.selectbox("Serie:", ['Todas'] + sorted(alunos_un['serie'].unique().tolist()) if 'serie' in alunos_un.columns else ['Todas'])

if filtro_tier == 'C (Risco)':
    lista = tier_c
elif filtro_tier == 'B (Atencao)':
    lista = tier_b
elif filtro_tier == 'A (Saudavel)':
    lista = tier_a
else:
    lista = pd.concat([tier_c, tier_b, tier_a])

if filtro_serie != 'Todas' and 'serie' in lista.columns:
    lista = lista[lista['serie'] == filtro_serie]

col_nome = 'aluno_nome' if 'aluno_nome' in lista.columns else 'nome' if 'nome' in lista.columns else 'aluno' if 'aluno' in lista.columns else lista.columns[0]

for _, row in lista.iterrows():
    tier = row.get('tier', 'A')
    card_class = {'A': 'aluno-card aluno-a', 'B': 'aluno-card aluno-b', 'C': 'aluno-card aluno-c'}.get(tier, 'aluno-card aluno-a')
    freq = row.get('frequencia', 100)
    ocorr = row.get('n_ocorrencias', 0)
    serie = row.get('serie', 'N/D')

    alerta = ''
    if freq < 75:
        alerta = ' | RISCO INFREQUENCIA (LDB)'
    elif ocorr >= 5:
        alerta = ' | OCORRENCIAS GRAVES'

    st.markdown(f"""
    <div class="{card_class}">
        <span class="aluno-nome">[{tier}] {row[col_nome]}</span>
        <div class="aluno-meta">
            Serie: {serie} | Frequencia: {freq:.0f}% | Ocorrencias: {int(ocorr)}{alerta}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.metric("Total em Risco (Tier C)", len(tier_c), f"{len(tier_c)/max(len(alunos_un),1)*100:.0f}% do total")
