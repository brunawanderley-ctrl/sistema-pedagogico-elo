"""
PEEX — Gerador de Pauta PEEX Unidade (Coordenador/Diretor)
Pauta para reuniao de unidade (35x/ano) com dados locais.
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit
from utils import calcular_semana_letiva, calcular_trimestre, UNIDADES_NOMES
from components import cabecalho_pagina
from peex_utils import info_semana, proximas_reunioes
from engine import carregar_missoes_pregeradas, carregar_conselheiro, carregar_preparador
from narrativa import gerar_nudge


# ========== MAIN ==========

cabecalho_pagina("Gerador PEEX Unidade", "Pauta para reuniao semanal da unidade")

semana = calcular_semana_letiva()
trimestre = calcular_trimestre(semana)
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)
info = info_semana(semana)
fase = info['fase']

st.markdown(f"### {nome_un} | Semana {semana} | Fase {info['fase_num']}: {fase['nome']}")

# Proxima reuniao
prox = info['proxima_reuniao']
if prox:
    fmt = info['formato_reuniao']
    st.info(f"Proxima: **{prox.get('titulo', '')}** — {fmt.get('nome', '')} ({fmt.get('duracao', 30)} min)")

# Missoes
missoes = carregar_missoes_pregeradas(user_unit)
urgentes = [b for b in missoes if b.get('nivel') == 'URGENTE']
importantes = [b for b in missoes if b.get('nivel') == 'IMPORTANTE']

st.markdown(f"**{len(missoes)} missoes** ({len(urgentes)} urgentes, {len(importantes)} importantes)")

# Conselheiro e Preparador data
conselheiro = carregar_conselheiro()
pauta_cons = conselheiro.get('pautas', {}).get(user_unit, {})
preparador = carregar_preparador()
roteiro_un = preparador.get('roteiro_por_unidade', {}).get(user_unit, {})

# Objetivo (PREPARADOR)
obj = preparador.get('objetivo_da_reuniao', '')
if obj:
    st.markdown(f"""
    <div style="background:#E3F2FD; border-left:4px solid #2196F3; padding:12px 16px; margin:8px 0; border-radius:4px;">
        <strong>Objetivo:</strong> {obj}
    </div>
    """, unsafe_allow_html=True)

# Situacao da unidade (PREPARADOR)
if roteiro_un.get('situacao_resumida'):
    st.markdown(f"**Situacao:** {roteiro_un['situacao_resumida']}")

# Gerar pauta
st.markdown("---")
st.markdown("### Pauta Gerada")

pauta_items = []
script = preparador.get('script_5_atos', {})

# Ato 1: Raizes
ato1 = script.get('ato1_raizes', {})
pauta_items.append(f"### Ato 1 — Raizes ({ato1.get('duracao', '5 min')})")
if ato1.get('o_que_dizer'):
    pauta_items.append(f'*"{ato1["o_que_dizer"]}"*')
else:
    pauta_items.append("Check-in: como esta a energia da equipe?")

# Ato 2: Solo
ato2 = script.get('ato2_solo', {})
pauta_items.append(f"### Ato 2 — Solo ({ato2.get('duracao', '10 min')})")
if ato2.get('o_que_dizer'):
    pauta_items.append(f'*"{ato2["o_que_dizer"]}"*')
pauta_items.append(f"Dados da semana: {len(missoes)} missoes ({len(urgentes)} urgentes)")
# Dados do preparador
for d in ato2.get('dados_para_mostrar', []):
    pauta_items.append(f"- {d}")
# Missoes urgentes
if urgentes and not ato2.get('dados_para_mostrar'):
    pauta_items.append("**Urgentes:**")
    for b in urgentes[:3]:
        pauta_items.append(f"- {b.get('icone', '')} {b.get('o_que', '')}")

# Pontos criticos da unidade (PREPARADOR)
criticos = roteiro_un.get('pontos_criticos', [])
if criticos:
    pauta_items.append("**Pontos criticos:**")
    for pc in criticos:
        pauta_items.append(f"- **{pc.get('tema', '')}**")
        if pc.get('como_abordar'):
            pauta_items.append(f"  Como abordar: {pc['como_abordar']}")

# Ato 3: Micelio
ato3 = script.get('ato3_micelio', {})
pauta_items.append(f"### Ato 3 — Micelio ({ato3.get('duracao', '10 min')})")
if ato3.get('o_que_dizer'):
    pauta_items.append(f'*"{ato3["o_que_dizer"]}"*')
else:
    pauta_items.append("Conexoes: quem precisa de ajuda? Quem pode ajudar?")

# Perguntas prontas do PREPARADOR ou conselheiro
perguntas_ato3 = ato3.get('perguntas_prontas', [])
if perguntas_ato3:
    for p in perguntas_ato3:
        pauta_items.append(f"- {p}")

# Topicos do conselheiro
topicos = pauta_cons.get('topicos', [])
if topicos:
    pauta_items.append("**Topicos sugeridos:**")
    for t in topicos[:5]:
        pauta_items.append(f"- {t}")

# Pergunta para coordenador (PREPARADOR)
pergunta_coord = roteiro_un.get('pergunta_para_diretor', '')
if pergunta_coord:
    pauta_items.append(f"**Pergunta-chave:** {pergunta_coord}")

# Ato 4: Sementes
ato4 = script.get('ato4_sementes', {})
pauta_items.append(f"### Ato 4 — Sementes ({ato4.get('duracao', '10 min')})")
compromissos_sug = ato4.get('compromissos_sugeridos', [])
if compromissos_sug:
    pauta_items.append("**Compromissos sugeridos:**")
    for c in compromissos_sug:
        pauta_items.append(f"- {c}")
else:
    pauta_items.append("3 compromissos concretos para a proxima semana:")
    pauta_items.append("1. _____________________")
    pauta_items.append("2. _____________________")
    pauta_items.append("3. _____________________")

# Compromisso esperado da unidade (PREPARADOR)
comp_esp = roteiro_un.get('compromisso_esperado', '')
if comp_esp:
    pauta_items.append(f"**Compromisso esperado:** {comp_esp}")

# Perguntas do conselheiro
perguntas = pauta_cons.get('perguntas', [])
if perguntas:
    pauta_items.append("**Perguntas para reflexao:**")
    for p in perguntas:
        pauta_items.append(f"- {p}")

# Ato 5: Chuva
ato5 = script.get('ato5_chuva', {})
pauta_items.append(f"### Ato 5 — Chuva ({ato5.get('duracao', '5 min')})")
celebracao = ato5.get('celebracao', '')
if celebracao:
    pauta_items.append(f"Celebracao: {celebracao}")
# Pontos positivos da unidade
positivos = roteiro_un.get('pontos_positivos', [])
if positivos:
    for pp in positivos:
        pauta_items.append(f"- {pp}")
if not celebracao and not positivos:
    pauta_items.append("Celebrar 1 conquista da semana. NUNCA terminar com problema.")

for item in pauta_items:
    st.markdown(item)

# Editavel
st.markdown("---")
st.markdown("### Notas Adicionais")
notas = st.text_area("Adicione suas notas para a reuniao:", height=100, key="notas_peex_un")

# Export
st.markdown("---")
texto = f"PAUTA PEEX — {nome_un} — Semana {semana}\n\n" + '\n'.join(pauta_items)
if notas:
    texto += f"\n\nNotas:\n{notas}"

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        "Baixar TXT",
        texto,
        file_name=f"pauta_peex_{user_unit}_sem{semana}.txt",
        mime="text/plain",
    )
with col2:
    st.download_button(
        "Baixar para WhatsApp",
        texto.replace('### ', '').replace('**', '*'),
        file_name=f"pauta_whatsapp_{user_unit}_sem{semana}.txt",
        mime="text/plain",
    )
