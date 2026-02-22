#!/usr/bin/env python3
"""
PÁGINA 25: DEVOLUTIVAS PERSONALIZADAS
Ficha de Feedback Docente - Modelo Integrado (3 C's + SBI + Feedforward).
Seções: Escuta e Diálogo Construtivo (SBI), Direcionamentos (Continuar-Começar-Cessar),
Olhando Para Frente (Feed Forward), Encaminhamentos e Combinados.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import json
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    DATA_DIR, WRITABLE_DIR, is_cloud, ultima_atualizacao,
    calcular_semana_letiva, calcular_capitulo_esperado, calcular_trimestre,
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje, _hoje,
    UNIDADES, UNIDADES_NOMES, SERIES_FUND_II, SERIES_EM, ORDEM_SERIES,
)
from config_cores import CORES_UNIDADES, CORES_SERIES

from auth import get_user_unit, get_user_role

# ========== ARQUIVO DE PERSISTÊNCIA ==========
DEVOLUTIVAS_FILE = WRITABLE_DIR / 'devolutivas.json'

def carregar_devolutivas():
    """Carrega devolutivas salvas."""
    if DEVOLUTIVAS_FILE.exists():
        try:
            with open(DEVOLUTIVAS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass
    return []

def salvar_devolutivas(devolutivas):
    """Salva devolutivas."""
    WRITABLE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DEVOLUTIVAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(devolutivas, f, ensure_ascii=False, indent=2)

# ========== CSS ==========
st.markdown("""
<style>
    .ccc-comecar {
        background: #E8F5E9; border-left: 5px solid #43A047;
        padding: 14px 18px; margin: 8px 0; border-radius: 6px;
    }
    .ccc-cessar {
        background: #FFEBEE; border-left: 5px solid #D32F2F;
        padding: 14px 18px; margin: 8px 0; border-radius: 6px;
    }
    .ccc-continuar {
        background: #E3F2FD; border-left: 5px solid #1565C0;
        padding: 14px 18px; margin: 8px 0; border-radius: 6px;
    }
    .ccc-feedforward {
        background: #F3E5F5; border-left: 5px solid #7B1FA2;
        padding: 14px 18px; margin: 8px 0; border-radius: 6px;
    }
    .ccc-combinados {
        background: #FFF3E0; border-left: 5px solid #E65100;
        padding: 14px 18px; margin: 8px 0; border-radius: 6px;
    }
    .ccc-escuta {
        background: #ECEFF1; border-left: 5px solid #455A64;
        padding: 14px 18px; margin: 8px 0; border-radius: 6px;
    }
    .ccc-sbi {
        background: #FFF8E1; border-left: 5px solid #F9A825;
        padding: 14px 18px; margin: 8px 0; border-radius: 6px;
    }
    .metric-card {
        background: #F5F5F5; border-radius: 8px;
        padding: 12px 16px; text-align: center;
    }
    .assinatura-box {
        border-top: 1px solid #999; margin-top: 30px; padding-top: 8px;
        text-align: center; font-size: 0.9em; color: #555;
    }
</style>
""", unsafe_allow_html=True)


def _calcular_metricas_professor(df_aulas, df_horario, professor, unidade, semana):
    """Calcula métricas resumo de um professor para contexto da devolutiva."""
    df_prof = df_aulas[(df_aulas['professor'] == professor) & (df_aulas['unidade'] == unidade)]
    df_hor = df_horario[(df_horario['professor'] == professor) & (df_horario['unidade'] == unidade)]

    aulas_registradas = len(df_prof)
    aulas_esperadas = int(df_hor['aulas_semana'].sum() * semana) if not df_hor.empty else 0
    taxa_registro = (aulas_registradas / aulas_esperadas * 100) if aulas_esperadas > 0 else 0

    com_conteudo = df_prof['conteudo'].notna().sum() if 'conteudo' in df_prof.columns else 0
    taxa_conteudo = (com_conteudo / aulas_registradas * 100) if aulas_registradas > 0 else 0

    com_tarefa = df_prof['tarefa'].notna().sum() if 'tarefa' in df_prof.columns else 0
    taxa_tarefa = (com_tarefa / aulas_registradas * 100) if aulas_registradas > 0 else 0

    series_prof = sorted(df_prof['serie'].unique()) if 'serie' in df_prof.columns else []
    disciplinas_prof = sorted(df_prof['disciplina'].unique()) if 'disciplina' in df_prof.columns else []

    ultimo_registro = df_prof['data'].max() if 'data' in df_prof.columns and not df_prof.empty else None
    dias_sem = (_hoje() - ultimo_registro).days if ultimo_registro is not None and pd.notna(ultimo_registro) else None

    return {
        'aulas_registradas': aulas_registradas,
        'aulas_esperadas': aulas_esperadas,
        'taxa_registro': taxa_registro,
        'taxa_conteudo': taxa_conteudo,
        'taxa_tarefa': taxa_tarefa,
        'series': series_prof,
        'disciplinas': disciplinas_prof,
        'dias_sem_registro': dias_sem,
    }


def main():
    st.title("💬 Devolutivas Personalizadas")
    st.markdown("**Ficha de Feedback Docente - Modelo Integrado (3 C's + SBI + Feedforward)**")

    hoje = _hoje()
    semana = calcular_semana_letiva(hoje)
    trimestre = calcular_trimestre(semana)
    cap_esperado = calcular_capitulo_esperado(semana)

    # Carregar dados
    df_aulas = carregar_fato_aulas()
    df_horario = carregar_horario_esperado()
    devolutivas = carregar_devolutivas()

    if df_aulas.empty:
        st.error("Dados de aulas não disponíveis.")
        return
    df_aulas = filtrar_ate_hoje(df_aulas)

    # ========== SIDEBAR: SELEÇÃO ==========
    with st.sidebar:
        st.markdown("---")
        st.subheader("Selecionar Professor")

        _user_unit = get_user_unit()
        _un_default = UNIDADES.index(_user_unit) if _user_unit and _user_unit in UNIDADES else 0

        # Verifica se veio de um alerta (pagina 14)
        _alerta_ctx = st.session_state.get('devolutiva_from_alerta')
        if _alerta_ctx:
            st.success(f"Alerta: {_alerta_ctx.get('nome_alerta', '')} - {_alerta_ctx.get('professor', '')}")
            # Se veio de alerta, pre-seleciona a unidade do alerta
            if _alerta_ctx.get('unidade') in UNIDADES:
                _un_default = UNIDADES.index(_alerta_ctx['unidade'])

        unidade_sel = st.selectbox("Unidade:", UNIDADES, index=_un_default,
            format_func=lambda x: UNIDADES_NOMES.get(x, x),
            key='dev_unidade')

        segmento_sel = st.selectbox("Segmento:", ['Todos', 'Anos Finais', 'Ensino Médio'],
            key='dev_segmento')

        # Filtrar professores por unidade e segmento
        df_f = df_aulas[df_aulas['unidade'] == unidade_sel].copy()
        if segmento_sel == 'Anos Finais' and 'serie' in df_f.columns:
            df_f = df_f[df_f['serie'].isin(SERIES_FUND_II)]
        elif segmento_sel == 'Ensino Médio' and 'serie' in df_f.columns:
            df_f = df_f[df_f['serie'].isin(SERIES_EM)]

        professores_disp = sorted(df_f['professor'].dropna().unique()) if 'professor' in df_f.columns else []

        if not professores_disp:
            st.warning("Nenhum professor encontrado para esta unidade/segmento.")
            return

        _alerta_prof = _alerta_ctx.get('professor') if _alerta_ctx else None
        _prof_default = professores_disp.index(_alerta_prof) if _alerta_prof and _alerta_prof in professores_disp else 0
        prof_sel = st.selectbox("Professor:", professores_disp, index=_prof_default, key='dev_professor')

        # Disciplinas do professor selecionado
        disc_prof = sorted(df_f[df_f['professor'] == prof_sel]['disciplina'].dropna().unique()) if 'disciplina' in df_f.columns else []
        disciplina_sel = st.selectbox("Disciplina:", ['Todas'] + disc_prof, key='dev_disciplina')

        st.markdown("---")
        st.caption(f"Semana {semana} | {trimestre}º Trimestre | Cap. {cap_esperado}")

    # ========== MÉTRICAS DO PROFESSOR (contexto) ==========
    metricas = _calcular_metricas_professor(df_aulas, df_horario, prof_sel, unidade_sel, semana)

    st.markdown(f"### {prof_sel}")
    disc_info = disciplina_sel if disciplina_sel != 'Todas' else ', '.join(str(d) for d in metricas['disciplinas'])
    st.caption(f"{UNIDADES_NOMES.get(unidade_sel, unidade_sel)} | {segmento_sel} | "
               f"Séries: {', '.join(str(s) for s in metricas['series'])} | "
               f"Disciplinas: {disc_info}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cor_reg = '#43A047' if metricas['taxa_registro'] >= 80 else '#F57C00' if metricas['taxa_registro'] >= 60 else '#D32F2F'
        st.metric("Aulas Registradas", f"{metricas['aulas_registradas']}/{metricas['aulas_esperadas']}",
                  delta=f"{metricas['taxa_registro']:.0f}%")
    with col2:
        st.metric("Conteúdo Registrado", f"{metricas['taxa_conteudo']:.0f}%")
    with col3:
        st.metric("Tarefa/Atividade", f"{metricas['taxa_tarefa']:.0f}%")
    with col4:
        if metricas['dias_sem_registro'] is not None:
            st.metric("Dias sem Registro", metricas['dias_sem_registro'])
        else:
            st.metric("Dias sem Registro", "—")

    st.markdown("---")

    # ========== TABS ==========
    tab_nova, tab_historico = st.tabs(["Nova Devolutiva", "Histórico"])

    # ========== TAB: NOVA DEVOLUTIVA ==========
    with tab_nova:
        with st.form("form_devolutiva", clear_on_submit=True):

            # ===== SEÇÃO 1: ESCUTA E DIÁLOGO CONSTRUTIVO =====
            st.subheader("1. Escuta e Diálogo Construtivo")

            st.markdown('<div class="ccc-escuta"><strong>RELATO RECEBIDO</strong><br>'
                        '<small>Situação relatada por terceiros: quem relatou, contexto, recorrência</small></div>',
                        unsafe_allow_html=True)
            _relato_default = ""
            if _alerta_ctx and _alerta_ctx.get('professor') == prof_sel:
                _relato_default = (
                    f"[Alerta {_alerta_ctx.get('nome_alerta', '')}] "
                    f"{_alerta_ctx.get('detalhe', '')} | "
                    f"Disciplinas: {_alerta_ctx.get('disciplinas', '')} | "
                    f"Acao sugerida: {_alerta_ctx.get('acao_sugerida', '')}"
                )
            relato_recebido = st.text_area("Relato da situação:", height=100, key='dev_relato',
                value=_relato_default,
                placeholder="Ex: A família relatou que... / O aluno X mencionou que... / "
                "Observação em sala no dia...")

            st.markdown('<div class="ccc-escuta"><strong>POSICIONAMENTO DO(A) PROFESSOR(A)</strong><br>'
                        '<small>Reflexão, justificativa ou percepção do docente sobre o relato</small></div>',
                        unsafe_allow_html=True)
            posicionamento_prof = st.text_area("Posicionamento do(a) professor(a):", height=100,
                key='dev_posicionamento',
                placeholder="Ex: O professor explicou que... / Reconheceu que... / "
                "Justificou a abordagem por...")

            st.markdown('<div class="ccc-sbi"><strong>ANÁLISE DO COORDENADOR(A) - MODELO SBI</strong><br>'
                        '<small>Situação, Comportamento e Impacto</small></div>',
                        unsafe_allow_html=True)
            col_sbi1, col_sbi2, col_sbi3 = st.columns(3)
            with col_sbi1:
                sbi_situacao = st.text_area("Situação (quando/onde):", height=80, key='dev_sbi_sit',
                    placeholder="Ex: Na aula de 05/02, turma 7ºA...")
            with col_sbi2:
                sbi_comportamento = st.text_area("Comportamento (o que foi observado):", height=80,
                    key='dev_sbi_comp',
                    placeholder="Ex: O professor utilizou apenas exposição oral sem recursos visuais...")
            with col_sbi3:
                sbi_impacto = st.text_area("Impacto (consequência observada):", height=80,
                    key='dev_sbi_imp',
                    placeholder="Ex: Os alunos demonstraram desatenção, 40% não entregaram a atividade...")

            # ===== SEÇÃO 2: DIRECIONAMENTOS - MODELO 3C =====
            st.markdown("---")
            st.subheader("2. Direcionamentos - Modelo 3C")

            col_e, col_d = st.columns(2)

            with col_e:
                st.markdown('<div class="ccc-continuar"><strong>CONTINUAR</strong><br>'
                            '<small>Pontos fortes que demonstram resultados positivos</small></div>',
                            unsafe_allow_html=True)
                continuar = st.text_area("O que continuar:", height=100, key='dev_continuar',
                    placeholder="Ex: Boa organização do diário, registro detalhado de conteúdo...")

                st.markdown('<div class="ccc-cessar"><strong>CESSAR</strong><br>'
                            '<small>Práticas que não contribuem e devem ser repensadas</small></div>',
                            unsafe_allow_html=True)
                cessar = st.text_area("O que cessar:", height=100, key='dev_cessar',
                    placeholder="Ex: Aulas exclusivamente expositivas sem interação...")

            with col_d:
                st.markdown('<div class="ccc-comecar"><strong>COMEÇAR</strong><br>'
                            '<small>Práticas a incorporar para potencializar resultados</small></div>',
                            unsafe_allow_html=True)
                comecar = st.text_area("O que começar a fazer:", height=100, key='dev_comecar',
                    placeholder="Ex: Utilizar roteiros de estudo, diversificar instrumentos avaliativos...")

            # ===== SEÇÃO 3: OLHANDO PARA FRENTE (FEED FORWARD) =====
            st.markdown("---")
            st.subheader("3. Olhando Para Frente (Feed Forward)")

            st.markdown('<div class="ccc-feedforward"><strong>SUGESTÕES PARA O FUTURO E APOIO DA COORDENAÇÃO</strong></div>',
                        unsafe_allow_html=True)
            feedforward = st.text_area("Sugestões e apoio:", height=100, key='dev_feedforward',
                placeholder="Ex: Participar da formação sobre metodologias ativas, a coordenação pode auxiliar com...")

            # ===== SEÇÃO 4: ENCAMINHAMENTOS E COMBINADOS =====
            st.markdown("---")
            st.subheader("4. Encaminhamentos e Combinados")
            st.markdown('<div class="ccc-combinados"><strong>PRÓXIMAS AÇÕES E COMPROMISSOS</strong><br>'
                        '<small>Ações concretas, prazos e responsabilidades</small></div>',
                        unsafe_allow_html=True)

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                proximas_acoes = st.text_area("Próximas ações:", height=80, key='dev_acoes',
                    placeholder="1. ...\n2. ...\n3. ...")
                apoio_necessario = st.text_area("Apoio necessário (o que o professor pediu):", height=80,
                    key='dev_apoio',
                    placeholder="Ex: Material de apoio para diferenciação, formação em avaliação formativa...")

            with col_c2:
                prazo = st.date_input("Prazo para reavaliação:", value=(hoje + timedelta(days=30)).date()
                    if hasattr(hoje, 'date') else hoje + timedelta(days=30),
                    key='dev_prazo')
                compromisso_prof = st.text_area("Compromisso do professor:", height=60, key='dev_comp_prof',
                    placeholder="O que o professor se compromete a fazer...")
                compromisso_coord = st.text_area("Compromisso da coordenação:", height=60, key='dev_comp_coord',
                    placeholder="O que a coordenação se compromete a providenciar...")

            # ===== RODAPÉ: COORDENADOR E ASSINATURAS =====
            st.markdown("---")
            col_rod1, col_rod2 = st.columns(2)
            with col_rod1:
                coordenador = st.text_input("Coordenador(a) responsável:",
                    value=st.session_state.get("display_name", ""), key='dev_coordenador')
            with col_rod2:
                status_dev = st.selectbox("Status:", ['Pendente', 'Em andamento', 'Concluido'],
                    key='dev_status')

            submitted = st.form_submit_button("Salvar Devolutiva", type="primary", use_container_width=True)

            if submitted:
                if not (comecar.strip() or cessar.strip() or continuar.strip() or
                        relato_recebido.strip() or posicionamento_prof.strip()):
                    st.error("Preencha ao menos um campo de Escuta ou dos 3C (Continuar, Começar, Cessar).")
                else:
                    disc_valor = disciplina_sel if disciplina_sel != 'Todas' else ''
                    # Limpa contexto de alerta apos uso
                    alerta_origem = None
                    if _alerta_ctx and _alerta_ctx.get('professor') == prof_sel:
                        alerta_origem = {
                            'tipo': _alerta_ctx.get('tipo_alerta', ''),
                            'nome': _alerta_ctx.get('nome_alerta', ''),
                            'detalhe': _alerta_ctx.get('detalhe', ''),
                        }
                        st.session_state.pop('devolutiva_from_alerta', None)

                    registro = {
                        'id': f"{unidade_sel}_{prof_sel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
                        'professor': prof_sel,
                        'unidade': unidade_sel,
                        'disciplina': disc_valor,
                        'segmento': segmento_sel,
                        'trimestre': trimestre,
                        'semana': semana,
                        'capitulo_esperado': cap_esperado,
                        'status': status_dev,
                        'alerta_origem': alerta_origem,
                        # Seção 1: Escuta e Diálogo Construtivo
                        'relato_recebido': relato_recebido.strip(),
                        'posicionamento_professor': posicionamento_prof.strip(),
                        'sbi_situacao': sbi_situacao.strip(),
                        'sbi_comportamento': sbi_comportamento.strip(),
                        'sbi_impacto': sbi_impacto.strip(),
                        # Seção 2: Continuar-Começar-Cessar
                        'continuar': continuar.strip(),
                        'comecar': comecar.strip(),
                        'cessar': cessar.strip(),
                        # Seção 3: Feed Forward
                        'feedforward': feedforward.strip(),
                        # Seção 4: Encaminhamentos e Combinados
                        'proximas_acoes': proximas_acoes.strip(),
                        'apoio_necessario': apoio_necessario.strip(),
                        'prazo': prazo.strftime('%d/%m/%Y'),
                        'compromisso_professor': compromisso_prof.strip(),
                        'compromisso_coordenacao': compromisso_coord.strip(),
                        # Métricas do momento
                        'metricas_snapshot': {
                            'taxa_registro': round(metricas['taxa_registro'], 1),
                            'taxa_conteudo': round(metricas['taxa_conteudo'], 1),
                            'taxa_tarefa': round(metricas['taxa_tarefa'], 1),
                            'aulas_registradas': metricas['aulas_registradas'],
                            'aulas_esperadas': metricas['aulas_esperadas'],
                        },
                        # Metadata
                        'coordenador': coordenador.strip(),
                        'registrado_por': st.session_state.get("username", "sistema"),
                    }
                    devolutivas.append(registro)
                    salvar_devolutivas(devolutivas)
                    st.success(f"Devolutiva registrada para {prof_sel}!")
                    st.balloons()

    # ========== TAB: HISTÓRICO ==========
    with tab_historico:
        st.subheader("Histórico de Devolutivas")

        # Filtrar devolutivas do professor selecionado
        dev_prof = [d for d in devolutivas
                    if d.get('professor') == prof_sel and d.get('unidade') == unidade_sel]

        if not dev_prof:
            st.info(f"Nenhuma devolutiva registrada para {prof_sel}.")
        else:
            # Ordenar do mais recente ao mais antigo
            dev_prof.sort(key=lambda x: x.get('data', ''), reverse=True)

            for i, dev in enumerate(dev_prof):
                _status = dev.get('status', 'Pendente')
                _status_icon = {'Pendente': '🟡', 'Em andamento': '🔵', 'Concluido': '✅'}.get(_status, '⚪')
                _alerta_tag = ''
                if dev.get('alerta_origem'):
                    _alerta_tag = f" | Alerta: {dev['alerta_origem'].get('nome', '')}"
                with st.expander(
                    f"{_status_icon} {dev.get('data', '—')} | {dev.get('trimestre', '?')}º Tri · Semana {dev.get('semana', '?')} | "
                    f"por {dev.get('coordenador', '—')}{_alerta_tag}",
                    expanded=(i == 0)
                ):
                    # Atualizar status
                    col_st1, col_st2 = st.columns([3, 1])
                    with col_st1:
                        st.caption(f"Status atual: **{_status}**")
                    with col_st2:
                        _novo_status = st.selectbox("Atualizar:", ['Pendente', 'Em andamento', 'Concluido'],
                            index=['Pendente', 'Em andamento', 'Concluido'].index(_status),
                            key=f'status_upd_{i}')
                        if _novo_status != _status:
                            dev['status'] = _novo_status
                            salvar_devolutivas(devolutivas)
                            st.rerun()

                    # Métricas do momento
                    snap = dev.get('metricas_snapshot', {})
                    if snap:
                        mc1, mc2, mc3 = st.columns(3)
                        with mc1:
                            st.metric("Registro (na data)", f"{snap.get('taxa_registro', 0):.0f}%")
                        with mc2:
                            st.metric("Conteúdo (na data)", f"{snap.get('taxa_conteudo', 0):.0f}%")
                        with mc3:
                            st.metric("Tarefa (na data)", f"{snap.get('taxa_tarefa', 0):.0f}%")

                    # Escuta e Diálogo Construtivo
                    has_escuta = any(dev.get(k) for k in ['relato_recebido', 'posicionamento_professor',
                                                          'sbi_situacao', 'sbi_comportamento', 'sbi_impacto'])
                    if has_escuta:
                        st.markdown("**1. Escuta e Diálogo Construtivo**")
                        if dev.get('relato_recebido'):
                            st.markdown(f'<div class="ccc-escuta"><strong>RELATO RECEBIDO</strong><br>{dev["relato_recebido"]}</div>',
                                        unsafe_allow_html=True)
                        if dev.get('posicionamento_professor'):
                            st.markdown(f'<div class="ccc-escuta"><strong>POSICIONAMENTO DO PROFESSOR</strong><br>{dev["posicionamento_professor"]}</div>',
                                        unsafe_allow_html=True)
                        if any(dev.get(k) for k in ['sbi_situacao', 'sbi_comportamento', 'sbi_impacto']):
                            sc1, sc2, sc3 = st.columns(3)
                            with sc1:
                                if dev.get('sbi_situacao'):
                                    st.markdown(f'<div class="ccc-sbi"><strong>Situação</strong><br>{dev["sbi_situacao"]}</div>',
                                                unsafe_allow_html=True)
                            with sc2:
                                if dev.get('sbi_comportamento'):
                                    st.markdown(f'<div class="ccc-sbi"><strong>Comportamento</strong><br>{dev["sbi_comportamento"]}</div>',
                                                unsafe_allow_html=True)
                            with sc3:
                                if dev.get('sbi_impacto'):
                                    st.markdown(f'<div class="ccc-sbi"><strong>Impacto</strong><br>{dev["sbi_impacto"]}</div>',
                                                unsafe_allow_html=True)

                    # Continuar-Começar-Cessar
                    if any(dev.get(k) for k in ['continuar', 'comecar', 'cessar']):
                        st.markdown("**2. Direcionamentos - Modelo 3C**")
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        if dev.get('continuar'):
                            st.markdown(f'<div class="ccc-continuar"><strong>CONTINUAR</strong><br>{dev["continuar"]}</div>',
                                        unsafe_allow_html=True)
                        if dev.get('cessar'):
                            st.markdown(f'<div class="ccc-cessar"><strong>CESSAR</strong><br>{dev["cessar"]}</div>',
                                        unsafe_allow_html=True)
                    with col_h2:
                        if dev.get('comecar'):
                            st.markdown(f'<div class="ccc-comecar"><strong>COMEÇAR</strong><br>{dev["comecar"]}</div>',
                                        unsafe_allow_html=True)

                    # Feed Forward
                    if dev.get('feedforward'):
                        st.markdown("**3. Olhando Para Frente**")
                        st.markdown(f'<div class="ccc-feedforward"><strong>FEED FORWARD</strong><br>{dev["feedforward"]}</div>',
                                    unsafe_allow_html=True)

                    # Encaminhamentos
                    if any(dev.get(k) for k in ['proximas_acoes', 'apoio_necessario', 'compromisso_professor', 'compromisso_coordenacao']):
                        st.markdown("**4. Encaminhamentos e Combinados**")
                        st.markdown('<div class="ccc-combinados"><strong>ENCAMINHAMENTOS E COMBINADOS</strong></div>',
                                    unsafe_allow_html=True)
                        ce1, ce2 = st.columns(2)
                        with ce1:
                            if dev.get('proximas_acoes'):
                                st.markdown(f"**Próximas ações:**\n{dev['proximas_acoes']}")
                            if dev.get('apoio_necessario'):
                                st.markdown(f"**Apoio solicitado pelo professor:**\n{dev['apoio_necessario']}")
                        with ce2:
                            if dev.get('compromisso_professor'):
                                st.markdown(f"**Compromisso do professor:**\n{dev['compromisso_professor']}")
                            if dev.get('compromisso_coordenacao'):
                                st.markdown(f"**Compromisso da coordenação:**\n{dev['compromisso_coordenacao']}")
                            if dev.get('prazo'):
                                st.markdown(f"**Prazo:** {dev['prazo']}")

            # Exportar histórico
            st.markdown("---")
            if st.button("Exportar Devolutivas deste Professor", key='dev_export'):
                linhas = []
                for dev in dev_prof:
                    linhas.append(f"={'=' * 60}")
                    linhas.append("FICHA DE FEEDBACK DOCENTE - MODELO INTEGRADO (3 C's + SBI + Feedforward)")
                    linhas.append(f"={'=' * 60}")
                    linhas.append(f"Data: {dev.get('data', '')}")
                    linhas.append(f"Professor(a): {dev.get('professor', '')} | {UNIDADES_NOMES.get(dev.get('unidade', ''), '')}")
                    disc = dev.get('disciplina', '')
                    seg = dev.get('segmento', '')
                    if disc or seg:
                        linhas.append(f"Disciplina: {disc or 'Todas'} | Segmento: {seg}")
                    linhas.append(f"Trimestre: {dev.get('trimestre', '')}º | Semana: {dev.get('semana', '')} | Cap. esperado: {dev.get('capitulo_esperado', '')}")
                    linhas.append(f"Coordenador(a): {dev.get('coordenador', '')}")
                    snap = dev.get('metricas_snapshot', {})
                    if snap:
                        linhas.append(f"Métricas: Registro {snap.get('taxa_registro', 0):.0f}% | Conteúdo {snap.get('taxa_conteudo', 0):.0f}% | Tarefa {snap.get('taxa_tarefa', 0):.0f}%")
                    linhas.append("")
                    # Seção 1: Escuta e Diálogo Construtivo
                    has_escuta = any(dev.get(k) for k in ['relato_recebido', 'posicionamento_professor',
                                                          'sbi_situacao', 'sbi_comportamento', 'sbi_impacto'])
                    if has_escuta:
                        linhas.append("1. ESCUTA E DIÁLOGO CONSTRUTIVO")
                        linhas.append("-" * 40)
                        if dev.get('relato_recebido'):
                            linhas.append(f"Relato recebido:\n{dev['relato_recebido']}")
                        if dev.get('posicionamento_professor'):
                            linhas.append(f"\nPosicionamento do professor:\n{dev['posicionamento_professor']}")
                        if any(dev.get(k) for k in ['sbi_situacao', 'sbi_comportamento', 'sbi_impacto']):
                            linhas.append("\nAnálise SBI:")
                            if dev.get('sbi_situacao'):
                                linhas.append(f"  Situação: {dev['sbi_situacao']}")
                            if dev.get('sbi_comportamento'):
                                linhas.append(f"  Comportamento: {dev['sbi_comportamento']}")
                            if dev.get('sbi_impacto'):
                                linhas.append(f"  Impacto: {dev['sbi_impacto']}")
                        linhas.append("")
                    # Seção 2: Direcionamentos 3C
                    linhas.append("2. DIRECIONAMENTOS - MODELO 3C")
                    linhas.append("-" * 40)
                    if dev.get('continuar'):
                        linhas.append(f"CONTINUAR:\n{dev['continuar']}")
                    if dev.get('comecar'):
                        linhas.append(f"\nCOMEÇAR:\n{dev['comecar']}")
                    if dev.get('cessar'):
                        linhas.append(f"\nCESSAR:\n{dev['cessar']}")
                    linhas.append("")
                    # Seção 3: Feed Forward
                    if dev.get('feedforward'):
                        linhas.append("3. OLHANDO PARA FRENTE (FEED FORWARD)")
                        linhas.append("-" * 40)
                        linhas.append(dev['feedforward'])
                        linhas.append("")
                    # Seção 4: Encaminhamentos e Combinados
                    if any(dev.get(k) for k in ['proximas_acoes', 'apoio_necessario', 'compromisso_professor', 'compromisso_coordenacao']):
                        linhas.append("4. ENCAMINHAMENTOS E COMBINADOS")
                        linhas.append("-" * 40)
                        if dev.get('proximas_acoes'):
                            linhas.append(f"Próximas ações: {dev['proximas_acoes']}")
                        if dev.get('apoio_necessario'):
                            linhas.append(f"Apoio solicitado: {dev['apoio_necessario']}")
                        if dev.get('compromisso_professor'):
                            linhas.append(f"Compromisso do professor: {dev['compromisso_professor']}")
                        if dev.get('compromisso_coordenacao'):
                            linhas.append(f"Compromisso da coordenação: {dev['compromisso_coordenacao']}")
                        if dev.get('prazo'):
                            linhas.append(f"Prazo: {dev['prazo']}")
                    linhas.append("")
                    # Rodapé com assinaturas
                    linhas.append(f"Recife, ___ de _______________ de ___")
                    linhas.append("")
                    linhas.append(f"_________________________________          _________________________________")
                    linhas.append(f"   {dev.get('professor', 'Professor(a)')}                    {dev.get('coordenador', 'Coordenador(a)')}")
                    linhas.append(f"        Professor(a)                              Coordenador(a)")
                    linhas.append("")

                texto = '\n'.join(linhas)
                st.download_button(
                    "Baixar TXT",
                    texto.encode('utf-8'),
                    file_name=f"devolutivas_{prof_sel.replace(' ', '_')}_{unidade_sel}.txt",
                    mime="text/plain"
                )

        # Visão geral: todos os professores com devolutiva
        st.markdown("---")
        st.subheader("Resumo Geral")

        dev_unidade = [d for d in devolutivas if d.get('unidade') == unidade_sel]
        if dev_unidade:
            # Última devolutiva por professor
            ultimo_por_prof = {}
            for d in dev_unidade:
                prof = d.get('professor', '')
                if prof not in ultimo_por_prof or d.get('data', '') > ultimo_por_prof[prof].get('data', ''):
                    ultimo_por_prof[prof] = d

            resumo = []
            for prof, d in sorted(ultimo_por_prof.items()):
                snap = d.get('metricas_snapshot', {})
                _st = d.get('status', 'Pendente')
                _st_icon = {'Pendente': '🟡', 'Em andamento': '🔵', 'Concluido': '✅'}.get(_st, '⚪')
                resumo.append({
                    'Professor': prof,
                    'Última Devolutiva': d.get('data', ''),
                    'Status': f"{_st_icon} {_st}",
                    'Trimestre': f"{d.get('trimestre', '')}º",
                    'Registro %': f"{snap.get('taxa_registro', 0):.0f}%",
                    'Prazo': d.get('prazo', ''),
                    'Coordenador': d.get('coordenador', ''),
                })

            df_resumo = pd.DataFrame(resumo)
            st.dataframe(df_resumo, use_container_width=True, hide_index=True)
            st.caption(f"{len(ultimo_por_prof)} professores com devolutiva | "
                       f"{len(professores_disp)} professores na unidade | "
                       f"{len(professores_disp) - len(ultimo_por_prof)} sem devolutiva")
        else:
            st.info("Nenhuma devolutiva registrada para esta unidade.")


main()
