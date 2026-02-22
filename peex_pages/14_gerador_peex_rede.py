"""
PEEX — Gerador de Pauta PEEX Rede (CEO)
Pauta para reuniao de rede (10x/ano) com dados consolidados.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_role, ROLE_CEO
from utils import calcular_semana_letiva, calcular_trimestre, DATA_DIR, UNIDADES_NOMES
from components import cabecalho_pagina
from peex_utils import info_semana, proximas_reunioes, calcular_indice_elo
from engine import carregar_missoes_pregeradas, carregar_comparador, carregar_preparador


# ========== GATE ==========

role = get_user_role()
if role != ROLE_CEO:
    st.stop()


# ========== MAIN ==========

cabecalho_pagina("Gerador PEEX Rede", "Pauta para reuniao de rede (10x/ano)")

semana = calcular_semana_letiva()
trimestre = calcular_trimestre(semana)
info = info_semana(semana)

# Proxima reuniao de rede
reunioes = proximas_reunioes(semana, n=5)
reuniao_rede = None
for r in reunioes:
    if r.get('titulo', '').lower().startswith('rede') or r.get('formato') == 'E':
        reuniao_rede = r
        break

st.markdown(f"### Semana {semana} | Fase {info['fase_num']}: {info['fase']['nome']} | {trimestre}o Tri")

if reuniao_rede:
    st.info(f"Proxima reuniao de rede: **{reuniao_rede.get('titulo', '')}** (Semana {reuniao_rede.get('semana', '?')}, formato {reuniao_rede.get('formato_nome', '')})")

# Dados consolidados
resumo_path = DATA_DIR / "resumo_Executivo.csv"
if not resumo_path.exists():
    st.warning("Dados nao disponiveis.")
    st.stop()

resumo_df = pd.read_csv(resumo_path)

# IE por unidade
st.markdown("### Indice ELO por Unidade")
ies = []
for un_code in ['BV', 'CD', 'JG', 'CDR']:
    row = resumo_df[resumo_df['unidade'] == un_code]
    if not row.empty:
        ie = calcular_indice_elo(row.iloc[0])
        ies.append({'unidade': UNIDADES_NOMES.get(un_code, un_code), 'IE': ie})

if ies:
    cols = st.columns(4)
    for i, ie_data in enumerate(sorted(ies, key=lambda x: x['IE'], reverse=True)):
        with cols[i]:
            st.metric(ie_data['unidade'], f"{ie_data['IE']:.0f}/100")

# Carregar PREPARADOR
preparador = carregar_preparador()

# Objetivo da reuniao (PREPARADOR)
obj = preparador.get('objetivo_da_reuniao', '')
if obj:
    st.markdown(f"""
    <div style="background:#E3F2FD; border-left:4px solid #2196F3; padding:12px 16px; margin:8px 0; border-radius:4px;">
        <strong>Objetivo:</strong> {obj}
    </div>
    """, unsafe_allow_html=True)

# Missoes por unidade
st.markdown("### Panorama de Missoes")
for un_code in ['BV', 'CD', 'JG', 'CDR']:
    missoes = carregar_missoes_pregeradas(un_code)
    urgentes = [b for b in missoes if b.get('nivel') == 'URGENTE']
    nome = UNIDADES_NOMES.get(un_code, un_code)
    st.markdown(f"- **{nome}**: {len(missoes)} missoes ({len(urgentes)} urgentes)")

# Roteiro por unidade (PREPARADOR)
roteiro_un = preparador.get('roteiro_por_unidade', {})
if roteiro_un:
    st.markdown("### Roteiro por Unidade")
    for un_code in ['BV', 'CD', 'JG', 'CDR']:
        rot = roteiro_un.get(un_code, {})
        if not rot:
            continue
        nome = UNIDADES_NOMES.get(un_code, un_code)
        with st.expander(f"{nome} — {rot.get('situacao_resumida', '')[:80]}"):
            # Pontos criticos
            criticos = rot.get('pontos_criticos', [])
            if criticos:
                st.markdown("**Pontos criticos:**")
                for pc in criticos:
                    st.markdown(f"- **{pc.get('tema', '')}**")
                    if pc.get('como_abordar'):
                        st.caption(f"Como abordar: {pc['como_abordar']}")
            # Pontos positivos
            positivos = rot.get('pontos_positivos', [])
            if positivos:
                st.markdown("**Destaques positivos:**")
                for pp in positivos:
                    st.markdown(f"- {pp}")
            # Pergunta para diretor
            pergunta = rot.get('pergunta_para_diretor', '')
            if pergunta:
                st.info(f"Pergunta para diretor: {pergunta}")
            # Compromisso esperado
            comp = rot.get('compromisso_esperado', '')
            if comp:
                st.markdown(f"**Compromisso esperado:** {comp}")

# Rankings
comparador = carregar_comparador()
if comparador:
    st.markdown("### Rankings")
    r_saude = comparador.get('ranking_saude', [])
    if r_saude:
        for r in r_saude:
            pos_emoji = ['🥇', '🥈', '🥉', '4️⃣'][r.get('posicao', 4) - 1]
            st.markdown(f"{pos_emoji} **{r.get('nome', '')}** — IE: {r.get('score', 0):.0f}")

# Gerar pauta
st.markdown("---")
st.markdown("### Pauta Gerada")

pauta_items = [
    f"1. Abertura e check-in (5 min)",
    f"2. Panorama da rede — Semana {semana}, {trimestre}o Trimestre",
    "3. IE por unidade: " + ', '.join(f"{d['unidade']}: {d['IE']:.0f}" for d in ies),
]

# Top 3 problemas da rede
todas_missoes = carregar_missoes_pregeradas()
urgentes_rede = [b for b in todas_missoes if b.get('nivel') == 'URGENTE']
if urgentes_rede:
    pauta_items.append(f"4. Missoes urgentes na rede: {len(urgentes_rede)} ({', '.join(set(b.get('tipo','') for b in urgentes_rede[:5]))})")
else:
    pauta_items.append("4. Nenhuma missao urgente na rede")

# Celebracoes do PREPARADOR
script = preparador.get('script_5_atos', {})
celebracao = script.get('ato5_chuva', {}).get('celebracao', '')
if celebracao:
    pauta_items.append(f"5. Celebracao: {celebracao}")
else:
    pauta_items.append("5. Destaques positivos e celebracoes")

pauta_items.extend([
    "6. Compromissos e encaminhamentos",
    "7. Encerramento positivo",
])

for item in pauta_items:
    st.markdown(item)

# Export
st.markdown("---")
texto = f"PAUTA PEEX REDE — Semana {semana}\n" + '\n'.join(pauta_items)
if roteiro_un:
    texto += "\n\nROTEIRO POR UNIDADE:\n"
    for un_code in ['BV', 'CD', 'JG', 'CDR']:
        rot = roteiro_un.get(un_code, {})
        if rot:
            nome = UNIDADES_NOMES.get(un_code, un_code)
            texto += f"\n{nome}:\n"
            texto += f"  Situacao: {rot.get('situacao_resumida', '')}\n"
            for pc in rot.get('pontos_criticos', []):
                texto += f"  - {pc.get('tema', '')}\n"
            for pp in rot.get('pontos_positivos', []):
                texto += f"  + {pp}\n"

st.download_button(
    "Baixar Pauta TXT",
    texto,
    file_name=f"pauta_peex_rede_sem{semana}.txt",
    mime="text/plain",
)
