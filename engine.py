"""
Engine PEEX — Orquestrador Vigilia + Estrategista.

Vigilia: roda apos cada extracao, gera missoes pre-computadas.
Estrategista: roda semanalmente, atualiza historico, narrativa e scorecard.

Outputs: JSONs pre-computados em WRITABLE_DIR.

Funcoes publicas:
  - executar_vigilia()
  - executar_estrategista()
  - carregar_missoes_pregeradas(unidade, series)
  - carregar_narrativa_ceo()
  - carregar_scorecard_diretor(unidade)
"""

import json
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path

from utils import (
    WRITABLE_DIR, DATA_DIR, UNIDADES_NOMES,
    calcular_semana_letiva, calcular_capitulo_esperado,
    carregar_fato_aulas, carregar_horario_esperado, filtrar_ate_hoje,
    CONFORMIDADE_META, CONFORMIDADE_BAIXO,
)
from missoes import (
    gerar_todas_missoes_rede, gerar_missoes,
    gerar_missao_fingerprint,
)
from missoes_historico import atualizar_historico, obter_persistentes
from narrativa import gerar_narrativa_ceo, gerar_decisoes_ceo

logger = logging.getLogger("engine_peex")

# Paths dos outputs pre-computados
_MISSOES_FILE = WRITABLE_DIR / "missoes_pregeradas.json"
_NARRATIVA_FILE = WRITABLE_DIR / "narrativa_ceo.json"
_SCORECARD_FILE = WRITABLE_DIR / "scorecard_diretores.json"


# ========== VIGILIA ==========

def executar_vigilia():
    """Roda apos cada extracao do scheduler.
    Gera missoes para toda a rede e salva em missoes_pregeradas.json.

    Returns:
        dict com metadados da execucao
    """
    inicio = datetime.now()
    logger.info("Vigilia: iniciando geracao de missoes...")

    try:
        missoes_rede = gerar_todas_missoes_rede()

        # Serializar para JSON (remover campos nao-serializaveis)
        output = {
            'gerado_em': inicio.isoformat(),
            'semana': calcular_semana_letiva(),
            'unidades': {},
        }

        total_missoes = 0
        for un, missoes in missoes_rede.items():
            serializado = []
            for b in missoes:
                b_clean = {k: v for k, v in b.items() if not isinstance(v, (pd.Timestamp,))}
                # Converter datetime para string
                for k, v in b_clean.items():
                    if isinstance(v, datetime):
                        b_clean[k] = v.isoformat()
                b_clean['fingerprint'] = gerar_missao_fingerprint(b)
                serializado.append(b_clean)

            output['unidades'][un] = serializado
            total_missoes += len(serializado)

        with open(_MISSOES_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)

        duracao = (datetime.now() - inicio).total_seconds()
        logger.info(f"Vigilia: {total_missoes} missoes geradas em {duracao:.1f}s")

        return {
            'ok': True,
            'total_missoes': total_missoes,
            'duracao': duracao,
            'unidades': {un: len(bs) for un, bs in missoes_rede.items()},
        }

    except Exception as e:
        logger.error(f"Vigilia: erro - {e}", exc_info=True)
        return {'ok': False, 'erro': str(e)}


# ========== ESTRATEGISTA ==========

def executar_estrategista():
    """Roda semanalmente (domingo 22h).
    Atualiza historico de missoes, gera narrativa CEO e scorecard diretores.

    Returns:
        dict com metadados da execucao
    """
    inicio = datetime.now()
    semana = calcular_semana_letiva()
    logger.info(f"Estrategista: semana {semana}, iniciando...")

    try:
        # 1. Gerar missoes frescas para toda a rede
        missoes_rede = gerar_todas_missoes_rede()

        # 2. Atualizar historico
        atualizar_historico(missoes_rede, semana)

        # 3. Obter persistentes para as 3 Decisoes CEO
        persistentes = obter_persistentes(min_semanas=4)

        # 4. Gerar narrativa CEO
        resumo_path = DATA_DIR / "resumo_Executivo.csv"
        if resumo_path.exists():
            resumo_df = pd.read_csv(resumo_path)
        else:
            resumo_df = pd.DataFrame()

        # Historico de semanas anteriores (simplificado)
        historico_semanas = _carregar_historico_semanas()

        narrativa_texto = gerar_narrativa_ceo(resumo_df, historico_semanas, semana)
        decisoes = gerar_decisoes_ceo(persistentes)

        narrativa_output = {
            'gerado_em': inicio.isoformat(),
            'semana': semana,
            'narrativa': narrativa_texto,
            'decisoes': decisoes,
            'n_persistentes': len(persistentes),
        }

        with open(_NARRATIVA_FILE, 'w', encoding='utf-8') as f:
            json.dump(narrativa_output, f, ensure_ascii=False, indent=2)

        # 5. Gerar scorecard por unidade (diretores)
        scorecard = _gerar_scorecard_todas_unidades(resumo_df, missoes_rede)

        with open(_SCORECARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(scorecard, f, ensure_ascii=False, indent=2)

        # 6. Salvar snapshot da semana
        _salvar_snapshot_semana(semana, resumo_df)

        duracao = (datetime.now() - inicio).total_seconds()
        logger.info(f"Estrategista: concluido em {duracao:.1f}s")

        return {
            'ok': True,
            'semana': semana,
            'duracao': duracao,
            'n_missoes_rede': sum(len(bs) for bs in missoes_rede.values()),
            'n_persistentes': len(persistentes),
            'n_decisoes': len(decisoes),
        }

    except Exception as e:
        logger.error(f"Estrategista: erro - {e}", exc_info=True)
        return {'ok': False, 'erro': str(e)}


# ========== CONSELHEIRO ==========

_CONSELHEIRO_FILE = WRITABLE_DIR / "conselheiro_output.json"


def executar_conselheiro():
    """Roda segunda 5h. Gera pauta de reuniao PEEX + perguntas + rituais.

    Returns:
        dict com metadados da execucao
    """
    inicio = datetime.now()
    semana = calcular_semana_letiva()
    logger.info(f"Conselheiro: semana {semana}, gerando pauta...")

    try:
        from peex_utils import info_semana, proximas_reunioes
        from peex_config import REUNIOES, FORMATOS_REUNIAO, DIFERENCIACAO_UNIDADE

        info = info_semana(semana)
        prox = info['proxima_reuniao']
        formato = info['formato_reuniao']

        # Carregar missoes
        missoes_rede = gerar_todas_missoes_rede()
        persistentes = obter_persistentes(min_semanas=4)

        # Gerar pauta por unidade
        pautas = {}
        for un_code in ['BV', 'CD', 'JG', 'CDR']:
            missoes_un = missoes_rede.get(un_code, [])
            urgentes = [b for b in missoes_un if b.get('nivel') == 'URGENTE']
            diff = DIFERENCIACAO_UNIDADE.get(un_code, {})

            # Topicos baseados nas missoes
            topicos = []
            if urgentes:
                topicos.append(f"Revisao de {len(urgentes)} missao(oes) urgente(s)")
            if any(b.get('tipo') == 'PROF_SILENCIOSO' for b in missoes_un):
                topicos.append("Plano de contato com professores silenciosos")
            if any(b.get('tipo') == 'ALUNO_FREQUENCIA' for b in missoes_un):
                topicos.append("Protocolo de busca ativa — alunos em risco")
            if any(b.get('tipo') == 'CURRICULO_ATRASADO' for b in missoes_un):
                topicos.append("Alinhamento SAE — professores com gap de capitulo")

            # Foco especifico da unidade
            if diff.get('foco'):
                topicos.append(f"Foco {un_code}: {diff['foco'][:60]}")

            # Pauta da reuniao do calendario
            if prox:
                topicos.append(f"Pauta programada: {prox.get('foco', '')[:80]}")

            # Perguntas para o coordenador
            perguntas = _gerar_perguntas_conselheiro(missoes_un, un_code)

            # Rituais de floresta (5 atos)
            rituais = _gerar_rituais(missoes_un, un_code)

            # Formato sugerido
            formato_sugerido = _sugerir_formato(missoes_un, formato)

            pautas[un_code] = {
                'topicos': topicos[:7],
                'perguntas': perguntas,
                'rituais': rituais,
                'formato_sugerido': formato_sugerido,
                'n_missoes': len(missoes_un),
                'n_urgentes': len(urgentes),
            }

        output = {
            'gerado_em': inicio.isoformat(),
            'semana': semana,
            'proxima_reuniao': prox,
            'pautas': pautas,
            'n_persistentes': len(persistentes),
        }

        with open(_CONSELHEIRO_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)

        duracao = (datetime.now() - inicio).total_seconds()
        logger.info(f"Conselheiro: concluido em {duracao:.1f}s")

        return {
            'ok': True,
            'semana': semana,
            'duracao': duracao,
            'unidades': list(pautas.keys()),
        }

    except Exception as e:
        logger.error(f"Conselheiro: erro - {e}", exc_info=True)
        return {'ok': False, 'erro': str(e)}


def _gerar_perguntas_conselheiro(missoes, unidade):
    """Gera 3 perguntas reflexivas para o coordenador."""
    perguntas = []
    tipos = [b.get('tipo') for b in missoes]

    if 'PROF_SILENCIOSO' in tipos:
        perguntas.append("Quantos professores voce contatou pessoalmente esta semana? Qual foi a resposta deles?")
    if 'ALUNO_FREQUENCIA' in tipos:
        perguntas.append("Quais alunos em risco ja foram encaminhados para orientacao? Ha algum caso familiar que precisa de intervencao?")
    if 'TURMA_CRITICA' in tipos:
        perguntas.append("Existe alguma turma onde os problemas se concentram? O que ha de diferente nela?")
    if 'CURRICULO_ATRASADO' in tipos:
        perguntas.append("Os professores com gap SAE sabem que estao atrasados? Ja combinaram plano de compactacao?")
    if 'PROF_SEM_CONTEUDO' in tipos:
        perguntas.append("Os professores entendem a importancia do registro de conteudo? Ha barreira tecnica?")

    # Pergunta generica
    if not perguntas:
        perguntas.append("Qual foi a maior conquista da sua equipe esta semana?")
    perguntas.append("O que voce precisa da direcao que nao esta conseguindo resolver sozinho(a)?")
    perguntas.append("Se pudesse mudar UMA coisa na rotina da proxima semana, o que seria?")

    return perguntas[:3]


def _gerar_rituais(missoes, unidade):
    """Gera os 5 atos do Ritual de Floresta (RAIZES)."""
    urgentes = [b for b in missoes if b.get('nivel') == 'URGENTE']

    return [
        {
            'ato': 1, 'nome': 'Raizes', 'duracao': '5 min',
            'conteudo': 'Ancoragem: como esta a energia da equipe? Roda rapida de check-in.',
        },
        {
            'ato': 2, 'nome': 'Solo', 'duracao': '10 min',
            'conteudo': f"Dados da semana: {len(missoes)} missoes ({len(urgentes)} urgentes). Revisao dos indicadores.",
        },
        {
            'ato': 3, 'nome': 'Micelio', 'duracao': '10 min',
            'conteudo': 'Conexoes: quem precisa de ajuda? Quem pode ajudar? Pareamentos possiveis.',
        },
        {
            'ato': 4, 'nome': 'Sementes', 'duracao': '10 min',
            'conteudo': 'Plano de acao: 3 compromissos concretos para a proxima semana.',
        },
        {
            'ato': 5, 'nome': 'Chuva', 'duracao': '5 min',
            'conteudo': 'Encerramento positivo: celebrar 1 conquista da semana. NUNCA terminar com problema.',
        },
    ]


def _sugerir_formato(missoes, formato_calendario):
    """Sugere formato de reuniao baseado nos indicadores."""
    urgentes = [b for b in missoes if b.get('nivel') == 'URGENTE']

    if len(urgentes) >= 5:
        return {'formato': 'C', 'nome': 'CRISE', 'duracao': 60, 'motivo': f'{len(urgentes)} urgentes requerem CRISE'}
    if len(urgentes) >= 3:
        return {'formato': 'FO', 'nome': 'FOCO', 'duracao': 45, 'motivo': f'{len(urgentes)} urgentes requerem FOCO'}

    # Usar formato do calendario se disponivel
    if formato_calendario:
        return {
            'formato': formato_calendario.get('icone', 'F'),
            'nome': formato_calendario.get('nome', 'FLASH'),
            'duracao': formato_calendario.get('duracao', 30),
            'motivo': 'Conforme calendario PEEX',
        }
    return {'formato': 'F', 'nome': 'FLASH', 'duracao': 30, 'motivo': 'Padrao semanal'}


# ========== COMPARADOR ==========

_COMPARADOR_FILE = WRITABLE_DIR / "comparador_output.json"


def executar_comparador():
    """Roda segunda 5h30. Calcula estrelas e rankings.

    Returns:
        dict com metadados da execucao
    """
    inicio = datetime.now()
    semana = calcular_semana_letiva()
    logger.info(f"Comparador: semana {semana}, calculando rankings...")

    try:
        from estrelas import (
            calcular_estrelas_semana, registrar_estrelas_semana,
            ranking_evolucao, ranking_saude, ranking_generosidade,
        )
        from utils import calcular_trimestre

        trimestre = calcular_trimestre(semana)

        resumo_path = DATA_DIR / "resumo_Executivo.csv"
        resumo_df = pd.read_csv(resumo_path) if resumo_path.exists() else pd.DataFrame()

        # Historico para comparar
        historico_semanas = _carregar_historico_semanas()
        if historico_semanas:
            # Reconstruir resumo anterior simplificado
            resumo_anterior = pd.DataFrame()
        else:
            resumo_anterior = pd.DataFrame()

        # Calcular e registrar estrelas
        if not resumo_df.empty:
            estrelas = calcular_estrelas_semana(resumo_df, resumo_anterior, trimestre)
            registrar_estrelas_semana(semana, estrelas)

            r_evolucao = ranking_evolucao()
            r_saude = ranking_saude(resumo_df)
            r_generosidade = ranking_generosidade()
        else:
            estrelas = {}
            r_evolucao = []
            r_saude = []
            r_generosidade = []

        output = {
            'gerado_em': inicio.isoformat(),
            'semana': semana,
            'estrelas_semana': estrelas,
            'ranking_evolucao': r_evolucao,
            'ranking_saude': r_saude,
            'ranking_generosidade': r_generosidade,
        }

        with open(_COMPARADOR_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)

        duracao = (datetime.now() - inicio).total_seconds()
        logger.info(f"Comparador: concluido em {duracao:.1f}s")

        return {'ok': True, 'semana': semana, 'duracao': duracao}

    except Exception as e:
        logger.error(f"Comparador: erro - {e}", exc_info=True)
        return {'ok': False, 'erro': str(e)}


# ========== PREDITOR ==========

_PREDITOR_FILE = WRITABLE_DIR / "preditor_output.json"


def executar_preditor():
    """Roda sexta 20h. Projecoes baseadas em series temporais.

    Usa regressao linear simples sobre 4+ semanas de dados para projetar
    conformidade, frequencia e risco para as proximas 2 semanas.

    Returns:
        dict com metadados da execucao
    """
    inicio = datetime.now()
    semana = calcular_semana_letiva()
    logger.info(f"Preditor: semana {semana}, gerando projecoes...")

    try:
        historico = _carregar_historico_semanas()

        if len(historico) < 4:
            logger.info("Preditor: historico insuficiente (<4 semanas). Pulando.")
            return {'ok': True, 'semana': semana, 'motivo': 'historico_insuficiente'}

        projecoes = {}
        alertas = []

        for un_code in ['BV', 'CD', 'JG', 'CDR']:
            campo = f'conf_{un_code}'
            valores = [(h['semana'], h.get(campo, 0)) for h in historico if campo in h]

            if len(valores) < 3:
                continue

            # Regressao linear simples: y = a*x + b
            xs = [v[0] for v in valores]
            ys = [v[1] for v in valores]
            n = len(xs)
            sum_x = sum(xs)
            sum_y = sum(ys)
            sum_xy = sum(x * y for x, y in zip(xs, ys))
            sum_x2 = sum(x * x for x in xs)

            denom = n * sum_x2 - sum_x ** 2
            if denom == 0:
                continue

            a = (n * sum_xy - sum_x * sum_y) / denom
            b = (sum_y - a * sum_x) / n

            # Projetar 2 semanas adiante
            proj_1 = round(a * (semana + 1) + b, 1)
            proj_2 = round(a * (semana + 2) + b, 1)
            atual = ys[-1]
            tendencia = 'subindo' if a > 0.5 else ('caindo' if a < -0.5 else 'estavel')

            projecoes[un_code] = {
                'atual': atual,
                'proj_sem_mais_1': max(0, min(100, proj_1)),
                'proj_sem_mais_2': max(0, min(100, proj_2)),
                'tendencia': tendencia,
                'coef_angular': round(a, 3),
                'n_pontos': n,
            }

            # Alertas preventivos
            if tendencia == 'caindo' and atual > 50 and proj_2 < 50:
                alertas.append({
                    'unidade': un_code,
                    'tipo': 'queda_critica',
                    'mensagem': f'{UNIDADES_NOMES.get(un_code, un_code)}: conformidade projetada para cair abaixo de 50% em 2 semanas',
                    'urgencia': 'alta',
                })
            elif tendencia == 'caindo':
                alertas.append({
                    'unidade': un_code,
                    'tipo': 'tendencia_queda',
                    'mensagem': f'{UNIDADES_NOMES.get(un_code, un_code)}: tendencia de queda ({a:.1f}pp/sem)',
                    'urgencia': 'media',
                })

        output = {
            'gerado_em': inicio.isoformat(),
            'semana': semana,
            'projecoes': projecoes,
            'alertas': alertas,
            'n_semanas_historico': len(historico),
        }

        with open(_PREDITOR_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        duracao = (datetime.now() - inicio).total_seconds()
        logger.info(f"Preditor: concluido em {duracao:.1f}s, {len(alertas)} alerta(s)")

        return {
            'ok': True, 'semana': semana, 'duracao': duracao,
            'n_projecoes': len(projecoes), 'n_alertas': len(alertas),
        }

    except Exception as e:
        logger.error(f"Preditor: erro - {e}", exc_info=True)
        return {'ok': False, 'erro': str(e)}


def carregar_preditor():
    """Carrega output do preditor pre-gerado."""
    if _PREDITOR_FILE.exists():
        try:
            with open(_PREDITOR_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


# ========== RETROALIMENTADOR ==========

_RETRO_FILE = WRITABLE_DIR / "retroalimentador_output.json"


def executar_retroalimentador():
    """Roda cada 6h. Verifica execucao de acoes e escala se necessario.

    Checa:
    - Se coordenador executou acoes do plano semanal
    - Se missoes urgentes foram resolvidas
    - Se execucao <60% em 2+ semanas -> escala

    Returns:
        dict com metadados
    """
    inicio = datetime.now()
    semana = calcular_semana_letiva()
    logger.info(f"Retroalimentador: semana {semana}, verificando execucao...")

    try:
        verificacoes = {}
        escalacoes = []

        for un_code in ['BV', 'CD', 'JG', 'CDR']:
            # Verificar plano de acao
            plano_path = WRITABLE_DIR / f"plano_acao_{un_code}_sem{semana}.json"
            if plano_path.exists():
                try:
                    with open(plano_path, 'r', encoding='utf-8') as f:
                        plano = json.load(f)
                    acoes = plano.get('acoes', [])
                    total = len(acoes)
                    resolvidas = sum(1 for a in acoes if a.get('status') == 'resolvida')
                    taxa = resolvidas / max(total, 1) * 100
                except (json.JSONDecodeError, IOError):
                    total = 0
                    resolvidas = 0
                    taxa = 0
            else:
                total = 0
                resolvidas = 0
                taxa = 0

            verificacoes[un_code] = {
                'acoes_total': total,
                'acoes_resolvidas': resolvidas,
                'taxa_execucao': round(taxa, 1),
            }

            # Verificar semana anterior tambem
            plano_ant_path = WRITABLE_DIR / f"plano_acao_{un_code}_sem{semana - 1}.json"
            taxa_ant = 0
            if plano_ant_path.exists():
                try:
                    with open(plano_ant_path, 'r', encoding='utf-8') as f:
                        plano_ant = json.load(f)
                    acoes_ant = plano_ant.get('acoes', [])
                    total_ant = len(acoes_ant)
                    resolvidas_ant = sum(1 for a in acoes_ant if a.get('status') == 'resolvida')
                    taxa_ant = resolvidas_ant / max(total_ant, 1) * 100
                except (json.JSONDecodeError, IOError):
                    pass

            # Escalar se execucao <60% por 2+ semanas
            if taxa < 60 and taxa_ant < 60 and total > 0:
                escalacoes.append({
                    'unidade': un_code,
                    'motivo': f'Execucao abaixo de 60% por 2 semanas consecutivas '
                              f'(sem {semana - 1}: {taxa_ant:.0f}%, sem {semana}: {taxa:.0f}%)',
                    'acao': 'Escalar para diretor: coordenador precisa de apoio',
                })

        output = {
            'gerado_em': inicio.isoformat(),
            'semana': semana,
            'verificacoes': verificacoes,
            'escalacoes': escalacoes,
        }

        with open(_RETRO_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        duracao = (datetime.now() - inicio).total_seconds()
        logger.info(f"Retroalimentador: {len(escalacoes)} escalacao(es) em {duracao:.1f}s")

        return {
            'ok': True, 'semana': semana, 'duracao': duracao,
            'n_escalacoes': len(escalacoes),
        }

    except Exception as e:
        logger.error(f"Retroalimentador: erro - {e}", exc_info=True)
        return {'ok': False, 'erro': str(e)}


def carregar_retroalimentador():
    """Carrega output do retroalimentador."""
    if _RETRO_FILE.exists():
        try:
            with open(_RETRO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def carregar_comparador():
    """Carrega output do comparador pre-gerado."""
    if _COMPARADOR_FILE.exists():
        try:
            with open(_COMPARADOR_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def carregar_conselheiro():
    """Carrega output do conselheiro pre-gerado."""
    if _CONSELHEIRO_FILE.exists():
        try:
            with open(_CONSELHEIRO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


# ========== PREPARADOR ==========

_PREPARADOR_FILE = WRITABLE_DIR / "preparador_output.json"


def executar_preparador():
    """Roda segunda 5h45 (apos CONSELHEIRO e COMPARADOR).
    Consolida a inteligencia de TODOS os robos para gerar roteiro completo de reuniao.

    Input: outputs de VIGILIA, ESTRATEGISTA, CONSELHEIRO, COMPARADOR, PREDITOR, RETROALIMENTADOR
    Output: preparador_output.json com roteiro por unidade e script dos 5 atos.

    Returns:
        dict com metadados da execucao
    """
    inicio = datetime.now()
    semana = calcular_semana_letiva()
    logger.info(f"Preparador: semana {semana}, consolidando inteligencia...")

    try:
        from peex_utils import info_semana, estacao_atual
        from peex_config import DIFERENCIACAO_UNIDADE

        info = info_semana(semana)
        prox = info['proxima_reuniao']
        formato = info['formato_reuniao']
        estacao, tom = estacao_atual(semana)

        # Carregar outputs de todos os robos
        missoes_rede = gerar_todas_missoes_rede()
        conselheiro_data = carregar_conselheiro()
        comparador_data = carregar_comparador()
        preditor_data = carregar_preditor()
        retro_data = carregar_retroalimentador()
        persistentes = obter_persistentes(min_semanas=4)

        # Resumo executivo
        resumo_path = DATA_DIR / "resumo_Executivo.csv"
        resumo_df = pd.read_csv(resumo_path) if resumo_path.exists() else pd.DataFrame()

        # === Objetivo da reuniao ===
        objetivo = _gerar_objetivo(prox, missoes_rede, formato)

        # === Preparacao CEO ===
        prep_ceo = _gerar_preparacao_ceo(missoes_rede, prox, estacao, tom)

        # === Roteiro por unidade ===
        roteiro = {}
        versao_diretor = {}
        for un_code in ['BV', 'CD', 'JG', 'CDR']:
            missoes_un = missoes_rede.get(un_code, [])
            conselheiro_un = conselheiro_data.get('pautas', {}).get(un_code, {})
            diff = DIFERENCIACAO_UNIDADE.get(un_code, {})
            retro_un = retro_data.get('verificacoes', {}).get(un_code, {})

            urgentes = [m for m in missoes_un if m.get('nivel') == 'URGENTE']
            importantes = [m for m in missoes_un if m.get('nivel') == 'IMPORTANTE']

            # Resumo da situacao
            un_resumo = ''
            if not resumo_df.empty:
                row = resumo_df[resumo_df['unidade'] == un_code]
                if not row.empty:
                    r = row.iloc[0]
                    conf = r.get('pct_conformidade_media', 0)
                    un_resumo = f"Conformidade: {conf:.0f}%. {len(missoes_un)} missoes ({len(urgentes)} urgentes)."

            # Pontos criticos
            pontos_criticos = []
            for m in urgentes[:3]:
                pontos_criticos.append({
                    'tema': f"{m.get('tipo', '')}: {m.get('professor', m.get('serie', ''))}",
                    'como_abordar': m.get('como', [''])[0] if m.get('como') else '',
                    'objetivo': m.get('o_que', '')[:100],
                })

            # Pontos positivos
            positivos = []
            if diff.get('foco'):
                positivos.append(f"Foco da unidade: {diff['foco'][:80]}")

            # Pergunta
            pergunta = ''
            if conselheiro_un.get('perguntas'):
                pergunta = conselheiro_un['perguntas'][0]
            elif urgentes:
                pergunta = f"O que voce precisa para resolver as {len(urgentes)} missoes urgentes?"

            # Compromisso
            compromisso = ''
            if urgentes:
                compromisso = f"Cada coordenador assume 1 missao urgente para resolucao ate quarta-feira."
            elif importantes:
                compromisso = f"Cada coordenador reporta status das {len(importantes)} missoes importantes."

            roteiro[un_code] = {
                'diretor': diff.get('coordenadores', ''),
                'situacao_resumida': un_resumo,
                'pontos_criticos': pontos_criticos,
                'pontos_positivos': positivos,
                'pergunta_para_diretor': pergunta,
                'compromisso_esperado': compromisso,
            }

            # Versao diretor
            topicos_dir = [m.get('o_que', '')[:80] for m in missoes_un[:3]]
            perguntas_dir = conselheiro_un.get('perguntas', [])

            versao_diretor[un_code] = {
                'topicos_principais': topicos_dir,
                'abordagem_sugerida': f"Tom {tom}. {len(urgentes)} urgentes requerem atencao." if urgentes else f"Tom {tom}. Sem urgencias, foco em acompanhamento.",
                'perguntas': perguntas_dir,
            }

        # === Script dos 5 atos ===
        script = _gerar_script_5_atos(missoes_rede, resumo_df, roteiro, estacao, tom, formato)

        # === Output final ===
        output = {
            'gerado_em': inicio.isoformat(),
            'semana': semana,
            'reuniao': {
                'titulo': prox.get('titulo', '') if prox else '',
                'semana': prox.get('semana', semana) if prox else semana,
                'formato': formato.get('nome', 'FLASH'),
                'duracao_min': formato.get('duracao', 30),
                'tipo': prox.get('tipo_reuniao', 'RU') if prox else 'RU',
            },
            'objetivo_da_reuniao': objetivo,
            'preparacao_ceo': prep_ceo,
            'roteiro_por_unidade': roteiro,
            'script_5_atos': script,
            'versao_diretor': versao_diretor,
        }

        with open(_PREPARADOR_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)

        duracao = (datetime.now() - inicio).total_seconds()
        logger.info(f"Preparador: concluido em {duracao:.1f}s")

        return {'ok': True, 'semana': semana, 'duracao': duracao}

    except Exception as e:
        logger.error(f"Preparador: erro - {e}", exc_info=True)
        return {'ok': False, 'erro': str(e)}


def _gerar_objetivo(prox, missoes_rede, formato):
    """Gera objetivo da reuniao baseado no contexto."""
    total_urgentes = sum(
        len([m for m in ms if m.get('nivel') == 'URGENTE'])
        for ms in missoes_rede.values()
    )
    if total_urgentes >= 5:
        return f"Resolver {total_urgentes} missoes urgentes na rede. Modo CRISE."
    if prox and prox.get('foco'):
        return prox['foco']
    return "Acompanhamento semanal dos indicadores pedagogicos."


def _gerar_preparacao_ceo(missoes_rede, prox, estacao, tom):
    """Gera bloco de preparacao da CEO."""
    antes = ["Revisar missoes urgentes de cada unidade"]
    levar = ["Lista nominal de professores criticos", "Comparativo semana anterior"]

    total_urgentes = sum(
        len([m for m in ms if m.get('nivel') == 'URGENTE'])
        for ms in missoes_rede.values()
    )
    if total_urgentes > 0:
        antes.append(f"Verificar status das {total_urgentes} missoes urgentes")
    if prox:
        antes.append(f"Preparar pauta: {prox.get('foco', '')[:60]}")

    return {
        'antes_da_reuniao': antes,
        'o_que_levar': levar,
        'tom_recomendado': f"{tom}. Estacao: {estacao}.",
    }


def _gerar_script_5_atos(missoes_rede, resumo_df, roteiro, estacao, tom, formato):
    """Gera script dos 5 atos com falas sugeridas."""
    total_missoes = sum(len(ms) for ms in missoes_rede.values())
    total_urgentes = sum(
        len([m for m in ms if m.get('nivel') == 'URGENTE'])
        for ms in missoes_rede.values()
    )

    # Dados de conformidade por unidade
    dados_solo = []
    if not resumo_df.empty:
        for _, row in resumo_df[resumo_df['unidade'] != 'TOTAL'].iterrows():
            un = row.get('unidade', '')
            conf = row.get('pct_conformidade_media', 0)
            nome = UNIDADES_NOMES.get(un, un)
            dados_solo.append(f"{nome}: {conf:.0f}%")

    # Compromissos sugeridos
    compromissos = []
    for un_code, un_roteiro in roteiro.items():
        comp = un_roteiro.get('compromisso_esperado', '')
        if comp:
            compromissos.append(f"{UNIDADES_NOMES.get(un_code, un_code)}: {comp[:80]}")

    # Celebracao
    celebracao = "Equipe reunida, dados na mao, compromissos definidos. Vamos!"

    dur_total = formato.get('duracao', 30)
    if dur_total <= 30:
        d1, d2, d3, d4, d5 = '3 min', '10 min', '10 min', '5 min', '2 min'
    elif dur_total <= 45:
        d1, d2, d3, d4, d5 = '5 min', '15 min', '12 min', '8 min', '5 min'
    else:
        d1, d2, d3, d4, d5 = '5 min', '20 min', '20 min', '10 min', '5 min'

    return {
        'ato1_raizes': {
            'duracao': d1,
            'o_que_dizer': f"Bom dia, equipe. Antes dos dados: como voces estao? {tom}.",
            'tecnica': 'Roda rapida: 1 palavra por pessoa',
        },
        'ato2_solo': {
            'duracao': d2,
            'o_que_dizer': f"Vamos aos numeros. {total_missoes} missoes ativas ({total_urgentes} urgentes).",
            'dados_para_mostrar': dados_solo,
            'tecnica': 'Comece pelo positivo. Depois mostre os gaps.',
        },
        'ato3_micelio': {
            'duracao': d3,
            'o_que_dizer': "Quem precisa de ajuda? Quem pode compartilhar uma estrategia que funcionou?",
            'tecnica': 'Peca que a unidade com melhor resultado compartilhe com a que precisa',
        },
        'ato4_sementes': {
            'duracao': d4,
            'o_que_dizer': "Cada unidade define 1 compromisso. Registrem agora.",
            'compromissos_sugeridos': compromissos[:4],
            'tecnica': 'Compromisso SMART: especifico, com prazo, responsavel definido',
        },
        'ato5_chuva': {
            'duracao': d5,
            'celebracao': celebracao,
            'o_que_dizer': f"Terminamos celebrando: {celebracao}",
        },
    }


def carregar_preparador():
    """Carrega output do preparador pre-gerado."""
    if _PREPARADOR_FILE.exists():
        try:
            with open(_PREPARADOR_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


# ========== LEITURA (consumido pelas paginas) ==========

def carregar_missoes_pregeradas(unidade=None, series=None):
    """Carrega missoes pre-geradas. Fallback: gera on-demand.

    Args:
        unidade: codigo da unidade (ou None para todas)
        series: lista de series (para filtrar)

    Returns:
        lista de dicts de missoes
    """
    # Tentar pre-geradas
    if _MISSOES_FILE.exists():
        try:
            with open(_MISSOES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if unidade:
                missoes = data.get('unidades', {}).get(unidade, [])
            else:
                missoes = []
                for un_missoes in data.get('unidades', {}).values():
                    missoes.extend(un_missoes)

            # Filtrar por series se especificado
            if series and missoes:
                missoes = [
                    b for b in missoes
                    if b.get('serie', '') in series
                    or b.get('series', '') in series
                    or not b.get('serie')  # manter missoes sem serie (ex: deadline)
                ]

            return missoes

        except (json.JSONDecodeError, IOError):
            pass

    # Fallback: gerar on-demand
    if unidade and series:
        return gerar_missoes(unidade, series)
    return []


def carregar_narrativa_ceo():
    """Carrega narrativa CEO pre-gerada. Fallback: gera on-the-fly.

    Returns:
        dict com chaves: narrativa, decisoes, semana, gerado_em
    """
    if _NARRATIVA_FILE.exists():
        try:
            with open(_NARRATIVA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Fallback: gerar on-the-fly
    semana = calcular_semana_letiva()
    resumo_path = DATA_DIR / "resumo_Executivo.csv"
    resumo_df = pd.read_csv(resumo_path) if resumo_path.exists() else pd.DataFrame()
    historico_semanas = _carregar_historico_semanas()
    persistentes = obter_persistentes(min_semanas=4)

    return {
        'gerado_em': datetime.now().isoformat(),
        'semana': semana,
        'narrativa': gerar_narrativa_ceo(resumo_df, historico_semanas, semana),
        'decisoes': gerar_decisoes_ceo(persistentes),
        'n_persistentes': len(persistentes),
    }


def carregar_scorecard_diretor(unidade):
    """Carrega scorecard de uma unidade para o diretor.

    Args:
        unidade: codigo da unidade

    Returns:
        dict com metricas da unidade ou {} se nao disponivel
    """
    if _SCORECARD_FILE.exists():
        try:
            with open(_SCORECARD_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('unidades', {}).get(unidade, {})
        except (json.JSONDecodeError, IOError):
            pass

    # Fallback: calcular on-the-fly
    return _calcular_scorecard_unidade(unidade)


# ========== HELPERS INTERNOS ==========

def _gerar_scorecard_todas_unidades(resumo_df, missoes_rede):
    """Gera scorecard para todas as 4 unidades."""
    output = {
        'gerado_em': datetime.now().isoformat(),
        'unidades': {},
    }

    for un_code in ['BV', 'CD', 'JG', 'CDR']:
        sc = {}

        # Dados do resumo executivo
        if not resumo_df.empty:
            row = resumo_df[resumo_df['unidade'] == un_code]
            if not row.empty:
                r = row.iloc[0]
                sc['conformidade'] = round(r.get('pct_conformidade_media', 0), 1)
                sc['total_professores'] = int(r.get('total_professores', 0))
                sc['professores_criticos'] = int(r.get('professores_criticos', 0))
                sc['total_alunos'] = int(r.get('total_alunos', 0))
                sc['frequencia_media'] = round(r.get('frequencia_media', 0), 1)
                sc['pct_alunos_risco'] = round(r.get('pct_alunos_risco', 0), 1)
                sc['semaforo'] = r.get('semaforo', 'Vermelho')
                sc['ocorr_graves'] = int(r.get('ocorr_graves', 0))

        # Missoes da unidade
        missoes_un = missoes_rede.get(un_code, [])
        sc['n_missoes'] = len(missoes_un)
        sc['n_urgentes'] = len([b for b in missoes_un if b.get('nivel') == 'URGENTE'])
        if missoes_un:
            sc['top_missao'] = missoes_un[0].get('o_que', '')[:80]
        else:
            sc['top_missao'] = 'Nenhuma missao ativa'

        # Semaforo
        conf = sc.get('conformidade', 0)
        if conf >= CONFORMIDADE_META:
            sc['cor_semaforo'] = 'verde'
        elif conf >= CONFORMIDADE_BAIXO:
            sc['cor_semaforo'] = 'amarelo'
        else:
            sc['cor_semaforo'] = 'vermelho'

        output['unidades'][un_code] = sc

    return output


def _calcular_scorecard_unidade(unidade):
    """Calcula scorecard para uma unidade on-the-fly."""
    resumo_path = DATA_DIR / "resumo_Executivo.csv"
    if not resumo_path.exists():
        return {}

    resumo_df = pd.read_csv(resumo_path)
    row = resumo_df[resumo_df['unidade'] == unidade]
    if row.empty:
        return {}

    r = row.iloc[0]
    return {
        'conformidade': round(r.get('pct_conformidade_media', 0), 1),
        'total_professores': int(r.get('total_professores', 0)),
        'professores_criticos': int(r.get('professores_criticos', 0)),
        'total_alunos': int(r.get('total_alunos', 0)),
        'frequencia_media': round(r.get('frequencia_media', 0), 1),
        'pct_alunos_risco': round(r.get('pct_alunos_risco', 0), 1),
        'semaforo': r.get('semaforo', ''),
        'ocorr_graves': int(r.get('ocorr_graves', 0)),
    }


def _carregar_historico_semanas():
    """Carrega snapshots de semanas anteriores para tendencia."""
    path = WRITABLE_DIR / "historico_semanas.json"
    if not path.exists():
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _salvar_snapshot_semana(semana, resumo_df):
    """Salva snapshot da semana atual para historico de tendencia."""
    path = WRITABLE_DIR / "historico_semanas.json"
    historico = _carregar_historico_semanas()

    # Evitar duplicata
    semanas_salvas = {h.get('semana') for h in historico}
    if semana in semanas_salvas:
        return

    total_row = resumo_df[resumo_df['unidade'] == 'TOTAL'] if not resumo_df.empty else pd.DataFrame()
    snapshot = {
        'semana': semana,
        'data': datetime.now().strftime('%Y-%m-%d'),
        'conformidade_rede': round(total_row.iloc[0].get('pct_conformidade_media', 0), 1) if not total_row.empty else 0,
    }

    # Conformidade por unidade
    if not resumo_df.empty:
        for _, row in resumo_df[resumo_df['unidade'] != 'TOTAL'].iterrows():
            un = row.get('unidade', '')
            snapshot[f'conf_{un}'] = round(row.get('pct_conformidade_media', 0), 1)

    historico.append(snapshot)

    # Manter apenas ultimas 47 semanas
    historico = historico[-47:]

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)
