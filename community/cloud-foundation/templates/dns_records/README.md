# Networks and subnets

Templated Cloud DNS creating record sets template

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)

## Deployment

### Resources

- [gcp-types/v1](https://cloud.google.com/compute/docs/reference/latest/networks)

### Properties

See `properties` section in the schema files

-  [DNS Records](dns_records.py.schema)

### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/cloud-foundation](community/cloud-foundation) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/dns_records.yaml](examples/dns_records.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```(shell)
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/cloud-foundation
cp templates/dns_records/examples/dns_records.yaml my_dns_records.yaml
vim my_dns_records.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_dns_records.yaml
```

#### Create

```(shell)
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_dns_records.yaml
```


#### Delete

```(shell)
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Create DNS ResourceRecordSets](examples/dns_records.yaml)
