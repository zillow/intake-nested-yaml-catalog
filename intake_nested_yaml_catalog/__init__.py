from ._version import get_versions

__version__ = get_versions()['version']

# Importing here for Intake.autodiscover() to discover these catalog plugins
from intake_nested_yaml_catalog.nested_yaml_catalog import YAMLCatalog, YAMLFileNestedCatalog  # noqa: F401
