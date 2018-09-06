# Managed Instance Group

Templated Managed Instance Group deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)

## Deployment

### Resources

- [compute.v1.instance](https://cloud.google.com/compute/docs/reference/latest/instances)
- [compute.v1.autoscaler](https://cloud.google.com/compute/docs/reference/latest/autoscalers)
- [compute.v1.regionalAutoscaler](https://cloud.google.com/compute/docs/reference/latest/regionAutoscalers)
- [compute.v1.instanceTemplate](https://cloud.google.com/compute/docs/reference/latest/instanceTemplates)
- [compute.v1.instanceGroupManager](https://cloud.google.com/compute/docs/reference/latest/instanceGroupManagers)
- [compute.v1.regionalInstanceGroupManager](https://cloud.google.com/compute/docs/reference/latest/regionInstanceGroupManagers)

### Properties

See `properties` section in the schema files

- [Managed Instance Group](managed_instance_group.py.schema)

### Outputs

See `outputs` section in the schema files

- [Managed Instance Group](managed_instance_group.py.schema)

### Deployment

#### Usage

1. Clone the [DM Samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)
2. Go to the [community/cloud-foundation](../../) directory
3. Copy the example DM config to be used as a model for the deployment, in this
   case [examples/managed\_instance\_group.yaml](examples/managed_instance_group.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name

For example:

``` bash
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
cd community/cloud-foundation
cp templates/managed_instance_group/examples/managed_instance_group.yaml \
    my_managed_instance_group.yaml
vim my_managed_instance_group.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_managed_instance_group.yaml
```

#### Create

``` bash
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_managed_instance_group.yaml
```

#### Delete

``` bash
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

## Examples

- [Managed Instance Group](examples/managed_instance_group.yaml)
