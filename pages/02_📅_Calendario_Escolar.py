#!/usr/bin/env python3
"""
PÁGINA 2: CALENDÁRIO ESCOLAR 2026
Trimestres, feriados, recessos, semanas especiais, marcos de avaliação
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import math
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import carregar_calendario, _hoje, calcular_semana_letiva, calcular_capitulo_esperado
from config_cores import CORES_SERIES, ORDEM_SERIES

st.set_page_config(page_title="Calendario Escolar", page_icon="📅", layout="wide")
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
    .table-header {
        background: #3f51b5;
        color: white;
        padding: 10px;
        text-align: center;
        border-radius: 4px 4px 0 0;
        margin-top: 20px;
    }
    .feriado-nacional { background-color: #ffcdd2; }
    .feriado-regional { background-color: #ffe0b2; }
    .ferias { background-color: #c8e6c9; }
    .legenda-serie {
        display: inline-block; padding: 4px 12px; border-radius: 16px;
        margin: 3px 4px; font-size: 0.85em; font-weight: 600; color: white;
    }
    .legenda-grupo {
        border: 2px solid #E0E0E0; border-radius: 8px; padding: 10px 15px;
        margin: 5px 0; background: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📅 Calendário Escolar 2026")
    st.markdown("**Estrutura completa do ano letivo com todos os marcos importantes**")

    # ========== LEGENDA DE CORES POR SÉRIE ==========
    st.markdown("""
    <div class="legenda-grupo">
        <strong>🎨 Legenda de Cores por Série</strong><br>
        <div style="margin-top: 8px;">
            <span style="font-weight:600; margin-right: 10px;">📘 Anos Finais:</span>
            <span class="legenda-serie" style="background:{azul6}">6º Ano</span>
            <span class="legenda-serie" style="background:{azul7}">7º Ano</span>
            <span class="legenda-serie" style="background:{azul8}">8º Ano</span>
        </div>
        <div style="margin-top: 6px;">
            <span style="font-weight:600; margin-right: 10px;">📙 Transição:</span>
            <span class="legenda-serie" style="background:{laranja9}">9º Ano</span>
        </div>
        <div style="margin-top: 6px;">
            <span style="font-weight:600; margin-right: 10px;">📗 Ensino Médio:</span>
            <span class="legenda-serie" style="background:{verde1}">1ª Série</span>
            <span class="legenda-serie" style="background:{verde2}">2ª Série</span>
        </div>
        <div style="margin-top: 6px;">
            <span style="font-weight:600; margin-right: 10px;">📕 Pré-vestibular:</span>
            <span class="legenda-serie" style="background:{verm3}">3ª Série</span>
        </div>
    </div>
    """.format(
        azul6=CORES_SERIES['6º Ano'], azul7=CORES_SERIES['7º Ano'], azul8=CORES_SERIES['8º Ano'],
        laranja9=CORES_SERIES['9º Ano'],
        verde1=CORES_SERIES['1ª Série'], verde2=CORES_SERIES['2ª Série'],
        verm3=CORES_SERIES['3ª Série'],
    ), unsafe_allow_html=True)

    # ========== ORGANIZAÇÃO ANUAL ==========
    st.markdown("---")
    st.header("📆 1. Organização Anual por Trimestre")

    st.markdown("""
    <div class="info-box">
        <strong>Ano Letivo 2026:</strong> 199 dias letivos distribuídos em 3 trimestres de aproximadamente 14 semanas cada.
    </div>
    """, unsafe_allow_html=True)

    # Tabela de trimestres
    trimestres = pd.DataFrame({
        'Período': ['1º TRIMESTRE', '2º TRIMESTRE', '3º TRIMESTRE', 'ANO LETIVO'],
        'Início': ['26/01/2026', '11/05/2026', '31/08/2026', '26/01/2026'],
        'Término': ['08/05/2026', '28/08/2026', '21/12/2026', '21/12/2026'],
        'Dias Letivos': [68, 57, 75, 200],
        'Semanas': [14, 14, 14, 42],
        'Capítulos SAE': ['1 a 4', '5 a 8', '9 a 12', '1 a 12'],
        'Volumes': ['V1', 'V2 + V3', 'V4', 'V1 a V4']
    })

    st.dataframe(trimestres, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 📊 Distribuição de Dias Letivos

        | Trimestre | Dias | % do Ano |
        |-----------|------|----------|
        | 1º Trimestre | 68 | 34% |
        | 2º Trimestre | 57 | 28,5% |
        | 3º Trimestre | 75 | 37,5% |
        | **TOTAL** | **200** | **100%** |
        """)

    with col2:
        st.markdown("""
        ### 📚 Capítulos por Trimestre

        | Trimestre | Capítulos | Ritmo |
        |-----------|-----------|-------|
        | 1º Tri | 4 capítulos (1-4) | ~3,5 semanas/cap |
        | 2º Tri | 4 capítulos (5-8) | ~3,5 semanas/cap |
        | 3º Tri | 4 capítulos (9-12) | ~3,5 semanas/cap |

        *Fórmula: Capítulo = Semana ÷ 3,5*
        """)

    # Agrupamento por turma TEEN
    st.markdown("""
    <div class="legenda-grupo">
        <strong>👥 Agrupamento por Turma TEEN (Material SAE)</strong>
        <table style="width: 100%; margin-top: 8px; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border: 1px solid #E0E0E0; width: 15%;"><strong>TEEN 1</strong></td>
                <td style="padding: 8px; border: 1px solid #E0E0E0;">
                    <span class="legenda-serie" style="background:{azul6}">6º Ano</span>
                    <span class="legenda-serie" style="background:{azul7}">7º Ano</span>
                    <span class="legenda-serie" style="background:{azul8}">8º Ano</span>
                    <span style="margin-left: 10px; color: #666;">Livro Integrado: 4 volumes (3 caps/vol)</span>
                </td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #E0E0E0;"><strong>TEEN 2</strong></td>
                <td style="padding: 8px; border: 1px solid #E0E0E0;">
                    <span class="legenda-serie" style="background:{laranja9}">9º Ano</span>
                    <span class="legenda-serie" style="background:{verde1}">1ª Série</span>
                    <span class="legenda-serie" style="background:{verde2}">2ª Série</span>
                    <span class="legenda-serie" style="background:{verm3}">3ª Série</span>
                    <span style="margin-left: 10px; color: #666;">Livro Integrado: 4 volumes (3 caps/vol)</span>
                </td>
            </tr>
        </table>
    </div>
    """.format(
        azul6=CORES_SERIES['6º Ano'], azul7=CORES_SERIES['7º Ano'], azul8=CORES_SERIES['8º Ano'],
        laranja9=CORES_SERIES['9º Ano'],
        verde1=CORES_SERIES['1ª Série'], verde2=CORES_SERIES['2ª Série'],
        verm3=CORES_SERIES['3ª Série'],
    ), unsafe_allow_html=True)

    # ========== FERIADOS E RECESSOS ==========
    st.markdown("---")
    st.header("🎌 2. Feriados e Recessos")

    st.markdown("""
    <div class="info-box">
        <strong>Legenda:</strong>
        🔴 Feriado Nacional |
        🟠 Feriado Regional (PE/Jaboatão) |
        🟢 Recesso/Férias
    </div>
    """, unsafe_allow_html=True)

    feriados = pd.DataFrame({
        'Data': ['14-17/02', '06/03', '02-03/04', '13/04', '21/04', '01/05',
                 '04/06', '24/06', '06-31/07', '07/09', '12/10', '02/11',
                 '15/11', '20/11', '08/12'],
        'Evento': ['Carnaval', 'Data Magna PE', 'Semana Santa', 'Feriado Jaboatão',
                   'Tiradentes', 'Dia do Trabalho', 'Corpus Christi', 'São João',
                   'Férias de Julho', 'Independência', 'N.S. Aparecida', 'Finados',
                   'Proclamação República', 'Consciência Negra', 'N.S. Conceição'],
        'Tipo': ['🔴 Nacional', '🟠 Regional PE', '🔴 Nacional', '🟠 Regional Jaboatão',
                 '🔴 Nacional', '🔴 Nacional', '🔴 Nacional', '🟠 Regional PE',
                 '🟢 Férias', '🔴 Nacional', '🔴 Nacional', '🔴 Nacional',
                 '🔴 Nacional', '🔴 Nacional', '🔴 Nacional'],
        'Dias Não Letivos': [4, 1, 2, 1, 1, 1, 1, 1, '~20', 1, 1, 1, 1, 1, 1],
        'Impacto': ['Semana reduzida', 'Apenas Pernambuco', 'Quinta e Sexta-feira',
                    'Apenas Candeias (CD)', 'Terça-feira', 'Sexta-feira',
                    'Quinta-feira', 'Quarta-feira', 'Recesso escolar completo',
                    'Segunda-feira', 'Segunda-feira', 'Segunda-feira',
                    'Domingo (sem impacto)', 'Sexta-feira', 'Terça-feira'],
        'Unidades Afetadas': ['TODAS', 'TODAS', 'TODAS', 'Apenas CD',
                              'TODAS', 'TODAS', 'TODAS', 'TODAS',
                              'TODAS', 'TODAS', 'TODAS', 'TODAS',
                              'TODAS', 'TODAS', 'TODAS']
    })

    st.dataframe(feriados, use_container_width=True, hide_index=True)

    # Resumo de impacto
    st.markdown("""
    ### 📉 Impacto dos Feriados por Trimestre

    | Trimestre | Feriados | Dias Perdidos | Observação |
    |-----------|----------|---------------|------------|
    | **1º Tri** | Carnaval, Data Magna, Semana Santa, Jaboatão, Tiradentes, Trabalho | ~10 dias | Maior concentração |
    | **2º Tri** | Corpus Christi, São João, Férias Julho | ~22 dias | Inclui férias |
    | **3º Tri** | Independência, N.S. Aparecida, Finados, República, Consciência Negra, N.S. Conceição | ~6 dias | Menor impacto |
    """)

    st.warning("""
    **⚠️ Atenção Especial - Feriado de Jaboatão (13/04):**
    Este feriado afeta APENAS a unidade Candeias (CD), que está localizada em Jaboatão dos Guararapes.
    As demais unidades (BV, JG, CDR) têm aula normal nesta data.
    """)

    # ========== SEMANAS ESPECIAIS ==========
    st.markdown("---")
    st.header("🌟 3. Semanas Especiais")

    st.markdown("""
    <div class="info-box">
        Semanas com atividades diferenciadas que impactam o ritmo regular das aulas.
    </div>
    """, unsafe_allow_html=True)

    semanas_especiais = pd.DataFrame({
        'Semana': [1, 2, 3, '7-8', '11-12', '13-14'],
        'Período': ['26-30/Jan', '02-06/Fev', '09-13/Fev', '09-20/Mar', '06-17/Abr', '20/Abr-08/Mai'],
        'Evento': ['Semana de Adaptação', 'Semana de Diagnose', 'Elo Folia',
                   'Avaliações A1', 'Avaliações A2', 'Recuperação/Fechamento'],
        'Atividades': [
            'Acolhimento, apresentação do material SAE, organização das turmas',
            'Avaliação diagnóstica SAE, início do conteúdo regular',
            'Atividades temáticas de Carnaval, encerramento 13/fev',
            'Primeira rodada avaliativa do trimestre (A1.1 a A1.4)',
            'Segunda rodada avaliativa (A1.5, A2)',
            'Recuperação paralela e fechamento do 1º Trimestre'
        ],
        'Impacto no Ritmo': [
            'Sem conteúdo regular - foco em apresentação',
            'Ritmo reduzido - avaliação inicial',
            'Semana curta (até 13/fev)',
            'Ritmo normal com avaliações',
            'Ritmo normal com avaliações',
            'Revisões e recuperação'
        ]
    })

    st.dataframe(semanas_especiais, use_container_width=True, hide_index=True)

    # ========== MARCOS DE AVALIAÇÃO ==========
    st.markdown("---")
    st.header("📝 4. Marcos de Avaliação")

    st.subheader("4.1 Ciclos Avaliativos por Trimestre")

    ciclos = pd.DataFrame({
        'Ciclo': ['Avaliação 1', 'Avaliação 2', 'Recuperação', 'Simulado'],
        'Código': ['A1.1 a A1.4', 'A1.5, A2', 'REC', 'SIM'],
        'Período': ['Semanas 7-8', 'Semanas 11-12', 'Semanas 13-14', 'Final do trimestre'],
        'Capítulos Avaliados': ['Caps 1-3', 'Caps 4-6', 'Todo trimestre', 'Acumulativo'],
        'Descrição': [
            'Primeira rodada - avalia primeiros capítulos',
            'Segunda rodada - avalia capítulos seguintes',
            'Para alunos abaixo da média',
            'Formato vestibular/ENEM'
        ]
    })

    st.dataframe(ciclos, use_container_width=True, hide_index=True)

    st.subheader("4.2 Calendário de Avaliações - 1º Trimestre 2026")

    aval_1tri = pd.DataFrame({
        'Semana': [7, 7, 8, 8, 11, 11, 12, 12, 13, 14],
        'Data Aproximada': ['09/03', '10/03', '16/03', '17/03', '06/04', '07/04', '13/04', '14/04', '20-24/04', '27/04-08/05'],
        'Avaliação': ['A1.1', 'A1.2', 'A1.3', 'A1.4', 'A1.5', 'A1.5', 'A2', 'A2', 'Recuperação', 'Simulado + Fechamento'],
        'Componentes': [
            'Português, Matemática',
            'Ciências, História',
            'Geografia, Inglês',
            'Arte, Filosofia, Ed.Física',
            'Português, Matemática (cont.)',
            'Demais componentes',
            'Avaliação integradora',
            'Avaliação integradora',
            'Todos - conforme necessidade',
            'Todas as disciplinas'
        ]
    })

    st.dataframe(aval_1tri, use_container_width=True, hide_index=True)

    # ========== INSTRUMENTOS AVALIATIVOS ==========
    st.markdown("---")
    st.header("📋 5. Instrumentos Avaliativos SAE")

    st.markdown("""
    <div class="info-box">
        <strong>O que são?</strong> São as diferentes formas de avaliar o aprendizado dos alunos no sistema SAE.
        Cada instrumento tem uma frequência e objetivo específico.
    </div>
    """, unsafe_allow_html=True)

    instrumentos = pd.DataFrame({
        'Instrumento': ['Trilhas Digitais', 'Avaliações Escritas', 'Simulados',
                        'Tarefas de Casa', 'Participação', 'Projetos'],
        'Frequência': ['Ao final de cada capítulo', '2 rodadas/trimestre', '1 por trimestre',
                       'Diárias', 'Contínua', 'Por unidade temática'],
        'Descrição': [
            'Atividades interativas no portal SAE Digital que o aluno faz online',
            'Provas escritas por componente curricular aplicadas em sala',
            'Avaliação no formato ENEM/vestibular com todas as matérias',
            'Exercícios do livro para fazer em casa',
            'Engajamento e participação nas aulas e atividades',
            'Trabalhos em grupo ou individuais sobre temas específicos'
        ],
        'Onde Verificar (SIGA)': [
            'Campo "tarefa" com menção a trilhas',
            'Registrado como conteúdo de avaliação',
            'Evento específico no calendário',
            'Campo "tarefa" no diário',
            'Observações do professor',
            'Campo "conteudo" com menção a projeto'
        ],
        'Peso Sugerido': ['15%', '40%', '15%', '10%', '10%', '10%']
    })

    st.dataframe(instrumentos, use_container_width=True, hide_index=True)

    st.info("""
    **💡 Como usar esta informação:**
    - Verifique se os professores estão registrando as trilhas após cada capítulo
    - Confirme se as avaliações estão sendo aplicadas nas semanas corretas
    - Acompanhe se há tarefas sendo atribuídas regularmente
    """)

    # ========== CALENDÁRIO VISUAL ==========
    st.markdown("---")
    st.header("📆 6. Visão do Calendário")

    # Tenta carregar o calendario do CSV
    df_cal = carregar_calendario()

    if not df_cal.empty:

        # --- Referência: Capítulo esperado por semana ---
        hoje = _hoje()
        semana_atual = calcular_semana_letiva(hoje)
        cap_esperado = calcular_capitulo_esperado(semana_atual)
        trimestre_atual = 1 if semana_atual <= 14 else (2 if semana_atual <= 28 else 3)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Semana Letiva", f"{semana_atual}ª")
        c2.metric("Trimestre", f"{trimestre_atual}º")
        c3.metric("Capítulo Esperado", f"Cap {cap_esperado}")
        c4.metric("Semanas Restantes", f"{max(0, 42 - semana_atual)}")

        # Barra de progressão visual do ano
        progresso_pct = min(100, round(semana_atual / 42 * 100))
        st.markdown(f"""
        <div style="background: #E0E0E0; border-radius: 10px; height: 24px; margin: 10px 0 20px 0; position: relative;">
            <div style="background: linear-gradient(90deg, {CORES_SERIES['6º Ano']}, {CORES_SERIES['1ª Série']});
                        width: {progresso_pct}%; height: 100%; border-radius: 10px; transition: width 0.3s;"></div>
            <span style="position: absolute; top: 2px; left: 50%; transform: translateX(-50%); font-size: 0.8em; font-weight: 600;">
                {progresso_pct}% do ano letivo
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Filtra por mês
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        mes_sel = st.selectbox("Selecione o mês:", meses, index=_hoje().month - 1)
        mes_num = meses.index(mes_sel) + 1

        df_mes = df_cal[df_cal['data'].dt.month == mes_num].copy()

        if len(df_mes) > 0:
            df_mes['Dia'] = df_mes['data'].dt.day
            df_mes['Dia Semana'] = df_mes['dia_semana'] if 'dia_semana' in df_mes.columns else df_mes['data'].dt.day_name()
            df_mes['Semana Letiva'] = df_mes['semana_letiva'] if 'semana_letiva' in df_mes.columns else ''
            df_mes['Tipo'] = df_mes['eh_letivo'].apply(lambda x: '✅ Letivo' if x == 1 else '❌ Não Letivo')
            df_mes['Evento'] = df_mes['evento'].fillna('')

            # Adicionar coluna de capítulo esperado por semana
            def cap_da_semana(sem):
                try:
                    s = int(sem)
                    return f"Cap {min(12, math.ceil(s / 3.5))}" if s > 0 else ""
                except (ValueError, TypeError):
                    return ""

            df_mes['Cap Esperado'] = df_mes['Semana Letiva'].apply(cap_da_semana)

            # Adicionar trimestre
            def tri_da_semana(sem):
                try:
                    s = int(sem)
                    if s <= 14: return "1º Tri"
                    elif s <= 28: return "2º Tri"
                    else: return "3º Tri"
                except (ValueError, TypeError):
                    return ""

            df_mes['Trimestre'] = df_mes['Semana Letiva'].apply(tri_da_semana)

            # Mostra tabela do mês
            cols_show = ['Dia', 'Dia Semana', 'Tipo', 'Semana Letiva', 'Trimestre', 'Cap Esperado', 'Evento']

            st.dataframe(df_mes[cols_show], use_container_width=True, hide_index=True)

            # Resumo do mês
            col_r1, col_r2, col_r3 = st.columns(3)
            letivos = len(df_mes[df_mes['eh_letivo'] == 1])
            nao_letivos = len(df_mes[df_mes['eh_letivo'] != 1])
            semanas_mes = sorted(df_mes['semana_letiva'].dropna().unique())
            col_r1.metric(f"Dias Letivos em {mes_sel}", letivos)
            col_r2.metric("Dias Não Letivos", nao_letivos)
            caps_mes = set()
            for s in semanas_mes:
                try:
                    caps_mes.add(min(12, math.ceil(int(s) / 3.5)))
                except (ValueError, TypeError):
                    pass
            if caps_mes:
                cap_range = f"Cap {min(caps_mes)} a {max(caps_mes)}" if len(caps_mes) > 1 else f"Cap {min(caps_mes)}"
                col_r3.metric("Capítulos do Mês", cap_range)
    else:
        st.warning("Arquivo de calendário não encontrado. Execute a geração do dim_Calendario.csv")

    # ========== RODAPÉ ==========
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        📅 Calendário Escolar 2026 - Colégio ELO<br>
        <em>Use este material como referência para planejamento e acompanhamento</em>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
