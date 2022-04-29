![Tests](https://github.com/chris8838/netprox/actions/workflows/tox.yml/badge.svg)
# NetProx
Application that connects Netbox with Proxmox in order to create VMs in proxmox.

## Usage
Webhooks from Netbox need to be send to Netprox application and it will create VMs via an API call in Proxmox.  
Netprox will act as a middleware between Netbox and Proxmox.

##TODO
- [X] write a docker file 
- [X] write tox file
- [X] write setup.py file
- [ ] create tests for tox
- [ ] test tox environment and tests
