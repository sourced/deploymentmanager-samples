# Cloud Foundation Toolkit

User Guide
<!-- TOC -->

- [Overview](#overview)
    - [The CLU](#the-clu)
    - [CFT-compliant Configs](#cft-compliant-configs)
    - [Templates](#templates)
- [Toolkit Installation](#toolkit-installation)
- [Creation/Update of Multiple Resources](#creationupdate-of-multiple-resources)
- [Deletion of Multiple Resources](#deletion-of-multiple-resources)
- [*** Do we need sections for Get, Validate, Render...? ***](#-do-we-need-sections-for-get-validate-render-)
- [Cross-deployment References](#cross-deployment-references)
- [*** Any other cases? ***](#-any-other-cases-)

<!-- /TOC -->

## Overview

The Cloud Foundation toolkit (henceforth, CFT) expands the capabilities of Google's Deployment Manager and gcloud to support the following scenarios:

* Creation or update of multiple deployments/resources in a single operation that:
  * Accepts multiple config files as input
  * Automatically resolves dependencies between the multiple configs
  * Deploys or updates the config-defined resources in the dependency-stipulated order
* Cross-deployment (including cross-project) referencing of deployment outputs, which obviates the need for hard-coding many parameters in the configs

The CFT includes:

* A command-line utility (henceforth, CLU) that deploys resources defined in single or multiple CFT-compliant config files
* A comprehensive set of production-ready resource templates that follow Google's best practices, to be imported by CFT-compliant config files

`Note:` The CFT does not support gcloud-standard config files. For details on config enhancements required to ensure CFT compliance, see the [CFT-compliant Configs](#cft-compliant-configs) section below.

### The CLU

*** Whatever we want to say here about the tool as such - codebase, reliance on gcloud, possibility of parsing/API'ing, etc. - keeping in mind that this User Guide is more for "black box" users than for opens source gurus. ***

### CFT-compliant Configs

To support the expanded capabilities of the CFT (multi-config deployment and cross-deployment references), every config file must include the following components, which are not found in gcloud-standard configs:

1. The environment in which the config is to be deployed, For example:

```yaml
    {% set environment = 'prod' %}
```

2. The resource name that includes the environment. For example:

```yaml
    name: my-firewall-{{environment}}
```

3. The resource description *** is this really a "must have"? Is it technically mandatory? ***. For example:

```yaml
    description: My firewall deployment for {{environment}} environment
```

4. The project in which the resource is deployed. For example:

```yaml
    project: my-project
```

5. Support for cross-deployment references. For example:

```yaml
    network: !DMOutput dm://my-project/my-network-{{environment}}/my-network-prod/name
```

The `!DMOutput` construct works as follows: *** need to explain what it does and how ***.

*** Probably would be good to give a complete config example here - a simple, straightforward one. ***

### Templates

*** I envision a list (table) of our templates with very brief descriptions, and with links to the templates' Readmes for more info. Alternative suggestions are welcome. ***

## Toolkit Installation

To install the CFT, proceed as follows:

1. Copy *** to ***:

```shell
    cp ***
```

2. Move to the *** directory:

```shell
    cd ***
```

3. Initiate the installation process:

```shell
    ***
```

4. Export ***: ***

## Creation/Update of Multiple Resources

The deployment Creation and Update actions are similar to each other; therefore, they are described in the same section. In a sense, the two are parts/stages of the same action. The CFT first checks if the resources defined in the submitted configs already exist in the environment. If they do, an attempt is made to update them. If they don't, an attempt is made to create them.

Resource creation/update (deployment/re-deployment) based on a single config in CFT is not much different from that in gcloud. This is why we are not going to discuss the "single config" scenario separately. Rather, we will consider it a sub-case of the "multi-config" scenario.

To deploy/update multiple interdependent configs, proceed as follows:

1. In the CLU, specify the desired action, the config files to undergo that action, and the optional parameters:

```shell
    cft apply [--preview = PREVEW] [.yaml files]
```

In the above command:

* The "apply" command that appears immediately after the CLU prompt, "cft", defines the required action: create/update *** is it "apply"? Why not "create"... or "update"... or "upsert"? ***
* The PREVIEW parameter, if present, requires that the computed deployment changes (additions/updates) be shown to the user for review/approval before committing them to the Deployment Manager
* The config (.yaml) files to be created/updated can be defined in several ways:
  - Explicitly by path/name, divided by comma; for eaxample: config1.yaml, config2.yaml, config3.yaml
  - By path to a directory - all .yaml files found in that directory are included; for example: .../deployment1/configs
  - With the use of wildcards: for example: *** please explain / provide example ***  

The CFT parses the submitted config files and computes the dependencies between them. For example, if you submitted three config files - one defining a network (N) and two defining VM instances to be hosted on that network (VM1 and VM2) - the VMs will depend on the network. I.e., the network will have to be created first, and the VMs afterwards. *** Would be nice to give the reader the actucal configs we are using as examples here - network and two VMs... or a more representative group of resources. ***
  
Based on the computed dependency graph, the CFT determines the sequence of deployments to be created or updated. If the PREVIEW parameter was used, the following information is displayed:

  ```shell
      *** Need to show the info displayed for each of the resources ***
  ```

1. Having reviewed the displayed information, you can use of the following options *** commands? *** for each of the previewed resources:

- u - update (run the creation/update as shown)
- s - skip (do not create/update; consider the next resource in the sequence)
- a - abort (cancel the entire deployment run)

3. The "u" command initiates the actual deployment. *** what appears on the screen? what does the user need to do, if anything? ***

4. The "s" command causes the CFT to re-compute the dependency graph without the skipped (excluded) resource. *** what appears on the screen? what does the user need to do, if anything? ***

*** Shall we describe what can go wrong and how the toolset will react to it? ***

## Deletion of Multiple Resources

***

## *** Do we need sections for Get, Validate, Render...? ***

***

## Cross-deployment References

To have resources in one deployment reference resources in another deployment, even if that deployment is in another project *** should this be a separate case - and, therefore, a separate UG section? Or should it a be a subcase of create/update/etc. - one of the sections above? ***.

## *** Any other cases? ***