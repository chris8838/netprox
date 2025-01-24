FROM python:3.11-slim

ENV POETRY_VERSION="1.8.4"

ENV LOG_LEVEL="DEBUG"
ENV NETBOX_URL=""
ENV NETBOX_TOKEN=""
ENV NETBOX_WEBHOOK_SECRET=""
ENV NETBOX_SSL_VERIFY=0
ENV PROXMOX_HOST=""
ENV PROXMOX_TOKEN=""
ENV PROXMOX_TOKEN_NAME=""
ENV PROXMOX_USER=""
ENV PROXMOX_SSL_VERIFY=0
ENV FLASK_DEBUG=True
ENV FLASK_HOST="127.0.0.1"
ENV FLASK_SECRETKEY="beX0aem3vee7ohn"

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

