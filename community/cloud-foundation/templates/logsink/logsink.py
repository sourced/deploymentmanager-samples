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
"""This template creates a logsink (logging sink)."""


def generate_config(context):
    """ Entry point for the deployment resources. """

    project_id = context.env['project']
    name = context.properties.get('name', context.env['name'])

    if context.properties.get('orgId'):
        source_id = str(context.properties.get('orgId'))
        source_type = 'organizations'
    elif context.properties.get('billingAccountId'):
        source_id = context.properties.get('billingAccountId')
        source_type = 'billingAccounts'
    elif context.properties.get('folderId'):
        source_id = str(context.properties.get('folderId'))
        source_type = 'folders'
    elif context.properties.get('projectId'):
        source_id = context.properties.get('projectId')
        source_type = 'projects'

    if context.properties['destinationType'] == 'pubsub':
        destination = 'pubsub.googleapis.com/projects/{}/topics/{}'.format(
            project_id,
            context.properties['destinationName']
        )
    elif context.properties['destinationType'] == 'storage':
        destination = 'storage.googleapis.com/{}'.format(
            context.properties['destinationName']
        )
    elif context.properties['destinationType'] == 'bigquery':
        destination = 'bigquery.googleapis.com/projects/{}/datasets/{}'.format(
            project_id,
            context.properties['destinationName']
        )

    properties = {
        'name': name,
        'parent': '{}/{}'.format(source_type,
                                 source_id),
        'destination': destination,
        'uniqueWriterIdentity': context.properties['uniqueWriterIdentity']
    }

    sink_filter = context.properties.get('filter')
    if sink_filter:
        properties['filter'] = sink_filter

    base_type = 'gcp-types/logging-v2:logging.'
    create_name = 'logsink-create-{}'.format(context.env['name'])
    delete_name = 'logsink-delete-{}'.format(context.env['name'])
    resources = [
        {
            'name': create_name,
            'action': base_type + source_type + '.sinks.create',
            'properties': properties
        },
        {
            'name': delete_name,
            'action': base_type + source_type + '.sinks.delete',
            'metadata': {
                'runtimePolicy': ['DELETE'],
            },
            'properties':
                {
                    'sinkName':
                        '{}/{}/sinks/{}'.format(source_type,
                                                source_id,
                                                name)
                }
        }
    ]

    return {
        'resources':
            resources,
        'outputs':
            [
                {
                    'name': 'writerIdentity',
                    'value': '$(ref.{}.writerIdentity)'.format(create_name)
                }
            ]
    }
