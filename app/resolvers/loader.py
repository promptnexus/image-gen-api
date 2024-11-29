import traceback
import strawberry
import importlib
from pathlib import Path
from typing import Type
import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich import box
import sys
from app.loading_status import ResolverLoadingStatus

# Set up rich console
console = Console()

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

# Get logger
logger = logging.getLogger(__name__)


def load_resolvers(
    status: ResolverLoadingStatus, base_path: Path, resolver_type: str = "mutation"
) -> list[Type]:

    resolver_classes = []
    print(f"Loading {resolver_type}s from {base_path}")

    base_path = Path(base_path).resolve()
    app_root = base_path.parent.parent.resolve()

    if str(app_root) not in sys.path:
        sys.path.insert(0, str(app_root))

    for domain_dir in base_path.glob("*/"):
        if not domain_dir.is_dir() or domain_dir.name == "__pycache__":
            continue

        for path in domain_dir.glob("*.py"):
            if path.stem == "__init__":
                continue

            status.total_files_processed += 1

            try:
                relative_path = path.relative_to(app_root)
                module_name = ".".join(relative_path.with_suffix("").parts)
                module = importlib.import_module(module_name)

                # Only get classes defined in THIS module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and hasattr(attr, "__strawberry_definition__")
                        and attr.__module__ == module.__name__
                    ):
                        resolver_classes.append(attr)
                        status.successful_loads += 1
                        if resolver_type == "query":
                            status.query_resolvers.append(attr.__name__)
                        else:
                            status.mutation_resolvers.append(attr.__name__)

            except ImportError as e:
                print("Import failed:")
                traceback.print_exc()
                status.failed_loads += 1
            except Exception as e:
                print("Processing failed:")
                traceback.print_exc()
                status.failed_loads += 1

    return resolver_classes


# Modify create_resolver_type to not print anything
def create_resolver_type(name: str, classes: list[Type]) -> Type:
    if not classes:
        return strawberry.type(type(name, (), {}))
    return strawberry.type(type(name, tuple(classes), {}))


# def create_resolver_type(name: str, classes: list[Type]) -> Type:
#     """
#     Creates a new strawberry type that combines all resolver classes

#     Args:
#         name: Name for the combined type
#         classes: List of resolver classes to combine

#     Returns:
#         Type: Combined strawberry type
#     """
#     if not classes:
#         console.print(
#             Panel(
#                 "[bold yellow]Warning:[/bold yellow] No classes provided to create resolver type",
#                 border_style="yellow",
#                 box=box.ROUNDED,
#             )
#         )
#         return strawberry.type(type(name, (), {}))

#     console.print(
#         Panel(
#             f"[bold green]Created Combined Resolver Type:[/bold green] {name}\n"
#             f"[dim]Number of Classes:[/dim] {len(classes)}",
#             border_style="green",
#             box=box.ROUNDED,
#         )
#     )

#     return strawberry.type(type(name, tuple(classes), {}))
