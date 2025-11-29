import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from utils import sidebar_topo, sidebar_rodape

# ============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(page_title="Performance do Modelo", layout="wide")

# AJUSTE AQUI: Menu no topo
sidebar_topo()

st.title("Performance e Validação do Modelo")
st.markdown("""
Esta página apresenta as métricas técnicas do modelo de **Random Forest** utilizado no sistema. 
Os dados apresentados referem-se ao **Conjunto de Teste (20% dos dados)**, que o modelo não viu durante o treinamento.
""")

# ============================================================================
# 2. CARREGAMENTO E PREPARAÇÃO
# ============================================================================
@st.cache_data
def load_and_prep_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'obesity.csv')
    
    try:
        df = pd.read_csv(file_path)
            
        if 'NObeyesdad' in df.columns:
            df.rename(columns={'NObeyesdad': 'Obesity'}, inplace=True)
        elif 'Obesity' in df.columns:
            df.rename(columns={'Obesity': 'Obesity'}, inplace=True)
            
        cols_to_round = ['FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']
        for col in cols_to_round:
            if col in df.columns:
                df[col] = df[col].round().astype(int)
                
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

try:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, 'saved_model', 'modelo_obesidade.joblib')
    pipeline = joblib.load(model_path)
except:
    st.error("Erro ao carregar o modelo. Verifique o caminho 'saved_model/modelo_obesidade.joblib'")
    st.stop()

df = load_and_prep_data()

if df is not None:
    X = df.drop('Obesity', axis=1)
    y = df['Obesity']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    y_pred = pipeline.predict(X_test)
    
    # ============================================================================
    # 3. MÉTRICAS GERAIS (LINHA DE TOPO)
    # ============================================================================
    st.markdown("### Métricas Globais (Test Set)")
    st.caption("Visão geral do desempenho do modelo em dados desconhecidos.")
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
    st.caption("**Como ler:** O eixo Y mostra o que a pessoa *realmente* tem. O eixo X mostra o que o modelo *disse* que ela tinha. Quanto mais azul na diagonal principal, melhor (acertos).")
    
    labels_ordenadas = [
        'Insufficient_Weight', 'Normal_Weight', 
        'Overweight_Level_I', 'Overweight_Level_II',
        'Obesity_Type_I', 'Obesity_Type_II', 'Obesity_Type_III'
    ]
    
    dict_labels_curtos = {
        'Insufficient_Weight': 'Abaixo', 'Normal_Weight': 'Normal',
        'Overweight_Level_I': 'Sobrepeso I', 'Overweight_Level_II': 'Sobrepeso II',
        'Obesity_Type_I': 'Obes. I', 'Obesity_Type_II': 'Obes. II', 'Obesity_Type_III': 'Obes. III'
    }
    
    cm = confusion_matrix(y_test, y_pred, labels=labels_ordenadas)
    
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
    st.caption("**Precision:** Confiança do acerto. **Recall:** Capacidade de detecção. **Support:** Quantas pessoas desse tipo existiam no teste.")
    
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    df_report = pd.DataFrame(report_dict).transpose()
    
    df_report = df_report.loc[labels_ordenadas]
    
    df_report.index = df_report.index.map(dict_labels_curtos)
    
    st.dataframe(
        df_report.style
        .format("{:.1%}", subset=['precision', 'recall', 'f1-score'])
        .format("{:.0f}", subset=['support'])
        .background_gradient(cmap="Greens", subset=['precision', 'recall', 'f1-score']),
        use_container_width=True
    )
    
    st.info("**Nota:** O modelo apresenta excelente performance nas classes extremas (Abaixo do Peso e Obesidade III), com ligeira confusão entre os níveis de Sobrepeso, o que é esperado devido à proximidade dos limites de IMC.")

    sidebar_rodape()

else:
    st.warning("Aguardando dados...")