#!/usr/bin/env python3
"""
PAGINA 18: ANALISE POR TURMA
Visao cross-disciplina para uma turma/serie:
saude da turma, alinhamento entre disciplinas, gaps.
"""

import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
    filtrar_por_periodo, PERIODOS_OPCOES,
    calcular_semana_letiva, calcular_capitulo_esperado, _hoje,
    SERIES_FUND_II, SERIES_EM,
    CONFORMIDADE_META, CONFORMIDADE_BAIXO, CONFORMIDADE_CRITICO,
    CONTEUDO_VAZIO_ALERTA,
    DIAS_SEM_REGISTRO_ATENCAO, DIAS_SEM_REGISTRO_URGENTE,
)
from config_cores import CORES_SERIES, CORES_UNIDADES, ORDEM_SERIES

st.set_page_config(page_title="Analise por Turma", page_icon="🏫", layout="wide")
from auth import check_password, logout_button, get_user_unit
if not check_password():
    st.stop()
logout_button()

# Regex para detectar capitulos
CAP_PATTERNS = [
    r'[Cc]ap(?:ítulo|itulo)?\.?\s*(\d{1,2})',
    r'[Uu]nidade\s+(\d{1,2})',
]


def extrair_capitulo(texto):
    if pd.isna(texto) or texto in ('.', '', ','):
        return None
    for pattern in CAP_PATTERNS:
        match = re.search(pattern, str(texto))
        if match:
            cap = int(match.group(1))
            if 1 <= cap <= 12:
                return cap
    return None


@st.cache_data(ttl=300)
def calcular_saude_turma(df_turma, df_horario, semana, unidade, serie):
    """Calcula score de saude da turma (0-100)."""
    score = 0
    peso_total = 0

    disciplinas = df_turma['disciplina'].dropna().unique()

    for disc in disciplinas:
        df_d = df_turma[df_turma['disciplina'] == disc]

        # Conformidade da disciplina
        slots = len(df_horario[
            (df_horario['unidade'] == unidade) &
            (df_horario['serie'] == serie) &
            (df_horario['disciplina'] == disc)
        ])
        esperado = slots * semana
        realizado = len(df_d)
        conf = min(100, (realizado / esperado * 100) if esperado > 0 else 0)

        # Qualidade
        vazios = df_d['conteudo'].isin(['.', ',', '-', '']).sum() + df_d['conteudo'].isna().sum()
        pct_preenchido = ((len(df_d) - vazios) / len(df_d) * 100) if len(df_d) > 0 else 0

        # Score da disciplina: 60% conformidade + 40% qualidade
        score_disc = conf * 0.6 + pct_preenchido * 0.4
        peso = slots if slots > 0 else 1
        score += score_disc * peso
        peso_total += peso

    return (score / peso_total) if peso_total > 0 else 0


def main():
    st.title("🏫 Analise por Turma")
    st.markdown("**Visao completa de cada turma: todas as disciplinas, alinhamento e saude**")

    df = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()

    if df.empty:
        st.error("Dados nao carregados.")
        return

    df = filtrar_ate_hoje(df)

    # Filtro de periodo (selectbox sera renderizado abaixo nos filtros)
    periodo_sel = st.session_state.get('periodo_18', PERIODOS_OPCOES[0])
    df = filtrar_por_periodo(df, periodo_sel)

    hoje = _hoje()
    semana = calcular_semana_letiva(hoje)
    cap_esperado = calcular_capitulo_esperado(semana)

    # Enriquece
    df['capitulo_detectado'] = df['conteudo'].apply(extrair_capitulo)

    # ========== FILTROS ==========
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        opcoes_un = sorted(df['unidade'].dropna().unique().tolist())
        user_unit = get_user_unit()
        default_un = opcoes_un.index(user_unit) if user_unit and user_unit in opcoes_un else 0
        un_sel = st.selectbox("Unidade:", opcoes_un, index=default_un)

    with col_f2:
        st.selectbox("Periodo:", PERIODOS_OPCOES, key='periodo_18')

    # Filtra por unidade
    df_un = df[df['unidade'] == un_sel]
    df_hor_un = df_horario[df_horario['unidade'] == un_sel]

    with col_f3:
        series_disponiveis = [s for s in ORDEM_SERIES if s in df_un['serie'].unique()]
        serie_sel = st.selectbox("Serie:", series_disponiveis)

    with col_f4:
        turmas_serie = sorted(df_un[df_un['serie'] == serie_sel]['turma'].dropna().unique())
        if len(turmas_serie) > 1:
            turma_sel = st.selectbox("Turma:", ['TODAS'] + turmas_serie)
        else:
            turma_sel = turmas_serie[0] if turmas_serie else 'TODAS'
            st.info(f"Turma: {turma_sel}")

    # Filtra
    df_turma = df_un[df_un['serie'] == serie_sel]
    if turma_sel != 'TODAS':
        df_turma = df_turma[df_turma['turma'] == turma_sel]

    if len(df_turma) == 0:
        st.warning("Nenhum registro para esta turma.")
        return

    # ========== SAUDE DA TURMA ==========
    saude = calcular_saude_turma(df_turma, df_hor_un, semana, un_sel, serie_sel)
    cor_saude = '#43A047' if saude >= CONFORMIDADE_META else ('#F57C00' if saude >= 60 else '#E53935')

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {cor_saude}dd 0%, {cor_saude} 100%); color: white; padding: 25px; border-radius: 15px; margin: 10px 0;">
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div style="text-align: center;">
                <p style="margin: 0; opacity: 0.9; font-size: 1.1em;">Saude da Turma</p>
                <p style="font-size: 3em; font-weight: bold; margin: 0;">{saude:.0f}</p>
                <p style="margin: 0; opacity: 0.8;">de 100</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; opacity: 0.9;">Serie</p>
                <p style="font-size: 1.5em; font-weight: bold; margin: 0;">{serie_sel}</p>
                <p style="margin: 0; opacity: 0.8;">{un_sel}</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; opacity: 0.9;">Disciplinas</p>
                <p style="font-size: 1.5em; font-weight: bold; margin: 0;">{df_turma['disciplina'].nunique()}</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; opacity: 0.9;">Professores</p>
                <p style="font-size: 1.5em; font-weight: bold; margin: 0;">{df_turma['professor'].nunique()}</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; opacity: 0.9;">Total Aulas</p>
                <p style="font-size: 1.5em; font-weight: bold; margin: 0;">{len(df_turma):,}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ========== TABS ==========
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Panorama Disciplinas",
        "📖 Alinhamento Capitulos",
        "👨‍🏫 Mapa de Professores",
        "📋 Detalhes"
    ])

    # ========== TAB 1: PANORAMA ==========
    with tab1:
        st.header("📊 Panorama por Disciplina")

        panorama = []
        for disc in sorted(df_turma['disciplina'].dropna().unique()):
            df_d = df_turma[df_turma['disciplina'] == disc]

            # Conformidade
            slots = len(df_hor_un[
                (df_hor_un['serie'] == serie_sel) & (df_hor_un['disciplina'] == disc)
            ])
            esperado = slots * semana
            realizado = len(df_d)
            conf = (realizado / esperado * 100) if esperado > 0 else 0

            # Qualidade
            vazios = df_d['conteudo'].isin(['.', ',', '-', '']).sum() + df_d['conteudo'].isna().sum()
            pct_preenchido = ((len(df_d) - vazios) / len(df_d) * 100) if len(df_d) > 0 else 0

            # Capitulo
            caps = df_d['capitulo_detectado'].dropna()
            max_cap = int(caps.max()) if len(caps) > 0 else 0

            # Professor(es)
            profs = ', '.join(df_d['professor'].dropna().unique()[:2])

            # Status geral
            if conf >= CONFORMIDADE_META and pct_preenchido >= CONFORMIDADE_BAIXO:
                status = '✅'
            elif conf >= CONFORMIDADE_BAIXO or pct_preenchido >= CONFORMIDADE_CRITICO:
                status = '⚠️'
            else:
                status = '🔴'

            panorama.append({
                'Status': status,
                'Disciplina': disc,
                'Professor(es)': profs,
                'Aulas/Sem': slots,
                'Registradas': realizado,
                'Esperadas': esperado,
                'Conformidade': f"{conf:.0f}%",
                '% Preenchido': f"{pct_preenchido:.0f}%",
                'Cap. Max': max_cap if max_cap > 0 else '-',
                'Cap. Esperado': cap_esperado,
            })

        df_pan = pd.DataFrame(panorama)
        st.dataframe(df_pan, use_container_width=True, hide_index=True)

        # Grafico radar de conformidade por disciplina
        if len(panorama) >= 3:
            st.subheader("Radar de Conformidade")

            conf_values = [float(p['Conformidade'].replace('%', '')) for p in panorama]
            disc_names = [p['Disciplina'][:15] for p in panorama]

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=conf_values + [conf_values[0]],
                theta=disc_names + [disc_names[0]],
                fill='toself',
                name='Conformidade',
                line=dict(color='#1976D2'),
            ))
            fig.add_trace(go.Scatterpolar(
                r=[CONFORMIDADE_META] * (len(disc_names) + 1),
                theta=disc_names + [disc_names[0]],
                fill='none',
                name=f'Meta {CONFORMIDADE_META}%',
                line=dict(color='#43A047', dash='dash'),
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 120])),
                showlegend=True,
                height=450,
                title=f'Radar de Conformidade - {serie_sel} ({un_sel})',
            )
            st.plotly_chart(fig, use_container_width=True)

        # Barras empilhadas: registrado vs esperado
        st.subheader("Registrado vs Esperado")

        fig = go.Figure()
        for p in panorama:
            fig.add_trace(go.Bar(
                name=p['Disciplina'],
                x=[p['Disciplina']],
                y=[p['Registradas']],
                marker_color='#1976D2',
                showlegend=False,
            ))

        # Adiciona linha de esperado
        fig.add_trace(go.Scatter(
            x=[p['Disciplina'] for p in panorama],
            y=[p['Esperadas'] for p in panorama],
            mode='markers+lines',
            name='Esperado',
            line=dict(color='#E53935', dash='dash'),
            marker=dict(size=10, symbol='diamond'),
        ))
        fig.update_layout(title=f'Aulas Registradas vs Esperadas - {serie_sel}', barmode='group')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # ========== TAB 2: ALINHAMENTO DE CAPITULOS ==========
    with tab2:
        st.header("📖 Alinhamento de Capitulos entre Disciplinas")

        st.markdown(f"""
        Verifica se as disciplinas estao progredindo de forma alinhada.
        **Capitulo esperado para semana {semana}: {cap_esperado}/12**
        """)

        # Mapa de capitulos por disciplina
        cap_data = []
        for disc in sorted(df_turma['disciplina'].dropna().unique()):
            df_d = df_turma[df_turma['disciplina'] == disc]
            caps = df_d['capitulo_detectado'].dropna()
            max_cap = int(caps.max()) if len(caps) > 0 else 0
            min_cap = int(caps.min()) if len(caps) > 0 else 0

            diff = max_cap - cap_esperado
            if diff > 0:
                status = 'Adiantado'
            elif diff >= -1:
                status = 'No prazo'
            elif max_cap > 0:
                status = 'Atrasado'
            else:
                status = 'Sem dados'

            cap_data.append({
                'Disciplina': disc,
                'Cap. Minimo': min_cap if min_cap > 0 else '-',
                'Cap. Maximo': max_cap if max_cap > 0 else '-',
                'Esperado': cap_esperado,
                'Diferenca': diff if max_cap > 0 else '-',
                'Status': status,
            })

        df_cap = pd.DataFrame(cap_data)
        st.dataframe(df_cap, use_container_width=True, hide_index=True)

        # Grafico de barras: capitulo atual vs esperado
        cap_plot = [c for c in cap_data if c['Cap. Maximo'] != '-']
        if cap_plot:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[c['Disciplina'] for c in cap_plot],
                y=[c['Cap. Maximo'] for c in cap_plot],
                name='Cap. Atual (detectado)',
                marker_color=[
                    '#43A047' if c['Status'] == 'Adiantado'
                    else '#1976D2' if c['Status'] == 'No prazo'
                    else '#E53935'
                    for c in cap_plot
                ],
            ))
            fig.add_hline(y=cap_esperado, line_dash="dash", line_color="red",
                         annotation_text=f"Esperado: Cap {cap_esperado}")
            fig.update_layout(
                title=f'Capitulo Maximo Detectado por Disciplina - {serie_sel}',
                yaxis_title='Capitulo',
                yaxis=dict(range=[0, 13]),
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        # Alertas de desalinhamento
        atrasados = [c for c in cap_data if c['Status'] == 'Atrasado']
        sem_dados = [c for c in cap_data if c['Status'] == 'Sem dados']

        if atrasados:
            st.warning(f"⚠️ {len(atrasados)} disciplina(s) atrasada(s): " +
                      ', '.join(c['Disciplina'] for c in atrasados))

        if sem_dados:
            st.info(f"ℹ️ {len(sem_dados)} disciplina(s) sem mencao a capitulos: " +
                   ', '.join(c['Disciplina'] for c in sem_dados))

    # ========== TAB 3: MAPA DE PROFESSORES ==========
    with tab3:
        st.header("👨‍🏫 Mapa de Professores da Turma")

        prof_map = []
        for prof in sorted(df_turma['professor'].dropna().unique()):
            df_p = df_turma[df_turma['professor'] == prof]
            discs = ', '.join(sorted(df_p['disciplina'].dropna().unique()))
            ultimo_reg = df_p['data'].max()
            dias_sem = (_hoje() - ultimo_reg).days if pd.notna(ultimo_reg) else 999

            # Qualidade
            vazios = df_p['conteudo'].isin(['.', ',', '-', '']).sum() + df_p['conteudo'].isna().sum()
            pct_preenchido = ((len(df_p) - vazios) / len(df_p) * 100) if len(df_p) > 0 else 0

            # Status
            if dias_sem > DIAS_SEM_REGISTRO_URGENTE or pct_preenchido < CONTEUDO_VAZIO_ALERTA:
                status = '🔴'
            elif dias_sem > DIAS_SEM_REGISTRO_ATENCAO or pct_preenchido < 60:
                status = '⚠️'
            else:
                status = '✅'

            prof_map.append({
                'Status': status,
                'Professor': prof,
                'Disciplina(s)': discs,
                'Aulas': len(df_p),
                'Ultimo Registro': ultimo_reg.strftime('%d/%m') if pd.notna(ultimo_reg) else '-',
                'Dias Sem Reg.': dias_sem if dias_sem < 999 else '-',
                '% Preenchido': f"{pct_preenchido:.0f}%",
            })

        df_prof_map = pd.DataFrame(prof_map)
        st.dataframe(df_prof_map, use_container_width=True, hide_index=True)

        # Timeline: quando cada professor registrou
        st.subheader("Timeline de Registros")

        timeline_data = df_turma.groupby([
            df_turma['data'].dt.strftime('%d/%m'),
            'professor'
        ]).size().reset_index(name='aulas')
        timeline_data.columns = ['Data', 'Professor', 'Aulas']

        if len(timeline_data) > 0:
            fig = px.scatter(
                timeline_data, x='Data', y='Professor', size='Aulas',
                color='Aulas', color_continuous_scale='Blues',
                title=f'Quando Cada Professor Registrou - {serie_sel}',
            )
            fig.update_layout(height=max(300, len(df_turma['professor'].unique()) * 30 + 100))
            st.plotly_chart(fig, use_container_width=True)

    # ========== TAB 4: DETALHES ==========
    with tab4:
        st.header("📋 Detalhes de Aulas da Turma")

        # Filtro de disciplina
        discs_turma = ['TODAS'] + sorted(df_turma['disciplina'].dropna().unique().tolist())
        disc_det = st.selectbox("Disciplina:", discs_turma)

        df_det = df_turma.copy()
        if disc_det != 'TODAS':
            df_det = df_det[df_det['disciplina'] == disc_det]

        df_det = df_det.sort_values('data', ascending=False)

        # Formata para exibicao
        colunas_show = ['data', 'disciplina', 'professor', 'conteudo', 'tarefa']
        df_show = df_det[colunas_show].copy()
        df_show['data'] = df_show['data'].dt.strftime('%d/%m/%Y')

        st.dataframe(df_show, use_container_width=True, hide_index=True, height=500)

        # Contagem por disciplina
        st.subheader("Distribuicao de Aulas por Disciplina")

        disc_count = df_turma.groupby('disciplina').size().reset_index(name='aulas')
        disc_count = disc_count.sort_values('aulas', ascending=False)

        fig = px.bar(disc_count, x='disciplina', y='aulas',
                    title=f'Aulas por Disciplina - {serie_sel} ({un_sel})',
                    color_discrete_sequence=['#1976D2'])
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # ========== COMPARATIVO ENTRE UNIDADES (mesmo serie) ==========
    if len(df[df['serie'] == serie_sel]['unidade'].unique()) > 1:
        st.markdown("---")
        st.header(f"🔄 Comparativo: {serie_sel} entre Unidades")

        comp = []
        for un in sorted(df[df['serie'] == serie_sel]['unidade'].unique()):
            df_un_comp = df[(df['serie'] == serie_sel) & (df['unidade'] == un)]
            df_hor_comp = df_horario[(df_horario['serie'] == serie_sel) & (df_horario['unidade'] == un)]

            saude_un = calcular_saude_turma(df_un_comp, df_horario, semana, un, serie_sel)

            comp.append({
                'Unidade': un,
                'Saude': f"{saude_un:.0f}",
                'Aulas': len(df_un_comp),
                'Professores': df_un_comp['professor'].nunique(),
                'Disciplinas': df_un_comp['disciplina'].nunique(),
            })

        df_comp = pd.DataFrame(comp)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)

        # Grafico
        df_comp['Saude_Num'] = df_comp['Saude'].astype(float)
        fig = px.bar(df_comp, x='Unidade', y='Saude_Num',
                    color='Unidade', color_discrete_map=CORES_UNIDADES,
                    title=f'Saude da Turma {serie_sel} por Unidade')
        fig.add_hline(y=CONFORMIDADE_META, line_dash="dash", line_color="green", annotation_text=f"Meta {CONFORMIDADE_META}")
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
