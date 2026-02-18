#!/usr/bin/env python3
"""
extrair_pipefy_rh.py - Extração completa do Pipefy RH para Power BI
Colégio ELO

Extrai todos os cards dos 4 pipes e registros da tabela Candidatos.

Saída (em power_bi/):
  - fato_Vagas_RH.csv           (Abertura de Vagas - 328+ cards)
  - fato_Admissoes_Pipefy.csv   (Admissão Digital - 43+ cards)
  - fato_Desligamentos_Pipefy.csv (Desligamento - 6+ cards)
  - fato_Solicitacoes_DP.csv    (Solicitações DP - 1710+ cards)
  - dim_Candidatos.csv          (Tabela Candidatos)
"""

import os
import time
from datetime import datetime

import pandas as pd
import requests

# ── Configuração ──────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "power_bi")

PIPEFY_URL = "https://api.pipefy.com/graphql"
PIPEFY_TOKEN = (
    "eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE3NzA3NjYzMjYsImp0aSI6"
    "Ijk2OTFhYzM5LTQwNTUtNGM2ZC1iYjlkLTYxZjNjNGE4ZWVmNiIsInN1YiI6MzA0NTExODc4LCJ1"
    "c2VyIjp7ImlkIjozMDQ1MTE4NzgsImVtYWlsIjoicmhlbG9AY29sZWdpb2Vsby5jb20uYnIifSwi"
    "dXNlcl90eXBlIjoiYXV0aGVudGljYXRlZCJ9.B3nm6AzWF0iPRL1IW4rUkTn2AvlThwjjlj4A8luV"
    "C_jHp-pfxHpnWIu_BKHif4IRJFsdDtV00ZbbXR33S1joqg"
)

HEADERS = {
    "Authorization": f"Bearer {PIPEFY_TOKEN}",
    "Content-Type": "application/json",
}

PIPES = {
    304091160: "Abertura de Vagas",
    304091162: "Desligamento",
    304091163: "Admissão Digital",
    305999985: "Solicitações DP",
}

PAGE_SIZE = 50
RATE_LIMIT_PAUSE = 0.5  # segundos entre requests


# ── API ───────────────────────────────────────────────────────────────────────

def graphql(query: str, retries: int = 3) -> dict:
    """Executa query GraphQL com retry."""
    for attempt in range(retries):
        try:
            r = requests.post(PIPEFY_URL, json={"query": query}, headers=HEADERS, timeout=30)
            if r.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    Rate limit, aguardando {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json()
            if "errors" in data and not data.get("data"):
                print(f"    Erro GraphQL: {data['errors'][0]['message']}")
                return {}
            return data.get("data", {})
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"    Falha após {retries} tentativas: {e}")
                return {}
    return {}


def extrair_cards_pipe(pipe_id: int, pipe_name: str) -> list[dict]:
    """Extrai todos os cards de um pipe com paginação."""
    print(f"\n  Extraindo: {pipe_name} (pipe {pipe_id})")

    all_cards = []
    cursor = None
    page = 0

    while True:
        page += 1
        after_clause = f', after: "{cursor}"' if cursor else ""

        query = """
        {
          allCards(pipeId: %d, first: %d%s) {
            edges {
              node {
                id
                title
                createdAt
                finished_at
                due_date
                current_phase {
                  name
                }
                assignees {
                  name
                }
                fields {
                  name
                  value
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """ % (pipe_id, PAGE_SIZE, after_clause)

        data = graphql(query)
        if not data or "allCards" not in data:
            break

        edges = data["allCards"]["edges"]
        for edge in edges:
            node = edge["node"]
            card = {
                "card_id": node["id"],
                "titulo": node.get("title", ""),
                "fase_atual": node.get("current_phase", {}).get("name", ""),
                "criado_em": node.get("createdAt", ""),
                "concluido_em": node.get("finished_at", ""),
                "due_date": node.get("due_date", ""),
                "responsaveis": ", ".join(
                    a.get("name", "") for a in (node.get("assignees") or [])
                ),
            }
            # Flatten fields
            for field in node.get("fields", []):
                fname = field["name"]
                fval = field["value"]
                # Limpar valores de lista JSON
                if isinstance(fval, str) and fval.startswith("["):
                    try:
                        import json
                        parsed = json.loads(fval)
                        if isinstance(parsed, list):
                            fval = ", ".join(str(v) for v in parsed)
                    except Exception:
                        pass
                card[fname] = fval

            all_cards.append(card)

        has_next = data["allCards"]["pageInfo"]["hasNextPage"]
        cursor = data["allCards"]["pageInfo"]["endCursor"]

        print(f"    Página {page}: +{len(edges)} cards (total: {len(all_cards)})")

        if not has_next:
            break
        time.sleep(RATE_LIMIT_PAUSE)

    print(f"    Total: {len(all_cards)} cards")
    return all_cards


def extrair_tabela(table_id: str, table_name: str) -> list[dict]:
    """Extrai todos os registros de uma tabela Pipefy."""
    print(f"\n  Extraindo tabela: {table_name} (ID: {table_id})")

    all_records = []
    cursor = None
    page = 0

    while True:
        page += 1
        after_clause = f', after: "{cursor}"' if cursor else ""

        query = """
        {
          table_records(table_id: "%s", first: %d%s) {
            edges {
              node {
                id
                title
                created_at
                record_fields {
                  name
                  value
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """ % (table_id, PAGE_SIZE, after_clause)

        data = graphql(query)
        if not data or "table_records" not in data:
            break

        edges = data["table_records"]["edges"]
        for edge in edges:
            node = edge["node"]
            rec = {
                "record_id": node["id"],
                "titulo": node.get("title", ""),
                "criado_em": node.get("created_at", ""),
            }
            for field in node.get("record_fields", []):
                fname = field["name"]
                fval = field["value"]
                if isinstance(fval, str) and fval.startswith("["):
                    try:
                        import json
                        parsed = json.loads(fval)
                        if isinstance(parsed, list):
                            fval = ", ".join(str(v) for v in parsed)
                    except Exception:
                        pass
                rec[fname] = fval

            all_records.append(rec)

        has_next = data["table_records"]["pageInfo"]["hasNextPage"]
        cursor = data["table_records"]["pageInfo"]["endCursor"]

        print(f"    Página {page}: +{len(edges)} registros (total: {len(all_records)})")

        if not has_next:
            break
        time.sleep(RATE_LIMIT_PAUSE)

    print(f"    Total: {len(all_records)} registros")
    return all_records


# ── Processamento para Power BI ──────────────────────────────────────────────

def parse_datetime(val):
    """Converte string datetime Pipefy para date."""
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return val


def parse_date_br(val):
    """Converte data BR (dd/mm/yyyy) para ISO."""
    if not val:
        return None
    try:
        parts = val.strip().split(" ")[0]  # pega só a data, ignora hora
        if "/" in parts:
            d, m, y = parts.split("/")
            return f"{y}-{m}-{d}"
    except Exception:
        pass
    return val


def processar_vagas(cards: list[dict]) -> pd.DataFrame:
    """Processa cards de Abertura de Vagas para Power BI."""
    rows = []
    for c in cards:
        rows.append({
            "card_id": c.get("card_id"),
            "vaga": c.get("Vaga solicitada para abertura", c.get("titulo", "")),
            "unidade": c.get("Unidade", ""),
            "departamento": c.get("Departamento", ""),
            "jornada": c.get("Jornada", ""),
            "horario": (c.get("Horario", "") or "")[:200],
            "tipo_recrutamento": c.get("Tipo de recrutamento", ""),
            "motivo": c.get("Motivo da nova posição", ""),
            "substituido": c.get("Quem será substituído?", ""),
            "regime_trabalho": c.get("Regime de trabalho", ""),
            "salario_ofertado": c.get("Valor do salário", ""),
            "modalidade": c.get("Modalidade de trabalho", ""),
            "fase_atual": c.get("fase_atual", ""),
            "data_solicitacao": parse_date_br(c.get("Data de solicitação da vaga", "")),
            "criado_em": parse_datetime(c.get("criado_em", "")),
            "concluido_em": parse_datetime(c.get("concluido_em", "")),
            "responsavel_triagem": c.get("Analista responsável pela triagem", ""),
            "responsavel_selecao": c.get("Analista responsável", ""),
        })

    df = pd.DataFrame(rows)

    # Limpar salário
    if "salario_ofertado" in df.columns:
        df["salario_ofertado"] = (
            df["salario_ofertado"]
            .astype(str)
            .str.replace(r"[R$\s.]", "", regex=True)
            .str.replace(",", ".")
            .apply(lambda x: float(x) if x.replace(".", "").replace("-", "").isdigit() else 0)
        )

    # Calcular tempo de preenchimento (dias)
    df["criado_dt"] = pd.to_datetime(df["criado_em"], errors="coerce")
    df["concluido_dt"] = pd.to_datetime(df["concluido_em"], errors="coerce")
    df["dias_preenchimento"] = (df["concluido_dt"] - df["criado_dt"]).dt.days
    df = df.drop(columns=["criado_dt", "concluido_dt"])

    # Status derivado
    def status_vaga(fase):
        if "CONTRATADO" in str(fase).upper() or "CONCLU" in str(fase).upper():
            return "Contratado"
        if "CONGELAD" in str(fase).upper():
            return "Congelada"
        if "ARQUIVAD" in str(fase).upper():
            return "Arquivada"
        return "Em andamento"

    df["status_vaga"] = df["fase_atual"].apply(status_vaga)

    return df


def processar_admissoes(cards: list[dict]) -> pd.DataFrame:
    """Processa cards de Admissão Digital para Power BI."""
    rows = []
    for c in cards:
        rows.append({
            "card_id": c.get("card_id"),
            "nome": c.get("Nome do(a) colaborador(a):", c.get("titulo", "")),
            "cargo": c.get("Cargo:", ""),
            "setor": c.get("Setor para qual você está sendo contratado(a)", ""),
            "unidade": c.get("Unidade:", ""),
            "turno": c.get("Turno de trabalho:", ""),
            "email": c.get("E-mail do(a) colaborador(a):", ""),
            "data_nascimento": c.get("Data de nascimento:", ""),
            "cpf": c.get("CPF ", ""),
            "cidade_nascimento": c.get("Cidade /estado do seu nascimento", ""),
            "estado_civil": c.get("Estado civil :", ""),
            "escolaridade": c.get("Escolaridade:", ""),
            "curso": c.get("Curso :", ""),
            "tipo_vinculo": c.get("Tipo vínculo:", ""),
            "optante_vt": c.get("Optante do vale transporte ", ""),
            "optante_odonto": c.get("Optante pelo plano odontológico", ""),
            "raca_cor": c.get("Raça/ cor", ""),
            "dependentes": c.get("Dependentes:", ""),
            "data_inicio": c.get("Data de início do(a) colaborador(a)", ""),
            "salario": c.get("Salário", ""),
            "escala": c.get("Escala", ""),
            "superior_direto": c.get("Superior Direto", ""),
            "segmento": c.get("Segmento ", ""),
            "fase_atual": c.get("fase_atual", ""),
            "criado_em": parse_datetime(c.get("criado_em", "")),
            "concluido_em": parse_datetime(c.get("concluido_em", "")),
        })

    df = pd.DataFrame(rows)

    # Status derivado
    def status_admissao(fase):
        if "realizadas" in str(fase).lower() or "conclu" in str(fase).lower():
            return "Concluída"
        if "cancelad" in str(fase).lower():
            return "Cancelada"
        return "Em andamento"

    df["status_admissao"] = df["fase_atual"].apply(status_admissao)

    return df


def processar_desligamentos(cards: list[dict]) -> pd.DataFrame:
    """Processa cards de Desligamento para Power BI."""
    rows = []
    for c in cards:
        rows.append({
            "card_id": c.get("card_id"),
            "nome_colaborador": c.get("Nome Colaborador", c.get("titulo", "")),
            "nome_solicitante": c.get("Nome solicitante do desligamento", ""),
            "setor": c.get("Setor do Calaborador", ""),
            "unidade": c.get("Unidade que trabalha", ""),
            "motivo": c.get("Motivo do desligamento ", ""),
            "detalhe_motivo": c.get("Detalhar o motivo do desligamento", ""),
            "informacoes_adicionais": c.get(
                "Informações adicionais sobre o desligamento  ", ""
            ),
            "fase_atual": c.get("fase_atual", ""),
            "data_solicitacao": parse_datetime(
                c.get("Data e hora da solicitação ", c.get("criado_em", ""))
            ),
            "data_desligamento": c.get("Data e hora do desligamento ", ""),
            "feedback": c.get("Feedback do colaborador ", ""),
            "criado_em": parse_datetime(c.get("criado_em", "")),
            "concluido_em": parse_datetime(c.get("concluido_em", "")),
        })

    return pd.DataFrame(rows)


def processar_solicitacoes_dp(cards: list[dict]) -> pd.DataFrame:
    """Processa cards de Solicitações DP para Power BI."""
    rows = []
    for c in cards:
        rows.append({
            "card_id": c.get("card_id"),
            "solicitante": c.get("Nome do solicitante", c.get("titulo", "")),
            "cpf": c.get("CPF", ""),
            "cargo": c.get("Cargo", ""),
            "tipo_solicitacao": c.get(
                "Tipo de Solicitações ao DP - Departamento Pessoal", ""
            ),
            "unidade": c.get("Unidade", ""),
            "descricao": (c.get("Descrição da Necessidade Atual", "") or "")[:500],
            "fase_atual": c.get("fase_atual", ""),
            "data_solicitacao": parse_date_br(c.get("Data da solicitação ", "")),
            "criado_em": parse_datetime(c.get("criado_em", "")),
            "concluido_em": parse_datetime(c.get("concluido_em", "")),
        })

    df = pd.DataFrame(rows)

    # Simplificar tipo de solicitação (são muito longos)
    tipo_map = {
        "Ponto e jornada": "Ponto/Jornada",
        "Atestados": "Atestados/Licença",
        "Afastamento": "Atestados/Licença",
        "Licença": "Atestados/Licença",
        "documentos e declarações": "Documentos",
        "Atualização de dados": "Atualização Cadastral",
        "IR": "Imposto de Renda",
        "Férias": "Férias",
        "Benefícios": "Benefícios",
        "Outros": "Outros",
    }

    def simplificar_tipo(tipo):
        if not tipo:
            return "Não informado"
        for chave, valor in tipo_map.items():
            if chave.lower() in tipo.lower():
                return valor
        return tipo[:50]

    df["tipo_simplificado"] = df["tipo_solicitacao"].apply(simplificar_tipo)

    # Status derivado
    def status_dp(fase):
        if "conclu" in str(fase).lower():
            return "Concluído"
        if "reprovad" in str(fase).lower():
            return "Reprovado"
        if "arquivad" in str(fase).lower():
            return "Arquivado"
        return "Em andamento"

    df["status_solicitacao"] = df["fase_atual"].apply(status_dp)

    return df


def processar_candidatos(records: list[dict]) -> pd.DataFrame:
    """Processa registros da tabela Candidatos para Power BI."""
    rows = []
    for r in records:
        rows.append({
            "record_id": r.get("record_id"),
            "nome_candidato": r.get("Nome do candidato", r.get("titulo", "")),
            "cargo": r.get("Cargo ", ""),
            "telefone": r.get("Telefone", ""),
            "avaliador_rh": r.get("Avaliador(a)RH", ""),
            "data_entrevista": r.get("Data e hora da entrevista ", ""),
            "avaliacao_candidato": r.get("Avaliação do candidato ", ""),
            "avaliacao_1fase": (r.get("Avaliação geral -1º fase", "") or "")[:300],
            "avaliacao_2fase": (r.get("Avaliação geral 2º fase", "") or "")[:300],
            "observacoes": (r.get("Observações Extras", "") or "")[:300],
            "criado_em": r.get("criado_em", ""),
        })

    df = pd.DataFrame(rows)

    # Derivar resultado da avaliação
    def resultado(aval):
        if not aval:
            return "Não avaliado"
        aval_lower = str(aval).lower()
        if "aprovado no processo" in aval_lower or "aprovado 2" in aval_lower:
            return "Aprovado"
        if "reprovado" in aval_lower:
            return "Reprovado"
        if "desistente" in aval_lower:
            return "Desistente"
        if "aprovado 1" in aval_lower:
            return "Em processo"
        return "Em processo"

    df["resultado"] = df["avaliacao_candidato"].apply(resultado)

    return df


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Extração Pipefy RH → Power BI - Colégio ELO")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Extrair todos os pipes
    print("\n── Extraindo pipes ──")
    raw_vagas = extrair_cards_pipe(304091160, "Abertura de Vagas")
    raw_deslig = extrair_cards_pipe(304091162, "Desligamento")
    raw_admissao = extrair_cards_pipe(304091163, "Admissão Digital")
    raw_dp = extrair_cards_pipe(305999985, "Solicitações DP")

    # 2. Extrair tabela Candidatos
    print("\n── Extraindo tabelas ──")
    raw_candidatos = extrair_tabela("oZFeylUO", "Candidatos")

    # 3. Processar para Power BI
    print("\n── Processando para Power BI ──")

    print("\n  [1/5] fato_Vagas_RH.csv")
    df_vagas = processar_vagas(raw_vagas)
    print(f"    {len(df_vagas)} vagas")
    print(f"    Status: {df_vagas['status_vaga'].value_counts().to_dict()}")
    print(f"    Unidades: {df_vagas['unidade'].value_counts().to_dict()}")
    print(f"    Departamentos: {df_vagas['departamento'].value_counts().head(5).to_dict()}")
    if df_vagas["dias_preenchimento"].notna().any():
        print(f"    Tempo médio preenchimento: {df_vagas['dias_preenchimento'].dropna().mean():.0f} dias")
        print(f"    Mediana preenchimento: {df_vagas['dias_preenchimento'].dropna().median():.0f} dias")

    print("\n  [2/5] fato_Admissoes_Pipefy.csv")
    df_admissao = processar_admissoes(raw_admissao)
    print(f"    {len(df_admissao)} admissões")
    print(f"    Status: {df_admissao['status_admissao'].value_counts().to_dict()}")
    print(f"    Unidades: {df_admissao['unidade'].value_counts().to_dict()}")

    print("\n  [3/5] fato_Desligamentos_Pipefy.csv")
    df_deslig = processar_desligamentos(raw_deslig)
    print(f"    {len(df_deslig)} desligamentos")
    if len(df_deslig) > 0:
        print(f"    Motivos: {df_deslig['motivo'].value_counts().to_dict()}")

    print("\n  [4/5] fato_Solicitacoes_DP.csv")
    df_dp = processar_solicitacoes_dp(raw_dp)
    print(f"    {len(df_dp)} solicitações")
    print(f"    Status: {df_dp['status_solicitacao'].value_counts().to_dict()}")
    print(f"    Tipos: {df_dp['tipo_simplificado'].value_counts().to_dict()}")
    print(f"    Unidades: {df_dp['unidade'].value_counts().head(8).to_dict()}")

    print("\n  [5/5] dim_Candidatos.csv")
    df_candidatos = processar_candidatos(raw_candidatos)
    print(f"    {len(df_candidatos)} candidatos")
    if len(df_candidatos) > 0:
        print(f"    Resultados: {df_candidatos['resultado'].value_counts().to_dict()}")

    # 4. Salvar CSVs
    print("\n── Salvando CSVs ──")
    arquivos = [
        ("fato_Vagas_RH.csv", df_vagas),
        ("fato_Admissoes_Pipefy.csv", df_admissao),
        ("fato_Desligamentos_Pipefy.csv", df_deslig),
        ("fato_Solicitacoes_DP.csv", df_dp),
        ("dim_Candidatos.csv", df_candidatos),
    ]

    for nome, df in arquivos:
        path = os.path.join(OUTPUT_DIR, nome)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        size_kb = os.path.getsize(path) / 1024
        print(f"  {nome}: {len(df)} linhas, {len(df.columns)} colunas, {size_kb:.0f}KB")

    # 5. Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DA EXTRAÇÃO")
    print("=" * 60)
    total = sum(len(df) for _, df in arquivos)
    print(f"  Total de registros extraídos: {total}")
    print(f"  Vagas:         {len(df_vagas)} (contratadas: {(df_vagas['status_vaga']=='Contratado').sum()})")
    print(f"  Admissões:     {len(df_admissao)} (concluídas: {(df_admissao['status_admissao']=='Concluída').sum()})")
    print(f"  Desligamentos: {len(df_deslig)}")
    print(f"  Solicitações:  {len(df_dp)} (concluídas: {(df_dp['status_solicitacao']=='Concluído').sum()})")
    print(f"  Candidatos:    {len(df_candidatos)}")
    print(f"\n  Arquivos salvos em: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
