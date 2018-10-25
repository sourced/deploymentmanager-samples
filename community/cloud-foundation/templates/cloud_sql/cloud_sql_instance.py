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
""" This template creates a Cloud SQL instance. """


def set_optional_property(receiver, source, property_name):
    """ If set, copies the given property value from one object to another. """

    if property_name in source:
        receiver[property_name] = source[property_name]


def generate_config(context):
    """ Create Cloud SQL Instance. """

    properties = context.properties
    name = properties.get('name', context.env['name'])
    project_id = properties.get('project', context.env['project'])

    instance_properties = {
        'region': properties['region'],
        'project': project_id,
        'name': name
    }

    optional_properties = [
        'connectionName',
        'databaseVersion',
        'tier',
        'gceZone',
        'instanceType',
        'ipAddresses',
        'ipv6Address',
        'masterInstanceName',
        'maxDiskSize',
        'onPremisesConfiguration',
        'replicaConfiguration',
        'settings',
        'serverCaCert',
        'serviceAccountEmailAddress'
    ]

    for prop in optional_properties:
        set_optional_property(instance_properties, properties, prop)

    instance = {
        'name': name,
        'type': 'sqladmin.v1beta4.instance',
        'properties': instance_properties
    }

    outputs = [
        {
            'name': 'name',
            'value': '$(ref.{}.name)'.format(name)
        },
        {
            'name': 'selfLink',
            'value': '$(ref.{}.selfLink)'.format(name)
        }
    ]

    return {'resources': [instance], 'outputs': outputs}
