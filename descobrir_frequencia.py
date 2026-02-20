#!/usr/bin/env python3
"""
AGENTE THETA - CACADOR DE ENDPOINTS OCULTOS DE FREQUENCIA
==========================================================
Testa exaustivamente todos os endpoints hipoteticos do SIGA ActiveSoft
para encontrar dados de frequencia/presenca individual de alunos.

Arena 4 - Endpoint Discovery - 2026-02-20

Estrategia:
1. Faz login no SIGA via Playwright (reutiliza padrao existente)
2. Obtem IDs reais (diario, aula, aluno, turma)
3. Testa 70+ variantes de endpoint sistematicamente
4. Classifica e pontua cada grupo
5. Salva relatorio completo em JSON

Modo dry-run: Se SIGA_SENHA nao estiver definida, gera lista de endpoints
sem executar requests.

USO:
  export SIGA_SENHA='sua_senha'
  python3 descobrir_frequencia.py
"""

import json
import os
import sys
import time
import requests
from datetime import datetime
from pathlib import Path

# =============================================================================
# CONFIGURACAO
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "power_bi"
API_BASE = "https://siga02.activesoft.com.br"
SIGA_LOGIN = "https://siga.activesoft.com.br"
TIMEOUT = 10  # segundos por request

CONFIG = {
    "instituicao": os.environ.get("SIGA_INSTITUICAO", "COLEGIOELO"),
    "login": os.environ.get("SIGA_LOGIN", "bruna"),
    "senha": os.environ.get("SIGA_SENHA", ""),
    "unidades": [
        {"nome": "Boa Viagem", "codigo": "BV", "periodo": 80, "seletor": '1 - BV (Boa Viagem)'},
        {"nome": "Candeias", "codigo": "CD", "periodo": 78, "seletor": '2 - CD (Jaboatão)'},
        {"nome": "Janga", "codigo": "JG", "periodo": 79, "seletor": '3 - JG (Paulista)'},
        {"nome": "Cordeiro", "codigo": "CDR", "periodo": 77, "seletor": '4 - CDR (Cordeiro)'},
    ],
}

# =============================================================================
# KEYWORDS que indicam dados de frequencia individual
# =============================================================================

FREQUENCIA_KEYWORDS = [
    'presente', 'ausente', 'falta', 'presenca', 'frequencia',
    'chamada', 'attendance', 'absent', 'present',
    'presenca_aluno', 'falta_aluno', 'situacao_presenca',
    'total_faltas', 'total_presencas', 'percentual_frequencia',
    'quantidade_faltas', 'is_presente', 'is_ausente',
    'NomeAluno', 'IdAluno',  # combinado com presenca
]

# =============================================================================
# LOGIN (reutiliza padrao do projeto)
# =============================================================================

def fazer_login_playwright():
    """Faz login no SIGA via Playwright e retorna cookies."""
    from playwright.sync_api import sync_playwright

    print("[LOGIN] Iniciando login via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(f"{SIGA_LOGIN}/login/")
        page.wait_for_timeout(2000)

        page.fill('#codigoInstituicao', CONFIG["instituicao"])
        page.fill('#id_login', CONFIG["login"])
        page.fill('#id_senha', CONFIG["senha"])
        page.click('button:has-text("ENTRAR")')
        page.wait_for_timeout(4000)

        # Seleciona unidade BV (primeira)
        page.click('text="1 - BV (Boa Viagem)"', timeout=5000)
        page.wait_for_timeout(3000)

        cookies = context.cookies()
        browser.close()

    cookie_dict = {c['name']: c['value'] for c in cookies}
    print(f"[LOGIN] OK! {len(cookie_dict)} cookies capturados")
    return cookie_dict


def criar_session(cookies):
    """Cria requests.Session com cookies e headers."""
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    return session


# =============================================================================
# OBTER IDs REAIS
# =============================================================================

def obter_ids_reais(session):
    """
    Obtem IDs reais de diario, aula, aluno e turma para usar nos testes.
    Retorna dict com: diario_id, aula_id, aluno_id, turma_id, periodo
    """
    ids = {
        'diario_id': None,
        'aula_id': None,
        'aluno_id': None,
        'turma_id': None,
        'periodo': 80,
    }

    print("\n[IDs] Obtendo IDs reais para testes...")

    # 1. Buscar diario com aulas registradas
    print("  [1/4] Buscando diario com aulas...")
    try:
        url = f"{API_BASE}/api/v1/diario/diario/lista/?limit=50&offset=0&periodo=80"
        resp = session.get(url, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            diarios = data.get('results', [])
            for d in diarios:
                qtd = d.get('qtd_aula_registradas', 0)
                if qtd and qtd > 0:
                    ids['diario_id'] = d['id']
                    ids['turma_id'] = d.get('turma')
                    print(f"    Diario: {d['id']} ({d.get('disciplina_nome', '?')}, "
                          f"{d.get('nome_serie', '?')}, {qtd} aulas)")
                    break
            if not ids['diario_id'] and diarios:
                ids['diario_id'] = diarios[0]['id']
                ids['turma_id'] = diarios[0].get('turma')
                print(f"    Diario (fallback, sem aulas): {ids['diario_id']}")
        else:
            print(f"    ERRO: HTTP {resp.status_code}")
    except Exception as e:
        print(f"    ERRO: {e}")

    # 2. Buscar aula com frequencia CONCLUIDA
    if ids['diario_id']:
        print("  [2/4] Buscando aula com frequencia CONCLUIDA...")
        try:
            url = (f"{API_BASE}/api/v1/diario/diario_aula/"
                   f"?limit=50&offset=0&diario={ids['diario_id']}&situacao_aula=TODAS")
            resp = session.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                aulas = data.get('results', [])
                for a in aulas:
                    if a.get('frequencia') == 'CONCLUIDA':
                        ids['aula_id'] = a['id']
                        print(f"    Aula CONCLUIDA: {a['id']} (data: {a.get('data_aula', '?')})")
                        break
                if not ids['aula_id'] and aulas:
                    ids['aula_id'] = aulas[0]['id']
                    print(f"    Aula (fallback, nao CONCLUIDA): {ids['aula_id']} "
                          f"(freq: {aulas[0].get('frequencia', '?')})")
                if not aulas:
                    print("    Nenhuma aula encontrada neste diario")
            else:
                print(f"    ERRO: HTTP {resp.status_code}")
        except Exception as e:
            print(f"    ERRO: {e}")

    # 3. Buscar aluno real
    if ids['diario_id']:
        print("  [3/4] Buscando aluno...")
        try:
            url = (f"{API_BASE}/api/v1/diario/{ids['diario_id']}/alunos/lista/"
                   f"?busca=&apenas_ativos=false&ensino_superior=0")
            resp = session.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                ct = resp.headers.get('content-type', '')
                if 'json' in ct:
                    alunos = resp.json()
                    if isinstance(alunos, list) and alunos:
                        ids['aluno_id'] = alunos[0].get('IdAluno')
                        print(f"    Aluno: {ids['aluno_id']} ({alunos[0].get('NomeAluno', '?')[:30]})")
                    elif isinstance(alunos, dict):
                        results = alunos.get('results', [])
                        if results:
                            ids['aluno_id'] = results[0].get('IdAluno') or results[0].get('id')
                            print(f"    Aluno: {ids['aluno_id']}")
            else:
                print(f"    ERRO: HTTP {resp.status_code}")
        except Exception as e:
            print(f"    ERRO: {e}")

    # 4. Se nao temos turma_id, tentar via alunoturma
    if not ids['turma_id']:
        print("  [4/4] Buscando turma via alunoturma...")
        try:
            url = f"{API_BASE}/api/v1/alunoturma/?periodo=80&limit=1"
            resp = session.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get('results', [])
                if results:
                    ids['turma_id'] = results[0].get('turma')
                    print(f"    Turma: {ids['turma_id']}")
        except Exception as e:
            print(f"    ERRO: {e}")
    else:
        print(f"  [4/4] Turma ja obtida: {ids['turma_id']}")

    print(f"\n[IDs] Resultado final:")
    for k, v in ids.items():
        status = "OK" if v is not None else "FALTANDO"
        print(f"  {k}: {v} [{status}]")

    return ids


# =============================================================================
# GERADOR DE ENDPOINTS
# =============================================================================

def gerar_endpoints(ids):
    """Gera a lista completa de endpoints para testar, substituindo IDs reais."""
    diario_id = ids.get('diario_id') or 99999
    aula_id = ids.get('aula_id') or 99999
    aluno_id = ids.get('aluno_id') or 99999
    turma_id = ids.get('turma_id') or 99999
    periodo = ids.get('periodo', 80)

    endpoints = []

    def add(grupo, nome, url, headers_extra=None):
        endpoints.append({
            'grupo': grupo,
            'nome': nome,
            'url': url,
            'headers_extra': headers_extra or {},
        })

    # =========================================================================
    # GRUPO 1: Frequencia por diario (padrao DRF modelo/modelo/lista/)
    # =========================================================================
    g = "01_frequencia_diario"
    add(g, "diario/{id}/chamada/lista/",
        f"/api/v1/diario/{diario_id}/chamada/lista/")
    add(g, "diario/{id}/frequencia/lista/",
        f"/api/v1/diario/{diario_id}/frequencia/lista/")
    add(g, "diario/{id}/presencas/",
        f"/api/v1/diario/{diario_id}/presencas/")
    add(g, "diario/{id}/faltas/lista/",
        f"/api/v1/diario/{diario_id}/faltas/lista/")
    add(g, "diario/{id}/chamadas/lista/",
        f"/api/v1/diario/{diario_id}/chamadas/lista/")
    add(g, "diario/{id}/presencas/lista/",
        f"/api/v1/diario/{diario_id}/presencas/lista/")
    add(g, "diario/{id}/frequencia_aluno/lista/",
        f"/api/v1/diario/{diario_id}/frequencia_aluno/lista/")
    add(g, "diario/{id}/registro_chamada/lista/",
        f"/api/v1/diario/{diario_id}/registro_chamada/lista/")

    # =========================================================================
    # GRUPO 2: Chamada online
    # =========================================================================
    g = "02_chamada_online"
    add(g, "diario/chamada_online/?diario=",
        f"/api/v1/diario/chamada_online/?diario={diario_id}")
    add(g, "diario/chamada_online/lista/?diario=",
        f"/api/v1/diario/chamada_online/lista/?diario={diario_id}")
    add(g, "chamada_online/?diario=",
        f"/api/v1/chamada_online/?diario={diario_id}")
    add(g, "chamada/?diario=",
        f"/api/v1/chamada/?diario={diario_id}")
    add(g, "chamada_online/chamada_online/lista/?diario=",
        f"/api/v1/chamada_online/chamada_online/lista/?diario={diario_id}")

    # =========================================================================
    # GRUPO 3: Frequencia de aula especifica
    # =========================================================================
    g = "03_frequencia_aula"
    add(g, "diario/diario_aula/{aula}/alunos/lista/",
        f"/api/v1/diario/diario_aula/{aula_id}/alunos/lista/")
    add(g, "diario/diario_aula/{aula}/chamada/lista/",
        f"/api/v1/diario/diario_aula/{aula_id}/chamada/lista/")
    add(g, "diario/diario_aula/{aula}/presenca/lista/",
        f"/api/v1/diario/diario_aula/{aula_id}/presenca/lista/")
    add(g, "diario/diario_aula/{aula}/frequencia/lista/",
        f"/api/v1/diario/diario_aula/{aula_id}/frequencia/lista/")
    add(g, "diario/diario_aula_aluno/?diario_aula=",
        f"/api/v1/diario/diario_aula_aluno/?diario_aula={aula_id}")
    add(g, "diario/diario_aula_aluno/?diario=",
        f"/api/v1/diario/diario_aula_aluno/?diario={diario_id}")
    add(g, "diario_aula_aluno/?diario=",
        f"/api/v1/diario_aula_aluno/?diario={diario_id}")
    add(g, "diario_aula_aluno/?diario_aula=",
        f"/api/v1/diario_aula_aluno/?diario_aula={aula_id}")
    add(g, "diario/diario_aula_aluno/lista/?diario=",
        f"/api/v1/diario/diario_aula_aluno/lista/?diario={diario_id}")
    add(g, "diario/diario_aula_aluno/lista/?diario_aula=",
        f"/api/v1/diario/diario_aula_aluno/lista/?diario_aula={aula_id}")
    add(g, "diario_aula_aluno/lista/?diario=",
        f"/api/v1/diario_aula_aluno/lista/?diario={diario_id}")
    add(g, "diario/diario_aula/{aula}/alunos/",
        f"/api/v1/diario/diario_aula/{aula_id}/alunos/")

    # =========================================================================
    # GRUPO 4: Frequencia do aluno (top-level)
    # =========================================================================
    g = "04_frequencia_aluno"
    add(g, "frequencia_aluno/?diario=",
        f"/api/v1/frequencia_aluno/?diario={diario_id}")
    add(g, "frequencia_aluno/?periodo=80",
        f"/api/v1/frequencia_aluno/?periodo={periodo}")
    add(g, "frequencia_aluno/?aluno=",
        f"/api/v1/frequencia_aluno/?aluno={aluno_id}")
    add(g, "frequencia_aluno/?turma=",
        f"/api/v1/frequencia_aluno/?turma={turma_id}")
    add(g, "falta_aluno/?diario=",
        f"/api/v1/falta_aluno/?diario={diario_id}")
    add(g, "falta_aluno/?periodo=80",
        f"/api/v1/falta_aluno/?periodo={periodo}")
    add(g, "presenca_aluno/?diario=",
        f"/api/v1/presenca_aluno/?diario={diario_id}")
    add(g, "frequencia_aluno/frequencia_aluno/lista/?diario=",
        f"/api/v1/frequencia_aluno/frequencia_aluno/lista/?diario={diario_id}")
    add(g, "falta_aluno/falta_aluno/lista/?diario=",
        f"/api/v1/falta_aluno/falta_aluno/lista/?diario={diario_id}")

    # =========================================================================
    # GRUPO 5: Apuracao/registro
    # =========================================================================
    g = "05_apuracao_registro"
    add(g, "apuracao_frequencia/?periodo=80",
        f"/api/v1/apuracao_frequencia/?periodo={periodo}")
    add(g, "apuracao_frequencia/?diario=",
        f"/api/v1/apuracao_frequencia/?diario={diario_id}")
    add(g, "registro_frequencia/?diario=",
        f"/api/v1/registro_frequencia/?diario={diario_id}")
    add(g, "diario/registro_frequencia/?diario=",
        f"/api/v1/diario/registro_frequencia/?diario={diario_id}")
    add(g, "diario/diario_frequencia/?diario=",
        f"/api/v1/diario/diario_frequencia/?diario={diario_id}")
    add(g, "diario/diario_frequencia/lista/?diario=",
        f"/api/v1/diario/diario_frequencia/lista/?diario={diario_id}")
    add(g, "apuracao_frequencia/apuracao_frequencia/lista/?periodo=",
        f"/api/v1/apuracao_frequencia/apuracao_frequencia/lista/?periodo={periodo}")
    add(g, "registro_frequencia/registro_frequencia/lista/?diario=",
        f"/api/v1/registro_frequencia/registro_frequencia/lista/?diario={diario_id}")

    # =========================================================================
    # GRUPO 6: Frequencia em lote
    # =========================================================================
    g = "06_frequencia_lote"
    add(g, "diario/frequencia_em_lote/lista/?periodo=80",
        f"/api/v1/diario/frequencia_em_lote/lista/?periodo={periodo}")
    add(g, "frequencia_em_lote/?periodo=80",
        f"/api/v1/frequencia_em_lote/?periodo={periodo}")
    add(g, "frequencia_em_lote/resumo/?periodo=80",
        f"/api/v1/frequencia_em_lote/resumo/?periodo={periodo}")
    add(g, "frequencia_em_lote/frequencia_em_lote/lista/?periodo=80",
        f"/api/v1/frequencia_em_lote/frequencia_em_lote/lista/?periodo={periodo}")
    add(g, "diario/frequencia_em_lote/?diario=",
        f"/api/v1/diario/frequencia_em_lote/?diario={diario_id}")

    # =========================================================================
    # GRUPO 7: Fields/select exploracao
    # =========================================================================
    g = "07_fields_select"
    add(g, "fields/select/frequencia/",
        f"/api/v1/fields/select/frequencia/")
    add(g, "fields/select/chamada/",
        f"/api/v1/fields/select/chamada/")
    add(g, "fields/select/diario_aula/?diario=",
        f"/api/v1/fields/select/diario_aula/?diario={diario_id}")
    add(g, "fields/select/diario_frequencia/",
        f"/api/v1/fields/select/diario_frequencia/")
    add(g, "fields/select/apuracao_frequencia/",
        f"/api/v1/fields/select/apuracao_frequencia/")
    add(g, "fields/select/falta/",
        f"/api/v1/fields/select/falta/")
    add(g, "fields/select/presenca/",
        f"/api/v1/fields/select/presenca/")
    add(g, "fields/select/frequencia_aluno/",
        f"/api/v1/fields/select/frequencia_aluno/")
    add(g, "fields/select/diario_aula_aluno/",
        f"/api/v1/fields/select/diario_aula_aluno/")
    add(g, "fields/select/chamada_online/",
        f"/api/v1/fields/select/chamada_online/")
    add(g, "fields/select/registro_frequencia/",
        f"/api/v1/fields/select/registro_frequencia/")
    add(g, "fields/select/falta_aluno/",
        f"/api/v1/fields/select/falta_aluno/")
    add(g, "fields/select/presenca_aluno/",
        f"/api/v1/fields/select/presenca_aluno/")

    # =========================================================================
    # GRUPO 8: Relatorios
    # =========================================================================
    g = "08_relatorios"
    add(g, "relatorio/frequencia/?periodo=80",
        f"/api/v1/relatorio/frequencia/?periodo={periodo}")
    add(g, "relatorio/faltas/?periodo=80",
        f"/api/v1/relatorio/faltas/?periodo={periodo}")
    add(g, "relatorio/diario_classe/?diario=",
        f"/api/v1/relatorio/diario_classe/?diario={diario_id}")
    add(g, "relatorio/boletim/?aluno=",
        f"/api/v1/relatorio/boletim/?aluno={aluno_id}")
    add(g, "exportar/frequencia/?periodo=80",
        f"/api/v1/exportar/frequencia/?periodo={periodo}")
    add(g, "relatorio/relatorio/lista/?periodo=80",
        f"/api/v1/relatorio/relatorio/lista/?periodo={periodo}")
    add(g, "relatorio/frequencia_aluno/?aluno=",
        f"/api/v1/relatorio/frequencia_aluno/?aluno={aluno_id}")
    add(g, "exportar/diario/?diario=",
        f"/api/v1/exportar/diario/?diario={diario_id}")

    # =========================================================================
    # GRUPO 9: Chamada por modelo (padrao DRF)
    # =========================================================================
    g = "09_chamada_modelo_drf"
    add(g, "chamada/chamada/lista/?diario=",
        f"/api/v1/chamada/chamada/lista/?diario={diario_id}")
    add(g, "chamada/chamada/crud/{aula}/",
        f"/api/v1/chamada/chamada/crud/{aula_id}/")
    add(g, "presenca/presenca/lista/?diario=",
        f"/api/v1/presenca/presenca/lista/?diario={diario_id}")
    add(g, "falta/falta/lista/?diario=",
        f"/api/v1/falta/falta/lista/?diario={diario_id}")
    add(g, "chamada/chamada/lista/?diario_aula=",
        f"/api/v1/chamada/chamada/lista/?diario_aula={aula_id}")
    add(g, "presenca/presenca/lista/?diario_aula=",
        f"/api/v1/presenca/presenca/lista/?diario_aula={aula_id}")

    # =========================================================================
    # GRUPO 10: Portal professor
    # =========================================================================
    g = "10_portal_professor"
    add(g, "portal_professor/frequencia/?diario=",
        f"/api/v1/portal_professor/frequencia/?diario={diario_id}")
    add(g, "portal_professor/chamada/?diario=",
        f"/api/v1/portal_professor/chamada/?diario={diario_id}")
    add(g, "portal_professor/diario/{id}/chamada/",
        f"/api/v1/portal_professor/diario/{diario_id}/chamada/")
    add(g, "portal_professor/diario/{id}/frequencia/",
        f"/api/v1/portal_professor/diario/{diario_id}/frequencia/")
    add(g, "portal_professor/diario/{id}/alunos/",
        f"/api/v1/portal_professor/diario/{diario_id}/alunos/")
    add(g, "portal_professor/portal_professor/lista/?diario=",
        f"/api/v1/portal_professor/portal_professor/lista/?diario={diario_id}")

    # =========================================================================
    # GRUPO 11: Headers especiais (Accept: application/json nos endpoints SPA)
    # =========================================================================
    g = "11_headers_especiais"
    json_headers = {'Accept': 'application/json'}
    add(g, "diario/{id}/chamada/ [Accept:json]",
        f"/api/v1/diario/{diario_id}/chamada/", json_headers)
    add(g, "diario/{id}/frequencia/ [Accept:json]",
        f"/api/v1/diario/{diario_id}/frequencia/", json_headers)
    add(g, "diario/{id}/notas_faltas/ [Accept:json]",
        f"/api/v1/diario/{diario_id}/notas_faltas/", json_headers)
    add(g, "planilha_notas_faltas/?diario= [Accept:json]",
        f"/api/v1/planilha_notas_faltas/?diario={diario_id}", json_headers)
    add(g, "diario/{id}/notas/ [Accept:json]",
        f"/api/v1/diario/{diario_id}/notas/", json_headers)
    add(g, "diario/{id}/chamada/ [format=json]",
        f"/api/v1/diario/{diario_id}/chamada/?format=json")
    add(g, "diario/{id}/frequencia/ [format=json]",
        f"/api/v1/diario/{diario_id}/frequencia/?format=json")
    add(g, "diario/{id}/chamada/ [format=api]",
        f"/api/v1/diario/{diario_id}/chamada/?format=api")

    # =========================================================================
    # GRUPO 12: Swagger/docs
    # =========================================================================
    g = "12_swagger_docs"
    add(g, "/docs/",
        f"/docs/")
    add(g, "/swagger/",
        f"/swagger/")
    add(g, "/api/docs/",
        f"/api/docs/")
    add(g, "/api/swagger.json",
        f"/api/swagger.json")
    add(g, "/api/v1/swagger.json",
        f"/api/v1/swagger.json")
    add(g, "/api/v1/?format=openapi",
        f"/api/v1/?format=openapi")
    add(g, "/api/v1/?format=api",
        f"/api/v1/?format=api")
    add(g, "/api/schema/",
        f"/api/schema/")
    add(g, "/openapi.json",
        f"/openapi.json")
    add(g, "/api/v1/schema/",
        f"/api/v1/schema/")
    # Tambem no dominio siga (nao siga02)
    add(g, "siga.activesoft/docs/ [dominio siga]",
        f"https://siga.activesoft.com.br/docs/")
    add(g, "siga.activesoft/swagger/ [dominio siga]",
        f"https://siga.activesoft.com.br/swagger/")
    add(g, "siga.activesoft/api/docs/ [dominio siga]",
        f"https://siga.activesoft.com.br/api/docs/")

    # =========================================================================
    # GRUPO 13: Tentativas adicionais criativas
    # =========================================================================
    g = "13_criativos"
    add(g, "diario/diario/{id}/chamada/",
        f"/api/v1/diario/diario/{diario_id}/chamada/")
    add(g, "diario/diario/{id}/frequencia/",
        f"/api/v1/diario/diario/{diario_id}/frequencia/")
    add(g, "diario/diario/{id}/alunos/frequencia/",
        f"/api/v1/diario/diario/{diario_id}/alunos/frequencia/")
    add(g, "diario/diario/crud/{id}/ (detalhes diario)",
        f"/api/v1/diario/diario/crud/{diario_id}/")
    add(g, "diario/diario_aula/crud/{aula}/ (detalhes aula)",
        f"/api/v1/diario/diario_aula/crud/{aula_id}/")
    add(g, "aula_frequencia/?diario=",
        f"/api/v1/aula_frequencia/?diario={diario_id}")
    add(g, "aula_frequencia/?diario_aula=",
        f"/api/v1/aula_frequencia/?diario_aula={aula_id}")
    add(g, "aula_frequencia/aula_frequencia/lista/?diario=",
        f"/api/v1/aula_frequencia/aula_frequencia/lista/?diario={diario_id}")
    add(g, "diario/aula_frequencia/?diario=",
        f"/api/v1/diario/aula_frequencia/?diario={diario_id}")
    add(g, "diario/aula_frequencia/lista/?diario=",
        f"/api/v1/diario/aula_frequencia/lista/?diario={diario_id}")
    add(g, "historico_notas/?aluno= (ref: faltas)",
        f"/api/v1/historico_notas/?aluno={aluno_id}")
    add(g, "fase_nota_aluno_avaliacao/?periodo=80 (ref: notas atuais)",
        f"/api/v1/fase_nota_aluno_avaliacao/?periodo={periodo}")
    add(g, "diario/diario_aula/?diario=&limit=5 (ref: campo frequencia)",
        f"/api/v1/diario/diario_aula/?diario={diario_id}&limit=5&situacao_aula=TODAS")
    # Variantes com underscore/hifen
    add(g, "diario-aula-aluno/?diario=",
        f"/api/v1/diario-aula-aluno/?diario={diario_id}")
    add(g, "frequencia-aluno/?diario=",
        f"/api/v1/frequencia-aluno/?diario={diario_id}")
    add(g, "chamada-online/?diario=",
        f"/api/v1/chamada-online/?diario={diario_id}")

    return endpoints


# =============================================================================
# TESTADOR DE ENDPOINTS
# =============================================================================

def classificar_resposta(resp_text, status_code, content_type):
    """
    Classifica a resposta:
    - 'JSON_FREQUENCIA': JSON com dados de frequencia individual
    - 'JSON_DADOS': JSON com dados (mas nao de frequencia)
    - 'JSON_VAZIO': JSON valido mas sem resultados
    - 'JSON_ERRO': JSON com mensagem de erro
    - 'HTML_SPA': Retornou HTML (provavelmente SPA React)
    - 'HTML_DOCS': HTML que pode ser documentacao
    - 'REDIRECT': Redirecionamento
    - 'NOT_FOUND': 404
    - 'FORBIDDEN': 403
    - 'ERROR': Outro erro
    """
    if status_code == 404:
        return 'NOT_FOUND'
    if status_code == 403:
        return 'FORBIDDEN'
    if status_code in (301, 302):
        return 'REDIRECT'
    if status_code >= 500:
        return 'SERVER_ERROR'

    ct = (content_type or '').lower()

    if 'json' in ct:
        try:
            data = json.loads(resp_text)
        except (json.JSONDecodeError, ValueError):
            return 'JSON_ERRO'

        # Verificar se tem dados
        if isinstance(data, dict):
            if 'detail' in data or 'error' in data:
                return 'JSON_ERRO'
            results = data.get('results', [])
            count = data.get('count', 0)
            if count == 0 and not results:
                # Pode ter outros campos
                if len(data) <= 3:  # count + results + next/previous
                    return 'JSON_VAZIO'

        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and 'results' in data:
            items = data['results']

        # Verificar keywords de frequencia
        text_lower = resp_text.lower()
        has_freq = any(kw.lower() in text_lower for kw in FREQUENCIA_KEYWORDS[:10])
        has_aluno = 'aluno' in text_lower or 'idaluno' in text_lower or 'nome_aluno' in text_lower

        if has_freq and has_aluno and items:
            return 'JSON_FREQUENCIA'
        elif items:
            return 'JSON_DADOS'
        elif isinstance(data, dict) and len(data) > 3:
            if has_freq and has_aluno:
                return 'JSON_FREQUENCIA'
            return 'JSON_DADOS'
        else:
            return 'JSON_VAZIO'

    if 'html' in ct:
        text_lower = resp_text.lower()
        if 'swagger' in text_lower or 'openapi' in text_lower or 'api documentation' in text_lower:
            return 'HTML_DOCS'
        if '<script' in text_lower and ('react' in text_lower or 'bundle' in text_lower or 'chunk' in text_lower):
            return 'HTML_SPA'
        if 'django rest framework' in text_lower:
            return 'HTML_DOCS'
        return 'HTML_SPA'

    if 'openapi' in ct or 'yaml' in ct:
        return 'JSON_DADOS'

    return 'ERROR'


def testar_endpoint(session, endpoint):
    """
    Testa um unico endpoint e retorna resultado detalhado.
    """
    url = endpoint['url']
    nome = endpoint['nome']
    grupo = endpoint['grupo']
    headers_extra = endpoint.get('headers_extra', {})

    resultado = {
        'grupo': grupo,
        'nome': nome,
        'url_completa': '',
        'status_http': None,
        'content_type': '',
        'tamanho_bytes': 0,
        'classificacao': '',
        'preview': '',
        'tem_frequencia': False,
        'erro': None,
        'tempo_ms': 0,
    }

    # Construir URL completa
    if url.startswith('http'):
        full_url = url
    else:
        full_url = f"{API_BASE}{url}"
    resultado['url_completa'] = full_url

    try:
        start = time.time()

        # Merge headers
        extra_headers = {}
        extra_headers.update(headers_extra)

        resp = session.get(full_url, timeout=TIMEOUT, headers=extra_headers,
                          allow_redirects=False)
        elapsed = (time.time() - start) * 1000

        resultado['status_http'] = resp.status_code
        resultado['content_type'] = resp.headers.get('Content-Type', '')
        resultado['tamanho_bytes'] = len(resp.content)
        resultado['tempo_ms'] = round(elapsed, 1)

        # Classificar
        classificacao = classificar_resposta(
            resp.text, resp.status_code, resultado['content_type']
        )
        resultado['classificacao'] = classificacao

        # Preview
        if 'json' in resultado['content_type'].lower():
            resultado['preview'] = resp.text[:500]
        elif classificacao == 'HTML_SPA':
            resultado['preview'] = 'SPA HTML (React/jQuery)'
        elif classificacao == 'HTML_DOCS':
            resultado['preview'] = resp.text[:500]
        else:
            resultado['preview'] = resp.text[:200]

        # Flag de frequencia
        if classificacao == 'JSON_FREQUENCIA':
            resultado['tem_frequencia'] = True

    except requests.Timeout:
        resultado['erro'] = 'TIMEOUT (>10s)'
        resultado['classificacao'] = 'TIMEOUT'
    except requests.ConnectionError as e:
        resultado['erro'] = f'CONNECTION_ERROR: {str(e)[:100]}'
        resultado['classificacao'] = 'CONNECTION_ERROR'
    except Exception as e:
        resultado['erro'] = f'{type(e).__name__}: {str(e)[:100]}'
        resultado['classificacao'] = 'ERROR'

    return resultado


# =============================================================================
# EXECUCAO PRINCIPAL
# =============================================================================

def executar_testes(session, endpoints):
    """Executa todos os testes e retorna lista de resultados."""
    total = len(endpoints)
    resultados = []

    print(f"\n{'='*70}")
    print(f"  INICIANDO TESTES: {total} endpoints")
    print(f"{'='*70}\n")

    grupo_atual = None
    grupo_count = 0
    grupo_start = 0

    for i, ep in enumerate(endpoints):
        # Header de grupo
        if ep['grupo'] != grupo_atual:
            if grupo_atual:
                print(f"  --- Grupo {grupo_atual}: {grupo_count} testados ---\n")
            grupo_atual = ep['grupo']
            grupo_count = 0
            grupo_num = ep['grupo'].split('_')[0]
            grupo_nome = ep['grupo'].split('_', 1)[1] if '_' in ep['grupo'] else ep['grupo']
            print(f"  GRUPO {grupo_num}: {grupo_nome.upper()}")

        grupo_count += 1

        # Testar
        resultado = testar_endpoint(session, ep)
        resultados.append(resultado)

        # Status icon
        cls = resultado['classificacao']
        if cls == 'JSON_FREQUENCIA':
            icon = ">>> FREQUENCIA ENCONTRADA <<<"
        elif cls == 'JSON_DADOS':
            icon = "[JSON+DADOS]"
        elif cls == 'JSON_VAZIO':
            icon = "[JSON vazio]"
        elif cls == 'JSON_ERRO':
            icon = "[JSON erro]"
        elif cls == 'HTML_SPA':
            icon = "[HTML SPA]"
        elif cls == 'HTML_DOCS':
            icon = "[HTML docs]"
        elif cls == 'NOT_FOUND':
            icon = "[404]"
        elif cls == 'FORBIDDEN':
            icon = "[403]"
        elif cls == 'TIMEOUT':
            icon = "[TIMEOUT]"
        else:
            icon = f"[{cls}]"

        status = resultado.get('status_http', '???')
        size = resultado.get('tamanho_bytes', 0)
        ms = resultado.get('tempo_ms', 0)

        print(f"    [{i+1:3d}/{total}] {status or '???':>3} {size:>7}B {ms:>6.0f}ms "
              f"{icon:20s} {ep['nome'][:50]}")

        # Se encontrou frequencia, destaque extra
        if resultado['tem_frequencia']:
            print(f"\n    {'*'*60}")
            print(f"    *** ENDPOINT COM DADOS DE FREQUENCIA ENCONTRADO! ***")
            print(f"    *** URL: {resultado['url_completa']}")
            print(f"    *** Preview: {resultado['preview'][:200]}")
            print(f"    {'*'*60}\n")

        # Throttle leve para nao sobrecarregar
        time.sleep(0.15)

    if grupo_atual:
        print(f"  --- Grupo {grupo_atual}: {grupo_count} testados ---\n")

    return resultados


# =============================================================================
# ANALISE E RELATORIO
# =============================================================================

def analisar_resultados(resultados):
    """Analisa resultados e gera relatorio estruturado."""

    # Contagens gerais
    total = len(resultados)
    por_classificacao = {}
    por_grupo = {}
    encontrados_frequencia = []
    encontrados_json = []
    encontrados_docs = []

    for r in resultados:
        cls = r['classificacao']
        grp = r['grupo']

        por_classificacao[cls] = por_classificacao.get(cls, 0) + 1

        if grp not in por_grupo:
            por_grupo[grp] = {'total': 0, 'json': 0, 'freq': 0, 'spa': 0, 'err': 0}
        por_grupo[grp]['total'] += 1

        if cls == 'JSON_FREQUENCIA':
            por_grupo[grp]['freq'] += 1
            encontrados_frequencia.append(r)
        elif cls in ('JSON_DADOS', 'JSON_VAZIO'):
            por_grupo[grp]['json'] += 1
            if cls == 'JSON_DADOS':
                encontrados_json.append(r)
        elif cls == 'HTML_SPA':
            por_grupo[grp]['spa'] += 1
        elif cls == 'HTML_DOCS':
            encontrados_docs.append(r)
        else:
            por_grupo[grp]['err'] += 1

    # Scoring por grupo (0-10)
    scores = {}
    for grp, stats in por_grupo.items():
        if stats['freq'] > 0:
            scores[grp] = 10
        elif stats['json'] > 0:
            scores[grp] = min(8, 3 + stats['json'] * 2)
        elif stats['spa'] > 0:
            scores[grp] = 2  # SPA significa que a rota existe, mas nao retorna JSON
        else:
            scores[grp] = 0

    # Recomendacao
    if encontrados_frequencia:
        recomendacao = (
            "SUCESSO! Endpoints com dados de frequencia individual encontrados. "
            "Criar script de extracao imediatamente."
        )
    elif encontrados_json:
        recomendacao = (
            "Endpoints JSON encontrados mas sem dados de frequencia individual. "
            "Investigar os endpoints JSON para ver se contem dados derivaveis. "
            "Verificar se campos de frequencia estao em endpoints de aula/diario."
        )
    elif encontrados_docs:
        recomendacao = (
            "Documentacao/Swagger encontrada! Analisar para descobrir endpoints corretos."
        )
    else:
        recomendacao = (
            "Nenhum endpoint de frequencia individual encontrado via API REST. "
            "Opcoes: (1) Interceptar chamadas XHR do SPA React quando carrega a tela de chamada, "
            "(2) Usar Playwright para navegar ate a tela de frequencia e extrair via DOM, "
            "(3) Calcular frequencia indiretamente via historico_notas (quantidade_faltas_anual)."
        )

    relatorio = {
        'metadata': {
            'data_execucao': datetime.now().isoformat(),
            'agente': 'THETA',
            'arena': 4,
            'versao': '1.0',
        },
        'resumo': {
            'total_endpoints_testados': total,
            'total_json_com_dados': len(encontrados_json),
            'total_json_frequencia': len(encontrados_frequencia),
            'total_html_spa': por_classificacao.get('HTML_SPA', 0),
            'total_html_docs': len(encontrados_docs),
            'total_404': por_classificacao.get('NOT_FOUND', 0),
            'total_403': por_classificacao.get('FORBIDDEN', 0),
            'total_erros': por_classificacao.get('ERROR', 0) + por_classificacao.get('TIMEOUT', 0),
        },
        'contagem_por_classificacao': por_classificacao,
        'scores_por_grupo': scores,
        'estatisticas_por_grupo': por_grupo,
        'recomendacao': recomendacao,
        'endpoints_frequencia': [
            {
                'url': r['url_completa'],
                'nome': r['nome'],
                'status': r['status_http'],
                'preview': r['preview'][:300],
            }
            for r in encontrados_frequencia
        ],
        'endpoints_json_dados': [
            {
                'url': r['url_completa'],
                'nome': r['nome'],
                'grupo': r['grupo'],
                'status': r['status_http'],
                'tamanho': r['tamanho_bytes'],
                'preview': r['preview'][:300],
            }
            for r in encontrados_json
        ],
        'endpoints_docs': [
            {
                'url': r['url_completa'],
                'nome': r['nome'],
                'status': r['status_http'],
                'preview': r['preview'][:300],
            }
            for r in encontrados_docs
        ],
        'todos_resultados': resultados,
    }

    return relatorio


def imprimir_relatorio(relatorio):
    """Imprime relatorio formatado no terminal."""
    print("\n" + "=" * 70)
    print("  RELATORIO FINAL - AGENTE THETA - CACADOR DE ENDPOINTS")
    print("=" * 70)

    r = relatorio['resumo']
    print(f"\n  Total de endpoints testados:    {r['total_endpoints_testados']}")
    print(f"  Retornaram JSON com dados:      {r['total_json_com_dados']}")
    print(f"  Retornaram dados de FREQUENCIA: {r['total_json_frequencia']}")
    print(f"  Retornaram HTML (SPA):          {r['total_html_spa']}")
    print(f"  Retornaram documentacao:        {r['total_html_docs']}")
    print(f"  404 Not Found:                  {r['total_404']}")
    print(f"  403 Forbidden:                  {r['total_403']}")
    print(f"  Erros/Timeouts:                 {r['total_erros']}")

    print(f"\n  --- SCORES POR GRUPO (0-10) ---")
    for grp, score in sorted(relatorio['scores_por_grupo'].items()):
        bar = '#' * score + '.' * (10 - score)
        stats = relatorio['estatisticas_por_grupo'][grp]
        print(f"  [{bar}] {score:2d}/10  {grp} "
              f"(json:{stats['json']}, freq:{stats['freq']}, spa:{stats['spa']})")

    if relatorio['endpoints_frequencia']:
        print(f"\n  {'*'*60}")
        print(f"  *** ENDPOINTS COM DADOS DE FREQUENCIA ***")
        print(f"  {'*'*60}")
        for ep in relatorio['endpoints_frequencia']:
            print(f"    URL: {ep['url']}")
            print(f"    Status: {ep['status']}")
            print(f"    Preview: {ep['preview'][:200]}")
            print()

    if relatorio['endpoints_json_dados']:
        print(f"\n  --- ENDPOINTS JSON COM DADOS (sem frequencia individual) ---")
        for ep in relatorio['endpoints_json_dados']:
            print(f"    [{ep['grupo']}] {ep['nome']}")
            print(f"      URL: {ep['url']}")
            print(f"      Tamanho: {ep['tamanho']}B")
            print(f"      Preview: {ep['preview'][:150]}")
            print()

    if relatorio['endpoints_docs']:
        print(f"\n  --- DOCUMENTACAO ENCONTRADA ---")
        for ep in relatorio['endpoints_docs']:
            print(f"    URL: {ep['url']}")
            print()

    print(f"\n  RECOMENDACAO:")
    print(f"  {relatorio['recomendacao']}")

    print("\n" + "=" * 70)


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("  AGENTE THETA - CACADOR DE ENDPOINTS DE FREQUENCIA")
    print(f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  API Base: {API_BASE}")
    print("=" * 70)

    # Verificar modo
    senha = CONFIG.get('senha', '')
    dry_run = not senha

    if dry_run:
        print("\n[MODO DRY-RUN] SIGA_SENHA nao definida.")
        print("  Gerando lista de endpoints sem executar requests.")
        print("  Para executar testes reais: export SIGA_SENHA='sua_senha'")

        # Gerar endpoints com IDs placeholder
        ids = {
            'diario_id': 99999,
            'aula_id': 99999,
            'aluno_id': 99999,
            'turma_id': 99999,
            'periodo': 80,
        }
        endpoints = gerar_endpoints(ids)

        # Salvar lista de endpoints
        output = {
            'metadata': {
                'modo': 'dry_run',
                'data': datetime.now().isoformat(),
                'agente': 'THETA',
            },
            'total_endpoints': len(endpoints),
            'endpoints': [
                {
                    'grupo': ep['grupo'],
                    'nome': ep['nome'],
                    'url': ep['url'] if ep['url'].startswith('http') else f"{API_BASE}{ep['url']}",
                }
                for ep in endpoints
            ],
        }

        out_path = SCRIPT_DIR / "frequencia_endpoints_descobertos.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n  Lista de {len(endpoints)} endpoints salva em:")
        print(f"  {out_path}")

        # Imprimir grupos
        grupos = {}
        for ep in endpoints:
            g = ep['grupo']
            grupos[g] = grupos.get(g, 0) + 1
        print(f"\n  Distribuicao por grupo:")
        for g, n in sorted(grupos.items()):
            print(f"    {g}: {n} endpoints")

        return

    # ==========================================================
    # MODO REAL: Login + Testes
    # ==========================================================

    # 1. Login
    try:
        cookies = fazer_login_playwright()
    except Exception as e:
        print(f"\n[ERRO] Falha no login: {e}")
        print("  Verifique SIGA_SENHA e tente novamente.")
        sys.exit(1)

    session = criar_session(cookies)

    # 2. Obter IDs reais
    ids = obter_ids_reais(session)

    if not ids['diario_id']:
        print("\n[ERRO] Nao foi possivel obter nenhum diario. Abortando.")
        sys.exit(1)

    # 3. Gerar endpoints
    endpoints = gerar_endpoints(ids)
    print(f"\n  Total de endpoints a testar: {len(endpoints)}")

    # 4. Executar testes
    resultados = executar_testes(session, endpoints)

    # 5. Analisar
    relatorio = analisar_resultados(resultados)

    # 6. Salvar JSON
    out_path = SCRIPT_DIR / "frequencia_endpoints_descobertos.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n  Resultados salvos em: {out_path}")

    # 7. Imprimir relatorio
    imprimir_relatorio(relatorio)

    # 8. Se encontrou frequencia, criar script de extracao
    if relatorio['endpoints_frequencia']:
        print("\n" + "*" * 70)
        print("  FREQUENCIA ENCONTRADA! Criando script de extracao...")
        print("*" * 70)
        criar_script_extracao(relatorio['endpoints_frequencia'])

    return relatorio


def criar_script_extracao(endpoints_freq):
    """
    Se encontrou endpoints de frequencia, cria automaticamente
    o script extrair_frequencia_siga.py.
    """
    # Pegar o melhor endpoint (primeiro)
    melhor = endpoints_freq[0]
    url_template = melhor['url']

    script_content = f'''#!/usr/bin/env python3
"""
EXTRACAO DE FREQUENCIA INDIVIDUAL - SIGA ACTIVESOFT
====================================================
Gerado automaticamente pelo Agente THETA em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}.

Endpoint descoberto: {url_template}

Extrai frequencia individual de alunos de todas as 4 unidades.
"""

import json
import csv
import os
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "power_bi"
API_BASE = "https://siga02.activesoft.com.br"
SIGA_LOGIN = "https://siga.activesoft.com.br"

CONFIG = {{
    "instituicao": os.environ.get("SIGA_INSTITUICAO", "COLEGIOELO"),
    "login": os.environ.get("SIGA_LOGIN", "bruna"),
    "senha": os.environ.get("SIGA_SENHA", ""),
    "unidades": [
        {{"nome": "Boa Viagem", "codigo": "BV", "periodo": 80, "seletor": "1 - BV (Boa Viagem)"}},
        {{"nome": "Candeias", "codigo": "CD", "periodo": 78, "seletor": "2 - CD (Jaboatao)"}},
        {{"nome": "Janga", "codigo": "JG", "periodo": 79, "seletor": "3 - JG (Paulista)"}},
        {{"nome": "Cordeiro", "codigo": "CDR", "periodo": 77, "seletor": "4 - CDR (Cordeiro)"}},
    ],
}}

ENDPOINT_TEMPLATE = "{url_template}"


def fazer_login():
    """Faz login via Playwright e retorna cookies."""
    print("  Fazendo login no SIGA...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(f"{{SIGA_LOGIN}}/login/")
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
    return {{c['name']: c['value'] for c in cookies}}


def criar_session(cookies):
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({{
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0',
    }})
    return session


def main():
    if not CONFIG["senha"]:
        print("ERRO: SIGA_SENHA nao definida")
        sys.exit(1)

    print("EXTRACAO DE FREQUENCIA - SIGA")
    cookies = fazer_login()
    session = criar_session(cookies)

    todas_freq = []

    for unidade in CONFIG['unidades']:
        periodo = unidade['periodo']
        codigo = unidade['codigo']
        print(f"\\n  [{{codigo}}] Extraindo frequencia...")

        # Buscar diarios
        url = f"{{API_BASE}}/api/v1/diario/diario/lista/?limit=1000&offset=0&periodo={{periodo}}"
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"    ERRO: HTTP {{resp.status_code}}")
            continue

        diarios = resp.json().get('results', [])

        for diario in diarios:
            diario_id = diario.get('id')
            if not diario_id:
                continue

            # TODO: Adaptar URL para o endpoint descoberto
            # Endpoint: ENDPOINT_TEMPLATE (substituir IDs)
            try:
                freq_url = f"{{API_BASE}}/api/v1/..."  # ADAPTAR
                freq_resp = session.get(freq_url, timeout=10)
                if freq_resp.status_code == 200:
                    data = freq_resp.json()
                    # TODO: Processar dados conforme estrutura encontrada
                    print(f"    Diario {{diario_id}}: dados obtidos")
            except Exception as e:
                print(f"    ERRO diario {{diario_id}}: {{e}}")

            time.sleep(0.1)

    if todas_freq:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        csv_path = OUTPUT_DIR / 'fato_Frequencia_Aluno.csv'
        fieldnames = list(todas_freq[0].keys())
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(todas_freq)
        print(f"\\n  fato_Frequencia_Aluno.csv: {{len(todas_freq)}} registros")
    else:
        print("\\n  Nenhum dado de frequencia extraido.")

    print("CONCLUIDO")


if __name__ == "__main__":
    main()
'''

    out_path = SCRIPT_DIR / "extrair_frequencia_siga.py"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    print(f"  Script salvo em: {out_path}")


if __name__ == "__main__":
    main()
