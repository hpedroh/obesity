import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
from utils import sidebar_navegacao
from fpdf import FPDF
import datetime
import shap

from constants import (
    DICT_SIM_NAO, DICT_GENERO, DICT_FREQ_CALORICA, DICT_TRANSPORTE,
    DICT_FCVC_NUM, DICT_CH2O_NUM, DICT_FAF_NUM, DICT_TUE_NUM,
    DICT_RESULTADO_PDF, CORES_OBESIDADE,
    DICT_COLUNAS_PT
)

# ============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ============================================================================
st.set_page_config(
    page_title="Predição de Obesidade",
    layout="wide",
    initial_sidebar_state="expanded"
)

sidebar_navegacao()

# ============================================================================
# 2. CARREGAMENTO DOS ATIVOS (MODELO + METADATA)
# ============================================================================
@st.cache_resource
def load_assets():
    # Carrega o Modelo
    try:
        model = joblib.load('saved_model/modelo_obesidade.joblib')
    except FileNotFoundError:
        return None, None
        
    # Carrega o Metadata (Manual de Instruções)
    try:
        meta = joblib.load('saved_model/model_metadata.joblib')
    except FileNotFoundError:
        meta = None
        
    return model, meta

pipeline, metadata = load_assets()

if not pipeline:
    st.error("Erro crítico: Modelo (modelo_obesidade.joblib) não encontrado.")
    st.stop()

# ============================================================================
# FUNÇÃO: GERADOR DE SUGESTÕES
# ============================================================================
def gerar_sugestoes(riscos_identificados):
    """
    Gera dicas genéricas de saúde baseadas APENAS nos riscos detectados.
    Evita prescrever tratamentos, focando em diretrizes gerais de bem-estar.
    """
    sugestoes = []
    
    # Mapeamento: Texto do Risco (parcial) -> Dica
    base_conhecimento = {
        "Água": "**Hidratação:** A ingestão adequada de água (aprox. 2L/dia) é essencial para o metabolismo. Tente manter uma garrafa sempre por perto.",
        "Vegetais": "**Nutrição:** Aumentar o consumo de vegetais e fibras ajuda na saciedade e fornece micronutrientes essenciais.",
        "Calóricos": "**Alimentação:** Alimentos hipercalóricos e processados costumam ter baixa densidade nutricional. Tente substituí-los gradualmente por opções naturais.",
        "Sedentarismo": "**Movimento:** A OMS recomenda pelo menos 150 minutos de atividade moderada por semana. Caminhadas leves já fazem diferença.",
        "Tecnologia": "**Tempo de Tela:** O uso excessivo de dispositivos pode estar associado ao sedentarismo e piora do sono. Tente fazer pausas ativas.",
        "Álcool": "**Consumo de Álcool:** Bebidas alcoólicas possuem 'calorias vazias'. A moderação é chave para o controle de peso.",
        "Tabagismo": "**Saúde Geral:** O tabagismo afeta o sistema cardiovascular e o metabolismo. Buscar apoio profissional para parar é o melhor investimento para sua saúde.",
        "Monitora": "**Consciência:** Manter um diário alimentar ou monitorar o que se come pode ajudar a identificar excessos não percebidos."
    }

    # Verifica quais riscos estão presentes na lista do paciente
    for risco in riscos_identificados:
        for chave, dica in base_conhecimento.items():
            if chave in risco and dica not in sugestoes:
                sugestoes.append(dica)
    
    # Se não achou nada específico, mas tem risco
    if not sugestoes and riscos_identificados:
        sugestoes.append("**Estilo de Vida:** Pequenas mudanças consistentes na rotina, como priorizar alimentos naturais e se manter ativo, trazem grandes resultados a longo prazo.")

    return sugestoes

# ============================================================================
# FUNÇÃO: GERADOR DE PDF COMPLETO
# ============================================================================
def create_pdf(paciente_dados, resultado_final, probs_df, riscos, protecoes, sugestoes_lista):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.set_text_color(44, 62, 80)
            self.cell(0, 10, 'HealthAnalytics - Relatório Clínico', 0, 1, 'C')
            self.set_draw_color(44, 62, 80)
            self.set_line_width(0.5)
            self.line(10, 25, 200, 25)
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Página {self.page_no()} - Documento gerado via HealthAnalytics', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    COR_TITULO_FUNDO = (44, 62, 80)
    COR_TITULO_TEXTO = (255, 255, 255)
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(100)
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    pdf.cell(0, 6, f'Data de Emissão: {data_atual}', 0, 1, 'R')
    pdf.ln(5)

    # SEÇÃO 1: PERFIL
    pdf.set_fill_color(*COR_TITULO_FUNDO)
    pdf.set_text_color(*COR_TITULO_TEXTO)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '  1. PERFIL DO PACIENTE (ANAMNESE)', 0, 1, 'L', fill=True)
    pdf.ln(4)
    
    pdf.set_text_color(0)
    def linha_dado(label, valor, w_label=35, w_val=60, pula_linha=False):
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(w_label, 6, label, 0)
        pdf.set_font('Arial', '', 9)
        pdf.cell(w_val, 6, str(valor)[:35], 0, 1 if pula_linha else 0)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 6, 'Identificação:', 0, 1)
    pdf.set_font('Arial', 'B', 9); pdf.cell(35, 6, 'Nome Paciente:', 0)
    pdf.set_font('Arial', '', 9); pdf.cell(0, 6, str(paciente_dados.get('Nome', 'Não Informado')), 0, 1)
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 6, 'Biometria:', 0, 1)
    linha_dado('Idade:', f"{paciente_dados['Idade']} anos")
    linha_dado('Gênero:', paciente_dados['Genero'], pula_linha=True)
    linha_dado('Peso:', f"{paciente_dados['Peso']} kg")
    linha_dado('Altura:', f"{paciente_dados['Altura']} m", pula_linha=True)
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 6, 'Estilo de Vida e Histórico:', 0, 1)
    linha_dado('Hist. Familiar:', paciente_dados['Hist_Familiar'])
    linha_dado('Tabagismo:', paciente_dados['Fuma'], pula_linha=True)
    linha_dado('Álcool:', paciente_dados['Alcool'])
    linha_dado('Transporte:', paciente_dados['Transporte'], pula_linha=True)
    linha_dado('Ativ. Física:', paciente_dados['Atividade_Fisica'])
    linha_dado('Tempo Tela:', paciente_dados['Tecnologia'], pula_linha=True)
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 6, 'Hábitos Alimentares:', 0, 1)
    linha_dado('Cons. Calórico:', paciente_dados['Caloricos'])
    linha_dado('Vegetais:', paciente_dados['Vegetais'], pula_linha=True)
    linha_dado('Refeições/Dia:', str(paciente_dados['Refeicoes']))
    linha_dado('Entre Refeições:', paciente_dados['Belisca'], pula_linha=True)
    linha_dado('Ingestão Água:', paciente_dados['Agua'])
    linha_dado('Monitora Cal.?', paciente_dados['Monitora_Cal'], pula_linha=True)
    pdf.ln(2)

    # SEÇÃO 2: RESULTADO
    pdf.set_fill_color(*COR_TITULO_FUNDO)
    pdf.set_text_color(*COR_TITULO_TEXTO)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '  2. DIAGNÓSTICO PREDITIVO (IA)', 0, 1, 'L', fill=True)
    pdf.ln(5)

    pdf.set_fill_color(240, 240, 240); pdf.set_draw_color(200)
    y_antes = pdf.get_y()
    pdf.rect(10, y_antes, 190, 25, 'FD')
    pdf.set_y(y_antes + 5)
    pdf.set_text_color(80); pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, 'RESULTADO DA ANÁLISE:', 0, 1, 'C')
    
    pdf.set_font('Arial', 'B', 16)
    res_upper = resultado_final.upper()
    if "OBESIDADE" in res_upper: pdf.set_text_color(192, 57, 43)
    elif "SOBREPESO" in res_upper: pdf.set_text_color(211, 84, 0)
    else: pdf.set_text_color(39, 174, 96)
    pdf.cell(0, 8, res_upper, 0, 1, 'C')
    pdf.ln(12)

    # SEÇÃO 3: FATORES
    pdf.set_fill_color(*COR_TITULO_FUNDO)
    pdf.set_text_color(*COR_TITULO_TEXTO)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, '  3. ANÁLISE DETALHADA (IA EXPLAINABLE)', 0, 1, 'L', fill=True)
    pdf.ln(5)

    y_start = pdf.get_y()
    # Coluna Esquerda
    pdf.set_left_margin(10); pdf.set_right_margin(110)
    pdf.set_text_color(192, 57, 43); pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'FATORES QUE AUMENTAM O RISCO', 0, 1, 'L')
    pdf.set_text_color(50); pdf.set_font('Arial', '', 10)
    if riscos:
        for item in riscos: pdf.multi_cell(0, 6, f"- {item}", 0, 'L')
    else: pdf.multi_cell(0, 6, "Nenhum fator crítico identificado.", 0, 'L')
    y_end_left = pdf.get_y()

    # Coluna Direita
    pdf.set_y(y_start); pdf.set_left_margin(110); pdf.set_right_margin(10)
    pdf.set_text_color(39, 174, 96); pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'FATORES DE PROTEÇÃO (REDUZEM RISCO)', 0, 1, 'L')
    pdf.set_text_color(50); pdf.set_font('Arial', '', 10)
    if protecoes:
        for item in protecoes: pdf.multi_cell(0, 6, f"- {item}", 0, 'L')
    else: pdf.multi_cell(0, 6, "Poucos fatores protetores.", 0, 'L')
    
    # Restaura margens para o resto
    pdf.set_left_margin(10); pdf.set_right_margin(10)
    pdf.set_y(max(y_end_left, pdf.get_y()) + 10)

    # SEÇÃO 4: SUGESTÕES
    if sugestoes_lista:
        pdf.set_fill_color(230, 240, 255)
        pdf.set_text_color(0, 50, 100)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, '  DIRETRIZES DE BEM-ESTAR (Baseadas no perfil)', 0, 1, 'L', fill=True)
        pdf.ln(2)
        
        pdf.set_text_color(50)
        pdf.set_font('Arial', '', 9)
        for dica in sugestoes_lista:
            dica_clean = dica.replace('**', '')
            pdf.multi_cell(0, 5, f"> {dica_clean}")
            pdf.ln(1)
        pdf.ln(5)

    # Aviso Legal
    if pdf.get_y() > 250: pdf.add_page()
    pdf.set_draw_color(200); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(3)
    pdf.set_font('Arial', 'I', 8); pdf.set_text_color(150)
    pdf.multi_cell(0, 4, "AVISO LEGAL: Relatório gerado por IA para fins demonstrativos. As diretrizes acima são genéricas e não substituem prescrição médica.", 0, 'C')

    return pdf.output(dest='S').encode('latin-1', 'replace')

# ============================================================================
# 4. INTERFACE E FORMULÁRIO
# ============================================================================
st.sidebar.title("Sistema de Apoio Médico")
st.sidebar.info("Este sistema utiliza Machine Learning para auxiliar no diagnóstico de níveis de obesidade.")
st.sidebar.markdown("---")

st.title("Diagnóstico Preditivo de Obesidade")
st.markdown("Preencha o formulário abaixo com os dados do paciente para obter a classificação de risco.")
st.markdown("---")

# Controle de estado para exibir resultados
if 'diagnostico_realizado' not in st.session_state:
    st.session_state['diagnostico_realizado'] = False

# Lógica do texto do botão
label_botao = "Atualizar Diagnóstico" if st.session_state['diagnostico_realizado'] else "Realizar Diagnóstico"

with st.form("form_diagnostico", enter_to_submit=False):
    
    st.subheader("Identificação")
    nome_paciente = st.text_input("Nome Completo do Paciente", placeholder="Digite o nome para o laudo...")
    
    st.subheader("Dados Pessoais e Biometria")
    c1, c2, c3, c4 = st.columns(4)
    with c1: age = st.number_input("Idade", 1, 120, 25)
    with c2: gender_pt = st.selectbox("Gênero", list(DICT_GENERO.keys()))
    with c3: height = st.number_input("Altura (m)", 0.50, 2.50, 1.70, 0.01)
    with c4: weight = st.number_input("Peso (kg)", 10.0, 300.0, 70.0, 0.1)

    st.markdown("---")
    st.subheader("Histórico e Hábitos")
    c5, c6, c7 = st.columns(3)
    with c5:
        hist_pt = st.selectbox("Histórico Familiar?", list(DICT_SIM_NAO.keys()))
        calorico_pt = st.selectbox("Consome calóricos?", list(DICT_SIM_NAO.keys()))
        fcvc_label = st.selectbox("Vegetais", list(DICT_FCVC_NUM.keys()))
    with c6:
        ncp = st.slider("Refeições/dia", 1, 4, 3)
        belisca_pt = st.selectbox("Come entre refeições?", list(DICT_FREQ_CALORICA.keys()))
        fuma_pt = st.selectbox("Fuma?", list(DICT_SIM_NAO.keys()))
    with c7:
        ch2o_label = st.selectbox("Água diária", list(DICT_CH2O_NUM.keys()))
        monitora_pt = st.selectbox("Monitora calorias?", list(DICT_SIM_NAO.keys()))
        alcool_pt = st.selectbox("Álcool", list(DICT_FREQ_CALORICA.keys()))

    st.markdown("---")
    st.subheader("Atividade Física")
    c8, c9, c10 = st.columns(3)
    with c8: faf_label = st.selectbox("Ativ. Física Semanal", list(DICT_FAF_NUM.keys()))
    with c9: tue_label = st.selectbox("Tempo Tela/Dia", list(DICT_TUE_NUM.keys()))
    with c10: transporte_pt = st.selectbox("Transporte", list(DICT_TRANSPORTE.keys()))

    st.markdown("###")
    submit_button = st.form_submit_button(label_botao, type="primary")

# ============================================================================
# 5. LÓGICA DE PREDIÇÃO, SHAP E CACHE
# ============================================================================
if submit_button:
    # 1. Monta DataFrame
    dados_entrada = pd.DataFrame({
        'Gender': [DICT_GENERO[gender_pt]],
        'Age': [age], 'Height': [height], 'Weight': [weight],
        'family_history': [DICT_SIM_NAO[hist_pt]],
        'FAVC': [DICT_SIM_NAO[calorico_pt]],
        'FCVC': [DICT_FCVC_NUM[fcvc_label]],
        'NCP': [ncp],
        'CAEC': [DICT_FREQ_CALORICA[belisca_pt]],
        'SMOKE': [DICT_SIM_NAO[fuma_pt]],
        'CH2O': [DICT_CH2O_NUM[ch2o_label]],
        'SCC': [DICT_SIM_NAO[monitora_pt]],
        'FAF': [DICT_FAF_NUM[faf_label]],
        'TUE': [DICT_TUE_NUM[tue_label]],
        'CALC': [DICT_FREQ_CALORICA[alcool_pt]],
        'MTRANS': [DICT_TRANSPORTE[transporte_pt]]
    })
    
    if metadata:
        try:
            # 1. Recupera a lista de colunas esperadas pelo modelo
            cols_esperadas = metadata['features_expected']
            
            # 2. Reorganiza o DataFrame para ter EXATAMENTE a mesma ordem do treino
            dados_entrada = dados_entrada[cols_esperadas]
            
        except KeyError as e:
            st.error(f"Erro de Validação: O modelo esperava a coluna {e}, mas ela não foi gerada.")
            st.stop()

    try:
        # --- PREDIÇÃO ---
        predicao_en = pipeline.predict(dados_entrada)[0]
        predicao_pt = DICT_RESULTADO_PDF.get(predicao_en, predicao_en)
        probs = pipeline.predict_proba(dados_entrada)[0]
        df_probs = pd.DataFrame({'Classe': pipeline.classes_, 'Probabilidade': probs})
        df_probs['Nome_PT'] = df_probs['Classe'].map(DICT_RESULTADO_PDF)
        df_probs = df_probs.sort_values('Probabilidade', ascending=True)

        # --- CÁLCULO DO SHAP ---
        model = pipeline.named_steps['classifier']
        preprocessor = pipeline.named_steps['preprocessor']
        X_transformed = preprocessor.transform(dados_entrada)
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer(X_transformed, check_additivity=False)
        class_idx = list(pipeline.classes_).index(predicao_en)
        
        if len(shap_vals.shape) == 3: shap_values_class = shap_vals[0, :, class_idx].values
        else: shap_values_class = shap_vals[0].values

        # Nomes
        feature_names = []
        if hasattr(preprocessor, 'transformers_'):
            for trans in preprocessor.transformers_:
                if trans[0] != 'remainder':
                    if hasattr(trans[1], 'get_feature_names_out'):
                        feature_names.extend(trans[1].get_feature_names_out(trans[2]))
                    else:
                        feature_names.extend(trans[2])

        df_shap = pd.DataFrame({'Feature': feature_names, 'Impacto': shap_values_class})
        
        def limpar_nome(nome_tecnico):
            for col_code, col_name in DICT_COLUNAS_PT.items():
                if col_code in nome_tecnico:
                    return col_name 
            return nome_tecnico

        df_shap['Nome Amigável'] = df_shap['Feature'].apply(limpar_nome)
        
        # Agrupamento e Ordenação
        df_shap_grouped = df_shap.groupby('Nome Amigável')['Impacto'].sum().reset_index()
        df_shap_grouped['Abs_Impacto'] = df_shap_grouped['Impacto'].abs()
        df_shap_grouped = df_shap_grouped.sort_values('Abs_Impacto', ascending=False)

        # --- GERAÇÃO DAS LISTAS PARA O PDF E UI ---
        top_riscos = df_shap_grouped[df_shap_grouped['Impacto'] > 0].head(5)
        top_protecoes = df_shap_grouped[df_shap_grouped['Impacto'] < 0].head(5)

        fatores_risco = [f"{row['Nome Amigável']} (+{row['Impacto']:.1%})" for _, row in top_riscos.iterrows()]
        fatores_protecao = [f"{row['Nome Amigável']} ({row['Impacto']:.1%})" for _, row in top_protecoes.iterrows()]

        # --- GERAÇÃO DE SUGESTÕES  ---
        lista_riscos_amigaveis = top_riscos['Nome Amigável'].tolist()
        sugestoes_geradas = gerar_sugestoes(lista_riscos_amigaveis)

        # 4. Salvar TUDO no Session State
        st.session_state['resultado_dados'] = {
            'dados_entrada': dados_entrada,
            'predicao_en': predicao_en,
            'predicao_pt': predicao_pt,
            'df_probs': df_probs,
            'riscos': fatores_risco,
            'protecoes': fatores_protecao,
            'sugestoes': sugestoes_geradas, 
            'df_shap_grouped': df_shap_grouped,
            'pdf_context': {
                'Nome': nome_paciente if nome_paciente else "Não Informado",
                'Idade': age, 'Genero': gender_pt, 'Altura': height, 'Peso': weight,
                'Hist_Familiar': hist_pt, 'Fuma': fuma_pt, 'Alcool': alcool_pt,
                'Agua': ch2o_label, 'Monitora_Cal': monitora_pt, 'Caloricos': calorico_pt,
                'Vegetais': fcvc_label, 'Refeicoes': ncp, 'Belisca': belisca_pt,
                'Atividade_Fisica': faf_label, 'Tecnologia': tue_label, 'Transporte': transporte_pt
            }
        }
        st.session_state['diagnostico_realizado'] = True
        
        st.rerun()

    except Exception as e:
        st.error(f"Erro no processamento: {e}")

# ============================================================================
# 6. EXIBIÇÃO DOS RESULTADOS (PERSISTENTE)
# ============================================================================
if st.session_state.get('diagnostico_realizado'):
    
    res = st.session_state['resultado_dados']
    
    st.markdown("###")
    with st.container(border=True):
        st.subheader("Relatório de Análise Clínica")
        
        c_res, c_pdf = st.columns([0.7, 0.3])
        
        with c_res:
            if "Obesity" in res['predicao_en']: st.error(f"#### Diagnóstico: {res['predicao_pt']}")
            elif "Overweight" in res['predicao_en']: st.warning(f"#### Diagnóstico: {res['predicao_pt']}")
            else: st.success(f"#### Diagnóstico: {res['predicao_pt']}")
            st.markdown(f"**Análise:** Perfil compatível com **{res['predicao_pt']}**.")

        with c_pdf:
            pdf_bytes = create_pdf(
                res['pdf_context'], res['predicao_pt'], res['df_probs'], 
                res['riscos'], res['protecoes'], res['sugestoes']
            )
            nome_clean = res['pdf_context']['Nome'].split()[0] if res['pdf_context']['Nome'] != "Não Informado" else "paciente"
            st.download_button("Baixar Laudo PDF", pdf_bytes, f"laudo_{nome_clean}.pdf", "application/pdf", type="primary")

        st.markdown("#### Certeza do Modelo")
        fig_probs = px.bar(
            res['df_probs'], x='Probabilidade', y='Nome_PT', orientation='h', 
            color='Nome_PT', color_discrete_map=CORES_OBESIDADE,
            labels={'Nome_PT': 'Diagnóstico Clínico', 'Probabilidade': 'Nível de Confiança'}
        )
        fig_probs.update_traces(texttemplate='<b>%{x:.1%}</b>', textposition='inside', textfont=dict(size=14, color='white'), insidetextfont=dict(family="Arial Black"))
        fig_probs.update_layout(showlegend=False, height=250, margin=dict(t=10, b=0), xaxis=dict(showgrid=False, tickformat=".0%"), yaxis_title=None, xaxis_title=None)
        st.plotly_chart(fig_probs, use_container_width=True)

    # ---------------------------------------------------------------------
    # SUGESTÕES
    # ---------------------------------------------------------------------
    if res['sugestoes']:
        with st.container(border=True):
            st.subheader("Sugestões de Hábitos Saudáveis")
            st.caption("Abaixo estão diretrizes gerais baseadas nos fatores de risco identificados pelo sistema.")
            for dica in res['sugestoes']:
                st.info(dica)

    # ---------------------------------------------------------------------
    # SHAP VISUAL
    # ---------------------------------------------------------------------
    st.markdown("###")
    with st.expander("Por que o modelo deu esse resultado?", expanded=True):
        st.markdown("""
        O gráfico abaixo mostra **quanto cada fator contribuiu (em %)** para o diagnóstico final.
        - **Vermelho:** Aumenta o risco/probabilidade.
        - **Verde:** Diminui o risco/probabilidade (Proteção).
        """)
        
        df_shap_grouped = res['df_shap_grouped'].sort_values('Abs_Impacto', ascending=True)
        
        df_grafico = df_shap_grouped.tail(10)
        df_ocultos = df_shap_grouped.iloc[:-10]
        
        df_grafico['Tipo'] = df_grafico['Impacto'].apply(lambda x: 'Aumenta Risco' if x > 0 else 'Diminui Risco')
        color_map_shap = {'Aumenta Risco': '#d9534f', 'Diminui Risco': '#5cb85c'}

        fig_shap = px.bar(
            df_grafico, x='Impacto', y='Nome Amigável', orientation='h',
            color='Tipo', color_discrete_map=color_map_shap,
            labels={'Nome Amigável': 'Fator Analisado', 'Impacto': 'Influência no Resultado'}
        )
        
        fig_shap.update_traces(
            texttemplate='<b>%{x:+.1%}</b>', textposition='inside', textfont=dict(size=14, color='white'), insidetextfont=dict(family="Arial Black")
        )
        
        fig_shap.update_layout(
            showlegend=True, legend_title_text=None,
            xaxis_title="Contribuição para o Diagnóstico", yaxis_title=None,
            height=400, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(tickformat=".0%", showgrid=True, gridcolor='#eee')
        )
        fig_shap.add_vline(x=0, line_width=1, line_color="black")
        
        st.plotly_chart(fig_shap, use_container_width=True)
        
        if not df_ocultos.empty:
            limite_corte = df_ocultos['Abs_Impacto'].max()
            nomes_ocultos = df_ocultos['Nome Amigável'].unique().tolist()
            nomes_formatados = ", ".join(nomes_ocultos)
            
            st.info(
                f"**Nota de Leitura:** Fatores com impacto inferior a **{limite_corte:.1%}** "
                f"foram ocultados para simplificar a visualização.\n\n"
                f"Variáveis ocultas: *{nomes_formatados}*."
            )