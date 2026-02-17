"""
Scheduler para atualizacao automatica do SIGA.
Executa as 8h, 12h, 18h e 20h (horario de Recife).
Roda como thread em background dentro do processo Streamlit.
"""

import logging
import threading
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("scheduler_siga")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

_scheduler = None
_lock = threading.Lock()
_running = threading.Event()

# Guarda resultado da ultima atualizacao
_ultimo_resultado = {"timestamp": None, "ok": None, "total": None, "erro": None}


def _executar_atualizacao():
    """Executa a atualizacao do SIGA em background."""
    global _ultimo_resultado

    if _running.is_set():
        logger.warning("Atualizacao ja em andamento, pulando...")
        return

    _running.set()
    try:
        from atualizar_siga import run_update
        logger.info("Iniciando atualizacao automatica...")
        result = run_update()
        _ultimo_resultado = {
            "timestamp": datetime.now(),
            "ok": result.get("ok", False),
            "total": result.get("total", 0),
            "erro": result.get("erro"),
        }
        if result["ok"]:
            logger.info(f"Atualizacao OK: {result['total']} aulas em {result.get('duracao', 0):.0f}s")
        else:
            logger.error(f"Atualizacao falhou: {result.get('erro')}")
    except Exception as e:
        logger.error(f"Erro na atualizacao: {e}")
        _ultimo_resultado = {
            "timestamp": datetime.now(),
            "ok": False,
            "total": 0,
            "erro": str(e),
        }
    finally:
        _running.clear()


def iniciar_scheduler():
    """Inicia o scheduler se ainda nao estiver rodando. Retorna a instancia."""
    global _scheduler

    with _lock:
        if _scheduler is not None:
            return _scheduler

        _scheduler = BackgroundScheduler(timezone="America/Recife")

        # Atualiza as 8h, 12h, 18h e 20h (horario de Recife)
        _scheduler.add_job(
            _executar_atualizacao,
            CronTrigger(hour="8,12,18,20", minute=0, timezone="America/Recife"),
            id="atualizar_siga",
            name="Atualizacao SIGA",
            replace_existing=True,
        )

        _scheduler.start()
        logger.info("Scheduler iniciado: atualizacoes as 8h, 12h, 18h e 20h (Recife)")
        return _scheduler


def executar_agora():
    """Dispara atualizacao manual em thread separada. Retorna True se iniciou."""
    if _running.is_set():
        return False
    t = threading.Thread(target=_executar_atualizacao, daemon=True)
    t.start()
    return True


def is_running():
    """Retorna True se uma atualizacao esta em andamento."""
    return _running.is_set()


def ultimo_resultado():
    """Retorna dict com info da ultima atualizacao."""
    return dict(_ultimo_resultado)


def proxima_execucao():
    """Retorna datetime da proxima execucao agendada."""
    if _scheduler is None:
        return None
    job = _scheduler.get_job("atualizar_siga")
    if job and job.next_run_time:
        return job.next_run_time
    return None
