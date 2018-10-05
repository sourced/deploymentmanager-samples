# HA NAT Gateway

This template creates an HA NAT Gateway based on the number of regions specified

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)
- Grant the [compute.admin](https://cloud.google.com/compute/docs/access/iam) IAM
role to the [Deployment Manager service account](https://cloud.google.com/deployment-manager/docs/access-control#access_control_for_deployment_manager)

## Deployment

### Resources

- [compute.v1.addresses](https://cloud.google.com/compute/docs/reference/rest/v1/addresses)
- [compute.v1.instances](https://cloud.google.com/compute/docs/reference/rest/v1/instances)
- [compute.v1.firewalls](https://cloud.google.com/compute/docs/reference/rest/v1/firewalls)
- [compute.v1.routes](https://cloud.google.com/compute/docs/reference/rest/v1/routes)
- [compute.v1.healthChecks](https://cloud.google.com/compute/docs/reference/rest/v1/healthChecks)
- [compute.v1.instanceGroupManagers](https://cloud.google.com/compute/docs/reference/rest/v1/instanceGroupManagers)



### Properties

See `properties` section in the schema files

-  [HA NAT Gateway](ha_nat_gateway.py.schema)


#### Usage


1. Clone the [Deployment Manager samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)

```shell
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
```

2. Go to the [community/cloud-foundation](../../) directory

```shell
    cd community/cloud-foundation
```

3. Copy the example DM config to be used as a model for the deployment, in this
   case [examples/ha_nat_gateway.yaml](examples/ha_nat_gateway.yaml)

```shell
    cp templates/ha_nat_gateway/examples/ha_nat_gateway.yaml \
        my_ha_nat_gateway.yaml
```

4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.

```shell
    vim my_ha_nat_gateway.yaml  # <== change values to match your GCP setup
```

5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name

```shell
    gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
        --config my_ha_nat_gateway.yaml
```

6. In case you need to delete your deployment:

```shell
    gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_ha_nat_gateway.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [HA NAT Gateway] (examples/ha_nat_gateway.yaml )
