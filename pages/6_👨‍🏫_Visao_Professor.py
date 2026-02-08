#!/usr/bin/env python3
"""
PÁGINA 6: VISÃO DO PROFESSOR
Calendário individual, encontros no ano, metas por trimestre
MATERIAL IMPRIMÍVEL para entregar ao professor
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import math
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre, carregar_horario_esperado, carregar_fato_aulas, DATA_DIR

st.set_page_config(page_title="Visao do Professor", page_icon="👨‍🏫", layout="wide")
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
    .professor-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin: 10px 0;
    }
    .print-section {
        border: 2px dashed #ccc;
        padding: 20px;
        margin: 20px 0;
        border-radius: 8px;
    }
    @media print {
        .no-print { display: none; }
        .print-section { border: none; page-break-after: always; }
    }
</style>
""", unsafe_allow_html=True)


# Feriados 2026
FERIADOS_2026 = {
    '2026-02-14': 'Carnaval',
    '2026-02-15': 'Carnaval',
    '2026-02-16': 'Carnaval',
    '2026-02-17': 'Carnaval',
    '2026-03-06': 'Data Magna PE',
    '2026-04-02': 'Semana Santa',
    '2026-04-03': 'Semana Santa',
    '2026-04-13': 'Feriado Jaboatão',  # Apenas CD
    '2026-04-21': 'Tiradentes',
    '2026-05-01': 'Dia do Trabalho',
    '2026-06-04': 'Corpus Christi',
    '2026-06-24': 'São João',
    '2026-09-07': 'Independência',
    '2026-10-12': 'N.S. Aparecida',
    '2026-11-02': 'Finados',
    '2026-11-15': 'Proclamação República',
    '2026-11-20': 'Consciência Negra',
    '2026-12-08': 'N.S. Conceição'
}

# Férias de julho
for d in range(6, 32):
    FERIADOS_2026[f'2026-07-{d:02d}'] = 'Férias de Julho'

def calcular_encontros_disciplina(aulas_semana, total_semanas=42, feriados_impacto=15):
    """Calcula total de encontros esperados no ano considerando feriados"""
    encontros_base = aulas_semana * total_semanas
    # Desconta aproximadamente 15% por feriados e eventos
    encontros_real = int(encontros_base * 0.85)
    return encontros_real

def gerar_calendario_professor(disciplina, aulas_semana, turmas):
    """Gera calendário com expectativa de conteúdo por semana"""
    calendario = []
    inicio = datetime(2026, 1, 26)  # Início das aulas

    for semana in range(1, 43):
        data_inicio = inicio + timedelta(weeks=semana-1)
        data_fim = data_inicio + timedelta(days=4)

        # Calcula capítulo esperado
        capitulo = min(12, math.ceil(semana / 3.5))

        # Verifica trimestre
        if semana <= 14:
            trimestre = 1
        elif semana <= 28:
            trimestre = 2
        else:
            trimestre = 3

        # Verifica eventos
        eventos = []
        for d in range(5):
            data_check = (data_inicio + timedelta(days=d)).strftime('%Y-%m-%d')
            if data_check in FERIADOS_2026:
                eventos.append(FERIADOS_2026[data_check])

        evento_str = ', '.join(set(eventos)) if eventos else '-'
        aulas_semana_real = aulas_semana if not eventos else max(0, aulas_semana - len(set(eventos)) // 2)

        calendario.append({
            'Semana': semana,
            'Período': f"{data_inicio.strftime('%d/%m')} - {data_fim.strftime('%d/%m')}",
            'Tri': f'{trimestre}º',
            'Capítulo': capitulo,
            'Aulas Esperadas': aulas_semana_real,
            'Eventos': evento_str,
            'O que Trabalhar': f"Cap {capitulo}" + (" (Avaliações)" if semana in [7, 8, 11, 12] else "")
        })

    return pd.DataFrame(calendario)

def main():
    st.title("👨‍🏫 Visão do Professor")
    st.markdown("**Calendário individual, metas e material para impressão**")

    st.markdown("""
    <div class="info-box">
        <strong>Esta página gera material personalizado para cada professor:</strong>
        <ul>
            <li>Calendário com expectativa de conteúdo por semana</li>
            <li>Total de encontros no ano (descontando feriados)</li>
            <li>Metas por trimestre</li>
            <li>Material pronto para imprimir e entregar</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # ========== SELEÇÃO ==========
    st.markdown("---")
    st.header("🔧 Configuração")

    # Carrega dados
    df_horario = carregar_horario_esperado()
    df_aulas = carregar_fato_aulas()

    if not df_horario.empty:
        professores = sorted(df_horario['professor'].unique())
    else:
        professores = []

    col1, col2, col3 = st.columns(3)

    with col1:
        if professores:
            professor = st.selectbox("👤 Professor:", ['Selecione...'] + professores)
        else:
            professor = st.text_input("👤 Nome do Professor:")

    # Auto-preencher disciplina, turmas e aulas/semana do horário
    prof_disciplinas = []
    prof_turmas = []
    prof_aulas_sem = 3
    if professor and professor != 'Selecione...' and not df_horario.empty:
        df_prof = df_horario[df_horario['professor'] == professor]
        if not df_prof.empty:
            prof_disciplinas = sorted(df_prof['disciplina'].unique())
            prof_turmas = sorted(df_prof['turma'].unique()) if 'turma' in df_prof.columns else []
            if 'serie' in df_prof.columns:
                prof_series = sorted(df_prof['serie'].unique())

    with col2:
        if prof_disciplinas:
            disciplina = st.selectbox("📚 Disciplina:", prof_disciplinas)
        else:
            disciplinas = ['Língua Portuguesa', 'Matemática', 'Ciências', 'História', 'Geografia',
                          'Inglês', 'Arte', 'Filosofia', 'Educação Física', 'Redação',
                          'Física', 'Química', 'Biologia']
            disciplina = st.selectbox("📚 Disciplina:", disciplinas)

    # Calcular aulas/semana real do horário
    if professor and professor != 'Selecione...' and not df_horario.empty:
        df_disc = df_horario[(df_horario['professor'] == professor) & (df_horario['disciplina'] == disciplina)]
        if not df_disc.empty and 'aulas_semana' in df_disc.columns:
            prof_aulas_sem = int(df_disc['aulas_semana'].iloc[0])
        elif not df_disc.empty:
            # Conta número de slots/semana como estimativa
            prof_aulas_sem = len(df_disc)

    with col3:
        aulas_semana = st.number_input("📊 Aulas/Semana:", value=prof_aulas_sem, min_value=1, max_value=10)

    # Turmas - auto-selecionadas do horário
    if prof_turmas:
        st.markdown(f"**🎓 Turmas** (do horário): {', '.join(prof_turmas)}")
        turmas = prof_turmas
    else:
        st.subheader("🎓 Turmas")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            turmas_fund = st.multiselect("Anos Finais:",
                                         ['6º AM', '6º BM', '6º AT', '7º AM', '7º BM', '7º AT',
                                          '8º AM', '8º BM', '8º AT', '9º AM', '9º BM', '9º AT'])
        with col_t2:
            turmas_em = st.multiselect("Ensino Médio:",
                                       ['1ª A EM', '1ª B EM', '1ª C EM',
                                        '2ª A EM', '2ª B EM', '2ª C EM',
                                        '3ª A EM', '3ª B EM'])
        turmas = turmas_fund + turmas_em

    if not professor or professor == 'Selecione...':
        st.warning("Selecione um professor para gerar o material.")
        return

    # ========== CARD DO PROFESSOR ==========
    st.markdown("---")

    encontros_ano = calcular_encontros_disciplina(aulas_semana)
    encontros_trimestre = encontros_ano // 3

    st.markdown(f"""
    <div class="professor-card">
        <h2 style="color: white; border: none; margin-top: 0;">{professor}</h2>
        <p style="font-size: 1.2em;">{disciplina} | {aulas_semana} aulas/semana</p>
        <p>Turmas: {', '.join(turmas) if turmas else 'Não especificadas'}</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <div style="display: flex; justify-content: space-around;">
            <div>
                <h3 style="color: white; margin: 0;">{encontros_ano}</h3>
                <p style="margin: 0;">Encontros/Ano</p>
            </div>
            <div>
                <h3 style="color: white; margin: 0;">~{encontros_trimestre}</h3>
                <p style="margin: 0;">Por Trimestre</p>
            </div>
            <div>
                <h3 style="color: white; margin: 0;">12</h3>
                <p style="margin: 0;">Capítulos SAE</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ========== PROGRESSO REAL (do SIGA) ==========
    if not df_aulas.empty:
        # Buscar aulas reais deste professor (por nome completo ou parcial)
        nome_prof_upper = professor.split(' - ')[0].strip().upper()
        df_prof_aulas = df_aulas[df_aulas['professor'].str.upper().str.startswith(nome_prof_upper[:20])]

        if not df_prof_aulas.empty:
            st.markdown("---")
            st.header("📊 Progresso Real (dados do SIGA)")

            semana = calcular_semana_letiva()
            cap_esp = calcular_capitulo_esperado()

            total_aulas = len(df_prof_aulas)
            aulas_com_conteudo = len(df_prof_aulas[df_prof_aulas['conteudo'].notna() & (df_prof_aulas['conteudo'] != '')])
            aulas_com_tarefa = len(df_prof_aulas[df_prof_aulas['tarefa'].notna() & (df_prof_aulas['tarefa'] != '')])

            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Aulas Registradas", total_aulas)
            p2.metric("Com Conteúdo", f"{aulas_com_conteudo} ({round(aulas_com_conteudo/max(1,total_aulas)*100)}%)")
            p3.metric("Com Tarefa", f"{aulas_com_tarefa} ({round(aulas_com_tarefa/max(1,total_aulas)*100)}%)")
            p4.metric("Semana Atual / Cap Esperado", f"Sem {semana} / Cap {cap_esp}")

            # Últimas aulas
            with st.expander("📋 Últimas 10 aulas registradas"):
                cols_show = ['data', 'disciplina', 'serie', 'turma', 'conteudo', 'tarefa']
                cols_avail = [c for c in cols_show if c in df_prof_aulas.columns]
                st.dataframe(
                    df_prof_aulas.sort_values('data', ascending=False).head(10)[cols_avail],
                    use_container_width=True, hide_index=True
                )

    # ========== METAS POR TRIMESTRE ==========
    st.markdown("---")
    st.header("🎯 Metas por Trimestre")

    col_m1, col_m2, col_m3 = st.columns(3)

    with col_m1:
        st.markdown("""
        ### 1º Trimestre
        **Período:** 26/01 - 08/05

        | Meta | Detalhe |
        |------|---------|
        | Capítulos | 1 a 4 |
        | Volumes | V1 |
        | Trilhas | 4 trilhas |
        | Avaliações | A1 + A2 + Simulado |

        **Encontros estimados:** ~{} aulas
        """.format(int(encontros_trimestre * 1.1)))  # 1º tri tem mais dias

    with col_m2:
        st.markdown("""
        ### 2º Trimestre
        **Período:** 11/05 - 28/08

        | Meta | Detalhe |
        |------|---------|
        | Capítulos | 5 a 8 |
        | Volumes | V2 + V3 |
        | Trilhas | 4 trilhas |
        | Avaliações | A1 + A2 + Simulado |

        **Encontros estimados:** ~{} aulas
        """.format(int(encontros_trimestre * 0.9)))  # 2º tri tem férias

    with col_m3:
        st.markdown("""
        ### 3º Trimestre
        **Período:** 31/08 - 18/12

        | Meta | Detalhe |
        |------|---------|
        | Capítulos | 9 a 12 |
        | Volumes | V4 |
        | Trilhas | 4 trilhas |
        | Avaliações | A1 + A2 + Final |

        **Encontros estimados:** ~{} aulas
        """.format(encontros_trimestre))

    # ========== CALENDÁRIO ==========
    st.markdown("---")
    st.header("📅 Calendário de Progressão")

    df_calendario = gerar_calendario_professor(disciplina, aulas_semana, turmas)

    # Filtro de trimestre
    tri_filter = st.radio("Filtrar por trimestre:", ['Todos', '1º', '2º', '3º'], horizontal=True)

    if tri_filter != 'Todos':
        df_show = df_calendario[df_calendario['Tri'] == tri_filter]
    else:
        df_show = df_calendario

    st.dataframe(df_show, use_container_width=True, hide_index=True, height=400)

    # ========== MATERIAL PARA IMPRESSÃO ==========
    st.markdown("---")
    st.header("🖨️ Material para Impressão")

    st.info("Selecione o que deseja incluir no material imprimível e clique em 'Gerar Material'.")

    # Opções de conteúdo
    st.subheader("📋 Opções de Conteúdo")

    col_op1, col_op2 = st.columns(2)

    with col_op1:
        inc_visao_geral = st.checkbox("📊 Visão Geral do Ano", value=True)
        inc_metas = st.checkbox("🎯 Metas por Trimestre", value=True)
        inc_calendario = st.checkbox("📅 Calendário de Progressão", value=True)

    with col_op2:
        inc_feriados = st.checkbox("🗓️ Feriados e Recessos", value=True)
        inc_lembretes = st.checkbox("⚠️ Lembretes Importantes", value=True)
        inc_checkpoints = st.checkbox("📍 Checkpoints do Ano", value=True)

    # Opção de trimestres no calendário
    if inc_calendario:
        trimestres_cal = st.multiselect(
            "Incluir calendário de quais trimestres:",
            ['1º Trimestre', '2º Trimestre', '3º Trimestre'],
            default=['1º Trimestre', '2º Trimestre', '3º Trimestre']
        )
    else:
        trimestres_cal = []

    if st.button("📄 Gerar Material Completo", type="primary"):
        # Gera conteúdo para download
        conteudo = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PLANEJAMENTO INDIVIDUAL - COLÉGIO ELO 2026                ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PROFESSOR: {professor.upper()}
 DISCIPLINA: {disciplina}
 AULAS/SEMANA: {aulas_semana}
 TURMAS: {', '.join(turmas) if turmas else 'Ver com coordenação'}
 GERADO EM: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        # Visão Geral
        if inc_visao_geral:
            conteudo += f"""
================================================================================
                              📊 VISÃO GERAL DO ANO
================================================================================

ENCONTROS ESTIMADOS NO ANO: {encontros_ano} aulas
(Já descontados feriados e eventos)

Por trimestre:
┌─────────────┬─────────────────┬──────────────┬──────────────┐
│ Trimestre   │ Período         │ Aulas Est.   │ Capítulos    │
├─────────────┼─────────────────┼──────────────┼──────────────┤
│ 1º          │ 26/01 - 08/05   │ ~{int(encontros_trimestre * 1.1):3d}         │ 1 a 4        │
│ 2º          │ 11/05 - 28/08   │ ~{int(encontros_trimestre * 0.9):3d}         │ 5 a 8        │
│ 3º          │ 31/08 - 18/12   │ ~{encontros_trimestre:3d}         │ 9 a 12       │
└─────────────┴─────────────────┴──────────────┴──────────────┘

"""

        # Metas por Trimestre
        if inc_metas:
            conteudo += f"""
================================================================================
                           🎯 METAS POR TRIMESTRE
================================================================================

┌──────────────────────────────────────────────────────────────────────────────┐
│                            1º TRIMESTRE                                      │
│                         (26/01 - 08/05)                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Capítulos: 1 a 4 (Volume 1)                                                │
│ • Trilhas digitais: 4 trilhas                                                │
│ • Avaliações: A1 (semanas 7-8), A2 (semanas 11-12), Simulado                 │
│ • Encontros estimados: ~{int(encontros_trimestre * 1.1)} aulas{' '*(42-len(str(int(encontros_trimestre * 1.1))))}│
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                            2º TRIMESTRE                                      │
│                         (11/05 - 28/08)                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Capítulos: 5 a 8 (Volumes 2 e 3)                                           │
│ • Trilhas digitais: 4 trilhas                                                │
│ • Avaliações: A1, A2, Simulado                                               │
│ • Encontros estimados: ~{int(encontros_trimestre * 0.9)} aulas{' '*(42-len(str(int(encontros_trimestre * 0.9))))}│
│ • OBS: Inclui férias de julho (06-31/jul)                                    │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                            3º TRIMESTRE                                      │
│                         (31/08 - 18/12)                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Capítulos: 9 a 12 (Volume 4)                                               │
│ • Trilhas digitais: 4 trilhas                                                │
│ • Avaliações: A1, A2, Avaliação Final, Simulado                              │
│ • Encontros estimados: ~{encontros_trimestre} aulas{' '*(42-len(str(encontros_trimestre)))}│
└──────────────────────────────────────────────────────────────────────────────┘

"""

        # Calendário de Progressão
        if inc_calendario:
            if '1º Trimestre' in trimestres_cal:
                conteudo += """
================================================================================
                   📅 CALENDÁRIO DE PROGRESSÃO - 1º TRIMESTRE
================================================================================

  Sem │  Período      │ Cap │ Aulas │ Eventos/Observações
  ────┼───────────────┼─────┼───────┼────────────────────────────────────────
"""
                df_1tri = df_calendario[df_calendario['Tri'] == '1º']
                for _, row in df_1tri.iterrows():
                    conteudo += f"  {row['Semana']:2d}  │ {row['Período']:<13} │  {row['Capítulo']:2d} │  {row['Aulas Esperadas']:2d}   │ {row['Eventos']}\n"

            if '2º Trimestre' in trimestres_cal:
                conteudo += """

================================================================================
                   📅 CALENDÁRIO DE PROGRESSÃO - 2º TRIMESTRE
================================================================================

  Sem │  Período      │ Cap │ Aulas │ Eventos/Observações
  ────┼───────────────┼─────┼───────┼────────────────────────────────────────
"""
                df_2tri = df_calendario[df_calendario['Tri'] == '2º']
                for _, row in df_2tri.iterrows():
                    conteudo += f"  {row['Semana']:2d}  │ {row['Período']:<13} │  {row['Capítulo']:2d} │  {row['Aulas Esperadas']:2d}   │ {row['Eventos']}\n"

            if '3º Trimestre' in trimestres_cal:
                conteudo += """

================================================================================
                   📅 CALENDÁRIO DE PROGRESSÃO - 3º TRIMESTRE
================================================================================

  Sem │  Período      │ Cap │ Aulas │ Eventos/Observações
  ────┼───────────────┼─────┼───────┼────────────────────────────────────────
"""
                df_3tri = df_calendario[df_calendario['Tri'] == '3º']
                for _, row in df_3tri.iterrows():
                    conteudo += f"  {row['Semana']:2d}  │ {row['Período']:<13} │  {row['Capítulo']:2d} │  {row['Aulas Esperadas']:2d}   │ {row['Eventos']}\n"

        # Checkpoints
        if inc_checkpoints:
            conteudo += """

================================================================================
                        📍 CHECKPOINTS DO ANO
================================================================================

Onde você deve estar em cada momento:

  Semana │ Mês  │ Capítulo │ Observação
  ───────┼──────┼──────────┼─────────────────────────────────────────
     7   │ Mar  │    2     │ Capítulo 2 concluído
    14   │ Mai  │    4     │ Capítulo 4 concluído - FIM 1º TRIMESTRE
    21   │ Jun  │    6     │ Capítulo 6 concluído
    28   │ Ago  │    8     │ Capítulo 8 concluído - FIM 2º TRIMESTRE
    35   │ Out  │   10     │ Capítulo 10 concluído
    42   │ Dez  │   12     │ Capítulo 12 concluído - FIM DO ANO

FÓRMULA DE PROGRESSÃO:
Capítulo esperado = Semana letiva ÷ 3.5 (arredondado para cima)

Exemplo: Semana 10 → 10÷3.5 = 2.86 → Capítulo 3

"""

        # Feriados
        if inc_feriados:
            conteudo += """
================================================================================
                              🗓️ FERIADOS 2026
================================================================================

NACIONAIS:
  • 14-17/02: Carnaval (4 dias)
  • 21/04: Tiradentes
  • 01/05: Dia do Trabalho
  • 04/06: Corpus Christi
  • 07/09: Independência
  • 12/10: N.S. Aparecida
  • 02/11: Finados
  • 15/11: Proclamação da República
  • 20/11: Consciência Negra

REGIONAIS (Pernambuco):
  • 06/03: Data Magna de Pernambuco
  • 24/06: São João

ESPECÍFICO (Apenas Candeias):
  • 13/04: Feriado de Jaboatão dos Guararapes

RECESSO:
  • 06-31/07: Férias de Julho

"""

        # Lembretes
        if inc_lembretes:
            conteudo += """
================================================================================
                           ⚠️ LEMBRETES IMPORTANTES
================================================================================

1. Registre TODAS as aulas no SIGA diariamente
2. Descreva o conteúdo trabalhado (capítulo, seção)
3. Registre as tarefas atribuídas aos alunos
4. Aplique as trilhas digitais após cada capítulo
5. Comunique atrasos à coordenação com antecedência
6. Mantenha o material SAE como base principal
7. Atraso de 2+ capítulos: comunicar coordenação IMEDIATAMENTE

REGISTROS NO SIGA:
  ✓ Preencha o campo CONTEÚDO com o que foi trabalhado
  ✓ Preencha o campo TAREFA com atividades passadas
  ✓ Registre no mesmo dia da aula

"""

        # Rodapé
        conteudo += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                           Colégio ELO - 2026
              "Construindo conhecimento com excelência e valores"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # Exibe prévia
        st.subheader("📄 Prévia do Material")
        st.code(conteudo, language=None)

        # Botões de download
        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            st.download_button(
                label="📥 Baixar Material Completo (TXT)",
                data=conteudo,
                file_name=f"planejamento_{professor.replace(' ', '_')}_{disciplina}.txt",
                mime="text/plain"
            )

        with col_dl2:
            # Botão de impressão
            st.markdown("""
            <button onclick="window.print()" style="
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 5px;
            ">🖨️ Imprimir Esta Página</button>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
