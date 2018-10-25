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
""" This template creates a Cloud SQL user. """


def set_optional_property(receiver, source, property_name):
    """ If set, copies the given property value from one object to another. """

    if property_name in source:
        receiver[property_name] = source[property_name]


def generate_config(context):
    """ Creates Cloud SQL user. """

    properties = context.properties
    name = properties.get('name', context.env['name'])
    project_id = properties.get('project', context.env['project'])

    user_properties = {'name': name, 'project': project_id}

    optional_properties = [
        'host',
        'instance',
        'password',
    ]

    for prop in optional_properties:
        set_optional_property(user_properties, properties, prop)

    user = {
        'name': name,
        'type': 'sqladmin.v1beta4.user',
        'properties': user_properties
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

    return {'resources': [user], 'outputs': outputs}
