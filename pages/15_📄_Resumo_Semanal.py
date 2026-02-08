#!/usr/bin/env python3
"""
PÁGINA 15: RESUMO SEMANAL
Gera relatório semanal para reuniões de coordenação e compartilhamento via WhatsApp.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import math
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    carregar_fato_aulas, carregar_horario_esperado, carregar_progressao_sae,
    filtrar_ate_hoje, filtrar_por_periodo, PERIODOS_OPCOES,
    _hoje, DATA_DIR, UNIDADES_NOMES, ORDEM_SERIES,
    SERIES_FUND_II, SERIES_EM, INICIO_ANO_LETIVO,
    CONFORMIDADE_META, CONFORMIDADE_BAIXO,
)
from auth import check_password, logout_button, get_user_unit

st.set_page_config(page_title="Resumo Semanal", page_icon="📄", layout="wide")
if not check_password():
    st.stop()
logout_button()


def calcular_metricas_unidade(df_aulas, df_horario, semana):
    """Calcula metricas resumidas por unidade."""
    resultados = []
    unidades = sorted(df_aulas['unidade'].unique())

    for un in unidades:
        df_un = df_aulas[df_aulas['unidade'] == un]
        df_hor_un = df_horario[df_horario['unidade'] == un]

        total_aulas = len(df_un)
        profs_ativos = df_un['professor'].nunique()
        disciplinas = df_un['disciplina'].nunique()
        series = df_un['serie'].nunique()

        # Conformidade
        esperado = len(df_hor_un) * semana
        conf = (total_aulas / esperado * 100) if esperado > 0 else 0

        # Aulas na semana atual
        inicio_semana = INICIO_ANO_LETIVO + timedelta(weeks=semana - 1)
        fim_semana = inicio_semana + timedelta(days=6)
        aulas_semana = len(df_un[
            (df_un['data'] >= inicio_semana) & (df_un['data'] <= fim_semana)
        ])

        # Conteudo preenchido
        com_conteudo = df_un['conteudo'].notna().sum()
        taxa_conteudo = (com_conteudo / total_aulas * 100) if total_aulas > 0 else 0

        # Slots sem registro na semana (compara combinações serie+disciplina)
        slots_esperados = set(df_hor_un.groupby(['serie', 'disciplina']).size().index)
        df_un_sem = df_un[(df_un['data'] >= inicio_semana) & (df_un['data'] <= fim_semana)]
        slots_com_aula = set(df_un_sem.groupby(['serie', 'disciplina']).size().index) if not df_un_sem.empty else set()
        profs_sem = len(slots_esperados - slots_com_aula)

        resultados.append({
            'unidade': un,
            'nome': UNIDADES_NOMES.get(un, un),
            'aulas_total': total_aulas,
            'aulas_semana': aulas_semana,
            'profs_ativos': profs_ativos,
            'profs_sem_registro': profs_sem,
            'disciplinas': disciplinas,
            'series': series,
            'conformidade': round(conf, 1),
            'taxa_conteudo': round(taxa_conteudo, 1),
        })

    return pd.DataFrame(resultados)


def gerar_resumo_texto(semana, cap_esperado, trimestre, df_metricas, df_aulas, df_prog):
    """Gera texto formatado para WhatsApp/reunião."""
    hoje = _hoje()
    inicio_semana = INICIO_ANO_LETIVO + timedelta(weeks=semana - 1)
    fim_semana = inicio_semana + timedelta(days=4)  # Seg-Sex

    linhas = [
        f"*RESUMO SEMANAL - COLÉGIO ELO*",
        f"Semana {semana} | {inicio_semana.strftime('%d/%m')} a {fim_semana.strftime('%d/%m/%Y')}",
        f"Cap. esperado: {cap_esperado}/12 | {trimestre}º Trimestre",
        "",
        "=" * 40,
        "",
    ]

    # Por unidade
    for _, row in df_metricas.iterrows():
        # Emoji de status
        if row['conformidade'] >= CONFORMIDADE_META:
            emoji = '🟢'
        elif row['conformidade'] >= CONFORMIDADE_BAIXO:
            emoji = '🟡'
        else:
            emoji = '🔴'

        linhas.append(f"{emoji} *{row['nome']}*")
        linhas.append(f"   Conformidade: {row['conformidade']:.0f}%")
        linhas.append(f"   Aulas total: {row['aulas_total']} | Esta semana: {row['aulas_semana']}")
        linhas.append(f"   Professores ativos: {row['profs_ativos']}")
        if row['profs_sem_registro'] > 0:
            linhas.append(f"   ⚠️ {row['profs_sem_registro']} disciplina(s)/série(s) sem registro na semana")
        linhas.append(f"   Conteúdo preenchido: {row['taxa_conteudo']:.0f}%")
        linhas.append("")

    # Totais
    linhas.append("-" * 40)
    total_aulas = df_metricas['aulas_total'].sum()
    total_semana = df_metricas['aulas_semana'].sum()
    total_profs = df_metricas['profs_ativos'].sum()
    conf_media = df_metricas['conformidade'].mean()

    linhas.append(f"*REDE TOTAL:*")
    linhas.append(f"  Aulas: {total_aulas} (semana: {total_semana})")
    linhas.append(f"  Professores: {total_profs}")
    linhas.append(f"  Conformidade média: {conf_media:.0f}%")
    linhas.append("")

    # Progressao
    if not df_prog.empty and not df_aulas.empty:
        linhas.append("*PROGRESSÃO SAE:*")
        linhas.append(f"  Semana {semana} → Capítulo {cap_esperado}")
        pct_ano = round(semana / 42 * 100)
        linhas.append(f"  Progresso no ano: {pct_ano}%")
        linhas.append("")

    # Alertas rápidos
    linhas.append("*PONTOS DE ATENÇÃO:*")
    for _, row in df_metricas.iterrows():
        if row['conformidade'] < CONFORMIDADE_BAIXO:
            linhas.append(f"  🔴 {row['nome']}: conformidade {row['conformidade']:.0f}%")
        if row['profs_sem_registro'] > 3:
            linhas.append(f"  ⚠️ {row['nome']}: {row['profs_sem_registro']} disc/série sem registro")

    linhas.append("")
    linhas.append(f"_Gerado em {hoje.strftime('%d/%m/%Y %H:%M')}_")
    linhas.append(f"_Sistema Pedagógico ELO 2026_")

    return '\n'.join(linhas)


def gerar_resumo_reuniao(semana, cap_esperado, trimestre, df_metricas, df_aulas, df_horario):
    """Gera relatório detalhado para reunião de coordenação."""
    hoje = _hoje()
    inicio_semana = INICIO_ANO_LETIVO + timedelta(weeks=semana - 1)
    fim_semana = inicio_semana + timedelta(days=4)

    linhas = [
        "RELATÓRIO SEMANAL DE COORDENAÇÃO",
        f"Colégio ELO - Semana {semana} ({inicio_semana.strftime('%d/%m')} a {fim_semana.strftime('%d/%m/%Y')})",
        f"Capítulo esperado: {cap_esperado}/12 | {trimestre}º Trimestre",
        f"Gerado em: {hoje.strftime('%d/%m/%Y %H:%M')}",
        "=" * 70,
        "",
    ]

    # Visao geral
    linhas.append("1. VISÃO GERAL DA REDE")
    linhas.append("-" * 70)
    linhas.append(f"{'Unidade':<15} {'Conf.':>6} {'Aulas':>6} {'Semana':>7} {'Profs':>6} {'Conteúdo':>9}")
    linhas.append("-" * 70)
    for _, row in df_metricas.iterrows():
        linhas.append(
            f"{row['nome']:<15} {row['conformidade']:>5.0f}% {row['aulas_total']:>6} "
            f"{row['aulas_semana']:>7} {row['profs_ativos']:>6} {row['taxa_conteudo']:>8.0f}%"
        )
    linhas.append("-" * 70)
    linhas.append(
        f"{'TOTAL':<15} {df_metricas['conformidade'].mean():>5.0f}% "
        f"{df_metricas['aulas_total'].sum():>6} {df_metricas['aulas_semana'].sum():>7} "
        f"{df_metricas['profs_ativos'].sum():>6} {df_metricas['taxa_conteudo'].mean():>8.0f}%"
    )
    linhas.append("")

    # Detalhamento por unidade
    linhas.append("2. DETALHAMENTO POR UNIDADE")
    linhas.append("=" * 70)

    for un in sorted(df_aulas['unidade'].unique()):
        nome_un = UNIDADES_NOMES.get(un, un)
        df_un = df_aulas[df_aulas['unidade'] == un]
        linhas.append(f"\n--- {nome_un} ---")

        # Por serie
        for serie in ORDEM_SERIES:
            df_s = df_un[df_un['serie'] == serie]
            if df_s.empty:
                continue
            aulas_s = len(df_s)
            discs = df_s['disciplina'].nunique()
            profs_s = df_s['professor'].nunique()
            linhas.append(f"  {serie}: {aulas_s} aulas, {discs} disciplinas, {profs_s} professores")

        # Top conteudos registrados na semana
        df_sem = df_un[
            (df_un['data'] >= inicio_semana) & (df_un['data'] <= fim_semana)
        ]
        if not df_sem.empty:
            linhas.append(f"\n  Registros na semana {semana}:")
            for disc in sorted(df_sem['disciplina'].unique()):
                n = len(df_sem[df_sem['disciplina'] == disc])
                linhas.append(f"    - {disc}: {n} aulas")
        linhas.append("")

    # Disciplinas/séries sem registro na semana
    linhas.append("3. DISCIPLINAS SEM REGISTRO NA SEMANA")
    linhas.append("-" * 70)

    for un in sorted(df_aulas['unidade'].unique()):
        nome_un = UNIDADES_NOMES.get(un, un)
        df_hor_un = df_horario[df_horario['unidade'] == un]
        slots_esperados = set(df_hor_un.groupby(['serie', 'disciplina']).size().index)

        df_un_sem = df_aulas[
            (df_aulas['unidade'] == un) &
            (df_aulas['data'] >= inicio_semana) &
            (df_aulas['data'] <= fim_semana)
        ]
        slots_com = set(df_un_sem.groupby(['serie', 'disciplina']).size().index) if not df_un_sem.empty else set()
        slots_sem = sorted(slots_esperados - slots_com)

        if slots_sem:
            linhas.append(f"\n  {nome_un} ({len(slots_sem)} disciplinas/séries):")
            for (serie, disc) in slots_sem[:15]:
                linhas.append(f"    - {disc} ({serie})")
            if len(slots_sem) > 15:
                linhas.append(f"    ... e mais {len(slots_sem) - 15}")

    linhas.append("")
    linhas.append("=" * 70)
    linhas.append(f"Relatório gerado automaticamente - Sistema Pedagógico ELO 2026")

    return '\n'.join(linhas)


def main():
    st.title("📄 Resumo Semanal")
    st.markdown("**Relatório para reuniões de coordenação e compartilhamento**")

    semana_atual = calcular_semana_letiva()
    cap_esperado = calcular_capitulo_esperado(semana_atual)
    trimestre = calcular_trimestre(semana_atual)

    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()
    df_prog = carregar_progressao_sae()

    if df_aulas.empty or df_horario.empty:
        st.warning("Dados não carregados. Execute a extração do SIGA primeiro.")
        return

    df_aulas = filtrar_ate_hoje(df_aulas)

    # Filtro de unidade e periodo
    user_unit = get_user_unit()
    unidades = sorted(df_aulas['unidade'].unique())
    opcoes = ['Toda a Rede'] + unidades

    default_idx = 0
    if user_unit and user_unit in unidades:
        default_idx = opcoes.index(user_unit)

    col_cfg1, col_cfg2, col_cfg3 = st.columns([2, 1, 1])
    with col_cfg1:
        un_sel = st.selectbox("Unidade:", opcoes, index=default_idx)
    with col_cfg2:
        semana_sel = st.number_input("Semana:", min_value=1, max_value=42, value=semana_atual)
    with col_cfg3:
        periodo_sel = st.selectbox("Período:", PERIODOS_OPCOES, key='periodo_15')

    df_aulas = filtrar_por_periodo(df_aulas, periodo_sel)

    # Filtra por unidade
    df_f = df_aulas.copy()
    df_h = df_horario.copy()
    if un_sel != 'Toda a Rede':
        df_f = df_f[df_f['unidade'] == un_sel]
        df_h = df_h[df_h['unidade'] == un_sel]

    # Calcula metricas
    df_metricas = calcular_metricas_unidade(df_f, df_h, semana_sel)

    if df_metricas.empty:
        st.info("Nenhum dado para a seleção.")
        return

    # ========== VISAO RAPIDA ==========
    st.markdown("---")
    st.header(f"Semana {semana_sel} - Visão Rápida")

    # Cards
    col1, col2, col3, col4 = st.columns(4)
    total_aulas = int(df_metricas['aulas_total'].sum())
    total_semana = int(df_metricas['aulas_semana'].sum())
    conf_media = df_metricas['conformidade'].mean()
    total_profs = int(df_metricas['profs_ativos'].sum())

    with col1:
        st.metric("Aulas Totais", f"{total_aulas:,}")
    with col2:
        st.metric("Aulas na Semana", f"{total_semana}")
    with col3:
        st.metric("Conformidade Média", f"{conf_media:.0f}%")
    with col4:
        st.metric("Professores Ativos", f"{total_profs}")

    # Tabela por unidade
    st.subheader("Por Unidade")
    df_show = df_metricas[[
        'nome', 'conformidade', 'aulas_total', 'aulas_semana',
        'profs_ativos', 'profs_sem_registro', 'taxa_conteudo'
    ]].rename(columns={
        'nome': 'Unidade',
        'conformidade': 'Conformidade %',
        'aulas_total': 'Aulas Total',
        'aulas_semana': 'Aulas Semana',
        'profs_ativos': 'Professores',
        'profs_sem_registro': 'Slots s/ Registro',
        'taxa_conteudo': 'Conteúdo %',
    })
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    # ========== EXPORTAR ==========
    st.markdown("---")
    st.header("📥 Exportar Resumo")

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        st.subheader("WhatsApp")
        st.caption("Formato compacto para compartilhar no grupo")
        resumo_whats = gerar_resumo_texto(
            semana_sel, calcular_capitulo_esperado(semana_sel),
            calcular_trimestre(semana_sel), df_metricas, df_f, df_prog
        )
        st.download_button(
            "Baixar para WhatsApp (TXT)",
            resumo_whats,
            f"resumo_whatsapp_sem{semana_sel}.txt",
            "text/plain",
            key="btn_whats"
        )

    with col_e2:
        st.subheader("Reunião")
        st.caption("Relatório completo para reunião de coordenação")
        resumo_reuniao = gerar_resumo_reuniao(
            semana_sel, calcular_capitulo_esperado(semana_sel),
            calcular_trimestre(semana_sel), df_metricas, df_f, df_h
        )
        st.download_button(
            "Baixar Relatório (TXT)",
            resumo_reuniao,
            f"relatorio_coordenacao_sem{semana_sel}.txt",
            "text/plain",
            key="btn_reuniao"
        )

    with col_e3:
        st.subheader("Dados")
        st.caption("Métricas em CSV para análise")
        csv_data = df_metricas.to_csv(index=False)
        st.download_button(
            "Baixar Métricas (CSV)",
            csv_data,
            f"metricas_sem{semana_sel}.csv",
            "text/csv",
            key="btn_csv"
        )

    # ========== PREVIEW ==========
    st.markdown("---")

    tab1, tab2 = st.tabs(["Preview WhatsApp", "Preview Reunião"])

    with tab1:
        st.code(resumo_whats, language=None)

    with tab2:
        st.code(resumo_reuniao, language=None)


if __name__ == "__main__":
    main()
