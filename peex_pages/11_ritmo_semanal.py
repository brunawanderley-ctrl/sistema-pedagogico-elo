"""
PEEX — Ritmo Semanal (Coordenador)
Visualizacao expandida do ritmo de registros da semana.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit
from utils import (
    calcular_semana_letiva, _hoje,
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
    UNIDADES_NOMES, INICIO_ANO_LETIVO,
)
from components import cabecalho_pagina


# ========== CSS ==========

st.markdown("""
<style>
    .ritmo-grande {
        display: inline-block;
        padding: 16px 24px;
        border-radius: 12px;
        margin: 6px;
        font-weight: bold;
        text-align: center;
        min-width: 80px;
    }
    .ritmo-g-concluido { background: #c8e6c9; color: #2e7d32; }
    .ritmo-g-hoje { background: #fff9c4; color: #f57f17; border: 3px solid #f57f17; }
    .ritmo-g-futuro { background: #f5f5f5; color: #9e9e9e; }
    .ritmo-g-passado { background: #ffcdd2; color: #c62828; }
    .ritmo-detalhe {
        padding: 12px 16px;
        margin: 6px 0;
        border-radius: 8px;
        background: #fafafa;
        border-left: 4px solid;
    }
</style>
""", unsafe_allow_html=True)


# ========== MAIN ==========

cabecalho_pagina("Ritmo Semanal", "Registros dia a dia + historico")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)

hoje = _hoje()

df_aulas = carregar_fato_aulas()
df_horario = carregar_horario_esperado()

if df_aulas.empty:
    st.warning("Dados de aulas nao disponiveis.")
    st.stop()

df_aulas = filtrar_ate_hoje(df_aulas)
if 'unidade' in df_aulas.columns:
    df_aulas = df_aulas[df_aulas['unidade'] == user_unit]

# Semana atual — SEG a SEX
dia_semana_idx = hoje.weekday()
segunda = hoje - timedelta(days=dia_semana_idx)

dias_nome = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']

st.markdown(f"### Semana {semana} — {nome_un}")
st.markdown(f"{segunda.strftime('%d/%m')} a {(segunda + timedelta(days=4)).strftime('%d/%m/%Y')}")

# Contagem por dia
contagens = []
html_parts = []

for i, nome_dia in enumerate(dias_nome):
    dia = segunda + timedelta(days=i)

    if not df_aulas.empty and 'data' in df_aulas.columns:
        n_registros = (df_aulas['data'].dt.date == dia.date()).sum() if hasattr(df_aulas['data'], 'dt') else 0
    else:
        n_registros = 0

    contagens.append({'dia': nome_dia, 'data': dia, 'registros': n_registros})

    if dia > hoje:
        css = "ritmo-g-futuro"
        check = ""
    elif dia == hoje:
        css = "ritmo-g-hoje"
        check = f"<div>{n_registros} reg</div>"
    else:
        css = "ritmo-g-concluido" if n_registros > 0 else "ritmo-g-passado"
        check = f"<div>{n_registros} reg</div>"

    html_parts.append(f'<span class="ritmo-grande {css}"><div>{nome_dia}</div><div>{dia.strftime("%d/%m")}</div>{check}</span>')

st.markdown(''.join(html_parts), unsafe_allow_html=True)

# Metricas da semana
total_semana = sum(c['registros'] for c in contagens)
dias_com_registro = sum(1 for c in contagens if c['registros'] > 0 and c['data'] <= hoje)
dias_passados = sum(1 for c in contagens if c['data'] <= hoje)

c1, c2, c3 = st.columns(3)
c1.metric("Registros esta semana", total_semana)
c2.metric("Dias com registro", f"{dias_com_registro}/{dias_passados}")
c3.metric("Media/dia", f"{total_semana / max(dias_passados, 1):.0f}")

# Detalhamento por dia
st.markdown("---")
st.markdown("### Detalhamento por Dia")

for c in contagens:
    if c['data'] > hoje:
        continue

    dia = c['data']
    n = c['registros']
    cor = '#43a047' if n > 0 else '#e53935'

    # Professores que registraram nesse dia
    if not df_aulas.empty and 'data' in df_aulas.columns and 'professor' in df_aulas.columns:
        try:
            mask = df_aulas['data'].dt.date == dia.date()
            profs_dia = df_aulas[mask]['professor'].unique()
        except Exception:
            profs_dia = []
    else:
        profs_dia = []

    profs_txt = ', '.join(sorted(profs_dia)[:10]) if len(profs_dia) > 0 else 'Nenhum professor registrou'
    if len(profs_dia) > 10:
        profs_txt += f' (+{len(profs_dia) - 10})'

    st.markdown(f"""
    <div class="ritmo-detalhe" style="border-left-color:{cor};">
        <strong>{c['dia']} ({dia.strftime('%d/%m')})</strong>: {n} registro(s)<br>
        <span style="font-size:0.85em; color:#666;">Professores: {profs_txt}</span>
    </div>
    """, unsafe_allow_html=True)

# Historico ultimas 4 semanas
st.markdown("---")
st.markdown("### Historico (ultimas 4 semanas)")

if not df_aulas.empty and 'data' in df_aulas.columns:
    try:
        df_copy = df_aulas.copy()
        df_copy['data_dt'] = pd.to_datetime(df_copy['data'], errors='coerce')
        df_copy = df_copy.dropna(subset=['data_dt'])
        df_copy['semana_num'] = ((df_copy['data_dt'] - pd.Timestamp(INICIO_ANO_LETIVO)).dt.days // 7 + 1).clip(lower=1)

        hist = df_copy.groupby('semana_num').size().reset_index(name='registros')
        hist = hist[hist['semana_num'] >= max(1, semana - 3)]
        hist = hist[hist['semana_num'] <= semana]

        if len(hist) > 1:
            st.bar_chart(hist.set_index('semana_num')['registros'], use_container_width=True)
        else:
            st.info("Historico insuficiente para exibir grafico.")
    except Exception:
        st.info("Nao foi possivel processar historico.")
