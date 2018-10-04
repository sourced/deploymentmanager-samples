# Cloud Foundation Toolkit

User Guide
<!-- TOC -->

- [Overview](#overview)
    - [ Deployment Pipelining](#deployment-pipelining)
- [CFT Configs](#cft-configs)
    - [Principles](#principles)
    - [Samples](#samples)
        - [network.yaml](#networkyaml)
        - [firewall.yaml](#firewallyaml)
        - [instance.yaml](#instanceyaml)
- [Templates](#templates)
- [Toolkit Installation and Configuration](#toolkit-installation-and-configuration)
- [CLI Usage](#cli-usage)
    - [Syntax](#syntax)
    - [The "create" Action](#the-create-action)
    - [The "update" Action](#the-update-action)
    - [The "apply" Action](#the-apply-action)
    - [The "delete" Action](#the-delete-action)

<!-- /TOC -->

## Overview

The Cloud Foundation toolkit (henceforth, CFT) expands the capabilities of
Google's Deployment Manager and gcloud to support the following scenarios:

- Creation, update, and deletion of multiple deployments in a single operation
  that:
  - Accepts multiple config files as input
  - Automatically resolves dependencies between these configs
  - Creates or updates deployments in the dependency-stipulated order, or
    deletes deployments in the reverse dependency order
- Cross-deployment (including cross-project) referencing of deployment outputs,
  which obviates the need for hard-coding many parameters in the configs

`Note:` This User Guide assumes that you are familiar with the Google Cloud SDK
operations related to resource deployment and management. For additional
information, refer to the [SDK documentation](https://cloud.google.com/sdk/docs/).

The CFT includes:

- A command-line interface (henceforth, CLI) that deploys resources defined in
  single or multiple CFT-compliant config files
- A comprehensive set of production-ready resource templates that follow
  Google's best practices, that can be used with CFT or `gcloud` utility, which
  is part of the Google Cloud SDK

`Note:` The CFT does not support gcloud-standard config files. For details on
config enhancements required to ensure CFT compliance, see the
[CFT Configs](#cft-configs) section below.

### Deployment Pipelining 

Since GCP's Deployment Manager service does not support references between
deployments, and the `gcloud` utility does not support multiple, concurrent
deployments that have interdependecies between them, currently there's no
simple way of pipelining deployments together without writing quite a bit of
 custom code to overcome these limitations. This is where CFT can help.

For example, if config file `A` contains network resources, config file `B`
contains all instances, and config `C` contains firewall rules, router, and VPN,
you will need to *manually* define the config deployment order according to the
resource dependencies. For example, a VPN would depend on a cloud router, both
of them would depend on a network, etc. The CFT computes the dependencies
automatically, which eliminates the need for manual deployment ordering.

## CFT Configs

### Principles

To use the CFT CLI, you need to first create the config files for the desired
deployments. These configs are YAML structures that look very much like `gcloud`
config files, but to support the expanded capabilities of the CFT (multi-config
deployment and cross-deployment references), extra YAML directives and pieces
of functionality are implementedL

####  Mandatory Directives

Every config file must include at least these directives:

- `name` directive, which are not found in gcloud-standard configs::

  ```yaml
      name: my-firewall-prod
  ```

#### Optional Directives

CFT configs also supports for these optional directives:

- `project`: defines the project in which the resource is deployed. For example:

  ```yaml
      project: my-project
  ```

  Notice that while this directive is optional, it's highly recommended that it's
  specified in your configs. If not specified in the config, the CFT utility will
  lookup the project in the `CLOUD_FOUNDATION_TOOLKIT_PROJECT_ID` environment
  variable. And if this variable is not defined, the default project configured with
  the GCP SDK will be used. The `project` directive in the config always takes
  precedence.

  When different deployments have cross-project resources, this field will become
  mandatory in at least one of the deployments.

- `description`: The deployment description. Optional field that allows users
  to add some documentation to their configs.

  ```yaml
      description: My firewall deployment for {{environment}} environment
  ```

  Documentation is good. It's also recommended that this field is used.

#### Extra Features

##### Cross-deployment references via the `$(out)` tag:

```yaml
    $(out.<project>.<deployment>.<resource>.<output>)

# or
    
    $(out.<deployment>.<resource>.<output>)
```

wherein:

- `$(out)` is the prefix that indicates the value is referencing an output from
  a resource defined in an external deployment (in another config file)
- `project` is the ID of the project in which the external deployment is
   created
- `deployment` is the he name of the external deployment (config) that
  defines the referenced resource
- `resource` is the DM name of the referenced resource
- `output` is the name of the output parameter to be referenced

A config can specify a dependency on another deployment's output without the
user having to create the dependent deployment in advance. This is the
mechanism CFT uses to determine the order of execution of the deployments.

This construct works very similarly to DM's `$(ref.<resource>.<property>)`, but
instead of only defining references to resource properties *within* a
deployment, it allows for *inter-deployment/inter-project* references via
deployment outputs. The value of output of a dependent deployment is only
looked up during the current deployment's execution, which allows users to
create config files without knowing in advance the actual values of the
outputs of dependent deployments, or even having to create them.

For example:

```yaml
    network: $(out.my-network-prod.my-network-prod.name)
```

##### Jinja Templating

Any config provided to CFT CLI will be rendered by the [Jinja Template
Engine](http://jinja.pocoo.org/).

This allows for compact code by using a DRY pattern. For example, using a
variable substitution and `for loops`: 

```yaml
{% set environment = 'prod' %}
{% set applications = ['app1', 'app2', 'app3'] %}

name: my-network-{{environment}}
description: Network deployment for {{environment}} environment
project: sourced-gus-1
imports:
  - path: templates/network/network.py
resources:
{% for application in applications %}
  - type: templates/network/network.py
    name: {{application}}-{{environment}}-network
    properties:
      autoCreateSubnetworks: false
{% endfor %}
```

Notice that an alternative to using Jinja in your configs is to write wrapper DM
Python templates and referencing these templates in your configs.


### Samples

Following are three sample config files that illustrate the above principles,
and that will be used as examples in the action-specific sections of this
User Guide:

- [network.yaml](#network.yaml) - two networks, which have no dependencies
- [firewall.yaml](#firewall.yaml) - two firewall rules, which depend on the corresponding networks
- [instance.yaml](#instance.yaml) - one VM instance, which depends on the network


#### network.yaml

```yaml
name: my-networks
description: my networks deployment

imports:
  - path: templates/network/network.py

resources:
  - type: templates/network/network.py
    name: my-network-prod
    properties:
      autoCreateSubnetworks: true

  - type: templates/network/network.py
    name: my-network-dev
    properties:
      autoCreateSubnetworks: false
```

#### firewall.yaml

```yaml
name: my-firewall-prod
description: My firewalls deployment

imports:
  - path: templates/firewall/firewall.py
resources:
  - type: templates/firewall/firewall.py
    name: my-firewall-prod
    properties:
      network: $(out.my-networks.my-network-prod.name)
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
      network: $(out.my-networks.my-network-dev.name)
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
me: my-instance-prod-1
description: My instance deployment for prod environment

imports:
  - path: templates/instance/instance.py
    name: instance.py

resources:
  - name: my-instance-prod-1
    type: instance.py
    properties:
      zone: us-central1-a
      diskImage: projects/ubuntu-os-cloud/global/images/family/ubuntu-1804-lts
      diskSizeGb: 100
      machineType: f1-micro
      diskType: pd-ssd
      network: $(out.my-networks.my-network-prod.name)
      metadata:
        items:
          - key: startup-script
            value: sudo apt-get update && sudo apt-get install -y nginx
```

## Templates

CFT-compliant configs can use templates written in Python or Jinja2. [Templates
included in the toolkit](../templates) are recommended (although not mandatory) as they offer
robust functionality, ease of use, and adherence to best practice.


## Toolkit Installation and Configuration

This toolkit is developed primarily on Linux, therefore this is the platform
with the most seamless experience expected.

### Installation

#### Installing Pre Requisites

- Python 2.7. Follow your OS package manager instructions to install Python
  ```shell
      sudo apt-get install python2.7
  ```

- Google Cloud SDK
  1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/quickstarts).
  2. Ensure that the `gcloud` command is in the user's PATH:
     ```shell
         which gcloud
     ```

#### Getting the CFT the Code

```shell
    git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples
    cd deploymentmanager-samples/
    git checkout cloud-foundation  # CFT is in a branch for now
```

#### Install the CFT tool

```shell
    cd community/cloud-foundation
    make build                     # builds the package 
    sudo make install              # installs the package in /usr/local
```

#### Uninstall the CFT tool

```shell
    make uninstall
```

#### Reinstall
```shell
    make clean
    make install
```


## CLI Usage

### Syntax

The CLI commands adhere to the following syntax:

```shell
    cft [action] [configs] [action-options]
```

The above syntactic structure includes the following elements:

- `[action]` - one of the supported actions/commands:
  - **create** - creates deployments defined in the specified config files, in the dependency order
  - **update** - updates deployments defined in the specified config files, in the dependency order
  - **apply** - checks if the resources defined in the specified configs already exist; if they do, updates them; if they don't, creates them
  - **delete** - deletes deployments defined in the specified config files, in the reverse dependency order
- `[config]` - The path(s) to the config files to be affected by the specified
  action. [config] can be:
    - The path to directory containing config files with extensions `.yaml`,
      `.yaml`, or `.jinja`
    - A space-separated list of paths to the config files
    - A space-separated list of yaml-serialized strings, each representing a
      config. Useful when another tool is generating the configs on the fly.
      For example: `name: my-networks\nproject: my-project\nimports:\n  - path: templates/network/network.py\n    name: network.py\resources:\n  - type: templates/network/network.py\n    name: my-network-prod`
- `action-options` - one or more action-specific options. See `--help` option
  on the action for more details

```shell
cft --help
usage: Cloud Foundation Toolkit [-h] [--project PROJECT] [--dry-run]
                                [--verbosity VERBOSITY]
                                {apply,create,update,delete} ...

positional arguments:
  {apply,create,update,delete}

optional arguments:
  -h, --help            show this help message and exit
  --project PROJECT     The GCP project name
  --dry-run             Not implemented yet
  --verbosity VERBOSITY, -v VERBOSITY
                        The log level
```

### Actions

The `cft` command parses the submitted config files and computes the
dependencies between them. Based on the computed dependency graph, the script
determines the sequence of deployments to be executed. It then proceeds to
execute the action in the computed order.


#### The "create" Action

`Note:` Make sure that the deployments you are going to create do not exist in
your DM. An attempt to create a deployment that already exists will result in
an error. Yon can, however, do one of the following:

- Use the **update** action to update the existing deployments - see
  [The "update" Action](#the-update-action) section
- Use the **apply** action which will attempt to create the deployment if it
  doesn't already exist in DM, or update the deployment it already exist - see
  [The "apply" action](#the-apply-action) section

To create multiple deployments, in the CLI, type:

```shell
    cft create [configs] [create-options]
```


For example, if you submitted the [sample configs described above](#samples):

```shell
    cft create instance.yaml firewall.yaml network.yaml

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

In this example, the network config would have no dependencies, and the
firewall and instance configs would depend on the network. Therefore, the
network config would be deployed first (Stage 1), and the firewall and instance
would be deployed next (Stage 2).

Notice the order in which the configs are provided in the `cft create` command
has no signficance on the order of execution of the configs, which is always
resolved based on the depedency graph between the configs, that in its turn
constructed by analyzing and ordering the cross-dependency tokens
(`$(out.a.b.c.d)`)

The following conditions will result in the action failure,
with an error message displayed:

- One or more of the specified deployments already exist
- One or more of the submitted config files are invalid
- One or more of the submitted config files contain circular dependencies
  (i.e., deployment A depends on deployment B, and B depends on A)

### The "update" Action

`Note:` Make sure that the deployments you are going to update already exist in
DM. An attempt to update deployment that does not exist will result in an
error. Yon can, however, do one of the following:

- Use the **create** action to create the required deployments - see
  [The "create" action](#the-create-action) section
- Use the **apply** action which will attempt to create the deployment if it
  doesn't already exist in DM, or update the deployment it already exist - see
  [The "apply" action](#the-apply-action) section

To update multiple configs, in the CLI, type:

```shell
    cft update [configs] [create-options]
```

For example, if you submitted the three [sample configs described above](#samples):

```shell
    cft update instance.yaml firewall.yaml network.yaml

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
As in the case with `create`, the network config would have no dependencies,
and the firewall and instance configs would depend on the network. Therefore,
the network config would be updated first (Stage 1), and the firewall and
instance would be updated next (Stage 2).

The following conditions will result in the actin failure, with an error message displayed:

- One or more of the specified deployments do not exist
- One or more of the submitted config files are invalid
- One or more of the submitted config files contain circular dependencies
  (i.e., deployment A depends on deployment B, and B depends on A)

### The "apply" Action

The **apply** action makes the CFT decide which deployments must be created
(because they do not exist), and which ones must be updated (because they do
exist).

To create or update multiple configs, in the CLI, type:

```shell
    cft apply [configs] [create-options]
```

For example, if you submitted the three [sample configs described above](#samples):

```shell
    cft apply instance.yaml firewall.yaml network.yaml

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

The following conditions will result in the actin failure, with an error
message displayed:

- One or more of the submitted config files are invalid
- One or more of the submitted config files contain circular dependencies
(i.e., deployment A depends on deployment B, and B depends on A)

If you use the `--preview` option with `apply` or `update`:

```shell
    cft apply test/fixtures/configs/ --preview
```

CFT puts each deployment in `preview` mode within DM, and displays a preview
of the action results and enables you to approve/decline the action for each
of the submitted configs. The following prompt is displayed after Stage 1 log:

```shell
    ---------- Stage 1 ----------
    Waiting for preview my-network-prod (fingerprint 3fro0c2OmnBx2HhX2V421Q==) [operation-1538165828379-576f423ce6178-3612bbd1-52600977]...done.
    NAME             TYPE                STATE      ERRORS  INTENT
    my-network-dev   compute.v1.network  COMPLETED  []
    my-network-prod  compute.v1.network  COMPLETED  []
    Update(u), Skip (s), or Abort(a) Deployment?
```

2. Having reviewed the displayed information, enter one of the following responses:

- **u<pdate>** - confirm the change on the deployment as shown in the preview
- **s<kip>** - cancel this update (no change); and continues to the next config
  in the sequence
- **a<bort>** - cancel this update (no change), and abort the script execution


### The "delete" Action

To delete the previously created/updated multiple deployments, in the CLI, type:

```shell
    cft delete [configs] [create-options]
```

For example, if you submitted the three [sample configs described above](#samples):

```shell
    cft delete instance.yaml firewall.yaml network.yaml

    ---------- Stage 1 ----------
    Waiting for delete my-instance-prod-2 (fingerprint 3IWMMfbjsUWjtWgvs6Evdw==) [operation-1538159406282-576f2a504f510-2dceed8f-b222b564]...done.
    ---------- Stage 2 ----------
    Waiting for delete my-instance-prod-1 (fingerprint ifQgUyTSOtVE1H6VgaIlYA==) [operation-1538159505990-576f2aaf66170-fcc5246d-2d44d005]...done.
    Waiting for delete my-firewall-prod (fingerprint xFs1fcZiLJPVV1hUw61-og==) [operation-1538159629835-576f2b2581af9-a83468de-d3685d90]...done.
    ---------- Stage 3 ----------
    Waiting for delete my-network-prod (fingerprint EhMN6C5IeADJYRo40CmuAg==) [operation-1538159649120-576f2b37e5f02-35da3a44-cf279bfa]...done.
```

Notice that because of the there are depedencies between the deployments, the
order of execution on deletion is reversed, or else DM would attempt to delete
a network resource, when an instance resource was still exiting, causing a big
problem with DM which would have to be manually resolved.

Another thing to note is that the tool will silently ignore deletion of
deployments that don't exits. This is by design, to cover cases where the
deletion of a specific deployment failed, the problem was fixed, and the user
doesn't have to figure out which deployments to delete. The user can just
re-run the command

