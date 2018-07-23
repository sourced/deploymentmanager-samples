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

    name = context.properties.get('name', context.env['name'])
    network_name = generate_network_name_url(
        context.env['project'],
        context.properties['network']
        )

    # Common route properties
    properties = {
        "network": network_name,
        "tags": context.properties["tags"],
        "priority": context.properties["priority"],
        "destRange": context.properties["destRange"]
    }

    # Check the route type and fill the respective fields
    if context.properties["routeType"] == "IP":
        properties["nextHopIp"] = context.properties.get("nextHopIp")
    elif context.properties["routeType"] == "INSTANCE":
        instance_name = context.properties.get("instanceName")
        zone = context.properties.get("zone", "")
        hop_instance_name = generate_instance_name_url(
            context.env['project'],
            zone,
            instance_name
        )
        properties["nextHopInstance"] = hop_instance_name
    elif context.properties["routeType"] == "GATEWAY":
        gateway_name = context.properties.get("gatewayName")
        hop_gateway_name = generate_gateway_name_url(
            context.env['project'],
            gateway_name
        )
        properties['nextHopGateway'] = hop_gateway_name
    elif context.properties["routeType"] == "VPNTUNNEL":
        vpn_tunnel_name = context.properties.get("vpnTunnelName")
        region = context.properties.get("region", "")
        hop_vpn_tunnel_name = generate_vpn_tunnel_url(
            context.env['project'],
            region,
            vpn_tunnel_name
        )
        properties["nextHopVpnTunnel"] = hop_vpn_tunnel_name

    resources = [
        {
            "name": name,
            "type": "compute.v1.route",
            "properties": properties
        }
    ]

    return {"resources": resources}


def generate_network_name_url(project, network):
    return 'projects/{}/global/networks/{}'.format(
        project,
        network
    )


def generate_instance_name_url(project, zone, instance):
    return 'projects/{}/zones/{}/instances/{}'.format(
        project,
        zone,
        instance
    )


def generate_gateway_name_url(project, gateway):
    return 'projects/{}/global/gateways/{}'.format(
        project,
        gateway
    )


def generate_vpn_tunnel_url(project, region, vpn_tunnel):
    return 'projects/{}/regions/{}/vpnTunnels/{}'.format(
        project,
        region,
        vpn_tunnel
    )
