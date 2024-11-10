# validators/__init__.py
from pathlib import Path
from importlib import import_module
from typing import List, Type
from graphql import ValidationRule


def load_validators() -> List[Type[ValidationRule]]:
    validators = []
    validators_dir = Path(__file__).parent

    # Walk through all subdirectories
    for path in validators_dir.rglob("*.py"):
        if path.name == "__init__.py":
            continue

        # Convert path to module path (e.g. validators.image_generation_input.something)
        relative_path = path.relative_to(validators_dir.parent)
        module_path = str(relative_path.with_suffix("")).replace("/", ".")

        # Import the module and collect ValidationRule classes
        module = import_module(module_path)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, ValidationRule)
                and attr is not ValidationRule
            ):
                validators.append(attr)

    return validators
