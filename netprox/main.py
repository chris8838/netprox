#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christopher Hoffmann"
__contact__ = "christopher.hoffmann@zoutlook.com"
__license__ = "MIT"
__version__ = "0.1.0"
__virtual_name__ = "netprox_main"

import os
import logging
import hmac
import hashlib

from typing import Callable
from _hashlib import HASH


from flask import Flask
from flask import request, render_template

from classes import cf, config
from classes.Core import VMachine, Proxmox, NetboxCall

logger = logging.getLogger(__virtual_name__)


def prepare_logger():
    log_level = logging.getLevelName(os.getenv("LOG_LEVEL", "ERROR"))
    log_level = log_level if type(log_level) == int else logging.ERROR
    logger.setLevel(log_level)
    stream_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(stream_formatter)
    streamhandler.setLevel(logging.getLevelName(os.getenv("LOG_LEVEL", "ERROR")))
    logger.addHandler(streamhandler)
    logger.debug("!Debug mode enabled, do not use this mode in production!")
    return logger


def _check_signature(
    key: bytes,
    msg: bytes,
    signature: str,
    digestmode: Callable[[str], HASH] = hashlib.sha512,
) -> bool:
    digester = hmac.new(key=key, msg=msg, digestmod=digestmode)

    return digester.hexdigest() == signature


app = Flask(__name__)
app.secret_key = cf.flask_secret_key
prepare_logger()
logger.debug("Flask loaded")


@app.post("/webhook/update-vmachine")
def vm_update():
    if not request.json.get("event", ""):
        return "not a delete event", 401

    if not request.headers.get("X-Hook-Signature"):
        logger.warning("signature missing")
        return "signature missing", 401

    # logger.debug("Received the following Header:\n%s", request.headers)
    # logger.debug("Received the following data:\n%s", request.data)
    # logger.debug("Received the following data/json:\n%s", request.json)
    vm_info = request.json.get("data", {})

    p = Proxmox(
        host=cf.proxmox_host,
        username=cf.proxmox_user,
        token_name=cf.proxmox_token_name,
        token=cf.proxmox_token,
        ssl_verify=False,
        vm_id=vm_info.get("custom_fields", {}).get("vmid"),
    )

    if request.json.get("data", {}).get("status", {}).get("value", "") == "offline":
        p.stop_vm()
        return "VM marked as Offline, Proxmox stopped the VM"
    if request.json.get("data", {}).get("status", {}).get("value", "") == "active":
        p.start_vm()
        return "VM marked as Active, Proxmox is starting the VM"
    else:
        print(request.json.get("data", {}).get("status", {}).get("value", ""))
        return request.json.get("data", {}).get("status", {}).get("value", "")


@app.post("/webhook/delete-vmachine")
def webhook():
    """
    The Webhook endpoint fetches all incoming webhooks and return with a tuple.
    :return:
    """
    # pylint: disable=broad-except
    logger.debug("Received the following Header:\n%s", request.headers)
    logger.debug("Received the following data:\n%s", request.data)
    logger.debug("Received the following data/json:\n%s", request.json)

    if not request.json.get("event", ""):
        return "not a delete event", 401

    if not request.headers.get("X-Hook-Signature"):
        logger.warning("signature missing")
        return "signature missing", 401

    authorized_request = _check_signature(
        key=os.environ.get("NETBOX_WEBHOOK_SECRET").encode(),
        msg=request.data,
        signature=request.headers.get("X-Hook-Signature"),
    )

    if not authorized_request:
        logger.warning("signature not valid")
        return "signature not valid", 401

    vm_info = request.json.get("data", {})
    vm = VMachine(webhook_data=vm_info, **vm_info.get("custom_fields", {}))

    p = Proxmox(
        host=cf.proxmox_host,
        username=cf.proxmox_user,
        token_name=cf.proxmox_token_name,
        token=cf.proxmox_token,
        ssl_verify=False,
        vm_id=vm.vmid,
    )

    logger.info("%s" % p.delete_vm())

    return {"message": "ok"}


@app.route("/webhook/create-vm-button", methods=["GET"])
def button():

    nb = NetboxCall(
        netbox_url=cf.netbox_url,
        netbox_token=cf.netbox_token,
        ssl_verify=cf.netbox_ssl_verify,
        netbox_id=request.values.get("id"),
    )

    netbox_vm_vmid = nb.vm.custom_fields.get("vmid", None)

    p = Proxmox(
        host=cf.proxmox_host,
        username=cf.proxmox_user,
        token_name=cf.proxmox_token_name,
        token=cf.proxmox_token,
        ssl_verify=False,
        vm_id=netbox_vm_vmid,
    )

    all_vms = p.vms
    for vm in all_vms:
        if vm.get("vmid") == str(netbox_vm_vmid) and vm.get("name") == nb.vm.name:
            message = f"VM with the same name and ID exists already!"
            return render_template("error.html", message=message)

        if vm.get("vmid") == str(netbox_vm_vmid):
            message = (
                f"VMID already in use! The VM {nb.vm.name} comming from Netbox "
                f"has the same VM-ID ({vm.get('vmid')}) as the VM {vm.get('name')} from Proxmox."
            )
            return render_template("error.html", message=message)

    vm_raw_data = [
        netbox_vm_vmid,
        nb.vm.custom_fields.get("os", ""),
        nb.vm.name,
        nb.vm.memory,
        nb.vm.disk,
        nb.vm.vcpus,
    ]
    vm_data = {
        "vmid": netbox_vm_vmid,
        "cdrom": f'local:iso/{nb.vm.custom_fields.get("os", "")}',
        "name": nb.vm.name,
        "storage": "local",
        "memory": nb.vm.memory,
        "scsi0": f"local-lvm:{nb.vm.disk}",
        "cores": int(float(nb.vm.vcpus)),
        "start": 1,
    }

    if not all(vm_raw_data):
        # todo render missing data into html
        message = "Not all data to create the VM are provided."
        return render_template("error.html", message=message)

    if str(nb.vm.status) == "Staged":
        vm_data["start"] = 0
        tag = nb.create_tag(tag_name="staged", color="8bc34a")
        netbox_label = {"tags": [tag]}
        nb.update_vm_information(netbox_label)
        return render_template(
            "success.html",
            proxmox_url=cf.proxmox_host,
            result=f"VM crated with result: {p.create_vm(vm_specs=vm_data)} but not started",
        )
    if str(nb.vm.status) == "Planned":
        return render_template(
            "success.html",
            proxmox_url=cf.proxmox_host,
            result="Status of the VM is Planned. VM will not be created in Proxmox",
        )
    else:
        tag = nb.create_tag(tag_name="created", color="8bc34a")
        netbox_label = {"tags": [tag]}
        nb.update_vm_information(netbox_label)
        return render_template(
            "success.html",
            proxmox_url=cf.proxmox_host,
            result=p.create_vm(vm_specs=vm_data),
        )


@app.route("/health", methods=["GET"])
def health():
    return {"message": "ok"}


if __name__ == "__main__":
    pass
