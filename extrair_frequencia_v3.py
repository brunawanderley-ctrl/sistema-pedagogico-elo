#!/usr/bin/env python3
"""
EXTRACAO DE FREQUENCIA DO SIGA v3 - Colegio ELO 2026
=====================================================
Agente IOTA - Arena 4 - 2026-02-20

Endpoint DESCOBERTO pelo interceptador Playwright v3:
  /api/v1/diario/diario_frequencia/montar/?diario={id}

Retorna JSON com frequencia por aluno por aula:
  P = Presente, F = Falta, FJ = Falta Justificada, null = nao registrado

Fluxo:
1. Login via Playwright (headless) - captura cookies (igual atualizar_siga.py)
2. Extrai diarios via requests (4 unidades)
3. Para cada diario, busca frequencia via diario_frequencia/montar
4. Salva em power_bi/fato_Frequencia_Aluno.csv

USO:
  export SIGA_SENHA='sua_senha'
  python3 extrair_frequencia_v3.py
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
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "power_bi"
API_BASE = "https://siga02.activesoft.com.br"

CONFIG = {
    "instituicao": os.environ.get("SIGA_INSTITUICAO", "COLEGIOELO"),
    "login": os.environ.get("SIGA_LOGIN", "bruna"),
    "senha": os.environ.get("SIGA_SENHA", ""),
}

UNIDADES = [
    {"nome": "Boa Viagem", "codigo": "BV", "periodo": 80, "selector": "1 - BV (Boa Viagem)"},
    {"nome": "Candeias", "codigo": "CD", "periodo": 78, "selector": "2 - CD (Jaboatão)"},
    {"nome": "Janga", "codigo": "JG", "periodo": 79, "selector": "3 - JG (Paulista)"},
    {"nome": "Cordeiro", "codigo": "CDR", "periodo": 77, "selector": "4 - CDR (Cordeiro)"},
]

# Normalizacao
try:
    from normalizacao import normalizar_serie, normalizar_disciplina
except ImportError:
    SERIE_MAP = {
        '6º ANO': '6o Ano', '6º Ano': '6o Ano',
        '7º ANO': '7o Ano', '7º Ano': '7o Ano',
        '8º ANO': '8o Ano', '8º Ano': '8o Ano',
        '9º ANO': '9o Ano', '9º Ano': '9o Ano',
        '1ª Série EM': '1a Serie', '1ª Série': '1a Serie',
        '2ª Série EM': '2a Serie', '2ª Série': '2a Serie',
        '3ª Série EM': '3a Serie', '3ª Série': '3a Serie',
    }
    def normalizar_serie(s):
        return SERIE_MAP.get(s, s) if s else ''
    def normalizar_disciplina(d):
        return d.strip() if d else ''

CSV_FIELDNAMES = [
    'aluno_id', 'aluno_nome', 'diario_id', 'unidade', 'curso', 'serie',
    'turma', 'disciplina', 'professor', 'fase_nota',
    'aula_id', 'numero_aula', 'data_aula',
    'presenca',  # P=presente, F=falta, FJ=falta justificada, ''=nao registrado
    'frequencia_id',  # ID do registro (vazio se nao registrado)
    'ordem_chamada',
    'data_entrada', 'data_saida',
]


def fazer_login_e_capturar_cookies(unidade_selector="1 - BV (Boa Viagem)"):
    """Faz login com Playwright (headless) e retorna os cookies.
    Mesma abordagem do atualizar_siga.py."""
    print(f"  Login via Playwright (unidade: {unidade_selector})...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://siga.activesoft.com.br/login/", timeout=30000)
        page.wait_for_timeout(2000)

        page.fill('#codigoInstituicao', CONFIG["instituicao"])
        page.fill('#id_login', CONFIG["login"])
        page.fill('#id_senha', CONFIG["senha"])
        page.click('button:has-text("ENTRAR")')
        page.wait_for_timeout(4000)

        page.click(f'text="{unidade_selector}"', timeout=10000)
        page.wait_for_timeout(3000)

        cookies = context.cookies()
        browser.close()

    cookie_dict = {c['name']: c['value'] for c in cookies}
    print(f"  Login OK! {len(cookie_dict)} cookies")
    return cookie_dict


def criar_session(cookies):
    """Cria uma session requests com os cookies do Playwright."""
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value)
    session.headers.update({
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://siga02.activesoft.com.br/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    })
    return session


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, max=15),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
)
def obter_diarios(session, periodo):
    """Obtem lista de diarios via API requests."""
    url = f"{API_BASE}/api/v1/diario/diario/lista/?limit=1000&offset=0&periodo={periodo}"
    resp = session.get(url, timeout=30)
    if resp.status_code != 200:
        print(f"    ERRO diarios: HTTP {resp.status_code}")
        return []
    data = resp.json()
    return data.get('results', [])


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=10),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
)
def obter_frequencia_diario(session, diario_id):
    """Obtem frequencia via endpoint descoberto pelo IOTA."""
    url = f"{API_BASE}/api/v1/diario/diario_frequencia/montar/?diario={diario_id}"
    resp = session.get(url, timeout=15)
    if resp.status_code != 200:
        return {'error': f'HTTP {resp.status_code}'}
    return resp.json()


def main():
    print("=" * 70)
    print("EXTRACAO DE FREQUENCIA v3 (IOTA) - SIGA -> fato_Frequencia_Aluno.csv")
    print(f"Endpoint: /api/v1/diario/diario_frequencia/montar/?diario={{id}}")
    print(f"Inicio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    if not CONFIG["senha"]:
        print("\nERRO: Variavel de ambiente SIGA_SENHA nao definida.")
        print("  export SIGA_SENHA='sua_senha_aqui'")
        sys.exit(1)

    inicio = time.time()
    all_rows = []
    stats = {u['codigo']: {'diarios': 0, 'com_freq': 0, 'registros': 0,
                           'presentes': 0, 'faltas': 0, 'justificadas': 0}
             for u in UNIDADES}

    for unidade in UNIDADES:
        codigo = unidade['codigo']
        periodo = unidade['periodo']
        print(f"\n{'='*50}")
        print(f"  Unidade: {unidade['nome']} ({codigo}) - periodo={periodo}")
        print(f"{'='*50}")

        # Login por unidade (cada unidade tem sessao diferente no SIGA)
        try:
            cookies = fazer_login_e_capturar_cookies(unidade['selector'])
            session = criar_session(cookies)
        except Exception as e:
            print(f"  ERRO login: {e}")
            continue

        # Obter diarios
        diarios = obter_diarios(session, periodo)
        print(f"  Diarios total: {len(diarios)}")

        # Filtrar Fund II e EM com aulas registradas
        diarios_alvo = [
            d for d in diarios
            if (('Fundamental II' in (d.get('nome_curso', '') or '')
                 or 'Médio' in (d.get('nome_curso', '') or ''))
                and d.get('qtd_aula_registradas', 0) > 0)
        ]
        print(f"  Diarios Fund II/EM com aulas: {len(diarios_alvo)}")
        stats[codigo]['diarios'] = len(diarios_alvo)

        erros = 0
        for idx, diario in enumerate(diarios_alvo):
            diario_id = diario.get('id')
            disciplina = diario.get('disciplina_nome', '') or ''
            serie = diario.get('nome_serie', '') or ''
            turma_nome = diario.get('nome_turma', '') or ''
            professor = diario.get('professor_nome', '') or ''
            curso = diario.get('nome_curso', '') or ''
            fase = diario.get('fase_nota_nome', '') or ''
            serie_norm = normalizar_serie(serie)

            if (idx + 1) % 25 == 0 or idx == 0:
                print(f"    [{idx+1}/{len(diarios_alvo)}] {stats[codigo]['registros']} regs...")

            try:
                freq_data = obter_frequencia_diario(session, diario_id)

                if isinstance(freq_data, dict) and 'error' in freq_data:
                    erros += 1
                    if erros <= 3:
                        print(f"    ERRO diario {diario_id}: {freq_data['error']}")
                    continue

                if not isinstance(freq_data, dict):
                    continue

                has_data = False
                for key, aulas in freq_data.items():
                    if not isinstance(aulas, list):
                        continue

                    for aula in aulas:
                        has_data = True
                        presenca = aula.get('st_presenca_falta') or ''
                        freq_id = aula.get('id_frequencia') or ''

                        row = {
                            'aluno_id': aula.get('id_aluno', ''),
                            'aluno_nome': aula.get('nome_aluno', ''),
                            'diario_id': diario_id,
                            'unidade': codigo,
                            'curso': curso,
                            'serie': serie_norm,
                            'turma': turma_nome,
                            'disciplina': normalizar_disciplina(disciplina),
                            'professor': professor,
                            'fase_nota': fase,
                            'aula_id': aula.get('id_diario_aula', ''),
                            'numero_aula': aula.get('numero_aula', ''),
                            'data_aula': (aula.get('data_aula', '') or '')[:10],
                            'presenca': presenca,
                            'frequencia_id': freq_id,
                            'ordem_chamada': aula.get('ordem_chamada', ''),
                            'data_entrada': (aula.get('data_inicial', '') or '')[:10],
                            'data_saida': (aula.get('data_final', '') or '')[:10],
                        }
                        all_rows.append(row)
                        stats[codigo]['registros'] += 1

                        if presenca == 'P':
                            stats[codigo]['presentes'] += 1
                        elif presenca == 'F':
                            stats[codigo]['faltas'] += 1
                        elif presenca in ('FJ', 'J'):
                            stats[codigo]['justificadas'] += 1

                if has_data:
                    stats[codigo]['com_freq'] += 1

                # Throttle para nao sobrecarregar a API
                time.sleep(0.15)

            except Exception as e:
                erros += 1
                if erros <= 5:
                    print(f"    ERRO diario {diario_id}: {str(e)[:80]}")

        print(f"  {codigo}: {stats[codigo]['com_freq']} diarios com dados, "
              f"{stats[codigo]['registros']} registros, {erros} erros")

    # === Salvar ===
    print(f"\n{'='*70}")
    print("SALVANDO")
    print(f"{'='*70}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # CSV
    csv_path = OUTPUT_DIR / 'fato_Frequencia_Aluno.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"  fato_Frequencia_Aluno.csv: {len(all_rows)} registros")

    # Backup JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    json_path = SCRIPT_DIR / f"backup_frequencia_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_registros': len(all_rows),
            'stats': stats,
            'endpoint': '/api/v1/diario/diario_frequencia/montar/?diario={id}',
            'nota': 'Descoberto pelo interceptador Playwright v3 (Agente IOTA)',
        }, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Backup JSON: {json_path.name}")

    duracao = time.time() - inicio

    # === Resumo ===
    print(f"\n{'='*70}")
    print("RESUMO")
    print(f"{'='*70}")

    total_regs = 0
    total_p = 0
    total_f = 0
    total_fj = 0
    for cod, s in stats.items():
        print(f"  {cod}: {s['diarios']} diarios | {s['com_freq']} com freq | "
              f"{s['registros']} regs | P={s['presentes']} F={s['faltas']} FJ={s['justificadas']}")
        total_regs += s['registros']
        total_p += s['presentes']
        total_f += s['faltas']
        total_fj += s['justificadas']

    nao_reg = total_regs - total_p - total_f - total_fj
    print(f"\n  TOTAL: {total_regs} registros")
    if total_regs > 0:
        print(f"    Presentes (P):      {total_p:>8} ({100*total_p/total_regs:.1f}%)")
        print(f"    Faltas (F):         {total_f:>8} ({100*total_f/total_regs:.1f}%)")
        print(f"    Justificadas (FJ):  {total_fj:>8} ({100*total_fj/total_regs:.1f}%)")
        print(f"    Nao registrado:     {nao_reg:>8} ({100*nao_reg/total_regs:.1f}%)")

    alunos_unicos = len(set(r['aluno_id'] for r in all_rows if r['aluno_id']))
    print(f"\n  Alunos distintos: {alunos_unicos}")
    print(f"  Tempo: {duracao:.1f}s")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
