.. intake-nested-yaml-catalog documentation master file
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Intake plugin for nested YAML catalogs
==================================================

This is an `Intake <https://intake.readthedocs.io/en/latest/quickstart.html>`_ plugin supporting a
single YAML hierarchical catalog to organize datasets and avoid a data swamp.

.. code-block:: yaml

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

Can be accessed as

.. code-block:: python

  df = cat.entity.customer.customer_attributes.read()


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
