#!/usr/bin/env python3
"""
HOME — Dashboard principal do Sistema Pedagogico ELO 2026.
Extraido de Sistema_Pedagogico.py para uso com st.navigation.
"""

import streamlit as st
import pandas as pd
import subprocess
import os
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from auth import get_user_unit, get_user_role, ROLE_CEO, ROLE_DIRETOR, ROLE_COORDENADOR
from utils import (
    DATA_DIR, is_cloud, ultima_atualizacao,
    carregar_fato_aulas, carregar_horario_esperado, carregar_calendario, carregar_progressao_sae,
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre, filtrar_ate_hoje, _hoje, UNIDADES_NOMES
)


# ========== HEALTH CHECK: SCHEDULER EXTERNO ==========
def _ler_health_scheduler():
    health_file = Path(__file__).parent.parent / "scheduler_health.json"
    if not health_file.exists():
        return {}
    try:
        import json
        with open(health_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ========== SESSION STATE ==========
if 'semana_atual' not in st.session_state:
    st.session_state.semana_atual = calcular_semana_letiva()
if 'capitulo_esperado' not in st.session_state:
    st.session_state.capitulo_esperado = calcular_capitulo_esperado(st.session_state.semana_atual)
if 'trimestre_atual' not in st.session_state:
    st.session_state.trimestre_atual = calcular_trimestre(st.session_state.semana_atual)


# ========== SIDEBAR: ATUALIZACAO DE DADOS ==========
_aulas_path = DATA_DIR / "fato_Aulas.csv"

with st.sidebar:
    st.subheader("Atualizar Dados")
    st.caption(f"Ultima atualizacao: {ultima_atualizacao()}")

    _tem_senha = bool(os.environ.get("SIGA_SENHA"))
    if not _tem_senha:
        try:
            _tem_senha = bool(st.secrets.get("siga", {}).get("senha"))
        except (FileNotFoundError, AttributeError):
            pass

    if _tem_senha:
        if st.button("Atualizar Diario de Classe", type="primary", key="btn_atualizar_home"):
            _script_path = Path(__file__).parent.parent / "atualizar_siga.py"
            _env = os.environ.copy()
            if not is_cloud():
                try:
                    _env["SIGA_SENHA"] = st.secrets["siga"]["senha"]
                except (KeyError, FileNotFoundError):
                    pass
            with st.spinner("Atualizando dados do SIGA..."):
                _result = subprocess.run(
                    ["python3", str(_script_path)],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(Path(__file__).parent.parent),
                    env=_env,
                )
            if _result.returncode == 0:
                st.success("Dados atualizados com sucesso!")
                st.rerun()
            else:
                st.error("Erro na atualizacao:")
                st.code(_result.stderr or _result.stdout, language="text")
    else:
        st.info("Configure SIGA_SENHA para habilitar atualizacoes.")

    _health = _ler_health_scheduler()
    if _health.get("last_run"):
        try:
            _last_dt = datetime.fromisoformat(_health["last_run"])
            _last_str = _last_dt.strftime("%d/%m %H:%M")
            if _health.get("ok"):
                st.caption(f"Ultima extracao: {_last_str} ({_health.get('total', 0)} aulas)")
            else:
                st.caption(f"Ultima extracao: {_last_str} (ERRO: {_health.get('erro', '?')})")
        except (ValueError, TypeError):
            st.caption(f"Ultima extracao: {_health['last_run']}")
    st.caption("Scheduler: Externo (8h, 12h, 18h, 20h)")
    st.markdown("---")


# ========== CSS ==========
st.markdown("""
<style>
    .main > div { padding-top: 1rem; }
    h1 { color: #1a237e; text-align: center; }
    h2 { color: #303f9f; border-bottom: 2px solid #303f9f; padding-bottom: 8px; }
    h3 { color: #3f51b5; }
    .info-box {
        background: #e3f2fd; border-left: 4px solid #2196f3;
        padding: 15px; margin: 10px 0; border-radius: 4px;
    }
    .highlight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 25px; border-radius: 12px;
        text-align: center; margin: 10px 0;
    }
    .saude-card {
        padding: 20px; border-radius: 12px; text-align: center; margin: 5px 0;
        color: white; min-height: 120px;
    }
    .saude-verde { background: linear-gradient(135deg, #43A047, #66BB6A); }
    .saude-amarelo { background: linear-gradient(135deg, #F9A825, #FDD835); color: #333; }
    .saude-vermelho { background: linear-gradient(135deg, #E53935, #EF5350); }
</style>
""", unsafe_allow_html=True)


# ========== CONTEUDO PRINCIPAL ==========
st.title("Sistema Pedagogico Integrado")
st.markdown("### Colegio ELO - Planejamento 2026 | SIGA + SAE")
st.markdown("---")

st.markdown("""
<div class="highlight-card">
    <h2 style="color: white; border: none;">Bem-vindo ao Sistema de Gestao Pedagogica</h2>
    <p>Este sistema integra os dados do <strong>SIGA</strong> (Sistema de Gestao Academica)
    com a estrutura curricular do <strong>SAE Digital</strong> para acompanhamento em tempo real.</p>
</div>
""", unsafe_allow_html=True)

# ========== MISSAO DA SEMANA (DIRETORES E CEO) ==========

_role = get_user_role()
_user_unit = get_user_unit()

if _role in (ROLE_CEO, ROLE_DIRETOR, ROLE_COORDENADOR):
    _semana_home = calcular_semana_letiva()
    _resumo_path = DATA_DIR / "resumo_Executivo.csv"

    if _resumo_path.exists():
        try:
            _resumo_df = pd.read_csv(_resumo_path)

            # Filtrar por unidade do diretor, ou rede inteira para CEO
            if _role == ROLE_DIRETOR and _user_unit:
                _un_data = _resumo_df[_resumo_df['unidade'] == _user_unit]
                _un_nome = UNIDADES_NOMES.get(_user_unit, _user_unit)
            else:
                _un_data = _resumo_df[_resumo_df['unidade'] == 'TOTAL']
                _un_nome = 'Rede ELO'

            if not _un_data.empty:
                _r = _un_data.iloc[0]
                _conf = _r['pct_conformidade_media']
                _freq = _r['frequencia_media']
                _crit = int(_r['professores_criticos'])
                _graves = int(_r['ocorr_graves'])
                _risco = _r['pct_alunos_risco']

                # Gerar prioridades da semana
                _prioridades = []
                if _conf < 55:
                    _prioridades.append(
                        f'Conformidade em {_conf:.0f}% — contatar os {_crit} '
                        f'professores criticos esta semana'
                    )
                if _freq < 85:
                    _prioridades.append(
                        f'Frequencia em {_freq:.1f}% — ativar busca ativa '
                        f'para alunos com 3+ faltas'
                    )
                if _graves > 5:
                    _prioridades.append(
                        f'{_graves} ocorrencias graves — identificar turmas-foco '
                        f'e marcar presenca'
                    )
                if _risco > 20:
                    _prioridades.append(
                        f'{_risco:.0f}% alunos em risco — plano individual '
                        f'para os mais criticos'
                    )
                if not _prioridades:
                    _prioridades.append('Manter ritmo. Acompanhar indicadores.')

                # Reuniao da semana
                from peex_utils import info_semana as _info_semana
                _info = _info_semana(_semana_home)
                _prox = _info.get('proxima_reuniao', {})
                _reuniao_txt = ''
                if _prox:
                    _reuniao_txt = (
                        f"<div style='margin-top:10px; padding-top:8px; "
                        f"border-top:1px solid rgba(255,255,255,0.3);'>"
                        f"<strong>Proxima reuniao:</strong> "
                        f"{_prox.get('cod', '')} — {_prox.get('titulo', '')}<br>"
                        f"<small>Foco: {_prox.get('foco', '')}</small></div>"
                    )

                _cor_fundo = '#c62828' if _conf < 50 else '#e65100' if _conf < 70 else '#2e7d32'

                _prios_html = ''.join(
                    f'<div style="margin:4px 0;">• {p}</div>' for p in _prioridades
                )

                st.markdown(f"""
                <div style="background:linear-gradient(135deg, {_cor_fundo}, {_cor_fundo}dd);
                            color:white; padding:20px 24px; border-radius:12px; margin:16px 0;">
                    <h3 style="color:white; border:none; margin:0 0 10px 0;">
                        Missao da Semana {_semana_home} — {_un_nome}
                    </h3>
                    {_prios_html}
                    {_reuniao_txt}
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            pass

st.markdown("---")

# Saude da Rede
st.header("Saude da Rede")

df_aulas = carregar_fato_aulas()
df_aulas = filtrar_ate_hoje(df_aulas)
df_horario = carregar_horario_esperado()
df_cal = carregar_calendario()
df_prog = carregar_progressao_sae()

if not df_aulas.empty and not df_horario.empty:
    semana = calcular_semana_letiva()
    capitulo = calcular_capitulo_esperado(semana)
    trimestre = calcular_trimestre(semana)

    st.markdown(f"**Semana {semana}** | Capitulo esperado: {capitulo}/12 | {trimestre}o Trimestre")

    # Health cards per unit
    unidades = sorted(df_horario['unidade'].unique())
    cols_un = st.columns(len(unidades))

    for i, un in enumerate(unidades):
        df_un = df_aulas[df_aulas['unidade'] == un]
        df_hor_un = df_horario[df_horario['unidade'] == un]
        if df_un['data'].notna().any():
            semana_un = calcular_semana_letiva(df_un['data'].max())
        else:
            semana_un = 1
        esperado = len(df_hor_un) * semana_un
        real = len(df_un)
        conf = (real / esperado * 100) if esperado > 0 else 0
        profs = df_un['professor'].nunique()

        if conf >= 85:
            css = 'saude-verde'
        elif conf >= 70:
            css = 'saude-amarelo'
        else:
            css = 'saude-vermelho'

        nome_un = UNIDADES_NOMES.get(un, un)

        with cols_un[i]:
            st.markdown(f"""
            <div class="saude-card {css}">
                <h2 style="margin:0; border:none; color:inherit;">{conf:.0f}%</h2>
                <p style="margin:0; font-size:1.1em; font-weight:bold;">{nome_un}</p>
                <small>{real} aulas | {profs} profs</small>
            </div>
            """, unsafe_allow_html=True)

    # Data status row
    st.markdown("")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Aulas Registradas", f"{len(df_aulas):,}")
    with col_s2:
        st.metric("Grade Horaria", f"{len(df_horario):,}/sem")
    with col_s3:
        if not df_cal.empty:
            letivos = len(df_cal[df_cal['eh_letivo'] == 1])
            st.metric("Dias Letivos", f"{letivos}")
        else:
            st.metric("Calendario", "N/A")
    with col_s4:
        if not df_prog.empty:
            st.metric("Progressao SAE", f"{len(df_prog):,}")
        else:
            st.metric("Progressao SAE", "N/A")

    # ========== PONTOS DE ATENCAO HOJE ==========
    st.markdown("---")
    st.header("Pontos de Atencao Hoje")

    user_unit = get_user_unit()
    hoje = _hoje()

    pontos = []

    # 1. Disciplinas sem nenhum registro
    slots_esp = set(df_horario.groupby(['unidade', 'serie', 'disciplina']).size().index)
    slots_real = set(df_aulas.groupby(['unidade', 'serie', 'disciplina']).size().index)
    slots_sem = slots_esp - slots_real
    if user_unit:
        slots_sem_un = [s for s in slots_sem if s[0] == user_unit]
    else:
        slots_sem_un = list(slots_sem)
    if len(slots_sem_un) > 0:
        exemplos = [f"{d} ({s})" for u, s, d in sorted(slots_sem_un)[:4]]
        pontos.append(('🔴', f'{len(slots_sem_un)} disciplinas sem NENHUM registro', ', '.join(exemplos)))

    # 2. Professores com baixa conformidade
    df_un_user = df_aulas if not user_unit else df_aulas[df_aulas['unidade'] == user_unit]
    df_hor_user = df_horario if not user_unit else df_horario[df_horario['unidade'] == user_unit]
    profs_baixos = []
    for prof, df_p in df_un_user.groupby('professor'):
        un_p = df_p['unidade'].iloc[0]
        esp = 0
        for s in df_p['serie'].unique():
            for d in df_p['disciplina'].unique():
                esp += len(df_hor_user[
                    (df_hor_user['unidade'] == un_p) &
                    (df_hor_user['serie'] == s) &
                    (df_hor_user['disciplina'] == d)
                ]) * semana
        if esp > 0:
            conf_p = len(df_p) / esp * 100
            if conf_p < 60:
                profs_baixos.append((prof, conf_p))
    if profs_baixos:
        profs_baixos.sort(key=lambda x: x[1])
        nomes = [f"{p} ({c:.0f}%)" for p, c in profs_baixos[:3]]
        pontos.append(('🟡', f'{len(profs_baixos)} professores abaixo de 60%', ', '.join(nomes)))

    # 3. Aulas recentes sem conteudo
    df_recente = df_un_user[df_un_user['data'] >= (hoje - pd.Timedelta(days=7))]
    if not df_recente.empty:
        sem_cont = df_recente[df_recente['conteudo'].isna() | (df_recente['conteudo'] == '')]
        if len(sem_cont) > 0:
            pct_vazio = len(sem_cont) / len(df_recente) * 100
            if pct_vazio > 20:
                pontos.append(('🟡', f'{len(sem_cont)} aulas sem conteudo nos ultimos 7 dias ({pct_vazio:.0f}%)',
                               'Verificar registros dos professores'))

    # 4. Info positiva
    if not profs_baixos and len(slots_sem_un) == 0:
        pontos.append(('🟢', 'Tudo em ordem!', 'Todos os professores registrando e todas disciplinas cobertas'))

    for emoji, msg, detalhe in pontos:
        if emoji == '🔴':
            bg, border = '#FFEBEE', '#E53935'
        elif emoji == '🟡':
            bg, border = '#FFF8E1', '#FFA726'
        else:
            bg, border = '#E8F5E9', '#43A047'
        st.markdown(f"""
        <div style="background:{bg}; border-left:4px solid {border}; padding:12px 16px; margin:8px 0; border-radius:4px;">
            <strong>{emoji} {msg}</strong><br>
            <small style="color:#666;">{detalhe}</small>
        </div>
        """, unsafe_allow_html=True)

    if user_unit:
        st.caption(f"Mostrando alertas para: {UNIDADES_NOMES.get(user_unit, user_unit)}")

else:
    st.warning("Dados nao carregados. Execute a extracao do SIGA para ver a saude da rede.")

# Rodape
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    Sistema Pedagogico Integrado - Colegio ELO 2026<br>
    SIGA + SAE Digital | Ultima atualizacao: {datetime.now().strftime("%d/%m/%Y %H:%M")}
</div>
""", unsafe_allow_html=True)
