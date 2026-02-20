"""
Modelo de dominio canonico para o BI Unificado do Colegio ELO 2026.

Unifica os dois sistemas:
  - Pedagogico (SIGA): unidades BV/CD/JG/CDR, 7 series (6o ao 3a EM), CSVs
  - Vagas/Matriculas: unidades 01-BV/02-CD/03-JG/04-CDR, 16 series, SQLite

Incompatibilidades conhecidas resolvidas aqui:
  - CD = "Candeias" no SIGA, "Jaboatao" no Vagas (mesma unidade fisica)
  - JG = "Janga" no SIGA, "Paulista" no Vagas (mesma unidade fisica)
  - Pedagogico cobre 7 series (Fund II + EM), Vagas cobre 16 (Ed. Infantil ao EM)

Uso:
  from shared_domain import (
      UNIDADES_CANONICAL, SERIES_UNIVERSAL, METAS_2026,
      traduzir_unidade_vagas_para_pedagogico,
      traduzir_serie_vagas_para_pedagogico,
  )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# DATACLASSES
# ============================================================

@dataclass(frozen=True)
class Unidade:
    """Representa uma unidade escolar do Colegio ELO.

    Campos:
        codigo: Codigo interno no sistema pedagogico (BV, CD, JG, CDR).
        nome: Nome canonico da unidade (Boa Viagem, Candeias, Janga, Cordeiro).
        bairro: Bairro onde a unidade esta localizada.
        cidade: Cidade da unidade.
        codigo_vagas: Codigo no sistema de Vagas/Matriculas (01-BV, 02-CD, etc.).
        nome_vagas: Nome usado no sistema de Vagas (pode diferir do canonico).
        meta_2026: Meta de matriculas para 2026.
        periodo_api_siga: Codigo do periodo na API SIGA para esta unidade.
        seletor_login_siga: Numero do seletor de login SIGA (1-4).
    """
    codigo: str
    nome: str
    bairro: str
    cidade: str
    codigo_vagas: str
    nome_vagas: str
    meta_2026: int
    periodo_api_siga: int
    seletor_login_siga: int


@dataclass(frozen=True)
class SerieUniversal:
    """Representa uma serie escolar com mapeamento entre os dois sistemas.

    Campos:
        serie_canonica: Nome padrao usado como chave universal (ex: '6o Ano').
        serie_siga: Nome exato como aparece no SIGA/Pedagogico (None se nao coberta).
        serie_vagas: Nome exato como aparece no sistema Vagas (None se nao existir).
        segmento: Segmento educacional (Ed. Infantil, Fund. I, Fund. II, Ens. Medio).
        segmento_pedagogico: Segmento no sistema pedagogico (Anos Finais, Ensino Medio, ou None).
        ordem: Posicao para ordenacao (1 = mais novo, 16 = mais velho).
        turma_teen: Grupo TEEN SAE (TEEN 1, TEEN 2, ou None para series sem material SAE).
        coberta_pedagogico: True se a serie tem dados no sistema pedagogico.
        coberta_vagas: True se a serie tem dados no sistema de vagas.
    """
    serie_canonica: str
    serie_siga: Optional[str]
    serie_vagas: Optional[str]
    segmento: str
    segmento_pedagogico: Optional[str]
    ordem: int
    turma_teen: Optional[str]
    coberta_pedagogico: bool
    coberta_vagas: bool


# ============================================================
# UNIDADES - Mapeamento Canonico
# ============================================================

UNIDADES_CANONICAL: Dict[str, Unidade] = {
    'BV': Unidade(
        codigo='BV',
        nome='Boa Viagem',
        bairro='Boa Viagem',
        cidade='Recife',
        codigo_vagas='01-BV',
        nome_vagas='Boa Viagem',
        meta_2026=1250,
        periodo_api_siga=80,
        seletor_login_siga=1,
    ),
    'CD': Unidade(
        codigo='CD',
        nome='Candeias',
        bairro='Candeias',
        cidade='Jaboatao dos Guararapes',
        codigo_vagas='02-CD',
        nome_vagas='Jaboatao',  # ATENCAO: no Vagas aparece como "Jaboatao", nao "Candeias"
        meta_2026=1200,
        periodo_api_siga=78,
        seletor_login_siga=2,
    ),
    'JG': Unidade(
        codigo='JG',
        nome='Janga',
        bairro='Janga',
        cidade='Paulista',
        codigo_vagas='03-JG',
        nome_vagas='Paulista',  # ATENCAO: no Vagas aparece como "Paulista", nao "Janga"
        meta_2026=850,
        periodo_api_siga=79,
        seletor_login_siga=3,
    ),
    'CDR': Unidade(
        codigo='CDR',
        nome='Cordeiro',
        bairro='Cordeiro',
        cidade='Recife',
        codigo_vagas='04-CDR',
        nome_vagas='Cordeiro',
        meta_2026=800,
        periodo_api_siga=77,
        seletor_login_siga=4,
    ),
}

# ============================================================
# SERIES - Mapeamento Universal
# ============================================================

SERIES_UNIVERSAL: Dict[str, SerieUniversal] = {
    # --- Ed. Infantil (apenas Vagas) ---
    'Infantil II': SerieUniversal(
        serie_canonica='Infantil II',
        serie_siga=None,
        serie_vagas='Infantil II',
        segmento='Ed. Infantil',
        segmento_pedagogico=None,
        ordem=1,
        turma_teen=None,
        coberta_pedagogico=False,
        coberta_vagas=True,
    ),
    'Infantil III': SerieUniversal(
        serie_canonica='Infantil III',
        serie_siga=None,
        serie_vagas='Infantil III',
        segmento='Ed. Infantil',
        segmento_pedagogico=None,
        ordem=2,
        turma_teen=None,
        coberta_pedagogico=False,
        coberta_vagas=True,
    ),
    'Infantil IV': SerieUniversal(
        serie_canonica='Infantil IV',
        serie_siga=None,
        serie_vagas='Infantil IV',
        segmento='Ed. Infantil',
        segmento_pedagogico=None,
        ordem=3,
        turma_teen=None,
        coberta_pedagogico=False,
        coberta_vagas=True,
    ),
    'Infantil V': SerieUniversal(
        serie_canonica='Infantil V',
        serie_siga=None,
        serie_vagas='Infantil V',
        segmento='Ed. Infantil',
        segmento_pedagogico=None,
        ordem=4,
        turma_teen=None,
        coberta_pedagogico=False,
        coberta_vagas=True,
    ),
    # --- Fund. I (apenas Vagas) ---
    '1\u00ba Ano': SerieUniversal(
        serie_canonica='1\u00ba Ano',
        serie_siga=None,
        serie_vagas='1\u00ba Ano',
        segmento='Fund. I',
        segmento_pedagogico=None,
        ordem=5,
        turma_teen=None,
        coberta_pedagogico=False,
        coberta_vagas=True,
    ),
    '2\u00ba Ano': SerieUniversal(
        serie_canonica='2\u00ba Ano',
        serie_siga=None,
        serie_vagas='2\u00ba Ano',
        segmento='Fund. I',
        segmento_pedagogico=None,
        ordem=6,
        turma_teen=None,
        coberta_pedagogico=False,
        coberta_vagas=True,
    ),
    '3\u00ba Ano': SerieUniversal(
        serie_canonica='3\u00ba Ano',
        serie_siga=None,
        serie_vagas='3\u00ba Ano',
        segmento='Fund. I',
        segmento_pedagogico=None,
        ordem=7,
        turma_teen=None,
        coberta_pedagogico=False,
        coberta_vagas=True,
    ),
    '4\u00ba Ano': SerieUniversal(
        serie_canonica='4\u00ba Ano',
        serie_siga=None,
        serie_vagas='4\u00ba Ano',
        segmento='Fund. I',
        segmento_pedagogico=None,
        ordem=8,
        turma_teen=None,
        coberta_pedagogico=False,
        coberta_vagas=True,
    ),
    '5\u00ba Ano': SerieUniversal(
        serie_canonica='5\u00ba Ano',
        serie_siga=None,
        serie_vagas='5\u00ba Ano',
        segmento='Fund. I',
        segmento_pedagogico=None,
        ordem=9,
        turma_teen=None,
        coberta_pedagogico=False,
        coberta_vagas=True,
    ),
    # --- Fund. II (ambos os sistemas) ---
    '6\u00ba Ano': SerieUniversal(
        serie_canonica='6\u00ba Ano',
        serie_siga='6\u00ba Ano',
        serie_vagas='6\u00ba Ano',
        segmento='Fund. II',
        segmento_pedagogico='Anos Finais',
        ordem=10,
        turma_teen='TEEN 1',
        coberta_pedagogico=True,
        coberta_vagas=True,
    ),
    '7\u00ba Ano': SerieUniversal(
        serie_canonica='7\u00ba Ano',
        serie_siga='7\u00ba Ano',
        serie_vagas='7\u00ba Ano',
        segmento='Fund. II',
        segmento_pedagogico='Anos Finais',
        ordem=11,
        turma_teen='TEEN 1',
        coberta_pedagogico=True,
        coberta_vagas=True,
    ),
    '8\u00ba Ano': SerieUniversal(
        serie_canonica='8\u00ba Ano',
        serie_siga='8\u00ba Ano',
        serie_vagas='8\u00ba Ano',
        segmento='Fund. II',
        segmento_pedagogico='Anos Finais',
        ordem=12,
        turma_teen='TEEN 1',
        coberta_pedagogico=True,
        coberta_vagas=True,
    ),
    '9\u00ba Ano': SerieUniversal(
        serie_canonica='9\u00ba Ano',
        serie_siga='9\u00ba Ano',
        serie_vagas='9\u00ba Ano',
        segmento='Fund. II',
        segmento_pedagogico='Anos Finais',
        ordem=13,
        turma_teen='TEEN 2',
        coberta_pedagogico=True,
        coberta_vagas=True,
    ),
    # --- Ensino Medio (ambos os sistemas) ---
    '1\u00aa S\u00e9rie': SerieUniversal(
        serie_canonica='1\u00aa S\u00e9rie',
        serie_siga='1\u00aa S\u00e9rie',
        serie_vagas='1\u00aa S\u00e9rie',
        segmento='Ens. M\u00e9dio',
        segmento_pedagogico='Ensino M\u00e9dio',
        ordem=14,
        turma_teen='TEEN 2',
        coberta_pedagogico=True,
        coberta_vagas=True,
    ),
    '2\u00aa S\u00e9rie': SerieUniversal(
        serie_canonica='2\u00aa S\u00e9rie',
        serie_siga='2\u00aa S\u00e9rie',
        serie_vagas='2\u00aa S\u00e9rie',
        segmento='Ens. M\u00e9dio',
        segmento_pedagogico='Ensino M\u00e9dio',
        ordem=15,
        turma_teen='TEEN 2',
        coberta_pedagogico=True,
        coberta_vagas=True,
    ),
    '3\u00aa S\u00e9rie': SerieUniversal(
        serie_canonica='3\u00aa S\u00e9rie',
        serie_siga='3\u00aa S\u00e9rie',
        serie_vagas='3\u00aa S\u00e9rie',
        segmento='Ens. M\u00e9dio',
        segmento_pedagogico='Ensino M\u00e9dio',
        ordem=16,
        turma_teen='TEEN 2',
        coberta_pedagogico=True,
        coberta_vagas=True,
    ),
}


# ============================================================
# METAS DE MATRICULAS 2026
# ============================================================

METAS_2026: Dict[str, int] = {
    'BV': 1250,
    'CD': 1200,
    'JG': 850,
    'CDR': 800,
}
"""Metas de matriculas 2026 indexadas pelo codigo canonico da unidade."""

META_TOTAL_2026: int = 4100
"""Meta total de matriculas 2026 (soma de todas as unidades)."""

# Metas indexadas pelo nome do sistema Vagas (para uso direto em joins)
METAS_2026_POR_NOME_VAGAS: Dict[str, int] = {
    u.nome_vagas: u.meta_2026 for u in UNIDADES_CANONICAL.values()
}


# ============================================================
# INDICES REVERSOS (construidos automaticamente)
# ============================================================

# codigo_vagas -> codigo_pedagogico
_VAGAS_CODE_TO_PED: Dict[str, str] = {
    u.codigo_vagas: u.codigo for u in UNIDADES_CANONICAL.values()
}

# nome_vagas -> codigo_pedagogico
_VAGAS_NAME_TO_PED: Dict[str, str] = {
    u.nome_vagas: u.codigo for u in UNIDADES_CANONICAL.values()
}

# nome_vagas -> nome canonico
_VAGAS_NAME_TO_CANONICAL_NAME: Dict[str, str] = {
    u.nome_vagas: u.nome for u in UNIDADES_CANONICAL.values()
}

# nome canonico -> codigo
_CANONICAL_NAME_TO_CODE: Dict[str, str] = {
    u.nome: u.codigo for u in UNIDADES_CANONICAL.values()
}

# serie_vagas -> serie_canonica (util para series que podem ter nomes legados)
_SERIE_VAGAS_TO_CANONICA: Dict[str, str] = {}
for _s in SERIES_UNIVERSAL.values():
    if _s.serie_vagas is not None:
        _SERIE_VAGAS_TO_CANONICA[_s.serie_vagas] = _s.serie_canonica

# Nomes legados do EM no sistema Vagas ("1o Ano Medio" -> "1a Serie")
_NORMALIZAR_SERIE_EM_LEGADO: Dict[str, str] = {
    '1\u00ba Ano M\u00e9dio': '1\u00aa S\u00e9rie',
    '2\u00ba Ano M\u00e9dio': '2\u00aa S\u00e9rie',
    '3\u00ba Ano M\u00e9dio': '3\u00aa S\u00e9rie',
}


# ============================================================
# FUNCOES DE TRADUCAO
# ============================================================

def traduzir_unidade_vagas_para_pedagogico(valor: str) -> Optional[str]:
    """Converte identificador de unidade do sistema Vagas para o codigo pedagogico.

    Aceita tanto o codigo (ex: '01-BV') quanto o nome (ex: 'Jaboatao').
    Retorna o codigo canonico (ex: 'BV') ou None se nao encontrado.

    Exemplos:
        >>> traduzir_unidade_vagas_para_pedagogico('01-BV')
        'BV'
        >>> traduzir_unidade_vagas_para_pedagogico('02-CD')
        'CD'
        >>> traduzir_unidade_vagas_para_pedagogico('Jaboatao')
        'CD'
        >>> traduzir_unidade_vagas_para_pedagogico('Paulista')
        'JG'
    """
    if not valor:
        return None
    valor_strip = valor.strip()
    # Tenta pelo codigo Vagas (01-BV, 02-CD, etc.)
    if valor_strip in _VAGAS_CODE_TO_PED:
        return _VAGAS_CODE_TO_PED[valor_strip]
    # Tenta pelo nome Vagas (Jaboatao, Paulista, etc.)
    if valor_strip in _VAGAS_NAME_TO_PED:
        return _VAGAS_NAME_TO_PED[valor_strip]
    # Tenta pelo nome canonico (Candeias, Janga, etc.)
    if valor_strip in _CANONICAL_NAME_TO_CODE:
        return _CANONICAL_NAME_TO_CODE[valor_strip]
    # Tenta pelo proprio codigo pedagogico (BV, CD, etc.)
    if valor_strip in UNIDADES_CANONICAL:
        return valor_strip
    return None


def traduzir_unidade_pedagogico_para_vagas(codigo: str, formato: str = 'codigo') -> Optional[str]:
    """Converte codigo de unidade do sistema pedagogico para o sistema Vagas.

    Args:
        codigo: Codigo pedagogico (BV, CD, JG, CDR).
        formato: 'codigo' retorna '01-BV', 'nome' retorna 'Jaboatao'.

    Retorna None se codigo nao encontrado.

    Exemplos:
        >>> traduzir_unidade_pedagogico_para_vagas('CD', 'codigo')
        '02-CD'
        >>> traduzir_unidade_pedagogico_para_vagas('JG', 'nome')
        'Paulista'
    """
    if not codigo or codigo.strip() not in UNIDADES_CANONICAL:
        return None
    unidade = UNIDADES_CANONICAL[codigo.strip()]
    if formato == 'nome':
        return unidade.nome_vagas
    return unidade.codigo_vagas


def traduzir_serie_vagas_para_pedagogico(serie_vagas: str) -> Optional[str]:
    """Converte nome de serie do sistema Vagas para a serie canonica do pedagogico.

    Trata nomes legados como '1o Ano Medio' -> '1a Serie'.
    Retorna None se a serie nao existir no sistema pedagogico (ex: Ed. Infantil).

    Exemplos:
        >>> traduzir_serie_vagas_para_pedagogico('6o Ano')
        '6o Ano'
        >>> traduzir_serie_vagas_para_pedagogico('1o Ano Medio')
        '1a Serie'
        >>> traduzir_serie_vagas_para_pedagogico('Infantil III')  # Nao existe no pedagogico
        None
    """
    if not serie_vagas:
        return None
    serie_strip = serie_vagas.strip()
    # Normaliza nomes legados do EM
    if serie_strip in _NORMALIZAR_SERIE_EM_LEGADO:
        serie_strip = _NORMALIZAR_SERIE_EM_LEGADO[serie_strip]
    # Busca no mapeamento universal
    info = SERIES_UNIVERSAL.get(serie_strip)
    if info is None:
        return None
    # So retorna se a serie esta coberta pelo pedagogico
    if info.coberta_pedagogico:
        return info.serie_siga
    return None


def traduzir_serie_pedagogico_para_vagas(serie_siga: str) -> Optional[str]:
    """Converte nome de serie do sistema pedagogico para o formato Vagas.

    Exemplos:
        >>> traduzir_serie_pedagogico_para_vagas('6o Ano')
        '6o Ano'
        >>> traduzir_serie_pedagogico_para_vagas('1a Serie')
        '1a Serie'
    """
    if not serie_siga:
        return None
    serie_strip = serie_siga.strip()
    info = SERIES_UNIVERSAL.get(serie_strip)
    if info is None:
        return None
    return info.serie_vagas


# ============================================================
# FUNCOES AUXILIARES
# ============================================================

def obter_unidade(identificador: str) -> Optional[Unidade]:
    """Retorna a dataclass Unidade a partir de qualquer identificador conhecido.

    Aceita: codigo pedagogico (BV), codigo vagas (01-BV), nome canonico (Candeias),
    nome vagas (Jaboatao).

    Exemplos:
        >>> obter_unidade('Jaboatao').codigo
        'CD'
        >>> obter_unidade('03-JG').nome
        'Janga'
    """
    codigo = traduzir_unidade_vagas_para_pedagogico(identificador)
    if codigo is None:
        return None
    return UNIDADES_CANONICAL.get(codigo)


def obter_serie(identificador: str) -> Optional[SerieUniversal]:
    """Retorna a dataclass SerieUniversal a partir do nome da serie.

    Trata nomes legados automaticamente.

    Exemplos:
        >>> obter_serie('8o Ano').segmento
        'Fund. II'
        >>> obter_serie('1o Ano Medio').serie_canonica
        '1a Serie'
    """
    if not identificador:
        return None
    serie_strip = identificador.strip()
    # Normaliza legados
    if serie_strip in _NORMALIZAR_SERIE_EM_LEGADO:
        serie_strip = _NORMALIZAR_SERIE_EM_LEGADO[serie_strip]
    return SERIES_UNIVERSAL.get(serie_strip)


def listar_series_pedagogico() -> List[str]:
    """Retorna lista ordenada das 7 series cobertas pelo sistema pedagogico.

    Retorna:
        ['6o Ano', '7o Ano', '8o Ano', '9o Ano', '1a Serie', '2a Serie', '3a Serie']
    """
    return [
        s.serie_canonica
        for s in sorted(SERIES_UNIVERSAL.values(), key=lambda x: x.ordem)
        if s.coberta_pedagogico
    ]


def listar_series_vagas() -> List[str]:
    """Retorna lista ordenada das 16 series cobertas pelo sistema Vagas.

    Retorna:
        ['Infantil II', ..., '3a Serie']
    """
    return [
        s.serie_canonica
        for s in sorted(SERIES_UNIVERSAL.values(), key=lambda x: x.ordem)
        if s.coberta_vagas
    ]


def listar_series_por_segmento(segmento: str) -> List[str]:
    """Retorna lista ordenada de series para um dado segmento.

    Args:
        segmento: 'Ed. Infantil', 'Fund. I', 'Fund. II', 'Ens. Medio',
                  'Anos Finais' ou 'Ensino Medio' (nomes do pedagogico tambem aceitos).

    Exemplos:
        >>> listar_series_por_segmento('Fund. II')
        ['6o Ano', '7o Ano', '8o Ano', '9o Ano']
    """
    # Mapear nomes pedagogico -> vagas se necessario
    mapa_segmentos = {
        'Anos Finais': 'Fund. II',
        'Ensino M\u00e9dio': 'Ens. M\u00e9dio',
        'Ensino Medio': 'Ens. M\u00e9dio',
    }
    segmento_normalizado = mapa_segmentos.get(segmento, segmento)
    return [
        s.serie_canonica
        for s in sorted(SERIES_UNIVERSAL.values(), key=lambda x: x.ordem)
        if s.segmento == segmento_normalizado
    ]


def listar_series_intersecao() -> List[str]:
    """Retorna series presentes em AMBOS os sistemas (para cruzamento de dados).

    Sao as 7 series do Fund. II + EM.
    """
    return [
        s.serie_canonica
        for s in sorted(SERIES_UNIVERSAL.values(), key=lambda x: x.ordem)
        if s.coberta_pedagogico and s.coberta_vagas
    ]


def segmento_da_serie(serie: str) -> Optional[str]:
    """Retorna o segmento de uma serie.

    Exemplos:
        >>> segmento_da_serie('7o Ano')
        'Fund. II'
        >>> segmento_da_serie('2a Serie')
        'Ens. Medio'
    """
    info = obter_serie(serie)
    if info is None:
        return None
    return info.segmento


def nome_unidade_vagas_para_canonico(nome_vagas: str) -> Optional[str]:
    """Converte nome usado no sistema Vagas para o nome canonico.

    Exemplos:
        >>> nome_unidade_vagas_para_canonico('Jaboatao')
        'Candeias'
        >>> nome_unidade_vagas_para_canonico('Paulista')
        'Janga'
        >>> nome_unidade_vagas_para_canonico('Boa Viagem')
        'Boa Viagem'
    """
    if not nome_vagas:
        return None
    return _VAGAS_NAME_TO_CANONICAL_NAME.get(nome_vagas.strip())
