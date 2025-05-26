"""Api entry point."""

from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from api.routes import router
from app.logging import setup_logging
from app.utils import Utils

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
Utils.logger = setup_logging("api")
run = FastAPI()
run.include_router(router)
