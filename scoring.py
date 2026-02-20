"""
Modulo de scoring tipado do Sistema Pedagogico ELO 2026.

Define dataclasses para todos os tipos de score (professor, aluno ABC, alertas)
e funcoes de classificacao com thresholds extraidos da implementacao existente.

Uso:
    from scoring import (
        ScoreProfessor, ScoreABC, Alerta,
        classificar_semaforo, classificar_abc,
        gerar_alerta_professor, gerar_alerta_aluno,
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List


# ============================================================
# CONSTANTES - CONFORMIDADE DO PROFESSOR (%)
# Extraidas de utils.py, usadas em paginas 13 e 14
# ============================================================

CONFORMIDADE_CRITICO: int = 50
"""Abaixo de 50% de conformidade = situacao critica."""

CONFORMIDADE_BAIXO: int = 70
"""Abaixo de 70% = atencao necessaria."""

CONFORMIDADE_META: int = 85
"""Meta institucional de conformidade."""

CONFORMIDADE_EXCELENTE: int = 95
"""Acima de 95% = excelencia."""


# ============================================================
# CONSTANTES - SEMAFORO DO PROFESSOR
# Extraidas de pages/13_Semaforo_Professor.py
# ============================================================

SEMAFORO_VERDE_REGISTRO: int = 80
"""Taxa de registro minima para semaforo verde (%)."""

SEMAFORO_VERDE_CONTEUDO: int = 60
"""Taxa de conteudo minima para semaforo verde (%)."""

SEMAFORO_AMARELO_REGISTRO: int = 60
"""Taxa de registro minima para semaforo amarelo (%)."""


# ============================================================
# CONSTANTES - CONTEUDO E RECENCIA
# Extraidas de utils.py
# ============================================================

CONTEUDO_VAZIO_ALERTA: int = 30
"""Percentual de conteudo vazio que dispara alerta."""

CONTEUDO_VAZIO_CRITICO: int = 50
"""Percentual de conteudo vazio considerado critico."""

DIAS_SEM_REGISTRO_ATENCAO: int = 4
"""Dias sem registro que gera atencao."""

DIAS_SEM_REGISTRO_URGENTE: int = 7
"""Dias sem registro que gera urgencia."""


# ============================================================
# CONSTANTES - SCORE DE RISCO DO PROFESSOR
# Pesos extraidos de pages/14_Alertas_Inteligentes.py
# ============================================================

PESO_TAXA_REGISTRO: float = 0.35
"""Peso da taxa de registro no score composto."""

PESO_TAXA_CONTEUDO: float = 0.25
"""Peso da taxa de conteudo no score composto."""

PESO_TAXA_TAREFA: float = 0.15
"""Peso da taxa de tarefa no score composto."""

PESO_RECENCIA: float = 0.25
"""Peso da recencia (regularidade) no score composto."""


# ============================================================
# CONSTANTES - FREQUENCIA (LDB)
# ============================================================

THRESHOLD_FREQUENCIA_LDB: int = 75
"""Frequencia minima pela LDB art. 24, VI (%)."""


# ============================================================
# CONSTANTES - ABC (ALERTA PRECOCE DO ALUNO)
# Extraidas de pages/23_Alerta_Precoce_ABC.py
# ============================================================

ABC_THRESHOLD_A_RISCO: int = 85
"""Frequencia abaixo de 85% = flag A (alerta)."""

ABC_THRESHOLD_A_CRITICO: int = 75
"""Frequencia abaixo de 75% = flag A (critico, LDB)."""

ABC_THRESHOLD_B_RISCO: int = 2
"""2+ ocorrencias disciplinares = flag B (alerta)."""

ABC_THRESHOLD_B_CRITICO: int = 5
"""5+ ocorrencias disciplinares = flag B (critico)."""

ABC_THRESHOLD_C_RISCO: float = 5.0
"""Media abaixo de 5.0 = flag C (alerta)."""

ABC_THRESHOLD_C_CRITICO: float = 3.0
"""Media abaixo de 3.0 = flag C (critico)."""

ABC_PESO_A: float = 0.3
"""Peso da dimensao A (Attendance) no score ABC."""

ABC_PESO_B: float = 0.3
"""Peso da dimensao B (Behavior) no score ABC."""

ABC_PESO_C: float = 0.4
"""Peso da dimensao C (Coursework) no score ABC."""

ABC_THRESHOLDS: Dict[str, Dict[str, float]] = {
    'A': {'risco': ABC_THRESHOLD_A_RISCO, 'critico': ABC_THRESHOLD_A_CRITICO},
    'B': {'risco': ABC_THRESHOLD_B_RISCO, 'critico': ABC_THRESHOLD_B_CRITICO},
    'C': {'risco': ABC_THRESHOLD_C_RISCO, 'critico': ABC_THRESHOLD_C_CRITICO},
}
"""Thresholds consolidados por dimensao ABC."""


# ============================================================
# CONSTANTES - GRAVIDADE DE OCORRENCIAS
# Extraidas de gerar_csvs_powerbi_ceo.py e pages/22_Ocorrencias.py
# IMPORTANTE: 'Media' sem acento (formato do CSV)
# ============================================================

GRAVIDADES: List[str] = ['Leve', 'Media', 'Grave']
"""Niveis de gravidade de ocorrencias. NAO alterar: CSV usa 'Media' sem acento."""

GRAVIDADE_PESO: Dict[str, int] = {
    'Leve': 1,
    'Media': 2,
    'Grave': 5,
}
"""Peso numerico de cada nivel de gravidade para calculos agregados."""


# ============================================================
# CONSTANTES - TIERS ABC
# ============================================================

TIER_NOMES: Dict[int, str] = {
    0: 'Universal',
    1: 'Atencao',
    2: 'Intervencao',
    3: 'Intensivo',
}
"""Mapeamento tier numerico -> nome descritivo."""


# ============================================================
# DATACLASS: ScoreProfessor
# ============================================================

@dataclass
class ScoreProfessor:
    """
    Score consolidado de um professor.

    Combina taxa de registro, qualidade de conteudo, tarefa e recencia
    para produzir um score final de 0 a 100 e uma classificacao de semaforo.

    Campos:
        professor: Nome completo do professor.
        unidade: Codigo da unidade (BV, CD, JG, CDR).
        serie: Serie principal em que leciona.
        disciplina: Disciplina principal (ou lista separada por virgula).
        aulas_registradas: Total de aulas registradas no SIGA.
        aulas_esperadas: Total de aulas esperadas pelo horario.
        conformidade_pct: Percentual de conformidade (registradas / esperadas * 100).
        com_conteudo_pct: Percentual de aulas com campo conteudo preenchido.
        semaforo: Classificacao visual (Verde, Amarelo, Vermelho, Cinza).
        score_final: Score composto de 0 a 100 (maior = melhor).
        taxa_tarefa_pct: Percentual de aulas com campo tarefa preenchido.
        recencia: Indice de recencia de 0 a 100 (100 = registrou hoje).
        dias_sem_registro: Dias desde o ultimo registro.
    """
    professor: str
    unidade: str
    serie: str
    disciplina: str
    aulas_registradas: int
    aulas_esperadas: int
    conformidade_pct: float
    com_conteudo_pct: float
    semaforo: str
    score_final: float
    taxa_tarefa_pct: float = 0.0
    recencia: float = 0.0
    dias_sem_registro: int = 0


# ============================================================
# DATACLASS: ScoreABC
# ============================================================

@dataclass
class ScoreABC:
    """
    Score ABC de alerta precoce para um aluno.

    Framework Attendance + Behavior + Coursework (validado internacionalmente).
    Identifica alunos em risco ANTES que fracassem academicamente.

    Campos:
        aluno_id: Identificador unico do aluno no SIGA.
        aluno_nome: Nome completo do aluno.
        unidade: Codigo da unidade (BV, CD, JG, CDR).
        serie: Serie do aluno (ex: '6o Ano', '1a Serie').
        turma: Identificador da turma.
        score_a: Score da dimensao A - Attendance (0 a 1, 1 = risco maximo).
        score_b: Score da dimensao B - Behavior (0 a 1, 1 = risco maximo).
        score_c: Score da dimensao C - Coursework (0 a 1, 1 = risco maximo).
        score_total: Score total ponderado (0 a 3, maior = mais risco).
        classificacao: Tier do aluno (Universal, Atencao, Intervencao, Intensivo).
        detalhes: Dicionario com valores brutos (freq_pct, num_ocorrencias, media_notas, flags).
    """
    aluno_id: int
    aluno_nome: str
    unidade: str
    serie: str
    turma: str
    score_a: float
    score_b: float
    score_c: float
    score_total: float
    classificacao: str
    detalhes: Dict = field(default_factory=dict)


# ============================================================
# DATACLASS: Alerta
# ============================================================

@dataclass
class Alerta:
    """
    Alerta gerado pelo sistema de monitoramento.

    Representa uma situacao que demanda atencao da coordenacao pedagogica.

    Campos:
        tipo: Codigo do alerta (VERMELHO, AMARELO, LARANJA, AZUL, ROSA,
              FREQ_CRITICA, NOTA_BAIXA, COMPORTAMENTO, ABC_RISCO).
        nivel: Nivel de urgencia (CRITICO, ATENCAO, INFO).
        mensagem: Descricao curta do alerta.
        detalhe: Informacao detalhada com valores e contexto.
        acao_sugerida: Recomendacao de acao para a coordenacao.
        data_geracao: Data/hora em que o alerta foi gerado.
        entidade: Tipo da entidade afetada (professor, aluno, turma, disciplina).
        unidade: Codigo da unidade (BV, CD, JG, CDR).
    """
    tipo: str
    nivel: str
    mensagem: str
    detalhe: str
    acao_sugerida: str
    data_geracao: datetime
    entidade: str
    unidade: str


# ============================================================
# FUNCOES DE CLASSIFICACAO
# ============================================================

def classificar_semaforo(conformidade_pct: float, conteudo_pct: float = 100.0) -> str:
    """
    Classifica o semaforo do professor com base na conformidade e conteudo.

    Logica extraida de pages/13_Semaforo_Professor.py:
        - Verde:    conformidade >= 80% E conteudo >= 60%
        - Amarelo:  conformidade >= 60%
        - Cinza:    conformidade == 0 (nenhum registro)
        - Vermelho: demais casos (conformidade < 60%)

    Args:
        conformidade_pct: Percentual de aulas registradas vs esperadas.
        conteudo_pct: Percentual de aulas com conteudo preenchido.

    Returns:
        String com a cor do semaforo: 'Verde', 'Amarelo', 'Vermelho' ou 'Cinza'.
    """
    if conformidade_pct == 0:
        return 'Cinza'
    if conformidade_pct >= SEMAFORO_VERDE_REGISTRO and conteudo_pct >= SEMAFORO_VERDE_CONTEUDO:
        return 'Verde'
    if conformidade_pct >= SEMAFORO_AMARELO_REGISTRO:
        return 'Amarelo'
    return 'Vermelho'


def classificar_nivel_score(score: float) -> str:
    """
    Classifica o nivel do score de risco do professor.

    Logica extraida de pages/14_Alertas_Inteligentes.py:
        - Critico:  score < 50 (CONFORMIDADE_CRITICO)
        - Atencao:  50 <= score < 70 (CONFORMIDADE_BAIXO)
        - Em Dia:   score >= 70

    Args:
        score: Score composto de 0 a 100.

    Returns:
        String: 'Critico', 'Atencao' ou 'Em Dia'.
    """
    if score < CONFORMIDADE_CRITICO:
        return 'Critico'
    if score < CONFORMIDADE_BAIXO:
        return 'Atencao'
    return 'Em Dia'


def classificar_conformidade(pct: float) -> str:
    """
    Classifica o nivel de conformidade baseado no percentual.

    Logica extraida de utils.py (status_conformidade):
        - Excelente: >= 95%
        - Bom:       >= 85%
        - Atencao:   >= 70%
        - Critico:   < 70%

    Args:
        pct: Percentual de conformidade.

    Returns:
        String: 'Excelente', 'Bom', 'Atencao' ou 'Critico'.
    """
    if pct >= CONFORMIDADE_EXCELENTE:
        return 'Excelente'
    if pct >= CONFORMIDADE_META:
        return 'Bom'
    if pct >= CONFORMIDADE_BAIXO:
        return 'Atencao'
    return 'Critico'


def calcular_score_professor(
    taxa_registro: float,
    taxa_conteudo: float,
    taxa_tarefa: float,
    recencia: float,
) -> float:
    """
    Calcula o score composto de risco do professor.

    Formula extraida de pages/14_Alertas_Inteligentes.py (calcular_score_risco):
        Score = 0.35 * taxa_registro + 0.25 * taxa_conteudo
              + 0.15 * taxa_tarefa + 0.25 * recencia

    Todos os parametros devem estar na escala 0-100.
    Quanto MAIOR o score, MELHOR o professor esta.

    Args:
        taxa_registro: Percentual de aulas registradas vs esperadas (0-100).
        taxa_conteudo: Percentual de aulas com conteudo preenchido (0-100).
        taxa_tarefa: Percentual de aulas com tarefa preenchida (0-100).
        recencia: Indice de recencia, 100 = registrou hoje, 0 = 14+ dias sem registro.

    Returns:
        Score de 0 a 100, arredondado para 1 casa decimal.
    """
    score = (
        PESO_TAXA_REGISTRO * min(taxa_registro, 100)
        + PESO_TAXA_CONTEUDO * taxa_conteudo
        + PESO_TAXA_TAREFA * taxa_tarefa
        + PESO_RECENCIA * recencia
    )
    return round(score, 1)


def classificar_abc(score_total: float) -> str:
    """
    Classifica o tier ABC com base no score total ponderado.

    Logica extraida de pages/23_Alerta_Precoce_ABC.py:
        O tier e determinado pelo NUMERO de flags ativas, nao pelo score numerico.
        Esta funcao converte o score ponderado (0-100) em classificacao de risco.

        - score >= 75:  'Intensivo'   (equivale a Tier 3, tipicamente 3 flags)
        - score >= 50:  'Intervencao' (equivale a Tier 2, tipicamente 2 flags)
        - score > 0:    'Atencao'     (equivale a Tier 1, tipicamente 1 flag)
        - score == 0:   'Universal'   (equivale a Tier 0, nenhuma flag)

    Args:
        score_total: Score ponderado ABC (0-100).

    Returns:
        String: 'Universal', 'Atencao', 'Intervencao' ou 'Intensivo'.
    """
    if score_total >= 75:
        return 'Intensivo'
    if score_total >= 50:
        return 'Intervencao'
    if score_total > 0:
        return 'Atencao'
    return 'Universal'


def classificar_abc_por_flags(num_flags: int) -> str:
    """
    Classifica o tier ABC pelo numero de flags ativas.

    Esta e a classificacao canonica usada em pages/23_Alerta_Precoce_ABC.py:
        - 3 flags (A+B+C): Tier 3 = 'Intensivo'
        - 2 flags:         Tier 2 = 'Intervencao'
        - 1 flag:          Tier 1 = 'Atencao'
        - 0 flags:         Tier 0 = 'Universal'

    Args:
        num_flags: Numero de dimensoes com flag ativa (0-3).

    Returns:
        String: 'Universal', 'Atencao', 'Intervencao' ou 'Intensivo'.
    """
    if num_flags >= 3:
        return 'Intensivo'
    if num_flags >= 2:
        return 'Intervencao'
    if num_flags >= 1:
        return 'Atencao'
    return 'Universal'


def calcular_scores_abc(
    freq_pct: float,
    num_ocorrencias: int,
    media_notas: float,
) -> Dict:
    """
    Calcula os scores individuais ABC e o score total ponderado.

    Logica extraida de pages/23_Alerta_Precoce_ABC.py (calcular_score_abc).
    Replica exatamente a funcao original, retornando um dict tipado.

    Args:
        freq_pct: Percentual de frequencia do aluno (0-100).
        num_ocorrencias: Numero de ocorrencias disciplinares.
        media_notas: Media geral das notas do aluno (0-10).

    Returns:
        Dict com chaves:
            score_a (float): Score da dimensao A normalizado (0-100).
            score_b (float): Score da dimensao B normalizado (0-100).
            score_c (float): Score da dimensao C normalizado (0-100).
            score_total (float): Score ponderado (0-100).
            flags (List[str]): Dimensoes com flag ativa ('A', 'B', 'C').
            tier (int): Tier de intervencao (0-3).
            classificacao (str): Nome do tier.
    """
    flags: List[str] = []

    # A - Attendance (30% do score)
    if freq_pct < ABC_THRESHOLD_A_CRITICO:
        score_a = 100.0
        flags.append('A')
    elif freq_pct < ABC_THRESHOLD_A_RISCO:
        score_a = 50.0
        flags.append('A')
    else:
        score_a = max(0.0, (100 - freq_pct) * 2)

    # B - Behavior (30% do score)
    if num_ocorrencias >= ABC_THRESHOLD_B_CRITICO:
        score_b = 100.0
        flags.append('B')
    elif num_ocorrencias >= ABC_THRESHOLD_B_RISCO:
        score_b = 50.0
        flags.append('B')
    else:
        score_b = min(100.0, num_ocorrencias * 20.0)

    # C - Coursework (40% do score)
    if media_notas < ABC_THRESHOLD_C_CRITICO:
        score_c = 100.0
        flags.append('C')
    elif media_notas < ABC_THRESHOLD_C_RISCO:
        score_c = 50.0
        flags.append('C')
    else:
        score_c = max(0.0, (10 - media_notas) * 10)

    score_total = score_a * ABC_PESO_A + score_b * ABC_PESO_B + score_c * ABC_PESO_C

    tier = min(len(flags), 3)
    classificacao = classificar_abc_por_flags(tier)

    return {
        'score_a': round(score_a, 1),
        'score_b': round(score_b, 1),
        'score_c': round(score_c, 1),
        'score_total': round(score_total, 1),
        'flags': flags,
        'tier': tier,
        'classificacao': classificacao,
    }


# ============================================================
# GERACAO DE ALERTAS
# ============================================================

def gerar_alerta_professor(score: ScoreProfessor) -> Optional[Alerta]:
    """
    Gera alerta para professor baseado no seu score.

    Regras de geracao (extraidas de pages/13 e 14):
        - Semaforo Vermelho ou score < 50: alerta CRITICO
        - Semaforo Amarelo ou score entre 50-70: alerta ATENCAO
        - Dias sem registro >= 7: alerta CRITICO (Professor Silencioso)
        - Dias sem registro >= 4: alerta ATENCAO
        - Semaforo Verde/Cinza sem outros problemas: sem alerta (retorna None)

    Args:
        score: Instancia de ScoreProfessor com os dados calculados.

    Returns:
        Instancia de Alerta ou None se o professor nao demanda atencao.
    """
    agora = datetime.now()

    # Prioridade 1: Professor silencioso (muitos dias sem registro)
    if score.dias_sem_registro >= DIAS_SEM_REGISTRO_URGENTE:
        return Alerta(
            tipo='VERMELHO',
            nivel='CRITICO',
            mensagem=f'Professor Silencioso: {score.professor}',
            detalhe=(
                f'{score.dias_sem_registro} dias sem registro. '
                f'Unidade {score.unidade}, {score.disciplina}.'
            ),
            acao_sugerida='Contatar professor IMEDIATAMENTE.',
            data_geracao=agora,
            entidade='professor',
            unidade=score.unidade,
        )

    # Prioridade 2: Semaforo vermelho ou score critico
    if score.semaforo == 'Vermelho' or score.score_final < CONFORMIDADE_CRITICO:
        return Alerta(
            tipo='VERMELHO',
            nivel='CRITICO',
            mensagem=f'Conformidade critica: {score.professor}',
            detalhe=(
                f'Conformidade {score.conformidade_pct:.0f}% '
                f'({score.aulas_registradas}/{score.aulas_esperadas} aulas). '
                f'Score {score.score_final:.0f}/100. '
                f'Unidade {score.unidade}, {score.disciplina}.'
            ),
            acao_sugerida='Reuniao com professor para plano de recuperacao de registros.',
            data_geracao=agora,
            entidade='professor',
            unidade=score.unidade,
        )

    # Prioridade 3: Dias sem registro em nivel de atencao
    if score.dias_sem_registro >= DIAS_SEM_REGISTRO_ATENCAO:
        return Alerta(
            tipo='AZUL',
            nivel='ATENCAO',
            mensagem=f'Registro pendente: {score.professor}',
            detalhe=(
                f'{score.dias_sem_registro} dias sem registro. '
                f'Conformidade atual {score.conformidade_pct:.0f}%. '
                f'Unidade {score.unidade}, {score.disciplina}.'
            ),
            acao_sugerida='Lembrar professor de lancar registros no SIGA.',
            data_geracao=agora,
            entidade='professor',
            unidade=score.unidade,
        )

    # Prioridade 4: Semaforo amarelo ou score em atencao
    if score.semaforo == 'Amarelo' or score.score_final < CONFORMIDADE_BAIXO:
        return Alerta(
            tipo='AMARELO',
            nivel='ATENCAO',
            mensagem=f'Conformidade em atencao: {score.professor}',
            detalhe=(
                f'Conformidade {score.conformidade_pct:.0f}% '
                f'(meta: {CONFORMIDADE_META}%). '
                f'Score {score.score_final:.0f}/100. '
                f'Unidade {score.unidade}, {score.disciplina}.'
            ),
            acao_sugerida='Monitorar e conversar com o professor.',
            data_geracao=agora,
            entidade='professor',
            unidade=score.unidade,
        )

    # Sem alerta necessario
    return None


def gerar_alerta_aluno(score: ScoreABC) -> Optional[Alerta]:
    """
    Gera alerta para aluno baseado no seu score ABC.

    Regras de geracao (extraidas de pages/23_Alerta_Precoce_ABC.py):
        - Tier 3 (Intensivo, 3 flags): alerta CRITICO
        - Tier 2 (Intervencao, 2 flags): alerta CRITICO
        - Tier 1 (Atencao, 1 flag): alerta ATENCAO
        - Tier 0 (Universal, 0 flags): sem alerta (retorna None)

    Args:
        score: Instancia de ScoreABC com os dados calculados.

    Returns:
        Instancia de Alerta ou None se o aluno nao demanda atencao.
    """
    agora = datetime.now()

    flags = score.detalhes.get('flags', [])
    tier = score.detalhes.get('tier', 0)

    if tier == 0:
        return None

    # Monta descricao das flags ativas
    partes_detalhe = []
    if 'A' in flags:
        freq = score.detalhes.get('freq_pct', 0)
        partes_detalhe.append(f'Frequencia {freq:.0f}%')
    if 'B' in flags:
        ocorr = score.detalhes.get('num_ocorrencias', 0)
        partes_detalhe.append(f'{ocorr} ocorrencias disciplinares')
    if 'C' in flags:
        media = score.detalhes.get('media_notas', 0)
        partes_detalhe.append(f'Media {media:.1f}')

    detalhe_flags = '; '.join(partes_detalhe) if partes_detalhe else ''

    if tier >= 3:
        return Alerta(
            tipo='ABC_RISCO',
            nivel='CRITICO',
            mensagem=f'Aluno em risco INTENSIVO: {score.aluno_nome}',
            detalhe=(
                f'Tier 3 - TODAS as dimensoes com flag (A+B+C). '
                f'{detalhe_flags}. '
                f'Score total: {score.score_total:.0f}. '
                f'{score.serie}, {score.turma}, unidade {score.unidade}.'
            ),
            acao_sugerida=(
                'Acompanhamento diario, acionar equipe multidisciplinar, '
                'reuniao URGENTE com familia.'
            ),
            data_geracao=agora,
            entidade='aluno',
            unidade=score.unidade,
        )

    if tier == 2:
        return Alerta(
            tipo='ABC_RISCO',
            nivel='CRITICO',
            mensagem=f'Aluno em risco de INTERVENCAO: {score.aluno_nome}',
            detalhe=(
                f'Tier 2 - 2 dimensoes com flag ({", ".join(flags)}). '
                f'{detalhe_flags}. '
                f'Score total: {score.score_total:.0f}. '
                f'{score.serie}, {score.turma}, unidade {score.unidade}.'
            ),
            acao_sugerida=(
                'Reuniao com familia, plano de intervencao individualizado.'
            ),
            data_geracao=agora,
            entidade='aluno',
            unidade=score.unidade,
        )

    # tier == 1
    return Alerta(
        tipo='ABC_RISCO',
        nivel='ATENCAO',
        mensagem=f'Aluno requer ATENCAO: {score.aluno_nome}',
        detalhe=(
            f'Tier 1 - 1 dimensao com flag ({", ".join(flags)}). '
            f'{detalhe_flags}. '
            f'Score total: {score.score_total:.0f}. '
            f'{score.serie}, {score.turma}, unidade {score.unidade}.'
        ),
        acao_sugerida=(
            'Monitoramento semanal, conversa com professor responsavel.'
        ),
        data_geracao=agora,
        entidade='aluno',
        unidade=score.unidade,
    )
