# Google Cloud Storage Buckets

This Template creates a cloud storage bucket

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Create a [GCP project, setup billing, enable requisite APIs](../project/README.md)
- Grant the [/roles/storage.admin](https://cloud.google.com/storage/docs/access-control/iam-roles) to the project service account

## Deployment

### Resources

- [storage.v1.bucket](https://cloud.google.com/storage/docs/creating-buckets)

### Properties

See `properties` section in the schema files

- [gcs_bucket](gcs_bucket.py.schema)

### Usage

1. Clone the [DM Samples_repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)

```bash
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
```

2. Go to the [community/cloud-foundation](../../) directory

```bash
    cd community/cloud-foundation
```

3. Copy the example DM config to be used as a model for the deployment, in this case [examples/bigquery.yaml](examples/bigquery.yaml)

```bash
    cp templates/bigquery/examples/bigquery.yaml my_bigquery.yaml
```

4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.

```bash
    vim my_bigquery.yaml  # <== change values to match your GCP setup
```

5. Create your deployment as described below, replacing <YOUR_DEPLOYMENT_NAME>
   with your with your own deployment name

```bash
    gcloud deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
    --config my_bigquery.yaml
```

6. In case you need to delete your deployment:

```bash
    gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
```

## Examples

- [Create Storage Bucket](examples/gcs_bucket.yaml)
- [Create Storage Bucket with LifeCycle Enabled](examples/gcs_bucket_lifecycle.yaml)
- [Create Storage Bucket with IAM Bindings](examples/gcs_bucket_iam_bindings.yaml)
