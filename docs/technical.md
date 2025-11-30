# 🛠️ Detalhes Técnicos e Arquitetura

Documentação voltada para desenvolvedores que desejam manter ou expandir o HealthAnalytics.

## Estrutura de Arquivos

O projeto segue o padrão multipage do Streamlit.

```text
Obesity/
│
├── .streamlit/                 # Configuração de tema
├── assets/                     # Imagens, logos e prints
├── data/                       # Base de dados (obesity.csv)
├── docs/                       # (Novo) Pasta com os arquivos .md da documentação
│   ├── index.md
│   ├── modeling.md
│   ├── installation.md
│   ├── user_guide.md
│   └── technical.md
├── notebooks/                  # Estudos e treinamento (Jupyter)
├── pages/                      # Páginas da Aplicação
│   ├── 1_Diagnostico_Preditivo.py
│   ├── 2_Dashboard_Analitico.py
│   └── 3_Performance_do_Modelo.py
├── saved_model/                # Modelo treinado (.joblib)
├── .dockerignore               # Arquivos ignorados pelo Docker
├── .gitignore                  # Arquivos ignorados pelo Git
├── constants.py                # Dicionários e configurações globais
├── Dockerfile                  # Receita para construção do container
├── HealthAnalytics.py          # Entrypoint (Home)
├── mkdocs.yml                  # (Novo) Arquivo de configuração do site de doc
├── README.md                   # Documentação (pode adicionar link para o site agora)
├── requirements.txt            # (Atualizar) Adicionar dependências do MkDocs
└── utils.py                    # Funções auxiliares (Menu Lateral)
```

## Stack Tecnológico

- Frontend: Streamlit (Python puro). Escolhido pela rapidez de desenvolvimento e suporte nativo a dados.
- Backend/ML: Scikit-Learn 1.5+.
- Visualização: Plotly (Gráficos interativos) e Matplotlib/SHAP (Gráficos estáticos de explicabilidade).
- Containerização: Docker (Alpine Linux base para Python).

## Pipeline de Dados

O arquivo `modelo_obesidade.joblib` contém um Pipeline completo que executa:

1. OneHotEncoder: Para variáveis categóricas (ex: Gênero, Transporte).
2. OrdinalEncoder: Para variáveis com hierarquia (ex: "Nunca" < "Às vezes" < "Sempre").
3. Scaler: Normalização de dados numéricos.
4. Estimator: O classificador Random Forest.

!!! failure "Ponto de Atenção"
    Ao alterar o `HealthAnalytics.py` ou criar novas páginas, lembre-se de importar `sidebar_navegacao` de `utils.py` para manter o menu consistente em todas as telas.