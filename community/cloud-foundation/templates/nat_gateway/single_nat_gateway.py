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

""" Generates configuration for a single NAT gateway. """


def generate_config(context):
  """ Generates deployment configuration. """

  prefix = context.env['name']
  zone = context.properties['zone']

  resources = []
  
  """ Reserve a static External IP address to be used for the nat IP. """
  ip_name = prefix + '-ip'
  resources.append({
    'name': ip_name,
    'type': 'compute.v1.address',
    'properties': {
      'region': context.properties['region'],
      'addressType': 'EXTERNAL',
      'network-tier': 'STANDARD'
    }
  })  

  """ Create an instance template that points to a reserved static IP address. """
  template_name = prefix + '-gw'
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

  """ Create a route that will allow to use the NAT gateway VM as a next hop. """
  route_name = prefix + '-route'
  resources.append({
    'name': route_name,
    'type': 'compute.v1.route',
    'properties': {
      'network': context.properties['network'],
      'tags': [context.properties['nated-vm-tag']],
      'destRange': '0.0.0.0/0',
      'priority': context.properties['routePriority'],
      'nextHopInstance': '$(ref.' + template_name + '.selfLink)' 
    }
  }) 

  """ Create a firewall rule that will allow all traffic through the NAT gateway VM to internet. """
  network_name = context.properties['network'].split('/')[-1]
  subnetwork_name = context.properties['subnetwork'].split('/')[-1]
  firewall_name = prefix + '-fw'
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

  """ Outputs. """
  return {
    'resources':
        resources,
    'outputs':[
      {
        'name': 'natGatewayName',
        'value': template_name
      },{
        'name': 'natExternalIP',
        'value': '$(ref.' + ip_name + '.address)'
      },{
        'name': 'networkName',
        'value': network_name
      },{
        'name': 'subnetworkName',
        'value': subnetwork_name
      },{
        'name': 'firewallRuleName',
        'value': firewall_name
      },{
        'name': 'routeName',
        'value': route_name
      },{
        'name': 'nat-gw-tag',
        'value': context.properties['nat-gw-tag']
      },{
        'name': 'nated-vm-tag',
        'value': context.properties['nated-vm-tag']
      },{
        'name': 'zone',
        'value': context.properties['zone']
      },{
        'name': 'region',
        'value': context.properties['region']
      },
    ]
  }