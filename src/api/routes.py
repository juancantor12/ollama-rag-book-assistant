"""Entry point for the api ."""

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from api.auth import generate_access_token
from api.db import Database
from api.models.user import User
from api.schemas.actions import AskSchema, GenerateEmbeddingsSchema
from api.schemas.auth import LoginRequestSchema
from api.rbac import require_permission
from app.assistant import Assistant
from app.generate_embeddings import EmbeddingsGenerator
from app.utils import Utils
from app.logging import setup_logging


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login/")
async def login(login_data: LoginRequestSchema):
    """Endpoint to log in and generate a token."""
    db = Database()
    user = db.session.query(User).filter(User.username == login_data.username).first()
    if not user or not pwd_context.verify(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token_data = {"idx": user.idx, "permissions": user.role.get_role_permissions()}
    access_token = generate_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/generate_embeddings/")
async def generate_embeddings(
    book_data: GenerateEmbeddingsSchema,
    _=Depends(require_permission("generate_embeddings")),
):
    """Endpoint to generate the embeddings database."""
    book_filename = book_data.book_filename
    output_folder = Utils.strip_extension(book_filename)
    Utils.logger = setup_logging(output_folder)
    embeddings_generator = EmbeddingsGenerator(book_filename)
    embeddings = embeddings_generator.generate_embeddings()
    if embeddings:
        return {
            "message": f"Embeddings generated successfully at /output/{output_folder}"
        }
    raise HTTPException(status_code=500, detail="Failed to generate embeddings")


@router.post("/ask/")
async def ask_question(query: AskSchema, _=Depends(require_permission("ask"))):
    """Endpoint for asking a question."""
    embeddings_collection = Utils.get_embeddings_db(query.book_filename)
    if not embeddings_collection:
        raise HTTPException(
            status_code=400,
            detail="Embeddings not generated. Please run 'generate_embeddings' first.",
        )
    assistant = Assistant(query.book_filename, embeddings_collection)
    data = assistant.ask(query.question)
    return data


@router.get("/admin/create_db_tables")
async def create_db_tables(_=Depends(require_permission("create_db_tables"))):
    """Endpoint for admins to generate the api DB tables."""
    db = Database()
    if db.create_all_tables():
        return {"message": "The database tables have been created"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="The database tables creating failed, check logs for details.",
    )
