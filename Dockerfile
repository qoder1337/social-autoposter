FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    locales \
    libgbm-dev \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    libsqlite3-dev


RUN echo "de_DE.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    update-locale LC_ALL=de_DE.UTF-8 LANG=de_DE.UTF-8

# Setze die Zeitzone im Container
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime && echo "Europe/Berlin" > /etc/timezone

WORKDIR /code

COPY requirements-prod.txt .

RUN pip install --no-cache-dir -r requirements-prod.txt

COPY run.py ./
COPY favicon.ico ./
COPY app/ ./app/

# Startbefehl ohne Server
CMD ["python3", "run.py"]
