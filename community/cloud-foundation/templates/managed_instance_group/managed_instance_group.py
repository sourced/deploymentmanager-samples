# Copyright 2018 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" This template creates a managed instance group. """

REGIONAL_LOCAL_AUTOSCALER_TYPES = {
    True: 'compute.v1.regionAutoscaler',
    False: 'compute.v1.autoscaler'
}
REGIONAL_LOCAL_IGM_TYPES = {
    True: 'compute.v1.regionInstanceGroupManager',
    False: 'compute.v1.instanceGroupManager'
}

def set_optional_property(receiver, source, property_name):
    """ If set, copies the given property value from one object to another. """

    if property_name in source:
        receiver[property_name] = source[property_name]

def create_boot_disk(properties):
    """ Creates the boot disk configuration. """

    boot_disk = {
        'deviceName': 'boot',
        'type': 'PERSISTENT',
        'boot': True,
        'autoDelete': True,
        'initializeParams': {
            'sourceImage': properties['diskImage']
        }
    }

    for prop in ['diskSizeGb', 'diskType']:
        set_optional_property(boot_disk['initializeParams'], properties, prop)

    return boot_disk

def get_network(properties):
    """ Gets the configuration that connects an instance to an existing network
        and assigns to it an ephemeral public IP.
    """

    network_name = properties.get('network')
    return {
        'network': 'global/networks/{}'.format(network_name),
        'accessConfigs': [
            {
                'name': 'External NAT',
                'type': 'ONE_TO_ONE_NAT'
            }
        ]
    }

def create_instance_template(properties, context):
    """ Creates an instance template description. """

    name = properties.get('name', context.env['name'] + '-it')
    machine_type = properties['machineType']
    boot_disk = create_boot_disk(properties)
    network = get_network(properties)
    instance_template = {
        'name': name,
        'type': 'compute.v1.instanceTemplate',
        'properties':
            {
                'properties':
                    {
                        'machineType': machine_type,
                        'disks': [boot_disk],
                        'networkInterfaces': [network]
                    }
            }
        }

    template_props = instance_template['properties']['properties']

    for prop in ['metadata', 'canIpForward']:
        set_optional_property(template_props, properties, prop)

    self_link = '$(ref.{}.selfLink)'.format(name)

    return self_link, [instance_template], [
        {
            'name': 'instanceTemplateSelfLink',
            'value': self_link
        }
    ]

def get_instance_template(properties, context):
    """ If an instance template exists, returns a link to that template. 
    If no instance template exists: (a) creates that template; (b) retruns a link to it; 
    and (c) returns resources/outputs that were required to create the template. 
    """

    if 'url' in properties:
        return properties['url'], [], []

    return create_instance_template(properties, context)

def get_autoscaler(properties, is_regional, igm):
    """ Creates an autoscaler if one is necessary. """

    autoscaler_spec = properties.get('autoscaler')
    if autoscaler_spec:
        igm_name = igm['name']
        igm_properties = igm['properties']
        autoscaler_properties = {
            'autoscalingPolicy':
                {
                    'coolDownPeriodSec': autoscaler_spec['coolDownPeriodSec'],
                    'maxNumReplicas': igm_properties['targetSize'],
                    'minNumReplicas': autoscaler_spec['minSize'],
                },
            'target': '$(ref.{}.selfLink)'.format(igm_name)
        }

        utilization_configs = ['cpuUtilization',
                               'customMetricUtilizations',
                               'loadBalancingUtilization']
        for config in utilization_configs:
            set_optional_property(autoscaler_properties['autoscalingPolicy'],
                                  autoscaler_spec,
                                  config)

        for location in ['zone', 'region']:
            set_optional_property(autoscaler_properties,
                                  igm['properties'],
                                  location)

        set_optional_property(autoscaler_properties,
                              autoscaler_spec,
                              'description')

        autoscaler_name = autoscaler_spec.get('name', igm_name + '-autoscaler')
        autoscaler_resource = {
            'type': REGIONAL_LOCAL_AUTOSCALER_TYPES[is_regional],
            'name': autoscaler_name,
            'properties': autoscaler_properties
        }

        autoscaler_output = {
            'name': 'autoscalerSelfLink',
            'value': '$(ref.{}.selfLink)'.format(autoscaler_name)
        }

        return [autoscaler_resource], [autoscaler_output]

    return [], []

def get_igm_outputs(igm_name, igm_properties):
    """ Creates Instance Group Manaher (IGM) resource outputs. """

    igm_outputs = [
        {
            'name': 'selfLink',
            'value': '$(ref.{}.selfLink)'.format(igm_name)
        },
        {
            'name': 'name',
            'value': igm_name
        },
        {
            'name': 'instanceGroup',
            'value': '$(ref.{}.instanceGroup)'.format(igm_name)
        }
    ]

    if 'region' in igm_properties:
        igm_outputs.append({
            'name': 'region',
            'value': igm_properties['region']
        })
    else:
        igm_outputs.append({
            'name': 'zone',
            'value': igm_properties['zone']
        })

    return igm_outputs

def get_igm_resource(context):
    """ Creates the IGM resource with its outputs. """

    properties = context.properties
    igm_name = properties.get('name', context.env['name'] + '-igm')
    is_regional = 'region' in properties

    template = get_instance_template(properties['instanceTemplate'], context)
    template_link, template_resources, template_outputs = template

    igm_properties = {
        'instanceTemplate': template_link
    }

    igm_resources = [
        {
            'name': igm_name,
            'type': REGIONAL_LOCAL_IGM_TYPES[is_regional],
            'properties': igm_properties
        }
    ]

    known_properties = ['description',
                        'distributionPolicy',
                        'namedPorts',
                        'zone',
                        'region',
                        'targetSize',
                        'baseInstanceName']

    for prop in known_properties:
        set_optional_property(igm_properties, properties, prop)

    if 'healthChecks' in properties:
        igm_properties['autoHealingPolicies'] = properties['healthChecks']

    igm_outputs = get_igm_outputs(igm_name, igm_properties)

    return igm_resources + template_resources, igm_outputs + template_outputs

def generate_config(context):
    """ Entry point for the deployment resources. """

    igm_resources, igm_outputs = get_igm_resource(context)

    igm = igm_resources[0]
    is_regional = 'region' in igm['properties']

    autoscaler = get_autoscaler(context.properties, is_regional, igm)
    autoscaler_resources, autoscaler_outputs = autoscaler

    return {
        'resources': igm_resources +  autoscaler_resources,
        'outputs': igm_outputs + autoscaler_outputs,
    }
