import logging


# Setup logging and expose Logger object to the rest of the project
LOG = logging.getLogger("cft")
LOG.addHandler(logging.StreamHandler())
LOG.propagate = False
