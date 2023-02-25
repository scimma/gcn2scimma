import os
from setuptools import setup

# read in README
this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, 'README.md'), 'rb') as f:
    long_description = f.read().decode().strip()

# requirements
install_requires = [
    "hop-client >= 0.1",
    "pygcn",
    "schedule",
    "requests",
    "toml",
    "boto3"
]
extras_require = {
    'dev': [
        'autopep8',
        'flake8 >= 3.3.0',
        'pytest >= 5.0, < 5.4',
        'pytest-console-scripts',
        'pytest-cov',
        'pytest-runner',
        'twine',
    ],
}

setup(
    name = 'stream2hop',
    description = 'Publish GCNs and TNS to scimma',
    url = 'https://github.com/scimma/gcn2hop',
    author = 'Ron Tapia',
    license = 'GPLv3+',
    packages = ['stream2hop'],
    entry_points = {
        'console_scripts': [
            'stream2hop = stream2hop.__main__:main',
        ],
    },

    python_requires = '>=3.6.*',
    install_requires = install_requires,
    extras_require = extras_require,
    setup_requires = ['setuptools_scm'],
    use_scm_version = {
        'write_to': 'stream2hop/_version.py'
    },

    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],

)
