# 1. Imagem Base: Python 3.12 (igual ao seu ambiente)
FROM python:3.12-slim

# 2. Define diretório de trabalho
WORKDIR /app

# 3. Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Instalação de dependências do sistema
# CORREÇÃO: Removi 'software-properties-common' que estava dando erro
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Copia os requerimentos
COPY requirements.txt .

# 6. Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copia o código do projeto
COPY . .

# 8. Expõe a porta
EXPOSE 8501

# 9. Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 10. Comando de inicialização
ENTRYPOINT ["streamlit", "run", "HealthAnalytics.py", "--server.port=8501", "--server.address=0.0.0.0"]