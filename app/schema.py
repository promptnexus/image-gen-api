# schema.py
from app.loading_status import ResolverLoadingStatus
from app.validators import load_validators
import strawberry
from strawberry.extensions import AddValidationRules
from datetime import datetime
from rich.table import Table
from rich import box
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from app.resolvers.loader import load_resolvers, create_resolver_type

console = Console()

status = ResolverLoadingStatus()

base_dir = Path(__file__).resolve().parent
mutations_dir = base_dir / "resolvers" / "mutations"

queries_dir = base_dir / "resolvers" / "queries"


mutation_classes = load_resolvers(status, mutations_dir, "mutation")
status.mutation_resolvers = [cls.__name__ for cls in mutation_classes]
Mutation = create_resolver_type("Mutation", mutation_classes)

query_classes = load_resolvers(status, queries_dir, "query")
status.query_resolvers = [cls.__name__ for cls in query_classes]
Query = create_resolver_type("Query", query_classes)

console.log(f"Loading mutations from: {mutations_dir}")
console.log(f"Loading queries from: {queries_dir}")

status.print_summary()

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        AddValidationRules(load_validators()),
    ],
)
