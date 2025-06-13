"""Client routes"""

# import time
import shutil
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from fastapi.responses import StreamingResponse
import ollama
from api.controllers.auth import login_request, verify_token
from api.controllers.rbac import require_permission
from api.schemas.actions import AskSchema, GenerateEmbeddingsSchema
from api.schemas.auth import LoginRequestSchema
from app.assistant import Assistant
from app.generate_embeddings import EmbeddingsGenerator
from app.utils import Utils

router = APIRouter(tags=["client"])


@router.get("/status/")
async def status():
    """Endpoint to check server status."""
    try:
        ollama.list()
        return {"status": "ok"}
    except Exception as e:
        Utils.logger.critical("Ollama server is not up.")
        raise HTTPException(status_code=503, detail="Ollama server is not up") from e


@router.post("/login/")
async def login(login_data: LoginRequestSchema, response: Response):
    """Endpoint to log in and generate a token."""
    token, token_data = login_request(login_data)
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        max_age=Utils.API_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        samesite="None",
        path="/",
    )
    return {
        "message": "Login successful",
        "permissions": token_data["permissions"],
        "session_expiration": token_data["exp"],
    }


@router.get("/logout/")
async def logout(response: Response):
    """Endpoint to log out and clear the token cookie."""
    response.set_cookie(
        key="token",
        value="",
        httponly=True,
        max_age=0,
        secure=True,
        samesite="None",
        path="/",
    )
    return {"message": "Logged out successfully"}


@router.post("/upload_book/")
async def upload_book(
    file: UploadFile = File(...), _=Depends(require_permission("upload_book"))
):
    """Endpoint for uploading a book."""
    try:
        book_filename = Utils.strip_extension(file.filename)
        with open(Utils.get_data_path() / (book_filename + ".pdf"), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        Utils.logger.critical(e)
        raise HTTPException(status_code=500, detail="Failed to upload the file") from e


@router.get("/load_books/")
async def load_books(_=Depends(require_permission("load_books"))):
    """Endpoint to see uploaded books."""
    books_folder_path = Utils.get_data_path()
    pdf_files = []
    for file in books_folder_path.iterdir():
        if file.suffix.lower() == ".pdf" and file.is_file():
            embeddings_generator = EmbeddingsGenerator(file.name)
            pdf_files.append(
                {
                    "book": file.name,
                    "embeddings": embeddings_generator.check_collection(),
                }
            )
    return pdf_files


@router.get("/generate_embeddings/{book_filename}")
async def generate_embeddings(
    book_filename: str,
    _=Depends(require_permission("generate_embeddings")),
):
    """Endpoint to generate the embeddings database."""
    # book_filename = book_data.book_filename
    # output_folder = Utils.strip_extension(book_filename)
    # Utils.logger = setup_logging(output_folder)
    embeddings_generator = EmbeddingsGenerator(book_filename)
    return StreamingResponse(
        embeddings_generator.generate_embeddings(stream=True),
        media_type="text/event-stream"
        )
    # embeddings = embeddings_generator.generate_embeddings()
    # if embeddings:
    #     return {
    #         "message": f"Embeddings generated successfully at /output/{output_folder}"
    #     }
    # raise HTTPException(status_code=500, detail="Failed to generate embeddings")


@router.post("/ask/")
async def ask_question(query: AskSchema, _=Depends(require_permission("ask"))):
    """Endpoint for asking a question."""
    # time.sleep(2)
    # return {
    #     "answer": "Cool answer",
    #     "references": [
    #         {"section": "Random section.", "pages": [111, 222, 333]},
    #     ]
    # }
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


@router.get("/check_session/")
async def check_session(token_data=Depends(verify_token)):
    """Checks if the current http cookie has a valid, non-expired token."""
    return {
        "permissions": token_data.get("permissions", ""),
        "session_expiration": token_data.get("exp", ""),
        "username": token_data.get("username", ""),
    }
