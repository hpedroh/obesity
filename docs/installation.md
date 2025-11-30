# ⚙️ Guia de Instalação e Execução

Você pode executar o HealthAnalytics de duas formas. Escolha a que melhor se adapta ao seu perfil técnico.

## Escolha seu método

=== "🐳 Via Docker (Recomendado)"

    Esta é a forma mais simples e garante que tudo funcione sem conflitos de versão, pois usamos um container isolado.

    **Pré-requisitos:** Ter o Docker Desktop instalado.

    1.  **Clone o projeto:**
        ```bash
        git clone [https://github.com/hpedroh/obesity.git](https://github.com/hpedroh/obesity.git)
        cd obesity
        ```

    2.  **Construa a imagem:**
        ```bash
        docker build -t health-analytics .
        ```

    3.  **Rode a aplicação:**
        ```bash
        docker run -d -p 8501:8501 --name health-app health-analytics
        ```

    ➡️ **Acesse:** Abra seu navegador em `http://localhost:8501`

=== "🐍 Instalação Local (Python)"

    Ideal se você deseja editar o código ou não tem Docker.

    **Pré-requisitos:** Python 3.11 ou superior.

    1.  **Clone e entre na pasta:**
        ```bash
        git clone [https://github.com/hpedroh/obesity.git](https://github.com/hpedroh/obesity.git)
        cd obesity
        ```

    2.  **Crie um ambiente virtual (Boas Práticas):**
        ```bash
        # Windows
        python -m venv venv
        venv\Scripts\activate
        
        # Linux/Mac
        python3 -m venv venv
        source venv/bin/activate
        ```

    3.  **Instale as dependências:**
        ```bash
        pip install -r requirements.txt
        ```

    4.  **Inicie o Streamlit:**
        ```bash
        streamlit run HealthAnalytics.py
        ```

---

## Solução de Problemas Comuns

| Erro | Solução Provável |
| :--- | :--- |
| `ModuleNotFoundError` | Você esqueceu de rodar o `pip install -r requirements.txt` ou não ativou a venv. |
| `Port 8501 already in use` | Outra aplicação Streamlit está rodando. Tente matar o processo ou rodar em outra porta. |
| `FileNotFoundError: modelo_obesidade.joblib` | Verifique se você está rodando o comando na raiz da pasta `Obesity/`. |