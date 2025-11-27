import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from utils import sidebar_navegacao

# ============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(page_title="Performance do Modelo", layout="wide")
sidebar_navegacao() # Menu Lateral

st.title("Performance e Validação do Modelo")
st.markdown("""
Esta página apresenta as métricas técnicas do modelo de **Random Forest** utilizado no sistema. 
Os dados apresentados referem-se ao **Conjunto de Teste (20% dos dados)**, que o modelo não viu durante o treinamento.
""")

# ============================================================================
# 2. CARREGAMENTO E PREPARAÇÃO (Idêntico ao Treino para garantir fidelidade)
# ============================================================================
@st.cache_data
def load_and_prep_data():
    try:
        try:
            df = pd.read_csv('data/obesity.csv')
        except:
            df = pd.read_csv('../data/obesity.csv')
            
        if 'NObeyesdad' in df.columns:
            df.rename(columns={'NObeyesdad': 'Obesity'}, inplace=True)
        elif 'Obesity' in df.columns:
            df.rename(columns={'Obesity': 'Obesity'}, inplace=True)
            
        # --- TRATAMENTO DE RUÍDO (CRÍTICO) ---
        # Réplica exata do passo de limpeza do notebook de treino
        cols_to_round = ['FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']
        for col in cols_to_round:
            if col in df.columns:
                df[col] = df[col].round().astype(int)
                
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# Carrega Modelo e Dados
pipeline = joblib.load('saved_model/modelo_obesidade.joblib')
df = load_and_prep_data()

if df is not None:
    # Divisão Treino/Teste (Recriando o cenário de validação)
    X = df.drop('Obesity', axis=1)
    y = df['Obesity']
    
    # IMPORTANTE: random_state=42 garante que o X_test seja IGUAL ao do notebook
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Gera Predições
    y_pred = pipeline.predict(X_test)
    
    # ============================================================================
    # 3. MÉTRICAS GERAIS (LINHA DE TOPO)
    # ============================================================================
    st.markdown("### Métricas Globais (Test Set)")
    c1, c2, c3, c4 = st.columns(4)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted')
    rec = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    c1.metric("Acurácia Global", f"{acc:.1%}", help="Porcentagem de acertos totais do modelo.")
    c2.metric("Precisão (Média)", f"{prec:.1%}", help="Quando o modelo diz que é X, o quanto ele acerta?")
    c3.metric("Recall (Sensibilidade)", f"{rec:.1%}", help="De todos os casos reais de X, quantos o modelo encontrou?")
    c4.metric("F1-Score", f"{f1:.1%}", help="Média harmônica entre Precisão e Recall. Bom para classes desbalanceadas.")
    
    st.markdown("---")

    # ============================================================================
    # 4. MATRIZ DE CONFUSÃO (VISUAL)
    # ============================================================================
    st.subheader("Matriz de Confusão")
    st.caption("Compare o **Valor Real** (Eixo Y) com o **Valor Predito** (Eixo X). A diagonal principal mostra os acertos.")
    
    # Gera a matriz
    labels_ordenadas = [
        'Insufficient_Weight', 'Normal_Weight', 
        'Overweight_Level_I', 'Overweight_Level_II',
        'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III'
    ]
    
    # Mapeia para nomes curtos (PT) para caber no gráfico
    dict_labels_curtos = {
        'Insufficient_Weight': 'Abaixo', 'Normal_Weight': 'Normal',
        'Overweight_Level_I': 'Sobrepeso I', 'Overweight_Level_II': 'Sobrepeso II',
        'Obesity_Type_I': 'Obes. I', 'Obesity_Type_II': 'Obes. II', 'Obesity_Type_III': 'Obes. III'
    }
    
    cm = confusion_matrix(y_test, y_pred, labels=labels_ordenadas)
    
    # Cria gráfico Heatmap
    fig_cm = px.imshow(
        cm,
        text_auto=True,
        aspect="auto",
        labels=dict(x="Predição do Modelo", y="Valor Real (Gabarito)", color="Quantidade"),
        x=[dict_labels_curtos[l] for l in labels_ordenadas],
        y=[dict_labels_curtos[l] for l in labels_ordenadas],
        color_continuous_scale="Blues"
    )
    fig_cm.update_layout(xaxis_title="O que o modelo disse", yaxis_title="O que é na realidade")
    st.plotly_chart(fig_cm, use_container_width=True)
    
    st.markdown("---")

    # ============================================================================
    # 5. RELATÓRIO DETALHADO POR CLASSE
    # ============================================================================
    st.subheader("Relatório Detalhado por Classe")
    
    # Gera o report em formato de dicionário para converter em DataFrame
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    df_report = pd.DataFrame(report_dict).transpose()
    
    # Filtra apenas as classes (remove linhas de média)
    df_report = df_report.loc[labels_ordenadas]
    
    # Traduz os índices
    df_report.index = df_report.index.map(dict_labels_curtos)
    
    # Formatação visual da tabela (Highlight nos melhores valores)
    st.dataframe(
        df_report.style.format("{:.1%}").background_gradient(cmap="Greens", subset=['precision', 'recall', 'f1-score']),
        use_container_width=True
    )
    
    st.info("**Nota:** O modelo apresenta excelente performance nas classes extremas (Abaixo do Peso e Obesidade III), com ligeira confusão entre os níveis de Sobrepeso, o que é esperado devido à proximidade dos limites de IMC.")

else:
    st.warning("Aguardando dados...")