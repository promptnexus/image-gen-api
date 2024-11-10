# app/resolvers/loader.py
import strawberry
import importlib
from pathlib import Path
from typing import Type


def load_resolvers(base_path: Path) -> list[Type]:
    """
    Generic resolver loader that works for both queries and mutations

    Args:
        base_path: Path to the queries/ or mutations/ directory
    """
    resolver_classes = []

    # Walk through all subdirectories
    for domain_dir in base_path.glob("*/"):
        if domain_dir.is_dir():
            # Look for all .py files in each domain directory
            for path in domain_dir.glob("*.py"):
                if path.stem != "__init__":
                    # Get relative path from app/resolvers
                    relative_path = path.relative_to(base_path.parent.parent)
                    # Convert path to module name (e.g., 'app.resolvers.queries.health.health')
                    module_name = (
                        str(relative_path).replace("/", ".").replace("\\", ".")[:-3]
                    )

                    try:
                        # Import the module
                        module = importlib.import_module(module_name)

                        # Get all strawberry-decorated classes
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if isinstance(attr, type) and hasattr(
                                attr, "__strawberry_definition__"
                            ):
                                resolver_classes.append(attr)
                    except ImportError as e:
                        print(f"Failed to import {module_name}: {e}")

    return resolver_classes


def create_resolver_type(name: str, classes: list[Type]) -> Type:
    """Creates a new strawberry type that combines all resolver classes"""
    return strawberry.type(type(name, tuple(classes), {}))
