"""
PEEX — Comando CEO / Painel Diretor
Dashboard executivo com narrativa, 3 decisoes, heatmap, scorecard,
indice ELO, metas SMART e calendario PEEX.
CEO ve toda a rede. Diretor ve sua unidade + comparativo.
"""

import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import (
    get_user_role, get_user_unit, is_ceo, is_diretor,
    ROLE_CEO, ROLE_DIRETOR,
)
from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    _hoje, DATA_DIR, UNIDADES_NOMES, CONFORMIDADE_META, CONFORMIDADE_BAIXO,
)
from config_cores import CORES_UNIDADES
from engine import (
    carregar_narrativa_ceo, carregar_scorecard_diretor,
    carregar_missoes_pregeradas,
)
from peex_utils import (
    info_semana, calcular_indice_elo, progresso_metas, proximas_reunioes,
    estacao_atual, FORMATOS_REUNIAO,
)


# ========== GATE ==========

role = get_user_role()
if role != ROLE_CEO:
    st.stop()


# ========== CSS ==========

st.markdown("""
<style>
    .ceo-header {
        background: linear-gradient(135deg, #1a237e 0%, #4a148c 100%);
        color: white;
        padding: 28px;
        border-radius: 14px;
        margin-bottom: 24px;
    }
    .ceo-header h2 { color: white; margin: 0 0 8px 0; }
    .ceo-header .subtitle { opacity: 0.8; font-size: 0.95em; }
    .narrativa-box {
        background: #f5f5f5;
        border-left: 4px solid #1a237e;
        padding: 20px;
        border-radius: 8px;
        margin: 16px 0;
        line-height: 1.7;
        font-size: 1.05em;
    }
    .decisao-card {
        background: #fff3e0;
        border-left: 5px solid #e65100;
        padding: 16px 20px;
        margin: 10px 0;
        border-radius: 6px;
    }
    .decisao-titulo {
        font-weight: bold;
        font-size: 1.05em;
        margin-bottom: 6px;
    }
    .decisao-impacto {
        color: #bf360c;
        font-size: 0.9em;
        margin-top: 4px;
    }
    .scorecard {
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 12px;
    }
    .sc-verde { background: linear-gradient(135deg, #2e7d32, #43a047); }
    .sc-amarelo { background: linear-gradient(135deg, #e65100, #ff9800); }
    .sc-vermelho { background: linear-gradient(135deg, #b71c1c, #e53935); }
    .chip-container {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 10px;
    }
    .chip {
        background: rgba(255,255,255,0.15);
        padding: 4px 14px;
        border-radius: 16px;
        font-size: 0.9em;
    }
    .kpi-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .kpi-value { font-size: 2em; font-weight: bold; color: #1a237e; }
    .kpi-label { font-size: 0.85em; color: #666; margin-top: 4px; }
    .fase-bar {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 16px;
        font-weight: bold;
    }
    .fase-bar .fase-nome { font-size: 1.15em; }
    .fase-bar .fase-info { font-size: 0.85em; opacity: 0.85; }
    .reuniao-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: bold;
        color: white;
    }
    .ie-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .ie-value { font-size: 2.4em; font-weight: bold; }
    .ie-label { font-size: 0.85em; color: #666; margin-top: 4px; }
    .meta-row {
        margin: 8px 0;
    }
    .meta-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.9em;
        margin-bottom: 4px;
    }
    .meta-bar {
        width: 100%;
        height: 12px;
        background: #e0e0e0;
        border-radius: 6px;
        overflow: hidden;
    }
    .meta-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.3s;
    }
    .cal-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 16px;
        border-radius: 8px;
        margin: 6px 0;
        background: #f5f5f5;
    }
    .cal-item .cal-badge {
        padding: 4px 12px;
        border-radius: 16px;
        color: white;
        font-size: 0.8em;
        font-weight: bold;
        white-space: nowrap;
    }
    .cal-item .cal-titulo { font-weight: bold; font-size: 0.95em; }
    .cal-item .cal-foco { font-size: 0.85em; color: #666; }
</style>
""", unsafe_allow_html=True)


# ========== DADOS ==========

semana = calcular_semana_letiva()
capitulo = calcular_capitulo_esperado(semana)
trimestre = calcular_trimestre(semana)
hoje = _hoje()
user_unit = get_user_unit()

# Carregar resumo executivo
resumo_path = DATA_DIR / "resumo_Executivo.csv"
resumo_df = pd.read_csv(resumo_path) if resumo_path.exists() else pd.DataFrame()

# Carregar narrativa (pre-gerada ou on-the-fly)
narrativa_data = carregar_narrativa_ceo()

# Info PEEX da semana
info = info_semana(semana)
fase = info['fase']
estacao, tom_estacao = estacao_atual(semana)


# ========== SECAO 0: BARRA DE FASE + PROXIMA REUNIAO ==========

prox_reuniao = info['proxima_reuniao']
formato_reuniao = info['formato_reuniao']

st.markdown(f"""
<div class="fase-bar" style="background: {fase['cor']};">
    <div>
        <div class="fase-nome">Fase {info['fase_num']}: {fase['nome']}</div>
        <div class="fase-info">{fase['periodo']} | {fase['dias_letivos']} dias letivos | Estacao: {estacao.capitalize()} ({tom_estacao})</div>
    </div>
</div>
""", unsafe_allow_html=True)

if prox_reuniao:
    fmt_cor = formato_reuniao.get('cor', '#607D8B')
    fmt_icone = formato_reuniao.get('icone', '')
    fmt_nome = formato_reuniao.get('nome', prox_reuniao['formato'])
    st.markdown(f"""
    <div style="margin-bottom:16px;">
        <span class="reuniao-badge" style="background:{fmt_cor};">
            {fmt_icone} Proxima: {prox_reuniao['titulo']} ({fmt_nome}, sem {prox_reuniao['semana']})
        </span>
        <span style="color:#666; font-size:0.85em; margin-left:12px;">
            {prox_reuniao['data']} | {prox_reuniao['foco'][:80]}
        </span>
    </div>
    """, unsafe_allow_html=True)


# ========== SECAO 1: HEADER + NARRATIVA ==========

nome_display = st.session_state.get("display_name", "Gestor(a)")
titulo_papel = "Comando CEO" if is_ceo() else f"Painel Diretor — {UNIDADES_NOMES.get(user_unit, user_unit)}"

st.markdown(f"""
<div class="ceo-header">
    <h2>{titulo_papel}</h2>
    <div class="subtitle">{nome_display} — {hoje.strftime('%A, %d/%m/%Y').capitalize()}</div>
    <div class="chip-container">
        <span class="chip">Semana {semana}/47</span>
        <span class="chip">Cap {capitulo}/12</span>
        <span class="chip">{trimestre}o Trimestre</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Narrativa
st.markdown("### Narrativa da Semana")
narrativa_texto = narrativa_data.get('narrativa', 'Narrativa nao disponivel.')
st.markdown(f'<div class="narrativa-box">{narrativa_texto}</div>', unsafe_allow_html=True)

if narrativa_data.get('gerado_em'):
    st.caption(f"Gerado em: {narrativa_data['gerado_em'][:19].replace('T', ' ')}")


# ========== SECAO 2: 3 DECISOES ==========

st.markdown("---")
st.markdown("### 3 Decisoes Estrategicas")
st.caption("Missoes que persistem ha 4+ semanas sem resolucao")

decisoes = narrativa_data.get('decisoes', [])
if decisoes:
    for i, d in enumerate(decisoes, 1):
        unidade_nome = UNIDADES_NOMES.get(d.get('unidade', ''), d.get('unidade', ''))
        st.markdown(f"""
        <div class="decisao-card">
            <div class="decisao-titulo">#{i} — {d.get('titulo', '')} ({unidade_nome})</div>
            <div>{d.get('decisao', '')}</div>
            <div class="decisao-impacto">{d.get('impacto', '')}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Nenhuma missao persistente detectada (4+ semanas). Bom sinal!")


# ========== SECAO 3: HEATMAP ==========

st.markdown("---")
st.markdown("### Heatmap — Visao da Rede")

if not resumo_df.empty:
    unidades_df = resumo_df[resumo_df['unidade'] != 'TOTAL'].copy()

    if not unidades_df.empty:
        indicadores = {
            'Conformidade (%)': 'pct_conformidade_media',
            'Freq. >75% (%)': 'pct_freq_acima_75',
            'Prof. no Ritmo (%)': 'pct_prof_no_ritmo',
            'Conteudo Preenchido (%)': 'pct_conteudo_preenchido',
            'Alunos Risco (%)': 'pct_alunos_risco',
        }

        unidades_order = ['BV', 'CD', 'JG', 'CDR']
        unidades_presentes = [u for u in unidades_order if u in unidades_df['unidade'].values]
        nomes = [UNIDADES_NOMES.get(u, u) for u in unidades_presentes]

        z_data = []
        y_labels = []
        for label, col in indicadores.items():
            if col in unidades_df.columns:
                row = []
                for un in unidades_presentes:
                    val = unidades_df[unidades_df['unidade'] == un][col]
                    row.append(round(float(val.iloc[0]), 1) if not val.empty else 0)
                z_data.append(row)
                y_labels.append(label)

        if z_data:
            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=nomes,
                y=y_labels,
                colorscale='RdYlGn',
                text=[[f"{v:.0f}%" for v in row] for row in z_data],
                texttemplate="%{text}",
                textfont={"size": 14},
                hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>",
            ))
            fig.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("resumo_Executivo.csv nao encontrado. Execute a extracao do SIGA.")


# ========== SECAO 4: SCORECARD DIRETORES ==========

st.markdown("---")
st.markdown("### Scorecard por Unidade")

cols = st.columns(4)
for i, un_code in enumerate(['BV', 'CD', 'JG', 'CDR']):
    sc = carregar_scorecard_diretor(un_code)
    nome = UNIDADES_NOMES.get(un_code, un_code)
    cor = sc.get('cor_semaforo', 'vermelho')

    conf = sc.get('conformidade', 0)
    n_missoes = sc.get('n_missoes', 0)
    n_urgentes = sc.get('n_urgentes', 0)
    top = sc.get('top_missao', 'Sem dados')

    with cols[i]:
        st.markdown(f"""
        <div class="scorecard sc-{cor}">
            <div style="font-size:0.85em; opacity:0.85;">{nome}</div>
            <div style="font-size:2.2em; font-weight:bold;">{conf:.0f}%</div>
            <div style="font-size:0.8em;">conformidade</div>
        </div>
        """, unsafe_allow_html=True)

        st.metric("Missoes", n_missoes, f"{n_urgentes} urgentes" if n_urgentes else None,
                  delta_color="inverse")
        st.caption(f"Top: {top[:60]}...")

        if is_diretor() and user_unit == un_code:
            st.success("Sua unidade")


# ========== SECAO 5: METRICAS REDE ==========

st.markdown("---")
st.markdown("### Metricas da Rede")

if not resumo_df.empty:
    total = resumo_df[resumo_df['unidade'] == 'TOTAL']
    if not total.empty:
        t = total.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{int(t.get('total_alunos', 0)):,}</div>
                <div class="kpi-label">Alunos na Rede</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{t.get('pct_conformidade_media', 0):.0f}%</div>
                <div class="kpi-label">Conformidade Media</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{t.get('pct_prof_no_ritmo', 0):.0f}%</div>
                <div class="kpi-label">Profs no Ritmo SAE</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{t.get('pct_freq_acima_75', 0):.0f}%</div>
                <div class="kpi-label">Freq. acima 75%</div>
            </div>
            """, unsafe_allow_html=True)

        with c5:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{t.get('pct_alunos_risco', 0):.0f}%</div>
                <div class="kpi-label">Alunos em Risco</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Dados do resumo executivo nao disponiveis.")


# ========== SECAO 6: INDICE ELO DA REDE ==========

st.markdown("---")
st.markdown("### Indice ELO (IE)")
st.caption("Score composto 0-100: Conformidade 25% + Frequencia 20% + Ritmo SAE 20% + Freq>90% 15% + Risco 10% + Ocorrencias 10%")

if not resumo_df.empty:
    ie_cols = st.columns(5)
    # IE por unidade + rede
    unidades_ie = ['BV', 'CD', 'JG', 'CDR']
    for i, un_code in enumerate(unidades_ie):
        un_row = resumo_df[resumo_df['unidade'] == un_code]
        if not un_row.empty:
            ie = calcular_indice_elo(un_row.iloc[0])
        else:
            ie = 0
        cor_ie = '#2e7d32' if ie >= 70 else '#e65100' if ie >= 50 else '#c62828'
        nome = UNIDADES_NOMES.get(un_code, un_code)
        with ie_cols[i]:
            st.markdown(f"""
            <div class="ie-card">
                <div class="ie-value" style="color:{cor_ie};">{ie:.0f}</div>
                <div class="ie-label">{nome}</div>
            </div>
            """, unsafe_allow_html=True)

    # IE da rede
    total_row = resumo_df[resumo_df['unidade'] == 'TOTAL']
    ie_rede = calcular_indice_elo(total_row.iloc[0]) if not total_row.empty else 0
    cor_rede = '#2e7d32' if ie_rede >= 70 else '#e65100' if ie_rede >= 50 else '#c62828'
    with ie_cols[4]:
        st.markdown(f"""
        <div class="ie-card" style="border-color:{cor_rede};">
            <div class="ie-value" style="color:{cor_rede};">{ie_rede:.0f}</div>
            <div class="ie-label">Rede ELO</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Dados insuficientes para calcular IE.")


# ========== SECAO 7: METAS SMART COM PROGRESSO ==========

st.markdown("---")
st.markdown(f"### Metas SMART — Fase {info['fase_num']}: {fase['nome']}")

if not resumo_df.empty:
    total_row = resumo_df[resumo_df['unidade'] == 'TOTAL']
    if not total_row.empty:
        metas = progresso_metas(total_row.iloc[0], info['fase_num'])
        for m in metas:
            prog = m['progresso_pct']
            cor_barra = '#2e7d32' if prog >= 80 else '#ffa000' if prog >= 40 else '#c62828'
            direcao = '(menor = melhor)' if m['inverso'] else ''
            st.markdown(f"""
            <div class="meta-row">
                <div class="meta-label">
                    <span><strong>[{m['eixo']}]</strong> {m['indicador']} {direcao}</span>
                    <span>{m['atual']}{m['unidade_medida']} / meta: {m['meta']}{m['unidade_medida']} ({prog:.0f}%)</span>
                </div>
                <div class="meta-bar">
                    <div class="meta-bar-fill" style="width:{prog}%; background:{cor_barra};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Linha TOTAL nao encontrada no resumo executivo.")
else:
    st.info("Dados insuficientes para metas SMART.")


# ========== SECAO 8: CALENDARIO PEEX ==========

st.markdown("---")
st.markdown("### Calendario PEEX")
st.caption("Proximas reunioes programadas")

proximas = proximas_reunioes(semana, n=5)
if proximas:
    for r in proximas:
        st.markdown(f"""
        <div class="cal-item">
            <span class="cal-badge" style="background:{r['formato_cor']};">
                {r['formato_icone']} {r['formato_nome']} {r.get('formato_duracao', 30)}min
            </span>
            <div>
                <div class="cal-titulo">{r['cod']} — {r['titulo']} (Sem {r['semana']})</div>
                <div class="cal-foco">{r['data']} | {r['foco'][:100]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Nenhuma reuniao futura programada.")

# Marcos do trimestre
st.markdown("---")
st.markdown(f"### Marcos — Fase {info['fase_num']}")
marcos = info['marcos']
if marcos:
    for marco in marcos:
        st.markdown(f"- {marco}")
else:
    st.info("Nenhum marco definido para esta fase.")
