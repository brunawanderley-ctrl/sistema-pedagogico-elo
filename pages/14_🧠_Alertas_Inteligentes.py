#!/usr/bin/env python3
"""
PAGINA 14: ALERTAS INTELIGENTES
Sistema de 5 tipos de alerta + Score de Risco do Professor
Detecta problemas ANTES que se tornem criticos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_UNIDADES, ORDEM_SERIES
from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado,
    carregar_fato_aulas, carregar_horario_esperado, carregar_progressao_sae,
    filtrar_ate_hoje, filtrar_por_periodo, PERIODOS_OPCOES,
    _hoje, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM,
    CONFORMIDADE_CRITICO, CONFORMIDADE_BAIXO, CONFORMIDADE_META,
    CONTEUDO_VAZIO_ALERTA,
)

st.set_page_config(page_title="Alertas Inteligentes", page_icon="🧠", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

st.markdown("""
<style>
    .alerta-vermelho {
        background: #FFEBEE; border-left: 5px solid #D32F2F;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .alerta-amarelo {
        background: #FFF8E1; border-left: 5px solid #FFA000;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .alerta-laranja {
        background: #FFF3E0; border-left: 5px solid #E65100;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .alerta-azul {
        background: #E3F2FD; border-left: 5px solid #1565C0;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .alerta-rosa {
        background: #FCE4EC; border-left: 5px solid #AD1457;
        padding: 12px 16px; margin: 6px 0; border-radius: 4px;
    }
    .score-alto { background: #C8E6C9; padding: 6px 10px; border-radius: 12px; color: #1B5E20; font-weight: bold; }
    .score-medio { background: #FFF9C4; padding: 6px 10px; border-radius: 12px; color: #F57F17; font-weight: bold; }
    .score-baixo { background: #FFCDD2; padding: 6px 10px; border-radius: 12px; color: #B71C1C; font-weight: bold; }
    .legenda-box {
        background: #FAFAFA; border: 1px solid #E0E0E0;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== TIPOS DE ALERTA ==========
TIPOS_ALERTA = {
    'VERMELHO': {
        'nome': 'Professor Silencioso',
        'emoji': '🔴',
        'descricao': '0 registros na semana atual',
        'acao': 'Contatar professor IMEDIATAMENTE',
        'prioridade': 1,
    },
    'AMARELO': {
        'nome': 'Registro em Queda',
        'emoji': '🟡',
        'descricao': 'Taxa de registro caiu >30% vs semana anterior',
        'acao': 'Monitorar e conversar com o professor',
        'prioridade': 2,
    },
    'LARANJA': {
        'nome': 'Curriculo Atrasado',
        'emoji': '🟠',
        'descricao': 'Conteudo >1 capitulo atras do esperado SAE',
        'acao': 'Reuniao com professor para plano de recuperacao',
        'prioridade': 3,
    },
    'AZUL': {
        'nome': 'Frequencia Pendente',
        'emoji': '🔵',
        'descricao': '>5 dias sem lancar frequencia',
        'acao': 'Lembrar professor de lancar frequencia',
        'prioridade': 4,
    },
    'ROSA': {
        'nome': 'Disciplina Orfã',
        'emoji': '🩷',
        'descricao': 'Disciplina sem nenhum registro >1 semana',
        'acao': 'Verificar se ha professor alocado',
        'prioridade': 5,
    },
}


@st.cache_data(ttl=300)
def detectar_alertas(df_aulas, df_horario, semana_atual):
    """Detecta todos os 5 tipos de alerta usando fato_Aulas como base."""
    hoje = _hoje()
    alertas = []

    # Pre-calcula aulas por professor por semana
    if 'semana_letiva' in df_aulas.columns:
        prof_semana = df_aulas.groupby(['professor', 'semana_letiva']).size().reset_index(name='aulas')
    else:
        prof_semana = pd.DataFrame()

    # Itera sobre professores em fato_Aulas
    for prof in df_aulas['professor'].unique():
        df_prof_aulas = df_aulas[df_aulas['professor'] == prof]
        unidade = df_prof_aulas['unidade'].iloc[0]
        disciplinas = ', '.join(sorted(df_prof_aulas['disciplina'].unique())[:3])

        # --- ALERTA VERMELHO: Professor Silencioso ---
        if not prof_semana.empty:
            aulas_semana_atual = prof_semana[
                (prof_semana['professor'] == prof) &
                (prof_semana['semana_letiva'] == semana_atual)
            ]
            n_aulas_sem = aulas_semana_atual['aulas'].sum() if not aulas_semana_atual.empty else 0
        else:
            recentes = df_prof_aulas[df_prof_aulas['data'] >= (hoje - timedelta(days=7))]
            n_aulas_sem = len(recentes)

        if n_aulas_sem == 0 and semana_atual > 1:
            alertas.append({
                'tipo': 'VERMELHO',
                'professor': prof,
                'professor_raw': prof,
                'unidade': unidade,
                'disciplinas': disciplinas,
                'detalhe': f'0 registros na semana {semana_atual}',
                'valor': 0,
            })

        # --- ALERTA AMARELO: Registro em Queda ---
        if not prof_semana.empty and semana_atual > 2:
            sem_ant = prof_semana[
                (prof_semana['professor'] == prof) &
                (prof_semana['semana_letiva'] == semana_atual - 1)
            ]
            sem_ant_ant = prof_semana[
                (prof_semana['professor'] == prof) &
                (prof_semana['semana_letiva'] == semana_atual - 2)
            ]
            n_ant = sem_ant['aulas'].sum() if not sem_ant.empty else 0
            n_ant_ant = sem_ant_ant['aulas'].sum() if not sem_ant_ant.empty else 0

            if n_ant_ant > 0 and n_ant > 0:
                queda = ((n_ant_ant - n_ant) / n_ant_ant) * 100
                if queda > CONTEUDO_VAZIO_ALERTA:
                    alertas.append({
                        'tipo': 'AMARELO',
                        'professor': prof,
                        'professor_raw': prof,
                        'unidade': unidade,
                        'disciplinas': disciplinas,
                        'detalhe': f'Queda de {queda:.0f}%: sem {semana_atual-2}={n_ant_ant} -> sem {semana_atual-1}={n_ant}',
                        'valor': round(queda, 1),
                    })

        # --- ALERTA AZUL: Frequencia Pendente ---
        if df_prof_aulas['data'].notna().any():
            ultimo_registro = df_prof_aulas['data'].max()
            dias_sem = (hoje - ultimo_registro).days
            if dias_sem > 5:
                alertas.append({
                    'tipo': 'AZUL',
                    'professor': prof,
                    'professor_raw': prof,
                    'unidade': unidade,
                    'disciplinas': disciplinas,
                    'detalhe': f'{dias_sem} dias sem registro (ultimo: {ultimo_registro.strftime("%d/%m")})',
                    'valor': dias_sem,
                })

    # --- ALERTA LARANJA: Curriculo Atrasado (por disciplina/serie) ---
    for (un, serie, disc), grupo_hor in df_horario.groupby(['unidade', 'serie', 'disciplina']):
        df_disc_aulas = df_aulas[
            (df_aulas['unidade'] == un) &
            (df_aulas['serie'] == serie) &
            (df_aulas['disciplina'] == disc)
        ]

        if df_disc_aulas.empty:
            continue

        aulas_esp_total = len(grupo_hor) * semana_atual
        aulas_real = len(df_disc_aulas)
        taxa = (aulas_real / aulas_esp_total * 100) if aulas_esp_total > 0 else 0

        if taxa < CONFORMIDADE_CRITICO and aulas_real > 0:
            profs_disc = ', '.join(sorted(df_disc_aulas['professor'].unique())[:2])
            alertas.append({
                'tipo': 'LARANJA',
                'professor': profs_disc,
                'professor_raw': '',
                'unidade': un,
                'disciplinas': f'{disc} ({serie})',
                'detalhe': f'{taxa:.0f}% das aulas ({aulas_real}/{aulas_esp_total}) - possivel atraso curricular',
                'valor': round(100 - taxa, 1),
            })

    # --- ALERTA ROSA: Disciplina Orfa ---
    for (un, serie, disc), grupo_hor in df_horario.groupby(['unidade', 'serie', 'disciplina']):
        df_disc_aulas = df_aulas[
            (df_aulas['unidade'] == un) &
            (df_aulas['serie'] == serie) &
            (df_aulas['disciplina'] == disc)
        ]

        if len(df_disc_aulas) == 0 and semana_atual > 1:
            alertas.append({
                'tipo': 'ROSA',
                'professor': 'Nenhum registro',
                'professor_raw': '',
                'unidade': un,
                'disciplinas': f'{disc} ({serie})',
                'detalhe': f'Zero registros desde o inicio do ano',
                'valor': semana_atual,
            })

    return pd.DataFrame(alertas)


@st.cache_data(ttl=300)
def calcular_score_risco(df_aulas, df_horario, semana_atual):
    """Calcula Score de Risco do Professor (0-100, quanto MENOR pior).
    Usa fato_Aulas como base e calcula esperado via (unidade, serie, disciplina).
    """
    hoje = _hoje()
    scores = []

    for prof in df_aulas['professor'].unique():
        df_prof_aulas = df_aulas[df_aulas['professor'] == prof]
        unidade = df_prof_aulas['unidade'].iloc[0]
        disciplinas = sorted(df_prof_aulas['disciplina'].unique())
        series = df_prof_aulas['serie'].unique()

        # Calcula esperado via horario usando chaves (unidade, serie, disciplina)
        aulas_semana_esp = 0
        for serie_p in series:
            for disc_p in disciplinas:
                n = len(df_horario[
                    (df_horario['unidade'] == unidade) &
                    (df_horario['serie'] == serie_p) &
                    (df_horario['disciplina'] == disc_p)
                ])
                aulas_semana_esp += n

        esperado = aulas_semana_esp * semana_atual

        # 1. Taxa de registro (peso 0.35)
        registrado = len(df_prof_aulas)
        taxa_registro = min(100, (registrado / esperado * 100)) if esperado > 0 else 0

        # 2. Taxa de conteudo (peso 0.25)
        com_conteudo = df_prof_aulas[df_prof_aulas['conteudo'].notna() & (df_prof_aulas['conteudo'] != '')].shape[0]
        taxa_conteudo = (com_conteudo / registrado * 100) if registrado > 0 else 0

        # 3. Indice de tarefa (peso 0.15)
        com_tarefa = df_prof_aulas[df_prof_aulas['tarefa'].notna() & (df_prof_aulas['tarefa'] != '')].shape[0]
        taxa_tarefa = (com_tarefa / registrado * 100) if registrado > 0 else 0

        # 4. Regularidade/recencia (peso 0.25)
        if df_prof_aulas['data'].notna().any():
            ultimo = df_prof_aulas['data'].max()
            dias_sem = (hoje - ultimo).days
            recencia = max(0, min(100, 100 - (dias_sem * 100 / 14)))
        else:
            recencia = 0

        # Score composto
        score = (
            0.35 * taxa_registro +
            0.25 * taxa_conteudo +
            0.15 * taxa_tarefa +
            0.25 * recencia
        )

        scores.append({
            'Professor': prof,
            'Professor_Raw': prof,
            'Unidade': unidade,
            'Disciplinas': ', '.join(disciplinas[:3]) + ('...' if len(disciplinas) > 3 else ''),
            'Score': round(score, 1),
            'Taxa Registro': round(min(taxa_registro, 100), 1),
            'Taxa Conteudo': round(taxa_conteudo, 1),
            'Taxa Tarefa': round(taxa_tarefa, 1),
            'Recencia': round(recencia, 1),
            'Registrado': registrado,
            'Esperado': esperado,
        })

    return pd.DataFrame(scores)


def main():
    st.title("🧠 Alertas Inteligentes")
    st.markdown("**Detecta problemas ANTES que se tornem criticos**")

    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()

    if df_aulas.empty or df_horario.empty:
        st.error("Dados nao carregados. Execute a extracao do SIGA primeiro.")
        return

    df_aulas = filtrar_ate_hoje(df_aulas)
    semana = calcular_semana_letiva()
    capitulo = calcular_capitulo_esperado(semana)

    # ========== FILTROS ==========
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        un_opts = ['TODAS'] + sorted(df_horario['unidade'].unique().tolist())
        user_unit = get_user_unit()
        default_un = un_opts.index(user_unit) if user_unit and user_unit in un_opts else 0
        filtro_un = st.selectbox("🏫 Unidade", un_opts, index=default_un)

    with col_f2:
        seg_opts = ['TODOS', 'Anos Finais', 'Ensino Medio']
        filtro_seg = st.selectbox("📚 Segmento", seg_opts)

    with col_f3:
        periodo_sel = st.selectbox("📅 Periodo", PERIODOS_OPCOES, key='periodo_14')

    # Aplica filtro de periodo
    df_aulas = filtrar_por_periodo(df_aulas, periodo_sel)

    # Aplica filtros
    df_hor_f = df_horario.copy()
    df_aulas_f = df_aulas.copy()

    if filtro_un != 'TODAS':
        df_hor_f = df_hor_f[df_hor_f['unidade'] == filtro_un]
        df_aulas_f = df_aulas_f[df_aulas_f['unidade'] == filtro_un]

    if filtro_seg == 'Anos Finais':
        df_hor_f = df_hor_f[df_hor_f['serie'].isin(SERIES_FUND_II)]
        df_aulas_f = df_aulas_f[df_aulas_f['serie'].isin(SERIES_FUND_II)]
    elif filtro_seg == 'Ensino Medio':
        df_hor_f = df_hor_f[df_hor_f['serie'].isin(SERIES_EM)]
        df_aulas_f = df_aulas_f[df_aulas_f['serie'].isin(SERIES_EM)]

    if df_aulas_f.empty:
        st.info("Nenhum dado encontrado para os filtros selecionados.")
        return

    # ========== LEGENDA ==========
    st.markdown("---")
    st.markdown("""
    <div class="legenda-box">
        <strong>Tipos de Alerta:</strong><br>
        🔴 <strong>Professor Silencioso</strong> - 0 registros na semana |
        🟡 <strong>Registro em Queda</strong> - Queda >30% vs semana anterior |
        🟠 <strong>Curriculo Atrasado</strong> - >1 capitulo atras |
        🔵 <strong>Frequencia Pendente</strong> - >5 dias sem lancar |
        🩷 <strong>Disciplina Orfa</strong> - Sem registro >1 semana
    </div>
    """, unsafe_allow_html=True)

    # ========== DETECTA ALERTAS ==========
    df_alertas = detectar_alertas(df_aulas_f, df_hor_f, semana)

    # Cards resumo
    st.markdown("---")

    n_por_tipo = {}
    for tipo in TIPOS_ALERTA:
        n_por_tipo[tipo] = len(df_alertas[df_alertas['tipo'] == tipo]) if not df_alertas.empty else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    cores_bg = ['#FFEBEE', '#FFF8E1', '#FFF3E0', '#E3F2FD', '#FCE4EC']

    for i, (tipo, info) in enumerate(TIPOS_ALERTA.items()):
        with cols[i]:
            n = n_por_tipo[tipo]
            st.metric(
                f"{info['emoji']} {info['nome'][:15]}",
                n,
                delta="OK" if n == 0 else f"{n} alerta{'s' if n > 1 else ''}",
                delta_color="normal" if n == 0 else "inverse"
            )

    # ========== ALERTAS ATIVOS ==========
    st.markdown("---")
    st.header("🚨 Alertas Ativos")

    if df_alertas.empty:
        st.success("🎉 Nenhum alerta ativo! Todos os indicadores estao dentro do esperado.")
    else:
        # Filtro de tipo de alerta
        tipos_sel = st.multiselect(
            "Filtrar por tipo de alerta:",
            [f"{info['emoji']} {info['nome']}" for tipo, info in TIPOS_ALERTA.items()],
            default=[f"{info['emoji']} {info['nome']}" for tipo, info in TIPOS_ALERTA.items()
                     if n_por_tipo[tipo] > 0]
        )

        # Mapeia nomes para tipos
        nome_to_tipo = {f"{info['emoji']} {info['nome']}": tipo for tipo, info in TIPOS_ALERTA.items()}
        tipos_filtrados = [nome_to_tipo[t] for t in tipos_sel if t in nome_to_tipo]

        df_alertas_f = df_alertas[df_alertas['tipo'].isin(tipos_filtrados)]

        # Ordena por prioridade
        prioridade_map = {tipo: info['prioridade'] for tipo, info in TIPOS_ALERTA.items()}
        df_alertas_f = df_alertas_f.copy()
        df_alertas_f['_pri'] = df_alertas_f['tipo'].map(prioridade_map)
        df_alertas_f = df_alertas_f.sort_values('_pri')

        # Exibe alertas com HTML estilizado
        css_map = {
            'VERMELHO': 'alerta-vermelho',
            'AMARELO': 'alerta-amarelo',
            'LARANJA': 'alerta-laranja',
            'AZUL': 'alerta-azul',
            'ROSA': 'alerta-rosa',
        }

        for _, alerta in df_alertas_f.iterrows():
            tipo = alerta['tipo']
            info = TIPOS_ALERTA[tipo]
            css_class = css_map[tipo]
            st.markdown(f"""
            <div class="{css_class}">
                <strong>{info['emoji']} {info['nome']}</strong> | <strong>{alerta['professor']}</strong> ({alerta['unidade']}) - {alerta['disciplinas']}<br>
                <small>{alerta['detalhe']}</small><br>
                <em>Acao: {info['acao']}</em>
            </div>
            """, unsafe_allow_html=True)

        # Tabela resumo
        st.markdown("---")
        st.subheader("📋 Tabela de Alertas")

        df_tabela = df_alertas_f[['tipo', 'professor', 'unidade', 'disciplinas', 'detalhe']].copy()
        df_tabela['tipo'] = df_tabela['tipo'].apply(lambda t: f"{TIPOS_ALERTA[t]['emoji']} {TIPOS_ALERTA[t]['nome']}")
        df_tabela.columns = ['Tipo', 'Professor', 'Unidade', 'Disciplinas', 'Detalhe']
        st.dataframe(df_tabela, use_container_width=True, hide_index=True)

    # ========== SCORE DE RISCO ==========
    st.markdown("---")
    st.header("📊 Score de Risco do Professor")

    st.markdown("""
    <div class="legenda-box">
        <strong>Formula:</strong> Score = 0.35 x Taxa Registro + 0.25 x Taxa Conteudo + 0.15 x Taxa Tarefa + 0.25 x Recencia<br>
        <small>Quanto MAIOR o score, MELHOR o professor esta. Score < {CONFORMIDADE_CRITICO} = critico | {CONFORMIDADE_CRITICO}-{CONFORMIDADE_BAIXO} = atencao | > {CONFORMIDADE_BAIXO} = em dia</small>
    </div>
    """, unsafe_allow_html=True)

    df_scores = calcular_score_risco(df_aulas_f, df_hor_f, semana)

    if not df_scores.empty:
        df_scores = df_scores.sort_values('Score')

        # Categoriza
        df_scores['Nivel'] = df_scores['Score'].apply(
            lambda s: '🔴 Critico' if s < CONFORMIDADE_CRITICO else ('🟡 Atencao' if s < CONFORMIDADE_BAIXO else '🟢 Em Dia')
        )

        # Contadores
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        n_critico = len(df_scores[df_scores['Score'] < CONFORMIDADE_CRITICO])
        n_atencao = len(df_scores[(df_scores['Score'] >= CONFORMIDADE_CRITICO) & (df_scores['Score'] < CONFORMIDADE_BAIXO)])
        n_ok = len(df_scores[df_scores['Score'] >= CONFORMIDADE_BAIXO])
        media = df_scores['Score'].mean()

        with col_s1:
            st.metric(f"🔴 Critico (<{CONFORMIDADE_CRITICO})", n_critico)
        with col_s2:
            st.metric(f"🟡 Atencao ({CONFORMIDADE_CRITICO}-{CONFORMIDADE_BAIXO})", n_atencao)
        with col_s3:
            st.metric(f"🟢 Em Dia (>{CONFORMIDADE_BAIXO})", n_ok)
        with col_s4:
            st.metric("Score Medio", f"{media:.0f}")

        # Grafico de distribuicao
        fig_dist = px.histogram(
            df_scores, x='Score', nbins=20,
            title='Distribuicao de Scores',
            color_discrete_sequence=['#5C6BC0'],
            labels={'Score': 'Score de Risco', 'count': 'Professores'}
        )
        fig_dist.add_vline(x=CONFORMIDADE_CRITICO, line_dash="dash", line_color="red", annotation_text="Critico")
        fig_dist.add_vline(x=CONFORMIDADE_BAIXO, line_dash="dash", line_color="green", annotation_text="Em Dia")
        st.plotly_chart(fig_dist, use_container_width=True)

        # Grafico scatter: Score x Taxa Registro
        fig_scatter = px.scatter(
            df_scores, x='Taxa Registro', y='Score',
            color='Nivel', hover_name='Professor',
            hover_data=['Unidade', 'Disciplinas', 'Taxa Conteudo', 'Recencia'],
            title='Score de Risco vs Taxa de Registro',
            color_discrete_map={'🔴 Critico': '#F44336', '🟡 Atencao': '#FFC107', '🟢 Em Dia': '#4CAF50'}
        )
        fig_scatter.update_traces(marker_size=10)
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Tabela detalhada
        st.subheader("📋 Ranking de Professores por Score")

        df_rank = df_scores[['Nivel', 'Professor', 'Unidade', 'Disciplinas', 'Score',
                             'Taxa Registro', 'Taxa Conteudo', 'Taxa Tarefa', 'Recencia',
                             'Registrado', 'Esperado']].copy()
        df_rank['Score'] = df_rank['Score'].apply(lambda x: f'{x:.0f}')
        df_rank['Taxa Registro'] = df_rank['Taxa Registro'].apply(lambda x: f'{x:.0f}%')
        df_rank['Taxa Conteudo'] = df_rank['Taxa Conteudo'].apply(lambda x: f'{x:.0f}%')
        df_rank['Taxa Tarefa'] = df_rank['Taxa Tarefa'].apply(lambda x: f'{x:.0f}%')
        df_rank['Recencia'] = df_rank['Recencia'].apply(lambda x: f'{x:.0f}')

        st.dataframe(df_rank, use_container_width=True, hide_index=True, height=500)

    # ========== EVOLUCAO SEMANAL DE ALERTAS ==========
    st.markdown("---")
    st.header("📈 Evolucao Semanal")

    if 'semana_letiva' in df_aulas.columns and semana > 1:
        evolucao = []
        # Total de slots esperados/semana e professores conhecidos (de fato_Aulas)
        profs_total = df_aulas_f['professor'].nunique()
        esperado_sem = len(df_hor_f)

        for s in range(1, semana + 1):
            df_sem = df_aulas_f[df_aulas_f['semana_letiva'] == s]
            profs_ativos = df_sem['professor'].nunique()
            aulas_sem = len(df_sem)

            evolucao.append({
                'Semana': s,
                'Professores Ativos': profs_ativos,
                'Total Professores': profs_total,
                '% Ativos': round(profs_ativos / profs_total * 100, 1) if profs_total > 0 else 0,
                'Aulas Registradas': aulas_sem,
                'Aulas Esperadas': esperado_sem,
                '% Conformidade': round(aulas_sem / esperado_sem * 100, 1) if esperado_sem > 0 else 0,
            })

        df_evol = pd.DataFrame(evolucao)

        fig_evol = go.Figure()
        fig_evol.add_trace(go.Scatter(
            x=df_evol['Semana'], y=df_evol['% Ativos'],
            mode='lines+markers', name='% Professores Ativos',
            line=dict(color='#2196F3', width=3),
            marker=dict(size=8)
        ))
        fig_evol.add_trace(go.Scatter(
            x=df_evol['Semana'], y=df_evol['% Conformidade'],
            mode='lines+markers', name='% Conformidade',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=8)
        ))
        fig_evol.add_hline(y=80, line_dash="dash", line_color="orange", annotation_text="Meta 80%")
        fig_evol.update_layout(
            title='Evolucao Semanal de Atividade',
            xaxis_title='Semana Letiva',
            yaxis_title='Percentual (%)',
            yaxis_range=[0, 110],
            height=400
        )
        st.plotly_chart(fig_evol, use_container_width=True)

        st.dataframe(df_evol, use_container_width=True, hide_index=True)

    # ========== EXPORTACAO ==========
    st.markdown("---")
    st.header("📥 Exportar")

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        if not df_alertas.empty:
            csv_alertas = df_alertas.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 Alertas (CSV)",
                csv_alertas,
                f"alertas_inteligentes_{_hoje().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv"
            )

    with col_e2:
        if not df_scores.empty:
            csv_scores = df_scores.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 Scores (CSV)",
                csv_scores,
                f"scores_risco_{_hoje().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv"
            )

    with col_e3:
        # Relatorio TXT
        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("     ALERTAS INTELIGENTES - COLEGIO ELO 2026")
        relatorio.append("=" * 80)
        relatorio.append(f"Gerado em: {_hoje().strftime('%d/%m/%Y %H:%M')}")
        relatorio.append(f"Semana letiva: {semana}a | Capitulo esperado: {capitulo}")
        relatorio.append(f"Filtro: {filtro_un} | {filtro_seg}")
        relatorio.append("")

        if not df_alertas.empty:
            for tipo, info in TIPOS_ALERTA.items():
                grupo = df_alertas[df_alertas['tipo'] == tipo]
                if not grupo.empty:
                    relatorio.append(f"{info['emoji']} {info['nome'].upper()} ({len(grupo)})")
                    relatorio.append(f"   Acao: {info['acao']}")
                    relatorio.append("-" * 40)
                    for _, a in grupo.iterrows():
                        relatorio.append(f"  {a['professor']:<30} {a['unidade']:<5} {a['detalhe']}")
                    relatorio.append("")
        else:
            relatorio.append("Nenhum alerta ativo!")

        if not df_scores.empty:
            relatorio.append("")
            relatorio.append("SCORES DE RISCO (Top 10 piores)")
            relatorio.append("-" * 60)
            for _, row in df_scores.head(10).iterrows():
                relatorio.append(f"  Score {row['Score']:5.0f} | {row['Professor']:<30} {row['Unidade']:<5} {row['Disciplinas'][:20]}")

        relatorio.append("")
        relatorio.append("=" * 80)
        relatorio.append("                 Coordenacao Pedagogica - Colegio ELO")
        relatorio.append("=" * 80)

        txt = "\n".join(relatorio)
        st.download_button(
            "🖨️ Imprimir (TXT)",
            txt.encode('utf-8'),
            f"alertas_inteligentes_{_hoje().strftime('%Y%m%d_%H%M')}.txt",
            "text/plain"
        )


if __name__ == "__main__":
    main()
