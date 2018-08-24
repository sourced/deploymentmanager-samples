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
"""Create dns record-sets resources for a managed zone"""


def generate_config(context):
    """ Entry point for the deployment resources """

    resources = []
    zonename = context.properties['zoneName']

    # For each ResourceRecordSet. Create:
    # 1. A Change to create it.
    # 2. A Change to delete it.
    for resource_recordset in context.properties['resourceRecordSets']:
        # updates will be matched against names, so create a unique name
        # for this RRS.
        deployment_name = generate_unique_recordsetname(resource_recordset)
        # Change to create it.
        recordset_create = {
            'name': '%(deploymentName)s-create' % {
                'deploymentName': deployment_name},
            'action': 'gcp-types/dns-v1:dns.changes.create',
            'metadata': {
                'runtimePolicy': [
                    'CREATE',
                ],
            },
            'properties': {
                'managedZone': zonename,
                'additions': [
                    resource_recordset,
                ],
            },
        }
        # Change to delete it.
        recordset_delete = {
            'name': '%(deploymentName)s-delete' % {
                'deploymentName': deployment_name},
            'action': 'gcp-types/dns-v1:dns.changes.create',
            'metadata': {
                'runtimePolicy': [
                    'DELETE'
                ]
            },
            'properties': {
                'managedZone': zonename,
                'deletions': [
                    resource_recordset
                ]
            },
        }

        resources.append(recordset_create)
        resources.append(recordset_delete)

    return {'resources': resources}


def generate_unique_recordsetname(resource_recordset):
    """ generates a unique string joined with properties
    from a resourceRecordset """

    return '%(name)s-%(type)s-%(ttl)s' % {
        'name': resource_recordset['name'],
        'type': resource_recordset['type'].lower(),
        'ttl': resource_recordset['ttl']
    }
