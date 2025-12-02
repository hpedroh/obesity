import streamlit as st

def sidebar_topo():
    """
    Renderiza a parte superior da barra lateral (Sidebar).
    Responsável pela injeção de CSS personalizado, título e menu de navegação.
    """
    
    # 1. Configuração de Estilo (CSS)
    # Ajusta a largura mínima e máxima da sidebar
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"][aria-expanded="true"] {
            min-width: 300px;
            max-width: 600px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 2. Cabeçalho
    st.sidebar.title("HealthAnalytics")
    st.sidebar.markdown("---")
    
    # 3. Navegação
    st.sidebar.subheader("Navegação")
    
    st.sidebar.page_link(
        "HealthAnalytics.py",
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

def sidebar_rodape():
    """
    Renderiza a parte inferior da barra lateral.
    Contém links para Documentação, GitHub e créditos.
    """
    st.sidebar.caption("Recursos e Ajuda")
    
    st.sidebar.link_button(
        label="Ler Documentação", 
        url="https://hpedroh.github.io/obesity/",
        use_container_width=True,
        help="Guia de uso, modelagem e detalhes técnicos"
    )

    # Botão do GitHub
    st.sidebar.link_button(
        label="Ver Código no GitHub", 
        url="https://github.com/hpedroh/obesity",
        use_container_width=True,
        type="secondary"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("2025 | Desenvolvido por **Pedro Alves**")

def sidebar_navegacao():
    """Função principal chamada pelas páginas para montar a sidebar."""
    sidebar_topo()
    sidebar_rodape()