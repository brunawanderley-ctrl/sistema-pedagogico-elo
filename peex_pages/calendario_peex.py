"""
PEEX — Calendario 2026
Timeline visual de todas as 45 reunioes PEEX do ano.
Legenda de formatos, filtro por trimestre, ritual de floresta.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from peex_config import REUNIOES, FORMATOS_REUNIAO, FASES
from peex_utils import proximas_reunioes, info_semana
from utils import calcular_semana_letiva


# ========== CSS ==========

st.markdown("""
<style>
    .cal-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 14px;
        margin-bottom: 24px;
    }
    .cal-header h2 { color: white; margin: 0 0 8px 0; }
    .cal-header .cal-sub { opacity: 0.85; font-size: 0.95em; }
    .cal-semana-info {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px 20px;
        border-radius: 10px;
        background: #e8eaf6;
        border-left: 5px solid #1a237e;
        margin-bottom: 20px;
    }
    .cal-semana-info .semana-num {
        font-size: 2em;
        font-weight: bold;
        color: #1a237e;
    }
    .cal-semana-info .semana-detalhe {
        font-size: 0.95em;
        color: #333;
        line-height: 1.6;
    }
    .prox-destaque {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px 20px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 2px solid;
    }
    .prox-destaque .prox-badge {
        padding: 6px 16px;
        border-radius: 20px;
        color: white;
        font-size: 0.85em;
        font-weight: bold;
        white-space: nowrap;
    }
    .prox-destaque .prox-titulo { font-weight: bold; font-size: 1.05em; }
    .prox-destaque .prox-foco { font-size: 0.85em; color: #555; }
    .legenda-card {
        padding: 14px 18px;
        border-radius: 10px;
        border-left: 5px solid;
        margin-bottom: 10px;
        background: #fafafa;
    }
    .legenda-card .leg-titulo {
        font-weight: bold;
        font-size: 1em;
        margin-bottom: 4px;
    }
    .legenda-card .leg-detalhe {
        font-size: 0.9em;
        color: #555;
    }
    .tipo-card {
        padding: 14px 18px;
        border-radius: 10px;
        border-left: 5px solid;
        margin-bottom: 10px;
        background: #f5f5f5;
    }
    .tipo-card .tipo-titulo {
        font-weight: bold;
        font-size: 1em;
        margin-bottom: 4px;
    }
    .tipo-card .tipo-detalhe {
        font-size: 0.9em;
        color: #555;
    }
    .reuniao-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 16px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .reuniao-row .row-badge {
        padding: 4px 14px;
        border-radius: 16px;
        color: white;
        font-size: 0.8em;
        font-weight: bold;
        white-space: nowrap;
        min-width: 90px;
        text-align: center;
    }
    .reuniao-row .row-cod {
        font-weight: bold;
        min-width: 50px;
        font-size: 0.95em;
    }
    .reuniao-row .row-titulo { font-weight: bold; font-size: 0.95em; }
    .reuniao-row .row-foco { font-size: 0.85em; color: #666; }
    .row-highlight {
        background: #e8f5e9;
        border: 2px solid #43a047;
    }
    .row-proxima {
        background: #fff8e1;
        border: 1px solid #ffa000;
    }
    .row-normal {
        background: #f5f5f5;
    }
    .row-passada {
        background: #fafafa;
        opacity: 0.7;
    }
    .ato-card {
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid;
    }
    .ato-card .ato-titulo {
        font-weight: bold;
        font-size: 1.05em;
        margin-bottom: 4px;
    }
    .ato-card .ato-descricao {
        font-size: 0.9em;
        color: #444;
    }
    .ato-card .ato-tempo {
        font-size: 0.8em;
        color: #888;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ========== DADOS ==========

semana = calcular_semana_letiva()
info = info_semana(semana)
fase = info['fase']
hoje = datetime.now().date()


# ========== TITULO ==========

total_reunioes = len(REUNIOES)
reunioes_passadas = sum(1 for r in REUNIOES if r['semana'] < semana)
reunioes_restantes = total_reunioes - reunioes_passadas

st.markdown(f"""
<div class="cal-header">
    <h2>Calendario PEEX 2026</h2>
    <div class="cal-sub">
        {total_reunioes} reunioes programadas | {reunioes_passadas} realizadas | {reunioes_restantes} restantes |
        Fase {info['fase_num']}: {fase['nome']} ({fase['periodo']})
    </div>
</div>
""", unsafe_allow_html=True)


# ========== SECAO 1: INFO DA SEMANA ATUAL + PROXIMA REUNIAO ==========

st.markdown("### Semana Atual")

prox = info['proxima_reuniao']
fmt_prox = info['formato_reuniao']

st.markdown(f"""
<div class="cal-semana-info">
    <div class="semana-num">S{semana}</div>
    <div class="semana-detalhe">
        <strong>Semana {semana}/47</strong> — Fase {info['fase_num']}: {fase['nome']}<br>
        {fase['dias_letivos']} dias letivos | {fase['periodo']}
    </div>
</div>
""", unsafe_allow_html=True)

if prox:
    cor = fmt_prox.get('cor', '#607D8B')
    icone = fmt_prox.get('icone', '')
    nome_fmt = fmt_prox.get('nome', prox['formato'])
    duracao = fmt_prox.get('duracao', 30)
    st.markdown(f"""
    <div class="prox-destaque" style="border-color: {cor};">
        <span class="prox-badge" style="background: {cor};">{icone} {nome_fmt} {duracao}min</span>
        <div>
            <div class="prox-titulo">{prox['cod']} — {prox['titulo']} (Semana {prox['semana']}, {prox['data']})</div>
            <div class="prox-foco">{prox['foco']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Preview das proximas 3
st.markdown("**Proximas 3 reunioes:**")
prox3 = proximas_reunioes(semana, n=3)
for r in prox3:
    st.markdown(f"""
    <div class="prox-destaque" style="border-color: {r['formato_cor']}; border-width: 1px;">
        <span class="prox-badge" style="background: {r['formato_cor']};">{r['formato_icone']} {r['formato_nome']}</span>
        <div>
            <div class="prox-titulo">{r['cod']} — {r['titulo']} (Sem {r['semana']})</div>
            <div class="prox-foco">{r['data']} | {r['foco'][:100]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ========== SECAO 2: LEGENDA DOS FORMATOS ==========

st.markdown("---")
st.markdown("### Legenda dos Formatos")

formatos_info = [
    ('F',  'FLASH',       30, '#43A047', 'Relampago',   'Check rapido de indicadores. Objetivo: alinhamento em 30 minutos.'),
    ('FO', 'FOCO',        45, '#FFA000', 'Lupa',        'Aprofundamento em 1-2 temas criticos. Analise detalhada.'),
    ('C',  'CRISE',       60, '#C62828', 'Sirene',      'Emergencia ativada quando 5+ itens urgentes detectados.'),
    ('E',  'ESTRATEGICA', 90, '#1565C0', 'Alvo',        'Balanco trimestral completo. Planejamento e celebracao.'),
]

col1, col2 = st.columns(2)
for i, (cod, nome, dur, cor, icone_desc, desc) in enumerate(formatos_info):
    fmt = FORMATOS_REUNIAO.get(cod, {})
    icone = fmt.get('icone', '')
    container = col1 if i < 2 else col2
    with container:
        st.markdown(f"""
        <div class="legenda-card" style="border-left-color: {cor};">
            <div class="leg-titulo">{icone} {nome} ({cod}) — {dur} min</div>
            <div class="leg-detalhe">{desc}</div>
        </div>
        """, unsafe_allow_html=True)


# ========== SECAO 3: RR vs RU ==========

st.markdown("### Tipos de Reuniao")

tipos_info = [
    ('RR', 'Reuniao de Rede', '#1a237e',
     'CEO com todos os diretores e coordenadores das 4 unidades. Visao macro, decisoes estrategicas para toda a rede ELO.'),
    ('RU', 'Reuniao de Unidade', '#4a148c',
     'CEO/Diretor com coordenadores de 1 unidade especifica. Foco operacional, acompanhamento local.'),
]

for cod, nome, cor, desc in tipos_info:
    total_tipo = sum(1 for r in REUNIOES if r['tipo_reuniao'] == cod)
    st.markdown(f"""
    <div class="tipo-card" style="border-left-color: {cor};">
        <div class="tipo-titulo">{cod} — {nome} ({total_tipo} reunioes no ano)</div>
        <div class="tipo-detalhe">{desc}</div>
    </div>
    """, unsafe_allow_html=True)


# ========== SECAO 4: TABELA DE REUNIOES COM FILTRO ==========

st.markdown("---")
st.markdown("### Todas as Reunioes")

filtro_tri = st.selectbox(
    "Filtrar por trimestre",
    options=["Todos", "I Trimestre", "II Trimestre", "III Trimestre"],
    index=0,
)

# Filtrar reunioes
if filtro_tri == "I Trimestre":
    ini, fim = FASES[1]['semanas']
    reunioes_filtradas = [r for r in REUNIOES if ini <= r['semana'] <= fim]
    titulo_filtro = f"I Trimestre — Fase SOBREVIVENCIA ({FASES[1]['periodo']})"
elif filtro_tri == "II Trimestre":
    ini, fim = FASES[2]['semanas']
    reunioes_filtradas = [r for r in REUNIOES if ini <= r['semana'] <= fim]
    titulo_filtro = f"II Trimestre — Fase CONSOLIDACAO ({FASES[2]['periodo']})"
elif filtro_tri == "III Trimestre":
    ini, fim = FASES[3]['semanas']
    reunioes_filtradas = [r for r in REUNIOES if ini <= r['semana'] <= fim]
    titulo_filtro = f"III Trimestre — Fase EXCELENCIA ({FASES[3]['periodo']})"
else:
    reunioes_filtradas = REUNIOES
    titulo_filtro = "Ano Completo — 45 Reunioes"

st.caption(titulo_filtro)

# Identificar proximas 3 para destaque
prox3_ids = {r['id'] for r in proximas_reunioes(semana, n=3)}

# Montar DataFrame para exibicao
rows = []
for r in reunioes_filtradas:
    fmt = FORMATOS_REUNIAO.get(r['formato'], {})
    rows.append({
        'Data': r['data'],
        'Sem': r['semana'],
        'Codigo': r['cod'],
        'Tipo': r['tipo_reuniao'],
        'Formato': fmt.get('nome', r['formato']),
        'Duracao': f"{fmt.get('duracao', 30)} min",
        'Titulo': r['titulo'],
        'Foco': r['foco'],
    })

df_reunioes = pd.DataFrame(rows)

if not df_reunioes.empty:
    st.dataframe(
        df_reunioes,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Data': st.column_config.TextColumn('Data', width='small'),
            'Sem': st.column_config.NumberColumn('Sem', width='small'),
            'Codigo': st.column_config.TextColumn('Codigo', width='small'),
            'Tipo': st.column_config.TextColumn('Tipo', width='small'),
            'Formato': st.column_config.TextColumn('Formato', width='small'),
            'Duracao': st.column_config.TextColumn('Duracao', width='small'),
            'Titulo': st.column_config.TextColumn('Titulo', width='medium'),
            'Foco': st.column_config.TextColumn('Foco', width='large'),
        },
    )

# Timeline visual com badges coloridos
st.markdown("---")
st.markdown("### Timeline Visual")

for r in reunioes_filtradas:
    fmt = FORMATOS_REUNIAO.get(r['formato'], {})
    cor = fmt.get('cor', '#607D8B')
    icone = fmt.get('icone', '')
    nome_fmt = fmt.get('nome', r['formato'])

    # Determinar estilo da linha
    if r['semana'] == semana:
        row_class = "row-highlight"
        marker = " (ESTA SEMANA)"
    elif r['id'] in prox3_ids and r['semana'] > semana:
        row_class = "row-proxima"
        marker = ""
    elif r['semana'] < semana:
        row_class = "row-passada"
        marker = ""
    else:
        row_class = "row-normal"
        marker = ""

    st.markdown(f"""
    <div class="reuniao-row {row_class}">
        <span style="color:#999; font-size:0.8em; min-width:70px;">{r['data']}</span>
        <span class="row-cod">{r['cod']}</span>
        <span class="row-badge" style="background:{cor};">{icone} {nome_fmt}</span>
        <div>
            <div class="row-titulo">{r['titulo']}{marker}</div>
            <div class="row-foco">{r['foco'][:120]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ========== SECAO 5: ESTATISTICAS ==========

st.markdown("---")
st.markdown("### Estatisticas do Calendario")

c1, c2, c3, c4 = st.columns(4)

total_rr = sum(1 for r in REUNIOES if r['tipo_reuniao'] == 'RR')
total_ru = sum(1 for r in REUNIOES if r['tipo_reuniao'] == 'RU')

with c1:
    st.metric("Total de Reunioes", total_reunioes)
with c2:
    st.metric("Reunioes de Rede (RR)", total_rr)
with c3:
    st.metric("Reunioes de Unidade (RU)", total_ru)
with c4:
    st.metric("Realizadas / Restantes", f"{reunioes_passadas} / {reunioes_restantes}")

# Contagem por formato
st.markdown("**Distribuicao por formato:**")
fmt_cols = st.columns(4)
for i, (cod, fmt) in enumerate(FORMATOS_REUNIAO.items()):
    total_fmt = sum(1 for r in REUNIOES if r['formato'] == cod)
    horas_fmt = total_fmt * fmt['duracao'] / 60
    with fmt_cols[i]:
        st.markdown(f"""
        <div style="text-align:center; padding:12px; border-radius:10px; background:{fmt['cor']}15; border:1px solid {fmt['cor']}40;">
            <div style="font-size:1.8em;">{fmt['icone']}</div>
            <div style="font-weight:bold; color:{fmt['cor']};">{fmt['nome']}</div>
            <div style="font-size:1.4em; font-weight:bold;">{total_fmt}</div>
            <div style="font-size:0.8em; color:#666;">{horas_fmt:.1f}h total</div>
        </div>
        """, unsafe_allow_html=True)


# ========== SECAO 6: RITUAL DE FLORESTA ==========

st.markdown("---")
st.markdown("### Ritual de Floresta")
st.caption("Estrutura padrao de cada reuniao PEEX — 5 atos inspirados no ciclo da floresta")

atos = [
    {
        'num': 1, 'nome': 'Raizes', 'tempo': '5 min',
        'cor': '#5D4037',
        'descricao': 'Ancoragem emocional, check-in da equipe. Como cada um esta chegando? '
                     'Momento de presenca e conexao antes de olhar os dados.',
    },
    {
        'num': 2, 'nome': 'Solo', 'tempo': '10 min',
        'cor': '#795548',
        'descricao': 'Dados da semana, indicadores, numeros. O solo e o que sustenta: '
                     'conformidade, frequencia, ritmo SAE, ocorrencias. Leitura objetiva.',
    },
    {
        'num': 3, 'nome': 'Micelio', 'tempo': '10 min',
        'cor': '#2E7D32',
        'descricao': 'Conexoes invisiveis. Quem precisa de ajuda? Quais pareamentos funcionam? '
                     'Coordenador X pode apoiar Y? Rede de suporte entre pares.',
    },
    {
        'num': 4, 'nome': 'Sementes', 'tempo': '10 min',
        'cor': '#F57C00',
        'descricao': 'Plano de acao concreto. O que cada pessoa vai fazer ate a proxima reuniao? '
                     'Compromissos com nome, prazo e entregavel. Sem generalismos.',
    },
    {
        'num': 5, 'nome': 'Chuva', 'tempo': '5 min',
        'cor': '#1565C0',
        'descricao': 'Encerramento positivo. O que celebramos esta semana? Quem merece reconhecimento? '
                     'Energia para a semana que vem. Gratidao.',
    },
]

for ato in atos:
    st.markdown(f"""
    <div class="ato-card" style="border-left-color: {ato['cor']}; background: {ato['cor']}08;">
        <div class="ato-titulo" style="color: {ato['cor']};">Ato {ato['num']} — {ato['nome']}</div>
        <div class="ato-descricao">{ato['descricao']}</div>
        <div class="ato-tempo">{ato['tempo']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
> **Tempo total do ritual:** 40 minutos (ajustavel ao formato da reuniao).
> Em reunioes FLASH (30 min), comprimir Solo + Micelio.
> Em reunioes ESTRATEGICA (90 min), expandir cada ato com dados detalhados.
""")
