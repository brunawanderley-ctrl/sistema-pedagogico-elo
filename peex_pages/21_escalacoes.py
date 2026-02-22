"""
PEEX — Escalacoes (Diretor)
Missoes que subiram para nivel 2+ vindas dos coordenadores.
"""

import streamlit as st
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit, get_user_role, ROLE_DIRETOR, ROLE_CEO
from utils import calcular_semana_letiva, UNIDADES_NOMES, WRITABLE_DIR
from components import cabecalho_pagina
from missoes_historico import obter_historico_completo
from peex_utils import nivel_escalacao, info_escalacao
from peex_config import NIVEIS_ESCALACAO


# ========== CSS ==========

st.markdown("""
<style>
    .esc-card {
        padding: 16px 20px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 5px solid;
    }
    .esc-titulo { font-weight: bold; font-size: 1.05em; margin-bottom: 6px; }
    .esc-meta { font-size: 0.85em; color: #666; }
    .esc-nivel {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 10px;
        color: white;
        font-size: 0.8em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role not in (ROLE_CEO, ROLE_DIRETOR):
    st.stop()


# ========== MAIN ==========

cabecalho_pagina("Escalacoes", "Missoes que precisam da sua intervencao")

semana = calcular_semana_letiva()
user_unit = get_user_unit()

# Carregar historico e filtrar escalacoes
historico = obter_historico_completo()

escalacoes = []
for fp, entry in historico.items():
    sem_ativas = entry.get('semanas_ativas', 0)
    nivel = nivel_escalacao(sem_ativas)
    if nivel < 2:  # Diretor so ve nivel 2+
        continue
    un = entry.get('unidade', '')
    if user_unit and un != user_unit and role != 'ceo':
        continue

    esc_info = info_escalacao(nivel)
    escalacoes.append({
        **entry,
        'nivel_esc': nivel,
        'esc_info': esc_info,
    })

# Ordenar por nivel (maior primeiro) e semanas ativas
escalacoes.sort(key=lambda x: (-x['nivel_esc'], -x.get('semanas_ativas', 0)))

st.markdown(f"### {len(escalacoes)} escalacao(oes) ativa(s)")

if not escalacoes:
    st.success("Nenhuma escalacao pendente. As coordenacoes estao resolvendo as missoes.")
else:
    # Protocolo de escalacao
    with st.expander("Protocolo de Escalacao"):
        for n in NIVEIS_ESCALACAO:
            st.markdown(
                f"**Nivel {n['nivel']} — {n['nome']}**: {n['quando']} → {n['acao_direcao']}"
            )

    # Cards
    _ASSUMIR_PATH = WRITABLE_DIR / "escalacoes_assumidas.json"

    def carregar_assumidas():
        if _ASSUMIR_PATH.exists():
            try:
                with open(_ASSUMIR_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def salvar_assumida(fp, nota=""):
        assumidas = carregar_assumidas()
        assumidas[fp] = {
            'assumida_em': str(semana),
            'nota': nota,
        }
        with open(_ASSUMIR_PATH, 'w', encoding='utf-8') as f:
            json.dump(assumidas, f, ensure_ascii=False, indent=2)

    assumidas = carregar_assumidas()

    for i, esc in enumerate(escalacoes):
        nivel = esc['nivel_esc']
        esc_info = esc['esc_info']
        cor = esc_info['cor'] if esc_info else '#607D8B'
        nome_nivel = esc_info['nome'] if esc_info else f'N{nivel}'
        un_nome = UNIDADES_NOMES.get(esc.get('unidade', ''), esc.get('unidade', ''))
        fp = esc.get('fingerprint', '')
        ja_assumida = fp in assumidas

        st.markdown(f"""
        <div class="esc-card" style="border-left-color:{cor};">
            <span class="esc-nivel" style="background:{cor};">Nivel {nivel} — {nome_nivel}</span>
            <div class="esc-titulo">{esc.get('o_que', esc.get('tipo', ''))[:100]}</div>
            <div class="esc-meta">
                {un_nome} | {esc.get('semanas_ativas', 0)} semanas ativas |
                Score: {esc.get('score', 0)} | Tipo: {esc.get('tipo', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if ja_assumida:
            st.success(f"Assumida na semana {assumidas[fp].get('assumida_em', '?')}")
        else:
            if st.button(f"Assumir esta escalacao", key=f"assumir_{i}"):
                salvar_assumida(fp)
                st.rerun()
