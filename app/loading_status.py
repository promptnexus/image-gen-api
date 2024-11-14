from datetime import datetime
from rich.console import Console
from rich.table import Table, box
from rich.panel import Panel

console = Console()


class ResolverLoadingStatus:
    """Keeps track of resolver loading statistics"""

    def __init__(self):
        self.total_files_processed = 0
        self.successful_loads = 0
        self.failed_loads = 0
        self.loaded_resolvers = []
        self.start_time = datetime.now()
        self.query_resolvers = []
        self.mutation_resolvers = []

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

        table.add_row("Loaded Query Resolvers", "\n".join(self.query_resolvers))
        table.add_row("Loaded Mutation Resolvers", "\n".join(self.mutation_resolvers))

        console.print(Panel(table, border_style="green"))
