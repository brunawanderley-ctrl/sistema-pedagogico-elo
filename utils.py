"""
Funcoes compartilhadas do Sistema Pedagogico ELO 2026.
Centraliza calculos, carregamento de dados e constantes usados em todas as paginas.
"""

import math
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# ========== CONSTANTES ==========

INICIO_ANO_LETIVO = datetime(2026, 1, 26)
DATA_DIR = Path(__file__).parent / "power_bi"

UNIDADES = ['BV', 'CD', 'JG', 'CDR']

UNIDADES_NOMES = {
    'BV': 'Boa Viagem',
    'CD': 'Candeias',
    'JG': 'Janga',
    'CDR': 'Cordeiro',
}

# Re-exporta de config_cores para manter compatibilidade de imports
from config_cores import ORDEM_SERIES  # noqa: F401

SERIES_FUND_II = ['6º Ano', '7º Ano', '8º Ano', '9º Ano']
SERIES_EM = ['1ª Série', '2ª Série', '3ª Série']

# ============================================================
# THRESHOLDS DE CONFORMIDADE (%)
# ============================================================
CONFORMIDADE_CRITICO = 50
CONFORMIDADE_BAIXO = 70
CONFORMIDADE_META = 85
CONFORMIDADE_EXCELENTE = 95

# Qualidade de conteúdo (%)
CONTEUDO_VAZIO_ALERTA = 30
CONTEUDO_VAZIO_CRITICO = 50

# Dias sem registro
DIAS_SEM_REGISTRO_ATENCAO = 4
DIAS_SEM_REGISTRO_URGENTE = 7

# Aliases para compatibilidade interna
THRESHOLD_EXCELENTE = CONFORMIDADE_EXCELENTE
THRESHOLD_BOM = CONFORMIDADE_META
THRESHOLD_ATENCAO = CONFORMIDADE_BAIXO


# ========== FUNCOES DE CALCULO ==========

def calcular_semana_letiva(data_ref=None):
    """
    Calcula semana letiva baseada na data de referencia.
    Inicio: 26/01/2026.
    Formula: (data - 26/01/2026).days // 7 + 1
    """
    if data_ref is None:
        data_ref = _hoje()
    if isinstance(data_ref, str):
        data_ref = pd.to_datetime(data_ref)
    if hasattr(data_ref, 'to_pydatetime'):
        data_ref = data_ref.to_pydatetime()
    return max(1, (data_ref - INICIO_ANO_LETIVO).days // 7 + 1)


def calcular_capitulo_esperado(semana):
    """
    Calcula capitulo SAE esperado para a semana.
    Formula: CEILING(semana / 3.5), max 12.
    """
    if semana is None:
        return 1
    return min(12, math.ceil(semana / 3.5))


def calcular_trimestre(semana):
    """Retorna o trimestre (1, 2 ou 3) baseado na semana letiva."""
    if semana is None:
        return 1
    if semana <= 14:
        return 1
    elif semana <= 28:
        return 2
    else:
        return 3


def status_conformidade(pct):
    """Retorna (emoji, label) baseado no percentual de conformidade."""
    if pct >= CONFORMIDADE_EXCELENTE:
        return '✅', 'Excelente'
    elif pct >= CONFORMIDADE_META:
        return 'ℹ️', 'Bom'
    elif pct >= CONFORMIDADE_BAIXO:
        return '⚠️', 'Atencao'
    else:
        return '🔴', 'Critico'


# ========== NORMALIZACAO DE DISCIPLINAS ==========

# Normaliza disciplinas do fato_Aulas (SIGA) → nomes canonicos SAE
DISCIPLINA_NORM_FATO = {
    'Física 2': 'Física',
}

# Normaliza disciplinas numeradas do horario → nomes base do SIGA
# O horario EM divide disciplinas em slots (Matematica 1, 2, 3) mas
# o SIGA registra apenas o nome base (Matematica)
DISCIPLINA_NORM_HORARIO = {
    'Matemática 1': 'Matemática',
    'Matemática 2': 'Matemática',
    'Matemática 3': 'Matemática',
    'Física 1': 'Física',
    'Física 2': 'Física',
    'Física 3': 'Física',
    'Biologia 1': 'Biologia',
    'Biologia 2': 'Biologia',
    'Química 1': 'Química',
    'Química 2': 'Química',
    'Química 3': 'Química',
    'História 1': 'História',
    'História 2': 'História',
    'Geografia 1': 'Geografia',
    'Geografia 2': 'Geografia',
    'Língua Portuguesa 1': 'Língua Portuguesa',
    'Língua Portuguesa 2': 'Língua Portuguesa',
}


def _normalizar_disciplina_fato(df):
    """Aplica normalizacao de disciplinas e recalcula progressao_key."""
    if 'disciplina' not in df.columns:
        return df
    mask = df['disciplina'].isin(DISCIPLINA_NORM_FATO)
    if mask.any():
        df.loc[mask, 'disciplina'] = df.loc[mask, 'disciplina'].map(DISCIPLINA_NORM_FATO)
        if 'progressao_key' in df.columns and 'serie' in df.columns and 'semana_letiva' in df.columns:
            df.loc[mask, 'progressao_key'] = (
                df.loc[mask, 'disciplina'] + '|' +
                df.loc[mask, 'serie'] + '|' +
                df.loc[mask, 'semana_letiva'].astype(str)
            )
    return df


def _normalizar_disciplina_horario(df):
    """Normaliza disciplinas numeradas do horario (Matematica 1 → Matematica)."""
    if 'disciplina' not in df.columns:
        return df
    mask = df['disciplina'].isin(DISCIPLINA_NORM_HORARIO)
    if mask.any():
        df.loc[mask, 'disciplina'] = df.loc[mask, 'disciplina'].map(DISCIPLINA_NORM_HORARIO)
    return df


# ========== CARREGAMENTO DE DADOS COM CACHE ==========

@st.cache_data(ttl=300)
def carregar_fato_aulas():
    """Carrega fato_Aulas.csv com cache de 5 minutos."""
    path = DATA_DIR / "fato_Aulas.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = _normalizar_disciplina_fato(df)
    return df


@st.cache_data(ttl=300)
def carregar_horario_esperado():
    """Carrega dim_Horario_Esperado.csv com cache. Normaliza disciplinas numeradas."""
    path = DATA_DIR / "dim_Horario_Esperado.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df = _normalizar_disciplina_horario(df)
    return df


@st.cache_data(ttl=300)
def carregar_calendario():
    """Carrega dim_Calendario.csv com cache."""
    path = DATA_DIR / "dim_Calendario.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    return df


@st.cache_data(ttl=300)
def carregar_progressao_sae():
    """Carrega dim_Progressao_SAE.csv com cache."""
    path = DATA_DIR / "dim_Progressao_SAE.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=300)
def carregar_professores():
    """Carrega dim_Professores.csv com cache."""
    path = DATA_DIR / "dim_Professores.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=300)
def carregar_series():
    """Carrega dim_Series.csv com cache."""
    path = DATA_DIR / "dim_Series.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=300)
def carregar_disciplinas():
    """Carrega dim_Disciplinas.csv com cache."""
    path = DATA_DIR / "dim_Disciplinas.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=300)
def carregar_unidades():
    """Carrega dim_Unidades.csv com cache."""
    path = DATA_DIR / "dim_Unidades.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=300)
def carregar_alunos():
    """Carrega dim_Alunos.csv com cache."""
    path = DATA_DIR / "dim_Alunos.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=300)
def carregar_notas():
    """Carrega notas com cache. Tenta fato_Notas.csv (trimestral) ou fato_Notas_Historico.csv (anual)."""
    # Primeiro: notas 2026 trimestrais (quando disponivel)
    path = DATA_DIR / "fato_Notas.csv"
    if path.exists():
        df = pd.read_csv(path)
        if 'data_avaliacao' in df.columns:
            df['data_avaliacao'] = pd.to_datetime(df['data_avaliacao'], errors='coerce')
        return df
    # Fallback: historico de notas anuais (todas as unidades)
    path_hist = DATA_DIR / "fato_Notas_Historico.csv"
    if path_hist.exists():
        df = pd.read_csv(path_hist)
        # Compatibilidade: mapear colunas para schema esperado pelas paginas
        # nota pode existir mas estar vazia - usar nota_final como fallback
        if 'nota_final' in df.columns:
            if 'nota' not in df.columns or df['nota'].isna().all():
                df['nota'] = df['nota_final']
        if 'serie_atual' in df.columns and 'serie' not in df.columns:
            df['serie'] = df['serie_atual']
        # Enriquecer com turma do dim_Alunos (necessario para Boletim por Turma)
        if 'turma' not in df.columns:
            path_alunos = DATA_DIR / "dim_Alunos.csv"
            if path_alunos.exists():
                df_al = pd.read_csv(path_alunos, usecols=['aluno_id', 'turma'])
                df = df.merge(df_al, on='aluno_id', how='left')
        return df
    return pd.DataFrame()


@st.cache_data(ttl=300)
def carregar_frequencia_alunos():
    """Carrega fato_Frequencia_Aluno.csv com cache. Fallback: derive from historico."""
    path = DATA_DIR / "fato_Frequencia_Aluno.csv"
    if path.exists():
        df = pd.read_csv(path)
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
        return df
    # Fallback: derivar frequencia do historico (faltas + carga_horaria)
    return carregar_frequencia_historico()


@st.cache_data(ttl=300)
def carregar_frequencia_historico():
    """Deriva frequencia por aluno/disciplina/ano a partir de fato_Notas_Historico (faltas + carga_horaria)."""
    path = DATA_DIR / "fato_Notas_Historico.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    # Precisa de faltas e carga_horaria validos
    required = ['aluno_id', 'aluno_nome', 'faltas', 'carga_horaria']
    if not all(c in df.columns for c in required):
        return pd.DataFrame()
    df = df[df['faltas'].notna() & df['carga_horaria'].notna() & (df['carga_horaria'] > 0)]
    # Filtrar outlier de carga_horaria (ex: 240200)
    df = df[df['carga_horaria'] <= 1000]
    if df.empty:
        return pd.DataFrame()
    # Calcular frequencia
    df['pct_frequencia'] = ((df['carga_horaria'] - df['faltas']) / df['carga_horaria'] * 100).round(1)
    df['pct_frequencia'] = df['pct_frequencia'].clip(0, 100)
    df['total_aulas'] = df['carga_horaria'].astype(int)
    df['presencas'] = (df['carga_horaria'] - df['faltas']).astype(int)
    # Normalizar serie
    if 'serie_atual' in df.columns and 'serie' not in df.columns:
        df['serie'] = df['serie_atual']
    # Enriquecer com turma
    if 'turma' not in df.columns:
        path_al = DATA_DIR / "dim_Alunos.csv"
        if path_al.exists():
            df_al = pd.read_csv(path_al, usecols=['aluno_id', 'turma'])
            df = df.merge(df_al, on='aluno_id', how='left')
    # Colunas de saida
    cols_out = ['aluno_id', 'aluno_nome', 'unidade', 'serie', 'disciplina',
                'ano', 'faltas', 'carga_horaria', 'total_aulas', 'presencas',
                'pct_frequencia']
    if 'turma' in df.columns:
        cols_out.append('turma')
    if 'resultado' in df.columns:
        cols_out.append('resultado')
    cols_out = [c for c in cols_out if c in df.columns]
    # Marcar como dados derivados do historico
    df['fonte'] = 'historico'
    cols_out.append('fonte')
    return df[cols_out]


@st.cache_data(ttl=60)
def carregar_ocorrencias():
    """Carrega fato_Ocorrencias.csv com cache curto (permite refresh apos novo registro)."""
    path = DATA_DIR / "fato_Ocorrencias.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
    return df


def salvar_ocorrencia(registro: dict):
    """Salva nova ocorrencia em fato_Ocorrencias.csv. Retorna True se sucesso."""
    path = DATA_DIR / "fato_Ocorrencias.csv"
    colunas = ['ocorrencia_id', 'aluno_id', 'aluno_nome', 'data', 'unidade', 'serie',
               'turma', 'tipo', 'categoria', 'gravidade', 'descricao', 'responsavel',
               'providencia', 'registrado_por', 'data_registro']
    if path.exists():
        df = pd.read_csv(path)
        next_id = df['ocorrencia_id'].max() + 1 if 'ocorrencia_id' in df.columns and not df.empty else 1
    else:
        df = pd.DataFrame(columns=colunas)
        next_id = 1
    registro['ocorrencia_id'] = int(next_id)
    registro['data_registro'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')
    new_row = pd.DataFrame([registro])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(path, index=False)
    # Limpar cache para carregar dados atualizados
    carregar_ocorrencias.clear()
    return True


# Threshold de frequencia (LDB art. 24, VI)
THRESHOLD_FREQUENCIA_LDB = 75


def calcular_media_trimestral(notas_df, trimestre=None):
    """Calcula media trimestral por aluno/disciplina."""
    if notas_df.empty:
        return pd.DataFrame()
    df = notas_df.copy()
    if trimestre and 'trimestre' in df.columns:
        df = df[df['trimestre'] == trimestre]
    if 'nota' not in df.columns:
        return pd.DataFrame()
    cols_group = [c for c in ['aluno_id', 'aluno_nome', 'disciplina', 'serie', 'unidade'] if c in df.columns]
    if not cols_group:
        return pd.DataFrame()
    return df.groupby(cols_group)['nota'].mean().reset_index().rename(columns={'nota': 'media'})


def calcular_frequencia_aluno(freq_df, aluno_id=None):
    """Calcula percentual de frequencia por aluno/disciplina."""
    if freq_df.empty:
        return pd.DataFrame()
    df = freq_df.copy()
    if aluno_id is not None and 'aluno_id' in df.columns:
        df = df[df['aluno_id'] == aluno_id]
    if df.empty:
        return pd.DataFrame()
    cols_group = [c for c in ['aluno_id', 'aluno_nome', 'disciplina', 'serie', 'unidade'] if c in df.columns]
    if not cols_group:
        return pd.DataFrame()
    # Se dados ja tem pct_frequencia (formato historico), retorna direto
    if 'pct_frequencia' in df.columns:
        return df
    # Formato com coluna 'presente' (dados em tempo real)
    if 'presente' not in df.columns:
        return pd.DataFrame()
    agg = df.groupby(cols_group).agg(
        total_aulas=('presente', 'count'),
        presencas=('presente', 'sum'),
    ).reset_index()
    agg['pct_frequencia'] = (agg['presencas'] / agg['total_aulas'] * 100).round(1)
    return agg


def status_frequencia(pct):
    """Retorna (emoji, label) baseado no percentual de frequencia."""
    if pct >= 90:
        return '✅', 'Excelente'
    elif pct >= THRESHOLD_FREQUENCIA_LDB:
        return '⚠️', 'Regular'
    else:
        return '🔴', 'Risco Reprovacao'


def carregar_todos_dados():
    """Carrega todos os dados do sistema de uma vez. Retorna dict."""
    dados = {}
    df_aulas = carregar_fato_aulas()
    if not df_aulas.empty:
        dados['aulas'] = df_aulas
    df_horario = carregar_horario_esperado()
    if not df_horario.empty:
        dados['horario'] = df_horario
    df_cal = carregar_calendario()
    if not df_cal.empty:
        dados['calendario'] = df_cal
    df_prog = carregar_progressao_sae()
    if not df_prog.empty:
        dados['progressao'] = df_prog
    df_profs = carregar_professores()
    if not df_profs.empty:
        dados['professores'] = df_profs
    df_alunos = carregar_alunos()
    if not df_alunos.empty:
        dados['alunos'] = df_alunos
    df_notas = carregar_notas()
    if not df_notas.empty:
        dados['notas'] = df_notas
    df_freq = carregar_frequencia_alunos()
    if not df_freq.empty:
        dados['frequencia_alunos'] = df_freq
    df_ocorr = carregar_ocorrencias()
    if not df_ocorr.empty:
        dados['ocorrencias'] = df_ocorr
    return dados


# ========== FILTROS COMUNS ==========

def filtrar_por_segmento(df, segmento, col_serie='serie'):
    """Filtra DataFrame por segmento (Anos Finais / Ensino Medio)."""
    if segmento == 'Anos Finais':
        return df[df[col_serie].isin(SERIES_FUND_II)]
    elif segmento == 'Ensino Médio' or segmento == 'Ensino Medio':
        return df[df[col_serie].isin(SERIES_EM)]
    return df


def filtrar_ate_hoje(df, col_data='data'):
    """Filtra DataFrame para incluir apenas registros ate hoje."""
    hoje = _hoje()
    if col_data in df.columns:
        return df[df[col_data] <= hoje]
    return df


def filtrar_por_periodo(df, periodo, col_data='data', col_semana='semana_letiva'):
    """
    Filtra DataFrame por periodo selecionado.
    Opcoes: 'Esta Semana', 'Ultimos 7 dias', 'Ultimos 15 dias',
            'Este Mes', '1o Trimestre', '2o Trimestre', '3o Trimestre', 'Ano Completo'.
    """
    if periodo == 'Ano Completo':
        return df

    hoje = _hoje()

    if col_data not in df.columns:
        return df

    if periodo == 'Esta Semana':
        semana_atual = calcular_semana_letiva(hoje)
        if col_semana in df.columns:
            return df[df[col_semana] == semana_atual]
        inicio_semana = hoje - pd.Timedelta(days=hoje.weekday())
        return df[(df[col_data] >= inicio_semana) & (df[col_data] <= hoje)]

    elif periodo == 'Ultimos 7 dias':
        return df[df[col_data] >= (hoje - pd.Timedelta(days=7))]

    elif periodo == 'Ultimos 15 dias':
        return df[df[col_data] >= (hoje - pd.Timedelta(days=15))]

    elif periodo == 'Este Mes':
        return df[(df[col_data].dt.month == hoje.month) & (df[col_data].dt.year == hoje.year)]

    elif periodo == '1o Trimestre':
        if col_semana in df.columns:
            return df[df[col_semana] <= 14]
        return df[df[col_data] < datetime(2026, 5, 9)]

    elif periodo == '2o Trimestre':
        if col_semana in df.columns:
            return df[(df[col_semana] >= 15) & (df[col_semana] <= 28)]
        return df[(df[col_data] >= datetime(2026, 5, 9)) & (df[col_data] < datetime(2026, 8, 29))]

    elif periodo == '3o Trimestre':
        if col_semana in df.columns:
            return df[df[col_semana] >= 29]
        return df[df[col_data] >= datetime(2026, 8, 29)]

    return df


PERIODOS_OPCOES = [
    'Ano Completo', 'Esta Semana', 'Ultimos 7 dias', 'Ultimos 15 dias',
    'Este Mes', '1o Trimestre', '2o Trimestre', '3o Trimestre',
]


# ========== AMBIENTE ==========

def is_cloud():
    """Detecta se estamos rodando no Streamlit Cloud."""
    return os.environ.get('STREAMLIT_SHARING_MODE') == '1' or \
           os.environ.get('IS_STREAMLIT_CLOUD', '') == '1' or \
           not Path(__file__).parent.joinpath('atualizar_siga.py').exists()


# ========== HELPERS INTERNOS ==========

def _hoje():
    """Retorna data de hoje. Se ano < 2026, simula 05/02/2026."""
    hoje = datetime.now()
    if hoje.year < 2026:
        return datetime(2026, 2, 5)
    return hoje


def ultima_atualizacao():
    """Retorna string com data da ultima atualizacao do fato_Aulas."""
    path = DATA_DIR / "fato_Aulas.csv"
    if path.exists():
        mod_time = os.path.getmtime(path)
        return datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M")
    return "Dados nao extraidos"
