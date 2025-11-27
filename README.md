# HealthAnalytics: Predição de Obesidade

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red)
![Scikit-Learn](https://img.shields.io/badge/Model-RandomForest-green)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)

> **Tech Challenge - Fase 4 | Data Analytics**
> Sistema inteligente para apoio ao diagnóstico clínico e análise de saúde preventiva.

---

## Sobre o Projeto

Este projeto tem como objetivo auxiliar profissionais de saúde na **identificação precoce de riscos relacionados à obesidade**.

Utilizando um modelo de Machine Learning (**Random Forest Classifier**) treinado com dados clínicos e comportamentais, o sistema oferece:
1.  **Diagnóstico Preditivo:** Classificação do nível de obesidade com base em inputs do usuário.
2.  **Dashboard Analítico:** Visualização de dados históricos para entender padrões de alimentação, atividade física e fatores genéticos na população.

A aplicação foi desenvolvida em **Python** utilizando **Streamlit** para a interface web e **Plotly** para visualizações interativas.

---

## Funcionalidades

### 1. Diagnóstico Preditivo (IA)
* Formulário interativo para coleta de dados do paciente (Idade, Peso, Hábitos, etc.).
* Pré-processamento automático dos dados (Pipeline com OneHotEncoder e StandardScaler).
* Classificação em 7 níveis: *Abaixo do Peso* até *Obesidade Tipo III*.
* Recomendações automáticas baseadas no resultado.

### 2. Dashboard Analítico (Business Intelligence)
* **Visão Geral:** Distribuição demográfica, relação Peso x Altura e impacto do histórico familiar.
* **Fatores de Risco:** Análise profunda de alimentação (Vegetais, Calorias, Água) e sedentarismo.
* **Explorador Livre:** Ferramenta *Self-Service BI* onde o usuário cria seus próprios gráficos (Scatter, Histograma, Box Plot, Violino) cruzando variáveis e segmentações dinâmicas.

---

## Estrutura do Projeto

```text
Obesity/
│
├── .venv/                      # Ambiente virtual
├── assets/                     # Imagens e logos
│   └── balanca.png
├── data/                       # Base de dados
│   └── obesity.csv             # Dataset original/processado
├── notebooks/                  # Estudos e modelagem
│   └── 1_criando_modelo.ipynb  # EDA e Treinamento do Modelo
├── pages/                      # Páginas da Aplicação Streamlit
│   ├── 1_Diagnostico_Preditivo.py
│   └── 2_Dashboard_Analitico.py
├── saved_model/                # Modelo serializado
│   └── modelo_obesidade.joblib # Pipeline completa (Pré-proc + Modelo)
├── .gitignore                  # Arquivos ignorados pelo Git
├── HealthAnalytics.py          # Página Inicial (Entrypoint)
├── README.md                   # Documentação
└── requirements.txt            # Dependências do projeto