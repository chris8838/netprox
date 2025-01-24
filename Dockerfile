# syntax=docker/dockerfile:1
# check=skip=SecretsUsedInArgOrEnv

FROM python:3.11-slim

ENV POETRY_VERSION="1.8.4"



RUN pip install poetry==${POETRY_VERSION}

RUN mkdir -p /NetProx
WORKDIR /NetProx

COPY wsgi.py .
COPY pyproject.toml .
COPY poetry.lock .
COPY netprox netprox/
COPY README.md .

RUN poetry install

CMD ["poetry", "run", "gunicorn", "-w4", "-b0.0.0.0:5000", "wsgi:app"]

