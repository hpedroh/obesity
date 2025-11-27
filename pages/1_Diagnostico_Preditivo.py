import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
from utils import sidebar_navegacao
from fpdf import FPDF
import datetime

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
    return joblib.load('saved_model/modelo_obesidade.joblib')

try:
    pipeline = load_model()
except FileNotFoundError:
    st.error("Erro crítico: O arquivo do modelo 'modelo_obesidade.joblib' não foi encontrado.")
    st.stop()

# ============================================================================
# 3. DICIONÁRIOS DE MAPEAMENTO (FRONTEND -> BACKEND)
# ============================================================================
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

dict_fcvc = {"Nunca": 1, "Às vezes": 2, "Sempre": 3}
dict_ch2o = {"Menos de 1L": 1, "Entre 1L e 2L": 2, "Mais de 2L": 3}
dict_faf = {"Nenhuma": 0, "1 a 2 dias/sem": 1, "3 a 4 dias/sem": 2, "5 ou mais dias/sem": 3}
dict_tue = {"0 a 2 horas": 0, "3 a 5 horas": 1, "Mais de 5 horas": 2}

dict_resultado = {
    "Insufficient_Weight": "Abaixo do Peso",
    "Normal_Weight": "Peso Normal",
    "Overweight_Level_I": "Sobrepeso Nivel I",
    "Overweight_Level_II": "Sobrepeso Nivel II",
    "Obesity_Type_I": "Obesidade Tipo I",
    "Obesity_Type_II": "Obesidade Tipo II",
    "Obesity_Type_III": "Obesidade Tipo III (Morbida)"
}

# ============================================================================
# FUNÇÃO: GERADOR DE PDF PROFISSIONAL
# ============================================================================
def create_pdf(paciente_dados, resultado_final, probs_df, riscos, protecoes):
    class PDF(FPDF):
        def header(self):
            # Título do Sistema e Linha Superior
            self.set_font('Arial', 'B', 16)
            self.set_text_color(44, 62, 80)
            self.cell(0, 10, 'HealthAnalytics - Relatório Clínico', 0, 1, 'C')
            
            # Linha decorativa abaixo do título
            self.set_draw_color(44, 62, 80)
            self.set_line_width(0.5)
            self.line(10, 25, 200, 25)
            self.ln(10)

        def footer(self):
            # Rodapé com paginação
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128) # Cinza
            self.cell(0, 10, f'Página {self.page_no()} - Documento gerado via HealthAnalytics', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Definição de Cores Padrão
    COR_TITULO_FUNDO = (44, 62, 80)   # Azul Escuro
    COR_TITULO_TEXTO = (255, 255, 255) # Branco
    
    # 1. Cabeçalho do Laudo (Data)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(100)
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    pdf.cell(0, 6, f'Data de Emissão: {data_atual}', 0, 1, 'R')
    pdf.ln(5)

    # -------------------------------------------------------------------------
    # SEÇÃO 1: DADOS DO PACIENTE
    # -------------------------------------------------------------------------
    # Barra de Título da Seção
    pdf.set_fill_color(*COR_TITULO_FUNDO)
    pdf.set_text_color(*COR_TITULO_TEXTO)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '  1. PERFIL DO PACIENTE (ANAMNESE)', 0, 1, 'L', fill=True)
    pdf.ln(4)

    pdf.set_text_color(0) # Preto
    
    # Função auxiliar para desenhar linhas de dados
    def linha_dado(label, valor, w_label=35, w_val=60, pula_linha=False):
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(w_label, 6, label, 0)
        pdf.set_font('Arial', '', 9)
        # Corta strings muito longas para não quebrar layout
        val_str = str(valor)[:30] 
        pdf.cell(w_val, 6, val_str, 0, 1 if pula_linha else 0)

    # --- Bloco A: Biometria ---
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'Biometria e Dados Pessoais:', 0, 1)
    
    linha_dado('Idade:', f"{paciente_dados['Idade']} anos")
    linha_dado('Gênero:', paciente_dados['Genero'], pula_linha=True)
    
    linha_dado('Peso:', f"{paciente_dados['Peso']} kg")
    linha_dado('Altura:', f"{paciente_dados['Altura']} m", pula_linha=True)
    pdf.ln(2)

    # --- Bloco B: Hábitos e Estilo de Vida ---
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'Estilo de Vida:', 0, 1)

    linha_dado('Hist. Familiar:', paciente_dados['Hist_Familiar'])
    linha_dado('Tabagismo:', paciente_dados['Fuma'], pula_linha=True)

    linha_dado('Álcool:', paciente_dados['Alcool'])
    linha_dado('Ativ. Física:', paciente_dados['Atividade_Fisica'], pula_linha=True)

    linha_dado('Tecnologia:', paciente_dados['Tecnologia'])
    linha_dado('Transporte:', paciente_dados['Transporte'], pula_linha=True)
    pdf.ln(2)

    # --- Bloco C: Alimentação ---
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'Padrão Alimentar:', 0, 1)

    linha_dado('Cons. Calórico:', paciente_dados['Caloricos'])
    linha_dado('Vegetais:', paciente_dados['Vegetais'], pula_linha=True)

    linha_dado('Refeições/Dia:', str(paciente_dados['Refeicoes']))
    linha_dado('Entre Refeições:', paciente_dados['Belisca'], pula_linha=True)

    linha_dado('Ingestão Água:', paciente_dados['Agua'])
    linha_dado('Monitora Cal.:', paciente_dados['Monitora_Cal'], pula_linha=True)

    pdf.ln(5)

    # -------------------------------------------------------------------------
    # SEÇÃO 2: RESULTADO DO DIAGNÓSTICO
    # -------------------------------------------------------------------------
    pdf.set_fill_color(*COR_TITULO_FUNDO)
    pdf.set_text_color(*COR_TITULO_TEXTO)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '  2. DIAGNÓSTICO PREDITIVO (IA)', 0, 1, 'L', fill=True)
    pdf.ln(5)

    # Caixa de fundo cinza claro
    pdf.set_fill_color(240, 240, 240) 
    pdf.set_draw_color(200)
    
    y_antes = pdf.get_y()
    pdf.rect(10, y_antes, 190, 25, 'FD')
    
    pdf.set_y(y_antes + 5)
    pdf.set_text_color(80)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, 'RESULTADO DA ANÁLISE:', 0, 1, 'C')
    
    # Cor do texto baseada no resultado
    pdf.set_font('Arial', 'B', 16)
    res_upper = resultado_final.upper()
    if "OBESIDADE" in res_upper or "OBESITY" in res_upper:
        pdf.set_text_color(192, 57, 43) # Vermelho
    elif "SOBREPESO" in res_upper or "OVERWEIGHT" in res_upper:
        pdf.set_text_color(211, 84, 0)  # Laranja
    elif "ABAIXO" in res_upper or "INSUFFICIENT" in res_upper:
        pdf.set_text_color(41, 128, 185) # Azul
    else:
        pdf.set_text_color(39, 174, 96) # Verde
        
    pdf.cell(0, 8, res_upper, 0, 1, 'C')
    pdf.ln(12)

    # -------------------------------------------------------------------------
    # SEÇÃO 3: ANÁLISE DE FATORES
    # -------------------------------------------------------------------------
    pdf.set_fill_color(*COR_TITULO_FUNDO)
    pdf.set_text_color(*COR_TITULO_TEXTO)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '  3. ANÁLISE DETALHADA DE FATORES', 0, 1, 'L', fill=True)
    pdf.ln(5)

    y_start_columns = pdf.get_y()
    
    # --- Coluna Esquerda: RISCOS ---
    # Define margem direita para não invadir o lado do fator de proteção
    pdf.set_left_margin(10)
    pdf.set_right_margin(110) 
    
    pdf.set_text_color(192, 57, 43) # Vermelho
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'PONTOS DE ATENÇÃO (RISCOS)', 0, 1, 'L')
    
    pdf.set_text_color(50)
    pdf.set_font('Arial', '', 10)
    if riscos:
        for item in riscos:
            clean_item = item.replace('**', '').replace('__', '')
            pdf.multi_cell(0, 6, f"- {clean_item}", 0, 'L')
    else:
        pdf.multi_cell(0, 6, "Nenhum fator crítico identificado.", 0, 'L')
        
    y_end_left = pdf.get_y()
    
    # --- Coluna Direita: PROTEÇÃO ---
    pdf.set_y(y_start_columns)
    pdf.set_left_margin(110)
    pdf.set_right_margin(10)
    
    pdf.set_text_color(39, 174, 96) # Verde
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'FATORES DE PROTEÇÃO', 0, 1, 'L')
    
    pdf.set_text_color(50)
    pdf.set_font('Arial', '', 10)
    if protecoes:
        for item in protecoes:
            clean_item = item.replace('**', '').replace('__', '')
            pdf.multi_cell(0, 6, f"- {clean_item}", 0, 'L')
    else:
        pdf.multi_cell(0, 6, "Poucos hábitos protetores identificados.", 0, 'L')
        
    # Restaura margens originais
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    
    # Sincroniza o cursor para baixo da maior coluna
    pdf.set_y(max(y_end_left, pdf.get_y()) + 15)

    # -------------------------------------------------------------------------
    # AVISO LEGAL
    # -------------------------------------------------------------------------
    if pdf.get_y() > 250:
        pdf.add_page()

    pdf.set_draw_color(200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(150)
    aviso = ("AVISO LEGAL: Este relatório foi gerado automaticamente por inteligência artificial para fins "
             "demonstrativos e de suporte à decisão. As informações aqui contidas não substituem, "
             "sob nenhuma hipótese, a avaliação clínica completa realizada por um médico profissional.")
    pdf.multi_cell(0, 4, aviso, 0, 'C')

    return pdf.output(dest='S').encode('latin-1', 'replace')

# ============================================================================
# 4. INTERFACE DO USUÁRIO
# ============================================================================
st.sidebar.title("Sistema de Apoio Médico")
st.sidebar.info("Este sistema utiliza Machine Learning para auxiliar no diagnóstico de níveis de obesidade.")
st.sidebar.markdown("---")

st.title("Diagnóstico Preditivo de Obesidade")
st.markdown("Preencha o formulário abaixo com os dados do paciente para obter a classificação de risco.")
st.markdown("---")

# ============================================================================
# 5. FORMULÁRIO
# ============================================================================
with st.form("form_diagnostico"):
    
    st.subheader("Dados Pessoais e Biometria")
    c1, c2, c3, c4 = st.columns(4)
    with c1: age = st.number_input("Idade", min_value=1, max_value=120, value=25)
    with c2: gender_pt = st.selectbox("Gênero", list(dict_genero.keys()))
    with c3: height = st.number_input("Altura (m)", min_value=0.50, max_value=2.50, value=1.70, step=0.01, format="%.2f")
    with c4: weight = st.number_input("Peso (kg)", min_value=10.0, max_value=300.0, value=70.0, step=0.1, format="%.1f")

    st.markdown("---")

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

    st.subheader("Atividade Física e Rotina")
    c8, c9, c10 = st.columns(3)
    with c8: faf_label = st.selectbox("Frequência de atividade física semanal", options=list(dict_faf.keys()))
    with c9: tue_label = st.selectbox("Tempo diário em dispositivos tecnológicos", options=list(dict_tue.keys()))
    with c10: transporte_pt = st.selectbox("Meio de transporte principal", list(dict_transporte.keys()))

    st.markdown("###")
    submit_button = st.form_submit_button("Realizar Diagnóstico", type="primary")

# ============================================================================
# 6. LÓGICA DE PREDIÇÃO E RESULTADOS
# ============================================================================
if submit_button:
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
        # Predições
        predicao_en = pipeline.predict(dados_entrada)[0]
        predicao_pt = dict_resultado.get(predicao_en, predicao_en)
        
        probs = pipeline.predict_proba(dados_entrada)[0]
        classes = pipeline.classes_
        
        df_probs = pd.DataFrame({'Classe': classes, 'Probabilidade': probs})
        df_probs['Nome_PT'] = df_probs['Classe'].map(dict_resultado)
        df_probs = df_probs.sort_values('Probabilidade', ascending=True)

        # Fatores
        fatores_risco = []
        fatores_protecao = []

        if hist_pt == "Sim": fatores_risco.append("**Genética:** Histórico familiar presente.")
        else: fatores_protecao.append("**Genética:** Sem histórico familiar.")
        if calorico_pt == "Sim": fatores_risco.append("**Alimentação:** Consumo frequente de hipercalóricos.")
        else: fatores_protecao.append("**Alimentação:** Evita hipercalóricos.")
        if dict_fcvc[fcvc_label] <= 1: fatores_risco.append("**Vegetais:** Baixo consumo de vegetais.")
        elif dict_fcvc[fcvc_label] == 3: fatores_protecao.append("**Vegetais:** Alto consumo de vegetais.")
        if dict_ch2o[ch2o_label] <= 1: fatores_risco.append("**Hidratação:** Água abaixo do recomendado.")
        elif dict_ch2o[ch2o_label] == 3: fatores_protecao.append("**Hidratação:** Ótimo consumo de água.")
        if dict_faf[faf_label] == 0: fatores_risco.append("**Sedentarismo:** Nenhuma atividade física.")
        elif dict_faf[faf_label] >= 2: fatores_protecao.append("**Atividade Física:** Rotina ativa.")
        if dict_tue[tue_label] == 2: fatores_risco.append("**Tecnologia:** Tempo excessivo de tela.")
        if monitora_pt == "Sim": fatores_protecao.append("**Consciência:** Monitora calorias.")
        if fuma_pt == "Sim": fatores_risco.append("**Tabagismo:** Fumante.")
        if alcool_pt in ["Frequentemente", "Sempre"]: fatores_risco.append("**Álcool:** Consumo frequente.")

        # --- EXIBIÇÃO ---
        st.markdown("###")
        
        with st.container(border=True):
            st.subheader("Relatório de Análise Clínica")
            
            col_header_1, col_header_2 = st.columns([0.7, 0.3])
            
            with col_header_1:
                if "Obesity" in predicao_en:
                    st.error(f"#### Diagnóstico: {predicao_pt}")
                    st.markdown(f"**Análise:** O perfil biométrico e comportamental indica compatibilidade com **{predicao_pt}**.")
                elif "Overweight" in predicao_en:
                    st.warning(f"#### Diagnóstico: {predicao_pt}")
                    st.markdown(f"**Análise:** O perfil indica **{predicao_pt}**.")
                elif "Insufficient" in predicao_en:
                    st.warning(f"#### Diagnóstico: {predicao_pt}")
                else:
                    st.success(f"#### Diagnóstico: {predicao_pt}")
            
            with col_header_2:
                # COLETA DE TODOS OS DADOS PARA O PDF COMPLETO
                dados_pdf = {
                    'Idade': age, 
                    'Genero': gender_pt, 
                    'Altura': height, 
                    'Peso': weight,
                    
                    'Hist_Familiar': hist_pt, 
                    'Fuma': fuma_pt,
                    'Alcool': alcool_pt,
                    'Agua': ch2o_label,
                    'Monitora_Cal': monitora_pt,
                    
                    'Caloricos': calorico_pt,
                    'Vegetais': fcvc_label, 
                    'Refeicoes': ncp,
                    'Belisca': belisca_pt,
                    
                    'Atividade_Fisica': faf_label,
                    'Tecnologia': tue_label,
                    'Transporte': transporte_pt
                }
                
                pdf_bytes = create_pdf(dados_pdf, predicao_pt, df_probs, fatores_risco, fatores_protecao)
                
                st.download_button(
                    label="Baixar Laudo PDF",
                    data=pdf_bytes,
                    file_name="laudo_obesidade.pdf",
                    mime="application/pdf",
                    type="primary"
                )

            st.markdown("---")

            # ============================================================
            # GRÁFICO DE RISCO (ESTILO DASHBOARD)
            # ============================================================
            st.markdown("#### Análise de Risco Detalhada (Probabilidades)")
            st.caption("O gráfico abaixo mostra a certeza do modelo para cada categoria.")

            mapa_cores_obesidade = {
                'Abaixo do Peso': '#5bc0de', 'Peso Normal': '#5cb85c',
                'Sobrepeso Nivel I': '#f0ad4e', 'Sobrepeso Nivel II': '#ff9900',
                'Obesidade Tipo I': '#d9534f', 'Obesidade Tipo II': '#c9302c', 
                'Obesidade Tipo III (Morbida)': '#8b0000'
            }
            
            fig_probs = px.bar(
                df_probs, x='Probabilidade', y='Nome_PT', orientation='h',
                color='Nome_PT',
                color_discrete_map=mapa_cores_obesidade
            )
            
            fig_probs.update_traces(
                texttemplate='<b>%{x:.1%}</b>',
                textposition='inside',
                textfont=dict(size=14, color='white'), 
                insidetextfont=dict(family="Arial Black"),
                hovertemplate='<b>Nível:</b> %{y}<br><b>Probabilidade:</b> %{x:.2%}<extra></extra>'
            )
            
            fig_probs.update_layout(
                xaxis_title=None, yaxis_title=None,
                showlegend=False, 
                height=350,
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(tickformat=".0%", showgrid=False, range=[0, 1.05]),
                yaxis=dict(tickfont=dict(size=13))
            )
            
            st.plotly_chart(fig_probs, use_container_width=True)

        # Fatores na tela
        st.markdown("###")
        with st.expander("Entenda o Resultado: Fatores de Risco e Proteção", expanded=True):
            cr, cp = st.columns(2)
            with cr: 
                st.error(f"**Fatores de Risco ({len(fatores_risco)})**")
                for item in fatores_risco: st.write(item)
            with cp: 
                st.success(f"**Fatores de Proteção ({len(fatores_protecao)})**")
                for item in fatores_protecao: st.write(item)

    except Exception as e:
        st.error(f"Ocorreu um erro no processamento: {e}")