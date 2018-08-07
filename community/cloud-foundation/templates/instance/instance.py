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
"""Creates an instance."""

def create_boot_disk(properties, zone, instance_name):
    """ Create boot disk configuration """

    disk_name = instance_name
    boot_disk = {
        'deviceName': disk_name,
        'type': 'PERSISTENT',
        'boot': True,
        'autoDelete': True,
        'initializeParams': {
            'sourceImage': properties['diskImage']
        }
    }

    disk_size_gb = properties.get('diskSizeGb', None)
    if disk_size_gb is not None:
        boot_disk['initializeParams']['diskSizeGb'] = disk_size_gb

    disk_type = properties.get('diskType', None)
    if disk_type is not None:
        boot_disk['initializeParams']['diskType'] = 'zones/{}/diskTypes/{}'.format(zone, disk_type)

    return boot_disk

def get_network(properties):
    """ Get configuration that connects an instance to preexisting network
        and assigns ephemeral public IP. If network name is not provided,
        'default' network will be used.
    """

    network_name = properties.get('network', 'default')
    return {
        'network': 'global/networks/{}'.format(network_name),
        'accessConfigs': [
            {
                'name': 'External NAT',
                'type': 'ONE_TO_ONE_NAT'
            }
        ]
    }

def generate_config(context):
    """ Entry point for the deployment resources """

    zone = context.properties['zone']
    vm_name = context.properties.get('name', context.env['name'])
    machine_type = context.properties['machineType']

    boot_disk = create_boot_disk(context.properties, zone, vm_name)
    network = get_network(context.properties)
    instance = {
        'name': vm_name,
        'type': 'compute.v1.instance',
        'properties':{
            'zone': zone,
            'machineType': 'zones/{}/machineTypes/{}'.format(zone, machine_type),
            'disks': [boot_disk],
            'networkInterfaces': [network]
        }
    }

    metadata = context.properties.get('metadata', None)
    if metadata is not None:
        instance['properties']['metadata'] = metadata

    return {
        'resources': [instance],
        'outputs': [
            {
                'name': 'internalIp',
                'value': '$(ref.{}.networkInterfaces[0].networkIP)'.format(vm_name)
            },
            {
                'name': 'externalIp',
                'value': '$(ref.{}.networkInterfaces[0].accessConfigs[0].natIP)'.format(vm_name)
            }
        ]
    }
