"""
Testes dos 3 modulos de fundacao do Sistema Pedagogico ELO 2026.

Modulos testados:
    - normalizacao.py  : Mapeamentos e funcoes de normalizacao
    - scoring.py       : Dataclasses de scoring, classificacao e alertas
    - shared_domain.py : Modelo de dominio canonico (unidades, series, traducoes)

Executar: pytest tests/test_fundacao.py -v
"""

import sys
import os

# Garante que o diretorio raiz do projeto esta no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

# ============================================================
# IMPORTS - normalizacao
# ============================================================
from normalizacao import (
    normalizar_serie,
    normalizar_disciplina,
    normalizar_nome_professor,
    normalizar_disciplina_fato,
    normalizar_disciplina_horario,
    normalizar_disciplina_sae,
    normalizar_serie_sae,
    serie_eh_fund_ii,
    UNIDADES,
    UNIDADES_NOMES,
    SERIES_FUND_II,
    SERIES_EM,
    ORDEM_SERIES,
    SERIE_NORMALIZACAO,
    DISCIPLINA_NORMALIZACAO,
    DISCIPLINA_NORM_FATO,
    GRADE_MAP_SAE,
)

# ============================================================
# IMPORTS - scoring
# ============================================================
from scoring import (
    ScoreProfessor,
    ScoreABC,
    Alerta,
    classificar_semaforo,
    classificar_nivel_score,
    classificar_conformidade,
    calcular_score_professor,
    classificar_abc,
    classificar_abc_por_flags,
    calcular_scores_abc,
    gerar_alerta_professor,
    gerar_alerta_aluno,
    CONFORMIDADE_META,
    CONFORMIDADE_BAIXO,
    CONFORMIDADE_CRITICO,
    CONFORMIDADE_EXCELENTE,
    GRAVIDADES,
    GRAVIDADE_PESO,
    TIER_NOMES,
    ABC_THRESHOLD_A_RISCO,
    ABC_THRESHOLD_A_CRITICO,
    ABC_THRESHOLD_B_RISCO,
    ABC_THRESHOLD_B_CRITICO,
    ABC_THRESHOLD_C_RISCO,
    ABC_THRESHOLD_C_CRITICO,
    DIAS_SEM_REGISTRO_ATENCAO,
    DIAS_SEM_REGISTRO_URGENTE,
)

# ============================================================
# IMPORTS - shared_domain
# ============================================================
from shared_domain import (
    Unidade,
    SerieUniversal,
    UNIDADES_CANONICAL,
    SERIES_UNIVERSAL,
    METAS_2026,
    META_TOTAL_2026,
    METAS_2026_POR_NOME_VAGAS,
    traduzir_unidade_vagas_para_pedagogico,
    traduzir_unidade_pedagogico_para_vagas,
    traduzir_serie_vagas_para_pedagogico,
    traduzir_serie_pedagogico_para_vagas,
    obter_unidade,
    obter_serie,
    listar_series_pedagogico,
    listar_series_vagas,
    listar_series_por_segmento,
    listar_series_intersecao,
    segmento_da_serie,
    nome_unidade_vagas_para_canonico,
)


# ################################################################
#
#  TESTES: normalizacao.py
#
# ################################################################


class TestNormalizarSerie:
    """Testes da funcao normalizar_serie e constantes de series."""

    def test_normalizar_serie_fund_ii_maiusculas(self):
        """Series do Fund II em maiusculas devem ser normalizadas."""
        assert normalizar_serie('6º ANO') == '6º Ano'
        assert normalizar_serie('7º ANO') == '7º Ano'
        assert normalizar_serie('8º ANO') == '8º Ano'
        assert normalizar_serie('9º ANO') == '9º Ano'

    def test_normalizar_serie_em_ano_medio(self):
        """Formato 'Xo Ano Medio' deve converter para 'Xa Serie'."""
        assert normalizar_serie('1º Ano Médio') == '1ª Série'
        assert normalizar_serie('2º Ano Médio') == '2ª Série'
        assert normalizar_serie('3º Ano Médio') == '3ª Série'

    def test_normalizar_serie_em_serie_em(self):
        """Formato 'Xa Serie EM' deve converter para 'Xa Serie'."""
        assert normalizar_serie('1ª Série EM') == '1ª Série'
        assert normalizar_serie('2ª Série EM') == '2ª Série'
        assert normalizar_serie('3ª Série EM') == '3ª Série'

    def test_normalizar_serie_ja_canonica(self):
        """Series ja no formato canonico devem ser retornadas inalteradas."""
        assert normalizar_serie('6º Ano') == '6º Ano'
        assert normalizar_serie('1ª Série') == '1ª Série'

    def test_normalizar_serie_passthrough_desconhecida(self):
        """Series desconhecidas devem passar direto (com strip)."""
        assert normalizar_serie('Turma Especial') == 'Turma Especial'
        assert normalizar_serie('  5º Ano  ') == '5º Ano'

    def test_normalizar_serie_vazia_ou_none(self):
        """Valores vazios ou None devem retornar o proprio valor."""
        assert normalizar_serie('') == ''
        assert normalizar_serie(None) is None

    def test_series_fund_ii_tem_4_itens(self):
        """SERIES_FUND_II deve ter exatamente 4 series (6o ao 9o Ano)."""
        assert len(SERIES_FUND_II) == 4
        assert SERIES_FUND_II == ['6º Ano', '7º Ano', '8º Ano', '9º Ano']

    def test_series_em_tem_3_itens(self):
        """SERIES_EM deve ter exatamente 3 series (1a a 3a Serie)."""
        assert len(SERIES_EM) == 3
        assert SERIES_EM == ['1ª Série', '2ª Série', '3ª Série']

    def test_ordem_series_completa(self):
        """ORDEM_SERIES deve ter 7 series (Fund II + EM)."""
        assert len(ORDEM_SERIES) == 7
        assert ORDEM_SERIES == SERIES_FUND_II + SERIES_EM


class TestNormalizarDisciplina:
    """Testes da funcao normalizar_disciplina."""

    def test_normalizar_disciplina_portugues(self):
        """'Portugues' deve normalizar para 'Lingua Portuguesa'."""
        assert normalizar_disciplina('Português') == 'Língua Portuguesa'

    def test_normalizar_disciplina_ciencias(self):
        """'Ciencias' deve normalizar para 'Ciencias Naturais'."""
        assert normalizar_disciplina('Ciências') == 'Ciências Naturais'

    def test_normalizar_disciplina_ingles(self):
        """Variantes de Ingles devem normalizar para 'Lingua Estrangeira Ingles'."""
        assert normalizar_disciplina('Inglês') == 'Língua Estrangeira Inglês'
        assert normalizar_disciplina('Língua Inglesa') == 'Língua Estrangeira Inglês'

    def test_normalizar_disciplina_abreviacoes_em(self):
        """Abreviacoes do EM (BIO 2, QUIM 2, etc.) devem normalizar."""
        assert normalizar_disciplina('BIO 2') == 'Biologia 2'
        assert normalizar_disciplina('QUIM 2') == 'Química 2'
        assert normalizar_disciplina('FISIC 2') == 'Física 2'
        assert normalizar_disciplina('matem 2') == 'Matemática 2'

    def test_normalizar_disciplina_passthrough(self):
        """Disciplinas ja canonicas ou desconhecidas devem passar direto."""
        assert normalizar_disciplina('Matemática') == 'Matemática'
        assert normalizar_disciplina('Arte') == 'Arte'
        assert normalizar_disciplina('Educação Física') == 'Educação Física'

    def test_normalizar_disciplina_vazia_ou_none(self):
        """Valores vazios ou None devem retornar o proprio valor."""
        assert normalizar_disciplina('') == ''
        assert normalizar_disciplina(None) is None

    def test_normalizar_disciplina_fisica_ii(self):
        """'Fisica II' (romano) deve normalizar para 'Fisica 2'."""
        assert normalizar_disciplina('Física II') == 'Física 2'


class TestNormalizarNomeProfessor:
    """Testes da funcao normalizar_nome_professor."""

    def test_normalizar_professor_com_sufixo_bv(self):
        """Remove sufixo '- BV - 2026' e converte para maiusculas."""
        assert normalizar_nome_professor('João Silva - BV - 2026') == 'JOÃO SILVA'

    def test_normalizar_professor_com_sufixo_cdr(self):
        """Remove sufixo '- CDR - 2025'."""
        assert normalizar_nome_professor('Maria Souza - CDR - 2025') == 'MARIA SOUZA'

    def test_normalizar_professor_com_sufixo_teen(self):
        """Remove sufixo '- TEEN 1 - 2026'."""
        assert normalizar_nome_professor('Pedro Lima - TEEN 1 - 2026') == 'PEDRO LIMA'

    def test_normalizar_professor_sem_sufixo(self):
        """Nome sem sufixo deve apenas converter para maiusculas."""
        assert normalizar_nome_professor('ana costa') == 'ANA COSTA'

    def test_normalizar_professor_espacos_multiplos(self):
        """Espacos multiplos devem ser colapsados."""
        assert normalizar_nome_professor('jose   da   silva') == 'JOSE DA SILVA'

    def test_normalizar_professor_vazio_ou_none(self):
        """Valores vazios ou None devem retornar string vazia."""
        assert normalizar_nome_professor('') == ''
        assert normalizar_nome_professor(None) == ''


class TestNormalizarDisciplinaFato:
    """Testes da funcao normalizar_disciplina_fato."""

    def test_normalizar_fato_fisica_2(self):
        """'Fisica 2' deve normalizar para 'Fisica' (nome base para progressao)."""
        assert normalizar_disciplina_fato('Física 2') == 'Física'

    def test_normalizar_fato_biologia_2(self):
        """'Biologia 2' deve normalizar para 'Biologia'."""
        assert normalizar_disciplina_fato('Biologia 2') == 'Biologia'

    def test_normalizar_fato_matematica_3(self):
        """'Matematica 3' deve normalizar para 'Matematica'."""
        assert normalizar_disciplina_fato('Matemática 3') == 'Matemática'

    def test_normalizar_fato_lingua_portuguesa_2(self):
        """'Lingua Portuguesa 2' deve normalizar para 'Lingua Portuguesa'."""
        assert normalizar_disciplina_fato('Língua Portuguesa 2') == 'Língua Portuguesa'

    def test_normalizar_fato_passthrough_base(self):
        """Disciplinas base (sem numero) devem passar direto."""
        assert normalizar_disciplina_fato('Arte') == 'Arte'
        assert normalizar_disciplina_fato('Filosofia') == 'Filosofia'
        assert normalizar_disciplina_fato('Matemática') == 'Matemática'

    def test_normalizar_fato_vazia_ou_none(self):
        """Valores vazios ou None devem retornar o proprio valor."""
        assert normalizar_disciplina_fato('') == ''
        assert normalizar_disciplina_fato(None) is None


class TestConstantesUnidades:
    """Testes das constantes de unidades em normalizacao.py."""

    def test_unidades_tem_4_itens(self):
        """UNIDADES deve ter exatamente 4 codigos."""
        assert len(UNIDADES) == 4

    def test_unidades_codigos_corretos(self):
        """UNIDADES deve conter BV, CD, JG, CDR."""
        assert set(UNIDADES) == {'BV', 'CD', 'JG', 'CDR'}

    def test_unidades_nomes_mapeamento(self):
        """UNIDADES_NOMES deve mapear codigos para nomes por extenso."""
        assert UNIDADES_NOMES['BV'] == 'Boa Viagem'
        assert UNIDADES_NOMES['CD'] == 'Candeias'
        assert UNIDADES_NOMES['JG'] == 'Janga'
        assert UNIDADES_NOMES['CDR'] == 'Cordeiro'


class TestFuncoesAuxiliaresNormalizacao:
    """Testes de funcoes auxiliares do modulo normalizacao."""

    def test_normalizar_serie_sae_grade_ids(self):
        """Grade IDs do SAE (10-16) devem converter para series canonicas."""
        assert normalizar_serie_sae(10) == '6º Ano'
        assert normalizar_serie_sae(13) == '9º Ano'
        assert normalizar_serie_sae(14) == '1ª Série'
        assert normalizar_serie_sae(16) == '3ª Série'

    def test_normalizar_serie_sae_invalido(self):
        """Grade IDs invalidos ou None devem retornar None."""
        assert normalizar_serie_sae(99) is None
        assert normalizar_serie_sae(None) is None

    def test_serie_eh_fund_ii(self):
        """Verifica classificacao correta de series como Fund II ou nao."""
        assert serie_eh_fund_ii('6º Ano') is True
        assert serie_eh_fund_ii('9º Ano') is True
        assert serie_eh_fund_ii('1ª Série') is False
        assert serie_eh_fund_ii('3ª Série') is False

    def test_normalizar_disciplina_sae(self):
        """Disciplinas do SAE Digital devem normalizar para canonico SIGA."""
        assert normalizar_disciplina_sae('Ciências') == 'Ciências Naturais'
        assert normalizar_disciplina_sae('Artes') == 'Arte'
        assert normalizar_disciplina_sae('Língua Inglesa') == 'Língua Estrangeira Inglês'
        assert normalizar_disciplina_sae('Matemática') == 'Matemática'  # passthrough

    def test_normalizar_disciplina_horario(self):
        """Disciplinas numeradas do horario (slots EM) normalizam para base."""
        assert normalizar_disciplina_horario('Matemática 1') == 'Matemática'
        assert normalizar_disciplina_horario('Matemática 3') == 'Matemática'
        assert normalizar_disciplina_horario('Física 1') == 'Física'
        assert normalizar_disciplina_horario('Arte') == 'Arte'  # passthrough


# ################################################################
#
#  TESTES: scoring.py
#
# ################################################################


class TestConstantesScoring:
    """Testes das constantes do modulo scoring."""

    def test_conformidade_meta_valor(self):
        """CONFORMIDADE_META deve ser 85 (meta institucional)."""
        assert CONFORMIDADE_META == 85

    def test_conformidade_baixo_valor(self):
        """CONFORMIDADE_BAIXO deve ser 70."""
        assert CONFORMIDADE_BAIXO == 70

    def test_conformidade_critico_valor(self):
        """CONFORMIDADE_CRITICO deve ser 50."""
        assert CONFORMIDADE_CRITICO == 50

    def test_conformidade_excelente_valor(self):
        """CONFORMIDADE_EXCELENTE deve ser 95."""
        assert CONFORMIDADE_EXCELENTE == 95

    def test_gravidades_valores(self):
        """GRAVIDADES deve ter 3 niveis: Leve, Media (sem acento), Grave."""
        assert GRAVIDADES == ['Leve', 'Media', 'Grave']
        # IMPORTANTE: 'Media' sem acento conforme formato do CSV
        assert 'Média' not in GRAVIDADES

    def test_gravidade_pesos(self):
        """Pesos de gravidade: Leve=1, Media=2, Grave=5."""
        assert GRAVIDADE_PESO['Leve'] == 1
        assert GRAVIDADE_PESO['Media'] == 2
        assert GRAVIDADE_PESO['Grave'] == 5

    def test_tier_nomes_completo(self):
        """TIER_NOMES deve mapear 0-3 para os 4 niveis."""
        assert TIER_NOMES[0] == 'Universal'
        assert TIER_NOMES[1] == 'Atencao'
        assert TIER_NOMES[2] == 'Intervencao'
        assert TIER_NOMES[3] == 'Intensivo'
        assert len(TIER_NOMES) == 4


class TestClassificarSemaforo:
    """Testes da funcao classificar_semaforo."""

    def test_semaforo_verde(self):
        """Conformidade >= 80 E conteudo >= 60 => Verde."""
        assert classificar_semaforo(80, 60) == 'Verde'
        assert classificar_semaforo(100, 100) == 'Verde'
        assert classificar_semaforo(95, 75) == 'Verde'

    def test_semaforo_verde_limite_conteudo(self):
        """Conformidade alta mas conteudo < 60 => NAO Verde (Amarelo)."""
        assert classificar_semaforo(85, 59) == 'Amarelo'
        assert classificar_semaforo(90, 50) == 'Amarelo'

    def test_semaforo_amarelo(self):
        """Conformidade >= 60 (mas nao atinge Verde) => Amarelo."""
        assert classificar_semaforo(60, 50) == 'Amarelo'
        assert classificar_semaforo(70, 30) == 'Amarelo'
        assert classificar_semaforo(79, 100) == 'Amarelo'

    def test_semaforo_vermelho(self):
        """Conformidade < 60 (e > 0) => Vermelho."""
        assert classificar_semaforo(59, 100) == 'Vermelho'
        assert classificar_semaforo(30, 50) == 'Vermelho'
        assert classificar_semaforo(1, 0) == 'Vermelho'

    def test_semaforo_cinza(self):
        """Conformidade == 0 (nenhum registro) => Cinza."""
        assert classificar_semaforo(0, 0) == 'Cinza'
        assert classificar_semaforo(0, 100) == 'Cinza'

    def test_semaforo_conteudo_default(self):
        """Conteudo tem default 100, entao conformidade alta sozinha => Verde."""
        assert classificar_semaforo(80) == 'Verde'
        assert classificar_semaforo(100) == 'Verde'


class TestClassificarABCPorFlags:
    """Testes da funcao classificar_abc_por_flags."""

    def test_zero_flags_universal(self):
        """0 flags = Tier 0 = Universal (sem risco)."""
        assert classificar_abc_por_flags(0) == 'Universal'

    def test_uma_flag_atencao(self):
        """1 flag = Tier 1 = Atencao."""
        assert classificar_abc_por_flags(1) == 'Atencao'

    def test_duas_flags_intervencao(self):
        """2 flags = Tier 2 = Intervencao."""
        assert classificar_abc_por_flags(2) == 'Intervencao'

    def test_tres_flags_intensivo(self):
        """3 flags = Tier 3 = Intensivo."""
        assert classificar_abc_por_flags(3) == 'Intensivo'

    def test_mais_que_tres_flags_intensivo(self):
        """Mais de 3 flags (defensivo) = Intensivo."""
        assert classificar_abc_por_flags(5) == 'Intensivo'


class TestCalcularScoresABC:
    """Testes da funcao calcular_scores_abc."""

    def test_aluno_bom_baixo_risco(self):
        """Aluno com alta frequencia, 0 ocorrencias, nota boa => baixo risco."""
        resultado = calcular_scores_abc(
            freq_pct=95.0,
            num_ocorrencias=0,
            media_notas=8.0,
        )
        assert resultado['flags'] == []
        assert resultado['tier'] == 0
        assert resultado['classificacao'] == 'Universal'
        # Score total deve ser baixo (pouco risco)
        assert resultado['score_total'] < 30

    def test_aluno_risco_total_3_flags(self):
        """Aluno com baixa freq, muitas ocorrencias, nota ruim => 3 flags, Intensivo."""
        resultado = calcular_scores_abc(
            freq_pct=60.0,       # < 75 (critico A)
            num_ocorrencias=10,  # >= 5 (critico B)
            media_notas=2.0,     # < 3.0 (critico C)
        )
        assert 'A' in resultado['flags']
        assert 'B' in resultado['flags']
        assert 'C' in resultado['flags']
        assert len(resultado['flags']) == 3
        assert resultado['tier'] == 3
        assert resultado['classificacao'] == 'Intensivo'
        # Scores individuais devem ser 100 (todos criticos)
        assert resultado['score_a'] == 100.0
        assert resultado['score_b'] == 100.0
        assert resultado['score_c'] == 100.0
        # Score total = 100*0.3 + 100*0.3 + 100*0.4 = 100
        assert resultado['score_total'] == 100.0

    def test_aluno_risco_parcial_1_flag_frequencia(self):
        """Aluno com frequencia em risco (75-85%) mas resto ok => 1 flag A."""
        resultado = calcular_scores_abc(
            freq_pct=80.0,       # < 85 (risco A) mas >= 75
            num_ocorrencias=0,
            media_notas=7.0,
        )
        assert resultado['flags'] == ['A']
        assert resultado['tier'] == 1
        assert resultado['classificacao'] == 'Atencao'
        assert resultado['score_a'] == 50.0  # nivel risco (nao critico)

    def test_aluno_risco_parcial_2_flags(self):
        """Aluno com freq baixa e nota baixa => 2 flags, Intervencao."""
        resultado = calcular_scores_abc(
            freq_pct=80.0,       # flag A (risco)
            num_ocorrencias=0,   # sem flag B
            media_notas=4.0,     # flag C (risco, < 5.0)
        )
        assert 'A' in resultado['flags']
        assert 'C' in resultado['flags']
        assert 'B' not in resultado['flags']
        assert resultado['tier'] == 2
        assert resultado['classificacao'] == 'Intervencao'

    def test_aluno_score_b_risco(self):
        """Aluno com 2-4 ocorrencias disciplinares => flag B em nivel risco."""
        resultado = calcular_scores_abc(
            freq_pct=95.0,
            num_ocorrencias=3,   # >= 2 e < 5 (risco B)
            media_notas=8.0,
        )
        assert resultado['flags'] == ['B']
        assert resultado['score_b'] == 50.0

    def test_aluno_score_c_critico(self):
        """Aluno com media < 3.0 => flag C critico, score_c = 100."""
        resultado = calcular_scores_abc(
            freq_pct=95.0,
            num_ocorrencias=0,
            media_notas=2.5,  # < 3.0 (critico C)
        )
        assert 'C' in resultado['flags']
        assert resultado['score_c'] == 100.0


class TestScoreProfessorDataclass:
    """Testes da dataclass ScoreProfessor."""

    def test_instanciar_score_professor(self):
        """ScoreProfessor pode ser instanciada com campos obrigatorios."""
        score = ScoreProfessor(
            professor='JOAO SILVA',
            unidade='BV',
            serie='6º Ano',
            disciplina='Matemática',
            aulas_registradas=40,
            aulas_esperadas=50,
            conformidade_pct=80.0,
            com_conteudo_pct=70.0,
            semaforo='Verde',
            score_final=75.0,
        )
        assert score.professor == 'JOAO SILVA'
        assert score.unidade == 'BV'
        assert score.conformidade_pct == 80.0
        assert score.semaforo == 'Verde'

    def test_score_professor_defaults(self):
        """Campos opcionais devem ter defaults corretos."""
        score = ScoreProfessor(
            professor='ANA COSTA',
            unidade='CD',
            serie='7º Ano',
            disciplina='Ciências Naturais',
            aulas_registradas=30,
            aulas_esperadas=40,
            conformidade_pct=75.0,
            com_conteudo_pct=60.0,
            semaforo='Amarelo',
            score_final=65.0,
        )
        assert score.taxa_tarefa_pct == 0.0
        assert score.recencia == 0.0
        assert score.dias_sem_registro == 0


class TestGerarAlertaProfessor:
    """Testes da funcao gerar_alerta_professor."""

    def test_alerta_professor_vermelho_score_baixo(self):
        """Professor com score < 50 deve gerar alerta CRITICO."""
        score = ScoreProfessor(
            professor='PROFESSOR CRITICO',
            unidade='BV',
            serie='8º Ano',
            disciplina='Física',
            aulas_registradas=10,
            aulas_esperadas=50,
            conformidade_pct=20.0,
            com_conteudo_pct=30.0,
            semaforo='Vermelho',
            score_final=25.0,
        )
        alerta = gerar_alerta_professor(score)
        assert alerta is not None
        assert isinstance(alerta, Alerta)
        assert alerta.nivel == 'CRITICO'
        assert alerta.tipo == 'VERMELHO'
        assert alerta.entidade == 'professor'
        assert alerta.unidade == 'BV'

    def test_sem_alerta_professor_verde_score_alto(self):
        """Professor Verde com score alto nao deve gerar alerta."""
        score = ScoreProfessor(
            professor='PROFESSOR BOM',
            unidade='CD',
            serie='9º Ano',
            disciplina='Matemática',
            aulas_registradas=48,
            aulas_esperadas=50,
            conformidade_pct=96.0,
            com_conteudo_pct=90.0,
            semaforo='Verde',
            score_final=92.0,
        )
        alerta = gerar_alerta_professor(score)
        assert alerta is None

    def test_alerta_professor_silencioso(self):
        """Professor com >= 7 dias sem registro => alerta CRITICO (Professor Silencioso)."""
        score = ScoreProfessor(
            professor='PROFESSOR AUSENTE',
            unidade='JG',
            serie='1ª Série',
            disciplina='Biologia',
            aulas_registradas=30,
            aulas_esperadas=40,
            conformidade_pct=75.0,
            com_conteudo_pct=60.0,
            semaforo='Amarelo',
            score_final=70.0,
            dias_sem_registro=10,
        )
        alerta = gerar_alerta_professor(score)
        assert alerta is not None
        assert alerta.nivel == 'CRITICO'
        assert 'Silencioso' in alerta.mensagem

    def test_alerta_professor_atencao_dias_sem_registro(self):
        """Professor com 4-6 dias sem registro => alerta ATENCAO."""
        score = ScoreProfessor(
            professor='PROFESSOR PENDENTE',
            unidade='CDR',
            serie='2ª Série',
            disciplina='Química',
            aulas_registradas=35,
            aulas_esperadas=40,
            conformidade_pct=87.5,
            com_conteudo_pct=70.0,
            semaforo='Verde',
            score_final=80.0,
            dias_sem_registro=5,
        )
        alerta = gerar_alerta_professor(score)
        assert alerta is not None
        assert alerta.nivel == 'ATENCAO'
        assert alerta.tipo == 'AZUL'

    def test_alerta_professor_amarelo(self):
        """Professor Amarelo com score entre 50-70 => alerta ATENCAO."""
        score = ScoreProfessor(
            professor='PROFESSOR MEDIANO',
            unidade='BV',
            serie='3ª Série',
            disciplina='Geografia',
            aulas_registradas=30,
            aulas_esperadas=50,
            conformidade_pct=60.0,
            com_conteudo_pct=40.0,
            semaforo='Amarelo',
            score_final=55.0,
        )
        alerta = gerar_alerta_professor(score)
        assert alerta is not None
        assert alerta.nivel == 'ATENCAO'
        assert alerta.tipo == 'AMARELO'


class TestCalcularScoreProfessor:
    """Testes da funcao calcular_score_professor."""

    def test_score_professor_maximo(self):
        """Todas as metricas em 100 => score = 100."""
        score = calcular_score_professor(100, 100, 100, 100)
        assert score == 100.0

    def test_score_professor_zero(self):
        """Todas as metricas em 0 => score = 0."""
        score = calcular_score_professor(0, 0, 0, 0)
        assert score == 0.0

    def test_score_professor_pesos_corretos(self):
        """Verifica que os pesos sao aplicados corretamente."""
        # Apenas taxa_registro = 100, resto = 0 => 35
        assert calcular_score_professor(100, 0, 0, 0) == 35.0
        # Apenas taxa_conteudo = 100, resto = 0 => 25
        assert calcular_score_professor(0, 100, 0, 0) == 25.0
        # Apenas taxa_tarefa = 100, resto = 0 => 15
        assert calcular_score_professor(0, 0, 100, 0) == 15.0
        # Apenas recencia = 100, resto = 0 => 25
        assert calcular_score_professor(0, 0, 0, 100) == 25.0


class TestClassificarConformidade:
    """Testes da funcao classificar_conformidade."""

    def test_excelente(self):
        assert classificar_conformidade(95) == 'Excelente'
        assert classificar_conformidade(100) == 'Excelente'

    def test_bom(self):
        assert classificar_conformidade(85) == 'Bom'
        assert classificar_conformidade(94.9) == 'Bom'

    def test_atencao(self):
        assert classificar_conformidade(70) == 'Atencao'
        assert classificar_conformidade(84.9) == 'Atencao'

    def test_critico(self):
        assert classificar_conformidade(69.9) == 'Critico'
        assert classificar_conformidade(0) == 'Critico'


class TestClassificarNivelScore:
    """Testes da funcao classificar_nivel_score."""

    def test_critico(self):
        assert classificar_nivel_score(0) == 'Critico'
        assert classificar_nivel_score(49.9) == 'Critico'

    def test_atencao(self):
        assert classificar_nivel_score(50) == 'Atencao'
        assert classificar_nivel_score(69.9) == 'Atencao'

    def test_em_dia(self):
        assert classificar_nivel_score(70) == 'Em Dia'
        assert classificar_nivel_score(100) == 'Em Dia'


class TestGerarAlertaAluno:
    """Testes da funcao gerar_alerta_aluno."""

    def test_aluno_universal_sem_alerta(self):
        """Aluno Universal (tier 0) nao gera alerta."""
        score = ScoreABC(
            aluno_id=1, aluno_nome='ALUNO BOM', unidade='BV',
            serie='6º Ano', turma='A', score_a=5.0, score_b=0.0,
            score_c=10.0, score_total=5.0, classificacao='Universal',
            detalhes={'flags': [], 'tier': 0, 'freq_pct': 95, 'num_ocorrencias': 0, 'media_notas': 8},
        )
        assert gerar_alerta_aluno(score) is None

    def test_aluno_atencao_alerta(self):
        """Aluno Atencao (tier 1) gera alerta ATENCAO."""
        score = ScoreABC(
            aluno_id=2, aluno_nome='ALUNO ATENCAO', unidade='CD',
            serie='7º Ano', turma='B', score_a=50.0, score_b=0.0,
            score_c=10.0, score_total=25.0, classificacao='Atencao',
            detalhes={'flags': ['A'], 'tier': 1, 'freq_pct': 80, 'num_ocorrencias': 0, 'media_notas': 7},
        )
        alerta = gerar_alerta_aluno(score)
        assert alerta is not None
        assert alerta.nivel == 'ATENCAO'

    def test_aluno_intensivo_alerta_critico(self):
        """Aluno Intensivo (tier 3) gera alerta CRITICO."""
        score = ScoreABC(
            aluno_id=3, aluno_nome='ALUNO RISCO', unidade='JG',
            serie='8º Ano', turma='C', score_a=100.0, score_b=100.0,
            score_c=100.0, score_total=100.0, classificacao='Intensivo',
            detalhes={'flags': ['A', 'B', 'C'], 'tier': 3,
                      'freq_pct': 60, 'num_ocorrencias': 10, 'media_notas': 2},
        )
        alerta = gerar_alerta_aluno(score)
        assert alerta is not None
        assert alerta.nivel == 'CRITICO'
        assert 'INTENSIVO' in alerta.mensagem


# ################################################################
#
#  TESTES: shared_domain.py
#
# ################################################################


class TestUnidadesCanonical:
    """Testes do dicionario UNIDADES_CANONICAL."""

    def test_unidades_canonical_tem_4_entradas(self):
        """UNIDADES_CANONICAL deve ter exatamente 4 unidades."""
        assert len(UNIDADES_CANONICAL) == 4

    def test_unidades_canonical_codigos(self):
        """As 4 chaves devem ser BV, CD, JG, CDR."""
        assert set(UNIDADES_CANONICAL.keys()) == {'BV', 'CD', 'JG', 'CDR'}

    def test_unidade_bv(self):
        """Unidade BV deve ter dados corretos."""
        bv = UNIDADES_CANONICAL['BV']
        assert isinstance(bv, Unidade)
        assert bv.nome == 'Boa Viagem'
        assert bv.codigo_vagas == '01-BV'
        assert bv.meta_2026 == 1250
        assert bv.periodo_api_siga == 80

    def test_unidade_cd_nomes_diferentes(self):
        """Unidade CD: nome canonico='Candeias', nome vagas='Jaboatao'."""
        cd = UNIDADES_CANONICAL['CD']
        assert cd.nome == 'Candeias'
        assert cd.nome_vagas == 'Jaboatao'
        assert cd.cidade == 'Jaboatao dos Guararapes'

    def test_unidade_jg_nomes_diferentes(self):
        """Unidade JG: nome canonico='Janga', nome vagas='Paulista'."""
        jg = UNIDADES_CANONICAL['JG']
        assert jg.nome == 'Janga'
        assert jg.nome_vagas == 'Paulista'
        assert jg.cidade == 'Paulista'

    def test_unidades_frozen(self):
        """Unidades devem ser imutaveis (frozen dataclass)."""
        with pytest.raises(AttributeError):
            UNIDADES_CANONICAL['BV'].nome = 'Outro Nome'


class TestTraduzirUnidadeVagasParaPedagogico:
    """Testes da funcao traduzir_unidade_vagas_para_pedagogico."""

    def test_traduzir_por_codigo_vagas(self):
        """Codigo vagas '02-CD' deve traduzir para 'CD'."""
        assert traduzir_unidade_vagas_para_pedagogico('01-BV') == 'BV'
        assert traduzir_unidade_vagas_para_pedagogico('02-CD') == 'CD'
        assert traduzir_unidade_vagas_para_pedagogico('03-JG') == 'JG'
        assert traduzir_unidade_vagas_para_pedagogico('04-CDR') == 'CDR'

    def test_traduzir_por_nome_vagas_jaboatao(self):
        """Nome vagas 'Jaboatao' deve traduzir para 'CD'."""
        assert traduzir_unidade_vagas_para_pedagogico('Jaboatao') == 'CD'

    def test_traduzir_por_nome_vagas_paulista(self):
        """Nome vagas 'Paulista' deve traduzir para 'JG'."""
        assert traduzir_unidade_vagas_para_pedagogico('Paulista') == 'JG'

    def test_traduzir_por_nome_canonico(self):
        """Nome canonico 'Candeias' deve traduzir para 'CD'."""
        assert traduzir_unidade_vagas_para_pedagogico('Candeias') == 'CD'
        assert traduzir_unidade_vagas_para_pedagogico('Janga') == 'JG'

    def test_traduzir_por_codigo_pedagogico(self):
        """Codigo pedagogico 'BV' deve retornar 'BV' (passthrough)."""
        assert traduzir_unidade_vagas_para_pedagogico('BV') == 'BV'

    def test_traduzir_valor_desconhecido(self):
        """Valor desconhecido deve retornar None."""
        assert traduzir_unidade_vagas_para_pedagogico('Inexistente') is None
        assert traduzir_unidade_vagas_para_pedagogico('') is None
        assert traduzir_unidade_vagas_para_pedagogico(None) is None

    def test_traduzir_jaboatao_sem_acento(self):
        """'Jaboatao' (sem acento, como armazenado) deve funcionar."""
        # O nome_vagas armazenado e 'Jaboatao' sem acento
        assert traduzir_unidade_vagas_para_pedagogico('Jaboatao') == 'CD'


class TestSeriesUniversal:
    """Testes do dicionario SERIES_UNIVERSAL."""

    def test_series_universal_tem_16_entradas(self):
        """SERIES_UNIVERSAL deve ter exatamente 16 series."""
        assert len(SERIES_UNIVERSAL) == 16

    def test_series_universal_segmentos(self):
        """Deve ter 4 segmentos: Ed. Infantil, Fund. I, Fund. II, Ens. Medio."""
        segmentos = set(s.segmento for s in SERIES_UNIVERSAL.values())
        assert segmentos == {'Ed. Infantil', 'Fund. I', 'Fund. II', 'Ens. Médio'}

    def test_series_universal_coberta_pedagogico(self):
        """Exatamente 7 series devem ser cobertas pelo pedagogico."""
        cobertas = [s for s in SERIES_UNIVERSAL.values() if s.coberta_pedagogico]
        assert len(cobertas) == 7

    def test_series_universal_todas_cobertas_vagas(self):
        """Todas as 16 series devem ser cobertas pelo sistema de vagas."""
        cobertas = [s for s in SERIES_UNIVERSAL.values() if s.coberta_vagas]
        assert len(cobertas) == 16


class TestListarSeries:
    """Testes das funcoes listar_series_*."""

    def test_listar_series_pedagogico_7_series(self):
        """listar_series_pedagogico deve retornar exatamente 7 series."""
        series = listar_series_pedagogico()
        assert len(series) == 7
        assert '6º Ano' in series
        assert '9º Ano' in series
        assert '1ª Série' in series
        assert '3ª Série' in series

    def test_listar_series_pedagogico_ordem(self):
        """Series pedagogicas devem estar na ordem correta (6o ao 3a)."""
        series = listar_series_pedagogico()
        assert series[0] == '6º Ano'
        assert series[3] == '9º Ano'
        assert series[4] == '1ª Série'
        assert series[6] == '3ª Série'

    def test_listar_series_vagas_16_series(self):
        """listar_series_vagas deve retornar exatamente 16 series."""
        series = listar_series_vagas()
        assert len(series) == 16

    def test_listar_series_vagas_inclui_infantil(self):
        """Series de vagas devem incluir Ed. Infantil."""
        series = listar_series_vagas()
        assert 'Infantil II' in series
        assert 'Infantil V' in series

    def test_listar_series_intersecao(self):
        """Intersecao deve retornar as 7 series presentes em ambos os sistemas."""
        series = listar_series_intersecao()
        assert len(series) == 7
        assert series == listar_series_pedagogico()

    def test_listar_series_por_segmento_fund_ii(self):
        """Segmento Fund. II deve ter 4 series."""
        series = listar_series_por_segmento('Fund. II')
        assert len(series) == 4
        assert series == ['6º Ano', '7º Ano', '8º Ano', '9º Ano']

    def test_listar_series_por_segmento_anos_finais(self):
        """'Anos Finais' (nome pedagogico) deve resolver para Fund. II."""
        series = listar_series_por_segmento('Anos Finais')
        assert len(series) == 4


class TestMetasEObterUnidade:
    """Testes de metas e funcao obter_unidade."""

    def test_meta_total_2026(self):
        """META_TOTAL_2026 deve ser 4100."""
        assert META_TOTAL_2026 == 4100

    def test_metas_somam_total(self):
        """Soma das metas individuais deve igualar META_TOTAL_2026."""
        assert sum(METAS_2026.values()) == META_TOTAL_2026

    def test_metas_por_unidade(self):
        """Metas individuais devem estar corretas."""
        assert METAS_2026['BV'] == 1250
        assert METAS_2026['CD'] == 1200
        assert METAS_2026['JG'] == 850
        assert METAS_2026['CDR'] == 800

    def test_obter_unidade_por_codigo(self):
        """obter_unidade('BV') deve retornar Unidade com nome='Boa Viagem'."""
        unidade = obter_unidade('BV')
        assert unidade is not None
        assert isinstance(unidade, Unidade)
        assert unidade.nome == 'Boa Viagem'
        assert unidade.codigo == 'BV'

    def test_obter_unidade_por_nome_vagas(self):
        """obter_unidade('Jaboatao') deve retornar CD (Candeias)."""
        unidade = obter_unidade('Jaboatao')
        assert unidade is not None
        assert unidade.codigo == 'CD'
        assert unidade.nome == 'Candeias'

    def test_obter_unidade_por_codigo_vagas(self):
        """obter_unidade('03-JG') deve retornar JG (Janga)."""
        unidade = obter_unidade('03-JG')
        assert unidade is not None
        assert unidade.codigo == 'JG'
        assert unidade.nome == 'Janga'

    def test_obter_unidade_inexistente(self):
        """obter_unidade com valor inexistente deve retornar None."""
        assert obter_unidade('XX') is None
        assert obter_unidade('') is None
        assert obter_unidade(None) is None

    def test_metas_por_nome_vagas(self):
        """METAS_2026_POR_NOME_VAGAS deve indexar por nome do sistema Vagas."""
        assert METAS_2026_POR_NOME_VAGAS['Boa Viagem'] == 1250
        assert METAS_2026_POR_NOME_VAGAS['Jaboatao'] == 1200
        assert METAS_2026_POR_NOME_VAGAS['Paulista'] == 850
        assert METAS_2026_POR_NOME_VAGAS['Cordeiro'] == 800


class TestTraduzirSeriesEOutras:
    """Testes de traducao de series e funcoes auxiliares."""

    def test_traduzir_serie_vagas_para_pedagogico_fund_ii(self):
        """Series do Fund II devem traduzir diretamente."""
        assert traduzir_serie_vagas_para_pedagogico('6º Ano') == '6º Ano'
        assert traduzir_serie_vagas_para_pedagogico('9º Ano') == '9º Ano'

    def test_traduzir_serie_vagas_para_pedagogico_em_legado(self):
        """Nomes legados do EM devem normalizar para serie canonica."""
        assert traduzir_serie_vagas_para_pedagogico('1º Ano Médio') == '1ª Série'
        assert traduzir_serie_vagas_para_pedagogico('2º Ano Médio') == '2ª Série'
        assert traduzir_serie_vagas_para_pedagogico('3º Ano Médio') == '3ª Série'

    def test_traduzir_serie_vagas_infantil_retorna_none(self):
        """Series de Ed. Infantil nao existem no pedagogico => None."""
        assert traduzir_serie_vagas_para_pedagogico('Infantil III') is None
        assert traduzir_serie_vagas_para_pedagogico('Infantil V') is None

    def test_traduzir_unidade_pedagogico_para_vagas_codigo(self):
        """Codigo pedagogico => codigo vagas."""
        assert traduzir_unidade_pedagogico_para_vagas('BV', 'codigo') == '01-BV'
        assert traduzir_unidade_pedagogico_para_vagas('CD', 'codigo') == '02-CD'

    def test_traduzir_unidade_pedagogico_para_vagas_nome(self):
        """Codigo pedagogico => nome vagas."""
        assert traduzir_unidade_pedagogico_para_vagas('JG', 'nome') == 'Paulista'
        assert traduzir_unidade_pedagogico_para_vagas('CD', 'nome') == 'Jaboatao'

    def test_segmento_da_serie(self):
        """segmento_da_serie deve retornar o segmento correto."""
        assert segmento_da_serie('7º Ano') == 'Fund. II'
        assert segmento_da_serie('2ª Série') == 'Ens. Médio'
        assert segmento_da_serie('Infantil III') == 'Ed. Infantil'

    def test_nome_unidade_vagas_para_canonico(self):
        """Nome vagas deve converter para nome canonico."""
        assert nome_unidade_vagas_para_canonico('Jaboatao') == 'Candeias'
        assert nome_unidade_vagas_para_canonico('Paulista') == 'Janga'
        assert nome_unidade_vagas_para_canonico('Boa Viagem') == 'Boa Viagem'
        assert nome_unidade_vagas_para_canonico('Cordeiro') == 'Cordeiro'

    def test_obter_serie_legado(self):
        """obter_serie com nome legado deve normalizar e retornar SerieUniversal."""
        serie = obter_serie('1º Ano Médio')
        assert serie is not None
        assert serie.serie_canonica == '1ª Série'
        assert serie.segmento == 'Ens. Médio'
        assert serie.coberta_pedagogico is True

    def test_obter_serie_normal(self):
        """obter_serie com nome canonico deve retornar SerieUniversal."""
        serie = obter_serie('8º Ano')
        assert serie is not None
        assert serie.segmento == 'Fund. II'
        assert serie.turma_teen == 'TEEN 1'
        assert serie.ordem == 12
