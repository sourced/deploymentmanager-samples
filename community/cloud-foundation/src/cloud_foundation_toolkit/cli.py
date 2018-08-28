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
import sys

from cloud_foundation_toolkit import LOG
from cloud_foundation_toolkit.deployment import Config, Deployment, run


def build_common_args(parser):
    """ Configures arguments to all actions/subparsers """

    parser.add_argument(
        'config',
        type=str,
        nargs='+',
        help=('The path to the config files or directory')
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
        'upsert',
        'delete',
        'render',
        'validate'
    ]

    subparsers = {}
    for action in actions:
        subparsers[action] = subparser_obj.add_parser(action)
        build_common_args(subparsers[action])

    # action-specficic arguments
    #
    # update
    subparsers['update'].add_argument(
        '--preview',
        '-p',
        action='store_true',
        default=False,
        help='Preview changes'
    )

    # upsert
    subparsers['upsert'].add_argument(
        '--preview',
        '-p',
        action='store_true',
        default=False,
        help='Preview changes'
    )
    return parser.parse_args(args)


def main():
    """ CLI entry point"""

    # Parse CLI arguments
    args = parse_args(sys.argv[1:])

    # logging
    LOG.setLevel(args.verbosity.upper())

    config = Config(args.config)
#    [print(c) for c in config]
    [Deployment(c).upsert(preview=args.preview) for c in config]


if __name__ == '__main__':
    main()
