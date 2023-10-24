<br>

<div align="center">
  <H1> Netprox </H1>
    <p>Netbox and Proxmox integration</p>
  <img src="https://github.com/chris8838/netprox/actions/workflows/ci.yml/badge.svg" alt="CI status" />
</div>



An Application that connects Netbox with Proxmox in order to create VMs in Proxmox out of Netbox.

## Usage  

Webhooks will be send to Netprox and and it will create VMs via an API call in Proxmox.  
Netprox will act as a middleware between Netbox and Proxmox.

## Docker
In order to run a container you need to first build the docker image from the Dockerfile   
by typing the following command while you are in the folder `docker build -t netprox:latest .` .
If this build is finished it is recommended to create and `env.list` file containing all the needed environment variables.
Example of the content from a env.list file:
``` 
NETBOX_URL=https://netbox.myhome.org
PROXMOX_USER=admin
...
```
After you created the env.list file you can start the container temporary with the command:   
`docker run --rm --env-file envs.list -p 5000:5000 --name netprox netprox:latest`
or to have the container run as a demon:  
`docker run -d --env-file envs.list -p 5000:5000 --name netprox netprox:latest`

For the future there is a docker-compose file planed. 

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
