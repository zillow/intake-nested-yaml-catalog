from pathlib import Path
from unittest import TestCase

import intake
import yaml

from intake_nested_yaml_catalog.nested_yaml_catalog import YAMLFileNestedCatalog, to_yaml_cat, \
    to_yaml_nested_cat  # noqa: F401


class IntakeTest(TestCase):
    def test_intake_yaml_cat(self):
        catalog_path = str(Path(__file__).resolve().parent.joinpath(Path("yaml_cat.yaml")))
        cat = intake.Catalog(catalog_path)
        self.assertEqual('description1', cat.entity.description)
        self.assertEqual(['property', 'user'], list(cat.entity))
        self.assertEqual(['clean_attributes', 'zestimate_project'], list(cat.entity.property))

        self.validate_zestimate(cat)

    def test_intake_yaml_config_values(self):
        catalog_path = str(Path(__file__).resolve().parent.joinpath(Path("yaml_nested_cat.yaml")))
        cat = intake.Catalog(catalog_path)
        self.assertEqual(['property', 'user'], list(cat.entity))
        self.assertEqual(['clean_attributes', 'zestimate_project'], list(cat.entity.property))

        self.validate_zestimate(cat)

    def validate_zestimate(self, cat):
        entry_description = cat.entity.property.zestimate_project.zestimate.describe()
        self.assertEqual('zestimate', entry_description['name'])
        self.assertEqual('zestimate description', entry_description['description'])

        zestimate_discover = cat.entity.property.zestimate_project.zestimate.discover()
        self.assertEqual(set(zestimate_discover['dtype'].keys()), {'zpid', 'zestimate'})

        df = cat.entity.property.zestimate_project.zestimate.read()
        self.assertListEqual([101, 400302], df.loc[0].values.tolist())

    def test_catalog_transformation_inverse_relationship(self):
        """
        Tests that "yaml_nested_cat -> yaml_cat -> yaml_nested_cat" transformations work
        """
        nested_catalog = YAMLFileNestedCatalog(
            str(Path(__file__).resolve().parent.joinpath(Path("yaml_nested_cat.yaml"))))

        yaml_nested_dict = yaml.safe_load(nested_catalog.entity.yaml())

        self.assertDictEqual(
            yaml_nested_dict,
            to_yaml_nested_cat(to_yaml_cat(yaml_nested_dict), '')  # test to yaml_cat and back to yaml_nested
        )
