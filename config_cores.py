"""
Configuração de cores padrão para o sistema pedagógico.
"""

# Cores por série (seguindo padrão TEEN)
CORES_SERIES = {
    '6º Ano': '#4FC3F7',      # Azul claro - TEEN 1
    '7º Ano': '#29B6F6',      # Azul - TEEN 1
    '8º Ano': '#03A9F4',      # Azul médio - TEEN 1
    '9º Ano': '#FFD54F',      # Amarelo - Transição TEEN 2
    '1ª Série': '#AB47BC',    # Roxo - EM
    '2ª Série': '#9C27B0',    # Roxo escuro - EM
    '3ª Série': '#E91E63',    # Rosa/Magenta - 3ª Série (diferente)
}

# Cores por unidade
CORES_UNIDADES = {
    'BV': '#2196F3',   # Azul - Boa Viagem
    'CD': '#4CAF50',   # Verde - Candeias
    'JG': '#FF9800',   # Laranja - Janga
    'CDR': '#9C27B0',  # Roxo - Cordeiro
}

# Cores por segmento
CORES_SEGMENTOS = {
    'TEEN 1': '#03A9F4',      # Azul - 6º, 7º, 8º
    'TEEN 2': '#9C27B0',      # Roxo - 9º, EM
    'Anos Finais': '#03A9F4', # Azul
    'Ensino Médio': '#9C27B0', # Roxo
}

# Cores de status
CORES_STATUS = {
    'Excelente': '#4CAF50',   # Verde
    'Bom': '#8BC34A',         # Verde claro
    'Atenção': '#FF9800',     # Laranja
    'Crítico': '#F44336',     # Vermelho
}

# Ordem padrão das séries
ORDEM_SERIES = ['6º Ano', '7º Ano', '8º Ano', '9º Ano', '1ª Série', '2ª Série', '3ª Série']
