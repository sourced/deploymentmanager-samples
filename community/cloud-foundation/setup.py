#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup


def get_version():
    with open('VERSION') as f:
        return f.readline().rstrip()


def get_install_requirements():
    with open('requirements/install.txt') as f:
        return [l.strip() for l in f if l.strip() and not l.startswith('#')]


def get_dev_requirements():
    with open('requirements/development.txt') as f:
        return [l.strip() for l in f if l.strip() and not l.startswith('#')]


config = {
    'name': 'cloud-foundation-toolkit',
    'version': get_version(),
    'description': 'Cloud Foundation Toolkit',
    'author': 'Gustavo Baratto',
    'author_email': 'gbaratto@gmail.com',
    'url': 'https://github.com/GoogleCloudPlatform/deploymentmanager-sample',
    'packages': find_packages('src'),
    'package_dir': {'': 'src'},
#    'entry_points': {
#        'console_scripts': ['cft=cloud_foundation_toolkit.cli:main']
#    },
    'data_files': [
        ('bin', 'src/cft'),
        ('bin', 'src/cftenv')

    ],
    'install_requires': get_install_requirements(),
#    'tests_require': get_dev_requirements(),
    'include_package_data': True
}


setup(**config)
