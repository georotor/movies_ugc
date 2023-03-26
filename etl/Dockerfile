FROM python:3.11.2-slim

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt \
     \
     && apt autoremove -y \
     && apt-get clean \
     && rm -rf /var/lib/apt/lists/*

COPY src/ /opt/app/

RUN groupadd -r api && useradd -d /opt/app -r -g api api \
     && chown api:api -R /opt/app

USER api

ENTRYPOINT ["python", "main.py"]
