# Cloud Foundation Toolkit

User Guide
<!-- TOC -->

- [Overview](#overview)
    - [Dependency Resolution](#dependency-resolution)
    - [Cross-deployment References](#cross-deployment-references)
- [CFT-compliant Configs](#cft-compliant-configs)
    - [Principles](#principles)
    - [Samples](#samples)
        - [network.yaml](#networkyaml)
        - [firewall.yaml](#firewallyaml)
        - [instance.yaml](#instanceyaml)
- [Templates](#templates)
- [Toolkit Installation and Configuration](#toolkit-installation-and-configuration)
    - [Installation](#installation)
    - [Package Addition/Update](#package-additionupdate)
    - [Test Configuration](#test-configuration)
- [CLI Usage](#cli-usage)
    - [Syntax](#syntax)
    - [The "create" Action](#the-create-action)
    - [The "update" action](#the-update-action)
    - [The "apply" action](#the-apply-action)
    - [The "delete" action](#the-delete-action)
- [Notes for Developers](#notes-for-developers)

<!-- /TOC -->

## Overview

The Cloud Foundation toolkit (henceforth, CFT) expands the capabilities of Google's Deployment Manager and gcloud to support the following scenarios:

- Creation, update, and deletion of multiple deployments in a single operation that:
  - Accepts multiple config files as input
  - Automatically resolves dependencies between these configs
  - Creates or updates deployments in the dependency-stipulated order, or deletes deployments in the reverse dependency order
- Cross-deployment (including cross-project) referencing of deployment outputs, which obviates the need for hard-coding many parameters in the configs

`Note:` This User Guide assumes that you are familiar with the Google Cloud SDK operations related to resource deployment and management. For additional information, refer to the [SDK documentation](https://cloud.google.com/sdk/docs/).

The CFT includes:

- A command-line interface (henceforth, CLI) that deploys resources defined in single or multiple CFT-compliant config files
- A comprehensive set of production-ready resource templates that follow Google's best practices, to be imported by CFT-compliant config files

`Note:` The CFT does not support gcloud-standard config files. For details on config enhancements required to ensure CFT compliance, see the [CFT-compliant Configs](#cft-compliant-configs) section below.

### Dependency Resolution

Deployment Manger does not support ordering of deployments and inter-deployment dependencies. For example, if config file A contains all resources for networking, config file B contains all instances, and config C contains firewall rules, router, and VPN, you will need to manually define the config deployment order according to the resource dependencies. For example, a VPN would depend on a cloud router, both of them would depend on a network, etc. The CFT computes the dependencies automatically, which eliminates the need for manual deployment ordering.

`Note:` The current version of the CFT does not support updates to upstream dependencies of an updated resource. For example, if an update to a VPN bound to a cloud router removes that cloud router, the CFT will not remove the VPN prior to the cloud router's removal. As a result, the update will fail.

### Cross-deployment References

The CFT supports cross-deployment (including cross-project) references by *** need an explanation... **or NOT**. We need to decide whether the readers need to understand how things work "under the hood", or just enjoy the fact that the things do work ***.

## CFT-compliant Configs

### Principles

To use the CFT, you need to first create the config files for the desired deployments. To support the expanded capabilities of the CFT (multi-config deployment and cross-deployment references), every config file must include the following components, which are not found in gcloud-standard configs:

- The resource name that includes the environment. For example:

```yaml
    name: my-firewall-{{environment}}
```

- The resource description *** is this really a "must have"? Is it technically mandatory? ***. For example:

```yaml
    description: My firewall deployment for {{environment}} environment
```

- The project in which the resource is deployed. For example:

```yaml
    project: my-project
```

- Support for cross-deployment references via the `$(out)` tag:

```yaml
    $(out.<deployment-name>.<resource-name>.<output-name>)  
```

wherein:

- `$(out)` is the prefix that indicates the value is referencing an output from a resource defined in an external deployment (in another config file)
- `deployment-name` is the he name of the external deployment (config) that defines the referenced resource
- `resource-name` is the DM name of the referenced resource
- `output-name` is the name of the output parameter to be referenced

For example:

```yaml
    network: $(out.my-network-prod.my-network-prod.name)
```

### Samples

Following are three sample config files that illustrate the above principles, and that will be used as examples in the action-specific sections of this User Guide:

- [network.yaml](#network.yaml) - two networks, which have no dependencies
- [firewall.yaml](#firewall.yaml) - two firewall rules, which depend on the corresponding networks
- [instance.yaml](#instance.yaml) - one VM instance, which depends on the network

*** I understand that the "sample" config changed. However, before I replace the "old" ones with the "current" ones in the text below, can you tell me that the "current" are final - at least for the initial CFT/UG release?  ***

#### network.yaml

```yaml
{% set environment = 'prod' %}
name: my-network-{{environment}}
description: my network deployment for {{environment}} environment
project: mytestproject-vpun-test1

imports:
  - path: templates/network/network.py
resources:
  - type: templates/network/network.py
    name: my-network-{{environment}}
    properties:
      autoCreateSubnetworks: true

  - type: templates/network/network.py
    name: my-network-dev
    properties:
      autoCreateSubnetworks: false
```

#### firewall.yaml

```yaml
{% set environment = 'prod' %}
name: my-firewall-{{environment}}
description: My firewall deployment for {{environment}} environment
project: mytestproject-vpun-test1

imports:
  - path: templates/firewall/firewall.py
resources:
  - type: templates/firewall/firewall.py
    name: my-firewall-{{environment}}
    properties:
      network: !DMOutput dm://mytestproject-vpun-test1/my-network-{{environment}}/my-network-prod/name
      rules:
        - name: allow-proxy-from-inside-prod
          allowed:
            - IPProtocol: tcp
              ports:
                - "80"
                - "444"
          description: This rule allows connectivity to the HTTP proxies
          direction: INGRESS
          sourceRanges:
            - 10.0.0.0/8
        - name: allow-dns-from-inside-prod
          allowed:
            - IPProtocol: udp
              ports:
                - "53"
            - IPProtocol: tcp
              ports:
                - "53"
          description: this rule allows DNS queries to google's 8.8.8.8
          direction: EGRESS
          destinationRanges:
            - 8.8.8.8/32
  - type: templates/firewall/firewall.py
    name: my-firewall-dev
    properties:
      network: !DMOutput dm://mytestproject-vpun-test1/my-network-{{environment}}/my-network-dev/name
      rules:
        - name: allow-proxy-from-inside-dev
          allowed:
            - IPProtocol: tcp
              ports:
                - "80"
                - "444"
          description: This rule allows connectivity to the HTTP proxies
          direction: INGRESS
          sourceRanges:
            - 10.0.0.0/8
```

#### instance.yaml

```yaml
{% set environment = 'prod' %}
name: my-instance-{{environment}}
description: My instance deployment for {{environment}} environment
project: mytestproject-vpun-test1

imports:
  - path: templates/instance/instance.py
    name: instance.py

resources:
  - name: test-instance
    type: instance.py
    properties:
      zone: us-central1-a
      diskImage: projects/ubuntu-os-cloud/global/images/family/ubuntu-1804-lts
      diskSizeGb: 100
      machineType: f1-micro
      diskType: pd-ssd
      network: !DMOutput dm://mytestproject-vpun-test1/my-network-{{environment}}/my-network-prod/name
      metadata:
        items:
          - key: startup-script
            value: sudo apt-get update && sudo apt-get install -y nginx
```

## Templates

CFT-compliant configs can use templates written in Python or Jinja2. Templates included in the toolkit are recommended (although not mandatory) as they offer robust functionality, ease of use, and adherence to best practices:

- [autoscaler](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/autoscaler)
- [backend_service](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/backend_service)
- [bigquery](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/bigquery)
- [cloud_function](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/cloud_function)
- [cloud_router](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/cloud_router)
- [dns_managed_zone](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/dns_managed_zone)
- [dns_records](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/dns_records)
- [firewall](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/firewall)
- [folder](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/folder)
- [forwarding_rule](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/forwarding_rule)
- [gcs_bucket](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/gcs_bucket)
- [gke](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/gke)
- [haproxy](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/haproxy)
- [healthcheck](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/healthcheck)
- [iam_custom_role](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/iam_custom_role)
- [iam_member](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/iam_member)
- [instance](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/instance)
- [instance_template](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/instance_template)
- [ip_reservation](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/ip_reservation)
- [logsink](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/logsink)
- [network](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/network)
- [org_policy](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/org_policy)
- [project](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/project)
- [pubsub](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/pubsub)
- [route](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/route)
- [shared_vpc_subnet_iam](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/shared_vpc_subnet_iam)
- [vpn](https://github.com/GoogleCloudPlatform/deploymentmanager-samples/tree/cloud-foundation/community/cloud-foundation/templates/vpn)

## Toolkit Installation and Configuration

*** Please check this section. I tried to simplify Gus's instructions without losing info/meaning - might have made mistakes. ***

### Installation

To install the CFT, proceed as follows:

1. Install the [Google Cloud SDK for Linux or Debian/Ubuntu](https://cloud.google.com/sdk/?utm_source=google&utm_medium=cpc&utm_campaign=na-CA-all-en-dr-skws-all-all-trial-p-dr-1003905&utm_content=text-ad-none-any-DEV_c-CRE_293764940066-ADGP_Hybrid+%7C+AW+SEM+%7C+SKWS+%7C+CA+%7C+en+%7C+PHR+%7E+Developer+Tools+%7E+Cloud+SDK+%7E+Cloud+Sdk-KWID_43700036673591779-kwd-341391008142&utm_term=KW_cloud%20sdk-ST_cloud+sdk&gclid=EAIaIQobChMIjvbopt_i3QIVAY9pCh0jvQt1EAAYASAAEgI37_D_BwE&dclid=CP_Epanf4t0CFVArTwod13MLBg).
2. Ensure that the `gcloud` command is in the user's PATH.
3. Install the CFT prerequisites' package, in the Linux/Ubuntu terminal enter:

```shell
    sudo make cft-prerequisites
```

4. To create a virtual environment, called **venv**, with [tox](https://tox.readthedocs.io/en/latest/index.html) in the root of the project directory, in the Linux/Ubuntu terminal enter:

```shell
    make cft-venv
```

5. To activate the virtual environment, in the Linux/Ubuntu terminal enter:

```shell
    source venv/bin/activate
    source src/cftenv
```

The above commands activate the VE, then find the Google SDK path, and add the required libraries to PYTHONPATH.

`Note:` **tox.ini** in this project is configured to "install" the utility using pip's "develop" mode; i.e., the pip does not actually package and install the utility in the virtual environment's site-packages. *** sounds convoluted... can we rephrase? do we need this note at all? ***

### Package Addition/Update

To install or update packages, delete and re-create the virtual environment:

```shell
    deactivate
    unset CLOUDSDK_ROOT_DIR CLOUDSDK_PYTHON_SITEPACKAGES PYTHONPATH
    make cft-clean-ven
```

### Test Configuration

1. To run all tests from outside the development environment:

```shell
    make cft-test  
```

2. Alternatively, to run all tests within the development environment:

```shell
    # Use the make target to run all tests:
    make cft-test-venv

    # Alternatively, use pytest directly to run all tests:
    python -m pytest -v

    # Alternatively, run a single test file:
    python -m pytest -v tests/unit/test_deployment.py
```

## CLI Usage

### Syntax

The CLI commands adhere to the following syntax:

```shell
    cft [action] [config files] [options]
```

The above syntactic structure includes the following elements:

- `[action]` - one of the supported actions/commands:
  - **create** - creates deployments defined in the specified config files, in the dependency order
  - **update** - updates deployments defined in the specified config files, in the dependency order
  - **apply** - checks if the resources defined in the specified configs already exist; if they do, updates them; if they don't, creates them
  - **delete** - deletes deployments defined in the specified config files, in the reverse dependency order
- `[config files]` - an arbitrary number of config files to be affected by the specified action. The files can be specified in one of the following ways (or by combining these ways):
  - a space-separated list of the actual file names, optionally with wildcards; e.g., config_1.yaml config_2.yaml test*.yaml *** no path/directory required? ***
  - a directory that contains the files; e.g., ../infra1/configs; all .yaml, .yml, and .jinja2 files found in the specified directory are selected
- `options` - one or more action-specific options:
  - -**h** (or --**help**) - displays the help content either for the entire CFT (cft --help) or for a specific action (cft [action] --help)
  - --**project** - the name of the GCP project to perform actions in
  - -**v** (or --**verbosity**) - the log level *** what are the possible values? what does each mean? ***
  - --**dry-run** - *** what will it do? ***; pending implementation
  - -**p** (--**preview**) - displays the required changes (action results) without committing them to Deployment Manager (for the **apply** action only)
  - -**r** (or --**reverse**) - applies changes in the reverse dependency-defined order (for the **apply** action only)

### The "create" Action

`Note:` Make sure that the deployments you are going to create do not exist in your environment. An attempt to create a deployment that already exists will result in an error. Yon can, however, do one of the following:

- Use the **update** action to update the existing deployments - see [The "update" Action](#the-update-action) section
- Use the **apply** action to let the CFT decide which deployments must be created (because they do not exist), and which ones must be updated (because they do exist) - see [The "apply" Action](#the-apply-action) section

To create multiple deployments, in the CLI, type:

```shell
    cft create [config files] [options]
```

The CFT parses the submitted config files and computes the dependencies between them. Based on the computed dependency graph, the CFT determines the sequence of deployments to be created. It then proceeds to sequentially deploy the configs.  

For example, if you submitted the [sample configs described above](#samples):

```shell
    cft create instance.yaml firewall.yaml network.yaml
    # or
    cft create tests/fixtures/configs
```

the network would have no dependencies, and the firewall and instance would depend on the network. Therefore, the network would be deployed first (Stage 1), and the firewall and instance would be deployed next (Stage 2). The following would be displayed in the terminal:

```shell
    ---------- Stage 1 ----------
    Waiting for insert my-network-prod (fingerprint 7OyDHEL8-ZGbay4dTcXXEg==) [operation-1538159159516-576f2964f9b61-e64bdb44-8ab51124]...done.
    NAME             TYPE                STATE      ERRORS  INTENT
    my-network-dev   compute.v1.network  COMPLETED  []
    my-network-prod  compute.v1.network  COMPLETED  []
    ---------- Stage 2 ----------
    Waiting for insert my-instance-prod-1 (fingerprint tdbkal-dX_ppamFJVtBGew==) [operation-1538159204094-576f298f7d030-9707b687-a3f822d9]...done.
    NAME                TYPE                 STATE      ERRORS  INTENT
    my-instance-prod-1  compute.v1.instance  COMPLETED  []
    Waiting for insert my-firewall-prod (fingerprint Yuhd7khES_en86QtLYFV8w==) [operation-1538159238360-576f29b02abc2-b29dacc3-1b74eb12]...done.
    NAME                          TYPE                   STATE      ERRORS  INTENT
    allow-dns-from-inside-prod    compute.beta.firewall  COMPLETED  []
    allow-proxy-from-inside-dev   compute.beta.firewall  COMPLETED  []
    allow-proxy-from-inside-prod  compute.beta.firewall  COMPLETED  []
    ---------- Stage 3 ----------
    Waiting for insert my-instance-prod-2 (fingerprint z-lJJimsanFI6cIYLU8D_w==) [operation-1538159270905-576f29cf344a8-d28b6852-52527e20]...done.
    NAME                TYPE                 STATE      ERRORS  INTENT
    my-instance-prod-2  compute.v1.instance  COMPLETED  []
```

*** Not sure where we got 2 instances - the instance.yaml file had only 1... Also, not sure why my-instance-prod-1 is deployed in Stage 2, and my-instance-prod-2 is deployed in Stage 3 ***

*** Do we want to tell the reader that they should check the results/logs/whatever else? ***

The following conditions will result in the actin failure, with an error message displayed:

- One or more of the specified deployments already exist
- One or more of the submitted config files are invalid
- One or more of the submitted config files contain circular dependencies (i.e., deployment A depends on deployment B, and B depends on A)

### The "update" action

`Note:` Make sure that the deployments you are going to update already exist in your environment. An attempt to update deployment that does not exist will result in an error. Yon can, however, do one of the following:

- Use the **create** action to create the required deployments - see [The "create" action](#the-create-action) section
- Use the **apply** action to let the CFT decide which deployments must be created (because they do not exist), and which ones must be updated (because they do exist) - see [The "apply" action](#the-apply-action) section

To update multiple configs, in the CLI, type:

```shell
    cft update [config files] [options]
```

The CFT parses the submitted config files and computes the dependencies between them. Based on the computed dependency graph, the CFT determines the sequence of deployments to be created. It then proceeds to sequentially deploy the configs. 

For example, if you submitted the three [sample configs described above](#samples):

```shell
    cft update instance.yaml firewall.yaml network.yaml
    # or
    cft update tests/fixtures/configs
```

the networks would have no dependencies, and the firewall and instances would depend on the network. Therefore, the network would be updated first (Stage 1), and the firewall and instance would be updated next (Stage 2). The following would be displayed in the terminal:

```shell
    ---------- Stage 1 ----------
    Waiting for update my-network-prod (fingerprint 7OyDHEL8-ZGbay4dTcXXEg==) [operation-1538159159516-576f2964f9b61-e64bdb44-8ab51124]...done.
    NAME             TYPE                STATE      ERRORS  INTENT
    my-network-dev   compute.v1.network  COMPLETED  []
    my-network-prod  compute.v1.network  COMPLETED  []
    ---------- Stage 2 ----------
    Waiting for update my-instance-prod-1 (fingerprint tdbkal-dX_ppamFJVtBGew==) [operation-1538159204094-576f298f7d030-9707b687-a3f822d9]...done.
    NAME                TYPE                 STATE      ERRORS  INTENT
    my-instance-prod-1  compute.v1.instance  COMPLETED  []
    Waiting for update my-firewall-prod (fingerprint Yuhd7khES_en86QtLYFV8w==) [operation-1538159238360-576f29b02abc2-b29dacc3-1b74eb12]...done.
    NAME                          TYPE                   STATE      ERRORS  INTENT
    allow-dns-from-inside-prod    compute.beta.firewall  COMPLETED  []
    allow-proxy-from-inside-dev   compute.beta.firewall  COMPLETED  []
    allow-proxy-from-inside-prod  compute.beta.firewall  COMPLETED  []
    ---------- Stage 3 ----------
    Waiting for update my-instance-prod-2 (fingerprint z-lJJimsanFI6cIYLU8D_w==) [operation-1538159270905-576f29cf344a8-d28b6852-52527e20]...done.
    NAME                TYPE                 STATE      ERRORS  INTENT
    my-instance-prod-2  compute.v1.instance  COMPLETED  []
```

*** Same questions / concerns as described in the **create** section ***

The following conditions will result in the actin failure, with an error message displayed:

- One or more of the specified deployments do not exist
- One or more of the submitted config files are invalid
- One or more of the submitted config files contain circular dependencies (i.e., deployment A depends on deployment B, and B depends on A)

### The "apply" action

The **apply** action makes the CFT decide which deployments must be created (because they do not exist), and which ones must be updated (because they do exist).

To apply (create **or** update) multiple configs, proceed as follows:

1. In the CLI, type:

```shell
    cft apply [config files] [options]
```

The CFT parses the submitted config files and: (a) determines whether deployments corresponding to these configs already exist in the environment; and (b) computes the dependencies between the configs. Based on the computed dependency graph, the CFT determines the sequence of deployments to be created or updated. It then proceeds to sequentially deploy the configs.  

For example, if you submitted the three [sample configs described above](#samples):

```shell
    cft apply instance.yaml firewall.yaml network.yaml
    # or
    cft apply tests/fixtures/configs
```

the network would have no dependencies, and the firewall and instance would depend on the network. Therefore, the network would be created/updated first (Stage 1), and the firewall and instance would be created/updated next (Stage 2). The following would be displayed in the terminal:

```shell
    *** TBD ***
```

*** Same questions / concerns as described in the **create** section ***

The following conditions will result in the actin failure, with an error message displayed:

- One or more of the submitted config files are invalid
- One or more of the submitted config files contain circular dependencies (i.e., deployment A depends on deployment B, and B depends on A)
- *** Anything else? ***

If you use the --**preview** option

```shell
    cft apply test/fixtures/configs/ --preview
```

the CFT does not automatically submit the creation/update request to Deployment Manager. Instead, it displays a preview of the action results and enables you to approve/decline the action for each of the submitted configs. The following prompt is displayed after Stage 1 log:

  ```shell
    ---------- Stage 1 ----------
    Waiting for preview my-network-prod (fingerprint 3fro0c2OmnBx2HhX2V421Q==) [operation-1538165828379-576f423ce6178-3612bbd1-52600977]...done.
    NAME             TYPE                STATE      ERRORS  INTENT
    my-network-dev   compute.v1.network  COMPLETED  []
    my-network-prod  compute.v1.network  COMPLETED  []
    Update(u), Skip (s), or Abort(a) Deployment?
  ```

2. Having reviewed the displayed information, enter one of the following responses:

- **u<pdate>** - create/update the config as shown in the preview
- **s<kip>** - skip (do not create/update) the config; consider the next config in the sequence
- **a<bort>** - cancel the entire action (deployment run)

If you entered **u**, *** what appears on the screen? what does the user need to do, if anything? ***

If you entered **s**, the CFT re-computes the dependency graph without the skipped (excluded) config. *** what appears on the screen? what does the user need to do, if anything? what happens if the user "skips" a deployment on which downstream deployment depend? E.g., skips network in Stage 1 on which everything in Stages 2 and 3 depend? ***

If you entered **a**, *** what appears on the screen? what does the user need to do, if anything? ***  

### The "delete" action

To delete the previously created/updated multiple deployments, in the CLI, type:

```shell
    cft delete [config files] [options]
```

The CFT parses the submitted config files and computes the dependencies between them. Based on the computed dependency graph, the CFT determines the order of deployments to be deleted (the reverse from the creation order). It then proceeds to sequentially delete the deployments.  

For example, if you submitted the three [sample configs described above](#samples):

```shell
    cft delete instance.yaml firewall.yaml network.yaml
    # or
    cft delete tests/fixtures/configs
```

the network would have no dependencies, and the firewall and instance would depend on the network. Therefore, the firewall and instance would be deleted first (Stage 1), and the network would be deleted next (Stage 2). The following would be displayed in the terminal:

```shell
    ---------- Stage 1 ----------
    Waiting for delete my-instance-prod-2 (fingerprint 3IWMMfbjsUWjtWgvs6Evdw==) [operation-1538159406282-576f2a504f510-2dceed8f-b222b564]...done.
    ---------- Stage 2 ----------
    Waiting for delete my-instance-prod-1 (fingerprint ifQgUyTSOtVE1H6VgaIlYA==) [operation-1538159505990-576f2aaf66170-fcc5246d-2d44d005]...done.
    Waiting for delete my-firewall-prod (fingerprint xFs1fcZiLJPVV1hUw61-og==) [operation-1538159629835-576f2b2581af9-a83468de-d3685d90]...done.
    ---------- Stage 3 ----------
    Waiting for delete my-network-prod (fingerprint EhMN6C5IeADJYRo40CmuAg==) [operation-1538159649120-576f2b37e5f02-35da3a44-cf279bfa]...done.
```

*** Same questions / concerns as described in the **create** section ***

The following conditions will result in the actin failure, with an error message displayed:

- One or more of the specified deployments do not exist
- One or more of the submitted config files are invalid
- One or more of the submitted config files contain circular dependencies (i.e., deployment A depends on deployment B, and B depends on A)

## Notes for Developers

*** Here we should put notes for those folks who are going to treat the CFT as open-source code base - to modify and adapt to their own needs. I.e., what files are included in the code base, what each one is for, etc. Probably one or two "adaptation" scenarios - i.e., what developers can change to achieve a goal they are likely to have. The info here is going to be complemented by inline comments in the code (.py files). ***