from typing import List, Dict

import vcver
from intake import Catalog
from intake.catalog import exceptions
from intake.catalog.exceptions import ValidationError
from intake.catalog.local import YAMLFileCatalog, CatalogParser
from intake.utils import yaml_load


class NestedYAMLFileCatalog(YAMLFileCatalog):
    """
    Catalog as described by a single YAML file with hierarchy.
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

    customer_attributes can be accessed as such:
    >>> catalog.entity.customer.customer_attributes.describe()
    """
    version = vcver.get_version()
    container = 'catalog'
    partition_access = None
    name = 'nested_yaml_cat'

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
        super(NestedYAMLFileCatalog, self).__init__(path, autoreload, **kwargs)

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
            assert_msg = "nested_yaml_cat requires a `hierarchical_catalog: true` metadata entry"
            assert 'metadata' in data, assert_msg
            assert 'hierarchical_catalog' in data['metadata'], assert_msg
            assert data['metadata']['hierarchical_catalog'], assert_msg

            cat = self._create_nested_catalog(self.name, data)
            self._entries = cat._entries
            for _, entry in self._entries.items():
                if isinstance(entry, Catalog):
                    entry.cat = self
                    entry.catalog_object = self

            self.metadata = self.metadata or cat.metadata
            self.name = cat.name or self.name_from_path
            self.description = self.description or cat.description

    def _create_nested_catalog(self, name: str, nested_yaml_cat: dict) -> Catalog:
        # Validate and parse level_sources
        catalog_fields = ['metadata', 'plugins', 'args', 'cache']
        level_sources = {
            'sources': {k: v for k, v in nested_yaml_cat.items()
                        if isinstance(v, dict) and 'driver' in v},
            **{k: v for k, v in nested_yaml_cat.items()
               if not isinstance(v, dict) or k in catalog_fields}  # for (description, metadata, etc) fields
        }

        context = dict(root=self._dir)
        parsed_catalog = CatalogParser(level_sources, context=context, getenv=self.getenv, getshell=self.getshell)
        if parsed_catalog.errors:
            raise exceptions.ValidationError(
                "Catalog '{}' has validation errors:\n\n{}".format(self.path, "\n".join(parsed_catalog.errors)),
                parsed_catalog.errors)

        # list of catalogs at this level
        level_catalogs: List[Catalog] = [
            self._create_nested_catalog(k, v)  # recursive call!
            for k, v in nested_yaml_cat.items()
            if k not in catalog_fields and isinstance(v, dict) and 'driver' not in v
        ]

        cat = Catalog.from_dict(
            entries={
                **{c.name: c for c in level_catalogs},
                **{entry.name: entry for entry in parsed_catalog.data['data_sources']}
            },
            # plugins=parsed_catalog.data.get('plugin_sources', None),
            name=name or parsed_catalog.data.get('name') ,
            metadata=parsed_catalog.data.get('metadata', {}),
            description=parsed_catalog.data.get('description', None))

        for sub_cat in level_catalogs:
            sub_cat.cat = cat
            sub_cat.catalog_object = cat

        for entry in parsed_catalog.data['data_sources']:
            entry._catalog = cat
            entry._filesystem = self.filesystem

        return cat
