# HealthAnalytics: Predição de Obesidade

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://obesity-risk-app.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red)
![Scikit-Learn](https://img.shields.io/badge/Model-RandomForest-green)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)

> **Tech Challenge - Fase 4 | Data Analytics**
> Sistema inteligente para apoio ao diagnóstico clínico e análise de saúde preventiva.

---

## Acesso à Aplicação
Acesse a aplicação online clicando no link abaixo:
### [**https://obesity-risk-app.streamlit.app/**](https://obesity-risk-app.streamlit.app/)

---

## Sobre o Projeto

Este projeto tem como objetivo auxiliar profissionais de saúde na **identificação precoce de riscos relacionados à obesidade**.

Utilizando um modelo de Machine Learning (**Random Forest Classifier**) treinado com dados clínicos e comportamentais, o sistema oferece:
1.  **Diagnóstico Preditivo:** Classificação do nível de obesidade e análise de probabilidade (risco) com base em inputs do usuário.
2.  **Dashboard Analítico:** Visualização de dados históricos para entender padrões de alimentação, atividade física e fatores genéticos na população.
3.  **Auditoria de Modelo:** Área técnica para validação das métricas de performance do algoritmo.

A aplicação foi desenvolvida em **Python** utilizando **Streamlit** para a interface web e **Plotly** para visualizações interativas.

---

## Funcionalidades

### 1. Diagnóstico Preditivo (IA)
* Formulário interativo para coleta de dados do paciente.
* **Análise de Risco:** Gráfico de probabilidades que mostra a chance de pertencimento a cada classe de obesidade.
* **Geração de Laudo (PDF):** Download de relatório clínico completo com anamnese, resultados e fatores de risco.
* **Interpretador:** Feedback automático dos fatores de risco e proteção identificados no perfil.

### 2. Dashboard Analítico (Business Intelligence)
* **Visão Geral:** Distribuição demográfica, relação Peso x Altura e impacto do histórico familiar.
* **Fatores de Risco:** Análise profunda de alimentação e sedentarismo.
* **Explorador Livre:** Ferramenta *Self-Service BI* para criação de gráficos dinâmicos.

### 3. Performance do Modelo (Técnico)
* Visualização da **Matriz de Confusão**.
* Relatório detalhado de métricas (Acurácia, Precision, Recall, F1-Score).
* Transparência sobre os dados de teste utilizados.

---

## Estrutura do Projeto

```text
Obesity/
│
├── .streamlit/                 # Configuração de tema (config.toml)
├── .venv/                      # Ambiente virtual
├── assets/                     # Imagens e logos
│   └── balanca.png
├── data/                       # Base de dados
│   └── obesity.csv             # Dataset original
├── notebooks/                  # Estudos e modelagem
│   └── 1_criando_modelo.ipynb  # EDA e Treinamento do Modelo
├── pages/                      # Páginas da Aplicação Streamlit
│   ├── 1_Diagnostico_Preditivo.py
│   ├── 2_Dashboard_Analitico.py
│   └── 3_Performance_do_Modelo.py
├── saved_model/                # Modelo serializado
│   └── modelo_obesidade.joblib # Pipeline completa
├── .gitignore                  # Arquivos ignorados pelo Git
├── HealthAnalytics.py          # Página Inicial (Entrypoint)
├── LICENSE                     # Licença MIT
├── README.md                   # Documentação
├── requirements.txt            # Dependências do projeto
└── utils.py                    # Funções auxiliares (Menu Lateral)

## Como Rodar Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/hpedroh/obesity.git
cd obesity
```

### 2. Crie um ambiente virtual (opcional, mas recomendado):

```Bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux: source venv/bin/activate  
```

### 3. Instale as dependências:

```Bash
pip install -r requirements.txt
```

### 4. Execute a aplicação:

```Bash
streamlit run HealthAnalytics.py
```

## Licença

Este projeto está sob a licença MIT. Sinta-se à vontade para contribuir ou utilizar para fins educacionais.

<div align="center"> Desenvolvido por <b>Pedro Henrique</b> </div>