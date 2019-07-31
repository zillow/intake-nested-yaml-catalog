import os
from setuptools import setup, find_packages

BASE = os.path.dirname(os.path.abspath(__file__))

setup(
    name="intake-nested-yaml-catalog",
    setup_requires=["vcver", "setuptools-parcels"],
    vcver={"path": BASE},
    description="Intake single YAML hierarchical catalog.",
    author="Zillow AI Platform",
    author_email="aiplat@zillow.com",
    long_description=open('README.rst').read(),
    packages=find_packages(),
    install_requires=[
        'intake',
        'pandas',
        'PyYAML',
        'deepmerge',
        'orbital-core'
    ],
)
