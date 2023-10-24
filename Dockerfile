FROM python:3.7-slim

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

RUN mkdir -p /NetProx
WORKDIR /NetProx

COPY wsgi.py .
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY netprox netprox/
COPY setup.py .
COPY MANIFEST.in .
COPY README.md .

CMD ["/usr/local/bin/gunicorn", "-w4", "-b0.0.0.0:5000", "wsgi:app"]
