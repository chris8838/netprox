FROM python:3.7

RUN mkdir -p /NetProx/package
WORKDIR /NetProx

COPY wsgi.py .
COPY requirements.txt .
RUN pip3 install -r requirements.txt


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
ENV FLASK_HOST="0.0.0.0"
ENV FLASK_SECRETKEY="beX0aem3vee7ohn"

COPY netprox/. ./package/NetProx
COPY setup.py ./package
COPY MANIFEST.in ./package
COPY README.md ./package

WORKDIR /NetProx/package
RUN python setup.py install

WORKDIR /NetProx
CMD ["/usr/local/bin/gunicorn", "-w4", "-b0.0.0.0:5000", "wsgi:app"]
