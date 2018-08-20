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
"""Create a managed zone resource in clouddns """

def generate_config(context):
    """ Entry point for the deployment resources """

    resources = []

    managed_zone_name = context.properties.get('zoneName')
    dnsname = context.properties.get('dnsName')
    managed_zone_description = context.properties.get('description')

    managed_zone = {
        'name': context.env['name'],
        'type': 'dns.v1.managedZone',
        'properties': {
          'name': managed_zone_name,
          'dnsName': dnsname,
          'description': managed_zone_description
        }
    }

    resources.append(managed_zone)

    return {
        'resources':
            resources,
        'outputs':
            [
                {
                    'name': 'managedZoneName',
                    'value': managed_zone_name
                },
                {
                    'name': 'dnsName',
                    'value': dnsname
                }
            ]
    }

