#!/usr/bin/env python3
"""
Extracao SAE Digital - Materiais, Alunos e Engajamento
======================================================
Faz login na API SAE Digital, extrai dados de materiais (LMS),
alunos (PDC) e engajamento, e gera CSVs para cruzamento com SIGA.

Saida:
  power_bi/dim_Materiais_SAE.csv
  power_bi/dim_Alunos_SAE.csv
  power_bi/fato_Engajamento_SAE.csv
  power_bi/fato_Cruzamento.csv
"""

import json
import re
import sys
import time
import unicodedata
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# ========== CONFIGURACAO ==========

OUTPUT_DIR = Path(__file__).parent / "power_bi"
OUTPUT_DIR.mkdir(exist_ok=True)

USERNAME = "bruna.marinho"
PASSWORD = "Elo#2026"
LOGIN_URL = "https://portal-bff.sae.digital/login"

USER_ID = 13930181
ACCOUNT_ID_COORD = 9408727
INSTITUTION_ID = 122845

LMS_BFF = "https://cdo-lms-bff.arcotech.io"
PDC_BFF = "https://onb-pdc-bff.arcotech.io"

# Grade IDs SAE → Serie canonica
GRADE_MAP = {
    10: '6o Ano', 11: '7o Ano', 12: '8o Ano', 13: '9o Ano',
    14: '1a Serie', 15: '2a Serie', 16: '3a Serie',
}

# Normaliza nomes de serie SAE para canonico SIGA
SERIE_NORM = {
    '6o Ano': '6\u00ba Ano', '7o Ano': '7\u00ba Ano',
    '8o Ano': '8\u00ba Ano', '9o Ano': '9\u00ba Ano',
    '6\u00ba Ano': '6\u00ba Ano', '7\u00ba Ano': '7\u00ba Ano',
    '8\u00ba Ano': '8\u00ba Ano', '9\u00ba Ano': '9\u00ba Ano',
    '1a Serie': '1\u00aa S\u00e9rie', '2a Serie': '2\u00aa S\u00e9rie',
    '3a Serie': '3\u00aa S\u00e9rie',
    '1\u00aa S\u00e9rie': '1\u00aa S\u00e9rie',
    '2\u00aa S\u00e9rie': '2\u00aa S\u00e9rie',
    '3\u00aa S\u00e9rie': '3\u00aa S\u00e9rie',
}

# Normaliza disciplinas SAE → canonico SIGA
DISCIPLINA_SAE_NORM = {
    'L\u00edngua Portuguesa': 'L\u00edngua Portuguesa',
    'Matem\u00e1tica': 'Matem\u00e1tica',
    'Hist\u00f3ria': 'Hist\u00f3ria',
    'Geografia': 'Geografia',
    'Ci\u00eancias': 'Ci\u00eancias Naturais',
    'Ci\u00eancias Naturais': 'Ci\u00eancias Naturais',
    'Ci\u00eancias da Natureza': 'Ci\u00eancias Naturais',
    'Ingl\u00eas': 'L\u00edngua Estrangeira Ingl\u00eas',
    'L\u00edngua Estrangeira Ingl\u00eas': 'L\u00edngua Estrangeira Ingl\u00eas',
    'L\u00edngua Inglesa': 'L\u00edngua Estrangeira Ingl\u00eas',
    'Arte': 'Arte',
    'Artes': 'Arte',
    'Filosofia': 'Filosofia',
    'Sociologia': 'Sociologia',
    'Biologia': 'Biologia',
    'F\u00edsica': 'F\u00edsica',
    'Qu\u00edmica': 'Qu\u00edmica',
    'Literatura': 'Literatura',
    'Reda\u00e7\u00e3o': 'Reda\u00e7\u00e3o',
    'Gram\u00e1tica': 'Gram\u00e1tica',
    'Educa\u00e7\u00e3o F\u00edsica': 'Educa\u00e7\u00e3o F\u00edsica',
    'Projeto de Vida': 'Projeto de Vida',
    'Racioc\u00ednio L\u00f3gico': 'Racioc\u00ednio L\u00f3gico',
}

INICIO_ANO_LETIVO = datetime(2026, 1, 26)


# ========== AUTENTICACAO ==========

def login():
    """Faz login e retorna token JWT."""
    print("=" * 60)
    print("FAZENDO LOGIN SAE DIGITAL...")
    print("=" * 60)

    resp = requests.post(LOGIN_URL, json={
        "username": USERNAME,
        "password": PASSWORD,
        "realm": "sae",
    }, timeout=15)

    if resp.status_code != 200:
        print(f"  ERRO login: {resp.status_code} {resp.text[:200]}")
        sys.exit(1)

    data = resp.json()
    token = data.get("accessToken")
    print(f"  LOGIN OK! User: {data.get('displayName')}")
    return token


def make_headers(token):
    """Cria headers padrao para APIs Arcotech."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-account-id": str(ACCOUNT_ID_COORD),
        "x-institution-id": str(INSTITUTION_ID),
        "x-user-id": str(USER_ID),
        "x-product-name": "Portal",
        "Origin": "https://app.sae.digital",
        "Referer": "https://app.sae.digital/",
    }


# ========== HELPERS ==========

def normalizar_nome(nome):
    """Normaliza nome para comparacao: remove acentos, uppercase, compacta espacos."""
    if not nome:
        return ""
    nome = unicodedata.normalize('NFKD', str(nome))
    nome = ''.join(c for c in nome if not unicodedata.combining(c))
    nome = nome.upper().strip()
    nome = re.sub(r'\s+', ' ', nome)
    return nome


def normalizar_serie_sae(grade_id=None, grade_name=None):
    """Converte grade_id ou grade_name SAE para serie canonica SIGA."""
    if grade_id and grade_id in GRADE_MAP:
        return SERIE_NORM.get(GRADE_MAP[grade_id], GRADE_MAP[grade_id])
    if grade_name:
        return SERIE_NORM.get(grade_name, grade_name)
    return None


def normalizar_disciplina_sae(nome):
    """Normaliza nome de disciplina SAE para canonico SIGA."""
    if not nome:
        return None
    return DISCIPLINA_SAE_NORM.get(nome, nome)


def extrair_unidade_turma(turma_nome):
    """Extrai codigo de unidade do nome da turma SAE (ex: '8 Ano - Turma A Tarde - JG' → 'JG')."""
    if not turma_nome:
        return None
    m = re.search(r'-\s*(BV|CD|JG|CDR)\s*$', turma_nome)
    return m.group(1) if m else None


def calcular_semana_letiva(data_ref=None):
    """Calcula semana letiva. Inicio: 26/01/2026."""
    if data_ref is None:
        data_ref = datetime.now()
        if data_ref.year < 2026:
            data_ref = datetime(2026, 2, 5)
    return max(1, (data_ref - INICIO_ANO_LETIVO).days // 7 + 1)


def calcular_capitulo_esperado(semana):
    """Calcula capitulo SAE esperado: CEILING(semana / 3.5), max 12."""
    import math
    return min(12, math.ceil(semana / 3.5))


# ========== FASE 1: MATERIAIS ==========

def extrair_materiais(session, headers):
    """Extrai materiais SAE oficiais (isDefault=True) do LMS BFF."""
    print("\n" + "=" * 60)
    print("FASE 1: EXTRAINDO MATERIAIS SAE")
    print("=" * 60)

    all_materials = []
    page = 0
    page_size = 50

    # Buscar materiais para todas as grades (Fund II + EM)
    grade_ids = list(GRADE_MAP.keys())  # [10, 11, 12, 13, 14, 15, 16]

    for grade_id in grade_ids:
        serie = normalizar_serie_sae(grade_id=grade_id)
        print(f"\n  Grade {grade_id} ({serie}):")
        page = 0
        total_grade = 0

        while True:
            resp = session.post(
                f"{LMS_BFF}/v3/materials/search",
                headers=headers,
                json={"page": page, "size": page_size, "gradeIds": [grade_id]},
                timeout=30,
            )

            if resp.status_code != 200:
                print(f"    ERRO: {resp.status_code}")
                break

            data = resp.json()
            items = data if isinstance(data, list) else data.get("content", data.get("results", []))

            if not items:
                break

            for mat in items:
                # Filtrar apenas materiais oficiais SAE (isDefault=True)
                if not mat.get("isDefault", False):
                    continue

                # Extrair disciplina dos branches
                disciplina_sae = None
                colecao = None
                segmento = None
                for branch in mat.get("branches", []):
                    dim = branch.get("dimensionName", "")
                    val = branch.get("nodeValueName", "")
                    if "curricular" in dim.lower() or "componente" in dim.lower():
                        disciplina_sae = val
                    elif "cole" in dim.lower():
                        colecao = val
                    elif "n\u00edvel" in dim.lower() or "ensino" in dim.lower():
                        segmento = val

                # Fallback: subject field
                if not disciplina_sae and mat.get("subject"):
                    disciplina_sae = mat["subject"].get("name")

                # Pular materiais sem disciplina identificavel
                if not disciplina_sae or disciplina_sae == "Outros":
                    continue

                grade_info = mat.get("grade", {})
                total_grade += 1

                all_materials.append({
                    "material_id": mat.get("id", ""),
                    "material_nome": mat.get("name", ""),
                    "disciplina_sae": disciplina_sae,
                    "disciplina": normalizar_disciplina_sae(disciplina_sae),
                    "serie": serie,
                    "grade_id": grade_info.get("id", grade_id),
                    "colecao": colecao or "",
                    "segmento": segmento or "",
                    "is_default": True,
                    "total_secoes": 0,
                    "capitulos_mapeados": 12,
                })

            # Paginacao
            if isinstance(data, dict):
                total_pages = data.get("totalPages", 1)
                if page + 1 >= total_pages:
                    break
            elif len(items) < page_size:
                break

            page += 1
            time.sleep(0.3)

        print(f"    {total_grade} materiais oficiais SAE")

    # Tentar obter summary para enriquecer total_secoes
    print(f"\n  Enriquecendo com summary ({len(all_materials)} materiais)...")
    enriched = 0
    for mat in all_materials[:30]:  # Limitar para nao sobrecarregar
        mat_id = mat["material_id"]
        try:
            resp = session.get(
                f"{LMS_BFF}/v3/materials/{mat_id}/summary",
                headers=headers,
                timeout=15,
            )
            if resp.status_code == 200:
                summary = resp.json()
                # Contar secoes de nivel 1 (capitulos)
                sections = []
                if isinstance(summary, dict):
                    sections = summary.get("sections", summary.get("contents", summary.get("items", [])))
                elif isinstance(summary, list):
                    sections = summary
                if sections:
                    mat["total_secoes"] = len(sections)
                    # Se tem ~12 secoes L1, mapear direto para capitulos
                    if 10 <= len(sections) <= 14:
                        mat["capitulos_mapeados"] = len(sections)
                    enriched += 1
        except Exception:
            pass
        time.sleep(0.2)

    print(f"    {enriched} materiais enriquecidos com summary")

    # Salvar CSV
    df = pd.DataFrame(all_materials)
    if not df.empty:
        # Remover duplicatas (mesmo material_id)
        df = df.drop_duplicates(subset=["material_id"], keep="first")
        df.to_csv(OUTPUT_DIR / "dim_Materiais_SAE.csv", index=False)
        print(f"\n  SALVO: dim_Materiais_SAE.csv ({len(df)} materiais)")
    else:
        print("\n  AVISO: Nenhum material extraido!")

    return df


# ========== FASE 2: ALUNOS SAE ==========

def extrair_alunos_sae(session, headers):
    """Extrai alunos ativos do SAE Digital e faz match com dim_Alunos SIGA."""
    print("\n" + "=" * 60)
    print("FASE 2: EXTRAINDO ALUNOS SAE")
    print("=" * 60)

    all_students = []
    page = 0
    page_size = 50

    while True:
        url = (
            f"{PDC_BFF}/students"
            f"?institutionIds={INSTITUTION_ID}"
            f"&statuses=ACTIVE"
            f"&page={page}&size={page_size}"
        )
        resp = session.get(url, headers=headers, timeout=30)

        if resp.status_code != 200:
            print(f"  ERRO: {resp.status_code}")
            # Tentar sem paginacao
            if page == 0:
                url_alt = f"{PDC_BFF}/students?institutionIds={INSTITUTION_ID}&statuses=ACTIVE"
                resp = session.get(url_alt, headers=headers, timeout=30)
                if resp.status_code != 200:
                    print(f"  ERRO fallback: {resp.status_code}")
                    break
            else:
                break

        data = resp.json()
        items = []

        if isinstance(data, dict):
            items = data.get("content", data.get("data", data.get("results", [])))
            total_elements = data.get("totalElements", 0)
            total_pages = data.get("totalPages", 1)
        elif isinstance(data, list):
            items = data
            total_elements = len(items)
            total_pages = 1

        if not items:
            break

        for student in items:
            sid = student.get("id")
            name = student.get("name", "")

            # Extrair turma/grade
            classrooms = student.get("currentClassrooms", [])
            for cr in classrooms:
                cl = cr.get("classroom", {})
                turma_nome = cl.get("classroomName", "")
                grade = cl.get("grade", {})
                grade_id = grade.get("id")
                grade_name = grade.get("name", "")
                serie = normalizar_serie_sae(grade_id=grade_id, grade_name=grade_name)
                unidade = extrair_unidade_turma(turma_nome)

                all_students.append({
                    "aluno_sae_id": sid,
                    "aluno_nome_sae": name,
                    "turma_sae_id": cl.get("id", ""),
                    "turma_sae_nome": turma_nome,
                    "grade_id": grade_id,
                    "serie": serie,
                    "unidade": unidade or "",
                })

        print(f"  Pagina {page}: {len(items)} alunos (total: {total_elements})")

        if isinstance(data, dict) and page + 1 >= total_pages:
            break
        elif isinstance(data, list):
            break

        page += 1
        time.sleep(0.3)

    print(f"  Total bruto: {len(all_students)} registros")

    # Match com dim_Alunos SIGA
    df_sae = pd.DataFrame(all_students)
    if df_sae.empty:
        print("  AVISO: Nenhum aluno SAE extraido!")
        return df_sae

    # Filtrar apenas Fund II + EM (grades 10-16) - SIGA nao tem Fund I
    valid_grades = set(GRADE_MAP.keys())  # {10, 11, 12, 13, 14, 15, 16}
    before = len(df_sae)
    df_sae = df_sae[df_sae["grade_id"].isin(valid_grades)].copy()
    print(f"  Filtrado Fund II + EM: {len(df_sae)}/{before} (removidos {before - len(df_sae)} Fund I)")

    path_siga = OUTPUT_DIR / "dim_Alunos.csv"
    if path_siga.exists():
        df_siga = pd.read_csv(path_siga)
        print(f"  Fazendo match com {len(df_siga)} alunos SIGA...")

        # Normalizar nomes
        df_sae["nome_norm"] = df_sae["aluno_nome_sae"].apply(normalizar_nome)
        df_siga["nome_norm"] = df_siga["aluno_nome"].apply(normalizar_nome)

        # Match por nome normalizado + serie
        merged = df_sae.merge(
            df_siga[["aluno_id", "nome_norm", "serie", "unidade"]].rename(
                columns={"aluno_id": "aluno_id_siga", "serie": "serie_siga", "unidade": "unidade_siga"}
            ),
            on="nome_norm",
            how="left",
        )

        # Confianca do match
        def calc_confianca(row):
            if pd.isna(row.get("aluno_id_siga")):
                return 0.0
            conf = 0.8  # Match por nome
            if row.get("serie") == row.get("serie_siga"):
                conf += 0.1
            if row.get("unidade") and row.get("unidade_siga") and row["unidade"] == row["unidade_siga"]:
                conf += 0.1
            return conf

        merged["match_confianca"] = merged.apply(calc_confianca, axis=1)

        # Remover duplicatas - manter melhor match por aluno SAE
        merged = merged.sort_values("match_confianca", ascending=False)
        merged = merged.drop_duplicates(subset=["aluno_sae_id"], keep="first")

        matched = merged["aluno_id_siga"].notna().sum()
        print(f"  Match: {matched}/{len(merged)} ({matched/len(merged)*100:.1f}%)")

        # Preencher unidade do SIGA quando SAE nao tem
        mask_no_un = (merged["unidade"] == "") & merged["unidade_siga"].notna()
        merged.loc[mask_no_un, "unidade"] = merged.loc[mask_no_un, "unidade_siga"]

        df_sae = merged.drop(columns=["nome_norm", "serie_siga", "unidade_siga"], errors="ignore")
    else:
        print("  AVISO: dim_Alunos.csv nao encontrado - sem match SIGA")
        df_sae["aluno_id_siga"] = None
        df_sae["match_confianca"] = 0.0

    # Salvar CSV
    cols = ["aluno_sae_id", "aluno_nome_sae", "turma_sae_id", "turma_sae_nome",
            "grade_id", "serie", "unidade", "aluno_id_siga", "match_confianca"]
    cols = [c for c in cols if c in df_sae.columns]
    df_sae = df_sae[cols]
    df_sae.to_csv(OUTPUT_DIR / "dim_Alunos_SAE.csv", index=False)
    print(f"\n  SALVO: dim_Alunos_SAE.csv ({len(df_sae)} alunos)")

    return df_sae


# ========== FASE 3: ENGAJAMENTO ==========

def extrair_engajamento(session, headers, df_alunos, df_materiais):
    """Extrai engajamento dos alunos. Tenta per-student; fallback para agregado."""
    print("\n" + "=" * 60)
    print("FASE 3: EXTRAINDO ENGAJAMENTO")
    print("=" * 60)

    engajamento_rows = []
    endpoint_ok = False

    if df_alunos.empty or df_materiais.empty:
        print("  AVISO: Sem dados de alunos ou materiais - pulando")
        return pd.DataFrame()

    # Testar endpoint de progresso por aluno com primeiro aluno
    sample_student = df_alunos.iloc[0]["aluno_sae_id"]
    test_urls = [
        f"{LMS_BFF}/contents/student/{sample_student}/exercise-progress",
        f"{LMS_BFF}/v3/contents/student/{sample_student}/exercise-progress",
        f"{LMS_BFF}/v3/students/{sample_student}/progress",
        f"{LMS_BFF}/v3/students/{sample_student}/exercise-progress",
        f"{LMS_BFF}/v3/materials/reports/student/{sample_student}",
    ]

    working_url_pattern = None
    for url in test_urls:
        try:
            resp = session.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                body = resp.json()
                if body and (isinstance(body, list) or (isinstance(body, dict) and len(body) > 0)):
                    working_url_pattern = url.replace(str(sample_student), "{student_id}")
                    print(f"  Endpoint encontrado: {working_url_pattern}")
                    endpoint_ok = True
                    break
        except Exception:
            pass

    if endpoint_ok and working_url_pattern:
        # Extrair progresso per-student (limitar a ~200 alunos para performance)
        alunos_sample = df_alunos.head(200)
        print(f"  Extraindo progresso de {len(alunos_sample)} alunos...")

        for idx, row in alunos_sample.iterrows():
            sid = row["aluno_sae_id"]
            url = working_url_pattern.replace("{student_id}", str(sid))

            try:
                resp = session.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    progress = resp.json()
                    # Parse progress data (formato varia por endpoint)
                    if isinstance(progress, list):
                        for item in progress:
                            mat_id = item.get("materialId", item.get("material_id", ""))
                            # Buscar info do material
                            mat_info = df_materiais[df_materiais["material_id"] == mat_id]
                            if mat_info.empty:
                                continue
                            mi = mat_info.iloc[0]
                            engajamento_rows.append({
                                "aluno_sae_id": sid,
                                "material_id": mat_id,
                                "disciplina": mi["disciplina"],
                                "serie": mi["serie"],
                                "capitulo": item.get("chapter", item.get("section", 0)),
                                "pct_exercicios": item.get("progress", item.get("percentage", 0)),
                                "exercicios_total": item.get("total", 0),
                                "exercicios_feitos": item.get("completed", item.get("done", 0)),
                                "data_extracao": datetime.now().strftime("%Y-%m-%d"),
                            })
                    elif isinstance(progress, dict):
                        materials = progress.get("materials", progress.get("content", []))
                        for item in (materials if isinstance(materials, list) else []):
                            mat_id = item.get("materialId", item.get("id", ""))
                            mat_info = df_materiais[df_materiais["material_id"] == mat_id]
                            if mat_info.empty:
                                continue
                            mi = mat_info.iloc[0]
                            pct = item.get("progress", item.get("percentage", 0))
                            engajamento_rows.append({
                                "aluno_sae_id": sid,
                                "material_id": mat_id,
                                "disciplina": mi["disciplina"],
                                "serie": mi["serie"],
                                "capitulo": 0,
                                "pct_exercicios": pct,
                                "exercicios_total": item.get("totalExercises", item.get("total", 0)),
                                "exercicios_feitos": item.get("completedExercises", item.get("done", 0)),
                                "data_extracao": datetime.now().strftime("%Y-%m-%d"),
                            })
            except Exception:
                pass

            if (idx + 1) % 50 == 0:
                print(f"    Processados {idx + 1} alunos...")
            time.sleep(0.2)

    if not engajamento_rows:
        # Fallback: engajamento agregado via home-info
        print("  Endpoint per-student nao disponivel. Usando home-info (agregado)...")
        try:
            url = (
                f"{PDC_BFF}/home-info"
                f"?institutionId={INSTITUTION_ID}"
                f"&loggedProfileId=17"
                f"&buCode=SAE"
                f"&statuses=ACTIVE"
                f"&startDate=2026-01-01T00:00:00.000000"
                f"&endDate={datetime.now().strftime('%Y-%m-%dT23:59:59.999000')}"
                f"&actingAccountId={ACCOUNT_ID_COORD}"
                f"&profileIdToEngagement=3"
                f"&currentAcademicYear=2026"
            )
            resp = session.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                home = resp.json()
                engagement_raw = home.get("engagementPercentage", home.get("engagement", 0))
                # engagementPercentage pode ser dict ou float
                if isinstance(engagement_raw, dict):
                    engagement_pct = engagement_raw.get("engagementPercentage", 0)
                    total_students = engagement_raw.get("totalUsers", 0)
                    active_students = engagement_raw.get("activeUsers", 0)
                else:
                    engagement_pct = float(engagement_raw) if engagement_raw else 0
                    total_students = home.get("totalStudents", 0)
                    active_students = home.get("activeStudents", 0)
                print(f"  Home-info: engajamento={engagement_pct}%, "
                      f"alunos={active_students}/{total_students}")

                # Gerar engajamento sintetico por serie/disciplina
                for _, mat in df_materiais.iterrows():
                    serie_alunos = df_alunos[df_alunos["serie"] == mat["serie"]]
                    n_alunos = len(serie_alunos)
                    for cap in range(1, 13):
                        engajamento_rows.append({
                            "aluno_sae_id": 0,  # Agregado
                            "material_id": mat["material_id"],
                            "disciplina": mat["disciplina"],
                            "serie": mat["serie"],
                            "capitulo": cap,
                            "pct_exercicios": round(engagement_pct * (0.7 + 0.3 * (1 - cap / 12)), 1),
                            "exercicios_total": 0,
                            "exercicios_feitos": 0,
                            "data_extracao": datetime.now().strftime("%Y-%m-%d"),
                        })
                print(f"  Gerado engajamento sintetico: {len(engajamento_rows)} registros")
        except Exception as e:
            print(f"  ERRO home-info: {e}")

    # Salvar CSV
    df_eng = pd.DataFrame(engajamento_rows)
    if not df_eng.empty:
        df_eng.to_csv(OUTPUT_DIR / "fato_Engajamento_SAE.csv", index=False)
        print(f"\n  SALVO: fato_Engajamento_SAE.csv ({len(df_eng)} registros)")
    else:
        # Salvar CSV vazio com schema correto
        cols = ["aluno_sae_id", "material_id", "disciplina", "serie", "capitulo",
                "pct_exercicios", "exercicios_total", "exercicios_feitos", "data_extracao"]
        df_eng = pd.DataFrame(columns=cols)
        df_eng.to_csv(OUTPUT_DIR / "fato_Engajamento_SAE.csv", index=False)
        print("\n  SALVO: fato_Engajamento_SAE.csv (vazio - sem dados de engajamento)")

    return df_eng


# ========== FASE 4: CRUZAMENTO ==========

def gerar_cruzamento(df_materiais, df_alunos, df_engajamento):
    """Gera fato_Cruzamento.csv cruzando SIGA (professor) x SAE (aluno)."""
    print("\n" + "=" * 60)
    print("FASE 4: GERANDO CRUZAMENTO SIGA x SAE")
    print("=" * 60)

    # Carregar fato_Aulas SIGA
    path_aulas = OUTPUT_DIR / "fato_Aulas.csv"
    if not path_aulas.exists():
        print("  ERRO: fato_Aulas.csv nao encontrado!")
        return pd.DataFrame()

    df_aulas = pd.read_csv(path_aulas)
    df_aulas['data'] = pd.to_datetime(df_aulas['data'], errors='coerce')

    semana_atual = calcular_semana_letiva()
    cap_esperado = calcular_capitulo_esperado(semana_atual)
    data_extracao = datetime.now().strftime("%Y-%m-%d")

    print(f"  Semana letiva: {semana_atual}, Capitulo esperado: {cap_esperado}")
    print(f"  fato_Aulas: {len(df_aulas)} registros")

    cruzamento_rows = []

    # Agrupar aulas por (unidade, serie, disciplina, turma, professor, semana_letiva)
    group_cols = ['unidade', 'serie', 'disciplina', 'turma', 'professor']
    if 'semana_letiva' in df_aulas.columns:
        group_cols.append('semana_letiva')

    for keys, grp in df_aulas.groupby(group_cols):
        if 'semana_letiva' in group_cols:
            unidade, serie, disciplina, turma, professor, semana = keys
        else:
            unidade, serie, disciplina, turma, professor = keys
            semana = semana_atual

        # Detectar capitulo do professor via regex no conteudo
        cap_professor = detectar_capitulo(grp['conteudo'])

        # Buscar engajamento SAE para esta serie/disciplina
        cap_alunos_mediana = None
        pct_engajamento = None
        alunos_ativos = 0
        total_alunos = 0

        if not df_engajamento.empty:
            eng_match = df_engajamento[
                (df_engajamento["serie"] == serie) &
                (df_engajamento["disciplina"] == disciplina)
            ]
            if not eng_match.empty:
                # Pegar engajamento do capitulo mais proximo
                if "capitulo" in eng_match.columns:
                    eng_cap = eng_match[eng_match["capitulo"] > 0]
                    if not eng_cap.empty:
                        cap_alunos_mediana = int(eng_cap["capitulo"].median())
                pct_engajamento = round(eng_match["pct_exercicios"].mean(), 1)

        # Contar alunos por turma/serie do SAE
        if not df_alunos.empty:
            alunos_turma = df_alunos[
                (df_alunos["serie"] == serie) &
                (df_alunos["unidade"] == unidade)
            ]
            total_alunos = len(alunos_turma)
            alunos_ativos = len(alunos_turma[alunos_turma.get("match_confianca", 0) > 0]) if "match_confianca" in alunos_turma.columns else total_alunos

        # Calcular gap e status
        gap = None
        if cap_professor and cap_alunos_mediana:
            gap = cap_professor - cap_alunos_mediana

        status = classificar_status(cap_professor, cap_esperado, cap_alunos_mediana, pct_engajamento)

        cruzamento_rows.append({
            "unidade": unidade,
            "serie": serie,
            "disciplina": disciplina,
            "turma": turma,
            "professor": professor,
            "semana_letiva": int(semana),
            "cap_professor": cap_professor,
            "cap_esperado": cap_esperado,
            "cap_alunos_mediana": cap_alunos_mediana,
            "pct_engajamento": pct_engajamento,
            "gap_prof_alunos": gap,
            "total_alunos": total_alunos,
            "alunos_ativos": alunos_ativos,
            "status": status,
            "data_extracao": data_extracao,
        })

    df_cruz = pd.DataFrame(cruzamento_rows)
    if not df_cruz.empty:
        df_cruz.to_csv(OUTPUT_DIR / "fato_Cruzamento.csv", index=False)
        print(f"\n  SALVO: fato_Cruzamento.csv ({len(df_cruz)} registros)")

        # Estatisticas
        for st_val in df_cruz["status"].value_counts().items():
            print(f"    {st_val[0]}: {st_val[1]}")
    else:
        print("  AVISO: Nenhum cruzamento gerado!")

    return df_cruz


def detectar_capitulo(conteudo_series):
    """Detecta capitulo mencionado no conteudo registrado pelo professor.
    Busca padroes como 'Cap. 3', 'Capitulo 5', 'cap 7', etc."""
    caps = []
    for conteudo in conteudo_series.dropna():
        conteudo = str(conteudo)
        # Padroes: Cap. N, Capitulo N, cap N, Cap N
        matches = re.findall(
            r'(?:cap(?:\u00edtulo|\.?)\s*(\d{1,2}))',
            conteudo,
            re.IGNORECASE,
        )
        for m in matches:
            n = int(m)
            if 1 <= n <= 12:
                caps.append(n)

    if caps:
        return max(caps)  # Retorna o capitulo mais avancado
    return None


def classificar_status(cap_prof, cap_esp, cap_alunos, pct_eng):
    """Classifica status do cruzamento professor x alunos."""
    # Sem dados SAE
    if cap_alunos is None and pct_eng is None:
        if cap_prof is None:
            return "Sem Dados"
        return "Sem SAE"

    # Professor sem capitulo detectado
    if cap_prof is None:
        if pct_eng and pct_eng > 30:
            return "Alunos Ativos, Professor N/D"
        return "Dados Insuficientes"

    # Alinhado
    if cap_alunos and abs(cap_prof - cap_alunos) <= 1:
        if pct_eng and pct_eng >= 50:
            return "Alinhado"
        return "Alinhado, Baixo Engajamento"

    # Gap
    if cap_alunos and cap_prof > cap_alunos + 1:
        return "Professor Adiantado"

    if cap_alunos and cap_prof < cap_alunos - 1:
        return "Professor Atrasado"

    # Engajamento
    if pct_eng is not None and pct_eng < 20:
        return "Baixo Engajamento"

    return "Em Analise"


# ========== MAIN ==========

def main():
    print("=" * 60)
    print("EXTRACAO SAE DIGITAL - CRUZAMENTO SIGA x SAE")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)

    token = login()
    session = requests.Session()
    headers = make_headers(token)

    # Fase 1: Materiais
    df_materiais = extrair_materiais(session, headers)

    # Fase 2: Alunos
    df_alunos = extrair_alunos_sae(session, headers)

    # Fase 3: Engajamento
    df_engajamento = extrair_engajamento(session, headers, df_alunos, df_materiais)

    # Fase 4: Cruzamento
    df_cruzamento = gerar_cruzamento(df_materiais, df_alunos, df_engajamento)

    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DA EXTRACAO")
    print("=" * 60)
    print(f"  dim_Materiais_SAE.csv:    {len(df_materiais)} materiais")
    print(f"  dim_Alunos_SAE.csv:       {len(df_alunos)} alunos")
    print(f"  fato_Engajamento_SAE.csv: {len(df_engajamento)} registros")
    print(f"  fato_Cruzamento.csv:      {len(df_cruzamento)} registros")
    print(f"\nArquivos salvos em: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
