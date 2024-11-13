from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter
from pathlib import Path
import subprocess

from app.schema import schema
from app.services.auth import get_context

from dotenv import load_dotenv
import torch
from app.services.utils import pick_device

load_dotenv()

def initialize_torch_env():
    device = pick_device()
    num_cores = os.cpu_count() // 2

    # Set interop threads for CPU-GPU communication regardless of device
    # torch.set_num_interop_threads(num_cores // 2)

    if device == "cpu":
        print("Setting CPU-specific optimizations...")
        torch.set_num_threads(num_cores)
        os.environ["OMP_NUM_THREADS"] = str(num_cores)
        os.environ["MKL_NUM_THREADS"] = str(num_cores)

    return device


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    try:
        # Create schema and docs
        Path("schema.graphql").write_text(str(schema))
        Path("generated-docs").mkdir(exist_ok=True)
        try:
            if (
                subprocess.run(
                    "spectaql spectaql-config.yml", shell=True, check=True
                ).returncode
                != 0
            ):
                raise RuntimeError("Spectaql command failed")
            app.mount(
                "/docs",
                StaticFiles(directory="generated-docs", html=True),
                name="docs",
            )

            print("mounted docs")
        except FileNotFoundError:
            print("Spectaql not installed")
    except Exception as e:
        print(f"Documentation generation failed: {e}")
    yield


# Create FastAPI app
app = FastAPI(
    title="Image Generation API",
    description="GraphQL API for generating images with various styles and options",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)


async def dev_context():
    """Development context with no auth"""
    return {}

initialize_torch_env()

# Choose context based on environment
context_getter = dev_context if os.getenv("DISABLE_AUTH") else get_context

# Create GraphQL app
graphql_app = GraphQLRouter(schema, context_getter=context_getter, graphiql=True)

app.include_router(graphql_app, prefix="/graphql")  # GraphQL endpoint
app.add_route("/", graphql_app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=9000, reload=True)
