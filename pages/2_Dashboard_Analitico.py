import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import io
import os
from utils import sidebar_navegacao
from constants import (
    DICT_FCVC_TEXT, DICT_CH2O_TEXT, DICT_FAF_TEXT, DICT_TUE_TEXT,
    DICT_TRADUCAO_GERAL, DICT_COLUNAS_PT, CORES_OBESIDADE, ORDEM_OBESIDADE
)

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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'obesity.csv')
    
    try:
        df = pd.read_csv(file_path)
        if 'NObeyesdad' in df.columns:
            df.rename(columns={'NObeyesdad': 'Obesity'}, inplace=True)
        elif 'Obesity' in df.columns:
            df.rename(columns={'Obesity': 'Obesity'}, inplace=True)
        return df
    except Exception as e:
        st.error(f"Erro crítico ao carregar dados em '{file_path}': {e}")
        return None

df_raw = load_data()

# --- APLICAÇÃO DAS TRANSFORMAÇÕES ---
if df_raw is not None:
    df = df_raw.copy()
    
    cols_to_round = ['FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']
    
    if 'NCP' in df.columns:
        df['NCP'] = pd.to_numeric(df['NCP'], errors='coerce').fillna(1).round().astype(int)

    for col in cols_to_round:
        if col in df.columns and col != 'NCP':
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).round().astype(int)

    if 'FCVC' in df.columns: df['FCVC'] = df['FCVC'].replace(DICT_FCVC_TEXT)
    if 'CH2O' in df.columns: df['CH2O'] = df['CH2O'].replace(DICT_CH2O_TEXT)
    if 'FAF' in df.columns:  df['FAF']  = df['FAF'].replace(DICT_FAF_TEXT)
    if 'TUE' in df.columns:  df['TUE']  = df['TUE'].replace(DICT_TUE_TEXT)

    df.replace(DICT_TRADUCAO_GERAL, inplace=True)
    df.rename(columns=DICT_COLUNAS_PT, inplace=True)
    
    # ============================================================================
    # 3. BARRA LATERAL DE FILTROS
    # ============================================================================
    st.sidebar.header("Filtros Avançados")
    st.sidebar.markdown("Use os grupos abaixo para filtrar a base de dados.")

    with st.sidebar.expander("Dados Pessoais e Físicos", expanded=True):
        obesidade_filtro = st.multiselect("Nível de Obesidade", options=df['Nível de Obesidade'].unique(), default=df['Nível de Obesidade'].unique())
        genero_filtro = st.multiselect("Gênero", options=df['Gênero'].unique(), default=df['Gênero'].unique())
        
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

    with st.sidebar.expander("Hábitos Alimentares", expanded=False):
        favc_filtro = st.multiselect("Alimentos Calóricos", options=df['Consumo Calórico'].unique(), default=df['Consumo Calórico'].unique())
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

    with st.sidebar.expander("Estilo de Vida", expanded=False):
        smoke_filtro = st.multiselect("Fumante", options=df['Fumante'].unique(), default=df['Fumante'].unique())
        faf_order = ["Nenhuma", "1 a 2 dias/sem", "3 a 4 dias/sem", "5 ou mais dias/sem"]
        faf_options = [x for x in faf_order if x in df['Atividade Física'].unique()]
        faf_filtro = st.multiselect("Atividade Física", options=faf_options, default=faf_options)
        tue_order = ["0 a 2 horas", "3 a 5 horas", "Mais de 5 horas"]
        tue_options = [x for x in tue_order if x in df['Tempo em Tecnologia'].unique()]
        tue_filtro = st.multiselect("Tempo em Tecnologia", options=tue_options, default=tue_options)
        transp_filtro = st.multiselect("Transporte", options=df['Transporte'].unique(), default=df['Transporte'].unique())

    filtros_query = []
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

    query_final = " & ".join(filtros_query)
    df_filtered = df.query(query_final)

    st.markdown("### Resumo da Seleção")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    if len(df_filtered) > 0:
        total_pacientes = len(df_filtered)
        media_idade = int(df_filtered['Idade'].mean())
        qtd_obesos = len(df_filtered[df_filtered['Nível de Obesidade'].astype(str).str.contains("Obesidade")])
        perc_obesidade = (qtd_obesos / total_pacientes * 100)
        media_peso = df_filtered['Peso'].mean()

        kpi1.metric("Pacientes Analisados", f"{total_pacientes}", border=True)
        kpi2.metric("Média de Idade", f"{media_idade:} anos", border=True)
        kpi3.metric("Taxa de Obesidade", f"{perc_obesidade:.1f}%", border=True)
        kpi4.metric("Peso Médio", f"{media_peso:.1f} kg", border=True)
    else:
        kpi1.metric("Pacientes Analisados", "0", border=True)
        kpi2.metric("Média de Idade", "0 anos", border=True)
        kpi3.metric("Taxa de Obesidade", "0.0%", border=True)
        kpi4.metric("Peso Médio", "0.0 kg", border=True)
        st.warning("Nenhum paciente encontrado. Ajuste os filtros.")
    
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Visão Geral", "Fatores de Risco", "Explorador Avançado"])

    # --- ABA 1: VISÃO GERAL ---
    with tab1:
        st.header("1. Panorama Demográfico e Físico")
        
        st.subheader("A. Distribuição Total de Pacientes")
        st.caption("Visão geral da proporção de cada nível de obesidade no grupo selecionado.")
        fig_pie = px.pie(
            df_filtered, 
            names='Nível de Obesidade', 
            color='Nível de Obesidade',
            category_orders={'Nível de Obesidade': ORDEM_OBESIDADE},
            color_discrete_map=CORES_OBESIDADE,
            hole=0.4
        )
        fig_pie.update_traces(
            textposition='inside', textinfo='percent', 
            textfont=dict(size=16, color='white'), 
            insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>Nível:</b> %{label}<br>Percentual: %{percent}<extra></extra>'
        )
        fig_pie.update_traces(marker=dict(line=dict(color='#000000', width=1)))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("###") 

        st.subheader("B. Distribuição por Gênero")
        st.caption("Compara a quantidade de homens e mulheres em cada categoria de peso.") 
        fig_gender = px.histogram(
            df_filtered, x='Nível de Obesidade', color='Gênero', 
            barmode='group', text_auto=True,
            category_orders={'Nível de Obesidade': ORDEM_OBESIDADE},
            color_discrete_map={'Masculino': '#3366CC', 'Feminino': '#FF9900'}
        )
        fig_gender.update_traces(
            textfont=dict(size=14, color='white'), 
            textposition='inside', 
            insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>Classificação:</b> %{x}<br><b>Gênero:</b> %{data.name}<br><b>Quantidade:</b> %{y}<extra></extra>'
        )
        fig_gender.update_layout(xaxis_title=None, yaxis_title="Quantidade", bargap=0.15)
        st.plotly_chart(fig_gender, use_container_width=True)

        st.markdown("###")
        
        st.subheader("C. Distribuição por Faixa Etária")
        st.caption("Mostra como os níveis de obesidade estão espalhados pelas idades.") 
        fig_age = px.histogram(
            df_filtered, x='Idade', color='Nível de Obesidade', nbins=20, barmode='group', 
            category_orders={'Nível de Obesidade': ORDEM_OBESIDADE},
            color_discrete_map=CORES_OBESIDADE
        )
        fig_age.update_traces(
            textfont=dict(size=12, color='white'), textposition='inside', insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>Idade:</b> %{x}<br><b>Nível:</b> %{data.name}<br><b>Quantidade:</b> %{y}<extra></extra>'
        )
        fig_age.update_layout(yaxis_title="Quantidade", legend_title_text='Classificação')
        st.plotly_chart(fig_age, use_container_width=True)

        st.markdown("###")

        st.subheader("D. Impacto do Histórico Familiar")
        st.caption("Analisa se ter parentes com obesidade influencia o nível de peso atual.") 
        fig_family = px.histogram(
            df_filtered, x='Histórico Familiar', color='Nível de Obesidade', barmode='group', text_auto=True,
            category_orders={'Nível de Obesidade': ORDEM_OBESIDADE},
            color_discrete_map=CORES_OBESIDADE
        )
        fig_family.update_traces(
            textfont=dict(size=14, color='white'), textposition='inside', insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>Histórico:</b> %{x}<br><b>Nível:</b> %{data.name}<br><b>Quantidade:</b> %{y}<extra></extra>'
        )
        fig_family.update_layout(yaxis_title="Quantidade", xaxis_title="Histórico Familiar")
        st.plotly_chart(fig_family, use_container_width=True)

        st.markdown("###")

        st.subheader("E. Relação Peso x Altura")
        st.caption("Visualização de dispersão. Cada ponto é uma pessoa. Note como as cores se agrupam (IMC).") 
        fig_scatter = px.scatter(
            df_filtered, x='Altura', y='Peso', color='Nível de Obesidade',
            hover_data=['Gênero'],
            category_orders={'Nível de Obesidade': ORDEM_OBESIDADE},
            color_discrete_map=CORES_OBESIDADE,
            height=600
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- ABA 2: COMPORTAMENTO ---
    with tab2:
        st.header("2. Análise de Comportamento e Risco")
        
        st.subheader("A. Probabilidade por Fator de Risco")
        fator_risco = st.selectbox(
            "Selecione o Fator para analisar:",
            ["Histórico Familiar", "Consumo Calórico", "Monitora Calorias", "Fumante", "Atividade Física", "Consumo de Água"]
        )
        st.caption(f"Mostra a proporção (%) de cada nível de obesidade dentro das categorias de '{fator_risco}'.") 
        fig_bar_stack = px.histogram(
            df_filtered, x=fator_risco, color='Nível de Obesidade', barnorm='percent',
            category_orders={'Nível de Obesidade': ORDEM_OBESIDADE},
            color_discrete_map=CORES_OBESIDADE, height=500
        )
        fig_bar_stack.update_traces(
            texttemplate='<b>%{y:.0f}%</b>', textposition='inside',
            textfont=dict(size=14, color='white'), insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>%{x}</b><br><b>Nível:</b> %{data.name}<br><b>Percentual:</b> %{y:.1f}%<extra></extra>'
        )
        fig_bar_stack.update_layout(yaxis_title="Percentual (%)", xaxis_title=fator_risco)
        st.plotly_chart(fig_bar_stack, use_container_width=True)
        st.markdown("###")
        
        st.subheader("B. Consumo de Vegetais (Violino)")
        st.caption("A largura do 'violino' mostra onde está a maioria das pessoas. Ajuda a ver a densidade.") 
        fig_violin = px.violin(
            df_filtered, x='Nível de Obesidade', y='Consumo de Vegetais', color='Nível de Obesidade',
            category_orders={'Nível de Obesidade': ORDEM_OBESIDADE},
            color_discrete_map=CORES_OBESIDADE
        )
        fig_violin.update_layout(yaxis_title="Frequência", xaxis_title=None)
        st.plotly_chart(fig_violin, use_container_width=True)
        st.markdown("###")

        st.subheader("C. Distribuição de Atividade Física por Nível")
        st.caption("Revela se pessoas com obesidade tendem a praticar menos exercícios que as demais.") 
        ordem_atividade = ["Nenhuma", "1 a 2 dias/sem", "3 a 4 dias/sem", "5 ou mais dias/sem"]
        mapa_cores_atividade = {
            "Nenhuma": "#d9534f", "1 a 2 dias/sem": "#f0ad4e", 
            "3 a 4 dias/sem": "#5cb85c", "5 ou mais dias/sem": "#2e7d32"
        }
        fig_stack_faf = px.histogram(
            df_filtered, x='Nível de Obesidade', color='Atividade Física', barnorm='percent', text_auto='.0f',
            category_orders={'Nível de Obesidade': ORDEM_OBESIDADE, 'Atividade Física': ordem_atividade},
            color_discrete_map=mapa_cores_atividade
        )
        fig_stack_faf.update_traces(
            texttemplate='<b>%{y:.0f}%</b>', textposition='inside',
            textfont=dict(size=14, color='white'), insidetextfont=dict(family="Arial Black"),
            hovertemplate='<b>%{x}</b><br>Atividade: %{data.name}<br>Percentual: <b>%{y:.1f}%</b><extra></extra>'
        )
        fig_stack_faf.update_layout(yaxis_title="Percentual (%)", xaxis_title=None, legend_title_text="Frequência")
        st.plotly_chart(fig_stack_faf, use_container_width=True)
        st.markdown("###")

        # Heatmap
        st.subheader("D. Mapa de Calor Comportamental (Heatmap)")
        st.caption("Cores mais escuras indicam maior intensidade naquele hábito. Ex: Azul escuro em 'Consumo Calórico' para Obesidade III indica alto consumo.") 
        comport_cols_map = {
            "Consumo Calórico": "Consumo Calórico", "Consumo de Vegetais": "Consumo de Vegetais",
            "Refeições por Dia": "Refeições por Dia", "Comer entre Refeições": "Comer entre Refeições",
            "Consumo de Água": "Consumo de Água", "Atividade Física": "Atividade Física",
            "Tempo em Tecnologia": "Tempo em Tecnologia", "Consumo de Álcool": "Consumo de Álcool",
            "Monitora Calorias": "Monitora Calorias"
        }
        limites_maximos = {
            "Consumo Calórico": 1, "Monitora Calorias": 1, "Consumo de Vegetais": 3,
            "Refeições por Dia": 4, "Comer entre Refeições": 3, "Consumo de Água": 3,
            "Atividade Física": 3, "Tempo em Tecnologia": 2, "Consumo de Álcool": 3
        }

        df_heatmap = df_filtered.copy()
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
            for col in cols_validas:
                max_val = limites_maximos.get(col, 1)
                df_heatmap[col] = (df_heatmap[col] / max_val)

            df_heatmap_grouped = df_heatmap.groupby("Nível de Obesidade")[cols_validas].mean()
            ordem_existente = [o for o in ORDEM_OBESIDADE if o in df_heatmap_grouped.index]
            df_heatmap_grouped = df_heatmap_grouped.reindex(ordem_existente)

            fig_heatmap = px.imshow(
                df_heatmap_grouped, labels=dict(x="Comportamento", y="Classificação", color="Intensidade"),
                text_auto='.0%', aspect="auto", color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

        st.markdown("###")

        # Feature Importance
        st.markdown("### E. Importância das Variáveis no Modelo Preditivo")
        st.caption("Quais perguntas tiveram mais peso matemático para o modelo aprender a classificar a obesidade.") 
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, 'saved_model', 'modelo_obesidade.joblib')
            
            model = joblib.load(model_path)
            rf = model.named_steps["classifier"]
            importances = rf.feature_importances_
            preprocessor = model.named_steps["preprocessor"]
            feature_names = []

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

                def traduzir_nome_feature(nome_raw):
                    nome_limpo = nome_raw.split("__")[-1] if "__" in nome_raw else nome_raw
                    
                    if nome_limpo in DICT_COLUNAS_PT:
                        return DICT_COLUNAS_PT[nome_limpo]
                    
                    for col_eng, col_pt in DICT_COLUNAS_PT.items():
                        if col_eng in nome_limpo:
                            sufixo = nome_limpo.replace(col_eng, "").replace("_", " ").strip()
                            if sufixo:
                                sufixo_trad = DICT_TRADUCAO_GERAL.get(sufixo.strip(), sufixo)
                                return f"{col_pt} ({sufixo_trad})"
                            return col_pt
                            
                    return nome_limpo

                df_imp['Feature'] = df_imp['Feature_Raw'].apply(traduzir_nome_feature)
                df_imp = df_imp.sort_values("Importância", ascending=False)

                fig_imp = px.bar(
                    df_imp, x="Importância", y="Feature", orientation="h", 
                    color="Importância", color_continuous_scale="Viridis"
                )
                fig_imp.update_traces(
                    texttemplate='<b>%{x:.1%}</b>', 
                    textposition='inside',
                    textfont=dict(size=12, color='white'),
                    insidetextfont=dict(family="Arial Black")
                )
                fig_imp.update_layout(
                    showlegend=False, 
                    yaxis_title="Variável", 
                    xaxis_title="Grau de Importância",
                    height=800,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig_imp, use_container_width=True)
        except Exception as e:
            st.warning(f"Aviso: Não foi possível carregar detalhes do modelo. Erro: {e}")

    # --- ABA 3: EXPLORADOR ---
    with tab3:
        st.markdown("### Heatmap de Correlação")
        st.caption("Mostra se duas variáveis crescem juntas (vermelho) ou se opõem (azul). Foco: Veja a linha 'Nível de Obesidade'.") 
        df_corr = df_filtered.copy()
        
        mapa_obesidade_num = {k: i for i, k in enumerate(ORDEM_OBESIDADE)}
        
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
            if 'Nível de Obesidade' in corr_matrix.columns:
                cols_ordenadas = corr_matrix.sort_values('Nível de Obesidade', ascending=False).index
                corr_matrix = corr_matrix[cols_ordenadas].reindex(cols_ordenadas)

            fig_corr = px.imshow(corr_matrix, text_auto='.2f', aspect="auto", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Dados numéricos insuficientes para correlação.")

        st.markdown("### Crie sua própria análise")
        colunas_disponiveis = df_filtered.columns.tolist()
        
        c1, c2, c3 = st.columns(3)
        with c1: eixo_x = st.selectbox("Eixo X", colunas_disponiveis, index=0)
        with c2: eixo_y = st.selectbox("Eixo Y", colunas_disponiveis, index=1)
        with c3: cor_legenda = st.selectbox("Segmentação", colunas_disponiveis, index=colunas_disponiveis.index('Nível de Obesidade') if 'Nível de Obesidade' in colunas_disponiveis else 0)
        
        tipo_grafico = st.radio("Tipo de Gráfico", ["Dispersão", "Histograma", "Box Plot", "Violino"], horizontal=True)
        mapa_cores_dinamico = CORES_OBESIDADE if cor_legenda == 'Nível de Obesidade' else None

        st.caption("Use os controles acima para cruzar variáveis livremente.") 

        try:
            fig_custom = None
            if tipo_grafico == "Dispersão": 
                fig_custom = px.scatter(
                    df_filtered, x=eixo_x, y=eixo_y, color=cor_legenda,
                    color_discrete_map=mapa_cores_dinamico,
                    category_orders={'Nível de Obesidade': ORDEM_OBESIDADE}
                )
            elif tipo_grafico == "Histograma": 
                fig_custom = px.histogram(
                    df_filtered, x=eixo_x, color=cor_legenda, barmode='group', text_auto=True,
                    color_discrete_map=mapa_cores_dinamico,
                    category_orders={'Nível de Obesidade': ORDEM_OBESIDADE}
                )
                fig_custom.update_traces(
                    textfont=dict(size=12, color='white'), 
                    textposition='inside', 
                    insidetextfont=dict(family="Arial Black")
                )
            elif tipo_grafico == "Box Plot": 
                fig_custom = px.box(
                    df_filtered, x=eixo_x, y=eixo_y, color=cor_legenda,
                    color_discrete_map=mapa_cores_dinamico,
                    category_orders={'Nível de Obesidade': ORDEM_OBESIDADE}
                )
            elif tipo_grafico == "Violino": 
                fig_custom = px.violin(
                    df_filtered, x=eixo_x, y=eixo_y, color=cor_legenda, box=True,
                    color_discrete_map=mapa_cores_dinamico,
                    category_orders={'Nível de Obesidade': ORDEM_OBESIDADE}
                )

            if fig_custom:
                fig_custom.update_layout(height=500, margin=dict(t=20))
                st.plotly_chart(fig_custom, use_container_width=True)
        except Exception as e:
            st.error(f"Não foi possível gerar o gráfico: {e}")

        # Exportação
        st.markdown("---")
        with st.expander("Ver e Baixar Dados Brutos"):
            st.dataframe(df_filtered)
            col_csv, col_xlsx = st.columns(2)
            
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            col_csv.download_button("Baixar CSV", data=csv, file_name="dados.csv", mime="text/csv", type="primary")
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_filtered.to_excel(writer, index=False)
            col_xlsx.download_button("Baixar Excel", data=buffer, file_name="dados.xlsx", mime="application/vnd.ms-excel")

else:
    st.warning("Aguardando carregamento dos dados...")