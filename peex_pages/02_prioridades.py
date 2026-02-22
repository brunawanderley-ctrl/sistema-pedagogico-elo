"""
PEEX — Prioridades da Semana (versao melhorada)
Briefing do coordenador com nudges, ritmo semanal e saude dos professores.
"""

import json
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    _hoje, UNIDADES_NOMES, DATA_DIR,
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
    carregar_frequencia_alunos, carregar_ocorrencias,
    CONFORMIDADE_META,
)
from components import cabecalho_pagina, metricas_em_colunas
from missoes import gerar_missao_id, carregar_status, salvar_status
from auth import get_user_unit, get_user_role
from engine import carregar_missoes_pregeradas
from narrativa import gerar_nudge
from peex_utils import info_semana, progresso_metas, nivel_escalacao, info_escalacao, FORMATOS_REUNIAO
from missoes_historico import obter_historico_completo


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
    .missao-secao { margin: 6px 0; }
    .missao-secao strong { color: #37474f; }
    .nudge-text {
        background: #e8eaf6;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 8px 0;
        font-style: italic;
        color: #283593;
        font-size: 0.95em;
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
    .ritmo-dia {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 8px;
        margin: 3px;
        font-size: 0.9em;
        font-weight: bold;
    }
    .ritmo-concluido { background: #c8e6c9; color: #2e7d32; }
    .ritmo-hoje { background: #fff9c4; color: #f57f17; border: 2px solid #f57f17; }
    .ritmo-futuro { background: #f5f5f5; color: #9e9e9e; }
    .ritmo-passado { background: #ffcdd2; color: #c62828; }
    .saude-prof {
        padding: 8px 14px;
        border-radius: 6px;
        margin: 4px 0;
        font-size: 0.9em;
    }
    .saude-verde { background: #e8f5e9; border-left: 4px solid #43a047; }
    .saude-amarelo { background: #fff8e1; border-left: 4px solid #ffa000; }
    .saude-vermelho { background: #ffebee; border-left: 4px solid #e53935; }
    .fase-strip {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 18px;
        border-radius: 8px;
        color: white;
        margin-bottom: 12px;
        font-size: 0.9em;
    }
    .fase-strip strong { font-size: 1.05em; }
    .reuniao-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.8em;
        font-weight: bold;
        color: white;
    }
    .meta-mini {
        margin: 4px 0;
        font-size: 0.85em;
    }
    .meta-mini-bar {
        width: 100%;
        height: 8px;
        background: #e0e0e0;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 2px;
    }
    .meta-mini-fill {
        height: 100%;
        border-radius: 4px;
    }
    .escalacao-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75em;
        font-weight: bold;
        color: white;
        margin-left: 8px;
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
    if role == 'ceo':
        coords = config.get('coordenadores', [])
    else:
        coords = [c for c in config.get('coordenadores', [])
                  if user_unit is None or c['unidade'] == user_unit]

    if not coords:
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
    idx = st.session_state.get('_coord_idx_peex', 0)
    escolha = st.selectbox(
        "Selecione o(a) coordenador(a):",
        nomes,
        index=min(idx, len(nomes) - 1),
        key="peex_coord",
    )
    st.session_state['_coord_idx_peex'] = nomes.index(escolha)

    return coords[nomes.index(escolha)]


# ========== RENDER ==========

def render_saudacao(coord, semana, capitulo, trimestre, n_missoes, n_urgentes):
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
            Voce tem <strong>{n_missoes} missao{"es" if n_missoes != 1 else ""}</strong>
            esta semana. {badge}
        </p>
        <div class="series-info">Suas series: {series_txt}</div>
    </div>
    """, unsafe_allow_html=True)


def render_resumo(missoes):
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


def render_comece_aqui(missao, idx):
    acoes_html = ''.join(f"<li>{a}</li>" for a in missao.get('como', []))
    nudge = gerar_nudge(missao)

    st.markdown(f"""
    <div class="comece-aqui">
        <div class="comece-label">COMECE POR AQUI</div>
        <span class="missao-score">Score: {missao['score']:.0f}</span>
        <div class="missao-titulo">{missao['icone']} {missao.get('o_que', '')}</div>
        <div class="missao-secao"><strong>POR QUE:</strong> {missao.get('por_que', '')}</div>
        <div class="missao-secao"><strong>COMO:</strong><ol>{acoes_html}</ol></div>
    </div>
    """, unsafe_allow_html=True)

    # Nudge
    if nudge:
        st.markdown(f'<div class="nudge-text">{nudge}</div>', unsafe_allow_html=True)

    _render_links_status(missao, idx)


def render_card_missao(missao, idx, compacto=False):
    css_class = f"missao-card-{missao['nivel'].lower()}"
    acoes_html = ''.join(f"<li>{a}</li>" for a in missao.get('como', []))
    nudge = gerar_nudge(missao)

    # Verificar escalacao
    esc = _get_escalacao_missao(missao)
    esc_html = ''
    if esc:
        esc_html = f'<span class="escalacao-badge" style="background:{esc["cor"]};">N{esc["nivel"]} {esc["nome"]} ({esc["semanas"]}sem)</span>'

    if compacto:
        st.markdown(f"""
        <div class="{css_class}">
            <span class="missao-score">Score: {missao['score']:.0f}</span>
            <strong>{missao['icone']} {missao.get('o_que', '')}</strong>{esc_html}
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="{css_class}">
        <span class="missao-score">Score: {missao['score']:.0f}</span>
        <div class="missao-titulo">{missao['icone']} {missao.get('o_que', '')}{esc_html}</div>
        <div class="missao-secao"><strong>POR QUE:</strong> {missao.get('por_que', '')}</div>
        <div class="missao-secao"><strong>COMO:</strong><ol>{acoes_html}</ol></div>
    </div>
    """, unsafe_allow_html=True)

    # Nudge
    if nudge:
        st.markdown(f'<div class="nudge-text">{nudge}</div>', unsafe_allow_html=True)

    _render_links_status(missao, idx)


def _render_links_status(missao, idx):
    links = missao.get('links', [])
    bid = gerar_missao_id(missao)
    status_atual = carregar_status().get(bid, {}).get('status', 'nao_iniciada')

    cols = st.columns([3, 2])
    with cols[0]:
        # Links inline no card — apontam para o sistema original
        for page_path, label in links:
            st.markdown(f"[{label}]({page_path})")
    with cols[1]:
        opcoes = ['Nao iniciada', 'Em andamento', 'Resolvida']
        mapa = {'nao_iniciada': 0, 'em_andamento': 1, 'resolvida': 2}
        status_novo = st.radio(
            "Status:",
            opcoes,
            index=mapa.get(status_atual, 0),
            key=f"peex_status_{idx}_{bid}",
            horizontal=True,
        )
        status_key = status_novo.lower().replace(' ', '_').replace('ã', 'a')
        if status_key != status_atual:
            salvar_status(bid, status_key)


# ========== RITMO SEMANAL ==========

def render_ritmo_semanal():
    """Mostra SEG→SEX com checkmarks para dias com registros."""
    st.markdown("### Ritmo Semanal")

    hoje = _hoje()
    # Calcular inicio da semana (segunda)
    dia_semana_idx = hoje.weekday()  # 0=seg, 6=dom
    segunda = hoje - timedelta(days=dia_semana_idx)

    dias_nome = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
    html_parts = []

    df_aulas = carregar_fato_aulas()
    if not df_aulas.empty:
        df_aulas = filtrar_ate_hoje(df_aulas)
        # Filtrar por unidade do usuario
        user_unit = get_user_unit()
        if user_unit:
            df_aulas = df_aulas[df_aulas['unidade'] == user_unit]

    for i, nome_dia in enumerate(dias_nome):
        dia = segunda + timedelta(days=i)

        if dia > hoje:
            css = "ritmo-futuro"
            check = ""
        elif dia == hoje:
            # Verificar se ja tem registros hoje
            if not df_aulas.empty and 'data' in df_aulas.columns:
                tem_registro = (df_aulas['data'].dt.date == dia.date()).any()
            else:
                tem_registro = False
            css = "ritmo-hoje"
            check = " ✓" if tem_registro else " ←"
        else:
            # Dia passado — verificar registros
            if not df_aulas.empty and 'data' in df_aulas.columns:
                tem_registro = (df_aulas['data'].dt.date == dia.date()).any()
            else:
                tem_registro = False
            css = "ritmo-concluido" if tem_registro else "ritmo-passado"
            check = " ✓" if tem_registro else " ✗"

        html_parts.append(f'<span class="ritmo-dia {css}">{nome_dia}{check}</span>')

    st.markdown(''.join(html_parts), unsafe_allow_html=True)


# ========== SAUDE DOS PROFESSORES ==========

def render_saude_professores(unidade, semana):
    """Agrupa professores por verde/amarelo/vermelho."""
    st.markdown("### Saude dos Professores")

    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()

    if df_aulas.empty or df_horario.empty:
        st.info("Dados insuficientes para calcular saude dos professores.")
        return

    df_aulas = filtrar_ate_hoje(df_aulas)

    # Professores esperados na unidade
    hor_un = df_horario[df_horario['unidade'] == unidade]
    if hor_un.empty:
        return

    profs_esperados = hor_un.groupby('professor').agg(
        slots=('disciplina', 'count'),
    ).reset_index()

    # Registros por professor
    aulas_un = df_aulas[df_aulas['unidade'] == unidade]
    registros = aulas_un.groupby('professor').size().reset_index(name='n_registros')

    # Merge
    df = profs_esperados.merge(registros, on='professor', how='left')
    df['n_registros'] = df['n_registros'].fillna(0).astype(int)
    esperado = df['slots'] * semana
    df['conformidade'] = (df['n_registros'] / esperado.clip(lower=1) * 100).round(0)

    # Classificar
    verde = df[df['conformidade'] >= 85].sort_values('conformidade', ascending=False)
    amarelo = df[(df['conformidade'] >= 50) & (df['conformidade'] < 85)].sort_values('conformidade')
    vermelho = df[df['conformidade'] < 50].sort_values('conformidade')

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Verde ({len(verde)})**")
        for _, r in verde.head(10).iterrows():
            st.markdown(
                f'<div class="saude-prof saude-verde">{r["professor"]} — {r["conformidade"]:.0f}%</div>',
                unsafe_allow_html=True,
            )
        if len(verde) > 10:
            st.caption(f"+{len(verde) - 10} professores")

    with c2:
        st.markdown(f"**Amarelo ({len(amarelo)})**")
        for _, r in amarelo.head(10).iterrows():
            st.markdown(
                f'<div class="saude-prof saude-amarelo">{r["professor"]} — {r["conformidade"]:.0f}%</div>',
                unsafe_allow_html=True,
            )
        if len(amarelo) > 10:
            st.caption(f"+{len(amarelo) - 10} professores")

    with c3:
        st.markdown(f"**Vermelho ({len(vermelho)})**")
        for _, r in vermelho.head(10).iterrows():
            st.markdown(
                f'<div class="saude-prof saude-vermelho">{r["professor"]} — {r["conformidade"]:.0f}%</div>',
                unsafe_allow_html=True,
            )
        if len(vermelho) > 10:
            st.caption(f"+{len(vermelho) - 10} professores")


# ========== FASE PEEX + METAS ==========

def render_fase_peex(semana):
    """Mostra barra de fase + proxima reuniao PEEX."""
    info = info_semana(semana)
    fase = info['fase']
    prox = info['proxima_reuniao']
    fmt = info['formato_reuniao']

    st.markdown(f"""
    <div class="fase-strip" style="background:{fase['cor']};">
        <strong>Fase {info['fase_num']}: {fase['nome']}</strong>
        <span>{fase['periodo']}</span>
    </div>
    """, unsafe_allow_html=True)

    if prox:
        fmt_cor = fmt.get('cor', '#607D8B')
        fmt_icone = fmt.get('icone', '')
        fmt_nome = fmt.get('nome', prox['formato'])
        st.markdown(f"""
        <span class="reuniao-pill" style="background:{fmt_cor};">
            {fmt_icone} Proxima: {prox['titulo']} ({fmt_nome}, sem {prox['semana']})
        </span>
        """, unsafe_allow_html=True)


def render_metas_fase(semana):
    """Mostra barras de progresso das metas da fase atual."""
    info = info_semana(semana)
    resumo_path = DATA_DIR / "resumo_Executivo.csv"
    if not resumo_path.exists():
        return

    resumo_df = pd.read_csv(resumo_path)
    total_row = resumo_df[resumo_df['unidade'] == 'TOTAL']
    if total_row.empty:
        return

    metas = progresso_metas(total_row.iloc[0], info['fase_num'])

    st.markdown("#### Metas da Fase")
    for m in metas:
        prog = m['progresso_pct']
        cor = '#2e7d32' if prog >= 80 else '#ffa000' if prog >= 40 else '#c62828'
        st.markdown(f"""
        <div class="meta-mini">
            <span>[{m['eixo']}] {m['indicador']}: {m['atual']}{m['unidade_medida']} / {m['meta']}{m['unidade_medida']} ({prog:.0f}%)</span>
            <div class="meta-mini-bar">
                <div class="meta-mini-fill" style="width:{prog}%; background:{cor};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _get_escalacao_missao(missao):
    """Retorna info de escalacao se a missao e persistente."""
    historico = obter_historico_completo()
    from missoes import gerar_missao_fingerprint
    fp = gerar_missao_fingerprint(missao)
    entry = historico.get(fp)
    if not entry:
        return None
    semanas = entry.get('semanas_ativas', 0)
    nivel = nivel_escalacao(semanas)
    if nivel == 0:
        return None
    esc_info = info_escalacao(nivel)
    return {
        'nivel': nivel,
        'semanas': semanas,
        'nome': esc_info['nome'] if esc_info else '',
        'cor': esc_info['cor'] if esc_info else '#607D8B',
    }


# ========== PAINEL RAPIDO ==========

def render_painel_rapido(unidade, semana):
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


# ========== EXPORTAR ==========

def gerar_texto_imprimivel(coord, missoes, semana, capitulo, trimestre):
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
            nudge = gerar_nudge(b)
            if nudge:
                linhas.append(f"   Dica: {nudge}")
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
    linhas.append("PEEX Command Center — Colegio ELO 2026")

    return "\n".join(linhas)


# ========== INDICADORES COM METAS ==========

def render_indicadores_meta(unidade, semana):
    """Graficos de barra horizontal: valor atual vs meta para indicadores-chave."""
    st.markdown("### Indicadores vs Metas")

    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()
    df_freq = carregar_frequencia_alunos()
    df_ocorr = carregar_ocorrencias()

    if df_aulas.empty or df_horario.empty:
        return

    df_aulas = filtrar_ate_hoje(df_aulas)

    # Filtrar por unidade
    a_un = df_aulas[df_aulas['unidade'] == unidade]
    h_un = df_horario[df_horario['unidade'] == unidade]

    # 1. Conformidade professor
    esperado = len(h_un) * semana if not h_un.empty else 0
    conf_val = (len(a_un) / esperado * 100) if esperado > 0 else 0
    conf_meta = CONFORMIDADE_META

    # 2. Frequencia alunos
    freq_val = 0
    freq_meta = 85
    if not df_freq.empty and 'unidade' in df_freq.columns:
        freq_un = df_freq[df_freq['unidade'] == unidade]
        if not freq_un.empty and 'pct_frequencia' in freq_un.columns:
            freq_val = freq_un['pct_frequencia'].mean()

    # 3. Cobertura conteudo
    com_cont = len(a_un[a_un['conteudo'].notna() & (a_un['conteudo'].astype(str).str.strip() != '')])
    cont_val = (com_cont / max(esperado, 1) * 100)
    cont_meta = 80

    # 4. Ocorrencias ultimos 7 dias
    ocorr_val = 0
    if not df_ocorr.empty and 'unidade' in df_ocorr.columns:
        hoje = _hoje()
        ocorr_un = df_ocorr[(df_ocorr['unidade'] == unidade)]
        if 'data' in ocorr_un.columns:
            ocorr_7d = ocorr_un[ocorr_un['data'] >= (hoje - pd.Timedelta(days=7))]
            ocorr_val = len(ocorr_7d)

    # Render indicadores como barras visuais
    indicadores = [
        ('Conformidade Professor', conf_val, conf_meta, '%'),
        ('Frequencia Alunos', freq_val, freq_meta, '%'),
        ('Cobertura Conteudo', cont_val, cont_meta, '%'),
    ]

    cols = st.columns(len(indicadores))
    for i, (nome, atual, meta, unid) in enumerate(indicadores):
        with cols[i]:
            pct = min(atual / max(meta, 1) * 100, 100)
            cor = '#43A047' if atual >= meta else '#FFA000' if atual >= meta * 0.7 else '#E53935'
            delta = atual - meta
            delta_str = f"{delta:+.0f}{unid}" if delta != 0 else "Na meta"
            st.metric(nome, f"{atual:.0f}{unid}", delta_str)
            st.markdown(f"""
            <div style="width:100%; height:10px; background:#e0e0e0; border-radius:5px; overflow:hidden;">
                <div style="width:{pct:.0f}%; height:100%; background:{cor}; border-radius:5px;"></div>
            </div>
            <div style="text-align:right; font-size:0.75em; color:#888;">Meta: {meta:.0f}{unid}</div>
            """, unsafe_allow_html=True)

    # Ocorrencias como info separada
    if ocorr_val > 0:
        st.caption(f"Ocorrencias nos ultimos 7 dias: **{ocorr_val}**")


# ========== MAIN ==========

def main():
    cabecalho_pagina("Prioridades da Semana", "O que precisa da sua atencao AGORA")

    coord = selecionar_coordenador()
    unidade = coord['unidade']
    series = coord.get('series', [])

    semana = calcular_semana_letiva()
    capitulo = calcular_capitulo_esperado(semana)
    trimestre = calcular_trimestre(semana)

    # ========== FASE PEEX (NOVO) ==========
    render_fase_peex(semana)

    # Usar missoes pre-geradas com fallback
    missoes = carregar_missoes_pregeradas(unidade, series)

    n_missoes = len(missoes)
    n_urgentes = len([b for b in missoes if b.get('nivel') == 'URGENTE'])

    # ========== SAUDACAO ==========
    render_saudacao(coord, semana, capitulo, trimestre, n_missoes, n_urgentes)

    # ========== INDICADORES VS METAS ==========
    render_indicadores_meta(unidade, semana)

    # ========== RITMO SEMANAL (NOVO) ==========
    render_ritmo_semanal()

    if n_missoes == 0:
        st.success("Nenhuma missao esta semana! Tudo em dia. Continue acompanhando.")
        st.markdown("---")
        render_saude_professores(unidade, semana)
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

    # ========== SAUDE DOS PROFESSORES (NOVO) ==========
    st.markdown("---")
    render_saude_professores(unidade, semana)

    # ========== METAS DA FASE (NOVO) ==========
    st.markdown("---")
    render_metas_fase(semana)

    # ========== PAINEL RAPIDO ==========
    st.markdown("---")
    st.markdown("### Painel Rapido")
    render_painel_rapido(unidade, semana)

    # ========== EXPORTAR ==========
    st.markdown("---")
    texto = gerar_texto_imprimivel(coord, missoes, semana, capitulo, trimestre)
    with st.expander("Copiar para WhatsApp / Imprimir"):
        st.text_area("", texto, height=300, key="peex_txt_export")
        st.download_button(
            "Baixar TXT",
            texto,
            file_name=f"prioridades_semana_{semana}_{unidade}.txt",
            mime="text/plain",
            key="peex_dl_txt",
        )


main()
