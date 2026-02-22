"""
PEEX — Pauta Adaptativa
Gera pauta automatica para reunioes PEEX com Ritual de Floresta (5 atos).
"""

import json
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_role, get_user_unit
from utils import calcular_semana_letiva, UNIDADES_NOMES, DATA_DIR
from components import cabecalho_pagina
from engine import carregar_missoes_pregeradas, carregar_conselheiro, carregar_preparador
from peex_utils import info_semana, FORMATOS_REUNIAO
from narrativa import gerar_pauta_peex, gerar_nudge


# ========== CSS ==========

st.markdown("""
<style>
    .ritual-card {
        padding: 16px 20px;
        margin: 8px 0;
        border-radius: 10px;
        border-left: 5px solid;
    }
    .ritual-titulo {
        font-weight: bold;
        font-size: 1.05em;
        margin-bottom: 4px;
    }
    .ritual-duracao {
        font-size: 0.8em;
        color: #666;
        float: right;
    }
    .pauta-acao {
        padding: 10px 16px;
        margin: 4px 0;
        border-radius: 6px;
        background: #f5f5f5;
        font-size: 0.95em;
    }
    .formato-header {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 20px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


# ========== MAIN ==========

cabecalho_pagina("PEEX Adaptativo", "Pauta gerada automaticamente para sua proxima reuniao")

semana = calcular_semana_letiva()
info = info_semana(semana)
prox = info['proxima_reuniao']
formato = info['formato_reuniao']

user_unit = get_user_unit() or 'BV'

# Carregar dados do conselheiro e preparador
conselheiro = carregar_conselheiro()
pauta_un = conselheiro.get('pautas', {}).get(user_unit, {})
preparador = carregar_preparador()

# Formato da reuniao
fmt_nome = formato.get('nome', 'FLASH')
fmt_cor = formato.get('cor', '#607D8B')
fmt_icone = formato.get('icone', '')
fmt_duracao = formato.get('duracao', 30)

st.markdown(f"""
<span class="formato-header" style="background:{fmt_cor};">
    {fmt_icone} {fmt_nome} — {fmt_duracao} minutos
</span>
""", unsafe_allow_html=True)

if prox:
    st.markdown(f"**Reuniao:** {prox['cod']} — {prox['titulo']} (Semana {prox['semana']})")
    st.markdown(f"**Foco programado:** {prox['foco']}")

    # Objetivo do PREPARADOR (se disponivel)
    obj = preparador.get('objetivo_da_reuniao', '')
    if obj:
        st.markdown(f"""
        <div style="background:#E3F2FD; border-left:4px solid #2196F3; padding:12px 16px; margin:8px 0; border-radius:4px;">
            <strong>Objetivo:</strong> {obj}
        </div>
        """, unsafe_allow_html=True)

    # Explicacao inline do formato
    desc_formatos = {
        'FLASH': 'Check rapido de 30 min — foco em status e desbloqueio de acoes.',
        'FOCO': 'Aprofundamento de 45 min — mergulho em 1-2 temas criticos.',
        'ESTRATEGICA': 'Balanco de 90 min — analise de trimestre e realinhamento.',
        'CRISE': 'Reuniao emergencial de 60 min — resposta rapida a situacao critica.',
    }
    desc = desc_formatos.get(fmt_nome, '')
    if desc:
        st.caption(f"Formato {fmt_nome}: {desc}")
    st.markdown("")


# ========== TOPICOS ==========

st.markdown("### Topicos da Pauta")
topicos = pauta_un.get('topicos', [])
if topicos:
    for i, t in enumerate(topicos, 1):
        st.markdown(f"{i}. {t}")
else:
    st.info("Execute o Conselheiro (scheduler segunda 5h) para gerar a pauta.")


# ========== RITUAIS DE FLORESTA (5 ATOS) — COM SCRIPT DO PREPARADOR ==========

st.markdown("---")
st.markdown("### Ritual de Floresta — 5 Atos")

# Usar script do preparador se disponivel
script_5atos = preparador.get('script_5_atos', {})
rituais = pauta_un.get('rituais', [])

if script_5atos:
    # Script completo do PREPARADOR com falas sugeridas
    nomes_atos = [
        ('ato1_raizes', 'Raizes', '#795548'),
        ('ato2_solo', 'Solo', '#8D6E63'),
        ('ato3_micelio', 'Micelio', '#43A047'),
        ('ato4_sementes', 'Sementes', '#66BB6A'),
        ('ato5_chuva', 'Chuva', '#29B6F6'),
    ]
    for i, (key, nome, cor) in enumerate(nomes_atos, 1):
        ato = script_5atos.get(key, {})
        duracao = ato.get('duracao', '? min')
        o_que_dizer = ato.get('o_que_dizer', '')
        tecnica = ato.get('tecnica', '')
        dados = ato.get('dados_para_mostrar', [])
        perguntas_ato = ato.get('perguntas_prontas', [])
        compromissos = ato.get('compromissos_sugeridos', [])
        celebracao = ato.get('celebracao', '')

        conteudo_parts = []
        if o_que_dizer:
            conteudo_parts.append(f'<em>"{o_que_dizer}"</em>')
        if dados:
            conteudo_parts.append('<br>'.join(f'📊 {d}' for d in dados))
        if perguntas_ato:
            conteudo_parts.append('<br>'.join(f'❓ {p}' for p in perguntas_ato))
        if compromissos:
            conteudo_parts.append('<br>'.join(f'✅ {c}' for c in compromissos))
        if celebracao:
            conteudo_parts.append(f'🎉 {celebracao}')
        if tecnica:
            conteudo_parts.append(f'<small style="color:#888;">Tecnica: {tecnica}</small>')

        conteudo_html = '<br>'.join(conteudo_parts) if conteudo_parts else nome

        st.markdown(f"""
        <div class="ritual-card" style="border-left-color:{cor};">
            <span class="ritual-duracao">{duracao}</span>
            <div class="ritual-titulo">Ato {i}: {nome}</div>
            <div>{conteudo_html}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    # Fallback: rituais do conselheiro ou padrao
    if not rituais:
        missoes = carregar_missoes_pregeradas(user_unit)
        urgentes = [b for b in missoes if b.get('nivel') == 'URGENTE']
        rituais = [
            {'ato': 1, 'nome': 'Raizes', 'duracao': '5 min',
             'conteudo': 'Ancoragem: como esta a energia da equipe? Roda rapida de check-in.'},
            {'ato': 2, 'nome': 'Solo', 'duracao': '10 min',
             'conteudo': f'Dados da semana: {len(missoes)} missoes ({len(urgentes)} urgentes).'},
            {'ato': 3, 'nome': 'Micelio', 'duracao': '10 min',
             'conteudo': 'Conexoes: quem precisa de ajuda? Quem pode ajudar?'},
            {'ato': 4, 'nome': 'Sementes', 'duracao': '10 min',
             'conteudo': 'Plano de acao: 3 compromissos concretos.'},
            {'ato': 5, 'nome': 'Chuva', 'duracao': '5 min',
             'conteudo': 'Encerramento positivo. NUNCA terminar com problema.'},
        ]

    cores_ritual = ['#795548', '#8D6E63', '#43A047', '#66BB6A', '#29B6F6']
    for r in rituais:
        idx = r['ato'] - 1
        cor = cores_ritual[idx] if idx < len(cores_ritual) else '#607D8B'
        st.markdown(f"""
        <div class="ritual-card" style="border-left-color:{cor};">
            <span class="ritual-duracao">{r['duracao']}</span>
            <div class="ritual-titulo">Ato {r['ato']}: {r['nome']}</div>
            <div>{r['conteudo']}</div>
        </div>
        """, unsafe_allow_html=True)


# ========== PERGUNTAS GUIA ==========

st.markdown("---")
st.markdown("### Perguntas para Reflexao")

perguntas = pauta_un.get('perguntas', [
    "Qual foi a maior conquista da sua equipe esta semana?",
    "O que voce precisa da direcao que nao esta conseguindo resolver sozinho(a)?",
    "Se pudesse mudar UMA coisa na rotina da proxima semana, o que seria?",
])
for p in perguntas:
    st.markdown(f"- {p}")


# ========== FORMATO SUGERIDO ==========

fmt_sugerido = pauta_un.get('formato_sugerido', {})
if fmt_sugerido and fmt_sugerido.get('nome') != fmt_nome:
    st.markdown("---")
    st.warning(
        f"O sistema sugere formato **{fmt_sugerido.get('nome', '?')}** "
        f"({fmt_sugerido.get('duracao', '?')} min): {fmt_sugerido.get('motivo', '')}"
    )


# ========== EXPORTAR ==========

st.markdown("---")
with st.expander("Exportar pauta"):
    nome_un = UNIDADES_NOMES.get(user_unit, user_unit)
    texto = [
        f"PAUTA PEEX — SEMANA {semana} — {nome_un}",
        f"Formato: {fmt_nome} ({fmt_duracao} min)",
        "",
    ]
    if prox:
        texto.append(f"Reuniao: {prox['cod']} — {prox['titulo']}")
        texto.append(f"Foco: {prox['foco']}")
        texto.append("")
    texto.append("TOPICOS:")
    for i, t in enumerate(topicos, 1):
        texto.append(f"  {i}. {t}")
    texto.append("")
    texto.append("RITUAL DE FLORESTA:")
    for r in rituais:
        texto.append(f"  Ato {r['ato']} ({r['nome']}, {r['duracao']}): {r['conteudo']}")
    texto.append("")
    texto.append("PERGUNTAS:")
    for p in perguntas:
        texto.append(f"  - {p}")
    texto.append("")
    texto.append("---")
    texto.append("PEEX Command Center — Colegio ELO 2026")

    texto_final = "\n".join(texto)
    st.text_area("Texto gerado", texto_final, height=300, label_visibility="collapsed")
    st.download_button(
        "Baixar TXT",
        texto_final,
        file_name=f"pauta_peex_sem{semana}_{user_unit}.txt",
        mime="text/plain",
    )
