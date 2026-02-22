"""
PEEX — Plano de Acao Semanal
3-5 acoes concretas geradas a partir das missoes + nudge + persistencia.
"""

import json
import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit, get_user_role
from utils import calcular_semana_letiva, UNIDADES_NOMES, WRITABLE_DIR
from components import cabecalho_pagina
from engine import carregar_missoes_pregeradas
from narrativa import gerar_nudge


# ========== CSS ==========

st.markdown("""
<style>
    .acao-card {
        padding: 14px 18px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid;
        background: #fafafa;
    }
    .acao-titulo { font-weight: bold; font-size: 1em; margin-bottom: 6px; }
    .acao-meta { font-size: 0.85em; color: #666; }
    .nudge-semanal {
        background: #e8eaf6;
        border-radius: 10px;
        padding: 14px 20px;
        margin: 12px 0;
        font-style: italic;
        color: #283593;
    }
</style>
""", unsafe_allow_html=True)


# ========== PERSISTENCIA ==========

def _plano_path(semana, unidade):
    return WRITABLE_DIR / f"plano_acao_sem{semana}_{unidade}.json"


def carregar_plano(semana, unidade):
    path = _plano_path(semana, unidade)
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def salvar_plano(semana, unidade, plano):
    path = _plano_path(semana, unidade)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(plano, f, ensure_ascii=False, indent=2)


def gerar_plano_automatico(missoes, semana, unidade):
    """Gera plano de acao a partir das missoes."""
    acoes = []
    for b in missoes[:5]:
        como = b.get('como', [])
        acoes.append({
            'titulo': como[0] if como else f"Resolver: {b.get('tipo', '')}",
            'tipo_missao': b.get('tipo', ''),
            'responsavel': '',
            'prazo': 'sexta-feira',
            'status': 'nao_iniciada',
            'nota': '',
        })

    return {
        'semana': semana,
        'unidade': unidade,
        'gerado_em': datetime.now().isoformat(),
        'acoes': acoes[:5],
    }


# ========== NUDGES SEMANAIS ==========

_NUDGES_SEMANAIS = [
    "Coordenadores PEEX sao guardioes: cada registro e uma semente plantada.",
    "Uma conversa de 10 minutos pode mudar a semana inteira de um professor.",
    "23 de 28 coordenadores ja completaram o plano esta semana. Voce tambem pode.",
    "Quem registra primeiro, resolve primeiro. Comece pela missao #1.",
    "Pequenas acoes consistentes vencem grandes planos nunca executados.",
]


# ========== MAIN ==========

cabecalho_pagina("Plano de Acao Semanal", "Suas acoes concretas para esta semana")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)

# Carregar ou gerar plano
plano = carregar_plano(semana, user_unit)
if plano is None:
    missoes = carregar_missoes_pregeradas(user_unit)
    plano = gerar_plano_automatico(missoes, semana, user_unit)
    salvar_plano(semana, user_unit, plano)

# Nudge da semana
nudge_idx = (semana - 1) % len(_NUDGES_SEMANAIS)
st.markdown(f'<div class="nudge-semanal">{_NUDGES_SEMANAIS[nudge_idx]}</div>', unsafe_allow_html=True)

# Acoes
st.markdown(f"### Semana {semana} — {nome_un}")

cores_status = {
    'nao_iniciada': '#9e9e9e',
    'em_andamento': '#ffa000',
    'resolvida': '#43a047',
}

alterado = False
acoes = plano.get('acoes', [])

for i, acao in enumerate(acoes):
    cor = cores_status.get(acao.get('status', 'nao_iniciada'), '#9e9e9e')

    st.markdown(f"""
    <div class="acao-card" style="border-left-color:{cor};">
        <div class="acao-titulo">{i+1}. {acao['titulo']}</div>
        <div class="acao-meta">Prazo: {acao.get('prazo', 'sexta')} | Tipo: {acao.get('tipo_missao', '-')}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        nota = st.text_input(
            "Nota/observacao:",
            value=acao.get('nota', ''),
            key=f"plano_nota_{i}",
            label_visibility="collapsed",
            placeholder="Adicionar nota...",
        )
        if nota != acao.get('nota', ''):
            acao['nota'] = nota
            alterado = True

    with c2:
        opcoes = ['Nao iniciada', 'Em andamento', 'Resolvida']
        mapa = {'nao_iniciada': 0, 'em_andamento': 1, 'resolvida': 2}
        status_novo = st.radio(
            "Status:",
            opcoes,
            index=mapa.get(acao.get('status', 'nao_iniciada'), 0),
            key=f"plano_status_{i}",
            horizontal=True,
        )
        status_key = status_novo.lower().replace(' ', '_').replace('ã', 'a')
        if status_key != acao.get('status', 'nao_iniciada'):
            acao['status'] = status_key
            alterado = True

if alterado:
    plano['acoes'] = acoes
    plano['atualizado_em'] = datetime.now().isoformat()
    salvar_plano(semana, user_unit, plano)

# Resumo
st.markdown("---")
total = len(acoes)
resolvidas = sum(1 for a in acoes if a.get('status') == 'resolvida')
em_andamento = sum(1 for a in acoes if a.get('status') == 'em_andamento')

c1, c2, c3 = st.columns(3)
c1.metric("Total", total)
c2.metric("Em andamento", em_andamento)
c3.metric("Resolvidas", resolvidas, f"{resolvidas}/{total}" if total else None)

if resolvidas == total and total > 0:
    st.balloons()
    st.success("Todas as acoes resolvidas! Excelente trabalho!")
