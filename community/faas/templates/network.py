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
"""Create a network resource"""


def generate_config(context):
    """ Entry point for the deployment resources """

<<<<<<< HEAD
    name = context.properties.get('name') or context.env['name']
    network_self_link = '$(ref.{}.selfLink)'.format(name)
=======
    # If autoCreateSubnetworks is not provided in the config, the default
    # 'False' will be used. In this case, the VPC will use custom generated
    # subnets. If the value is 'True', subnets will be automatically generated
    # see https://cloud.google.com/vpc/docs/vpc#ip-ranges
>>>>>>> FAAS initial commit
    auto_create_subnetworks = context.properties.get(
        'autoCreateSubnetworks',
        False
    )

    resources = [
        {
<<<<<<< HEAD
            'type': 'compute.v1.network',
            'name': name,
            'properties':
                {
                    'name': name,
=======
            # A Network resource
            'type': 'compute.v1.network',
            'name': context.env['name'],
            'properties':
                {
                    'name': context.properties['name'],
>>>>>>> FAAS initial commit
                    'autoCreateSubnetworks': auto_create_subnetworks
                }
        }
    ]

<<<<<<< HEAD
    # Subnetwork Resources
    for subnetwork in context.properties.get('subnetworks', []):
        subnetwork['network'] = network_self_link
        resources.append(
            {
                'name': subnetwork['name'],
                'type': 'subnetwork.py',
                'properties': subnetwork
            }
        )

=======
>>>>>>> FAAS initial commit
    return {
        'resources':
            resources,
        'outputs':
            [
                {
<<<<<<< HEAD
                    'name': 'name',
                    'value': name
                },
                {
                    'name': 'networkUrl',
                    'value': network_self_link
=======
                    'name': 'networkUrl',
                    'value': '$(ref.' + context.env['name'] + '.selfLink)'
>>>>>>> FAAS initial commit
                }
            ]
    }
