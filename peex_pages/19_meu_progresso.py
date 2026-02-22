"""
PEEX — Meu Progresso (Professor)
Evolucao temporal do score, estrelas acumuladas, conquistas.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit, get_user_role, get_professor_name, ROLE_PROFESSOR
from utils import (
    calcular_semana_letiva, calcular_trimestre,
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
    UNIDADES_NOMES,
)
from components import cabecalho_pagina


# ========== CSS ==========

st.markdown("""
<style>
    .prog-conquista {
        padding: 12px 16px;
        margin: 6px 0;
        border-radius: 8px;
        background: #fff8e1;
        border-left: 4px solid #ffa000;
    }
    .prog-conquista-desbloqueada {
        background: #e8f5e9;
        border-left-color: #43a047;
    }
    .prog-titulo { font-weight: bold; }
    .prog-desc { font-size: 0.85em; color: #666; }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role != ROLE_PROFESSOR:
    st.stop()


# ========== CALCULO DE SCORE (reutiliza logica do espelho) ==========

_PESOS = {'registro': 0.35, 'conteudo': 0.25, 'tarefa': 0.15, 'recencia': 0.25}


def _score_simples(df_aulas_prof, df_horario_prof):
    """Calculo simplificado do score do professor."""
    total_esp = len(df_horario_prof)
    total_reg = len(df_aulas_prof)
    registro = min(100, total_reg / max(total_esp, 1) * 100)

    if not df_aulas_prof.empty and 'conteudo' in df_aulas_prof.columns:
        com_conteudo = df_aulas_prof['conteudo'].notna() & (df_aulas_prof['conteudo'].str.strip() != '')
        conteudo = com_conteudo.sum() / max(len(df_aulas_prof), 1) * 100
    else:
        conteudo = 0

    total = registro * _PESOS['registro'] + conteudo * _PESOS['conteudo'] + 50 * _PESOS['tarefa'] + 50 * _PESOS['recencia']
    return round(total, 1)


# ========== CONQUISTAS ==========

CONQUISTAS = [
    {'id': 'primeira_semana', 'nome': 'Primeiro Passo', 'desc': 'Registrou aulas na primeira semana',
     'check': lambda stats: stats.get('semana_inicio', 99) <= 2},
    {'id': 'conf_70', 'nome': 'Constante', 'desc': 'Conformidade acima de 70%',
     'check': lambda stats: stats.get('conformidade', 0) >= 70},
    {'id': 'conf_90', 'nome': 'Excelente', 'desc': 'Conformidade acima de 90%',
     'check': lambda stats: stats.get('conformidade', 0) >= 90},
    {'id': 'conteudo_100', 'nome': 'Detalhista', 'desc': '100% das aulas com conteudo registrado',
     'check': lambda stats: stats.get('pct_conteudo', 0) >= 100},
    {'id': 'sequencia_5', 'nome': 'Sequencia', 'desc': '5 semanas consecutivas com registro',
     'check': lambda stats: stats.get('sequencia_max', 0) >= 5},
    {'id': 'turmas_todas', 'nome': 'Cobertura Total', 'desc': 'Todas as turmas com registro',
     'check': lambda stats: stats.get('turmas_cobertas', 0) >= stats.get('turmas_total', 1)},
]


# ========== MAIN ==========

cabecalho_pagina("Meu Progresso", "Evolucao do seu desempenho ao longo do ano")

semana = calcular_semana_letiva()
trimestre = calcular_trimestre(semana)
user_unit = get_user_unit() or 'BV'
prof_nome = get_professor_name()

if not prof_nome:
    st.warning("Nome do professor nao configurado. Contate o administrador.")
    st.stop()

st.markdown(f"**Professor(a):** {prof_nome} | **Semana {semana}/47** | **{trimestre}o Trimestre**")

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

# Score atual
score_atual = _score_simples(aulas_prof, esp_prof)

total_reg = len(aulas_prof)
total_esp = len(esp_prof)
conf = total_reg / max(total_esp, 1) * 100

# Metricas
c1, c2, c3, c4 = st.columns(4)
c1.metric("Score Atual", f"{score_atual:.0f}/100")
c2.metric("Conformidade", f"{conf:.0f}%")
c3.metric("Aulas Registradas", total_reg)
c4.metric("Semana", f"{semana}/47")

st.markdown("---")

# Evolucao temporal (se houver dados por semana)
st.markdown("### Evolucao Semanal")

if not aulas_prof.empty and 'data' in aulas_prof.columns:
    try:
        aulas_prof_copy = aulas_prof.copy()
        aulas_prof_copy['data_dt'] = pd.to_datetime(aulas_prof_copy['data'], errors='coerce')
        aulas_prof_copy = aulas_prof_copy.dropna(subset=['data_dt'])

        from utils import INICIO_ANO_LETIVO
        aulas_prof_copy['semana_num'] = ((aulas_prof_copy['data_dt'] - pd.Timestamp(INICIO_ANO_LETIVO)).dt.days // 7 + 1).clip(lower=1)

        por_semana = aulas_prof_copy.groupby('semana_num').size().reset_index(name='aulas')
        por_semana = por_semana.sort_values('semana_num')

        if len(por_semana) > 1:
            st.line_chart(por_semana.set_index('semana_num')['aulas'], use_container_width=True)
        else:
            st.info("Dados insuficientes para grafico de evolucao (precisa 2+ semanas).")

        # Sequencia
        semanas_com_registro = set(por_semana['semana_num'].tolist())
        sequencia = 0
        seq_max = 0
        for s in range(1, semana + 1):
            if s in semanas_com_registro:
                sequencia += 1
                seq_max = max(seq_max, sequencia)
            else:
                sequencia = 0

        semana_inicio = min(semanas_com_registro) if semanas_com_registro else 99
    except Exception:
        seq_max = 0
        semana_inicio = 99
        st.info("Nao foi possivel processar evolucao temporal.")
else:
    seq_max = 0
    semana_inicio = 99
    st.info("Dados temporais nao disponiveis.")

# Conteudo
if not aulas_prof.empty and 'conteudo' in aulas_prof.columns:
    com_conteudo = (aulas_prof['conteudo'].notna() & (aulas_prof['conteudo'].str.strip() != '')).sum()
    pct_conteudo = com_conteudo / max(len(aulas_prof), 1) * 100
else:
    pct_conteudo = 0

# Turmas
if not esp_prof.empty and 'serie' in esp_prof.columns:
    turmas_total = esp_prof[['serie', 'disciplina']].drop_duplicates().shape[0] if 'disciplina' in esp_prof.columns else esp_prof['serie'].nunique()
else:
    turmas_total = 0

if not aulas_prof.empty and 'serie' in aulas_prof.columns:
    turmas_cobertas = aulas_prof[['serie', 'disciplina']].drop_duplicates().shape[0] if 'disciplina' in aulas_prof.columns else aulas_prof['serie'].nunique()
else:
    turmas_cobertas = 0

# Conquistas
st.markdown("---")
st.markdown("### Conquistas")

stats = {
    'conformidade': conf,
    'pct_conteudo': pct_conteudo,
    'sequencia_max': seq_max,
    'semana_inicio': semana_inicio,
    'turmas_total': turmas_total,
    'turmas_cobertas': turmas_cobertas,
}

desbloqueadas = 0
for c in CONQUISTAS:
    ativo = c['check'](stats)
    if ativo:
        desbloqueadas += 1
    card_class = 'prog-conquista prog-conquista-desbloqueada' if ativo else 'prog-conquista'
    icone = '🏅' if ativo else '🔒'
    st.markdown(f"""
    <div class="{card_class}">
        <div class="prog-titulo">{icone} {c['nome']}</div>
        <div class="prog-desc">{c['desc']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.metric("Conquistas Desbloqueadas", f"{desbloqueadas}/{len(CONQUISTAS)}")
