"""Client routes"""

from fastapi import APIRouter, Depends, HTTPException
from api.controllers.auth import login_request
from api.schemas.actions import AskSchema, GenerateEmbeddingsSchema
from api.schemas.auth import LoginRequestSchema
from api.controllers.rbac import require_permission
from app.assistant import Assistant
from app.generate_embeddings import EmbeddingsGenerator
from app.utils import Utils


router = APIRouter(tags=["client"])


@router.post("/login/")
async def login(login_data: LoginRequestSchema):
    """Endpoint to log in and generate a token."""
    access_token = login_request(login_data)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/generate_embeddings/")
async def generate_embeddings(
    book_data: GenerateEmbeddingsSchema,
    _=Depends(require_permission("generate_embeddings")),
):
    """Endpoint to generate the embeddings database."""
    book_filename = book_data.book_filename
    output_folder = Utils.strip_extension(book_filename)
    # Utils.logger = setup_logging(output_folder)
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
    output_folder = Utils.strip_extension(query.book_filename)
    embeddings_collection = Utils.get_embeddings_db(output_folder)
    if not embeddings_collection:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Embeddings for {query.book_filename} not generated."
                " Please run 'generate_embeddings' first."
            ),
        )
    assistant = Assistant(query.book_filename, embeddings_collection)
    data = assistant.ask(query.question)
    return data
