#!/usr/bin/env python3
"""
PAGINA 24: CRUZAMENTO SIGA x SAE DIGITAL
Compara o registro do professor (SIGA) com a atividade dos alunos (SAE Digital).
4 abas: Visao Geral, Gap Professor x Alunos, Engajamento por Capitulo, Alertas.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_SERIES, CORES_UNIDADES, ORDEM_SERIES
from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    carregar_cruzamento, carregar_materiais_sae, carregar_alunos_sae,
    carregar_engajamento_sae, carregar_fato_aulas, normalizar_disciplina_sae,
    normalizar_serie_sae, _hoje,
    DATA_DIR, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM, PERIODOS_OPCOES,
)

from auth import get_user_unit

# CSS
st.markdown("""
<style>
    .card-alinhado {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white; padding: 18px; border-radius: 10px; text-align: center; margin: 5px 0;
    }
    .card-atencao {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
        color: white; padding: 18px; border-radius: 10px; text-align: center; margin: 5px 0;
    }
    .card-gap {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white; padding: 18px; border-radius: 10px; text-align: center; margin: 5px 0;
    }
    .card-cinza {
        background: linear-gradient(135deg, #8e9eab 0%, #eef2f3 100%);
        color: #333; padding: 18px; border-radius: 10px; text-align: center; margin: 5px 0;
    }
    .alerta-cruzamento {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 4px;
    }
    .alerta-critico {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Mapa de status para cores do semaforo
STATUS_CORES = {
    "Alinhado": "#43A047",
    "Alinhado, Baixo Engajamento": "#FFA726",
    "Professor Adiantado": "#29B6F6",
    "Professor Atrasado": "#EF5350",
    "Baixo Engajamento": "#FF7043",
    "Alunos Ativos, Professor N/D": "#AB47BC",
    "Sem SAE": "#9E9E9E",
    "Sem Dados": "#BDBDBD",
    "Dados Insuficientes": "#E0E0E0",
    "Em Analise": "#78909C",
}


def main():
    st.title("\U0001f517 Cruzamento SIGA x SAE Digital")
    st.markdown("**Professor registrou no SIGA? Aluno fez na plataforma SAE?**")

    # Carregar dados
    df_cruz = carregar_cruzamento()
    df_materiais = carregar_materiais_sae()
    df_alunos_sae = carregar_alunos_sae()
    df_engajamento = carregar_engajamento_sae()

    if df_cruz.empty:
        st.warning(
            "Dados de cruzamento nao encontrados. "
            "Execute `python extrair_sae_digital.py` para gerar os dados."
        )
        mostrar_diagnostico(df_materiais, df_alunos_sae, df_engajamento)
        return

    # Contexto
    semana = calcular_semana_letiva()
    capitulo = calcular_capitulo_esperado(semana)
    trimestre = calcular_trimestre(semana)

    # ========== FILTROS ==========
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        unidades = ['TODAS'] + sorted(df_cruz['unidade'].dropna().unique().tolist())
        user_unit = get_user_unit()
        default_un = unidades.index(user_unit) if user_unit and user_unit in unidades else 0
        filtro_un = st.selectbox("\U0001f3eb Unidade", unidades, index=default_un, key="cruz_un")

    with col_f2:
        segmentos = ['TODOS', 'Anos Finais', 'Ensino M\u00e9dio']
        filtro_seg = st.selectbox("\U0001f4da Segmento", segmentos, key="cruz_seg")

    with col_f3:
        series_disp = ['TODAS'] + sorted(
            df_cruz['serie'].dropna().unique().tolist(),
            key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99
        )
        filtro_serie = st.selectbox("\U0001f393 S\u00e9rie", series_disp, key="cruz_serie")

    # Aplicar filtros
    df = df_cruz.copy()
    if filtro_un != 'TODAS':
        df = df[df['unidade'] == filtro_un]
    if filtro_seg == 'Anos Finais':
        df = df[df['serie'].isin(SERIES_FUND_II)]
    elif filtro_seg == 'Ensino M\u00e9dio':
        df = df[df['serie'].isin(SERIES_EM)]
    if filtro_serie != 'TODAS':
        df = df[df['serie'] == filtro_serie]

    if df.empty:
        st.info("Nenhum dado para os filtros selecionados.")
        return

    # ========== ABAS ==========
    tab1, tab2, tab3, tab4 = st.tabs([
        "\U0001f4ca Vis\u00e3o Geral",
        "\U0001f4cf Gap Professor x Alunos",
        "\U0001f4d6 Engajamento por Cap\u00edtulo",
        "\U0001f6a8 Alertas de Cruzamento",
    ])

    with tab1:
        render_visao_geral(df, semana, capitulo, trimestre)
    with tab2:
        render_gap(df)
    with tab3:
        render_engajamento(df, df_engajamento)
    with tab4:
        render_alertas(df)


# ========== ABA 1: VISAO GERAL ==========

def render_visao_geral(df, semana, capitulo, trimestre):
    st.header("\U0001f4ca Vis\u00e3o Geral do Cruzamento")

    # Cards resumo
    total = len(df)
    alinhados = len(df[df['status'].isin(['Alinhado', 'Alinhado, Baixo Engajamento'])])
    com_gap = len(df[df['status'].isin(['Professor Adiantado', 'Professor Atrasado'])])
    sem_sae = len(df[df['status'].isin(['Sem SAE', 'Sem Dados', 'Dados Insuficientes'])])
    baixo_eng = len(df[df['status'].str.contains('Baixo Engajamento', na=False)])

    pct_alinhado = (alinhados / total * 100) if total > 0 else 0
    pct_gap = (com_gap / total * 100) if total > 0 else 0
    pct_sem = (sem_sae / total * 100) if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="card-alinhado">
            <h1 style="margin:0; font-size: 2.5em;">{pct_alinhado:.0f}%</h1>
            <p style="margin:0;">Alinhados ({alinhados})</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card-gap">
            <h1 style="margin:0; font-size: 2.5em;">{pct_gap:.0f}%</h1>
            <p style="margin:0;">Com Gap ({com_gap})</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card-atencao">
            <h1 style="margin:0; font-size: 2.5em;">{baixo_eng}</h1>
            <p style="margin:0;">Baixo Engajamento</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="card-cinza">
            <h1 style="margin:0; font-size: 2.5em;">{pct_sem:.0f}%</h1>
            <p style="margin:0;">Sem Dados SAE ({sem_sae})</p>
        </div>
        """, unsafe_allow_html=True)

    # Contexto
    st.markdown(f"**Semana {semana} | Cap\u00edtulo esperado: {capitulo}/12 | {trimestre}\u00ba Trimestre**")

    # Matriz semaforo: Serie x Disciplina
    st.subheader("\U0001f6a6 Sem\u00e1foro: S\u00e9rie x Disciplina")

    # Pivotar para heatmap
    df_pivot = df.groupby(['serie', 'disciplina']).agg(
        status_principal=('status', lambda x: x.mode().iloc[0] if len(x) > 0 else 'Sem Dados'),
        pct_eng=('pct_engajamento', 'mean'),
    ).reset_index()

    series_order = [s for s in ORDEM_SERIES if s in df_pivot['serie'].unique()]
    disciplinas = sorted(df_pivot['disciplina'].unique())

    if not series_order or not disciplinas:
        st.info("Dados insuficientes para o sem\u00e1foro.")
        return

    # Criar matriz numerica para heatmap
    status_to_num = {
        "Alinhado": 4,
        "Alinhado, Baixo Engajamento": 3,
        "Professor Adiantado": 2,
        "Em Analise": 2,
        "Professor Atrasado": 1,
        "Baixo Engajamento": 1,
        "Alunos Ativos, Professor N/D": 2,
        "Sem SAE": 0,
        "Sem Dados": 0,
        "Dados Insuficientes": 0,
    }

    matrix = []
    text_matrix = []
    for serie in series_order:
        row = []
        text_row = []
        for disc in disciplinas:
            match = df_pivot[(df_pivot['serie'] == serie) & (df_pivot['disciplina'] == disc)]
            if match.empty:
                row.append(-1)
                text_row.append("N/A")
            else:
                st_val = match.iloc[0]['status_principal']
                row.append(status_to_num.get(st_val, 0))
                text_row.append(st_val)
        matrix.append(row)
        text_matrix.append(text_row)

    colorscale = [
        [0.0, "#E0E0E0"],    # Cinza (sem dados / N/A)
        [0.25, "#EF5350"],    # Vermelho (gap/atrasado)
        [0.5, "#FFA726"],     # Amarelo (atencao)
        [0.75, "#29B6F6"],    # Azul (adiantado/analise)
        [1.0, "#43A047"],     # Verde (alinhado)
    ]

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=disciplinas,
        y=series_order,
        text=text_matrix,
        texttemplate="%{text}",
        textfont={"size": 9},
        colorscale=colorscale,
        zmin=-1,
        zmax=4,
        showscale=False,
    ))
    fig.update_layout(
        height=50 + 45 * len(series_order),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(side="top", tickangle=-45),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Distribuicao de status
    st.subheader("\U0001f4ca Distribui\u00e7\u00e3o de Status")
    df_status = df['status'].value_counts().reset_index()
    df_status.columns = ['Status', 'Quantidade']
    fig = px.pie(
        df_status, values='Quantidade', names='Status',
        color='Status',
        color_discrete_map=STATUS_CORES,
    )
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)


# ========== ABA 2: GAP PROFESSOR x ALUNOS ==========

def render_gap(df):
    st.header("\U0001f4cf Gap: Cap\u00edtulo do Professor vs Alunos")

    df_gap = df[df['cap_professor'].notna() & df['cap_alunos_mediana'].notna()].copy()

    if df_gap.empty:
        st.info(
            "Nenhum dado com capitulo detectado tanto do professor (SIGA) quanto dos alunos (SAE). "
            "Isso pode ocorrer se o professor nao mencionou numeros de capitulo no conteudo registrado, "
            "ou se nao ha dados de engajamento per-student."
        )

        # Mostrar dados parciais
        df_partial = df[df['cap_professor'].notna()].copy()
        if not df_partial.empty:
            st.subheader("Professores com cap\u00edtulo detectado (sem dados SAE)")
            cols_show = ['unidade', 'serie', 'disciplina', 'professor', 'cap_professor', 'cap_esperado', 'status']
            cols_show = [c for c in cols_show if c in df_partial.columns]
            st.dataframe(df_partial[cols_show].head(30), use_container_width=True, hide_index=True)
        return

    # Scatter: Cap professor (X) vs Cap alunos (Y)
    st.subheader("Cap\u00edtulo Professor vs Cap\u00edtulo Alunos")
    st.markdown("*Pontos sobre a diagonal = alinhamento perfeito*")

    fig = px.scatter(
        df_gap,
        x='cap_professor',
        y='cap_alunos_mediana',
        color='serie',
        color_discrete_map=CORES_SERIES,
        hover_data=['disciplina', 'professor', 'unidade', 'pct_engajamento'],
        labels={
            'cap_professor': 'Cap\u00edtulo Professor (SIGA)',
            'cap_alunos_mediana': 'Cap\u00edtulo Alunos (SAE)',
        },
    )
    # Diagonal de alinhamento
    fig.add_shape(
        type="line", x0=0, y0=0, x1=12, y1=12,
        line=dict(color="gray", width=1, dash="dash"),
    )
    fig.update_layout(
        height=500,
        xaxis=dict(range=[0, 13], dtick=1),
        yaxis=dict(range=[0, 13], dtick=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de gap por disciplina
    st.subheader("Detalhamento do Gap por Disciplina")
    df_gap_agg = df_gap.groupby(['serie', 'disciplina']).agg(
        cap_prof_medio=('cap_professor', 'mean'),
        cap_alunos_medio=('cap_alunos_mediana', 'mean'),
        gap_medio=('gap_prof_alunos', 'mean'),
        registros=('status', 'count'),
    ).reset_index()
    df_gap_agg['cap_prof_medio'] = df_gap_agg['cap_prof_medio'].round(1)
    df_gap_agg['cap_alunos_medio'] = df_gap_agg['cap_alunos_medio'].round(1)
    df_gap_agg['gap_medio'] = df_gap_agg['gap_medio'].round(1)
    df_gap_agg = df_gap_agg.sort_values('gap_medio', ascending=False)

    st.dataframe(df_gap_agg, use_container_width=True, hide_index=True)


# ========== ABA 3: ENGAJAMENTO POR CAPITULO ==========

def render_engajamento(df, df_engajamento):
    st.header("\U0001f4d6 Engajamento por Cap\u00edtulo")

    if df_engajamento.empty:
        st.info(
            "Dados de engajamento por capitulo nao disponiveis. "
            "Isso pode ocorrer se o endpoint de progresso por aluno nao estiver ativo no SAE."
        )
        # Mostrar engajamento agregado do cruzamento
        if 'pct_engajamento' in df.columns and df['pct_engajamento'].notna().any():
            st.subheader("Engajamento Agregado por S\u00e9rie")
            df_eng_agg = df.groupby('serie').agg(
                engajamento_medio=('pct_engajamento', 'mean'),
                registros=('status', 'count'),
            ).reset_index()
            df_eng_agg['engajamento_medio'] = df_eng_agg['engajamento_medio'].round(1)
            fig = px.bar(
                df_eng_agg, x='serie', y='engajamento_medio',
                color='serie', color_discrete_map=CORES_SERIES,
                labels={'engajamento_medio': 'Engajamento M\u00e9dio (%)', 'serie': 'S\u00e9rie'},
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        return

    # Filtrar engajamento com capitulos validos
    df_eng = df_engajamento[df_engajamento['capitulo'] > 0].copy()

    if df_eng.empty:
        st.info("Dados de engajamento sem detalhamento por capitulo.")
        return

    # Filtro de disciplina
    disciplinas = sorted(df_eng['disciplina'].dropna().unique())
    filtro_disc = st.selectbox("\U0001f4da Disciplina", ['TODAS'] + disciplinas, key="eng_disc")
    if filtro_disc != 'TODAS':
        df_eng = df_eng[df_eng['disciplina'] == filtro_disc]

    # Barras empilhadas: % alunos por capitulo
    st.subheader("Progresso de Exerc\u00edcios por Cap\u00edtulo")

    df_cap = df_eng.groupby(['serie', 'capitulo']).agg(
        pct_medio=('pct_exercicios', 'mean'),
    ).reset_index()

    fig = px.bar(
        df_cap, x='capitulo', y='pct_medio', color='serie',
        barmode='group',
        color_discrete_map=CORES_SERIES,
        labels={'capitulo': 'Cap\u00edtulo', 'pct_medio': 'Exerc\u00edcios (%)'},
    )
    fig.update_layout(
        height=450,
        xaxis=dict(dtick=1, range=[0.5, 12.5]),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap: Serie x Capitulo
    st.subheader("Heatmap: S\u00e9rie x Cap\u00edtulo")

    series_order = [s for s in ORDEM_SERIES if s in df_cap['serie'].unique()]
    capitulos = list(range(1, 13))

    matrix = []
    for serie in series_order:
        row = []
        for cap in capitulos:
            match = df_cap[(df_cap['serie'] == serie) & (df_cap['capitulo'] == cap)]
            if match.empty:
                row.append(0)
            else:
                row.append(round(match.iloc[0]['pct_medio'], 1))
        matrix.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=[f"Cap {c}" for c in capitulos],
        y=series_order,
        text=[[f"{v:.0f}%" for v in row] for row in matrix],
        texttemplate="%{text}",
        colorscale="YlGn",
        zmin=0,
        zmax=100,
    ))
    fig.update_layout(
        height=50 + 45 * len(series_order),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(side="top"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ========== ABA 4: ALERTAS DE CRUZAMENTO ==========

def render_alertas(df):
    st.header("\U0001f6a8 Alertas de Cruzamento")

    alertas = []

    # Alerta 1: Professor diz cap X, mas 0 alunos fizeram exercicios do cap X
    df_prof_sem_aluno = df[
        (df['cap_professor'].notna()) &
        (df['cap_professor'] > 0) &
        ((df['pct_engajamento'].isna()) | (df['pct_engajamento'] < 5))
    ]
    for _, row in df_prof_sem_aluno.iterrows():
        alertas.append({
            'tipo': 'critico',
            'categoria': 'Professor sem Alunos',
            'msg': f"{row['professor']} registrou cap. {int(row['cap_professor'])} em {row['disciplina']} ({row['serie']}), "
                   f"mas engajamento SAE < 5%",
            'unidade': row['unidade'],
            'serie': row['serie'],
        })

    # Alerta 2: Professor atrasado E alunos sem atividade (risco duplo)
    df_risco_duplo = df[
        (df['status'] == 'Professor Atrasado') &
        ((df['pct_engajamento'].isna()) | (df['pct_engajamento'] < 20))
    ]
    for _, row in df_risco_duplo.iterrows():
        alertas.append({
            'tipo': 'critico',
            'categoria': 'Risco Duplo',
            'msg': f"RISCO DUPLO: {row['professor']} atrasado em {row['disciplina']} ({row['serie']}) "
                   f"E alunos com baixo engajamento SAE",
            'unidade': row['unidade'],
            'serie': row['serie'],
        })

    # Alerta 3: Alto engajamento mas professor sem registro
    df_alunos_sem_prof = df[
        (df['pct_engajamento'].notna()) &
        (df['pct_engajamento'] > 50) &
        (df['cap_professor'].isna())
    ]
    for _, row in df_alunos_sem_prof.iterrows():
        alertas.append({
            'tipo': 'atencao',
            'categoria': 'Alunos sem Professor',
            'msg': f"Alunos com {row['pct_engajamento']:.0f}% engajamento em {row['disciplina']} ({row['serie']}), "
                   f"mas professor sem capitulo registrado no SIGA",
            'unidade': row['unidade'],
            'serie': row['serie'],
        })

    # Alerta 4: Disciplinas SAE sem nenhum dado de cruzamento
    disc_sem_dados = df[df['status'].isin(['Sem SAE', 'Sem Dados'])].groupby(['serie', 'disciplina']).size()
    if not disc_sem_dados.empty:
        for (serie, disc), count in disc_sem_dados.items():
            alertas.append({
                'tipo': 'info',
                'categoria': 'Sem Dados SAE',
                'msg': f"{disc} ({serie}): {count} registros sem dados SAE",
                'unidade': '',
                'serie': serie,
            })

    # Exibir alertas
    if not alertas:
        st.success("Nenhum alerta de cruzamento ativo!")
        return

    # Resumo
    criticos = sum(1 for a in alertas if a['tipo'] == 'critico')
    atencao = sum(1 for a in alertas if a['tipo'] == 'atencao')
    info = sum(1 for a in alertas if a['tipo'] == 'info')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("\U0001f534 Cr\u00edticos", criticos)
    with col2:
        st.metric("\U0001f7e1 Aten\u00e7\u00e3o", atencao)
    with col3:
        st.metric("\U0001f535 Informativos", info)

    st.markdown("---")

    # Criticos primeiro
    for alerta in sorted(alertas, key=lambda a: {'critico': 0, 'atencao': 1, 'info': 2}.get(a['tipo'], 3)):
        if alerta['tipo'] == 'critico':
            st.markdown(f"""
            <div class="alerta-critico">
                <strong>\U0001f534 {alerta['categoria']}</strong><br>
                {alerta['msg']}
            </div>
            """, unsafe_allow_html=True)
        elif alerta['tipo'] == 'atencao':
            st.markdown(f"""
            <div class="alerta-cruzamento">
                <strong>\U0001f7e1 {alerta['categoria']}</strong><br>
                {alerta['msg']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(f"**{alerta['categoria']}**: {alerta['msg']}")

    # Tabela completa
    st.markdown("---")
    st.subheader("\U0001f4cb Tabela Completa de Alertas")
    df_alertas = pd.DataFrame(alertas)
    st.dataframe(df_alertas, use_container_width=True, hide_index=True)


# ========== DIAGNOSTICO (quando nao tem dados) ==========

def mostrar_diagnostico(df_materiais, df_alunos_sae, df_engajamento):
    """Mostra status dos CSVs SAE para diagnostico."""
    st.markdown("---")
    st.subheader("\U0001f50d Diagn\u00f3stico dos Dados SAE")

    col1, col2, col3 = st.columns(3)

    with col1:
        n = len(df_materiais) if not df_materiais.empty else 0
        icon = "\u2705" if n > 0 else "\u274c"
        st.metric(f"{icon} Materiais SAE", f"{n} registros")

    with col2:
        n = len(df_alunos_sae) if not df_alunos_sae.empty else 0
        icon = "\u2705" if n > 0 else "\u274c"
        st.metric(f"{icon} Alunos SAE", f"{n} registros")

    with col3:
        n = len(df_engajamento) if not df_engajamento.empty else 0
        icon = "\u2705" if n > 0 else "\u274c"
        st.metric(f"{icon} Engajamento SAE", f"{n} registros")

    st.markdown("""
    **Para gerar os dados, execute no terminal:**
    ```bash
    cd siga_extrator
    python extrair_sae_digital.py
    ```
    """)


main()
