import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
from utils import sidebar_navegacao

# ============================================================================
# 1. CONFIGURAÇÃO INICIAL E ESTILIZAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Predição de Obesidade",
    layout="wide",
    initial_sidebar_state="expanded"
)

sidebar_navegacao()

# ============================================================================
# 2. CARREGAMENTO DO MODELO (PIPELINE)
# ============================================================================
@st.cache_resource
def load_model():
    # Carrega o pipeline completo (Pré-processamento + Modelo)
    # O cache evita recarregar o arquivo pesado a cada interação do usuário.
    return joblib.load('saved_model/modelo_obesidade.joblib')

try:
    pipeline = load_model()
except FileNotFoundError:
    st.error("Erro crítico: O arquivo do modelo 'modelo_obesidade.joblib' não foi encontrado.")
    st.stop()

# ============================================================================
# 3. DICIONÁRIOS DE MAPEAMENTO (FRONTEND -> BACKEND)
# ============================================================================
# O modelo foi treinado com dados em Inglês ou códigos numéricos.
# Estes dicionários traduzem as entradas amigáveis (PT-BR) para o formato técnico.

# --- Mapeamentos Categóricos (Strings) ---
dict_sim_nao = {"Sim": "yes", "Não": "no"}
dict_genero = {"Masculino": "Male", "Feminino": "Female"}
dict_freq_calorica = {
    "Não": "no", 
    "Às vezes": "Sometimes", 
    "Frequentemente": "Frequently", 
    "Sempre": "Always"
}
dict_transporte = {
    "Transporte Público": "Public_Transportation", 
    "Caminhada": "Walking",
    "Carro": "Automobile", 
    "Moto": "Motorbike", 
    "Bicicleta": "Bike"
}

# --- Mapeamentos Numéricos (Escalas Ordinais) ---
# Convertem as escolhas de texto dos Selectbox para os números (0, 1, 2, 3) esperados pelo modelo.
dict_fcvc = {"Nunca": 1, "Às vezes": 2, "Sempre": 3}
dict_ch2o = {"Menos de 1L": 1, "Entre 1L e 2L": 2, "Mais de 2L": 3}
dict_faf = {"Nenhuma": 0, "1 a 2 dias/sem": 1, "3 a 4 dias/sem": 2, "5 ou mais dias/sem": 3}
dict_tue = {"0 a 2 horas": 0, "3 a 5 horas": 1, "Mais de 5 horas": 2}

# --- Tradução do Resultado (Target) ---
dict_resultado = {
    "Insufficient_Weight": "Abaixo do Peso",
    "Normal_Weight": "Peso Normal",
    "Overweight_Level_I": "Sobrepeso Nível I",
    "Overweight_Level_II": "Sobrepeso Nível II",
    "Obesity_Type_I": "Obesidade Tipo I",
    "Obesity_Type_II": "Obesidade Tipo II",
    "Obesity_Type_III": "Obesidade Tipo III (Mórbida)"
}

# ============================================================================
# 4. INTERFACE DO USUÁRIO (HEADER E SIDEBAR)
# ============================================================================
st.sidebar.title("Sistema de Apoio Médico")
st.sidebar.info("Este sistema utiliza Machine Learning para auxiliar no diagnóstico de níveis de obesidade com base em hábitos e biometria.")
st.sidebar.markdown("---")

st.title("Diagnóstico Preditivo de Obesidade")
st.markdown("Preencha o formulário abaixo com os dados do paciente para obter a classificação de risco.")
st.markdown("---")

# ============================================================================
# 5. FORMULÁRIO DE COLETA DE DADOS
# ============================================================================
# O uso de st.form agrupa as variáveis e envia tudo de uma vez ao clicar no botão.
with st.form("form_diagnostico"):
    
    # --- Seção A: Biometria ---
    st.subheader("Dados Pessoais e Biometria")
    c1, c2, c3, c4 = st.columns(4)
    with c1: age = st.number_input("Idade", min_value=1, max_value=120, value=25)
    with c2: gender_pt = st.selectbox("Gênero", list(dict_genero.keys()))
    with c3: height = st.number_input("Altura (m)", min_value=0.50, max_value=2.50, value=1.70, step=0.01, format="%.2f")
    with c4: weight = st.number_input("Peso (kg)", min_value=10.0, max_value=300.0, value=70.0, step=0.1, format="%.1f")

    st.markdown("---")

    # --- Seção B: Hábitos Alimentares ---
    st.subheader("Histórico e Hábitos")
    c5, c6, c7 = st.columns(3)
    with c5:
        hist_pt = st.selectbox("Histórico Familiar de Obesidade?", list(dict_sim_nao.keys()))
        calorico_pt = st.selectbox("Consome alimentos calóricos frequentemente?", list(dict_sim_nao.keys()))
        fcvc_label = st.selectbox("Frequência de consumo de vegetais", list(dict_fcvc.keys()))
    
    with c6:
        ncp = st.slider("Número de refeições principais por dia", 1, 4, 3)
        belisca_pt = st.selectbox("Come entre refeições?", list(dict_freq_calorica.keys()))
        fuma_pt = st.selectbox("Fuma?", list(dict_sim_nao.keys()))
        
    with c7:
        ch2o_label = st.selectbox("Consumo de água diário", options=list(dict_ch2o.keys()))
        monitora_pt = st.selectbox("Monitora calorias diárias?", list(dict_sim_nao.keys()))
        alcool_pt = st.selectbox("Consumo de álcool", list(dict_freq_calorica.keys()))

    st.markdown("---")

    # --- Seção C: Estilo de Vida ---
    st.subheader("Atividade Física e Rotina")
    c8, c9, c10 = st.columns(3)
    with c8: faf_label = st.selectbox("Frequência de atividade física semanal", options=list(dict_faf.keys()))
    with c9: tue_label = st.selectbox("Tempo diário em dispositivos tecnológicos", options=list(dict_tue.keys()))
    with c10: transporte_pt = st.selectbox("Meio de transporte principal", list(dict_transporte.keys()))

    st.markdown("###")
    submit_button = st.form_submit_button("Realizar Diagnóstico", type="primary")

# ============================================================================
# 6. LÓGICA DE PREDIÇÃO E ANÁLISE DE RISCO
# ============================================================================
if submit_button:
    # 1. Montagem do DataFrame (Input do Modelo)
    dados_entrada = pd.DataFrame({
        'Gender': [dict_genero[gender_pt]],
        'Age': [age],
        'Height': [height],
        'Weight': [weight],
        'family_history': [dict_sim_nao[hist_pt]],
        'FAVC': [dict_sim_nao[calorico_pt]],
        'FCVC': [dict_fcvc[fcvc_label]],
        'NCP': [ncp],
        'CAEC': [dict_freq_calorica[belisca_pt]],
        'SMOKE': [dict_sim_nao[fuma_pt]],
        'CH2O': [dict_ch2o[ch2o_label]],
        'SCC': [dict_sim_nao[monitora_pt]],
        'FAF': [dict_faf[faf_label]],
        'TUE': [dict_tue[tue_label]],
        'CALC': [dict_freq_calorica[alcool_pt]],
        'MTRANS': [dict_transporte[transporte_pt]]
    })

    try:
        # 2. Predições
        predicao_en = pipeline.predict(dados_entrada)[0]
        predicao_pt = dict_resultado.get(predicao_en, predicao_en)
        
        probs = pipeline.predict_proba(dados_entrada)[0]
        classes = pipeline.classes_
        
        # DataFrame para o gráfico
        df_probs = pd.DataFrame({'Classe': classes, 'Probabilidade': probs})
        df_probs['Nome_PT'] = df_probs['Classe'].map(dict_resultado)
        df_probs = df_probs.sort_values('Probabilidade', ascending=True) # Ordena para o gráfico

        # 3. Exibição dos Resultados (Visual Novo)
        st.markdown("###")
        
        # Container com borda para destacar o relatório do resto da página
        with st.container(border=True):
            st.subheader("Relatório de Análise Clínica")
            
            # --- Bloco A: Diagnóstico Principal (Topo) ---
            # Usamos ícones nativos do st.error/warning para dar destaque
            if "Obesity" in predicao_en:
                st.error(f"## Diagnóstico: {predicao_pt}")
                st.markdown(f"**Análise:** O perfil biométrico e comportamental indica compatibilidade com **{predicao_pt}**.")
                st.warning("**Recomendação Clínica:** Encaminhamento prioritário para endocrinologista e nutricionista.")
            
            elif "Overweight" in predicao_en:
                st.warning(f"## Diagnóstico: {predicao_pt}")
                st.markdown(f"**Análise:** O perfil indica **{predicao_pt}**, um sinal de alerta para progressão de peso.")
                st.info("**Recomendação Clínica:** Mudança de estilo de vida, foco em dieta e atividade física.")
            
            elif "Insufficient" in predicao_en:
                st.warning(f"## Diagnóstico: {predicao_pt}")
                st.info("**Recomendação:** Avaliação nutricional para ganho de massa magra/peso saudável.")
            
            else:
                st.success(f"## Diagnóstico: {predicao_pt}")
                st.markdown("**Análise:** Os indicadores estão dentro da normalidade. Manter hábitos saudáveis.")

            st.markdown("---")

            # --- Bloco B: Gráfico de Risco (Full Width) ---
            # Agora fora de colunas apertadas, ocupando a largura total
            st.markdown("#### Análise de Risco Detalhada (Probabilidades)")
            st.caption("O gráfico abaixo mostra a 'certeza' do modelo. Barras maiores indicam maior compatibilidade com aquele nível.")

            cores_risco = {
                'Abaixo do Peso': '#5bc0de', 'Peso Normal': '#5cb85c',
                'Sobrepeso Nível I': '#f0ad4e', 'Sobrepeso Nível II': '#ff9900',
                'Obesidade Tipo I': '#d9534f', 'Obesidade Tipo II': '#c9302c', 'Obesidade Tipo III': '#8b0000'
            }

            fig_probs = px.bar(
                df_probs, 
                x='Probabilidade', 
                y='Nome_PT', 
                orientation='h',
                text_auto='.1%', 
                color='Nome_PT',
                color_discrete_map=cores_risco
            )
            
            fig_probs.update_traces(
                textfont=dict(size=12, color='white'), # Fonte maior
                textposition='inside',
                insidetextfont=dict(family="Arial Black"),
                hovertemplate='<b>Nível:</b> %{y}<br><b>Probabilidade:</b> %{x:.1%}<extra></extra>'
            )
            
            fig_probs.update_layout(
                xaxis_title="Probabilidade (%)", yaxis_title=None,
                showlegend=False, 
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(range=[0, 1]), # Remove eixo X numérico para limpar
                height=300 # Altura um pouco maior para não espremer as barras
            )
            
            st.plotly_chart(fig_probs, use_container_width=True)

        # --- NOVO BLOCO: Análise de Fatores (Interpretador) ---
        st.markdown("###")
        with st.expander("Entenda o Resultado: Fatores de Risco e Proteção", expanded=True):
            st.write("Baseado nos dados informados, estes são os pontos que mais impactaram o diagnóstico:")
            
            c_risco, c_protecao = st.columns(2)
            
            # Listas para armazenar os feedbacks
            fatores_risco = []
            fatores_protecao = []

            # --- Lógica de Análise (Regras de Negócio) ---
            
            # 1. Histórico Familiar (Forte Preditivo)
            if hist_pt == "Sim":
                fatores_risco.append("**Genética:** Histórico familiar de obesidade presente.")
            else:
                fatores_protecao.append("**Genética:** Sem histórico familiar de obesidade.")

            # 2. Alimentação Calórica (FAVC)
            if calorico_pt == "Sim":
                fatores_risco.append("**Alimentação:** Consumo frequente de alimentos hipercalóricos.")
            else:
                fatores_protecao.append("**Alimentação:** Evita alimentos hipercalóricos.")

            # 3. Vegetais (FCVC) - Escala 1 a 3
            if dict_fcvc[fcvc_label] <= 1: # Nunca
                fatores_risco.append("**Vegetais:** Baixo consumo de vegetais nas refeições.")
            elif dict_fcvc[fcvc_label] == 3: # Sempre
                fatores_protecao.append("**Vegetais:** Alto consumo de vegetais (fator protetor).")

            # 4. Água (CH2O) - Escala 1 a 3
            if dict_ch2o[ch2o_label] <= 1: # Menos de 1L
                fatores_risco.append("**Hidratação:** Consumo de água abaixo do recomendado (< 1L).")
            elif dict_ch2o[ch2o_label] == 3: # Mais de 2L
                fatores_protecao.append("**Hidratação:** Ótimo consumo de água (> 2L).")

            # 5. Atividade Física (FAF) - Escala 0 a 3
            if dict_faf[faf_label] == 0: # Nenhuma
                fatores_risco.append("**Sedentarismo:** Nenhuma atividade física semanal.")
            elif dict_faf[faf_label] >= 2: # 3 a 4x ou mais
                fatores_protecao.append("**Atividade Física:** Rotina de exercícios ativa.")

            # 6. Tecnologia (TUE) - Escala 0 a 2
            if dict_tue[tue_label] == 2: # Mais de 5h
                fatores_risco.append("**Tecnologia:** Tempo excessivo de tela (> 5h/dia).")
            
            # 7. Monitoramento (SCC)
            if monitora_pt == "Sim":
                fatores_protecao.append("**Consciência:** Monitora a ingestão calórica.")

            # 8. Álcool e Fumo
            if fuma_pt == "Sim":
                fatores_risco.append("**Tabagismo:** Hábito de fumar presente.")
            if alcool_pt in ["Frequentemente", "Sempre"]:
                fatores_risco.append("**Álcool:** Consumo frequente de bebidas alcoólicas.")

            # --- Exibição Visual ---
            with c_risco:
                st.error(f"**Fatores de Risco ({len(fatores_risco)})**")
                if fatores_risco:
                    for item in fatores_risco:
                        st.write(item)
                else:
                    st.write("Nenhum fator de risco crítico identificado nos hábitos principais.")

            with c_protecao:
                st.success(f"**Fatores de Proteção ({len(fatores_protecao)})**")
                if fatores_protecao:
                    for item in fatores_protecao:
                        st.write(item)
                else:
                    st.write("Poucos hábitos protetores identificados. Sugerir mudanças no estilo de vida.")
            
    except Exception as e:
        st.error(f"Ocorreu um erro no processamento: {e}")
        st.write("Verifique os dados de entrada.")