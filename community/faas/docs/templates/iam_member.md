# IAM Member

IAM Member deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](docs/templates/project.md)

## Development

### Resources

- [projects.setIamPolicy](https://cloud.google.com/resource-manager/reference/rest/v1/projects/setIamPolicy)
- [projects.getIamPolicy](https://cloud.google.com/resource-manager/reference/rest/v1/projects/getIamPolicy)


### Properties

See `properties` section in the schema files

-  [iam_member](../../templates/iam_member.py.schema)


### Deployment

#### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-sample)
2. Go to the [community/faas](community/faas) directory
3. Copy the example DM config to be used as a model for the deployment, in this case [examples/iam_member.yaml](examples/iam_member.yaml)
4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.
5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name

#### Create

```
gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config <YOUR_DEPLOYMENT_CONFIG>.yaml
```


#### Delete

```
gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```


## Examples

- [Adding Roles to a member](../examples/iam_member.yaml)
