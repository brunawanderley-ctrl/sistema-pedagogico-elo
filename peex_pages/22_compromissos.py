"""
PEEX — Compromissos (Diretor)
Compromissos registrados em reuniao + status.
"""

import json
import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit, get_user_role, ROLE_DIRETOR, ROLE_CEO
from utils import calcular_semana_letiva, UNIDADES_NOMES, WRITABLE_DIR
from components import cabecalho_pagina


# ========== CSS ==========

st.markdown("""
<style>
    .comp-card {
        padding: 14px 18px;
        margin: 6px 0;
        border-radius: 8px;
        border-left: 4px solid;
        background: #fafafa;
    }
    .comp-titulo { font-weight: bold; }
    .comp-meta { font-size: 0.85em; color: #666; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role not in (ROLE_CEO, ROLE_DIRETOR):
    st.warning("Acesso restrito a CEO e Diretores.")
    st.stop()


# ========== PERSISTENCIA ==========

def _path_compromissos(unidade):
    return WRITABLE_DIR / f"compromissos_diretor_{unidade}.json"


def carregar_compromissos(unidade):
    path = _path_compromissos(unidade)
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def salvar_compromissos(unidade, compromissos):
    path = _path_compromissos(unidade)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(compromissos, f, ensure_ascii=False, indent=2)


# ========== MAIN ==========

cabecalho_pagina("Compromissos", "Compromissos registrados em reuniao")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)

compromissos = carregar_compromissos(user_unit)

# Adicionar novo compromisso
st.markdown("### Novo Compromisso")
with st.form("novo_compromisso"):
    titulo = st.text_input("Descricao do compromisso")
    c1, c2 = st.columns(2)
    with c1:
        responsavel = st.text_input("Responsavel")
    with c2:
        prazo = st.text_input("Prazo", value="sexta-feira")
    submitted = st.form_submit_button("Adicionar")

    if submitted and titulo:
        compromissos.append({
            'titulo': titulo,
            'responsavel': responsavel,
            'prazo': prazo,
            'status': 'pendente',
            'criado_em': datetime.now().isoformat(),
            'semana': semana,
        })
        salvar_compromissos(user_unit, compromissos)
        st.rerun()

# Listar compromissos
st.markdown("---")
st.markdown(f"### Compromissos — {nome_un}")

cores_status = {
    'pendente': '#ffa000',
    'em_andamento': '#1565c0',
    'concluido': '#43a047',
}

if not compromissos:
    st.info("Nenhum compromisso registrado ainda.")
else:
    alterado = False
    for i, c in enumerate(compromissos):
        cor = cores_status.get(c.get('status', 'pendente'), '#9e9e9e')
        st.markdown(f"""
        <div class="comp-card" style="border-left-color:{cor};">
            <div class="comp-titulo">{c['titulo']}</div>
            <div class="comp-meta">
                Responsavel: {c.get('responsavel', '-')} |
                Prazo: {c.get('prazo', '-')} |
                Semana {c.get('semana', '?')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        opcoes = ['Pendente', 'Em andamento', 'Concluido']
        mapa = {'pendente': 0, 'em_andamento': 1, 'concluido': 2}
        status_novo = st.radio(
            "Status:",
            opcoes,
            index=mapa.get(c.get('status', 'pendente'), 0),
            key=f"comp_status_{i}",
            horizontal=True,
        )
        status_key = status_novo.lower().replace(' ', '_').replace('í', 'i')
        if status_key != c.get('status', 'pendente'):
            c['status'] = status_key
            alterado = True

    if alterado:
        salvar_compromissos(user_unit, compromissos)

    # Resumo
    total = len(compromissos)
    concluidos = sum(1 for c in compromissos if c.get('status') == 'concluido')
    st.markdown("---")
    st.metric("Progresso", f"{concluidos}/{total}", f"{round(concluidos/max(total,1)*100)}%")
