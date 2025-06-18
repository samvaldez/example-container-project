FROM python:3.10-slim

# Instalar dependencias del sistema necesarias para Chromium
RUN apt-get update && apt-get install -y \
    chromium chromium-driver wget unzip gnupg curl \
    && apt-get clean

# Variables de entorno
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PATH="$CHROMEDRIVER_PATH:$PATH"

# Instalar librerías Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script
COPY scraper.py .

# Ejecutar el script
CMD ["python", "scraper.py"]
