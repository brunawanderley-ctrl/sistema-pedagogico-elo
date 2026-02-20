#!/usr/bin/env python3
"""
ATUALIZAÇÃO AUTOMÁTICA DO DIÁRIO DE CLASSE - COLÉGIO ELO 2026

Combina extração via API + salvamento direto em fato_Aulas.csv.
Pode ser executado standalone ou via botão no Sistema Pedagógico.

Fluxo:
1. Login via Playwright (headless) - captura cookies
2. Extração paralela via requests (4 unidades simultâneas)
3. Salva diretamente em power_bi/fato_Aulas.csv
4. Salva backup JSON timestampado
"""

import json
import csv
import os
import re
import sys
import requests
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

CONFIG = {
    "instituicao": os.environ.get("SIGA_INSTITUICAO", "COLEGIOELO"),
    "login": os.environ.get("SIGA_LOGIN", "bruna"),
    "senha": os.environ.get("SIGA_SENHA", ""),
    "unidades": [
        {"nome": "Boa Viagem", "codigo": "BV", "periodo": 80},
        {"nome": "Candeias", "codigo": "CD", "periodo": 78},
        {"nome": "Janga", "codigo": "JG", "periodo": 79},
        {"nome": "Cordeiro", "codigo": "CDR", "periodo": 77},
    ],
}

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "power_bi"
API_BASE = "https://siga02.activesoft.com.br"

INICIO_ANO_LETIVO = datetime(2026, 1, 26)

# ============================================================
# Normalização delegada para normalizacao.py (fonte única de verdade)
# ============================================================
from normalizacao import (
    SERIE_NORMALIZACAO,
    DISCIPLINA_NORMALIZACAO,
    SERIES_FUND_II as _SERIES_FUND_II_LIST,
    normalizar_serie,
    normalizar_disciplina,
    normalizar_nome_professor,
    serie_eh_fund_ii,
)

# atualizar_siga.py usava set; normalizacao.py exporta list.
# Convertemos para set para manter a semantica de lookup O(1).
SERIES_FUND_II = set(_SERIES_FUND_II_LIST)

FIELDNAMES = [
    'aula_id', 'data', 'unidade', 'curso', 'disciplina', 'serie', 'turma',
    'professor', 'professor_normalizado', 'numero_aula', 'conteudo', 'tarefa',
    'situacao', 'frequencia', 'semana_letiva', 'progressao_key'
]


def calcular_semana_letiva(data_str):
    if not data_str:
        return 0
    try:
        data = datetime.strptime(data_str[:10], '%Y-%m-%d')
        dias = (data - INICIO_ANO_LETIVO).days
        return max(1, dias // 7 + 1) if dias >= 0 else 0
    except (ValueError, TypeError):
        return 0


def fazer_login_e_capturar_cookies():
    """Faz login com Playwright (headless) e retorna os cookies."""
    print("Fazendo login no SIGA...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://siga.activesoft.com.br/login/")
        page.wait_for_timeout(2000)

        page.fill('#codigoInstituicao', CONFIG["instituicao"])
        page.fill('#id_login', CONFIG["login"])
        page.fill('#id_senha', CONFIG["senha"])
        page.click('button:has-text("ENTRAR")')
        page.wait_for_timeout(4000)

        page.click('text="1 - BV (Boa Viagem)"', timeout=5000)
        page.wait_for_timeout(3000)

        cookies = context.cookies()
        browser.close()

    cookie_dict = {c['name']: c['value'] for c in cookies}
    print(f"  Login OK! {len(cookie_dict)} cookies capturados")
    return cookie_dict


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, max=15),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
    before_sleep=lambda rs: print(f"  Retry #{rs.attempt_number} para {rs.args[1]['codigo']}...")
)
def extrair_diarios_unidade(session, unidade):
    """Extrai diários de uma unidade via API (requests). Retry automático em falha de rede."""
    periodo = unidade['periodo']
    codigo = unidade['codigo']
    aulas_formatadas = []

    try:
        url = f"{API_BASE}/api/v1/diario/diario/lista/?limit=1000&offset=0&periodo={periodo}"
        resp = session.get(url, timeout=30)

        if resp.status_code != 200:
            print(f"  ERRO {codigo}: HTTP {resp.status_code}")
            return codigo, [], []

        data = resp.json()
        lista_diarios = data.get('results', [])
        aulas_raw = []

        for diario in lista_diarios:
            nome_curso = diario.get('nome_curso', '') or ''
            fase_nota = diario.get('fase_nota_nome', '') or ''

            eh_fund_ii = 'Fundamental II' in nome_curso
            eh_medio = 'Médio' in nome_curso
            eh_1_trimestre = '1º TRIMESTRE' in fase_nota

            if (eh_fund_ii or eh_medio) and eh_1_trimestre:
                diario_id = diario.get('id')
                qtd_aulas = diario.get('qtd_aula_registradas', 0)

                if diario_id and qtd_aulas > 0:
                    try:
                        aulas_url = f"{API_BASE}/api/v1/diario/diario_aula/?limit=100&offset=0&diario={diario_id}&situacao_aula=TODAS"
                        aulas_resp = session.get(aulas_url, timeout=15)

                        if aulas_resp.status_code == 200:
                            aulas_data = aulas_resp.json()
                            for aula in aulas_data.get('results', []):
                                # Guarda raw para backup JSON
                                aula_raw = dict(aula)
                                aula_raw['unidade'] = codigo
                                aula_raw['curso'] = nome_curso
                                aula_raw['disciplina'] = diario.get('disciplina_nome', '')
                                aula_raw['serie'] = diario.get('nome_serie', '')
                                aula_raw['turma'] = diario.get('nome_turma', '')
                                # professor_nome vem da AULA (não do diário)
                                if not aula_raw.get('professor_nome'):
                                    aula_raw['professor_nome'] = diario.get('professor_nome', '')
                                aulas_raw.append(aula_raw)

                                # Formata para CSV com normalização
                                data_aula = aula.get('data_aula', '') or ''
                                if data_aula:
                                    data_aula = data_aula[:10]

                                serie = normalizar_serie(diario.get('nome_serie', ''))
                                disciplina = normalizar_disciplina(diario.get('disciplina_nome', ''))

                                # Sociologia no Fund II é na verdade Filosofia
                                if disciplina == 'Sociologia' and serie in SERIES_FUND_II:
                                    disciplina = 'Filosofia'

                                nome_professor = aula.get('professor_nome', '') or diario.get('professor_nome', '')
                                prof_norm = normalizar_nome_professor(nome_professor)
                                semana = calcular_semana_letiva(data_aula)

                                # Limpa multi-line em conteudo e tarefa
                                conteudo = (aula.get('conteudo_ministrado', '') or '')[:500]
                                conteudo = conteudo.replace('\n', ' | ').replace('\r', '')
                                tarefa = (aula.get('tarefa', '') or '')[:500]
                                tarefa = tarefa.replace('\n', ' | ').replace('\r', '')

                                pkey = f"{disciplina}|{serie}|{semana}" if disciplina and serie and semana else ''

                                aulas_formatadas.append({
                                    'aula_id': aula.get('id', ''),
                                    'data': data_aula,
                                    'unidade': codigo,
                                    'curso': nome_curso,
                                    'disciplina': disciplina,
                                    'serie': serie,
                                    'turma': diario.get('nome_turma', ''),
                                    'professor': nome_professor,
                                    'professor_normalizado': prof_norm,
                                    'numero_aula': aula.get('numero_aula', ''),
                                    'conteudo': conteudo,
                                    'tarefa': tarefa,
                                    'situacao': aula.get('situacao_aula', ''),
                                    'frequencia': aula.get('frequencia', ''),
                                    'semana_letiva': semana,
                                    'progressao_key': pkey,
                                })
                    except Exception as e:
                        print(f"  WARN {codigo}: diario {diario_id} falhou: {e}")

        print(f"  {codigo}: {len(aulas_formatadas)} aulas extraidas")
        return codigo, aulas_formatadas, aulas_raw

    except Exception as e:
        print(f"  ERRO {codigo}: {e}")
        return codigo, [], []


def run_update():
    """Executa a atualizacao e retorna dict com resultado.
    Chamavel pelo scheduler e pelo botao do Streamlit (sem sys.exit).
    """
    if not CONFIG["senha"]:
        return {"ok": False, "erro": "SIGA_SENHA nao definida"}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    print("=" * 60)
    print("ATUALIZACAO DO DIARIO DE CLASSE - SIGA")
    print(f"Inicio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

    inicio = datetime.now()

    # 1. Login
    try:
        cookies = fazer_login_e_capturar_cookies()
    except Exception as e:
        print(f"ERRO no login: {e}")
        return {"ok": False, "erro": f"Falha no login: {e}"}

    # 2. Sessao requests
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
    })

    # 3. Extrai em paralelo
    print("\nExtraindo dados de todas as unidades...")

    todas_aulas_csv = []
    todas_aulas_raw = []
    resultados = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(extrair_diarios_unidade, session, u): u
            for u in CONFIG['unidades']
        }

        for future in as_completed(futures):
            codigo, aulas_csv, aulas_raw = future.result()
            resultados[codigo] = len(aulas_csv)
            todas_aulas_csv.extend(aulas_csv)
            todas_aulas_raw.extend(aulas_raw)

    # 4. Validacao pos-extracao
    unidades_ok = [k for k, v in resultados.items() if v > 0]
    unidades_falha = set(['BV', 'CD', 'JG', 'CDR']) - set(unidades_ok)
    if unidades_falha:
        print(f"\n  ⚠️  ALERTA: Unidades sem dados: {unidades_falha}")
    if len(todas_aulas_csv) < 100:
        print(f"  ⚠️  ALERTA: Apenas {len(todas_aulas_csv)} aulas (esperado >500)")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 5. Salva CSV (fato_Aulas.csv)
    csv_path = OUTPUT_DIR / 'fato_Aulas.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(todas_aulas_csv)

    print(f"\n  fato_Aulas.csv: {len(todas_aulas_csv)} aulas salvas")

    # 6. Backup JSON (em /tmp no cloud para nao poluir)
    import tempfile
    backup_dir = Path(tempfile.gettempdir()) if os.environ.get('RENDER') else SCRIPT_DIR
    json_path = backup_dir / f"backup_aulas_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "resultados_por_unidade": resultados,
            "total_aulas": len(todas_aulas_raw),
            "aulas": todas_aulas_raw,
        }, f, indent=2, ensure_ascii=False)

    print(f"  Backup JSON: {json_path.name}")

    # Resumo
    duracao = (datetime.now() - inicio).total_seconds()

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    for codigo, total in sorted(resultados.items()):
        print(f"  {codigo}: {total} aulas")
    print(f"\n  TOTAL: {len(todas_aulas_csv)} aulas")
    print(f"  Tempo: {duracao:.1f} segundos")
    print("=" * 60)

    return {
        "ok": True,
        "total": len(todas_aulas_csv),
        "por_unidade": resultados,
        "duracao": duracao,
    }


def main():
    if not CONFIG["senha"]:
        print("ERRO: Variavel de ambiente SIGA_SENHA nao definida.")
        print("  export SIGA_SENHA='sua_senha_aqui'")
        sys.exit(1)

    result = run_update()
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
