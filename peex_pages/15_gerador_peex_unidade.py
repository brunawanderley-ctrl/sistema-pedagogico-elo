"""
PEEX — Gerador de Pauta PEEX Unidade (Coordenador/Diretor)
Pauta para reuniao de unidade (35x/ano) com dados locais.
Funciona com dados reais (CSV) + enriquecimento dos robos quando disponivel.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_user_unit
from utils import (
    DATA_DIR, calcular_semana_letiva, calcular_trimestre, UNIDADES_NOMES,
    carregar_fato_aulas, carregar_horario_esperado, carregar_ocorrencias,
    carregar_frequencia_alunos, filtrar_ate_hoje, _hoje,
)
from components import cabecalho_pagina
from peex_utils import info_semana, proximas_reunioes
from engine import carregar_missoes_pregeradas, carregar_conselheiro, carregar_preparador
from narrativa import gerar_nudge


# ========== HELPERS: DADOS REAIS ==========

def _carregar_dados_unidade(unidade, semana):
    """Carrega e processa dados reais da unidade a partir dos CSVs."""
    dados = {
        'conf': 0, 'freq': 0, 'profs_criticos': [],
        'profs_excelentes': [], 'total_profs': 0,
        'graves': 0, 'total_ocorr': 0, 'turmas_graves': [],
        'alunos_risco_pct': 0, 'total_alunos': 0,
        'aulas_sem_conteudo': 0, 'total_aulas': 0,
        'tem_dados': False,
    }

    # Resumo executivo (fonte principal)
    resumo_path = DATA_DIR / "resumo_Executivo.csv"
    if resumo_path.exists():
        try:
            df = pd.read_csv(resumo_path)
            un = df[df['unidade'] == unidade]
            if not un.empty:
                r = un.iloc[0]
                dados['conf'] = r.get('pct_conformidade_media', 0)
                dados['freq'] = r.get('frequencia_media', 0)
                dados['total_profs'] = int(r.get('total_professores', 0))
                dados['profs_criticos_n'] = int(r.get('professores_criticos', 0))
                dados['profs_excelentes_n'] = int(r.get('professores_excelentes', 0))
                dados['graves'] = int(r.get('ocorr_graves', 0))
                dados['total_ocorr'] = int(r.get('total_ocorrencias', 0))
                dados['alunos_risco_pct'] = r.get('pct_alunos_risco', 0)
                dados['total_alunos'] = int(r.get('total_alunos', 0))
                dados['aulas_sem_conteudo_pct'] = 100 - r.get('pct_conteudo_preenchido', 100)
                dados['tem_dados'] = True
        except Exception:
            pass

    # Professores individuais (para listar nomes)
    df_aulas = carregar_fato_aulas()
    df_aulas = filtrar_ate_hoje(df_aulas)
    df_hor = carregar_horario_esperado()

    if not df_aulas.empty and not df_hor.empty:
        df_un = df_aulas[df_aulas['unidade'] == unidade]
        df_hor_un = df_hor[df_hor['unidade'] == unidade]

        profs_conf = []
        for prof, df_p in df_un.groupby('professor'):
            esp = 0
            for s in df_p['serie'].unique():
                for d in df_p['disciplina'].unique():
                    esp += len(df_hor_un[
                        (df_hor_un['serie'] == s) & (df_hor_un['disciplina'] == d)
                    ]) * semana
            if esp > 0:
                c = len(df_p) / esp * 100
                profs_conf.append((prof, c))

        profs_conf.sort(key=lambda x: x[1])
        dados['profs_criticos'] = [(p, c) for p, c in profs_conf if c < 40][:5]
        dados['profs_excelentes'] = [(p, c) for p, c in profs_conf if c >= 85][:3]

        # Aulas sem conteudo recentes
        df_recente = df_un[df_un['data'] >= (_hoje() - pd.Timedelta(days=7))]
        if not df_recente.empty:
            sem = df_recente[df_recente['conteudo'].isna() | (df_recente['conteudo'] == '')]
            dados['aulas_sem_conteudo'] = len(sem)
            dados['total_aulas'] = len(df_recente)

    # Ocorrencias (turmas com mais graves)
    df_ocorr = carregar_ocorrencias()
    if not df_ocorr.empty:
        df_ocorr_un = df_ocorr[df_ocorr['unidade'] == unidade]
        graves_un = df_ocorr_un[df_ocorr_un['gravidade'] == 'Grave']
        if not graves_un.empty:
            top_turmas = (
                graves_un.groupby(['serie', 'turma']).size()
                .sort_values(ascending=False).head(3)
            )
            dados['turmas_graves'] = [
                (f"{s} {t}", int(n)) for (s, t), n in top_turmas.items()
            ]

    return dados


def _gerar_pauta_real(dados, semana, unidade, nome_un, info):
    """Gera os 5 atos com dados reais da unidade."""
    fase = info['fase']
    prox = info.get('proxima_reuniao', {})
    fmt = info.get('formato_reuniao', {})

    # Determinar tom baseado na saude
    if dados['conf'] >= 70 and dados['freq'] >= 85:
        tom = 'positivo'
        abertura = f"Boa semana, equipe! {nome_un} esta no caminho certo."
    elif dados['conf'] < 50 or dados['freq'] < 80:
        tom = 'urgente'
        abertura = f"Equipe, precisamos conversar. Os numeros desta semana pedem atencao."
    else:
        tom = 'atencao'
        abertura = f"Semana de ajustes. Temos pontos bons e pontos que precisam de foco."

    atos = []

    # ===== ATO 1: RAIZES =====
    atos.append({
        'nome': 'Raizes',
        'duracao': '5 min',
        'cor': '#795548',
        'abertura': abertura,
        'itens': [
            "Roda rapida: cada um diz em 1 palavra como esta chegando hoje.",
            f"Estamos na Semana {semana} — Fase {fase['nome']}.",
        ],
    })

    # ===== ATO 2: SOLO (DADOS) =====
    itens_solo = []
    itens_solo.append(f"**Conformidade:** {dados['conf']:.0f}% (meta: 70%)")
    itens_solo.append(f"**Frequencia:** {dados['freq']:.1f}% (meta: 88%)")

    if dados['graves'] > 0:
        itens_solo.append(f"**Ocorrencias graves:** {dados['graves']}")
    if dados['alunos_risco_pct'] > 15:
        itens_solo.append(
            f"**Alunos em risco:** {dados['alunos_risco_pct']:.0f}% "
            f"({int(dados['total_alunos'] * dados['alunos_risco_pct'] / 100)} alunos)"
        )

    # Professores criticos com nomes
    if dados['profs_criticos']:
        nomes = ', '.join(f"{p} ({c:.0f}%)" for p, c in dados['profs_criticos'][:3])
        itens_solo.append(f"**Professores criticos:** {nomes}")
    elif dados.get('profs_criticos_n', 0) > 0:
        itens_solo.append(f"**Professores criticos:** {dados['profs_criticos_n']}")

    # Turmas com ocorrencias graves
    if dados['turmas_graves']:
        turmas_txt = ', '.join(f"{t} ({n})" for t, n in dados['turmas_graves'])
        itens_solo.append(f"**Turmas com mais graves:** {turmas_txt}")

    atos.append({
        'nome': 'Solo',
        'duracao': '10 min',
        'cor': '#8D6E63',
        'abertura': "Vamos olhar os numeros desta semana:",
        'itens': itens_solo,
    })

    # ===== ATO 3: MICELIO (CONEXOES) =====
    itens_micelio = []

    if dados['profs_criticos']:
        itens_micelio.append(
            f"Quem pode ajudar os {len(dados['profs_criticos'])} professores "
            f"com baixa conformidade? Algum colega da mesma disciplina?"
        )
    if dados['turmas_graves']:
        turma_pior = dados['turmas_graves'][0][0]
        itens_micelio.append(
            f"O que esta acontecendo no {turma_pior}? "
            f"Quem tem turno com essa turma e pode observar?"
        )
    if dados['freq'] < 85:
        itens_micelio.append(
            "Quais alunos estao faltando? Alguem ja ligou para as familias?"
        )

    if not itens_micelio:
        itens_micelio = [
            "Quem precisa de ajuda esta semana?",
            "Quem pode compartilhar uma boa pratica?",
        ]

    itens_micelio.append(
        "Algum professor pediu suporte que ainda nao foi atendido?"
    )

    atos.append({
        'nome': 'Micelio',
        'duracao': '10 min',
        'cor': '#43A047',
        'abertura': "Hora das conexoes — ninguem resolve sozinho:",
        'itens': itens_micelio,
    })

    # ===== ATO 4: SEMENTES (COMPROMISSOS) =====
    compromissos = []

    if dados['profs_criticos']:
        n = len(dados['profs_criticos'])
        compromissos.append(
            f"Conversar individualmente com os {n} professores criticos "
            f"ate quarta-feira"
        )
    if dados['freq'] < 85:
        compromissos.append(
            "Fazer busca ativa: ligar para familias dos alunos "
            "com 3+ faltas esta semana"
        )
    if dados['turmas_graves']:
        turma_pior = dados['turmas_graves'][0][0]
        compromissos.append(
            f"Presenca na turma {turma_pior} por 2 dias consecutivos "
            f"para observacao"
        )
    if dados.get('aulas_sem_conteudo', 0) > 5:
        compromissos.append(
            f"Cobrar preenchimento de conteudo dos {dados['aulas_sem_conteudo']} "
            f"registros vazios desta semana"
        )
    if dados['conf'] < 50:
        compromissos.append(
            "Reuniao rapida (15 min) com cada professor que nao registrou "
            "nenhuma aula esta semana"
        )

    if not compromissos:
        compromissos = [
            "Manter o ritmo positivo — reconhecer 2 professores destaque",
            "Revisar plano de acao da semana anterior",
            "Identificar 1 melhoria para a proxima semana",
        ]

    atos.append({
        'nome': 'Sementes',
        'duracao': '10 min',
        'cor': '#66BB6A',
        'abertura': "Compromissos concretos — saimos daqui com nome, acao e prazo:",
        'itens': compromissos[:5],
    })

    # ===== ATO 5: CHUVA (CELEBRACAO) =====
    itens_chuva = []

    if dados['profs_excelentes']:
        nomes_ex = ', '.join(p for p, _ in dados['profs_excelentes'])
        itens_chuva.append(f"Destaque da semana: {nomes_ex} (acima de 85%)")
    if dados['conf'] > 60:
        itens_chuva.append(
            f"Conformidade em {dados['conf']:.0f}% — estamos evoluindo!"
        )
    if dados['freq'] >= 88:
        itens_chuva.append(
            f"Frequencia em {dados['freq']:.1f}% — acima da meta!"
        )

    if not itens_chuva:
        itens_chuva.append(
            "Qual foi a melhor coisa que aconteceu na unidade esta semana?"
        )

    itens_chuva.append("NUNCA terminar com problema. Sair com energia positiva.")

    atos.append({
        'nome': 'Chuva',
        'duracao': '5 min',
        'cor': '#29B6F6',
        'abertura': "Encerrando com o que temos de bom:",
        'itens': itens_chuva,
    })

    return atos


# ========== CSS ==========

st.markdown("""
<style>
    .ato-card {
        padding: 16px 20px;
        margin: 8px 0;
        border-radius: 10px;
        border-left: 5px solid;
        background: #fafafa;
    }
    .ato-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .ato-titulo { font-weight: bold; font-size: 1.1em; }
    .ato-duracao { font-size: 0.85em; color: #888; }
    .ato-abertura {
        font-style: italic;
        color: #555;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 1px solid #eee;
    }
    .ato-item { padding: 3px 0; }
    .saude-banner {
        padding: 16px 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


# ========== MAIN ==========

cabecalho_pagina("Pauta da Reuniao", "Roteiro para reuniao semanal da unidade")

semana = calcular_semana_letiva()
trimestre = calcular_trimestre(semana)
user_unit = get_user_unit() or 'BV'
nome_un = UNIDADES_NOMES.get(user_unit, user_unit)
info = info_semana(semana)
fase = info['fase']

st.markdown(f"### {nome_un} | Semana {semana} | Fase {info['fase_num']}: {fase['nome']}")

# Proxima reuniao
prox = info['proxima_reuniao']
if prox:
    fmt = info['formato_reuniao']
    st.info(
        f"**{prox.get('titulo', '')}** — Formato {fmt.get('nome', '')} "
        f"({fmt.get('duracao', 30)} min) | Foco: {prox.get('foco', '')}"
    )

# ========== CARREGAR DADOS ==========

dados = _carregar_dados_unidade(user_unit, semana)

# Banner de saude da unidade
if dados['tem_dados']:
    cor_saude = '#c62828' if dados['conf'] < 50 else '#e65100' if dados['conf'] < 70 else '#2e7d32'
    st.markdown(f"""
    <div class="saude-banner" style="background:linear-gradient(135deg, {cor_saude}, {cor_saude}dd);">
        <strong>{nome_un} esta semana:</strong>
        Conformidade {dados['conf']:.0f}% | Frequencia {dados['freq']:.1f}% |
        {dados['graves']} ocorrencias graves |
        {dados.get('profs_criticos_n', len(dados['profs_criticos']))} professores criticos
    </div>
    """, unsafe_allow_html=True)


# ========== GERAR PAUTA: ROBOS + DADOS REAIS ==========

# Tentar dados dos robos primeiro
conselheiro = carregar_conselheiro()
pauta_cons = conselheiro.get('pautas', {}).get(user_unit, {})
preparador = carregar_preparador()
script_robos = preparador.get('script_5_atos', {})
roteiro_un = preparador.get('roteiro_por_unidade', {}).get(user_unit, {})

# Se robos tem script completo, usar. Senao, dados reais.
usar_robos = bool(script_robos and script_robos.get('ato1_raizes', {}).get('o_que_dizer'))

if usar_robos:
    st.caption("Pauta enriquecida pelos robos CONSELHEIRO + PREPARADOR")
else:
    st.caption("Pauta gerada com dados reais da unidade")

st.markdown("---")
st.markdown("### Ritual de Floresta — 5 Atos")

if usar_robos:
    # ===== PATH ROBOS =====
    nomes_atos = [
        ('ato1_raizes', 'Raizes', '#795548'),
        ('ato2_solo', 'Solo', '#8D6E63'),
        ('ato3_micelio', 'Micelio', '#43A047'),
        ('ato4_sementes', 'Sementes', '#66BB6A'),
        ('ato5_chuva', 'Chuva', '#29B6F6'),
    ]
    pauta_texto_items = []
    for i, (key, nome, cor) in enumerate(nomes_atos, 1):
        ato = script_robos.get(key, {})
        duracao = ato.get('duracao', '? min')
        o_que_dizer = ato.get('o_que_dizer', '')
        dados_mostrar = ato.get('dados_para_mostrar', [])
        perguntas = ato.get('perguntas_prontas', [])
        compromissos_sug = ato.get('compromissos_sugeridos', [])
        celebracao = ato.get('celebracao', '')

        itens_html = []
        if o_que_dizer:
            itens_html.append(f'<div class="ato-abertura">"{o_que_dizer}"</div>')
        for d in dados_mostrar:
            itens_html.append(f'<div class="ato-item">📊 {d}</div>')
        for p in perguntas:
            itens_html.append(f'<div class="ato-item">❓ {p}</div>')
        for c in compromissos_sug:
            itens_html.append(f'<div class="ato-item">✅ {c}</div>')
        if celebracao:
            itens_html.append(f'<div class="ato-item">🎉 {celebracao}</div>')

        conteudo = '\n'.join(itens_html) if itens_html else nome

        st.markdown(f"""
        <div class="ato-card" style="border-left-color:{cor};">
            <div class="ato-header">
                <span class="ato-titulo">Ato {i}: {nome}</span>
                <span class="ato-duracao">{duracao}</span>
            </div>
            {conteudo}
        </div>
        """, unsafe_allow_html=True)

        # Para exportacao
        pauta_texto_items.append(f"ATO {i} — {nome} ({duracao})")
        if o_que_dizer:
            pauta_texto_items.append(f'  "{o_que_dizer}"')
        for d in dados_mostrar:
            pauta_texto_items.append(f"  - {d}")
        for p in perguntas:
            pauta_texto_items.append(f"  ? {p}")
        for c in compromissos_sug:
            pauta_texto_items.append(f"  > {c}")
        if celebracao:
            pauta_texto_items.append(f"  * {celebracao}")
        pauta_texto_items.append("")

else:
    # ===== PATH DADOS REAIS =====
    if dados['tem_dados']:
        atos = _gerar_pauta_real(dados, semana, user_unit, nome_un, info)
    else:
        # Fallback minimo
        atos = [
            {'nome': 'Raizes', 'duracao': '5 min', 'cor': '#795548',
             'abertura': 'Check-in: como esta a energia da equipe?',
             'itens': ['Roda rapida de uma palavra.']},
            {'nome': 'Solo', 'duracao': '10 min', 'cor': '#8D6E63',
             'abertura': 'Dados da semana:',
             'itens': ['Sem dados carregados. Verifique se a extracao do SIGA foi executada.']},
            {'nome': 'Micelio', 'duracao': '10 min', 'cor': '#43A047',
             'abertura': 'Conexoes:',
             'itens': ['Quem precisa de ajuda?', 'Quem pode compartilhar uma boa pratica?']},
            {'nome': 'Sementes', 'duracao': '10 min', 'cor': '#66BB6A',
             'abertura': 'Compromissos:',
             'itens': ['1. ___', '2. ___', '3. ___']},
            {'nome': 'Chuva', 'duracao': '5 min', 'cor': '#29B6F6',
             'abertura': 'Celebracao:',
             'itens': ['Qual a melhor coisa da semana? NUNCA terminar com problema.']},
        ]

    pauta_texto_items = []
    for i, ato in enumerate(atos, 1):
        itens_html = f'<div class="ato-abertura">{ato["abertura"]}</div>'
        for item in ato['itens']:
            itens_html += f'<div class="ato-item">• {item}</div>'

        st.markdown(f"""
        <div class="ato-card" style="border-left-color:{ato['cor']};">
            <div class="ato-header">
                <span class="ato-titulo">Ato {i}: {ato['nome']}</span>
                <span class="ato-duracao">{ato['duracao']}</span>
            </div>
            {itens_html}
        </div>
        """, unsafe_allow_html=True)

        # Para exportacao
        pauta_texto_items.append(f"ATO {i} — {ato['nome']} ({ato['duracao']})")
        pauta_texto_items.append(f"  {ato['abertura']}")
        for item in ato['itens']:
            pauta_texto_items.append(f"  - {item}")
        pauta_texto_items.append("")

# Topicos adicionais do conselheiro (se existirem)
topicos = pauta_cons.get('topicos', [])
if topicos:
    st.markdown("---")
    st.markdown("### Topicos Adicionais (Conselheiro)")
    for t in topicos:
        st.markdown(f"- {t}")
    for t in topicos:
        pauta_texto_items.append(f"  + {t}")

# ========== NOTAS ==========

st.markdown("---")
st.markdown("### Notas da Reuniao")
notas = st.text_area(
    "Notas da reuniao",
    height=100,
    key="notas_peex_un",
    placeholder="Anote aqui o que foi discutido, decisoes tomadas, observacoes...",
    label_visibility="collapsed",
)

# ========== EXPORTAR ==========

st.markdown("---")
texto_export = [
    f"PAUTA PEEX — {nome_un} — Semana {semana}",
    f"Fase {info['fase_num']}: {fase['nome']} | {trimestre}o Trimestre",
]
if prox:
    texto_export.append(f"Reuniao: {prox.get('titulo', '')} ({fmt.get('nome', '')})")
texto_export.append("")

if dados['tem_dados']:
    texto_export.append(
        f"SAUDE: Conformidade {dados['conf']:.0f}% | "
        f"Frequencia {dados['freq']:.1f}% | "
        f"{dados['graves']} graves | "
        f"{dados.get('profs_criticos_n', len(dados['profs_criticos']))} profs criticos"
    )
    texto_export.append("")

texto_export.extend(pauta_texto_items)

if notas:
    texto_export.append("NOTAS:")
    texto_export.append(notas)

texto_export.append("---")
texto_export.append("PEEX Command Center — Colegio ELO 2026")

texto_final = '\n'.join(texto_export)

# Versao WhatsApp (sem markdown)
texto_whatsapp = texto_final.replace('**', '*').replace('### ', '').replace('## ', '')

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        "Baixar TXT",
        texto_final,
        file_name=f"pauta_peex_{user_unit}_sem{semana}.txt",
        mime="text/plain",
    )
with col2:
    st.download_button(
        "Copiar para WhatsApp",
        texto_whatsapp,
        file_name=f"pauta_whatsapp_{user_unit}_sem{semana}.txt",
        mime="text/plain",
    )
