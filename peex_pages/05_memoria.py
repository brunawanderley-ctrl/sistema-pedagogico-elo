"""
PEEX — Memoria Institucional (Vacinas)
Catalogo de crises anteriores + intervencoes + resultados.
Quando dados atuais casam com gatilho, alerta preventivo.
"""

import json
import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_role, ROLE_CEO, ROLE_DIRETOR
from utils import calcular_semana_letiva, UNIDADES_NOMES, WRITABLE_DIR
from components import cabecalho_pagina
from engine import carregar_missoes_pregeradas


# ========== CSS ==========

st.markdown("""
<style>
    .vacina-card {
        padding: 16px 20px;
        margin: 8px 0;
        border-radius: 10px;
        border-left: 5px solid;
    }
    .vacina-ativa { background: #ffebee; border-left-color: #f44336; }
    .vacina-catalogada { background: #e8f5e9; border-left-color: #43a047; }
    .vacina-titulo { font-weight: bold; font-size: 1.05em; }
    .vacina-meta { font-size: 0.85em; color: #666; margin-top: 4px; }
    .vacina-intervencao { background: #e3f2fd; padding: 8px 14px; border-radius: 6px; margin: 6px 0; }
    .alerta-preventivo {
        padding: 14px 18px;
        margin: 8px 0;
        border-radius: 8px;
        background: #fff3e0;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role not in (ROLE_CEO, ROLE_DIRETOR):
    st.warning("Acesso restrito a CEO e Diretores.")
    st.stop()


# ========== PERSISTENCIA ==========

_VACINAS_PATH = WRITABLE_DIR / "vacinas_institucionais.json"


def _carregar_vacinas():
    if _VACINAS_PATH.exists():
        try:
            with open(_VACINAS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return _VACINAS_PADRAO.copy()


def _salvar_vacinas(vacinas):
    with open(_VACINAS_PATH, 'w', encoding='utf-8') as f:
        json.dump(vacinas, f, ensure_ascii=False, indent=2)


# Vacinas pre-catalogadas (banco inicial)
_VACINAS_PADRAO = [
    {
        'id': 'v1',
        'titulo': 'Queda massiva de registro pos-ferias',
        'gatilho': 'Conformidade cai >15pp apos periodo de ferias',
        'tipo_gatilho': 'conformidade_queda',
        'limiar': 15,
        'intervencao': 'Reuniao de retorno com foco em expectativas. Campanha "Primeira semana 100%". Meta visivel no mural.',
        'resultado_anterior': 'Recuperacao em 2 semanas quando aplicado (2025).',
        'semana_registro': 0,
    },
    {
        'id': 'v2',
        'titulo': 'Professor desistente (3+ semanas silencioso)',
        'gatilho': 'Professor sem registro por 3+ semanas consecutivas',
        'tipo_gatilho': 'prof_silencioso',
        'limiar': 3,
        'intervencao': 'Conversa individual (nao repreensiva). Oferecer suporte tecnico. Se recusa persistir, escalar para RH.',
        'resultado_anterior': '70% dos casos resolvidos na 1a conversa.',
        'semana_registro': 0,
    },
    {
        'id': 'v3',
        'titulo': 'Evasao pontual por serie',
        'gatilho': 'Frequencia de uma serie cai >5pp em 1 semana',
        'tipo_gatilho': 'frequencia_queda',
        'limiar': 5,
        'intervencao': 'Busca ativa imediata. Identificar se ha evento externo (doenca, evento comunitario). Contato com familias.',
        'resultado_anterior': 'Retorno medio em 3 dias quando busca ativa e iniciada no mesmo dia.',
        'semana_registro': 0,
    },
    {
        'id': 'v4',
        'titulo': 'Surto de ocorrencias graves',
        'gatilho': 'Mais de 10 ocorrencias graves em 1 semana na mesma unidade',
        'tipo_gatilho': 'ocorrencias_surto',
        'limiar': 10,
        'intervencao': 'Reuniao emergencial com equipe disciplinar. Revisar protocolo. Ativar mediacao. Comunicar familias.',
        'resultado_anterior': 'Reducao de 60% nas ocorrencias na semana seguinte.',
        'semana_registro': 0,
    },
]


# ========== VERIFICACAO DE GATILHOS ==========

def verificar_gatilhos(vacinas, missoes):
    """Verifica se alguma vacina deve ser ativada com base nos dados atuais.

    Returns:
        lista de dicts {vacina, motivo}
    """
    alertas = []

    for v in vacinas:
        tipo = v.get('tipo_gatilho', '')

        if tipo == 'prof_silencioso':
            profs_silenciosos = [b for b in missoes
                                 if b.get('tipo') == 'PROF_SILENCIOSO'
                                 and b.get('semanas_ativas', 0) >= v.get('limiar', 3)]
            if profs_silenciosos:
                alertas.append({
                    'vacina': v,
                    'motivo': f"{len(profs_silenciosos)} professor(es) silencioso(s) por {v.get('limiar', 3)}+ semanas",
                    'n_casos': len(profs_silenciosos),
                })

        elif tipo == 'ocorrencias_surto':
            ocorr_missoes = [b for b in missoes
                              if b.get('tipo') == 'ALUNO_OCORRENCIA'
                              and b.get('n_afetados', 0) >= v.get('limiar', 10)]
            if ocorr_missoes:
                alertas.append({
                    'vacina': v,
                    'motivo': f"Surto de ocorrencias detectado",
                    'n_casos': len(ocorr_missoes),
                })

    return alertas


# ========== MAIN ==========

cabecalho_pagina("Memoria Institucional", "Vacinas contra crises recorrentes")

semana = calcular_semana_letiva()
vacinas = _carregar_vacinas()

# Verificar alertas preventivos
missoes = carregar_missoes_pregeradas()
alertas = verificar_gatilhos(vacinas, missoes)

if alertas:
    st.markdown("### Alertas Preventivos Ativos")
    for alerta in alertas:
        v = alerta['vacina']
        st.markdown(f"""
        <div class="alerta-preventivo">
            <strong>ALERTA: {v['titulo']}</strong><br>
            {alerta['motivo']}<br>
            <div class="vacina-intervencao">
                <strong>Intervencao recomendada:</strong> {v['intervencao']}
            </div>
            <div class="vacina-meta">Resultado anterior: {v.get('resultado_anterior', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

# Catalogo de vacinas
st.markdown("### Catalogo de Vacinas")

for v in vacinas:
    ativa = any(a['vacina']['id'] == v['id'] for a in alertas)
    card_class = 'vacina-card vacina-ativa' if ativa else 'vacina-card vacina-catalogada'

    st.markdown(f"""
    <div class="{card_class}">
        <div class="vacina-titulo">{'⚠️ ' if ativa else '💉 '}{v['titulo']}</div>
        <div class="vacina-meta">Gatilho: {v['gatilho']}</div>
        <div class="vacina-intervencao">{v['intervencao']}</div>
        <div class="vacina-meta">Resultado anterior: {v.get('resultado_anterior', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)

# Adicionar nova vacina
st.markdown("---")
st.markdown("### Registrar Nova Vacina")
with st.form("nova_vacina"):
    titulo = st.text_input("Titulo da crise/vacina")
    gatilho = st.text_input("Gatilho (quando ativar)")
    intervencao = st.text_area("Intervencao recomendada", height=80)
    resultado = st.text_input("Resultado quando aplicada anteriormente")
    submitted = st.form_submit_button("Registrar Vacina")

    if submitted and titulo and intervencao:
        nova = {
            'id': f'v_custom_{len(vacinas)}',
            'titulo': titulo,
            'gatilho': gatilho,
            'tipo_gatilho': 'custom',
            'limiar': 0,
            'intervencao': intervencao,
            'resultado_anterior': resultado,
            'semana_registro': semana,
        }
        vacinas.append(nova)
        _salvar_vacinas(vacinas)
        st.rerun()

# Estatisticas
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("Total Vacinas", len(vacinas))
c2.metric("Alertas Ativos", len(alertas))
c3.metric("Customizadas", sum(1 for v in vacinas if v.get('tipo_gatilho') == 'custom'))
