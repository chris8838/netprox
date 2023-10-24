#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christopher Hoffmann"
__contact__ = "christopher.hoffmann@zoutlook.com"
__license__ = "MIT"
__version__ = "0.1.0"
__virtual_name__ = "netprox_main"

import os
import logging


from flask import Flask
from flask import request

from netprox.backend import update_vm, delete_vm, create_vm
from netprox.classes import cf

logger = logging.getLogger(__virtual_name__)


def prepare_logger():
    log_level = logging.getLevelName(os.getenv("LOG_LEVEL", "ERROR"))
    log_level = log_level if isinstance(log_level, int) else logging.ERROR
    logger.setLevel(log_level)
    stream_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(stream_formatter)
    streamhandler.setLevel(
        logging.getLevelName(os.getenv("LOG_LEVEL", "ERROR"))
    )
    logger.addHandler(streamhandler)
    logger.debug("!Debug mode enabled, do not use this mode in production!")
    return logger


app = Flask(__name__)
app.secret_key = cf.flask_secret_key
prepare_logger()
logger.debug("Flask loaded")


@app.post("/webhook/update-vmachine")
def webhook_vm_update() -> tuple:
    """
    The Webhook endpoint fetches all incoming webhook for updating
    a VM and return with a tuple.
    Returns: tuple

    """
    return update_vm(request_obj=request)


@app.post("/webhook/delete-vmachine")
def webhook_vm_delete() -> tuple:
    """
    The Webhook endpoint fetches all incoming webhooks and return with a tuple.
    :return:
    """

    return delete_vm(request_obj=request)


@app.route("/webhook/create-vm-button", methods=["GET"])
def button() -> str:
    """
    The Webhook endpoint fetches all incoming GET request from the Custom Link
    in Netbox and return with a tuple.
    Returns:

    """
    return create_vm(request_obj=request)


@app.route("/health", methods=["GET"])
def health() -> dict:
    """
    The Health endpoint fetches all incoming GET
    request and return with a tuple.
    Returns: dict

    """
    return {"message": "ok"}


if __name__ == "__main__":
    pass
