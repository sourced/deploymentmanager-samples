# App Engine

This template creates an App Engine resource.

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, set up billing, enable requisite APIs](../project/README.md)
- Enable the App Engine Admin API
- Grant the [appengine.appAdmin](https://cloud.google.com/compute/docs/access/iam) IAM
  role to the [Deployment Manager service account](https://cloud.google.com/deployment-manager/docs/access-control#access_control_for_deployment_manager)

## Deployment

### Resources

- [appengine.v1.version](https://cloud.google.com/appengine/docs/admin-api/reference/rest/v1/apps.services.versions)

### Properties

See the `properties` section in the schema file(s):

- [App Engine](app_engine.py.schema)

### Usage

1. Clone the [Deployment Manager samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)

```shell
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
```

2. Go to the [community/cloud-foundation](../../) directory

```shell
    cd community/cloud-foundation
```

3. Copy the example DM config to be used as a model for the deployment, in this
   case [examples/app_engine.yaml](examples/app_engine.yaml)

```shell
    cp templates/app_engine/examples/app_engine.yaml \
        my_app_engine.yaml
```

4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.

```shell
    vim my_app_engine.yaml  # <== change values to match your GCP setup
```

5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name

```shell
    gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
        --config my_app_engine.yaml
```

6. In case you need to delete your deployment:

```shell
    gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

## Examples

- [Standard App Engine Environment](examples/standard_app_engine.yaml)
- [Flexible App Engine Environment](examples/flexible_app_engine.yaml)
