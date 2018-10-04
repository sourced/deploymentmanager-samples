# Highly available NAT Gateway for GCE 

## Overview
This example shows how to create a single NAT gateway in single zone of a GCP region. It can be used by GCE VM with internal only IP addresses to access internet resources. Traffic is routed through the NAT Gateway VM via a network route to the same instance tag.

This deployment example deploys the following:
- NAT Gateway VM
- A VPC Network Route (for routing the traffic of all tagged internal VMs)
- A Firewall rule to allow all traffic from private IP VMs to internet.
  
## Prerequisites
Make sure that **Google Cloud RuntimeConfig API** is enabled in Developers Console for your GCP project. Check [Enable and disable APIs](https://support.google.com/cloud/answer/6158841?hl=en) article for more information.

## Deployment
Use `config.yaml` to deploy this example template. Before deploying,
edit the file and specify parameters like project id, network, subnetwork, NAT Gateway Tag, Natted VMs tag, zones to deploy the gateway VM. Review the full list of supported parameters in `single-nat-gateway.py.schema`. 

When ready, deploy with the following command:

    gcloud deployment-manager deployments create single-nat-example --config config.yaml

## Testing
Create a GCE instances without an external IP address, make sure it's tagged with a tag specified in *nated-vm-tag* parameter of your deployment, e.g.:

    gcloud compute instances create internal-ip-only-vm --no-address --tags no-ip --zone us-west1-a


SSH into the instance by hopping through one of the NAT gateway instances, first make sure that SSH agent is running and your private SSH key is added to the authentication agent.

```
eval ssh-agent $SHELL
ssh-add ~/.ssh/google_compute_engine
gcloud compute ssh $(gcloud compute instances list --filter=name~ha-nat-example- --limit=1 --uri) --zone us-west1-d --ssh-flag="-A" -- ssh  internal-ip-only-vm
```

Check that the VM can access external resources, note that IP address returned by curl will be one of the external IP addresses of our NAT gateways.
 
    while true; do curl http://ipinfo.io/ip; sleep 1; done

