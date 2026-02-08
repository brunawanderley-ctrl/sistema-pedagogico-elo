#!/usr/bin/env python3
"""
PÁGINA 5: PROGRESSÃO SAE
Ritmo esperado vs realizado com dados reais do SIGA.
Usa progressao_key para cruzar fato_Aulas com dim_Progressao_SAE.
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
from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    carregar_fato_aulas, carregar_progressao_sae, carregar_horario_esperado,
    filtrar_ate_hoje, _hoje, DATA_DIR, UNIDADES_NOMES, ORDEM_SERIES,
    SERIES_FUND_II, SERIES_EM
)

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
    .prog-card {
        padding: 15px; border-radius: 10px; text-align: center;
        margin: 5px 0; color: white; min-height: 90px;
    }
    .prog-verde { background: linear-gradient(135deg, #43A047, #66BB6A); }
    .prog-amarelo { background: linear-gradient(135deg, #F9A825, #FDD835); color: #333; }
    .prog-vermelho { background: linear-gradient(135deg, #E53935, #EF5350); }
    .prog-azul { background: linear-gradient(135deg, #1565C0, #42A5F5); }
</style>
""", unsafe_allow_html=True)


def estimar_capitulo_real(conteudos):
    """
    Estima o capitulo atual baseado nos conteudos registrados.
    Procura mencoes a 'capitulo X', 'cap X', 'cap. X' nos textos.
    """
    if conteudos is None or len(conteudos) == 0:
        return None
    import re
    max_cap = 0
    for texto in conteudos:
        if pd.isna(texto):
            continue
        texto = str(texto).lower()
        # Procura padroes: "capítulo 3", "cap 3", "cap. 3", "capitulo 3"
        matches = re.findall(r'cap[íi]?t?u?l?o?\.?\s*(\d{1,2})', texto)
        for m in matches:
            cap = int(m)
            if 1 <= cap <= 12 and cap > max_cap:
                max_cap = cap
    return max_cap if max_cap > 0 else None


def calcular_progressao_real(df_aulas, df_prog, semana_atual):
    """
    Cruza fato_Aulas com dim_Progressao_SAE para calcular status real.
    Retorna DataFrame com: unidade, serie, disciplina, aulas_registradas,
    capitulo_esperado, capitulo_estimado, status, gap.
    """
    if df_aulas.empty or df_prog.empty:
        return pd.DataFrame()

    # Join via progressao_key
    df_merged = df_aulas.merge(
        df_prog[['progressao_key', 'capitulo_esperado']].drop_duplicates(subset='progressao_key'),
        on='progressao_key',
        how='left'
    )

    # Agrupa por unidade/serie/disciplina
    resultados = []
    for (un, serie, disc), grupo in df_merged.groupby(['unidade', 'serie', 'disciplina']):
        aulas = len(grupo)
        profs = grupo['professor'].nunique()
        prof_nome = grupo['professor'].iloc[0] if len(grupo) > 0 else ''

        # Capitulo esperado (do SAE)
        cap_esperado = grupo['capitulo_esperado'].dropna()
        cap_esp = int(cap_esperado.max()) if len(cap_esperado) > 0 else calcular_capitulo_esperado(semana_atual)

        # Estima capitulo real pelo conteudo
        cap_real = estimar_capitulo_real(grupo['conteudo'].tolist())

        # Status
        if cap_real is None:
            status = 'Sem dados'
            gap = None
        elif cap_real >= cap_esp:
            status = 'No ritmo' if cap_real == cap_esp else 'Adiantado'
            gap = cap_real - cap_esp
        else:
            diff = cap_esp - cap_real
            status = 'Atrasado' if diff >= 2 else 'Atenção'
            gap = -diff

        # Ultimos conteudos
        ultimos = grupo['conteudo'].dropna().tail(2).tolist()
        ultimos_txt = ' | '.join(str(c)[:80] for c in ultimos) if ultimos else ''

        resultados.append({
            'unidade': un,
            'serie': serie,
            'disciplina': disc,
            'professor': prof_nome.split(' - ')[0] if ' - ' in prof_nome else prof_nome,
            'aulas': aulas,
            'cap_esperado': cap_esp,
            'cap_estimado': cap_real,
            'status': status,
            'gap': gap,
            'ultimos_conteudos': ultimos_txt,
        })

    return pd.DataFrame(resultados)


def main():
    st.title("📈 Progressão SAE")
    st.markdown("**Ritmo esperado vs realizado | Capítulos por semana**")

    semana_atual = calcular_semana_letiva()
    cap_esperado = calcular_capitulo_esperado(semana_atual)
    trimestre = calcular_trimestre(semana_atual)

    # ========== STATUS ATUAL ==========
    st.markdown("---")
    st.header("🎯 Status Atual da Progressão")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="prog-card prog-azul">
            <h2 style="margin:0; border:none; color:white;">{semana_atual}ª</h2>
            <p style="margin:0;">Semana Letiva</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="prog-card prog-azul">
            <h2 style="margin:0; border:none; color:white;">{cap_esperado}/12</h2>
            <p style="margin:0;">Capitulo Esperado</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="prog-card prog-azul">
            <h2 style="margin:0; border:none; color:white;">{trimestre}º</h2>
            <p style="margin:0;">Trimestre</p>
        </div>""", unsafe_allow_html=True)
    with col4:
        pct_ano = round(semana_atual / 42 * 100)
        st.markdown(f"""
        <div class="prog-card prog-azul">
            <h2 style="margin:0; border:none; color:white;">{pct_ano}%</h2>
            <p style="margin:0;">do Ano Letivo</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        <strong>📐 FÓRMULA DE PROGRESSÃO:</strong><br><br>
        <code>Capítulo = ⌈ Semana Letiva ÷ 3.5 ⌉</code><br><br>
        <strong>Tradução:</strong> 42 semanas ÷ 12 capítulos = <strong>3,5 semanas por capítulo</strong><br><br>
        ✅ Aplica-se a TODAS as turmas (Anos Finais e Ensino Médio)
    </div>
    """, unsafe_allow_html=True)

    # ========== DADOS REAIS DO SIGA ==========
    st.markdown("---")
    st.header("🔍 Progressão Real vs Esperada")

    df_aulas = carregar_fato_aulas()
    df_prog = carregar_progressao_sae()
    df_horario = carregar_horario_esperado()

    if df_aulas.empty:
        st.warning("Dados do SIGA nao carregados. Execute a extracao primeiro.")
        _mostrar_referencia(semana_atual, cap_esperado)
        return

    df_aulas_filtrado = filtrar_ate_hoje(df_aulas)

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        unidades = sorted(df_aulas_filtrado['unidade'].unique())
        un_sel = st.selectbox("Unidade:", ['Todas'] + unidades)
    with col_f2:
        segmento = st.selectbox("Segmento:", ['Todos', 'Anos Finais', 'Ensino Médio'])
    with col_f3:
        series_disp = sorted(
            df_aulas_filtrado['serie'].unique(),
            key=lambda s: ORDEM_SERIES.index(s) if s in ORDEM_SERIES else 99
        )
        serie_sel = st.selectbox("Série:", ['Todas'] + series_disp)

    # Aplica filtros
    df_f = df_aulas_filtrado.copy()
    if un_sel != 'Todas':
        df_f = df_f[df_f['unidade'] == un_sel]
    if segmento == 'Anos Finais':
        df_f = df_f[df_f['serie'].isin(SERIES_FUND_II)]
    elif segmento == 'Ensino Médio':
        df_f = df_f[df_f['serie'].isin(SERIES_EM)]
    if serie_sel != 'Todas':
        df_f = df_f[df_f['serie'] == serie_sel]

    # Calcula progressao
    df_status = calcular_progressao_real(df_f, df_prog, semana_atual)

    if df_status.empty:
        st.info("Nenhum dado encontrado para os filtros selecionados.")
        _mostrar_referencia(semana_atual, cap_esperado)
        return

    # ========== RESUMO POR STATUS ==========
    st.subheader("Resumo de Status")

    status_counts = df_status['status'].value_counts()
    total_disc = len(df_status)

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    n_ritmo = status_counts.get('No ritmo', 0) + status_counts.get('Adiantado', 0)
    n_atencao = status_counts.get('Atenção', 0)
    n_atrasado = status_counts.get('Atrasado', 0)
    n_sem = status_counts.get('Sem dados', 0)

    with col_s1:
        st.markdown(f"""
        <div class="prog-card prog-verde">
            <h2 style="margin:0; border:none; color:white;">{n_ritmo}</h2>
            <p style="margin:0;">No Ritmo / Adiantado</p>
        </div>""", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div class="prog-card prog-amarelo">
            <h2 style="margin:0; border:none; color:inherit;">{n_atencao}</h2>
            <p style="margin:0;">Atenção (-1 cap)</p>
        </div>""", unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
        <div class="prog-card prog-vermelho">
            <h2 style="margin:0; border:none; color:white;">{n_atrasado}</h2>
            <p style="margin:0;">Atrasado (-2+ caps)</p>
        </div>""", unsafe_allow_html=True)
    with col_s4:
        st.markdown(f"""
        <div class="prog-card" style="background: #9E9E9E;">
            <h2 style="margin:0; border:none; color:white;">{n_sem}</h2>
            <p style="margin:0;">Sem dados de capitulo</p>
        </div>""", unsafe_allow_html=True)

    # ========== TABELA DETALHADA ==========
    st.subheader("Detalhamento por Disciplina")

    # Prepara tabela de exibicao
    df_display = df_status.copy()
    df_display['Cap. Esperado'] = df_display['cap_esperado']
    df_display['Cap. Estimado'] = df_display['cap_estimado'].apply(
        lambda x: f"{int(x)}" if pd.notna(x) else "—"
    )

    status_emoji = {
        'Adiantado': '🟢 Adiantado',
        'No ritmo': '🟢 No ritmo',
        'Atenção': '🟡 Atenção',
        'Atrasado': '🔴 Atrasado',
        'Sem dados': '⚪ Sem dados',
    }
    df_display['Status'] = df_display['status'].map(status_emoji)
    df_display['Gap'] = df_display['gap'].apply(
        lambda x: f"+{int(x)}" if pd.notna(x) and x > 0 else (f"{int(x)}" if pd.notna(x) else "—")
    )

    colunas = ['unidade', 'serie', 'disciplina', 'professor', 'aulas',
               'Cap. Esperado', 'Cap. Estimado', 'Gap', 'Status']
    nomes = {
        'unidade': 'Unidade', 'serie': 'Série', 'disciplina': 'Disciplina',
        'professor': 'Professor', 'aulas': 'Aulas',
    }

    st.dataframe(
        df_display[colunas].rename(columns=nomes).sort_values(
            ['Série', 'Disciplina'],
            key=lambda col: col.map(lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99) if col.name == 'Série' else col
        ),
        use_container_width=True,
        hide_index=True,
        height=min(600, 35 * len(df_display) + 38)
    )

    # ========== GRAFICO: MAPA DE CALOR SERIE x DISCIPLINA ==========
    if serie_sel == 'Todas' and un_sel != 'Todas':
        st.subheader("Mapa: Série x Disciplina")

        # Pivota para heatmap
        df_heat = df_status[df_status['cap_estimado'].notna()].copy()
        if not df_heat.empty:
            df_heat['diff'] = df_heat['cap_estimado'] - df_heat['cap_esperado']
            pivot = df_heat.pivot_table(
                index='disciplina', columns='serie', values='diff', aggfunc='mean'
            )
            # Ordena series
            cols_ord = [s for s in ORDEM_SERIES if s in pivot.columns]
            pivot = pivot.reindex(columns=cols_ord)

            fig_heat = px.imshow(
                pivot,
                color_continuous_scale='RdYlGn',
                color_continuous_midpoint=0,
                labels={'color': 'Gap (caps)'},
                aspect='auto',
                title='Gap de Progressão (verde=adiantado, vermelho=atrasado)',
            )
            fig_heat.update_layout(height=max(300, len(pivot) * 30 + 100))
            st.plotly_chart(fig_heat, use_container_width=True)

    # ========== GRAFICO: BARRAS POR DISCIPLINA ==========
    if serie_sel != 'Todas':
        st.subheader(f"Progressão por Disciplina - {serie_sel}")

        df_bars = df_status[df_status['cap_estimado'].notna()].copy()
        if not df_bars.empty:
            fig_bar = go.Figure()

            fig_bar.add_trace(go.Bar(
                name='Capítulo Estimado',
                x=df_bars['disciplina'],
                y=df_bars['cap_estimado'],
                marker_color=df_bars['status'].map({
                    'Adiantado': '#43A047', 'No ritmo': '#66BB6A',
                    'Atenção': '#FDD835', 'Atrasado': '#E53935',
                }).fillna('#9E9E9E'),
            ))

            fig_bar.add_hline(
                y=cap_esperado, line_dash="dash", line_color="#1565C0",
                annotation_text=f"Esperado: Cap. {cap_esperado}"
            )

            fig_bar.update_layout(
                title=f"Capítulo Estimado vs Esperado - {serie_sel}",
                xaxis_title="Disciplina",
                yaxis_title="Capítulo",
                yaxis=dict(range=[0, 13], dtick=1),
                height=450,
                showlegend=False,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # ========== DISCIPLINAS SEM PROGRESSAO SAE ==========
    disc_sem_sae = df_status[df_status['cap_esperado'] == calcular_capitulo_esperado(semana_atual)]
    # Disciplinas que nao tem match na progressao (Ed. Fisica, Projeto de Vida, etc)
    df_no_match = df_f[~df_f['progressao_key'].isin(df_prog['progressao_key'])]
    if not df_no_match.empty:
        disc_no_sae = sorted(df_no_match['disciplina'].unique())
        with st.expander(f"Disciplinas sem material SAE ({len(disc_no_sae)})"):
            st.caption("Estas disciplinas nao possuem livro/capitulos SAE e nao entram na analise de progressao:")
            for d in disc_no_sae:
                n = len(df_no_match[df_no_match['disciplina'] == d])
                st.markdown(f"- **{d}**: {n} aulas registradas")

    # ========== CURVA DE PROGRESSAO ==========
    st.markdown("---")
    st.header("📊 Curva de Progressão SAE 2026")

    semanas = list(range(1, 43))
    capitulos = [min(12, math.ceil(s / 3.5)) for s in semanas]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=semanas, y=capitulos,
        mode='lines+markers',
        name='Capítulo Esperado',
        line=dict(color='#1565C0', width=3),
        marker=dict(size=6)
    ))

    fig.add_vline(x=semana_atual, line_dash="dash", line_color="red",
                 annotation_text=f"Semana {semana_atual}")
    fig.add_hline(y=cap_esperado, line_dash="dash", line_color="green",
                 annotation_text=f"Cap. {cap_esperado}")

    fig.add_vrect(x0=1, x1=14, fillcolor="blue", opacity=0.05,
                 annotation_text="1º Tri", annotation_position="top left")
    fig.add_vrect(x0=15, x1=28, fillcolor="green", opacity=0.05,
                 annotation_text="2º Tri", annotation_position="top left")
    fig.add_vrect(x0=29, x1=42, fillcolor="orange", opacity=0.05,
                 annotation_text="3º Tri", annotation_position="top left")

    fig.update_layout(
        title="Progressão de Capítulos ao Longo do Ano",
        xaxis_title="Semana Letiva",
        yaxis_title="Capítulo SAE",
        yaxis=dict(tickmode='linear', tick0=1, dtick=1, range=[0, 13]),
        xaxis=dict(tickmode='linear', tick0=1, dtick=2),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    # ========== REFERENCIA ==========
    _mostrar_referencia(semana_atual, cap_esperado)

    # ========== EXPORT ==========
    st.markdown("---")
    st.subheader("📥 Exportar")

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        # CSV detalhado
        csv_data = df_status.to_csv(index=False)
        st.download_button(
            "Baixar Progressao (CSV)",
            csv_data,
            f"progressao_sae_{un_sel}_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )

    with col_exp2:
        # Resumo TXT
        linhas = [
            f"PROGRESSÃO SAE - {un_sel} - Semana {semana_atual}",
            f"Capitulo esperado: {cap_esperado}/12 | {trimestre}º Trimestre",
            f"Data: {datetime.now().strftime('%d/%m/%Y')}",
            "=" * 60,
            "",
            f"RESUMO: {n_ritmo} no ritmo | {n_atencao} atenção | {n_atrasado} atrasados | {n_sem} sem dados",
            "",
        ]
        for _, row in df_status.iterrows():
            cap_est = int(row['cap_estimado']) if pd.notna(row['cap_estimado']) else '?'
            linhas.append(
                f"  {row['serie']:12s} | {row['disciplina']:25s} | "
                f"Cap. {cap_est}/{int(row['cap_esperado'])} | {row['status']}"
            )
        txt_data = '\n'.join(linhas)
        st.download_button(
            "Baixar Resumo (TXT)",
            txt_data,
            f"progressao_resumo_{un_sel}_{datetime.now().strftime('%Y%m%d')}.txt",
            "text/plain"
        )


def _mostrar_referencia(semana_atual, cap_esperado):
    """Mostra tabelas de referencia estaticas."""
    with st.expander("📋 Referência: Metas por Trimestre"):
        metas = pd.DataFrame({
            'Trimestre': ['1º Trimestre', '2º Trimestre', '3º Trimestre'],
            'Semanas': ['1-14', '15-28', '29-42'],
            'Capítulos': ['1 a 4', '5 a 8', '9 a 12'],
            'Volumes': ['V1 + início V2', 'V2 (final) + V3', 'V3 (final) + V4'],
            'Avaliações': ['A1 + A2 + Simulado', 'A1 + A2 + Simulado', 'A1 + A2 + Final + Simulado'],
        })
        st.dataframe(metas, use_container_width=True, hide_index=True)

    with st.expander("📋 Referência: Checkpoints"):
        checkpoints = pd.DataFrame({
            'Checkpoint': ['Semana 7', 'Semana 14', 'Semana 21', 'Semana 28', 'Semana 35', 'Semana 42'],
            'Cap. Mínimo': [2, 4, 6, 8, 10, 12],
            'Avaliações': ['A1', 'A1+A2+Rec', 'A1 (2ºTri)', 'A1+A2+Rec', 'A1 (3ºTri)', 'Todas'],
        })

        # Destaca checkpoint atual
        checkpoints['Status'] = checkpoints['Cap. Mínimo'].apply(
            lambda c: '👉 ATUAL' if c == cap_esperado else ('✅' if c < cap_esperado else '')
        )
        st.dataframe(checkpoints, use_container_width=True, hide_index=True)

    with st.expander("📋 Referência: Ritmo por Disciplina"):
        ritmo_disc = pd.DataFrame({
            'Disciplina': ['Português/Matemática', 'Ciências/História/Geografia',
                          'Inglês/Arte/Filosofia', 'Ed. Física', 'Redação'],
            'Aulas/Sem': ['5', '3', '1-2', '2', '2'],
            'Sem/Cap': ['~3.5', '~3.5', '~3.5', 'N/A', '~3.5'],
            'Material': ['4 volumes (3 caps)', '4 volumes (3 caps)',
                        '2 volumes (6 caps)', 'Digital', 'Complementar'],
        })
        st.dataframe(ritmo_disc, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
