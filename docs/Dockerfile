FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir sphinx myst-parser sphinx_rtd_theme

WORKDIR /app
