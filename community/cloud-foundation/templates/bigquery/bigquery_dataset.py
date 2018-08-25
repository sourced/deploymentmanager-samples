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
"""Creates a BigQuery Dataset."""


def generate_config(context):
    """ Entry point for the deployment resources """

    # You can modify the roles you wish to whitelist here
    whitelisted_roles = ['READER', 'WRITER', 'OWNER']

    name = context.properties['name']

    properties = {
        'datasetReference':
            {
                'datasetId': name,
                'projectId': context.env['project']
            },
        'location': context.properties.get('location',
                                           'US')
    }

    if context.properties.get('description'):
        properties['description'] = context.properties['description']

    if context.properties.get('access'):
        # Validate the access roles
        for access_role in context.properties.get('access'):
            role = access_role.get('role')
            if role and role not in whitelisted_roles:
                raise ValueError(
                    'Role supplied \"{}\" for dataset \"{}\" not '
                    ' within the whitelist: {} '.format(
                        role,
                        context.properties['name'],
                        whitelisted_roles
                    )
                )

        properties['access'] = context.properties['access']

        if context.properties.get('setDefaultOwner'):
            # build default owner for dataset
            base = '@cloudservices.gserviceaccount.com'
            default_dataset_owner = context.env['project_number'] + base

            # build default access for owner
            owner_access = {
                "role": "OWNER",
                "userByEmail": default_dataset_owner
            }
            properties['access'].append(owner_access)

    resources = [
        {
            'type': 'bigquery.v2.dataset',
            'name': name,
            'properties': properties
        }
    ]

    outputs = [
        {
            'name': 'selfLink',
            'value': '$(ref.{}.selfLink)'.format(name)
        },
        {
            'name': 'datasetId',
            'value': name
        },
        {
            'name': 'etag',
            'value': '$(ref.{}.etag)'.format(name)
        },
        {
            'name': 'creationTime',
            'value': '$(ref.{}.creationTime)'.format(name)
        },
        {
            'name': 'lastModifiedTime',
            'value': '$(ref.{}.lastModifiedTime)'.format(name)
        }
    ]

    return {'resources': resources, 'outputs': outputs}
