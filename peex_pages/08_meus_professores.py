"""
PEEX — Meus Professores (Coordenador)
Agrupados por saude (verde/amarelo/vermelho) + prescricao individualizada.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit
from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado, DATA_DIR,
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
    UNIDADES_NOMES, CONFORMIDADE_META, CONFORMIDADE_BAIXO,
)
from components import cabecalho_pagina


# ========== CSS ==========

st.markdown("""
<style>
    .prof-card {
        padding: 14px 18px;
        margin: 6px 0;
        border-radius: 8px;
        border-left: 5px solid;
    }
    .prof-verde { background: #e8f5e9; border-left-color: #43a047; }
    .prof-amarelo { background: #fff8e1; border-left-color: #ffa000; }
    .prof-vermelho { background: #ffebee; border-left-color: #e53935; }
    .prof-nome { font-weight: bold; font-size: 1.05em; }
    .prof-meta { font-size: 0.85em; color: #666; margin-top: 4px; }
    .prof-prescricao {
        background: #e3f2fd;
        padding: 8px 14px;
        border-radius: 6px;
        margin-top: 6px;
        font-size: 0.9em;
    }
    .prof-resumo {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


# ========== PRESCRICOES ==========

def _prescricao(prof_row):
    """Gera prescricao individualizada para um professor."""
    conf = prof_row.get('conformidade', 0)
    pct_conteudo = prof_row.get('pct_conteudo', 0)
    dias_gap = prof_row.get('dias_sem_registro', 0)

    prescricoes = []

    if dias_gap > 7:
        prescricoes.append(f"Sem registro ha {dias_gap} dias. Conversa individual urgente.")
    elif dias_gap > 3:
        prescricoes.append(f"Ultimo registro ha {dias_gap} dias. Verifique se ha dificuldade.")

    if conf < 30:
        prescricoes.append("Conformidade critica. Acompanhamento diario necessario.")
    elif conf < 50:
        prescricoes.append("Conformidade baixa. Definir meta semanal com o professor.")
    elif conf < 70:
        prescricoes.append("Conformidade em zona de atencao. Reforcar importancia do registro.")

    if pct_conteudo < 30 and conf > 30:
        prescricoes.append("Registra aulas mas sem conteudo. Orientar sobre preenchimento completo.")

    if not prescricoes:
        prescricoes.append("Desempenho adequado. Manter acompanhamento regular.")

    return prescricoes


# ========== MAIN ==========

cabecalho_pagina("Meus Professores", "Saude da equipe docente com prescricoes")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)

df_aulas = carregar_fato_aulas()
df_horario = carregar_horario_esperado()

if df_aulas.empty or df_horario.empty:
    st.warning("Dados insuficientes. Execute a extracao do SIGA.")
    st.stop()

df_aulas = filtrar_ate_hoje(df_aulas)

# Filtrar por unidade
hor_un = df_horario[df_horario['unidade'] == user_unit]
aulas_un = df_aulas[df_aulas['unidade'] == user_unit]

if hor_un.empty:
    st.warning(f"Nenhum professor encontrado para {nome_un}.")
    st.stop()

# Calcular metricas por professor
profs_esperados = hor_un.groupby('professor').agg(
    slots=('disciplina', 'count'),
    disciplinas=('disciplina', lambda x: ', '.join(sorted(x.unique()))),
    series=('serie', lambda x: ', '.join(sorted(x.unique()))),
).reset_index()

registros = aulas_un.groupby('professor').agg(
    n_registros=('disciplina', 'count'),
).reset_index()

# Conteudo
if 'conteudo' in aulas_un.columns:
    conteudo_ok = aulas_un[aulas_un['conteudo'].notna() & (aulas_un['conteudo'].str.strip() != '')]
    conteudo_por_prof = conteudo_ok.groupby('professor').size().reset_index(name='com_conteudo')
else:
    conteudo_por_prof = pd.DataFrame(columns=['professor', 'com_conteudo'])

# Ultimo registro
if 'data' in aulas_un.columns:
    aulas_un_copy = aulas_un.copy()
    aulas_un_copy['data_dt'] = pd.to_datetime(aulas_un_copy['data'], errors='coerce')
    ultimo_reg = aulas_un_copy.groupby('professor')['data_dt'].max().reset_index()
    ultimo_reg.columns = ['professor', 'ultima_data']
else:
    ultimo_reg = pd.DataFrame(columns=['professor', 'ultima_data'])

# Merge
df = profs_esperados.merge(registros, on='professor', how='left')
df = df.merge(conteudo_por_prof, on='professor', how='left')
df = df.merge(ultimo_reg, on='professor', how='left')

df['n_registros'] = df['n_registros'].fillna(0).astype(int)
df['com_conteudo'] = df['com_conteudo'].fillna(0).astype(int)
esperado = df['slots'] * semana
df['conformidade'] = (df['n_registros'] / esperado.clip(lower=1) * 100).round(0)
df['pct_conteudo'] = (df['com_conteudo'] / df['n_registros'].clip(lower=1) * 100).round(0)

# Dias sem registro
hoje = pd.Timestamp.now()
df['dias_sem_registro'] = 0
if 'ultima_data' in df.columns:
    df['dias_sem_registro'] = df['ultima_data'].apply(
        lambda x: (hoje - x).days if pd.notna(x) else 999
    )

# Classificar
verde = df[df['conformidade'] >= 85].sort_values('conformidade', ascending=False)
amarelo = df[(df['conformidade'] >= 50) & (df['conformidade'] < 85)].sort_values('conformidade')
vermelho = df[df['conformidade'] < 50].sort_values('conformidade')

# Resumo
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="prof-resumo" style="background: linear-gradient(135deg, #2e7d32, #43a047);">
        <div style="font-size:2em;">{len(verde)}</div>
        <div>SAUDAVEIS</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="prof-resumo" style="background: linear-gradient(135deg, #e65100, #ff9800);">
        <div style="font-size:2em;">{len(amarelo)}</div>
        <div>ATENCAO</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="prof-resumo" style="background: linear-gradient(135deg, #b71c1c, #e53935);">
        <div style="font-size:2em;">{len(vermelho)}</div>
        <div>CRITICOS</div>
    </div>
    """, unsafe_allow_html=True)

# Filtro
filtro = st.radio("Visualizar:", ['Todos', 'Criticos primeiro', 'Saudaveis'], horizontal=True)

if filtro == 'Criticos primeiro':
    lista = pd.concat([vermelho, amarelo, verde])
elif filtro == 'Saudaveis':
    lista = verde
else:
    lista = pd.concat([vermelho, amarelo, verde])

st.markdown("---")

# Cards com prescricao
for _, row in lista.iterrows():
    conf = row['conformidade']
    if conf >= 85:
        card_class = 'prof-card prof-verde'
    elif conf >= 50:
        card_class = 'prof-card prof-amarelo'
    else:
        card_class = 'prof-card prof-vermelho'

    prescricoes = _prescricao(row)

    prescricao_html = ''
    if conf < 85:
        prescricao_html = '<div class="prof-prescricao"><strong>Prescricao:</strong><br>'
        prescricao_html += '<br>'.join(f'- {p}' for p in prescricoes)
        prescricao_html += '</div>'

    st.markdown(f"""
    <div class="{card_class}">
        <div class="prof-nome">{row['professor']}</div>
        <div class="prof-meta">
            Conformidade: {conf:.0f}% |
            Aulas: {row['n_registros']}/{int(row['slots'] * semana)} |
            Conteudo: {row['pct_conteudo']:.0f}% |
            Disciplinas: {row['disciplinas']}
        </div>
        <div class="prof-meta">Series: {row['series']}</div>
        {prescricao_html}
    </div>
    """, unsafe_allow_html=True)
