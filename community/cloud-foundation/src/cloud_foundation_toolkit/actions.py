from cloud_foundation_toolkit import LOG
from cloud_foundation_toolkit.deployment import ConfigList, Deployment

def create(args):
    configs = ConfigList(args.config)
    [Deployment(c).create(preview=args.preview) for c in configs]

def delete(args):
    configs = ConfigList(args.config)
    [Deployment(c).delete() for c in configs[::-1]]

def get(args):
    configs = ConfigList(args.config)
    [Deployment(c).get() for c in configs]

def apply(args):
    configs = ConfigList(args.config)
    [Deployment(c).apply(preview=args.preview) for c in configs]

def update(args):
    configs = ConfigList(args.config)
    [Deployment(c).update(preview=args.preview) for c in configs]


