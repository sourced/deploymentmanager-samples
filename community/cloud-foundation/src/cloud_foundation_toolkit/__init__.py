import logging
import pkg_resources


# Setup logging and expose Logger object to the rest of the project
LOG = logging.getLogger("cft")
LOG.addHandler(logging.StreamHandler())
LOG.propagate = False

__VERSION__ = pkg_resources.get_distribution(__name__).version
