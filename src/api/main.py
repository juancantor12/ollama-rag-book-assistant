"""Api entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import client
from api.routes import admin
from api.routes import rbac

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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
