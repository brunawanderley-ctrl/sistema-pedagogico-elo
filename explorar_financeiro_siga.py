#!/usr/bin/env python3
"""
EXPLORAÇÃO DO MÓDULO FINANCEIRO SIGA - Vendas Livro/Produto 995
Colégio ELO - 10/02/2026

Objetivo: Descobrir endpoints financeiros e extrair vendas do produto 995
por unidade (BV, CD, JG), série e turma.

Estratégia:
1. Login via Playwright
2. Interceptar TODAS as requisições de rede ao navegar pelo módulo financeiro
3. Testar endpoints financeiros candidatos
4. Extrair dados do produto 995
"""

import json
import csv
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from playwright.sync_api import sync_playwright

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "power_bi"
SIGA_LOGIN = "https://siga.activesoft.com.br"
SIGA_APP = "https://siga02.activesoft.com.br"

CONFIG = {
    "instituicao": "COLEGIOELO",
    "login": "bruna",
    "senha": os.environ.get("SIGA_SENHA", "Sucesso@25"),
}

UNIDADES = [
    {"nome": "BV", "selector": '1 - BV (Boa Viagem)', "codigo": "BV", "periodo": 80},
    {"nome": "CD", "selector": '2 - CD (Jaboatão)', "codigo": "CD", "periodo": 78},
    {"nome": "JG", "selector": '3 - JG (Paulista)', "codigo": "JG", "periodo": 79},
]

# Endpoints financeiros candidatos para testar
FINANCIAL_ENDPOINTS = [
    # Títulos / Contas a receber
    "/api/v1/titulo/",
    "/api/v1/titulos/",
    "/api/v1/titulo/titulo/",
    "/api/v1/titulo/titulo/lista/",
    "/api/v1/conta_receber/",
    "/api/v1/contas_receber/",
    "/api/v1/financeiro/titulo/",
    "/api/v1/financeiro/titulo/lista/",
    "/api/v1/financeiro/conta_receber/",
    # Recebimentos
    "/api/v1/recebimento/",
    "/api/v1/recebimentos/",
    "/api/v1/financeiro/recebimento/",
    "/api/v1/caixa/",
    "/api/v1/caixa/recebimento/",
    "/api/v1/caixa/caixa/",
    # Boletos
    "/api/v1/boleto/",
    "/api/v1/boletos/",
    "/api/v1/cobranca/",
    "/api/v1/cobranca_ativa/",
    # Vendas / Produtos
    "/api/v1/venda/",
    "/api/v1/vendas/",
    "/api/v1/produto/",
    "/api/v1/produtos/",
    "/api/v1/servico/",
    "/api/v1/servicos/",
    "/api/v1/item_venda/",
    "/api/v1/itens_venda/",
    "/api/v1/loja/",
    "/api/v1/loja_online/",
    "/api/v1/pedido/",
    "/api/v1/pedidos/",
    # Livro (pode ser livro caixa / livro razão)
    "/api/v1/livro/",
    "/api/v1/livro_caixa/",
    "/api/v1/livro_razao/",
    # Fatura / Parcela
    "/api/v1/fatura/",
    "/api/v1/faturas/",
    "/api/v1/parcela/",
    "/api/v1/parcelas/",
    # Material didático
    "/api/v1/material/",
    "/api/v1/material_didatico/",
    "/api/v1/kit_material/",
    # Fields/select financeiros
    "/api/v1/fields/select/produto/",
    "/api/v1/fields/select/servico/",
    "/api/v1/fields/select/titulo/",
    "/api/v1/fields/select/forma_pagamento/",
    "/api/v1/fields/select/conta_financeira/",
    "/api/v1/fields/select/plano_contas/",
    "/api/v1/fields/select/centro_custo/",
    # Contratos
    "/api/v1/contrato/",
    "/api/v1/contratos/",
    "/api/v1/matricula_financeira/",
    # Responsável financeiro
    "/api/v1/responsavel_financeiro/",
    "/api/v1/responsavel/",
    # Portal ASP links
    "/api/v1/portal_financeiro/",
    "/api/v1/financeiro/",
    "/api/v1/nucleo_financeiro/",
]

# Rotas SPA que podem revelar o módulo financeiro
SPA_FINANCIAL_ROUTES = [
    "/financeiro/",
    "/financeiro/titulos/",
    "/financeiro/recebimentos/",
    "/financeiro/caixa/",
    "/financeiro/cobranca/",
    "/financeiro/vendas/",
    "/vendas/",
    "/loja/",
    "/material/",
    "/titulo/",
    "/cobranca/",
    "/faturamento/",
    "/contrato/",
    "/mensalidade/",
]

timestamp = datetime.now().strftime("%Y%m%d_%H%M")


def login_siga(page, unidade_selector):
    """Faz login no SIGA selecionando uma unidade."""
    page.goto(f"{SIGA_LOGIN}/login/")
    page.wait_for_timeout(2000)
    page.fill('#codigoInstituicao', CONFIG["instituicao"])
    page.fill('#id_login', CONFIG["login"])
    page.fill('#id_senha', CONFIG["senha"])
    page.click('button:has-text("ENTRAR")')
    page.wait_for_timeout(4000)
    page.click(f'text="{unidade_selector}"', timeout=5000)
    page.wait_for_timeout(5000)
    return True


def test_endpoint_fetch(page, endpoint, params="limit=5&offset=0"):
    """Testa um endpoint via fetch no contexto do browser."""
    url = f"{endpoint}?{params}" if params else endpoint
    try:
        result = page.evaluate(f"""
            async () => {{
                try {{
                    const resp = await fetch('{url}', {{
                        headers: {{
                            'Accept': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        }},
                    }});
                    const ct = resp.headers.get('content-type') || '';
                    if (ct.includes('json')) {{
                        const data = await resp.json();
                        return {{
                            status: resp.status,
                            type: 'json',
                            count: data.count || (Array.isArray(data) ? data.length : (data.results ? data.results.length : null)),
                            keys: data.results && data.results.length > 0
                                ? Object.keys(data.results[0])
                                : (Array.isArray(data) && data.length > 0
                                    ? Object.keys(data[0])
                                    : Object.keys(data)),
                            sample: data.results ? data.results.slice(0, 2) : (Array.isArray(data) ? data.slice(0, 2) : data),
                        }};
                    }} else {{
                        const text = await resp.text();
                        return {{
                            status: resp.status,
                            type: ct.includes('html') ? 'html' : 'other',
                            preview: text.substring(0, 200),
                        }};
                    }}
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}
        """)
        return result
    except Exception as e:
        return {"error": str(e)[:100]}


def intercept_network(page, url_to_visit, wait_ms=5000):
    """Navega para URL interceptando todas as requests de rede."""
    captured = []

    def on_request(request):
        if '/api/' in request.url or 'activesoft' in request.url:
            captured.append({
                'url': request.url,
                'method': request.method,
            })

    def on_response(response):
        if '/api/' in response.url:
            ct = response.headers.get('content-type', '')
            for cap in captured:
                if cap['url'] == response.url:
                    cap['status'] = response.status
                    cap['content_type'] = ct
                    cap['is_json'] = 'json' in ct
                    break

    page.on("request", on_request)
    page.on("response", on_response)

    try:
        page.goto(f"{SIGA_APP}{url_to_visit}", timeout=15000)
    except:
        pass
    page.wait_for_timeout(wait_ms)

    page.remove_listener("request", on_request)
    page.remove_listener("response", on_response)

    return captured


def extrair_vendas_995_via_observacoes(page, unidade_codigo):
    """Extrai TODAS as observações que mencionam 995 ou PEDIDO LOJA (sem filtro de data)."""
    print(f"\n  Extraindo observações com 995/LOJA para {unidade_codigo}...")

    # Primeiro: contar TOTAL de registros (sem filtro de data)
    count_result = page.evaluate("""
        async () => {
            const resp = await fetch(
                '/api/v1/aluno_observacao/?limit=1&offset=0&maximoPorPagina=1',
                { headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' } }
            );
            return await resp.json();
        }
    """)
    total = count_result.get('count', 0)
    print(f"    Total observações (todas as datas): {total}")

    # Buscar observações com "995" ou "LOJA" - vamos buscar TODAS as observações
    # do tipo "Observação sobre Material Didático" que são as que contêm vendas
    # Testar primeiro com busca por tipo
    tipo_result = page.evaluate("""
        async () => {
            // Tentar filtrar por tipo_ocorrencia (Material Didático)
            const resp = await fetch(
                '/api/v1/aluno_observacao/?limit=5&offset=0&maximoPorPagina=5&tipo_ocorrencia_nome=Observa%C3%A7%C3%A3o%20sobre%20Material%20Did%C3%A1tico',
                { headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' } }
            );
            return await resp.json();
        }
    """)
    print(f"    Filtro por 'Material Didático': {tipo_result.get('count', 'N/A')} registros")

    # Tentar filtrar por busca de texto (se o endpoint suporta)
    busca_result = page.evaluate("""
        async () => {
            const resp = await fetch(
                '/api/v1/aluno_observacao/?limit=5&offset=0&maximoPorPagina=5&search=995',
                { headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' } }
            );
            return await resp.json();
        }
    """)
    print(f"    Busca por '995': {busca_result.get('count', 'N/A')} registros")

    # Tentar filtrar por nome (campo de observação)
    nome_result = page.evaluate("""
        async () => {
            const resp = await fetch(
                '/api/v1/aluno_observacao/?limit=5&offset=0&maximoPorPagina=5&nome__icontains=995',
                { headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' } }
            );
            return await resp.json();
        }
    """)
    print(f"    Filtro nome__icontains=995: {nome_result.get('count', 'N/A')} registros")

    # Tentar com observacao__icontains
    obs_result = page.evaluate("""
        async () => {
            const resp = await fetch(
                '/api/v1/aluno_observacao/?limit=5&offset=0&maximoPorPagina=5&observacao__icontains=995',
                { headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' } }
            );
            return await resp.json();
        }
    """)
    print(f"    Filtro observacao__icontains=995: {obs_result.get('count', 'N/A')} registros")

    # Tentar vários filtros possíveis do Django REST Framework
    for filtro_nome in ['busca', 'q', 'texto', 'descricao__icontains']:
        fr = page.evaluate(f"""
            async () => {{
                const resp = await fetch(
                    '/api/v1/aluno_observacao/?limit=1&offset=0&maximoPorPagina=1&{filtro_nome}=995',
                    {{ headers: {{ 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }} }}
                );
                return await resp.json();
            }}
        """)
        cnt = fr.get('count', 'N/A')
        if cnt != 'N/A' and cnt != total:
            print(f"    Filtro {filtro_nome}=995: {cnt} registros *** DIFERENTE! ***")

    # Agora extrair todos os registros de Material Didático (sem filtro de data)
    # para capturar vendas históricas do 995
    tipo_filter = "tipo_ocorrencia_nome=Observa%C3%A7%C3%A3o%20sobre%20Material%20Did%C3%A1tico"

    # Contar com este filtro
    mat_count = page.evaluate(f"""
        async () => {{
            const resp = await fetch(
                '/api/v1/aluno_observacao/?limit=1&offset=0&maximoPorPagina=1&{tipo_filter}',
                {{ headers: {{ 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }} }}
            );
            return await resp.json();
        }}
    """)
    total_mat = mat_count.get('count', 0)
    print(f"    Material Didático (sem data): {total_mat} registros")

    # Se o filtro de tipo não funcionou, tentar buscar por tipo_ocorrencia ID
    if total_mat == 0 or total_mat == total:
        # Tentar tipo_ocorrencia_novo (campo alternativo)
        for tipo_id_test in [None]:  # Placeholder
            pass

        # Fallback: buscar TUDO e filtrar localmente
        # Mas só se o total for razoável (< 50K)
        if total > 50000:
            print(f"    Total muito grande ({total}). Buscando com filtros por ano...")
            # Buscar por ano (2025 e 2026) para pegar mais vendas
            all_records = []
            for year in [2025, 2026]:
                date_filter = f"data_inicial_ocorrencia=01%2F01%2F{year}"
                yr_count = page.evaluate(f"""
                    async () => {{
                        const resp = await fetch(
                            '/api/v1/aluno_observacao/?limit=1&offset=0&maximoPorPagina=1&{date_filter}',
                            {{ headers: {{ 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }} }}
                        );
                        return await resp.json();
                    }}
                """)
                yr_total = yr_count.get('count', 0)
                print(f"    Ano {year}: {yr_total} registros")

                # Extrair paginado
                offset = 0
                PAGE_SIZE = 500
                year_records = []
                while offset < yr_total:
                    batch = page.evaluate(f"""
                        async () => {{
                            const resp = await fetch(
                                '/api/v1/aluno_observacao/?limit={PAGE_SIZE}&offset={offset}&maximoPorPagina={PAGE_SIZE}&ordering=-data_ocorrencia&{date_filter}',
                                {{ headers: {{ 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }} }}
                            );
                            return await resp.json();
                        }}
                    """)
                    results = batch.get('results', [])
                    if not results:
                        break
                    year_records.extend(results)
                    offset += PAGE_SIZE
                    if len(year_records) % 2000 == 0:
                        print(f"      {len(year_records)}/{yr_total}...")

                # Filtrar localmente por "995" ou "LOJA"
                for rec in year_records:
                    texto = (rec.get('nome', '') or '').upper()
                    if '995' in texto or 'LOJA ONLINE' in texto or 'PEDIDO LOJA' in texto:
                        rec['_unidade'] = unidade_codigo
                        all_records.append(rec)

                print(f"    Ano {year}: {len(year_records)} total → {len([r for r in all_records if r.get('_unidade') == unidade_codigo])} com 995/LOJA")

            return all_records
        else:
            print(f"    Buscando todos os {total} registros...")
            all_records = []
            offset = 0
            PAGE_SIZE = 500
            while offset < total:
                batch = page.evaluate(f"""
                    async () => {{
                        const resp = await fetch(
                            '/api/v1/aluno_observacao/?limit={PAGE_SIZE}&offset={offset}&maximoPorPagina={PAGE_SIZE}&ordering=-data_ocorrencia',
                            {{ headers: {{ 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }} }}
                        );
                        return await resp.json();
                    }}
                """)
                results = batch.get('results', [])
                if not results:
                    break
                for rec in results:
                    texto = (rec.get('nome', '') or '').upper()
                    if '995' in texto or 'LOJA ONLINE' in texto or 'PEDIDO LOJA' in texto:
                        rec['_unidade'] = unidade_codigo
                        all_records.append(rec)
                offset += PAGE_SIZE
                if offset % 5000 == 0:
                    print(f"      Processados {offset}/{total}... (encontrados: {len(all_records)})")

            return all_records
    else:
        # Filtro de tipo funcionou - extrair só esses
        all_records = []
        offset = 0
        PAGE_SIZE = 200
        while offset < total_mat:
            batch = page.evaluate(f"""
                async () => {{
                    const resp = await fetch(
                        '/api/v1/aluno_observacao/?limit={PAGE_SIZE}&offset={offset}&maximoPorPagina={PAGE_SIZE}&ordering=-data_ocorrencia&{tipo_filter}',
                        {{ headers: {{ 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }} }}
                    );
                    return await resp.json();
                }}
            """)
            results = batch.get('results', [])
            if not results:
                break
            for rec in results:
                texto = (rec.get('nome', '') or '').upper()
                if '995' in texto:
                    rec['_unidade'] = unidade_codigo
                    all_records.append(rec)
            offset += PAGE_SIZE
            if offset % 1000 == 0:
                print(f"      Processados {offset}/{total_mat}... (com 995: {len(all_records)})")

        return all_records


def main():
    print("=" * 80)
    print("EXPLORAÇÃO MÓDULO FINANCEIRO SIGA - VENDAS PRODUTO 995")
    print(f"Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 80)

    all_findings = {
        'endpoints_json': [],
        'endpoints_html': [],
        'endpoints_error': [],
        'network_captured': [],
        'vendas_995': [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1400, 'height': 900})
        page = context.new_page()

        # ===== FASE 1: Login e testar endpoints financeiros =====
        print("\n" + "=" * 60)
        print("FASE 1: Login e descoberta de endpoints financeiros")
        print("=" * 60)

        login_siga(page, UNIDADES[0]["selector"])
        page.goto(f"{SIGA_APP}/info/", timeout=15000)
        page.wait_for_timeout(3000)
        print(f"  Logado em: {page.url}")

        # Testar todos os endpoints financeiros candidatos
        print(f"\n  Testando {len(FINANCIAL_ENDPOINTS)} endpoints financeiros...")
        for ep in FINANCIAL_ENDPOINTS:
            result = test_endpoint_fetch(page, ep)
            status = result.get('status', 'err')
            ep_type = result.get('type', 'unknown')
            count = result.get('count', '')
            keys = result.get('keys', [])

            if ep_type == 'json' and status == 200:
                marker = f"*** JSON {status} - {count} regs ***"
                if keys:
                    marker += f" keys={keys[:8]}"
                print(f"    {ep}: {marker}")
                all_findings['endpoints_json'].append({
                    'endpoint': ep,
                    'status': status,
                    'count': count,
                    'keys': keys,
                    'sample': result.get('sample'),
                })
            elif ep_type == 'html':
                all_findings['endpoints_html'].append(ep)
            else:
                err = result.get('error', f'{status}')
                all_findings['endpoints_error'].append({'endpoint': ep, 'error': err})

        # Também testar com periodo= de BV
        print(f"\n  Testando endpoints com periodo=80 (BV)...")
        extra_params = [
            ("/api/v1/titulo/?periodo=80&limit=5", None),
            ("/api/v1/titulo/titulo/lista/?periodo=80&limit=5", None),
            ("/api/v1/financeiro/titulo/?periodo=80&limit=5", None),
            ("/api/v1/venda/?periodo=80&limit=5", None),
            ("/api/v1/produto/?periodo=80&limit=5", None),
            ("/api/v1/servico/?periodo=80&limit=5", None),
            ("/api/v1/loja/?periodo=80&limit=5", None),
            ("/api/v1/contrato/?periodo=80&limit=5", None),
            ("/api/v1/parcela/?periodo=80&limit=5", None),
        ]
        for ep_url, _ in extra_params:
            result = test_endpoint_fetch(page, ep_url, params=None)
            if result.get('type') == 'json' and result.get('status') == 200:
                count = result.get('count', '')
                print(f"    {ep_url}: JSON {count} regs, keys={result.get('keys', [])[:8]}")
                all_findings['endpoints_json'].append({
                    'endpoint': ep_url,
                    'count': count,
                    'keys': result.get('keys', []),
                    'sample': result.get('sample'),
                })

        # ===== FASE 2: Navegar rotas SPA financeiras e capturar rede =====
        print(f"\n" + "=" * 60)
        print("FASE 2: Navegação SPA financeira (interceptar rede)")
        print("=" * 60)

        for route in SPA_FINANCIAL_ROUTES:
            captured = intercept_network(page, route, wait_ms=3000)
            api_calls = [c for c in captured if '/api/' in c.get('url', '')]
            if api_calls:
                print(f"\n  {route}:")
                for call in api_calls:
                    is_json = call.get('is_json', False)
                    status = call.get('status', '?')
                    marker = "JSON" if is_json else "HTML"
                    print(f"    {call['method']} {call['url'][:100]} → {status} {marker}")
                    all_findings['network_captured'].append(call)

        # ===== FASE 3: Explorar menu de navegação =====
        print(f"\n" + "=" * 60)
        print("FASE 3: Menu de navegação (links_navegacao)")
        print("=" * 60)

        nav_result = test_endpoint_fetch(page, "/api/v1/links_navegacao/", params="")
        if nav_result.get('type') == 'json':
            nav_data = nav_result.get('sample', [])
            print(f"  Menu items: {len(nav_data) if isinstance(nav_data, list) else 'dict'}")

            # Extrair links financeiros do menu
            nav_text = json.dumps(nav_data, ensure_ascii=False)
            financial_keywords = ['financ', 'titulo', 'caixa', 'cobran', 'venda', 'loja',
                                  'receb', 'bolet', 'fatura', 'parcel', 'contrato', 'materi']
            for kw in financial_keywords:
                matches = re.findall(rf'[^"]*{kw}[^"]*', nav_text, re.IGNORECASE)
                if matches:
                    unique = set(m.strip() for m in matches if len(m) < 100)
                    for m in list(unique)[:5]:
                        print(f"    [{kw}] {m}")

        # ===== FASE 4: Extrair vendas 995 via observações =====
        print(f"\n" + "=" * 60)
        print("FASE 4: Extrair vendas 995 por unidade")
        print("=" * 60)

        vendas_995_todas = []

        for idx, unidade in enumerate(UNIDADES):
            print(f"\n--- Unidade {unidade['nome']} ---")

            # Re-login para cada unidade
            if idx > 0:
                try:
                    login_siga(page, unidade["selector"])
                    page.goto(f"{SIGA_APP}/info/", timeout=15000)
                    page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"  FALHA login: {str(e)[:60]}")
                    continue

            vendas = extrair_vendas_995_via_observacoes(page, unidade["codigo"])
            print(f"  → {len(vendas)} registros com 995/LOJA encontrados em {unidade['nome']}")
            vendas_995_todas.extend(vendas)

        browser.close()

    # ===== FASE 5: Processar e analisar vendas 995 =====
    print(f"\n" + "=" * 80)
    print("FASE 5: ANÁLISE DAS VENDAS DO PRODUTO 995")
    print("=" * 80)

    # Separar pedidos com 995 vs todos os pedidos LOJA
    pedidos_995 = []
    pedidos_loja_total = []

    for rec in vendas_995_todas:
        texto = (rec.get('nome', '') or '')
        unidade = rec.get('_unidade', '')
        turma_nome = rec.get('nome_turma_completo', '') or ''
        aluno = rec.get('aluno_nome', '') or ''
        data = (rec.get('data_ocorrencia', '') or '')[:10]

        # Extrair série do nome da turma
        serie = ''
        serie_match = re.search(r'/\s*([\dºª]+\s*(?:Ano|Série)[^/]*)\s*/', turma_nome)
        if serie_match:
            serie = serie_match.group(1).strip()

        # Extrair turma
        turma_match = re.search(r'Turma\s+(\w)', turma_nome)
        turma_letra = turma_match.group(1) if turma_match else ''

        # Extrair valor pago
        valor_match = re.search(r'Valor pago\s*[-–]\s*R\$\s*([\d.,]+)', texto)
        valor = valor_match.group(1) if valor_match else ''

        # Extrair referência do pedido
        ref_match = re.search(r'Refer[eê]ncia do Pedido\s*[-–]\s*(\w+)', texto)
        ref = ref_match.group(1) if ref_match else ''

        # Extrair número da fatura
        fatura_match = re.search(r'N[uú]mero da fatura\s*[-–]\s*#?(\w+)', texto)
        fatura = fatura_match.group(1) if fatura_match else ''

        # Extrair produtos
        produtos = re.findall(r'(\d{3})\s*-\s*([^|]+?)(?:\||$)', texto)
        prod_str = '; '.join(f"{c}-{n.strip()}" for c, n in produtos)

        record = {
            'unidade': unidade,
            'aluno': aluno,
            'serie': serie,
            'turma': turma_letra,
            'data': data,
            'valor': valor,
            'referencia': ref,
            'fatura': fatura,
            'produtos': prod_str,
            'tem_995': '995' in texto,
        }

        if 'LOJA' in texto.upper() or 'PEDIDO' in texto.upper():
            pedidos_loja_total.append(record)

        if '995' in texto:
            pedidos_995.append(record)

    print(f"\n  Total pedidos LOJA encontrados: {len(pedidos_loja_total)}")
    print(f"  Total pedidos com 995 (Elo Tech): {len(pedidos_995)}")

    # Análise por unidade
    print(f"\n  === POR UNIDADE ===")
    by_unit = defaultdict(int)
    for p in pedidos_995:
        by_unit[p['unidade']] += 1
    for u, c in sorted(by_unit.items()):
        print(f"    {u}: {c}")

    # Análise por série
    print(f"\n  === POR SÉRIE ===")
    by_serie = defaultdict(int)
    for p in pedidos_995:
        by_serie[p['serie'] or 'Sem série'] += 1
    for s, c in sorted(by_serie.items(), key=lambda x: -x[1]):
        print(f"    {s}: {c}")

    # Análise por unidade × série
    print(f"\n  === POR UNIDADE × SÉRIE ===")
    by_unit_serie = defaultdict(lambda: defaultdict(int))
    for p in pedidos_995:
        by_unit_serie[p['unidade']][p['serie'] or 'Sem série'] += 1
    for u in sorted(by_unit_serie.keys()):
        print(f"\n    {u}:")
        for s, c in sorted(by_unit_serie[u].items(), key=lambda x: -x[1]):
            print(f"      {s}: {c}")

    # Análise por unidade × série × turma
    print(f"\n  === POR UNIDADE × SÉRIE × TURMA ===")
    by_unit_serie_turma = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for p in pedidos_995:
        by_unit_serie_turma[p['unidade']][p['serie'] or 'Sem série'][p['turma'] or '-'] += 1
    for u in sorted(by_unit_serie_turma.keys()):
        print(f"\n    {u}:")
        for s in sorted(by_unit_serie_turma[u].keys()):
            turmas = by_unit_serie_turma[u][s]
            turma_str = ', '.join(f"Turma {t}={c}" for t, c in sorted(turmas.items()))
            total_s = sum(turmas.values())
            print(f"      {s}: {total_s} ({turma_str})")

    # ===== FASE 6: Salvar resultados =====
    print(f"\n" + "=" * 60)
    print("FASE 6: Salvando resultados")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # CSV de vendas 995
    csv_995_path = OUTPUT_DIR / 'vendas_995_elo_tech.csv'
    if pedidos_995:
        fieldnames = ['unidade', 'aluno', 'serie', 'turma', 'data', 'valor',
                      'referencia', 'fatura', 'produtos']
        with open(csv_995_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in pedidos_995:
                row = {k: p.get(k, '') for k in fieldnames}
                writer.writerow(row)
        print(f"  vendas_995_elo_tech.csv: {len(pedidos_995)} registros")

    # CSV de TODOS os pedidos LOJA
    csv_loja_path = OUTPUT_DIR / 'vendas_loja_online_elo.csv'
    if pedidos_loja_total:
        fieldnames = ['unidade', 'aluno', 'serie', 'turma', 'data', 'valor',
                      'referencia', 'fatura', 'produtos', 'tem_995']
        with open(csv_loja_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in pedidos_loja_total:
                row = {k: p.get(k, '') for k in fieldnames}
                writer.writerow(row)
        print(f"  vendas_loja_online_elo.csv: {len(pedidos_loja_total)} registros")

    # JSON completo com todos os achados
    json_path = SCRIPT_DIR / f"financeiro_siga_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'endpoints_json': all_findings['endpoints_json'],
            'endpoints_html_count': len(all_findings['endpoints_html']),
            'endpoints_html': all_findings['endpoints_html'],
            'endpoints_error_count': len(all_findings['endpoints_error']),
            'network_captured': all_findings['network_captured'],
            'vendas_995_count': len(pedidos_995),
            'vendas_loja_total_count': len(pedidos_loja_total),
            'vendas_995_por_unidade': dict(by_unit),
            'vendas_995_por_serie': dict(by_serie),
        }, f, indent=2, ensure_ascii=False, default=str)
    print(f"  {json_path.name}: resultados completos")

    # Resumo final
    duracao = datetime.now()
    print(f"\n" + "=" * 80)
    print("RESUMO FINAL")
    print("=" * 80)
    print(f"  Endpoints JSON encontrados: {len(all_findings['endpoints_json'])}")
    print(f"  Endpoints HTML (SPA): {len(all_findings['endpoints_html'])}")
    print(f"  Pedidos LOJA Online total: {len(pedidos_loja_total)}")
    print(f"  Pedidos com 995 (Elo Tech): {len(pedidos_995)}")
    print(f"    BV: {by_unit.get('BV', 0)}")
    print(f"    CD: {by_unit.get('CD', 0)}")
    print(f"    JG: {by_unit.get('JG', 0)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
