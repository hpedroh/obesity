import streamlit as st

def sidebar_topo():
    """
    Renderiza a parte superior da barra lateral (Sidebar).
    Responsável pela injeção de CSS personalizado, título e menu de navegação entre páginas.
    """
    
    # 1. Configuração de Estilo (CSS)
    # Ajusta a largura mínima e máxima da sidebar para melhor visualização em telas grandes
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

    # 2. Cabeçalho do Projeto
    st.sidebar.title("HealthAnalytics")
    st.sidebar.markdown("---") # Linha divisória visual
    
    # 3. Menu de Navegação Interna
    st.sidebar.subheader("Navegação")
    
    # Link: Home / Entrypoint
    st.sidebar.page_link(
        "HealthAnalytics.py",
        label="Página Inicial", 
        use_container_width=True
    )
    
    # Link: Módulo de IA
    st.sidebar.page_link(
        "pages/1_Diagnostico_Preditivo.py", 
        label="Diagnóstico IA", 
        use_container_width=True
    )
    
    # Link: Módulo de BI
    st.sidebar.page_link(
        "pages/2_Dashboard_Analitico.py", 
        label="Dashboard e KPIs", 
        use_container_width=True
    )
    
    # Link: Módulo Técnico
    st.sidebar.page_link(
        "pages/3_Performance_do_Modelo.py", 
        label="Performance do Modelo", 
        use_container_width=True
    )
    
    # Separação para o rodapé
    st.sidebar.markdown("---")

def sidebar_rodape():
    """
    Renderiza a parte inferior da barra lateral.
    Contém links para recursos externos (Documentação/GitHub) e créditos.
    """
    
    # 1. Cabeçalho de Recursos
    st.sidebar.caption("Recursos e Ajuda")

    # 2. Botões de Links Externos
    
    # Link para Documentação (MkDocs)
    st.sidebar.link_button(
        label="Ler Documentação", 
        url="https://hpedroh.github.io/obesity/",
        use_container_width=True,
        help="Guia de uso, modelagem e detalhes técnicos do sistema."
    )

    # Link para Repositório (GitHub)
    st.sidebar.link_button(
        label="Ver Código no GitHub", 
        url="https://github.com/hpedroh/obesity",
        use_container_width=True,
        type="secondary",
    )
    
    # 3. Créditos e Copyright
    st.sidebar.markdown("---")
    st.sidebar.caption("2025 | Desenvolvido por **Pedro Alves**")

def sidebar_navegacao():
    """
    Função controladora principal da Sidebar.
    
    Deve ser importada e chamada em todas as páginas do projeto para 
    garantir a consistência visual e de navegação.
    """
    sidebar_topo()
    sidebar_rodape()