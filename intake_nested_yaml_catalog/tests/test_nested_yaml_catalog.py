from pathlib import Path

import intake
import pytest

nested_yaml_cat_path = str(Path(__file__).resolve().parent.joinpath(Path("nested_yaml_cat.yaml")))


def test_intake_nested_yaml_cat():
    cat = intake.open_nested_yaml_cat(nested_yaml_cat_path)
    assert {'customer', 'user'} == set(cat.entity)
    assert {'customer_attributes', 'retention_project'} == set(cat.entity.customer)
    assert 'description' == cat.entity.description

    entry_description = cat.entity.customer.retention_project.good_customers.describe()
    assert 'good_customers' == entry_description['name']
    assert 'good_customers description' == entry_description['description']

    discover = cat.entity.customer.retention_project.good_customers.discover()
    assert discover['dtype'].keys() == {'customer_id', 'name'}

    df = cat.entity.customer.retention_project.good_customers().read()
    assert [101, 'Bob'] == df.loc[0].values.tolist()

    df = cat.entity.customer.retention_project.good_customers(kind="funny").read()
    assert [31, 'Donald Duck'] == df.loc[0].values.tolist()


def test_version():
    cat = intake.open_nested_yaml_cat(nested_yaml_cat_path)
    assert cat.version != ''


@pytest.mark.xfail(
    raises=AssertionError,
    reason="nested_yaml_cat requires a `hierarchical_catalog: true` metadata entry")
def test_missing_hierarchical_catalog():
    invalid_nested_yaml_cat_path = str(Path(__file__).resolve().parent.joinpath(Path("invalid_nested_yaml_cat.yaml")))
    intake.open_nested_yaml_cat(invalid_nested_yaml_cat_path)


def test_nested_cat_walk():
    cat = intake.open_nested_yaml_cat(nested_yaml_cat_path)
    assert 'entity.customer.retention_project.good_customers' not in list(cat.walk(depth=3))
    assert 'entity.customer.retention_project.good_customers' in list(cat.walk(depth=4))


def test_gui():
    pytest.importorskip('panel')
    cat = intake.open_nested_yaml_cat(nested_yaml_cat_path)
    assert repr(intake.gui).startswith('Row')
    intake.gui.add(cat)