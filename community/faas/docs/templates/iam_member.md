# IAM Member

IAM Member deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](docs/templates/project.md)


## Deployment

### Resources

- [projects.setIamPolicy](https://cloud.google.com/resource-manager/reference/rest/v1/projects/setIamPolicy)
- [projects.getIamPolicy](https://cloud.google.com/resource-manager/reference/rest/v1/projects/getIamPolicy)


### Properties

See `properties` section in the schema files

-  [iam_member](../../templates/iam_member.py.schema)


### Deployment

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
