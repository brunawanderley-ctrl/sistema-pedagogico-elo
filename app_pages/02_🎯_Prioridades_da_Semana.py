#!/usr/bin/env python3
"""
PAGINA 02: PRIORIDADES DA SEMANA
Painel de missoes semanais personalizado para cada coordenador.
Detecta, prioriza e sugere acoes concretas.
Combina propostas Time Vermelho + Time Azul da Arena.
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
from missoes import (
    gerar_missoes, carregar_status, salvar_status, gerar_missao_id,
)

from auth import get_user_unit, get_user_role, ROLE_CEO

# ========== CSS ==========
st.markdown("""
<style>
    .briefing-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .briefing-header h2 { color: white; margin: 0; }
    .briefing-header .subtitle { opacity: 0.85; margin: 4px 0; }
    .briefing-header .badge-urgente {
        background: #f44336;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.9em;
        font-weight: bold;
    }
    .briefing-header .series-info {
        font-size: 0.85em;
        opacity: 0.7;
        margin-top: 8px;
    }
    .resumo-card {
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    .resumo-urgente { background: linear-gradient(135deg, #c62828, #e53935); }
    .resumo-importante { background: linear-gradient(135deg, #e65100, #ff9800); }
    .resumo-ok { background: linear-gradient(135deg, #2e7d32, #43a047); }
    .comece-aqui {
        background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
        border: 2px solid #FF8F00;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
    }
    .comece-label {
        font-size: 0.85em;
        color: #E65100;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .missao-card-urgente {
        background: #ffebee;
        border-left: 5px solid #f44336;
        padding: 16px 20px;
        margin: 10px 0;
        border-radius: 6px;
    }
    .missao-card-importante {
        background: #fff8e1;
        border-left: 5px solid #ffa000;
        padding: 16px 20px;
        margin: 10px 0;
        border-radius: 6px;
    }
    .missao-card-monitorar {
        background: #e3f2fd;
        border-left: 5px solid #1565c0;
        padding: 16px 20px;
        margin: 10px 0;
        border-radius: 6px;
    }
    .missao-score {
        float: right;
        background: #424242;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8em;
    }
    .missao-titulo {
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .missao-secao {
        margin: 6px 0;
    }
    .missao-secao strong {
        color: #37474f;
    }
    .context-chips {
        display: flex;
        gap: 12px;
        margin: 8px 0 0 0;
        flex-wrap: wrap;
    }
    .context-chip {
        background: rgba(255,255,255,0.15);
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)


# ========== COORDENADOR ==========

def carregar_config_coordenadores():
    path = DATA_DIR / "config_coordenadores.json"
    if not path.exists():
        return {"coordenadores": [], "periodos_feedback": []}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def selecionar_coordenador():
    """Retorna dict do coordenador selecionado {nome, unidade, series}.
    CEO ve TODOS os coordenadores de todas as unidades."""
    config = carregar_config_coordenadores()
    user_unit = get_user_unit()
    role = get_user_role()

    # CEO ve todos os coordenadores, independente da unidade
    if role == ROLE_CEO:
        coords = config.get('coordenadores', [])
    else:
        coords = [c for c in config.get('coordenadores', [])
                  if user_unit is None or c['unidade'] == user_unit]

    if not coords:
        # Fallback: admin sem coordenador cadastrado
        from config_cores import ORDEM_SERIES
        return {
            'nome': 'Administrador',
            'unidade': user_unit or 'BV',
            'series': ORDEM_SERIES,
        }

    if len(coords) == 1:
        return coords[0]

    # Multiplos coordenadores — seletor no topo da pagina
    nomes = [f"{c['nome']} ({UNIDADES_NOMES.get(c['unidade'], c['unidade'])})" for c in coords]
    idx = st.session_state.get('_coord_idx', 0)
    escolha = st.selectbox(
        "Selecione o(a) coordenador(a):",
        nomes,
        index=min(idx, len(nomes) - 1),
        key="pg02_coord",
    )
    st.session_state['_coord_idx'] = nomes.index(escolha)

    return coords[nomes.index(escolha)]


# ========== RENDER ==========

def render_saudacao(coord, semana, capitulo, trimestre, n_missoes, n_urgentes):
    """Renderiza header com saudacao personalizada para missoes."""
    hora = datetime.now().hour
    if hora < 12:
        saudacao = "Bom dia"
    elif hora < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    dias_pt = ['segunda-feira', 'terca-feira', 'quarta-feira',
               'quinta-feira', 'sexta-feira', 'sabado', 'domingo']
    hoje = _hoje()
    dia_semana = dias_pt[hoje.weekday()]

    badge = ""
    if n_urgentes > 0:
        badge = f'<span class="badge-urgente">{n_urgentes} urgente{"s" if n_urgentes != 1 else ""}</span>'

    series_txt = ', '.join(coord.get('series', []))

    st.markdown(f"""
    <div class="briefing-header">
        <h2>{saudacao}, {coord['nome']}!</h2>
        <div class="subtitle">
            {dia_semana.capitalize()}, {hoje.strftime('%d/%m/%Y')}
        </div>
        <div class="context-chips">
            <span class="context-chip">Semana {semana}/47</span>
            <span class="context-chip">Cap {capitulo}/12</span>
            <span class="context-chip">{trimestre}o Trimestre</span>
        </div>
        <p style="font-size:1.15em; margin-top:14px;">
            Voce tem <strong>{n_missoes} miss{"oes" if n_missoes != 1 else "ao"}</strong>
            esta semana. {badge}
        </p>
        <div class="series-info">Suas series: {series_txt}</div>
    </div>
    """, unsafe_allow_html=True)


def render_resumo(missoes):
    """3 cards: urgentes, importantes, monitorar."""
    urgentes = [b for b in missoes if b['nivel'] == 'URGENTE']
    importantes = [b for b in missoes if b['nivel'] == 'IMPORTANTE']
    monitorar = [b for b in missoes if b['nivel'] == 'MONITORAR']

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="resumo-card resumo-urgente">
            <div style="font-size:2.2em;">{len(urgentes)}</div>
            <div>URGENTE{"S" if len(urgentes) != 1 else ""}</div>
            <div style="font-size:0.8em; opacity:0.8;">Resolver HOJE</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="resumo-card resumo-importante">
            <div style="font-size:2.2em;">{len(importantes)}</div>
            <div>IMPORTANTE{"S" if len(importantes) != 1 else ""}</div>
            <div style="font-size:0.8em; opacity:0.8;">Esta semana</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="resumo-card resumo-ok">
            <div style="font-size:2.2em;">{len(monitorar)}</div>
            <div>MONITORAR</div>
            <div style="font-size:0.8em; opacity:0.8;">Acompanhar</div>
        </div>
        """, unsafe_allow_html=True)

    if urgentes:
        st.markdown(
            f"*Comece pela primeira missao — e a que mais afeta alunos esta semana.*"
        )


def render_comece_aqui(missao, idx):
    """Destaque visual para a missao #1."""
    acoes_html = ''.join(f"<li>{a}</li>" for a in missao.get('como', []))
    st.markdown(f"""
    <div class="comece-aqui">
        <div class="comece-label">COMECE POR AQUI</div>
        <span class="missao-score">Score: {missao['score']:.0f}</span>
        <div class="missao-titulo">{missao['icone']} {missao.get('o_que', '')}</div>
        <div class="missao-secao"><strong>POR QUE:</strong> {missao.get('por_que', '')}</div>
        <div class="missao-secao"><strong>COMO:</strong><ol>{acoes_html}</ol></div>
    </div>
    """, unsafe_allow_html=True)

    # Links e status
    _render_links_status(missao, idx)


def render_card_missao(missao, idx, compacto=False):
    """Card de missao normal."""
    css_class = f"missao-card-{missao['nivel'].lower()}"
    acoes_html = ''.join(f"<li>{a}</li>" for a in missao.get('como', []))

    if compacto:
        st.markdown(f"""
        <div class="{css_class}">
            <span class="missao-score">Score: {missao['score']:.0f}</span>
            <strong>{missao['icone']} {missao.get('o_que', '')}</strong>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="{css_class}">
        <span class="missao-score">Score: {missao['score']:.0f}</span>
        <div class="missao-titulo">{missao['icone']} {missao.get('o_que', '')}</div>
        <div class="missao-secao"><strong>POR QUE:</strong> {missao.get('por_que', '')}</div>
        <div class="missao-secao"><strong>COMO:</strong><ol>{acoes_html}</ol></div>
    </div>
    """, unsafe_allow_html=True)

    _render_links_status(missao, idx)


def _render_links_status(missao, idx):
    """Links para paginas + botoes de status."""
    links = missao.get('links', [])
    bid = gerar_missao_id(missao)
    status_atual = carregar_status().get(bid, {}).get('status', 'nao_iniciada')

    cols = st.columns([3, 2])
    with cols[0]:
        for path, label in links:
            if Path(f"app_pages/{Path(path).name}").exists() or Path(path).exists():
                try:
                    st.page_link(path, label=label)
                except Exception:
                    pass
    with cols[1]:
        opcoes = ['Nao iniciada', 'Em andamento', 'Resolvida']
        mapa = {'nao_iniciada': 0, 'em_andamento': 1, 'resolvida': 2}
        status_novo = st.radio(
            "Status:",
            opcoes,
            index=mapa.get(status_atual, 0),
            key=f"status_{idx}_{bid}",
            horizontal=True,
        )
        status_key = status_novo.lower().replace(' ', '_').replace('ã', 'a')
        if status_key != status_atual:
            salvar_status(bid, status_key)


def render_painel_rapido(unidade, semana):
    """Metricas de referencia no rodape."""
    df_aulas = carregar_fato_aulas()
    if df_aulas.empty:
        return
    df_aulas = filtrar_ate_hoje(df_aulas)
    df_horario = carregar_horario_esperado()

    mask_a = df_aulas['unidade'] == unidade
    mask_h = df_horario['unidade'] == unidade if not df_horario.empty else pd.Series(dtype=bool)

    aulas_un = df_aulas[mask_a]
    hor_un = df_horario[mask_h] if not df_horario.empty else pd.DataFrame()

    total = len(aulas_un)
    esperado = len(hor_un) * semana if not hor_un.empty else 0
    conf = round(total / esperado * 100, 1) if esperado > 0 else 0

    profs_ativos = aulas_un['professor'].nunique()
    profs_total = hor_un['professor'].nunique() if not hor_un.empty else profs_ativos

    # Conteudo real (fix do bug)
    com_conteudo = len(aulas_un[aulas_un['conteudo'].notna() & (aulas_un['conteudo'].astype(str).str.strip() != '')])
    pct_conteudo = round(com_conteudo / max(esperado, 1) * 100, 1)

    metricas = [
        {'label': f'Conformidade {unidade}', 'value': f'{conf:.0f}%'},
        {'label': 'Professores', 'value': f'{profs_ativos}/{profs_total}'},
        {'label': 'Cobertura Conteudo', 'value': f'{pct_conteudo:.0f}%',
         'help': 'Aulas com conteudo / aulas esperadas pela grade'},
        {'label': 'Aulas Registradas', 'value': f'{total:,}'},
    ]
    metricas_em_colunas(metricas)


def gerar_texto_imprimivel(coord, missoes, semana, capitulo, trimestre):
    """Gera texto limpo para copiar/WhatsApp."""
    hoje = _hoje()
    linhas = [
        "=" * 60,
        f"PRIORIDADES DA SEMANA {semana} - {UNIDADES_NOMES.get(coord['unidade'], coord['unidade'])}",
        "=" * 60,
        f"Coordenador(a): {coord['nome']}",
        f"Series: {', '.join(coord.get('series', []))}",
        f"Semana {semana} | {trimestre}o Tri | Cap {capitulo}/12 | {hoje.strftime('%d/%m/%Y')}",
        "",
    ]

    urgentes = [b for b in missoes if b['nivel'] == 'URGENTE']
    importantes = [b for b in missoes if b['nivel'] == 'IMPORTANTE']
    monitorar = [b for b in missoes if b['nivel'] == 'MONITORAR']

    n = 1
    if urgentes:
        linhas.append("--- URGENTES (resolver HOJE) ---")
        linhas.append("")
        for b in urgentes:
            linhas.append(f"{n}. [!] {b['o_que']}")
            if b.get('como'):
                linhas.append(f"   Acao: {b['como'][0]}")
            linhas.append("")
            n += 1

    if importantes:
        linhas.append("--- IMPORTANTES (esta semana) ---")
        linhas.append("")
        for b in importantes:
            linhas.append(f"{n}. [*] {b['o_que']}")
            if b.get('como'):
                linhas.append(f"   Acao: {b['como'][0]}")
            linhas.append("")
            n += 1

    if monitorar:
        linhas.append("--- MONITORAR ---")
        linhas.append("")
        for b in monitorar:
            linhas.append(f"{n}. [-] {b['o_que']}")
            linhas.append("")
            n += 1

    linhas.append(f"Total: {len(missoes)} missoes mapeadas")
    linhas.append("---")
    linhas.append("Sistema Pedagogico ELO 2026")

    return "\n".join(linhas)


# ========== MAIN ==========

def main():
    cabecalho_pagina("🎯 Prioridades da Semana", "O que precisa da sua atencao AGORA")

    coord = selecionar_coordenador()
    unidade = coord['unidade']
    series = coord.get('series', [])

    semana = calcular_semana_letiva()
    capitulo = calcular_capitulo_esperado(semana)
    trimestre = calcular_trimestre(semana)

    # Gerar missoes
    missoes = gerar_missoes(unidade, series)

    n_missoes = len(missoes)
    n_urgentes = len([b for b in missoes if b['nivel'] == 'URGENTE'])

    # ========== SAUDACAO ==========
    render_saudacao(coord, semana, capitulo, trimestre, n_missoes, n_urgentes)

    if n_missoes == 0:
        st.success("Nenhuma missao esta semana! Tudo em dia. Continue acompanhando.")
        st.markdown("---")
        render_painel_rapido(unidade, semana)
        return

    # ========== RESUMO (3 cards) ==========
    render_resumo(missoes)

    st.markdown("---")

    # ========== COMECE POR AQUI (missao #1) ==========
    render_comece_aqui(missoes[0], 0)

    # ========== MISSOES #2-5 ==========
    for i, b in enumerate(missoes[1:5], 1):
        st.markdown("")
        render_card_missao(b, i)

    # ========== RESTANTES (expander) ==========
    restantes = missoes[5:]
    if restantes:
        with st.expander(f"Ver mais {len(restantes)} situacao(oes)"):
            for i, b in enumerate(restantes, 5):
                render_card_missao(b, i, compacto=True)

    # ========== PAINEL RAPIDO ==========
    st.markdown("---")
    st.markdown("### 📊 Painel Rapido")
    render_painel_rapido(unidade, semana)

    # ========== EXPORTAR ==========
    st.markdown("---")
    texto = gerar_texto_imprimivel(coord, missoes, semana, capitulo, trimestre)
    with st.expander("📱 Copiar para WhatsApp / Imprimir"):
        st.text_area("", texto, height=300, key="txt_export")
        st.download_button(
            "Baixar TXT",
            texto,
            file_name=f"prioridades_semana_{semana}_{unidade}.txt",
            mime="text/plain",
            key="dl_txt",
        )


main()
