#!/usr/bin/env python3
"""
processar_rh_powerbi.py - Processamento de dados RH para Power BI
Colégio ELO - Dashboard RH CEO

Entrada:
  - PLANILHA GERAL BRUNA MARINHO - UNIFICADA.xls (1.686 registros, 203 colunas)
  - power_bi/dim_Professores.csv (mapeamento professor → unidade)

Saída (em power_bi/):
  - dim_Colaboradores.csv
  - dim_Setores_RH.csv
  - dim_Empresas_RH.csv
  - fato_Movimentacoes_RH.csv
  - fato_Quadro_Atual.csv
  - resumo_Headcount_Mensal.csv
"""

import os
import re
import unicodedata
from datetime import date

import pandas as pd
import numpy as np

# ── Caminhos ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "power_bi")

XLS_PATHS = [
    os.path.join(BASE_DIR, "PLANILHA GERAL BRUNA MARINHO - UNIFICADA.xls"),
    os.path.expanduser(
        "~/Library/Containers/net.whatsapp.WhatsApp/Data/tmp/documents/"
        "79E1A717-7CEF-4494-ADAA-E9764DE63FFE/"
        "PLANILHA GERAL BRUNA MARINHO - UNIFICADA.xls"
    ),
    os.path.expanduser(
        "~/Library/Containers/net.whatsapp.WhatsApp/Data/tmp/documents/"
        "29C1A144-8E69-4233-B823-3A57FE2D73C2/"
        "PLANILHA GERAL BRUNA MARINHO - UNIFICADA.xls"
    ),
]

PROFESSORES_CSV = os.path.join(OUTPUT_DIR, "dim_Professores.csv")

HOJE = date.today()


# ── Funções auxiliares ────────────────────────────────────────────────────────

def normalizar_nome(nome: str) -> str:
    """Remove acentos e converte para UPPER."""
    if not isinstance(nome, str):
        return ""
    texto = unicodedata.normalize("NFD", nome)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.upper().strip()


def classificar_setor(funcao: str, cbo: str) -> str:
    """Classifica colaborador em setor RH por regex na função e CBO."""
    f = (funcao or "").upper()
    c = (cbo or "").upper()
    texto = f"{f} | {c}"

    # Ordem importa: mais específico primeiro
    if re.search(r"ESTAGI[AÁ]RI[OA]|JOVEM APRENDIZ", texto):
        return "Estagiário"
    if re.search(r"DIRETOR|GERENTE|GESTOR", texto):
        return "Gestão"
    if re.search(r"PSIC[OÓ]LOG|FONOAUDI[OÓ]LOG|TERAPEUTA|FISIOTERAPEUT|PISICOLOGO", texto):
        return "Clínico"
    if re.search(
        r"COORDENADOR|COORD\b|ORIENTADOR|PSICOPEDAG|MONITOR|"
        r"APOIO PEDAG|ASSIST.{0,5}PEDAG|ASSIST.{0,5}COORD|"
        r"AUX.{0,5}COORD|INSPETOR|SECRETARIA ESCOLAR",
        texto
    ):
        return "Apoio Pedagógico"
    if re.search(
        r"PROFESSOR|PROF\b|PROF\(|PROF\.|\bPROF\s|DOCENTE|"
        r"PROFESSORA|PROF\sDE\s|PROF\sFUNDAMENTAL|"
        r"PROFESSOR.*DISCIPL.*PEDAG|"
        r"PROFESSOR.*N[IÍ]VEL",
        texto
    ):
        return "Docente"
    if re.search(
        r"ZELADOR|PORTEIR|LIMPEZA|COZINHA|CANTINA|MOTORISTA|"
        r"MANUTEN[CÇ]|FAXINEIR|VIGIA|SEGURAN[CÇ]A|SERV.{0,3}GERAIS|"
        r"CONSERVA[CÇ][AÃ]O|ALIMENTA[CÇ][AÃ]O|LANCHONETE|"
        r"MEC[AÂ]NICO|REFRIGERA[CÇ]|OPER.{0,5}COMPUTADOR",
        texto
    ):
        return "Operacional"
    if re.search(
        r"ADMINISTRATIV|FINANCEIRO|\bRH\b|MARKETING|\bTI\b|"
        r"SECRET[AÁ]RI|RECEPCION|COBRAN[CÇ]A|CONT[AÁ]BIL|"
        r"PESSOAL|DESIGNER|DIAGRAMADOR|SOCIAL MEDIA|"
        r"GR[AÁ]FIC|ESCRITÓRIO|AUXILIAR DE ESCRITÓRIO|"
        r"ASSIST.{0,5}ADMIN|ANALISTA",
        texto
    ):
        return "Administrativo"
    if re.search(r"AUXILIAR DE SALA|AUX.{0,3}DE SALA|AUXILIAR DE CLASSE|DESENVOLVIMENTO INFANTIL", texto):
        return "Apoio Pedagógico"

    return "Administrativo"  # fallback


def normalizar_funcao(funcao: str) -> str:
    """Agrupa variações de nomes de função."""
    if not isinstance(funcao, str):
        return "NÃO INFORMADO"
    f = funcao.upper().strip()

    if re.search(r"ESTAGI[AÁ]RI[OA]|JOVEM APRENDIZ", f):
        return "ESTAGIÁRIO"
    if re.search(r"PROF.*FUNDAMENTAL.*[1I]|PROF.*ANOS INICIAIS|PROF.*POLIVALENTE|PROF.*ED.*INF", f):
        return "PROFESSOR FUND. I / ED. INFANTIL"
    if re.search(r"PROF.*FUNDAMENTAL.*[2II]|PROF.*ENSINO.*MEDIO|PROF.*MATEM|PROF.*PORTUG|PROF.*INGL|PROF.*GEOG|PROF.*HIST|PROF.*BI[OÓ]L|PROF.*QU[IÍ]M|PROF.*F[IÍ]S|PROF.*ART|PROF.*DAN|PROF.*MUS|PROF.*SOCIO|PROF.*AEE|PROF.*DEFICI|PROF.*ED.*FIS|PROF.*ESPORT|PROF.*L[IÍ]NG|PROF.*CI[EÊ]N|PROF.*GRAM", f):
        return "PROFESSOR FUND. II / EM"
    if re.search(r"^PROFESSOR\s*\(?A?\)?$|^PROFESSORA$|^PROFESSOR$", f):
        return "PROFESSOR (GENÉRICO)"
    if re.search(r"APOIO PEDAG", f):
        return "APOIO PEDAGÓGICO"
    if re.search(r"AUX.*SALA|AUXILIAR DE CLASSE", f):
        return "AUXILIAR DE SALA"
    if re.search(r"COORDENADOR|COORD\b", f):
        return "COORDENADOR(A)"
    if re.search(r"AUX.*COORD|ASSIST.*COORD", f):
        return "AUXILIAR DE COORDENAÇÃO"
    if re.search(r"AUX.*SERV.*GER|SERV.*GERAIS|FAXINEIR", f):
        return "SERVIÇOS GERAIS"
    if re.search(r"AUX.*ADMIN|ASSIST.*ADMIN", f):
        return "AUXILIAR/ASSISTENTE ADMINISTRATIVO"
    if re.search(r"ZELADOR", f):
        return "ZELADOR"
    if re.search(r"PORTEIR|PORTARIA", f):
        return "PORTEIRO"
    if re.search(r"COZINHA|CANTINA|LANCHONETE|ALIMENTA", f):
        return "COZINHA/CANTINA"
    if re.search(r"RECEPCION", f):
        return "RECEPCIONISTA"
    if re.search(r"PSIC[OÓ]LOG|PISICOLOGO", f):
        return "PSICÓLOGO(A)"
    if re.search(r"MOTORISTA", f):
        return "MOTORISTA"
    if re.search(r"DESIGNER|DIAGRAMAD|SOCIAL MEDIA|GR[AÁ]FIC", f):
        return "DESIGN/COMUNICAÇÃO"
    if re.search(r"MANUTEN[CÇ]|MEC[AÂ]NICO|REFRIGERA", f):
        return "MANUTENÇÃO"
    if re.search(r"VIGIA|SEGURAN", f):
        return "VIGILÂNCIA/SEGURANÇA"
    if re.search(r"DIRETOR", f):
        return "DIRETOR(A)"
    if re.search(r"ANALISTA|FINANCEIRO|CONT[AÁ]BIL|PESSOAL", f):
        return "ANALISTA/FINANCEIRO"
    if re.search(r"SECRET[AÁ]RI", f):
        return "SECRETARIA"
    if re.search(r"ORIENT.*DISCIPL|INSPETOR", f):
        return "ORIENTADOR/INSPETOR"
    if re.search(r"ASSIST.*RH|ASSIST.*DP|COORD.*RH|COORD.*DP", f):
        return "RH/DP"

    return f  # mantém original se não bateu


def simplificar_grau(grau: str) -> str:
    """Simplifica grau de instrução removendo código numérico."""
    if not isinstance(grau, str):
        return "Não informado"
    m = re.match(r"\d+\s*-\s*(.+)", grau)
    if m:
        txt = m.group(1).strip()
        # Simplificações
        if "Analfabeto" in txt:
            return "Analfabeto"
        if "5º ano" in txt.lower() and "incompleto" in txt.lower():
            return "Fundamental I incompleto"
        if "5º ano completo" in txt.lower():
            return "Fundamental I completo"
        if "6º ao 9º" in txt.lower():
            return "Fundamental II incompleto"
        if "fundamental completo" in txt.lower():
            return "Fundamental completo"
        if "médio incompleto" in txt.lower():
            return "Ensino Médio incompleto"
        if "médio completo" in txt.lower():
            return "Ensino Médio completo"
        if "superior incompleta" in txt.lower():
            return "Superior incompleto"
        if "superior completa" in txt.lower():
            return "Superior completo"
        if "mestrado" in txt.lower():
            return "Mestrado"
        if "doutorado" in txt.lower():
            return "Doutorado"
        if "graduado" in txt.lower():
            return "Pós-graduação"
        return txt
    return grau.strip()


def simplificar_vinculo(vinculo: str) -> str:
    """Simplifica vínculo empregatício."""
    if not isinstance(vinculo, str):
        return "Não informado"
    v = vinculo.strip()
    if v.startswith("10 "):
        return "CLT Indeterminado"
    if v.startswith("60 "):
        return "CLT Determinado"
    if v.startswith("96 ") or v.startswith("97 "):
        return "Prazo Determinado (Lei)"
    return v[:50]


def inferir_unidade(row, prof_map: dict) -> str:
    """Infere unidade física do colaborador."""
    nome_norm = row.get("nome_normalizado", "")
    empresa = row.get("empresa", "")

    # 1. Match por nome normalizado nos JSONs/dim_Professores
    if nome_norm in prof_map:
        return prof_map[nome_norm]

    # 2. Heurísticas por empresa
    if empresa == "PAULISTA":
        return "JG"
    if empresa == "LUBIENSKA":
        return "CDR"

    # 3. Sem inferência confiável - retorna empresa como proxy
    return ""


def faixa_salarial(sal: float) -> str:
    if pd.isna(sal) or sal <= 0:
        return "Sem salário"
    if sal <= 1500:
        return "Até 1.500"
    if sal <= 2500:
        return "1.500-2.500"
    if sal <= 4000:
        return "2.500-4.000"
    return "4.000+"


def faixa_tempo(meses: int) -> str:
    if pd.isna(meses) or meses < 0:
        return "N/A"
    if meses < 6:
        return "< 6 meses"
    if meses < 12:
        return "6m-1 ano"
    if meses < 36:
        return "1-3 anos"
    if meses < 60:
        return "3-5 anos"
    return "5+ anos"


def faixa_etaria(idade: int) -> str:
    if pd.isna(idade) or idade < 0:
        return "N/A"
    if idade <= 25:
        return "18-25"
    if idade <= 35:
        return "26-35"
    if idade <= 45:
        return "36-45"
    if idade <= 55:
        return "46-55"
    return "55+"


# ── Carregamento ──────────────────────────────────────────────────────────────

def carregar_xls() -> pd.DataFrame:
    """Carrega o XLS da planilha geral RH."""
    xls_path = None
    for path in XLS_PATHS:
        if os.path.exists(path):
            xls_path = path
            break

    if xls_path is None:
        raise FileNotFoundError(
            "XLS não encontrado. Copie 'PLANILHA GERAL BRUNA MARINHO - UNIFICADA.xls' "
            f"para {XLS_PATHS[0]}"
        )

    print(f"  Lendo XLS: {os.path.basename(xls_path)}")
    df = pd.read_excel(xls_path, sheet_name="PLANILHA GERAL - UNIFICADA")

    # Remove linhas totalmente vazias
    df = df.dropna(subset=["Colaborador"])
    df["Colaborador"] = df["Colaborador"].astype(int)
    print(f"  {len(df)} registros carregados")
    return df


def carregar_mapa_professores() -> dict:
    """Carrega mapeamento professor → unidade do dim_Professores.csv."""
    if not os.path.exists(PROFESSORES_CSV):
        print("  AVISO: dim_Professores.csv não encontrado, sem mapeamento de unidade docente")
        return {}

    df = pd.read_csv(PROFESSORES_CSV)
    mapa = {}
    for _, row in df.iterrows():
        nome = str(row.get("nome_normalizado", "")).strip()
        unidade = str(row.get("unidade", "")).strip()
        if nome and unidade and unidade not in ("", "nan", "TEEN 1", "TEEN 2"):
            # Se o professor aparece em múltiplas unidades, mantém a primeira
            if nome not in mapa:
                mapa[nome] = unidade
    print(f"  {len(mapa)} professores mapeados a unidades")
    return mapa


# ── Processamento principal ───────────────────────────────────────────────────

def processar_dim_colaboradores(df: pd.DataFrame, prof_map: dict) -> pd.DataFrame:
    """Cria dim_Colaboradores com todas as colunas necessárias."""
    print("\n[1/6] dim_Colaboradores.csv")

    out = pd.DataFrame()
    out["colaborador_id"] = df["Colaborador"]
    out["nome"] = df["Nome"].str.strip()
    out["nome_normalizado"] = df["Nome"].apply(normalizar_nome)
    out["empresa"] = df["Empresa"].str.strip()
    out["funcao"] = df["Descrição função (Dados diários)"].str.strip()
    out["funcao_normalizada"] = out["funcao"].apply(normalizar_funcao)
    out["cbo"] = df["Descrição do CBO"].str.strip()
    out["setor_rh"] = [
        classificar_setor(f, c)
        for f, c in zip(
            df["Descrição função (Dados diários)"].fillna(""),
            df["Descrição do CBO"].fillna("")
        )
    ]
    out["data_admissao"] = pd.to_datetime(df["Data de admissão"]).dt.date
    out["data_rescisao"] = pd.to_datetime(df["Rescisão"]).dt.date
    out["status"] = out["data_rescisao"].apply(lambda x: "Desligado" if pd.notna(x) else "Ativo")
    out["salario_base"] = df["Salário base (Dados diários)"].round(2)
    out["tipo_colaborador"] = df["Tipo colaborador"].str.strip()
    out["classe"] = df["Descrição classe"].str.strip()
    out["horas_semana"] = df["Horas semana"]
    out["sexo"] = df["Sexo"].str.strip()
    out["grau_instrucao"] = df["Grau de instrução"].apply(simplificar_grau)
    out["estado_civil"] = df["Estado civil"].str.strip()
    out["cidade"] = df["Nome da cidade de endereço"].str.strip()
    out["data_nascimento"] = pd.to_datetime(df["Data de nascimento"]).dt.date
    out["vinculo"] = df["Vínculo empregatício"].apply(simplificar_vinculo)

    # Idade
    out["idade"] = out["data_nascimento"].apply(
        lambda d: (HOJE - d).days // 365 if pd.notna(d) else None
    )

    # Tempo de casa (meses)
    def calc_tempo(row):
        adm = row["data_admissao"]
        resc = row["data_rescisao"]
        if pd.isna(adm):
            return None
        fim = resc if pd.notna(resc) else HOJE
        return max(0, (fim.year - adm.year) * 12 + (fim.month - adm.month))

    out["tempo_casa_meses"] = out.apply(calc_tempo, axis=1)

    # Unidade (JSON match para docentes, heurística para demais)
    out["unidade_json"] = out.apply(
        lambda r: prof_map.get(r["nome_normalizado"], ""), axis=1
    )
    out["unidade_inferida"] = out.apply(
        lambda r: inferir_unidade(r, prof_map), axis=1
    )

    # Estatísticas
    ativos = (out["status"] == "Ativo").sum()
    desligados = (out["status"] == "Desligado").sum()
    print(f"  {len(out)} registros | {ativos} ativos | {desligados} desligados")
    print(f"  Setores: {out[out['status']=='Ativo']['setor_rh'].value_counts().to_dict()}")
    print(f"  Unidade inferida (ativos): {out[out['status']=='Ativo']['unidade_inferida'].value_counts().to_dict()}")

    return out


def processar_dim_setores() -> pd.DataFrame:
    """Cria dim_Setores_RH com cores para visualização."""
    print("\n[2/6] dim_Setores_RH.csv")

    setores = [
        (1, "Docente", "#2E86C1"),
        (2, "Apoio Pedagógico", "#27AE60"),
        (3, "Operacional", "#E67E22"),
        (4, "Administrativo", "#8E44AD"),
        (5, "Estagiário", "#F1C40F"),
        (6, "Gestão", "#E74C3C"),
        (7, "Clínico", "#1ABC9C"),
    ]
    df = pd.DataFrame(setores, columns=["setor_id", "setor_rh", "cor"])
    print(f"  {len(df)} setores")
    return df


def processar_dim_empresas(dim_colab: pd.DataFrame) -> pd.DataFrame:
    """Cria dim_Empresas_RH com contagens."""
    print("\n[3/6] dim_Empresas_RH.csv")

    ativos = dim_colab[dim_colab["status"] == "Ativo"].groupby("empresa").size().rename("qtd_ativos")
    desligados = dim_colab[dim_colab["status"] == "Desligado"].groupby("empresa").size().rename("qtd_desligados")

    df = pd.DataFrame({"qtd_ativos": ativos, "qtd_desligados": desligados}).fillna(0).astype(int)
    df = df.reset_index().rename(columns={"index": "empresa"})
    df.insert(0, "empresa_id", range(1, len(df) + 1))

    # Perfil dominante por empresa
    perfis = {}
    for emp in df["empresa"]:
        subset = dim_colab[(dim_colab["empresa"] == emp) & (dim_colab["status"] == "Ativo")]
        if len(subset) == 0:
            perfis[emp] = "Sem ativos"
        else:
            top_setor = subset["setor_rh"].value_counts().head(2)
            desc_parts = [f"{c} {s}" for s, c in top_setor.items()]
            perfis[emp] = " + ".join(desc_parts)
    df["perfil"] = df["empresa"].map(perfis)

    print(f"  {len(df)} empresas")
    for _, row in df.iterrows():
        print(f"    {row['empresa']}: {row['qtd_ativos']} ativos, {row['qtd_desligados']} deslig.")
    return df


def processar_fato_movimentacoes(dim_colab: pd.DataFrame) -> pd.DataFrame:
    """Cria fato_Movimentacoes_RH com uma linha por admissão e uma por desligamento."""
    print("\n[4/6] fato_Movimentacoes_RH.csv")

    rows = []
    mov_id = 0

    for _, r in dim_colab.iterrows():
        # Admissão
        if pd.notna(r["data_admissao"]):
            mov_id += 1
            d = r["data_admissao"]
            rows.append({
                "movimentacao_id": mov_id,
                "colaborador_id": r["colaborador_id"],
                "data": d,
                "ano": d.year,
                "mes": d.month,
                "tipo": "Admissão",
                "empresa": r["empresa"],
                "funcao": r["funcao"],
                "setor_rh": r["setor_rh"],
                "unidade_inferida": r["unidade_inferida"],
            })

        # Desligamento
        if pd.notna(r["data_rescisao"]):
            mov_id += 1
            d = r["data_rescisao"]
            rows.append({
                "movimentacao_id": mov_id,
                "colaborador_id": r["colaborador_id"],
                "data": d,
                "ano": d.year,
                "mes": d.month,
                "tipo": "Desligamento",
                "empresa": r["empresa"],
                "funcao": r["funcao"],
                "setor_rh": r["setor_rh"],
                "unidade_inferida": r["unidade_inferida"],
            })

    df = pd.DataFrame(rows)
    adm = (df["tipo"] == "Admissão").sum()
    desl = (df["tipo"] == "Desligamento").sum()
    print(f"  {len(df)} movimentações ({adm} admissões + {desl} desligamentos)")
    return df


def processar_fato_quadro_atual(dim_colab: pd.DataFrame) -> pd.DataFrame:
    """Cria fato_Quadro_Atual com snapshot dos ativos e faixas calculadas."""
    print("\n[5/6] fato_Quadro_Atual.csv")

    ativos = dim_colab[dim_colab["status"] == "Ativo"].copy()

    df = pd.DataFrame()
    df["colaborador_id"] = ativos["colaborador_id"].values
    df["nome"] = ativos["nome"].values
    df["empresa"] = ativos["empresa"].values
    df["funcao"] = ativos["funcao"].values
    df["funcao_normalizada"] = ativos["funcao_normalizada"].values
    df["setor_rh"] = ativos["setor_rh"].values
    df["unidade_inferida"] = ativos["unidade_inferida"].values
    df["salario_base"] = ativos["salario_base"].values
    df["horas_semana"] = ativos["horas_semana"].values
    df["tempo_casa_meses"] = ativos["tempo_casa_meses"].values
    df["idade"] = ativos["idade"].values
    df["sexo"] = ativos["sexo"].values
    df["grau_instrucao"] = ativos["grau_instrucao"].values

    df["faixa_salarial"] = df["salario_base"].apply(faixa_salarial)
    df["faixa_tempo"] = df["tempo_casa_meses"].apply(faixa_tempo)
    df["faixa_etaria"] = df["idade"].apply(faixa_etaria)

    sal_total = df["salario_base"].sum()
    sal_medio = df["salario_base"].mean()
    print(f"  {len(df)} colaboradores ativos")
    print(f"  Salário total mensal: R$ {sal_total:,.2f}")
    print(f"  Salário médio: R$ {sal_medio:,.2f}")
    print(f"  Faixas salariais: {df['faixa_salarial'].value_counts().to_dict()}")
    print(f"  Faixas tempo: {df['faixa_tempo'].value_counts().to_dict()}")

    return df


def processar_headcount_mensal(fato_mov: pd.DataFrame) -> pd.DataFrame:
    """Calcula headcount mensal por empresa e setor (série temporal)."""
    print("\n[6/6] resumo_Headcount_Mensal.csv")

    if fato_mov.empty:
        return pd.DataFrame(columns=["ano_mes", "empresa", "setor_rh", "headcount"])

    # Range de meses
    fato_mov["data"] = pd.to_datetime(fato_mov["data"])
    min_date = fato_mov["data"].min()
    max_date = fato_mov["data"].max()

    meses = pd.date_range(
        start=min_date.replace(day=1),
        end=max_date.replace(day=1),
        freq="MS"
    )

    rows = []
    empresas = sorted(fato_mov["empresa"].dropna().unique())
    setores = sorted(fato_mov["setor_rh"].dropna().unique())

    for emp in empresas:
        for setor in setores:
            subset = fato_mov[
                (fato_mov["empresa"] == emp) & (fato_mov["setor_rh"] == setor)
            ]
            if subset.empty:
                continue

            for mes in meses:
                fim_mes = mes + pd.offsets.MonthEnd(0)
                adm_ate = subset[
                    (subset["tipo"] == "Admissão") & (subset["data"] <= fim_mes)
                ].shape[0]
                desl_ate = subset[
                    (subset["tipo"] == "Desligamento") & (subset["data"] <= fim_mes)
                ].shape[0]
                hc = adm_ate - desl_ate
                if hc != 0:
                    rows.append({
                        "ano_mes": mes.strftime("%Y-%m"),
                        "empresa": emp,
                        "setor_rh": setor,
                        "headcount": hc,
                    })

    df = pd.DataFrame(rows)

    # Também gerar totais agregados (sem empresa/setor) para gráfico de linha geral
    for mes in meses:
        fim_mes = mes + pd.offsets.MonthEnd(0)
        adm_ate = fato_mov[
            (fato_mov["tipo"] == "Admissão") & (fato_mov["data"] <= fim_mes)
        ].shape[0]
        desl_ate = fato_mov[
            (fato_mov["tipo"] == "Desligamento") & (fato_mov["data"] <= fim_mes)
        ].shape[0]
        hc = adm_ate - desl_ate
        if hc != 0:
            rows.append({
                "ano_mes": mes.strftime("%Y-%m"),
                "empresa": "_TOTAL",
                "setor_rh": "_TOTAL",
                "headcount": hc,
            })

    df = pd.DataFrame(rows)
    n_meses = df["ano_mes"].nunique()
    print(f"  {len(df)} linhas cobrindo {n_meses} meses")
    if not df.empty:
        ultimo = df[df["empresa"] == "_TOTAL"].sort_values("ano_mes").iloc[-1]
        print(f"  Headcount mais recente ({ultimo['ano_mes']}): {ultimo['headcount']}")

    return df


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Dashboard RH Power BI - Colégio ELO")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Carregar dados
    print("\n── Carregando dados ──")
    df_xls = carregar_xls()
    prof_map = carregar_mapa_professores()

    # Processar tabelas
    print("\n── Processando tabelas ──")
    dim_colab = processar_dim_colaboradores(df_xls, prof_map)
    dim_setores = processar_dim_setores()
    dim_empresas = processar_dim_empresas(dim_colab)
    fato_mov = processar_fato_movimentacoes(dim_colab)
    fato_quadro = processar_fato_quadro_atual(dim_colab)
    headcount = processar_headcount_mensal(fato_mov)

    # Salvar CSVs
    print("\n── Salvando CSVs ──")
    arquivos = [
        ("dim_Colaboradores.csv", dim_colab),
        ("dim_Setores_RH.csv", dim_setores),
        ("dim_Empresas_RH.csv", dim_empresas),
        ("fato_Movimentacoes_RH.csv", fato_mov),
        ("fato_Quadro_Atual.csv", fato_quadro),
        ("resumo_Headcount_Mensal.csv", headcount),
    ]

    for nome, tabela in arquivos:
        path = os.path.join(OUTPUT_DIR, nome)
        tabela.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"  ✓ {nome}: {len(tabela)} linhas")

    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    ativos = dim_colab[dim_colab["status"] == "Ativo"]
    print(f"  Total registros:    {len(dim_colab)}")
    print(f"  Ativos:             {len(ativos)}")
    print(f"  Desligados:         {len(dim_colab) - len(ativos)}")
    print(f"  Empresas:           {dim_colab['empresa'].nunique()}")
    print(f"  Movimentações:      {len(fato_mov)}")
    print(f"  Salário total/mês:  R$ {ativos['salario_base'].sum():,.2f}")
    print(f"  Salário médio:      R$ {ativos['salario_base'].mean():,.2f}")
    print(f"  Setores RH:         {dim_setores['setor_rh'].tolist()}")
    print(f"  Headcount linhas:   {len(headcount)}")

    # Validações
    print("\n── Validações ──")
    ok = True

    # V1: 1686 registros
    if len(dim_colab) != 1686:
        print(f"  ⚠ dim_Colaboradores: {len(dim_colab)} (esperado 1686)")
        ok = False
    else:
        print(f"  ✓ dim_Colaboradores: 1686 registros")

    # V2: 537 ativos (538 raw menos 1 linha em branco no XLS)
    if len(ativos) != 537:
        print(f"  ⚠ Ativos: {len(ativos)} (esperado 537)")
        ok = False
    else:
        print(f"  ✓ 537 ativos (538 raw - 1 linha em branco)")

    # V3: fato_Quadro_Atual = 537
    if len(fato_quadro) != 537:
        print(f"  ⚠ fato_Quadro_Atual: {len(fato_quadro)} (esperado 537)")
        ok = False
    else:
        print(f"  ✓ fato_Quadro_Atual: 537 linhas")

    # V4: 11 empresas
    if dim_colab["empresa"].nunique() != 11:
        print(f"  ⚠ Empresas: {dim_colab['empresa'].nunique()} (esperado 11)")
        ok = False
    else:
        print(f"  ✓ 11 empresas")

    # V5: 7 setores
    if dim_setores.shape[0] != 7:
        print(f"  ⚠ Setores: {dim_setores.shape[0]} (esperado 7)")
    else:
        print(f"  ✓ 7 setores RH")

    if ok:
        print("\n  ✅ Todas as validações passaram!")
    else:
        print("\n  ⚠ Algumas validações falharam (ver acima)")

    print(f"\n  Arquivos salvos em: {OUTPUT_DIR}/")
    print("  Pronto para importar no Power BI Desktop!")


if __name__ == "__main__":
    main()
