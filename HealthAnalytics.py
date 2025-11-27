import streamlit as st
from utils import sidebar_navegacao

# ============================================================================
# 1. CONFIGURAÇÃO INICIAL DA PÁGINA
# ============================================================================
# Define o título da aba do navegador, layout (wide) e estado inicial da barra lateral.
st.set_page_config(
    page_title="HealthAnalytics - Obesidade",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 2. BARRA LATERAL (SIDEBAR)
# ============================================================================
sidebar_navegacao()

# ============================================================================
# 3. CORPO PRINCIPAL (MAIN PAGE)
# ============================================================================

# Cabeçalho principal: Título do projeto e subtítulo explicativo.
st.title("Sistema Inteligente de Predição de Obesidade")
st.subheader("Utilizando Inteligência Artificial para apoio ao diagnóstico clínico e saúde preventiva.")

st.markdown("---") # Linha divisória horizontal

# Layout de Colunas: Divide a tela em proporção 2:1 (Texto ocupa 2/3, Imagem ocupa 1/3).
col1, col2 = st.columns([2, 1])

# Coluna 1: Descrição do Projeto e Funcionalidades
with col1:
    st.markdown("### Objetivo")
    st.write("""
    Este projeto foi desenvolvido para auxiliar profissionais de saúde na **identificação precoce de riscos relacionados à obesidade**. 
    Utilizando algoritmos de Machine Learning treinados com dados clínicos e comportamentais, o sistema é capaz de classificar o nível de obesidade de um paciente.
    
    **Principais Funcionalidades:**
    * **Diagnóstico em Tempo Real:** Previsão instantânea baseada em formulário interativo.
    * **Análise de Fatores de Risco:** Identificação de padrões alimentares e de rotina que impactam a saúde.
    * **Suporte à Decisão:** Ferramenta complementar para triagem e encaminhamento médico.
    """)

# Coluna 2: Elemento Visual (Imagem ilustrativa)
with col2:
    st.image("assets/balanca.png", caption="Saúde & Tecnologia", width=256)

st.markdown("---")

# ============================================================================
# 4. GUIA DE NAVEGAÇÃO (LINKS INTERNOS)
# ============================================================================
st.markdown("### Como navegar no sistema")

# Cria duas colunas iguais para os cartões de navegação
c1, c2, c3 = st.columns(3)

# Altura fixa para garantir alinhamento (Ajuste o px se precisar mais/menos espaço)
altura_descricao = "min-height: 100x; display: flex; align-items: center;"

# Bloco de Navegação: Diagnóstico Preditivo
with c1:
    with st.container(border=True):
        st.info("**1. Diagnóstico Preditivo**")
        st.markdown(f"""
        <div style="{altura_descricao}">
            Acesse esta página para realizar uma nova consulta. Preencha os dados biométricos e comportamentais do paciente para obter a classificação de risco.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("####")
        st.page_link("pages/1_Diagnostico_Preditivo.py", label="Ir para Diagnóstico", use_container_width=True)

# Bloco de Navegação: Dashboard Analítico
with c2:
    with st.container(border=True):
        st.info("**2. Dashboard Analítico**")
        st.write(f"""
        <div style="{altura_descricao}">
            Explore os dados históricos e insights visuais. Entenda as correlações entre hábitos (alimentação, exercícios) e os níveis de obesidade na população estudada.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("####")
        st.page_link("pages/2_Dashboard_Analitico.py", label="Ir para Dashboard", use_container_width=True)

# CARD 3: PERFORMANCE
with c3:
    with st.container(border=True):
        st.info("**3. Performance do Modelo**")
        st.write(f"""
        <div style="{altura_descricao}">
            Área técnica. Visualize métricas de acurácia, matriz de confusão e validação do algoritmo Random Forest.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("####")
        st.page_link("pages/3_Performance_do_Modelo.py", label="Ver Performance", use_container_width=True)

st.markdown("---")

# ============================================================================
# 5. RODAPÉ (DISCLAIMER E CRÉDITOS)
# ============================================================================
# Aviso legal importante para sistemas de saúde (Disclaimer)
st.warning("""
**Aviso Importante:** Este sistema é uma ferramenta de **apoio à decisão** e não substitui o diagnóstico clínico realizado por um médico. 
Os resultados devem ser interpretados em conjunto com exames laboratoriais e avaliação presencial.
""")

# Créditos do desenvolvedor e informações técnicas do modelo (HTML centralizado)
st.markdown("""
<div style="text-align: center; color: grey; font-size: 12px;">
    Desenvolvido por Pedro Henrique | Tech Challenge Fase 4 - Data Analytics<br>
    Modelo de Machine Learning: Random Forest Classifier | Acurácia: ~94%
</div>
""", unsafe_allow_html=True)