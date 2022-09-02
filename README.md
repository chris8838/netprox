![Tests](https://github.com/chris8838/netprox/actions/workflows/pylint.yml/badge.svg)
# NetProx  
Application that connects Netbox with Proxmox in order to create VMs in proxmox.

## Usage  

Webhooks will be send to Netprox and and it will create VMs via an API call in Proxmox.  
Netprox will act as a middleware between Netbox and Proxmox.

## Netbox configuration

In order to let Netbox create a VM for you it is recommanded to 
create a `Custome link` that will trigger the webhook.
Here is an example of configuration of a `Custome link` that should work:
```
Content type: Virtualization > virtual maschine
Name: Create VM
Link text: Create {{ obj.name }} in Proxmox
Link URL: http://192.168.1.10:5000/webhook/create-vm-button?id={{ obj.id }} 
          # the URL differs from your installtion
```
You should also create `Custome fields`, because these are parameters used by the app.


#### OS Field
Required=TRUE  

```
Type: Selection
Name: os
Label: os
Description: operating system
Content types: Virtualization > virtual maschine
Choices: ubuntu-20.04.1-desktop-amd64.iso,ubuntu-20.04.1-live-server-amd64.iso,debian-10.10.0-amd64-netinst.iso
        # Choices my differ from you needs.
```
#### Template Field
Required=FALSE  
```
Type: Selection
Name: template
Label: template
Description: OS template stored in Proxmox to use
Content types: Virtualization > virtual maschine
Choices: Template-103-ubuntu-20.04.1-live-server,None
        # Choices my differ from you needs.
```

#### VMID Field
Required=TRUE  

```
Type: Integer
Name: vmid
Label: vmid
Description: VM-ID in Proxmox
Content types: Virtualization > virtual maschine

```

## TODO  

- [X] write a docker file 
- [X] write tox file
- [X] write setup.py file
- [ ] create tests for tox
- [ ] test tox environment and tests