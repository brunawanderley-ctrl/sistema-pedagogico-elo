"""
PEEX — Rankings da Rede
4 rankings: Saude | Generosidade | Evolucao | Solo
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_role, ROLE_CEO, ROLE_DIRETOR
from utils import calcular_semana_letiva, calcular_trimestre, DATA_DIR, UNIDADES_NOMES
from components import cabecalho_pagina
from engine import carregar_comparador


# ========== CSS ==========

st.markdown("""
<style>
    .rank-card {
        padding: 16px 20px;
        border-radius: 10px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .rank-pos {
        font-size: 2em;
        font-weight: bold;
        min-width: 50px;
        text-align: center;
    }
    .rank-nome { font-size: 1.1em; font-weight: bold; }
    .rank-score { font-size: 0.9em; color: #666; }
    .estrela { color: #FFC107; font-size: 1.2em; }
</style>
""", unsafe_allow_html=True)


# ========== GATE ==========

role = get_user_role()
if role not in (ROLE_CEO, ROLE_DIRETOR, 'coordenador'):
    st.warning("Acesso restrito.")
    st.stop()


# ========== MAIN ==========

cabecalho_pagina("Rankings da Rede", "Competicao saudavel entre unidades")

semana = calcular_semana_letiva()
trimestre = calcular_trimestre(semana)

comparador = carregar_comparador()

# Tabs
tab_saude, tab_evolucao, tab_generosidade = st.tabs(["Saude", "Evolucao", "Generosidade"])

cores_posicao = ['#FFD700', '#C0C0C0', '#CD7F32', '#607D8B']
bg_posicao = ['#FFF8E1', '#F5F5F5', '#FBE9E7', '#ECEFF1']


def render_ranking(ranking, score_label="Score"):
    if not ranking:
        st.info("Execute o Comparador para gerar rankings.")
        return
    for r in ranking:
        pos = r.get('posicao', 0) - 1
        cor = cores_posicao[min(pos, 3)]
        bg = bg_posicao[min(pos, 3)]
        st.markdown(f"""
        <div class="rank-card" style="background:{bg};">
            <div class="rank-pos" style="color:{cor};">#{r['posicao']}</div>
            <div>
                <div class="rank-nome">{r.get('nome', r.get('unidade', ''))}</div>
                <div class="rank-score">{score_label}: {r.get('total', r.get('score', 0)):.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


with tab_saude:
    st.markdown("### Ranking de Saude")
    st.caption("Baseado no Indice ELO (IE): Conformidade + Frequencia + Ritmo + Risco")
    ranking_saude = comparador.get('ranking_saude', [])
    if not ranking_saude:
        # Calcular on-the-fly
        resumo_path = DATA_DIR / "resumo_Executivo.csv"
        if resumo_path.exists():
            from estrelas import ranking_saude as calc_ranking_saude
            resumo_df = pd.read_csv(resumo_path)
            ranking_saude = calc_ranking_saude(resumo_df)
    render_ranking(ranking_saude, "IE")


with tab_evolucao:
    st.markdown("### Ranking de Evolucao")
    st.caption(f"Estrelas acumuladas no {trimestre}o trimestre — mede CRESCIMENTO, nao posicao")
    ranking_evolucao = comparador.get('ranking_evolucao', [])
    if ranking_evolucao:
        for r in ranking_evolucao:
            pos = r.get('posicao', 0) - 1
            cor = cores_posicao[min(pos, 3)]
            bg = bg_posicao[min(pos, 3)]
            detalhes = r.get('detalhes', {})
            estrelas_visual = ''.join(['<span class="estrela">&#11088;</span>'] * min(r.get('total', 0), 15))
            st.markdown(f"""
            <div class="rank-card" style="background:{bg};">
                <div class="rank-pos" style="color:{cor};">#{r['posicao']}</div>
                <div>
                    <div class="rank-nome">{r.get('nome', '')}</div>
                    <div class="rank-score">Total: {r.get('total', 0)} estrelas</div>
                    <div>{estrelas_visual}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma estrela registrada ainda. O Comparador roda segunda 5h30.")

    st.markdown("---")
    st.markdown("#### Como funcionam as Estrelas")
    st.markdown("""
    - **0 estrelas**: piorou ou estagnou 2+ semanas
    - **1 estrela**: estavel (variacao <1pp)
    - **2 estrelas**: melhorou 1-3pp
    - **3 estrelas**: melhorou >3pp OU atingiu a meta
    - **Max por semana**: 5 indicadores x 3 = 15 estrelas
    - **Acumulativo**: estrelas nunca sao perdidas no trimestre
    """)


with tab_generosidade:
    st.markdown("### Ranking de Generosidade")
    st.caption("Mede quanto voce AJUDOU outros — visitas, pareamentos, praticas compartilhadas")
    ranking_gen = comparador.get('ranking_generosidade', [])
    if not ranking_gen:
        from estrelas import ranking_generosidade as calc_ranking_gen
        ranking_gen = calc_ranking_gen()
    render_ranking(ranking_gen, "Pontos")

    st.markdown("---")
    st.markdown("#### Tabela de Pontos")
    st.markdown("""
    | Acao | Pontos |
    |------|--------|
    | Visita a outra unidade | +15 |
    | Pareamento com resultado | +10 |
    | Pratica compartilhada | +5 |
    | Material compartilhado | +3 |
    """)
