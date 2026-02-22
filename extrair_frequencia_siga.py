#!/usr/bin/env python3
"""
EXTRACAO DE FREQUENCIA INDIVIDUAL DE ALUNOS - SIGA ACTIVESOFT
==============================================================
Agente THETA - Arena 4 - 2026-02-20

Este script extrai dados de frequencia/presenca individual de alunos
do SIGA ActiveSoft para todas as 4 unidades do Colegio ELO.

IMPORTANTE: Este script deve ser atualizado com o endpoint correto
apos a execucao de descobrir_frequencia.py. O endpoint sera preenchido
automaticamente se descobrir_frequencia.py encontrar dados.

Estrategia de fallback (3 niveis):
  1. Endpoint direto de frequencia (se descoberto)
  2. diario_aula_aluno (se retornar presenca por aula)
  3. historico_notas (quantidade_faltas_anual - 10% cobertura)

Saida: power_bi/fato_Frequencia_Aluno.csv

USO:
  export SIGA_SENHA='sua_senha'
  python3 extrair_frequencia_siga.py
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

CONFIG = {
    "instituicao": os.environ.get("SIGA_INSTITUICAO", "COLEGIOELO"),
    "login": os.environ.get("SIGA_LOGIN", "bruna"),
    "senha": os.environ.get("SIGA_SENHA", ""),
    "unidades": [
        {"nome": "Boa Viagem", "codigo": "BV", "periodo": 80, "seletor": "1 - BV (Boa Viagem)"},
        {"nome": "Candeias", "codigo": "CD", "periodo": 78, "seletor": "2 - CD (Jaboatao)"},
        {"nome": "Janga", "codigo": "JG", "periodo": 79, "seletor": "3 - JG (Paulista)"},
        {"nome": "Cordeiro", "codigo": "CDR", "periodo": 77, "seletor": "4 - CDR (Cordeiro)"},
    ],
}

# ---------------------------------------------------------------------------
# Normalizacao (reutiliza do projeto)
# ---------------------------------------------------------------------------
try:
    from normalizacao import normalizar_serie, normalizar_disciplina
except ImportError:
    # Fallback se normalizacao.py nao estiver disponivel
    SERIE_MAP = {
        '6o ANO': '6o Ano', '7o ANO': '7o Ano', '8o ANO': '8o Ano', '9o ANO': '9o Ano',
        '1o Ano Medio': '1a Serie', '2o Ano Medio': '2a Serie', '3o Ano Medio': '3a Serie',
    }
    def normalizar_serie(s):
        return SERIE_MAP.get(s, s) if s else None
    def normalizar_disciplina(d):
        return d

# ---------------------------------------------------------------------------
# Endpoint de frequencia descoberto
# ---------------------------------------------------------------------------
# PREENCHER APOS RODAR descobrir_frequencia.py
# Se vazio, usa fallback (historico_notas)
ENDPOINT_FREQUENCIA = ""  # Ex: "/api/v1/diario/{diario_id}/chamada/lista/"

# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def fazer_login():
    """Faz login via Playwright e retorna cookies."""
    print("  Fazendo login no SIGA...")
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
        page.click('text="1 - BV (Boa Viagem)"', timeout=5000)
        page.wait_for_timeout(3000)
        cookies = context.cookies()
        browser.close()
    cookie_dict = {c['name']: c['value'] for c in cookies}
    print(f"  Login OK! {len(cookie_dict)} cookies")
    return cookie_dict


def criar_session(cookies):
    """Cria requests.Session com cookies e headers."""
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0',
    })
    return session


def fetch_json(session, path, timeout=15):
    """Fetch JSON. Retorna parsed JSON ou dict com 'error'."""
    url = f"{API_BASE}{path}" if path.startswith('/') else path
    try:
        resp = session.get(url, timeout=timeout)
        if resp.status_code == 200:
            ct = resp.headers.get('content-type', '')
            if 'json' in ct:
                return resp.json()
            return {'error': f'not json (content-type: {ct})', 'size': len(resp.text)}
        return {'error': f'HTTP {resp.status_code}'}
    except Exception as e:
        return {'error': str(e)}


def fetch_all_pages(session, path, limit=500):
    """Fetch todas as paginas paginadas."""
    all_results = []
    offset = 0
    sep = '&' if '?' in path else '?'
    while True:
        url = f"{path}{sep}limit={limit}&offset={offset}"
        data = fetch_json(session, url)
        if isinstance(data, dict) and 'error' in data:
            break
        if isinstance(data, list):
            all_results.extend(data)
            break
        if isinstance(data, dict):
            results = data.get('results', [])
            all_results.extend(results)
            total = data.get('count', 0)
            if not results or len(all_results) >= total:
                break
            offset += limit
    return all_results


# ---------------------------------------------------------------------------
# Estrategia 1: Endpoint direto de frequencia
# ---------------------------------------------------------------------------

def extrair_via_endpoint_direto(session):
    """Tenta usar o endpoint descoberto para extrair frequencia."""
    if not ENDPOINT_FREQUENCIA:
        return None

    print("\n[ESTRATEGIA 1] Endpoint direto de frequencia...")
    print(f"  Template: {ENDPOINT_FREQUENCIA}")

    todas_freq = []

    for unidade in CONFIG['unidades']:
        periodo = unidade['periodo']
        codigo = unidade['codigo']
        print(f"\n  [{codigo}] Extraindo...")

        # Buscar diarios
        diarios = fetch_all_pages(session, f"/api/v1/diario/diario/lista/?periodo={periodo}")
        diarios_validos = [
            d for d in diarios
            if d.get('qtd_aula_registradas', 0) > 0
            and ('Fundamental II' in (d.get('nome_curso', '') or '') or
                 'Medio' in (d.get('nome_curso', '') or ''))
        ]
        print(f"    Diarios com aulas: {len(diarios_validos)}")

        for d in diarios_validos:
            diario_id = d['id']
            try:
                # Substituir placeholder no template
                ep = ENDPOINT_FREQUENCIA.replace('{diario_id}', str(diario_id))
                data = fetch_json(session, ep)

                if isinstance(data, dict) and 'error' not in data:
                    results = data.get('results', [data]) if isinstance(data, dict) else data
                    if isinstance(data, list):
                        results = data
                    for r in results:
                        r['unidade'] = codigo
                        r['diario_id'] = diario_id
                        r['serie'] = normalizar_serie(d.get('nome_serie', ''))
                        r['disciplina'] = normalizar_disciplina(d.get('disciplina_nome', ''))
                        r['turma'] = d.get('nome_turma', '')
                        todas_freq.append(r)
                elif isinstance(data, list):
                    for r in data:
                        if isinstance(r, dict):
                            r['unidade'] = codigo
                            r['diario_id'] = diario_id
                            r['serie'] = normalizar_serie(d.get('nome_serie', ''))
                            r['disciplina'] = normalizar_disciplina(d.get('disciplina_nome', ''))
                            r['turma'] = d.get('nome_turma', '')
                            todas_freq.append(r)
            except Exception as e:
                print(f"    ERRO diario {diario_id}: {e}")

            time.sleep(0.1)

        print(f"    Acumulado: {len(todas_freq)} registros")

    return todas_freq if todas_freq else None


# ---------------------------------------------------------------------------
# Estrategia 2: diario_aula_aluno (presenca por aula)
# ---------------------------------------------------------------------------

def extrair_via_diario_aula_aluno(session):
    """
    Tenta extrair presenca via endpoint diario_aula_aluno.
    Testa varias variantes do endpoint.
    """
    print("\n[ESTRATEGIA 2] Tentando diario_aula_aluno...")

    # Testar qual variante funciona
    variantes = [
        "/api/v1/diario/diario_aula_aluno/?diario={diario_id}",
        "/api/v1/diario_aula_aluno/?diario={diario_id}",
        "/api/v1/diario/diario_aula_aluno/lista/?diario={diario_id}",
    ]

    # Pegar um diario de teste
    test_diarios = fetch_all_pages(session, "/api/v1/diario/diario/lista/?periodo=80")
    test_diario = None
    for d in test_diarios:
        if d.get('qtd_aula_registradas', 0) > 0:
            test_diario = d
            break

    if not test_diario:
        print("  Nenhum diario com aulas para teste")
        return None

    endpoint_funcional = None
    for v in variantes:
        url = v.replace('{diario_id}', str(test_diario['id']))
        data = fetch_json(session, url)
        if isinstance(data, dict) and 'error' not in data:
            results = data.get('results', [])
            if results:
                print(f"  FUNCIONA: {v}")
                print(f"    Exemplo: {json.dumps(results[0], ensure_ascii=False)[:200]}")
                endpoint_funcional = v
                break
        elif isinstance(data, list) and data:
            print(f"  FUNCIONA: {v}")
            print(f"    Exemplo: {json.dumps(data[0], ensure_ascii=False)[:200]}")
            endpoint_funcional = v
            break

    if not endpoint_funcional:
        print("  Nenhuma variante de diario_aula_aluno funciona.")
        return None

    # Extrair para todas as unidades
    todas_freq = []
    for unidade in CONFIG['unidades']:
        periodo = unidade['periodo']
        codigo = unidade['codigo']
        print(f"\n  [{codigo}] Extraindo via {endpoint_funcional}...")

        diarios = fetch_all_pages(session, f"/api/v1/diario/diario/lista/?periodo={periodo}")
        diarios_validos = [
            d for d in diarios
            if d.get('qtd_aula_registradas', 0) > 0
            and ('Fundamental II' in (d.get('nome_curso', '') or '') or
                 'Medio' in (d.get('nome_curso', '') or ''))
        ]

        for d in diarios_validos:
            diario_id = d['id']
            try:
                ep = endpoint_funcional.replace('{diario_id}', str(diario_id))
                results = fetch_all_pages(session, ep)
                for r in results:
                    r['unidade'] = codigo
                    r['diario_id'] = diario_id
                    r['serie'] = normalizar_serie(d.get('nome_serie', ''))
                    r['disciplina'] = normalizar_disciplina(d.get('disciplina_nome', ''))
                    r['turma'] = d.get('nome_turma', '')
                todas_freq.extend(results)
            except Exception as e:
                print(f"    ERRO diario {diario_id}: {e}")
            time.sleep(0.1)

        print(f"    Acumulado: {len(todas_freq)} registros")

    return todas_freq if todas_freq else None


# ---------------------------------------------------------------------------
# Estrategia 3: historico_notas (fallback - faltas anuais agregadas)
# ---------------------------------------------------------------------------

def extrair_via_historico_notas(session):
    """
    Fallback: Extrai quantidade_faltas_anual do historico_notas.
    Cobertura limitada (~10%), mas melhor que nada.
    """
    print("\n[ESTRATEGIA 3] Fallback via historico_notas (faltas anuais agregadas)...")

    # Primeiro, obter todos os alunos
    todos_alunos = {}

    for unidade in CONFIG['unidades']:
        periodo = unidade['periodo']
        codigo = unidade['codigo']
        print(f"\n  [{codigo}] Buscando alunos...")

        diarios = fetch_all_pages(session, f"/api/v1/diario/diario/lista/?periodo={periodo}")
        turmas_vistas = set()

        for d in diarios:
            nome_curso = d.get('nome_curso', '') or ''
            if not ('Fundamental II' in nome_curso or 'Medio' in nome_curso):
                continue
            turma_id = d.get('turma')
            if turma_id in turmas_vistas:
                continue
            turmas_vistas.add(turma_id)

            diario_id = d['id']
            try:
                alunos_resp = fetch_json(
                    session,
                    f"/api/v1/diario/{diario_id}/alunos/lista/?busca=&apenas_ativos=false&ensino_superior=0"
                )
                if isinstance(alunos_resp, list):
                    for al in alunos_resp:
                        aid = al.get('IdAluno')
                        if aid and aid not in todos_alunos:
                            todos_alunos[aid] = {
                                'aluno_id': aid,
                                'aluno_nome': al.get('NomeAluno', ''),
                                'unidade': codigo,
                                'serie': normalizar_serie(d.get('nome_serie', '')),
                                'turma': d.get('nome_turma', ''),
                            }
            except Exception:
                pass
            time.sleep(0.1)

        print(f"    Alunos acumulados: {len(todos_alunos)}")

    # Agora buscar historico_notas para cada aluno
    print(f"\n  Buscando faltas no historico para {len(todos_alunos)} alunos...")
    frequencia_dados = []
    erros = 0
    com_faltas = 0

    for i, (aluno_id, info) in enumerate(todos_alunos.items()):
        if (i + 1) % 100 == 0:
            print(f"    Processando {i+1}/{len(todos_alunos)}... "
                  f"(com faltas: {com_faltas})")

        try:
            notas = fetch_json(session, f"/api/v1/historico_notas/?aluno={aluno_id}")
            if isinstance(notas, list):
                for n in notas:
                    faltas = n.get('quantidade_faltas_anual')
                    ch = n.get('carga_horaria_anual')
                    if faltas is not None and faltas != '' and faltas != 0:
                        com_faltas += 1
                        freq_pct = None
                        if ch and int(ch) > 0:
                            try:
                                freq_pct = round((1 - int(faltas) / int(ch)) * 100, 1)
                            except (ValueError, ZeroDivisionError):
                                pass

                        frequencia_dados.append({
                            'aluno_id': aluno_id,
                            'aluno_nome': info['aluno_nome'],
                            'unidade': info['unidade'],
                            'serie': info['serie'],
                            'turma': info['turma'],
                            'disciplina': n.get('disciplina_nome', ''),
                            'serie_historico': n.get('serie', ''),
                            'ano': n.get('ano_conclusao', ''),
                            'faltas_anual': faltas,
                            'carga_horaria': ch,
                            'frequencia_pct': freq_pct,
                            'resultado': n.get('resultado_final', ''),
                            'fonte': 'historico_notas',
                        })
        except Exception:
            erros += 1

        if (i + 1) % 200 == 0:
            time.sleep(0.3)

    print(f"\n  Resultado: {len(frequencia_dados)} registros com faltas "
          f"({com_faltas} entradas, {erros} erros)")

    return frequencia_dados if frequencia_dados else None


# ---------------------------------------------------------------------------
# Salvar CSV
# ---------------------------------------------------------------------------

def salvar_csv(dados, filename):
    """Salva lista de dicts como CSV."""
    if not dados:
        print(f"  Nenhum dado para salvar em {filename}")
        return None

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename

    # Determinar fieldnames a partir dos dados
    fieldnames = list(dados[0].keys())

    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(dados)

    print(f"  {filename}: {len(dados)} registros salvos em {path}")
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("EXTRACAO DE FREQUENCIA INDIVIDUAL - SIGA")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

    if not CONFIG["senha"]:
        print("\nERRO: SIGA_SENHA nao definida.")
        print("  export SIGA_SENHA='sua_senha'")
        sys.exit(1)

    inicio = datetime.now()

    # Login
    print("\n--- LOGIN ---")
    try:
        cookies = fazer_login()
    except Exception as e:
        print(f"ERRO no login: {e}")
        sys.exit(1)

    session = criar_session(cookies)

    # Testar sessao
    test = fetch_json(session, "/api/v1/diario/diario/lista/?periodo=80&limit=1")
    if isinstance(test, dict) and 'error' in test:
        print(f"ERRO sessao: {test['error']}")
        sys.exit(1)
    print("  Sessao OK!")

    # Tentar estrategias em ordem
    dados = None

    # Estrategia 1: Endpoint direto
    if ENDPOINT_FREQUENCIA:
        dados = extrair_via_endpoint_direto(session)
        if dados:
            print(f"\n  ESTRATEGIA 1 SUCESSO: {len(dados)} registros")

    # Estrategia 2: diario_aula_aluno
    if not dados:
        dados = extrair_via_diario_aula_aluno(session)
        if dados:
            print(f"\n  ESTRATEGIA 2 SUCESSO: {len(dados)} registros")

    # Estrategia 3: historico_notas (fallback)
    if not dados:
        dados = extrair_via_historico_notas(session)
        if dados:
            print(f"\n  ESTRATEGIA 3 (FALLBACK): {len(dados)} registros")

    # Salvar
    if dados:
        salvar_csv(dados, 'fato_Frequencia_Aluno.csv')

        # Backup JSON
        backup_path = SCRIPT_DIR / f"backup_frequencia_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total': len(dados),
                'dados': dados[:100],  # Amostra
            }, f, indent=2, ensure_ascii=False, default=str)
        print(f"  Backup: {backup_path.name}")
    else:
        print("\n  NENHUMA ESTRATEGIA retornou dados de frequencia.")
        print("  Alternativas:")
        print("    1. Executar descobrir_frequencia.py para encontrar endpoints")
        print("    2. Usar Playwright para scraping da tela de chamada")
        print("    3. Solicitar API de frequencia ao suporte ActiveSoft")

    # Resumo
    duracao = (datetime.now() - inicio).total_seconds()
    print(f"\n{'='*60}")
    print("RESUMO")
    print(f"  Total registros: {len(dados) if dados else 0}")
    print(f"  Tempo: {duracao:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
