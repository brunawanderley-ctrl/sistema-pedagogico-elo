#!/usr/bin/env python3
"""
DASHBOARD CEO - EXCELÊNCIA PEDAGÓGICA
Colégio ELO 2026 | 5 Abas Estratégicas

Uso: streamlit run Dashboard_CEO.py --server.port 8510
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import date, datetime
import math
import subprocess
import os

# ========== CONFIGURAÇÃO ==========
st.set_page_config(
    page_title="CEO - Excelência Pedagógica",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_DIR = Path(__file__).parent / "power_bi"
INICIO_LETIVO = date(2026, 1, 26)
HOJE = date.today()

NOMES_UNIDADES = {"BV": "Boa Viagem", "CD": "Candeias", "JG": "Janga", "CDR": "Cordeiro"}
CORES_UNIDADES = {"BV": "#1976D2", "CD": "#388E3C", "JG": "#F57C00", "CDR": "#7B1FA2"}
CORES_SERIES = {
    "6º Ano": "#64B5F6", "7º Ano": "#42A5F5", "8º Ano": "#1E88E5",
    "9º Ano": "#FFA726", "1ª Série": "#66BB6A", "2ª Série": "#388E3C", "3ª Série": "#E53935",
}
CORES_STATUS = {"Excelente": "#43A047", "Bom": "#66BB6A", "Atenção": "#FFA726", "Crítico": "#E53935"}
CORES_TIER = {"Verde": "#43A047", "Monitorar": "#FFC107", "Atenção": "#FF9800", "Crítico": "#E53935"}
ORDEM_SERIES = ["6º Ano", "7º Ano", "8º Ano", "9º Ano", "1ª Série", "2ª Série", "3ª Série"]


def semana_letiva():
    return max(1, (HOJE - INICIO_LETIVO).days // 7 + 1)


def capitulo_esperado(sem):
    return min(12, math.ceil(sem / 3.5))


def trimestre(sem):
    if sem <= 14:
        return "1º Trimestre"
    elif sem <= 28:
        return "2º Trimestre"
    return "3º Trimestre"


SEM = semana_letiva()
CAP = capitulo_esperado(SEM)
TRI = trimestre(SEM)


# ========== CARREGAMENTO DE DADOS ==========
@st.cache_data(ttl=300)
def carregar(nome):
    path = DATA_DIR / nome
    if path.exists():
        return pd.read_csv(path, encoding="utf-8-sig")
    return pd.DataFrame()


def carregar_tudo():
    return {
        "prof": carregar("score_Professor.csv"),
        "abc": carregar("score_Aluno_ABC.csv"),
        "exec": carregar("resumo_Executivo.csv"),
        "aulas": carregar("fato_Aulas.csv"),
        "ocorr": carregar("fato_Ocorrencias.csv"),
        "cruz": carregar("fato_Cruzamento.csv"),
        "engaj": carregar("fato_Engajamento_SAE.csv"),
        "notas": carregar("fato_Notas_Historico.csv"),
        "alunos": carregar("dim_Alunos.csv"),
        "disc": carregar("dim_Disciplinas.csv"),
    }


# ========== CSS ==========
st.markdown("""
<style>
    .main > div { padding-top: 0.5rem; }
    h1 { text-align: center; color: #1a237e; margin-bottom: 0; }
    .subtitle { text-align: center; color: #5c6bc0; font-size: 1.1em; margin-bottom: 1rem; }

    .kpi-card {
        padding: 20px 15px; border-radius: 12px; text-align: center;
        color: white; min-height: 130px;
        display: flex; flex-direction: column; justify-content: center;
    }
    .kpi-card h2 { margin: 0; font-size: 2.2em; color: white; border: none; padding: 0; }
    .kpi-card p { margin: 4px 0 0 0; font-size: 0.9em; opacity: 0.9; }

    .semaforo-card {
        padding: 18px; border-radius: 12px; text-align: center;
        min-height: 140px; color: white;
        display: flex; flex-direction: column; justify-content: center;
    }
    .semaforo-card h3 { color: white; border: none; margin: 0; padding: 0; font-size: 1.1em; }
    .semaforo-card .valor { font-size: 2.5em; font-weight: bold; margin: 5px 0; }
    .semaforo-card .meta { font-size: 0.85em; opacity: 0.8; }

    .alerta-box {
        padding: 14px 18px; border-radius: 8px; margin: 6px 0;
        border-left: 5px solid;
    }
    .alerta-urgente { background: #FFEBEE; border-color: #D32F2F; }
    .alerta-atencao { background: #FFF3E0; border-color: #F57C00; }
    .alerta-info { background: #E3F2FD; border-color: #1976D2; }
    .alerta-ok { background: #E8F5E9; border-color: #388E3C; }

    .stat-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 0; border-bottom: 1px solid #eee;
    }

    .quadrante-label {
        font-size: 0.85em; font-weight: 600; padding: 4px 10px;
        border-radius: 12px; display: inline-block;
    }

    div[data-testid="stMetric"] label { font-size: 0.85em; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { font-size: 1.8em; }
</style>
""", unsafe_allow_html=True)


# ========== AUTENTICAÇÃO DESATIVADA (acesso direto CEO) ==========


# ========== HEADER ==========
st.markdown("# 🎯 Excelência Pedagógica")
st.markdown(f'<p class="subtitle">Semana {SEM} | Capítulo {CAP} esperado | {TRI} | {HOJE.strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

# Dados
dados = carregar_tudo()

# Sidebar: filtros + atualizar
with st.sidebar:
    st.markdown("### Filtros")
    unidades_opcoes = ["Todas"] + list(NOMES_UNIDADES.keys())
    filtro_unidade = st.selectbox("Unidade", unidades_opcoes, format_func=lambda x: NOMES_UNIDADES.get(x, x))

    series_opcoes = ["Todas"] + ORDEM_SERIES
    filtro_serie = st.selectbox("Série", series_opcoes)

    st.markdown("---")
    st.markdown("### Atualizar Dados")
    if st.button("Regenerar CSVs", type="primary"):
        script = Path(__file__).parent / "gerar_csvs_powerbi_ceo.py"
        with st.spinner("Gerando CSVs..."):
            result = subprocess.run(["python3", str(script)], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            st.success("CSVs atualizados!")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(result.stderr or result.stdout)



def aplicar_filtros(df, col_unidade="unidade", col_serie="serie"):
    """Aplica filtros de unidade e série."""
    if df.empty:
        return df
    if filtro_unidade != "Todas" and col_unidade in df.columns:
        df = df[df[col_unidade] == filtro_unidade]
    if filtro_serie != "Todas" and col_serie in df.columns:
        df = df[df[col_serie] == filtro_serie]
    return df


# ========================================================================
# ABAS
# ========================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Pulso da Escola",
    "👨‍🏫 Raio-X Professor",
    "🎓 Perfil do Aluno",
    "📖 Engajamento SAE",
    "🎯 Painel de Ação",
])


# ========================================================================
# ABA 1: PULSO DA ESCOLA
# ========================================================================
with tab1:
    resumo = dados["exec"]
    prof = aplicar_filtros(dados["prof"])
    abc = aplicar_filtros(dados["abc"])
    aulas = dados["aulas"].copy()

    if not aulas.empty:
        aulas["data"] = pd.to_datetime(aulas["data"], errors="coerce")
        aulas = aulas[aulas["data"] <= pd.Timestamp(HOJE)]
        aulas = aplicar_filtros(aulas)

    # --- KPIs ---
    col1, col2, col3, col4, col5 = st.columns(5)

    # KPI 1: Conformidade
    conf = prof["pct_conformidade"].mean() if not prof.empty else 0
    cor_conf = "#43A047" if conf >= 85 else ("#FFA726" if conf >= 70 else "#E53935")
    col1.markdown(f'''<div class="kpi-card" style="background: linear-gradient(135deg, {cor_conf}, {cor_conf}dd);">
        <h2>{conf:.0f}%</h2><p>Conformidade<br>Meta: 80%</p>
    </div>''', unsafe_allow_html=True)

    # KPI 2: Professores no ritmo
    if not prof.empty:
        profs_ritmo = prof.groupby("professor_normalizado")["pct_conformidade"].mean()
        pct_ritmo = (profs_ritmo >= 70).sum() / max(1, len(profs_ritmo)) * 100
    else:
        pct_ritmo = 0
    cor_ritmo = "#43A047" if pct_ritmo >= 80 else ("#FFA726" if pct_ritmo >= 60 else "#E53935")
    col2.markdown(f'''<div class="kpi-card" style="background: linear-gradient(135deg, {cor_ritmo}, {cor_ritmo}dd);">
        <h2>{pct_ritmo:.0f}%</h2><p>Professores no Ritmo<br>Meta: 80%</p>
    </div>''', unsafe_allow_html=True)

    # KPI 3: Conteúdo preenchido
    if not aulas.empty:
        def conteudo_real(t):
            if pd.isna(t): return False
            return str(t).strip() not in ("", ".", "..", ",", "-", "--", "...")
        pct_cont = aulas["conteudo"].apply(conteudo_real).mean() * 100
    else:
        pct_cont = 0
    cor_cont = "#43A047" if pct_cont >= 90 else ("#FFA726" if pct_cont >= 70 else "#E53935")
    col3.markdown(f'''<div class="kpi-card" style="background: linear-gradient(135deg, {cor_cont}, {cor_cont}dd);">
        <h2>{pct_cont:.0f}%</h2><p>Conteúdo Preenchido<br>Meta: 90%</p>
    </div>''', unsafe_allow_html=True)

    # KPI 4: Média notas
    media = abc["media_geral"].mean() if not abc.empty and abc["media_geral"].notna().any() else 0
    cor_nota = "#43A047" if media >= 7 else ("#FFA726" if media >= 5 else "#E53935")
    col4.markdown(f'''<div class="kpi-card" style="background: linear-gradient(135deg, {cor_nota}, {cor_nota}dd);">
        <h2>{media:.1f}</h2><p>Média Geral (2025)<br>Meta: 6.0</p>
    </div>''', unsafe_allow_html=True)

    # KPI 5: Alunos em risco
    if not abc.empty:
        pct_risco = (abc["tier"] >= 2).sum() / max(1, len(abc)) * 100
    else:
        pct_risco = 0
    cor_risco = "#43A047" if pct_risco <= 5 else ("#FFA726" if pct_risco <= 15 else "#E53935")
    col5.markdown(f'''<div class="kpi-card" style="background: linear-gradient(135deg, {cor_risco}, {cor_risco}dd);">
        <h2>{pct_risco:.0f}%</h2><p>Alunos em Risco<br>Meta: < 10%</p>
    </div>''', unsafe_allow_html=True)

    st.markdown("")

    # --- SEMÁFORO POR UNIDADE ---
    st.subheader("Semáforo por Unidade")
    cols_u = st.columns(4)
    for i, (cod, nome) in enumerate(NOMES_UNIDADES.items()):
        profs_u = dados["prof"][dados["prof"]["unidade"] == cod]
        conf_u = profs_u["pct_conformidade"].mean() if not profs_u.empty else 0
        n_profs = profs_u["professor_normalizado"].nunique() if not profs_u.empty else 0

        abc_u = dados["abc"][dados["abc"]["unidade"] == cod]
        n_alunos = len(abc_u)

        cor = "#43A047" if conf_u >= 85 else ("#FFA726" if conf_u >= 70 else "#E53935")
        icone = "✅" if conf_u >= 85 else ("⚠️" if conf_u >= 70 else "🔴")

        cols_u[i].markdown(f'''<div class="semaforo-card" style="background: linear-gradient(135deg, {CORES_UNIDADES[cod]}, {CORES_UNIDADES[cod]}cc);">
            <h3>{nome}</h3>
            <div class="valor">{icone} {conf_u:.0f}%</div>
            <div class="meta">{n_profs} professores | {n_alunos} alunos</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("")

    # --- TENDÊNCIA + ALERTAS ---
    c_left, c_right = st.columns([3, 2])

    with c_left:
        st.subheader("Aulas Registradas por Semana")
        if not aulas.empty and "semana_letiva" in aulas.columns:
            aulas_sem = aulas.groupby("semana_letiva").size().reset_index(name="aulas")
            aulas_sem = aulas_sem[aulas_sem["semana_letiva"] <= SEM]
            fig = px.bar(aulas_sem, x="semana_letiva", y="aulas",
                         labels={"semana_letiva": "Semana Letiva", "aulas": "Aulas Registradas"},
                         color_discrete_sequence=["#5C6BC0"])
            fig.update_layout(height=300, margin=dict(t=10, b=30, l=40, r=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de aulas para exibir tendência.")

    with c_right:
        st.subheader("Alertas Principais")
        # Professor com pior score
        if not prof.empty:
            piores = prof.groupby("professor_normalizado").agg(
                score=("score_composto", "mean"), unidade=("unidade", "first")
            ).sort_values("score").head(3)
            for _, row in piores.iterrows():
                nome_p = row.name.title()
                st.markdown(f'''<div class="alerta-box alerta-urgente">
                    <strong>🔴 {nome_p}</strong> ({row["unidade"]})<br>
                    Score: {row["score"]:.0f}/100
                </div>''', unsafe_allow_html=True)

        # Disciplinas sem registro
        if not aulas.empty:
            disc_registradas = set(aulas["disciplina"].unique())
            disc_todas = set(dados["disc"]["disciplina"].unique()) if not dados["disc"].empty else set()
            sem_registro = disc_todas - disc_registradas
            if sem_registro:
                lista = ", ".join(sorted(sem_registro)[:5])
                st.markdown(f'''<div class="alerta-box alerta-atencao">
                    <strong>⚠️ Disciplinas sem registro:</strong><br>{lista}
                </div>''', unsafe_allow_html=True)

        # Classificação geral dos professores
        if not prof.empty:
            classif = prof.groupby("professor_normalizado")["classificacao"].first().value_counts()
            total_p = classif.sum()
            criticos = classif.get("Crítico", 0)
            if criticos > 0:
                st.markdown(f'''<div class="alerta-box alerta-info">
                    <strong>📊 Distribuição:</strong> {classif.get("Excelente", 0)} excelentes,
                    {classif.get("Bom", 0)} bons, {classif.get("Atenção", 0)} atenção,
                    {criticos} críticos (de {total_p} professores)
                </div>''', unsafe_allow_html=True)


# ========================================================================
# ABA 2: RAIO-X DO PROFESSOR
# ========================================================================
with tab2:
    prof = aplicar_filtros(dados["prof"])

    if prof.empty:
        st.warning("Sem dados de score de professores. Rode `python3 gerar_csvs_powerbi_ceo.py` primeiro.")
    else:
        # Agregado por professor
        prof_agg = prof.groupby("professor_normalizado").agg(
            professor_nome=("professor_nome", "first"),
            unidade=("unidade", "first"),
            pct_conformidade=("pct_conformidade", "mean"),
            pct_qualidade_conteudo=("pct_qualidade_conteudo", "mean"),
            pct_uso_tarefas=("pct_uso_tarefas", "mean"),
            pct_alinhamento=("pct_alinhamento", "mean"),
            score_composto=("score_composto", "mean"),
            classificacao=("classificacao", "first"),
            quadrante=("quadrante", "first"),
            aulas_registradas=("aulas_registradas", "sum"),
        ).reset_index().sort_values("score_composto", ascending=False)

        # KPIs rápidos
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Professores", len(prof_agg))
        c2.metric("Score Médio", f"{prof_agg['score_composto'].mean():.0f}/100")
        c3.metric("Excelentes", (prof_agg["classificacao"] == "Excelente").sum())
        c4.metric("Críticos", (prof_agg["classificacao"] == "Crítico").sum(),
                  delta=f"-{(prof_agg['classificacao'] == 'Crítico').sum()}" if (prof_agg["classificacao"] == "Crítico").sum() > 0 else None,
                  delta_color="inverse")

        st.markdown("")

        col_rank, col_quad = st.columns([3, 2])

        # --- RANKING ---
        with col_rank:
            st.subheader("Ranking de Professores")
            top_n = st.slider("Exibir top/bottom", 5, min(50, len(prof_agg)), 20, key="rank_n")
            prof_show = prof_agg.head(top_n)

            fig_rank = px.bar(
                prof_show.sort_values("score_composto"),
                y="professor_nome",
                x="score_composto",
                color="classificacao",
                color_discrete_map=CORES_STATUS,
                orientation="h",
                labels={"score_composto": "Score", "professor_nome": ""},
                hover_data=["unidade", "pct_conformidade", "pct_qualidade_conteudo"],
            )
            fig_rank.update_layout(
                height=max(400, top_n * 28),
                margin=dict(t=10, b=30, l=10, r=10),
                yaxis=dict(tickfont=dict(size=10)),
                legend=dict(orientation="h", y=1.02),
                xaxis=dict(range=[0, 100]),
            )
            fig_rank.add_vline(x=70, line_dash="dash", line_color="gray", annotation_text="Meta 70")
            st.plotly_chart(fig_rank, use_container_width=True)

        # --- QUADRANTE ---
        with col_quad:
            st.subheader("Quadrante Estratégico")
            prof_quad = prof_agg[prof_agg["pct_alinhamento"].notna()].copy()
            if not prof_quad.empty:
                fig_quad = px.scatter(
                    prof_quad,
                    x="pct_conformidade",
                    y="pct_alinhamento",
                    color="quadrante",
                    size="aulas_registradas",
                    hover_name="professor_nome",
                    hover_data=["unidade", "score_composto"],
                    labels={"pct_conformidade": "Conformidade %", "pct_alinhamento": "Alinhamento SAE %"},
                    color_discrete_map={
                        "Q1 - Excelente": "#43A047",
                        "Q2 - Registra pouco": "#FFA726",
                        "Q3 - Fora do ritmo": "#29B6F6",
                        "Q4 - Crítico": "#E53935",
                    },
                )
                fig_quad.add_hline(y=70, line_dash="dash", line_color="gray")
                fig_quad.add_vline(x=70, line_dash="dash", line_color="gray")
                fig_quad.update_layout(
                    height=400, margin=dict(t=10, b=30),
                    legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
                )
                st.plotly_chart(fig_quad, use_container_width=True)
            else:
                st.info("Dados de alinhamento SAE ainda insuficientes para o quadrante.")

            # Legenda do quadrante
            st.markdown("""
| Quadrante | Significado | Ação |
|-----------|------------|------|
| **Q1** | Registra e está no ritmo | Reconhecer |
| **Q2** | No ritmo mas registra pouco | Cobrar diário |
| **Q3** | Registra mas fora do ritmo | Alinhar currículo |
| **Q4** | Nem registra nem está no ritmo | Intervenção |
""")

        # --- TABELA DETALHADA ---
        st.subheader("Detalhamento por Professor")
        df_show = prof_agg[["professor_nome", "unidade", "pct_conformidade", "pct_qualidade_conteudo",
                            "pct_uso_tarefas", "pct_alinhamento", "score_composto", "classificacao",
                            "aulas_registradas"]].copy()
        df_show.columns = ["Professor", "Unidade", "Conformidade %", "Qualidade %", "Tarefas %",
                           "Alinhamento %", "Score", "Status", "Aulas"]
        df_show = df_show.round(1)

        def cor_score(val):
            if isinstance(val, (int, float)):
                if val >= 85: return "background-color: #C8E6C9"
                elif val >= 70: return "background-color: #FFF9C4"
                elif val >= 50: return "background-color: #FFE0B2"
                else: return "background-color: #FFCDD2"
            return ""

        styled = df_show.style.applymap(cor_score, subset=["Conformidade %", "Qualidade %", "Tarefas %", "Alinhamento %", "Score"])
        st.dataframe(styled, use_container_width=True, height=400)


# ========================================================================
# ABA 3: PERFIL DO ALUNO
# ========================================================================
with tab3:
    abc = aplicar_filtros(dados["abc"])

    if abc.empty:
        st.warning("Sem dados de score ABC. Rode `python3 gerar_csvs_powerbi_ceo.py` primeiro.")
    else:
        # --- DISTRIBUIÇÃO POR TIER ---
        c1, c2, c3, c4, c5 = st.columns(5)
        total = len(abc)
        tiers = abc["tier_label"].value_counts()

        c1.markdown(f'''<div class="kpi-card" style="background: #1a237e;">
            <h2>{total}</h2><p>Total Alunos</p>
        </div>''', unsafe_allow_html=True)

        for i, (tier, cor) in enumerate([("Verde", "#43A047"), ("Monitorar", "#FFC107"),
                                          ("Atenção", "#FF9800"), ("Crítico", "#E53935")]):
            n = tiers.get(tier, 0)
            pct = n / max(1, total) * 100
            [c2, c3, c4, c5][i].markdown(f'''<div class="kpi-card" style="background: {cor};">
                <h2>{n}</h2><p>{tier}<br>{pct:.1f}%</p>
            </div>''', unsafe_allow_html=True)

        st.markdown("")

        col_chart, col_list = st.columns([3, 2])

        # --- COMPARATIVO POR TURMA ---
        with col_chart:
            st.subheader("Saúde por Série")
            if "serie" in abc.columns:
                serie_stats = abc.groupby("serie").agg(
                    media=("media_geral", "mean"),
                    frequencia=("pct_frequencia", "mean"),
                    ocorrencias=("total_ocorrencias", "mean"),
                    risco=("tier", lambda x: (x >= 2).sum()),
                    total=("aluno_id", "count"),
                ).reset_index()

                # Ordenar por ORDEM_SERIES
                serie_stats["ordem"] = serie_stats["serie"].map({s: i for i, s in enumerate(ORDEM_SERIES)})
                serie_stats = serie_stats.sort_values("ordem")

                fig_serie = go.Figure()
                fig_serie.add_trace(go.Bar(
                    name="Média Notas", x=serie_stats["serie"], y=serie_stats["media"],
                    marker_color=[CORES_SERIES.get(s, "#999") for s in serie_stats["serie"]],
                    text=serie_stats["media"].round(1), textposition="auto",
                ))
                fig_serie.add_hline(y=6.0, line_dash="dash", line_color="red", annotation_text="Meta 6.0")
                fig_serie.update_layout(
                    height=350, margin=dict(t=10, b=30),
                    yaxis_title="Média Notas (2025)", showlegend=False,
                )
                st.plotly_chart(fig_serie, use_container_width=True)

                # Frequência por série
                st.subheader("Frequência Média por Série")
                fig_freq = go.Figure()
                fig_freq.add_trace(go.Bar(
                    x=serie_stats["serie"], y=serie_stats["frequencia"],
                    marker_color=[CORES_SERIES.get(s, "#999") for s in serie_stats["serie"]],
                    text=serie_stats["frequencia"].round(1), textposition="auto",
                ))
                fig_freq.add_hline(y=75, line_dash="dash", line_color="red", annotation_text="LDB 75%")
                fig_freq.update_layout(
                    height=300, margin=dict(t=10, b=30),
                    yaxis_title="Frequência %", showlegend=False,
                    yaxis=dict(range=[0, 105]),
                )
                st.plotly_chart(fig_freq, use_container_width=True)

        # --- LISTA DE RISCO ---
        with col_list:
            st.subheader("Alunos em Risco")
            risco = abc[abc["tier"] >= 1].sort_values("tier", ascending=False)
            if risco.empty:
                st.markdown('''<div class="alerta-box alerta-ok">
                    <strong>✅ Nenhum aluno em risco identificado!</strong><br>
                    Baseado nos dados de 2025. Os dados de 2026 ainda não estão disponíveis.
                </div>''', unsafe_allow_html=True)
            else:
                for _, row in risco.head(30).iterrows():
                    tier = row["tier_label"]
                    css = "alerta-urgente" if tier == "Crítico" else ("alerta-atencao" if tier == "Atenção" else "alerta-info")
                    icone = "🔴" if tier == "Crítico" else ("🟠" if tier == "Atenção" else "🟡")
                    flags = []
                    if row.get("flag_A") in ("Risco", "Crítico"): flags.append(f"Freq: {row.get('pct_frequencia', '?'):.0f}%")
                    if row.get("flag_B") in ("Risco", "Crítico"): flags.append(f"Ocorr: {row.get('total_ocorrencias', 0)}")
                    if row.get("flag_C") in ("Risco", "Crítico"): flags.append(f"Média: {row.get('media_geral', '?'):.1f}")
                    flags_str = " | ".join(flags) if flags else "Monitorar"

                    st.markdown(f'''<div class="alerta-box {css}">
                        {icone} <strong>{row["aluno_nome"]}</strong> — {row.get("serie", "")} ({row.get("unidade", "")})<br>
                        <small>{tier}: {flags_str}</small><br>
                        <small>Ação: {row.get("intervencao_sugerida", "—")}</small>
                    </div>''', unsafe_allow_html=True)

            st.markdown("")
            st.subheader("Distribuição por Unidade e Tier")
            if "unidade" in abc.columns:
                pivot = abc.groupby(["unidade", "tier_label"]).size().reset_index(name="qtd")
                fig_tier = px.bar(pivot, x="unidade", y="qtd", color="tier_label",
                                  color_discrete_map=CORES_TIER,
                                  labels={"unidade": "Unidade", "qtd": "Alunos", "tier_label": "Tier"},
                                  barmode="stack")
                fig_tier.update_layout(height=280, margin=dict(t=10, b=30), legend=dict(orientation="h", y=1.1))
                st.plotly_chart(fig_tier, use_container_width=True)


# ========================================================================
# ABA 4: ENGAJAMENTO SAE
# ========================================================================
with tab4:
    cruz = aplicar_filtros(dados["cruz"])
    engaj = dados["engaj"]

    if cruz.empty:
        st.warning("Sem dados de cruzamento SIGA x SAE. Rode `python3 extrair_sae_digital.py` primeiro.")
    else:
        # KPIs
        c1, c2, c3 = st.columns(3)
        eng_medio = cruz["pct_engajamento"].mean() if "pct_engajamento" in cruz.columns else 0
        alinhados = (cruz["status"] == "Alinhado").sum() / max(1, len(cruz)) * 100 if "status" in cruz.columns else 0
        gap_medio = cruz["gap_prof_alunos"].mean() if "gap_prof_alunos" in cruz.columns and cruz["gap_prof_alunos"].notna().any() else 0

        c1.metric("Engajamento Médio SAE", f"{eng_medio:.0f}%")
        c2.metric("% Alinhados (Prof↔Alunos)", f"{alinhados:.0f}%")
        c3.metric("Gap Médio", f"{gap_medio:+.1f} cap")

        st.markdown("")

        col_sem, col_fun = st.columns(2)

        # --- SEMÁFORO POR DISCIPLINA ---
        with col_sem:
            st.subheader("Status por Disciplina")
            if "status" in cruz.columns:
                STATUS_CORES = {
                    "Alinhado": "#43A047",
                    "Professor Adiantado": "#29B6F6",
                    "Professor Atrasado": "#EF5350",
                    "Baixo Engajamento": "#FF7043",
                    "Alinhado, Baixo Engajamento": "#FFA726",
                    "Alunos Ativos, Professor N/D": "#AB47BC",
                    "Sem SAE": "#9E9E9E",
                    "Sem Dados": "#BDBDBD",
                }
                status_disc = cruz.groupby(["disciplina", "status"]).size().reset_index(name="qtd")
                fig_status = px.bar(status_disc, x="disciplina", y="qtd", color="status",
                                    color_discrete_map=STATUS_CORES,
                                    labels={"disciplina": "", "qtd": "Turmas", "status": "Status"},
                                    barmode="stack")
                fig_status.update_layout(height=400, margin=dict(t=10, b=80),
                                         xaxis_tickangle=-45, legend=dict(orientation="h", y=-0.3, font=dict(size=9)))
                st.plotly_chart(fig_status, use_container_width=True)

        # --- FUNIL DE ENGAJAMENTO ---
        with col_fun:
            st.subheader("Engajamento por Capítulo")
            if not engaj.empty and "capitulo" in engaj.columns:
                eng_cap = engaj.groupby("capitulo")["pct_exercicios"].mean().reset_index()
                eng_cap = eng_cap.sort_values("capitulo")
                fig_funil = px.bar(eng_cap, x="capitulo", y="pct_exercicios",
                                   labels={"capitulo": "Capítulo", "pct_exercicios": "% Exercícios"},
                                   color="pct_exercicios",
                                   color_continuous_scale=["#E53935", "#FFA726", "#43A047"])
                fig_funil.update_layout(height=400, margin=dict(t=10, b=30), coloraxis_showscale=False)
                fig_funil.add_vline(x=CAP + 0.5, line_dash="dash", line_color="blue",
                                    annotation_text=f"Esperado: Cap {CAP}")
                st.plotly_chart(fig_funil, use_container_width=True)
            else:
                st.info("Dados de engajamento por capítulo não disponíveis.")

        # --- TABELA DETALHADA ---
        st.subheader("Detalhamento do Cruzamento")
        cols_show = [c for c in ["unidade", "serie", "disciplina", "professor", "cap_professor",
                                  "cap_esperado", "pct_engajamento", "gap_prof_alunos", "status",
                                  "alunos_ativos"] if c in cruz.columns]
        df_cruz = cruz[cols_show].copy()

        rename = {
            "unidade": "Unidade", "serie": "Série", "disciplina": "Disciplina",
            "professor": "Professor", "cap_professor": "Cap Prof", "cap_esperado": "Cap Esperado",
            "pct_engajamento": "Engaj %", "gap_prof_alunos": "Gap", "status": "Status",
            "alunos_ativos": "Alunos Ativos",
        }
        df_cruz = df_cruz.rename(columns={k: v for k, v in rename.items() if k in df_cruz.columns})
        st.dataframe(df_cruz, use_container_width=True, height=400)


# ========================================================================
# ABA 5: PAINEL DE AÇÃO
# ========================================================================
with tab5:
    prof = aplicar_filtros(dados["prof"])
    abc = aplicar_filtros(dados["abc"])

    # --- CARDS DE INTERVENÇÃO ---
    st.subheader("Intervenções Necessárias")
    c1, c2, c3, c4 = st.columns(4)

    if not abc.empty and "intervencao_sugerida" in abc.columns:
        n_reforco = abc["intervencao_sugerida"].str.contains("Reforço", na=False).sum()
        n_familia = abc["intervencao_sugerida"].str.contains("Família", na=False).sum()
        n_orientacao = abc["intervencao_sugerida"].str.contains("Orientação", na=False).sum()
    else:
        n_reforco = n_familia = n_orientacao = 0

    if not prof.empty:
        prof_agg = prof.groupby("professor_normalizado")["score_composto"].mean()
        n_reuniao_prof = (prof_agg < 50).sum()
    else:
        n_reuniao_prof = 0

    c1.markdown(f'''<div class="kpi-card" style="background: #7B1FA2;">
        <h2>{n_reforco}</h2><p>Alunos para<br>Reforço Escolar</p>
    </div>''', unsafe_allow_html=True)
    c2.markdown(f'''<div class="kpi-card" style="background: #E65100;">
        <h2>{n_familia}</h2><p>Contatos com<br>Família Necessários</p>
    </div>''', unsafe_allow_html=True)
    c3.markdown(f'''<div class="kpi-card" style="background: #1565C0;">
        <h2>{n_orientacao}</h2><p>Alunos para<br>Orientação</p>
    </div>''', unsafe_allow_html=True)
    c4.markdown(f'''<div class="kpi-card" style="background: #C62828;">
        <h2>{n_reuniao_prof}</h2><p>Professores para<br>Reunião Urgente</p>
    </div>''', unsafe_allow_html=True)

    st.markdown("")

    col_acoes, col_metas = st.columns([3, 2])

    # --- LISTA DE AÇÕES PRIORITÁRIAS ---
    with col_acoes:
        st.subheader("Ações Prioritárias")

        # Professores críticos
        if not prof.empty:
            st.markdown("**Professores para intervenção imediata:**")
            prof_criticos = prof.groupby("professor_normalizado").agg(
                nome=("professor_nome", "first"),
                unidade=("unidade", "first"),
                score=("score_composto", "mean"),
                conformidade=("pct_conformidade", "mean"),
            ).reset_index()
            prof_criticos = prof_criticos[prof_criticos["score"] < 50].sort_values("score")

            if prof_criticos.empty:
                st.markdown('''<div class="alerta-box alerta-ok">
                    ✅ Nenhum professor com score abaixo de 50
                </div>''', unsafe_allow_html=True)
            else:
                for _, row in prof_criticos.head(10).iterrows():
                    st.markdown(f'''<div class="alerta-box alerta-urgente">
                        <strong>🔴 {row["nome"]}</strong> ({row["unidade"]})<br>
                        Score: {row["score"]:.0f}/100 | Conformidade: {row["conformidade"]:.0f}%<br>
                        <small>Ação: Agendar reunião individual esta semana</small>
                    </div>''', unsafe_allow_html=True)

        # Alunos críticos
        if not abc.empty:
            st.markdown("")
            st.markdown("**Alunos para contato com família:**")
            alunos_crit = abc[abc["tier"] >= 2].sort_values("tier", ascending=False)
            if alunos_crit.empty:
                st.markdown('''<div class="alerta-box alerta-ok">
                    ✅ Nenhum aluno em tier de atenção/crítico (dados 2025)
                </div>''', unsafe_allow_html=True)
            else:
                for _, row in alunos_crit.head(10).iterrows():
                    css = "alerta-urgente" if row["tier"] == 3 else "alerta-atencao"
                    st.markdown(f'''<div class="alerta-box {css}">
                        <strong>{"🔴" if row["tier"]==3 else "🟠"} {row["aluno_nome"]}</strong> — {row.get("serie","")} ({row.get("unidade","")})<br>
                        <small>{row.get("intervencao_sugerida", "—")}</small>
                    </div>''', unsafe_allow_html=True)

    # --- METAS TRIMESTRAIS ---
    with col_metas:
        st.subheader("Progresso das Metas")

        metas = [
            ("Conformidade", conf if 'conf' in dir() else (prof["pct_conformidade"].mean() if not prof.empty else 0), 80, "%"),
            ("Frequência OK", (abc["pct_frequencia"].dropna() >= 75).mean() * 100 if not abc.empty and abc["pct_frequencia"].notna().any() else 0, 90, "%"),
            ("Média Notas", abc["media_geral"].mean() if not abc.empty and abc["media_geral"].notna().any() else 0, 6.0, ""),
            ("Alunos Seguros", 100 - ((abc["tier"] >= 2).sum() / max(1, len(abc)) * 100) if not abc.empty else 100, 90, "%"),
        ]

        for nome_meta, atual, meta, sufixo in metas:
            progresso = min(100, atual / meta * 100) if meta > 0 else 0
            cor_barra = "#43A047" if progresso >= 100 else ("#FFA726" if progresso >= 70 else "#E53935")

            st.markdown(f"**{nome_meta}**: {atual:.1f}{sufixo} / {meta}{sufixo}")
            st.progress(min(1.0, progresso / 100))
            st.markdown("")

        st.markdown("---")

        # Resumo de reconhecimento
        st.subheader("Reconhecimento")
        if not prof.empty:
            prof_exc = prof.groupby("professor_normalizado").agg(
                nome=("professor_nome", "first"),
                unidade=("unidade", "first"),
                score=("score_composto", "mean"),
            ).reset_index()
            prof_exc = prof_exc[prof_exc["score"] >= 85].sort_values("score", ascending=False)

            if prof_exc.empty:
                st.info("Nenhum professor com score acima de 85 ainda.")
            else:
                for _, row in prof_exc.head(5).iterrows():
                    st.markdown(f'''<div class="alerta-box alerta-ok">
                        ⭐ <strong>{row["nome"]}</strong> ({row["unidade"]})<br>
                        Score: {row["score"]:.0f}/100
                    </div>''', unsafe_allow_html=True)

    # --- DISTRIBUIÇÃO POR TIPO DE INTERVENÇÃO ---
    st.markdown("")
    st.subheader("Distribuição por Tipo de Intervenção")
    if not abc.empty and "intervencao_sugerida" in abc.columns:
        intervencoes = abc[abc["intervencao_sugerida"] != "Nenhuma"]["intervencao_sugerida"]
        if not intervencoes.empty:
            # Separar intervenções compostas
            tipos = []
            for i in intervencoes:
                for t in str(i).split(" | "):
                    if t.strip():
                        tipos.append(t.strip().split(" → ")[0])
            if tipos:
                tipo_df = pd.DataFrame({"tipo": tipos})
                fig_donut = px.pie(tipo_df, names="tipo", hole=0.5,
                                   color_discrete_sequence=["#7B1FA2", "#E65100", "#1565C0", "#C62828"])
                fig_donut.update_layout(height=300, margin=dict(t=10, b=10))
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("Nenhuma intervenção necessária identificada.")
        else:
            st.success("Todos os alunos estão bem! Nenhuma intervenção necessária.")
    else:
        st.info("Dados de intervenção não disponíveis.")


# ========== RODAPÉ ==========
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #999; font-size: 0.85em;'>"
    f"Dashboard CEO - Colégio ELO 2026 | Dados: {HOJE.strftime('%d/%m/%Y')} | "
    f"Semana {SEM} | {TRI}"
    f"</div>",
    unsafe_allow_html=True,
)
