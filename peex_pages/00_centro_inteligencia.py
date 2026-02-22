"""
PEEX — Centro de Inteligencia
Landing page da CEO com visao consolidada: narrativa, decisoes, mapa da rede,
projecoes, reunioes e genealogia intelectual do PEEX.
"""

import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_role, ROLE_CEO
from utils import (
    WRITABLE_DIR, DATA_DIR, UNIDADES_NOMES,
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    _hoje,
)
from engine import (
    carregar_narrativa_ceo, carregar_scorecard_diretor,
    carregar_missoes_pregeradas, carregar_preditor, carregar_preparador,
)
from peex_utils import (
    info_semana, calcular_indice_elo, progresso_metas,
    estacao_atual, proximas_reunioes,
)
from peex_config import FASES, DIFERENCIACAO_UNIDADE, REUNIOES, FORMATOS_REUNIAO

# LLM engine — modulo opcional, pode nao existir ainda
try:
    from llm_engine import AnalistaELO, carregar_analista, _llm_disponivel
    _HAS_LLM = True
except ImportError:
    _HAS_LLM = False

    def _llm_disponivel():
        return False

    def carregar_analista():
        return None


# ========== GATE ==========

role = get_user_role()
if role != ROLE_CEO:
    st.warning("Acesso restrito ao Centro de Inteligencia PEEX. Perfil CEO necessario.")
    st.stop()


# ========== CSS ==========

st.markdown("""
<style>
    .ci-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2838 40%, #1a237e 100%);
        color: white;
        padding: 32px;
        border-radius: 14px;
        margin-bottom: 24px;
    }
    .ci-header h2 {
        color: white !important;
        margin: 0 0 6px 0;
        font-size: 1.8em;
        letter-spacing: 2px;
    }
    .ci-header .ci-subtitle {
        opacity: 0.85;
        font-size: 0.95em;
        margin-bottom: 10px;
    }
    .ci-header .ci-motto {
        font-style: italic;
        opacity: 0.7;
        font-size: 0.88em;
        margin-top: 8px;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 8px;
    }
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
    .narrativa-box {
        background: #f5f5f5;
        border-left: 4px solid #1a237e;
        padding: 20px;
        border-radius: 8px;
        margin: 16px 0;
        line-height: 1.7;
        font-size: 1.05em;
    }
    .fonte-badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.78em;
        font-weight: bold;
        color: white;
        margin-top: 6px;
    }
    .fonte-llm { background: #7B1FA2; }
    .fonte-template { background: #607D8B; }
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
    .decisao-opcoes {
        font-size: 0.9em;
        color: #555;
        margin-top: 4px;
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
    .semaforo-dot {
        display: inline-block;
        width: 14px; height: 14px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .proj-card {
        background: #f5f5f5;
        border-left: 4px solid #1565C0;
        padding: 14px 18px;
        border-radius: 6px;
        margin: 8px 0;
    }
    .proj-tendencia { font-size: 0.9em; font-weight: bold; }
    .tend-subindo { color: #2e7d32; }
    .tend-caindo { color: #c62828; }
    .tend-estavel { color: #e65100; }
    .alerta-proj {
        background: #ffebee;
        border-left: 4px solid #c62828;
        padding: 10px 16px;
        border-radius: 6px;
        margin: 6px 0;
        font-size: 0.9em;
    }
    .gen-tree {
        background: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        font-family: monospace;
        font-size: 0.88em;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .gen-node {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        margin: 2px 4px;
        font-weight: bold;
    }
    .gen-plano { background: #E3F2FD; color: #1565C0; }
    .gen-competidor { background: #FFF3E0; color: #E65100; }
    .gen-sintese { background: #E8F5E9; color: #2E7D32; }
    .gen-impl { background: #F3E5F5; color: #7B1FA2; }
    .diff-note {
        background: #E8EAF6;
        border-left: 3px solid #3F51B5;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 6px 0;
        font-size: 0.88em;
    }
    .reuniao-preview {
        background: #f8f9fa;
        border-left: 4px solid #1565C0;
        padding: 14px 18px;
        border-radius: 6px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)


# ========== DADOS ==========

semana = calcular_semana_letiva()
capitulo = calcular_capitulo_esperado(semana)
trimestre = calcular_trimestre(semana)
hoje = _hoje()

info = info_semana(semana)
fase = info['fase']
fase_num = info['fase_num']
estacao, tom_estacao = estacao_atual(semana)


# ========== HEADER ==========

st.markdown(f"""
<div class="ci-header">
    <h2>CENTRO DE INTELIGENCIA PEEX</h2>
    <div class="ci-subtitle">
        Guardiao da Floresta | Semana {semana} | Fase {fase_num}: {fase['nome']} | Estacao: {estacao.capitalize()}
    </div>
    <div class="chip-container">
        <span class="chip">Sem {semana}/47</span>
        <span class="chip">Cap {capitulo}/12</span>
        <span class="chip">{trimestre}o Trimestre</span>
        <span class="chip">{tom_estacao}</span>
    </div>
    <div class="ci-motto">"Mede quanto voce cresce, nao onde voce esta"</div>
</div>
""", unsafe_allow_html=True)


# ========== 6 TABS ==========

tab_narrativa, tab_decisoes, tab_mapa, tab_projecoes, tab_reunioes, tab_genealogia = st.tabs([
    "Narrativa", "Decisoes", "Mapa da Rede", "Projecoes", "Reunioes", "Genealogia",
])


# ---------- TAB 1: NARRATIVA ----------

with tab_narrativa:
    st.markdown("### Narrativa da Semana")

    # Try LLM-enriched narrative first, fallback to template
    fonte = "Template"
    narrativa_data = {}
    analista = None

    if _HAS_LLM and _llm_disponivel():
        try:
            analista = carregar_analista()
            if analista and hasattr(analista, 'narrativa') and analista.narrativa:
                narrativa_data = {
                    'narrativa': analista.narrativa,
                    'decisoes': getattr(analista, 'decisoes', []),
                    'gerado_em': getattr(analista, 'gerado_em', ''),
                }
                fonte = "LLM"
        except Exception:
            analista = None

    if not narrativa_data or not narrativa_data.get('narrativa'):
        try:
            narrativa_data = carregar_narrativa_ceo()
            fonte = "Template"
        except Exception:
            narrativa_data = {'narrativa': 'Narrativa nao disponivel. Execute o Estrategista.'}
            fonte = "Template"

    narrativa_texto = narrativa_data.get('narrativa', 'Narrativa nao disponivel.')
    st.markdown(f'<div class="narrativa-box">{narrativa_texto}</div>', unsafe_allow_html=True)

    # Fonte badge
    badge_class = 'fonte-llm' if fonte == 'LLM' else 'fonte-template'
    st.markdown(f'<span class="fonte-badge {badge_class}">Fonte: {fonte}</span>', unsafe_allow_html=True)

    if narrativa_data.get('gerado_em'):
        gerado = str(narrativa_data['gerado_em'])[:19].replace('T', ' ')
        st.caption(f"Gerado em: {gerado}")

    with st.expander("Origem"):
        st.markdown(
            "Narrativa baseada na **Sintese Final** + **Plano Definitivo**. "
            "O Estrategista consolida dados do resumo executivo, historico semanal "
            "e missoes persistentes para gerar a narrativa."
        )
        st.caption(f"Semana: {narrativa_data.get('semana', semana)} | "
                    f"Persistentes: {narrativa_data.get('n_persistentes', '?')}")


# ---------- TAB 2: DECISOES ----------

with tab_decisoes:
    st.markdown("### 3 Decisoes Estrategicas")
    st.caption("Missoes que persistem ha 4+ semanas sem resolucao")

    decisoes = narrativa_data.get('decisoes', [])

    if not decisoes and analista:
        try:
            decisoes = getattr(analista, 'decisoes', [])
        except Exception:
            decisoes = []

    if decisoes:
        for i, d in enumerate(decisoes[:3], 1):
            titulo = d.get('titulo', d.get('o_que', f'Decisao {i}'))
            unidade_nome = UNIDADES_NOMES.get(d.get('unidade', ''), d.get('unidade', ''))
            analise = d.get('decisao', d.get('analise', ''))
            impacto = d.get('impacto', '')
            opcoes = d.get('opcoes', d.get('como', []))

            opcoes_html = ''
            if opcoes:
                if isinstance(opcoes, list):
                    opcoes_html = '<div class="decisao-opcoes"><strong>Opcoes:</strong> ' + \
                        ' | '.join(str(o) for o in opcoes[:3]) + '</div>'
                elif isinstance(opcoes, str):
                    opcoes_html = f'<div class="decisao-opcoes"><strong>Opcoes:</strong> {opcoes}</div>'

            st.markdown(f"""
            <div class="decisao-card">
                <div class="decisao-titulo">#{i} — {titulo}{f' ({unidade_nome})' if unidade_nome else ''}</div>
                <div>{analise}</div>
                {opcoes_html}
                {'<div class="decisao-impacto">' + impacto + '</div>' if impacto else ''}
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Origem — Decisao #{i}"):
                st.markdown(
                    f"**Tipo:** {d.get('tipo', d.get('tipo_gatilho', 'Persistente'))}\n\n"
                    f"**Unidade:** {unidade_nome or 'Rede'}\n\n"
                    f"**Semanas ativa:** {d.get('semanas_ativas', '?')}\n\n"
                    f"Decisao derivada da Sintese Final + Plano Definitivo."
                )
    else:
        st.info("Nenhuma missao persistente detectada (4+ semanas). Bom sinal!")


# ---------- TAB 3: MAPA DA REDE ----------

with tab_mapa:
    st.markdown("### Mapa da Rede — Heatmap + Indice ELO")

    resumo_path = DATA_DIR / "resumo_Executivo.csv"
    try:
        resumo_df = pd.read_csv(resumo_path) if resumo_path.exists() else pd.DataFrame()
    except Exception:
        resumo_df = pd.DataFrame()

    if not resumo_df.empty:
        unidades_df = resumo_df[resumo_df['unidade'] != 'TOTAL'].copy()

        # --- Heatmap ---
        if not unidades_df.empty:
            indicadores = {
                'Conformidade (%)': 'pct_conformidade_media',
                'Frequencia (%)': 'frequencia_media',
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
                    height=360,
                    margin=dict(l=10, r=10, t=10, b=10),
                    yaxis=dict(autorange="reversed"),
                )
                st.plotly_chart(fig, use_container_width=True)

        # --- Indice ELO por unidade ---
        st.markdown("#### Indice ELO (IE) por Unidade")
        ie_cols = st.columns(4)
        for i, un_code in enumerate(['BV', 'CD', 'JG', 'CDR']):
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

        # --- Semaforo ---
        st.markdown("#### Semaforo")
        for un_code in ['BV', 'CD', 'JG', 'CDR']:
            sc = carregar_scorecard_diretor(un_code)
            cor_sem = sc.get('cor_semaforo', 'vermelho')
            cor_map = {'verde': '#4CAF50', 'amarelo': '#FFA000', 'vermelho': '#F44336'}
            cor_dot = cor_map.get(cor_sem, '#F44336')
            nome = UNIDADES_NOMES.get(un_code, un_code)
            conf = sc.get('conformidade', 0)
            st.markdown(
                f'<span class="semaforo-dot" style="background:{cor_dot};"></span>'
                f'**{nome}** — {conf:.0f}% conformidade | '
                f'{sc.get("n_missoes", 0)} missoes ({sc.get("n_urgentes", 0)} urgentes)',
                unsafe_allow_html=True,
            )

        # --- Diferenciacao por unidade ---
        st.markdown("#### Diferenciacao por Unidade")
        for un_code in ['BV', 'CD', 'JG', 'CDR']:
            diff = DIFERENCIACAO_UNIDADE.get(un_code, {})
            nome = UNIDADES_NOMES.get(un_code, un_code)
            foco = diff.get('foco', '')
            coord = diff.get('coordenadores', '')
            st.markdown(f"""
            <div class="diff-note">
                <strong>{nome}</strong>: {foco}<br>
                <small>Coordenadores: {coord} | Escalacao: {diff.get('escalacao', 'N/A')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("resumo_Executivo.csv nao encontrado. Execute a extracao do SIGA.")


# ---------- TAB 4: PROJECOES ----------

with tab_projecoes:
    st.markdown("### Projecoes de Conformidade")
    st.caption("Regressao linear sobre historico semanal — gerada pelo Preditor (sexta 20h)")

    try:
        preditor_data = carregar_preditor()
    except Exception:
        preditor_data = {}

    projecoes = preditor_data.get('projecoes', {})
    alertas_pred = preditor_data.get('alertas', [])

    if projecoes:
        n_semanas = preditor_data.get('n_semanas_historico', '?')
        st.caption(f"Baseado em {n_semanas} semanas de historico")

        for un_code in ['BV', 'CD', 'JG', 'CDR']:
            proj = projecoes.get(un_code, {})
            if not proj:
                continue

            nome = UNIDADES_NOMES.get(un_code, un_code)
            atual = proj.get('atual', 0)
            p1 = proj.get('proj_sem_mais_1', 0)
            p2 = proj.get('proj_sem_mais_2', 0)
            tendencia = proj.get('tendencia', 'estavel')

            tend_class = f'tend-{tendencia}'
            tend_seta = {'subindo': '/\\', 'caindo': '\\/', 'estavel': '--'}.get(tendencia, '--')

            st.markdown(f"""
            <div class="proj-card">
                <strong>{nome}</strong>
                <span class="proj-tendencia {tend_class}" style="float:right;">{tend_seta} {tendencia.upper()}</span>
                <br>
                <table style="width:100%; margin-top:8px; font-size:0.9em;">
                    <tr>
                        <td><strong>Atual:</strong> {atual:.1f}%</td>
                        <td><strong>+1 sem:</strong> {p1:.1f}%</td>
                        <td><strong>+2 sem:</strong> {p2:.1f}%</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

        # Alertas do preditor
        if alertas_pred:
            st.markdown("#### Alertas Preventivos")
            for alerta in alertas_pred:
                urgencia = alerta.get('urgencia', 'media')
                st.markdown(f"""
                <div class="alerta-proj">
                    <strong>[{urgencia.upper()}]</strong> {alerta.get('mensagem', '')}
                </div>
                """, unsafe_allow_html=True)

        if preditor_data.get('gerado_em'):
            gerado = str(preditor_data['gerado_em'])[:19].replace('T', ' ')
            st.caption(f"Ultima execucao do Preditor: {gerado}")
    else:
        st.info(
            "Projecoes nao disponiveis. O Preditor precisa de 4+ semanas de historico "
            "e roda automaticamente toda sexta 20h."
        )


# ---------- TAB 5: REUNIOES ----------

with tab_reunioes:
    st.markdown("### Proxima Reuniao")

    prox_reuniao = info.get('proxima_reuniao')
    formato_reuniao = info.get('formato_reuniao', {})

    if prox_reuniao:
        fmt_nome = formato_reuniao.get('nome', 'FLASH')
        fmt_dur = formato_reuniao.get('duracao', 30)
        fmt_cor = formato_reuniao.get('cor', '#607D8B')
        fmt_icone = formato_reuniao.get('icone', '')

        st.markdown(f"""
        <div class="reuniao-preview">
            <strong>{fmt_icone} {prox_reuniao.get('titulo', 'Reuniao da Semana')}</strong><br>
            <strong>Semana {prox_reuniao.get('semana', semana)}</strong> |
            {prox_reuniao.get('cod', '')} |
            <span style="background:{fmt_cor}; color:white; padding:2px 10px; border-radius:12px;">
                {fmt_nome} ({fmt_dur}min)
            </span><br>
            <em>Foco: {prox_reuniao.get('foco', '')}</em>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma reuniao programada.")

    # Resumo do preparador
    st.markdown("#### Resumo do Preparador")
    try:
        prep_data = carregar_preparador()
    except Exception:
        prep_data = {}

    if prep_data:
        objetivo = prep_data.get('objetivo_da_reuniao', '')
        if objetivo:
            st.markdown(f"**Objetivo:** {objetivo}")

        prep_ceo = prep_data.get('preparacao_ceo', {})
        if prep_ceo:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Antes da reuniao:**")
                for item in prep_ceo.get('antes_da_reuniao', []):
                    st.markdown(f"- {item}")
            with col_b:
                st.markdown("**O que levar:**")
                for item in prep_ceo.get('o_que_levar', []):
                    st.markdown(f"- {item}")

            if prep_ceo.get('tom_recomendado'):
                st.info(f"Tom recomendado: {prep_ceo['tom_recomendado']}")

        if prep_data.get('gerado_em'):
            gerado = str(prep_data['gerado_em'])[:19].replace('T', ' ')
            st.caption(f"Preparador atualizado em: {gerado}")
    else:
        st.info("Preparador ainda nao executado. Roda segunda 5h45.")

    # Link para pagina completa
    st.markdown("---")
    st.markdown("**[Ir para Preparador de Reuniao completo -->]**")
    st.caption("Acesse a pagina Preparador de Reuniao para ver o roteiro detalhado, "
               "script dos 5 atos e visao por unidade.")

    # Proximas reunioes (lista)
    st.markdown("#### Proximas Reunioes")
    prox_lista = proximas_reunioes(semana, n=5)
    if prox_lista:
        for r in prox_lista:
            fmt = FORMATOS_REUNIAO.get(r.get('formato', 'F'), {})
            st.markdown(
                f"**Sem {r.get('semana', '?')}** — {r.get('cod', '')} "
                f"({fmt.get('nome', '?')}, {fmt.get('duracao', 30)}min): "
                f"{r.get('titulo', '')} | _{r.get('foco', '')[:100]}_"
            )
    else:
        st.info("Nenhuma reuniao futura programada.")


# ---------- TAB 6: GENEALOGIA ----------

with tab_genealogia:
    st.markdown("### Genealogia Intelectual do PEEX")
    st.caption("Como nasceu o programa: dos 4 planos a implementacao final")

    st.markdown("""
<div class="gen-tree">
<strong>FASE 1: OS 4 PLANOS ORIGINAIS</strong>

   <span class="gen-node gen-plano">Plano A</span> Conformidade primeiro, registro SIGA como prioridade #1
   <span class="gen-node gen-plano">Plano B</span> Foco em frequencia e busca ativa de alunos
   <span class="gen-node gen-plano">Plano C</span> Alinhamento curricular SAE como eixo central
   <span class="gen-node gen-plano">Plano D</span> Clima escolar e ocorrencias como indicador lead

<strong>FASE 2: OS 2 COMPETIDORES</strong>

   <span class="gen-node gen-competidor">Competidor 1</span> Unificou A+B: registro + frequencia integrados
   <span class="gen-node gen-competidor">Competidor 2</span> Unificou C+D: curriculo + clima como sistema

<strong>FASE 3: SINTESE FINAL</strong>

   <span class="gen-node gen-sintese">Sintese</span> Combinacao dos 2 competidores em 5 eixos (A-E)
       Conformidade | Frequencia | Desempenho | Clima | Engajamento Digital
       Gerou: 7 indicadores lead, 3 fases, 45 reunioes, escalacao 4 niveis

<strong>FASE 4: IMPLEMENTACAO</strong>

   <span class="gen-node gen-impl">PEEX 2026</span> Programa de Excelencia Pedagogica
       9 robos: Vigilia, Estrategista, Conselheiro, Comparador, Preditor,
                Retroalimentador, Preparador, Gerador PEEX, Adaptativo
       Metafora: Floresta (Raizes, Solo, Micelio, Sementes, Chuva)
       Principio: "Mede quanto voce cresce, nao onde voce esta"
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Resumo das 3 Fases do Ano")

    for n_fase, fase_info in FASES.items():
        cor = fase_info['cor']
        nome = fase_info['nome']
        periodo = fase_info['periodo']
        dias = fase_info['dias_letivos']
        prioridades = fase_info.get('prioridades', [])
        prios_txt = ', '.join(p['nome'] for p in prioridades)

        ativo = " (FASE ATUAL)" if n_fase == fase_num else ""

        st.markdown(
            f'<div style="border-left:4px solid {cor}; padding:8px 14px; margin:6px 0; '
            f'border-radius:4px; background:#f8f9fa;">'
            f'<strong>Fase {n_fase}: {nome}{ativo}</strong><br>'
            f'<small>{periodo} | {dias} dias letivos</small><br>'
            f'<small>Prioridades: {prios_txt}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("**[Ir para Genealogia completa -->]**")
    st.caption("Acesse a pagina de Genealogia para ver o historico completo "
               "dos documentos fundadores e a evolucao do pensamento PEEX.")
