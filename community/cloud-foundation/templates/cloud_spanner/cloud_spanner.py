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
"""
Cloud Spanner Instance and Database Templates
"""


def get_spanner_instance_id(project_id, base_name):
    return "projects/{}/instances/{}".format(project_id, base_name)


def get_spanner_instance_config(project_id, config):
    return "projects/{}/instanceConfigs/{}".format(project_id, config)


def generate_config(context):
    '''
    Generates the config gcloud recognizes to create a cloud spanner instance
    Input: context
           context is generated by gcloud when loading the input config file
    Returns: dictionary with key name resources
           This contains all the information gcloud needs to create a spanner
           instance, databases and permissions.
    '''
    resources_list = []
    instance_id = get_spanner_instance_id(
        context.env['project'],
        context.env['name']
    )
    instance_config = get_spanner_instance_config(
        context.env['project'],
        context.properties['instanceConfig']
    )
    resource = {
        'name': context.env['name'],
        'type': 'spanner.v1.instance',
        'properties':
            {
                'instanceId': context.env['name'],
                'parent': 'projects/{}'.format(context.env['project']),
                'instance':
                    {
                        'name': instance_id,
                        'config': instance_config,
                        'nodeCount': context.properties['nodeCount'],
                        'displayName': context.properties['displayName']
                    }
            }
    }
    resources_list.append(resource)

    if context.properties.get('bindings'):
        policy = {
            'name':
                "{}{}".format(context.env['name'],
                              '-setIamPolicy'),
            'action':
                (
                    'gcp-types/spanner-v1:spanner.projects.instances.setIamPolicy'
                ),
            'properties':
                {
                    'resource': instance_id,
                    'policy': {
                        'bindings': context.properties['bindings']
                    }
                },
            'metadata': {
                'dependsOn': [context.env['name']]
            }
        }
        resources_list.append(policy)

    for database in context.properties.get("databases", []):
        database_resource_name = "{}{}{}".format(
            instance_id,
            "/databases/",
            database['name']
        )
        database_resource = {
            'name': database_resource_name,
            'type': 'gcp-types/spanner-v1:projects.instances.databases',
            'properties':
                {
                    'parent': instance_id,
                    'databaseId': database['name']
                },
            'metadata': {
                'dependsOn': [context.env['name']]
            }
        }
        resources_list.append(database_resource)

        if database.get('bindings'):
            database_policy = {
                'name':
                    "{}{}".format(database_resource_name,
                                  "-setIamPolicy"),
                'action':
                    (
                        'gcp-types/spanner-v1:spanner.projects.instances.databases.setIamPolicy'
                    ),
                'properties':
                    {
                        'resource': database_resource_name,
                        'policy': {
                            'bindings': database['bindings']
                        }
                    },
                'metadata': {
                    'dependsOn': [database_resource_name]
                }
            }
            resources_list.append(database_policy)

    return {'resources': resources_list}
