#!/usr/bin/env python3
"""
PÁGINA 5: PROGRESSÃO SAE
Ritmo esperado, capítulos por semana, onde está vs onde deveria
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import math
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import calcular_semana_letiva, calcular_capitulo_esperado, carregar_fato_aulas, DATA_DIR

st.set_page_config(page_title="Progressao SAE", page_icon="📈", layout="wide")
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
    .formula-box {
        background: #f3e5f5;
        border-left: 4px solid #9c27b0;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
        font-family: monospace;
    }
    .status-adiantado { color: #4caf50; font-weight: bold; }
    .status-no-ritmo { color: #2196f3; font-weight: bold; }
    .status-atrasado { color: #f44336; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("📈 Progressão SAE")
    st.markdown("**Ritmo esperado vs realizado | Capítulos por semana**")

    semana_atual = calcular_semana_letiva()
    cap_esperado = calcular_capitulo_esperado(semana_atual)

    # ========== FÓRMULA E STATUS ATUAL ==========
    st.markdown("---")
    st.header("🎯 Status Atual da Progressão")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📅 Semana Letiva Atual", f"{semana_atual}ª")

    with col2:
        st.metric("📖 Capítulo Esperado", f"{cap_esperado}")

    with col3:
        trimestre = 1 if semana_atual <= 14 else (2 if semana_atual <= 28 else 3)
        st.metric("📊 Trimestre", f"{trimestre}º")

    st.markdown("""
    <div class="formula-box">
        <strong>📐 FÓRMULA DE PROGRESSÃO:</strong><br><br>
        <code>Capítulo = ⌈ Semana Letiva ÷ 3.5 ⌉</code><br><br>
        <strong>Tradução:</strong> 42 semanas ÷ 12 capítulos = <strong>3,5 semanas por capítulo</strong><br><br>
        ✅ Aplica-se a TODAS as turmas (Anos Finais e Ensino Médio)<br>
        ✅ O que muda é a profundidade: disciplinas com mais aulas exploram mais o capítulo
    </div>
    """, unsafe_allow_html=True)

    # ========== TABELA DE RITMO ==========
    st.markdown("---")
    st.header("📋 Ritmo Esperado - 1º Trimestre")

    st.markdown("""
    <div class="info-box">
        Esta tabela mostra onde cada turma deveria estar em cada semana.
        Use para comparar com os registros reais do SIGA.
    </div>
    """, unsafe_allow_html=True)

    # Tabela completa do 1º trimestre (4 capítulos)
    ritmo_1tri = pd.DataFrame({
        'Semana': list(range(1, 15)),
        'Data Início': [
            '26/01', '02/02', '09/02', '16/02', '23/02', '02/03', '09/03',
            '16/03', '23/03', '30/03', '06/04', '13/04', '20/04', '27/04'
        ],
        'Capítulo Esperado': [1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4],
        'Status': [
            'Adaptação/Início Cap 1',
            'Desenvolvimento Cap 1',
            'Conclusão Cap 1 (Elo Folia)',
            'Pós-Carnaval - Início Cap 2',
            'Desenvolvimento Cap 2',
            'Desenvolvimento Cap 2',
            'Conclusão Cap 2 + Avaliações A1',
            'Início Cap 3 + Avaliações A1',
            'Desenvolvimento Cap 3',
            'Conclusão Cap 3',
            'Início Cap 4 + Avaliações A2',
            'Desenvolvimento Cap 4 + A2',
            'Desenvolvimento Cap 4',
            'Conclusão Cap 4 + Recuperação'
        ],
        'Evento': [
            'Semana de Adaptação',
            'Início conteúdo regular',
            'Elo Folia (até 13/fev)',
            'Carnaval (14-17/fev)',
            '-',
            'Data Magna PE (06/03)',
            'Avaliações A1',
            'Avaliações A1',
            '-',
            'Semana Santa (02-03/04)',
            'Avaliações A2',
            'Feriado Jaboatão CD (13/04)',
            'Tiradentes (21/04)',
            'Recuperação + Fechamento'
        ]
    })

    # Destaca a semana atual
    ritmo_1tri['Atual'] = ritmo_1tri['Semana'].apply(
        lambda x: '👉' if x == semana_atual else ''
    )

    st.dataframe(ritmo_1tri, use_container_width=True, hide_index=True)

    # ========== GRÁFICO DE PROGRESSÃO ==========
    st.markdown("---")
    st.header("📊 Curva de Progressão SAE 2026")

    semanas = list(range(1, 43))
    capitulos = [min(12, math.ceil(s / 3.5)) for s in semanas]

    fig = go.Figure()

    # Linha de progressão esperada
    fig.add_trace(go.Scatter(
        x=semanas, y=capitulos,
        mode='lines+markers',
        name='Capítulo Esperado',
        line=dict(color='#2196f3', width=3),
        marker=dict(size=8)
    ))

    # Marca posição atual
    fig.add_vline(x=semana_atual, line_dash="dash", line_color="red",
                 annotation_text=f"Semana {semana_atual}")
    fig.add_hline(y=cap_esperado, line_dash="dash", line_color="green",
                 annotation_text=f"Cap. {cap_esperado}")

    # Zonas de trimestre
    fig.add_vrect(x0=1, x1=14, fillcolor="blue", opacity=0.1,
                 annotation_text="1º Tri", annotation_position="top left")
    fig.add_vrect(x0=15, x1=28, fillcolor="green", opacity=0.1,
                 annotation_text="2º Tri", annotation_position="top left")
    fig.add_vrect(x0=29, x1=42, fillcolor="orange", opacity=0.1,
                 annotation_text="3º Tri", annotation_position="top left")

    fig.update_layout(
        title="Progressão de Capítulos ao Longo do Ano",
        xaxis_title="Semana Letiva",
        yaxis_title="Capítulo SAE",
        yaxis=dict(tickmode='linear', tick0=1, dtick=1, range=[0, 13]),
        xaxis=dict(tickmode='linear', tick0=1, dtick=2),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # ========== METAS POR TRIMESTRE ==========
    st.markdown("---")
    st.header("🎯 Metas por Trimestre")

    metas = pd.DataFrame({
        'Trimestre': ['1º Trimestre', '2º Trimestre', '3º Trimestre'],
        'Semanas': ['1-14', '15-28', '29-42'],
        'Capítulos': ['1 a 4', '5 a 8', '9 a 12'],
        'Volumes': ['V1 (caps 1-3) + V2 início', 'V2 (final) + V3', 'V3 (final) + V4'],
        'Avaliações': ['A1 + A2 + Simulado', 'A1 + A2 + Simulado', 'A1 + A2 + Final + Simulado'],
        'Trilhas SAE': ['4 trilhas', '4 trilhas', '4 trilhas'],
        'Observação': [
            '~3,5 semanas por capítulo',
            'Inclui férias de julho',
            'Fechamento do ano'
        ]
    })

    st.dataframe(metas, use_container_width=True, hide_index=True)

    # ========== RITMO POR DISCIPLINA ==========
    st.markdown("---")
    st.header("⏱️ Ritmo por Disciplina")

    st.markdown("""
    O ritmo varia conforme a carga horária. Disciplinas com mais aulas
    devem avançar no mesmo capítulo, mas com mais profundidade.
    """)

    ritmo_disc = pd.DataFrame({
        'Disciplina': ['Português', 'Matemática', 'Ciências', 'História', 'Geografia',
                      'Inglês', 'Arte', 'Filosofia', 'Ed. Física', 'Redação'],
        'Aulas/Semana': [5, 5, 3, 3, 3, 2, 1, 1, 2, 2],
        'Aulas/Capítulo': [10, 10, 6, 6, 6, 4, '2-3', '2-3', 4, 4],
        'Semanas/Capítulo': ['~2', '~2', '~2', '~2', '~2', '~2', '~2-3', '~2-3', '~2', '~2'],
        'Tempo para Seções': [
            '2-3 aulas/seção',
            '2-3 aulas/seção',
            '1-2 aulas/seção',
            '1-2 aulas/seção',
            '1-2 aulas/seção',
            '1 aula/seção',
            'Flexível',
            'Flexível',
            'Por habilidade',
            'Por tipo textual'
        ]
    })

    st.dataframe(ritmo_disc, use_container_width=True, hide_index=True)

    # ========== MATERIAL IMPRIMÍVEL ==========
    st.markdown("---")
    st.header("🖨️ Material para Impressão")

    st.markdown("""
    <div class="info-box">
        Clique no botão abaixo para gerar um PDF com o ritmo esperado
        que pode ser entregue aos professores.
    </div>
    """, unsafe_allow_html=True)

    # Cria conteúdo para download
    conteudo_impressao = """
RITMO ESPERADO SAE 2026 - COLÉGIO ELO
=====================================

FÓRMULA DE PROGRESSÃO:
Capítulo = ⌈ Semana Letiva ÷ 3.5 ⌉

TRADUÇÃO: 42 semanas ÷ 12 capítulos = 3,5 SEMANAS POR CAPÍTULO

APLICA-SE A: Anos Finais (6º-9º) E Ensino Médio (1ª-3ª)

PROGRESSÃO DETALHADA:
- Semanas 1-4: Capítulo 1
- Semanas 5-7: Capítulo 2
- Semanas 8-11: Capítulo 3
- Semanas 12-14: Capítulo 4

METAS POR TRIMESTRE (4 capítulos cada):
---------------------------------------
1º TRIMESTRE (Semanas 1-14):
- Capítulos 1 a 4
- Volumes 1 e início do 2
- Avaliações: A1, A2, Simulado
- 4 Trilhas Digitais

2º TRIMESTRE (Semanas 15-28):
- Capítulos 5 a 8
- Volumes 2 (final) e 3
- Avaliações: A1, A2, Simulado
- 4 Trilhas Digitais

3º TRIMESTRE (Semanas 29-42):
- Capítulos 9 a 12
- Volumes 3 (final) e 4
- Avaliações: A1, A2, Final, Simulado
- 4 Trilhas Digitais

PONTOS DE VERIFICAÇÃO:
---------------------
Semana 7: Deve estar no capítulo 2 (início A1)
Semana 14: Deve ter concluído capítulo 4
Semana 21: Deve estar no capítulo 6
Semana 28: Deve ter concluído capítulo 8
Semana 35: Deve estar no capítulo 10
Semana 42: Deve ter concluído capítulo 12

ATENÇÃO:
- Atraso de 1 capítulo: ATENÇÃO (monitorar)
- Atraso de 2+ capítulos: ALERTA (reunião)
"""

    st.download_button(
        label="📥 Baixar Ritmo Esperado (TXT)",
        data=conteudo_impressao,
        file_name="ritmo_esperado_sae_2026.txt",
        mime="text/plain"
    )

    # Tabela de verificação
    st.subheader("📋 Pontos de Verificação (Checkpoints)")

    checkpoints = pd.DataFrame({
        'Checkpoint': ['Fim Semana 7', 'Fim Semana 14', 'Fim Semana 21',
                      'Fim Semana 28', 'Fim Semana 35', 'Fim Semana 42'],
        'Data Aproximada': ['13/03', '08/05', '26/06', '28/08', '16/10', '18/12'],
        'Capítulo Mínimo': [2, 4, 6, 8, 10, 12],
        'Volume Concluído': ['V1 em andamento', 'V1 + início V2', 'V2 + início V3',
                            'V3 em andamento', 'V3 + início V4', 'V4 concluído'],
        'Avaliações Realizadas': ['A1', 'A1+A2+Rec', 'A1 (2ºTri)', 'A1+A2+Rec', 'A1 (3ºTri)', 'Todas'],
        'Trilhas Aplicadas': [2, 4, 6, 8, 10, 12]
    })

    st.dataframe(checkpoints, use_container_width=True, hide_index=True)

    # ========== COMPARATIVO COM DADOS REAIS ==========
    st.markdown("---")
    st.header("🔍 Verificação com Dados do SIGA")

    # Carrega dados reais se disponiveis
    df_aulas = carregar_fato_aulas()

    if not df_aulas.empty:

        # Recalcula semana e capítulo baseado nos dados reais
        if df_aulas['data'].notna().any():
            data_max = df_aulas['data'].max()
            semana_dados = calcular_semana_letiva(data_max)
            cap_esperado = calcular_capitulo_esperado(semana_dados)
            st.info(f"📅 **Dados até:** {data_max.strftime('%d/%m/%Y')} | **Semana {semana_dados}** | **Capítulo esperado: {cap_esperado}**")

        st.markdown("""
        <div class="info-box">
            Compare os registros do SIGA com o ritmo esperado.
            O sistema analisa os conteúdos registrados para estimar em qual capítulo cada disciplina está.
        </div>
        """, unsafe_allow_html=True)

        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            unidades = sorted(df_aulas['unidade'].unique())
            un_sel = st.selectbox("Unidade:", unidades)
        with col_f2:
            series = sorted(df_aulas[df_aulas['unidade'] == un_sel]['serie'].unique())
            serie_sel = st.selectbox("Série:", series)

        # Filtra
        df_filtrado = df_aulas[(df_aulas['unidade'] == un_sel) & (df_aulas['serie'] == serie_sel)]

        # Mostra resumo por disciplina
        resumo = df_filtrado.groupby('disciplina').agg({
            'aula_id': 'count',
            'professor': lambda x: x.iloc[0] if len(x) > 0 else '',
            'conteudo': lambda x: ' | '.join(x.dropna().unique()[-3:]) if len(x.dropna()) > 0 else ''
        }).reset_index()
        resumo.columns = ['Disciplina', 'Aulas Registradas', 'Professor', 'Últimos Conteúdos']

        st.dataframe(resumo, use_container_width=True, hide_index=True)

        st.info(f"""
        **Análise para {serie_sel} - {un_sel}:**
        - Total de aulas registradas: {len(df_filtrado)}
        - Disciplinas com registro: {df_filtrado['disciplina'].nunique()}
        - Professores ativos: {df_filtrado['professor'].nunique()}

        **Verificação:** Analise os "Últimos Conteúdos" e compare com o capítulo esperado ({cap_esperado}).
        """)
    else:
        st.warning("Dados do SIGA nao carregados. Execute a extracao primeiro.")

if __name__ == "__main__":
    main()
