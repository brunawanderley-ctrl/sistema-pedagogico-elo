"""
Estrelas de Evolucao — competicao por melhoria, nao por posicao.
5 indicadores x 0-3 estrelas = max 15/semana. Acumulativo por trimestre.

Funcoes publicas:
  - calcular_estrelas_semana(resumo_atual, resumo_anterior, metas)
  - acumular_estrelas_trimestre(semana)
  - ranking_evolucao()
  - ranking_saude()
  - ranking_generosidade()
"""

import json
from pathlib import Path
from datetime import datetime

from utils import WRITABLE_DIR, UNIDADES_NOMES
from peex_utils import calcular_estrelas as _calc_estrela_indicador

_ESTRELAS_PATH = WRITABLE_DIR / "estrelas_historico.json"
_GENEROSIDADE_PATH = WRITABLE_DIR / "generosidade.json"

# 5 indicadores para estrelas
INDICADORES_ESTRELAS = [
    {'campo': 'pct_conformidade_media', 'nome': 'Conformidade', 'inverso': False},
    {'campo': 'frequencia_media', 'nome': 'Frequencia', 'inverso': False},
    {'campo': 'pct_prof_no_ritmo', 'nome': 'Ritmo SAE', 'inverso': False},
    {'campo': 'pct_alunos_risco', 'nome': 'Alunos Risco', 'inverso': True},
    {'campo': 'ocorr_graves', 'nome': 'Ocorrencias', 'inverso': True},
]

# Metas por trimestre
_METAS_TRI = {
    1: {'pct_conformidade_media': 70, 'frequencia_media': 88, 'pct_prof_no_ritmo': 35,
        'pct_alunos_risco': 15, 'ocorr_graves': 26},
    2: {'pct_conformidade_media': 78, 'frequencia_media': 89, 'pct_prof_no_ritmo': 55,
        'pct_alunos_risco': 12, 'ocorr_graves': 13},
    3: {'pct_conformidade_media': 80, 'frequencia_media': 90, 'pct_prof_no_ritmo': 65,
        'pct_alunos_risco': 10, 'ocorr_graves': 20},
}


def _carregar_estrelas():
    if _ESTRELAS_PATH.exists():
        try:
            with open(_ESTRELAS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def _salvar_estrelas(data):
    with open(_ESTRELAS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def calcular_estrelas_semana(resumo_atual, resumo_anterior, trimestre=1):
    """Calcula estrelas da semana para cada unidade.

    Args:
        resumo_atual: DataFrame do resumo_Executivo (semana atual)
        resumo_anterior: DataFrame do resumo_Executivo (semana anterior)
        trimestre: 1, 2 ou 3

    Returns:
        dict {unidade: {indicador: estrelas, total: N}}
    """
    metas = _METAS_TRI.get(trimestre, _METAS_TRI[1])
    resultado = {}

    for un_code in ['BV', 'CD', 'JG', 'CDR']:
        row_atual = resumo_atual[resumo_atual['unidade'] == un_code]
        row_ant = resumo_anterior[resumo_anterior['unidade'] == un_code] if not resumo_anterior.empty else None

        estrelas_un = {}
        total = 0

        for ind in INDICADORES_ESTRELAS:
            campo = ind['campo']
            val_atual = float(row_atual.iloc[0].get(campo, 0)) if not row_atual.empty else 0
            val_ant = float(row_ant.iloc[0].get(campo, val_atual)) if row_ant is not None and not row_ant.empty else val_atual
            meta = metas.get(campo, 0)

            n_estrelas = _calc_estrela_indicador(val_atual, val_ant, meta, ind['inverso'])
            estrelas_un[ind['nome']] = n_estrelas
            total += n_estrelas

        estrelas_un['total'] = total
        resultado[un_code] = estrelas_un

    return resultado


def registrar_estrelas_semana(semana, estrelas_semana):
    """Persiste estrelas da semana no historico."""
    historico = _carregar_estrelas()
    key = str(semana)
    historico[key] = {
        'semana': semana,
        'data': datetime.now().isoformat(),
        'unidades': estrelas_semana,
    }
    _salvar_estrelas(historico)


def acumular_estrelas_trimestre(semana_atual, trimestre=1):
    """Acumula estrelas no trimestre (nunca perde).

    Returns:
        dict {unidade: {indicador: total_estrelas, total: N}}
    """
    from utils import calcular_trimestre
    historico = _carregar_estrelas()

    # Determinar range de semanas do trimestre
    ranges = {1: (1, 15), 2: (16, 33), 3: (34, 47)}
    ini, fim = ranges.get(trimestre, (1, 47))

    acumulado = {}
    for un_code in ['BV', 'CD', 'JG', 'CDR']:
        acc = {ind['nome']: 0 for ind in INDICADORES_ESTRELAS}
        acc['total'] = 0

        for key, entry in historico.items():
            sem = entry.get('semana', 0)
            if ini <= sem <= fim:
                un_data = entry.get('unidades', {}).get(un_code, {})
                for ind in INDICADORES_ESTRELAS:
                    acc[ind['nome']] += un_data.get(ind['nome'], 0)
                acc['total'] += un_data.get('total', 0)

        acumulado[un_code] = acc

    return acumulado


def ranking_evolucao():
    """Ranking por total de estrelas acumuladas (trimestre atual).

    Returns:
        lista de dicts [{unidade, nome, total, posicao}, ...] ordenado desc
    """
    from utils import calcular_semana_letiva, calcular_trimestre
    semana = calcular_semana_letiva()
    tri = calcular_trimestre(semana)
    acumulado = acumular_estrelas_trimestre(semana, tri)

    ranking = []
    for un_code, data in acumulado.items():
        ranking.append({
            'unidade': un_code,
            'nome': UNIDADES_NOMES.get(un_code, un_code),
            'total': data['total'],
            'detalhes': {k: v for k, v in data.items() if k != 'total'},
        })

    ranking.sort(key=lambda x: x['total'], reverse=True)
    for i, r in enumerate(ranking, 1):
        r['posicao'] = i

    return ranking


def ranking_saude(resumo_df):
    """Ranking por indice de saude (conformidade + frequencia ponderados).

    Returns:
        lista de dicts [{unidade, nome, score, posicao}, ...]
    """
    from peex_utils import calcular_indice_elo

    ranking = []
    for un_code in ['BV', 'CD', 'JG', 'CDR']:
        row = resumo_df[resumo_df['unidade'] == un_code]
        if not row.empty:
            ie = calcular_indice_elo(row.iloc[0])
        else:
            ie = 0
        ranking.append({
            'unidade': un_code,
            'nome': UNIDADES_NOMES.get(un_code, un_code),
            'score': ie,
        })

    ranking.sort(key=lambda x: x['score'], reverse=True)
    for i, r in enumerate(ranking, 1):
        r['posicao'] = i

    return ranking


# ========== GENEROSIDADE ==========

def _carregar_generosidade():
    if _GENEROSIDADE_PATH.exists():
        try:
            with open(_GENEROSIDADE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def _salvar_generosidade(data):
    with open(_GENEROSIDADE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Tabela de pontos de generosidade (RAIZES)
PONTOS_GENEROSIDADE = {
    'visita': {'pontos': 15, 'descricao': 'Visita a outra unidade'},
    'pareamento_resultado': {'pontos': 10, 'descricao': 'Pareamento com resultado positivo'},
    'pratica_compartilhada': {'pontos': 5, 'descricao': 'Pratica compartilhada no feed'},
    'material_compartilhado': {'pontos': 3, 'descricao': 'Material didatico compartilhado'},
    'mentoria_ativa': {'pontos': 8, 'descricao': 'Mentoria ativa entre professores'},
    'adocao_pratica': {'pontos': 4, 'descricao': 'Adotou pratica de outra unidade'},
    'feedback_construtivo': {'pontos': 2, 'descricao': 'Feedback construtivo registrado'},
}


def registrar_generosidade(unidade, tipo, pontos=None, descricao=""):
    """Registra acao de generosidade.

    Args:
        unidade: codigo da unidade
        tipo: chave de PONTOS_GENEROSIDADE ou tipo livre
        pontos: pontos a atribuir (se None, usa tabela)
        descricao: descricao livre da acao
    """
    if pontos is None:
        pontos = PONTOS_GENEROSIDADE.get(tipo, {}).get('pontos', 1)
    gen = _carregar_generosidade()
    if unidade not in gen:
        gen[unidade] = {'total': 0, 'acoes': []}

    gen[unidade]['acoes'].append({
        'tipo': tipo,
        'pontos': pontos,
        'descricao': descricao,
        'data': datetime.now().isoformat(),
    })
    gen[unidade]['total'] += pontos
    _salvar_generosidade(gen)


def ranking_generosidade():
    """Ranking por pontos de generosidade.

    Returns:
        lista de dicts [{unidade, nome, total, posicao}, ...]
    """
    gen = _carregar_generosidade()
    ranking = []
    for un_code in ['BV', 'CD', 'JG', 'CDR']:
        data = gen.get(un_code, {'total': 0})
        ranking.append({
            'unidade': un_code,
            'nome': UNIDADES_NOMES.get(un_code, un_code),
            'total': data.get('total', 0),
        })

    ranking.sort(key=lambda x: x['total'], reverse=True)
    for i, r in enumerate(ranking, 1):
        r['posicao'] = i

    return ranking
