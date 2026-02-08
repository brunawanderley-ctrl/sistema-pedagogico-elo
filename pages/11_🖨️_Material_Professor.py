#!/usr/bin/env python3
"""
PÁGINA 11: MATERIAL IMPRIMÍVEL POR PROFESSOR
Gera relatórios individuais para cada professor, filtrados por unidade
Com opção de visualização: Semanal, Mensal ou Trimestral
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import math
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre, carregar_fato_aulas, carregar_horario_esperado, DATA_DIR

st.set_page_config(page_title="Material do Professor", page_icon="🖨️", layout="wide")
from auth import check_password, logout_button
if not check_password():
    st.stop()
logout_button()

# Datas de início de cada semana letiva
INICIO_ANO = datetime(2026, 1, 26)
SEMANAS_DATAS = {
    1: "26/01", 2: "02/02", 3: "09/02", 4: "16/02", 5: "23/02",
    6: "02/03", 7: "09/03", 8: "16/03", 9: "23/03", 10: "30/03",
    11: "06/04", 12: "13/04", 13: "20/04", 14: "27/04",
    15: "11/05", 16: "18/05", 17: "25/05", 18: "01/06", 19: "08/06",
    20: "15/06", 21: "22/06", 22: "29/06", 23: "03/08", 24: "10/08",
    25: "17/08", 26: "24/08", 27: "31/08", 28: "07/09",
    29: "14/09", 30: "21/09", 31: "28/09", 32: "05/10", 33: "12/10",
    34: "19/10", 35: "26/10", 36: "02/11", 37: "09/11", 38: "16/11",
    39: "23/11", 40: "30/11", 41: "07/12", 42: "14/12"
}

EVENTOS_SEMANA = {
    1: "Adaptação",
    2: "Diagnose",
    3: "Elo Folia",
    4: "Pós-Carnaval",
    7: "Avaliações A1",
    8: "Avaliações A1",
    10: "Semana Santa",
    11: "Avaliações A2",
    12: "Feriado Jaboatão (CD)",
    13: "Tiradentes",
    14: "Recuperação 1ºTri",
    23: "Retorno Férias",
    28: "Recuperação 2ºTri",
    42: "Encerramento"
}

def get_trimestre(semana):
    """Retorna o trimestre de uma semana."""
    if semana <= 14:
        return 1
    elif semana <= 28:
        return 2
    else:
        return 3

def gerar_tabela_semanal(semana_inicio, semana_fim, aulas_por_semana):
    """Gera tabela semana a semana."""
    linhas = []
    for sem in range(semana_inicio, semana_fim + 1):
        cap = calcular_capitulo_esperado(sem)
        data = SEMANAS_DATAS.get(sem, "")
        evento = EVENTOS_SEMANA.get(sem, "-")
        aulas_esperadas = aulas_por_semana

        linhas.append(f"  {sem:3d}  │ {data:>5s} │   {cap:2d}    │ {aulas_esperadas:3d} aulas │ {evento}")

    return linhas

def gerar_conteudo_professor(prof_nome, df_aulas_prof, df_horario_prof, semana_atual, visualizacao,
                              incluir_conteudo=False, incluir_tarefa=False):
    """Gera o conteúdo textual do relatório do professor."""

    cap_esperado = calcular_capitulo_esperado(semana_atual)
    trimestre = get_trimestre(semana_atual)

    # Informações gerais - prioriza dados reais de aulas
    if len(df_aulas_prof) > 0:
        unidades = ', '.join(df_aulas_prof['unidade'].dropna().unique())
        disciplinas = ', '.join(df_aulas_prof['disciplina'].dropna().unique())
        turmas_list = df_aulas_prof['turma'].dropna().unique()
    elif len(df_horario_prof) > 0:
        unidades = ', '.join(df_horario_prof['unidade'].unique())
        disciplinas = ', '.join(df_horario_prof['disciplina'].unique())
        turmas_list = df_horario_prof['turma'].unique()
    else:
        unidades = 'N/A'
        disciplinas = 'N/A'
        turmas_list = []

    turmas = ', '.join(turmas_list) if len(turmas_list) <= 5 else f"{len(turmas_list)} turmas"

    # Cálculos - usa horário se disponível, senão estima pelos dados
    if len(df_horario_prof) > 0:
        aulas_por_semana = len(df_horario_prof)
    else:
        # Estima pela média de aulas registradas
        aulas_por_semana = max(1, len(df_aulas_prof) // max(1, semana_atual))

    aulas_esperadas = aulas_por_semana * semana_atual
    aulas_registradas = len(df_aulas_prof)
    conformidade = (aulas_registradas / aulas_esperadas * 100) if aulas_esperadas > 0 else 0

    # Cabeçalho
    conteudo = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RELATÓRIO INDIVIDUAL DO PROFESSOR                         ║
║                         COLÉGIO ELO - SAE 2026                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PROFESSOR(A): {prof_nome.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 INFORMAÇÕES GERAIS
─────────────────────────────────────────────────────────────────────────────
  Unidade(s):    {unidades}
  Disciplina(s): {disciplinas}
  Turma(s):      {turmas}
  Aulas/Semana:  {aulas_por_semana}
  Gerado em:     {datetime.now().strftime('%d/%m/%Y às %H:%M')}

📊 STATUS ATUAL (Semana {semana_atual} - {trimestre}º Trimestre)
─────────────────────────────────────────────────────────────────────────────
  ✓ Capítulo esperado agora:  {cap_esperado} de 12
  ✓ Aulas esperadas até agora: {aulas_esperadas}
  ✓ Aulas registradas:         {aulas_registradas}
  ✓ Taxa de conformidade:      {conformidade:.1f}%

  Status: {'✅ EXCELENTE' if conformidade >= 95 else '✓ BOM' if conformidade >= 85 else '⚠️ ATENÇÃO' if conformidade >= 70 else '❌ CRÍTICO'}

"""

    # ========== VISUALIZAÇÃO SEMANAL ==========
    if visualizacao == "Semanal":
        conteudo += f"""📅 PROGRESSÃO SEMANAL - {trimestre}º TRIMESTRE (Semana a Semana)
─────────────────────────────────────────────────────────────────────────────
  Sem  │ Data  │ Capítulo │ Esperado  │ Evento
  ─────┼───────┼──────────┼───────────┼─────────────────────────────
"""
        if trimestre == 1:
            sem_inicio, sem_fim = 1, 14
        elif trimestre == 2:
            sem_inicio, sem_fim = 15, 28
        else:
            sem_inicio, sem_fim = 29, 42

        for sem in range(sem_inicio, sem_fim + 1):
            cap = calcular_capitulo_esperado(sem)
            data = SEMANAS_DATAS.get(sem, "")
            evento = EVENTOS_SEMANA.get(sem, "-")
            marcador = " 👉" if sem == semana_atual else ""
            conteudo += f"  {sem:3d}  │ {data:>5s} │    {cap:2d}    │ {aulas_por_semana:3d} aulas │ {evento}{marcador}\n"

    # ========== VISUALIZAÇÃO MENSAL ==========
    elif visualizacao == "Mensal":
        conteudo += f"""📅 PROGRESSÃO MENSAL - ANO 2026
─────────────────────────────────────────────────────────────────────────────
  Mês        │ Semanas │ Capítulos │ Aulas Esp. │ Observações
  ───────────┼─────────┼───────────┼────────────┼─────────────────────────
"""
        meses = [
            ("Janeiro", "1", "1", 1, "Início - Adaptação"),
            ("Fevereiro", "2-5", "1-2", 4, "Carnaval + Elo Folia"),
            ("Março", "6-9", "2-3", 4, "Avaliações A1"),
            ("Abril", "10-13", "3-4", 4, "Semana Santa + A2"),
            ("Maio", "14-17", "4-5", 4, "Fechamento 1ºTri + Início 2ºTri"),
            ("Junho", "18-21", "5-6", 4, "São João"),
            ("Julho", "22", "6-7", 1, "Férias (1 semana letiva)"),
            ("Agosto", "23-27", "7-8", 5, "Retorno + A1 2ºTri"),
            ("Setembro", "28-31", "8-9", 4, "Fechamento 2ºTri"),
            ("Outubro", "32-35", "9-10", 4, "A1 3ºTri"),
            ("Novembro", "36-39", "10-11", 4, "A2 3ºTri"),
            ("Dezembro", "40-42", "11-12", 3, "Encerramento")
        ]

        for mes, semanas, caps, qtd_sem, obs in meses:
            aulas_mes = aulas_por_semana * qtd_sem
            conteudo += f"  {mes:10s} │  {semanas:5s}  │    {caps:5s}  │ {aulas_mes:4d} aulas │ {obs}\n"

    # ========== VISUALIZAÇÃO TRIMESTRAL ==========
    else:  # Trimestral
        conteudo += f"""📅 PROGRESSÃO TRIMESTRAL - ANO 2026
─────────────────────────────────────────────────────────────────────────────
"""
        trimestres_info = [
            (1, "1-14", "1 a 4", "26/01 - 08/05", "Adaptação, A1, A2, Simulado"),
            (2, "15-28", "5 a 8", "11/05 - 28/08", "Férias Julho, A1, A2, Simulado"),
            (3, "29-42", "9 a 12", "31/08 - 21/12", "A1, A2, Final, Simulado")
        ]

        for tri, semanas, caps, periodo, avaliacoes in trimestres_info:
            aulas_tri = aulas_por_semana * 14
            marcador = " 👈 ATUAL" if tri == trimestre else ""
            conteudo += f"""
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ {tri}º TRIMESTRE{marcador:40s}│
  ├─────────────────────────────────────────────────────────────────────────┤
  │ Período:      {periodo:56s}│
  │ Semanas:      {semanas:56s}│
  │ Capítulos:    {caps:56s}│
  │ Aulas esp.:   {aulas_tri} aulas ({aulas_por_semana}/semana × 14 semanas){' '*(30-len(str(aulas_tri)))}│
  │ Avaliações:   {avaliacoes:56s}│
  └─────────────────────────────────────────────────────────────────────────┘
"""

    # Seção de conteúdos (expandida se solicitado)
    if incluir_conteudo:
        conteudo += f"""
📝 CONTEÚDOS REGISTRADOS NO DIÁRIO
─────────────────────────────────────────────────────────────────────────────
"""
        df_conteudos = df_aulas_prof[df_aulas_prof['conteudo'].notna() & (df_aulas_prof['conteudo'] != '')]
        if len(df_conteudos) > 0:
            df_conteudos = df_conteudos.sort_values('data', ascending=False)
            for _, row in df_conteudos.head(15).iterrows():
                data_str = row['data'].strftime('%d/%m') if pd.notna(row['data']) else ''
                disc = row.get('disciplina', '')[:15] if pd.notna(row.get('disciplina')) else ''
                turma = row.get('turma', '')[:10] if pd.notna(row.get('turma')) else ''
                cont_texto = str(row['conteudo'])[:55] + '...' if len(str(row['conteudo'])) > 55 else str(row['conteudo'])
                conteudo += f"  {data_str} | {disc:<15} | {turma:<10} | {cont_texto}\n"
            if len(df_conteudos) > 15:
                conteudo += f"\n  ... e mais {len(df_conteudos) - 15} registros\n"
        else:
            conteudo += "  (Nenhum conteúdo registrado ainda)\n"
    else:
        # Versão resumida
        ultimos_conteudos = df_aulas_prof[df_aulas_prof['conteudo'].notna()]['conteudo'].tail(5).tolist()
        conteudo += f"""
📝 ÚLTIMOS CONTEÚDOS REGISTRADOS
─────────────────────────────────────────────────────────────────────────────
"""
        if ultimos_conteudos:
            for i, cont in enumerate(ultimos_conteudos, 1):
                cont_truncado = cont[:65] + '...' if len(str(cont)) > 65 else cont
                conteudo += f"  {i}. {cont_truncado}\n"
        else:
            conteudo += "  (Nenhum conteúdo registrado ainda)\n"

    # Seção de tarefas (se solicitado)
    if incluir_tarefa:
        conteudo += f"""
📋 TAREFAS REGISTRADAS NO DIÁRIO
─────────────────────────────────────────────────────────────────────────────
"""
        df_tarefas = df_aulas_prof[df_aulas_prof['tarefa'].notna() & (df_aulas_prof['tarefa'] != '')]
        if len(df_tarefas) > 0:
            df_tarefas = df_tarefas.sort_values('data', ascending=False)
            for _, row in df_tarefas.head(15).iterrows():
                data_str = row['data'].strftime('%d/%m') if pd.notna(row['data']) else ''
                disc = row.get('disciplina', '')[:15] if pd.notna(row.get('disciplina')) else ''
                turma = row.get('turma', '')[:10] if pd.notna(row.get('turma')) else ''
                tarefa_texto = str(row['tarefa'])[:55] + '...' if len(str(row['tarefa'])) > 55 else str(row['tarefa'])
                conteudo += f"  {data_str} | {disc:<15} | {turma:<10} | {tarefa_texto}\n"
            if len(df_tarefas) > 15:
                conteudo += f"\n  ... e mais {len(df_tarefas) - 15} registros\n"
        else:
            conteudo += "  (Nenhuma tarefa registrada ainda)\n"

    # Pontos de verificação
    conteudo += f"""
📋 CHECKPOINTS DO ANO (onde você deve estar)
─────────────────────────────────────────────────────────────────────────────
  Semana  7 (Mar): Capítulo 2 concluído
  Semana 14 (Mai): Capítulo 4 concluído - Fim 1º Trimestre
  Semana 21 (Jun): Capítulo 6 concluído
  Semana 28 (Ago): Capítulo 8 concluído - Fim 2º Trimestre
  Semana 35 (Out): Capítulo 10 concluído
  Semana 42 (Dez): Capítulo 12 concluído - Fim do Ano

⚠️ LEMBRETES IMPORTANTES
─────────────────────────────────────────────────────────────────────────────
  • Fórmula: Capítulo = Semana ÷ 3,5 (arredondado para cima)
  • Cada capítulo deve levar aproximadamente 3-4 semanas
  • Registrar SEMPRE conteúdo E tarefa no diário SIGA
  • Aplicar Trilha Digital ao final de cada capítulo
  • Atraso de 2+ capítulos: comunicar coordenação imediatamente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    Coordenação Pedagógica - Colégio ELO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return conteudo


def gerar_relatorio_por_disciplina(prof_nome, df_aulas_prof, df_horario_prof, semana_atual,
                                    visualizacao, disciplina_sel, incluir_conteudo, incluir_tarefa):
    """Gera relatório detalhado por componente curricular (disciplina)."""

    cap_esperado = calcular_capitulo_esperado(semana_atual)
    trimestre = get_trimestre(semana_atual)

    # Cabeçalho
    conteudo = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║            RELATÓRIO POR COMPONENTE CURRICULAR - DIÁRIO DE CLASSE            ║
║                         COLÉGIO ELO - SAE 2026                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PROFESSOR(A): {prof_nome.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 INFORMAÇÕES GERAIS
─────────────────────────────────────────────────────────────────────────────
  Semana Atual:        {semana_atual}ª ({trimestre}º Trimestre)
  Capítulo Esperado:   {cap_esperado} de 12
  Gerado em:           {datetime.now().strftime('%d/%m/%Y às %H:%M')}

"""

    # Lista disciplinas a processar
    if disciplina_sel == 'TODAS':
        disciplinas = sorted(df_aulas_prof['disciplina'].dropna().unique())
    else:
        disciplinas = [disciplina_sel]

    # Processa cada disciplina
    for disc in disciplinas:
        df_disc = df_aulas_prof[df_aulas_prof['disciplina'] == disc]
        df_hor_disc = df_horario_prof[df_horario_prof['disciplina'] == disc] if len(df_horario_prof) > 0 else pd.DataFrame()

        # Turmas desta disciplina
        turmas = sorted(df_disc['turma'].dropna().unique())

        # Cálculo de aulas
        if len(df_hor_disc) > 0:
            aulas_esperadas = len(df_hor_disc) * semana_atual
        else:
            aulas_por_semana = max(1, len(df_disc) // max(1, semana_atual))
            aulas_esperadas = aulas_por_semana * semana_atual

        aulas_registradas = len(df_disc)
        conformidade = (aulas_registradas / aulas_esperadas * 100) if aulas_esperadas > 0 else 0

        conteudo += f"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ 📚 DISCIPLINA: {disc.upper():<62}│
├──────────────────────────────────────────────────────────────────────────────┤
│ Turma(s): {', '.join(turmas):<67}│
│ Aulas Registradas: {aulas_registradas:<3} | Esperadas: {aulas_esperadas:<3} | Conformidade: {conformidade:>5.1f}%{' '*(14)}│
│ Status: {'✅ OK' if conformidade >= 85 else ('⚠️ ATENÇÃO' if conformidade >= 70 else '❌ CRÍTICO'):<70}│
└──────────────────────────────────────────────────────────────────────────────┘
"""

        # Conteúdos da disciplina
        if incluir_conteudo:
            df_conteudos = df_disc[df_disc['conteudo'].notna() & (df_disc['conteudo'] != '')]
            conteudo += f"""
  📝 CONTEÚDOS REGISTRADOS ({disc})
  ─────────────────────────────────────────────────────────────────────────
"""
            if len(df_conteudos) > 0:
                df_conteudos = df_conteudos.sort_values('data', ascending=False)
                for _, row in df_conteudos.head(10).iterrows():
                    data_str = row['data'].strftime('%d/%m') if pd.notna(row['data']) else ''
                    turma = row.get('turma', '')[:12] if pd.notna(row.get('turma')) else ''
                    cont_texto = str(row['conteudo'])
                    # Quebra texto longo em múltiplas linhas
                    if len(cont_texto) > 60:
                        conteudo += f"  {data_str} | {turma:<12} |\n"
                        conteudo += f"    {cont_texto}\n"
                    else:
                        conteudo += f"  {data_str} | {turma:<12} | {cont_texto}\n"
                if len(df_conteudos) > 10:
                    conteudo += f"\n  ... e mais {len(df_conteudos) - 10} registros\n"
            else:
                conteudo += "  (Nenhum conteúdo registrado)\n"

        # Tarefas da disciplina
        if incluir_tarefa:
            df_tarefas = df_disc[df_disc['tarefa'].notna() & (df_disc['tarefa'] != '')]
            conteudo += f"""
  📋 TAREFAS REGISTRADAS ({disc})
  ─────────────────────────────────────────────────────────────────────────
"""
            if len(df_tarefas) > 0:
                df_tarefas = df_tarefas.sort_values('data', ascending=False)
                for _, row in df_tarefas.head(10).iterrows():
                    data_str = row['data'].strftime('%d/%m') if pd.notna(row['data']) else ''
                    turma = row.get('turma', '')[:12] if pd.notna(row.get('turma')) else ''
                    tarefa_texto = str(row['tarefa'])
                    if len(tarefa_texto) > 60:
                        conteudo += f"  {data_str} | {turma:<12} |\n"
                        conteudo += f"    {tarefa_texto}\n"
                    else:
                        conteudo += f"  {data_str} | {turma:<12} | {tarefa_texto}\n"
                if len(df_tarefas) > 10:
                    conteudo += f"\n  ... e mais {len(df_tarefas) - 10} registros\n"
            else:
                conteudo += "  (Nenhuma tarefa registrada)\n"

        conteudo += "\n"

    # Rodapé
    conteudo += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    Coordenação Pedagógica - Colégio ELO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return conteudo


def normalizar_nome(nome):
    """Normaliza nome de professor para comparação."""
    if pd.isna(nome):
        return ""
    # Remove sufixo do tipo "- BV - 2026"
    nome = str(nome).upper().strip()
    if " - " in nome:
        nome = nome.split(" - ")[0].strip()
    # Remove acentos e normaliza
    import unicodedata
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return nome

def criar_mapeamento_professores(df_aulas, df_horario):
    """Cria mapeamento entre nomes de professores de aulas e horário."""
    mapeamento = {}

    # Professores de aulas (nomes completos)
    profs_aulas = df_aulas['professor'].dropna().unique()
    # Professores de horário (nomes abreviados com sufixo)
    profs_horario = df_horario['professor'].dropna().unique()

    for prof_aula in profs_aulas:
        nome_norm_aula = normalizar_nome(prof_aula)
        palavras_aula = nome_norm_aula.split()[:2]  # Primeiras 2 palavras

        for prof_hor in profs_horario:
            nome_norm_hor = normalizar_nome(prof_hor)
            palavras_hor = nome_norm_hor.split()[:2]  # Primeiras 2 palavras

            # Verifica se as primeiras palavras coincidem
            if palavras_aula and palavras_hor:
                if palavras_aula[0] == palavras_hor[0]:  # Primeiro nome igual
                    if len(palavras_aula) > 1 and len(palavras_hor) > 1:
                        if palavras_aula[1] == palavras_hor[1]:  # Segundo nome igual
                            mapeamento[prof_aula] = prof_hor
                            break
                    else:
                        mapeamento[prof_aula] = prof_hor
                        break

    return mapeamento

def main():
    st.title("🖨️ Material Imprimível por Professor")
    st.markdown("**Gere relatórios individuais para entregar aos professores**")

    # Carrega dados
    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()

    if df_aulas.empty or df_horario.empty:
        st.error("Dados nao carregados. Execute a extracao do SIGA primeiro.")
        return

    from utils import filtrar_ate_hoje, _hoje
    hoje = _hoje()
    df_aulas = filtrar_ate_hoje(df_aulas)

    # Cria mapeamento entre nomes de professores
    mapeamento_profs = criar_mapeamento_professores(df_aulas, df_horario)

    # ========== FILTROS ==========
    st.markdown("---")
    st.header("🎯 Selecione os Filtros")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Usa unidades que têm aulas registradas
        unidades = sorted(df_aulas['unidade'].dropna().unique())
        unidade_sel = st.selectbox("🏫 Unidade:", unidades)

    with col2:
        segmentos = ['Todos', 'Anos Finais (6º-9º)', 'Ensino Médio (1ª-3ª)']
        segmento_sel = st.selectbox("📚 Segmento:", segmentos)

    with col3:
        visualizacao = st.selectbox("📅 Visualização:",
                                    ['Semanal', 'Mensal', 'Trimestral'],
                                    help="Escolha como mostrar a progressão no relatório")

    with col4:
        semana_atual = calcular_semana_letiva()
        st.metric("📅 Semana Atual", f"{semana_atual}ª")

    # Filtra por unidade
    df_horario_un = df_horario[df_horario['unidade'] == unidade_sel].copy()
    df_aulas_un = df_aulas[df_aulas['unidade'] == unidade_sel].copy()

    # Aplica filtro de segmento
    if segmento_sel == 'Anos Finais (6º-9º)':
        df_horario_un = df_horario_un[df_horario_un['serie'].str.contains('Ano', na=False)]
        df_aulas_un = df_aulas_un[df_aulas_un['serie'].str.contains('Ano', na=False)]
    elif segmento_sel == 'Ensino Médio (1ª-3ª)':
        df_horario_un = df_horario_un[df_horario_un['serie'].str.contains('Série|EM', na=False)]
        df_aulas_un = df_aulas_un[df_aulas_un['serie'].str.contains('Série|EM', na=False)]

    # Lista de professores da unidade (usa nomes de fato_Aulas que tem registros reais)
    professores = sorted(df_aulas_un['professor'].dropna().unique())

    # Debug info
    st.sidebar.markdown("---")
    st.sidebar.caption(f"📊 Debug: {len(df_aulas_un)} aulas, {len(professores)} professores")

    st.markdown("---")
    st.header(f"👨‍🏫 Professores - {unidade_sel} ({len(professores)} professores)")

    # ========== OPÇÕES DE GERAÇÃO ==========
    col_opt1, col_opt2 = st.columns(2)

    with col_opt1:
        modo = st.radio("Modo de geração:",
                       ['📄 Professor individual', '📚 Todos da unidade'],
                       horizontal=True)

    with col_opt2:
        tipo_relatorio = st.radio("Tipo de relatório:",
                                  ['📊 Resumo geral', '📖 Por componente curricular'],
                                  horizontal=True,
                                  help="Resumo: visão geral do professor. Por componente: detalhamento por disciplina.")

    # Opções adicionais
    st.markdown("##### Opções de detalhamento")
    col_det1, col_det2 = st.columns(2)

    with col_det1:
        incluir_conteudo = st.checkbox("📝 Incluir conteúdos registrados", value=False,
                                       help="Mostra o que o professor digitou no campo 'conteúdo' do diário")
    with col_det2:
        incluir_tarefa = st.checkbox("📋 Incluir tarefas registradas", value=False,
                                     help="Mostra as tarefas que o professor registrou no diário")

    if modo == '📄 Professor individual':
        prof_sel = st.selectbox("👤 Selecione o professor:", professores)

        # Se for por componente curricular, mostra seletor de disciplina
        if prof_sel and tipo_relatorio == '📖 Por componente curricular':
            disciplinas_prof = sorted(df_aulas_un[df_aulas_un['professor'] == prof_sel]['disciplina'].dropna().unique())
            disciplina_sel = st.selectbox("📚 Selecione a disciplina:", ['TODAS'] + list(disciplinas_prof))
        else:
            disciplina_sel = 'TODAS'

        if prof_sel:
            # Gera relatório individual
            df_aulas_prof = df_aulas_un[df_aulas_un['professor'] == prof_sel]

            # Usa mapeamento para encontrar dados do horário
            prof_horario = mapeamento_profs.get(prof_sel, None)
            if prof_horario:
                df_horario_prof = df_horario_un[df_horario_un['professor'] == prof_horario]
            else:
                df_horario_prof = pd.DataFrame()  # Sem correspondência no horário

            # Filtra por disciplina se necessário
            if tipo_relatorio == '📖 Por componente curricular' and disciplina_sel != 'TODAS':
                df_aulas_prof_filtrado = df_aulas_prof[df_aulas_prof['disciplina'] == disciplina_sel]
                df_horario_prof_filtrado = df_horario_prof[df_horario_prof['disciplina'] == disciplina_sel] if len(df_horario_prof) > 0 else df_horario_prof
            else:
                df_aulas_prof_filtrado = df_aulas_prof
                df_horario_prof_filtrado = df_horario_prof

            # Gera relatório
            if tipo_relatorio == '📊 Resumo geral':
                conteudo = gerar_conteudo_professor(prof_sel, df_aulas_prof_filtrado, df_horario_prof_filtrado,
                                                    semana_atual, visualizacao, incluir_conteudo, incluir_tarefa)
            else:
                # Por componente curricular
                conteudo = gerar_relatorio_por_disciplina(prof_sel, df_aulas_prof, df_horario_prof,
                                                          semana_atual, visualizacao, disciplina_sel,
                                                          incluir_conteudo, incluir_tarefa)

            # Preview
            st.markdown("---")
            st.subheader(f"📋 Prévia do Relatório ({visualizacao})")
            st.code(conteudo, language=None)

            # Download
            nome_arquivo = f"relatorio_{prof_sel.replace(' ', '_')}_{unidade_sel}"
            if tipo_relatorio == '📖 Por componente curricular' and disciplina_sel != 'TODAS':
                nome_arquivo += f"_{disciplina_sel.replace(' ', '_')}"
            nome_arquivo += f"_{visualizacao}_{datetime.now().strftime('%Y%m%d')}.txt"

            st.download_button(
                "📥 Baixar Relatório (TXT)",
                conteudo,
                nome_arquivo,
                "text/plain"
            )

    else:  # Todos da unidade
        st.markdown("---")
        st.subheader(f"📚 Gerar relatórios para todos os {len(professores)} professores de {unidade_sel}")
        st.info(f"Visualização: **{visualizacao}** | Tipo: **{tipo_relatorio}**")

        if st.button("🚀 Gerar Todos os Relatórios", type="primary"):
            with st.spinner("Gerando relatórios..."):
                todos_relatorios = []

                for prof in professores:
                    df_aulas_prof = df_aulas_un[df_aulas_un['professor'] == prof]

                    # Usa mapeamento para encontrar dados do horário
                    prof_horario = mapeamento_profs.get(prof, None)
                    if prof_horario:
                        df_horario_prof = df_horario_un[df_horario_un['professor'] == prof_horario]
                    else:
                        df_horario_prof = pd.DataFrame()

                    if tipo_relatorio == '📊 Resumo geral':
                        conteudo_rel = gerar_conteudo_professor(prof, df_aulas_prof, df_horario_prof,
                                                                semana_atual, visualizacao,
                                                                incluir_conteudo, incluir_tarefa)
                    else:
                        conteudo_rel = gerar_relatorio_por_disciplina(prof, df_aulas_prof, df_horario_prof,
                                                                       semana_atual, visualizacao, 'TODAS',
                                                                       incluir_conteudo, incluir_tarefa)
                    todos_relatorios.append({
                        'professor': prof,
                        'conteudo': conteudo_rel
                    })

                # Cria arquivo consolidado
                tipo_str = "RESUMO" if tipo_relatorio == '📊 Resumo geral' else "POR DISCIPLINA"
                arquivo_consolidado = f"""
{'='*80}
         RELATÓRIOS INDIVIDUAIS - {unidade_sel} - {datetime.now().strftime('%d/%m/%Y')}
         Total de professores: {len(professores)}
         Segmento: {segmento_sel}
         Visualização: {visualizacao}
         Tipo: {tipo_str}
         Conteúdos: {'Sim' if incluir_conteudo else 'Não'} | Tarefas: {'Sim' if incluir_tarefa else 'Não'}
{'='*80}

"""
                for rel in todos_relatorios:
                    arquivo_consolidado += rel['conteudo']
                    arquivo_consolidado += "\n\n" + "="*80 + "\n" + "═" * 30 + " PRÓXIMO PROFESSOR " + "═" * 30 + "\n" + "="*80 + "\n\n"

                st.success(f"✅ {len(todos_relatorios)} relatórios gerados!")

                st.download_button(
                    f"📥 Baixar Todos os Relatórios - {unidade_sel} (TXT)",
                    arquivo_consolidado,
                    f"relatorios_{unidade_sel}_{visualizacao}_{datetime.now().strftime('%Y%m%d')}.txt",
                    "text/plain"
                )

    # ========== TABELA RESUMO ==========
    st.markdown("---")
    st.header("📊 Resumo dos Professores")

    resumo = []
    for prof in professores:
        df_aulas_prof = df_aulas_un[df_aulas_un['professor'] == prof]

        # Usa mapeamento para encontrar dados do horário
        prof_horario = mapeamento_profs.get(prof, None)
        if prof_horario:
            df_horario_prof = df_horario_un[df_horario_un['professor'] == prof_horario]
        else:
            df_horario_prof = pd.DataFrame()

        # Calcula esperado baseado no horário OU estima pelo número de turmas/disciplinas
        if len(df_horario_prof) > 0:
            esperado = len(df_horario_prof) * semana_atual
            disciplinas = ', '.join(df_horario_prof['disciplina'].unique())
            turmas = df_horario_prof['turma'].nunique()
        else:
            # Sem correspondência no horário - usa dados das aulas
            disciplinas = ', '.join(df_aulas_prof['disciplina'].dropna().unique())
            turmas = df_aulas_prof['turma'].nunique()
            # Estima: aulas registradas / semana_atual = aulas por semana esperadas
            aulas_por_semana = max(1, len(df_aulas_prof) // max(1, semana_atual))
            esperado = aulas_por_semana * semana_atual

        registrado = len(df_aulas_prof)
        conf = (registrado / esperado * 100) if esperado > 0 else 0

        resumo.append({
            'Professor': prof,
            'Disciplinas': disciplinas[:30] + '...' if len(disciplinas) > 30 else disciplinas,
            'Turmas': turmas,
            'Registrado': registrado,
            'Esperado': esperado,
            'Conformidade': f'{conf:.0f}%',
            'Status': '✅' if conf >= 85 else ('⚠️' if conf >= 70 else '🔴')
        })

    df_resumo = pd.DataFrame(resumo)
    if not df_resumo.empty:
        df_resumo = df_resumo.sort_values('Conformidade', ascending=True)
    st.dataframe(df_resumo, use_container_width=True, hide_index=True)

    # Download da tabela
    csv = df_resumo.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📥 Exportar Tabela (CSV)",
        csv,
        f"resumo_professores_{unidade_sel}_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv"
    )

if __name__ == "__main__":
    main()
