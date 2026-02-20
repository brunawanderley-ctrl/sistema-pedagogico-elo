"""
Módulo centralizado de normalização — Colégio ELO 2026.

FONTE ÚNICA DE VERDADE para todas as conversões de nomes entre sistemas:
  - Séries (SIGA → canônico, SAE grade_id → canônico)
  - Disciplinas (SIGA → canônico, fato → progressão, horário → base, SAE → canônico)
  - Nomes de professores (limpeza de sufixos de unidade/ano)

Projetado para ser importável por qualquer módulo do projeto sem dependências
externas (usa apenas a stdlib do Python).

Convenções de nomes canônicos:
  Séries:       '6º Ano', '7º Ano', '8º Ano', '9º Ano',
                '1ª Série', '2ª Série', '3ª Série'
  Disciplinas:  conforme registradas no dim_Disciplinas.csv (35 disciplinas)

Uso:
    from normalizacao import normalizar_serie, normalizar_disciplina
    serie = normalizar_serie('6º ANO')        # → '6º Ano'
    disc  = normalizar_disciplina('Português') # → 'Língua Portuguesa'
"""

import re

# ============================================================
# CONSTANTES — UNIDADES
# ============================================================

UNIDADES = ['BV', 'CD', 'JG', 'CDR']
"""Códigos das 4 unidades do Colégio ELO, na ordem padrão."""

UNIDADES_NOMES = {
    'BV': 'Boa Viagem',
    'CD': 'Candeias',
    'JG': 'Janga',
    'CDR': 'Cordeiro',
}
"""Mapeamento código → nome por extenso de cada unidade."""

# ============================================================
# CONSTANTES — SÉRIES
# ============================================================

ORDEM_SERIES = [
    '6º Ano', '7º Ano', '8º Ano', '9º Ano',
    '1ª Série', '2ª Série', '3ª Série',
]
"""Ordem canônica das 7 séries atendidas (Fund II + EM)."""

SERIES_FUND_II = ['6º Ano', '7º Ano', '8º Ano', '9º Ano']
"""Séries do Ensino Fundamental II (Anos Finais)."""

SERIES_EM = ['1ª Série', '2ª Série', '3ª Série']
"""Séries do Ensino Médio."""

# Conjunto para lookups rápidos (usado em regras como Sociologia → Filosofia)
_SERIES_FUND_II_SET = set(SERIES_FUND_II)

# ============================================================
# MAPEAMENTOS — SÉRIES
# ============================================================

SERIE_NORMALIZACAO = {
    # SIGA retorna em maiúsculas ou com sufixos variados
    '6º ANO': '6º Ano',
    '7º ANO': '7º Ano',
    '8º ANO': '8º Ano',
    '9º ANO': '9º Ano',
    '1º Ano Médio': '1ª Série',
    '2º Ano Médio': '2ª Série',
    '3º Ano Médio': '3ª Série',
    '1ª Série EM': '1ª Série',
    '2ª Série EM': '2ª Série',
    '3ª Série EM': '3ª Série',
}
"""Normalização de séries vindas do SIGA para o formato canônico."""

# Grade IDs do SAE Digital → Série canônica
GRADE_MAP_SAE = {
    10: '6º Ano',
    11: '7º Ano',
    12: '8º Ano',
    13: '9º Ano',
    14: '1ª Série',
    15: '2ª Série',
    16: '3ª Série',
}
"""Mapeamento grade_id SAE Digital (10-16) → série canônica."""

# ============================================================
# MAPEAMENTOS — DISCIPLINAS
# ============================================================

DISCIPLINA_NORMALIZACAO = {
    # Nomes alternativos vindos do SIGA → canônico
    'Português': 'Língua Portuguesa',
    'Ciências': 'Ciências Naturais',
    'Língua Inglesa': 'Língua Estrangeira Inglês',
    'Inglês': 'Língua Estrangeira Inglês',
    'Física II': 'Física 2',
    'Ciências Sociais': 'Sociologia',
    'Projeto de Vida / LIV': 'Projeto de Vida',
    'Oficina de Redação e Prod. Textual': 'Redação',
    'IF - Projeto de Vida': 'Projeto de Vida',
    'LÍNGUA PORTUGUESA 1': 'Língua Portuguesa 1',
    'LÍNGUA PORTUGUESA 2': 'Língua Portuguesa 2',
    # Abreviações do SIGA para disciplinas numeradas do EM
    'BIO 2': 'Biologia 2',
    'QUIM 2': 'Química 2',
    'QUIM 3': 'Química 3',
    'FISIC 2': 'Física 2',
    'matem 2': 'Matemática 2',
}
"""Normalização de disciplinas vindas do SIGA (nomes alternativos/abreviados) → canônico."""

DISCIPLINA_NORM_FATO = {
    # Disciplinas numeradas do fato_Aulas → nome base para progressão SAE
    # O SIGA registra 'Física 2', 'Matemática 3' etc., mas a progressão
    # SAE usa apenas o nome base ('Física', 'Matemática').
    'Física 2': 'Física',
    'Física 3': 'Física',
    'Biologia 2': 'Biologia',
    'Matemática 2': 'Matemática',
    'Matemática 3': 'Matemática',
    'Química 2': 'Química',
    'Química 3': 'Química',
    'História 2': 'História',
    'Geografia 2': 'Geografia',
    'Língua Portuguesa 2': 'Língua Portuguesa',
}
"""Normalização de disciplinas numeradas (fato_Aulas) → nome base para progressão SAE."""

DISCIPLINA_NORM_HORARIO = {
    # O horário do EM divide disciplinas em slots (Matemática 1, 2, 3),
    # mas o SIGA registra apenas o nome base (Matemática).
    'Matemática 1': 'Matemática',
    'Matemática 2': 'Matemática',
    'Matemática 3': 'Matemática',
    'Física 1': 'Física',
    'Física 2': 'Física',
    'Física 3': 'Física',
    'Biologia 1': 'Biologia',
    'Biologia 2': 'Biologia',
    'Química 1': 'Química',
    'Química 2': 'Química',
    'Química 3': 'Química',
    'História 1': 'História',
    'História 2': 'História',
    'Geografia 1': 'Geografia',
    'Geografia 2': 'Geografia',
    'Língua Portuguesa 1': 'Língua Portuguesa',
    'Língua Portuguesa 2': 'Língua Portuguesa',
}
"""Normalização de disciplinas numeradas do horário (slots EM) → nome base SIGA."""

DISCIPLINA_SAE_MAP = {
    # Nomes usados no SAE Digital → canônico SIGA
    'Ciências': 'Ciências Naturais',
    'Ciências da Natureza': 'Ciências Naturais',
    'Inglês': 'Língua Estrangeira Inglês',
    'Língua Inglesa': 'Língua Estrangeira Inglês',
    'Artes': 'Arte',
}
"""Normalização de disciplinas do SAE Digital → canônico SIGA."""

# ============================================================
# REGEX — PROFESSOR
# ============================================================

_RE_SUFIXO_PROFESSOR = re.compile(
    r'\s*-\s*(?:BV|CD|JG|CDR|CORD|TEEN\s*\d?)\s*-\s*\d{4}\s*$'
)
"""Regex para remover sufixos de unidade/ano do nome do professor.
Exemplos removidos: '- BV - 2026', '- CDR - 2025', '- TEEN 1 - 2026'."""

_RE_ESPACOS_MULTIPLOS = re.compile(r'\s+')
"""Regex para colapsar espaços múltiplos em um único espaço."""


# ============================================================
# FUNÇÕES DE NORMALIZAÇÃO
# ============================================================

def normalizar_serie(serie):
    """
    Normaliza o nome de uma série vinda do SIGA para o formato canônico.

    Exemplos:
        '6º ANO'        → '6º Ano'
        '1º Ano Médio'  → '1ª Série'
        '2ª Série EM'   → '2ª Série'
        '7º Ano'        → '7º Ano' (já canônico, retorna inalterado)

    Args:
        serie: Nome da série como string (pode conter espaços extras).

    Returns:
        Nome canônico da série, ou o valor original (strip) se não encontrado
        no mapeamento. Retorna o valor original se None/vazio.
    """
    if not serie:
        return serie
    return SERIE_NORMALIZACAO.get(serie.strip(), serie.strip())


def normalizar_disciplina(disciplina):
    """
    Normaliza o nome de uma disciplina vinda do SIGA para o formato canônico.

    Aplica o mapeamento DISCIPLINA_NORMALIZACAO que cobre nomes alternativos,
    abreviações e variações de caixa usados pelo SIGA.

    Exemplos:
        'Português'       → 'Língua Portuguesa'
        'Ciências'        → 'Ciências Naturais'
        'Física II'       → 'Física 2'
        'BIO 2'           → 'Biologia 2'
        'Matemática'      → 'Matemática' (já canônico)

    Args:
        disciplina: Nome da disciplina como string.

    Returns:
        Nome canônico da disciplina, ou o valor original (strip) se não
        encontrado no mapeamento. Retorna o valor original se None/vazio.
    """
    if not disciplina:
        return disciplina
    return DISCIPLINA_NORMALIZACAO.get(disciplina.strip(), disciplina.strip())


def normalizar_nome_professor(nome):
    """
    Normaliza o nome de um professor removendo sufixos de unidade/ano.

    O SIGA frequentemente retorna nomes no formato:
        'JOAO SILVA - BV - 2026'
        'MARIA SOUZA - CDR - 2025'
        'PEDRO LIMA - TEEN 1 - 2026'

    Esta função remove o sufixo e normaliza para maiúsculas com espaços simples.

    Exemplos:
        'João Silva - BV - 2026'  → 'JOAO SILVA'
        'maria souza'             → 'MARIA SOUZA'
        ''                        → ''
        None                      → ''

    Args:
        nome: Nome do professor como string.

    Returns:
        Nome normalizado em maiúsculas, sem sufixos.
        Retorna string vazia se None/vazio.
    """
    if not nome:
        return ''
    nome = nome.strip().upper()
    nome = _RE_SUFIXO_PROFESSOR.sub('', nome)
    return _RE_ESPACOS_MULTIPLOS.sub(' ', nome).strip()


def normalizar_disciplina_fato(nome):
    """
    Normaliza disciplina numerada do fato_Aulas para nome base (progressão SAE).

    Disciplinas numeradas como 'Física 2', 'Matemática 3' são variantes do EM
    que, para fins de progressão SAE, devem ser tratadas como disciplina base.

    Exemplos:
        'Física 2'              → 'Física'
        'Matemática 3'          → 'Matemática'
        'Língua Portuguesa 2'   → 'Língua Portuguesa'
        'Arte'                  → 'Arte' (não está no mapeamento, retorna igual)

    Args:
        nome: Nome da disciplina como string.

    Returns:
        Nome base da disciplina para progressão, ou o valor original se
        não encontrado no mapeamento. Retorna o valor original se None/vazio.
    """
    if not nome:
        return nome
    return DISCIPLINA_NORM_FATO.get(nome.strip(), nome.strip())


def normalizar_disciplina_horario(nome):
    """
    Normaliza disciplina numerada do horário (slots EM) para nome base SIGA.

    O horário do Ensino Médio divide disciplinas em múltiplos slots
    (ex: Matemática 1, Matemática 2, Matemática 3), mas o SIGA registra
    apenas o nome base (Matemática).

    Exemplos:
        'Matemática 1' → 'Matemática'
        'Física 3'     → 'Física'
        'Arte'         → 'Arte' (não está no mapeamento, retorna igual)

    Args:
        nome: Nome da disciplina como string.

    Returns:
        Nome base da disciplina, ou o valor original se não encontrado
        no mapeamento. Retorna o valor original se None/vazio.
    """
    if not nome:
        return nome
    return DISCIPLINA_NORM_HORARIO.get(nome.strip(), nome.strip())


def normalizar_disciplina_sae(nome):
    """
    Normaliza nome de disciplina do SAE Digital para o canônico SIGA.

    O SAE Digital usa nomes ligeiramente diferentes para algumas disciplinas.

    Exemplos:
        'Ciências'          → 'Ciências Naturais'
        'Língua Inglesa'    → 'Língua Estrangeira Inglês'
        'Artes'             → 'Arte'
        'Matemática'        → 'Matemática' (já canônico)

    Args:
        nome: Nome da disciplina no SAE Digital.

    Returns:
        Nome canônico SIGA, ou o valor original se já estiver correto.
        Retorna o valor original se None/vazio.
    """
    if not nome:
        return nome
    return DISCIPLINA_SAE_MAP.get(nome, nome)


def normalizar_serie_sae(grade_id):
    """
    Converte grade_id do SAE Digital (10-16) para série canônica.

    Mapeamento:
        10 → '6º Ano'    11 → '7º Ano'    12 → '8º Ano'    13 → '9º Ano'
        14 → '1ª Série'  15 → '2ª Série'  16 → '3ª Série'

    Args:
        grade_id: ID numérico da grade no SAE Digital (int ou conversível).

    Returns:
        Nome canônico da série, ou None se grade_id não reconhecido ou None.
    """
    if grade_id is None:
        return None
    return GRADE_MAP_SAE.get(int(grade_id))


def serie_eh_fund_ii(serie):
    """
    Verifica se uma série (já normalizada) pertence ao Fundamental II.

    Útil para regras condicionais como: Sociologia no Fund II é na verdade Filosofia.

    Args:
        serie: Nome canônico da série.

    Returns:
        True se a série é do Fundamental II, False caso contrário.
    """
    return serie in _SERIES_FUND_II_SET
