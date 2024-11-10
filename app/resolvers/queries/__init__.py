# app/resolvers/queries/__init__.py
from pathlib import Path
from ..loader import load_resolvers, create_resolver_type

Query = create_resolver_type("Query", load_resolvers(Path(__file__).parent))
