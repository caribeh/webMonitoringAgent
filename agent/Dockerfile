# Usa uma imagem base oficial do Python
FROM python:3.9-slim

# Instala o pacote 'ping' que não vem na imagem 'slim'
# O '&& rm...' é uma boa prática para manter a imagem pequena
RUN apt-get update && apt-get install -y iputils-ping --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
# ---------------------------

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do agente para o diretório de trabalho
COPY agent.py .

# Comando para executar o agente quando o container iniciar
CMD ["python", "agent.py"]