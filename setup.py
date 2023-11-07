# !/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='NetProx',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    url='',
    license='MIT',
    author='Christopher Hoffmann',
    author_email='christopher.hoffmann@outlook.com',
    zip_safe=False,
    description='connect netbox with proxmox',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
