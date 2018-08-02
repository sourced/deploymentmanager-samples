# Cloud Router

Templated Cloud Router deployment

## Prerequisites
- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)
- Create a [network](../network/README.md)


## Deployment

### Resources

- [compute.v1.router](https://cloud.google.com/compute/docs/reference/rest/v1/routers)


### Properties

See `properties` section in the schema files

-  [Cloud Router](cloud_router.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/faas](community/faas) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/cloud-router.yaml](examples/cloud-router.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/faas
cp templates/cloud_router/examples/cloud-router.yaml my-cloud-router.yaml
vim my-cloud-router.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my-cloud-router.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my-cloud-router.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Cloud Router](examples/cloud-router.yaml)
