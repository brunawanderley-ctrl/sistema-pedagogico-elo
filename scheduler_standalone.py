#!/usr/bin/env python3
"""
SCHEDULER STANDALONE - Atualizacao automatica do SIGA
Colégio ELO 2026

Executa extraccoes do diario de classe nos horarios agendados,
independente do processo Streamlit.

Uso:
    # Modo daemon (roda continuamente com APScheduler):
    python3 scheduler_standalone.py

    # Modo unico (executa 1x e sai - ideal para cron/Render Cron Job):
    python3 scheduler_standalone.py --once

    # Teste de saude (verifica ultimo run):
    python3 scheduler_standalone.py --health

Horarios de execucao: 8h, 12h, 18h e 20h (America/Recife)

Health check: Escreve timestamp em scheduler_health.json apos cada execucao.
Log: scheduler.log (rotacao automatica, max 5MB x 3 backups)
"""

import argparse
import json
import logging
import os
import signal
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
HEALTH_FILE = SCRIPT_DIR / "scheduler_health.json"
LOG_FILE = SCRIPT_DIR / "scheduler.log"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("scheduler_standalone")
logger.setLevel(logging.INFO)

# File handler (rotativo: 5 MB x 3 backups)
_fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(_fh)

# Console handler
_ch = logging.StreamHandler()
_ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(_ch)

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def write_health(result: dict) -> None:
    """Escreve resultado da ultima execucao em scheduler_health.json."""
    health = {
        "last_run": datetime.now().isoformat(),
        "ok": result.get("ok", False),
        "total": result.get("total", 0),
        "erro": result.get("erro"),
        "duracao": result.get("duracao", 0),
        "por_unidade": result.get("por_unidade", {}),
    }
    try:
        with open(HEALTH_FILE, "w", encoding="utf-8") as f:
            json.dump(health, f, indent=2, ensure_ascii=False)
        logger.info(f"Health check atualizado: {HEALTH_FILE.name}")
    except Exception as e:
        logger.error(f"Falha ao escrever health check: {e}")


def read_health() -> dict:
    """Le o health check. Retorna dict vazio se nao existir."""
    if not HEALTH_FILE.exists():
        return {}
    try:
        with open(HEALTH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Execucao da atualizacao
# ---------------------------------------------------------------------------

def executar_atualizacao() -> None:
    """Executa run_update() e grava health check. Roda Vigilia apos sucesso."""
    logger.info("Iniciando atualizacao do SIGA...")
    try:
        from atualizar_siga import run_update
        result = run_update()
        write_health(result)
        if result.get("ok"):
            logger.info(
                f"Atualizacao concluida: {result.get('total', 0)} aulas "
                f"em {result.get('duracao', 0):.0f}s"
            )
            # Rodar Vigilia apos extracao com sucesso
            _executar_vigilia()
        else:
            logger.error(f"Atualizacao falhou: {result.get('erro', '?')}")
    except Exception as e:
        logger.error(f"Erro fatal na atualizacao: {e}", exc_info=True)
        write_health({"ok": False, "erro": str(e)})


def _executar_vigilia() -> None:
    """Executa engine.executar_vigilia() para pre-gerar missoes."""
    try:
        from engine import executar_vigilia
        result = executar_vigilia()
        if result.get("ok"):
            logger.info(
                f"Vigilia concluida: {result.get('total_missoes', 0)} missoes "
                f"em {result.get('duracao', 0):.1f}s"
            )
        else:
            logger.warning(f"Vigilia falhou: {result.get('erro', '?')}")
    except Exception as e:
        logger.warning(f"Vigilia nao executada: {e}")


def _executar_estrategista() -> None:
    """Executa engine.executar_estrategista() semanal."""
    logger.info("Estrategista: iniciando execucao semanal...")
    try:
        from engine import executar_estrategista
        result = executar_estrategista()
        if result.get("ok"):
            logger.info(
                f"Estrategista concluido: semana {result.get('semana')}, "
                f"{result.get('n_missoes_rede', 0)} missoes, "
                f"{result.get('n_decisoes', 0)} decisoes em {result.get('duracao', 0):.1f}s"
            )
        else:
            logger.error(f"Estrategista falhou: {result.get('erro', '?')}")
    except Exception as e:
        logger.error(f"Estrategista nao executado: {e}", exc_info=True)


def _executar_comparador() -> None:
    """Executa engine.executar_comparador() semanal (segunda 5h30)."""
    logger.info("Comparador: iniciando calculo de rankings...")
    try:
        from engine import executar_comparador
        result = executar_comparador()
        if result.get("ok"):
            logger.info(f"Comparador concluido: semana {result.get('semana')} em {result.get('duracao', 0):.1f}s")
        else:
            logger.error(f"Comparador falhou: {result.get('erro', '?')}")
    except Exception as e:
        logger.error(f"Comparador nao executado: {e}", exc_info=True)


def _executar_preditor() -> None:
    """Executa engine.executar_preditor() semanal (sexta 20h)."""
    logger.info("Preditor: iniciando projecoes...")
    try:
        from engine import executar_preditor
        result = executar_preditor()
        if result.get("ok"):
            logger.info(
                f"Preditor concluido: semana {result.get('semana')}, "
                f"{result.get('n_alertas', 0)} alerta(s) em {result.get('duracao', 0):.1f}s"
            )
        else:
            logger.error(f"Preditor falhou: {result.get('erro', '?')}")
    except Exception as e:
        logger.error(f"Preditor nao executado: {e}", exc_info=True)


def _executar_retroalimentador() -> None:
    """Executa engine.executar_retroalimentador() a cada 6h."""
    logger.info("Retroalimentador: verificando execucao de acoes...")
    try:
        from engine import executar_retroalimentador
        result = executar_retroalimentador()
        if result.get("ok"):
            logger.info(
                f"Retroalimentador concluido: {result.get('n_escalacoes', 0)} escalacao(es) "
                f"em {result.get('duracao', 0):.1f}s"
            )
        else:
            logger.error(f"Retroalimentador falhou: {result.get('erro', '?')}")
    except Exception as e:
        logger.error(f"Retroalimentador nao executado: {e}", exc_info=True)


def _executar_analista() -> None:
    """Executa llm_engine.executar_analista() semanal (domingo 23h)."""
    logger.info("Analista: iniciando analise integrada LLM...")
    try:
        from llm_engine import executar_analista
        result = executar_analista()
        if result.get("ok"):
            logger.info(
                f"Analista concluido: semana {result.get('semana')}, "
                f"fonte={result.get('fonte', '?')} em {result.get('duracao', 0):.1f}s"
            )
        else:
            logger.error(f"Analista falhou: {result.get('erro', '?')}")
    except Exception as e:
        logger.error(f"Analista nao executado: {e}", exc_info=True)


def _executar_conselheiro() -> None:
    """Executa engine.executar_conselheiro() semanal (segunda 5h)."""
    logger.info("Conselheiro: iniciando geracao de pauta PEEX...")
    try:
        from engine import executar_conselheiro
        result = executar_conselheiro()
        if result.get("ok"):
            logger.info(
                f"Conselheiro concluido: semana {result.get('semana')}, "
                f"unidades={result.get('unidades')} em {result.get('duracao', 0):.1f}s"
            )
        else:
            logger.error(f"Conselheiro falhou: {result.get('erro', '?')}")
    except Exception as e:
        logger.error(f"Conselheiro nao executado: {e}", exc_info=True)


def _executar_preparador() -> None:
    """Executa engine.executar_preparador() semanal (segunda 5h45).
    Consolida inteligencia de todos os robos para roteiro de reuniao."""
    logger.info("Preparador: iniciando geracao de roteiro de reuniao...")
    try:
        from engine import executar_preparador
        result = executar_preparador()
        if result.get("ok"):
            logger.info(
                f"Preparador concluido: semana {result.get('semana')}, "
                f"reuniao='{result.get('reuniao', '?')}' em {result.get('duracao', 0):.1f}s"
            )
        else:
            logger.error(f"Preparador falhou: {result.get('erro', '?')}")
    except Exception as e:
        logger.error(f"Preparador nao executado: {e}", exc_info=True)


# ---------------------------------------------------------------------------
# Modo daemon (APScheduler)
# ---------------------------------------------------------------------------

def run_daemon() -> None:
    """Inicia o scheduler APScheduler e bloqueia ate receber SIGTERM/SIGINT."""
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BlockingScheduler(timezone="America/Recife")

    scheduler.add_job(
        executar_atualizacao,
        CronTrigger(hour="8,12,18,20", minute=0, timezone="America/Recife"),
        id="atualizar_siga",
        name="Atualizacao SIGA",
        replace_existing=True,
    )

    # Estrategista semanal (domingo 22h)
    scheduler.add_job(
        _executar_estrategista,
        CronTrigger(day_of_week="sun", hour=22, minute=0, timezone="America/Recife"),
        id="estrategista_semanal",
        name="Estrategista Semanal PEEX",
        replace_existing=True,
    )

    # Analista semanal (domingo 23h — apos Estrategista)
    scheduler.add_job(
        _executar_analista,
        CronTrigger(day_of_week="sun", hour=23, minute=0, timezone="America/Recife"),
        id="analista_semanal",
        name="Analista LLM PEEX",
        replace_existing=True,
    )

    # Conselheiro semanal (segunda 5h)
    scheduler.add_job(
        _executar_conselheiro,
        CronTrigger(day_of_week="mon", hour=5, minute=0, timezone="America/Recife"),
        id="conselheiro_semanal",
        name="Conselheiro PEEX",
        replace_existing=True,
    )

    # Comparador semanal (segunda 5h30)
    scheduler.add_job(
        _executar_comparador,
        CronTrigger(day_of_week="mon", hour=5, minute=30, timezone="America/Recife"),
        id="comparador_semanal",
        name="Comparador PEEX",
        replace_existing=True,
    )

    # Preparador semanal (segunda 5h45 — apos Conselheiro e Comparador)
    scheduler.add_job(
        _executar_preparador,
        CronTrigger(day_of_week="mon", hour=5, minute=45, timezone="America/Recife"),
        id="preparador_semanal",
        name="Preparador Reuniao PEEX",
        replace_existing=True,
    )

    # Preditor semanal (sexta 20h)
    scheduler.add_job(
        _executar_preditor,
        CronTrigger(day_of_week="fri", hour=20, minute=0, timezone="America/Recife"),
        id="preditor_semanal",
        name="Preditor PEEX",
        replace_existing=True,
    )

    # Retroalimentador a cada 6h (8h, 14h, 20h, 2h)
    scheduler.add_job(
        _executar_retroalimentador,
        CronTrigger(hour="2,8,14,20", minute=30, timezone="America/Recife"),
        id="retroalimentador_continuo",
        name="Retroalimentador PEEX",
        replace_existing=True,
    )

    # Shutdown gracioso
    def _shutdown(signum, frame):
        sig_name = signal.Signals(signum).name
        logger.info(f"Recebido {sig_name}, encerrando scheduler...")
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    logger.info("=" * 60)
    logger.info("SCHEDULER STANDALONE INICIADO")
    logger.info("Horarios: 8h, 12h, 18h, 20h (America/Recife) + Estrategista dom 22h + Analista dom 23h + Conselheiro seg 5h + Comparador seg 5h30 + Preparador seg 5h45 + Preditor sex 20h + Retro 6h")
    logger.info(f"Health check: {HEALTH_FILE}")
    logger.info(f"Log: {LOG_FILE}")
    logger.info(f"PID: {os.getpid()}")
    logger.info("=" * 60)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler encerrado.")


# ---------------------------------------------------------------------------
# Modo --once (execucao imediata)
# ---------------------------------------------------------------------------

def run_once() -> int:
    """Executa uma unica atualizacao e retorna exit code (0=ok, 1=erro)."""
    logger.info("Modo --once: executando atualizacao imediata...")
    executar_atualizacao()
    health = read_health()
    if health.get("ok"):
        logger.info("Modo --once: concluido com sucesso.")
        return 0
    else:
        logger.error(f"Modo --once: falhou - {health.get('erro', '?')}")
        return 1


# ---------------------------------------------------------------------------
# Modo --health (verificacao de saude)
# ---------------------------------------------------------------------------

def show_health() -> int:
    """Exibe o status do health check e retorna exit code."""
    health = read_health()
    if not health:
        print("Nenhum health check encontrado. O scheduler ainda nao executou.")
        return 1

    last_run = health.get("last_run", "?")
    ok = health.get("ok", False)
    total = health.get("total", 0)
    erro = health.get("erro")
    duracao = health.get("duracao", 0)
    por_unidade = health.get("por_unidade", {})

    print(f"Ultima execucao: {last_run}")
    print(f"Status: {'OK' if ok else 'ERRO'}")
    if ok:
        print(f"Total de aulas: {total}")
        print(f"Duracao: {duracao:.0f}s")
        if por_unidade:
            for un, qtd in sorted(por_unidade.items()):
                print(f"  {un}: {qtd} aulas")
    else:
        print(f"Erro: {erro}")

    # Verifica se esta stale (>5 horas sem atualizar)
    try:
        last_dt = datetime.fromisoformat(last_run)
        delta = (datetime.now() - last_dt).total_seconds() / 3600
        if delta > 5:
            print(f"\nALERTA: Ultima atualizacao ha {delta:.1f} horas (>5h)")
            return 2
    except (ValueError, TypeError):
        pass

    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scheduler standalone para atualizacao do SIGA - Colegio ELO 2026"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Executa uma unica atualizacao e sai (ideal para cron jobs)",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Exibe status do ultimo health check e sai",
    )
    args = parser.parse_args()

    if args.health:
        sys.exit(show_health())
    elif args.once:
        sys.exit(run_once())
    else:
        run_daemon()


if __name__ == "__main__":
    main()
