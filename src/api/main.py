"""Api entry point."""

from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from api.routes import client
from api.routes import admin
from api.routes import rbac

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
run = FastAPI()
run.include_router(client.router)
run.include_router(admin.router)
run.include_router(rbac.router)
