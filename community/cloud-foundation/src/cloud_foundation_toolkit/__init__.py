import logging

LOG = logging.getLogger("cft")
LOG.addHandler(logging.StreamHandler())
LOG.propagate = False
