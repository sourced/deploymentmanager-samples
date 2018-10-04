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
from cloud_foundation_toolkit.actions import execute


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
#    parser = argparse.ArgumentParser('Cloud Foundation Toolkit')
    parser = argparse.ArgumentParser('cft')

    parser.add_argument(
        '--project',
        type=str,
        default='',
        help='The GCP project name'
    )
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
        'apply',
        'create',
        'delete',
        'update'
    ]

    subparsers = {}
    for action in actions:
        subparsers[action] = subparser_obj.add_parser(action)
        build_common_args(subparsers[action])

    # action-specficic arguments
    #
    # create
    subparsers['create'].add_argument(
        '--preview',
        '-p',
        action='store_true',
        default=False,
        help='Preview changes'
    )

    # update
    subparsers['update'].add_argument(
        '--preview',
        '-p',
        action='store_true',
        default=False,
        help='Preview changes'
    )

    # upsert
    subparsers['apply'].add_argument(
        '--preview',
        '-p',
        action='store_true',
        default=False,
        help='Preview changes'
    )
    subparsers['apply'].add_argument(
        '--reverse',
        '-r',
        action='store_true',
        default=False,
        help='Whether to apply changes in reverse order'
    )

    return parser.parse_args(args)


def main():
    """ CLI entry point"""

    # Parse CLI arguments
    args = parse_args(sys.argv[1:])

    # logging
    LOG.setLevel(args.verbosity.upper())
    execute(args)
#    globals()[args.action](args)


if __name__ == '__main__':
    main()
