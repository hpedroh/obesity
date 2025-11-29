"""
Arquivo central de constantes, dicionários e configurações do projeto HealthAnalytics.
"""

# ============================================================================
# 1. MAPEAMENTOS DE FORMULÁRIO (Frontend PT -> Backend EN/Codes)
# ============================================================================
DICT_SIM_NAO = {"Sim": "yes", "Não": "no"}
DICT_GENERO = {"Masculino": "Male", "Feminino": "Female"}

DICT_FREQ_CALORICA = {
    "Não": "no", 
    "Às vezes": "Sometimes", 
    "Frequentemente": "Frequently", 
    "Sempre": "Always"
}

DICT_TRANSPORTE = {
    "Transporte Público": "Public_Transportation", 
    "Caminhada": "Walking",
    "Carro": "Automobile", 
    "Moto": "Motorbike", 
    "Bicicleta": "Bike"
}

# Escalas Numéricas (Texto -> Número)
DICT_FCVC_NUM = {"Nunca": 1, "Às vezes": 2, "Sempre": 3}
DICT_CH2O_NUM = {"Menos de 1L": 1, "Entre 1L e 2L": 2, "Mais de 2L": 3}
DICT_FAF_NUM  = {"Nenhuma": 0, "1 a 2 dias/sem": 1, "3 a 4 dias/sem": 2, "5 ou mais dias/sem": 3}
DICT_TUE_NUM  = {"0 a 2 horas": 0, "3 a 5 horas": 1, "Mais de 5 horas": 2}

# ============================================================================
# 2. MAPEAMENTOS DE VISUALIZAÇÃO (Backend Codes -> Frontend PT)
# ============================================================================
# Escalas Reversas (Número -> Texto)
DICT_FCVC_TEXT = {v: k for k, v in DICT_FCVC_NUM.items()}
DICT_CH2O_TEXT = {v: k for k, v in DICT_CH2O_NUM.items()}
DICT_FAF_TEXT  = {v: k for k, v in DICT_FAF_NUM.items()}
DICT_TUE_TEXT  = {v: k for k, v in DICT_TUE_NUM.items()}

# Dicionário Geral de Tradução (Inglês -> Português com acentos)
DICT_TRADUCAO_GERAL = {
    # Classes Alvo
    'Insufficient_Weight': 'Abaixo do Peso',
    'Normal_Weight': 'Peso Normal',
    'Overweight_Level_I': 'Sobrepeso Nível I',
    'Overweight_Level_II': 'Sobrepeso Nível II',
    'Obesity_Type_I': 'Obesidade Tipo I',
    'Obesity_Type_II': 'Obesidade Tipo II',
    'Obesity_Type_III': 'Obesidade Tipo III (Mórbida)',
    
    # Categorias Gerais
    'Male': 'Masculino', 'Female': 'Feminino',
    'yes': 'Sim', 'no': 'Não',
    'Public_Transportation': 'Transporte Público', 'Walking': 'Caminhada',
    'Automobile': 'Carro', 'Motorbike': 'Moto', 'Bike': 'Bicicleta',
    'Sometimes': 'Às vezes', 'Frequently': 'Frequentemente', 'Always': 'Sempre'
}

# Dicionário "Safe" (Sem acentos críticos) para o PDF (evita erros de encoding)
DICT_RESULTADO_PDF = {
    "Insufficient_Weight": "Abaixo do Peso",
    "Normal_Weight": "Peso Normal",
    "Overweight_Level_I": "Sobrepeso Nivel I",
    "Overweight_Level_II": "Sobrepeso Nivel II",
    "Obesity_Type_I": "Obesidade Tipo I",
    "Obesity_Type_II": "Obesidade Tipo II",
    "Obesity_Type_III": "Obesidade Tipo III (Morbida)"
}

# Nomes Amigáveis das Colunas (Dashboard)
DICT_COLUNAS_PT = {
    'Obesity': 'Nível de Obesidade',
    'Gender': 'Gênero',
    'Age': 'Idade',
    'Height': 'Altura',
    'Weight': 'Peso',
    'family_history': 'Histórico Familiar',
    'FAVC': 'Consumo Calórico',
    'FCVC': 'Consumo de Vegetais',
    'NCP': 'Refeições por Dia',
    'CAEC': 'Comer entre Refeições',
    'SMOKE': 'Fumante',
    'CH2O': 'Consumo de Água',
    'SCC': 'Monitora Calorias',
    'FAF': 'Atividade Física',
    'TUE': 'Tempo em Tecnologia',
    'CALC': 'Consumo de Álcool',
    'MTRANS': 'Transporte'
}

# ============================================================================
# 3. PALETA DE CORES E ORDENAÇÃO
# ============================================================================
# Cores padronizadas para os gráficos
CORES_OBESIDADE = {
    'Abaixo do Peso': '#5bc0de',       # Azul claro
    'Peso Normal': '#5cb85c',          # Verde
    'Sobrepeso Nível I': '#f0ad4e',    # Amarelo
    'Sobrepeso Nível II': '#ff9900',   # Laranja
    'Obesidade Tipo I': '#d9534f',     # Vermelho claro
    'Obesidade Tipo II': '#c9302c',    # Vermelho escuro
    'Obesidade Tipo III (Mórbida)': '#8b0000', # Vinho
    
    # Versões sem acento (para PDF ou fallback)
    'Sobrepeso Nivel I': '#f0ad4e',
    'Sobrepeso Nivel II': '#ff9900',
    'Obesidade Tipo III (Morbida)': '#8b0000'
}

# Ordem lógica para gráficos (Eixo X)
ORDEM_OBESIDADE = [
    'Abaixo do Peso', 
    'Peso Normal', 
    'Sobrepeso Nível I', 
    'Sobrepeso Nível II', 
    'Obesidade Tipo I', 
    'Obesidade Tipo II', 
    'Obesidade Tipo III (Mórbida)'
]