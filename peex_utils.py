"""
Utilitarios PEEX — funcoes de conveniencia que consomem peex_config.py.
Wire central entre a configuracao PEEX e as paginas/engine.
"""

from peex_config import (
    FASES, fase_atual, EIXOS, INDICADORES_LEAD,
    REUNIOES, FORMATOS_REUNIAO, proxima_reuniao, reuniao_anterior, reunioes_do_trimestre,
    METAS_SMART, DIFERENCIACAO_UNIDADE, NIVEIS_ESCALACAO, MARCOS,
)


# ========== INFO DA SEMANA ==========

def info_semana(semana):
    """Retorna dict com fase, reuniao, metas ativas, marcos."""
    n_fase, fase = fase_atual(semana)
    prox = proxima_reuniao(semana)
    ant = reuniao_anterior(semana)
    formato = FORMATOS_REUNIAO.get(prox['formato'], {}) if prox else {}
    metas_fase = fase['prioridades']
    marcos_fase = MARCOS.get(n_fase, [])
    return {
        'fase_num': n_fase,
        'fase': fase,
        'proxima_reuniao': prox,
        'reuniao_anterior': ant,
        'formato_reuniao': formato,
        'metas': metas_fase,
        'marcos': marcos_fase,
        'diferenciacao': DIFERENCIACAO_UNIDADE,
    }


# ========== INDICE ELO (IE) ==========

# Pesos dos indicadores para o IE (0-100)
_PESOS_IE = {
    'pct_conformidade_media': 0.25,
    'frequencia_media': 0.20,
    'pct_prof_no_ritmo': 0.20,
    'pct_freq_acima_90': 0.15,
    'pct_alunos_risco': 0.10,      # inverso: menor = melhor
    'ocorr_graves': 0.10,           # inverso: menor = melhor
}

# Limites para normalizacao (valor minimo e maximo para escala 0-100)
_LIMITES_IE = {
    'pct_conformidade_media': (0, 100),
    'frequencia_media': (60, 100),
    'pct_prof_no_ritmo': (0, 100),
    'pct_freq_acima_90': (0, 100),
    'pct_alunos_risco': (0, 50),    # inverso
    'ocorr_graves': (0, 100),        # inverso
}


def calcular_indice_elo(resumo_row):
    """IE = soma ponderada de 6 indicadores, normalizada 0-100.

    Args:
        resumo_row: dict ou Series com campos do resumo_Executivo

    Returns:
        float 0-100
    """
    ie = 0.0
    for campo, peso in _PESOS_IE.items():
        val = resumo_row.get(campo, 0) if hasattr(resumo_row, 'get') else 0
        if val is None:
            val = 0
        vmin, vmax = _LIMITES_IE.get(campo, (0, 100))
        # Normalizar para 0-100
        if campo in ('pct_alunos_risco', 'ocorr_graves'):
            # Inverso: menor = melhor
            norm = max(0, min(100, (1 - (val - vmin) / max(vmax - vmin, 1)) * 100))
        else:
            norm = max(0, min(100, (val - vmin) / max(vmax - vmin, 1) * 100))
        ie += norm * peso
    return round(ie, 1)


# ========== ESTRELAS DE EVOLUCAO ==========

def calcular_estrelas(valor_atual, valor_anterior, meta, inverso=False):
    """0-3 estrelas por indicador baseado na evolucao.

    0: piorou ou estagnou 2+ semanas
    1: estavel (variacao <1pp)
    2: melhorou 1-3pp
    3: melhorou >3pp OU atingiu meta

    Args:
        valor_atual: valor atual do indicador
        valor_anterior: valor da semana anterior
        meta: meta do trimestre
        inverso: True se menor = melhor (ex: alunos_risco)

    Returns:
        int 0-3
    """
    if valor_atual is None or valor_anterior is None:
        return 0

    if inverso:
        delta = valor_anterior - valor_atual  # queda e positivo
        atingiu_meta = valor_atual <= meta
    else:
        delta = valor_atual - valor_anterior
        atingiu_meta = valor_atual >= meta

    if atingiu_meta:
        return 3
    if delta > 3:
        return 3
    if delta >= 1:
        return 2
    if abs(delta) < 1:
        return 1
    return 0


# ========== ESCALACAO ==========

def nivel_escalacao(semanas_ativas):
    """Retorna nivel de escalacao (1-4) baseado em semanas ativas.

    1 = Informar (2+ semanas)
    2 = Pedir apoio (3+ semanas)
    3 = Intervencao direta (4+ semanas)
    4 = Crise institucional (6+ semanas)
    """
    if semanas_ativas >= 6:
        return 4
    if semanas_ativas >= 4:
        return 3
    if semanas_ativas >= 3:
        return 2
    if semanas_ativas >= 2:
        return 1
    return 0


def info_escalacao(nivel):
    """Retorna dict do nivel de escalacao (nome, quando, acao, cor)."""
    if 1 <= nivel <= 4:
        return NIVEIS_ESCALACAO[nivel - 1]
    return None


# ========== ESTACOES (RAIZES) ==========

ESTACOES = {
    'plantio':       (1, 6,   'Acolhedor, orientador'),
    'crescimento':   (7, 20,  'Desafiador, motivador'),
    'dormencia':     (21, 27, 'Reflexivo, planejador'),
    'florescimento': (28, 38, 'Celebratorio, intenso'),
    'colheita':      (39, 47, 'Estrategico, prospectivo'),
}


def estacao_atual(semana):
    """Retorna (nome, tom) da estacao baseado na semana."""
    for nome, (ini, fim, tom) in ESTACOES.items():
        if ini <= semana <= fim:
            return nome, tom
    return 'colheita', 'Estrategico, prospectivo'


def ajustar_pesos_estacao(pesos_base, semana):
    """Ajusta pesos da formula de saude conforme estacao do ano.

    Args:
        pesos_base: dict {campo: peso} (ex: _PESOS_IE)
        semana: semana letiva

    Returns:
        dict com pesos ajustados
    """
    estacao, _ = estacao_atual(semana)
    ajustes = {
        'plantio': {'pct_conformidade_media': 1.2, 'frequencia_media': 0.8},
        'crescimento': {'pct_prof_no_ritmo': 1.3, 'pct_alunos_risco': 1.1},
        'dormencia': {'pct_conformidade_media': 0.9, 'frequencia_media': 0.9},
        'florescimento': {'pct_prof_no_ritmo': 1.2, 'ocorr_graves': 1.2},
        'colheita': {'pct_alunos_risco': 1.3, 'frequencia_media': 1.2},
    }
    multiplicadores = ajustes.get(estacao, {})
    resultado = dict(pesos_base)
    for campo, mult in multiplicadores.items():
        if campo in resultado:
            resultado[campo] = resultado[campo] * mult

    # Renormalizar para que soma = 1.0
    total = sum(resultado.values())
    if total > 0:
        resultado = {k: v / total for k, v in resultado.items()}

    return resultado


# ========== METAS SMART COM PROGRESSO ==========

def progresso_metas(resumo_row, fase_num):
    """Calcula progresso de cada meta SMART da fase.

    Args:
        resumo_row: dict ou Series com campos do resumo_Executivo (TOTAL)
        fase_num: 1, 2 ou 3

    Returns:
        lista de dicts: [{indicador, baseline, meta, atual, progresso_pct}, ...]
    """
    meta_key = {1: 'meta_tri1', 2: 'meta_tri2', 3: 'meta_ano'}
    key = meta_key.get(fase_num, 'meta_tri1')

    resultado = []
    for m in METAS_SMART:
        campo = m.get('campo_resumo', '')
        atual = resumo_row.get(campo, 0) if hasattr(resumo_row, 'get') else 0
        if atual is None:
            atual = 0
        baseline = m['baseline']
        meta = m.get(key, m.get('meta_ano', 0))
        inverso = m.get('inverso', False)

        if inverso:
            # Menor = melhor: progresso inverso
            total_range = baseline - meta
            if total_range != 0:
                progresso = (baseline - atual) / total_range * 100
            else:
                progresso = 100 if atual <= meta else 0
        else:
            total_range = meta - baseline
            if total_range != 0:
                progresso = (atual - baseline) / total_range * 100
            else:
                progresso = 100 if atual >= meta else 0

        progresso = max(0, min(100, progresso))

        resultado.append({
            'eixo': m['eixo'],
            'indicador': m['indicador'],
            'baseline': baseline,
            'meta': meta,
            'atual': round(atual, 1) if isinstance(atual, float) else atual,
            'progresso_pct': round(progresso, 0),
            'unidade_medida': m.get('unidade', ''),
            'inverso': inverso,
        })

    return resultado


# ========== PROXIMAS REUNIOES ==========

def proximas_reunioes(semana, n=3):
    """Retorna as proximas N reunioes a partir da semana."""
    futuras = [r for r in REUNIOES if r['semana'] >= semana]
    resultado = []
    for r in futuras[:n]:
        fmt = FORMATOS_REUNIAO.get(r['formato'], {})
        resultado.append({
            **r,
            'formato_nome': fmt.get('nome', r['formato']),
            'formato_duracao': fmt.get('duracao', 30),
            'formato_cor': fmt.get('cor', '#607D8B'),
            'formato_icone': fmt.get('icone', '📅'),
        })
    return resultado
