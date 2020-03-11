import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = ["pygcn", "scimma-client >= 0.0.4"]

setuptools.setup(
    name="scimma-gcn2scimma",
    version="0.0.1",
    author="Ron Tapia",
    author_email="rdt12@psu.edu",
    description="Read from GCN/TAM and write to SCiMMA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scimma/gcn2scimma",
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: MMA',
        'Topic :: Scientific/Engineering :: Multi-Messenger Astronomy',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
    ],
    python_requires='>=3.6',
)
