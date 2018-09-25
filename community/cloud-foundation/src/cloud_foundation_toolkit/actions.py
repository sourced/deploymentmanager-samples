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
""" Deployment Actions """
import glob
from cloud_foundation_toolkit import LOG
from cloud_foundation_toolkit.deployment import ConfigGraph, Deployment
from apitools.base.py import exceptions as apitools_exceptions


# To avoid code repetition this ACTION_MAP is used to translate the 
# args provided to the cmd line to the appropriate method of the
# deployment object
ACTION_MAP = {
    'apply':  {'preview': 'preview'},
    'create': {'preview': 'preview'},
    'update': {'preview': 'preview'}
}

def get_config_files(config):
    """ Build a list of config files """

    config_list = config
    dir_config_list = []

    # Can be multiple files or directories
    for config_args in config:

        # Try to search as a directory
        files = glob.glob(config_args + '/*')

        if files:
            # Support only *.yaml, *.yml and *.jinja files
            tmp_list = [
                f for f in files if '.yaml' in f or '.yml' in f or '.jinja' in f
            ]

            dir_config_list.extend(tmp_list)

            LOG.debug(
                'Found config config files %s in directory %s',
                tmp_list,
                config_args
            )

    if dir_config_list:
        config_list = dir_config_list

    LOG.debug('Config files %s', config_list)

    return config_list


def execute(args):
    action = args.action

    if action == 'delete' or (hasattr(args, 'reverse') and args.reverse):
        graph = reversed(ConfigGraph(get_config_files(args.config)))
    else:
        graph = ConfigGraph(get_config_files(args.config))

    arguments = {}
    for k, v in vars(args).items():
        if k in ACTION_MAP.get(action, {}):
            arguments[ACTION_MAP[action][k]] = v

    LOG.debug('Excuting %s on %s with arguments %s',
        args.action, args.config, arguments
    )

    for level in graph:
        for config in level:
            LOG.debug('%s config %s', action, config.deployment)
            deployment = Deployment(config)
            method = getattr(deployment, action)
            method(**arguments)

