# Copyright 2017 Google Inc. All rights reserved.
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

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

    
def GenerateConfig(context):
    """Generates deployment configuration """
  
    resources = []

    prefix = context.env['name']
    hc_name = prefix + '-hc'
    fw_name = prefix + '-hc-fw'
    zones = context.properties['zones']
    region = context.properties['region']
    nat_gw_tag = context.properties['nat-gw-tag'] 

    network_name = context.properties['network'].split('/')[-1]
    subnetwork_name = context.properties['subnetwork'].split('/')[-1]

    # A health check to be used by managed instance groups
    resources.append({
        'name': hc_name,
        'type': 'compute.v1.httpHealthCheck',
        'properties': {
            'port': 80,
            'requestPath': '/health-check',
            'healthyThreshold': 1,
            'unhealthyThreshold': 5,
            'checkIntervalSec': 30
        }
    })


  # Firewall rule that allows the health check to work. See
  # https://cloud.google.com/compute/docs/load-balancing/health-checks#health_check_source_ips_and_firewall_rules.
    resources.append({
        'name': fw_name,
        'type': 'compute.v1.firewall',
        'properties': {
            'network': context.properties['network'],
            'sourceRanges': ['130.211.0.0/22', '35.191.0.0/16', '130.211.0.0/22'],
            'targetTags': [nat_gw_tag],
            'description': 'rule for allowing all health check traffic',
            'allowed': [{
                'IPProtocol': 'TCP',
                'ports': [80]
            }]
        }
    })
  
    # create an instance template for the Instance Group Manager
    # https://cloud.google.com/vpc/docs/special-configurations#multiple-natgateways
    instance_template_name = prefix  + '-itpl'
    resources.append({
        'name': instance_template_name,
        'type': 'compute.v1.instanceTemplate',
        'properties': {
            'properties': {
            'disks': [{
                'deviceName': 'boot',
                'type': 'PERSISTENT',
                'mode': 'READ_WRITE',
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                'sourceImage': context.properties['imageType'],
                'diskType': context.properties['diskType'],
                'diskSizeGb': context.properties['diskSizeGb']
                }
            }],
            'tags': {
                'items': [context.properties['nat-gw-tag']]
            },
            'zone': zones[0],
            'machineType': context.properties['machineType'],
            'metadata': {
                'items': [{
                'key': 'startup-script',
                'value': context.properties['startupScript']
                },
                ]
            },
            'serviceAccounts': [{
                'email': 'default',
                'scopes': [
                # The following scope allows an instance to create runtime variable resources.
                'https://www.googleapis.com/auth/cloudruntimeconfig'
                ]
            }], 
            'canIpForward': True,
            'networkInterfaces': [{
            'accessConfigs': [{
                'name': 'External-IP',
                'type': 'ONE_TO_ONE_NAT' }] 
            }]
            }
        }
    })
  
    nat_gw_list = []
    nat_externalip_list = []
    instance_group_manager_list = []
    route_list = []
    
    # Create a NAT gateways for each zone specified in zones property 
    i = 1
    for zone in context.properties['zones']:
        #reserve a static IP address
        ip_name = prefix  + '-ip-' +  str(i)
        resources.append({
            'name': ip_name,
            'type': 'compute.v1.address',
            'properties': {
            'region': context.properties['region'],
            'addressType': 'EXTERNAL',
            'network-tier': 'STANDARD'
            }
        }) 
        nat_externalip_list.append('$(ref.' + ip_name + '.address)')
        
        # create NAT gateway vm
        template_name = prefix  + '-gw-' +  str(i) + '-' + zone
        nat_gw_list.append(template_name)
        resources.append({
            'name': template_name,
            'type': 'compute.v1.instance',
            'properties': {
            'disks': [{
                'deviceName': 'boot',
                'type': 'PERSISTENT',
                'mode': 'READ_WRITE',
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                'sourceImage': context.properties['imageType'],
                'diskType': 'zones/' + zone + '/diskTypes/' +  context.properties['diskType'],
                'diskSizeGb': context.properties['diskSizeGb']
                }
            }],
            'tags': {
                'items': [context.properties['nat-gw-tag']]
            },
            'zone': zone,
            'machineType': 'zones/' + zone + '/machineTypes/' + context.properties['machineType'],
            'metadata': {
                'items': [{
                'key': 'startup-script',
                'value': context.properties['startupScript']
                },
                ]
            },
            'serviceAccounts': [{
                'email': 'default',
                'scopes': [
                # The following scope allows an instance to create runtime variable resources.
                'https://www.googleapis.com/auth/cloudruntimeconfig'
                ]
            }], 
            'canIpForward': True,
            'networkInterfaces': [{
                'network': context.properties['network'],
                'subnetwork': context.properties['subnetwork'],
            'accessConfigs': [{
                'name': 'External-IP',
                'type': 'ONE_TO_ONE_NAT',
                'natIP': '$(ref.' + ip_name + '.address)' }] 
            }]
            }
        })

        #create Instance Group Manager for Health Check and AutoHealing
        instance_group_manager_name = prefix + '-igm-' + str(i) + '-' + zone
        instance_group_manager_list.append(instance_group_manager_name)
        resources.append({
            'name': instance_group_manager_name,
            'type': 'compute.v1.instanceGroupManager',
            'properties': {
            'instanceTemplate': '$(ref.' + instance_template_name + '.selfLink)',
            'baseInstanceName': template_name,
            'zone': zone,
            'targetSize': 1,
            'autoHealingPolicies': [{
                'healthCheck': '$(ref.' + hc_name + '.selfLink)',
                'initialDelaySec': 120
            }] 
            }
        }) 

        
        #create a route that will allow to use the NAT gateway VM as a next hop
        route_priority = context.properties['routePriority'] + 100
        route_name = prefix + '-route-' + str(i) + '-' + zone
        route_list.append(route_name)
        resources.append({
            'name': route_name,
            'type': 'compute.v1.route',
            'properties': {
            'network': context.properties['network'],
            'tags': [context.properties['nated-vm-tag']],
            'destRange': '0.0.0.0/0',
            'priority': route_priority,
            'nextHopInstance': '$(ref.' + template_name + '.selfLink)' 
            }
        }) 
        i += 1

    firewall_name = prefix + '-fw'
    #create a firewall rule that will allow all traffic through the NAT gateway VMs to internet
    resources.append({
        'name': firewall_name,
        'type': 'firewall.py',
        'properties':{
        'network': network_name, 
        'rules':[{
            'name': firewall_name,
            'allowed':[{
                'IPProtocol': 'tcp',
                'ports':[
                    '1-65535',
                ],
                },{
                'IPProtocol': 'udp',
                'ports':[
                    '1-65535',
                ],
                },{
                'IPProtocol': 'icmp'
                }],
            'description': 'rule for allowing all traffic out through NAT GW',
            'direction': 'INGRESS',
            'sourceRanges':[context.properties['nat-ip-range'],],
        }]
        }
    })

    # outputs
    return {
            'resources':
                resources,
            'outputs':
                [
                {
                    'name': 'natGatewayName',
                    'value': nat_gw_list
                },{
                    'name': 'natExternalIP',
                    'value': nat_externalip_list
                },{
                    'name': 'networkName',
                    'value': network_name
                },
                {
                    'name': 'subnetworkName',
                    'value': subnetwork_name
                },
                {
                    'name': 'firewallRuleName',
                    'value': firewall_name
                },
                {
                    'name': 'routeName',
                    'value': route_list
                },
                {
                    'name': 'nat-gw-tag',
                    'value': context.properties['nat-gw-tag']
                },
                {
                    'name': 'nated-vm-tag',
                    'value': context.properties['nated-vm-tag']
                },
                {
                    'name': 'zones',
                    'value': context.properties['zones']
                },
                {
                    'name': 'region',
                    'value': context.properties['region']
                },
                {
                    'name': 'instanceTemplateName',
                    'value': instance_template_name
                },
                {
                    'name': 'instanceGroupManager',
                    'value': instance_group_manager_list
                },
                {
                    'name': 'healthCheck',
                    'value': hc_name
                },
                ]
    }
