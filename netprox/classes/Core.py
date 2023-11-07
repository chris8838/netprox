#!/usr/bin/env python3

__author__ = "Christopher Hoffmann"
__contact__ = "christopher.hoffmann@zalando.de"
__license__ = "MIT"
__copyright__ = "(c) by Zalando SE"
__version__ = "0.1.0"

import logging

import pynetbox
from proxmoxer import ProxmoxAPI

logger = logging.getLogger(__name__)


class NetboxObject:
    def __init__(self, webhook_data=None, **kwargs):
        """
        Main Class for all Webhooks.
        :param webhook_data: data from the webhook POST
        :type webhook_data: dict
        :param kwargs:
        """
        self.__dict__.update(kwargs)
        self.id = webhook_data.get("id", None)
        self.name = webhook_data.get("name", "")
        self.comments = webhook_data.get("comments", "")
        self.status = webhook_data.get("status", {}).get("value", "")


class VMachine(NetboxObject):
    def __init__(self, webhook_data, **kwargs):
        """

        :param webhook_data:
        :param kwargs:
        """
        super().__init__(webhook_data)
        self.__dict__.update(kwargs)
        self.memory = webhook_data.get("memory", None)
        self.disk = webhook_data.get("disk", None)
        self.vcpus = webhook_data.get("vcpus", "")
        self.os = webhook_data.get("custom_fields", {}).get("os", "")
        self.vmid = webhook_data.get("custom_fields", {}).get("vmid", "")


class Proxmox(ProxmoxAPI):
    def __init__(
        self,
        host: str,
        username: str,
        token_name: str,
        token: str,
        vm_id: str,
        ssl_verify=True,
        node_name="proxmox",
    ):
        super().__init__(
            host=host,
            user=username,
            token_name=token_name,
            token_value=token,
            verify_ssl=ssl_verify,
        )
        self.vm_id = vm_id
        self.ssl_verify = ssl_verify
        self.node_name = node_name

    def _check_ssl_verify(self):
        if self.ssl_verify == 0:
            self.ssl_verify = False
        if self.ssl_verify == 1:
            self.ssl_verify = True
        else:
            self.ssl_verify = self.ssl_verify

    def _get_vm_status(self):
        return (
            self.nodes(self.node_name)
            .qemu(self.vm_id)
            .status.current.get()
            .get("status")
        )

    def create_vm(self, vm_specs: dict = None):
        if not vm_specs:
            return False
        node = self.nodes(self.node_name)
        node.qemu.create(**vm_specs)
        return True

    def stop_vm(self):
        self.nodes(self.node_name).qemu(self.vm_id).status.stop.post()
        if self._get_vm_status() == "stopped":
            return True

        return False

    def suspend_vm(self):
        self.nodes(self.node_name).qemu(self.vm_id).status.suspend.post()
        return True

    def start_vm(self):
        if self._get_vm_status() == "stopped":
            self.nodes(self.node_name).qemu(self.vm_id).status.start.post()
            return True
        else:
            return False

    def shutdown_vm(self):
        self.nodes(self.node_name).qemu(self.vm_id).status.shutdown.post()
        return True

    def delete_vm(self):
        if self._get_vm_status() == "running":
            self.stop_vm()
            if self._get_vm_status() != "stopped":
                return False
            else:
                self.nodes(self.node_name).qemu.delete(self.vm_id)
                return True
        if self._get_vm_status() == "stopped":
            self.nodes(self.node_name).qemu.delete(self.vm_id)
            return True
        return False

    def vm_network_interface(self):
        return (
            self.nodes(self.node_name)
            .qemu(self.vm_id)
            .agent.get("network-get-interfaces")
        )

    def clone_template_vm(self, new_vm_id: int = None):
        self.nodes(self.node_name).qemu(self.vm_id).clone().post(
            newid=new_vm_id
        )
        return True

    @property
    def vms(self):
        all_vms = []
        vms = self.nodes(self.node_name).qemu.get()
        for vm in vms:
            if vm.get("template") != 1:
                all_vms.append(vm)
        return all_vms


class NetboxCall(pynetbox.api):
    def __init__(self, netbox_url, netbox_token, netbox_id, ssl_verify=True):
        super().__init__(
            url=netbox_url,
            token=netbox_token,
        )
        self.vm = None
        self.netbox_id = netbox_id
        self.vm_raw_dict = {}
        self.vm_opj = None
        self.ssl_verify = ssl_verify
        self._check_ssl_verify()
        self.http_session.verify = None
        self.netbox_vm_raw()

    def _check_ssl_verify(self):
        if self.ssl_verify == 0:
            self.http_session.verify = False
        if self.ssl_verify == 1:
            self.http_session = True

    def netbox_vm_raw(self):
        """
        getting the raw data from a Netbox device and fills self.device_raw_dict
        :return:
        """
        logger.debug("getting device %s", self.vm)
        self.vm = self.virtualization.virtual_machines.get(self.netbox_id)
        self.vm_raw_dict = dict(self.vm)

    def update_vm_information(self, new_info: dict = None):
        if not new_info:
            return None
        self.vm.update(new_info)
        return dict(self.vm)

    def create_tag(self, tag_name: str, color: str = "c0c0c0"):
        """
        checks if a tag in Netbox exists, if not it will create the tag.
        :param tag_name: Name of the tag.
        :param color: Enter a valid hexadecimal RGB color code. Default is grey.
        :return: tag name
        """
        if not tag_name:
            return None

        tag = self.extras.tags.get(name=tag_name)
        if not tag:
            print(f"Tag does not exist. Creating tag {tag_name}...")
            self.extras.tags.create(
                name=tag_name, slug=tag_name.lower(), color=color.lower()
            )
            tag = self.extras.tags.get(name=tag_name)
            return tag.id
        else:
            return tag.id
