import streamlit as st

def sidebar_navegacao():
    """
    Função para criar a barra lateral personalizada em todas as páginas.
    """

    st.markdown(
        """
        <style>
        /* Ajusta a largura apenas quando a barra está aberta */
        section[data-testid="stSidebar"][aria-expanded="true"] {
            min-width: 300px;
            max-width: 600px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.title("HealthAnalytics")
    
    # Linha divisória
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("Navegação")
    
    # Botões de Navegação (st.page_link é NATIVO e muito rápido)
    # Dica: Use use_container_width=True para ficar igual ao do seu amigo (preenchendo tudo)
    
    st.sidebar.page_link(
        "HealthAnalytics.py", # Nome exato do seu arquivo principal
        label="Página Inicial", 
        use_container_width=True
    )
    
    st.sidebar.page_link(
        "pages/1_Diagnostico_Preditivo.py", 
        label="Diagnóstico IA", 
        use_container_width=True
    )
    
    st.sidebar.page_link(
        "pages/2_Dashboard_Analitico.py", 
        label="Dashboard e KPIs", 
        use_container_width=True
    )
    
    st.sidebar.page_link(
        "pages/3_Performance_do_Modelo.py", 
        label="Performance do Modelo", 
        use_container_width=True
    )
    
    st.sidebar.markdown("---")

    st.sidebar.caption("Acesso ao Código")
    
    st.sidebar.link_button(
        label="Ver Repositório GitHub", 
        url="https://github.com/hpedroh/obesity#",
        use_container_width=True,
        type="secondary"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 | Desenvolvido por **Pedro Henrique**")