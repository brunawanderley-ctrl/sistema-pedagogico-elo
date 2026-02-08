"""
Configuração de cores padrão para o sistema pedagógico.

Esquema pensado para distinguir visualmente 3 grupos:
  - Anos Finais (6º-8º): tons de AZUL
  - 9º Ano: LARANJA (transição TEEN 2)
  - 1ª-2ª Série EM: tons de VERDE
  - 3ª Série EM: VERMELHO (pré-vestibular)
"""

# Cores por série - grupos visualmente distintos
CORES_SERIES = {
    '6º Ano': '#64B5F6',      # Azul claro - Fund II
    '7º Ano': '#42A5F5',      # Azul - Fund II
    '8º Ano': '#1E88E5',      # Azul escuro - Fund II
    '9º Ano': '#FFA726',      # Laranja - Transição (TEEN 2)
    '1ª Série': '#66BB6A',    # Verde - EM
    '2ª Série': '#388E3C',    # Verde escuro - EM
    '3ª Série': '#E53935',    # Vermelho - 3ª EM (pré-vestibular)
}

# Cores por unidade
CORES_UNIDADES = {
    'BV': '#1976D2',   # Azul - Boa Viagem
    'CD': '#388E3C',   # Verde - Candeias
    'JG': '#F57C00',   # Laranja - Janga
    'CDR': '#7B1FA2',  # Roxo - Cordeiro
}

# Cores por segmento
CORES_SEGMENTOS = {
    'TEEN 1': '#1E88E5',      # Azul - 6º, 7º, 8º
    'TEEN 2': '#388E3C',      # Verde - 9º, EM
    'Anos Finais': '#1E88E5', # Azul
    'Ensino Médio': '#388E3C', # Verde
}

# Cores de status
CORES_STATUS = {
    'Excelente': '#43A047',   # Verde
    'Bom': '#66BB6A',         # Verde claro
    'Atenção': '#FFA726',     # Laranja
    'Crítico': '#E53935',     # Vermelho
}

# Ordem padrão das séries
ORDEM_SERIES = ['6º Ano', '7º Ano', '8º Ano', '9º Ano', '1ª Série', '2ª Série', '3ª Série']
