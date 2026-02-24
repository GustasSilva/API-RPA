# Imagem base
FROM python:3.11-slim

# Diretório dentro do container
WORKDIR /app

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (melhora cache)
COPY app/requirements.txt ./requirements.txt

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar projeto
COPY app ./app

# Expor porta
EXPOSE 8000

# Comando para rodar API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]