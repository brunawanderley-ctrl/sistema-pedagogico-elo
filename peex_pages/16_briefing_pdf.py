"""
PEEX — Briefing Imprimivel
Gera HTML imprimivel com missoes + pauta PEEX + plano de acao.
"""

import json
import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit
from utils import calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre, UNIDADES_NOMES, _hoje
from components import cabecalho_pagina
from engine import carregar_missoes_pregeradas, carregar_conselheiro
from narrativa import gerar_nudge
from peex_utils import info_semana


# ========== MAIN ==========

cabecalho_pagina("Briefing Imprimivel", "Gere e baixe o briefing da semana")

semana = calcular_semana_letiva()
capitulo = calcular_capitulo_esperado(semana)
trimestre = calcular_trimestre(semana)
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)
hoje = _hoje()

missoes = carregar_missoes_pregeradas(user_unit)
conselheiro = carregar_conselheiro()
pauta = conselheiro.get('pautas', {}).get(user_unit, {})
info = info_semana(semana)
fase = info['fase']

# Gerar HTML
urgentes = [b for b in missoes if b.get('nivel') == 'URGENTE']
importantes = [b for b in missoes if b.get('nivel') == 'IMPORTANTE']
monitorar = [b for b in missoes if b.get('nivel') == 'MONITORAR']

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Briefing PEEX — Semana {semana}</title>
<style>
    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }}
    h1 {{ color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 8px; }}
    h2 {{ color: #283593; margin-top: 24px; }}
    .fase {{ background: {fase['cor']}; color: white; padding: 8px 16px; border-radius: 6px; display: inline-block; }}
    .urgente {{ background: #ffebee; border-left: 4px solid #f44336; padding: 10px 16px; margin: 6px 0; }}
    .importante {{ background: #fff8e1; border-left: 4px solid #ffa000; padding: 10px 16px; margin: 6px 0; }}
    .monitorar {{ background: #e3f2fd; border-left: 4px solid #1565c0; padding: 10px 16px; margin: 6px 0; }}
    .nudge {{ background: #e8eaf6; padding: 8px 14px; font-style: italic; border-radius: 6px; margin: 4px 0; }}
    .ritual {{ background: #f5f5f5; padding: 8px 14px; margin: 4px 0; border-radius: 4px; }}
    .footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #ccc; font-size: 0.8em; color: #999; }}
    @media print {{ body {{ font-size: 11pt; }} }}
</style>
</head>
<body>
<h1>PEEX Command Center — Briefing Semanal</h1>
<p><strong>{nome_un}</strong> | {hoje.strftime('%d/%m/%Y')} | Semana {semana}/47 | Cap {capitulo}/12 | {trimestre}o Tri</p>
<p><span class="fase">Fase {info['fase_num']}: {fase['nome']}</span></p>
"""

# Missoes
if urgentes:
    html += "<h2>Urgentes (resolver HOJE)</h2>\n"
    for b in urgentes:
        nudge = gerar_nudge(b)
        html += f'<div class="urgente"><strong>{b.get("icone","")} {b.get("o_que","")}</strong>'
        if b.get('como'):
            html += f'<br>Acao: {b["como"][0]}'
        if nudge:
            html += f'<div class="nudge">{nudge}</div>'
        html += '</div>\n'

if importantes:
    html += "<h2>Importantes (esta semana)</h2>\n"
    for b in importantes:
        html += f'<div class="importante"><strong>{b.get("icone","")} {b.get("o_que","")}</strong>'
        if b.get('como'):
            html += f'<br>Acao: {b["como"][0]}'
        html += '</div>\n'

if monitorar:
    html += "<h2>Monitorar</h2>\n"
    for b in monitorar:
        html += f'<div class="monitorar">{b.get("icone","")} {b.get("o_que","")}</div>\n'

# Pauta PEEX
if pauta:
    html += "<h2>Pauta PEEX</h2>\n"
    topicos = pauta.get('topicos', [])
    html += "<ol>\n"
    for t in topicos:
        html += f"<li>{t}</li>\n"
    html += "</ol>\n"

    rituais = pauta.get('rituais', [])
    if rituais:
        html += "<h2>Ritual de Floresta</h2>\n"
        for r in rituais:
            html += f'<div class="ritual"><strong>Ato {r["ato"]}: {r["nome"]}</strong> ({r["duracao"]}) — {r["conteudo"]}</div>\n'

    perguntas = pauta.get('perguntas', [])
    if perguntas:
        html += "<h2>Perguntas para Reflexao</h2>\n<ul>\n"
        for p in perguntas:
            html += f"<li>{p}</li>\n"
        html += "</ul>\n"

html += f"""
<div class="footer">
    PEEX Command Center — Colegio ELO 2026<br>
    Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>
</body>
</html>"""

# Preview
st.markdown("### Preview")
st.components.v1.html(html, height=600, scrolling=True)

# Download
st.markdown("---")
st.download_button(
    "Baixar HTML (imprimivel)",
    html,
    file_name=f"briefing_peex_sem{semana}_{user_unit}.html",
    mime="text/html",
)

# Texto puro tambem
texto_puro = []
texto_puro.append(f"BRIEFING PEEX — SEMANA {semana} — {nome_un}")
texto_puro.append(f"{hoje.strftime('%d/%m/%Y')} | Cap {capitulo}/12 | {trimestre}o Tri")
texto_puro.append(f"Fase {info['fase_num']}: {fase['nome']}")
texto_puro.append("")
if urgentes:
    texto_puro.append("=== URGENTES ===")
    for b in urgentes:
        texto_puro.append(f"[!] {b.get('o_que', '')}")
        if b.get('como'):
            texto_puro.append(f"    Acao: {b['como'][0]}")
    texto_puro.append("")
if importantes:
    texto_puro.append("=== IMPORTANTES ===")
    for b in importantes:
        texto_puro.append(f"[*] {b.get('o_que', '')}")
    texto_puro.append("")
texto_puro.append("---")
texto_puro.append("PEEX Command Center — Colegio ELO 2026")

st.download_button(
    "Baixar TXT (WhatsApp)",
    "\n".join(texto_puro),
    file_name=f"briefing_peex_sem{semana}_{user_unit}.txt",
    mime="text/plain",
)
