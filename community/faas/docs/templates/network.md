# Networks and subnets

Templated network and subnet deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](docs/templates/project.md)


## Deployment

### Resources

- [compute.v1.network](https://cloud.google.com/compute/docs/reference/latest/networks)
- [compute.v1.subnetwork](https://cloud.google.com/compute/docs/reference/latest/subnetworks)


### Properties

See `properties` section in the schema files

-  [network](../../templates/network.py.schema)
-  [subnetwork](../../templates/subnetwork.py.schema)


### Deployment

<<<<<<< HEAD
#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/faas](community/faas) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/network.yaml](examples/network.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name

=======
>>>>>>> FAAS initial commit
#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
<<<<<<< HEAD
    --config network.yaml
=======
    --config <YOUR_DEPLOYMENT_CONFIG>.yaml
>>>>>>> FAAS initial commit
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Network with subnets](../examples/network.yaml)
