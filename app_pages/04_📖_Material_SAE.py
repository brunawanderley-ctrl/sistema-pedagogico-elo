#!/usr/bin/env python3
"""
PÁGINA 4: MATERIAL SAE
Estrutura dos livros, seções, metodologia Design Thinking
Material de referência para coordenação
"""

import streamlit as st
import pandas as pd


st.markdown("""
<style>
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .metodologia-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .secao-livro {
        background: #f5f5f5;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .dica-coord {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📖 Material SAE Digital")
    st.markdown("**Guia completo para coordenação e professores**")

    st.markdown("""
    <div class="info-box">
        <strong>Esta página contém:</strong>
        <ul>
            <li>Estrutura dos livros e volumes</li>
            <li>Explicação da metodologia Design Thinking</li>
            <li>Seções de cada capítulo e como usar</li>
            <li>Diferenças entre Anos Finais e Ensino Médio</li>
            <li>Dicas para a coordenação orientar os professores</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Tabs para organizar
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Estrutura do Material", "🎯 Metodologia",
                                       "📝 Seções do Livro", "💡 Orientações"])

    # ========== TAB 1: ESTRUTURA ==========
    with tab1:
        st.header("📚 Estrutura do Material SAE")

        st.subheader("Organização por Volume")

        st.markdown("""
        <div class="info-box">
            O material SAE é organizado em <strong>4 volumes por ano</strong>, com <strong>3 capítulos cada</strong>,
            totalizando <strong>12 capítulos</strong> para todas as disciplinas.
        </div>
        """, unsafe_allow_html=True)

        volumes = pd.DataFrame({
            'Volume': ['Volume 1', 'Volume 2', 'Volume 3', 'Volume 4'],
            'Capítulos': ['1, 2 e 3', '4, 5 e 6', '7, 8 e 9', '10, 11 e 12'],
            'Período': ['Janeiro - Fevereiro', 'Março - Maio', 'Maio - Agosto', 'Agosto - Dezembro'],
            'Equivalência': ['~1º Bimestre', '~2º Bimestre', '~3º Bimestre', '~4º Bimestre'],
            'Trimestre ELO': ['1º Trimestre', '1º Trimestre', '2º Trimestre', '3º Trimestre']
        })

        st.dataframe(volumes, use_container_width=True, hide_index=True)

        st.warning("""
        **⚠️ Atenção:**
        O SAE trabalha por bimestre (4 volumes), mas o Colégio ELO trabalha por **trimestre**.
        Por isso, no 1º Trimestre são trabalhados os Volumes 1 e 2 (capítulos 1 a 6).
        """)

        # Material por segmento
        st.subheader("Material por Segmento")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 📘 Anos Finais (6º ao 9º)
            **Nome:** Livro Integrado SAE

            | Tipo | Volumes | Capítulos | Disciplinas |
            |------|---------|-----------|-------------|
            | Livro Integrado | 4 | 12 | Port, Mat, Ciê, His, Geo |
            | Livros Semestrais | 2 | 12 | Arte, Filosofia, Inglês |
            | Fichas de Atividades | 4 | 12 | Complemento (6º e 7º) |
            | Material Digital | - | - | Educação Física |

            **Observações:**
            - 6º e 7º ano têm Fichas de Atividades como complemento
            - Livros semestrais: 6 capítulos por semestre
            - Ed. Física é 100% digital
            """)

        with col2:
            st.markdown("""
            ### 📗 Ensino Médio (1ª a 3ª)
            **Nome:** Conexões & Contextos

            | Tipo | Volumes | Organização |
            |------|---------|-------------|
            | Conexões & Contextos | 4 | Por área de conhecimento |
            | Itinerários Formativos | Digital | Projetos |
            | Projeto de Vida | Digital | Anual |

            **Áreas de Conhecimento:**
            - Linguagens e suas Tecnologias
            - Matemática e suas Tecnologias
            - Ciências da Natureza
            - Ciências Humanas

            **Diferencial:** Organizado por ÁREA, não por disciplina
            """)

        # Materiais complementares
        st.subheader("Materiais Complementares")

        complementares = pd.DataFrame({
            'Material': ['Portal SAE Digital', 'Trilhas Digitais', 'Videoaulas',
                        'Banco de Questões', 'Simulados Online', 'App SAE'],
            'Acesso': ['sae.digital', 'Portal do aluno', 'Portal do aluno',
                      'Portal do professor', 'Portal do aluno', 'iOS/Android'],
            'Uso': ['Conteúdo principal', 'Avaliação formativa', 'Reforço/revisão',
                   'Elaboração de provas', 'Preparação ENEM', 'Acesso mobile'],
            'Frequência Esperada': ['Diário', 'Após cada capítulo', 'Conforme necessidade',
                                    'Quinzenal', 'Mensal', 'Livre']
        })

        st.dataframe(complementares, use_container_width=True, hide_index=True)

    # ========== TAB 2: METODOLOGIA ==========
    with tab2:
        st.header("🎯 Metodologia Design Thinking")

        st.markdown("""
        <div class="metodologia-box">
            <h2 style="color: white; border: none;">O que é Design Thinking?</h2>
            <p>É uma abordagem centrada no ser humano para resolução de problemas.
            No contexto educacional, significa partir do que o aluno já sabe e
            construir o conhecimento de forma ativa e significativa.</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Etapas da Metodologia")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 1. EMPATIZAR
            - Entender o contexto do aluno
            - Conectar com conhecimentos prévios
            - Criar interesse pelo tema

            *No livro SAE: Seção "Conversa vai, conversa vem"*

            ### 2. DEFINIR
            - Identificar o problema/questão
            - Estabelecer objetivos claros
            - Organizar o que será aprendido

            *No livro SAE: Início de "Organizando o conhecimento"*
            """)

        with col2:
            st.markdown("""
            ### 3. IDEAR
            - Explorar possibilidades
            - Construir conceitos
            - Sistematizar conhecimento

            *No livro SAE: "Organizando o conhecimento"*

            ### 4. PROTOTIPAR e TESTAR
            - Aplicar na prática
            - Resolver exercícios
            - Avaliar aprendizado

            *No livro SAE: "Saberes em ação" e "Testando ideias"*
            """)

        st.markdown("---")

        # Fluxo visual
        st.subheader("Fluxo de uma Aula Design Thinking")

        st.markdown("""
        ```
        ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
        │   EMPATIZAR  │ → │    DEFINIR   │ → │    IDEAR     │ → │PROTOTIPAR/   │
        │              │    │              │    │              │    │   TESTAR     │
        │ Conectar com │    │ O que vamos  │    │ Construir o  │    │  Aplicar e   │
        │ o aluno      │    │ aprender?    │    │ conhecimento │    │  avaliar     │
        └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
              ↓                   ↓                   ↓                   ↓
         5-10 min            10-15 min           20-25 min           10-15 min
        ```
        """)

        st.markdown("""
        <div class="dica-coord">
            <strong>💡 Dica para Coordenação:</strong><br>
            Ao observar aulas, verifique se o professor está seguindo esse fluxo.
            Uma aula bem estruturada deve ter essas 4 etapas, mesmo que em proporções diferentes.
        </div>
        """, unsafe_allow_html=True)

    # ========== TAB 3: SEÇÕES DO LIVRO ==========
    with tab3:
        st.header("📝 Seções do Livro SAE")

        st.markdown("""
        Cada capítulo do livro SAE é dividido em seções específicas. Entender cada seção
        ajuda a coordenação a verificar se o professor está usando o material corretamente.
        """)

        st.subheader("Seções de um Capítulo - Anos Finais")

        secoes = pd.DataFrame({
            'Seção': ['Conversa vai, conversa vem', 'Organizando o conhecimento',
                     'Saberes em ação', 'Testando ideias'],
            'Objetivo': ['Ativação de conhecimentos prévios', 'Sistematização conceitual',
                        'Aplicação prática', 'Avaliação formativa'],
            '% do Capítulo': ['15%', '40%', '30%', '15%'],
            'Tempo Sugerido (Port/Mat)': ['1-2 aulas', '4-5 aulas', '3 aulas', '1-2 aulas'],
            'Tempo Sugerido (3 aulas/sem)': ['1 aula', '2-3 aulas', '2 aulas', '1 aula']
        })

        st.dataframe(secoes, use_container_width=True, hide_index=True)

        # Detalhamento de cada seção
        st.markdown("---")

        st.markdown("""
        <div class="secao-livro">
            <h3>📌 Conversa vai, conversa vem (15%)</h3>
            <p><strong>O que é:</strong> Abertura do capítulo com perguntas, imagens ou situações
            que conectam o conteúdo novo com o que o aluno já sabe.</p>
            <p><strong>Como usar:</strong> O professor deve fazer as perguntas propostas e deixar
            os alunos discutirem antes de dar respostas. Não pular esta etapa!</p>
            <p><strong>O que verificar:</strong> Se o professor está registrando atividades de
            "contextualização", "introdução" ou "discussão inicial".</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="secao-livro">
            <h3>📌 Organizando o conhecimento (40%)</h3>
            <p><strong>O que é:</strong> Conteúdo teórico principal do capítulo. Conceitos,
            definições, explicações e exemplos.</p>
            <p><strong>Como usar:</strong> Leitura compartilhada, explicação do professor,
            anotações no caderno, discussão de exemplos.</p>
            <p><strong>O que verificar:</strong> Se o conteúdo registrado menciona os conceitos
            principais do capítulo. Ex: "Equações do 1º grau" no capítulo sobre equações.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="secao-livro">
            <h3>📌 Saberes em ação (30%)</h3>
            <p><strong>O que é:</strong> Exercícios práticos para aplicar o que foi aprendido.
            Inclui questões individuais, em dupla e em grupo.</p>
            <p><strong>Como usar:</strong> Resolução de exercícios em sala, correção coletiva,
            atividades para casa.</p>
            <p><strong>O que verificar:</strong> Se há registro de "exercícios", "atividades",
            "resolução de questões" ou "correção".</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="secao-livro">
            <h3>📌 Testando ideias (15%)</h3>
            <p><strong>O que é:</strong> Atividades de verificação da aprendizagem. Preparação
            para avaliações e autoavaliação do aluno.</p>
            <p><strong>Como usar:</strong> Pode ser usado como "prova" do capítulo ou como
            revisão antes das avaliações oficiais.</p>
            <p><strong>O que verificar:</strong> Se há registro de "avaliação", "verificação",
            "testando ideias" ou "revisão".</p>
        </div>
        """, unsafe_allow_html=True)

        # Resumo visual
        st.subheader("Resumo Visual - Distribuição do Capítulo")

        import plotly.express as px

        df_secoes = pd.DataFrame({
            'Seção': ['Conversa vai, conversa vem', 'Organizando o conhecimento',
                     'Saberes em ação', 'Testando ideias'],
            'Percentual': [15, 40, 30, 15]
        })

        fig = px.pie(df_secoes, values='Percentual', names='Seção',
                    title='Distribuição de Tempo por Seção',
                    color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    # ========== TAB 4: ORIENTAÇÕES ==========
    with tab4:
        st.header("💡 Orientações para a Coordenação")

        st.markdown("""
        <div class="info-box">
            Este guia ajuda a coordenação a orientar os professores sobre o uso correto
            do material SAE e o que buscar nos registros do SIGA.
        </div>
        """, unsafe_allow_html=True)

        st.subheader("O que Observar nos Registros")

        observar = pd.DataFrame({
            'Aspecto': ['Conteúdo registrado', 'Tarefa de casa', 'Progressão',
                       'Diversidade de atividades', 'Trilhas SAE'],
            'O que esperar': [
                'Descrição clara do que foi trabalhado, mencionando capítulo/seção',
                'Exercícios específicos com página/número ou trilha digital',
                'Avançando ~1 capítulo a cada 2 semanas',
                'Variação entre explicação, exercício, discussão, prática',
                'Registro de aplicação após cada capítulo'
            ],
            'Sinal de alerta': [
                'Conteúdo vago como "Correção" ou "Continuação"',
                'Nenhuma tarefa registrada por semanas',
                'Mesmo capítulo por mais de 3 semanas',
                'Apenas "exercícios" ou apenas "explicação"',
                'Nenhuma menção a trilhas digitais'
            ],
            'Ação sugerida': [
                'Orientar sobre detalhamento do registro',
                'Verificar se estão usando o livro/portal',
                'Verificar dificuldades da turma ou do professor',
                'Sugerir variação metodológica',
                'Relembrar importância das trilhas para avaliação'
            ]
        })

        st.dataframe(observar, use_container_width=True, hide_index=True)

        st.markdown("---")

        st.subheader("Perguntas para Reunião com Professor")

        st.markdown("""
        **Sobre o Material:**
        1. Em qual capítulo você está com cada turma?
        2. Está conseguindo usar todas as seções do livro?
        3. Os alunos estão fazendo as trilhas digitais?
        4. Precisa de algum material complementar?

        **Sobre o Ritmo:**
        5. Está conseguindo manter o ritmo de 1 capítulo a cada 2 semanas?
        6. Qual turma está mais adiantada? E mais atrasada?
        7. O que está causando atraso (se houver)?

        **Sobre as Dificuldades:**
        8. Qual seção do livro os alunos têm mais dificuldade?
        9. Algum conteúdo específico está sendo problemático?
        10. Como posso ajudar?
        """)

        st.markdown("---")

        st.subheader("Checklist de Acompanhamento Mensal")

        checklist = pd.DataFrame({
            'Item': [
                'Todos os professores registrando aulas',
                'Progressão dentro do esperado',
                'Trilhas sendo aplicadas',
                'Tarefas sendo atribuídas',
                'Conteúdo bem detalhado',
                'Avaliações no prazo',
                'Recuperação sendo feita'
            ],
            'Jan': ['⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜'],
            'Fev': ['⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜'],
            'Mar': ['⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜'],
            'Abr': ['⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜'],
            'Mai': ['⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜']
        })

        st.dataframe(checklist, use_container_width=True, hide_index=True)

        st.info("""
        **💡 Dica:** Imprima este checklist e use nas reuniões mensais de coordenação.
        Marque ✅ para itens OK, ⚠️ para atenção e ❌ para problemas.
        """)

main()
