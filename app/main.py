import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter
from pathlib import Path
import subprocess

from app.services.customer_management_service.utils import (
    get_new_customer_management_router,
)
from fastapi_login.exceptions import InvalidCredentialsException

from app.schema import schema
from app.services.api_key_service.admin.main import create_admin_routes
from app.services.api_key_service.api_key_service_driver import create_api_key_routes
from app.services.auth import get_context

from dotenv import load_dotenv
import torch
from app.services.utils import pick_device
from rich.console import Console
from rich.table import Table

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


# Define a custom exception
class NotAuthenticatedException(Exception):
    pass


# Define the global exception handler once in the main app
@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/manage"):
        return RedirectResponse(url="/manage/auth/login", status_code=302)
    return RedirectResponse(url="/auth/login", status_code=302)


async def dev_context():
    """Development context with no auth"""
    return {}


initialize_torch_env()

# Choose context based on environment
context_getter = dev_context if os.getenv("DISABLE_AUTH") else get_context

# Create GraphQL app
graphql_app = GraphQLRouter(
    schema,
    context_getter=context_getter,
    graphiql=os.getenv("PN_IMAGE_GEN_APP_ENV") == "development",
    path="/",
)

app.include_router(graphql_app)  # GraphQL endpoint

app.include_router(create_api_key_routes(), prefix="/manage")  # API key routes

app.include_router(create_admin_routes(), prefix="/admin")  # Admin routes

app.include_router(get_new_customer_management_router(), prefix="/customer-management")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 443))
    reload_app = int(bool(os.getenv("SHOULD_RELOAD", False)))
    env = os.getenv("PN_IMAGE_GEN_APP_ENV", "production")

    uvicorn_kwargs = {
        "app": "app.main:app",
        "host": "0.0.0.0",
        "port": port,
        "reload": reload_app,
    }

    if env != "development":
        uvicorn_kwargs["ssl_certfile"] = (
            "/etc/letsencrypt/live/api.rank3.dev/fullchain.pem"
        )
        uvicorn_kwargs["ssl_keyfile"] = (
            "/etc/letsencrypt/live/api.rank3.dev/privkey.pem"
        )

    uvicorn.run(**uvicorn_kwargs, workers=4)
