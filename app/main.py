from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter
from pathlib import Path
import subprocess

from app.schema import schema
from app.services.auth import get_context


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    try:
        # Create schema and docs
        Path("schema.graphql").write_text(str(schema))
        Path("generated-docs").mkdir(exist_ok=True)
        try:
            subprocess.run(["spectaql", "spectaql-config.yml"], check=True)
            app.mount(
                "/docs", StaticFiles(directory="generated-docs", html=True), name="docs"
            )
        except FileNotFoundError:
            print("Spectaql not installed")
    except Exception as e:
        print(f"Documentation generation failed: {e}")
    yield


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Handle startup and shutdown events"""
#     try:
#         # On startup: Generate docs
#         schema_path = Path("schema.graphql")
#         with open(schema_path, "w") as f:
#             f.write(str(schema))

#         subprocess.run(["spectaql", "spectaql-config.yml"], check=True)

#         # Mount docs if generation succeeded
#         if Path("generated-docs").exists():
#             app.mount(
#                 "/docs", StaticFiles(directory="generated-docs", html=True), name="docs"
#             )
#     except Exception as e:
#         print(f"Documentation generation failed: {e}")

#     yield  # Server runs here

#     # On shutdown: Cleanup if needed
#     pass


# Create FastAPI app
app = FastAPI(
    title="Image Generation API",
    description="GraphQL API for generating images with various styles and options",
    version="1.0.0",
    lifespan=lifespan,
)

# Create GraphQL app
graphql_app = GraphQLRouter(schema, context_getter=get_context)

app.add_route("/", graphql_app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
