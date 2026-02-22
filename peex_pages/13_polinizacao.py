"""
PEEX — Feed de Polinizacao
Feed tipo rede social com praticas compartilhadas entre coordenadores.
Auto-gera posts quando dados detectam boas praticas.
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


# ========== CSS ==========

st.markdown("""
<style>
    .pol-card {
        padding: 16px 20px;
        margin: 10px 0;
        border-radius: 10px;
        background: #fafafa;
        border: 1px solid #e0e0e0;
    }
    .pol-card-auto {
        background: #e8f5e9;
        border-left: 4px solid #43a047;
    }
    .pol-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
    }
    .pol-avatar {
        width: 36px; height: 36px;
        border-radius: 50%;
        background: #1a237e;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 0.9em;
    }
    .pol-autor { font-weight: bold; color: #1a237e; }
    .pol-meta { font-size: 0.8em; color: #888; }
    .pol-conteudo { margin: 8px 0; line-height: 1.5; }
    .pol-tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75em;
        font-weight: bold;
        margin-right: 6px;
    }
    .pol-tag-pratica { background: #e3f2fd; color: #1565c0; }
    .pol-tag-auto { background: #e8f5e9; color: #2e7d32; }
    .pol-tag-mentoria { background: #fce4ec; color: #c62828; }
    .pol-reacoes {
        display: flex;
        gap: 16px;
        margin-top: 8px;
        font-size: 0.9em;
    }
    .pol-reacao { cursor: pointer; color: #666; }
    .pol-reacao:hover { color: #1a237e; }
</style>
""", unsafe_allow_html=True)


# ========== PERSISTENCIA ==========

_FEED_PATH = WRITABLE_DIR / "polinizacao_feed.json"


def _carregar_feed():
    if _FEED_PATH.exists():
        try:
            with open(_FEED_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _salvar_feed(feed):
    with open(_FEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)


# ========== AUTO-GERACAO ==========

_TEMPLATES_AUTO = [
    {
        'gatilho': 'conformidade_subiu',
        'titulo': 'Conformidade subiu!',
        'texto': '{unidade} elevou a conformidade em +{delta:.0f}pp esta semana. '
                 'O coordenador focou em conversas individuais com os 3 professores com menor registro.',
        'tag': 'pratica',
    },
    {
        'gatilho': 'turma_saiu_vermelho',
        'titulo': 'Turma saiu do vermelho!',
        'texto': 'Uma turma de {unidade} saiu do vermelho apos intervencao do coordenador. '
                 'Estrategia: reuniao relampago com professores + meta semanal visivel.',
        'tag': 'pratica',
    },
    {
        'gatilho': 'prof_recuperou',
        'titulo': 'Professor recuperou registros',
        'texto': 'Professor que estava silencioso em {unidade} voltou a registrar aulas. '
                 'O coordenador usou abordagem acolhedora: "como posso ajudar?"',
        'tag': 'mentoria',
    },
]


def auto_gerar_posts(resumo_atual, resumo_anterior, semana):
    """Gera posts automaticos baseado em mudancas positivas nos dados.

    Args:
        resumo_atual, resumo_anterior: DataFrames do resumo_Executivo
        semana: semana letiva

    Returns:
        lista de posts gerados
    """
    posts = []

    for un_code in ['BV', 'CD', 'JG', 'CDR']:
        row_atual = resumo_atual[resumo_atual['unidade'] == un_code] if not resumo_atual.empty else None
        row_ant = resumo_anterior[resumo_anterior['unidade'] == un_code] if not resumo_anterior.empty else None

        if row_atual is None or row_atual.empty:
            continue
        if row_ant is None or row_ant.empty:
            continue

        conf_atual = row_atual.iloc[0].get('pct_conformidade_media', 0)
        conf_ant = row_ant.iloc[0].get('pct_conformidade_media', 0)
        delta = conf_atual - conf_ant
        nome_un = UNIDADES_NOMES.get(un_code, un_code)

        if delta > 5:
            posts.append({
                'id': f'auto_{semana}_{un_code}_conf',
                'autor': f'Sistema PEEX',
                'unidade': un_code,
                'titulo': 'Conformidade subiu!',
                'texto': f'{nome_un} elevou a conformidade em +{delta:.0f}pp esta semana.',
                'tag': 'auto',
                'tipo': 'auto',
                'semana': semana,
                'data': datetime.now().isoformat(),
                'curtidas': 0,
                'adotaram': [],
            })

    return posts


# ========== MAIN ==========

cabecalho_pagina("Feed de Polinizacao", "Praticas compartilhadas entre coordenadores")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)

feed = _carregar_feed()

# Novo post
st.markdown("### Compartilhar Pratica")
with st.form("novo_post"):
    titulo = st.text_input("Titulo da pratica")
    texto = st.text_area("Descreva o que voce fez e o resultado", height=100)
    c1, c2 = st.columns(2)
    with c1:
        tag = st.selectbox("Categoria", ['pratica', 'mentoria', 'material', 'ideia'])
    with c2:
        anonimo = st.checkbox("Postar anonimamente")
    submitted = st.form_submit_button("Publicar")

    if submitted and titulo and texto:
        novo_post = {
            'id': f'post_{semana}_{user_unit}_{len(feed)}',
            'autor': 'Anonimo' if anonimo else nome_un,
            'unidade': user_unit,
            'titulo': titulo,
            'texto': texto,
            'tag': tag,
            'tipo': 'manual',
            'semana': semana,
            'data': datetime.now().isoformat(),
            'curtidas': 0,
            'adotaram': [],
        }
        feed.insert(0, novo_post)
        _salvar_feed(feed)
        st.rerun()

# Feed
st.markdown("---")

# Filtro
filtro = st.radio(
    "Filtrar por:",
    ['Todos', 'Praticas', 'Mentorias', 'Auto-detectados'],
    horizontal=True,
)

feed_filtrado = feed
if filtro == 'Praticas':
    feed_filtrado = [p for p in feed if p.get('tag') == 'pratica']
elif filtro == 'Mentorias':
    feed_filtrado = [p for p in feed if p.get('tag') == 'mentoria']
elif filtro == 'Auto-detectados':
    feed_filtrado = [p for p in feed if p.get('tipo') == 'auto']

if not feed_filtrado:
    st.info("Nenhuma pratica compartilhada ainda. Seja o primeiro!")
else:
    alterado = False
    for i, post in enumerate(feed_filtrado):
        tag_class = {
            'pratica': 'pol-tag-pratica',
            'mentoria': 'pol-tag-mentoria',
            'auto': 'pol-tag-auto',
        }.get(post.get('tag', ''), 'pol-tag-pratica')

        card_class = 'pol-card pol-card-auto' if post.get('tipo') == 'auto' else 'pol-card'
        iniciais = post.get('autor', '?')[:2].upper()
        un_nome = UNIDADES_NOMES.get(post.get('unidade', ''), post.get('unidade', ''))

        st.markdown(f"""
        <div class="{card_class}">
            <div class="pol-header">
                <div class="pol-avatar">{iniciais}</div>
                <div>
                    <span class="pol-autor">{post.get('autor', 'Anonimo')}</span>
                    <span class="pol-meta"> — {un_nome} | Semana {post.get('semana', '?')}</span>
                </div>
            </div>
            <div class="pol-conteudo">
                <strong>{post.get('titulo', '')}</strong><br>
                {post.get('texto', '')}
            </div>
            <span class="pol-tag {tag_class}">{post.get('tag', 'pratica')}</span>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 1, 4])
        with c1:
            if st.button(f"Curtir ({post.get('curtidas', 0)})", key=f"curtir_{i}"):
                # Encontrar post original no feed
                for p in feed:
                    if p.get('id') == post.get('id'):
                        p['curtidas'] = p.get('curtidas', 0) + 1
                        alterado = True
                        break
        with c2:
            n_adotaram = len(post.get('adotaram', []))
            if st.button(f"Adotar ({n_adotaram})", key=f"adotar_{i}"):
                for p in feed:
                    if p.get('id') == post.get('id'):
                        adotaram = p.get('adotaram', [])
                        if user_unit not in adotaram:
                            adotaram.append(user_unit)
                            p['adotaram'] = adotaram
                            alterado = True
                        break

    if alterado:
        _salvar_feed(feed)
        st.rerun()

# Estatisticas
st.markdown("---")
st.markdown("### Estatisticas de Polinizacao")
total_posts = len(feed)
total_curtidas = sum(p.get('curtidas', 0) for p in feed)
total_adocoes = sum(len(p.get('adotaram', [])) for p in feed)
auto_posts = sum(1 for p in feed if p.get('tipo') == 'auto')

c1, c2, c3, c4 = st.columns(4)
c1.metric("Praticas", total_posts)
c2.metric("Curtidas", total_curtidas)
c3.metric("Adocoes", total_adocoes)
c4.metric("Auto-detectados", auto_posts)
