#!/usr/bin/env python3

__author__ = "Christopher Hoffmann"
__contact__ = "christopher.hoffmann@zalando.de"
__license__ = "MIT"
__copyright__ = "(c) by Zalando SE"
__version__ = "0.1.0"

import logging
import os

logger = logging.getLogger(__name__)


class Config:
    """
    Gets the config from environment variables and sets them as class objects.
    In addition, you can
    provide kwargs which become class objects as well.
    In addition, all the config will be stored in a dict which you can
    access via the class object 'get_config' .
    Example:
        cf = Config(MYCONFIG='TEST.cfg')
        print(cf.MYCONFIG)
    Output:
        Test.cfg
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.kwargs = kwargs
        self.netbox_url = os.getenv("NETBOX_URL")
        self.netbox_token = os.getenv("NETBOX_TOKEN")
        self.netbox_webhook_secret = os.getenv("NETBOX_WEBHOOK_SECRET")
        self.netbox_ssl_verify = os.getenv("NETBOX_SSL_VERIFY")
        self.proxmox_host = os.getenv("PROXMOX_HOST")
        self.proxmox_user = os.getenv("PROXMOX_USER")
        self.proxmox_token_name = os.getenv("PROXMOX_TOKEN_NAME")
        self.proxmox_token = os.getenv("PROXMOX_TOKEN")
        self.proxmox_ssl_verify = os.getenv("PROXMOX_SSL_VERIFY")
        self.flask_secret_key = os.getenv("FLASK_SECRETKEY")
        self.flask_host = os.getenv("FLASK_HOST")
        self.flask_debug = os.getenv("FLASK_DEBUG")
        self.all_config_dict = {}
        self.all_config()

    @property
    def get_config(self):
        logger.debug("get_config(self): return config dict")
        return self.all_config_dict

    def all_config(self):
        logger.debug("all_config(self): create config dict")
        standard_conf = {
            "NETBOX_URL": self.netbox_url,
            "NETBOX_TOKEN": self.netbox_token,
            "NETBOX_WEBHOOK_SECRET": self.netbox_webhook_secret,
            "NETBOX_SSL_VERIFY": self.netbox_ssl_verify,
            "PROXMOX_HOST": self.proxmox_host,
            "PROXMOX_USER": self.proxmox_user,
            "PROXMOX_TOKEN_NAME": self.proxmox_token_name,
            "PROXMOX_TOKEN": self.proxmox_token,
            "PROXMOX_SSL_VERIFY": self.proxmox_ssl_verify,
            "FLASK_SECRETKEY": self.flask_secret_key,
            "FLASK_HOST": self.flask_host,
            "FLASK_DEBUG": self.flask_debug,
        }
        if self.kwargs:
            logger.debug(
                "all_config(self): kwargs are set and will "
                "be added to the config dict"
            )
            self.all_config_dict.update(standard_conf)
            self.all_config_dict.update(self.kwargs)
        self.all_config_dict.update(standard_conf)

    def check_config(self):
        logger.debug("check_config(self): check if all config is set.")
        if not all(self.all_config_dict.values()):
            missing_config = []
            for env_key, env_value in self.all_config_dict.items():
                if not env_value:
                    missing_config.append(env_key)
            logger.error("Not all envs are set! %s" % missing_config)
            return False
        return True


if __name__ == "__main__":
    pass
