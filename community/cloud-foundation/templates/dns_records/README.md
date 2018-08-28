# DNS Resource RecordSets

Template for creating cloud dns resource record-sets

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)
- Grant [/roles/dns.admin](https://cloud.google.com/dns/access-control)

## Deployment

### Resources

- [gcp-types/dns-v1](https://cloud.google.com/dns/api/v1/changes)

### Properties

See `properties` section in the schema files

- [DNS Records](dns_records.py.schema)

### Deployment Overview

#### Usage

1. Clone the [DM Samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)
2. Navigate to the [community/cloud-foundation](../../../cloud-foundation) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/dns_records.yaml](examples/dns_records.yaml)
4. Change the values in the config file to match your specific GCP setup. Refer to the properties in the [schema file](dns_records.py.schema)
5. DNS resource record-sets can be added to an existing zone. Ensure that a managed-zone exists before running the next step
   - Cloud DNS managed zone created either using `gcloud dns managed-zone create ZONE_NAME --dns-name=<DNS_NAME> --description=<ZONE_DESCRIPTION>` OR
   - Using the [DNS managed zone](../../../cloud-foundation/templates/dns_managed_zone) template deployment
6. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME> with your with your own deployment name

For example:

```(shell)
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/cloud-foundation
cp templates/dns_records/examples/dns_records.yaml my_dns_records.yaml
vim my_dns_records.yaml  # <== change values to match your GCP setup
gcloud dns managed-zones create <MANAGED_ZONE_NAME_FROM_YAML> \
    --dns-name="<DNS_DOMAINNAME_FROM_YAML>" --description="<YOUR_MANAGED_ZONE_DESCRIPTION>"
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
