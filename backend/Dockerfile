FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libfreetype6 \
    libharfbuzz0b \
    shared-mime-info \
    fonts-dejavu \
    locales \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i '/es_MX.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen

ENV LANG es_MX.UTF-8
ENV LANGUAGE es_MX:es
ENV LC_ALL es_MX.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000
