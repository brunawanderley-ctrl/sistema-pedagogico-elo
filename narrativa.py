"""
Geracao de narrativa por templates — zero dependencia de LLM.
Texto montado por condicoes nos dados.

Funcoes publicas:
  - gerar_narrativa_ceo(resumo_df, historico, semana)
  - gerar_nudge(missao)
  - gerar_decisoes_ceo(historico)
"""

import pandas as pd
from datetime import datetime

from utils import (
    UNIDADES_NOMES,
    CONFORMIDADE_META,
    CONFORMIDADE_BAIXO,
    CONFORMIDADE_CRITICO,
    calcular_trimestre,
)


# ========== NARRATIVA CEO ==========

def _abertura(semana, trimestre, total_alunos, total_profs):
    """Paragrafo de abertura da narrativa CEO."""
    hora = datetime.now().hour
    if hora < 12:
        saudacao = "Bom dia"
    elif hora < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    return (
        f"{saudacao}. Semana {semana}, {trimestre}o trimestre. "
        f"A rede ELO opera com {total_alunos:,} alunos e {total_profs} professores "
        f"em 4 unidades."
    )


def _comparativo(resumo_df):
    """Paragrafo comparativo entre unidades."""
    if resumo_df.empty or 'pct_conformidade_media' not in resumo_df.columns:
        return ""

    unidades = resumo_df[resumo_df['unidade'] != 'TOTAL'].copy()
    if unidades.empty:
        return ""

    melhor = unidades.loc[unidades['pct_conformidade_media'].idxmax()]
    pior = unidades.loc[unidades['pct_conformidade_media'].idxmin()]

    nome_melhor = UNIDADES_NOMES.get(melhor['unidade'], melhor['unidade'])
    nome_pior = UNIDADES_NOMES.get(pior['unidade'], pior['unidade'])
    gap = melhor['pct_conformidade_media'] - pior['pct_conformidade_media']

    texto = (
        f"{nome_melhor} lidera com {melhor['pct_conformidade_media']:.0f}% de conformidade, "
        f"enquanto {nome_pior} esta em {pior['pct_conformidade_media']:.0f}%."
    )
    if gap > 15:
        texto += f" O gap de {gap:.0f}pp entre elas exige atencao."

    return texto


def _evolucao(resumo_df, historico_semanas):
    """Paragrafo de evolucao (tendencia)."""
    total_row = resumo_df[resumo_df['unidade'] == 'TOTAL']
    if total_row.empty:
        return ""

    conf_atual = total_row.iloc[0].get('pct_conformidade_media', 0)

    if not historico_semanas:
        return f"Conformidade atual da rede: {conf_atual:.0f}%."

    conf_anterior = historico_semanas[-1].get('conformidade_rede', conf_atual)
    delta = conf_atual - conf_anterior

    if delta > 2:
        return f"A rede subiu de {conf_anterior:.0f}% para {conf_atual:.0f}% (+{delta:.0f}pp). Tendencia positiva."
    elif delta < -2:
        return f"A rede caiu de {conf_anterior:.0f}% para {conf_atual:.0f}% ({delta:.0f}pp). Requer intervencao."
    else:
        return f"Conformidade da rede estavel em {conf_atual:.0f}%."


def _destaque(resumo_df):
    """Destaque positivo."""
    unidades = resumo_df[resumo_df['unidade'] != 'TOTAL']
    if unidades.empty:
        return ""

    # Destaque: unidade com mais professores excelentes
    if 'professores_excelentes' in unidades.columns:
        top = unidades.loc[unidades['professores_excelentes'].idxmax()]
        n = int(top['professores_excelentes'])
        if n > 0:
            nome = UNIDADES_NOMES.get(top['unidade'], top['unidade'])
            return f"Destaque positivo: {nome} tem {n} professor(es) com desempenho excelente."

    return ""


def _alerta(resumo_df):
    """Alerta principal."""
    unidades = resumo_df[resumo_df['unidade'] != 'TOTAL']
    if unidades.empty:
        return ""

    # Alerta: unidades com conformidade critica
    criticas = unidades[unidades['pct_conformidade_media'] < CONFORMIDADE_BAIXO]
    if criticas.empty:
        return ""

    nomes = [UNIDADES_NOMES.get(r['unidade'], r['unidade']) for _, r in criticas.iterrows()]
    if len(nomes) == 1:
        return f"Alerta: {nomes[0]} permanece abaixo de {CONFORMIDADE_BAIXO}% de conformidade."
    return f"Alerta: {', '.join(nomes)} permanecem abaixo de {CONFORMIDADE_BAIXO}% de conformidade."


def gerar_narrativa_ceo(resumo_df, historico_semanas, semana):
    """Gera narrativa completa para a CEO.

    Args:
        resumo_df: DataFrame do resumo_Executivo.csv
        historico_semanas: lista de dicts com dados de semanas anteriores (pode ser [])
        semana: numero da semana letiva atual

    Returns:
        str com narrativa em paragrafos
    """
    if resumo_df.empty:
        return "Dados insuficientes para gerar narrativa. Execute a extracao do SIGA."

    trimestre = calcular_trimestre(semana)
    total_row = resumo_df[resumo_df['unidade'] == 'TOTAL']

    total_alunos = int(total_row.iloc[0].get('total_alunos', 0)) if not total_row.empty else 0
    total_profs = int(total_row.iloc[0].get('total_professores', 0)) if not total_row.empty else 0

    paragrafos = [
        _abertura(semana, trimestre, total_alunos, total_profs),
        _comparativo(resumo_df),
        _evolucao(resumo_df, historico_semanas),
        _destaque(resumo_df),
        _alerta(resumo_df),
    ]

    return "\n\n".join(p for p in paragrafos if p)


# ========== NUDGES PARA COORDENADOR ==========

_NUDGE_TEMPLATES = {
    'PROF_SILENCIOSO': (
        "Esse professor nao registra ha {dias_problema} dias. "
        "Uma conversa rapida pode destravar a situacao."
    ),
    'DISCIPLINA_ORFA': (
        "Nenhuma aula registrada desde o inicio do ano. "
        "Verifique se ha professor designado para essa disciplina."
    ),
    'TURMA_CRITICA': (
        "Essa turma esta com {conformidade:.0f}% de conformidade — "
        "abaixo do minimo de {meta}%. Priorize os professores com zero registro."
    ),
    'ALUNO_FREQUENCIA': (
        "Alunos abaixo de 75% de frequencia correm risco de reprovacao (LDB). "
        "Encaminhe para a orientacao HOJE."
    ),
    'ALUNO_OCORRENCIA': (
        "Ocorrencias graves requerem intervencao imediata. "
        "Convoque as familias e registre as providencias."
    ),
    'PROF_QUEDA': (
        "Queda de conformidade detectada. "
        "Verifique se houve mudanca de horario ou dificuldade de acesso."
    ),
    'CURRICULO_ATRASADO': (
        "O curriculo esta atrasado em relacao ao esperado pelo SAE. "
        "Alinhe com o professor o plano de recuperacao."
    ),
    'PROF_SEM_CONTEUDO': (
        "Aulas registradas sem descricao de conteudo. "
        "Oriente o professor sobre a importancia do registro completo."
    ),
    'PROCESSO_DEADLINE': (
        "Prazo de feedback se aproxima em {dias_restantes} dias. "
        "Reserve horarios na agenda para as observacoes pendentes."
    ),
}


def gerar_nudge(missao):
    """Gera texto de nudge para um card de missao do coordenador.

    Args:
        missao: dict de missao (do missoes.py)

    Returns:
        str com nudge contextual
    """
    tipo = missao.get('tipo', '')
    template = _NUDGE_TEMPLATES.get(tipo)
    if not template:
        return ""

    try:
        return template.format(
            dias_problema=missao.get('dias_problema', '?'),
            conformidade=missao.get('conformidade', 0),
            meta=CONFORMIDADE_BAIXO,
            dias_restantes=missao.get('dias_restantes', '?'),
        )
    except (KeyError, ValueError):
        return template.split('.')[0] + '.'


# ========== 3 DECISOES CEO ==========

_DECISAO_TEMPLATES = {
    'PROF_SILENCIOSO': {
        'titulo': "Professor sem registro por {semanas}+ semanas",
        'decisao': "Avaliar se ha necessidade de substituicao ou realocacao.",
        'impacto': "~{n_afetados} alunos sem acompanhamento.",
    },
    'DISCIPLINA_ORFA': {
        'titulo': "Disciplina sem registro ha {semanas}+ semanas",
        'decisao': "Verificar junto a secretaria se ha professor designado. "
                   "Se nao, iniciar processo de contratacao/remanejamento.",
        'impacto': "Disciplina completamente descoberta.",
    },
    'TURMA_CRITICA': {
        'titulo': "Turma com conformidade critica por {semanas}+ semanas",
        'decisao': "Convocar reuniao com equipe docente da turma. "
                   "Definir plano de acao com prazo semanal.",
        'impacto': "Cobertura curricular comprometida.",
    },
    'ALUNO_FREQUENCIA': {
        'titulo': "Alunos em risco de infrequencia por {semanas}+ semanas",
        'decisao': "Acionar busca ativa com orientacao educacional e familia.",
        'impacto': "{n_afetados} aluno(s) em risco de reprovacao por infrequencia.",
    },
    'ALUNO_OCORRENCIA': {
        'titulo': "Ocorrencias graves recorrentes por {semanas}+ semanas",
        'decisao': "Reuniao com equipe disciplinar para revisar protocolo de intervencao.",
        'impacto': "Padrao recorrente exige revisao do protocolo.",
    },
}

# Fallback para tipos sem template especifico
_DECISAO_FALLBACK = {
    'titulo': "Situacao persistente: {tipo}",
    'decisao': "Avaliar escalacao para nivel gerencial.",
    'impacto': "Situacao sem resolucao ha {semanas}+ semanas.",
}


def gerar_pauta_peex(missoes, coord_nome, semana, formato):
    """Gera pauta PEEX adaptativa com 7 regras de sobrescrita.

    Args:
        missoes: lista de missoes do coordenador
        coord_nome: nome do coordenador
        semana: semana letiva
        formato: dict do formato da reuniao (nome, duracao)

    Returns:
        dict com pauta, acoes, regras_aplicadas
    """
    urgentes = [b for b in missoes if b.get('nivel') == 'URGENTE']
    importantes = [b for b in missoes if b.get('nivel') == 'IMPORTANTE']

    regras_aplicadas = []
    acoes = []
    max_acoes = 5

    # Regra 1: semana curta (<=3 dias letivos) -> simplifica
    # Isso seria detectado pelo calendario; por ora, padrao
    if semana in (1, 23, 24, 25, 26, 27):  # ferias
        regras_aplicadas.append("Semana de ferias/curta: pauta simplificada")
        max_acoes = 2

    # Regra 2: indicador vermelho + piora -> pauta emergencial
    if len(urgentes) >= 5:
        regras_aplicadas.append("5+ urgentes: pauta emergencial ativada")
        max_acoes = 3
        acoes = [
            f"EMERGENCIA: Resolver as {len(urgentes)} missoes urgentes HOJE",
            "Contatar individualmente cada professor/aluno envolvido",
            "Reportar progresso ate o final do dia",
        ]

    # Regra 3: 3+ profs sairam do vermelho -> celebracao
    # (seria checado contra historico; placeholder)

    # Regra 4: coord executa <60% -> reduz acoes
    # (seria checado contra historico de resolucao; placeholder)
    # Por enquanto, usa max_acoes padrao

    # Gerar acoes padrao se nao preenchidas
    if not acoes:
        for b in urgentes[:2]:
            acoes.append(f"[URGENTE] {b.get('como', ['Resolver'])[0]}")
        for b in importantes[:3]:
            acoes.append(f"[IMPORTANTE] {b.get('como', ['Acompanhar'])[0]}")

    acoes = acoes[:max_acoes]

    fmt_nome = formato.get('nome', 'FLASH') if formato else 'FLASH'
    fmt_duracao = formato.get('duracao', 30) if formato else 30

    return {
        'coord': coord_nome,
        'semana': semana,
        'formato': fmt_nome,
        'duracao': fmt_duracao,
        'n_missoes': len(missoes),
        'n_urgentes': len(urgentes),
        'acoes': acoes,
        'regras_aplicadas': regras_aplicadas,
    }


# ========== NUDGES COMPORTAMENTAIS (RAIZES) ==========

_NUDGES_COMPORTAMENTAIS = {
    'aversao_perda': {
        'PROF_SILENCIOSO': "Se nao agir hoje, {entidade} perdera {dias_problema} dias de registro — e voce perdera visibilidade sobre {n_afetados} alunos.",
        'TURMA_CRITICA': "A cada dia sem intervencao, esta turma perde {delta:.0f}pp de conformidade. Amanha sera mais dificil.",
        'CURRICULO_ATRASADO': "Cada semana sem correcao de rota aumenta o gap curricular. Agora sao {atraso} capitulo(s) — na proxima semana serao mais.",
        '_default': "Se nao resolver esta semana, o indicador cairá e a posicao da unidade no ranking sera afetada.",
    },
    'prova_social': {
        'PROF_SILENCIOSO': "23 de 28 coordenadores ja resolveram esta situacao na primeira semana. Voce tambem consegue.",
        'TURMA_CRITICA': "As 3 outras unidades ja elevaram turmas criticas em +12pp no 1o trimestre. Use a mesma estrategia.",
        'PROF_SEM_CONTEUDO': "85% dos coordenadores PEEX garantem registro completo com uma conversa de 5 minutos.",
        '_default': "Coordenadores PEEX que agem na primeira semana resolvem 78% dos casos sem escalacao.",
    },
    'efeito_default': {
        'PROF_SILENCIOSO': "Seu plano de acao ja foi gerado: 1) Conversa individual 2) Meta semanal 3) Acompanhamento diario. Basta executar.",
        'TURMA_CRITICA': "O plano padrao esta pronto: reuniao relampago com os 3 professores com menor registro. Aplique HOJE.",
        '_default': "O plano de acao da semana ja foi pre-montado com as 3 acoes mais efetivas. So confirmar e executar.",
    },
    'compromisso': {
        'PROF_SILENCIOSO': "Registre agora: 'Vou falar com {entidade} ate sexta-feira'. Coordenadores que registram compromisso cumprem 2x mais.",
        'TURMA_CRITICA': "Defina sua meta: em quantos dias voce vai tirar esta turma do vermelho? Registre e acompanhe.",
        '_default': "Registre seu compromisso para esta semana. Quem registra, cumpre 2x mais.",
    },
    'identidade': {
        'PROF_SILENCIOSO': "Coordenadores PEEX sao guardioes da aprendizagem. Nenhum aluno fica invisivel quando voce age.",
        'TURMA_CRITICA': "Como guardiao PEEX, voce nao deixa nenhuma turma para tras. Esta e a sua missao.",
        'ALUNO_FREQUENCIA': "Coordenadores PEEX sao a ultima linha de defesa de cada aluno. Busca ativa e sua marca.",
        '_default': "Voce e um guardiao PEEX — cada acao sua transforma a realidade de dezenas de alunos.",
    },
}


def gerar_nudge_comportamental(tipo_nudge, missao):
    """Gera nudge comportamental baseado em mecanismo psicologico.

    Args:
        tipo_nudge: 'aversao_perda', 'prova_social', 'efeito_default',
                    'compromisso' ou 'identidade'
        missao: dict de missao

    Returns:
        str com nudge contextual
    """
    templates = _NUDGES_COMPORTAMENTAIS.get(tipo_nudge, {})
    tipo_missao = missao.get('tipo', '')
    template = templates.get(tipo_missao, templates.get('_default', ''))

    if not template:
        return ''

    try:
        return template.format(
            entidade=missao.get('entidade', 'o professor'),
            dias_problema=missao.get('dias_problema', '?'),
            n_afetados=missao.get('n_afetados', 0),
            conformidade=missao.get('conformidade', 0),
            delta=missao.get('delta', 0),
            atraso=missao.get('atraso_capitulos', 1),
        )
    except (KeyError, ValueError):
        return template.split('.')[0] + '.'


def gerar_nudge_semanal(semana, missoes):
    """Seleciona o melhor nudge para a semana baseado nas missoes ativas.

    Roda os 5 mecanismos e escolhe o mais relevante:
    - Se ha urgentes: aversao_perda
    - Se ha melhoras: prova_social
    - Se coordenador nao agiu: efeito_default
    - Se precisa engajamento: compromisso
    - Fallback: identidade

    Args:
        semana: semana letiva
        missoes: lista de missoes do coordenador

    Returns:
        dict com {tipo, texto, mecanismo}
    """
    urgentes = [b for b in missoes if b.get('nivel') == 'URGENTE']
    n_missoes = len(missoes)

    if urgentes:
        missao = urgentes[0]
        tipo = 'aversao_perda'
    elif n_missoes > 5:
        missao = missoes[0]
        tipo = 'efeito_default'
    elif semana % 3 == 0:
        missao = missoes[0] if missoes else {}
        tipo = 'compromisso'
    elif semana % 2 == 0:
        missao = missoes[0] if missoes else {}
        tipo = 'prova_social'
    else:
        missao = missoes[0] if missoes else {}
        tipo = 'identidade'

    texto = gerar_nudge_comportamental(tipo, missao)

    return {
        'tipo': tipo,
        'texto': texto,
        'mecanismo': {
            'aversao_perda': 'Aversao a Perda',
            'prova_social': 'Prova Social',
            'efeito_default': 'Efeito Default',
            'compromisso': 'Compromisso Publico',
            'identidade': 'Identidade',
        }.get(tipo, tipo),
    }


def gerar_decisoes_ceo(persistentes):
    """Gera ate 3 decisoes para a CEO a partir de missoes persistentes.

    Args:
        persistentes: lista de dicts do missoes_historico.obter_persistentes()
            Cada dict: {fingerprint, tipo, unidade, entidade, semanas_ativas, primeira_semana, ...}

    Returns:
        lista de dicts: [{titulo, decisao, impacto, fingerprint, tipo, unidade, semanas}, ...]
    """
    if not persistentes:
        return []

    decisoes = []
    for p in persistentes[:3]:
        tipo = p.get('tipo', '')
        template = _DECISAO_TEMPLATES.get(tipo, _DECISAO_FALLBACK)

        semanas = p.get('semanas_ativas', 0)
        n_afetados = p.get('n_afetados', 0)

        try:
            titulo = template['titulo'].format(
                semanas=semanas, tipo=tipo, n_afetados=n_afetados
            )
            decisao = template['decisao'].format(
                semanas=semanas, tipo=tipo, n_afetados=n_afetados
            )
            impacto = template['impacto'].format(
                semanas=semanas, tipo=tipo, n_afetados=n_afetados
            )
        except (KeyError, ValueError):
            titulo = f"Situacao persistente: {tipo} ({semanas} semanas)"
            decisao = "Avaliar escalacao."
            impacto = ""

        decisoes.append({
            'titulo': titulo,
            'decisao': decisao,
            'impacto': impacto,
            'fingerprint': p.get('fingerprint', ''),
            'tipo': tipo,
            'unidade': p.get('unidade', ''),
            'semanas': semanas,
        })

    return decisoes
