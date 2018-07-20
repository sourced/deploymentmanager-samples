# Logsink

Templated logsink deployment

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](docs/templates/project.md)


## Deployment

### Resources

- [logging.v2.sink](https://cloud.google.com/logging/docs/reference/v2/rest/v2/projects.sinks)


### Properties

See `properties` section in the schema files

-  [logsink](../../templates/logsink.py.schema)


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

- [Log entries exported to PubSub, Storage, BigQuery](../examples/logsink.yaml)
