#!/usr/bin/env python3
"""
ONBOARDING — Pagina de boas-vindas e tutorial adaptativo por perfil.
Explica o sistema, mostra o que cada perfil ve e sugere primeiros passos.
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from auth import get_user_role


# ---------------------------------------------------------------------------
# Constantes por perfil
# ---------------------------------------------------------------------------

PERFIL_LABELS = {
    "ceo": "CEO / Administrador",
    "diretor": "Diretor(a) de Unidade",
    "coordenador": "Coordenador(a) Pedagogico(a)",
    "professor": "Professor(a)",
}

VISAO_POR_PERFIL = {
    "ceo": (
        "Voce tem acesso a **TODAS** as paginas. "
        "Visao completa de 4 unidades, estrategia PEEX, reunioes e relatorios."
    ),
    "diretor": (
        "Voce ve a estrategia e acompanhamento da sua unidade "
        "+ visao de rede nos rankings."
    ),
    "coordenador": (
        "Voce ve seus professores, seus alunos, suas missoes "
        "e as ferramentas de reuniao."
    ),
    "professor": (
        "Voce ve seu espelho (como esta indo), suas turmas "
        "e seu progresso."
    ),
}

PRIMEIROS_PASSOS = {
    "ceo": [
        ("Comando CEO", "Visao executiva de toda a rede em uma unica tela."),
        ("Preparador de Reuniao", "Roteiro automatico para a proxima reuniao de gestao."),
        ("Scorecard", "Como cada unidade esta nos indicadores-chave."),
    ],
    "diretor": [
        ("Quadro de Gestao", "Visao geral da sua unidade: aulas, conformidade, alertas."),
        ("Sinais Vitais", "Indicadores criticos que precisam de atencao imediata."),
        ("Preparador de Reuniao", "Roteiro para a reuniao com coordenadores."),
    ],
    "coordenador": [
        ("Prioridades da Semana", "Missoes geradas automaticamente para esta semana."),
        ("Semaforo do Professor", "Quem precisa de atencao? Vermelho, amarelo e verde."),
        ("Meus Alunos", "Visao consolidada de frequencia, notas e alertas por aluno."),
    ],
    "professor": [
        ("Meu Espelho", "Como voce esta indo: conformidade, conteudo e frequencia."),
        ("Minhas Turmas", "Detalhamento por turma: quem esta presente, quem faltou."),
        ("Meu Progresso", "Avanco no material SAE e capitulos registrados."),
    ],
}


# ---------------------------------------------------------------------------
# Pagina
# ---------------------------------------------------------------------------

role = get_user_role()
label_perfil = PERFIL_LABELS.get(role, "Visitante")

# ===== Cabecalho =====
st.title("Bem-vindo ao Sistema Pedagogico ELO")
st.caption(f"Seu perfil: **{label_perfil}**")
st.markdown("---")


# ===== 1. O que e o Sistema Pedagogico ELO? =====
st.header("O que e o Sistema Pedagogico ELO?")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.subheader("SIGA")
    st.markdown(
        "Sistema de Gestao Academica: diarios de classe, notas, frequencia e ocorrencias."
    )

with col_b:
    st.subheader("SAE Digital")
    st.markdown(
        "Plataforma de conteudo: materiais didaticos, exercicios, avaliações e progresso."
    )

with col_c:
    st.subheader("Sistema ELO")
    st.markdown(
        "Integra SIGA + SAE em tempo real para acompanhamento pedagogico completo da rede."
    )

st.info(
    "O sistema extrai dados automaticamente (4x ao dia) e gera indicadores, "
    "alertas e missoes para cada perfil da escola."
)

st.markdown("---")


# ===== 2. O que voce ve? =====
st.header("O que voce ve?")

visao = VISAO_POR_PERFIL.get(role, "Acesso basico ao sistema.")
st.markdown(visao)

st.markdown("---")


# ===== 3. Por onde comecar? =====
st.header("Por onde comecar?")
st.markdown("Tres passos recomendados para o seu perfil:")

passos = PRIMEIROS_PASSOS.get(role, [])

cols_passos = st.columns(3) if passos else []

for idx, (titulo, descricao) in enumerate(passos):
    with cols_passos[idx]:
        st.subheader(f"{idx + 1}. {titulo}")
        st.markdown(descricao)

st.markdown("---")


# ===== 4. Como funciona a semana PEEX? =====
st.header("Como funciona a semana PEEX?")
st.markdown(
    "O ciclo semanal do **Programa de Excelencia e Execucao (PEEX)** "
    "garante que dados virem acao de forma sistematica."
)

col_seg, col_qt, col_sex, col_dom = st.columns(4)

with col_seg:
    st.subheader("Segunda")
    st.markdown(
        "Robos geram **missoes** da semana e o **roteiro de reuniao** "
        "com base nos dados atualizados."
    )

with col_qt:
    st.subheader("Terca a Quinta")
    st.markdown(
        "Coordenadores **executam acoes**: devolutivas, acompanhamento "
        "de aulas e intervencoes com alunos."
    )

with col_sex:
    st.subheader("Sexta")
    st.markdown(
        "O **Preditor** projeta a proxima semana: quem vai precisar de "
        "atencao, quais turmas estao em risco."
    )

with col_dom:
    st.subheader("Domingo")
    st.markdown(
        "O **Estrategista** consolida tudo: relatorio semanal, "
        "scorecard atualizado e ajustes de rota."
    )

st.markdown("---")

# Rodape
st.caption(
    "Sistema Pedagogico Integrado - Colegio ELO 2026 | "
    "Duvidas? Procure a coordenacao pedagogica da sua unidade."
)
