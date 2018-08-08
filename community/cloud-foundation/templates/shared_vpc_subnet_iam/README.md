# Shared VPC Subnet IAM

Template to grant IAM roles for a user on a shared VPC subnet.

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)
- Create a [network and subnetworks](../network/README.md)

## Deployment

### Resources

- [gcp-types/compute-beta:compute.subnetworks.setIamPolicy](https://cloud.google.com/compute/docs/reference/rest/beta/subnetworks/setIamPolicy)
- [gcp-types/compute-beta:compute.subnetworks.getIamPolicy](https://cloud.google.com/compute/docs/reference/rest/beta/subnetworks/getIamPolicy)


### Properties

See `properties` section in the schema files

-  [Shared VPC Subnet IAM](shared_vpc_subnet_iam.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/cloud_foundation](community/cloud_foundation) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/shared-vpc-subnet-iam.yaml](examples/shared-vpc-subnet-iam.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name


For example:

```
git clone https://github.com/GoogleCloudPlatform/deploymentmanager-sample
cd community/cloud_foundation
cp templates/shared_vpc_subnet_iam/examples/shared-vpc-subnet-iam.yaml my-shared-vpc-subnet-iam.yaml
vim my-shared-vpc-subnet-iam.yaml  # <== change values to match your GCP setup
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my-shared-vpc-subnet-iam.yaml
```

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my-shared-vpc-subnet-iam.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Shared VPC Subnet IAM](examples/shared-vpc-subnet-iam.yaml)
