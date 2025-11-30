import streamlit as st
from utils import sidebar_navegacao

# ============================================================================
# 1. CONFIGURAÇÃO INICIAL DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="HealthAnalytics - Home",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 2. BARRA LATERAL (SIDEBAR)
# ============================================================================
sidebar_navegacao()

# ============================================================================
# 3. CORPO PRINCIPAL (HERO SECTION)
# ============================================================================

# Cabeçalho com Emojis para modernizar
st.title("Sistema Inteligente de Predição de Obesidade")
st.subheader("Inteligência Artificial Explicável (XAI) para apoio ao diagnóstico clínico.")

st.markdown("---") 

# Layout de Colunas: Texto (2) vs Imagem (1)
col1, col2 = st.columns([2, 1])

# Coluna 1: Pitch do Projeto
with col1:
    st.markdown("### Objetivo do Sistema")
    st.write("""
    Este projeto utiliza algoritmos de **Machine Learning (Random Forest)** para identificar riscos de obesidade com alta precisão. 
    Mais do que apenas classificar, o sistema explica o **porquê** da decisão e gera documentação clínica automática.
    """)
    
    st.markdown("#### Funcionalidades Avançadas:")
    st.success("**IA Explicável (SHAP):** Entenda matematicamente quais fatores aumentaram ou diminuíram o risco do paciente.")
    st.info("**Laudos Médicos (PDF):** Gere relatórios completos com anamnese e diagnóstico prontos para impressão.")
    st.warning("**Dashboard Interativo:** Explore tendências populacionais com filtros dinâmicos e mapas de calor.")

# Coluna 2: Imagem
with col2:
    st.image("assets/balanca.png", caption="HealthAnalytics v2.0", use_container_width=True)

st.markdown("---")

# ============================================================================
# 4. GUIA DE NAVEGAÇÃO (CARTÕES)
# ============================================================================
st.markdown("### Escolha um módulo para iniciar")

c1, c2, c3 = st.columns(3)

# --- Card 1: Diagnóstico ---
with c1:
    with st.container(border=True):
        st.subheader("Diagnóstico IA")
        st.markdown("""
        Realize consultas individuais. Preencha o formulário biométrico e receba a classificação imediata.
        
        **Inclui:**
        * Gráfico de Risco
        * Análise SHAP (Waterfall)
        * Download de PDF
        """)
        st.markdown("###")
        st.page_link("pages/1_Diagnostico_Preditivo.py", label="Acessar Diagnóstico", use_container_width=True)

# --- Card 2: Dashboard ---
with c2:
    with st.container(border=True):
        st.subheader("Dashboard BI")
        st.markdown("""
        Visão macroscópica dos dados. Entenda correlações entre hábitos alimentares, sedentarismo e peso.
        
        **Inclui:**
        * Filtros Cruzados
        * Mapas de Calor
        * Exportação (Excel/CSV)
        """)
        st.markdown("###")
        st.page_link("pages/2_Dashboard_Analitico.py", label="Acessar Dashboard", use_container_width=True)

# --- Card 3: Performance ---
with c3:
    with st.container(border=True):
        st.subheader("Métricas Técnicas")
        st.markdown("""
        Área de auditoria e validação do modelo. Veja como o algoritmo se comporta em dados de teste.
        
        **Inclui:**
        * Acurácia e F1-Score
        * Matriz de Confusão
        * Relatório por Classe
        """)
        st.markdown("###")
        st.page_link("pages/3_Performance_do_Modelo.py", label="Ver Performance", use_container_width=True)

st.markdown("---")

# ============================================================================
# 5. RODAPÉ
# ============================================================================
st.warning("""
**Aviso Legal:** Este sistema é uma ferramenta de **apoio à decisão** baseada em dados estatísticos. 
Ele não substitui, sob nenhuma hipótese, o diagnóstico clínico e a avaliação presencial realizada por um médico qualificado.
""")

st.markdown("""
<div style="text-align: center; color: grey; font-size: 12px; margin-top: 20px;">
    © 2025 HealthAnalytics | Desenvolvido por <b>Pedro Alves</b><br>
    Tech Challenge Fase 4 - Data Analytics | Modelo: Random Forest Classifier
</div>
""", unsafe_allow_html=True)