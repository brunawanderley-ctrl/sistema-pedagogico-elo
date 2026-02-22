"""
PEEX — Centro de Inteligencia
Landing page da CEO com visao consolidada: narrativa, decisoes, mapa da rede,
projecoes, reunioes e genealogia intelectual do PEEX.

Funciona com dados reais (resumo_Executivo.csv) como base.
Quando robos/LLM estiverem ativos, enriquece com analises mais profundas.
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
    info_semana, calcular_indice_elo, estacao_atual, proximas_reunioes,
)
from peex_config import (
    FASES, DIFERENCIACAO_UNIDADE, REUNIOES, FORMATOS_REUNIAO,
    METAS_SMART,
)

# LLM engine — modulo opcional
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


# ========== HELPERS: GERAR INTELIGENCIA DOS DADOS ==========

def _carregar_resumo():
    """Carrega resumo executivo. Retorna (total_row, unidades_df) ou (None, empty)."""
    path = DATA_DIR / "resumo_Executivo.csv"
    if not path.exists():
        return None, pd.DataFrame()
    try:
        df = pd.read_csv(path)
        total = df[df['unidade'] == 'TOTAL']
        total_row = total.iloc[0] if not total.empty else None
        unidades = df[df['unidade'] != 'TOTAL'].copy()
        return total_row, unidades
    except Exception:
        return None, pd.DataFrame()


def _gerar_narrativa(total, unidades, semana, fase_info):
    """Gera narrativa da semana a partir dos dados reais."""
    if total is None:
        return "Dados nao disponiveis. Execute a extracao do SIGA."

    conf = total['pct_conformidade_media']
    freq = total['frequencia_media']
    profs_crit = int(total['professores_criticos'])
    total_profs = int(total['total_professores'])
    alunos_risco = total['pct_alunos_risco']
    graves = int(total['ocorr_graves'])

    # Identificar unidade mais critica e melhor
    un_sort = unidades.sort_values('pct_conformidade_media')
    pior = un_sort.iloc[0]
    melhor = un_sort.iloc[-1]
    pior_nome = UNIDADES_NOMES.get(pior['unidade'], pior['unidade'])
    melhor_nome = UNIDADES_NOMES.get(melhor['unidade'], melhor['unidade'])

    # JG frequencia
    jg = unidades[unidades['unidade'] == 'JG']
    jg_freq = float(jg['frequencia_media'].iloc[0]) if not jg.empty else 0
    jg_risco = float(jg['pct_alunos_risco'].iloc[0]) if not jg.empty else 0

    # CDR ocorrencias
    cdr = unidades[unidades['unidade'] == 'CDR']
    cdr_graves = int(cdr['ocorr_graves'].iloc[0]) if not cdr.empty else 0
    pct_cdr = (cdr_graves / graves * 100) if graves > 0 else 0

    meta_conf = 70  # meta tri 1
    gap_conf = meta_conf - conf
    semanas_restantes = 15 - semana  # fim do tri 1
    pp_por_semana = gap_conf / semanas_restantes if semanas_restantes > 0 else gap_conf

    narrativa = (
        f"<strong>Semana {semana} — Fase SOBREVIVENCIA</strong><br><br>"
        f"A rede esta em <strong>{conf:.1f}% de conformidade</strong> "
        f"(meta do trimestre: {meta_conf}%). "
        f"Faltam <strong>{gap_conf:.1f} pontos percentuais</strong> em "
        f"{semanas_restantes} semanas — precisa ganhar "
        f"<strong>{pp_por_semana:.1f}pp por semana</strong> para atingir a meta.<br><br>"
        f"Dos {total_profs} professores, <strong>{profs_crit} estao criticos</strong> "
        f"(registram menos de 30% do esperado). "
        f"Apenas {total['pct_prof_no_ritmo']:.0f}% estao no ritmo SAE.<br><br>"
        f"<strong>Frequencia:</strong> {freq:.1f}% na rede. "
        f"Janga e o alerta principal: {jg_freq:.1f}% de frequencia com "
        f"{jg_risco:.0f}% dos alunos em risco de evasao.<br><br>"
        f"<strong>Ocorrencias graves:</strong> {graves} na rede. "
        f"Cordeiro concentra {cdr_graves} ({pct_cdr:.0f}%).<br><br>"
        f"<strong>{melhor_nome}</strong> lidera com {melhor['pct_conformidade_media']:.1f}% "
        f"de conformidade. "
        f"<strong>{pior_nome}</strong> esta mais atras com {pior['pct_conformidade_media']:.1f}%."
    )
    return narrativa


def _gerar_decisoes(total, unidades, semana):
    """Gera 3 decisoes estrategicas a partir dos dados reais."""
    if total is None:
        return []

    decisoes = []

    # Decisao 1: Professores criticos (sempre relevante na fase 1)
    profs_crit = int(total['professores_criticos'])
    total_profs = int(total['total_professores'])
    pct_crit = profs_crit / total_profs * 100 if total_profs else 0

    # Qual unidade tem mais criticos?
    un_crit = unidades.sort_values('professores_criticos', ascending=False).iloc[0]
    un_crit_nome = UNIDADES_NOMES.get(un_crit['unidade'], un_crit['unidade'])

    decisoes.append({
        'titulo': f'{profs_crit} professores criticos na rede ({pct_crit:.0f}%)',
        'unidade': 'Rede (pior: ' + un_crit_nome + f" com {int(un_crit['professores_criticos'])})",
        'por_que': (
            f'Professores criticos registram menos de 30% das aulas esperadas. '
            f'Sem registro, nao ha dado para acompanhar aprendizagem, frequencia nem conteudo. '
            f'E a prioridade #1 da Fase Sobrevivencia.'
        ),
        'opcoes': [
            f'Conversa individual com cada um dos {profs_crit} (Bruna Vitoria + Gilberto em BV, coordenadores nas demais)',
            'Contrato de Pratica Docente: prazo de 2 semanas para regularizar, com acompanhamento diario',
            'Escalar para direcao os que nao responderem apos 2 feedbacks',
        ],
        'impacto': f'Cada professor que regulariza pode mover a conformidade em +{100/total_profs:.1f}pp',
        'origem': 'Sintese Final, Secao Registro como Prioridade #1 + Plano Definitivo, Fase 1',
    })

    # Decisao 2: Frequencia JG
    jg = unidades[unidades['unidade'] == 'JG']
    if not jg.empty:
        jg_row = jg.iloc[0]
        jg_freq = float(jg_row['frequencia_media'])
        jg_risco = float(jg_row['pct_alunos_risco'])
        jg_tier3 = int(jg_row['alunos_tier_3'])
        jg_tier2 = int(jg_row['alunos_tier_2'])

        decisoes.append({
            'titulo': f'Janga: {jg_freq:.1f}% frequencia, {jg_risco:.0f}% alunos em risco',
            'unidade': 'Janga',
            'por_que': (
                f'Janga tem a pior frequencia da rede. {jg_tier2 + jg_tier3} alunos estao em '
                f'risco (tier 2+3). Se nao agir agora, esses alunos podem evadir '
                f'antes do fim do trimestre. A busca ativa precisa comecar esta semana.'
            ),
            'opcoes': [
                'Pietro + secretaria: ligar para familias dos alunos com 3+ faltas consecutivas ESTA semana',
                'Lecinane: visita domiciliar aos 5 casos mais graves',
                'Reuniao FOCO especifica para JG na proxima semana (alem da RU regular)',
            ],
            'impacto': f'Recuperar 10 alunos = +{10/int(jg_row["total_alunos"])*100:.1f}pp na frequencia de JG',
            'origem': 'Sintese Final, Protocolo de Busca Ativa 3 Niveis + Plano Sinais Original',
        })

    # Decisao 3: Ocorrencias CDR
    cdr = unidades[unidades['unidade'] == 'CDR']
    if not cdr.empty:
        cdr_row = cdr.iloc[0]
        cdr_graves = int(cdr_row['ocorr_graves'])
        total_graves = int(total['ocorr_graves'])
        pct = cdr_graves / total_graves * 100 if total_graves else 0

        decisoes.append({
            'titulo': f'Cordeiro: {cdr_graves} ocorrencias graves ({pct:.0f}% da rede)',
            'unidade': 'Cordeiro',
            'por_que': (
                f'Cordeiro concentra {pct:.0f}% de todas as ocorrencias graves. '
                f'Isso indica um problema disciplinar concentrado em turmas especificas. '
                f'Sem intervencao, o clima piora e a evasao aumenta.'
            ),
            'opcoes': [
                'Ana Claudia + Vanessa: gerar mapa de calor (turma x tipo x dia) para identificar 3 focos',
                'Presenca fisica da coordenacao nas 3 turmas-foco por 5 dias consecutivos',
                'Reuniao com professores dessas turmas: o que esta provocando as ocorrencias?',
            ],
            'impacto': f'Meta: reduzir de {cdr_graves} para {cdr_graves//2} graves ate fim do trimestre',
            'origem': 'Sintese Final, Protocolo de Crise CDR + Competidor B (clima como indicador lead)',
        })

    return decisoes


def _gerar_projecoes(total, unidades, semana):
    """Gera projecoes simples: atual vs meta + ritmo necessario."""
    if total is None:
        return []

    semanas_restantes_tri1 = max(15 - semana, 1)
    projecoes = []

    for meta in METAS_SMART:
        campo = meta['campo_resumo']
        if campo not in total.index:
            continue

        atual = float(total[campo])
        meta_tri1 = meta['meta_tri1']
        baseline = meta['baseline']
        inverso = meta.get('inverso', False)
        unid = meta['unidade']

        # Calcular gap e ritmo
        if inverso:
            gap = atual - meta_tri1  # precisa diminuir
            por_semana = gap / semanas_restantes_tri1
            no_caminho = atual <= meta_tri1
            direcao = 'diminuir'
        else:
            gap = meta_tri1 - atual  # precisa aumentar
            por_semana = gap / semanas_restantes_tri1
            no_caminho = atual >= meta_tri1
            direcao = 'ganhar'

        # Variacao desde baseline
        variacao = atual - baseline

        projecoes.append({
            'indicador': meta['indicador'],
            'eixo': meta['eixo'],
            'atual': atual,
            'baseline': baseline,
            'meta_tri1': meta_tri1,
            'gap': abs(gap),
            'por_semana': abs(por_semana),
            'no_caminho': no_caminho,
            'variacao': variacao,
            'direcao': direcao,
            'inverso': inverso,
            'unidade': unid,
            'semanas_restantes': semanas_restantes_tri1,
        })

    return projecoes


def _propostas_por_unidade(unidades):
    """Gera propostas de acao por unidade baseado nos dados."""
    propostas = {}
    for _, row in unidades.iterrows():
        un = row['unidade']
        nome = UNIDADES_NOMES.get(un, un)
        diff = DIFERENCIACAO_UNIDADE.get(un, {})
        acoes = []

        conf = row['pct_conformidade_media']
        freq = row['frequencia_media']
        crit = int(row['professores_criticos'])
        graves = int(row['ocorr_graves'])
        risco = row['pct_alunos_risco']

        # Prioridade por dados
        if conf < 40:
            acoes.append({
                'prioridade': 'URGENTE',
                'acao': f'Conformidade em {conf:.0f}% — abaixo de 40%. Contato direto com os {crit} professores criticos esta semana.',
                'responsavel': diff.get('coordenadores', 'Coordenacao'),
            })
        elif conf < 55:
            acoes.append({
                'prioridade': 'IMPORTANTE',
                'acao': f'Conformidade em {conf:.0f}% — precisa chegar a 70%. Foco nos {crit} criticos.',
                'responsavel': diff.get('coordenadores', 'Coordenacao'),
            })

        if freq < 82:
            acoes.append({
                'prioridade': 'URGENTE',
                'acao': f'Frequencia em {freq:.1f}% — protocolo de busca ativa imediato.',
                'responsavel': diff.get('coordenadores', 'Coordenacao'),
            })
        elif freq < 88:
            acoes.append({
                'prioridade': 'IMPORTANTE',
                'acao': f'Frequencia em {freq:.1f}% — meta 88%. Monitorar alunos com 3+ faltas.',
                'responsavel': diff.get('coordenadores', 'Coordenacao'),
            })

        if graves > 10:
            acoes.append({
                'prioridade': 'URGENTE',
                'acao': f'{graves} ocorrencias graves. Mapa de calor + presenca fisica nas turmas-foco.',
                'responsavel': diff.get('coordenadores', 'Coordenacao'),
            })

        if risco > 20:
            acoes.append({
                'prioridade': 'IMPORTANTE',
                'acao': f'{risco:.0f}% alunos em risco. Plano individual para tier 2/3.',
                'responsavel': diff.get('coordenadores', 'Coordenacao'),
            })

        if not acoes:
            acoes.append({
                'prioridade': 'MONITORAR',
                'acao': 'Indicadores dentro do esperado. Manter ritmo.',
                'responsavel': diff.get('coordenadores', 'Coordenacao'),
            })

        propostas[un] = {'nome': nome, 'acoes': acoes, 'foco': diff.get('foco', '')}

    return propostas


# ========== CSS ==========

st.markdown("""
<style>
    .ci-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2838 40%, #1a237e 100%);
        color: white; padding: 32px; border-radius: 14px; margin-bottom: 24px;
    }
    .ci-header h2 { color: white !important; margin: 0 0 6px 0; font-size: 1.8em; letter-spacing: 2px; }
    .ci-header .ci-subtitle { opacity: 0.85; font-size: 0.95em; margin-bottom: 10px; }
    .ci-header .ci-motto {
        font-style: italic; opacity: 0.7; font-size: 0.88em; margin-top: 8px;
        border-top: 1px solid rgba(255,255,255,0.2); padding-top: 8px;
    }
    .chip-container { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
    .chip { background: rgba(255,255,255,0.15); padding: 4px 14px; border-radius: 16px; font-size: 0.9em; }
    .narrativa-box {
        background: #f5f5f5; border-left: 4px solid #1a237e; padding: 20px;
        border-radius: 8px; margin: 16px 0; line-height: 1.7; font-size: 1.05em;
    }
    .decisao-card {
        background: #fff3e0; border-left: 5px solid #e65100;
        padding: 16px 20px; margin: 12px 0; border-radius: 6px;
    }
    .decisao-titulo { font-weight: bold; font-size: 1.1em; margin-bottom: 8px; color: #bf360c; }
    .decisao-porque {
        background: white; padding: 10px 14px; border-radius: 6px;
        border: 1px solid #e0e0e0; margin: 8px 0; line-height: 1.6;
    }
    .decisao-opcoes { margin: 8px 0; }
    .decisao-opcoes li { margin: 4px 0; }
    .decisao-impacto { color: #2e7d32; font-weight: bold; font-size: 0.9em; margin-top: 6px; }
    .decisao-origem { font-size: 0.8em; color: #888; margin-top: 6px; font-style: italic; }
    .ie-card {
        background: white; border: 2px solid #e0e0e0; border-radius: 12px;
        padding: 20px; text-align: center;
    }
    .ie-value { font-size: 2.4em; font-weight: bold; }
    .ie-label { font-size: 0.85em; color: #666; margin-top: 4px; }
    .semaforo-dot {
        display: inline-block; width: 14px; height: 14px;
        border-radius: 50%; margin-right: 6px;
    }
    .proposta-card {
        padding: 14px 18px; margin: 8px 0; border-radius: 6px;
    }
    .proposta-urgente { background: #ffebee; border-left: 4px solid #c62828; }
    .proposta-importante { background: #fff3e0; border-left: 4px solid #e65100; }
    .proposta-monitorar { background: #e8f5e9; border-left: 4px solid #4caf50; }
    .proj-row {
        display: flex; align-items: center; padding: 12px 16px;
        margin: 6px 0; border-radius: 6px; background: #f8f9fa;
    }
    .proj-indicador { flex: 1; font-weight: bold; }
    .proj-valor { width: 80px; text-align: center; font-size: 1.2em; font-weight: bold; }
    .proj-meta { width: 80px; text-align: center; color: #666; }
    .proj-ritmo { flex: 1; font-size: 0.9em; }
    .no-caminho { color: #2e7d32; }
    .fora-meta { color: #c62828; }
    .diff-note {
        background: #E8EAF6; border-left: 3px solid #3F51B5;
        padding: 10px 14px; border-radius: 4px; margin: 6px 0; font-size: 0.88em;
    }
    .reuniao-preview {
        background: #f8f9fa; border-left: 4px solid #1565C0;
        padding: 14px 18px; border-radius: 6px; margin: 8px 0;
    }
    .gen-tree {
        background: #f5f5f5; padding: 20px; border-radius: 10px;
        font-family: monospace; font-size: 0.88em; line-height: 1.6; white-space: pre-wrap;
    }
    .gen-node {
        display: inline-block; padding: 4px 12px; border-radius: 6px;
        margin: 2px 4px; font-weight: bold;
    }
    .gen-plano { background: #E3F2FD; color: #1565C0; }
    .gen-competidor { background: #FFF3E0; color: #E65100; }
    .gen-sintese { background: #E8F5E9; color: #2E7D32; }
    .gen-impl { background: #F3E5F5; color: #7B1FA2; }
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

total_row, unidades_df = _carregar_resumo()


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

    # Tentar robos/LLM primeiro, fallback para dados reais
    fonte = "Dados"
    narrativa_texto = None

    # 1. Tentar LLM (Analista)
    if _HAS_LLM and _llm_disponivel():
        try:
            analista = carregar_analista()
            if analista and getattr(analista, 'narrativa', None):
                narrativa_texto = analista.narrativa
                fonte = "LLM (Analista)"
        except Exception:
            pass

    # 2. Tentar robo Estrategista (narrativa_ceo)
    if not narrativa_texto:
        try:
            narr_data = carregar_narrativa_ceo()
            if narr_data and narr_data.get('narrativa'):
                narrativa_texto = narr_data['narrativa']
                fonte = "Robo (Estrategista)"
        except Exception:
            pass

    # 3. Fallback: gerar dos dados reais
    if not narrativa_texto:
        narrativa_texto = _gerar_narrativa(total_row, unidades_df, semana, fase)
        fonte = "Dados em tempo real"

    st.markdown(f'<div class="narrativa-box">{narrativa_texto}</div>', unsafe_allow_html=True)

    badge_class = 'fonte-llm' if 'LLM' in fonte else 'fonte-template'
    st.markdown(
        f'<span class="fonte-badge" style="background:{"#7B1FA2" if "LLM" in fonte else "#607D8B"}; '
        f'color:white; padding:3px 12px; border-radius:12px; font-size:0.78em;">'
        f'Fonte: {fonte}</span>',
        unsafe_allow_html=True,
    )
    st.caption(f"Semana {semana} | {hoje.strftime('%d/%m/%Y')}")

    with st.expander("O que e esta narrativa?"):
        st.markdown(
            "A narrativa resume os numeros da semana em linguagem clara para a CEO. "
            "Mostra: conformidade, frequencia, professores criticos, ocorrencias, e "
            "quanto falta para atingir a meta do trimestre.\n\n"
            "**3 niveis de inteligencia:**\n"
            "1. **LLM (Analista)**: Quando a API Claude estiver ativa — narrativa contextual profunda\n"
            "2. **Robo (Estrategista)**: Quando o robo roda domingo 22h — narrativa pre-gerada\n"
            "3. **Dados em tempo real**: Sempre disponivel — gera do resumo executivo\n\n"
            "**Atualizacao:** Automatica apos cada extracao (4x/dia: 8h, 12h, 18h, 20h)."
        )

    # Pauta resumida da semana
    prox = info.get('proxima_reuniao')
    if prox:
        st.markdown("---")
        st.markdown("### Sua Pauta Esta Semana")
        st.markdown(f"**Reuniao:** {prox.get('cod', '')} — {prox.get('titulo', '')}")
        st.markdown(f"**Foco:** {prox.get('foco', '')}")

        # Acoes concretas da semana
        st.markdown("**O que fazer antes da proxima reuniao:**")
        st.markdown(
            f"1. Verificar se os {int(total_row['professores_criticos']) if total_row is not None else '?'} "
            f"professores criticos foram contatados\n"
            f"2. Checar frequencia de Janga (busca ativa ativada?)\n"
            f"3. Ver mapa de calor de Cordeiro (aba **Mapa da Rede** acima)\n"
            f"4. Revisar dados atualizados antes da reuniao (pagina **Quadro Gestao**)"
        )


# ---------- TAB 2: DECISOES ----------

with tab_decisoes:
    st.markdown("### 3 Decisoes Estrategicas")
    st.caption("Baseadas nos dados reais da semana — o que precisa de acao AGORA")

    decisoes = _gerar_decisoes(total_row, unidades_df, semana)

    if decisoes:
        for i, d in enumerate(decisoes, 1):
            opcoes_html = ""
            if d.get('opcoes'):
                opcoes_items = ''.join(f'<li>{o}</li>' for o in d['opcoes'])
                opcoes_html = f'<div class="decisao-opcoes"><strong>Opcoes de acao:</strong><ol>{opcoes_items}</ol></div>'

            st.markdown(f"""
            <div class="decisao-card">
                <div class="decisao-titulo">#{i} — {d['titulo']}</div>
                <div class="decisao-porque">{d['por_que']}</div>
                {opcoes_html}
                <div class="decisao-impacto">Impacto estimado: {d['impacto']}</div>
                <div class="decisao-origem">Origem: {d['origem']}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Por que essa decisao aparece? (#{i})"):
                st.markdown(
                    f"**Unidade:** {d['unidade']}\n\n"
                    f"**Analise:** {d['por_que']}\n\n"
                    f"**De onde veio:** {d['origem']}\n\n"
                    "Essa decisao foi gerada automaticamente a partir dos dados reais "
                    "cruzados com o planejamento da Sintese Final. Aparece porque os "
                    "indicadores estao fora da meta e requerem acao."
                )
    else:
        st.info("Nenhuma decisao urgente identificada. Dados nao disponiveis.")


# ---------- TAB 3: MAPA DA REDE ----------

with tab_mapa:
    st.markdown("### Mapa da Rede — Heatmap + Propostas de Acao")

    if not unidades_df.empty:
        # --- Heatmap ---
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
                z=z_data, x=nomes, y=y_labels,
                colorscale='RdYlGn',
                text=[[f"{v:.0f}%" for v in row] for row in z_data],
                texttemplate="%{text}",
                textfont={"size": 14},
                hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>",
            ))
            fig.update_layout(
                height=360, margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- Indice ELO + Semaforo ---
        st.markdown("#### Indice ELO (IE) por Unidade")
        ie_cols = st.columns(4)
        for i, un_code in enumerate(unidades_order):
            un_row = unidades_df[unidades_df['unidade'] == un_code]
            ie = calcular_indice_elo(un_row.iloc[0]) if not un_row.empty else 0
            cor_ie = '#2e7d32' if ie >= 70 else '#e65100' if ie >= 50 else '#c62828'
            nome = UNIDADES_NOMES.get(un_code, un_code)
            with ie_cols[i]:
                st.markdown(f"""
                <div class="ie-card">
                    <div class="ie-value" style="color:{cor_ie};">{ie:.0f}</div>
                    <div class="ie-label">{nome}</div>
                </div>
                """, unsafe_allow_html=True)

        # --- PROPOSTAS DE ACAO POR UNIDADE (novo!) ---
        st.markdown("#### O Que Fazer — Propostas por Unidade")
        st.caption("Acoes geradas automaticamente a partir dos indicadores criticos de cada unidade")

        propostas = _propostas_por_unidade(unidades_df)
        for un_code in unidades_order:
            prop = propostas.get(un_code)
            if not prop:
                continue

            with st.expander(f"{prop['nome']} — {prop['foco']}", expanded=True):
                for acao in prop['acoes']:
                    prio = acao['prioridade']
                    css_class = {
                        'URGENTE': 'proposta-urgente',
                        'IMPORTANTE': 'proposta-importante',
                        'MONITORAR': 'proposta-monitorar',
                    }.get(prio, 'proposta-monitorar')

                    st.markdown(f"""
                    <div class="proposta-card {css_class}">
                        <strong>[{prio}]</strong> {acao['acao']}<br>
                        <small>Responsavel: {acao['responsavel']}</small>
                    </div>
                    """, unsafe_allow_html=True)

        # --- MAPA DE CALOR DE OCORRENCIAS (CDR em destaque) ---
        st.markdown("#### Mapa de Calor — Ocorrencias Graves por Turma")
        st.caption("Onde estao concentradas as ocorrencias graves? Dados reais do SIGA.")

        ocorr_path = DATA_DIR / "fato_Ocorrencias.csv"
        if ocorr_path.exists():
            try:
                ocorr_df = pd.read_csv(ocorr_path)
                graves_df = ocorr_df[ocorr_df['gravidade'] == 'Grave'].copy()

                if not graves_df.empty:
                    # Extrair serie limpa
                    graves_df['serie_limpa'] = graves_df['serie'].fillna('Outros')

                    # Heatmap: unidade x serie
                    pivot = graves_df.groupby(['unidade', 'serie_limpa']).size().reset_index(name='qtd')
                    series_order = ['6º Ano', '7º Ano', '8º Ano', '9º Ano', '1º Ano', '2º Ano', '3º Ano']
                    series_presentes = [s for s in series_order if s in pivot['serie_limpa'].values]

                    z_ocorr = []
                    for un in ['BV', 'CD', 'JG', 'CDR']:
                        row = []
                        for s in series_presentes:
                            val = pivot[(pivot['unidade'] == un) & (pivot['serie_limpa'] == s)]['qtd']
                            row.append(int(val.iloc[0]) if not val.empty else 0)
                        z_ocorr.append(row)

                    nomes_un = [UNIDADES_NOMES.get(u, u) for u in ['BV', 'CD', 'JG', 'CDR']]

                    fig_ocorr = go.Figure(data=go.Heatmap(
                        z=z_ocorr, x=series_presentes, y=nomes_un,
                        colorscale='Reds',
                        text=[[str(v) if v > 0 else '' for v in row] for row in z_ocorr],
                        texttemplate="%{text}",
                        textfont={"size": 16},
                        hovertemplate="<b>%{y}</b> - %{x}<br>Graves: %{z}<extra></extra>",
                    ))
                    fig_ocorr.update_layout(
                        height=250, margin=dict(l=10, r=10, t=10, b=10),
                    )
                    st.plotly_chart(fig_ocorr, use_container_width=True)

                    # Top 3 turmas CDR
                    cdr_graves = graves_df[graves_df['unidade'] == 'CDR']
                    if not cdr_graves.empty:
                        import re
                        def extrair_turma(t):
                            m = re.search(r'(\d+[ºªo]\s*\w+.*?Turma\s*\w)', str(t))
                            return m.group(1) if m else str(t)[:40]

                        cdr_graves = cdr_graves.copy()
                        cdr_graves['turma_curta'] = cdr_graves['turma'].apply(extrair_turma)
                        top_turmas = cdr_graves['turma_curta'].value_counts().head(3)

                        st.markdown("**Cordeiro — 3 turmas com mais ocorrencias graves:**")
                        for turma, qtd in top_turmas.items():
                            st.markdown(
                                f'<div class="proposta-card proposta-urgente">'
                                f'<strong>{turma}</strong>: {qtd} ocorrencias graves'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                        st.caption(
                            "Acao: Ana Claudia + Vanessa devem marcar presenca fisica "
                            "nestas 3 turmas por 5 dias consecutivos."
                        )
            except Exception:
                st.caption("Erro ao carregar dados de ocorrencias.")
        else:
            st.caption("fato_Ocorrencias.csv nao encontrado.")

        # --- Diferenciacao ---
        with st.expander("Diferenciacao por Unidade (do planejamento)"):
            for un_code in unidades_order:
                diff = DIFERENCIACAO_UNIDADE.get(un_code, {})
                nome = UNIDADES_NOMES.get(un_code, un_code)
                st.markdown(f"""
                <div class="diff-note">
                    <strong>{nome}</strong>: {diff.get('foco', '')}<br>
                    <small>Coordenadores: {diff.get('coordenadores', '')} |
                    Escalacao: {diff.get('escalacao', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("resumo_Executivo.csv nao encontrado. Execute a extracao do SIGA.")


# ---------- TAB 4: PROJECOES ----------

with tab_projecoes:
    st.markdown("### Projecoes — Atual vs Meta do Trimestre")
    st.caption("Quanto falta e qual o ritmo necessario para atingir cada meta")

    # Tentar Preditor primeiro (roda sexta 20h)
    try:
        preditor_data = carregar_preditor()
    except Exception:
        preditor_data = {}

    if preditor_data.get('projecoes'):
        st.success("Projecoes do Preditor disponiveis (regressao linear sobre historico)")
        pred_proj = preditor_data['projecoes']
        for un_code in ['BV', 'CD', 'JG', 'CDR']:
            proj = pred_proj.get(un_code, {})
            if proj:
                nome = UNIDADES_NOMES.get(un_code, un_code)
                st.markdown(
                    f"**{nome}**: Atual {proj.get('atual', 0):.1f}% | "
                    f"+1sem: {proj.get('proj_sem_mais_1', 0):.1f}% | "
                    f"+2sem: {proj.get('proj_sem_mais_2', 0):.1f}% | "
                    f"Tendencia: {proj.get('tendencia', 'estavel')}"
                )
        if preditor_data.get('alertas'):
            st.markdown("#### Alertas do Preditor")
            for alerta in preditor_data['alertas']:
                st.warning(alerta.get('mensagem', ''))
        st.markdown("---")
        st.markdown("**Complemento: Ritmo necessario por indicador**")

    # Sempre mostrar projecoes baseadas em metas (dados reais)
    projecoes = _gerar_projecoes(total_row, unidades_df, semana)

    if projecoes:
        semanas_rest = max(15 - semana, 1)
        st.markdown(f"**Semanas restantes no 1o Trimestre: {semanas_rest}**")
        st.markdown("")

        # Dicas de acao por indicador
        _DICAS = {
            'Conformidade media': 'Contato direto com professores criticos. Contrato de Pratica Docente.',
            'Professores criticos': 'Conversa individual de 5 min com cada um. Prazo de 2 semanas.',
            'Profs no ritmo SAE': 'Protocolo de Ritmo: verificar capitulo atual vs esperado por professor.',
            'Frequencia media': 'Busca ativa 3 niveis (ligacao, visita, reuniao familia). Foco: JG.',
            'Alunos freq >90%': 'Identificar os que cairam de >90% para <90% e intervir rapido.',
            'Alunos em risco': 'Plano individual para tier 2/3. Reuniao com familia dos tier 3.',
            'Media de notas': 'Manter. Atentar para unidades abaixo de 7.5.',
            'Ocorrencias graves': 'Mapa de calor CDR. Presenca fisica nas 3 turmas-foco.',
        }

        for p in projecoes:
            # Barra de progresso visual
            if p['inverso']:
                range_total = p['baseline'] - p['meta_tri1']
                progresso_feito = p['baseline'] - p['atual']
                pct_progresso = (progresso_feito / range_total * 100) if range_total > 0 else 0
            else:
                range_total = p['meta_tri1'] - p['baseline']
                progresso_feito = p['atual'] - p['baseline']
                pct_progresso = (progresso_feito / range_total * 100) if range_total > 0 else 0

            pct_progresso = max(0, min(100, pct_progresso))
            unid = p['unidade']

            if p['no_caminho']:
                ritmo_txt = "Meta atingida!"
                cor_fundo = '#E8F5E9'
                cor_borda = '#4CAF50'
                cor_valor = '#2e7d32'
                icone = '✅'
            else:
                ritmo_txt = f"Precisa {p['direcao']} {p['por_semana']:.1f}{unid}/semana"
                if pct_progresso >= 30:
                    cor_fundo = '#FFF3E0'
                    cor_borda = '#FF9800'
                    cor_valor = '#e65100'
                    icone = '⚠️'
                else:
                    cor_fundo = '#FFEBEE'
                    cor_borda = '#F44336'
                    cor_valor = '#c62828'
                    icone = '🔴'

            dica = _DICAS.get(p['indicador'], '')

            # Barra de progresso
            cor_barra = '#4CAF50' if pct_progresso >= 60 else '#FFA000' if pct_progresso >= 30 else '#F44336'
            barra_width = max(pct_progresso, 3)  # minimo 3% para ser visivel

            st.markdown(f"""
            <div style="background:{cor_fundo}; border-left:5px solid {cor_borda};
                        padding:14px 18px; margin:8px 0; border-radius:0 8px 8px 0;">
                <div style="display:flex; align-items:center; margin-bottom:6px;">
                    <span style="font-size:1.1em;">{icone}</span>
                    <strong style="margin-left:8px; flex:1;">{p['indicador']}</strong>
                    <span style="font-size:1.4em; font-weight:bold; color:{cor_valor};">
                        {p['atual']:.1f}{unid}
                    </span>
                    <span style="margin-left:12px; color:#666;">Meta: {p['meta_tri1']}{unid}</span>
                </div>
                <div style="background:#e0e0e0; border-radius:4px; height:10px; margin:6px 0;">
                    <div style="background:{cor_barra}; width:{barra_width:.0f}%;
                                height:100%; border-radius:4px;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:4px;">
                    <span style="color:{cor_valor}; font-weight:bold; font-size:0.9em;">
                        {ritmo_txt}
                    </span>
                    <span style="font-size:0.8em; color:#666;">
                        Progresso: {pct_progresso:.0f}%
                    </span>
                </div>
                <div style="font-size:0.85em; color:#555; margin-top:6px;
                            border-top:1px solid rgba(0,0,0,0.1); padding-top:6px;">
                    <strong>O que fazer:</strong> {dica}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("Como usar estas projecoes"):
            st.markdown(
                "**Leitura rapida:**\n"
                "- 🔴 **Vermelho**: Indicador longe da meta, precisa de acao urgente\n"
                "- ⚠️ **Amarelo**: Indicador em progresso, manter ritmo\n"
                "- ✅ **Verde**: Meta atingida, celebrar e manter\n\n"
                "**Na pratica:**\n"
                "1. Olhe os vermelhos primeiro — sao suas prioridades da semana\n"
                "2. Leia o \"O que fazer\" de cada um\n"
                "3. Na reuniao, pergunte: \"Qual o status desta acao?\"\n"
                "4. Acompanhe semanalmente: a barra de progresso deve crescer\n\n"
                "**Fonte:** Metas definidas na Sintese Final PEEX 2026."
            )
    else:
        st.info("Dados nao disponiveis para projecoes.")


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

        # O que preparar para esta reuniao
        st.markdown("#### O que preparar")
        foco = prox_reuniao.get('foco', '')
        st.markdown(
            f"1. **Dados atualizados**: Quadro Gestao com conformidade por unidade\n"
            f"2. **Lista nominal**: professores criticos — quem ja foi contatado?\n"
            f"3. **Foco especifico**: {foco}\n"
            f"4. **Perguntar a cada diretor**: qual o status dos compromissos da semana passada?"
        )
    else:
        st.info("Nenhuma reuniao programada.")

    # Calendario visual do trimestre
    st.markdown("#### Calendario do Trimestre")
    st.caption("Todas as reunioes ate o fim da Fase Sobrevivencia")

    prox_lista = proximas_reunioes(semana, n=20)
    for r in prox_lista:
        fmt = FORMATOS_REUNIAO.get(r.get('formato', 'F'), {})
        cor = fmt.get('cor', '#607D8B')
        icone = fmt.get('icone', '')
        sem_r = r.get('semana', '?')
        atual = " **(PROXIMA)**" if sem_r == prox_reuniao.get('semana') else ""

        st.markdown(
            f"<span style='color:{cor}; font-weight:bold;'>{icone}</span> "
            f"**Sem {sem_r}** — {r.get('cod', '')} "
            f"({fmt.get('nome', '?')}, {fmt.get('duracao', 30)}min): "
            f"{r.get('titulo', '')} | _{r.get('foco', '')[:120]}_{atual}",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("Roteiro detalhado: **Preparador de Reuniao** (menu lateral)")


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
    st.markdown("Arvore completa dos 31 conceitos: **Genealogia da Proposta** (menu lateral)")
