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

ORDEM_SERIES = ['6º Ano', '7º Ano', '8º Ano', '9º Ano', '1ª Série', '2ª Série', '3ª Série']

SERIES_FUND_II = ['6º Ano', '7º Ano', '8º Ano', '9º Ano']
SERIES_EM = ['1ª Série', '2ª Série', '3ª Série']

# Thresholds de conformidade
THRESHOLD_EXCELENTE = 95
THRESHOLD_BOM = 85
THRESHOLD_ATENCAO = 70


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
    if semana <= 14:
        return 1
    elif semana <= 28:
        return 2
    else:
        return 3


def status_conformidade(pct):
    """Retorna (emoji, label) baseado no percentual de conformidade."""
    if pct >= THRESHOLD_EXCELENTE:
        return '✅', 'Excelente'
    elif pct >= THRESHOLD_BOM:
        return 'ℹ️', 'Bom'
    elif pct >= THRESHOLD_ATENCAO:
        return '⚠️', 'Atencao'
    else:
        return '🔴', 'Critico'


# ========== CARREGAMENTO DE DADOS COM CACHE ==========

@st.cache_data(ttl=300)
def carregar_fato_aulas():
    """Carrega fato_Aulas.csv com cache de 5 minutos."""
    path = DATA_DIR / "fato_Aulas.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    return df


@st.cache_data(ttl=300)
def carregar_horario_esperado():
    """Carrega dim_Horario_Esperado.csv com cache."""
    path = DATA_DIR / "dim_Horario_Esperado.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


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
