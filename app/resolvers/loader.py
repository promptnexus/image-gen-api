import strawberry
import importlib
from pathlib import Path
from typing import Type
import logging

# Set up logging
logger = logging.getLogger(__name__)

def load_resolvers(base_path: Path) -> list[Type]:
    """
    Generic resolver loader that works for both queries and mutations on any platform.
    
    Args:
        base_path: Path to the queries/ or mutations/ directory
    
    Returns:
        list[Type]: List of resolver classes decorated with strawberry
    """
    resolver_classes = []
    
    # Ensure we're working with a Path object
    base_path = Path(base_path)
    
    # Get the absolute path to the app root directory
    app_root = base_path.parent.parent
    
    # Walk through all subdirectories
    for domain_dir in base_path.glob("*/"):
        if not domain_dir.is_dir():
            continue
            
        # Look for all .py files in each domain directory
        for path in domain_dir.glob("*.py"):
            if path.stem == "__init__":
                continue
                
            try:
                # Get relative path from app root
                relative_path = path.relative_to(app_root)
                
                # Convert path to module name using parts to handle any platform
                module_parts = relative_path.with_suffix('').parts
                module_name = '.'.join(module_parts)
                
                # Import the module
                module = importlib.import_module(module_name)
                
                # Get all strawberry-decorated classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and hasattr(attr, "__strawberry_definition__"):
                        resolver_classes.append(attr)
                        logger.debug(f"Loaded resolver class: {attr.__name__} from {module_name}")
                        
            except ImportError as e:
                logger.error(f"Failed to import {path}: {e}")
            except ValueError as e:
                logger.error(f"Path error processing {path}: {e}")
                
    return resolver_classes

def create_resolver_type(name: str, classes: list[Type]) -> Type:
    """
    Creates a new strawberry type that combines all resolver classes
    
    Args:
        name: Name for the combined type
        classes: List of resolver classes to combine
        
    Returns:
        Type: Combined strawberry type
    """
    if not classes:
        logger.warning(f"No classes provided to create resolver type {name}")
        
    return strawberry.type(type(name, tuple(classes), {}))