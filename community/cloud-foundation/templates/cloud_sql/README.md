# Cloud DNS Managed Zone

This template creates a managed zone in the Cloud DNS (Domain Name System).

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, set up billing, enable requisite APIs](../project/README.md)
- Grant the [dns.admin](https://cloud.google.com/dns/access-control) IAM role to the Deployment Manager service account

Private IP Pre-reqs
API and IAM requirements

    You must have enabled the Service Networking API for your project.

    Enabling APIs requires the servicemanagement.services.bind IAM permission.

    Establishing private services access requires the following IAM permissions, which are included in the Network Administrator role:
        compute.networks.list
        compute.globalAddresses.list
        compute.globalAddresses.create
        servicenetworking.services.addPeering

    After private services access is established for your network, you do not need extra IAM permissions to configure an instance to use private IP.

The activation policy specifies when the instance is activated; it is applicable only when the instance state is RUNNABLE. Valid values:
ALWAYS: The instance is on, and remains so even in the absence of connection requests.
NEVER: The instance is off; it is not activated, even if a connection request arrives.
ON_DEMAND: First Generation instances only. The instance responds to incoming requests, and turns itself off when not in use. Instances with PER_USE pricing turn off after 15 minutes of inactivity. Instances with PER_PACKAGE pricing turn off after 12 hours of inactivity.


https://cloud.google.com/sql/docs/mysql/flags#list-flags
https://cloud.google.com/sql/docs/postgres/flags#list-flags-postgres

## Deployment

### Resources

- [dns.v1.managedZone](https://cloud.google.com/dns/docs/)

### Properties

See the `properties` section in the schema file(s):
- [Cloud DNS Managed Zone](dns_managed_zone.py.schema)

### Usage

1. Clone the [Deployment Manager samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples):

```shell
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
```

2. Go to the [community/cloud-foundation](../../) directory:

```shell
    cd community/cloud-foundation
```

3. Copy the example DM config to be used as a model for the deployment; in this case, [examples/dns_managed_zone.yaml](examples/dns_managed_zone.yaml):

```shell
    cp templates/dns_managed_zone/examples/dns_managed_zone.yaml my_dns_managed_zone.yaml
```

4. Change the values in the config file to match your specific GCP setup (for properties, refer to the schema files listed above):

```shell
    vim my_dns_managed_zone.yaml  # <== change values to match your GCP setup
```

5. Create your deployment (replace <YOUR_DEPLOYMENT_NAME> with the relevant deployment name):

```shell
    gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_dns_managed_zone.yaml
```

6. In case you need to delete your deployment:

```shell
    gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

## Examples

- [Cloud DNS Managed Zone](examples/dns_managed_zone.yaml)