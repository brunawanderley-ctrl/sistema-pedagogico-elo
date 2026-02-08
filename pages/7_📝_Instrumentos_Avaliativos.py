#!/usr/bin/env python3
"""
PÁGINA 7: INSTRUMENTOS AVALIATIVOS
Trilhas, avaliações, simulados - quem usou, quando, onde
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import carregar_fato_aulas

st.set_page_config(page_title="Instrumentos Avaliativos", page_icon="📝", layout="wide")
from auth import check_password, logout_button, get_user_unit
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
    .instrumento-card {
        background: #f5f5f5;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("📝 Instrumentos Avaliativos SAE")
    st.markdown("**Trilhas, avaliações, simulados - acompanhamento de uso**")

    # ========== EXPLICAÇÃO ==========
    st.markdown("---")
    st.header("📚 O que são Instrumentos Avaliativos?")

    st.markdown("""
    <div class="info-box">
        Instrumentos avaliativos são as diferentes formas de verificar e acompanhar
        o aprendizado dos alunos. O SAE oferece diversos instrumentos que devem ser
        utilizados de forma complementar.
    </div>
    """, unsafe_allow_html=True)

    # Lista de instrumentos
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="instrumento-card">
            <h3>🖥️ Trilhas Digitais</h3>
            <p><strong>O que é:</strong> Atividades interativas no portal SAE Digital</p>
            <p><strong>Frequência:</strong> Ao final de cada capítulo</p>
            <p><strong>Como aplicar:</strong> Aluno acessa portal, faz atividades, sistema registra</p>
            <p><strong>Onde verificar:</strong> Portal SAE ou registro do professor</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="instrumento-card">
            <h3>📋 Avaliações Escritas</h3>
            <p><strong>O que é:</strong> Provas tradicionais por componente</p>
            <p><strong>Frequência:</strong> 2 rodadas por trimestre (A1 e A2)</p>
            <p><strong>Como aplicar:</strong> Em sala, com questões do banco SAE ou próprias</p>
            <p><strong>Onde verificar:</strong> SIGA - registro de avaliação</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="instrumento-card">
            <h3>📝 Simulados</h3>
            <p><strong>O que é:</strong> Avaliação no formato ENEM/vestibular</p>
            <p><strong>Frequência:</strong> 1 por trimestre (mensal no EM)</p>
            <p><strong>Como aplicar:</strong> Dia específico, todas as disciplinas</p>
            <p><strong>Onde verificar:</strong> Calendário escolar</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="instrumento-card">
            <h3>📖 Tarefas de Casa</h3>
            <p><strong>O que é:</strong> Exercícios do livro para fazer em casa</p>
            <p><strong>Frequência:</strong> Diárias ou após cada aula</p>
            <p><strong>Como aplicar:</strong> Professor indica página/exercícios</p>
            <p><strong>Onde verificar:</strong> SIGA - campo "tarefa"</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="instrumento-card">
            <h3>🙋 Participação</h3>
            <p><strong>O que é:</strong> Engajamento do aluno nas aulas</p>
            <p><strong>Frequência:</strong> Contínua</p>
            <p><strong>Como avaliar:</strong> Observação, perguntas, trabalhos em grupo</p>
            <p><strong>Onde registrar:</strong> Observações do professor</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="instrumento-card">
            <h3>🎨 Projetos</h3>
            <p><strong>O que é:</strong> Trabalhos sobre temas específicos</p>
            <p><strong>Frequência:</strong> Por unidade temática ou trimestre</p>
            <p><strong>Como aplicar:</strong> Individual ou em grupo</p>
            <p><strong>Onde verificar:</strong> SIGA - menção a projeto no conteúdo</p>
        </div>
        """, unsafe_allow_html=True)

    # ========== TABELA DE PESO ==========
    st.markdown("---")
    st.header("⚖️ Peso Sugerido dos Instrumentos")

    pesos = pd.DataFrame({
        'Instrumento': ['Avaliações Escritas', 'Trilhas Digitais', 'Simulados',
                       'Tarefas de Casa', 'Participação', 'Projetos'],
        'Peso Sugerido': ['40%', '15%', '15%', '10%', '10%', '10%'],
        'Justificativa': [
            'Principal forma de verificação formal',
            'Feedback imediato e acompanhamento digital',
            'Preparação para vestibular',
            'Reforço e prática contínua',
            'Engajamento e habilidades socioemocionais',
            'Aplicação prática e interdisciplinaridade'
        ]
    })

    st.dataframe(pesos, use_container_width=True, hide_index=True)

    # ========== VERIFICAÇÃO NOS DADOS ==========
    st.markdown("---")
    st.header("🔍 Verificação nos Registros do SIGA")

    df = carregar_fato_aulas()

    if not df.empty:

        st.markdown("""
        <div class="info-box">
            Análise dos registros buscando menções aos instrumentos avaliativos.
        </div>
        """, unsafe_allow_html=True)

        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            unidades = ['TODAS'] + sorted(df['unidade'].unique().tolist())
            user_unit = get_user_unit()
            default_un = unidades.index(user_unit) if user_unit and user_unit in unidades else 0
            un_sel = st.selectbox("Unidade:", unidades, index=default_un)
        with col_f2:
            disciplinas = ['TODAS'] + sorted(df['disciplina'].dropna().unique().tolist())
            disc_sel = st.selectbox("Disciplina:", disciplinas)

        # Aplica filtros
        df_filtrado = df.copy()
        if un_sel != 'TODAS':
            df_filtrado = df_filtrado[df_filtrado['unidade'] == un_sel]
        if disc_sel != 'TODAS':
            df_filtrado = df_filtrado[df_filtrado['disciplina'] == disc_sel]

        # Busca menções
        def busca_instrumento(texto, palavras):
            if pd.isna(texto):
                return False
            texto_lower = str(texto).lower()
            return any(p in texto_lower for p in palavras)

        # Conta menções
        trilhas = df_filtrado[df_filtrado['conteudo'].apply(
            lambda x: busca_instrumento(x, ['trilha', 'digital', 'portal sae']))
        ]
        avaliacoes = df_filtrado[df_filtrado['conteudo'].apply(
            lambda x: busca_instrumento(x, ['avaliação', 'prova', 'teste', 'a1', 'a2']))
        ]
        simulados = df_filtrado[df_filtrado['conteudo'].apply(
            lambda x: busca_instrumento(x, ['simulado', 'enem']))
        ]
        tarefas = df_filtrado[df_filtrado['tarefa'].notna() & (df_filtrado['tarefa'] != '')]
        projetos = df_filtrado[df_filtrado['conteudo'].apply(
            lambda x: busca_instrumento(x, ['projeto', 'trabalho']))
        ]

        # Mostra resultados
        col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)

        with col_r1:
            st.metric("🖥️ Trilhas", len(trilhas))
        with col_r2:
            st.metric("📋 Avaliações", len(avaliacoes))
        with col_r3:
            st.metric("📝 Simulados", len(simulados))
        with col_r4:
            st.metric("📖 Tarefas", len(tarefas))
        with col_r5:
            st.metric("🎨 Projetos", len(projetos))

        # Detalhamento
        st.subheader("📊 Detalhamento por Instrumento")

        instrumento_sel = st.selectbox("Selecione o instrumento para ver detalhes:",
                                       ['Trilhas', 'Avaliações', 'Simulados', 'Tarefas', 'Projetos'])

        if instrumento_sel == 'Trilhas' and len(trilhas) > 0:
            st.dataframe(trilhas[['data', 'unidade', 'disciplina', 'professor', 'conteudo']].head(50),
                        use_container_width=True, hide_index=True)
        elif instrumento_sel == 'Avaliações' and len(avaliacoes) > 0:
            st.dataframe(avaliacoes[['data', 'unidade', 'disciplina', 'professor', 'conteudo']].head(50),
                        use_container_width=True, hide_index=True)
        elif instrumento_sel == 'Simulados' and len(simulados) > 0:
            st.dataframe(simulados[['data', 'unidade', 'disciplina', 'professor', 'conteudo']].head(50),
                        use_container_width=True, hide_index=True)
        elif instrumento_sel == 'Tarefas' and len(tarefas) > 0:
            st.dataframe(tarefas[['data', 'unidade', 'disciplina', 'professor', 'tarefa']].head(50),
                        use_container_width=True, hide_index=True)
        elif instrumento_sel == 'Projetos' and len(projetos) > 0:
            st.dataframe(projetos[['data', 'unidade', 'disciplina', 'professor', 'conteudo']].head(50),
                        use_container_width=True, hide_index=True)
        else:
            st.info(f"Nenhum registro de {instrumento_sel} encontrado com os filtros selecionados.")

        # Quem mais usa
        st.subheader("🏆 Professores que Mais Registram Tarefas")
        if len(tarefas) > 0:
            ranking = tarefas.groupby(['professor', 'unidade']).size().reset_index(name='tarefas')
            if not ranking.empty:
                ranking = ranking.sort_values('tarefas', ascending=False).head(10)
            st.dataframe(ranking, use_container_width=True, hide_index=True)

    else:
        st.warning("Dados do SIGA não carregados.")

    # ========== CALENDÁRIO DE AVALIAÇÕES ==========
    st.markdown("---")
    st.header("📅 Calendário de Avaliações 2026")

    calendario = pd.DataFrame({
        'Trimestre': ['1º', '1º', '1º', '1º', '2º', '2º', '2º', '3º', '3º', '3º', '3º'],
        'Avaliação': ['A1.1-A1.2', 'A1.3-A1.4', 'A1.5-A2', 'Simulado + Rec', 'A1', 'A2', 'Simulado + Rec',
                     'A1', 'A2', 'Final', 'Simulado'],
        'Semana': ['7', '8', '11-12', '13-14', '19-20', '24-25', '27-28', '32-33', '37-38', '40', '41'],
        'Período Aproximado': ['09-13/Mar', '16-20/Mar', '06-17/Abr', '20/Abr-08/Mai',
                              '15-26/Jun', '03-14/Ago', '24-28/Ago',
                              '28/Set-09/Out', '02-13/Nov', '30/Nov-04/Dez', '07-11/Dez'],
        'Conteúdo': ['Caps 1-2', 'Cap 3', 'Caps 4-6', '1º Tri completo',
                    'Caps 7-8', 'Cap 9', '2º Tri completo',
                    'Caps 10-11', 'Cap 12', 'Ano completo', 'Ano completo']
    })

    st.dataframe(calendario, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
