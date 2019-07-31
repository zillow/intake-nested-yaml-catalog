==========================
intake-nested-yaml-catalog
==========================

This is an Anaconda Intake plugin supporting a single YAML hierarchical
catalog to organize datasets and avoid a data swamp.

.. code-block:: yaml

  entity:
    property:
      clean_attributes:
        args:
          urlpath: s3://foo
        driver: parquet
      zestimate:
        args:
          urlpath: '{{ CATALOG_DIR }}/zestimate.csv'
        description: zestimate description
        driver: csv
    user:
      user_profile:
        args:
          urlpath: s3://foo
        driver: parquet

Can be accessed as

.. code-block:: python

  df = cat.entity.property.clean_attributes.read()


Development
--

    ./uranium

Running Tests
--

    ./uranium test

Run Single Test
--

    ./uranium test -k search_item (e.g., name of test)

See https://docs.pytest.org/en/latest/usage.html for -k options
