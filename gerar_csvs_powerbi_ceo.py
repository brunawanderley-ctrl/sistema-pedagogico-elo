#!/usr/bin/env python3
"""
GERADOR DE CSVs PRÉ-CALCULADOS PARA POWER BI - CEO COORDENAÇÃO
Gera 3 tabelas calculadas para o dashboard de 5 páginas:
  1. score_Professor.csv  - Score composto por professor
  2. score_Aluno_ABC.csv  - Classificação ABC de risco por aluno
  3. resumo_Executivo.csv - KPIs agregados por unidade/semana
"""

import pandas as pd
import numpy as np
import re
import math
from pathlib import Path
from datetime import date

# ========== CONFIGURAÇÃO ==========
POWER_BI_DIR = Path(__file__).parent / "power_bi"
INICIO_LETIVO = date(2026, 1, 26)
HOJE = date.today()


def semana_letiva(dt=None):
    """Calcula semana letiva a partir de 26/01/2026."""
    if dt is None:
        dt = HOJE
    if isinstance(dt, str):
        dt = pd.to_datetime(dt).date()
    return max(1, (dt - INICIO_LETIVO).days // 7 + 1)


def capitulo_esperado(semana):
    """Capítulo SAE esperado - SWITCH calibrado calendário 205 dias."""
    if semana is None or semana < 1:
        return 1
    if semana <= 4: return 1
    elif semana <= 8: return 2
    elif semana <= 12: return 3
    elif semana <= 15: return 4
    elif semana <= 18: return 5
    elif semana <= 22: return 6
    elif semana <= 30: return 7   # inclui férias julho (sem 23-27)
    elif semana <= 33: return 8
    elif semana <= 37: return 9
    elif semana <= 40: return 10
    elif semana <= 43: return 11
    else: return 12


SEMANA_ATUAL = semana_letiva()
CAP_ATUAL = capitulo_esperado(SEMANA_ATUAL)

print(f"Data: {HOJE} | Semana letiva: {SEMANA_ATUAL} | Capítulo esperado: {CAP_ATUAL}")
print(f"Diretório Power BI: {POWER_BI_DIR}")
print("=" * 70)


# ========== CARREGAR DADOS BASE ==========
def carregar(nome):
    """Carrega CSV do diretório power_bi."""
    path = POWER_BI_DIR / nome
    if path.exists():
        df = pd.read_csv(path, encoding="utf-8-sig")
        print(f"  Carregado {nome}: {len(df)} registros")
        return df
    print(f"  AVISO: {nome} não encontrado")
    return pd.DataFrame()


print("\nCarregando dados base...")
df_aulas = carregar("fato_Aulas.csv")
df_esperadas = carregar("resumo_Aulas_Esperadas.csv")
df_progressao = carregar("dim_Progressao_SAE.csv")
df_alunos = carregar("dim_Alunos.csv")
df_notas = carregar("fato_Notas_Historico.csv")
df_ocorrencias = carregar("fato_Ocorrencias.csv")
df_cruzamento = carregar("fato_Cruzamento.csv")
df_engajamento = carregar("fato_Engajamento_SAE.csv")
df_disciplinas = carregar("dim_Disciplinas.csv")
df_calendario = carregar("dim_Calendario.csv")
df_freq_chamada = carregar("fato_Frequencia_Aluno.csv")


# ========================================================================
# 1. SCORE PROFESSOR
# ========================================================================
def gerar_score_professor():
    """
    Calcula score composto por professor:
    - Conformidade (40%): aulas registradas / aulas esperadas
    - Alinhamento SAE (25%): capítulo registrado vs esperado
    - Qualidade registro (20%): % de aulas com conteúdo real (não ".")
    - Uso de tarefas (15%): % de aulas com tarefa preenchida
    """
    print("\n" + "=" * 70)
    print("1. GERANDO score_Professor.csv")
    print("=" * 70)

    if df_aulas.empty or df_esperadas.empty:
        print("  ERRO: fato_Aulas ou resumo_Aulas_Esperadas vazio")
        return

    # Filtrar apenas aulas até hoje
    aulas = df_aulas.copy()
    aulas["data"] = pd.to_datetime(aulas["data"])
    aulas = aulas[aulas["data"] <= pd.Timestamp(HOJE)]

    # --- A) CONFORMIDADE (aulas registradas / esperadas) ---
    # Contar aulas registradas por professor/unidade/disciplina/serie
    aulas_por_prof = (
        aulas.groupby(["professor_normalizado", "unidade", "disciplina", "serie"])
        .agg(
            aulas_registradas=("aula_id", "count"),
            professor_nome=("professor", "first"),
        )
        .reset_index()
    )

    # Calcular aulas esperadas até a semana atual
    esperadas = df_esperadas.copy()
    esperadas["aulas_esperadas_ate_agora"] = esperadas["aulas_esperadas_semana"] * SEMANA_ATUAL

    # Merge
    score = aulas_por_prof.merge(
        esperadas[["unidade", "serie", "disciplina", "aulas_esperadas_semana"]],
        on=["unidade", "serie", "disciplina"],
        how="left",
    )
    score["aulas_esperadas_ate_agora"] = score["aulas_esperadas_semana"].fillna(0) * SEMANA_ATUAL
    score["pct_conformidade"] = np.where(
        score["aulas_esperadas_ate_agora"] > 0,
        (score["aulas_registradas"] / score["aulas_esperadas_ate_agora"] * 100).clip(0, 100),
        0,
    )

    # --- B) QUALIDADE DO REGISTRO ---
    def conteudo_vazio(txt):
        if pd.isna(txt):
            return True
        txt = str(txt).strip()
        return txt in ("", ".", "..", ",", "-", "--", "...", "s/c", "S/C", "sem conteúdo")

    def tarefa_preenchida(txt):
        if pd.isna(txt):
            return False
        txt = str(txt).strip()
        return txt not in ("", ".", "..", ",", "-", "--", "...", "s/t", "S/T", "sem tarefa")

    aulas["conteudo_ok"] = ~aulas["conteudo"].apply(conteudo_vazio)
    aulas["tarefa_ok"] = aulas["tarefa"].apply(tarefa_preenchida)

    qualidade = (
        aulas.groupby(["professor_normalizado", "unidade", "disciplina", "serie"])
        .agg(
            pct_qualidade_conteudo=("conteudo_ok", "mean"),
            pct_uso_tarefas=("tarefa_ok", "mean"),
        )
        .reset_index()
    )
    qualidade["pct_qualidade_conteudo"] = (qualidade["pct_qualidade_conteudo"] * 100).round(1)
    qualidade["pct_uso_tarefas"] = (qualidade["pct_uso_tarefas"] * 100).round(1)

    score = score.merge(
        qualidade,
        on=["professor_normalizado", "unidade", "disciplina", "serie"],
        how="left",
    )

    # --- C) ALINHAMENTO SAE ---
    # Detectar capítulo no conteúdo
    def detectar_capitulo(txt):
        if pd.isna(txt):
            return None
        txt = str(txt)
        # Padrões: "Cap. 1", "Capítulo 3", "cap 2", "Cap.1"
        match = re.search(r"[Cc]ap(?:ítulo|\.?\s*)(\d{1,2})", txt)
        if match:
            return int(match.group(1))
        return None

    aulas["cap_detectado"] = aulas["conteudo"].apply(detectar_capitulo)

    # Capítulo mais recente por professor/disciplina/serie
    caps_prof = (
        aulas.dropna(subset=["cap_detectado"])
        .sort_values("data", ascending=False)
        .groupby(["professor_normalizado", "unidade", "disciplina", "serie"])
        .agg(cap_mais_recente=("cap_detectado", "first"))
        .reset_index()
    )

    score = score.merge(
        caps_prof,
        on=["professor_normalizado", "unidade", "disciplina", "serie"],
        how="left",
    )

    # Verificar se disciplina tem SAE (capitulos_ano > 0)
    disc_sae = df_disciplinas[df_disciplinas["capitulos_ano"] > 0]["disciplina"].tolist()
    score["tem_sae"] = score["disciplina"].isin(disc_sae)

    # Gap de alinhamento (positivo = adiantado, negativo = atrasado)
    score["gap_alinhamento"] = np.where(
        score["tem_sae"] & score["cap_mais_recente"].notna(),
        score["cap_mais_recente"] - CAP_ATUAL,
        np.nan,
    )

    # Score de alinhamento (100 = perfeito, 0 = muito atrasado)
    score["pct_alinhamento"] = np.where(
        score["gap_alinhamento"].notna(),
        np.clip(100 - (np.abs(score["gap_alinhamento"]) * 25), 0, 100),
        np.nan,
    )

    # --- D) SCORE COMPOSTO ---
    # Pesos: Conformidade 40%, Alinhamento 25%, Qualidade 20%, Tarefas 15%
    score["pct_qualidade_conteudo"] = score["pct_qualidade_conteudo"].fillna(0)
    score["pct_uso_tarefas"] = score["pct_uso_tarefas"].fillna(0)

    score["score_composto"] = (
        score["pct_conformidade"] * 0.40
        + score["pct_alinhamento"].fillna(score["pct_conformidade"]) * 0.25
        + score["pct_qualidade_conteudo"] * 0.20
        + score["pct_uso_tarefas"] * 0.15
    ).round(1)

    # --- E) CLASSIFICAÇÃO ---
    def classificar_professor(row):
        s = row["score_composto"]
        if s >= 85:
            return "Excelente"
        elif s >= 70:
            return "Bom"
        elif s >= 50:
            return "Atenção"
        else:
            return "Crítico"

    score["classificacao"] = score.apply(classificar_professor, axis=1)

    # Quadrante estratégico (para scatter plot)
    score["quadrante"] = np.where(
        (score["pct_conformidade"] >= 70) & (score["pct_alinhamento"].fillna(70) >= 70),
        "Q1 - Excelente",
        np.where(
            (score["pct_conformidade"] < 70) & (score["pct_alinhamento"].fillna(70) >= 70),
            "Q2 - Registra pouco",
            np.where(
                (score["pct_conformidade"] >= 70) & (score["pct_alinhamento"].fillna(70) < 70),
                "Q3 - Fora do ritmo",
                "Q4 - Crítico",
            ),
        ),
    )

    # Selecionar colunas finais
    cols_final = [
        "professor_normalizado",
        "professor_nome",
        "unidade",
        "disciplina",
        "serie",
        "aulas_registradas",
        "aulas_esperadas_semana",
        "aulas_esperadas_ate_agora",
        "pct_conformidade",
        "pct_qualidade_conteudo",
        "pct_uso_tarefas",
        "cap_mais_recente",
        "tem_sae",
        "gap_alinhamento",
        "pct_alinhamento",
        "score_composto",
        "classificacao",
        "quadrante",
    ]
    score = score[[c for c in cols_final if c in score.columns]]
    score = score.round(1)

    # Salvar
    output = POWER_BI_DIR / "score_Professor.csv"
    score.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"\n  Salvo: {output}")
    print(f"  Total: {len(score)} registros (professor x disciplina x série x unidade)")
    print(f"  Classificação:")
    print(score["classificacao"].value_counts().to_string(header=False))
    print(f"  Quadrante:")
    print(score["quadrante"].value_counts().to_string(header=False))

    return score


# ========================================================================
# 2. SCORE ALUNO ABC
# ========================================================================
def gerar_score_aluno_abc():
    """
    Calcula score ABC (Attendance-Behavior-Coursework) por aluno:
    - A (Frequência): dados de chamada 2026 (fato_Frequencia_Aluno.csv), fallback histórico
    - B (Comportamento): contagem e gravidade de ocorrências (filtrado 2026)
    - C (Desempenho): média de notas (histórico 2025)
    - Tier: 0 (verde), 1 (monitorar), 2 (atenção), 3 (crítico)
    """
    print("\n" + "=" * 70)
    print("2. GERANDO score_Aluno_ABC.csv")
    print("=" * 70)

    if df_alunos.empty:
        print("  ERRO: dim_Alunos vazio")
        return

    # Filtrar apenas alunos efetivamente cursando
    alunos = df_alunos[
        df_alunos["situacao"] == "Cursando"
    ].copy()
    print(f"  Alunos cursando: {len(alunos)}")

    # --- A) FREQUÊNCIA (chamada 2026, fallback histórico) ---
    freq_data = pd.DataFrame()
    freq_source_default = "sem_dados"

    # Tentar dados de chamada 2026 primeiro
    if not df_freq_chamada.empty:
        print("  [Eixo A] Usando fato_Frequencia_Aluno.csv (chamada 2026)")
        fc = df_freq_chamada.copy()
        # Filtrar apenas registros com chamada feita (P, F ou J)
        # Ignorar registros sem presença registrada (NaN = chamada não feita)
        fc_validos = fc[fc["presenca"].isin(["P", "F", "J"])].copy()
        print(f"    Registros com chamada feita: {len(fc_validos)} de {len(fc)}")

        # Calcular frequência por aluno:
        # Presente = P, Falta = F, Falta Justificada = J
        # % frequência = P / (P + F + J) * 100
        freq_aluno_chamada = (
            fc_validos.groupby("aluno_id")
            .agg(
                presentes=("presenca", lambda x: (x == "P").sum()),
                faltas=("presenca", lambda x: (x == "F").sum()),
                justificadas=("presenca", lambda x: (x == "J").sum()),
                total_chamadas=("presenca", "count"),
            )
            .reset_index()
        )
        freq_aluno_chamada["pct_frequencia"] = np.where(
            freq_aluno_chamada["total_chamadas"] > 0,
            (freq_aluno_chamada["presentes"] / freq_aluno_chamada["total_chamadas"] * 100).clip(0, 100),
            np.nan,
        )
        freq_aluno_chamada["total_faltas"] = freq_aluno_chamada["faltas"] + freq_aluno_chamada["justificadas"]
        freq_aluno_chamada["freq_source"] = "chamada_2026"

        freq_data = freq_aluno_chamada[["aluno_id", "pct_frequencia", "total_faltas", "freq_source"]].copy()
        freq_source_default = "chamada_2026"

        n_alunos_freq = freq_aluno_chamada["aluno_id"].nunique()
        print(f"    Alunos com dados de chamada: {n_alunos_freq}")
        print(f"    Frequência média: {freq_aluno_chamada['pct_frequencia'].mean():.1f}%")
    else:
        print("  [Eixo A] AVISO: fato_Frequencia_Aluno.csv não encontrado")

    # Fallback: preencher alunos sem dados de chamada com histórico
    fallback_count = 0
    if not df_notas.empty:
        notas = df_notas.copy()
        anos_disponiveis = notas["ano"].dropna().unique()
        ano_recente = max(anos_disponiveis) if len(anos_disponiveis) > 0 else 2025
        print(f"  [Eixo A fallback] Ano histórico disponível: {ano_recente}")

        notas_ano = notas[notas["ano"] == ano_recente].copy()
        notas_ano["carga_horaria"] = pd.to_numeric(notas_ano["carga_horaria"], errors="coerce")
        notas_ano["faltas"] = pd.to_numeric(notas_ano["faltas"], errors="coerce")

        freq_hist = (
            notas_ano.groupby("aluno_id")
            .agg(
                total_faltas=("faltas", "sum"),
                total_carga=("carga_horaria", "sum"),
            )
            .reset_index()
        )
        freq_hist["pct_frequencia"] = np.where(
            freq_hist["total_carga"] > 0,
            ((freq_hist["total_carga"] - freq_hist["total_faltas"]) / freq_hist["total_carga"] * 100).clip(0, 100),
            np.nan,
        )
        freq_hist["freq_source"] = "historico_2025"
        freq_hist = freq_hist[["aluno_id", "pct_frequencia", "total_faltas", "freq_source"]].copy()

        if not freq_data.empty:
            # Apenas preencher alunos que NÃO têm dados de chamada 2026
            alunos_com_chamada = set(freq_data["aluno_id"].tolist())
            freq_hist_faltantes = freq_hist[~freq_hist["aluno_id"].isin(alunos_com_chamada)]
            fallback_count = len(freq_hist_faltantes)
            if not freq_hist_faltantes.empty:
                freq_data = pd.concat([freq_data, freq_hist_faltantes], ignore_index=True)
                print(f"    Alunos completados com histórico (fallback): {fallback_count}")
        else:
            freq_data = freq_hist
            freq_source_default = "historico_2025"
            fallback_count = len(freq_hist)
            print(f"    Usando APENAS histórico: {fallback_count} alunos")

    # --- B) COMPORTAMENTO (filtrado para 2026) ---
    ocorr_data = pd.DataFrame()
    if not df_ocorrencias.empty:
        ocorr = df_ocorrencias.copy()
        ocorr["data"] = pd.to_datetime(ocorr["data"], errors="coerce")

        # Filtrar apenas ocorrências de 2026 (a partir do início do ano letivo)
        ocorr = ocorr[ocorr["data"] >= "2026-01-27"].copy()
        print(f"  [Eixo B] Ocorrências 2026 (>= 27/01): {len(ocorr)}")

        # Peso por gravidade
        peso_gravidade = {"Leve": 1, "Media": 2, "Grave": 5}
        ocorr["peso"] = ocorr["gravidade"].map(peso_gravidade).fillna(1)

        # Excluir ocorrências puramente administrativas
        ocorr_disc = ocorr[ocorr["categoria"] != "Administrativo"].copy()

        ocorr_aluno = (
            ocorr_disc.groupby("aluno_id")
            .agg(
                total_ocorrencias=("ocorrencia_id", "count"),
                ocorr_graves=("gravidade", lambda x: (x == "Grave").sum()),
                ocorr_medias=("gravidade", lambda x: (x == "Media").sum()),
                ocorr_leves=("gravidade", lambda x: (x == "Leve").sum()),
                score_comportamento=("peso", "sum"),
            )
            .reset_index()
        )
        ocorr_data = ocorr_aluno

    # --- C) DESEMPENHO (NOTAS) - histórico 2025 ---
    notas_data = pd.DataFrame()
    flag_c_source = "sem_dados"
    if not df_notas.empty:
        notas = df_notas.copy()
        anos_disponiveis = notas["ano"].dropna().unique()
        ano_recente = max(anos_disponiveis) if len(anos_disponiveis) > 0 else 2025
        flag_c_source = f"historico_{ano_recente}"

        notas_ano = notas[notas["ano"] == ano_recente].copy()
        notas_ano["nota_final"] = pd.to_numeric(notas_ano["nota_final"], errors="coerce")

        # Média por aluno
        notas_aluno = (
            notas_ano.groupby("aluno_id")
            .agg(
                media_geral=("nota_final", "mean"),
                menor_nota=("nota_final", "min"),
                disciplinas_abaixo_5=("nota_final", lambda x: (x < 5).sum()),
                total_disciplinas=("nota_final", "count"),
            )
            .reset_index()
        )
        notas_data = notas_aluno

    # --- MONTAR TABELA FINAL ---
    resultado = alunos[["aluno_id", "aluno_nome", "unidade", "serie", "turma", "segmento"]].copy()

    if not freq_data.empty:
        resultado = resultado.merge(freq_data, on="aluno_id", how="left")
    else:
        resultado["pct_frequencia"] = np.nan
        resultado["total_faltas"] = 0
        resultado["freq_source"] = "sem_dados"

    # Preencher freq_source para alunos sem nenhum dado
    resultado["freq_source"] = resultado["freq_source"].fillna("sem_dados")
    # Corrigir: se pct_frequencia é NaN, a fonte é efetivamente "sem_dados"
    resultado.loc[resultado["pct_frequencia"].isna(), "freq_source"] = "sem_dados"

    if not ocorr_data.empty:
        resultado = resultado.merge(ocorr_data, on="aluno_id", how="left")
        resultado["total_ocorrencias"] = resultado["total_ocorrencias"].fillna(0).astype(int)
        resultado["score_comportamento"] = resultado["score_comportamento"].fillna(0)
    else:
        resultado["total_ocorrencias"] = 0
        resultado["score_comportamento"] = 0

    if not notas_data.empty:
        resultado = resultado.merge(notas_data, on="aluno_id", how="left")
    else:
        resultado["media_geral"] = np.nan

    # Rastreabilidade de fontes
    resultado["flag_C_source"] = np.where(
        resultado["media_geral"].notna(), flag_c_source, "sem_dados"
    )

    # --- CALCULAR FLAGS ABC ---
    # A - Attendance (Frequência)
    # OK: >= 85% | Alerta: 70-85% | Risco: < 70% | Sem dados: NaN
    resultado["flag_A"] = np.where(
        resultado["pct_frequencia"].isna(), "Sem dados",
        np.where(resultado["pct_frequencia"] < 70, "Risco",
                 np.where(resultado["pct_frequencia"] < 85, "Alerta", "OK"))
    )

    # B - Behavior (Comportamento)
    resultado["flag_B"] = np.where(
        resultado["total_ocorrencias"] >= 5, "Crítico",
        np.where(resultado["total_ocorrencias"] >= 2, "Risco", "OK")
    )

    # C - Coursework (Desempenho)
    resultado["flag_C"] = np.where(
        resultado["media_geral"].isna(), "Sem dados",
        np.where(resultado["media_geral"] < 3.0, "Crítico",
                 np.where(resultado["media_geral"] < 5.0, "Risco", "OK"))
    )

    # --- TIER DE RISCO ---
    def calcular_tier(row):
        flags_critico = sum(1 for f in [row["flag_A"], row["flag_B"], row["flag_C"]]
                           if f in ("Crítico", "Risco"))
        flags_alerta = sum(1 for f in [row["flag_A"], row["flag_B"], row["flag_C"]]
                          if f == "Alerta")

        if flags_critico >= 2:
            return 3  # Crítico
        elif flags_critico >= 1 and flags_alerta >= 1:
            return 2  # Atenção
        elif flags_critico >= 1:
            return 2  # Atenção
        elif flags_alerta >= 2:
            return 1  # Monitorar
        elif flags_alerta >= 1:
            return 1  # Monitorar
        else:
            return 0  # Verde

    resultado["tier"] = resultado.apply(calcular_tier, axis=1)

    tier_labels = {0: "Verde", 1: "Monitorar", 2: "Atenção", 3: "Crítico"}
    resultado["tier_label"] = resultado["tier"].map(tier_labels)

    # Tipo de intervenção sugerido
    def tipo_intervencao(row):
        tipos = []
        if row["flag_A"] in ("Risco", "Crítico", "Alerta"):
            tipos.append("Frequência → Família")
        if row["flag_B"] in ("Risco", "Crítico"):
            tipos.append("Comportamento → Orientação")
        if row["flag_C"] in ("Risco", "Crítico"):
            tipos.append("Acadêmico → Reforço")
        return " | ".join(tipos) if tipos else "Nenhuma"

    resultado["intervencao_sugerida"] = resultado.apply(tipo_intervencao, axis=1)

    # Arredondar
    for col in ["pct_frequencia", "media_geral", "menor_nota"]:
        if col in resultado.columns:
            resultado[col] = resultado[col].round(1)

    # Selecionar colunas
    cols = [
        "aluno_id", "aluno_nome", "unidade", "serie", "turma", "segmento",
        "pct_frequencia", "total_faltas", "freq_source",
        "total_ocorrencias", "ocorr_graves", "ocorr_medias", "ocorr_leves", "score_comportamento",
        "media_geral", "menor_nota", "disciplinas_abaixo_5", "total_disciplinas", "flag_C_source",
        "flag_A", "flag_B", "flag_C",
        "tier", "tier_label", "intervencao_sugerida",
    ]
    resultado = resultado[[c for c in cols if c in resultado.columns]]

    # Salvar
    output = POWER_BI_DIR / "score_Aluno_ABC.csv"
    resultado.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"\n  Salvo: {output}")
    print(f"  Total: {len(resultado)} alunos")
    print(f"\n  Cobertura de frequência:")
    print(resultado["freq_source"].value_counts().to_string(header=False))
    print(f"  Alunos SEM dados de freq: {(resultado['freq_source'] == 'sem_dados').sum()}")
    print(f"\n  Distribuição flag_A:")
    print(resultado["flag_A"].value_counts().to_string(header=False))
    print(f"\n  Distribuição por Tier:")
    print(resultado["tier_label"].value_counts().to_string(header=False))
    print(f"\n  Por Unidade:")
    print(resultado.groupby("unidade")["tier"].mean().round(2).to_string(header=False))

    return resultado


# ========================================================================
# 3. RESUMO EXECUTIVO
# ========================================================================
def gerar_resumo_executivo(score_prof=None, score_abc=None):
    """
    Gera resumo executivo semanal por unidade para a página 1 (Pulso da Escola).
    KPIs: conformidade, frequência, notas, conteúdo, alunos em risco.
    """
    print("\n" + "=" * 70)
    print("3. GERANDO resumo_Executivo.csv")
    print("=" * 70)

    unidades = ["BV", "CD", "JG", "CDR"]
    registros = []

    for unidade in unidades:
        row = {"unidade": unidade, "semana_atual": SEMANA_ATUAL, "capitulo_esperado": CAP_ATUAL}

        # KPI 1: % Conformidade (professores)
        if score_prof is not None and not score_prof.empty:
            profs_u = score_prof[score_prof["unidade"] == unidade]
            row["pct_conformidade_media"] = profs_u["pct_conformidade"].mean()
            row["pct_conformidade_mediana"] = profs_u["pct_conformidade"].median()
            row["total_professores"] = profs_u["professor_normalizado"].nunique()
            row["professores_criticos"] = (profs_u.groupby("professor_normalizado")["score_composto"].mean() < 50).sum()
            row["professores_excelentes"] = (profs_u.groupby("professor_normalizado")["score_composto"].mean() >= 85).sum()
            row["pct_prof_no_ritmo"] = (
                (profs_u.groupby("professor_normalizado")["pct_conformidade"].mean() >= 70).sum()
                / max(1, profs_u["professor_normalizado"].nunique())
                * 100
            )
        else:
            row["pct_conformidade_media"] = 0
            row["total_professores"] = 0

        # KPI 2: % Alunos com frequência OK
        if score_abc is not None and not score_abc.empty:
            alunos_u = score_abc[score_abc["unidade"] == unidade]
            row["total_alunos"] = len(alunos_u)
            freq_ok = alunos_u["pct_frequencia"].notna()
            if freq_ok.sum() > 0:
                row["pct_freq_acima_75"] = (alunos_u.loc[freq_ok, "pct_frequencia"] >= 75).sum() / freq_ok.sum() * 100
                row["pct_freq_acima_90"] = (alunos_u.loc[freq_ok, "pct_frequencia"] >= 90).sum() / freq_ok.sum() * 100
                row["frequencia_media"] = alunos_u.loc[freq_ok, "pct_frequencia"].mean()
            else:
                row["pct_freq_acima_75"] = np.nan
                row["pct_freq_acima_90"] = np.nan
                row["frequencia_media"] = np.nan

            # KPI 3: Média de notas
            notas_ok = alunos_u["media_geral"].notna()
            row["media_notas"] = alunos_u.loc[notas_ok, "media_geral"].mean() if notas_ok.sum() > 0 else np.nan

            # KPI 5: Alunos em risco
            row["alunos_tier_0"] = (alunos_u["tier"] == 0).sum()
            row["alunos_tier_1"] = (alunos_u["tier"] == 1).sum()
            row["alunos_tier_2"] = (alunos_u["tier"] == 2).sum()
            row["alunos_tier_3"] = (alunos_u["tier"] == 3).sum()
            row["pct_alunos_risco"] = (
                (alunos_u["tier"] >= 2).sum() / max(1, len(alunos_u)) * 100
            )
        else:
            row["total_alunos"] = 0

        # KPI 4: % Aulas com conteúdo preenchido
        if not df_aulas.empty:
            aulas_u = df_aulas[df_aulas["unidade"] == unidade].copy()
            aulas_u["data"] = pd.to_datetime(aulas_u["data"])
            aulas_u = aulas_u[aulas_u["data"] <= pd.Timestamp(HOJE)]
            if len(aulas_u) > 0:
                def conteudo_real(txt):
                    if pd.isna(txt):
                        return False
                    txt = str(txt).strip()
                    return txt not in ("", ".", "..", ",", "-", "--", "...", "s/c")
                row["total_aulas"] = len(aulas_u)
                row["pct_conteudo_preenchido"] = aulas_u["conteudo"].apply(conteudo_real).mean() * 100
            else:
                row["total_aulas"] = 0
                row["pct_conteudo_preenchido"] = 0

        # KPI: Ocorrências
        if not df_ocorrencias.empty:
            ocorr_u = df_ocorrencias[df_ocorrencias["unidade"] == unidade]
            row["total_ocorrencias"] = len(ocorr_u)
            row["ocorr_graves"] = (ocorr_u["gravidade"] == "Grave").sum()
        else:
            row["total_ocorrencias"] = 0

        # Semáforo da unidade
        conf = row.get("pct_conformidade_media", 0) or 0
        if conf >= 85:
            row["semaforo"] = "Verde"
        elif conf >= 70:
            row["semaforo"] = "Amarelo"
        else:
            row["semaforo"] = "Vermelho"

        registros.append(row)

    # Adicionar linha TOTAL
    df_resumo = pd.DataFrame(registros)

    totais = {
        "unidade": "TOTAL",
        "semana_atual": SEMANA_ATUAL,
        "capitulo_esperado": CAP_ATUAL,
    }
    for col in df_resumo.select_dtypes(include=[np.number]).columns:
        if col in ("semana_atual", "capitulo_esperado"):
            continue
        if "pct_" in col or "media" in col or "frequencia" in col:
            totais[col] = df_resumo[col].mean()
        else:
            totais[col] = df_resumo[col].sum()
    totais["semaforo"] = "Verde" if totais.get("pct_conformidade_media", 0) >= 85 else (
        "Amarelo" if totais.get("pct_conformidade_media", 0) >= 70 else "Vermelho"
    )
    df_resumo = pd.concat([df_resumo, pd.DataFrame([totais])], ignore_index=True)

    # Arredondar
    for col in df_resumo.select_dtypes(include=[np.number]).columns:
        df_resumo[col] = df_resumo[col].round(1)

    # Salvar
    output = POWER_BI_DIR / "resumo_Executivo.csv"
    df_resumo.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"\n  Salvo: {output}")
    print(f"  Registros: {len(df_resumo)} (4 unidades + TOTAL)")
    print(f"\n  Preview:")
    print(df_resumo[["unidade", "semaforo", "total_professores", "total_alunos",
                      "pct_conformidade_media", "pct_alunos_risco"]].to_string(index=False))

    return df_resumo


# ========================================================================
# EXECUÇÃO
# ========================================================================
if __name__ == "__main__":
    score_prof = gerar_score_professor()
    score_abc = gerar_score_aluno_abc()
    resumo = gerar_resumo_executivo(score_prof, score_abc)

    print("\n" + "=" * 70)
    print("CONCLUÍDO! Arquivos gerados em:", POWER_BI_DIR)
    print("=" * 70)
    print("  - score_Professor.csv")
    print("  - score_Aluno_ABC.csv")
    print("  - resumo_Executivo.csv")
    print("\nPróximo passo: Importar esses CSVs no Power BI Desktop")
