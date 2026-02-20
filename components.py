"""
Componentes Streamlit reutilizaveis - Sistema Pedagogico ELO 2026.

Encapsula padroes de UI que se repetem em 3+ paginas do sistema:
  - Filtros (unidade, segmento, serie, periodo, trimestre)
  - Cabecalho de pagina
  - Metricas em colunas
  - Download CSV
  - Aplicacao de filtros em DataFrames

Uso:
    from components import (
        filtro_unidade, filtro_segmento, filtro_serie,
        filtro_periodo, cabecalho_pagina, botao_download_csv,
        metricas_em_colunas, aplicar_filtro_segmento,
        filtro_unidade_multi,
    )
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import pandas as pd
import streamlit as st

from auth import get_user_unit
from utils import (
    PERIODOS_OPCOES,
    SERIES_EM,
    SERIES_FUND_II,
    UNIDADES,
    UNIDADES_NOMES,
)

try:
    from config_cores import ORDEM_SERIES
except ImportError:
    ORDEM_SERIES = SERIES_FUND_II + SERIES_EM


# ============================================================
# FILTRO: UNIDADE (selectbox)
# ============================================================

def filtro_unidade(
    opcoes: Optional[List[str]] = None,
    *,
    label: str = "Unidade",
    todas_label: str = "TODAS",
    usar_nomes: bool = False,
    key: Optional[str] = None,
) -> str:
    """Renderiza selectbox de unidade com default para unidade do usuario logado.

    O valor "Todas"/"TODAS" e colocado como primeira opcao. Se o usuario logado
    pertence a uma unidade, ela e pre-selecionada.

    Args:
        opcoes: Lista de codigos de unidade (ex: ['BV','CD']). Se None, usa
                a lista completa UNIDADES.
        label: Rotulo exibido no selectbox.
        todas_label: Texto da opcao "Todas". Passar '' para omiti-la.
        usar_nomes: Se True, exibe nome por extenso via format_func.
        key: Chave Streamlit para o widget.

    Returns:
        Codigo da unidade selecionada, ou o valor de *todas_label* quando
        o usuario escolhe "Todas".
    """
    if opcoes is None:
        opcoes = list(UNIDADES)

    un_list: List[str] = ([todas_label] + opcoes) if todas_label else list(opcoes)

    user_unit = get_user_unit()
    default_idx = 0
    if user_unit and user_unit in un_list:
        default_idx = un_list.index(user_unit)

    format_fn = None
    if usar_nomes:
        format_fn = lambda x: UNIDADES_NOMES.get(x, x) if x != todas_label else todas_label

    return st.selectbox(
        label,
        un_list,
        index=default_idx,
        format_func=format_fn,
        key=key,
    )


# ============================================================
# FILTRO: UNIDADE (multiselect)
# ============================================================

def filtro_unidade_multi(
    opcoes: Optional[List[str]] = None,
    *,
    label: str = "Unidade:",
    key: Optional[str] = None,
) -> List[str]:
    """Renderiza multiselect de unidades com default para unidade do usuario.

    Se o usuario logado pertence a uma unidade, apenas essa vem pre-selecionada.
    Caso contrario, todas as unidades sao selecionadas por padrao.

    Args:
        opcoes: Lista de codigos de unidade. Se None, usa UNIDADES.
        label: Rotulo exibido.
        key: Chave Streamlit para o widget.

    Returns:
        Lista de codigos de unidade selecionados.
    """
    if opcoes is None:
        opcoes = list(UNIDADES)

    user_unit = get_user_unit()
    default = [user_unit] if user_unit and user_unit in opcoes else opcoes

    return st.multiselect(
        label,
        opcoes,
        default=default,
        format_func=lambda x: UNIDADES_NOMES.get(x, x),
        key=key,
    )


# ============================================================
# FILTRO: SEGMENTO
# ============================================================

def filtro_segmento(
    *,
    label: str = "Segmento",
    todos_label: str = "Todos",
    key: Optional[str] = None,
) -> str:
    """Renderiza selectbox de segmento (Todos / Anos Finais / Ensino Medio).

    Args:
        label: Rotulo exibido.
        todos_label: Texto da opcao universal ('Todos' ou 'TODOS').
        key: Chave Streamlit.

    Returns:
        Texto selecionado: 'Todos', 'Anos Finais' ou 'Ensino Medio'.
    """
    opcoes = [todos_label, 'Anos Finais', 'Ensino Medio']
    return st.selectbox(label, opcoes, key=key)


# ============================================================
# FILTRO: SERIE
# ============================================================

def filtro_serie(
    series_disponiveis: Optional[List[str]] = None,
    *,
    label: str = "Serie",
    todas_label: str = "Todas",
    key: Optional[str] = None,
) -> str:
    """Renderiza selectbox de serie, ordenado pela ORDEM_SERIES canonica.

    Args:
        series_disponiveis: Lista de series para popular o filtro.
            Se None, usa ORDEM_SERIES completa.
        label: Rotulo exibido.
        todas_label: Texto da opcao universal. Passar '' para omitir.
        key: Chave Streamlit.

    Returns:
        Serie selecionada ou *todas_label*.
    """
    if series_disponiveis is None:
        series_disponiveis = list(ORDEM_SERIES)
    else:
        series_disponiveis = sorted(
            series_disponiveis,
            key=lambda x: ORDEM_SERIES.index(x) if x in ORDEM_SERIES else 99,
        )

    opcoes = ([todas_label] + series_disponiveis) if todas_label else series_disponiveis
    return st.selectbox(label, opcoes, key=key)


# ============================================================
# FILTRO: PERIODO / TRIMESTRE
# ============================================================

def filtro_periodo(
    *,
    label: str = "Periodo",
    opcoes: Optional[List[str]] = None,
    key: Optional[str] = None,
) -> str:
    """Renderiza selectbox de periodo letivo.

    Por padrao usa PERIODOS_OPCOES de utils.py:
        ['Ano Completo', 'Ultimos 7 dias', 'Ultimos 15 dias',
         'Este Mes', '1o Trimestre', '2o Trimestre', '3o Trimestre']

    Args:
        label: Rotulo exibido.
        opcoes: Lista customizada de opcoes. Se None, usa PERIODOS_OPCOES.
        key: Chave Streamlit.

    Returns:
        Texto do periodo selecionado.
    """
    if opcoes is None:
        opcoes = list(PERIODOS_OPCOES)
    return st.selectbox(label, opcoes, key=key)


def filtro_trimestre(
    *,
    label: str = "Trimestre",
    key: Optional[str] = None,
) -> int:
    """Renderiza selectbox de trimestre e retorna o numero (1, 2 ou 3).

    Args:
        label: Rotulo exibido.
        key: Chave Streamlit.

    Returns:
        Numero do trimestre selecionado (1, 2 ou 3).
    """
    opcoes = ['1o Trimestre', '2o Trimestre', '3o Trimestre']
    sel = st.selectbox(label, opcoes, key=key)
    return opcoes.index(sel) + 1


# ============================================================
# CABECALHO DE PAGINA
# ============================================================

def cabecalho_pagina(
    titulo: str,
    subtitulo: str = "",
    *,
    mostrar_data: bool = True,
) -> None:
    """Renderiza cabecalho padrao de pagina com titulo, subtitulo e data.

    Padrao encontrado em todas as 25 paginas:
        st.title("... Titulo")
        st.markdown("**subtitulo**")

    Args:
        titulo: Texto do st.title (pode incluir emoji no inicio).
        subtitulo: Texto em negrito exibido abaixo do titulo.
        mostrar_data: Se True, exibe caption com data atual.
    """
    st.title(titulo)
    if subtitulo:
        st.markdown(f"**{subtitulo}**")
    if mostrar_data:
        st.caption(f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")


# ============================================================
# METRICAS EM COLUNAS
# ============================================================

def metricas_em_colunas(
    metricas: List[Dict[str, Any]],
    *,
    num_colunas: Optional[int] = None,
) -> None:
    """Renderiza N metricas lado a lado usando st.columns + st.metric.

    Padrao encontrado em 10+ paginas (ex: paginas 01, 05, 13, 22, 23).

    Args:
        metricas: Lista de dicts com chaves:
            - 'label' (str, obrigatorio): rotulo da metrica
            - 'value' (Any, obrigatorio): valor exibido
            - 'delta' (str, opcional): texto de delta
            - 'delta_color' (str, opcional): 'normal', 'inverse' ou 'off'
            - 'help' (str, opcional): tooltip
        num_colunas: Numero de colunas. Se None, usa len(metricas).

    Exemplo:
        metricas_em_colunas([
            {'label': 'Total Aulas', 'value': 1234},
            {'label': 'Professores', 'value': 42},
            {'label': 'Conformidade', 'value': '87%', 'delta': '+5%'},
        ])
    """
    n = num_colunas or len(metricas)
    colunas = st.columns(n)

    for i, metrica in enumerate(metricas):
        col = colunas[i % n]
        kwargs: Dict[str, Any] = {
            'label': metrica['label'],
            'value': metrica['value'],
        }
        if 'delta' in metrica:
            kwargs['delta'] = metrica['delta']
        if 'delta_color' in metrica:
            kwargs['delta_color'] = metrica['delta_color']
        if 'help' in metrica:
            kwargs['help'] = metrica['help']
        col.metric(**kwargs)


# ============================================================
# DOWNLOAD CSV
# ============================================================

def botao_download_csv(
    df: pd.DataFrame,
    nome_arquivo: str,
    *,
    label: str = "Download CSV",
    key: Optional[str] = None,
    incluir_data: bool = True,
    encoding: str = "utf-8-sig",
) -> bool:
    """Renderiza botao de download CSV para um DataFrame.

    Padrao encontrado em 10+ paginas (ex: paginas 05, 10, 13, 22).

    Args:
        df: DataFrame a ser exportado.
        nome_arquivo: Nome base do arquivo (sem extensao e sem data).
            Exemplo: 'semaforo_professores'.
        label: Texto do botao.
        key: Chave Streamlit para o widget.
        incluir_data: Se True, adiciona timestamp YYYYMMDD_HHMM ao nome.
        encoding: Encoding do CSV (default utf-8-sig para Excel BR).

    Returns:
        True se o botao foi clicado (mesma semantica de st.download_button).
    """
    csv_data = df.to_csv(index=False).encode(encoding)

    if incluir_data:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        arquivo_final = f"{nome_arquivo}_{timestamp}.csv"
    else:
        arquivo_final = f"{nome_arquivo}.csv"

    return st.download_button(
        label,
        csv_data,
        file_name=arquivo_final,
        mime="text/csv",
        key=key,
    )


# ============================================================
# APLICAR FILTROS EM DATAFRAME
# ============================================================

def aplicar_filtro_unidade(
    df: pd.DataFrame,
    unidade: str,
    *,
    coluna: str = "unidade",
    todas_label: str = "TODAS",
) -> pd.DataFrame:
    """Filtra DataFrame por unidade. Retorna inalterado se unidade == todas_label.

    Args:
        df: DataFrame a filtrar.
        unidade: Codigo da unidade selecionada ou valor de 'todas'.
        coluna: Nome da coluna no DataFrame.
        todas_label: Valor que indica "sem filtro".

    Returns:
        DataFrame filtrado (ou copia inalterada).
    """
    if unidade == todas_label or not unidade:
        return df
    if coluna in df.columns:
        return df[df[coluna] == unidade]
    return df


def aplicar_filtro_segmento(
    df: pd.DataFrame,
    segmento: str,
    *,
    coluna: str = "serie",
) -> pd.DataFrame:
    """Filtra DataFrame por segmento (Anos Finais / Ensino Medio).

    Padrao encontrado em 10+ paginas — substitui o bloco:
        if segmento == 'Anos Finais':
            df = df[df['serie'].isin(SERIES_FUND_II)]
        elif segmento == 'Ensino Medio':
            df = df[df['serie'].isin(SERIES_EM)]

    Args:
        df: DataFrame a filtrar.
        segmento: 'Todos'/'TODOS', 'Anos Finais' ou 'Ensino Medio'.
        coluna: Nome da coluna de serie no DataFrame.

    Returns:
        DataFrame filtrado (ou inalterado se 'Todos').
    """
    if coluna not in df.columns:
        return df
    if segmento == 'Anos Finais':
        return df[df[coluna].isin(SERIES_FUND_II)]
    elif segmento in ('Ensino Medio', 'Ensino Médio'):
        return df[df[coluna].isin(SERIES_EM)]
    return df


def aplicar_filtro_serie(
    df: pd.DataFrame,
    serie: str,
    *,
    coluna: str = "serie",
    todas_label: str = "Todas",
) -> pd.DataFrame:
    """Filtra DataFrame por serie. Retorna inalterado se serie == todas_label.

    Args:
        df: DataFrame a filtrar.
        serie: Serie selecionada ou valor de 'todas'.
        coluna: Nome da coluna no DataFrame.
        todas_label: Valor que indica "sem filtro".

    Returns:
        DataFrame filtrado.
    """
    if serie == todas_label or not serie:
        return df
    if coluna in df.columns:
        return df[df[coluna] == serie]
    return df


def aplicar_filtros_padrao(
    df: pd.DataFrame,
    *,
    unidade: Optional[str] = None,
    segmento: Optional[str] = None,
    serie: Optional[str] = None,
    todas_un: str = "TODAS",
    todas_serie: str = "Todas",
    col_unidade: str = "unidade",
    col_serie: str = "serie",
) -> pd.DataFrame:
    """Aplica filtros padrao de unidade, segmento e serie de uma vez.

    Equivale a chamar aplicar_filtro_unidade + aplicar_filtro_segmento +
    aplicar_filtro_serie em sequencia.

    Args:
        df: DataFrame a filtrar.
        unidade: Codigo da unidade ou valor de 'todas'.
        segmento: 'Todos', 'Anos Finais' ou 'Ensino Medio'.
        serie: Serie selecionada ou valor de 'todas'.
        todas_un: Valor que indica "sem filtro" para unidade.
        todas_serie: Valor que indica "sem filtro" para serie.
        col_unidade: Nome da coluna de unidade.
        col_serie: Nome da coluna de serie.

    Returns:
        DataFrame com todos os filtros aplicados.
    """
    result = df
    if unidade is not None:
        result = aplicar_filtro_unidade(result, unidade, coluna=col_unidade, todas_label=todas_un)
    if segmento is not None:
        result = aplicar_filtro_segmento(result, segmento, coluna=col_serie)
    if serie is not None:
        result = aplicar_filtro_serie(result, serie, coluna=col_serie, todas_label=todas_serie)
    return result


# ============================================================
# BARRA DE FILTROS (combina multiplos filtros em colunas)
# ============================================================

def barra_filtros_padrao(
    *,
    mostrar_unidade: bool = True,
    mostrar_segmento: bool = True,
    mostrar_serie: bool = True,
    mostrar_periodo: bool = True,
    series_disponiveis: Optional[List[str]] = None,
    todas_un_label: str = "TODAS",
    todas_serie_label: str = "Todas",
    todos_seg_label: str = "TODOS",
    key_prefix: str = "",
) -> Dict[str, str]:
    """Renderiza barra de filtros padrao em st.columns.

    Combina os filtros mais comuns lado a lado. Padrao encontrado em
    paginas 01, 05, 10, 13 e outras.

    Args:
        mostrar_unidade: Exibir filtro de unidade.
        mostrar_segmento: Exibir filtro de segmento.
        mostrar_serie: Exibir filtro de serie.
        mostrar_periodo: Exibir filtro de periodo.
        series_disponiveis: Series para popular o filtro de serie.
        todas_un_label: Texto da opcao "Todas" para unidade.
        todas_serie_label: Texto da opcao "Todas" para serie.
        todos_seg_label: Texto da opcao "Todos" para segmento.
        key_prefix: Prefixo para chaves dos widgets (evita colisao).

    Returns:
        Dict com chaves: 'unidade', 'segmento', 'serie', 'periodo'.
        Cada valor e o texto selecionado no respectivo filtro, ou None
        se o filtro nao foi exibido.
    """
    filtros_ativos = []
    if mostrar_unidade:
        filtros_ativos.append('unidade')
    if mostrar_segmento:
        filtros_ativos.append('segmento')
    if mostrar_serie:
        filtros_ativos.append('serie')
    if mostrar_periodo:
        filtros_ativos.append('periodo')

    n = len(filtros_ativos)
    if n == 0:
        return {'unidade': None, 'segmento': None, 'serie': None, 'periodo': None}

    colunas = st.columns(n)
    resultado: Dict[str, Any] = {
        'unidade': None,
        'segmento': None,
        'serie': None,
        'periodo': None,
    }

    idx = 0
    if 'unidade' in filtros_ativos:
        with colunas[idx]:
            resultado['unidade'] = filtro_unidade(
                todas_label=todas_un_label,
                key=f"{key_prefix}un" if key_prefix else None,
            )
        idx += 1

    if 'segmento' in filtros_ativos:
        with colunas[idx]:
            resultado['segmento'] = filtro_segmento(
                todos_label=todos_seg_label,
                key=f"{key_prefix}seg" if key_prefix else None,
            )
        idx += 1

    if 'serie' in filtros_ativos:
        with colunas[idx]:
            resultado['serie'] = filtro_serie(
                series_disponiveis=series_disponiveis,
                todas_label=todas_serie_label,
                key=f"{key_prefix}serie" if key_prefix else None,
            )
        idx += 1

    if 'periodo' in filtros_ativos:
        with colunas[idx]:
            resultado['periodo'] = filtro_periodo(
                key=f"{key_prefix}periodo" if key_prefix else None,
            )
        idx += 1

    return resultado
