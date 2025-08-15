FROM python:3.11-slim

# Variables regionales
ENV LANG=es_MX.UTF-8 \
    LANGUAGE=es_MX:es \
    LC_ALL=es_MX.UTF-8

WORKDIR /app

# Instala dependencias del sistema y msodbcsql17
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg2 \
    unixodbc-dev \
    gcc \
    g++ \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libxml2 \
    libjpeg62-turbo \
    libfreetype6 \
    libharfbuzz0b \
    locales \
    apt-transport-https \
    ca-certificates \
 && mkdir -p /etc/apt/keyrings \
 && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
 && chmod 644 /etc/apt/keyrings/microsoft.gpg \
 && echo "deb [signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
 && rm -rf /var/lib/apt/lists/* \
 && sed -i '/es_MX.UTF-8/s/^# //g' /etc/locale.gen \
 && locale-gen

# Copiar archivos e instalar Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
