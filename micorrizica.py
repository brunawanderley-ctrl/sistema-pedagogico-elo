"""
Rede Micorrizica — pareamento automatico de professores.
Sugere pares de professores para troca de praticas baseado em complementaridade.

Criterios de peso:
  - Mesma disciplina (30%)
  - Mesma serie (25%)
  - Padrao temporal similar (20%)
  - Unidades diferentes (15%)
  - Complementaridade de score (10%)

Funcoes publicas:
  - gerar_pareamentos(resumo_profs_df)
  - sugerir_pares(professor_id, resumo_profs_df, n=3)
"""

import json
from pathlib import Path
from datetime import datetime
from itertools import combinations

from utils import WRITABLE_DIR, UNIDADES_NOMES

_PAREAMENTOS_PATH = WRITABLE_DIR / "pareamentos_micorrizica.json"

# Pesos dos criterios
_PESO_DISCIPLINA = 0.30
_PESO_SERIE = 0.25
_PESO_TEMPORAL = 0.20
_PESO_UNIDADE_DIFF = 0.15
_PESO_COMPLEMENTAR = 0.10


def _score_pareamento(prof_a, prof_b):
    """Calcula score de pareamento entre dois professores (0-100).

    Args:
        prof_a, prof_b: dicts com campos: professor, disciplina, serie,
            unidade, conformidade, score, total_aulas

    Returns:
        float 0-100
    """
    score = 0.0

    # 1. Mesma disciplina (30%)
    disc_a = prof_a.get('disciplina', '').strip().lower()
    disc_b = prof_b.get('disciplina', '').strip().lower()
    if disc_a and disc_b and disc_a == disc_b:
        score += _PESO_DISCIPLINA * 100

    # 2. Mesma serie (25%)
    serie_a = prof_a.get('serie', '')
    serie_b = prof_b.get('serie', '')
    if serie_a and serie_b and serie_a == serie_b:
        score += _PESO_SERIE * 100

    # 3. Padrao temporal similar (20%)
    # Proxy: diferenca de total_aulas — quanto mais similar, maior score
    aulas_a = prof_a.get('total_aulas', 0)
    aulas_b = prof_b.get('total_aulas', 0)
    max_aulas = max(aulas_a, aulas_b, 1)
    sim_temporal = 1 - abs(aulas_a - aulas_b) / max_aulas
    score += _PESO_TEMPORAL * sim_temporal * 100

    # 4. Unidades diferentes (15%) — incentiva troca cross-unit
    un_a = prof_a.get('unidade', '')
    un_b = prof_b.get('unidade', '')
    if un_a and un_b and un_a != un_b:
        score += _PESO_UNIDADE_DIFF * 100

    # 5. Complementaridade de score (10%)
    # Um forte + um fraco = bom pareamento para mentoria
    conf_a = prof_a.get('conformidade', 50)
    conf_b = prof_b.get('conformidade', 50)
    diff_conf = abs(conf_a - conf_b)
    # Ideal: diferenca 20-40pp (um pode mentorar o outro)
    if 20 <= diff_conf <= 40:
        score += _PESO_COMPLEMENTAR * 100
    elif 10 <= diff_conf < 20:
        score += _PESO_COMPLEMENTAR * 60

    return round(score, 1)


def _tipo_pareamento(prof_a, prof_b):
    """Determina o tipo de pareamento.

    Returns:
        str: 'mentoria', 'troca', 'espelho'
    """
    conf_a = prof_a.get('conformidade', 50)
    conf_b = prof_b.get('conformidade', 50)
    diff = abs(conf_a - conf_b)

    if diff > 25:
        return 'mentoria'
    elif prof_a.get('unidade') != prof_b.get('unidade'):
        return 'troca'
    else:
        return 'espelho'


def gerar_pareamentos(profs_list, min_score=30, max_pares=20):
    """Gera lista de pareamentos sugeridos para toda a rede.

    Args:
        profs_list: lista de dicts com dados dos professores
            Cada dict: {professor, disciplina, serie, unidade,
                        conformidade, score, total_aulas}
        min_score: score minimo para sugerir pareamento
        max_pares: maximo de pares retornados

    Returns:
        lista de dicts: [{prof_a, prof_b, score, tipo, motivo}, ...]
    """
    if len(profs_list) < 2:
        return []

    pareamentos = []
    for a, b in combinations(range(len(profs_list)), 2):
        prof_a = profs_list[a]
        prof_b = profs_list[b]
        sc = _score_pareamento(prof_a, prof_b)

        if sc >= min_score:
            tipo = _tipo_pareamento(prof_a, prof_b)

            # Gerar motivo
            motivos = []
            if prof_a.get('disciplina', '').lower() == prof_b.get('disciplina', '').lower():
                motivos.append(f"mesma disciplina ({prof_a.get('disciplina', '')})")
            if prof_a.get('serie') == prof_b.get('serie'):
                motivos.append(f"mesma serie ({prof_a.get('serie', '')})")
            if prof_a.get('unidade') != prof_b.get('unidade'):
                motivos.append("unidades diferentes (troca cross-unit)")
            if tipo == 'mentoria':
                forte = prof_a if prof_a.get('conformidade', 0) > prof_b.get('conformidade', 0) else prof_b
                motivos.append(f"mentoria ({forte.get('professor', '')} como referencia)")

            pareamentos.append({
                'prof_a': prof_a.get('professor', ''),
                'prof_b': prof_b.get('professor', ''),
                'un_a': prof_a.get('unidade', ''),
                'un_b': prof_b.get('unidade', ''),
                'score': sc,
                'tipo': tipo,
                'motivo': ' | '.join(motivos) if motivos else 'complementaridade geral',
            })

    pareamentos.sort(key=lambda x: x['score'], reverse=True)
    return pareamentos[:max_pares]


def sugerir_pares(professor_nome, profs_list, n=3):
    """Sugere os N melhores pares para um professor especifico.

    Args:
        professor_nome: nome do professor
        profs_list: lista de dicts de professores
        n: numero de sugestoes

    Returns:
        lista de dicts: [{par, score, tipo, motivo}, ...]
    """
    prof_ref = None
    for p in profs_list:
        if p.get('professor', '') == professor_nome:
            prof_ref = p
            break

    if not prof_ref:
        return []

    sugestoes = []
    for p in profs_list:
        if p.get('professor', '') == professor_nome:
            continue
        sc = _score_pareamento(prof_ref, p)
        tipo = _tipo_pareamento(prof_ref, p)
        sugestoes.append({
            'par': p.get('professor', ''),
            'unidade': p.get('unidade', ''),
            'disciplina': p.get('disciplina', ''),
            'score': sc,
            'tipo': tipo,
        })

    sugestoes.sort(key=lambda x: x['score'], reverse=True)
    return sugestoes[:n]


def carregar_pareamentos_salvos():
    """Carrega pareamentos salvos do disco."""
    if _PAREAMENTOS_PATH.exists():
        try:
            with open(_PAREAMENTOS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def salvar_pareamentos(pareamentos):
    """Persiste pareamentos no disco."""
    data = {
        'gerado_em': datetime.now().isoformat(),
        'pareamentos': pareamentos,
    }
    with open(_PAREAMENTOS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
