# Cloud Foundation Toolkit

User Guide
<!-- TOC -->

- [Overview](#overview)
    - [CLU](#clu)
    - [Configs](#configs)
    - [Templates](#templates)
- [Toolkit Installation](#toolkit-installation)
- [Deployment of a Single Config](#deployment-of-a-single-config)
- [Deployment of Multiple Configs](#deployment-of-multiple-configs)
- [Cross-deployment References](#cross-deployment-references)
- [*** What else? ***](#-what-else-)

<!-- /TOC -->

## Overview

The Cloud Foundation toolkit (henceforth, CFT) expands the capabilities of Google's Deployment Manager and gcloud to support the following scenarios:

* Creation or update of multiple deployments/resources in a single operation that:
  * Accepts multiple config files as input
  * Automatically resolves dependencies between the multiple configs
  * Deploys or updates the config-defined resources in the dependency-stipulated order
* Cross-deployment (including cross-project) referencing of deployment outputs, which obviates the need for hard-coding many parameters in the configs.

The CFT includes:

* A comprehensive set of production-ready resource templates that follow Google's best practices
* A command-line utility (henceforth, CLU) that deploys resources defined in single or multiple enhanced config files, which utilize the above templates

`Note:` The CFT does not support gcloud-standard config files. For details on config enhancements required to ensure CFT compliance, see the [Configs](#Configs) section below.

### CLU

*** Whatever we want to say here about the tool as such - codebase, reliance on gcloud, possibility of parsing/API'ing, etc. - keeping in mind that this User Guide is more for "black box" users than for opens source gurus. ***

### Configs

To support the expanded capabilities of the CFT (multi-config deployment and cross-deployment references), every config file must include the following components, which are not found in gcloud-standard configs:

1. The deployment *** resource? *** name. For example:

```yaml
    name: my-firewall-{{environment}}
```

2. The project in which the deployment is created. For example:

```yaml
    project: my-project
```

3. Support for cross-deployment references. For example:

```yaml
    network: !DMOutput dm://my-project/my-network-{{environment}}/my-network-prod/name
```

Note that `!DMOutput` *** does what for referencing? ***.

### Templates

*** I envision a table of our templates with very brief descriptions, and with links to the templates' Readmes for more info. ***

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

## Deployment of a Single Config

Deployment of a single config with the use of the CLU is quite similar to that with the use of gcloud:

1. Do ***

```shell
    ***
```

2. Do ***

```shell
    ***
```

3. Etc.

## Deployment of Multiple Configs

To deploy multiple interdependent configs, proceed as follows:

1. Place all the configs to be deployed in the same directory; for example XYZ:

```shell
    cp ***
```

2. Run the CLU.

   The following prompt appears:

```shell
    ***
```

3. Enter the following command:

```shell
    ***
```

4. Etc.

## Cross-deployment References

## *** What else? ***