import copy
from pathlib import Path

import vcver
import yaml
from intake.catalog.exceptions import ValidationError
from intake.catalog.local import YAMLFileCatalog
from intake.utils import yaml_load
from deepmerge import always_merger


def to_yaml_nested_cat_desugared(yaml_nested_cat: dict):
    """
    Converts from yaml_nested_cat structure to yaml_nested_cat_desugared structure.
    """
    return dict(sources=to_yaml_nested_cat_desugared_helper(copy.deepcopy(yaml_nested_cat)))


def to_yaml_nested_cat_desugared_helper(yaml_nested_cat: dict):
    for key, value in yaml_nested_cat.items():
        if isinstance(value, dict) and 'driver' not in value:
            # This becomes a YAMLFileNestedCatalogDesugared, a step in the taxonomy
            description = value.pop('description', None)
            new_sources = to_yaml_nested_cat_desugared_helper(value)
            yaml_nested_cat[key] = dict(
                driver='yaml_nested_cat_desugared',
                metadata=dict(sources=new_sources)
            )
            if description:
                yaml_nested_cat[key]['description'] = description
    return yaml_nested_cat


def to_yaml_nested_cat(yaml_nested_cat_desugared: dict, cls_name: str):
    """
    Converts from yaml_nested_cat_desugared structure to yaml_nested_cat structure.
    """
    # unwind the first 'sources'
    return to_yaml_nested_cat_helper(yaml_nested_cat_desugared['sources'], cls_name)


def to_yaml_nested_cat_helper(yaml_nested_cat_desugared: dict, cls_name: str):
    ret = {}
    for key, value in yaml_nested_cat_desugared.items():
        if 'driver' in value and (
                value['driver'] == YAMLFileNestedCatalogDesugared.name or value['driver'] == cls_name):
            # unwind this entry
            node = copy.deepcopy(value)
            del node['driver']
            nested = to_yaml_nested_cat_helper(node['metadata']['sources'], cls_name)
            # new_node = {**node, **nested}
            new_node = always_merger.merge(node, nested)

            # cleanup
            del new_node['metadata']['sources']
            for k in list(node):
                if new_node[k] == {}:
                    del new_node[k]

            ret[key] = new_node
        else:
            ret[key] = value

    # clean up empty dicts
    return ret



class YAMLFileNestedCatalogDesugared(YAMLFileCatalog):
    """
    Catalog as described by a single YAML file with hierarchy.
    The catalog entries are defined within `metadata`.

    The format of this YAML is hard to work with but lends to simple reuse of YAMLFileCatalog parse().
    YAMLFileNestedCatalog is a syntactic sugar translator to this hard to use format.

    Example:
      sources:
        user:
          driver: yaml_nested_cat_desugared
          metadata:
            sources:
              user_profile:
                args:
                  urlpath: s3://foo
                driver: parquet
    """

    version = vcver.get_version()
    container = 'catalog'
    partition_access = None
    name = 'yaml_nested_cat_desugared'

    def __init__(self, **kwargs):
        super(YAMLFileNestedCatalogDesugared, self).__init__(path=kwargs.get("name", ""), **kwargs)

    def _load(self, reload=False):
        self._dir = self.metadata['catalog_dir']
        text = yaml.dump(self.metadata, default_flow_style=False)
        self._yaml_text = text

        # Reuse default YAMLFileCatalog YAML parser
        # parse() does the heavy lifting of loading the catalog
        super().parse(text)

    def yaml(self, with_plugin=False):
        """Return YAML representation of this data-source

        The output may be roughly appropriate for inclusion in a YAML
        catalog. This is a best-effort implementation

        Parameters
        ----------
        with_plugin: bool
            If True, create a "plugins" section, for cases where this source
            is created with a plugin not expected to be in the global Intake
            registry.
        """
        from yaml import dump
        data = self._yaml(with_plugin=with_plugin)

        # convert back to syntactic sugar of yaml_nested_cat
        yaml_nested_cat = to_yaml_nested_cat(data, self.classname)
        return dump(yaml_nested_cat, default_flow_style=False)


class YAMLFileNestedCatalog(YAMLFileCatalog):
    """
    Catalog as described by a single YAML file with hierarchy.
    This is syntactic sugar of `YAMLFileNestedCatalogDesugared`.
    Example:
    ```
        entity:
            description: "description"
            customer:
              customer_attributes:
                args:
                  urlpath: s3://foo
                driver: parquet
            user:
              user_profile:
                args:
                  urlpath: s3://foo
                driver: parquet
    ```

    Clean_attributes can be accessed as such:
    >>> catalog.entity.customer.customer_attributes.describe()
    """
    version = vcver.get_version()
    container = 'catalog'
    partition_access = None
    name = 'yaml_nested_cat'

    def __init__(self, path, autoreload=True, **kwargs):
        """
        Parameters
        ----------
        path: str
            Location of the file to parse (can be remote)
        reload : bool
            Whether to watch the source file for changes; make False if you want
            an editable Catalog
        """
        self.path = path
        self.text = None
        self.autoreload = autoreload  # set this to False if don't want reloads
        super(YAMLFileNestedCatalog, self).__init__(path, autoreload, **kwargs)

    def parse(self, text):
        self.text = text
        data = yaml_load(self.text)

        try:
            # Try the default YAMLFileCatalog first
            # Reuse default YAMLFileCatalog YAML parser
            # parse() does the heavy lifting of populating the catalog
            super().parse(text)
        except ValidationError:
            # Try to parse as a nested Catalog by
            # transforming it to yaml_nested_cat_desugared format.
            transformed_data = to_yaml_nested_cat_desugared(data)
            transformed_text = yaml.dump(transformed_data, default_flow_style=False)
            super().parse(transformed_text)
