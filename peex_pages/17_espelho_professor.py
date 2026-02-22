"""
PEEX — Espelho do Professor
Score decomposto, comparativo anonimo, caminho de melhoria.
NUNCA mostra nomes ou rankings de outros professores.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit, get_user_role, get_professor_name, ROLE_PROFESSOR
from utils import (
    calcular_semana_letiva, DATA_DIR, UNIDADES_NOMES,
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
)
from components import cabecalho_pagina


# ========== CSS ==========

st.markdown("""
<style>
    .esp-score-card {
        padding: 24px;
        border-radius: 14px;
        text-align: center;
        color: white;
        margin-bottom: 16px;
    }
    .esp-verde { background: linear-gradient(135deg, #2e7d32, #43a047); }
    .esp-amarelo { background: linear-gradient(135deg, #e65100, #ff9800); }
    .esp-vermelho { background: linear-gradient(135deg, #b71c1c, #e53935); }
    .esp-componente {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        margin: 6px 0;
        border-radius: 8px;
        background: #fafafa;
    }
    .esp-comp-nome { flex: 1; font-weight: bold; }
    .esp-comp-peso { font-size: 0.8em; color: #888; min-width: 50px; text-align: right; }
    .esp-comp-bar {
        flex: 2;
        height: 10px;
        background: #e0e0e0;
        border-radius: 5px;
        overflow: hidden;
        margin: 0 12px;
    }
    .esp-comp-fill { height: 100%; border-radius: 5px; }
    .esp-comp-val { font-weight: bold; min-width: 50px; text-align: right; }
    .esp-melhoria {
        padding: 14px 18px;
        margin: 8px 0;
        border-radius: 8px;
        background: #e8f5e9;
        border-left: 4px solid #43a047;
    }
    .esp-comparativo {
        padding: 12px 16px;
        margin: 6px 0;
        border-radius: 8px;
        background: #e3f2fd;
    }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role != ROLE_PROFESSOR:
    st.warning("Acesso restrito a professores.")
    st.stop()


# ========== CALCULO DE SCORE ==========

# Pesos do score do professor
_PESOS = {
    'registro': 0.35,
    'conteudo': 0.25,
    'tarefa': 0.15,
    'recencia': 0.25,
}


def calcular_score_professor(df_aulas, df_horario, prof_nome, semana):
    """Calcula score decomposto do professor.

    Returns:
        dict com componentes e score total (0-100)
    """
    if df_aulas.empty or df_horario.empty:
        return {'total': 0, 'registro': 0, 'conteudo': 0, 'tarefa': 0, 'recencia': 0}

    aulas_prof = df_aulas[df_aulas['professor'] == prof_nome]
    esp_prof = df_horario[df_horario['professor'] == prof_nome]

    total_esperadas = len(esp_prof)
    total_registradas = len(aulas_prof)

    # Registro (35%): % aulas registradas vs esperadas
    registro = min(100, total_registradas / max(total_esperadas, 1) * 100)

    # Conteudo (25%): % aulas com campo conteudo preenchido
    if not aulas_prof.empty and 'conteudo' in aulas_prof.columns:
        com_conteudo = aulas_prof['conteudo'].notna() & (aulas_prof['conteudo'].str.strip() != '')
        conteudo = com_conteudo.sum() / max(len(aulas_prof), 1) * 100
    else:
        conteudo = 0

    # Tarefa (15%): % aulas com tarefa/atividade registrada
    if not aulas_prof.empty and 'tarefa' in aulas_prof.columns:
        com_tarefa = aulas_prof['tarefa'].notna() & (aulas_prof['tarefa'].str.strip() != '')
        tarefa = com_tarefa.sum() / max(len(aulas_prof), 1) * 100
    elif not aulas_prof.empty and 'atividade' in aulas_prof.columns:
        com_tarefa = aulas_prof['atividade'].notna() & (aulas_prof['atividade'].str.strip() != '')
        tarefa = com_tarefa.sum() / max(len(aulas_prof), 1) * 100
    else:
        tarefa = 50  # default se campo nao existe

    # Recencia (25%): penaliza gap recente
    if not aulas_prof.empty and 'data' in aulas_prof.columns:
        try:
            datas = pd.to_datetime(aulas_prof['data'], errors='coerce')
            ultima = datas.max()
            if pd.notna(ultima):
                dias_gap = (pd.Timestamp.now() - ultima).days
                recencia = max(0, 100 - dias_gap * 10)
            else:
                recencia = 0
        except Exception:
            recencia = 50
    else:
        recencia = 50

    total = (
        registro * _PESOS['registro'] +
        conteudo * _PESOS['conteudo'] +
        tarefa * _PESOS['tarefa'] +
        recencia * _PESOS['recencia']
    )

    return {
        'total': round(total, 1),
        'registro': round(registro, 1),
        'conteudo': round(conteudo, 1),
        'tarefa': round(tarefa, 1),
        'recencia': round(recencia, 1),
        'total_esperadas': total_esperadas,
        'total_registradas': total_registradas,
    }


# ========== MAIN ==========

cabecalho_pagina("Meu Espelho", "Seu desempenho decomposto — so voce ve estes dados")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
prof_nome = get_professor_name()

if not prof_nome:
    st.warning("Nome do professor nao configurado. Contate o administrador.")
    st.stop()

st.markdown(f"**Professor(a):** {prof_nome}")

# Carregar dados
df_aulas = carregar_fato_aulas()
df_horario = carregar_horario_esperado()

if df_aulas.empty:
    st.warning("Dados de aulas nao disponiveis.")
    st.stop()

df_aulas = filtrar_ate_hoje(df_aulas)

# Filtrar por unidade do professor
if 'unidade' in df_aulas.columns:
    df_aulas_un = df_aulas[df_aulas['unidade'] == user_unit]
else:
    df_aulas_un = df_aulas

if 'unidade' in df_horario.columns:
    df_horario_un = df_horario[df_horario['unidade'] == user_unit]
else:
    df_horario_un = df_horario

# Score do professor
score = calcular_score_professor(df_aulas_un, df_horario_un, prof_nome, semana)

# Card do score total
total = score['total']
if total >= 75:
    cor = 'esp-verde'
    status = 'BOM DESEMPENHO'
elif total >= 50:
    cor = 'esp-amarelo'
    status = 'PODE MELHORAR'
else:
    cor = 'esp-vermelho'
    status = 'ATENCAO NECESSARIA'

st.markdown(f"""
<div class="esp-score-card {cor}">
    <div style="font-size:0.9em; opacity:0.85;">Seu Score</div>
    <div style="font-size:3em; font-weight:bold;">{total:.0f}/100</div>
    <div style="font-size:1.1em;">{status}</div>
</div>
""", unsafe_allow_html=True)

# Componentes decompostos
st.markdown("### Decomposicao do Score")

componentes = [
    ('Registro de Aulas', 'registro', _PESOS['registro']),
    ('Conteudo Registrado', 'conteudo', _PESOS['conteudo']),
    ('Tarefas/Atividades', 'tarefa', _PESOS['tarefa']),
    ('Recencia', 'recencia', _PESOS['recencia']),
]

for nome, campo, peso in componentes:
    val = score[campo]
    cor_bar = '#2e7d32' if val >= 75 else ('#ff9800' if val >= 50 else '#e53935')
    st.markdown(f"""
    <div class="esp-componente">
        <div class="esp-comp-nome">{nome}</div>
        <div class="esp-comp-bar">
            <div class="esp-comp-fill" style="width:{val:.0f}%; background:{cor_bar};"></div>
        </div>
        <div class="esp-comp-val" style="color:{cor_bar};">{val:.0f}%</div>
        <div class="esp-comp-peso">({peso*100:.0f}%)</div>
    </div>
    """, unsafe_allow_html=True)

# Comparativo anonimo
st.markdown("### Comparativo (anonimo)")
st.caption("Sua posicao vs media — sem nomes de colegas")

# Calcular media da unidade
profs_un = df_horario_un['professor'].unique() if 'professor' in df_horario_un.columns else []
scores_un = []
for p in profs_un:
    s = calcular_score_professor(df_aulas_un, df_horario_un, p, semana)
    scores_un.append(s['total'])

if scores_un:
    media_un = sum(scores_un) / len(scores_un)
    posicao = sum(1 for s in scores_un if s > total) + 1
    total_profs = len(scores_un)

    st.markdown(f"""
    <div class="esp-comparativo">
        <strong>Sua posicao:</strong> {posicao}o de {total_profs} professores da unidade<br>
        <strong>Seu score:</strong> {total:.0f} | <strong>Media da unidade:</strong> {media_un:.0f}
    </div>
    """, unsafe_allow_html=True)

    delta = total - media_un
    if delta > 0:
        st.success(f"Voce esta {delta:.0f} pontos ACIMA da media da unidade!")
    elif delta < -10:
        st.warning(f"Voce esta {abs(delta):.0f} pontos abaixo da media. Veja as sugestoes abaixo.")

# Caminho de melhoria
st.markdown("### Caminho de Melhoria")

sugestoes = []
if score['registro'] < 75:
    gap = score['total_esperadas'] - score['total_registradas']
    sugestoes.append(f"Registre {gap} aula(s) pendente(s) para elevar o componente de Registro.")
if score['conteudo'] < 75:
    sugestoes.append("Adicione descricao de conteudo em todas as suas aulas registradas.")
if score['tarefa'] < 75:
    sugestoes.append("Registre tarefas/atividades nas suas aulas para ganhar pontos.")
if score['recencia'] < 75:
    sugestoes.append("Registre aulas com mais frequencia — gaps longos penalizam o score.")

if sugestoes:
    for s in sugestoes:
        st.markdown(f"""
        <div class="esp-melhoria">{s}</div>
        """, unsafe_allow_html=True)

    # Projecao
    if score['registro'] < 75:
        melhoria_estimada = min(100, total + 15)
        st.info(f"Se registrar as aulas pendentes, seu score pode subir para ~{melhoria_estimada:.0f}")
else:
    st.success("Parabens! Seu score esta acima de 75 em todos os componentes.")
