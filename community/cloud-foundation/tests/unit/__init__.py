#import logging
#import os
#import sys

# Gloud is not in Pypi, so the system installed version is
# required. Here gcloud's root dir is added to sys path
#CLOUDSDK_ROOT_DIR = os.environ.get('CLOUDSDK_ROOT_DIR')

#if not CLOUDSDK_ROOT_DIR:
#    raise SystemExit('Cannot find gcloud root dir')
#sys.path.insert(1, '{}/lib/third_party'.format(CLOUDSDK_ROOT_DIR))
#sys.path.insert(1, '{}/lib'.format(CLOUDSDK_ROOT_DIR))


# Setup logging and expose Logger object to the rest of the project
#LOG = logging.getLogger("cft")
#LOG.addHandler(logging.StreamHandler())
#LOG.propagate = False
