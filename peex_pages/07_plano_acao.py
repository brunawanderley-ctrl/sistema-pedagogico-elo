"""
PEEX — Plano de Acao Semanal
3-5 acoes concretas geradas a partir dos dados reais + missoes dos robos.
Cada acao tem responsavel, prazo e status rastreavel.
"""

import json
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit, get_user_role
from utils import (
    DATA_DIR, calcular_semana_letiva, UNIDADES_NOMES, WRITABLE_DIR,
    carregar_fato_aulas, carregar_horario_esperado, carregar_ocorrencias,
    filtrar_ate_hoje, _hoje,
)
from components import cabecalho_pagina
from engine import carregar_missoes_pregeradas
from narrativa import gerar_nudge


# ========== CSS ==========

st.markdown("""
<style>
    .acao-card {
        padding: 14px 18px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid;
        background: #fafafa;
    }
    .acao-titulo { font-weight: bold; font-size: 1em; margin-bottom: 2px; }
    .acao-contexto { font-size: 0.85em; color: #666; margin-bottom: 4px; }
    .acao-meta { font-size: 0.8em; color: #999; }
    .nudge-semanal {
        background: #e8eaf6;
        border-radius: 10px;
        padding: 14px 20px;
        margin: 12px 0;
        font-style: italic;
        color: #283593;
    }
    .progresso-bar {
        background: #e0e0e0;
        border-radius: 10px;
        height: 12px;
        margin: 8px 0;
    }
    .progresso-fill {
        border-radius: 10px;
        height: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ========== PERSISTENCIA ==========

def _plano_path(semana, unidade):
    return WRITABLE_DIR / f"plano_acao_sem{semana}_{unidade}.json"


def carregar_plano(semana, unidade):
    path = _plano_path(semana, unidade)
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def salvar_plano(semana, unidade, plano):
    path = _plano_path(semana, unidade)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(plano, f, ensure_ascii=False, indent=2)


# ========== GERAR ACOES COM DADOS REAIS ==========

def _gerar_acoes_reais(unidade, semana):
    """Gera acoes concretas baseadas nos dados reais da unidade."""
    acoes = []

    # Carregar resumo executivo
    resumo_path = DATA_DIR / "resumo_Executivo.csv"
    conf, freq, graves, risco = 0, 0, 0, 0
    profs_criticos_n, total_profs = 0, 0

    if resumo_path.exists():
        try:
            df = pd.read_csv(resumo_path)
            un = df[df['unidade'] == unidade]
            if not un.empty:
                r = un.iloc[0]
                conf = r.get('pct_conformidade_media', 0)
                freq = r.get('frequencia_media', 0)
                graves = int(r.get('ocorr_graves', 0))
                risco = r.get('pct_alunos_risco', 0)
                profs_criticos_n = int(r.get('professores_criticos', 0))
                total_profs = int(r.get('total_professores', 0))
        except Exception:
            pass

    # Professores individuais
    profs_nomes = []
    df_aulas = carregar_fato_aulas()
    df_aulas = filtrar_ate_hoje(df_aulas)
    df_hor = carregar_horario_esperado()

    if not df_aulas.empty and not df_hor.empty:
        df_un = df_aulas[df_aulas['unidade'] == unidade]
        df_hor_un = df_hor[df_hor['unidade'] == unidade]

        for prof, df_p in df_un.groupby('professor'):
            esp = 0
            for s in df_p['serie'].unique():
                for d in df_p['disciplina'].unique():
                    esp += len(df_hor_un[
                        (df_hor_un['serie'] == s) & (df_hor_un['disciplina'] == d)
                    ]) * semana
            if esp > 0:
                c = len(df_p) / esp * 100
                if c < 40:
                    profs_nomes.append((prof, c))

        profs_nomes.sort(key=lambda x: x[1])

    # Turmas com ocorrencias graves
    turmas_graves = []
    df_ocorr = carregar_ocorrencias()
    if not df_ocorr.empty:
        df_ocorr_un = df_ocorr[df_ocorr['unidade'] == unidade]
        g = df_ocorr_un[df_ocorr_un['gravidade'] == 'Grave']
        if not g.empty:
            top = g.groupby(['serie', 'turma']).size().sort_values(ascending=False).head(3)
            turmas_graves = [(f"{s} {t}", int(n)) for (s, t), n in top.items()]

    # ===== GERAR ACOES POR PRIORIDADE =====

    # 1. Conformidade baixa → falar com professores
    if profs_nomes:
        nomes_lista = ', '.join(f"{p}" for p, _ in profs_nomes[:3])
        acoes.append({
            'titulo': f'Conversar com {len(profs_nomes)} professores criticos',
            'contexto': (
                f'Conformidade da unidade em {conf:.0f}%. '
                f'Prioridade: {nomes_lista}'
            ),
            'como': (
                'Agendar 10 min com cada. Perguntar: "O que esta impedindo '
                'voce de registrar?" Ouvir antes de cobrar.'
            ),
            'responsavel': 'Coordenador(a)',
            'prazo': 'quarta-feira',
            'status': 'nao_iniciada',
            'nota': '',
        })
    elif profs_criticos_n > 0:
        acoes.append({
            'titulo': f'Identificar e conversar com {profs_criticos_n} professores criticos',
            'contexto': f'Conformidade da unidade em {conf:.0f}% (meta: 70%)',
            'como': (
                'Abrir o Semaforo Professor, filtrar por vermelho. '
                'Agendar 10 min com os 3 piores.'
            ),
            'responsavel': 'Coordenador(a)',
            'prazo': 'quarta-feira',
            'status': 'nao_iniciada',
            'nota': '',
        })

    # 2. Frequencia baixa → busca ativa
    if freq < 85:
        acoes.append({
            'titulo': 'Busca ativa: alunos com 3+ faltas na semana',
            'contexto': (
                f'Frequencia em {freq:.1f}% (meta: 88%). '
                f'{risco:.0f}% dos alunos estao em risco.'
            ),
            'como': (
                'Abrir Frequencia Escolar, filtrar abaixo de 75%. '
                'Secretaria liga para as familias. '
                'Coordenador conversa com aluno no retorno.'
            ),
            'responsavel': 'Secretaria + Coordenador(a)',
            'prazo': 'quinta-feira',
            'status': 'nao_iniciada',
            'nota': '',
        })

    # 3. Ocorrencias graves → presenca na turma
    if turmas_graves:
        turma_pior, n_graves = turmas_graves[0]
        acoes.append({
            'titulo': f'Presenca fisica na turma {turma_pior} ({n_graves} graves)',
            'contexto': (
                f'{graves} ocorrencias graves na unidade. '
                f'Turma {turma_pior} concentra a maioria.'
            ),
            'como': (
                'Ficar no corredor/sala nos 2 primeiros horarios '
                'por 2 dias consecutivos. Observar e anotar. '
                'Conversar individualmente com alunos reincidentes.'
            ),
            'responsavel': 'Coordenador(a)',
            'prazo': 'sexta-feira',
            'status': 'nao_iniciada',
            'nota': '',
        })

    # 4. Alunos em risco alto → plano individual
    if risco > 20:
        n_risco = int(risco * total_profs / 100) if total_profs else 0
        acoes.append({
            'titulo': 'Plano individual para alunos em risco critico',
            'contexto': (
                f'{risco:.0f}% dos alunos em situacao de risco. '
                f'Abrir Alerta Precoce ABC para lista completa.'
            ),
            'como': (
                'Selecionar os 5 mais criticos. '
                'Para cada: 1 conversa com aluno, 1 contato com familia, '
                '1 combinado com professor regente.'
            ),
            'responsavel': 'Coordenador(a) + Professor regente',
            'prazo': 'sexta-feira',
            'status': 'nao_iniciada',
            'nota': '',
        })

    # 5. Acao positiva (sempre incluir)
    if conf >= 70:
        acoes.append({
            'titulo': 'Reconhecer professores destaque da semana',
            'contexto': (
                f'Conformidade em {conf:.0f}% — acima da meta! '
                f'Reconhecimento reforca o comportamento.'
            ),
            'como': (
                'Mandar mensagem no grupo da unidade citando os '
                '3 professores com melhor conformidade. '
                'Um elogio publico vale mais que 10 cobranças.'
            ),
            'responsavel': 'Diretor(a) / Coordenador(a)',
            'prazo': 'sexta-feira',
            'status': 'nao_iniciada',
            'nota': '',
        })
    else:
        acoes.append({
            'titulo': 'Revisar plano da semana anterior e registrar aprendizados',
            'contexto': 'Fechar o ciclo: o que funcionou? O que mudar?',
            'como': (
                'Abrir Plano de Acao da semana anterior. '
                'Marcar o que foi concluido. '
                'Anotar o que nao foi feito e por que.'
            ),
            'responsavel': 'Coordenador(a)',
            'prazo': 'segunda-feira',
            'status': 'nao_iniciada',
            'nota': '',
        })

    return acoes[:5]


def _gerar_acoes_missoes(missoes, semana, unidade):
    """Fallback: gera acoes a partir das missoes dos robos."""
    acoes = []
    for b in missoes[:5]:
        como = b.get('como', [])
        acoes.append({
            'titulo': como[0] if como else f"Resolver: {b.get('tipo', '')}",
            'contexto': b.get('o_que', ''),
            'como': como[1] if len(como) > 1 else '',
            'tipo_missao': b.get('tipo', ''),
            'responsavel': '',
            'prazo': 'sexta-feira',
            'status': 'nao_iniciada',
            'nota': '',
        })
    return acoes


# ========== NUDGES SEMANAIS ==========

_NUDGES_SEMANAIS = [
    "Coordenadores PEEX sao guardioes: cada registro e uma semente plantada.",
    "Uma conversa de 10 minutos pode mudar a semana inteira de um professor.",
    "23 de 28 coordenadores ja completaram o plano esta semana. Voce tambem pode.",
    "Quem registra primeiro, resolve primeiro. Comece pela acao #1.",
    "Pequenas acoes consistentes vencem grandes planos nunca executados.",
    "O segredo nao e fazer tudo — e fazer o mais importante primeiro.",
    "Lideranca nao e cobrar. E perguntar: como posso te ajudar?",
    "Dados sem acao sao so numeros. Acao sem dados e achismo. Use os dois.",
]


# ========== MAIN ==========

cabecalho_pagina("Plano de Acao Semanal", "Acoes concretas para esta semana")

semana = calcular_semana_letiva()
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)

# Nudge da semana
nudge_idx = (semana - 1) % len(_NUDGES_SEMANAIS)
st.markdown(f'<div class="nudge-semanal">{_NUDGES_SEMANAIS[nudge_idx]}</div>', unsafe_allow_html=True)

st.markdown(f"### Semana {semana} — {nome_un}")

# Carregar plano salvo ou gerar novo
plano = carregar_plano(semana, user_unit)

if plano is None:
    # Tentar gerar com dados reais primeiro
    acoes = _gerar_acoes_reais(user_unit, semana)

    # Se nao gerou acoes suficientes, complementar com missoes dos robos
    if len(acoes) < 3:
        missoes = carregar_missoes_pregeradas(user_unit)
        if missoes:
            acoes_robos = _gerar_acoes_missoes(missoes, semana, user_unit)
            # Adicionar apenas as que nao duplicam
            titulos_existentes = {a['titulo'] for a in acoes}
            for ar in acoes_robos:
                if ar['titulo'] not in titulos_existentes and len(acoes) < 5:
                    acoes.append(ar)

    if not acoes:
        acoes = [{
            'titulo': 'Verificar dados do SIGA',
            'contexto': 'Sem dados carregados para gerar acoes automaticas.',
            'como': 'Execute a extracao do SIGA ou verifique se os CSVs existem.',
            'responsavel': 'Coordenador(a)',
            'prazo': 'hoje',
            'status': 'nao_iniciada',
            'nota': '',
        }]

    plano = {
        'semana': semana,
        'unidade': user_unit,
        'gerado_em': datetime.now().isoformat(),
        'fonte': 'dados_reais',
        'acoes': acoes,
    }
    salvar_plano(semana, user_unit, plano)
    st.caption("Plano gerado automaticamente com dados reais da unidade")
else:
    st.caption(f"Plano salvo em {plano.get('gerado_em', '?')[:10]}")


# ========== EXIBIR ACOES ==========

cores_status = {
    'nao_iniciada': '#9e9e9e',
    'em_andamento': '#ffa000',
    'resolvida': '#43a047',
}

alterado = False
acoes = plano.get('acoes', [])

for i, acao in enumerate(acoes):
    cor = cores_status.get(acao.get('status', 'nao_iniciada'), '#9e9e9e')
    contexto = acao.get('contexto', '')
    como = acao.get('como', '')

    # Card visual
    st.markdown(f"""
    <div class="acao-card" style="border-left-color:{cor};">
        <div class="acao-titulo">{i+1}. {acao['titulo']}</div>
        {f'<div class="acao-contexto">📌 {contexto}</div>' if contexto else ''}
        {f'<div class="acao-contexto">💡 {como}</div>' if como else ''}
        <div class="acao-meta">
            Responsavel: {acao.get('responsavel', '-')} |
            Prazo: {acao.get('prazo', 'sexta')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        nota = st.text_input(
            "Nota/observacao:",
            value=acao.get('nota', ''),
            key=f"plano_nota_{i}",
            label_visibility="collapsed",
            placeholder="Adicionar observacao...",
        )
        if nota != acao.get('nota', ''):
            acao['nota'] = nota
            alterado = True

    with c2:
        opcoes = ['Nao iniciada', 'Em andamento', 'Resolvida']
        mapa = {'nao_iniciada': 0, 'em_andamento': 1, 'resolvida': 2}
        status_novo = st.radio(
            "Status:",
            opcoes,
            index=mapa.get(acao.get('status', 'nao_iniciada'), 0),
            key=f"plano_status_{i}",
            horizontal=True,
        )
        status_key = status_novo.lower().replace(' ', '_').replace('ã', 'a')
        if status_key != acao.get('status', 'nao_iniciada'):
            acao['status'] = status_key
            alterado = True

if alterado:
    plano['acoes'] = acoes
    plano['atualizado_em'] = datetime.now().isoformat()
    salvar_plano(semana, user_unit, plano)

# ========== REGENERAR ==========

st.markdown("---")
if st.button("Regenerar plano com dados atuais", type="secondary"):
    acoes_novas = _gerar_acoes_reais(user_unit, semana)
    if acoes_novas:
        plano['acoes'] = acoes_novas
        plano['gerado_em'] = datetime.now().isoformat()
        plano['fonte'] = 'dados_reais'
        salvar_plano(semana, user_unit, plano)
        st.rerun()

# ========== RESUMO ==========

st.markdown("---")
total = len(acoes)
resolvidas = sum(1 for a in acoes if a.get('status') == 'resolvida')
em_andamento = sum(1 for a in acoes if a.get('status') == 'em_andamento')
pct = round(resolvidas / max(total, 1) * 100)

# Barra de progresso visual
cor_progresso = '#43a047' if pct >= 80 else '#ffa000' if pct >= 40 else '#e53935'
st.markdown(f"""
<div class="progresso-bar">
    <div class="progresso-fill" style="width:{pct}%; background:{cor_progresso};"></div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Total", total)
c2.metric("Em andamento", em_andamento)
c3.metric("Resolvidas", f"{resolvidas}/{total}", f"{pct}%")

if resolvidas == total and total > 0:
    st.balloons()
    st.success("Todas as acoes resolvidas! Excelente trabalho esta semana!")
