"""Api entry point."""

# Must run before importing passlib-backed controllers.
from api.compat import bcrypt_compat  # noqa: F401

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.controllers.recovery import RecoveryController
from api.routes import client
from api.routes import admin
from api.routes import rbac
from app.utils import Utils

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://juancantor12.github.io",
]
run = FastAPI()
run.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
)
run.include_router(client.router)
run.include_router(admin.router)
run.include_router(rbac.router)
run.mount("/data", StaticFiles(directory=Utils.get_data_path()), name="data")


@run.on_event("startup")
async def startup_recovery_code():
    """Print a short-lived admin recovery code on startup."""
    controller = RecoveryController()
    code = controller.generate_code()
    if code:
        Utils.logger.warning("Admin recovery code: %s", code)
