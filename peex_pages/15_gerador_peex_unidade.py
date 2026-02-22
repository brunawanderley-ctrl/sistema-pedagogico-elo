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


import random
from datetime import date

# Banco de frases por etapa — rotaciona a cada dia/acesso
_FRASES = {
    'como_estamos': [
        "O dia começa com a decisão de fazer diferença.",
        "Sua presença muda o ambiente. Sua atencao muda os resultados.",
        "Grandes líderes começam o dia perguntando: como posso ajudar?",
        "A energia que você traz para a reunião define o tom da semana.",
        "Estar presente de verdade já é metade do caminho.",
        "Comece pelo que é possível. O extraordinário nasce do simples.",
        "Cada semana é uma página em branco. Você decide o que escrever.",
        "Liderar é cuidar. E cuidar começa por perguntar.",
    ],
    'raio_x': [
        "Dados são aliados, não julgamentos. Eles mostram onde agir.",
        "Quem conhece seus números toma decisões melhores.",
        "Os números contam uma história. Qual história a sua unidade está contando?",
        "Medir é o primeiro passo para transformar.",
        "Não existe gestão sem informação. Você já está à frente.",
        "Cada indicador é uma oportunidade disfarçada.",
        "Olhar os dados com coragem é o que separa gestão de rotina.",
        "A realidade não é obstáculo. É ponto de partida.",
    ],
    'quem_precisa': [
        "As melhores soluções nascem de quem está mais perto do problema.",
        "Pedir ajuda é sinal de inteligência, não de fraqueza.",
        "Uma equipe forte se constrói quando todos sabem que podem contar uns com os outros.",
        "Compartilhar uma boa prática multiplica o impacto de todo mundo.",
        "Quem já passou por isso pode encurtar o caminho de quem está passando agora.",
        "Colaboração não é dividir tarefas. É multiplicar capacidades.",
        "A resposta que você procura pode estar na sala ao lado.",
        "Conectar pessoas é o superpoder de um bom líder.",
    ],
    'o_que_vamos_fazer': [
        "Um bom plano executado hoje vale mais que um plano perfeito adiado.",
        "Compromisso com nome, ação e prazo. Sem isso, é só intenção.",
        "Foco: escolha 3 coisas e faça bem feito. Melhor que 10 pela metade.",
        "A diferença entre querer e fazer é uma decisão tomada agora.",
        "Cada ação concreta desta semana constrói o resultado do trimestre.",
        "Menos promessas, mais entregas. Comece pelo mais urgente.",
        "Não tente resolver tudo. Resolva o que mais importa.",
        "Ação imperfeita supera planejamento infinito.",
    ],
    'conquistas': [
        "Celebrar o progresso é o que nos mantém em movimento.",
        "Reconhecer o esforço da equipe não custa nada e vale tudo.",
        "Cada pequena vitória é prova de que estamos no caminho certo.",
        "Terminar com energia positiva é garantir que a próxima semana comece bem.",
        "O que você celebra hoje vira cultura amanhã.",
        "Gratidão transforma o clima de qualquer equipe.",
        "Antes de pensar no que falta, olhe para o que já conquistamos.",
        "O mérito é de quem faz acontecer no dia a dia.",
    ],
}


def _frase_do_dia(categoria):
    """Retorna frase rotativa baseada na data atual."""
    hoje = date.today()
    seed = hoje.toordinal() + hash(categoria) % 1000
    rng = random.Random(seed)
    return rng.choice(_FRASES[categoria])


def _gerar_pauta_real(dados, semana, unidade, nome_un, info):
    """Gera pauta de autogerencia com dados reais da unidade."""
    fase = info['fase']

    etapas = []

    # ===== 1. COMO ESTAMOS? =====
    if dados['conf'] >= 70 and dados['freq'] >= 85:
        frase_abertura = (
            f"Semana {semana}, {nome_un}. Os indicadores estao positivos — "
            f"vamos manter o ritmo e celebrar o que conquistamos."
        )
    elif dados['conf'] < 50 or dados['freq'] < 80:
        frase_abertura = (
            f"Semana {semana}, {nome_un}. Alguns indicadores pedem atencao "
            f"imediata — mas lembre: reconhecer o problema e o primeiro passo "
            f"para resolve-lo."
        )
    else:
        frase_abertura = (
            f"Semana {semana}, {nome_un}. Estamos evoluindo, mas ainda temos "
            f"espaco para crescer. Cada ajuste conta."
        )

    etapas.append({
        'nome': 'Como Estamos?',
        'cor': '#5C6BC0',
        'icone': '🤝',
        'frase': _frase_do_dia('como_estamos'),
        'itens': [
            "Roda rapida: em uma palavra, como voce esta chegando hoje?",
            frase_abertura,
        ],
    })

    # ===== 2. RAIO-X DA SEMANA =====
    itens_raio = []
    itens_raio.append(f"**Conformidade:** {dados['conf']:.0f}% (meta: 70%)")
    itens_raio.append(f"**Frequencia:** {dados['freq']:.1f}% (meta: 88%)")

    if dados['graves'] > 0:
        itens_raio.append(f"**Ocorrencias graves:** {dados['graves']}")
    if dados['alunos_risco_pct'] > 15:
        n_risco = int(dados['total_alunos'] * dados['alunos_risco_pct'] / 100)
        itens_raio.append(f"**Alunos em risco:** {dados['alunos_risco_pct']:.0f}% ({n_risco} alunos)")

    if dados['profs_criticos']:
        nomes = ', '.join(f"{p} ({c:.0f}%)" for p, c in dados['profs_criticos'][:3])
        itens_raio.append(f"**Professores que precisam de apoio:** {nomes}")
    elif dados.get('profs_criticos_n', 0) > 0:
        itens_raio.append(f"**Professores que precisam de apoio:** {dados['profs_criticos_n']}")

    if dados['turmas_graves']:
        turmas_txt = ', '.join(f"{t} ({n})" for t, n in dados['turmas_graves'])
        itens_raio.append(f"**Turmas que pedem atencao:** {turmas_txt}")

    # Frases positivas inline
    if dados['conf'] >= 70:
        itens_raio.append("✅ Parabens! Conformidade acima da meta. O trabalho esta aparecendo.")
    if dados['freq'] >= 88:
        itens_raio.append("✅ Frequencia acima da meta! Os alunos estao presentes.")
    if dados.get('profs_excelentes_n', len(dados.get('profs_excelentes', []))) > 0:
        if dados['profs_excelentes']:
            nomes_ex = ', '.join(p for p, _ in dados['profs_excelentes'])
            itens_raio.append(f"✅ Destaque: {nomes_ex} — acima de 85%. Reconheca!")
        else:
            itens_raio.append(f"✅ {dados.get('profs_excelentes_n', 0)} professores acima de 85%!")

    etapas.append({
        'nome': 'Raio-X da Semana',
        'cor': '#FF7043',
        'icone': '📊',
        'frase': _frase_do_dia('raio_x'),
        'itens': itens_raio,
    })

    # ===== 3. QUEM PRECISA DE QUEM? =====
    itens_rede = []

    if dados['profs_criticos']:
        itens_rede.append(
            f"Quem pode apoiar os {len(dados['profs_criticos'])} professores "
            f"com dificuldade? Um colega da mesma area pode fazer a diferenca."
        )
    if dados['turmas_graves']:
        turma_pior = dados['turmas_graves'][0][0]
        itens_rede.append(
            f"Turma {turma_pior}: o que esta acontecendo? "
            f"Quem conhece melhor essa turma?"
        )
    if dados['freq'] < 85:
        itens_rede.append(
            "Quais alunos estao se afastando? "
            "Quem na equipe pode ser a ponte com a familia?"
        )

    if not itens_rede:
        itens_rede = [
            "Alguem da equipe precisa de suporte esta semana?",
            "Quem tem uma boa pratica para compartilhar com os colegas?",
        ]

    itens_rede.append("Tem algum pedido de ajuda que ainda nao foi atendido?")

    etapas.append({
        'nome': 'Quem Precisa de Quem?',
        'cor': '#26A69A',
        'icone': '🤲',
        'frase': _frase_do_dia('quem_precisa'),
        'itens': itens_rede,
    })

    # ===== 4. O QUE VAMOS FAZER? =====
    compromissos = []

    if dados['profs_criticos']:
        n = len(dados['profs_criticos'])
        compromissos.append(
            f"Conversar individualmente com os {n} professores que "
            f"precisam de apoio — ate quarta-feira"
        )
    if dados['freq'] < 85:
        compromissos.append(
            "Busca ativa: ligar para as familias dos alunos "
            "com 3 ou mais faltas nesta semana"
        )
    if dados['turmas_graves']:
        turma_pior = dados['turmas_graves'][0][0]
        compromissos.append(
            f"Estar presente na turma {turma_pior} por 2 dias "
            f"consecutivos — observar e escutar antes de agir"
        )
    if dados.get('aulas_sem_conteudo', 0) > 5:
        compromissos.append(
            f"Apoiar os professores com {dados['aulas_sem_conteudo']} "
            f"registros sem conteudo — perguntar: precisa de ajuda?"
        )
    if dados['conf'] < 50:
        compromissos.append(
            "Conversa de 15 min com cada professor que nao registrou "
            "esta semana — ouvir primeiro, orientar depois"
        )

    if not compromissos:
        compromissos = [
            "Reconhecer publicamente 2 professores destaque da semana",
            "Revisar o plano de acao anterior — o que funcionou?",
            "Escolher 1 melhoria para testar na proxima semana",
        ]

    etapas.append({
        'nome': 'O Que Vamos Fazer?',
        'cor': '#FFA726',
        'icone': '🎯',
        'frase': _frase_do_dia('o_que_vamos_fazer'),
        'itens': compromissos[:5],
    })

    # ===== 5. NOSSAS CONQUISTAS =====
    itens_conquistas = []

    if dados['profs_excelentes']:
        nomes_ex = ', '.join(p for p, _ in dados['profs_excelentes'])
        itens_conquistas.append(
            f"Parabens, {nomes_ex}! Voces sao referencia esta semana. "
            f"O esforco de voces faz diferenca na vida dos alunos."
        )
    if dados['conf'] >= 60:
        itens_conquistas.append(
            f"Conformidade em {dados['conf']:.0f}% — cada ponto percentual "
            f"representa um professor que esta fazendo acontecer."
        )
    if dados['freq'] >= 88:
        itens_conquistas.append(
            f"Frequencia em {dados['freq']:.1f}% — acima da meta! "
            f"Alunos presentes sao alunos aprendendo."
        )
    if dados['graves'] == 0:
        itens_conquistas.append(
            "Zero ocorrencias graves esta semana. "
            "Isso e resultado de um ambiente bem cuidado."
        )

    if not itens_conquistas:
        itens_conquistas.append(
            "Qual foi a melhor coisa que aconteceu na nossa unidade esta semana? "
            "Vamos reconhecer antes de encerrar."
        )

    itens_conquistas.append(
        "Encerrar com energia positiva. "
        "O que voce vai levar de bom desta reuniao?"
    )

    etapas.append({
        'nome': 'Nossas Conquistas',
        'cor': '#AB47BC',
        'icone': '🏆',
        'frase': _frase_do_dia('conquistas'),
        'itens': itens_conquistas,
    })

    return etapas


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
        margin-bottom: 8px;
    }
    .ato-titulo { font-weight: bold; font-size: 1.1em; }
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

cabecalho_pagina("Minha Semana", "Autogerencia: seu roteiro para liderar a semana")

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
st.markdown("### Roteiro da Semana")

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
        etapas = _gerar_pauta_real(dados, semana, user_unit, nome_un, info)
    else:
        # Fallback minimo
        etapas = [
            {'nome': 'Como Estamos?', 'cor': '#5C6BC0',
             'icone': '🤝', 'frase': _frase_do_dia('como_estamos'),
             'itens': ['Roda rapida: em uma palavra, como voce esta chegando hoje?']},
            {'nome': 'Raio-X da Semana', 'cor': '#FF7043',
             'icone': '📊', 'frase': _frase_do_dia('raio_x'),
             'itens': ['Sem dados carregados. Verifique se a extracao do SIGA foi executada.']},
            {'nome': 'Quem Precisa de Quem?', 'cor': '#26A69A',
             'icone': '🤲', 'frase': _frase_do_dia('quem_precisa'),
             'itens': ['Quem precisa de ajuda?', 'Quem pode compartilhar uma boa pratica?']},
            {'nome': 'O Que Vamos Fazer?', 'cor': '#FFA726',
             'icone': '🎯', 'frase': _frase_do_dia('o_que_vamos_fazer'),
             'itens': ['1. ___', '2. ___', '3. ___']},
            {'nome': 'Nossas Conquistas', 'cor': '#AB47BC',
             'icone': '🏆', 'frase': _frase_do_dia('conquistas'),
             'itens': ['Qual a melhor coisa da semana?']},
        ]

    pauta_texto_items = []
    for i, etapa in enumerate(etapas, 1):
        icone = etapa.get('icone', '')
        frase = etapa.get('frase', '')

        itens_html = ''
        if frase:
            itens_html += (
                f'<div style="font-style:italic; color:#5C6BC0; '
                f'margin-bottom:8px; font-size:0.92em;">"{frase}"</div>'
            )
        for item in etapa['itens']:
            itens_html += f'<div class="ato-item">• {item}</div>'

        st.markdown(f"""
        <div class="ato-card" style="border-left-color:{etapa['cor']};">
            <div class="ato-header">
                <span class="ato-titulo">{icone} {etapa['nome']}</span>
            </div>
            {itens_html}
        </div>
        """, unsafe_allow_html=True)

        # Para exportacao
        pauta_texto_items.append(f"{icone} {etapa['nome']}")
        if frase:
            pauta_texto_items.append(f'  "{frase}"')
        for item in etapa['itens']:
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
st.markdown("### Minhas Reflexoes")
notas = st.text_area(
    "Minhas reflexoes",
    height=100,
    key="notas_peex_un",
    placeholder="O que aprendi esta semana? O que faria diferente? O que quero levar para a proxima...",
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
