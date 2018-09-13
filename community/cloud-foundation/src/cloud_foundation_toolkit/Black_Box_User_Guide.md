# 1. Cloud Foundation Toolkit

User Guide
<!-- TOC -->

- [1. Cloud Foundation Toolkit](#1-cloud-foundation-toolkit)
    - [1.1. Overview](#11-overview)
        - [1.1.1. CLU](#111-clu)
        - [1.1.2. Templates](#112-templates)
    - [1.2. Toolkit Installation](#12-toolkit-installation)
    - [1.3. Deployment of a Single Config](#13-deployment-of-a-single-config)
    - [1.4. Deployment of Multiple Configs](#14-deployment-of-multiple-configs)
    - [1.5. Cross-deployment References](#15-cross-deployment-references)
    - [1.6. *** What else? ***](#16--what-else-)

<!-- /TOC -->

## 1.1. Overview

The Cloud Foundation toolkit (henceforth, CFT) expands the capabilities of Google's Deployment Manager and gcloud to support the following scenarios:

* Creation or update of multiple deployments/resources in a single operation that:
  * Accepts multiple config files as input
  * Automatically resolves dependencies between the multiple configs
  * Deploys or updates the config-defined resources in the dependency-stipulated order
* Cross-deployment (including cross-project) referencing of deployment outputs, which obviates the need for hard-coding many parameters in the configs.

The CFT includes:

* A comprehencive set of production-ready resource templates that follow Google's best practices
* A command-line utility (henceforth, CLU) that deploys resources defined in single or multiple enhanced config files that utilize the above templates

`Note:` The CLU does not support gcloud-standard config files. *** Need to explain the difference between the "standard" and "enhanced." We provide only config **examples** with our templates... Are these examples sufficient for the users to start creating their own "enhanced" configs? ***  

### 1.1.1. CLU

*** Whatever we want to say here about the tool sas such - codebase, reliance on gcloud, possibility of parsing/API'ing, etc. - keeping in mind that this User Guide is more for "black box" users than opens source gurus. ***

### 1.1.2. Templates

*** I envision a table of our templates with very brief descriptions, and with links to the templates' Readmes for more info. ***

## 1.2. Toolkit Installation

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

## 1.3. Deployment of a Single Config

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

## 1.4. Deployment of Multiple Configs

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

3. Etc.

## 1.5. Cross-deployment References

## 1.6. *** What else? ***