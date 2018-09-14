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
from cloud_foundation_toolkit.deployment import ConfigList, Deployment


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


def create(args):
    """ Create deployments """

    config_list = ConfigList(get_config_files(args.config))
    for configs in config_list:
        for config in configs:
            Deployment(config).create(preview=args.preview)


def delete(args):
    """ Delete deployments """

    config_list = ConfigList(get_config_files(args.config))
    for configs in config_list[::-1]:
        for config in configs[::-1]:
            Deployment(config).delete()


def get(args):
    """ Get deployments """

    config_list = ConfigList(get_config_files(args.config))
    for configs in config_list:
        for config in configs:
            Deployment(config).get()


def apply(args):
    """ Apply deployments """

    config_list = ConfigList(get_config_files(args.config))
    for configs in config_list:
        for config in configs:
            Deployment(config).apply(preview=args.preview)


def update(args):
    """ Update deployments """

    config_list = ConfigList(get_config_files(args.config))
    for configs in config_list:
        for config in configs:
            Deployment(config).update(preview=args.preview)
