#!/usr/bin/env python3

__author__ = "Christopher Hoffmann"
__contact__ = "christopher.hoffmann@zalando.de"
__license__ = "MIT"
__virtual_name__ = "netprox_backend"

import hashlib
import hmac
import logging
import os
from typing import Callable

from _hashlib import HASH
from flask import render_template

from netprox.classes import cf
from netprox.classes.Core import NetboxCall, Proxmox, VMachine

logger = logging.getLogger(__virtual_name__)


def _check_signature(
    key: bytes,
    msg: bytes,
    signature: str,
    digestmode: Callable[[str], HASH] = hashlib.sha512,
) -> bool:
    """
    This function is checking the signature of the webhook
    Args:
        key: key from the webhook
        msg: message from the webhook
        signature: signature from the webhook
        digestmode: mode for the digest

    Returns: bool

    """
    digester = hmac.new(key=key, msg=msg, digestmod=digestmode)

    return digester.hexdigest() == signature


def update_vm(request_obj) -> tuple:
    """
    This function is called by the webhook and will update the VM in Netbox
    Args:
        request_obj: request object from flask

    Returns: tuple with message and status code

    """
    if not request_obj.json.get("event", ""):
        return "not a delete event", 401

    if not request_obj.headers.get("X-Hook-Signature"):
        logger.warning("signature missing")
        return "signature missing", 401

    vm_info = request_obj.json.get("data", {})

    p = Proxmox(
        host=cf.proxmox_host,
        username=cf.proxmox_user,
        token_name=cf.proxmox_token_name,
        token=cf.proxmox_token,
        ssl_verify=False,
        vm_id=vm_info.get("custom_fields", {}).get("vmid"),
    )

    if (
        request_obj.json.get("data", {}).get("status", {}).get("value", "")
        == "offline"
    ):
        p.stop_vm()
        return "VM marked as Offline, Proxmox stopped the VM", 200
    if (
        request_obj.json.get("data", {}).get("status", {}).get("value", "")
        == "active"
    ):
        p.start_vm()
        return "VM marked as Active, Proxmox is starting the VM", 200
    else:
        logger.debug(
            request_obj.json.get("data", {}).get("status", {}).get("value", "")
        )
        return (
            request_obj.json.get("data", {}).get("status", {}).get("value", "")
        )


def delete_vm(request_obj) -> tuple:
    """
    This function is called by the webhook and will delete the VM in Proxmox
    Args:
        request_obj: request object from flask

    Returns: tuple with message and status code

    """
    logger.debug("Received the following Header:\n%s", request_obj.headers)
    logger.debug("Received the following data:\n%s", request_obj.data)
    logger.debug("Received the following data/json:\n%s", request_obj.json)

    if not request_obj.json.get("event", ""):
        return "not a delete event", 401

    if not request_obj.headers.get("X-Hook-Signature"):
        logger.warning("signature missing")
        return "signature missing", 401

    authorized_request = _check_signature(
        key=os.environ.get("NETBOX_WEBHOOK_SECRET").encode(),
        msg=request_obj.data,
        signature=request_obj.headers.get("X-Hook-Signature"),
    )

    if not authorized_request:
        logger.warning("signature not valid")
        return "signature not valid", 401

    vm_info = request_obj.json.get("data", {})
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

    return {"message": "ok"}, 200


def create_vm(request_obj) -> render_template:
    """
    This function is called by the webhook and will create the VM in Proxmox
    Args:
        request_obj: request object from flask

    Returns: render_template

    """
    logger.debug("Received the following Header:\n%s", request_obj.headers)
    # logger.debug("Received the following data:\n%s", request.data)
    # logger.debug("Received the following data/json:\n%s", request.json)
    nb = NetboxCall(
        netbox_url=cf.netbox_url,
        netbox_token=cf.netbox_token,
        ssl_verify=cf.netbox_ssl_verify,
        netbox_id=request_obj.values.get("id"),
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
        if (
            vm.get("vmid") == str(netbox_vm_vmid)
            and vm.get("name") == nb.vm.name
        ):
            message = "VM with the same name and ID exists already!"
            return render_template("error.html", message=message)

        if vm.get("vmid") == str(netbox_vm_vmid):
            message = (
                f"VMID already in use! The VM {nb.vm.name} comming from Netbox"
                f"has the same VM-ID ({vm.get('vmid')}) "
                f"as the VM {vm.get('name')} from Proxmox."
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
        "net0": "virtio,bridge=vmbr0",
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
            result=f"VM crated with result: "
            f"{p.create_vm(vm_specs=vm_data)} but not started",
        )
    if str(nb.vm.status) == "Planned":
        return render_template(
            "success.html",
            proxmox_url=cf.proxmox_host,
            result="Status of the VM is Planned. "
            "VM will not be created in Proxmox",
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


if __name__ == "__main__":
    pass
