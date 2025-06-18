FROM python:3.10-slim

# Instalar dependencias necesarias para Selenium + Chromium
RUN apt-get update && apt-get install -y \
    chromium chromium-driver fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    wget unzip gnupg curl \
    && apt-get clean

# Variables de entorno
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PATH="$CHROMEDRIVER_PATH:$PATH"

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script
COPY scraper.py .

# Ejecutar el script
CMD ["python", "scraper.py"]
