"""
PEEX — Minhas Turmas (Professor)
Visao do professor das suas turmas: conformidade, frequencia, alertas.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit, get_user_role, get_professor_name, ROLE_PROFESSOR
from utils import (
    calcular_semana_letiva, DATA_DIR,
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
    UNIDADES_NOMES,
)
from components import cabecalho_pagina


# ========== CSS ==========

st.markdown("""
<style>
    .turma-card {
        padding: 16px 20px;
        margin: 8px 0;
        border-radius: 10px;
        border-left: 5px solid;
        background: #fafafa;
    }
    .turma-titulo { font-weight: bold; font-size: 1.05em; }
    .turma-meta { font-size: 0.85em; color: #666; margin-top: 4px; }
    .turma-alerta {
        padding: 8px 14px;
        margin: 4px 0;
        border-radius: 6px;
        background: #fff3e0;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role != ROLE_PROFESSOR:
    st.stop()


# ========== MAIN ==========

cabecalho_pagina("Minhas Turmas", "Visao das suas turmas e disciplinas")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
prof_nome = get_professor_name()

if not prof_nome:
    st.warning("Nome do professor nao configurado. Contate o administrador.")
    st.stop()

st.markdown(f"**Professor(a):** {prof_nome} | **Unidade:** {UNIDADES_NOMES.get(user_unit, user_unit)}")

# Carregar dados
df_aulas = carregar_fato_aulas()
df_horario = carregar_horario_esperado()

if df_aulas.empty:
    st.warning("Dados de aulas nao disponiveis.")
    st.stop()

df_aulas = filtrar_ate_hoje(df_aulas)

# Filtrar por unidade e professor
if 'unidade' in df_aulas.columns:
    df_aulas = df_aulas[df_aulas['unidade'] == user_unit]
if 'unidade' in df_horario.columns:
    df_horario = df_horario[df_horario['unidade'] == user_unit]

aulas_prof = df_aulas[df_aulas['professor'] == prof_nome] if 'professor' in df_aulas.columns else pd.DataFrame()
esp_prof = df_horario[df_horario['professor'] == prof_nome] if 'professor' in df_horario.columns else pd.DataFrame()

if aulas_prof.empty and esp_prof.empty:
    st.info("Nenhuma aula encontrada para seu perfil.")
    st.stop()

# Agrupar por turma (serie + disciplina)
turmas = {}

if not esp_prof.empty:
    for _, row in esp_prof.iterrows():
        serie = row.get('serie', 'N/D')
        disc = row.get('disciplina', 'N/D')
        key = f"{serie} | {disc}"
        if key not in turmas:
            turmas[key] = {'serie': serie, 'disciplina': disc, 'esperadas': 0, 'registradas': 0,
                           'com_conteudo': 0, 'alertas': []}
        turmas[key]['esperadas'] += 1

if not aulas_prof.empty:
    for _, row in aulas_prof.iterrows():
        serie = row.get('serie', 'N/D')
        disc = row.get('disciplina', 'N/D')
        key = f"{serie} | {disc}"
        if key not in turmas:
            turmas[key] = {'serie': serie, 'disciplina': disc, 'esperadas': 0, 'registradas': 0,
                           'com_conteudo': 0, 'alertas': []}
        turmas[key]['registradas'] += 1
        # Conteudo
        conteudo = row.get('conteudo', '')
        if pd.notna(conteudo) and str(conteudo).strip():
            turmas[key]['com_conteudo'] += 1

# Metricas gerais
total_esp = sum(t['esperadas'] for t in turmas.values())
total_reg = sum(t['registradas'] for t in turmas.values())
conf_geral = total_reg / max(total_esp, 1) * 100

c1, c2, c3 = st.columns(3)
c1.metric("Turmas", len(turmas))
c2.metric("Aulas Registradas", f"{total_reg}/{total_esp}")
c3.metric("Conformidade Geral", f"{conf_geral:.0f}%")

st.markdown("---")

# Cards por turma
for key, t in sorted(turmas.items()):
    conf = t['registradas'] / max(t['esperadas'], 1) * 100
    pct_conteudo = t['com_conteudo'] / max(t['registradas'], 1) * 100

    if conf >= 80:
        cor = '#43a047'
    elif conf >= 50:
        cor = '#ff9800'
    else:
        cor = '#e53935'

    alertas_html = ''
    if conf < 50:
        alertas_html += '<div class="turma-alerta">Conformidade abaixo de 50% — priorize registros desta turma</div>'
    if t['registradas'] > 0 and pct_conteudo < 50:
        alertas_html += '<div class="turma-alerta">Menos de 50% das aulas tem conteudo registrado</div>'

    st.markdown(f"""
    <div class="turma-card" style="border-left-color:{cor};">
        <div class="turma-titulo">{t['serie']} — {t['disciplina']}</div>
        <div class="turma-meta">
            Aulas: {t['registradas']}/{t['esperadas']} ({conf:.0f}%) |
            Com conteudo: {t['com_conteudo']}/{t['registradas']} ({pct_conteudo:.0f}%)
        </div>
        {alertas_html}
    </div>
    """, unsafe_allow_html=True)
