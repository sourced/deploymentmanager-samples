# 1. Cloud Foundation Toolkit v0.x

User Guide
<!-- TOC -->

- [1. Cloud Foundation Toolkit v0.x](#1-cloud-foundation-toolkit-v0x)
    - [1.1. Overview](#11-overview)
        - [1.1.1. CFT](#111-cft)
        - [1.1.2. Templates](#112-templates)
    - [1.2. Installation](#12-installation)
    - [1.3. Deployment of a Single Config](#13-deployment-of-a-single-config)
    - [1.4. Concurrent Deployment of Multiple Configs](#14-concurrent-deployment-of-multiple-configs)
    - [1.5. Cross-deployment References](#15-cross-deployment-references)
    - [1.6. *** What else? ***](#16--what-else-)

<!-- /TOC -->

## 1.1. Overview

The Cloud Foundation toolkit expands the capabilities of Google's Deployment Manager and gcloud to support the following scenarios:

* Concurrent creation/update of multipe deployments/resources. This operation:
  * Accepts multiple config files as input
  * Automatically resolves dependencies between the multiple configs
  * Deploys the config-defined resources in the dependency-stipulated order
* Cross-deployment (or even cross-project) referencing of any of the resource parameters. This operation: *** does what? ***.

The Cloud Foundation toolkit includes:

* A comprehenvive set of resource deployment templates *** would be nice toat least briefly state how **our** remplates are better/richer than all the others *** 
* A command-line untility (henceforth, Cloud Foundation Tool, or CFT) that deploys resources using the above templates

`Note:` The templates included in the toolkit are guaranteed to work with Deployment Manager / gcloud. CFT is not guatanteed to support multiple-deployment and cross-deployment scenatios with templates other than those included in the toolkit.

### 1.1.1. CFT

*** Whatever we want to say here about the tool sas such - codebase, reliance on gcloud, possibility of parsing/API'ing, eyc. - keeing in mind that this User Guide is more for "black box" users than opens source gurus. ***

### 1.1.2. Templates

*** I envision a table of our templates with very brief descriptions, and with links to the templates' Readmes for more info. ***

## 1.2. Installation

To install CFT, proceed as follows:

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

## 1.3. Deployment of a Single Config

Deployment of a single config with the use of CFT is quite similar to that with the use of gcloud:

1. Do ***

```shell
    ***
```

2. Do ***

```shell
    ***
```

3. Etc.

## 1.4. Concurrent Deployment of Multiple Configs

To deploy multiple interdependent configs, proceed as follows:

1. Place all the configs to be deployed in the same directory; for example XYZ:

```shell
    cp ***
```

2. Run CFT.

   The following prompt appears:

```shell
    ***
```

3. Enter the following command:

```shell
    ***
```

3. Etc.

## 1.5. Cross-deployment References

## 1.6. *** What else? ***