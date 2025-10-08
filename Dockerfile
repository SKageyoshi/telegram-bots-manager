FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primeiro para cache
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app.py .

# Comando para rodar
CMD ["python", "app.py"]
