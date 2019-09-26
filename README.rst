Welcome to Intake plugin for nested YAML catalogs
==================================================

This is an `Intake <https://intake.readthedocs.io/en/latest/quickstart.html>`_ plugin supporting a
single YAML hierarchical catalog to organize datasets and avoid a data swamp.


Example of organizing the datasets by business domain entities:

.. code-block:: yaml

    metadata:
      hierarchical_catalog: true
    entity:
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

Can be accessed as:

.. code-block:: python

  df = catalog.entity.customer.customer_attributes.read()
