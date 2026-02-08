#!/usr/bin/env python3
"""
PÁGINA 3: ESTRUTURA CURRICULAR
Carga horária por série (padrão para todas as unidades)
Divergências entre unidades
Total de aulas por unidade (considera quantidade de turmas)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_SERIES, CORES_UNIDADES, ORDEM_SERIES
from utils import carregar_horario_esperado, SERIES_FUND_II, SERIES_EM

st.set_page_config(page_title="Estrutura Curricular", page_icon="📚", layout="wide")
from auth import check_password, logout_button
if not check_password():
    st.stop()
logout_button()

st.markdown("""
<style>
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .warning-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

def carregar_grade():
    df = carregar_horario_esperado()
    return df if not df.empty else None

def main():
    st.title("📚 Estrutura Curricular")
    st.markdown("**Carga horária por série, divergências entre unidades, total de aulas**")

    df = carregar_grade()

    if df is None:
        st.error("Arquivo de grade horária não encontrado.")
        return

    # ========== QUANTIDADE DE TURMAS ==========
    st.markdown("---")
    st.header("🏫 1. Quantidade de Turmas por Unidade")

    st.markdown("""
    <div class="info-box">
        Cada unidade tem uma quantidade diferente de turmas.
        Isso explica por que o <strong>total de aulas</strong> varia entre unidades,
        mesmo que a <strong>carga horária por turma</strong> seja igual.
    </div>
    """, unsafe_allow_html=True)

    # Conta turmas por unidade e série
    turmas = df.groupby(['unidade', 'serie'])['turma'].nunique().reset_index()
    turmas_pivot = turmas.pivot(index='serie', columns='unidade', values='turma').fillna(0).astype(int)

    # Adiciona total
    turmas_pivot['TOTAL'] = turmas_pivot.sum(axis=1)
    turmas_pivot.loc['TOTAL'] = turmas_pivot.sum()

    st.dataframe(turmas_pivot, use_container_width=True)

    # Gráfico por unidade
    turmas_total = df.groupby('unidade')['turma'].nunique().reset_index()
    turmas_total.columns = ['Unidade', 'Turmas']
    fig = px.bar(turmas_total, x='Unidade', y='Turmas',
                title='Total de Turmas por Unidade (Fund II + EM)',
                color='Unidade', text='Turmas',
                color_discrete_map=CORES_UNIDADES)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    # Gráfico por série com cores corretas
    turmas_serie = df.groupby('serie')['turma'].nunique().reset_index()
    turmas_serie.columns = ['Série', 'Turmas']
    # Ordena as séries
    turmas_serie['ordem'] = turmas_serie['Série'].apply(lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99)
    turmas_serie = turmas_serie.sort_values('ordem')

    fig2 = px.bar(turmas_serie, x='Série', y='Turmas',
                 title='Total de Turmas por Série',
                 color='Série', text='Turmas',
                 color_discrete_map=CORES_SERIES)
    fig2.update_traces(textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

    # ========== CARGA HORÁRIA POR SÉRIE ==========
    st.markdown("---")
    st.header("📋 2. Carga Horária por Série (aulas/semana por turma)")

    st.markdown("""
    <div class="info-box">
        Esta é a grade padrão de cada série. Uma turma de 6º ano, por exemplo,
        tem a mesma quantidade de aulas em TODAS as unidades.
    </div>
    """, unsafe_allow_html=True)

    # Seletor de série
    series_disp = sorted(df['serie'].unique(), key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99)
    serie_sel = st.selectbox("Selecione a série:", series_disp)

    # Calcula aulas por turma (média, que deve ser igual)
    aulas_turma = df.groupby(['unidade', 'serie', 'turma', 'disciplina']).size().reset_index(name='aulas')
    media_serie = aulas_turma.groupby(['unidade', 'serie', 'disciplina'])['aulas'].mean().reset_index()

    # Filtra série selecionada
    df_serie = media_serie[media_serie['serie'] == serie_sel]

    # Pivot para comparar unidades
    pivot_serie = df_serie.pivot(index='disciplina', columns='unidade', values='aulas').fillna(0)

    # Verifica divergências
    def check_divergencia(row):
        valores = row[row > 0].unique()
        return '⚠️' if len(valores) > 1 else '✅'

    pivot_serie['Status'] = pivot_serie.apply(check_divergencia, axis=1)

    # Adiciona total
    pivot_serie['Aulas/Semana'] = pivot_serie[['BV', 'CD', 'CDR', 'JG']].max(axis=1).astype(int)

    # Ordena por aulas
    pivot_serie = pivot_serie.sort_values('Aulas/Semana', ascending=False)

    # Mostra tabela
    st.subheader(f"Grade do {serie_sel}")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.dataframe(pivot_serie, use_container_width=True)

    with col2:
        total_aulas = pivot_serie['Aulas/Semana'].sum()
        divergencias = (pivot_serie['Status'] == '⚠️').sum()

        st.metric("Total Aulas/Semana", int(total_aulas))
        st.metric("Disciplinas", len(pivot_serie))

        if divergencias > 0:
            st.metric("⚠️ Divergências", divergencias)
        else:
            st.success("✅ Sem divergências")

    # ========== DIVERGÊNCIAS ==========
    st.markdown("---")
    st.header("⚠️ 3. Divergências Entre Unidades")

    st.markdown("""
    <div class="warning-box">
        Divergência = mesma série/disciplina com carga horária DIFERENTE entre unidades.
        Isso pode indicar erro na grade ou particularidade de alguma unidade.
    </div>
    """, unsafe_allow_html=True)

    # Calcula todas as divergências
    todas_divergencias = []

    for serie in df['serie'].unique():
        df_s = media_serie[media_serie['serie'] == serie]
        pivot_s = df_s.pivot(index='disciplina', columns='unidade', values='aulas').fillna(0)

        for disc in pivot_s.index:
            row = pivot_s.loc[disc]
            valores = row[row > 0]
            if len(valores.unique()) > 1:
                todas_divergencias.append({
                    'Série': serie,
                    'Disciplina': disc,
                    'BV': int(row.get('BV', 0)),
                    'CD': int(row.get('CD', 0)),
                    'CDR': int(row.get('CDR', 0)),
                    'JG': int(row.get('JG', 0)),
                    'Observação': 'Verificar grade'
                })

    if todas_divergencias:
        df_div = pd.DataFrame(todas_divergencias)
        st.warning(f"Encontradas {len(df_div)} divergências:")
        st.dataframe(df_div, use_container_width=True, hide_index=True)

        # Download
        csv = df_div.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Exportar Divergências", csv, "divergencias_grade.csv")
    else:
        st.markdown("""
        <div class="success-box">
            ✅ <strong>Nenhuma divergência encontrada!</strong><br>
            Todas as séries têm a mesma carga horária em todas as unidades.
        </div>
        """, unsafe_allow_html=True)

    # ========== TOTAL POR UNIDADE ==========
    st.markdown("---")
    st.header("📊 4. Total de Aulas por Unidade")

    st.markdown("""
    <div class="info-box">
        O total de aulas varia porque cada unidade tem quantidade diferente de turmas.
        <strong>Não significa que a grade é diferente</strong>, apenas que há mais/menos turmas.
    </div>
    """, unsafe_allow_html=True)

    # Calcula totais
    totais = df.groupby('unidade').agg({
        'turma': 'nunique',
        'professor': 'nunique',
        'disciplina': 'nunique'
    }).reset_index()
    totais['aulas_semana'] = df.groupby('unidade').size().values
    totais.columns = ['Unidade', 'Turmas', 'Professores', 'Disciplinas', 'Aulas/Semana']

    # Adiciona aulas por turma (para mostrar que é proporcional)
    totais['Média Aulas/Turma'] = (totais['Aulas/Semana'] / totais['Turmas']).round(1)

    st.dataframe(totais, use_container_width=True, hide_index=True)

    # Gráfico comparativo
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Aulas/Semana', x=totais['Unidade'], y=totais['Aulas/Semana'],
                        text=totais['Aulas/Semana'], textposition='outside'))
    fig.add_trace(go.Bar(name='Turmas x10', x=totais['Unidade'], y=totais['Turmas']*10,
                        text=totais['Turmas'], textposition='outside'))
    fig.update_layout(title='Relação Turmas vs Aulas (aulas são proporcionais às turmas)',
                     barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    # ========== RESUMO POR SEGMENTO ==========
    st.markdown("---")
    st.header("📚 5. Resumo por Segmento")

    tab1, tab2 = st.tabs(["Anos Finais (6º ao 9º)", "Ensino Médio (1ª a 3ª)"])

    with tab1:
        st.subheader("Grade Padrão - Anos Finais")

        # Pega grade do 6º ano como referência (de BV)
        ref_fund = media_serie[(media_serie['unidade'] == 'BV') &
                               (media_serie['serie'].isin(SERIES_FUND_II))]

        # Agrupa por disciplina (pega a média entre séries)
        resumo_fund = ref_fund.groupby('disciplina')['aulas'].mean().reset_index()
        resumo_fund.columns = ['Componente', 'Aulas/Semana']
        resumo_fund['Aulas/Semana'] = resumo_fund['Aulas/Semana'].round(0).astype(int)
        resumo_fund = resumo_fund.sort_values('Aulas/Semana', ascending=False)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.dataframe(resumo_fund, use_container_width=True, hide_index=True)

        with col2:
            st.metric("Total Médio/Semana", resumo_fund['Aulas/Semana'].sum())
            st.info("*Média das séries 6º ao 9º ano")

    with tab2:
        st.subheader("Grade Padrão - Ensino Médio")

        ref_em = media_serie[(media_serie['unidade'] == 'BV') &
                             (media_serie['serie'].isin(SERIES_EM))]

        resumo_em = ref_em.groupby('disciplina')['aulas'].mean().reset_index()
        resumo_em.columns = ['Componente', 'Aulas/Semana']
        resumo_em['Aulas/Semana'] = resumo_em['Aulas/Semana'].round(0).astype(int)
        resumo_em = resumo_em.sort_values('Aulas/Semana', ascending=False)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.dataframe(resumo_em, use_container_width=True, hide_index=True)

        with col2:
            st.metric("Total Médio/Semana", resumo_em['Aulas/Semana'].sum())
            st.info("*Média das séries 1ª a 3ª EM")

    # ========== TEMPO POR CAPÍTULO ==========
    st.markdown("---")
    st.header("⏱️ 6. Tempo por Capítulo SAE")

    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ ATENÇÃO:</strong> O tempo por capítulo é DIFERENTE entre Anos Finais e Ensino Médio
        porque a carga horária e a estrutura do material são diferentes.
    </div>
    """, unsafe_allow_html=True)

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.subheader("📘 Anos Finais (6º ao 9º)")
        st.markdown("**Material:** Livro Integrado SAE (4 volumes, 3 caps cada)")

        tempo_fund = pd.DataFrame({
            'Componente': ['Língua Portuguesa', 'Matemática', 'Ciências/História/Geografia',
                          'Inglês', 'Redação', 'Arte/Filosofia', 'Ed. Física'],
            'Aulas/Sem': [4, 4, '2-3', 2, 2, 1, 1],
            'Aulas/Cap (2 sem)': ['8', '8', '4-6', '4', '4', '2', '2'],
            'Ritmo Sugerido': [
                '2 aulas por seção',
                '2 aulas por seção',
                '1-2 aulas por seção',
                '1 aula por seção',
                '1 aula por seção',
                'Flexível (projeto)',
                'Por habilidade'
            ]
        })
        st.dataframe(tempo_fund, use_container_width=True, hide_index=True)

    with col_t2:
        st.subheader("📗 Ensino Médio (1ª a 3ª)")
        st.markdown("**Material:** Conexões & Contextos (por área de conhecimento)")

        tempo_em = pd.DataFrame({
            'Componente': ['Português/Literatura', 'Matemática 1+2', 'Física/Química/Biologia',
                          'História/Geografia', 'Redação', 'Filosofia/Sociologia', 'Inglês'],
            'Aulas/Sem': ['4', '4', '2 cada', '2 cada', '2', '1 cada', '1'],
            'Aulas/Cap (2 sem)': ['8', '8', '4 cada', '4 cada', '4', '2 cada', '2'],
            'Ritmo Sugerido': [
                '2 aulas por seção',
                '2 aulas por seção',
                '1 aula por seção',
                '1 aula por seção',
                '1 aula por seção',
                'Flexível',
                '1 aula por seção'
            ]
        })
        st.dataframe(tempo_em, use_container_width=True, hide_index=True)

    st.info("""
    **📌 Diferenças importantes:**
    - **Anos Finais**: Livro Integrado com 12 capítulos = ~2 semanas por capítulo
    - **Ensino Médio**: Organizado por área, foco em preparação vestibular, ritmo pode variar
    - **9º Ano**: Transição - já tem Química, Física e Biologia separadas
    """)

if __name__ == "__main__":
    main()
