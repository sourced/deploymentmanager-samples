#!/usr/bin/env python
# Copyright 2017 Gustavo Baratto. All Rights Reserved.
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


""" Cloud Foundation Toolkit CLI """

from __future__ import print_function
import argparse
#import logging
import os
import sys

# Gloud is not in Pypi, so the system installed version is
# required. Here gcloud's root dir is added to sys path
CLOUDSDK_ROOT_DIR = os.environ.get('CLOUDSDK_ROOT_DIR')

if not CLOUDSDK_ROOT_DIR:
    raise SystemExit('Cannot find gcloud root dir')
sys.path.insert(1, '{}/lib/third_party'.format(CLOUDSDK_ROOT_DIR))
sys.path.insert(1, '{}/lib'.format(CLOUDSDK_ROOT_DIR))


# Now we're clear to import local modules that will make use
# of gcloud code
from . import LOG
from deployment import Config
import deployment

def build_common_args(parser):
    """ Configures arguments to all actions/subparsers """

    parser.add_argument(
        'config',
        type=str,
        help=('The path to the config file or directory')
    )


def parse_args(args):
    """parse CLI options """
    parser = argparse.ArgumentParser('Cloud Foundation Toolkit')

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Not implemented yet'
    )
    parser.add_argument(
        '--verbosity',
        '-v',
        default='warning',
        help='The log level'
    )

    # subparser for each action
    subparser_obj = parser.add_subparsers(dest='action')
    actions = [
        'create',
        'update',
        'delete',
        'render',
        'validate'
    ]

    subparsers = {}
    for action in actions:
        subparsers[action] = subparser_obj.add_parser(action)
        build_common_args(subparsers[action])

    return parser.parse_args(args)


def main():
    """ CLI entry point"""

    # Parse CLI arguments
    args = parse_args(sys.argv[1:])

    # logging
    LOG.setLevel(args.verbosity.upper())
    deployment.run(args.config)

#    config = Config(args.config)
#    print(config.deployments[0].target_config)
#    config.deploy()
#    import yaml_utils
#    out = yaml_utils.get_dm_item("dm://sourced-gus-1/my-network-prod/output/networkUrl")
#    print(out)
#    print(config.obj)
#    print('==============================')
#    [print(d.config) for d in config.deployments]
#    print(config.deployments)
#    print(config.deployments[0].target_config)
#    config.deployments[0].run()


if __name__ == '__main__':
    main()
