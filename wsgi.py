#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Script that Gunicorn is starting the flask application with."""

__author__ = "Christopher Hoffmann"
__contact__ = "christopher.hoffmann@zalando.de"
__license__ = "MIT"
__copyright__ = "(c) by Zalando SE"
__version__ = "0.1.0"

from netprox.main import app
from netprox.classes import cf, all_config

if __name__ == "__main__":
    if all_config:
        app.run(host=cf.flask_host, debug=cf.flask_debug)
