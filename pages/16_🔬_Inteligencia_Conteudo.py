#!/usr/bin/env python3
"""
PAGINA 16: INTELIGENCIA DE CONTEUDO
Analise profunda do campo conteudo para extrair capitulos,
medir qualidade dos registros e detectar alinhamento com SAE.
"""

import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
    filtrar_por_periodo, PERIODOS_OPCOES,
    calcular_semana_letiva, calcular_capitulo_esperado, _hoje,
    SERIES_FUND_II, SERIES_EM, UNIDADES_NOMES,
)
from config_cores import CORES_SERIES, CORES_UNIDADES, ORDEM_SERIES

st.set_page_config(page_title="Inteligência de Conteúdo", page_icon="🔬", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

# ========== FUNCOES DE ANALISE ==========

# Regex para detectar capitulos no conteudo
CAP_PATTERNS = [
    r'[Cc]ap(?:ítulo|itulo)?\.?\s*(\d{1,2})',
    r'[Cc]apítulo\s+(\d{1,2})',
    r'[Uu]nidade\s+(\d{1,2})',
    r'[Mm]ódulo\s+(\d{1,2})',
]

# Palavras-chave que indicam atividade avaliativa
KEYWORDS_AVALIACAO = ['prova', 'avaliação', 'avaliaç', 'simulado', 'teste', 'a1', 'a2']
KEYWORDS_PRATICA = ['atividade', 'exercício', 'exercicio', 'resolução', 'correção', 'tarefa']
KEYWORDS_EXPOSICAO = ['exposição', 'explicação', 'aula expositiva', 'apresentação', 'conteúdo']
KEYWORDS_PROJETO = ['projeto', 'trabalho', 'pesquisa', 'seminário']
KEYWORDS_LEITURA = ['leitura', 'livro', 'texto', 'interpretação', 'pp.', 'pág']


def extrair_capitulo(texto):
    """Extrai numero do capitulo mencionado no conteudo."""
    if pd.isna(texto) or texto in ('.', '', ','):
        return None
    for pattern in CAP_PATTERNS:
        match = re.search(pattern, str(texto))
        if match:
            cap = int(match.group(1))
            if 1 <= cap <= 12:
                return cap
    return None


def classificar_tipo_aula(texto):
    """Classifica o tipo de atividade descrita no conteudo."""
    if pd.isna(texto) or texto in ('.', '', ','):
        return 'Vazio'
    texto_lower = str(texto).lower()
    if any(k in texto_lower for k in KEYWORDS_AVALIACAO):
        return 'Avaliativa'
    if any(k in texto_lower for k in KEYWORDS_PROJETO):
        return 'Projeto'
    if any(k in texto_lower for k in KEYWORDS_PRATICA):
        return 'Pratica'
    if any(k in texto_lower for k in KEYWORDS_LEITURA):
        return 'Leitura'
    if any(k in texto_lower for k in KEYWORDS_EXPOSICAO):
        return 'Expositiva'
    return 'Outro'


def calcular_score_qualidade(row):
    """Score 0-100 de qualidade do registro."""
    conteudo = str(row.get('conteudo', '')) if pd.notna(row.get('conteudo')) else ''
    tarefa = str(row.get('tarefa', '')) if pd.notna(row.get('tarefa')) else ''

    score = 0

    # Conteudo preenchido (0-40)
    if conteudo and conteudo not in ('.', ',', '-'):
        length = len(conteudo)
        if length >= 80:
            score += 40
        elif length >= 40:
            score += 30
        elif length >= 15:
            score += 20
        else:
            score += 10

    # Tarefa preenchida (0-20)
    if tarefa and tarefa not in ('.', ',', '-'):
        score += 20

    # Mencao a capitulo (0-20)
    if extrair_capitulo(conteudo):
        score += 20

    # Mencao a pagina do livro (0-10)
    if re.search(r'p[pg]?\.\s*\d+|página\s+\d+', conteudo, re.IGNORECASE):
        score += 10

    # Tipo de atividade identificavel (0-10)
    tipo = classificar_tipo_aula(conteudo)
    if tipo not in ('Vazio', 'Outro'):
        score += 10

    return min(100, score)


def main():
    st.title("🔬 Inteligência de Conteúdo")
    st.markdown("**Análise profunda dos registros: qualidade, capítulos e alinhamento SAE**")

    df = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()

    if df.empty:
        st.error("Dados não carregados.")
        return

    df = filtrar_ate_hoje(df)

    # Filtro de periodo (selectbox sera renderizado abaixo nos filtros)
    periodo_sel = st.session_state.get('periodo_16', PERIODOS_OPCOES[0])
    df = filtrar_por_periodo(df, periodo_sel)

    hoje = _hoje()
    semana_atual = calcular_semana_letiva(hoje)
    cap_esperado = calcular_capitulo_esperado(semana_atual)

    # Enriquece dados
    df['capitulo_detectado'] = df['conteudo'].apply(extrair_capitulo)
    df['tipo_aula'] = df['conteudo'].apply(classificar_tipo_aula)
    df['score_qualidade'] = df.apply(calcular_score_qualidade, axis=1)

    # ========== FILTROS ==========
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        opcoes_un = ['TODAS'] + sorted(df['unidade'].dropna().unique().tolist())
        user_unit = get_user_unit()
        default_un = opcoes_un.index(user_unit) if user_unit and user_unit in opcoes_un else 0
        un_sel = st.selectbox("Unidade:", opcoes_un, index=default_un)

    with col_f2:
        st.selectbox("Período:", PERIODOS_OPCOES, key='periodo_16')

    with col_f3:
        segmento = st.radio("Segmento:", ['Todos', 'Fund II', 'EM'], horizontal=True)

    with col_f4:
        st.metric("Semana Letiva", f"{semana_atual}a")
        st.metric("Capítulo Esperado", f"{cap_esperado}/12")

    # Aplica filtros
    df_f = df.copy()
    if un_sel != 'TODAS':
        df_f = df_f[df_f['unidade'] == un_sel]
    if segmento == 'Fund II':
        df_f = df_f[df_f['serie'].isin(SERIES_FUND_II)]
    elif segmento == 'EM':
        df_f = df_f[df_f['serie'].isin(SERIES_EM)]

    # ========== METRICAS PRINCIPAIS ==========
    st.markdown("---")

    total = len(df_f)
    vazios = len(df_f[df_f['tipo_aula'] == 'Vazio'])
    com_capitulo = df_f['capitulo_detectado'].notna().sum()
    score_medio = df_f['score_qualidade'].mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Aulas", f"{total:,}")
    with col2:
        pct_vazio = (vazios / total * 100) if total > 0 else 0
        st.metric("Registros Vazios", f"{vazios} ({pct_vazio:.0f}%)",
                  delta=f"-{pct_vazio:.0f}%" if pct_vazio > 0 else "0%",
                  delta_color="inverse")
    with col3:
        pct_cap = (com_capitulo / total * 100) if total > 0 else 0
        st.metric("Com Capítulo", f"{com_capitulo} ({pct_cap:.0f}%)")
    with col4:
        st.metric("Score Médio", f"{score_medio:.0f}/100")
    with col5:
        # Capitulos unicos detectados
        caps_unicos = sorted(df_f['capitulo_detectado'].dropna().unique())
        st.metric("Capítulos Cobertos", f"{len(caps_unicos)}/12")

    # ========== TABS ==========
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Qualidade por Professor",
        "📖 Cobertura de Capítulos",
        "🎯 Tipos de Atividade",
        "⚠️ Alertas de Conteúdo"
    ])

    # ========== TAB 1: QUALIDADE POR PROFESSOR ==========
    with tab1:
        st.header("📊 Score de Qualidade por Professor")

        st.markdown("""
        **Como funciona o Score:** Cada registro recebe 0-100 pontos baseado em:
        conteúdo preenchido (40pts), tarefa registrada (20pts), capítulo mencionado (20pts),
        página do livro (10pts), tipo de atividade (10pts).
        """)

        # Agrupa por professor
        prof_qual = df_f.groupby(['professor', 'unidade']).agg(
            aulas=('conteudo', 'count'),
            score_medio=('score_qualidade', 'mean'),
            vazios=('tipo_aula', lambda x: (x == 'Vazio').sum()),
            com_capitulo=('capitulo_detectado', lambda x: x.notna().sum()),
        ).reset_index()

        prof_qual['pct_vazios'] = (prof_qual['vazios'] / prof_qual['aulas'] * 100).round(1)
        prof_qual['pct_capitulo'] = (prof_qual['com_capitulo'] / prof_qual['aulas'] * 100).round(1)

        # Classificacao
        prof_qual['classificacao'] = prof_qual['score_medio'].apply(
            lambda x: 'Excelente' if x >= 70 else ('Bom' if x >= 50 else ('Regular' if x >= 30 else 'Precisa Melhorar'))
        )

        prof_qual = prof_qual.sort_values('score_medio', ascending=False)

        # Tabela
        df_show = prof_qual.rename(columns={
            'professor': 'Professor',
            'unidade': 'Unidade',
            'aulas': 'Aulas',
            'score_medio': 'Score',
            'pct_vazios': '% Vazios',
            'pct_capitulo': '% c/ Capítulo',
            'classificacao': 'Classificação',
        })
        df_show['Score'] = df_show['Score'].round(0).astype(int)

        st.dataframe(
            df_show[['Professor', 'Unidade', 'Aulas', 'Score', '% Vazios', '% c/ Capítulo', 'Classificação']],
            use_container_width=True, hide_index=True, height=400
        )

        # Grafico
        fig = px.bar(
            prof_qual.head(20),
            x='professor', y='score_medio',
            color='unidade',
            color_discrete_map=CORES_UNIDADES,
            title='Top 20 - Score de Qualidade por Professor',
            labels={'professor': 'Professor', 'score_medio': 'Score'},
        )
        fig.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Meta mínima")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

        # Distribuicao
        fig2 = px.histogram(
            prof_qual, x='score_medio', nbins=10,
            title='Distribuição dos Scores de Qualidade',
            labels={'score_medio': 'Score Médio'},
            color_discrete_sequence=['#1976D2'],
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ========== TAB 2: COBERTURA DE CAPITULOS ==========
    with tab2:
        st.header("📖 Cobertura de Capítulos SAE")

        st.markdown(f"""
        **Semana {semana_atual}** - Capítulo esperado: **{cap_esperado}/12**

        A análise detecta menções a capítulos no campo de conteúdo e compara
        com a progressão esperada SAE (3.5 semanas por capítulo).
        """)

        # Filtro de disciplina
        disciplinas = sorted(df_f['disciplina'].dropna().unique())
        disc_sel = st.selectbox("Disciplina:", ['TODAS'] + disciplinas)

        df_cap = df_f.copy()
        if disc_sel != 'TODAS':
            df_cap = df_cap[df_cap['disciplina'] == disc_sel]

        # Cobertura por serie
        st.subheader("Cobertura por Série")

        cobertura = []
        series_list = [s for s in ORDEM_SERIES if s in df_cap['serie'].unique()]

        for serie in series_list:
            df_s = df_cap[df_cap['serie'] == serie]
            caps_detectados = sorted(df_s['capitulo_detectado'].dropna().unique())
            max_cap = max(caps_detectados) if caps_detectados else 0

            cobertura.append({
                'Série': serie,
                'Capítulos Detectados': ', '.join(str(int(c)) for c in caps_detectados) if caps_detectados else '-',
                'Max Capítulo': int(max_cap),
                'Esperado': cap_esperado,
                'Diferença': int(max_cap) - cap_esperado,
                'Status': 'Adiantado' if max_cap > cap_esperado else ('No prazo' if max_cap >= cap_esperado - 1 else 'Atrasado'),
                'Registros c/ Cap': df_s['capitulo_detectado'].notna().sum(),
                'Total Registros': len(df_s),
            })

        df_cob = pd.DataFrame(cobertura)
        st.dataframe(df_cob, use_container_width=True, hide_index=True)

        # Heatmap: Serie x Capitulo (contagem de aulas)
        if len(df_cap[df_cap['capitulo_detectado'].notna()]) > 0:
            st.subheader("Mapa de Calor: Aulas por Capítulo")

            pivot = df_cap[df_cap['capitulo_detectado'].notna()].copy()
            pivot['capitulo_detectado'] = pivot['capitulo_detectado'].astype(int)

            heat = pivot.groupby(['serie', 'capitulo_detectado']).size().reset_index(name='aulas')
            heat_pivot = heat.pivot(index='serie', columns='capitulo_detectado', values='aulas').fillna(0)

            # Reordenar series
            ordered = [s for s in ORDEM_SERIES if s in heat_pivot.index]
            heat_pivot = heat_pivot.reindex(ordered)

            # Adiciona colunas faltantes ate 12
            for c in range(1, 13):
                if c not in heat_pivot.columns:
                    heat_pivot[c] = 0
            heat_pivot = heat_pivot[sorted(heat_pivot.columns)]

            fig = go.Figure(data=go.Heatmap(
                z=heat_pivot.values,
                x=[f'Cap {c}' for c in heat_pivot.columns],
                y=heat_pivot.index.tolist(),
                colorscale='Blues',
                text=heat_pivot.values.astype(int),
                texttemplate='%{text}',
                hovertemplate='%{y}<br>%{x}: %{z} aulas<extra></extra>',
            ))

            # Linha vertical no capitulo esperado
            fig.add_vline(x=cap_esperado - 0.5, line_dash="dash", line_color="red",
                         annotation_text=f"Esperado (Cap {cap_esperado})")

            fig.update_layout(
                title='Aulas por Série x Capítulo (detectado no conteúdo)',
                xaxis_title='Capítulo',
                yaxis_title='Série',
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)

        # Cobertura por disciplina
        if disc_sel == 'TODAS':
            st.subheader("Cobertura por Disciplina")

            disc_cob = []
            for disc in disciplinas:
                df_d = df_cap[df_cap['disciplina'] == disc]
                caps = sorted(df_d['capitulo_detectado'].dropna().unique())
                max_c = max(caps) if caps else 0

                disc_cob.append({
                    'Disciplina': disc,
                    'Max Capítulo': int(max_c),
                    'Esperado': cap_esperado,
                    'Diferença': int(max_c) - cap_esperado,
                    'Registros c/ Cap': df_d['capitulo_detectado'].notna().sum(),
                    'Total Registros': len(df_d),
                })

            df_disc_cob = pd.DataFrame(disc_cob).sort_values('Diferença')
            st.dataframe(df_disc_cob, use_container_width=True, hide_index=True)

    # ========== TAB 3: TIPOS DE ATIVIDADE ==========
    with tab3:
        st.header("🎯 Distribuição de Tipos de Atividade")

        st.markdown("""
        Cada registro é classificado automaticamente pelo conteúdo:
        **Expositiva** (aula teórica), **Prática** (exercícios),
        **Leitura** (livro/texto), **Avaliativa** (prova/teste),
        **Projeto** (trabalho/pesquisa), **Outro** ou **Vazio**.
        """)

        # Contagem por tipo
        tipos = df_f['tipo_aula'].value_counts().reset_index()
        tipos.columns = ['Tipo', 'Quantidade']

        col1, col2 = st.columns(2)

        with col1:
            cores_tipo = {
                'Expositiva': '#1976D2',
                'Pratica': '#43A047',
                'Leitura': '#7B1FA2',
                'Avaliativa': '#E53935',
                'Projeto': '#F57C00',
                'Outro': '#9E9E9E',
                'Vazio': '#BDBDBD',
            }
            fig = px.pie(tipos, values='Quantidade', names='Tipo',
                        title='Distribuição Geral',
                        color='Tipo',
                        color_discrete_map=cores_tipo)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(tipos, x='Tipo', y='Quantidade',
                        title='Contagem por Tipo',
                        color='Tipo',
                        color_discrete_map=cores_tipo)
            st.plotly_chart(fig, use_container_width=True)

        # Por unidade
        st.subheader("Tipos por Unidade")
        tipo_un = df_f.groupby(['unidade', 'tipo_aula']).size().reset_index(name='qtd')
        fig = px.bar(tipo_un, x='unidade', y='qtd', color='tipo_aula',
                    title='Tipos de Atividade por Unidade',
                    color_discrete_map=cores_tipo,
                    barmode='stack')
        st.plotly_chart(fig, use_container_width=True)

        # Por serie
        st.subheader("Tipos por Série")
        tipo_serie = df_f.groupby(['serie', 'tipo_aula']).size().reset_index(name='qtd')
        # Ordena series
        tipo_serie['ordem'] = tipo_serie['serie'].apply(
            lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99)
        tipo_serie = tipo_serie.sort_values('ordem')

        fig = px.bar(tipo_serie, x='serie', y='qtd', color='tipo_aula',
                    title='Tipos de Atividade por Série',
                    color_discrete_map=cores_tipo,
                    barmode='stack')
        st.plotly_chart(fig, use_container_width=True)

    # ========== TAB 4: ALERTAS DE CONTEUDO ==========
    with tab4:
        st.header("⚠️ Alertas de Conteúdo")

        # Alerta 1: Professores com muitos registros vazios
        st.subheader("🔴 Professores com Registros Vazios Excessivos")

        prof_vazio = df_f.groupby(['professor', 'unidade']).agg(
            total=('conteudo', 'count'),
            vazios=('tipo_aula', lambda x: (x == 'Vazio').sum()),
        ).reset_index()
        prof_vazio['pct_vazio'] = (prof_vazio['vazios'] / prof_vazio['total'] * 100).round(1)
        prof_vazio = prof_vazio[prof_vazio['pct_vazio'] > 30].sort_values('pct_vazio', ascending=False)

        if len(prof_vazio) > 0:
            st.warning(f"{len(prof_vazio)} professores com mais de 30% de registros vazios")
            st.dataframe(
                prof_vazio.rename(columns={
                    'professor': 'Professor', 'unidade': 'Unidade',
                    'total': 'Total Aulas', 'vazios': 'Vazios', 'pct_vazio': '% Vazio'
                }),
                use_container_width=True, hide_index=True
            )
        else:
            st.success("Nenhum professor com mais de 30% de registros vazios")

        # Alerta 2: Disciplinas sem mencao a capitulos
        st.subheader("📖 Disciplinas sem Menção a Capítulos")

        disc_sem_cap = []
        for disc in disciplinas:
            df_d = df_f[df_f['disciplina'] == disc]
            cap_count = df_d['capitulo_detectado'].notna().sum()
            if cap_count == 0 and len(df_d) >= 5:
                disc_sem_cap.append({
                    'Disciplina': disc,
                    'Total Aulas': len(df_d),
                    'Observação': 'Nenhuma menção a capítulo detectada'
                })

        if disc_sem_cap:
            st.info(f"{len(disc_sem_cap)} disciplinas sem menção a capítulos")
            st.dataframe(pd.DataFrame(disc_sem_cap), use_container_width=True, hide_index=True)
        else:
            st.success("Todas as disciplinas com registros mencionam capítulos")

        # Alerta 3: Score abaixo da media
        st.subheader("📉 Professores com Score Abaixo de 30")

        prof_baixo = df_f.groupby(['professor', 'unidade']).agg(
            score=('score_qualidade', 'mean'),
            aulas=('conteudo', 'count'),
        ).reset_index()
        prof_baixo = prof_baixo[prof_baixo['score'] < 30].sort_values('score')

        if len(prof_baixo) > 0:
            st.error(f"{len(prof_baixo)} professores com score abaixo de 30")
            prof_baixo['score'] = prof_baixo['score'].round(0).astype(int)
            st.dataframe(
                prof_baixo.rename(columns={
                    'professor': 'Professor', 'unidade': 'Unidade',
                    'score': 'Score', 'aulas': 'Aulas',
                }),
                use_container_width=True, hide_index=True
            )
        else:
            st.success("Nenhum professor com score abaixo de 30")

        # Alerta 4: Conteudo repetido (possivel copia)
        st.subheader("🔄 Conteúdos Repetidos (Possível Cópia)")

        # Encontra conteudos identicos de professores diferentes
        df_cont = df_f[df_f['tipo_aula'] != 'Vazio'].copy()
        cont_counts = df_cont.groupby('conteudo').agg(
            professores=('professor', 'nunique'),
            total=('conteudo', 'count'),
        ).reset_index()
        cont_repetidos = cont_counts[(cont_counts['professores'] > 1) & (cont_counts['total'] > 3)]
        cont_repetidos = cont_repetidos.sort_values('total', ascending=False).head(10)

        if len(cont_repetidos) > 0:
            st.info(f"{len(cont_repetidos)} conteúdos idênticos usados por múltiplos professores")
            st.dataframe(
                cont_repetidos.rename(columns={
                    'conteudo': 'Conteúdo', 'professores': 'Professores', 'total': 'Ocorrências'
                }),
                use_container_width=True, hide_index=True
            )

        # Alerta 5: Evolucao semanal do score
        st.subheader("📈 Evolução Semanal do Score de Qualidade")

        df_semanal = df_f.groupby('semana_letiva').agg(
            score_medio=('score_qualidade', 'mean'),
            aulas=('conteudo', 'count'),
            pct_vazio=('tipo_aula', lambda x: (x == 'Vazio').sum() / max(1, len(x)) * 100),
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_semanal['semana_letiva'], y=df_semanal['score_medio'],
            mode='lines+markers', name='Score Médio',
            line=dict(color='#1976D2', width=3),
        ))
        fig.add_trace(go.Scatter(
            x=df_semanal['semana_letiva'], y=df_semanal['pct_vazio'],
            mode='lines+markers', name='% Vazios',
            line=dict(color='#E53935', width=2, dash='dot'),
            yaxis='y2',
        ))
        fig.update_layout(
            title='Evolução Semanal: Score de Qualidade e % Vazios',
            xaxis_title='Semana Letiva',
            yaxis=dict(title='Score Médio', range=[0, 100]),
            yaxis2=dict(title='% Vazios', overlaying='y', side='right', range=[0, 100]),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
