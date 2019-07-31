from uranium import current_build

current_build.config.set_defaults({
    "package_name": "intake-nested-yaml-catalog",
    "module": "intake_nested_yaml_catalog",
    "binaries": {"enabled": True},
})

current_build.packages.install(".", develop=True)
from orbital_core.build import bootstrap_build
bootstrap_build(current_build)
