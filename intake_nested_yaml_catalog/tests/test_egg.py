

# write functional, low overhead tests like this
def test_has_tests():
    pass
    # assert_true (False, "There aren't any tests.")


def test_import_intake_nested_yaml_catalog():
    import intake_nested_yaml_catalog  # noqa: F401 - suppress one type of error on this line
