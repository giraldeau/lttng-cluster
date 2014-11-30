from distutils.core import setup

config = {
    'name': 'LTTng Cluster',
    'description': 'Setup and trace a cluster using LTTng',
    'author': 'Francis Giraldeau',
    'author_email': 'francis.giraldeau@gmail.com.',
    'url': 'https://github.com/giraldeau/lttng-cluster',
    'download_url': 'TBD',
    'version': '0.1dev',
    'install_requires': ['fabric'],
    'packages': ['lttngcluster',
                 'lttngcluster/commands',
                 'lttngcluster/experiments'],
    'scripts': ['bin/lttng-cluster'],
}

setup(**config)