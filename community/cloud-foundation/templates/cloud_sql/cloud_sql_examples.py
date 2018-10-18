#!/usr/bin/env python
"""
Unit tests for the cloud_function_template.py script
"""
import unittest
import json
from gcp_foundation import common
from gcp_foundation import cloudsql_instance_template
import yaml

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
EXPECTED_OUTPUT_MASTER = {
    "resources": [
        {
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-master",
            "properties": {
                "name": "mysql-master",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "locationPreference": {
                        "zone": "us-central1-b"
                    },
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS",
                    "backupConfiguration": {
                        "enabled": True,
                        "startTime": "02:00",
                        "binaryLogEnabled": True
                    }
                },
                "region": "us-central1",
                "project": "test-project",
                "databaseVersion": "MYSQL_5_7",
                "failoverReplica": {
                    "name": "mysql-master-fo"
                }
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-master"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-master-database-db1",
            "properties": {
                "project": "test-project",
                "instance": "mysql-master",
                "name": "db1"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-master",
                    "mysql-master-database-db1"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-master-database-db2",
            "properties": {
                "project": "test-project",
                "instance": "mysql-master",
                "name": "db2"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-master",
                    "mysql-master-database-db1",
                    "mysql-master-database-db2"
                ]
            },
            "type": "sqladmin.v1beta4.user",
            "name": "mysql-master-user-user1-10.1.1.1",
            "properties": {
                "instance": "mysql-master",
                "host": "10.1.1.1",
                "name": "user1"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-master",
                    "mysql-master-database-db1",
                    "mysql-master-database-db2",
                    "mysql-master-user-user1-10.1.1.1"
                ]
            },
            "type": "sqladmin.v1beta4.user",
            "name": "mysql-master-user-user2-10.1.1.2",
            "properties": {
                "instance": "mysql-master",
                "host": "10.1.1.2",
                "name": "user2"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-master",
                    "mysql-master-database-db1",
                    "mysql-master-database-db2",
                    "mysql-master-user-user1-10.1.1.1",
                    "mysql-master-user-user2-10.1.1.2"
                ]
            },
            "type": "sqladmin.v1beta4.user",
            "name": "mysql-master-user-user2-10.1.1.3",
            "properties": {
                "instance": "mysql-master",
                "host": "10.1.1.3",
                "name": "user2"
            }
        }
    ]
}

MOCK_YAML_REPLICA = '''
env:
    name: mysql-replica
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
EXPECTED_OUTPUT_REPLICA = {
    "resources": [
        {
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-replica",
            "properties": {
                "name": "mysql-replica",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "locationPreference": {
                        "zone": "us-central1-c"
                    },
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS",
                    "backupConfiguration": {
                        "enabled": True,
                        "startTime": "02:00",
                        "binaryLogEnabled": True
                    }
                },
                "region": "us-central1",
                "project": "test-project",
                "databaseVersion": "MYSQL_5_7",
                "failoverReplica": {
                    "name": "mysql-replica-fo"
                }
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica"
                ]
            },
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-replica-replica-usc1-0",
            "properties": {
                "name": "mysql-replica-replica-usc1-0",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "locationPreference": {
                        "zone": "us-central1-a"
                    },
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS"
                },
                "region": "us-central1",
                "masterInstanceName": "mysql-replica",
                "project": "test-project",
                "databaseVersion": "MYSQL_5_7"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-replica-database-db1",
            "properties": {
                "project": "test-project",
                "instance": "mysql-replica",
                "name": "db1"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0",
                    "mysql-replica-database-db1"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-replica-database-db2",
            "properties": {
                "project": "test-project",
                "instance": "mysql-replica",
                "name": "db2"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0",
                    "mysql-replica-database-db1",
                    "mysql-replica-database-db2"
                ]
            },
            "type": "sqladmin.v1beta4.user",
            "name": "mysql-replica-user-user1-10.1.1.1",
            "properties": {
                "instance": "mysql-replica",
                "host": "10.1.1.1",
                "name": "user1"
            }
        }
    ]
}

MOCK_YAML_MULTIPLE_REPLICAS = '''
env:
    name: mysql-replica
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
      count: 2
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
EXPECTED_OUTPUT_MULTIPLE_REPLICAS = {
    "resources": [
        {
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-replica",
            "properties": {
                "name": "mysql-replica",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "locationPreference": {
                        "zone": "us-central1-c"
                    },
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS",
                    "backupConfiguration": {
                        "enabled": True,
                        "startTime": "02:00",
                        "binaryLogEnabled": True
                    }
                },
                "region": "us-central1",
                "project": "test-project",
                "databaseVersion": "MYSQL_5_7",
                "failoverReplica": {
                    "name": "mysql-replica-fo"
                }
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica"
                ]
            },
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-replica-replica-usc1-0",
            "properties": {
                "name": "mysql-replica-replica-usc1-0",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "locationPreference": {
                        "zone": "us-central1-a"
                    },
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS"
                },
                "region": "us-central1",
                "masterInstanceName": "mysql-replica",
                "project": "test-project",
                "databaseVersion": "MYSQL_5_7"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0"
                ]
            },
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-replica-replica-usc1-1",
            "properties": {
                "name": "mysql-replica-replica-usc1-1",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "locationPreference": {
                        "zone": "us-central1-a"
                    },
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS"
                },
                "region": "us-central1",
                "masterInstanceName": "mysql-replica",
                "project": "test-project",
                "databaseVersion": "MYSQL_5_7"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0",
                    "mysql-replica-replica-usc1-1"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-replica-database-db1",
            "properties": {
                "project": "test-project",
                "instance": "mysql-replica",
                "name": "db1"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0",
                    "mysql-replica-replica-usc1-1",
                    "mysql-replica-database-db1"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-replica-database-db2",
            "properties": {
                "project": "test-project",
                "instance": "mysql-replica",
                "name": "db2"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0",
                    "mysql-replica-replica-usc1-1",
                    "mysql-replica-database-db1",
                    "mysql-replica-database-db2"
                ]
            },
            "type": "sqladmin.v1beta4.user",
            "name": "mysql-replica-user-user1-10.1.1.1",
            "properties": {
                "instance": "mysql-replica",
                "host": "10.1.1.1",
                "name": "user1"
            }
        }
    ]
}

MOCK_YAML_REPLICA_NO_ZONE_PREFERENCE = '''
env:
    name: mysql-replica
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
      zone: us-central1-c
    databases:
    - name: db1
    - name: db2
    users:
    - name: user1
      host: 10.1.1.1
'''
EXPECTED_OUTPUT_REPLICA_NO_ZONE_PREFERENCE = {
    "resources": [
        {
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-replica",
            "properties": {
                "name": "mysql-replica",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "locationPreference": {
                        "zone": "us-central1-c"
                    },
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS",
                    "backupConfiguration": {
                        "enabled": True,
                        "startTime": "02:00",
                        "binaryLogEnabled": True
                    }
                },
                "region": "us-central1",
                "project": "test-project",
                "databaseVersion": "MYSQL_5_7",
                "failoverReplica": {
                    "name": "mysql-replica-fo"
                }
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica"
                ]
            },
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-replica-replica-usc1-0",
            "properties": {
                "name": "mysql-replica-replica-usc1-0",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS"
                },
                "region": "us-central1",
                "masterInstanceName": "mysql-replica",
                "project": "test-project",
                "databaseVersion": "MYSQL_5_7"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-replica-database-db1",
            "properties": {
                "project": "test-project",
                "instance": "mysql-replica",
                "name": "db1"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0",
                    "mysql-replica-database-db1"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-replica-database-db2",
            "properties": {
                "project": "test-project",
                "instance": "mysql-replica",
                "name": "db2"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0",
                    "mysql-replica-database-db1",
                    "mysql-replica-database-db2"
                ]
            },
            "type": "sqladmin.v1beta4.user",
            "name": "mysql-replica-user-user1-10.1.1.1",
            "properties": {
                "instance": "mysql-replica",
                "host": "10.1.1.1",
                "name": "user1"
            }
        }
    ]
}

MOCK_YAML_REPLICA_INVALID_BACKUP = '''
env:
    name: mysql-replica
    project: test-project
properties:
    region: us-central1
    databaseVersion: MYSQL_5_7
    tier: db-n1-standard-1
    dataDiskSizeGb: 10
    dataDiskType: PD_HDD
    backupConfiguration:
      enabled: True  
    locationPreference:
      zone: us-central1-c
    databases:
    - name: db1
    - name: db2
    users:
    - name: user1
      host: 10.1.1.1
'''

EXPECTED_OUTPUT_REPLICA_INVALID_BACKUP = "Cannot have an SQL Instance without specifying backupConfiguration startTime setting."

MOCK_YAML_REPLICA_INVALID_USER = '''
env:
    name: mysql-replica
    project: test-project
properties:
    region: us-central1
    databaseVersion: MYSQL_5_7
    tier: db-n1-standard-1
    dataDiskSizeGb: 10
    backupConfiguration:
      startTime: '02:00'
    dataDiskType: PD_HDD
    locationPreference:
      zone: us-central1-c
    users:
    - name: user1
      host: '%'
'''

EXPECTED_OUTPUT_REPLICA_INVALID_USER = "You must define a restrictive host for database user access"

MOCK_YAML_NO_FAILOVER = '''
env:
    name: mysql-replica
    project: test-project
properties:
    region: us-central1
    databaseVersion: MYSQL_5_7
    tier: db-n1-standard-1
    dataDiskSizeGb: 10
    dataDiskType: PD_HDD
    backupConfiguration:
      startTime: '02:00'
    createFailoverReplica: False
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
EXPECTED_OUTPUT_NO_FAILOVER = {
    "resources": [
        {
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-replica",
            "properties": {
                "project": "test-project",
                "region": "us-central1",
                "databaseVersion": "MYSQL_5_7",
                "name": "mysql-replica",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "locationPreference": {
                        "zone": "us-central1-c"
                    },
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS",
                    "backupConfiguration": {
                        "enabled": True,
                        "startTime": "02:00",
                        "binaryLogEnabled": True
                    }
                }
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica"
                ]
            },
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-replica-replica-usc1-0",
            "properties": {
                "name": "mysql-replica-replica-usc1-0",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "locationPreference": {
                        "zone": "us-central1-a"
                    },
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS"
                },
                "region": "us-central1",
                "masterInstanceName": "mysql-replica",
                "project": "test-project",
                "databaseVersion": "MYSQL_5_7"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-replica-database-db1",
            "properties": {
                "project": "test-project",
                "instance": "mysql-replica",
                "name": "db1"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0",
                    "mysql-replica-database-db1"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-replica-database-db2",
            "properties": {
                "project": "test-project",
                "instance": "mysql-replica",
                "name": "db2"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-replica-usc1-0",
                    "mysql-replica-database-db1",
                    "mysql-replica-database-db2"
                ]
            },
            "type": "sqladmin.v1beta4.user",
            "name": "mysql-replica-user-user1-10.1.1.1",
            "properties": {
                "instance": "mysql-replica",
                "host": "10.1.1.1",
                "name": "user1"
            }
        }
    ]
}

MOCK_YAML_NO_ZONE_PREFERENCE = '''
env:
    name: mysql-replica
    project: test-project
properties:
    region: us-central1
    databaseVersion: MYSQL_5_7
    tier: db-n1-standard-1
    dataDiskSizeGb: 10
    dataDiskType: PD_HDD
    backupConfiguration:
      startTime: '02:00'
    createFailoverReplica: False
    databases:
    - name: db1
    - name: db2
    users:
    - name: user1
      host: 10.1.1.1
'''
EXPECTED_OUTPUT_NO_ZONE_PREFERENCE = {
    "resources": [
        {
            "type": "sqladmin.v1beta4.instance",
            "name": "mysql-replica",
            "properties": {
                "project": "test-project",
                "region": "us-central1",
                "databaseVersion": "MYSQL_5_7",
                "name": "mysql-replica",
                "settings": {
                    "ipConfiguration": {
                        "authorizedNetworks": [],
                        "ipv4Enabled": True,
                        "requireSsl": True
                    },
                    "dataDiskType": "PD_HDD",
                    "tier": "db-n1-standard-1",
                    "storageAutoResizeLimit": 0,
                    "storageAutoResize": True,
                    "maintenanceWindow": {
                        "day": 1,
                        "hour": 5
                    },
                    "dataDiskSizeGb": 10,
                    "activationPolicy": "ALWAYS",
                    "backupConfiguration": {
                        "enabled": True,
                        "startTime": "02:00",
                        "binaryLogEnabled": True
                    }
                }
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-replica-database-db1",
            "properties": {
                "project": "test-project",
                "instance": "mysql-replica",
                "name": "db1"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-database-db1"
                ]
            },
            "type": "sqladmin.v1beta4.database",
            "name": "mysql-replica-database-db2",
            "properties": {
                "project": "test-project",
                "instance": "mysql-replica",
                "name": "db2"
            }
        },
        {
            "metadata": {
                "dependsOn": [
                    "mysql-replica",
                    "mysql-replica-database-db1",
                    "mysql-replica-database-db2"
                ]
            },
            "type": "sqladmin.v1beta4.user",
            "name": "mysql-replica-user-user1-10.1.1.1",
            "properties": {
                "instance": "mysql-replica",
                "host": "10.1.1.1",
                "name": "user1"
            }
        }
    ]
}

class TestCloudSQLTemplate(unittest.TestCase):

    def test_happy_generate_config_master(self):
        yaml_input = yaml.load(MOCK_YAML_MASTER)
        yaml_with_dot_notation = common.dotdict(yaml_input)
        generate_config_return = cloudsql_instance_template.generate_config(yaml_with_dot_notation)
        self.assertEquals(generate_config_return, EXPECTED_OUTPUT_MASTER)

    def test_happy_generate_config_replica(self):
        yaml_input = yaml.load(MOCK_YAML_REPLICA)
        yaml_with_dot_notation = common.dotdict(yaml_input)
        generate_config_return = cloudsql_instance_template.generate_config(yaml_with_dot_notation)
        self.assertEquals(generate_config_return, EXPECTED_OUTPUT_REPLICA)

    def test_happy_generate_config_multiple_replicas(self):
        yaml_input = yaml.load(MOCK_YAML_MULTIPLE_REPLICAS)
        yaml_with_dot_notation = common.dotdict(yaml_input)
        generate_config_return = cloudsql_instance_template.generate_config(yaml_with_dot_notation)
        self.assertEquals(generate_config_return, EXPECTED_OUTPUT_MULTIPLE_REPLICAS)

    def test_happy_generate_config_replica_no_zone_preference(self):
        yaml_input = yaml.load(MOCK_YAML_REPLICA_NO_ZONE_PREFERENCE)
        yaml_with_dot_notation = common.dotdict(yaml_input)
        generate_config_return = cloudsql_instance_template.generate_config(yaml_with_dot_notation)
        with file('test.json', 'w+') as f:
            f.write(json.dumps(generate_config_return, indent=4, separators=(',', ': ')))
        self.assertEquals(generate_config_return, EXPECTED_OUTPUT_REPLICA_NO_ZONE_PREFERENCE)

    def test_happy_generate_config_no_failover(self):
        yaml_input = yaml.load(MOCK_YAML_NO_FAILOVER)
        yaml_with_dot_notation = common.dotdict(yaml_input)
        generate_config_return = cloudsql_instance_template.generate_config(yaml_with_dot_notation)
        self.assertEquals(generate_config_return, EXPECTED_OUTPUT_NO_FAILOVER)
    
    def test_happy_generate_config_no_zone_preference(self):
        yaml_input = yaml.load(MOCK_YAML_NO_ZONE_PREFERENCE)
        yaml_with_dot_notation = common.dotdict(yaml_input)
        generate_config_return = cloudsql_instance_template.generate_config(yaml_with_dot_notation)
        self.assertEquals(generate_config_return, EXPECTED_OUTPUT_NO_ZONE_PREFERENCE)

    def test_sad_generate_config_replica_invalid_backup(self):
        yaml_input = yaml.load(MOCK_YAML_REPLICA_INVALID_BACKUP)
        yaml_with_dot_notation = common.dotdict(yaml_input)
        with self.assertRaises(ValueError) as context:
            generate_config_return = cloudsql_instance_template.generate_config(yaml_with_dot_notation)
        self.assertEquals(context.exception.message, EXPECTED_OUTPUT_REPLICA_INVALID_BACKUP)

    def test_sad_generate_config_replica_invalid_failover(self):
        yaml_input = yaml.load(MOCK_YAML_REPLICA_INVALID_USER)
        yaml_with_dot_notation = common.dotdict(yaml_input)
        with self.assertRaises(ValueError) as context:
            generate_config_return = cloudsql_instance_template.generate_config(yaml_with_dot_notation)
        self.assertEquals(context.exception.message, EXPECTED_OUTPUT_REPLICA_INVALID_USER)
