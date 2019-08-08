from pathlib import Path

import intake
import pytest
import yaml

from intake_nested_yaml_catalog.nested_yaml_catalog import YAMLFileNestedCatalog, \
    to_yaml_nested_cat, to_yaml_nested_cat_desugared  # noqa: F401

yaml_nested_cat_path = str(Path(__file__).resolve().parent.joinpath(Path("yaml_nested_cat.yaml")))


def test_intake_yaml_cat():
    catalog_path = str(Path(__file__).resolve().parent.joinpath(Path("yaml_cat.yaml")))
    cat = intake.Catalog(catalog_path)
    assert 'description' == cat.entity.description
    assert ['customer', 'user'] == list(cat.entity)
    assert ['customer_attributes', 'retention_project'] == list(cat.entity.customer)

    validate_retention_project(cat)


def test_intake_yaml_nested_cat():
    cat = intake.open_yaml_nested_cat(yaml_nested_cat_path)
    assert ['customer', 'user'] == list(cat.entity)
    assert ['customer_attributes', 'retention_project'] == list(cat.entity.customer)

    validate_retention_project(cat)


def test_version():
    cat = intake.open_yaml_nested_cat(yaml_nested_cat_path)
    assert cat.version != ''


def validate_retention_project(cat):
    entry_description = cat.entity.customer.retention_project.good_customers.describe()
    assert 'good_customers' == entry_description['name']
    assert 'good_customers description' == entry_description['description']

    discover = cat.entity.customer.retention_project.good_customers.discover()
    assert discover['dtype'].keys() == {'customer_id', 'name'}

    df = cat.entity.customer.retention_project.good_customers.read()
    assert [101, 'Bob'] == df.loc[0].values.tolist()


def test_catalog_transformation_inverse_relationship():
    """
    Tests that "yaml_nested_cat -> yaml_cat -> yaml_nested_cat" transformations work
    """
    nested_catalog = YAMLFileNestedCatalog(yaml_nested_cat_path)

    yaml_nested_dict = yaml.safe_load(nested_catalog.entity.yaml())

    assert yaml_nested_dict == to_yaml_nested_cat(
        to_yaml_nested_cat_desugared(yaml_nested_dict),
        '')  # test to yaml_cat and back to yaml_nested


@pytest.mark.xfail(raises=AssertionError)
def test_missing_hierarchical_catalog():
    invalid_yaml_nested_cat_path = str(Path(__file__).resolve().parent.joinpath(Path("invalid_yaml_nested_cat.yaml")))
    intake.open_yaml_nested_cat(invalid_yaml_nested_cat_path)
