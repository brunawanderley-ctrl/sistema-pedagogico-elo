#!/usr/bin/env python3
"""
INTERCEPTADOR DE FREQUENCIA v3 - Playwright SPA Navigator + Network Interceptor

=== POR QUE v1 e v2 FALHARAM ===
v1 (interceptar_api_siga.py):
  - Navegou via page.goto() direto para /diario/{id}/frequencia/
  - O endpoint retorna HTML SPA shell (11788 bytes), NAO JSON
  - A interceptacao de rede so viu a carga inicial, nao os AJAX calls
  - Tentou fetch via requests (contexto diferente da sessao do SPA)

v2 (interceptar_api_siga_v2.py):
  - Navegou no dominio siga02, mas tambem via page.goto()
  - Mesmo problema: o SPA nao carrega os chunks de frequencia
  - Nao injetou interceptor de XHR/fetch ANTES da navegacao
  - Nao tentou interagir com a UI (clicar em abas, botoes)

=== ESTRATEGIA v3 ===
1. Login via Playwright (identico ao extrair_ocorrencias_siga.py que FUNCIONA)
2. Injetar interceptor de XHR/fetch ANTES de qualquer navegacao
3. Navegar para /diarios/ e INTERAGIR com a UI (clicar em diarios, abas)
4. Capturar TODAS as requisicoes de rede (page.on + window.__xhrCalls)
5. Se AJAX nao revelar endpoints, fazer DOM scraping das tabelas
6. Analisar chunks JS carregados em busca de URLs de API
7. Salvar TUDO em JSON para analise

Autor: Agente IOTA (Arena 4)
Data: 2026-02-20
"""

import json
import os
import re
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

# Verificar Playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("ERRO: Playwright nao instalado!")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
SIGA_LOGIN = "https://siga.activesoft.com.br"
SIGA_APP = "https://siga02.activesoft.com.br"

CONFIG = {
    "instituicao": os.environ.get("SIGA_INSTITUICAO", "COLEGIOELO"),
    "login": os.environ.get("SIGA_LOGIN", "bruna"),
    "senha": os.environ.get("SIGA_SENHA", ""),
}

# Unidades e periodos
UNIDADES = [
    {"nome": "Boa Viagem", "codigo": "BV", "periodo": 80, "selector": "1 - BV (Boa Viagem)"},
    {"nome": "Candeias", "codigo": "CD", "periodo": 78, "selector": "2 - CD (Jaboatão)"},
    {"nome": "Janga", "codigo": "JG", "periodo": 79, "selector": "3 - JG (Paulista)"},
    {"nome": "Cordeiro", "codigo": "CDR", "periodo": 77, "selector": "4 - CDR (Cordeiro)"},
]

# Timeout generoso para SPA lento
TIMEOUT_NAV = 30000      # 30s para navegacao
TIMEOUT_CLICK = 15000    # 15s para clicks
TIMEOUT_WAIT = 10000     # 10s para esperar elementos
WAIT_AFTER_NAV = 5000    # 5s apos navegacao
WAIT_AFTER_CLICK = 4000  # 4s apos click

# ============================================================
# INTERCEPTOR JAVASCRIPT (injetado no browser ANTES da navegacao)
# ============================================================
XHR_FETCH_INTERCEPTOR_JS = """
// === INTERCEPTOR XHR/fetch - Agente IOTA v3 ===
// Captura TODAS as chamadas AJAX feitas pelo SPA

(function() {
    // Evitar dupla-injecao
    if (window.__iotaInterceptorActive) return;
    window.__iotaInterceptorActive = true;

    // ---- XMLHttpRequest ----
    window.__xhrCalls = [];
    const origOpen = XMLHttpRequest.prototype.open;
    const origSend = XMLHttpRequest.prototype.send;
    const origSetHeader = XMLHttpRequest.prototype.setRequestHeader;

    XMLHttpRequest.prototype.open = function(method, url, async_, user, pass_) {
        this._iota_method = method;
        this._iota_url = url;
        this._iota_headers = {};
        return origOpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.setRequestHeader = function(name, value) {
        if (this._iota_headers) {
            this._iota_headers[name] = value;
        }
        return origSetHeader.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function(body) {
        const xhr = this;
        const entry = {
            method: xhr._iota_method,
            url: xhr._iota_url,
            headers: Object.assign({}, xhr._iota_headers || {}),
            requestBody: body ? String(body).substring(0, 2000) : null,
            timestamp: Date.now(),
            source: 'xhr',
        };

        xhr.addEventListener('load', function() {
            entry.status = xhr.status;
            entry.responseHeaders = {};
            try {
                const allHeaders = xhr.getAllResponseHeaders();
                allHeaders.split('\\r\\n').forEach(function(line) {
                    const parts = line.split(': ');
                    if (parts.length >= 2) {
                        entry.responseHeaders[parts[0].toLowerCase()] = parts.slice(1).join(': ');
                    }
                });
            } catch(e) {}
            entry.contentType = xhr.getResponseHeader('content-type') || '';
            try {
                entry.responseSize = xhr.responseText ? xhr.responseText.length : 0;
                entry.responsePreview = xhr.responseText ? xhr.responseText.substring(0, 3000) : null;
                // Tentar parsear como JSON
                if (entry.contentType.includes('json') ||
                    (xhr.responseText && (xhr.responseText.trim().startsWith('[') || xhr.responseText.trim().startsWith('{')))) {
                    try {
                        const data = JSON.parse(xhr.responseText);
                        entry.isJson = true;
                        if (Array.isArray(data)) {
                            entry.jsonType = 'array';
                            entry.jsonCount = data.length;
                            if (data.length > 0 && typeof data[0] === 'object') {
                                entry.jsonKeys = Object.keys(data[0]).slice(0, 20);
                                entry.jsonSample = JSON.stringify(data[0]).substring(0, 1000);
                            }
                        } else if (typeof data === 'object') {
                            entry.jsonType = 'object';
                            entry.jsonKeys = Object.keys(data).slice(0, 20);
                            if (data.results) {
                                entry.jsonCount = data.count || data.results.length;
                                if (data.results.length > 0 && typeof data.results[0] === 'object') {
                                    entry.jsonResultKeys = Object.keys(data.results[0]).slice(0, 20);
                                    entry.jsonSample = JSON.stringify(data.results[0]).substring(0, 1000);
                                }
                            }
                        }
                    } catch(e) {
                        entry.isJson = false;
                    }
                }
            } catch(e) {
                entry.responseError = e.message;
            }
            window.__xhrCalls.push(entry);
        });

        xhr.addEventListener('error', function() {
            entry.error = true;
            entry.status = 0;
            window.__xhrCalls.push(entry);
        });

        return origSend.apply(this, arguments);
    };

    // ---- fetch API ----
    window.__fetchCalls = [];
    const origFetch = window.fetch;

    window.fetch = function(input, init) {
        const url = typeof input === 'string' ? input : (input instanceof Request ? input.url : String(input));
        const method = (init && init.method) || (input instanceof Request ? input.method : 'GET');
        const entry = {
            url: url,
            method: method.toUpperCase(),
            timestamp: Date.now(),
            source: 'fetch',
        };

        if (init && init.body) {
            try {
                entry.requestBody = typeof init.body === 'string'
                    ? init.body.substring(0, 2000)
                    : '[non-string body]';
            } catch(e) {}
        }
        if (init && init.headers) {
            try {
                entry.requestHeaders = {};
                if (init.headers instanceof Headers) {
                    init.headers.forEach(function(v, k) { entry.requestHeaders[k] = v; });
                } else if (typeof init.headers === 'object') {
                    entry.requestHeaders = Object.assign({}, init.headers);
                }
            } catch(e) {}
        }

        return origFetch.apply(this, arguments).then(function(response) {
            entry.status = response.status;
            entry.contentType = response.headers.get('content-type') || '';

            // Clone para ler o body sem consumir a resposta
            const clone = response.clone();
            clone.text().then(function(text) {
                entry.responseSize = text.length;
                entry.responsePreview = text.substring(0, 3000);
                // Tentar parsear JSON
                if (entry.contentType.includes('json') ||
                    (text.trim().startsWith('[') || text.trim().startsWith('{'))) {
                    try {
                        const data = JSON.parse(text);
                        entry.isJson = true;
                        if (Array.isArray(data)) {
                            entry.jsonType = 'array';
                            entry.jsonCount = data.length;
                            if (data.length > 0 && typeof data[0] === 'object') {
                                entry.jsonKeys = Object.keys(data[0]).slice(0, 20);
                                entry.jsonSample = JSON.stringify(data[0]).substring(0, 1000);
                            }
                        } else if (typeof data === 'object') {
                            entry.jsonType = 'object';
                            entry.jsonKeys = Object.keys(data).slice(0, 20);
                            if (data.results) {
                                entry.jsonCount = data.count || data.results.length;
                                if (data.results.length > 0 && typeof data.results[0] === 'object') {
                                    entry.jsonResultKeys = Object.keys(data.results[0]).slice(0, 20);
                                    entry.jsonSample = JSON.stringify(data.results[0]).substring(0, 1000);
                                }
                            }
                        }
                    } catch(e) {
                        entry.isJson = false;
                    }
                }
            }).catch(function(e) {
                entry.responseError = e.message;
            });

            window.__fetchCalls.push(entry);
            return response;
        }).catch(function(err) {
            entry.error = true;
            entry.errorMessage = err.message;
            window.__fetchCalls.push(entry);
            throw err;
        });
    };

    // ---- jQuery $.ajax interceptor (se jQuery estiver carregado) ----
    window.__jqueryAjaxCalls = [];

    function hookJQuery() {
        if (window.jQuery && !window.__jqueryHooked) {
            window.__jqueryHooked = true;
            const origAjax = window.jQuery.ajax;
            window.jQuery.ajax = function(url, settings) {
                // jQuery.ajax pode ser chamado com (url, settings) ou ({url, ...settings})
                let opts = {};
                if (typeof url === 'object') {
                    opts = url;
                } else {
                    opts = settings || {};
                    opts.url = url;
                }

                window.__jqueryAjaxCalls.push({
                    url: opts.url,
                    method: (opts.method || opts.type || 'GET').toUpperCase(),
                    data: opts.data ? JSON.stringify(opts.data).substring(0, 1000) : null,
                    dataType: opts.dataType,
                    timestamp: Date.now(),
                });

                return origAjax.apply(this, arguments);
            };
        }
    }

    // Tentar hookar jQuery agora e periodicamente (pode carregar depois)
    hookJQuery();
    setInterval(hookJQuery, 1000);

    console.log('[IOTA v3] XHR/fetch/jQuery interceptors installed');
})();
"""


def log(msg, level="INFO"):
    """Log com timestamp."""
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "  ", "OK": "  [OK]", "WARN": "  [!]", "ERR": "  [X]", "HEAD": "\n---"}
    print(f"{prefix.get(level, '  ')} [{ts}] {msg}")


def safe_json_serialize(obj):
    """Serializa para JSON de forma segura."""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        return str(obj)


class SIGAInterceptorV3:
    """Interceptador completo de frequencia do SIGA via Playwright."""

    def __init__(self):
        self.captured_responses = []   # page.on('response')
        self.captured_requests = []    # page.on('request')
        self.js_chunks_loaded = []     # arquivos .js carregados
        self.dom_tables = {}           # HTML de tabelas extraidas
        self.screenshots = {}          # Screenshots (base64) por etapa
        self.api_urls_from_js = []     # URLs de API descobertas nos JS chunks
        self.diario_id = None
        self.turma_id = None
        self.page = None
        self.context = None
        self.dry_run = False

    def _on_request(self, request):
        """Callback para CADA request feito pelo browser."""
        url = request.url
        resource = request.resource_type
        # Filtrar estaticos ruidosos
        if resource in ('image', 'font', 'stylesheet', 'media', 'manifest', 'other'):
            return
        # Registrar JS chunks
        if resource == 'script' or url.endswith('.js'):
            self.js_chunks_loaded.append({
                'url': url,
                'timestamp': datetime.now().isoformat(),
            })
        entry = {
            'url': url,
            'method': request.method,
            'resource_type': resource,
            'post_data': None,
            'timestamp': datetime.now().isoformat(),
        }
        try:
            if request.post_data:
                entry['post_data'] = request.post_data[:2000]
        except Exception:
            pass
        self.captured_requests.append(entry)

    def _on_response(self, response):
        """Callback para CADA response recebido pelo browser."""
        url = response.url
        resource = response.request.resource_type
        if resource in ('image', 'font', 'stylesheet', 'media', 'manifest', 'other'):
            return

        content_type = response.headers.get('content-type', '')
        entry = {
            'url': url,
            'method': response.request.method,
            'status': response.status,
            'content_type': content_type[:100],
            'resource_type': resource,
            'timestamp': datetime.now().isoformat(),
        }

        is_json = 'application/json' in content_type
        is_siga = 'siga' in url or 'activesoft' in url

        if is_json and is_siga:
            try:
                body = response.json()
                if isinstance(body, list):
                    entry['json_type'] = 'list'
                    entry['json_count'] = len(body)
                    if body and isinstance(body[0], dict):
                        entry['json_keys'] = list(body[0].keys())[:20]
                        entry['json_sample'] = {k: str(v)[:100] for k, v in list(body[0].items())[:8]}
                elif isinstance(body, dict):
                    entry['json_type'] = 'dict'
                    entry['json_keys'] = list(body.keys())[:20]
                    if 'results' in body:
                        entry['json_count'] = body.get('count', len(body.get('results', [])))
                        results = body.get('results', [])
                        if results and isinstance(results[0], dict):
                            entry['json_result_keys'] = list(results[0].keys())[:20]
                            entry['json_sample'] = {k: str(v)[:100] for k, v in list(results[0].items())[:8]}
                entry['is_json'] = True
                # Highlight na saida
                path = url.replace(SIGA_APP, '').replace(SIGA_LOGIN, '')
                count = entry.get('json_count', '?')
                keys = entry.get('json_keys', entry.get('json_result_keys', []))
                log(f"JSON [{entry['method']}] {path} -> {count} regs, keys={keys[:8]}", "OK")
            except Exception:
                pass

        self.captured_responses.append(entry)

    def login(self, page, unidade_selector="1 - BV (Boa Viagem)"):
        """Faz login no SIGA via Playwright."""
        log(f"Fazendo login (unidade: {unidade_selector})...", "HEAD")

        page.goto(f"{SIGA_LOGIN}/login/", timeout=TIMEOUT_NAV)
        page.wait_for_timeout(2000)

        # Preencher formulario
        page.fill('#codigoInstituicao', CONFIG["instituicao"])
        page.fill('#id_login', CONFIG["login"])
        page.fill('#id_senha', CONFIG["senha"])
        log("Formulario preenchido, clicando ENTRAR...")

        page.click('button:has-text("ENTRAR")')
        page.wait_for_timeout(4000)

        # Selecionar unidade
        try:
            page.click(f'text="{unidade_selector}"', timeout=TIMEOUT_CLICK)
            log(f"Unidade selecionada: {unidade_selector}", "OK")
        except PlaywrightTimeout:
            log(f"Timeout selecionando unidade. URL atual: {page.url}", "ERR")
            raise

        page.wait_for_timeout(5000)

        url_pos_login = page.url
        log(f"URL pos-login: {url_pos_login}")

        if 'siga02' not in url_pos_login and 'info' not in url_pos_login:
            log(f"Login pode ter falhado! URL nao eh siga02", "WARN")

        return url_pos_login

    def get_diario_test(self, page, periodo=80):
        """Obtem um diario de teste via fetch no contexto do browser."""
        log("Obtendo diario de teste via fetch...", "HEAD")

        result = page.evaluate(f"""
            async () => {{
                try {{
                    const resp = await fetch('/api/v1/diario/diario/lista/?limit=1000&offset=0&periodo={periodo}', {{
                        headers: {{'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest'}}
                    }});
                    const data = await resp.json();
                    const results = data.results || [];

                    // Buscar diario Fund II com aulas registradas
                    const comAulas = results.filter(d =>
                        (d.nome_curso || '').includes('Fundamental II') &&
                        d.qtd_aula_registradas > 0
                    );

                    // Se nao houver Fund II, tentar EM
                    const candidatos = comAulas.length > 0 ? comAulas : results.filter(d =>
                        (d.nome_curso || '').includes('Médio') &&
                        d.qtd_aula_registradas > 0
                    );

                    if (candidatos.length === 0) return {{ error: 'Nenhum diario com aulas encontrado' }};

                    const d = candidatos[0];
                    return {{
                        id: d.id,
                        turma: d.turma,
                        disciplina: d.disciplina_nome,
                        serie: d.nome_serie,
                        turma_nome: d.nome_turma,
                        professor: d.professor_nome,
                        qtd_aulas: d.qtd_aula_registradas,
                        fase: d.fase_nota_nome,
                        total_diarios: results.length,
                        total_candidatos: candidatos.length,
                    }};
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}
        """)

        if result.get('error'):
            log(f"Erro obtendo diario: {result['error']}", "ERR")
            return None

        self.diario_id = result['id']
        self.turma_id = result['turma']
        log(f"Diario: {self.diario_id} ({result['disciplina']} - {result['serie']})", "OK")
        log(f"Turma: {self.turma_id} ({result['turma_nome']})")
        log(f"Professor: {result.get('professor', '?')}")
        log(f"Aulas: {result['qtd_aulas']} | Fase: {result.get('fase', '?')}")
        log(f"Total diarios: {result['total_diarios']} | Candidatos: {result['total_candidatos']}")
        return result

    def collect_xhr_calls(self, page):
        """Coleta chamadas XHR/fetch/jQuery interceptadas pelo JS injetado."""
        try:
            xhr = page.evaluate("window.__xhrCalls || []")
            fetch = page.evaluate("window.__fetchCalls || []")
            jquery = page.evaluate("window.__jqueryAjaxCalls || []")
            return {'xhr': xhr, 'fetch': fetch, 'jquery': jquery}
        except Exception as e:
            log(f"Erro coletando interceptados: {e}", "WARN")
            return {'xhr': [], 'fetch': [], 'jquery': []}

    def extract_dom_tables(self, page, label=""):
        """Extrai todas as tabelas HTML do DOM atual."""
        try:
            tables = page.evaluate("""
                () => {
                    const results = [];
                    const tables = document.querySelectorAll('table');
                    tables.forEach((t, i) => {
                        const rows = [];
                        t.querySelectorAll('tr').forEach(tr => {
                            const cells = [];
                            tr.querySelectorAll('th, td').forEach(td => {
                                cells.push(td.innerText.trim().substring(0, 200));
                            });
                            if (cells.length > 0) rows.push(cells);
                        });
                        results.push({
                            index: i,
                            rows: rows.length,
                            cols: rows.length > 0 ? rows[0].length : 0,
                            html: t.outerHTML.substring(0, 10000),
                            data: rows.slice(0, 50),  // primeiras 50 linhas
                            classes: t.className,
                            id: t.id,
                        });
                    });
                    return results;
                }
            """)
            if tables:
                log(f"  DOM: {len(tables)} tabela(s) encontrada(s) em '{label}'")
                for t in tables:
                    log(f"    Table #{t['index']}: {t['rows']}x{t['cols']} (class={t.get('classes','')})")
                self.dom_tables[label] = tables
            else:
                log(f"  DOM: Nenhuma tabela em '{label}'")
            return tables
        except Exception as e:
            log(f"  DOM: Erro extraindo tabelas: {e}", "WARN")
            return []

    def extract_page_info(self, page, label=""):
        """Extrai informacoes gerais da pagina atual."""
        try:
            info = page.evaluate("""
                () => {
                    return {
                        url: window.location.href,
                        title: document.title,
                        tables: document.querySelectorAll('table').length,
                        forms: document.querySelectorAll('form').length,
                        selects: document.querySelectorAll('select').length,
                        buttons: document.querySelectorAll('button').length,
                        inputs: document.querySelectorAll('input').length,
                        links: document.querySelectorAll('a[href]').length,
                        grids: document.querySelectorAll('[class*=grid], [class*=ag-], .table-responsive').length,
                        spinners: document.querySelectorAll('.spinner, .loading, [class*=spinner], [class*=loading]').length,
                        tabs: document.querySelectorAll('.nav-tabs .nav-link, .tab-pane, [role=tab]').length,
                        modals: document.querySelectorAll('.modal, [role=dialog]').length,
                        bodyText: document.body ? document.body.innerText.substring(0, 2000) : '',
                    };
                }
            """)
            log(f"  Pagina '{label}': tables={info['tables']}, forms={info['forms']}, "
                f"selects={info['selects']}, tabs={info['tabs']}, grids={info['grids']}")
            return info
        except Exception as e:
            log(f"  Erro extraindo info pagina: {e}", "WARN")
            return {}

    def navigate_and_capture(self, page, url, label, wait_ms=None):
        """Navega para uma URL e captura tudo."""
        wait = wait_ms or WAIT_AFTER_NAV
        log(f"Navegando: {label} ({url.replace(SIGA_APP, '')})")

        xhr_before = self.collect_xhr_calls(page)
        count_before = len(xhr_before['xhr']) + len(xhr_before['fetch']) + len(xhr_before['jquery'])
        resp_before = len(self.captured_responses)

        try:
            page.goto(url, timeout=TIMEOUT_NAV, wait_until='domcontentloaded')
        except PlaywrightTimeout:
            log(f"  Timeout navegando para {label}", "WARN")
        except Exception as e:
            log(f"  Erro navegando: {e}", "WARN")

        page.wait_for_timeout(wait)

        # Esperar spinners desaparecerem
        try:
            page.wait_for_selector('.spinner, .loading, [class*=spinner]',
                                   state='hidden', timeout=5000)
        except Exception:
            pass

        # Coletar
        url_final = page.url
        info = self.extract_page_info(page, label)
        tables = self.extract_dom_tables(page, label)

        xhr_after = self.collect_xhr_calls(page)
        count_after = len(xhr_after['xhr']) + len(xhr_after['fetch']) + len(xhr_after['jquery'])
        resp_after = len(self.captured_responses)

        new_intercepted = count_after - count_before
        new_responses = resp_after - resp_before

        if url_final != url:
            log(f"  Redirecionou: {url_final.replace(SIGA_APP, '')}")
        log(f"  Capturado: +{new_responses} respostas rede, +{new_intercepted} XHR/fetch injetados")

        return {
            'label': label,
            'url_requested': url,
            'url_final': url_final,
            'page_info': info,
            'tables_count': len(tables),
            'new_responses': new_responses,
            'new_intercepted': new_intercepted,
        }

    def click_and_capture(self, page, selector, label, wait_ms=None):
        """Clica em um elemento e captura o que acontece."""
        wait = wait_ms or WAIT_AFTER_CLICK
        log(f"Clicando: {label} (selector: {selector})")

        xhr_before = self.collect_xhr_calls(page)
        count_before = len(xhr_before['xhr']) + len(xhr_before['fetch']) + len(xhr_before['jquery'])
        resp_before = len(self.captured_responses)

        try:
            page.click(selector, timeout=TIMEOUT_CLICK)
        except PlaywrightTimeout:
            log(f"  Timeout clicando '{label}'", "WARN")
            return None
        except Exception as e:
            log(f"  Erro clicando '{label}': {e}", "WARN")
            return None

        page.wait_for_timeout(wait)

        # Esperar spinners
        try:
            page.wait_for_selector('.spinner, .loading, [class*=spinner]',
                                   state='hidden', timeout=5000)
        except Exception:
            pass

        info = self.extract_page_info(page, f"apos_click_{label}")
        tables = self.extract_dom_tables(page, f"apos_click_{label}")

        xhr_after = self.collect_xhr_calls(page)
        count_after = len(xhr_after['xhr']) + len(xhr_after['fetch']) + len(xhr_after['jquery'])
        resp_after = len(self.captured_responses)

        new_intercepted = count_after - count_before
        new_responses = resp_after - resp_before

        log(f"  Pos-click: URL={page.url.replace(SIGA_APP,'')}")
        log(f"  Capturado: +{new_responses} respostas, +{new_intercepted} XHR/fetch")

        return {
            'label': label,
            'selector': selector,
            'url_after': page.url,
            'page_info': info,
            'tables_count': len(tables),
            'new_responses': new_responses,
            'new_intercepted': new_intercepted,
        }

    def find_and_click_tabs(self, page, label_prefix=""):
        """Encontra abas (tabs) na pagina e clica em cada uma."""
        log(f"Buscando abas na pagina...")

        tabs = page.evaluate("""
            () => {
                const tabs = [];
                // Bootstrap tabs
                document.querySelectorAll('.nav-tabs .nav-link, .nav-tabs a, [role=tab]').forEach(t => {
                    tabs.push({
                        text: t.innerText.trim().substring(0, 60),
                        href: t.getAttribute('href') || '',
                        id: t.id,
                        class: t.className,
                        ariaSelected: t.getAttribute('aria-selected'),
                    });
                });
                // Botoes que parecem abas
                document.querySelectorAll('.btn-group .btn, .nav-pills .nav-link').forEach(t => {
                    tabs.push({
                        text: t.innerText.trim().substring(0, 60),
                        href: t.getAttribute('href') || '',
                        id: t.id,
                        class: t.className,
                        type: 'btn-group',
                    });
                });
                return tabs;
            }
        """)

        if tabs:
            log(f"  Encontradas {len(tabs)} aba(s):")
            for t in tabs:
                log(f"    '{t['text']}' (id={t.get('id','')}, href={t.get('href','')})")
        else:
            log(f"  Nenhuma aba encontrada")

        results = []
        for tab in tabs:
            text = tab.get('text', '')
            if not text:
                continue
            # Focar em abas de frequencia/chamada/notas
            keywords = ['frequen', 'chamada', 'presenc', 'falta', 'nota', 'faltas',
                        'attendance', 'diario', 'aluno', 'turma']
            is_relevant = any(kw in text.lower() for kw in keywords)

            # Clicar em TODAS as abas, mas logar relevancia
            try:
                if tab.get('id'):
                    selector = f"#{tab['id']}"
                elif tab.get('href') and tab['href'].startswith('#'):
                    selector = f"[href='{tab['href']}']"
                else:
                    selector = f"text='{text}'"

                relevance = " ** RELEVANTE **" if is_relevant else ""
                result = self.click_and_capture(page, selector, f"{label_prefix}tab_{text}{relevance}")
                if result:
                    result['tab_text'] = text
                    result['is_relevant'] = is_relevant
                    results.append(result)
            except Exception as e:
                log(f"  Erro clicando aba '{text}': {e}", "WARN")

        return results

    def find_links_in_page(self, page):
        """Encontra links relevantes (diarios, frequencia, etc) na pagina."""
        links = page.evaluate("""
            () => {
                const allLinks = document.querySelectorAll('a[href], [onclick], tr[data-id], tr[class*=clickable]');
                const results = [];
                allLinks.forEach(el => {
                    const href = el.getAttribute('href') || '';
                    const onclick = el.getAttribute('onclick') || '';
                    const text = el.innerText.trim().substring(0, 100);
                    const tag = el.tagName;
                    const dataId = el.getAttribute('data-id') || '';

                    if (href.includes('diario') || href.includes('frequen') ||
                        href.includes('chamada') || href.includes('notas') ||
                        onclick.includes('diario') || onclick.includes('frequen') ||
                        dataId) {
                        results.push({
                            tag, href, onclick: onclick.substring(0, 200),
                            text: text.substring(0, 80), dataId,
                            class: el.className.substring(0, 80),
                        });
                    }
                });
                return results.slice(0, 30);
            }
        """)
        return links

    def analyze_js_chunks(self, page):
        """Analisa JS chunks carregados em busca de URLs de API."""
        log("Analisando chunks JS carregados...", "HEAD")

        # Pegar scripts externos
        scripts = page.evaluate("""
            () => Array.from(document.querySelectorAll('script[src]')).map(s => s.src)
        """)
        log(f"Scripts externos: {len(scripts)}")

        api_patterns_found = set()

        for src in scripts:
            filename = src.split('/')[-1].split('?')[0]
            # Focar em chunks que possam conter logica de diario/frequencia
            if any(kw in filename.lower() for kw in
                   ['chunk', 'app', 'main', 'diario', 'vendor', 'siga', 'bundle']):
                log(f"  Baixando: {filename}")
                try:
                    js_content = page.evaluate(f"""
                        async () => {{
                            try {{
                                const r = await fetch('{src}');
                                return await r.text();
                            }} catch(e) {{
                                return '';
                            }}
                        }}
                    """)
                    if js_content:
                        # Buscar URLs de API
                        apis = set(re.findall(r'["\'](/api/v[12]/[a-zA-Z0-9_/?=&{}.%+-]+)["\']', js_content))
                        # Buscar URLs com frequencia/chamada/notas/faltas
                        freq_urls = set(re.findall(
                            r'["\']([^"\']*(?:frequen|chamada|presenc|attendance|falta)[^"\']*)["\']',
                            js_content, re.IGNORECASE))
                        # Buscar $.ajax / fetch patterns
                        ajax_patterns = re.findall(
                            r'(?:\$\.(?:ajax|get|post|getJSON)|fetch|axios\.(?:get|post))\s*\(\s*[`"\']([^`"\']+)[`"\']',
                            js_content)

                        if apis:
                            log(f"    API URLs ({len(apis)}):")
                            for a in sorted(apis)[:20]:
                                log(f"      {a}")
                                api_patterns_found.add(a)
                        if freq_urls:
                            log(f"    URLs frequencia ({len(freq_urls)}):")
                            for f in sorted(freq_urls)[:15]:
                                log(f"      {f}")
                                api_patterns_found.add(f)
                        if ajax_patterns:
                            log(f"    AJAX calls ({len(ajax_patterns)}):")
                            for a in sorted(set(ajax_patterns))[:15]:
                                log(f"      {a}")
                                api_patterns_found.add(a)

                        # Tamanho do chunk
                        log(f"    Size: {len(js_content):,} chars")
                except Exception as e:
                    log(f"    Erro: {str(e)[:80]}", "WARN")

        # Analisar scripts inline
        try:
            inline_apis = page.evaluate("""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script:not([src])'));
                    const allText = scripts.map(s => s.textContent).join('\\n');
                    const patterns = new Set();

                    // /api/v1/... patterns
                    const apiMatches = allText.match(/\\/api\\/v[12]\\/[a-zA-Z0-9_\\/?.&=]+/g);
                    if (apiMatches) apiMatches.forEach(m => patterns.add(m));

                    // frequencia/chamada patterns
                    const freqMatches = allText.match(/[a-zA-Z0-9_\\/]*(?:frequen|chamada|presenc|attendance|falta)[a-zA-Z0-9_\\/]*/gi);
                    if (freqMatches) freqMatches.forEach(m => patterns.add(m));

                    return [...patterns].slice(0, 30);
                }
            """)
            if inline_apis:
                log(f"  Padroes em scripts inline ({len(inline_apis)}):")
                for p in inline_apis:
                    log(f"    {p}")
                    api_patterns_found.add(p)
        except Exception as e:
            log(f"  Erro inline JS: {e}", "WARN")

        self.api_urls_from_js = list(api_patterns_found)
        return api_patterns_found

    def try_discovered_endpoints(self, page, api_patterns):
        """Tenta acessar endpoints descobertos na analise de JS."""
        log("Testando endpoints descobertos...", "HEAD")
        results = []

        # Filtrar apenas padroes que parecem URLs de API validas
        api_urls = [p for p in api_patterns if p.startswith('/api/')]

        # Adicionar variantes com diario_id
        if self.diario_id:
            extra = []
            for url in api_urls:
                if '{' in url:  # Template URL
                    filled = url.replace('{id}', str(self.diario_id))
                    filled = filled.replace('{diario_id}', str(self.diario_id))
                    filled = filled.replace('{pk}', str(self.diario_id))
                    extra.append(filled)
            api_urls.extend(extra)

        # Tambem testar endpoints especulativos baseados nos padroes do SIGA
        if self.diario_id:
            speculative = [
                f"/api/v1/diario/{self.diario_id}/frequencia/lista/",
                f"/api/v1/diario/{self.diario_id}/chamada/lista/",
                f"/api/v1/diario/{self.diario_id}/presenca/",
                f"/api/v1/diario/{self.diario_id}/presencas/",
                f"/api/v1/diario/{self.diario_id}/frequencia_alunos/",
                f"/api/v1/diario/{self.diario_id}/faltas_alunos/",
                f"/api/v1/diario_chamada/?diario={self.diario_id}",
                f"/api/v1/diario_frequencia/?diario={self.diario_id}",
                f"/api/v1/chamada/?diario={self.diario_id}",
                f"/api/v1/frequencia/?diario={self.diario_id}",
                f"/api/v1/presenca/?diario={self.diario_id}",
                f"/api/v1/diario/chamada/?diario={self.diario_id}",
                f"/api/v1/diario/frequencia/?diario={self.diario_id}",
                f"/api/v1/diario/presenca/?diario={self.diario_id}",
                f"/api/v1/diario/{self.diario_id}/alunos/frequencia/",
                f"/api/v1/frequencia_em_lote/?periodo=80",
                f"/api/v1/diario/frequencia_em_lote/?periodo=80",
                f"/api/v1/diario/frequencia_em_lote/?diario={self.diario_id}",
                f"/api/v1/reprovacao_por_faltas/?periodo=80",
                f"/api/v1/diario/reprovacao_por_faltas/?periodo=80",
                # Variantes com /lista/ que funcionam no SIGA
                f"/api/v1/diario/diario_aula/?diario={self.diario_id}&limit=5&situacao_aula=TODAS",
                f"/api/v1/diario/{self.diario_id}/aulas/",
                # Alunos do diario (sabemos que funciona - precisa busca param)
                f"/api/v1/diario/{self.diario_id}/alunos/lista/?busca=&apenas_ativos=true&ensino_superior=0",
            ]
            api_urls.extend(speculative)

        # Deduplicar
        api_urls = list(set(api_urls))

        for ep in api_urls:
            try:
                result = page.evaluate(f"""
                    async () => {{
                        try {{
                            const resp = await fetch('{ep}', {{
                                headers: {{
                                    'Accept': 'application/json',
                                    'X-Requested-With': 'XMLHttpRequest',
                                }},
                            }});
                            const ct = resp.headers.get('content-type') || '';
                            const status = resp.status;
                            const text = await resp.text();

                            let info = {{ url: '{ep}', status, ct, size: text.length }};

                            if (ct.includes('json') || text.trim().startsWith('[') || text.trim().startsWith('{{')) {{
                                try {{
                                    const data = JSON.parse(text);
                                    info.is_json = true;
                                    if (Array.isArray(data)) {{
                                        info.type = 'list';
                                        info.count = data.length;
                                        if (data.length > 0 && typeof data[0] === 'object') {{
                                            info.keys = Object.keys(data[0]).slice(0, 20);
                                            info.sample = JSON.stringify(data[0]).substring(0, 500);
                                        }}
                                    }} else if (typeof data === 'object') {{
                                        info.type = 'dict';
                                        info.keys = Object.keys(data).slice(0, 20);
                                        if (data.results) {{
                                            info.count = data.count || data.results.length;
                                            if (data.results.length > 0 && typeof data.results[0] === 'object') {{
                                                info.result_keys = Object.keys(data.results[0]).slice(0, 20);
                                                info.sample = JSON.stringify(data.results[0]).substring(0, 500);
                                            }}
                                        }}
                                    }}
                                }} catch(e) {{}}
                            }} else {{
                                info.is_html = text.includes('<!doctype') || text.includes('<html');
                            }}

                            return info;
                        }} catch(e) {{
                            return {{ url: '{ep}', error: e.message }};
                        }}
                    }}
                """)

                results.append(result)

                if result.get('error'):
                    pass  # Silencioso para erros
                elif result.get('is_json'):
                    count = result.get('count', '?')
                    keys = result.get('keys', result.get('result_keys', []))
                    log(f"  JSON: {ep} -> {count} regs, keys={keys[:8]}", "OK")
                    # Se tem frequencia/chamada no nome, destacar
                    if any(kw in ep.lower() for kw in ['frequen', 'chamada', 'presenc', 'falta']):
                        log(f"  *** ENDPOINT DE FREQUENCIA ENCONTRADO! ***", "OK")
                        log(f"  *** URL: {ep}", "OK")
                        if result.get('sample'):
                            log(f"  *** Amostra: {result['sample'][:200]}", "OK")
                elif not result.get('is_html'):
                    # Pode ser um erro ou outro formato
                    if result.get('status', 200) not in (200, 301, 302):
                        pass  # Silencioso
            except Exception:
                pass

        return results

    def phase_spa_navigation(self, page):
        """Fase 4: Navegar pelas paginas de frequencia do SPA."""
        log("FASE 4: Navegacao SPA + Interacao com UI", "HEAD")
        results = []

        # 4a. Navegar para lista de diarios
        r = self.navigate_and_capture(page, f"{SIGA_APP}/diarios/", "lista_diarios")
        results.append(r)

        # Buscar links para diarios individuais
        links = self.find_links_in_page(page)
        if links:
            log(f"  Links relevantes: {len(links)}")
            for link in links[:5]:
                log(f"    {link['tag']} {link.get('text','')[:40]} -> {link.get('href','')[:60]}")

        # 4b. Navegar para diario especifico
        if self.diario_id:
            r = self.navigate_and_capture(
                page, f"{SIGA_APP}/diario/{self.diario_id}/", "diario_especifico")
            results.append(r)

            # Buscar e clicar em abas dentro do diario
            tab_results = self.find_and_click_tabs(page, "diario_")
            results.extend(tab_results or [])

            # 4c. Navegar para paginas especificas de frequencia
            freq_pages = [
                (f"{SIGA_APP}/diario/{self.diario_id}/chamada/", "chamada"),
                (f"{SIGA_APP}/diario/{self.diario_id}/frequencia/", "frequencia"),
                (f"{SIGA_APP}/diario/{self.diario_id}/notas-faltas/", "notas_faltas"),
                (f"{SIGA_APP}/diario/{self.diario_id}/notas/", "notas"),
            ]

            for url, label in freq_pages:
                r = self.navigate_and_capture(page, url, label, wait_ms=8000)
                results.append(r)

                # Em cada pagina, buscar abas e clicar
                tab_results = self.find_and_click_tabs(page, f"{label}_")
                results.extend(tab_results or [])

                # Buscar selects/dropdowns e tentar interagir
                try:
                    selects = page.evaluate("""
                        () => {
                            const selects = document.querySelectorAll('select');
                            return Array.from(selects).map(s => ({
                                id: s.id,
                                name: s.name,
                                class: s.className,
                                options: Array.from(s.options).map(o => ({
                                    value: o.value,
                                    text: o.text.substring(0, 60),
                                })).slice(0, 20),
                            }));
                        }
                    """)
                    if selects:
                        log(f"  Selects encontrados: {len(selects)}")
                        for sel in selects:
                            log(f"    #{sel['id']} ({sel['name']}): {len(sel['options'])} opcoes")
                            if sel['options']:
                                log(f"      Opcoes: {[o['text'] for o in sel['options'][:5]]}")
                except Exception:
                    pass

        # 4d. Paginas de frequencia em lote / planilha
        batch_pages = [
            (f"{SIGA_APP}/diarios/frequencia_em_lote", "freq_em_lote"),
            (f"{SIGA_APP}/frequencia_em_lote/", "freq_em_lote_v2"),
            (f"{SIGA_APP}/planilha_notas_faltas/", "planilha_notas_faltas"),
            (f"{SIGA_APP}/planilha-notas-faltas/", "planilha_notas_faltas_v2"),
            (f"{SIGA_APP}/reprovacao_por_faltas/", "reprovacao_por_faltas"),
            (f"{SIGA_APP}/reprovacao-por-faltas/", "reprovacao_por_faltas_v2"),
        ]

        for url, label in batch_pages:
            r = self.navigate_and_capture(page, url, label)
            results.append(r)
            tab_results = self.find_and_click_tabs(page, f"{label}_")
            results.extend(tab_results or [])

        return results

    def phase_direct_fetch(self, page):
        """Fase extra: Tentar fetch direto com headers variados."""
        log("FASE EXTRA: Fetch direto com Accept headers variados", "HEAD")
        results = []

        if not self.diario_id:
            log("  Sem diario_id, pulando.", "WARN")
            return results

        # Tentar com Accept header diferente (text/html vs application/json)
        endpoints = [
            f"/api/v1/diario/{self.diario_id}/frequencia/",
            f"/api/v1/diario/{self.diario_id}/chamada/",
            f"/api/v1/diario/{self.diario_id}/notas/",
            f"/api/v1/diario/{self.diario_id}/notas_faltas/",
        ]

        accept_headers = [
            'application/json',
            'application/json, text/plain, */*',
            '*/*',
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        ]

        for ep in endpoints:
            for accept in accept_headers:
                try:
                    result = page.evaluate(f"""
                        async () => {{
                            try {{
                                const csrfCookie = document.cookie.split(';')
                                    .map(c => c.trim())
                                    .find(c => c.startsWith('csrftoken='));
                                const csrf = csrfCookie ? csrfCookie.split('=')[1] : '';

                                const resp = await fetch('{ep}', {{
                                    headers: {{
                                        'Accept': '{accept}',
                                        'X-Requested-With': 'XMLHttpRequest',
                                        'X-CSRFToken': csrf,
                                    }},
                                    credentials: 'include',
                                }});
                                const ct = resp.headers.get('content-type') || '';
                                const text = await resp.text();

                                return {{
                                    url: '{ep}',
                                    accept: '{accept}',
                                    status: resp.status,
                                    ct: ct,
                                    size: text.length,
                                    is_json: ct.includes('json'),
                                    is_html: text.includes('<!doctype') || text.includes('<html'),
                                    preview: text.substring(0, 300),
                                }};
                            }} catch(e) {{
                                return {{ url: '{ep}', accept: '{accept}', error: e.message }};
                            }}
                        }}
                    """)
                    results.append(result)

                    if result.get('is_json'):
                        log(f"  JSON com Accept='{accept}': {ep}", "OK")
                    elif not result.get('is_html') and not result.get('error'):
                        log(f"  Nao-HTML: {ep} (Accept='{accept}', CT={result.get('ct','')})")
                except Exception:
                    pass

        return results

    def run(self):
        """Executa o interceptador completo."""
        print("=" * 70)
        print("INTERCEPTADOR DE FREQUENCIA v3 - Agente IOTA")
        print(f"Inicio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 70)

        inicio = time.time()

        # Validar credenciais
        if not CONFIG["senha"]:
            log("SIGA_SENHA nao definida!", "ERR")
            log("  export SIGA_SENHA='sua_senha_aqui'")
            log("Executando em MODO DRY-RUN (sem autenticacao)...", "WARN")
            self.dry_run = True

        all_results = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'dry_run' if self.dry_run else 'live',
            'config': {
                'instituicao': CONFIG['instituicao'],
                'login': CONFIG['login'],
                'has_senha': bool(CONFIG['senha']),
            },
        }

        if self.dry_run:
            log("Modo dry-run: mostrando o que SERIA executado.", "WARN")
            log("Fases planejadas:")
            log("  1. Login via Playwright (siga.activesoft.com.br/login/)")
            log("  2. Injetar XHR/fetch interceptor (window.__xhrCalls)")
            log("  3. Obter diario de teste via fetch")
            log("  4. Navegar em /diarios/, /diario/{id}/chamada/, /diario/{id}/frequencia/")
            log("  5. Clicar em abas dentro do diario")
            log("  6. Extrair tabelas do DOM")
            log("  7. Analisar chunks JS carregados")
            log("  8. Testar endpoints descobertos")
            log("  9. Salvar resultados em JSON")

            all_results['phases'] = {
                'login': 'skipped (dry_run)',
                'interceptor': 'XHR/fetch/jQuery hooks would be injected',
                'navigation': [
                    '/diarios/',
                    '/diario/{id}/',
                    '/diario/{id}/chamada/',
                    '/diario/{id}/frequencia/',
                    '/diario/{id}/notas-faltas/',
                    '/diarios/frequencia_em_lote',
                    '/planilha_notas_faltas/',
                    '/reprovacao_por_faltas/',
                ],
                'note': 'Execute com SIGA_SENHA definida para resultado real.',
            }

            output_path = SCRIPT_DIR / "frequencia_interceptacao_v3.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
            log(f"Resultados (dry-run) salvos em: {output_path}")
            return all_results

        # ===== EXECUCAO REAL =====
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled'],
            )
            self.context = browser.new_context(
                viewport={'width': 1400, 'height': 900},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            )
            page = self.context.new_page()
            self.page = page

            # === FASE 1: Login ===
            log("FASE 1: Login", "HEAD")
            try:
                self.login(page, UNIDADES[0]['selector'])
                all_results['login'] = {'ok': True, 'url': page.url}
            except Exception as e:
                log(f"Login falhou: {e}", "ERR")
                all_results['login'] = {'ok': False, 'error': str(e)}
                browser.close()
                return all_results

            # === FASE 2: Injetar interceptor ANTES de qualquer navegacao ===
            log("FASE 2: Injetando interceptor XHR/fetch/jQuery", "HEAD")
            try:
                # add_init_script roda em CADA nova pagina/navegacao
                self.context.add_init_script(XHR_FETCH_INTERCEPTOR_JS)
                # Tambem injetar na pagina atual
                page.evaluate(XHR_FETCH_INTERCEPTOR_JS)
                log("Interceptor injetado via add_init_script + evaluate", "OK")
                all_results['interceptor'] = {'ok': True}
            except Exception as e:
                log(f"Erro injetando interceptor: {e}", "WARN")
                all_results['interceptor'] = {'ok': False, 'error': str(e)}

            # Registrar listeners de rede do Playwright
            page.on("request", self._on_request)
            page.on("response", self._on_response)
            log("Listeners page.on(request/response) registrados", "OK")

            # === FASE 3: Obter diario de teste ===
            log("FASE 3: Obter diario de teste", "HEAD")
            diario_info = self.get_diario_test(page, periodo=UNIDADES[0]['periodo'])
            all_results['diario_teste'] = diario_info

            # === FASE 4: Navegacao SPA ===
            nav_results = self.phase_spa_navigation(page)
            all_results['navigation_results'] = nav_results

            # === FASE 5: Extrair DOM tables (ja feito durante navegacao) ===
            log("FASE 5: Resumo de tabelas DOM extraidas", "HEAD")
            for label, tables in self.dom_tables.items():
                for t in tables:
                    if t['rows'] > 1:
                        log(f"  [{label}] Table #{t['index']}: {t['rows']}x{t['cols']}")
                        if t.get('data') and len(t['data']) > 0:
                            log(f"    Header: {t['data'][0][:8]}")
                            if len(t['data']) > 1:
                                log(f"    Row 1: {t['data'][1][:8]}")

            # === FASE 6: Analisar JS chunks ===
            api_patterns = self.analyze_js_chunks(page)
            all_results['api_patterns_from_js'] = list(api_patterns)

            # === FASE 7: Testar endpoints descobertos ===
            endpoint_results = self.try_discovered_endpoints(page, api_patterns)
            all_results['discovered_endpoints'] = endpoint_results

            # === FASE EXTRA: Fetch direto com headers variados ===
            direct_results = self.phase_direct_fetch(page)
            all_results['direct_fetch_results'] = direct_results

            # === FASE 8: Coletar todos os interceptados finais ===
            log("FASE 8: Coletando dados interceptados finais", "HEAD")
            final_intercepted = self.collect_xhr_calls(page)
            log(f"  XHR calls: {len(final_intercepted['xhr'])}")
            log(f"  Fetch calls: {len(final_intercepted['fetch'])}")
            log(f"  jQuery AJAX calls: {len(final_intercepted['jquery'])}")
            all_results['intercepted_calls'] = final_intercepted

            # === FASE 9: Salvar tudo ===
            log("FASE 9: Salvando resultados", "HEAD")

            all_results['captured_responses'] = self.captured_responses
            all_results['captured_requests_count'] = len(self.captured_requests)
            all_results['js_chunks_loaded'] = self.js_chunks_loaded
            all_results['dom_tables'] = {
                label: [
                    {'index': t['index'], 'rows': t['rows'], 'cols': t['cols'],
                     'data': t.get('data', [])[:30], 'classes': t.get('classes', ''),
                     'id': t.get('id', '')}
                    for t in tables
                ]
                for label, tables in self.dom_tables.items()
            }

            browser.close()

        # Salvar JSON
        output_path = SCRIPT_DIR / "frequencia_interceptacao_v3.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
        log(f"Resultados salvos: {output_path}", "OK")

        duracao = time.time() - inicio

        # === RELATORIO FINAL ===
        print("\n" + "=" * 70)
        print("RELATORIO FINAL - INTERCEPTADOR v3")
        print("=" * 70)

        # Resumo de rede
        total_responses = len(self.captured_responses)
        json_responses = [r for r in self.captured_responses if r.get('is_json')]
        siga_responses = [r for r in self.captured_responses if 'siga' in r.get('url', '')]

        print(f"\n  Total respostas de rede: {total_responses}")
        print(f"  Respostas JSON: {len(json_responses)}")
        print(f"  Respostas SIGA: {len(siga_responses)}")
        print(f"  JS chunks carregados: {len(self.js_chunks_loaded)}")

        # JSON SIGA endpoints
        json_siga = [r for r in self.captured_responses if r.get('is_json') and 'siga' in r.get('url', '')]
        if json_siga:
            print(f"\n  ENDPOINTS SIGA JSON ({len(json_siga)}):")
            for r in json_siga:
                path = r['url'].replace(SIGA_APP, '').replace(SIGA_LOGIN, '')
                count = r.get('json_count', '?')
                keys = r.get('json_keys', r.get('json_result_keys', []))
                print(f"    [{r['method']}] {path}: {count} regs -> {keys[:6]}")

        # Intercepted JS calls
        if final_intercepted:
            total_js = (len(final_intercepted['xhr']) +
                        len(final_intercepted['fetch']) +
                        len(final_intercepted['jquery']))
            print(f"\n  XHR/fetch/jQuery interceptados: {total_js}")

            # Filtrar chamadas relevantes (frequencia/chamada)
            all_js_calls = (
                final_intercepted['xhr'] +
                final_intercepted['fetch'] +
                final_intercepted['jquery']
            )
            freq_calls = [c for c in all_js_calls
                          if any(kw in (c.get('url', '') or '').lower()
                                 for kw in ['frequen', 'chamada', 'presenc', 'falta'])]
            if freq_calls:
                print(f"\n  *** CHAMADAS DE FREQUENCIA INTERCEPTADAS ({len(freq_calls)})! ***")
                for c in freq_calls:
                    print(f"    [{c.get('method','?')}] {c.get('url','?')}")
                    if c.get('isJson'):
                        print(f"      JSON! count={c.get('jsonCount','?')}, keys={c.get('jsonKeys', c.get('jsonResultKeys', []))[:8]}")
            else:
                print(f"\n  Nenhuma chamada de frequencia interceptada nas {total_js} chamadas JS")

        # Tabelas DOM
        total_tables = sum(len(t) for t in self.dom_tables.values())
        tables_with_data = sum(
            1 for tables in self.dom_tables.values()
            for t in tables if t.get('rows', 0) > 1
        )
        print(f"\n  Tabelas DOM extraidas: {total_tables} (com dados: {tables_with_data})")
        for label, tables in self.dom_tables.items():
            for t in tables:
                if t.get('rows', 0) > 1:
                    print(f"    [{label}] {t['rows']}x{t['cols']}")

        # Endpoints descobertos nos JS
        json_discovered = [e for e in endpoint_results if e.get('is_json')]
        freq_discovered = [e for e in json_discovered
                           if any(kw in e.get('url', '').lower()
                                  for kw in ['frequen', 'chamada', 'presenc', 'falta'])]

        if freq_discovered:
            print(f"\n  *** ENDPOINTS DE FREQUENCIA DESCOBERTOS ({len(freq_discovered)})! ***")
            for e in freq_discovered:
                print(f"    {e['url']}: {e.get('count','?')} regs")
                print(f"      Keys: {e.get('keys', e.get('result_keys', []))}")
        elif json_discovered:
            print(f"\n  Endpoints JSON descobertos (nenhum de frequencia): {len(json_discovered)}")
            for e in json_discovered[:10]:
                print(f"    {e['url']}: {e.get('count','?')} regs")

        # Recomendacao
        print(f"\n  {'=' * 50}")
        print(f"  RECOMENDACAO:")
        if freq_discovered or freq_calls:
            print(f"  -> ENDPOINTS DE FREQUENCIA ENCONTRADOS!")
            print(f"  -> Proximo passo: criar extrair_frequencia_siga.py")
        elif tables_with_data > 0:
            print(f"  -> Nenhum endpoint REST de frequencia encontrado.")
            print(f"  -> MAS tabelas DOM com dados foram extraidas!")
            print(f"  -> Proximo passo: criar scrape_frequencia_siga.py (DOM scraping)")
        else:
            print(f"  -> Nenhum endpoint REST nem tabela DOM de frequencia.")
            print(f"  -> O SPA pode usar WebSocket ou renderizacao server-side.")
            print(f"  -> Proximo passo: investigar WebSockets ou usar diario_aula API (campo frequencia)")
        print(f"  {'=' * 50}")

        print(f"\n  Tempo total: {duracao:.1f}s")
        print(f"  Resultados em: {output_path}")
        print("=" * 70)

        return all_results


def main():
    interceptor = SIGAInterceptorV3()
    results = interceptor.run()
    return results


if __name__ == "__main__":
    main()
