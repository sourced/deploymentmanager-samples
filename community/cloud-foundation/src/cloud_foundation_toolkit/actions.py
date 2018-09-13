from cloud_foundation_toolkit import LOG
from cloud_foundation_toolkit.deployment import ConfigList, Deployment


def create(args):
    config_list = ConfigList(args.config)
    for configs in config_list:
        for config in configs:
            Deployment(config).create(preview=args.preview)


def delete(args):
    config_list = ConfigList(args.config)
    for configs in config_list[::-1]:
        for config in configs[::-1]:
            Deployment(config).delete()


def get(args):
    config_list = ConfigList(args.config)
    for configs in config_list:
        for config in configs:
            Deployment(config).get()


def apply(args):
    config_list = ConfigList(args.config)
    for configs in config_list:
        for config in configs:
            Deployment(config).apply(preview=args.preview)


def update(args):
    config_list = ConfigList(args.config)
    for configs in config_list:
        for config in configs:
            Deployment(config).update(preview=args.preview)
