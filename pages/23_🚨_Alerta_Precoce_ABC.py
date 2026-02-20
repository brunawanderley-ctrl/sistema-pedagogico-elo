#!/usr/bin/env python3
"""
PÁGINA 23: SISTEMA ABC DE ALERTA PRECOCE
Framework validado internacionalmente: Attendance + Behavior + Coursework.
Identifica alunos em risco ANTES que fracassem academicamente.

Baseado em pesquisa:
- Panorama Education (EWS)
- PBIS Framework
- US Dept of Education Early Warning Systems
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_UNIDADES, CORES_SERIES, ORDEM_SERIES
from utils import (
    calcular_semana_letiva, calcular_trimestre, calcular_capitulo_esperado,
    carregar_alunos, carregar_notas, carregar_frequencia_alunos,
    carregar_ocorrencias, carregar_fato_aulas, filtrar_ate_hoje,
    filtrar_por_periodo, _hoje,
    calcular_frequencia_aluno, status_frequencia,
    THRESHOLD_FREQUENCIA_LDB, PERIODOS_OPCOES,
    UNIDADES, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM,
)
from components import (
    filtro_unidade, filtro_segmento,
    aplicar_filtro_unidade, aplicar_filtro_segmento,
    cabecalho_pagina, metricas_em_colunas,
)

st.set_page_config(page_title="Alerta Precoce ABC", page_icon="🚨", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

st.markdown("""
<style>
    .abc-header {
        background: linear-gradient(135deg, #B71C1C 0%, #D32F2F 100%);
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 15px;
    }
    .tier3-card {
        background: #FFEBEE; border-left: 5px solid #B71C1C;
        padding: 15px; margin: 8px 0; border-radius: 5px;
    }
    .tier2-card {
        background: #FFF3E0; border-left: 5px solid #E65100;
        padding: 15px; margin: 8px 0; border-radius: 5px;
    }
    .tier1-card {
        background: #FFF8E1; border-left: 5px solid #F9A825;
        padding: 15px; margin: 8px 0; border-radius: 5px;
    }
    .abc-badge {
        display: inline-block; padding: 3px 10px; border-radius: 12px;
        font-weight: bold; font-size: 0.85em; margin: 2px;
    }
    .badge-a { background: #E3F2FD; color: #1565C0; }
    .badge-b { background: #FFF3E0; color: #E65100; }
    .badge-c { background: #F3E5F5; color: #7B1FA2; }
    .badge-ok { background: #E8F5E9; color: #2E7D32; }
    .badge-risco { background: #FFCDD2; color: #B71C1C; }
</style>
""", unsafe_allow_html=True)


# Thresholds ABC (baseados em pesquisa educacional)
ABC_THRESHOLDS = {
    'A': {'risco': 85, 'critico': 75},   # Frequência %
    'B': {'risco': 2, 'critico': 5},     # Ocorrências (num)
    'C': {'risco': 5.0, 'critico': 3.0}, # Média de notas
}


def calcular_score_abc(freq_pct, num_ocorrencias, media_notas):
    """
    Calcula score ABC e tier de risco.

    Retorna:
        flags: list de dimensoes com flag ('A', 'B', 'C')
        tier: 0 (universal), 1 (atencao), 2 (intervencao), 3 (intensivo)
        score: 0-100 (100 = risco maximo)
    """
    flags = []

    # A - Attendance (30% do score)
    if freq_pct < ABC_THRESHOLDS['A']['critico']:
        score_a = 100
        flags.append('A')
    elif freq_pct < ABC_THRESHOLDS['A']['risco']:
        score_a = 50
        flags.append('A')
    else:
        score_a = max(0, (100 - freq_pct) * 2)

    # B - Behavior (30% do score)
    if num_ocorrencias >= ABC_THRESHOLDS['B']['critico']:
        score_b = 100
        flags.append('B')
    elif num_ocorrencias >= ABC_THRESHOLDS['B']['risco']:
        score_b = 50
        flags.append('B')
    else:
        score_b = min(100, num_ocorrencias * 20)

    # C - Coursework (40% do score)
    if media_notas < ABC_THRESHOLDS['C']['critico']:
        score_c = 100
        flags.append('C')
    elif media_notas < ABC_THRESHOLDS['C']['risco']:
        score_c = 50
        flags.append('C')
    else:
        score_c = max(0, (10 - media_notas) * 10)

    score = score_a * 0.3 + score_b * 0.3 + score_c * 0.4

    # Tier baseado em numero de flags
    if len(flags) >= 3:
        tier = 3
    elif len(flags) >= 2:
        tier = 2
    elif len(flags) >= 1:
        tier = 1
    else:
        tier = 0

    return flags, tier, round(score, 1)


def main():
    cabecalho_pagina(
        "🚨 Sistema ABC de Alerta Precoce",
        "Framework: Attendance + Behavior + Coursework | Alunos em risco antes que fracassem",
    )

    hoje = _hoje()
    semana = calcular_semana_letiva(hoje)
    trimestre = calcular_trimestre(semana)

    # Carregar dados
    df_alunos = carregar_alunos()
    df_notas = carregar_notas()
    df_freq = carregar_frequencia_alunos()
    df_ocorr = carregar_ocorrencias()

    tem_alunos = not df_alunos.empty
    tem_notas = not df_notas.empty
    tem_freq = not df_freq.empty
    tem_ocorr = not df_ocorr.empty

    # Verificar dados minimos
    if not tem_alunos:
        st.warning("⚠️ Dados de alunos ainda não extraídos do SIGA.")
        _mostrar_explicacao_abc()
        _mostrar_preview_simulado()
        return

    # ========== FILTROS ==========
    n_cols = 3 if (tem_notas and 'ano' in df_notas.columns) else 2
    cols_f = st.columns(n_cols)
    with cols_f[0]:
        unidade_sel = filtro_unidade(
            todas_label="Todas", usar_nomes=True, key="pg23_un",
        )
    with cols_f[1]:
        segmento_sel = filtro_segmento(key="pg23_seg")

    # Filtro de ano para dados historicos
    ano_abc = None
    if tem_notas and 'ano' in df_notas.columns:
        with cols_f[2]:
            anos_disp = sorted(df_notas['ano'].dropna().unique(), reverse=True)
            ano_abc = st.selectbox("Ano:", anos_disp if anos_disp else [2025], key='abc_ano')
        # Pre-filtrar notas e frequencia pelo ano selecionado
        df_notas = df_notas[df_notas['ano'] == ano_abc]
        if tem_freq and 'ano' in df_freq.columns:
            df_freq = df_freq[df_freq['ano'] == ano_abc]

    # ========== CALCULAR ABC PARA CADA ALUNO ==========
    df = aplicar_filtro_unidade(df_alunos.copy(), unidade_sel, todas_label="Todas")
    df = aplicar_filtro_segmento(df, segmento_sel)

    # Filtrar ocorrências para 2026 (a partir do início do ano letivo)
    if tem_ocorr and 'data' in df_ocorr.columns:
        df_ocorr['data'] = pd.to_datetime(df_ocorr['data'], errors='coerce')
        df_ocorr = df_ocorr[df_ocorr['data'] >= '2026-01-27'].copy()

    # Pre-agregar frequência por aluno para performance
    freq_por_aluno = {}
    if tem_freq and 'aluno_id' in df_freq.columns and 'pct_frequencia' in df_freq.columns:
        # Agregar por aluno (média ponderada por total_aulas)
        if 'total_aulas' in df_freq.columns and 'presentes' in df_freq.columns:
            freq_agg = df_freq.groupby('aluno_id').agg(
                total_aulas=('total_aulas', 'sum'),
                presentes=('presentes', 'sum'),
            ).reset_index()
            freq_agg['pct_frequencia'] = (
                freq_agg['presentes'] / freq_agg['total_aulas'].clip(lower=1) * 100
            )
            for _, r in freq_agg.iterrows():
                freq_por_aluno[r['aluno_id']] = round(r['pct_frequencia'], 1)
        else:
            # Fallback: média simples
            freq_agg = df_freq.groupby('aluno_id')['pct_frequencia'].mean()
            for aid, val in freq_agg.items():
                freq_por_aluno[aid] = round(val, 1)

    resultados = []
    for _, aluno in df.iterrows():
        aluno_id = aluno.get('aluno_id')
        if aluno_id is None:
            continue

        # A - Frequência (sem default artificial - NaN = sem dados)
        freq_pct = freq_por_aluno.get(aluno_id, None)
        tem_dados_freq = freq_pct is not None

        # B - Ocorrências (apenas disciplinares, 2026 apenas)
        num_ocorr = 0
        if tem_ocorr and 'aluno_id' in df_ocorr.columns:
            ocorr_aluno = df_ocorr[df_ocorr['aluno_id'] == aluno_id]
            if 'categoria' in df_ocorr.columns:
                num_ocorr = len(ocorr_aluno[ocorr_aluno['categoria'] == 'Disciplinar'])
            else:
                num_ocorr = len(ocorr_aluno)

        # C - Média de notas (sem default artificial - NaN = sem dados)
        media = None
        tem_dados_notas = False
        if tem_notas and 'aluno_id' in df_notas.columns:
            notas_aluno = df_notas[df_notas['aluno_id'] == aluno_id]
            if not notas_aluno.empty and 'nota' in notas_aluno.columns:
                val = notas_aluno['nota'].mean()
                if pd.notna(val):
                    media = val
                    tem_dados_notas = True

        # Calcular score ABC com valores reais (usar neutro quando sem dados)
        # Sem dados de freq -> usa 100% (neutro, não penaliza)
        # Sem dados de notas -> usa 7.0 (neutro, não penaliza)
        freq_para_score = freq_pct if tem_dados_freq else 100.0
        media_para_score = media if tem_dados_notas else 7.0

        flags, tier, score = calcular_score_abc(freq_para_score, num_ocorr, media_para_score)

        # Marcar flags de "Sem dados" (não contar como OK real)
        flag_a_str = 'Sem dados' if not tem_dados_freq else ('OK' if freq_pct >= 85 else ('Alerta' if freq_pct >= 70 else 'Risco'))
        flag_c_str = 'Sem dados' if not tem_dados_notas else ('OK' if media >= 5.0 else ('Risco' if media >= 3.0 else 'Crítico'))

        resultados.append({
            'aluno_id': aluno_id,
            'aluno_nome': aluno.get('aluno_nome', ''),
            'serie': aluno.get('serie', ''),
            'turma': aluno.get('turma', ''),
            'unidade': aluno.get('unidade', ''),
            'freq_pct': round(freq_pct, 1) if tem_dados_freq else None,
            'freq_source': 'chamada_2026' if tem_dados_freq else 'sem_dados',
            'num_ocorr': num_ocorr,
            'media_notas': round(media, 1) if tem_dados_notas else None,
            'flag_a_detail': flag_a_str,
            'flag_c_detail': flag_c_str,
            'flags': flags,
            'flags_str': ', '.join(flags) if flags else 'OK',
            'num_flags': len(flags),
            'tier': tier,
            'tier_nome': {0: 'Universal', 1: 'Atenção', 2: 'Intervenção', 3: 'Intensivo'}[tier],
            'score': score,
        })

    if not resultados:
        st.info("Nenhum aluno encontrado com os filtros selecionados.")
        return

    df_abc = pd.DataFrame(resultados).sort_values('score', ascending=False)

    # ========== METRICAS ==========
    tier_counts = df_abc['tier'].value_counts()
    n_total = len(df_abc)
    n_tier3 = tier_counts.get(3, 0)
    n_tier2 = tier_counts.get(2, 0)
    n_tier1 = tier_counts.get(1, 0)
    n_ok = tier_counts.get(0, 0)

    metricas_em_colunas([
        {'label': 'Total Alunos', 'value': n_total},
        {'label': '🔴 Tier 3 (Intensivo)', 'value': n_tier3},
        {'label': '🟠 Tier 2 (Intervenção)', 'value': n_tier2},
        {'label': '🟡 Tier 1 (Atenção)', 'value': n_tier1},
        {'label': '🟢 Universal (OK)', 'value': n_ok},
    ])

    # Cobertura de dados
    n_com_freq = df_abc['freq_pct'].notna().sum()
    n_com_notas = df_abc['media_notas'].notna().sum()
    pct_freq = n_com_freq / max(1, n_total) * 100
    pct_notas = n_com_notas / max(1, n_total) * 100
    st.caption(
        f"Cobertura de dados: Frequência (chamada 2026): {n_com_freq}/{n_total} ({pct_freq:.0f}%) | "
        f"Notas (historico): {n_com_notas}/{n_total} ({pct_notas:.0f}%)"
    )

    # ========== TABS ==========
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔴 Alunos em Risco", "📊 Visão Geral", "🏫 Por Turma", "📈 Correlações", "ℹ️ Sobre o ABC"
    ])

    # TAB 1: ALUNOS EM RISCO
    with tab1:
        st.subheader("🔴 Alunos que Precisam de Intervenção Imediata")

        for tier_val, tier_label, css_class in [(3, 'TIER 3 - INTERVENÇÃO INTENSIVA', 'tier3-card'),
                                                  (2, 'TIER 2 - INTERVENÇÃO DIRECIONADA', 'tier2-card'),
                                                  (1, 'TIER 1 - ATENÇÃO', 'tier1-card')]:
            alunos_tier = df_abc[df_abc['tier'] == tier_val]
            if alunos_tier.empty:
                continue

            st.markdown(f"### {tier_label} ({len(alunos_tier)} alunos)")

            for _, row in alunos_tier.iterrows():
                badges = ''
                if 'A' in row['flags']:
                    freq_val = f'{row["freq_pct"]:.0f}%' if pd.notna(row.get("freq_pct")) else 'S/D'
                    badges += f'<span class="abc-badge badge-a">A Frequência: {freq_val}</span>'
                if 'B' in row['flags']:
                    badges += f'<span class="abc-badge badge-b">B Comportamento: {row["num_ocorr"]} ocorr.</span>'
                if 'C' in row['flags']:
                    nota_val = f'{row["media_notas"]:.1f}' if pd.notna(row.get("media_notas")) else 'S/D'
                    badges += f'<span class="abc-badge badge-c">C Notas: {nota_val}</span>'

                st.markdown(f"""
                <div class="{css_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong style="font-size:1.1em;">{row['aluno_nome']}</strong>
                            <span style="color:#666; margin-left:10px;">
                                {row['serie']} | {UNIDADES_NOMES.get(row['unidade'], row['unidade'])}
                            </span>
                        </div>
                        <div>
                            <span class="abc-badge badge-risco">Score: {row['score']:.0f}</span>
                        </div>
                    </div>
                    <div style="margin-top:8px;">{badges}</div>
                </div>
                """, unsafe_allow_html=True)

    # TAB 2: VISAO GERAL
    with tab2:
        st.subheader("📊 Distribuição de Risco")

        col_e, col_d = st.columns(2)

        with col_e:
            # Donut de tiers
            tier_data = pd.DataFrame({
                'Tier': ['Tier 3 (Intensivo)', 'Tier 2 (Intervenção)', 'Tier 1 (Atenção)', 'Universal (OK)'],
                'Quantidade': [n_tier3, n_tier2, n_tier1, n_ok],
                'Cor': ['#B71C1C', '#E65100', '#F9A825', '#2E7D32'],
            })
            fig = px.pie(tier_data, values='Quantidade', names='Tier',
                        color='Tier',
                        color_discrete_map={
                            'Tier 3 (Intensivo)': '#B71C1C',
                            'Tier 2 (Intervenção)': '#E65100',
                            'Tier 1 (Atenção)': '#F9A825',
                            'Universal (OK)': '#2E7D32',
                        },
                        title='Distribuição por Tier', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        with col_d:
            # Distribuicao de flags
            flags_count = {'A (Frequência)': 0, 'B (Comportamento)': 0, 'C (Notas)': 0}
            for flags in df_abc['flags']:
                for f in flags:
                    if f == 'A':
                        flags_count['A (Frequência)'] += 1
                    elif f == 'B':
                        flags_count['B (Comportamento)'] += 1
                    elif f == 'C':
                        flags_count['C (Notas)'] += 1

            fig2 = px.bar(
                x=list(flags_count.values()), y=list(flags_count.keys()),
                orientation='h',
                color=list(flags_count.keys()),
                color_discrete_map={
                    'A (Frequência)': '#1565C0',
                    'B (Comportamento)': '#E65100',
                    'C (Notas)': '#7B1FA2',
                },
                title='Dimensões com Mais Alertas'
            )
            fig2.update_layout(showlegend=False, xaxis_title='Alunos Alertados', yaxis_title='')
            st.plotly_chart(fig2, use_container_width=True)

        # Histograma de score
        fig3 = px.histogram(
            df_abc, x='score', nbins=20,
            color_discrete_sequence=['#B71C1C'],
            title='Distribuição do Score de Risco'
        )
        fig3.add_vline(x=50, line_dash="dash", line_color="orange", annotation_text="Risco Moderado")
        fig3.add_vline(x=75, line_dash="dash", line_color="red", annotation_text="Risco Alto")
        st.plotly_chart(fig3, use_container_width=True)

    # TAB 3: POR TURMA
    with tab3:
        st.subheader("🏫 Risco por Turma")

        if 'serie' in df_abc.columns:
            # Heatmap serie x tier
            pivot = df_abc.pivot_table(
                index='serie', columns='tier_nome', values='aluno_id', aggfunc='count', fill_value=0
            )
            for col in ['Intensivo', 'Intervenção', 'Atenção', 'Universal']:
                if col not in pivot.columns:
                    pivot[col] = 0
            pivot = pivot[['Intensivo', 'Intervenção', 'Atenção', 'Universal']]

            fig = px.imshow(
                pivot, text_auto=True,
                color_continuous_scale=['#E8F5E9', '#FFF9C4', '#FFCCBC', '#FFCDD2'],
                title='Alunos por Tier e Série'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Ranking de turmas por % de risco
            if 'turma' in df_abc.columns:
                turma_risco = df_abc.groupby('turma').agg(
                    total=('aluno_id', 'count'),
                    em_risco=('tier', lambda x: (x >= 2).sum()),
                ).reset_index()
                turma_risco['pct_risco'] = (turma_risco['em_risco'] / turma_risco['total'].clip(lower=1) * 100).round(1)
                turma_risco = turma_risco.sort_values('pct_risco', ascending=False)

                st.subheader("Turmas com Maior % de Alunos em Risco")
                st.dataframe(turma_risco.head(15), use_container_width=True, hide_index=True)

    # TAB 4: CORRELACOES
    with tab4:
        st.subheader("📈 Correlações entre Dimensões")

        # Scatter: Frequência x Notas (cor = ocorrências)
        # Filtrar apenas alunos com ambos os dados para o scatter
        df_scatter = df_abc.dropna(subset=['freq_pct', 'media_notas'])
        if df_scatter.empty:
            st.info("Dados insuficientes para correlação (necessita frequência E notas).")
        else:
            st.caption(f"Exibindo {len(df_scatter)} alunos com dados de frequência E notas.")
        df_plot = df_scatter if not df_scatter.empty else df_abc
        fig = px.scatter(
            df_plot, x='freq_pct', y='media_notas',
            color='tier_nome',
            color_discrete_map={
                'Intensivo': '#B71C1C', 'Intervenção': '#E65100',
                'Atenção': '#F9A825', 'Universal': '#2E7D32',
            },
            size='num_ocorr' if df_plot['num_ocorr'].max() > 0 else None,
            hover_data=['aluno_nome', 'serie', 'unidade'],
            title='Frequência x Notas (tamanho = ocorrências)',
            labels={'freq_pct': '% Frequência', 'media_notas': 'Média de Notas'},
        )
        fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Nota mínima")
        fig.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="Meta")
        fig.add_vline(x=75, line_dash="dash", line_color="red", annotation_text="LDB 75%")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Quadrante de desempenho
        st.markdown("""
        **Leitura do gráfico:**
        - **Superior-direito:** Bom aluno (boa frequência + boas notas)
        - **Superior-esquerdo:** Frequenta mas não aprende (precisa de suporte pedagógico)
        - **Inferior-direito:** Bom quando vem, mas falta muito (ação: frequência)
        - **Inferior-esquerdo:** Risco máximo (intervenção urgente em tudo)
        """)

    # TAB 5: SOBRE O ABC
    with tab5:
        _mostrar_explicacao_abc()


def _mostrar_explicacao_abc():
    """Mostra explicacao do framework ABC."""
    st.markdown("""
    ## O que é o Sistema ABC de Alerta Precoce?

    O framework **ABC** é o método mais validado internacionalmente para identificar alunos
    em risco de fracasso escolar. Pesquisas mostram que ele identifica **50-75% dos futuros
    fracassos** antes que aconteçam.

    ### As 3 Dimensões:

    | Dimensão | O que mede | Threshold de Risco |
    |----------|-----------|-------------------|
    | **A** - Attendance (Frequência) | % de presença nas aulas | < 85% (alerta) / < 75% (crítico - LDB) |
    | **B** - Behavior (Comportamento) | Número de ocorrências disciplinares | >= 2 (alerta) / >= 5 (crítico) |
    | **C** - Coursework (Notas) | Média geral das avaliações | < 5.0 (alerta) / < 3.0 (crítico) |

    ### Tiers de Intervenção:

    | Tier | Critério | Ação |
    |------|---------|------|
    | **Tier 0** - Universal | 0 flags | Acompanhamento normal |
    | **Tier 1** - Atenção | 1 flag (A, B ou C) | Monitoramento semanal, conversa com professor |
    | **Tier 2** - Intervenção | 2 flags | Reunião com família, plano de intervenção |
    | **Tier 3** - Intensivo | 3 flags (A+B+C) | Acompanhamento diário, equipe multidisciplinar |

    ### Pesos do Score:
    - **A** (Frequência): 30%
    - **B** (Comportamento): 30%
    - **C** (Notas): 40%

    ### Fontes:
    - Panorama Education - Early Warning System
    - US Dept of Education - Early Warning Systems Brief
    - PBIS Framework (Positive Behavioral Interventions and Supports)
    """)


def _mostrar_preview_simulado():
    """Preview com dados simulados."""
    import numpy as np

    st.markdown("---")
    st.subheader("📋 Preview do Sistema ABC (dados simulados)")

    np.random.seed(42)
    n = 30
    nomes = [f"Aluno {i+1}" for i in range(n)]
    freqs = np.random.normal(88, 10, n).clip(50, 100)
    ocorrs = np.random.poisson(1, n)
    notas = np.random.normal(6.5, 1.5, n).clip(0, 10)

    dados_sim = []
    for i in range(n):
        flags, tier, score = calcular_score_abc(freqs[i], ocorrs[i], notas[i])
        dados_sim.append({
            'Aluno': nomes[i],
            'Frequência': f"{freqs[i]:.0f}%",
            'Ocorrências': int(ocorrs[i]),
            'Média': f"{notas[i]:.1f}",
            'Flags': ', '.join(flags) if flags else 'OK',
            'Tier': {0: '🟢 Universal', 1: '🟡 Atenção', 2: '🟠 Intervenção', 3: '🔴 Intensivo'}[tier],
            'Score': score,
        })

    df_sim = pd.DataFrame(dados_sim).sort_values('Score', ascending=False)
    st.dataframe(df_sim, use_container_width=True, hide_index=True, height=400)
    st.caption("⚠️ Dados simulados. Execute a extração de dados de alunos para dados reais.")


if __name__ == "__main__":
    main()
