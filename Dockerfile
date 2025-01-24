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

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN mkdir -p /NetProx
WORKDIR /NetProx

COPY wsgi.py .
COPY pyproject.toml .
COPY poetry.lock .
COPY netprox netprox/
RUN poetry install
COPY README.md .

CMD ["poetry", "run", "gunicorn", "-w4", "-b0.0.0.0:5000", "wsgi:app"]

