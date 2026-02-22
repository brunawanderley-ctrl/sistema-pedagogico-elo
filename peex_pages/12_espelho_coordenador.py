"""
PEEX — Espelho do Coordenador
360 graus: missoes resolvidas, tempo medio, feedbacks, comparativo com rede.
"""

import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit, get_user_role
from utils import (
    calcular_semana_letiva, UNIDADES_NOMES, WRITABLE_DIR, DATA_DIR,
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
    CONFORMIDADE_META,
)
from components import cabecalho_pagina
from missoes import carregar_status


# ========== CSS ==========

st.markdown("""
<style>
    .espelho-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .espelho-valor { font-size: 2em; font-weight: bold; color: #1a237e; }
    .espelho-label { font-size: 0.85em; color: #666; margin-top: 4px; }
    .espelho-comp {
        font-size: 0.8em;
        margin-top: 6px;
        padding: 3px 10px;
        border-radius: 10px;
        display: inline-block;
    }
    .comp-acima { background: #e8f5e9; color: #2e7d32; }
    .comp-abaixo { background: #ffebee; color: #c62828; }
    .guia-box {
        background: #E8EAF6;
        border-left: 4px solid #3F51B5;
        padding: 16px 20px;
        border-radius: 6px;
        margin: 12px 0;
    }
    .guia-box h4 { margin: 0 0 8px 0; color: #1a237e; }
    .passo-num {
        display: inline-block;
        background: #3F51B5;
        color: white;
        width: 28px; height: 28px;
        border-radius: 50%;
        text-align: center;
        line-height: 28px;
        font-weight: bold;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ========== MAIN ==========

cabecalho_pagina("Espelho do Coordenador", "Sua performance em 360 graus")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)

# ========== CONFORMIDADE REAL (dados do SIGA) ==========

df_aulas = carregar_fato_aulas()
df_horario = carregar_horario_esperado()

conf_val = 0
profs_ativos = 0
profs_total = 0
total_aulas = 0

if not df_aulas.empty and not df_horario.empty:
    df_aulas = filtrar_ate_hoje(df_aulas)
    a_un = df_aulas[df_aulas['unidade'] == user_unit]
    h_un = df_horario[df_horario['unidade'] == user_unit]
    esperado = len(h_un) * semana if not h_un.empty else 0
    total_aulas = len(a_un)
    conf_val = (total_aulas / esperado * 100) if esperado > 0 else 0
    profs_ativos = a_un['professor'].nunique()
    profs_total = h_un['professor'].nunique() if not h_un.empty else profs_ativos

# Carregar status de missoes
todos_status = carregar_status()

total_missoes = len(todos_status)
resolvidas = sum(1 for s in todos_status.values() if s.get('status') == 'resolvida')
em_andamento = sum(1 for s in todos_status.values() if s.get('status') == 'em_andamento')
nao_iniciadas = total_missoes - resolvidas - em_andamento
pct_resolvidas = round(resolvidas / max(total_missoes, 1) * 100, 0)

# ========== HEADER COM CONTEXTO ==========

st.markdown(f"### {nome_un} — Semana {semana}")

# Se tudo zerado, mostrar guia de orientacao
if total_missoes == 0 and total_aulas == 0:
    st.markdown("""
    <div class="guia-box">
        <h4>Bem-vindo ao seu Espelho!</h4>
        <p>Esta pagina mostra seu desempenho como coordenador(a). Ela sera preenchida automaticamente
        conforme o sistema coleta dados e voce interage com as missoes.</p>
        <p><strong>O que precisa acontecer para os dados aparecerem:</strong></p>
        <p><span class="passo-num">1</span> Os professores registram aulas no SIGA (diario de classe)</p>
        <p><span class="passo-num">2</span> O sistema extrai esses dados automaticamente (4x ao dia)</p>
        <p><span class="passo-num">3</span> Missoes sao geradas com base nos dados (o que precisa de atencao)</p>
        <p><span class="passo-num">4</span> Voce acessa <strong>Prioridades da Semana</strong> para ver e resolver suas missoes</p>
        <p>Conforme voce resolve missoes e os professores registram, este espelho vai refletir seu progresso.</p>
    </div>
    """, unsafe_allow_html=True)

elif total_missoes == 0:
    st.info(
        "Nenhuma missao rastreada ainda. Acesse **Prioridades da Semana** para ver suas missoes "
        "e comece a marcar o status de cada uma (Nao iniciada / Em andamento / Resolvida)."
    )


# ========== METRICAS REAIS ==========

c1, c2, c3, c4 = st.columns(4)

with c1:
    cor = '#2e7d32' if conf_val >= CONFORMIDADE_META else '#FFA000' if conf_val >= 50 else '#c62828'
    st.markdown(f"""
    <div class="espelho-card">
        <div class="espelho-valor" style="color:{cor};">{conf_val:.0f}%</div>
        <div class="espelho-label">Conformidade</div>
        <div style="font-size:0.75em; color:#999;">Meta: {CONFORMIDADE_META}%</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="espelho-card">
        <div class="espelho-valor">{profs_ativos}/{profs_total}</div>
        <div class="espelho-label">Professores Registrando</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="espelho-card">
        <div class="espelho-valor">{total_aulas:,}</div>
        <div class="espelho-label">Aulas Registradas</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    if total_missoes > 0:
        st.markdown(f"""
        <div class="espelho-card">
            <div class="espelho-valor">{pct_resolvidas:.0f}%</div>
            <div class="espelho-label">Missoes Resolvidas</div>
            <div style="font-size:0.75em; color:#999;">{resolvidas}/{total_missoes}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="espelho-card">
            <div class="espelho-valor">—</div>
            <div class="espelho-label">Missoes Resolvidas</div>
            <div style="font-size:0.75em; color:#999;">Acesse Prioridades</div>
        </div>
        """, unsafe_allow_html=True)


# ========== COMO FUNCIONA (sempre visivel) ==========

st.markdown("---")
with st.expander("Como funciona este espelho?", expanded=(total_missoes == 0)):
    st.markdown("""
**O que e uma missao?**
Missoes sao situacoes que o sistema detecta automaticamente a partir dos dados do SIGA:
- Professor que nao registra aulas ha mais de 5 dias
- Turma com conformidade muito baixa
- Disciplina sem nenhum registro no ano
- Queda brusca no ritmo de um professor

**De onde vem?**
O sistema analisa os dados 4 vezes ao dia e gera missoes ordenadas por urgencia.

**O que eu faco?**
1. Acesse **Prioridades da Semana** — la estao suas missoes da semana
2. Cada missao explica: O QUE e, POR QUE importa, e COMO resolver
3. Marque o status: **Nao iniciada** → **Em andamento** → **Resolvida**
4. Este espelho mostra seu progresso ao longo do tempo

**O que a CEO ve?**
A CEO ve o espelho de todos os coordenadores, comparando o desempenho entre unidades.
""")


# ========== GRAFICO DE EVOLUCAO ==========

st.markdown("---")
st.markdown("### Evolucao Temporal")

resumo_path = DATA_DIR / "resumo_Executivo.csv"
if resumo_path.exists():
    historico_path = WRITABLE_DIR / "historico_semanas.json"
    if historico_path.exists():
        try:
            with open(historico_path, 'r', encoding='utf-8') as f:
                historico = json.load(f)

            if historico:
                semanas = [h['semana'] for h in historico]
                conf_un = [h.get(f'conf_{user_unit}', 0) for h in historico]
                conf_rede = [h.get('conformidade_rede', 0) for h in historico]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=semanas, y=conf_un,
                    name=nome_un,
                    line=dict(width=3),
                    mode='lines+markers',
                ))
                fig.add_trace(go.Scatter(
                    x=semanas, y=conf_rede,
                    name='Media Rede',
                    line=dict(width=2, dash='dash', color='gray'),
                    mode='lines',
                ))
                fig.add_hline(y=CONFORMIDADE_META, line_dash="dot", line_color="green",
                              annotation_text=f"Meta {CONFORMIDADE_META}%")
                fig.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis_title='Semana',
                    yaxis_title='Conformidade (%)',
                    legend=dict(orientation='h', y=1.1),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("O grafico aparecera a partir da semana 2, quando houver dados para comparar.")
        except (json.JSONDecodeError, IOError):
            st.info("Erro ao carregar historico de semanas.")
    else:
        st.info("O grafico aparecera a partir da semana 2, quando houver dados para comparar.")
else:
    st.info("Aguardando primeira extracao de dados para gerar o grafico de evolucao.")


# ========== DETALHES ==========

st.markdown("---")
st.markdown("### Detalhamento")

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Missoes por Status**")
    if total_missoes > 0:
        st.markdown(f"- Resolvidas: **{resolvidas}**")
        st.markdown(f"- Em andamento: **{em_andamento}**")
        st.markdown(f"- Nao iniciadas: **{nao_iniciadas}**")
    else:
        st.caption("Nenhuma missao rastreada. Acesse Prioridades da Semana para comecar.")

with c2:
    # Carregar planos de acao
    planos_resolvidos = 0
    planos_total = 0
    for sem in range(1, semana + 1):
        path = WRITABLE_DIR / f"plano_acao_sem{sem}_{user_unit}.json"
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    plano = json.load(f)
                acoes = plano.get('acoes', [])
                planos_total += len(acoes)
                planos_resolvidos += sum(1 for a in acoes if a.get('status') == 'resolvida')
            except (json.JSONDecodeError, IOError):
                pass

    pct_execucao_plano = round(planos_resolvidos / max(planos_total, 1) * 100, 0)

    st.markdown("**Plano de Acao**")
    if planos_total > 0:
        st.markdown(f"- Acoes totais: **{planos_total}**")
        st.markdown(f"- Acoes resolvidas: **{planos_resolvidos}**")
        st.markdown(f"- Taxa de execucao: **{pct_execucao_plano:.0f}%**")
    else:
        st.caption("Nenhum plano de acao criado. Acesse Plano de Acao para criar o seu.")
