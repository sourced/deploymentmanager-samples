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
"""Creates custom Routes."""


def generate_config(context):
    """ Entry point for the deployment resources """

    network_name = generate_network_url(
        context.env['project'],
        context.properties['network']
    )

    resources = []
    for i, route in enumerate(context.properties['routes'], 1000):

        # Common route properties
        properties = {
            'network': network_name,
            'tags': route['tags'],
            'priority': route.get('priority',
                                  i),
            'destRange': route['destRange']
        }

        # Check the route type and fill the respective fields
        if route['routeType'] == 'ipaddress':
            properties['nextHopIp'] = route.get('nextHopIp')
        elif route['routeType'] == 'instance':
            instance_name = route.get('instanceName')
            zone = route.get('zone', '')
            properties['nextHopInstance'] = generate_instance_url(
                context.env['project'],
                zone,
                instance_name
            )
        elif route['routeType'] == 'gateway':
            gateway_name = route.get('gatewayName')
            properties['nextHopGateway'] = generate_gateway_url(
                context.env['project'],
                gateway_name
            )
        elif route['routeType'] == 'vpntunnel':
            vpn_tunnel_name = route.get('vpnTunnelName')
            region = route.get('region', '')
            properties['nextHopVpnTunnel'] = generate_vpn_tunnel_url(
                context.env['project'],
                region,
                vpn_tunnel_name
            )

        resources.append(
            {
                'name': route['name'],
                'type': 'compute.v1.route',
                'properties': properties
            }
        )

    return {'resources': resources}


def generate_network_url(project, network):
    """Format the resource name to a resource URI"""
    return 'projects/{}/global/networks/{}'.format(project, network)


def generate_instance_url(project, zone, instance):
    """Format the resource name to a resource URI"""
    return 'projects/{}/zones/{}/instances/{}'.format(project, zone, instance)


def generate_gateway_url(project, gateway):
    """Format the resource name to a resource URI"""
    return 'projects/{}/global/gateways/{}'.format(project, gateway)


def generate_vpn_tunnel_url(project, region, vpn_tunnel):
    """Format the resource name to a resource URI"""
    return 'projects/{}/regions/{}/vpnTunnels/{}'.format(
        project,
        region,
        vpn_tunnel
    )
