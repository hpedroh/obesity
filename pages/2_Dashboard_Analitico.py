import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np
import io
from utils import sidebar_navegacao

# ============================================================================
# 1. CONFIGURAÇÃO E ESTILIZAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(page_title="Dashboard Analítico", layout="wide")

sidebar_navegacao()

st.title("Dashboard Analítico de Obesidade")
st.markdown("Explore os dados históricos de forma dinâmica. Utilize os **filtros na barra lateral** para segmentar a análise.")

# ============================================================================
# 2. CARREGAMENTO E PRÉ-PROCESSAMENTO DE DADOS
# ============================================================================
@st.cache_data
def load_data():
    # Tenta carregar o CSV de diferentes caminhos (local vs produção/nuvem)
    try:
        try:
            df = pd.read_csv('data/obesity.csv')
        except:
            df = pd.read_csv('../data/obesity.csv')
            
        # Padroniza o nome da coluna alvo (Target)
        if 'NObeyesdad' in df.columns:
            df.rename(columns={'NObeyesdad': 'Obesity'}, inplace=True)
        elif 'Obesity' in df.columns:
            df.rename(columns={'Obesity': 'Obesity'}, inplace=True)
            
        return df
    except Exception as e:
        st.error(f"Erro crítico ao carregar dados: {e}")
        return None

df_raw = load_data()

# --- MAPEAMENTOS E TRADUÇÕES ---
# Estes dicionários são usados para traduzir os dados brutos (Inglês/Códigos)
# para Português amigável no Dashboard.

# Dicionário Geral (Categorias simples)
dict_geral = {
    'Insufficient_Weight': 'Abaixo do Peso',
    'Normal_Weight': 'Peso Normal',
    'Overweight_Level_I': 'Sobrepeso Nível I',
    'Overweight_Level_II': 'Sobrepeso Nível II',
    'Obesity_Type_I': 'Obesidade Tipo I',
    'Obesity_Type_II': 'Obesidade Tipo II',
    'Obesity_Type_III': 'Obesidade Tipo III',
    'Male': 'Masculino', 'Female': 'Feminino',
    'yes': 'Sim', 'no': 'Não',
    'Public_Transportation': 'Transporte Público', 'Walking': 'Caminhada',
    'Automobile': 'Carro', 'Motorbike': 'Moto', 'Bike': 'Bicicleta',
    'Sometimes': 'Às vezes',
    'Frequently': 'Frequentemente',
    'Always': 'Sempre'
}

# Dicionários Específicos (Para transformar códigos numéricos em texto explicativo)
dict_fcvc_map = {1: "Nunca", 2: "Às vezes", 3: "Sempre"}
dict_ch2o_map = {1: "Menos de 1L", 2: "Entre 1L e 2L", 3: "Mais de 2L"}
dict_faf_map = {0: "Nenhuma", 1: "1 a 2 dias/sem", 2: "3 a 4 dias/sem", 3: "5 ou mais dias/sem"}
dict_tue_map = {0: "0 a 2 horas", 1: "3 a 5 horas", 2: "Mais de 5 horas"}

# Renomeação das Colunas para Português (Exibição final)
dict_colunas = {
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

# Mapa de Cores Semântico (Vermelho = Perigo, Verde = Bom)
# Garante consistência visual em todos os gráficos
mapa_cores_obesidade = {
    'Abaixo do Peso': '#5bc0de',       # Azul claro
    'Peso Normal': '#5cb85c',          # Verde
    'Sobrepeso Nível I': '#f0ad4e',    # Amarelo
    'Sobrepeso Nível II': '#ff9900',   # Laranja
    'Obesidade Tipo I': '#d9534f',     # Vermelho claro
    'Obesidade Tipo II': '#c9302c',    # Vermelho escuro
    'Obesidade Tipo III': '#8b0000'    # Vinho/Sangue (Crítico)
}

# --- APLICAÇÃO DAS TRANSFORMAÇÕES ---
if df_raw is not None:
    df = df_raw.copy()
    
    # 1. Tratamento de Dados Numéricos (Arredondamento)
    # As colunas de escala (1 a 3) vêm com decimais do dataset original (ruído).
    # Precisamos arredondar para converter em categorias limpas.
    cols_to_round = ['FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']
    
    # NCP deve ser tratado com cuidado para não virar texto antes da hora
    if 'NCP' in df.columns:
        df['NCP'] = pd.to_numeric(df['NCP'], errors='coerce').fillna(1).round().astype(int)

    for col in cols_to_round:
        if col in df.columns and col != 'NCP':
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).round().astype(int)

    # 2. Tradução de Códigos Numéricos para Texto (Visualização)
    if 'FCVC' in df.columns: df['FCVC'] = df['FCVC'].replace(dict_fcvc_map)
    if 'CH2O' in df.columns: df['CH2O'] = df['CH2O'].replace(dict_ch2o_map)
    if 'FAF' in df.columns:  df['FAF']  = df['FAF'].replace(dict_faf_map)
    if 'TUE' in df.columns:  df['TUE']  = df['TUE'].replace(dict_tue_map)

    # 3. Tradução Geral e Renomeação
    df.replace(dict_geral, inplace=True)
    df.rename(columns=dict_colunas, inplace=True)

    # Ordem Lógica dos Níveis de Obesidade (Para ordenar eixos dos gráficos)
    ordem_obesidade = [
        'Abaixo do Peso', 'Peso Normal', 'Sobrepeso Nível I', 
        'Sobrepeso Nível II', 'Obesidade Tipo I', 'Obesidade Tipo II', 'Obesidade Tipo III'
    ]
    
    # ============================================================================
    # 3. BARRA LATERAL DE FILTROS
    # ============================================================================
    st.sidebar.header("Filtros Avançados")
    st.sidebar.markdown("Use os grupos abaixo para filtrar a base de dados.")

    # --- GRUPO 1: DADOS DEMOGRÁFICOS ---
    with st.sidebar.expander("Dados Pessoais e Físicos", expanded=True):
        obesidade_filtro = st.multiselect("Nível de Obesidade", options=df['Nível de Obesidade'].unique(), default=df['Nível de Obesidade'].unique())
        genero_filtro = st.multiselect("Gênero", options=df['Gênero'].unique(), default=df['Gênero'].unique())
        
        # Sliders com proteção para min/max iguais (evita erro do Streamlit)
        min_age, max_age = int(df['Idade'].min()), int(df['Idade'].max())
        if min_age == max_age: max_age += 1
        idade_filtro = st.slider("Faixa Etária", min_age, max_age, (min_age, max_age))

        min_height, max_height = float(df['Altura'].min()), float(df['Altura'].max())
        if min_height == max_height: max_height += 0.01
        altura_filtro = st.slider("Altura (m)", min_height, max_height, (min_height, max_height))

        min_weight, max_weight = float(df['Peso'].min()), float(df['Peso'].max())
        if min_weight == max_weight: max_weight += 1.0
        peso_filtro = st.slider("Peso (kg)", min_weight, max_weight, (min_weight, max_weight))
        
        hist_filtro = st.multiselect("Histórico Familiar", options=df['Histórico Familiar'].unique(), default=df['Histórico Familiar'].unique())

    # --- GRUPO 2: HÁBITOS ALIMENTARES ---
    with st.sidebar.expander("Hábitos Alimentares", expanded=False):
        favc_filtro = st.multiselect("Alimentos Calóricos", options=df['Consumo Calórico'].unique(), default=df['Consumo Calórico'].unique())
        
        # Ordenação manual das opções para lógica (Nunca -> Sempre)
        fcvc_order = ["Nunca", "Às vezes", "Sempre"]
        fcvc_options = [x for x in fcvc_order if x in df['Consumo de Vegetais'].unique()]
        fcvc_filtro = st.multiselect("Consumo de Vegetais", options=fcvc_options, default=fcvc_options)
        
        ncp_options = sorted(df['Refeições por Dia'].unique().astype(int))
        ncp_filtro = st.multiselect("Refeições por Dia", options=ncp_options, default=ncp_options)
        
        caec_filtro = st.multiselect("Comer entre Refeições", options=df['Comer entre Refeições'].unique(), default=df['Comer entre Refeições'].unique())
        
        ch2o_order = ["Menos de 1L", "Entre 1L e 2L", "Mais de 2L"]
        ch2o_options = [x for x in ch2o_order if x in df['Consumo de Água'].unique()]
        ch2o_filtro = st.multiselect("Consumo de Água", options=ch2o_options, default=ch2o_options)
        
        scc_filtro = st.multiselect("Monitora Calorias?", options=df['Monitora Calorias'].unique(), default=df['Monitora Calorias'].unique())
        calc_filtro = st.multiselect("Consumo de Álcool", options=df['Consumo de Álcool'].unique(), default=df['Consumo de Álcool'].unique())

    # --- GRUPO 3: ESTILO DE VIDA ---
    with st.sidebar.expander("Estilo de Vida", expanded=False):
        smoke_filtro = st.multiselect("Fumante", options=df['Fumante'].unique(), default=df['Fumante'].unique())
        
        faf_order = ["Nenhuma", "1 a 2 dias/sem", "3 a 4 dias/sem", "5 ou mais dias/sem"]
        faf_options = [x for x in faf_order if x in df['Atividade Física'].unique()]
        faf_filtro = st.multiselect("Atividade Física", options=faf_options, default=faf_options)
        
        tue_order = ["0 a 2 horas", "3 a 5 horas", "Mais de 5 horas"]
        tue_options = [x for x in tue_order if x in df['Tempo em Tecnologia'].unique()]
        tue_filtro = st.multiselect("Tempo em Tecnologia", options=tue_options, default=tue_options)
        
        transp_filtro = st.multiselect("Transporte", options=df['Transporte'].unique(), default=df['Transporte'].unique())

    # --- FILTRAGEM DO DATAFRAME ---
    # Construção dinâmica da query para performance e clareza
    filtros_query = []
    
    # Adiciona condições à query apenas se os filtros estiverem ativos
    filtros_query.append("`Nível de Obesidade` in @obesidade_filtro")
    filtros_query.append("`Gênero` in @genero_filtro")
    filtros_query.append("Idade >= @idade_filtro[0] and Idade <= @idade_filtro[1]")
    filtros_query.append("Altura >= @altura_filtro[0] and Altura <= @altura_filtro[1]")
    filtros_query.append("Peso >= @peso_filtro[0] and Peso <= @peso_filtro[1]")
    filtros_query.append("`Histórico Familiar` in @hist_filtro")
    filtros_query.append("`Consumo Calórico` in @favc_filtro")
    filtros_query.append("`Consumo de Vegetais` in @fcvc_filtro")
    filtros_query.append("`Refeições por Dia` in @ncp_filtro")
    filtros_query.append("`Comer entre Refeições` in @caec_filtro")
    filtros_query.append("`Consumo de Água` in @ch2o_filtro")
    filtros_query.append("`Monitora Calorias` in @scc_filtro")
    filtros_query.append("`Consumo de Álcool` in @calc_filtro")
    filtros_query.append("`Fumante` in @smoke_filtro")
    filtros_query.append("`Atividade Física` in @faf_filtro")
    filtros_query.append("`Tempo em Tecnologia` in @tue_filtro")
    filtros_query.append("`Transporte` in @transp_filtro")

    # Executa o filtro
    query_final = " & ".join(filtros_query)
    df_filtered = df.query(query_final)

    # ============================================================================
    # 4. KPIs (INDICADORES CHAVE DE DESEMPENHO)
    # ============================================================================
    st.markdown("### Resumo da Seleção")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    if len(df_filtered) > 0:
        total_pacientes = len(df_filtered)
        media_idade = int(df_filtered['Idade'].mean())
        
        # Conta quantos pacientes têm "Obesidade" no nome da categoria
        qtd_obesos = len(df_filtered[df_filtered['Nível de Obesidade'].astype(str).str.contains("Obesidade")])
        perc_obesidade = (qtd_obesos / total_pacientes * 100)
        media_peso = df_filtered['Peso'].mean()

        kpi1.metric("Pacientes Analisados", f"{total_pacientes}", border=True)
        kpi2.metric("Média de Idade", f"{media_idade:} anos", border=True)
        kpi3.metric("Taxa de Obesidade", f"{perc_obesidade:.1f}%", border=True)
        kpi4.metric("Peso Médio", f"{media_peso:.1f} kg", border=True)
    
    else:
        # Tratamento para quando o filtro zera os dados
        kpi1.metric("Pacientes Analisados", "0", border=True)
        kpi2.metric("Média de Idade", "0 anos", border=True)
        kpi3.metric("Taxa de Obesidade", "0.0%", border=True)
        kpi4.metric("Peso Médio", "0.0 kg", border=True)
        st.warning("Nenhum paciente encontrado com essa combinação de filtros. Tente limpar alguns filtros na barra lateral.")
    
    st.markdown("---")

    # ============================================================================
    # 5. CONTEÚDO PRINCIPAL (ABAS DE ANÁLISE)
    # ============================================================================
    tab1, tab2, tab3 = st.tabs(["Visão Geral", "Fatores de Risco", "Explorador Avançado"])

    # --- ABA 1: VISÃO GERAL DEMOGRÁFICA ---
    with tab1:
        st.header("1. Panorama Demográfico e Físico")
        
        # Gráfico de Pizza: Distribuição Total
        st.subheader("A. Distribuição Total de Pacientes")
        fig_pie = px.pie(
            df_filtered, 
            names='Nível de Obesidade', 
            color='Nível de Obesidade',
            category_orders={'Nível de Obesidade': ordem_obesidade},
            color_discrete_map=mapa_cores_obesidade,
            hole=0.4 # Estilo Rosca (Donut)
        )
        # Formatação para legibilidade (Negrito, Borda)
        fig_pie.update_traces(
            textposition='inside', textinfo='percent', 
            textfont=dict(size=16, color='white'), 
            insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>Nível de Obesidade:</b> %{label}<br>Percentual: %{percent}<extra></extra>'
        )
        fig_pie.update_traces(marker=dict(line=dict(color='#000000', width=1)))
        fig_pie.update_layout(
            legend_title_text='Classificação',
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("###") 

        # Histograma: Gênero
        st.subheader("B. Distribuição por Gênero")
        fig_gender = px.histogram(
            df_filtered, x='Nível de Obesidade', color='Gênero', 
            barmode='group', text_auto=True,
            category_orders={'Nível de Obesidade': ordem_obesidade},
            color_discrete_map={'Masculino': '#3366CC', 'Feminino': '#FF9900'},
            labels={'Nível de Obesidade': 'Nível de Obesidade', 'Gênero': 'Gênero'}
        )
        fig_gender.update_traces(
            textfont=dict(size=14, color='white'), textposition='inside', insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>Gênero:</b> %{data.name}<br><b>Nível:</b> %{x}<br><b>Qtd:</b> %{y}<extra></extra>'
        )
        fig_gender.update_layout(
            legend_title_text='Gênero',
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01),
            xaxis_title=None, yaxis_title="Quantidade de Pacientes", bargap=0.15
        )
        st.plotly_chart(fig_gender, use_container_width=True)

        st.markdown("###")
        
        # --- C. DISTRIBUIÇÃO POR IDADE ---
        st.subheader("C. Distribuição por Faixa Etária")
        st.caption("Como os níveis de obesidade estão distribuídos nas diferentes idades.")
        
        fig_age = px.histogram(
            df_filtered, 
            x='Idade', 
            color='Nível de Obesidade', 
            nbins=20, 
            barmode='group', 
            category_orders={'Nível de Obesidade': ordem_obesidade},
            color_discrete_map=mapa_cores_obesidade,
            labels={'Idade': 'Idade (Anos)', 'count': 'Contagem'}
        )
        
        fig_age.update_traces(
            textfont=dict(size=12, color='white'),
            textposition='inside',
            insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>Idade:</b> %{x}<br><b>Nível:</b> %{data.name}<br><b>Qtd:</b> %{y}<extra></extra>'
        )
        
        fig_age.update_layout(
            legend_title_text='Classificação',
            yaxis_title="Quantidade de Pacientes",
            bargap=0.1
        )
        
        st.plotly_chart(fig_age, use_container_width=True)

        st.markdown("###")

        # --- D. HISTÓRICO FAMILIAR ---
        # Agora ocupando a largura total (sem colunas)
        st.subheader("D. Impacto do Histórico Familiar")
        st.caption("Relação entre ter parentes obesos e o nível de obesidade atual.")
        
        fig_family = px.histogram(
            df_filtered, 
            x='Histórico Familiar', 
            color='Nível de Obesidade', 
            barmode='group',
            text_auto=True,
            category_orders={'Nível de Obesidade': ordem_obesidade},
            color_discrete_map=mapa_cores_obesidade
        )
        
        fig_family.update_traces(
            textfont=dict(size=14, color='white'),
            textposition='inside',
            insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>Histórico:</b> %{x}<br><b>Nível:</b> %{data.name}<br><b>Qtd:</b> %{y}<extra></extra>'
        )
        
        fig_family.update_layout(
            yaxis_title="Quantidade",
            xaxis_title="Possui Histórico Familiar?",
            legend_title_text='Classificação',
            # Ajuste da legenda para não comer espaço lateral
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01)
        )
        
        st.plotly_chart(fig_family, use_container_width=True)

        st.markdown("###")

        # --- E. DISPERSÃO PESO X ALTURA ---
        # Agora ocupando a largura total (sem colunas)
        st.subheader("E. Relação Peso x Altura")
        st.caption("Visualização dos clusters (IMC).")
        
        fig_scatter = px.scatter(
            df_filtered, 
            x='Altura', 
            y='Peso', 
            color='Nível de Obesidade',
            hover_data=['Gênero'],
            category_orders={'Nível de Obesidade': ordem_obesidade},
            color_discrete_map=mapa_cores_obesidade,
            height=600 # Aumentei um pouco a altura para aproveitar o espaço vertical
        )
        
        fig_scatter.update_traces(
            hovertemplate='<b>Peso:</b> %{y}kg<br><b>Altura:</b> %{x:.2f}m<br><b>Nível:</b> %{data.name}<extra></extra>'
        )
        
        fig_scatter.update_layout(
            xaxis_title="Altura (m)",
            yaxis_title="Peso (kg)",
            legend_title_text='Classificação'
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- ABA 2: ANÁLISE DE COMPORTAMENTO E RISCO ---
    with tab2:
        st.header("2. Análise de Comportamento e Risco")
        
        # Barras Empilhadas 100%
        st.subheader("A. Probabilidade por Fator de Risco")
        fator_risco = st.selectbox(
            "Selecione o Fator para analisar:",
            ["Histórico Familiar", "Consumo Calórico", "Monitora Calorias", "Fumante", "Atividade Física", "Consumo de Água"]
        )
        coluna_fator = fator_risco

        fig_bar_stack = px.histogram(
            df_filtered, x=coluna_fator, color='Nível de Obesidade', 
            barnorm='percent', # Normaliza para 100% para comparar proporções
            category_orders={'Nível de Obesidade': ordem_obesidade},
            color_discrete_map=mapa_cores_obesidade,
            height=500
        )
        fig_bar_stack.update_traces(
            texttemplate='<b>%{y:.0f}%</b>', textposition='inside',
            textfont=dict(size=14, color='white'), insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>%{x}</b><br><b>Nível:</b> %{data.name}<br><b>Percentual:</b> %{y:.1f}%<extra></extra>'
        )
        fig_bar_stack.update_layout(
            yaxis_title="Porcentagem (%)", xaxis_title=coluna_fator,
            legend_title_text='Classificação', legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01)
        )
        st.plotly_chart(fig_bar_stack, use_container_width=True)
        st.markdown("###")
        
        # Gráfico de Violino: Distribuição de Vegetais
        st.subheader("B. Consumo de Vegetais (Gráfico de Violino)")
        st.caption("A largura do 'violino' indica onde há mais pacientes concentrados.")
        fig_violin = px.violin(
            df_filtered, x='Nível de Obesidade', y='Consumo de Vegetais', color='Nível de Obesidade',
            category_orders={'Nível de Obesidade': ordem_obesidade},
            color_discrete_map=mapa_cores_obesidade
        )
        fig_violin.update_layout(showlegend=False, yaxis_title="Frequência de Consumo", xaxis_title=None)
        st.plotly_chart(fig_violin, use_container_width=True)
        st.markdown("###")

        # Distribuição de Atividade Física (Barras Empilhadas por Categoria)
        st.subheader("C. Distribuição de Atividade Física por Nível")
        st.caption("Como a frequência de atividade varia dentro de cada grupo de peso.")
        
        ordem_atividade = ["Nenhuma", "1 a 2 dias/sem", "3 a 4 dias/sem", "5 ou mais dias/sem"]
        mapa_cores_atividade = {
            "Nenhuma": "#d9534f", "1 a 2 dias/sem": "#f0ad4e", 
            "3 a 4 dias/sem": "#5cb85c", "5 ou mais dias/sem": "#2e7d32"
        }

        fig_stack_faf = px.histogram(
            df_filtered, x='Nível de Obesidade', color='Atividade Física', 
            barnorm='percent', text_auto='.0f',
            category_orders={'Nível de Obesidade': ordem_obesidade, 'Atividade Física': ordem_atividade},
            color_discrete_map=mapa_cores_atividade
        )
        fig_stack_faf.update_traces(
            texttemplate='<b>%{y:.0f}%</b>', textposition='inside',
            textfont=dict(size=14, color='white'), insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>%{x}</b><br>Atividade: %{data.name}<br>Representa: <b>%{y:.1f}%</b> do grupo<extra></extra>'
        )
        fig_stack_faf.update_layout(
            yaxis_title="Proporção (%)", xaxis_title=None,
            legend_title_text="Frequência", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_stack_faf, use_container_width=True)
        st.markdown("###")

        # Heatmap Comportamental (Mapa de Calor)
        st.subheader("D. Mapa de Calor Comportamental (Heatmap)")
        st.caption("Intensidade média dos comportamentos (0% a 100%). Cores mais escuras indicam maior frequência/adesão.")

        comport_cols_map = {
            "Consumo Calórico": "Consumo Calórico", "Consumo de Vegetais": "Consumo de Vegetais",
            "Refeições por Dia": "Refeições por Dia", "Comer entre Refeições": "Comer entre Refeições",
            "Consumo de Água": "Consumo de Água", "Atividade Física": "Atividade Física",
            "Tempo em Tecnologia": "Tempo em Tecnologia", "Consumo de Álcool": "Consumo de Álcool",
            "Monitora Calorias": "Monitora Calorias"
        }
        
        # Valores máximos para normalização (Transformar escalas diferentes em %)
        limites_maximos = {
            "Consumo Calórico": 1, "Monitora Calorias": 1, "Consumo de Vegetais": 3,
            "Refeições por Dia": 4, "Comer entre Refeições": 3, "Consumo de Água": 3,
            "Atividade Física": 3, "Tempo em Tecnologia": 2, "Consumo de Álcool": 3
        }

        df_heatmap = df_filtered.copy()
        
        # Mapeamento reverso para cálculo numérico
        mapa_numerico = {
            "Não": 0, "Sim": 1, "no": 0, "yes": 1,
            "Nunca": 0, "Às vezes": 1, "Frequentemente": 2, "Sempre": 3, "Always": 3,
            "Menos de 1L": 1, "Entre 1L e 2L": 2, "Mais de 2L": 3,
            "Nenhuma": 0, "1 a 2 dias/sem": 1, "3 a 4 dias/sem": 2, "5 ou mais dias/sem": 3,
            "0 a 2 horas": 0, "3 a 5 horas": 1, "Mais de 5 horas": 2,
            "Sometimes": 1, "Frequently": 2
        }
        df_heatmap.replace(mapa_numerico, inplace=True)

        cols_validas = [c for c in comport_cols_map.values() if pd.api.types.is_numeric_dtype(df_heatmap[c])]
        
        if cols_validas:
            # Normalização (Divisão pelo máximo)
            for col in cols_validas:
                max_val = limites_maximos.get(col, 1)
                df_heatmap[col] = (df_heatmap[col] / max_val)

            df_heatmap_grouped = df_heatmap.groupby("Nível de Obesidade")[cols_validas].mean()
            
            # Reordenar linhas do heatmap pela gravidade da obesidade
            ordem_existente = [o for o in ordem_obesidade if o in df_heatmap_grouped.index]
            df_heatmap_grouped = df_heatmap_grouped.reindex(ordem_existente)

            fig_heatmap = px.imshow(
                df_heatmap_grouped,
                labels=dict(x="Comportamento", y="Classificação", color="Intensidade"),
                x=cols_validas, y=df_heatmap_grouped.index,
                text_auto='.0%', aspect="auto", color_continuous_scale="Blues"
            )
            fig_heatmap.update_traces(
                textfont=dict(size=14),
                hovertemplate='<b>%{y}</b><br>Comportamento: %{x}<br>Intensidade Média: <b>%{z:.0%}</b><br><i>(Relativo ao máximo da escala)</i><extra></extra>'
            )
            fig_heatmap.update_layout(
                height=500, xaxis_title=None, yaxis_title=None, xaxis=dict(tickangle=-45),
                coloraxis_colorbar=dict(tickformat='.0%')
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.warning("Dados insuficientes para gerar o mapa de calor.")

        st.markdown("###")

        # Gráfico de Importância das Variáveis (Feature Importance)
        st.markdown("### E. Importância das Variáveis no Modelo Preditivo")
        st.caption("Quais variáveis tiveram maior peso na decisão do algoritmo (Random Forest).")

        try:
            model = joblib.load("saved_model/modelo_obesidade.joblib")
            rf = model.named_steps["classifier"]
            importances = rf.feature_importances_
            preprocessor = model.named_steps["preprocessor"]
            feature_names = []

            # Extração dos nomes das features do Pipeline (Scikit-Learn)
            if hasattr(preprocessor, 'transformers_'):
                num_features = preprocessor.transformers_[0][2]
                feature_names.extend(num_features)
                if hasattr(preprocessor.transformers_[1][1], 'named_steps'):
                    ohe = preprocessor.transformers_[1][1].named_steps["onehot"]
                    ohe_features = ohe.get_feature_names_out(preprocessor.transformers_[1][2])
                    feature_names.extend(ohe_features)
                ordinal_features = preprocessor.transformers_[2][2]
                feature_names.extend(ordinal_features)

            if len(feature_names) == len(importances):
                df_imp = pd.DataFrame({"Feature_Raw": feature_names, "Importância": importances})

                # Limpeza dos nomes técnicos para exibição
                def traduzir_nome_feature(nome_raw):
                    if "__" in nome_raw: nome_limpo = nome_raw.split("__")[-1]
                    else: nome_limpo = nome_raw
                    
                    if nome_limpo in dict_colunas: return dict_colunas[nome_limpo]
                    
                    for col_eng, col_pt in dict_colunas.items():
                        if nome_limpo.startswith(col_eng):
                            valor_eng = nome_limpo.replace(col_eng + "_", "")
                            valor_pt = dict_geral.get(valor_eng, valor_eng)
                            return f"{col_pt}: {valor_pt}"
                    return nome_limpo

                df_imp['Feature'] = df_imp['Feature_Raw'].apply(traduzir_nome_feature)
                df_imp = df_imp.sort_values("Importância", ascending=False)

                fig_imp = px.bar(
                    df_imp, x="Importância", y="Feature", orientation="h", 
                    color="Importância", color_continuous_scale="Viridis"
                )
                fig_imp.update_traces(
                    texttemplate='<b>%{x:.1%}</b>', textposition='inside',
                    textfont=dict(size=12, color='white'), insidetextfont=dict(family="Arial Black"),
                    hovertemplate='<b>%{y}</b><br>Impacto: %{x:.2%}<extra></extra>'
                )
                fig_imp.update_layout(
                    height=700, xaxis_title="Grau de Importância (%)", yaxis_title=None,
                    showlegend=False, coloraxis_showscale=False, xaxis=dict(tickformat=".0%")
                )
                st.plotly_chart(fig_imp, use_container_width=True)
            else:
                 st.warning("Divergência na contagem de features vs importâncias.")
        except Exception as e:
            st.warning(f"Aviso: Não foi possível carregar detalhes do modelo. Erro: {e}")

    # --- ABA 3: EXPLORADOR AVANÇADO ---
    with tab3:
        # Matriz de Correlação
        st.markdown("### Heatmap de Correlação")
        st.caption("Correlação linear. Foco: Veja a linha/coluna 'Nível de Obesidade' para entender o que sobe ou desce junto com o peso.")

        df_corr = df_filtered.copy()
        
        # Mapeamento ordinal da obesidade (para ver correlação linear correta)
        mapa_obesidade_num = {
            'Abaixo do Peso': 0, 'Peso Normal': 1, 'Sobrepeso Nível I': 2,
            'Sobrepeso Nível II': 3, 'Obesidade Tipo I': 4, 'Obesidade Tipo II': 5, 'Obesidade Tipo III': 6
        }
        mapa_conversao_corr = {
            "Não": 0, "Sim": 1, "Masculino": 0, "Feminino": 1,
            "Nunca": 0, "Às vezes": 1, "Frequentemente": 2, "Sempre": 3,
            "Menos de 1L": 1, "Entre 1L e 2L": 2, "Mais de 2L": 3,
            "Nenhuma": 0, "1 a 2 dias/sem": 1, "3 a 4 dias/sem": 2, "5 ou mais dias/sem": 3,
            "0 a 2 horas": 0, "3 a 5 horas": 1, "Mais de 5 horas": 2,
            "Transporte Público": 0, "Caminhada": 1, "Carro": 2, "Moto": 3, "Bicicleta": 4
        }
        
        df_corr['Nível de Obesidade'] = df_corr['Nível de Obesidade'].replace(mapa_obesidade_num)
        df_corr.replace(mapa_conversao_corr, inplace=True)

        df_num = df_corr.select_dtypes(include=['int64', 'float64', 'int32'])

        if df_num.shape[1] >= 2:
            corr_matrix = df_num.corr()
            # Ordena pela correlação com a Obesidade
            if 'Nível de Obesidade' in corr_matrix.columns:
                cols_ordenadas = corr_matrix.sort_values('Nível de Obesidade', ascending=False).index
                corr_matrix = corr_matrix[cols_ordenadas].reindex(cols_ordenadas)

            fig_corr = px.imshow(
                corr_matrix, text_auto='.2f', aspect="auto", 
                color_continuous_scale="RdBu_r", zmin=-1, zmax=1
            )
            fig_corr.update_traces(
                texttemplate='<b>%{z:.2f}</b>', textfont=dict(size=12),
                hovertemplate='<b>Var 1:</b> %{x}<br><b>Var 2:</b> %{y}<br><b>Correlação:</b> %{z:.2f}<extra></extra>'
            )
            fig_corr.update_layout(
                height=700, title_text="", margin=dict(t=30),
                xaxis_title=None, yaxis_title=None, coloraxis_colorbar=dict(title="Grau")
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Dados numéricos insuficientes para correlação.")

        st.markdown("###")

        # Seção Interativa (Self-Service BI)
        st.markdown("### Crie sua própria análise")
        st.caption("Escolha as variáveis para os eixos X e Y. Use a **Segmentação** para separar os dados em grupos (cores).")

        colunas_disponiveis = df_filtered.columns.tolist()
        
        c1, c2, c3 = st.columns(3)
        with c1: eixo_x = st.selectbox("Eixo X", colunas_disponiveis, index=0)
        with c2: eixo_y = st.selectbox("Eixo Y", colunas_disponiveis, index=1)
        with c3: cor_legenda = st.selectbox("Segmentação", colunas_disponiveis, index=colunas_disponiveis.index('Nível de Obesidade') if 'Nível de Obesidade' in colunas_disponiveis else 0)
        
        tipo_grafico = st.radio("Tipo de Gráfico", ["Dispersão", "Histograma", "Box Plot", "Violino"], horizontal=True)

        mapa_cores_dinamico = mapa_cores_obesidade if cor_legenda == 'Nível de Obesidade' else None

        try:
            fig_custom = None
            # Geração dinâmica do gráfico escolhido
            if tipo_grafico == "Dispersão": 
                fig_custom = px.scatter(
                    df_filtered, x=eixo_x, y=eixo_y, color=cor_legenda,
                    title=f"{eixo_y} por {eixo_x}",
                    color_discrete_map=mapa_cores_dinamico,
                    category_orders={'Nível de Obesidade': ordem_obesidade}
                )
                fig_custom.update_traces(hovertemplate='<b>%{x}</b><br>%{y}<extra></extra>')

            elif tipo_grafico == "Histograma": 
                fig_custom = px.histogram(
                    df_filtered, x=eixo_x, color=cor_legenda, barmode='group', text_auto=True,
                    title=f"Distribuição de {eixo_x}",
                    color_discrete_map=mapa_cores_dinamico,
                    category_orders={'Nível de Obesidade': ordem_obesidade}
                )
                fig_custom.update_traces(
                    textfont=dict(size=12, color='white'), textposition='inside',
                    insidetextfont=dict(family="Arial Black"),
                    hovertemplate='<b>%{x}</b><br>Contagem: %{y}<extra></extra>'
                )

            elif tipo_grafico == "Box Plot": 
                fig_custom = px.box(
                    df_filtered, x=eixo_x, y=eixo_y, color=cor_legenda,
                    title=f"Box Plot: {eixo_y} por {eixo_x}",
                    color_discrete_map=mapa_cores_dinamico,
                    category_orders={'Nível de Obesidade': ordem_obesidade}
                )

            elif tipo_grafico == "Violino": 
                fig_custom = px.violin(
                    df_filtered, x=eixo_x, y=eixo_y, color=cor_legenda, box=True, points=False,
                    title=f"Violino: {eixo_y} por {eixo_x}",
                    color_discrete_map=mapa_cores_dinamico,
                    category_orders={'Nível de Obesidade': ordem_obesidade}
                )

            if fig_custom:
                fig_custom.update_layout(height=500, title_text="", legend_title_text=cor_legenda, margin=dict(t=20))
                st.plotly_chart(fig_custom, use_container_width=True)

        except Exception as e:
            st.error(f"Não foi possível gerar o gráfico com essa combinação. (Erro: {e})")
        
        # ============================================================================
        # 6. EXPORTAÇÃO DE DADOS
        # ============================================================================
        st.markdown("---")
        with st.expander("Ver e Baixar Dados Brutos"):
            st.dataframe(df_filtered)
            col_csv, col_xlsx = st.columns(2)
            
            # Botão CSV
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            col_csv.download_button(
                label="Baixar CSV", data=csv, file_name="dados_filtrados.csv", mime="text/csv", type="primary"
            )
            
            # Botão Excel (usa buffer em memória)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_filtered.to_excel(writer, index=False, sheet_name='Dados')
                # Ajuste de largura das colunas
                worksheet = writer.sheets['Dados']
                for i, col in enumerate(df_filtered.columns):
                    worksheet.set_column(i, i, 20)
            
            col_xlsx.download_button(
                label="Baixar Excel (XLSX)", data=buffer, file_name="dados_filtrados.xlsx", mime="application/vnd.ms-excel"
            )

else:
    st.warning("Aguardando carregamento dos dados...")