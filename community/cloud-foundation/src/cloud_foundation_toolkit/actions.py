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

def sync(args):
    configs = ConfigList(args.config)
    [Deployment(c).sync(preview=args.preview) for c in configs]

def update(args):
    configs = ConfigList(args.config)
    [Deployment(c).upsert(preview=args.preview) for c in configs]


