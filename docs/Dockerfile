FROM python:3.11-slim

RUN pip install sphinx myst-parser sphinx-rtd-theme

WORKDIR /app

COPY . .

RUN sphinx-build -b html source build/html
