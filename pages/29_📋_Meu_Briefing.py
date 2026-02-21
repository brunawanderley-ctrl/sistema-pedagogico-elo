#!/usr/bin/env python3
"""
PAGINA 29: MEU BRIEFING
Versao alternativa do painel de batalhas semanais.
Tom pessoal, framework militar O QUE / POR QUE / COMO / ONDE.
Agrupamento por secao: URGENTES > IMPORTANTES > MONITORAR > PENDENCIAS.
"""

import json
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    _hoje, UNIDADES_NOMES, DATA_DIR,
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
)
from components import cabecalho_pagina, metricas_em_colunas
from batalhas import (
    gerar_batalhas, carregar_status, salvar_status, gerar_batalha_id,
)

st.set_page_config(page_title="Meu Briefing", page_icon="📋", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

# ========== CSS ==========
st.markdown("""
<style>
    .briefing-hero {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1976d2 100%);
        color: white;
        padding: 28px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .briefing-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
    }
    .briefing-hero h1 { color: white; margin: 0; font-size: 1.8em; }
    .briefing-hero .data-ctx {
        opacity: 0.8;
        font-size: 0.95em;
        margin: 6px 0;
    }
    .briefing-hero .resumo-frase {
        font-size: 1.2em;
        margin-top: 16px;
        line-height: 1.5;
    }
    .briefing-hero .badge-u {
        background: #ff1744;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85em;
    }
    .briefing-hero .series-tag {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        margin: 2px 4px 2px 0;
    }
    .secao-titulo {
        font-size: 1.1em;
        font-weight: bold;
        padding: 10px 0 6px 0;
        border-bottom: 2px solid;
        margin: 20px 0 12px 0;
    }
    .secao-urgente { color: #c62828; border-color: #c62828; }
    .secao-importante { color: #e65100; border-color: #e65100; }
    .secao-monitorar { color: #1565c0; border-color: #1565c0; }
    .secao-pendencia { color: #5c6bc0; border-color: #5c6bc0; }
    .card-briefing {
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .card-urgente {
        background: #fff5f5;
        border: 1px solid #ffcdd2;
        border-left: 6px solid #f44336;
    }
    .card-importante {
        background: #fffbf0;
        border: 1px solid #ffe0b2;
        border-left: 6px solid #ff9800;
    }
    .card-monitorar {
        background: #f0f7ff;
        border: 1px solid #bbdefb;
        border-left: 6px solid #2196f3;
    }
    .card-pendencia {
        background: #f3f0ff;
        border: 1px solid #d1c4e9;
        border-left: 6px solid #7c4dff;
    }
    .card-briefing .titulo-batalha {
        font-size: 1.05em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .card-briefing .campo {
        margin: 8px 0;
        padding: 6px 0;
    }
    .card-briefing .campo-label {
        display: inline-block;
        width: 80px;
        font-weight: bold;
        color: #37474f;
        vertical-align: top;
    }
    .card-briefing .campo-valor {
        display: inline-block;
        width: calc(100% - 90px);
        vertical-align: top;
    }
    .score-badge {
        float: right;
        background: #263238;
        color: white;
        padding: 3px 12px;
        border-radius: 14px;
        font-size: 0.78em;
        font-weight: bold;
    }
    .contador-inline {
        display: inline-flex;
        align-items: center;
        gap: 16px;
        margin: 12px 0;
    }
    .contador-item {
        text-align: center;
    }
    .contador-item .num {
        font-size: 2em;
        font-weight: bold;
        line-height: 1;
    }
    .contador-item .lbl {
        font-size: 0.75em;
        text-transform: uppercase;
        opacity: 0.7;
    }
    .impressao-box {
        background: #fafafa;
        border: 1px dashed #bdbdbd;
        border-radius: 8px;
        padding: 16px;
        font-family: monospace;
        font-size: 0.85em;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)


# ========== COORDENADOR ==========

def carregar_config():
    path = DATA_DIR / "config_coordenadores.json"
    if not path.exists():
        return {"coordenadores": [], "periodos_feedback": []}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def identificar_coordenador():
    config = carregar_config()
    user_unit = get_user_unit()
    coords = [c for c in config.get('coordenadores', [])
              if user_unit is None or c['unidade'] == user_unit]

    if not coords:
        from config_cores import ORDEM_SERIES
        return {'nome': 'Administrador', 'unidade': user_unit or 'BV', 'series': ORDEM_SERIES}

    if len(coords) == 1:
        return coords[0]

    nomes = [c['nome'] for c in coords]
    idx = st.session_state.get('_bf_coord_idx', 0)
    with st.sidebar:
        escolha = st.selectbox("Quem e voce?", nomes,
                               index=min(idx, len(nomes) - 1), key="bf_coord")
        st.session_state['_bf_coord_idx'] = nomes.index(escolha)
    return next(c for c in coords if c['nome'] == escolha)


# ========== RENDERS ==========

def render_hero(coord, semana, capitulo, trimestre, batalhas):
    hoje = _hoje()
    dias_pt = ['segunda-feira', 'terca-feira', 'quarta-feira',
               'quinta-feira', 'sexta-feira', 'sabado', 'domingo']
    hora = datetime.now().hour
    saudacao = "Bom dia" if hora < 12 else ("Boa tarde" if hora < 18 else "Boa noite")

    n = len(batalhas)
    n_u = len([b for b in batalhas if b['nivel'] == 'URGENTE'])
    n_i = len([b for b in batalhas if b['nivel'] == 'IMPORTANTE'])
    n_m = len([b for b in batalhas if b['nivel'] == 'MONITORAR'])

    series_tags = ''.join(f'<span class="series-tag">{s}</span>' for s in coord.get('series', []))

    badge = f'<span class="badge-u">{n_u} urgente{"s" if n_u != 1 else ""}</span>' if n_u else ''

    st.markdown(f"""
    <div class="briefing-hero">
        <h1>{saudacao}, {coord['nome']}!</h1>
        <div class="data-ctx">
            {dias_pt[hoje.weekday()].capitalize()}, {hoje.strftime('%d/%m/%Y')} |
            Semana {semana} de 47 | {trimestre}o Trimestre | Capitulo {capitulo}/12
        </div>
        <div style="margin-top:8px;">{series_tags}</div>
        <div class="resumo-frase">
            Voce tem <strong>{n} batalha{"s" if n != 1 else ""}</strong> esta semana. {badge}
        </div>
        <div class="contador-inline" style="color:white; margin-top:12px;">
            <div class="contador-item"><div class="num" style="color:#ff5252;">{n_u}</div><div class="lbl">Urgentes</div></div>
            <div class="contador-item"><div class="num" style="color:#ffab40;">{n_i}</div><div class="lbl">Importantes</div></div>
            <div class="contador-item"><div class="num" style="color:#82b1ff;">{n_m}</div><div class="lbl">Monitorar</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_card(batalha, idx, css_class):
    acoes = batalha.get('como', [])
    acoes_html = ''.join(f"<li>{a}</li>" for a in acoes)

    links_html = ''
    for path, label in batalha.get('links', []):
        links_html += f'<code>{label}</code> '

    st.markdown(f"""
    <div class="card-briefing {css_class}">
        <span class="score-badge">Score {batalha['score']:.0f}</span>
        <div class="titulo-batalha">{batalha['icone']} {batalha.get('o_que', '')}</div>
        <div class="campo">
            <span class="campo-label">POR QUE:</span>
            <span class="campo-valor">{batalha.get('por_que', '')}</span>
        </div>
        <div class="campo">
            <span class="campo-label">COMO:</span>
            <span class="campo-valor"><ol style="margin:0;padding-left:20px;">{acoes_html}</ol></span>
        </div>
        <div class="campo">
            <span class="campo-label">ONDE:</span>
            <span class="campo-valor">{links_html}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status + nota
    bid = gerar_batalha_id(batalha)
    status_salvo = carregar_status().get(bid, {}).get('status', 'nao_iniciada')
    nota_salva = carregar_status().get(bid, {}).get('nota', '')

    c1, c2 = st.columns([1, 2])
    with c1:
        opcoes = ['Nao iniciada', 'Em andamento', 'Resolvida']
        mapa = {'nao_iniciada': 0, 'em_andamento': 1, 'resolvida': 2}
        status_novo = st.radio("", opcoes, index=mapa.get(status_salvo, 0),
                               key=f"bf_st_{idx}", horizontal=True)
        sk = status_novo.lower().replace(' ', '_').replace('ã', 'a')
        if sk != status_salvo:
            salvar_status(bid, sk)
    with c2:
        nota = st.text_input("Nota:", value=nota_salva, key=f"bf_nota_{idx}",
                             placeholder="Ex: Falei com o professor, vai regularizar...")
        if nota != nota_salva:
            salvar_status(bid, status_salvo, nota)

    # Links como page_link
    for path, label in batalha.get('links', []):
        if Path(f"pages/{Path(path).name}").exists() or Path(path).exists():
            try:
                st.page_link(path, label=f"Ir para {label}")
            except Exception:
                pass


def render_secao(titulo, batalhas_secao, css_secao, css_card, start_idx):
    if not batalhas_secao:
        return start_idx
    st.markdown(f'<div class="secao-titulo {css_secao}">{titulo} ({len(batalhas_secao)})</div>',
                unsafe_allow_html=True)
    for i, b in enumerate(batalhas_secao):
        render_card(b, start_idx + i, css_card)
    return start_idx + len(batalhas_secao)


def render_painel(unidade, semana):
    df_aulas = carregar_fato_aulas()
    if df_aulas.empty:
        return
    df_aulas = filtrar_ate_hoje(df_aulas)
    df_horario = carregar_horario_esperado()

    un_a = df_aulas[df_aulas['unidade'] == unidade]
    un_h = df_horario[df_horario['unidade'] == unidade] if not df_horario.empty else pd.DataFrame()

    total = len(un_a)
    esperado = len(un_h) * semana if not un_h.empty else 0
    conf = round(total / esperado * 100, 1) if esperado > 0 else 0
    profs = f"{un_a['professor'].nunique()}/{un_h['professor'].nunique() if not un_h.empty else '?'}"
    com_cont = len(un_a[un_a['conteudo'].notna() & (un_a['conteudo'].astype(str).str.strip() != '')])
    cobertura = round(com_cont / max(esperado, 1) * 100, 1)

    metricas_em_colunas([
        {'label': f'Conformidade {unidade}', 'value': f'{conf:.0f}%'},
        {'label': 'Professores', 'value': profs},
        {'label': 'Cobertura Conteudo', 'value': f'{cobertura:.0f}%',
         'help': 'Aulas com conteudo / esperadas pela grade'},
        {'label': 'Aulas', 'value': f'{total:,} / {esperado:,}'},
    ])


def gerar_impressao(coord, batalhas, semana, capitulo, trimestre):
    hoje = _hoje()
    sep = "=" * 64
    linhas = [
        sep,
        f"  MEU BRIEFING SEMANAL — COLEGIO ELO 2026",
        sep,
        f"Coordenador(a): {coord['nome']}",
        f"Unidade: {UNIDADES_NOMES.get(coord['unidade'], coord['unidade'])} ({coord['unidade']})",
        f"Series: {', '.join(coord.get('series', []))}",
        f"Semana {semana} | {trimestre}o Tri | Cap {capitulo}/12 | {hoje.strftime('%d/%m/%Y')}",
        "",
        f"RESUMO: {len(batalhas)} batalhas",
        f"  Urgentes: {len([b for b in batalhas if b['nivel'] == 'URGENTE'])}",
        f"  Importantes: {len([b for b in batalhas if b['nivel'] == 'IMPORTANTE'])}",
        f"  Monitorar: {len([b for b in batalhas if b['nivel'] == 'MONITORAR'])}",
        "",
    ]

    grupos = [
        ('URGENTE', '--- URGENTES (resolver HOJE) ---'),
        ('IMPORTANTE', '--- IMPORTANTES (esta semana) ---'),
        ('MONITORAR', '--- MONITORAR ---'),
    ]

    n = 1
    for nivel, header in grupos:
        secao = [b for b in batalhas if b['nivel'] == nivel]
        if not secao:
            continue
        linhas.append(header)
        linhas.append("")
        for b in secao:
            linhas.append(f"{n}. {b['icone']} {b['o_que']}")
            linhas.append(f"   POR QUE: {b.get('por_que', '')}")
            if b.get('como'):
                linhas.append(f"   ACAO: {b['como'][0]}")
            linhas.append("")
            n += 1

    linhas.append(sep)
    linhas.append(f"Impresso em {hoje.strftime('%d/%m/%Y %H:%M')} | Coordenacao Pedagogica ELO")
    linhas.append(sep)
    return "\n".join(linhas)


# ========== MAIN ==========

def main():
    cabecalho_pagina("📋 Meu Briefing", "Seu resumo semanal personalizado")

    coord = identificar_coordenador()
    unidade = coord['unidade']
    series = coord.get('series', [])

    semana = calcular_semana_letiva()
    capitulo = calcular_capitulo_esperado(semana)
    trimestre = calcular_trimestre(semana)

    batalhas = gerar_batalhas(unidade, series)

    # ========== HERO ==========
    render_hero(coord, semana, capitulo, trimestre, batalhas)

    if not batalhas:
        st.balloons()
        st.success("Nenhuma batalha esta semana! Tudo sob controle. Parabens, {coord['nome']}!")
        st.markdown("---")
        render_painel(unidade, semana)
        return

    # ========== SECOES AGRUPADAS ==========
    urgentes = [b for b in batalhas if b['nivel'] == 'URGENTE']
    importantes = [b for b in batalhas if b['nivel'] == 'IMPORTANTE']
    monitorar = [b for b in batalhas if b['nivel'] == 'MONITORAR']

    idx = 0
    idx = render_secao("🔴 URGENTES — resolver HOJE", urgentes, "secao-urgente", "card-urgente", idx)
    idx = render_secao("🟡 IMPORTANTES — resolver esta semana", importantes, "secao-importante", "card-importante", idx)

    if monitorar:
        with st.expander(f"🔵 MONITORAR — {len(monitorar)} item(ns) para acompanhar"):
            for i, b in enumerate(monitorar):
                render_card(b, idx + i, "card-monitorar")

    # ========== PAINEL RAPIDO ==========
    st.markdown("---")
    st.markdown("### 📊 Numeros da Semana")
    render_painel(unidade, semana)

    # ========== LINKS RAPIDOS ==========
    st.markdown("---")
    st.markdown("### 🔗 Ir para...")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.page_link("pages/01_📊_Quadro_Gestão.py", label="📊 Quadro de Gestao")
        st.page_link("pages/13_🚦_Semáforo_Professor.py", label="🚦 Semaforo")
    with c2:
        st.page_link("pages/14_🧠_Alertas_Inteligentes.py", label="🧠 Alertas")
        st.page_link("pages/22_📋_Ocorrências.py", label="📋 Ocorrencias")
    with c3:
        st.page_link("pages/23_🚨_Alerta_Precoce_ABC.py", label="🚨 Alerta ABC")
        if Path("pages/12_📋_Agenda_Coordenação.py").exists():
            st.page_link("pages/12_📋_Agenda_Coordenação.py", label="📋 Agenda")

    # ========== IMPRESSAO / WHATSAPP ==========
    st.markdown("---")
    texto = gerar_impressao(coord, batalhas, semana, capitulo, trimestre)
    with st.expander("🖨️ Imprimir / Enviar por WhatsApp"):
        st.markdown(f'<div class="impressao-box">{texto}</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📄 Baixar TXT",
                texto,
                file_name=f"briefing_semana_{semana}_{unidade}.txt",
                mime="text/plain",
                key="bf_dl",
            )
        with col2:
            st.code(texto, language=None)


main()
