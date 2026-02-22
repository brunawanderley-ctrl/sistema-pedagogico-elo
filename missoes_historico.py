"""
Rastreamento de missoes entre semanas.
Fingerprint estavel (sem semana no ID) permite detectar missoes persistentes.

Funcoes publicas:
  - atualizar_historico(missoes_por_unidade, semana)
  - obter_persistentes(min_semanas=4)
  - gerar_fingerprint(missao) — alias de missoes.gerar_missao_fingerprint
"""

import json
from pathlib import Path
from datetime import datetime

from utils import WRITABLE_DIR
from missoes import gerar_missao_fingerprint

# Re-export para conveniencia
gerar_fingerprint = gerar_missao_fingerprint

_HISTORICO_PATH = WRITABLE_DIR / "missoes_historico.json"


def _carregar_historico():
    """Carrega historico de missoes do JSON."""
    if not _HISTORICO_PATH.exists():
        return {}
    try:
        with open(_HISTORICO_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _salvar_historico(historico):
    """Salva historico de missoes em JSON."""
    with open(_HISTORICO_PATH, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)


def atualizar_historico(missoes_por_unidade, semana):
    """Atualiza historico com as missoes da semana atual.

    Args:
        missoes_por_unidade: dict {unidade: [missoes]} — output de gerar_todas_missoes_rede()
        semana: numero da semana letiva atual

    Returns:
        dict do historico atualizado
    """
    historico = _carregar_historico()
    agora = datetime.now().isoformat()

    # Coletar todos os fingerprints ativos nesta semana
    fingerprints_ativos = set()

    for unidade, missoes in missoes_por_unidade.items():
        for b in missoes:
            fp = gerar_missao_fingerprint(b)
            fingerprints_ativos.add(fp)

            if fp in historico:
                # Atualizar registro existente
                entry = historico[fp]
                entry['ultima_semana'] = semana
                entry['atualizado_em'] = agora
                if semana not in entry.get('semanas_vistas', []):
                    entry['semanas_vistas'].append(semana)
                entry['semanas_ativas'] = len(entry['semanas_vistas'])
                # Atualizar dados da missao mais recente
                entry['score'] = b.get('score', 0)
                entry['nivel'] = b.get('nivel', '')
                entry['n_afetados'] = b.get('n_afetados', 0)
                entry['o_que'] = b.get('o_que', '')
            else:
                # Novo registro
                historico[fp] = {
                    'fingerprint': fp,
                    'tipo': b.get('tipo', ''),
                    'unidade': unidade,
                    'entidade': b.get('professor', b.get('serie', b.get('disciplina', ''))),
                    'primeira_semana': semana,
                    'ultima_semana': semana,
                    'semanas_vistas': [semana],
                    'semanas_ativas': 1,
                    'criado_em': agora,
                    'atualizado_em': agora,
                    'score': b.get('score', 0),
                    'nivel': b.get('nivel', ''),
                    'n_afetados': b.get('n_afetados', 0),
                    'o_que': b.get('o_que', ''),
                }

    _salvar_historico(historico)
    return historico


def obter_persistentes(min_semanas=4):
    """Retorna missoes que aparecem em min_semanas ou mais semanas.

    Args:
        min_semanas: minimo de semanas ativas para considerar persistente (default 4)

    Returns:
        lista de dicts ordenada por semanas_ativas desc, score desc
    """
    historico = _carregar_historico()
    persistentes = [
        entry for entry in historico.values()
        if entry.get('semanas_ativas', 0) >= min_semanas
    ]
    persistentes.sort(key=lambda x: (-x.get('semanas_ativas', 0), -x.get('score', 0)))
    return persistentes


def obter_historico_completo():
    """Retorna o historico completo para analise."""
    return _carregar_historico()


def limpar_historico_antigo(semana_atual, max_inatividade=8):
    """Remove entradas que nao aparecem ha mais de max_inatividade semanas.

    Args:
        semana_atual: semana letiva atual
        max_inatividade: semanas sem aparecer para remover (default 8)

    Returns:
        int: numero de entradas removidas
    """
    historico = _carregar_historico()
    removidos = 0
    para_remover = []

    for fp, entry in historico.items():
        ultima = entry.get('ultima_semana', 0)
        if semana_atual - ultima > max_inatividade:
            para_remover.append(fp)

    for fp in para_remover:
        del historico[fp]
        removidos += 1

    if removidos > 0:
        _salvar_historico(historico)

    return removidos
