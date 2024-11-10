# app/resolvers/mutations/__init__.py
from pathlib import Path
from ..loader import load_resolvers, create_resolver_type

Mutation = create_resolver_type("Mutation", load_resolvers(Path(__file__).parent))
