#!/usr/bin/env python
"""Gcloud deploy manager template script to create a Cloud SQL Instance"""

import copy

USER_NAME_PATTERN = '{}-user-{}-{}'
DATABASE_NAME_PATTERN = '{}-database-{}'

def generate_config(context):
    """Create Cloud SQL Instance."""
    props = context.properties
    region = props['region']
    project_id = context.env['project']
    instance_name = context.env['name']

    maintenance_window = props.get('maintenanceWindow', {})
    ip_config = props.get('ipConfiguration', {})

    resources = []
    instance_template = {
        'name': instance_name,
        'type': 'sqladmin.v1beta4.instance',
        'properties': {
            'name': instance_name,
            'project': project_id,
            'databaseVersion': props['databaseVersion'],
            'region': region,
            'settings': {
                'tier': props['tier'],
                'storageAutoResize': '',
                'storageAutoResizeLimit': '',
                'maintenanceWindow': {
                    'day': '',
                    'hour': ''
                },
                'activationPolicy': '',
                'ipConfiguration': {
                    'ipv4Enabled': '',
                    'requireSsl': '',
                    'authorizedNetworks': []
                },
                'dataDiskSizeGb': '',
                'dataDiskType': '',
            }
        }
    }

    instance_resource = copy.deepcopy(instance_template)
    instance_settings = instance_resource['properties']['settings']
    instance_maintenance_window = instance_settings['maintenanceWindow']
    instance_ip_config = instance_settings['ipConfiguration']

    instance_settings['storageAutoResize'] = props.get('storageAutoResize', True)
    instance_settings['storageAutoResizeLimit'] = props.get('storageAutoResizeLimit', 0)
    instance_settings['activationPolicy'] = props.get('activationPolicy')
    instance_settings['dataDiskSizeGb'] = props.get('dataDiskSizeGb')
    instance_settings['dataDiskType'] = props.get('dataDiskType')
    instance_maintenance_window['day'] = maintenance_window.get('day', 1)
    instance_maintenance_window['hour'] = maintenance_window.get('hour', 5)
    instance_ip_config['ipv4Enabled'] = ip_config.get('ipv4Enabled', True)
    instance_ip_config['requireSsl'] = ip_config.get('requireSsl', True)
    instance_ip_config['authorizedNetworks'] = ip_config.get('authorizedNetworks')

    resources.append(instance_resource)
    dependencies = [instance_name]

    # Add a failover replica to the master instance if supplied
    if 'createFailoverReplica' in props:
        failover_replica_name = instance_name + '-fo'
        instance_resource['properties']['failoverReplica'] = {
            'name': failover_replica_name
        }

    # Add a backup configuration
    if 'backupConfiguration' in props:
        backup_config = props['backupConfiguration']
        instance_settings['backupConfiguration'] = {
            'enabled': backup_config.get('enabled', True),
            'binaryLogEnabled': backup_config.get('binaryLogEnabled', True),
            'startTime': backup_config.get('startTime')
        }

    if 'locationPreference' in props:
        instance_settings['locationPreference'] = {
            'zone': props['locationPreference']['zone']
        }

    if 'readReplicas' in props:
        read_replicas = props.get('readReplicas')
        for replica in read_replicas:
            replica_count = replica.get('count', 1)
            replica_region = replica.get('region')
            for i in range(0, replica_count):
                replica_name = instance_name + '-replica-' + str(i)
                replica_resource = copy.deepcopy(instance_template)
                replica_resource['metadata'] = {
                    'dependsOn': list(dependencies)
                }
                replica_properties = replica_resource['properties']
                replica_settings = replica_resource['properties']['settings']
                replica_maintenance_window = replica_settings['maintenanceWindow']
                replica_ip_config = replica_settings['ipConfiguration']
                
                replica_resource['name'] = replica_name
                replica_properties['masterInstanceName'] = instance_name
                replica_properties['region'] = replica_region
                replica_settings['storageAutoResize'] = props.get('storageAutoResize', True)
                replica_settings['storageAutoResizeLimit'] = props.get('storageAutoResizeLimit', 0)
                replica_settings['activationPolicy'] = props.get('activationPolicy')
                replica_settings['dataDiskSizeGb'] = props.get('dataDiskSizeGb')
                replica_settings['dataDiskType'] = props.get('dataDiskType')
                replica_maintenance_window['day'] = maintenance_window.get('day', 1)
                replica_maintenance_window['hour'] = maintenance_window.get('hour', 5)
                replica_ip_config['ipv4Enabled'] = ip_config.get('ipv4Enabled', True)
                replica_ip_config['requireSsl'] = ip_config.get('requireSsl', True)
                replica_ip_config['authorizedNetworks'] = ip_config.get('authorizedNetworks')

                if 'locationPreference' in replica:
                    replica_settings['locationPreference'] = {
                        'zone': replica['locationPreference']['zone']
                    }
                resources.append(replica_resource)
                dependencies.append(replica_resource['name'])

    databases = context.properties.get('databases', [])
    for database in databases:
        db_name = database['name']
        resource = {
            'name': DATABASE_NAME_PATTERN.format(instance_name, db_name),
            'type': 'sqladmin.v1beta4.database',
            'properties': {
                'instance': instance_name,
                'project': project_id,
                'name': db_name
            },
            'metadata': {
                'dependsOn': list(dependencies)
            }
        }
        dependencies.append(resource['name'])
        resources.append(resource)

    users = context.properties.get('users', [])
    for user in users:
        user_name = user['name']
        host = user.get('host', None)
        if host is None or host == '' or host == '%':
            raise ValueError('You must define a restrictive host for database user access')
        resource = {
            'name': USER_NAME_PATTERN.format(instance_name, user_name, host),
            'type': 'sqladmin.v1beta4.user',
            'properties': {
                'name': user_name,
                'host': host,
                'instance': instance_name
            },
            'metadata': {
                'dependsOn': list(dependencies)
            }
        }
        dependencies.append(resource['name'])
        resources.append(resource)

    return {'resources': resources}
