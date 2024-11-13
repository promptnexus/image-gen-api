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
from datetime import datetime

# Set up rich console
console = Console()

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

# Get logger
logger = logging.getLogger(__name__)

class ResolverLoadingStatus:
    """Keeps track of resolver loading statistics"""
    def __init__(self):
        self.total_files_processed = 0
        self.successful_loads = 0
        self.failed_loads = 0
        self.loaded_resolvers = []
        self.start_time = datetime.now()
    
    def print_summary(self):
        """Prints a beautiful summary table of the loading process"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        table = Table(title="Resolver Loading Summary", box=box.ROUNDED)
        
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Files Processed", str(self.total_files_processed))
        table.add_row("Successful Loads", str(self.successful_loads))
        table.add_row("Failed Loads", str(self.failed_loads))
        table.add_row("Processing Time", f"{duration:.2f} seconds")
        
        console.print(Panel(table, border_style="green"))

def load_resolvers(base_path: Path) -> list[Type]:
    """
    Generic resolver loader that works for both queries and mutations on any platform.
    
    Args:
        base_path: Path to the queries/ or mutations/ directory
    
    Returns:
        list[Type]: List of resolver classes decorated with strawberry
    """
    status = ResolverLoadingStatus()
    resolver_classes = []
    
    # Print startup banner
    console.print(Panel(
        "[bold blue]Starting Resolver Loading Process[/bold blue]\n"
        f"[cyan]Base Path:[/cyan] {base_path}",
        border_style="blue",
        box=box.DOUBLE
    ))
    
    # Ensure we're working with a Path object and resolve to absolute path
    base_path = Path(base_path).resolve()
    app_root = base_path.parent.parent.resolve()
    
    # Ensure the base directory is in the Python path
    if str(app_root) not in sys.path:
        sys.path.insert(0, str(app_root))
    
    # Walk through all subdirectories
    for domain_dir in base_path.glob("*/"):
        if not domain_dir.is_dir():
            continue
            
        console.print(f"\n[bold yellow]Scanning domain:[/bold yellow] {domain_dir.name}")
            
        # Look for all .py files in each domain directory
        for path in domain_dir.glob("*.py"):
            if path.stem == "__init__":
                continue
                
            status.total_files_processed += 1
            
            try:
                # Get relative path from app root
                relative_path = path.relative_to(app_root)
                module_parts = list(relative_path.with_suffix('').parts)
                module_name = '.'.join(part for part in module_parts)
                
                # Import the module
                module = importlib.import_module(module_name)
                
                # Get all strawberry-decorated classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and hasattr(attr, "__strawberry_definition__"):
                        resolver_classes.append(attr)
                        status.successful_loads += 1
                        status.loaded_resolvers.append(attr.__name__)
                        
                        # Print beautiful success message
                        console.print(Panel(
                            f"[bold green]Loaded Resolver:[/bold green] {attr.__name__}\n"
                            f"[dim]Module:[/dim] {module_name}",
                            border_style="green",
                            box=box.ROUNDED
                        ))
                        
            except ImportError as e:
                status.failed_loads += 1
                console.print(Panel(
                    f"[bold red]Import Error[/bold red]\n"
                    f"File: {path}\n"
                    f"Error: {str(e)}",
                    border_style="red",
                    box=box.HEAVY
                ))
            except Exception as e:
                status.failed_loads += 1
                console.print(Panel(
                    f"[bold red]Unexpected Error[/bold red]\n"
                    f"File: {path}\n"
                    f"Error: {str(e)}",
                    border_style="red",
                    box=box.HEAVY
                ))
    
    # Print summary
    status.print_summary()
                
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
        console.print(Panel(
            "[bold yellow]Warning:[/bold yellow] No classes provided to create resolver type",
            border_style="yellow",
            box=box.ROUNDED
        ))
        return strawberry.type(type(name, (), {}))
        
    console.print(Panel(
        f"[bold green]Created Combined Resolver Type:[/bold green] {name}\n"
        f"[dim]Number of Classes:[/dim] {len(classes)}",
        border_style="green",
        box=box.ROUNDED
    ))
    
    return strawberry.type(type(name, tuple(classes), {}))