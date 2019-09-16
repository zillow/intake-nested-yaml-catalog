# OPTIONAL, but recommended:
# this block is useful for specifying when a build should
# use the 'release' version. it allows specifying a release version
# with an additional argument in the setup.py:
# $ python setup.py upload --release
import sys
is_release = False
if "--release" in sys.argv:
    sys.argv.remove("--release")
    is_release = True


import os
from setuptools import setup, find_packages

base = os.path.dirname(os.path.abspath(__file__))

setup(
    name="intake-nested-yaml-catalog",
    setup_requires=["vcver", "setuptools-parcels"],
    vcver={"path": base, "is_release": is_release},
    description="Intake single YAML hierarchical catalog.",
    author="Zillow AI Platform",
    author_email="",
    long_description=open('README.rst').read(),
    packages=find_packages(),
    install_requires=[
        'vcver',
        'intake',
        'pandas',
        'PyYAML',
        'deepmerge',
    ],
    python_requires=">=3.6",
    entry_points={
        'intake.drivers': [
            'nested_yaml_cat = intake_nested_yaml_catalog.nested_yaml_catalog:NestedYAMLFileCatalog',
        ]
    },
)
