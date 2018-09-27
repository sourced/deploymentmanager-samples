# Cloud Foundation Toolkit

User Guide
<!-- TOC -->

- [Overview](#overview)
    - [Dependency Resolution](#dependency-resolution)
    - [Cross-deployment References](#cross-deployment-references)
- [CFT-compliant Configs](#cft-compliant-configs)
- [Templates](#templates)
- [Toolkit Installation](#toolkit-installation)
- [CLI Usage](#cli-usage)
    - [Syntax](#syntax)
    - [Deployment Creation](#deployment-creation)
    - [Deployment Update](#deployment-update)
    - [Deployment Application (Creation or Update)](#deployment-application-creation-or-update)
    - [Deployment Deletion](#deployment-deletion)
    - [Deployment *** Get, Validate, Render...? ***](#deployment--get-validate-render-)
- [Notes for Developers](#notes-for-developers)

<!-- /TOC -->

## Overview

The Cloud Foundation toolkit (henceforth, CFT) expands the capabilities of Google's Deployment Manager and gcloud to support the following scenarios:

* Creation or update of multiple deployments in a single operation that:
  * Accepts multiple config files as input
  * Automatically resolves dependencies between the multiple configs
  * Creates or updates deployments in the dependency-stipulated order
* Cross-deployment (including cross-project) referencing of deployment outputs, which obviates the need for hard-coding many parameters in the configs

The CFT includes:

* A command-line interface (henceforth, CLI) that deploys resources defined in single or multiple CFT-compliant config files
* A comprehensive set of production-ready resource templates that follow Google's best practices, to be imported by CFT-compliant config files

`Note:` The CFT does not support gcloud-standard config files. For details on config enhancements required to ensure CFT compliance, see the [CFT-compliant Configs](#cft-compliant-configs) section below.

### Dependency Resolution

The autmated dependency resolution the CFT supports is based on *** need an explanation ***.

### Cross-deployment References

The CFT supports cross-deployment (including cross-project) references by *** need an explanation ***.

## CFT-compliant Configs

To use the CFT, you need to first create the config files for the desired deployments. To support the expanded capabilities of the CFT (multi-config deployment and cross-deployment references), every config file must include the following components, which are not found in gcloud-standard configs: *** I umderstand that the contents of this section have to change. Can you please go right in and make the changes. Don't worry about verbiage/format - I'll edit after. ***

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

*** Config examples please. ***

## Templates

The CFT-compliant configs can use templates (Python or Jinja2). You can (although you don't have to) use templates from the set that is uncluded in the toolkit:
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


## CLI Usage

Once you have installed the CFT, the CLI becomes available *** in cmd? in GitBash? or where? ***.

### Syntax

The CLI commands adhere to the following syntax:

```shell
    cft [action] -[options] [config files]
```

The above syntactic structure includes the following elements:

* `cft` - the prefix *** the prompt? or...? ***
* `[action]` - one of the supported actions/commands:
  * create - cretaes deployments defined in the specified config files, in the dependency order
  * update - cretaes deployments defined in the specified config files, in the dependency order
  * apply - checks if the resources defined in the specified configs already exist; if they do, updates them; if they don't, creates them
  * get - *** does what? ***
  * render - *** does what? ***
  * validate - *** does what? ***
  * delete - deltes deployments defined in the specified config files, in the reverse dependency order
* `options` - one or more action-specific options:
  * -h (or --help) - displays the help content either for the entite CFT or for the current action
  * --project - the name of GCP project to perform actons in
  * -v (or --verbosity) - the log level *** what are the possible values? what does each mean? ***
  * --dry-run - pending implementation
  * -p (--preview) - displays the required changes (action results) for review/approavel before committing these changes to Deployment Manager (for the `apply` action only)
  * -r (or --reverse) - applies changes in the reverse dependency-defined order (for the `apply` action only)
* `[config files]` - an arbitrary number of config files to be affected by the specified action. The files can be specified in one of the following ways (or by acombining any of these ways):
  * a comma-separated list of the  actual file names; e.g., config_1.yaml, config_2.yaml, ..., config_n.yaml *** no path/directory required? ***
  * a directory that contains the files; e.g., ../infra1/configs; all .yaml files found in the specified directory are selected
  * wildcards *** please explain ***

You can request help eitehr for the entire CLI:

```shell
    cft --help
```

or for a specific action:

```shell
    cft [action] --help
```

The information displayed on the screen is a subset of the "global" help that pertains to the specific action.

### Deployment Creation

To deploy multiple interdependent configs, proceed as follows:

1. In the CLI, type:

```shell
    cft create [options] [.yaml files]
```

The CFT parses the submitted config files and computes the dependencies between them. For example, if you submitted three config files - one defining a network (N) and two defining VM instances to be hosted on that network (VM1 and VM2) - the VMs will depend on the network. I.e., the network will have to be created first, and the VMs afterwards. *** Would be nice to give the reader the actucal configs we are using as examples here - network and two VMs... or a more representative group of resources. *** Based on the computed dependency graph, the CFT determines the sequence of deployments to be created or updated. If the PREVIEW parameter was used, the following information is displayed:

  ```shell
      *** Need to show the info displayed for each of the configs ***
  ```

2. Having reviewed the displayed information, you can use of the following options *** commands? *** for each of the previewed configs:

- u - update - deploy the config as shown
- s - skip - (do not deploy) the config; consider the next resource in the sequence
- a - abort - cancel the entire deployment run

If you entered "u" in the above step, *** what appears on the screen? what does the user need to do, if anything? ***

If you entered "s" in the above step, the CFT re-computes the dependency graph without the skipped (excluded) config. *** what appears on the screen? what does the user need to do, if anything? ***

*** Shall we describe what can go wrong and how the toolset will react to it? ***
*** Example)s)?

### Deployment Update

*** Let's complete "Deployment Creation", A to Z - I'll reuse all that can be reused from there. ***

### Deployment Application (Creation or Update)

*** Let's complete "Deployment Creation", A to Z - I'll reuse all that can be reused from there. ***

### Deployment Deletion

*** Let's complete "Deployment Creation", A to Z - I'll reuse all that can be reused from there. *** 

### Deployment *** Get, Validate, Render...? ***

***

## Notes for Developers

*** Here we shoukd put notes for those folks who are going to treat the CFT as open-sporce code base - to modify and adapt to their own needs. Like what files are included in the code base, what each one is for, etc. Probably one or two "adaptation" scenarios - i.e., what developers can change to achieve a goal they are likley to have. The info here is going to be complemented by inline comments in the code (.py files). ***