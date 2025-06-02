"""Api entry point."""

from fastapi import FastAPI
from api.routes import client
from api.routes import admin
from api.routes import rbac

run = FastAPI()
run.include_router(client.router)
run.include_router(admin.router)
run.include_router(rbac.router)
