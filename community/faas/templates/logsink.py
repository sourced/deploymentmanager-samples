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
"""Creates a logging sink."""


def generate_config(context):
    """ Entry point for the deployment resources """

    project_id = context.env['project']
    name = context.properties.get('name', context.env['name'])

    if context.properties['destinationType'] == 'PUBSUB':
        destination = 'pubsub.googleapis.com/projects/{}/topics/{}'.format(
            project_id,
            context.properties['destinationName']
        )
    elif context.properties['destinationType'] == 'STORAGE':
        destination = 'storage.googleapis.com/{}'.format(
            context.properties['destinationName']
        )
    elif context.properties['destinationType'] == 'BIGQUERY':
        destination = 'bigquery.googleapis.com/projects/{}/datasets/{}'.format(
            project_id,
            context.properties['destinationName']
        )

    properties = {
        'name': name,
        'sink': name,
        'destination': destination,
        'uniqueWriterIdentity': context.properties['uniqueWriterIdentity']
    }

    sink_filter = context.properties.get('filter')
    if sink_filter:
        properties['filter'] = sink_filter

    resources = [
        {
            'name': context.env['name'],
            'type': 'logging.v2.sink',
            'properties': properties
        }
    ]

    return {'resources': resources}
