from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter
from pathlib import Path
import subprocess

from .schema import schema
from .services.auth import get_context

# Create FastAPI app
app = FastAPI(
    title="Image Generation API",
    description="GraphQL API for generating images with various styles and options",
    version="1.0.0",
)

# Create GraphQL app
graphql_app = GraphQLRouter(schema, context_getter=get_context)

# Mount GraphQL at root
app.include_router(graphql_app, prefix="")

# Mount documentation
app.mount("/docs", StaticFiles(directory="generated-docs", html=True), name="docs")


@app.on_event("startup")
async def generate_docs():
    """Generate API documentation on startup."""
    # Export schema
    schema_path = Path("schema.graphql")
    with open(schema_path, "w") as f:
        f.write(str(schema))

    # Generate documentation
    subprocess.run(["spectaql", "spectaql-config.yml"], check=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
