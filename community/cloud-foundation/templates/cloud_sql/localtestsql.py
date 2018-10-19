#!/usr/bin/env python
import cloud_sql
import yaml
import json

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

MOCK_YAML_MASTER = '''
env:
    name: mysql-master
    project: test-project
properties:
    region: us-central1
    databaseVersion: MYSQL_5_7
    tier: db-n1-standard-1
    dataDiskSizeGb: 10
    dataDiskType: PD_HDD
    locationPreference:
      zone: us-central1-b
    backupConfiguration:
      startTime: '02:00'
    databases:
    - name: db1
    - name: db2
    users:
    - name: user1
      host: 10.1.1.1
    - name: user2
      host: 10.1.1.2
    - name: user2
      host: 10.1.1.3
'''

MOCK_YAML_REPLICA = '''
env:
    name: mysql-replica-ex
    project: test-project
properties:
    region: us-central1
    databaseVersion: MYSQL_5_7
    tier: db-n1-standard-1
    dataDiskSizeGb: 10
    dataDiskType: PD_HDD
    backupConfiguration:
      startTime: '02:00'
    readReplicas:
    - region: us-central1
      locationPreference:
        zone: us-central1-a
    locationPreference:
      zone: us-central1-c
    databases:
    - name: db1
    - name: db2
    users:
    - name: user1
      host: 10.1.1.1
'''

# No read replicas
yaml_input = yaml.load(MOCK_YAML_MASTER)
yaml_with_dot_notation = dotdict(yaml_input)
resources = cloud_sql.generate_config(yaml_with_dot_notation)
print(json.dumps(resources, indent=4))

# Read replicas
yaml_input = yaml.load(MOCK_YAML_REPLICA)
yaml_with_dot_notation = dotdict(yaml_input)
resources = cloud_sql.generate_config(yaml_with_dot_notation)
print(json.dumps(resources, indent=4))