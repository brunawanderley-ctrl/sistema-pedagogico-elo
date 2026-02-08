#!/usr/bin/env python3
"""
EXTRAÇÃO DE OCORRÊNCIAS DO SIGA - Colégio ELO 2026

Endpoint descoberto: /api/v1/aluno_observacao/
- Total histórico: 166.226 registros
- Filtro data_in: limita por período

Fluxo:
1. Login via Playwright (headless) - captura cookies
2. Fetch via browser (contexto autenticado do SPA)
3. Paginação automática (limit/offset)
4. Salva em power_bi/fato_Ocorrencias.csv
"""

import json
import csv
import os
import re
from datetime import datetime
from pathlib import Path
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

# Normalização de séries (SIGA → canônico)
SERIE_NORMALIZACAO = {
    '6º ANO': '6º Ano',
    '7º ANO': '7º Ano',
    '8º ANO': '8º Ano',
    '9º ANO': '9º Ano',
    '1º Ano Médio': '1ª Série',
    '2º Ano Médio': '2ª Série',
    '3º Ano Médio': '3ª Série',
    '1ª Série EM': '1ª Série',
    '2ª Série EM': '2ª Série',
    '3ª Série EM': '3ª Série',
}

# Classificação de tipos: categoria + gravidade
# Baseado nos 58 tipos extraídos do SIGA em 08/02/2026
TIPO_CLASSIFICACAO = {
    # DISCIPLINAR - Leve
    'ATRASO NA ENTRADA': ('Disciplinar', 'Leve'),
    'USO DO CELULAR NA ESCOLA': ('Disciplinar', 'Leve'),
    'FARDAMENTO INCOMPLETO': ('Disciplinar', 'Leve'),
    # DISCIPLINAR - Media
    'FORA DE SALA EM HORÁRIO DE AULA': ('Disciplinar', 'Media'),
    'Não realizou atividade': ('Disciplinar', 'Media'),
    'NÃO REALIZOU A TAREFA': ('Disciplinar', 'Media'),
    # DISCIPLINAR - Grave
    'INDISCIPLINA': ('Disciplinar', 'Grave'),
    'Indisciplina': ('Disciplinar', 'Grave'),
    # PEDAGÓGICO
    'Atendimento pedagógico': ('Pedagogico', 'Leve'),
    'REL- Acomp. pedagógico mensal': ('Pedagogico', 'Leve'),
    'Atendimento - COORDENAÇÃO X RESPONSÁVEIS': ('Pedagogico', 'Leve'),
    'Plantão Pedagógico': ('Pedagogico', 'Leve'),
    'Psicológa': ('Pedagogico', 'Media'),
    'Falta Justificada (Atestado Médico)': ('Pedagogico', 'Leve'),
    'Doença - OBS INFO.': ('Pedagogico', 'Leve'),
    'Esportes -  Pedagógico': ('Pedagogico', 'Leve'),
    'Pais': ('Pedagogico', 'Leve'),
    # ADMINISTRATIVO (não impacta ABC)
    'Cobrança': ('Administrativo', 'Leve'),
    'Observação sobre Matricula': ('Administrativo', 'Leve'),
    'Observação sobre Documentação': ('Administrativo', 'Leve'),
    'Observação sobre Material Didático': ('Administrativo', 'Leve'),
    'SOLICITAÇÃO DE TRANSF - VIA REQUERIMENTO': ('Administrativo', 'Leve'),
    'AUTORIZAÇÃO DE SAÍDA': ('Administrativo', 'Leve'),
    'AUTORIZAÇÃO- SAÍDA ANTECIPADA': ('Administrativo', 'Leve'),
    'Esportes -  Financeiro': ('Administrativo', 'Leve'),
    'Relacionamento - Customer Success': ('Administrativo', 'Leve'),
    'Desconto': ('Administrativo', 'Leve'),
    'PENDÊNCIAS DOCUMENTAÇÃO': ('Administrativo', 'Leve'),
    'DADOS CADASTRAIS': ('Administrativo', 'Leve'),
    'TELEFONES': ('Administrativo', 'Leve'),
    'AFASTAMENTO EXTERNO': ('Administrativo', 'Leve'),
    'ENTREGA DE LAUDO NEUROPSICOLÓGICO': ('Administrativo', 'Leve'),
}

# Padrões para tipos não listados explicitamente
TIPO_PATTERNS_ADMIN = [
    'MATRÍCULA', 'CANCEL', 'RECEP', 'PGTO', 'CASHBACK', 'CONTRATO',
    'REL-', 'REL -', 'LOJA', 'ENTURM', 'PAIXÃO',
]


def classificar_tipo(tipo_nome):
    """Retorna (categoria, gravidade) para um tipo de ocorrência."""
    if not tipo_nome:
        return 'Administrativo', 'Leve'

    # Busca exata
    if tipo_nome in TIPO_CLASSIFICACAO:
        return TIPO_CLASSIFICACAO[tipo_nome]

    # Padrões administrativos
    tipo_upper = tipo_nome.upper()
    for pattern in TIPO_PATTERNS_ADMIN:
        if pattern in tipo_upper:
            return 'Administrativo', 'Leve'

    # Padrões disciplinares por keyword
    tipo_lower = tipo_nome.lower()
    disciplinar_grave = ['agressao', 'bullying', 'violencia', 'vandalismo', 'drogas', 'furto']
    disciplinar_media = ['indisciplina', 'desobediencia', 'desrespeito', 'evasao', 'fora de sala']
    disciplinar_leve = ['atraso', 'celular', 'fardamento', 'uniforme']

    for kw in disciplinar_grave:
        if kw in tipo_lower:
            return 'Disciplinar', 'Grave'
    for kw in disciplinar_media:
        if kw in tipo_lower:
            return 'Disciplinar', 'Media'
    for kw in disciplinar_leve:
        if kw in tipo_lower:
            return 'Disciplinar', 'Leve'

    # Default: Outros → Administrativo
    if tipo_nome == 'Outros':
        return 'Administrativo', 'Leve'

    return 'Administrativo', 'Leve'


CSV_FIELDNAMES = [
    'ocorrencia_id', 'aluno_id', 'aluno_nome', 'data', 'unidade', 'serie',
    'turma', 'tipo', 'categoria', 'gravidade', 'descricao', 'responsavel',
    'providencia', 'registrado_por', 'data_registro'
]


def extrair_serie_da_turma(turma_nome):
    """Extrai e normaliza a série do nome da turma SIGA."""
    if not turma_nome:
        return ''

    # Padrões comuns: "1- BV - Ensino Fundamental II - Unidade Boa Viagem / 6º Ano / 2026 / 6º Ano - Turma A"
    # Ou: "1- BV - Ensino Médio - Unidade Boa Viagem / 1ª Série / 2026 / 1ª Série EM"
    match = re.search(r'/\s*((?:\d+[ºª]\s*(?:Ano|Série)[^/]*))\s*/', turma_nome)
    if match:
        serie_raw = match.group(1).strip()
        return SERIE_NORMALIZACAO.get(serie_raw, serie_raw)

    # Fallback: buscar padrão direto
    for pattern, canonical in SERIE_NORMALIZACAO.items():
        if pattern.lower() in turma_nome.lower():
            return canonical

    return ''


def extrair_unidade_da_turma(turma_nome):
    """Extrai código da unidade do nome da turma."""
    if not turma_nome:
        return ''

    unidade_map = {
        'Boa Viagem': 'BV',
        'Candeias': 'CD',
        'Janga': 'JG',
        'Cordeiro': 'CDR',
    }

    for nome, codigo in unidade_map.items():
        if nome.lower() in turma_nome.lower():
            return codigo

    # Fallback: buscar sigla
    match = re.search(r'- (BV|CD|JG|CDR) -', turma_nome)
    if match:
        return match.group(1)

    return ''


def main():
    print("=" * 70)
    print("EXTRAÇÃO DE OCORRÊNCIAS - SIGA → fato_Ocorrencias.csv")
    print(f"Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    inicio = datetime.now()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1400, 'height': 900})
        page = context.new_page()

        # Unidades a extrair (seletores exatos da tela de login)
        UNIDADES = [
            {"nome": "BV", "selector": '1 - BV (Boa Viagem)', "codigo": "BV"},
            {"nome": "CD", "selector": '2 - CD (Jaboatão)', "codigo": "CD"},
            {"nome": "JG", "selector": '3 - JG (Paulista)', "codigo": "JG"},
            {"nome": "CDR", "selector": '4 - CDR (Cordeiro)', "codigo": "CDR"},
        ]

        def login_unidade(pg, selector):
            """Faz login no SIGA selecionando uma unidade específica."""
            pg.goto(f"{SIGA_LOGIN}/login/")
            pg.wait_for_timeout(2000)
            pg.fill('#codigoInstituicao', CONFIG["instituicao"])
            pg.fill('#id_login', CONFIG["login"])
            pg.fill('#id_senha', CONFIG["senha"])
            pg.click('button:has-text("ENTRAR")')
            pg.wait_for_timeout(4000)
            pg.click(f'text="{selector}"', timeout=5000)
            pg.wait_for_timeout(5000)
            pg.goto(f"{SIGA_APP}/ocorrencias_alunos/", timeout=30000)
            pg.wait_for_timeout(5000)

        # ===== FASE 1: Login inicial + estrutura =====
        print("\n--- LOGIN ---")
        login_unidade(page, UNIDADES[0]["selector"])
        print(f"  Login OK: {page.url}")

        amostra = page.evaluate("""
            async () => {
                const resp = await fetch('/api/v1/aluno_observacao/?limit=1&offset=0&maximoPorPagina=1', {
                    headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                });
                return await resp.json();
            }
        """)
        if amostra.get('results'):
            print(f"  Campos: {list(amostra['results'][0].keys())}")

        # ===== FASE 2: Extrair por unidade =====
        PAGE_SIZE = 200
        DATE_FILTER = "data_inicial_ocorrencia=01%2F01%2F2026"
        all_records = []

        for idx, unidade in enumerate(UNIDADES):
            print(f"\n--- Unidade {unidade['nome']} ---")

            # Re-login para cada unidade (exceto a primeira)
            if idx > 0:
                try:
                    login_unidade(page, unidade["selector"])
                except Exception as e:
                    print(f"  FALHA login: {str(e)[:60]}. Pulando unidade.")
                    continue

            # Contar registros desta unidade
            count_batch = page.evaluate(f"""
                async () => {{
                    const resp = await fetch(
                        '/api/v1/aluno_observacao/?limit=1&offset=0&maximoPorPagina=1&{DATE_FILTER}',
                        {{ headers: {{ 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }} }}
                    );
                    return await resp.json();
                }}
            """)
            total_unidade = count_batch.get('count', 0)
            print(f"  Total 2026: {total_unidade}")

            # Extrair paginado
            offset = 0
            count_unidade = 0
            while offset < total_unidade:
                batch = page.evaluate(f"""
                    async () => {{
                        const resp = await fetch(
                            '/api/v1/aluno_observacao/?limit={PAGE_SIZE}&offset={offset}&maximoPorPagina={PAGE_SIZE}&ordering=-data_ocorrencia&{DATE_FILTER}',
                            {{ headers: {{ 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }} }}
                        );
                        return await resp.json();
                    }}
                """)

                results = batch.get('results', [])
                if not results:
                    break

                # Marcar unidade forçada caso turma não identifique
                for rec in results:
                    rec['_unidade_login'] = unidade['codigo']

                all_records.extend(results)
                count_unidade += len(results)
                offset += PAGE_SIZE

                if count_unidade % 500 == 0:
                    print(f"    {count_unidade}/{total_unidade} extraídos...")

            print(f"  Extraídos: {count_unidade}")

        print(f"\n  Total extraído: {len(all_records)} registros")

        browser.close()

    # ===== FASE 3: Processar e filtrar =====
    print("\n--- FASE 3: Processando dados ---")

    # Filtrar apenas 2026
    records_2026 = []
    for rec in all_records:
        data = rec.get('data_ocorrencia', '') or ''
        if data.startswith('2026'):
            records_2026.append(rec)

    print(f"  Registros 2026: {len(records_2026)}")

    # Formatar para CSV
    # Campos da API: id, aluno_nome, aluno, tipo_ocorrencia, tipo_ocorrencia_nome,
    #   tipo_ocorrencia_novo, nome_turma_completo, usuario_registro, usuario_registro_nome,
    #   usuario_liberacao, usuario_liberacao_nome, professor_registro, professor_registro_nome,
    #   nome (=observação), impedimento, data_ocorrencia, data_liberacao, observacao_liberacao,
    #   data_inclusao, exibir_internet, data_inicial_atestado, data_final_atestado
    csv_rows = []
    for rec in records_2026:
        turma_nome = rec.get('nome_turma_completo', '') or ''
        tipo = rec.get('tipo_ocorrencia_nome', '') or ''
        # "nome" é na verdade a observação/descrição
        observacao = (rec.get('nome', '') or '').replace('\n', ' | ').replace('\r', '')
        # observacao_liberacao pode ser a providência/encaminhamento
        providencia = (rec.get('observacao_liberacao', '') or '').replace('\n', ' | ').replace('\r', '')
        data_ocorr = rec.get('data_ocorrencia', '') or ''

        # Normalizar data
        if 'T' in data_ocorr:
            data_ocorr = data_ocorr[:10]

        # Responsável: quem registrou (usuario ou professor)
        responsavel = (rec.get('usuario_registro_nome', '') or
                       rec.get('professor_registro_nome', '') or '')

        categoria, gravidade = classificar_tipo(tipo)

        row = {
            'ocorrencia_id': rec.get('id', ''),
            'aluno_id': rec.get('aluno', ''),
            'aluno_nome': rec.get('aluno_nome', ''),
            'data': data_ocorr,
            'unidade': extrair_unidade_da_turma(turma_nome) or rec.get('_unidade_login', ''),
            'serie': extrair_serie_da_turma(turma_nome),
            'turma': turma_nome,
            'tipo': tipo,
            'categoria': categoria,
            'gravidade': gravidade,
            'descricao': observacao[:500],
            'responsavel': responsavel,
            'providencia': providencia[:500],
            'registrado_por': 'siga_api',
            'data_registro': (rec.get('data_inclusao', '') or data_ocorr)[:16],
        }
        csv_rows.append(row)

    # ===== FASE 4: Salvar =====
    print("\n--- FASE 4: Salvando ---")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # CSV
    csv_path = OUTPUT_DIR / 'fato_Ocorrencias.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"  fato_Ocorrencias.csv: {len(csv_rows)} registros")

    # Backup JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    json_path = SCRIPT_DIR / f"backup_ocorrencias_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_extraido': len(all_records),
            'filtrado_2026': len(records_2026),
            'salvo_csv': len(csv_rows),
            'registros': all_records,  # Backup completo
        }, f, indent=2, ensure_ascii=False, default=str)

    print(f"  Backup JSON: {json_path.name}")

    # Estatísticas
    duracao = (datetime.now() - inicio).total_seconds()

    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)

    # Por unidade
    unidades = {}
    for row in csv_rows:
        un = row['unidade'] or 'Desconhecida'
        unidades[un] = unidades.get(un, 0) + 1
    print("\n  Por unidade:")
    for un, count in sorted(unidades.items()):
        print(f"    {un}: {count}")

    # Por tipo
    tipos = {}
    for row in csv_rows:
        tp = row['tipo'] or 'Sem tipo'
        tipos[tp] = tipos.get(tp, 0) + 1
    print("\n  Top tipos:")
    for tp, count in sorted(tipos.items(), key=lambda x: -x[1])[:10]:
        print(f"    {tp}: {count}")

    # Por categoria
    categorias = {}
    for row in csv_rows:
        cat = row['categoria']
        categorias[cat] = categorias.get(cat, 0) + 1
    print("\n  Por categoria:")
    for cat, count in sorted(categorias.items()):
        print(f"    {cat}: {count}")

    # Por gravidade
    gravidades = {}
    for row in csv_rows:
        g = row['gravidade']
        gravidades[g] = gravidades.get(g, 0) + 1
    print("\n  Por gravidade:")
    for g, count in sorted(gravidades.items()):
        print(f"    {g}: {count}")

    # Disciplinares por gravidade
    disc_grav = {}
    for row in csv_rows:
        if row['categoria'] == 'Disciplinar':
            g = row['gravidade']
            disc_grav[g] = disc_grav.get(g, 0) + 1
    if disc_grav:
        print("\n  Disciplinares por gravidade:")
        for g, count in sorted(disc_grav.items()):
            print(f"    {g}: {count}")

    print(f"\n  Tempo: {duracao:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()
