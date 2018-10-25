# Cloud Tasks

This template creates Cloud Tasks.

## Prerequisites

- Install [gcloud](https://cloud.google.com/sdk)
- Install gcloud **beta** components:

  ```shell
  gcloud components update
  gcloud components install beta
  ```

- Create a [GCP project, set up billing, enable requisite APIs](../project/README.md)
- Enable the [Cloud Tasks API](https://console.cloud.google.com/apis/library/cloudtasks.googleapis.com)
  from Google Cloud console
- Grant the [appengine.applications.get](https://cloud.google.com/appengine/docs/admin-api/access-control)
  IAM permission to the Deployment Manager service account
- Create a custom type-provider named `cloudtasks`

### Creating cloudtasks custom type-provider

- Create an oAuth Binding options file, copy the below contents into a file named `options.yaml`

  ```(yaml)
  options:
  inputMappings:
  - fieldName: Authorization
    location: HEADER
    value: >
      $.concat("Bearer ", $.googleOauth2AccessToken())
  ```

- Create a type-provider name `cloudtasks` by executing the below command

  ```(shell)
  $ gcloud beta deployment-manager type-providers create cloudtasks \
        --api-options-file=options.yaml \
        --descriptor-url "https://cloudtasks.googleapis.com/\$discovery/rest?version=v2beta3"

    Waiting for insert [operation-asdfewerwertf-....]...done.
    Created type_provider [cloudtasks].
  ```

- Verify that the type-provider is created successfully

  ```(shell)
  $ gcloud beta deployment-manager type-providers list

  NAME          INSERT_DATE
  cloudtasks    201xx-yy-zz
  ```

## Deployment

### Resources

- [projects.locations.queues](https://cloud.google.com/tasks/docs/reference/rest/v2beta3/projects.locations.queues)
- [projects.locations.queues.tasks](https://cloud.google.com/tasks/docs/reference/rest/v2beta3/projects.locations.queues.tasks)
- [Task Queues](https://cloud.google.com/appengine/docs/standard/python/taskqueue/)
- [CloudTasks v2beta3 Descriptor URL](https://cloudtasks.googleapis.com/$discovery/rest?version=v2beta3)

### Properties

See the `properties` section in the schema file(s):

- [CloudTasks Queue schema](queue.py.schema)
- [CloudTasks Task schema](task.py.schema)

### Usage

1. Clone the [Deployment Manager samples repository](https://github.com/GoogleCloudPlatform/deploymentmanager-samples)

   ```shell
   git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
   ```

2. Go to the [community/cloud-foundation](../../) directory

   ```shell
   cd community/cloud-foundation
   ```

3. Copy the example DM config to be used as a model for the deployment, in this case [examples/cloud\_tasks\_queue.yaml](examples/cloud_tasks_queue.yaml)

   ```shell
   cp templates/cloud_tasks/examples/cloud_tasks_queue.yaml my_cloud_tasks_queue.yaml
   ```

4. Change the values in the config file to match your specific GCP setup.
   Refer to the properties in the schema files described above.

   ```shell
   vim my_cloud_tasks_queue.yaml
   ```

5. Create your deployment as described below, replacing `<YOUR_DEPLOYMENT_NAME>`
   with your with your own deployment name

   ```shell
   gcloud beta deployment-manager deployments create <YOUR_DEPLOYMENT_NAME> \
       --config my_cloud_tasks_queue.yaml
   ```

6. In case you need to delete your deployment:

   ```shell
   gcloud deployment-manager deployments delete <YOUR_DEPLOYMENT_NAME>
   ```

## Examples

- [CloudTasks Queue](examples/cloud_tasks_queue.yaml)
- [CloudTasks Task](examples/cloud_tasks_task.yaml)
