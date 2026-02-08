#!/usr/bin/env python3
"""
PAGINA 13: SEMAFORO DO PROFESSOR
Visao matricial rapida: cada professor com cor de semaforo
Permite coordenacao ver em 5 segundos quem precisa de atencao HOJE
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_cores import CORES_UNIDADES, CORES_SERIES, ORDEM_SERIES
from utils import (
    calcular_semana_letiva, calcular_capitulo_esperado,
    carregar_fato_aulas, carregar_horario_esperado,
    filtrar_ate_hoje, _hoje, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM
)

st.set_page_config(page_title="Semaforo do Professor", page_icon="🚦", layout="wide")
from auth import check_password, logout_button
if not check_password():
    st.stop()
logout_button()

st.markdown("""
<style>
    .semaforo-verde {
        background: #C8E6C9; color: #1B5E20;
        padding: 8px 12px; border-radius: 6px; text-align: center;
        font-weight: bold; margin: 2px;
    }
    .semaforo-amarelo {
        background: #FFF9C4; color: #F57F17;
        padding: 8px 12px; border-radius: 6px; text-align: center;
        font-weight: bold; margin: 2px;
    }
    .semaforo-vermelho {
        background: #FFCDD2; color: #B71C1C;
        padding: 8px 12px; border-radius: 6px; text-align: center;
        font-weight: bold; margin: 2px;
    }
    .semaforo-cinza {
        background: #EEEEEE; color: #616161;
        padding: 8px 12px; border-radius: 6px; text-align: center;
        font-weight: bold; margin: 2px;
    }
    .resumo-card {
        padding: 20px; border-radius: 10px; text-align: center; margin: 5px 0;
    }
    .card-verde { background: linear-gradient(135deg, #4CAF50, #81C784); color: white; }
    .card-amarelo { background: linear-gradient(135deg, #FFC107, #FFD54F); color: #333; }
    .card-vermelho { background: linear-gradient(135deg, #F44336, #E57373); color: white; }
    .card-total { background: linear-gradient(135deg, #607D8B, #90A4AE); color: white; }
</style>
""", unsafe_allow_html=True)


def calcular_metricas_professor(df_aulas, df_horario, semana_atual):
    """Calcula metricas de cada professor cruzando aulas reais x esperadas."""
    hoje = _hoje()
    resultados = []

    for _, grupo in df_horario.groupby('professor'):
        prof = grupo['professor'].iloc[0]
        unidade = grupo['unidade'].iloc[0]
        disciplinas = grupo['disciplina'].unique()
        series = grupo['serie'].unique()

        # Aulas esperadas ate agora
        aulas_semana = len(grupo)
        esperado = aulas_semana * semana_atual

        # Aulas registradas
        df_prof = df_aulas[df_aulas['professor'] == prof]
        registrado = len(df_prof)

        # Taxa de registro
        taxa_registro = (registrado / esperado * 100) if esperado > 0 else 0

        # Conteudo preenchido
        com_conteudo = df_prof[df_prof['conteudo'].notna() & (df_prof['conteudo'] != '')].shape[0]
        taxa_conteudo = (com_conteudo / registrado * 100) if registrado > 0 else 0

        # Tarefa preenchida
        com_tarefa = df_prof[df_prof['tarefa'].notna() & (df_prof['tarefa'] != '')].shape[0]
        taxa_tarefa = (com_tarefa / registrado * 100) if registrado > 0 else 0

        # Dias sem registro
        if not df_prof.empty and df_prof['data'].notna().any():
            ultimo_registro = df_prof['data'].max()
            dias_sem = (hoje - ultimo_registro).days
        else:
            dias_sem = (hoje - datetime(2026, 1, 26)).days

        # Semaforo
        if taxa_registro >= 80 and taxa_conteudo >= 60:
            cor = 'verde'
        elif taxa_registro >= 60:
            cor = 'amarelo'
        elif registrado == 0:
            cor = 'cinza'
        else:
            cor = 'vermelho'

        # Nome limpo (remove sufixo "- BV - 2026")
        nome_limpo = prof.split(' - ')[0] if ' - ' in prof else prof

        resultados.append({
            'Professor': nome_limpo,
            'Professor_Raw': prof,
            'Unidade': unidade,
            'Disciplinas': ', '.join(sorted(disciplinas)),
            'Series': ', '.join(sorted(series, key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99)),
            'Aulas/Sem': aulas_semana,
            'Esperado': esperado,
            'Registrado': registrado,
            'Taxa Registro': round(taxa_registro, 1),
            'Taxa Conteudo': round(taxa_conteudo, 1),
            'Taxa Tarefa': round(taxa_tarefa, 1),
            'Dias Sem Registro': dias_sem,
            'Cor': cor,
        })

    return pd.DataFrame(resultados)


def render_semaforo_html(row):
    """Gera HTML do semaforo para uma linha."""
    css = f'semaforo-{row["Cor"]}'
    icon = {'verde': '🟢', 'amarelo': '🟡', 'vermelho': '🔴', 'cinza': '⚪'}.get(row['Cor'], '⚪')
    return f'{icon} {row["Taxa Registro"]:.0f}%'


def main():
    st.title("🚦 Semaforo do Professor")
    st.markdown("**Visao rapida: quem precisa de atencao HOJE**")

    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()

    if df_aulas.empty or df_horario.empty:
        st.error("Dados nao carregados. Execute a extracao do SIGA primeiro.")
        return

    df_aulas = filtrar_ate_hoje(df_aulas)
    semana = calcular_semana_letiva()
    capitulo = calcular_capitulo_esperado(semana)

    # ========== FILTROS ==========
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        un_opts = ['TODAS'] + sorted(df_horario['unidade'].unique().tolist())
        filtro_un = st.selectbox("🏫 Unidade", un_opts)

    with col_f2:
        seg_opts = ['TODOS', 'Anos Finais', 'Ensino Medio']
        filtro_seg = st.selectbox("📚 Segmento", seg_opts)

    with col_f3:
        cor_opts = ['TODOS', '🔴 Critico', '🟡 Atencao', '🟢 OK', '⚪ Sem dados']
        filtro_cor = st.selectbox("🚦 Status", cor_opts)

    # Filtra dados
    df_hor_f = df_horario.copy()
    df_aulas_f = df_aulas.copy()

    if filtro_un != 'TODAS':
        df_hor_f = df_hor_f[df_hor_f['unidade'] == filtro_un]
        df_aulas_f = df_aulas_f[df_aulas_f['unidade'] == filtro_un]

    if filtro_seg == 'Anos Finais':
        df_hor_f = df_hor_f[df_hor_f['serie'].isin(SERIES_FUND_II)]
        df_aulas_f = df_aulas_f[df_aulas_f['serie'].isin(SERIES_FUND_II)]
    elif filtro_seg == 'Ensino Medio':
        df_hor_f = df_hor_f[df_hor_f['serie'].isin(SERIES_EM)]
        df_aulas_f = df_aulas_f[df_aulas_f['serie'].isin(SERIES_EM)]

    # Calcula metricas
    df_semaforo = calcular_metricas_professor(df_aulas_f, df_hor_f, semana)

    if df_semaforo.empty:
        st.warning("Nenhum professor encontrado com os filtros selecionados.")
        return

    # Filtra por cor
    cor_map = {'🔴 Critico': 'vermelho', '🟡 Atencao': 'amarelo', '🟢 OK': 'verde', '⚪ Sem dados': 'cinza'}
    if filtro_cor != 'TODOS':
        df_semaforo = df_semaforo[df_semaforo['Cor'] == cor_map[filtro_cor]]

    # ========== CARDS RESUMO ==========
    st.markdown("---")

    n_verde = len(df_semaforo[df_semaforo['Cor'] == 'verde'])
    n_amarelo = len(df_semaforo[df_semaforo['Cor'] == 'amarelo'])
    n_vermelho = len(df_semaforo[df_semaforo['Cor'] == 'vermelho'])
    n_cinza = len(df_semaforo[df_semaforo['Cor'] == 'cinza'])
    n_total = len(df_semaforo)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="resumo-card card-verde">
            <h1 style="margin:0; font-size:3em; color:white;">{n_verde}</h1>
            <p style="margin:0; font-size:1.1em;">🟢 Em Dia</p>
            <small>≥80% registro + ≥60% conteudo</small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="resumo-card card-amarelo">
            <h1 style="margin:0; font-size:3em; color:#333;">{n_amarelo}</h1>
            <p style="margin:0; font-size:1.1em;">🟡 Atencao</p>
            <small>60-79% registro</small>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="resumo-card card-vermelho">
            <h1 style="margin:0; font-size:3em; color:white;">{n_vermelho + n_cinza}</h1>
            <p style="margin:0; font-size:1.1em;">🔴 Critico</p>
            <small>&lt;60% registro ou sem dados</small>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        pct_ok = (n_verde / n_total * 100) if n_total > 0 else 0
        st.markdown(f"""
        <div class="resumo-card card-total">
            <h1 style="margin:0; font-size:3em; color:white;">{pct_ok:.0f}%</h1>
            <p style="margin:0; font-size:1.1em;">Saude da Rede</p>
            <small>{n_total} professores no filtro</small>
        </div>
        """, unsafe_allow_html=True)

    # ========== MATRIZ SEMAFORO POR UNIDADE ==========
    st.markdown("---")
    st.header("🚦 Matriz por Unidade")

    if filtro_un == 'TODAS':
        # Mostra resumo por unidade
        resumo_un = df_semaforo.groupby('Unidade')['Cor'].value_counts().unstack(fill_value=0)
        for cor in ['verde', 'amarelo', 'vermelho', 'cinza']:
            if cor not in resumo_un.columns:
                resumo_un[cor] = 0

        resumo_un = resumo_un[['verde', 'amarelo', 'vermelho', 'cinza']]
        resumo_un.columns = ['🟢 Em Dia', '🟡 Atencao', '🔴 Critico', '⚪ Sem dados']
        resumo_un['Total'] = resumo_un.sum(axis=1)
        resumo_un['% Em Dia'] = (resumo_un['🟢 Em Dia'] / resumo_un['Total'] * 100).round(0).astype(int).astype(str) + '%'

        st.dataframe(resumo_un, use_container_width=True)

        # Grafico empilhado
        cores_graf = ['#4CAF50', '#FFC107', '#F44336', '#9E9E9E']
        fig = go.Figure()
        for col, cor in zip(['🟢 Em Dia', '🟡 Atencao', '🔴 Critico', '⚪ Sem dados'], cores_graf):
            fig.add_trace(go.Bar(
                name=col, x=resumo_un.index, y=resumo_un[col],
                marker_color=cor, text=resumo_un[col], textposition='inside'
            ))
        fig.update_layout(
            barmode='stack',
            title='Distribuicao de Professores por Unidade',
            yaxis_title='Quantidade',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    # ========== TABELA PRINCIPAL ==========
    st.markdown("---")
    st.header("📋 Detalhamento por Professor")

    # Ordena: vermelho primeiro, depois cinza, amarelo, verde
    ordem_cor = {'vermelho': 0, 'cinza': 1, 'amarelo': 2, 'verde': 3}
    df_semaforo['_ordem'] = df_semaforo['Cor'].map(ordem_cor)
    df_semaforo = df_semaforo.sort_values(['_ordem', 'Taxa Registro'])

    # Prepara tabela de exibicao
    df_show = df_semaforo[['Professor', 'Unidade', 'Disciplinas', 'Series',
                           'Aulas/Sem', 'Esperado', 'Registrado',
                           'Taxa Registro', 'Taxa Conteudo', 'Taxa Tarefa',
                           'Dias Sem Registro', 'Cor']].copy()

    # Icone de status
    icon_map = {'verde': '🟢', 'amarelo': '🟡', 'vermelho': '🔴', 'cinza': '⚪'}
    df_show['Status'] = df_show['Cor'].map(icon_map)
    df_show['Taxa Registro'] = df_show['Taxa Registro'].apply(lambda x: f'{x:.0f}%')
    df_show['Taxa Conteudo'] = df_show['Taxa Conteudo'].apply(lambda x: f'{x:.0f}%')
    df_show['Taxa Tarefa'] = df_show['Taxa Tarefa'].apply(lambda x: f'{x:.0f}%')

    # Reordena colunas
    cols_final = ['Status', 'Professor', 'Unidade', 'Disciplinas', 'Series',
                  'Registrado', 'Esperado', 'Taxa Registro',
                  'Taxa Conteudo', 'Taxa Tarefa', 'Dias Sem Registro']
    df_show = df_show[cols_final]

    st.dataframe(df_show, use_container_width=True, hide_index=True, height=500)

    # ========== DESTAQUES ==========
    st.markdown("---")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.subheader("🔴 Precisam de Atencao Imediata")
        criticos = df_semaforo[df_semaforo['Cor'].isin(['vermelho', 'cinza'])]
        if not criticos.empty:
            for _, row in criticos.head(10).iterrows():
                if row['Cor'] == 'cinza':
                    st.markdown(f"""
                    <div class="semaforo-cinza">
                        ⚪ <strong>{row['Professor']}</strong> ({row['Unidade']}) - {row['Disciplinas']}<br>
                        <small>NENHUM registro no periodo</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="semaforo-vermelho">
                        🔴 <strong>{row['Professor']}</strong> ({row['Unidade']}) - {row['Disciplinas']}<br>
                        <small>{row['Registrado']}/{row['Esperado']} aulas | {row['Taxa Registro']:.0f}% | {row['Dias Sem Registro']}d sem registro</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("Nenhum professor em situacao critica!")

    with col_d2:
        st.subheader("🏆 Destaques Positivos")
        top = df_semaforo[df_semaforo['Cor'] == 'verde'].nlargest(5, 'Taxa Registro')
        if not top.empty:
            for _, row in top.iterrows():
                st.markdown(f"""
                <div class="semaforo-verde">
                    🟢 <strong>{row['Professor']}</strong> ({row['Unidade']}) - {row['Disciplinas']}<br>
                    <small>{row['Taxa Registro']:.0f}% registro | {row['Taxa Conteudo']:.0f}% conteudo | {row['Taxa Tarefa']:.0f}% tarefa</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum professor atingiu status verde ainda.")

    # ========== HEATMAP POR SERIE x DISCIPLINA ==========
    st.markdown("---")
    st.header("🗺️ Mapa de Calor: Serie x Disciplina")

    # Para cada combinacao serie+disciplina, calcula taxa media
    if filtro_un != 'TODAS':
        unidade_heatmap = filtro_un
    else:
        un_hm_opts = sorted(df_horario['unidade'].unique().tolist())
        unidade_heatmap = st.selectbox("Selecione a unidade para o mapa:", un_hm_opts, key='hm_un')

    df_hor_hm = df_horario[df_horario['unidade'] == unidade_heatmap]
    df_aulas_hm = df_aulas[df_aulas['unidade'] == unidade_heatmap]

    # Agrupa por serie e disciplina
    heatmap_data = []
    series_hm = sorted(df_hor_hm['serie'].unique(), key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99)
    discs_hm = sorted(df_hor_hm['disciplina'].unique())

    for serie in series_hm:
        for disc in discs_hm:
            esp = len(df_hor_hm[(df_hor_hm['serie'] == serie) & (df_hor_hm['disciplina'] == disc)])
            if esp == 0:
                continue
            esp_total = esp * semana
            real = len(df_aulas_hm[(df_aulas_hm['serie'] == serie) & (df_aulas_hm['disciplina'] == disc)])
            taxa = (real / esp_total * 100) if esp_total > 0 else 0
            heatmap_data.append({
                'Serie': serie,
                'Disciplina': disc,
                'Taxa': round(taxa, 1)
            })

    if heatmap_data:
        df_hm = pd.DataFrame(heatmap_data)
        pivot_hm = df_hm.pivot(index='Disciplina', columns='Serie', values='Taxa')
        # Reordena colunas
        cols_ord = [s for s in ORDEM_SERIES if s in pivot_hm.columns]
        pivot_hm = pivot_hm[cols_ord]

        fig_hm = go.Figure(data=go.Heatmap(
            z=pivot_hm.values,
            x=pivot_hm.columns.tolist(),
            y=pivot_hm.index.tolist(),
            colorscale=[[0, '#F44336'], [0.6, '#FFC107'], [0.8, '#FFEB3B'], [1.0, '#4CAF50']],
            zmin=0, zmax=100,
            text=[[f'{v:.0f}%' if pd.notna(v) else '' for v in row] for row in pivot_hm.values],
            texttemplate='%{text}',
            textfont={'size': 12},
            colorbar={'title': 'Conformidade %'}
        ))
        fig_hm.update_layout(
            title=f'Conformidade por Serie x Disciplina ({unidade_heatmap})',
            height=max(400, len(pivot_hm) * 30 + 100),
            yaxis={'autorange': 'reversed'}
        )
        st.plotly_chart(fig_hm, use_container_width=True)

    # ========== EXPORTACAO ==========
    st.markdown("---")
    st.header("📥 Exportar")

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        csv_data = df_show.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 Download Semaforo (CSV)",
            csv_data,
            f"semaforo_professores_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )

    with col_e2:
        # Gera relatorio TXT para impressao
        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("     SEMAFORO DO PROFESSOR - COLEGIO ELO 2026")
        relatorio.append("=" * 80)
        relatorio.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        relatorio.append(f"Semana letiva: {semana}a | Capitulo esperado: {capitulo}")
        relatorio.append(f"Filtro: {filtro_un} | {filtro_seg}")
        relatorio.append("")
        relatorio.append(f"RESUMO: {n_verde} em dia | {n_amarelo} atencao | {n_vermelho} critico | {n_cinza} sem dados")
        relatorio.append("-" * 80)
        relatorio.append("")

        for cor_label, cor_val, emoji in [('CRITICO', 'vermelho', '🔴'), ('SEM DADOS', 'cinza', '⚪'),
                                           ('ATENCAO', 'amarelo', '🟡'), ('EM DIA', 'verde', '🟢')]:
            grupo = df_semaforo[df_semaforo['Cor'] == cor_val]
            if not grupo.empty:
                relatorio.append(f"{emoji} {cor_label} ({len(grupo)} professores)")
                relatorio.append("-" * 40)
                for _, row in grupo.iterrows():
                    relatorio.append(f"  {row['Professor']:<30} {row['Unidade']:<5} {row['Taxa Registro']:5.0f}% reg | {row['Taxa Conteudo']:5.0f}% cont | {row['Dias Sem Registro']:2d}d")
                relatorio.append("")

        relatorio.append("=" * 80)
        relatorio.append("                 Coordenacao Pedagogica - Colegio ELO")
        relatorio.append("=" * 80)

        txt = "\n".join(relatorio)
        st.download_button(
            "🖨️ Imprimir Relatorio (TXT)",
            txt.encode('utf-8'),
            f"semaforo_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            "text/plain"
        )


if __name__ == "__main__":
    main()
