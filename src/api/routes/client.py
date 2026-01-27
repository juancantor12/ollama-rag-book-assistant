"""Client routes"""

import re
# import time
import shutil
import requests
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from fastapi.responses import StreamingResponse
from api.controllers.auth import login_request, verify_token
from api.controllers.rbac import require_permission
from api.schemas.actions import AskSchema
from api.schemas.auth import LoginRequestSchema
from api.schemas.exam import ExamGenerateSchema, ExamEvaluateSchema, ExamEvaluateCodeSchema
from app.assistant import Assistant
from app.exam import ExamGenerator
from app.generate_embeddings import EmbeddingsGenerator
from app.utils import Utils

router = APIRouter(tags=["client"])


@router.get("/status/")
async def status():
    """Endpoint to check server status."""
    try:
        r = requests.get(Utils.OLLAMA_URL + "/tags", timeout=2)
        models = [m["name"] for m in r.json()["models"]]
        if Utils.CHAT_MODEL in models and Utils.EMBEDDINGS_MODEL in models:
            return {"status": "ok"}
        raise HTTPException(
            status_code=503,
            detail="Ollama is running but the required models are not available",
        )
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
        "username": login_data.username,
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
            progress = embeddings_generator.get_progress()
            pdf_files.append(
                {
                    "book": file.name,
                    "embeddings": embeddings_generator.check_collection(),
                    "progress": progress,
                }
            )
    return pdf_files


@router.get("/generate_embeddings/{book_filename}")
async def generate_embeddings(
    book_filename: str,
    resume: bool = False,
    _=Depends(require_permission("generate_embeddings")),
):
    """Endpoint to generate the embeddings database."""
    # book_filename = book_data.book_filename
    # output_folder = Utils.strip_extension(book_filename)
    # Utils.logger = setup_logging(output_folder)
    embeddings_generator = EmbeddingsGenerator(book_filename)
    return StreamingResponse(
        embeddings_generator.generate_embeddings(stream=True, resume=resume),
        media_type="text/event-stream",
    )


@router.get("/embeddings/{book_filename}")
async def list_embeddings(
    book_filename: str,
    limit: int = 20,
    offset: int = 0,
    _=Depends(require_permission("load_books")),
):
    """Paginated embeddings list for a book."""
    output_folder = Utils.strip_extension(book_filename)
    collection = Utils.get_embeddings_db(output_folder)
    if not collection:
        raise HTTPException(status_code=404, detail="Embeddings not found")
    total = collection.count()
    records = collection.get(
        include=["documents", "metadatas"], limit=limit, offset=offset
    )
    items = []
    for idx, doc in enumerate(records.get("documents", [])):
        meta = (records.get("metadatas") or [None])[idx] or {}
        doc_text = str(doc or "")
        snippet = doc_text[:200]
        items.append(
            {
                "id": (records.get("ids") or [None])[idx],
                "page": meta.get("page"),
                "title": meta.get("title"),
                "snippet": snippet,
            }
        )
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.get("/embeddings_index/{book_filename}")
async def embeddings_index(
    book_filename: str,
    _=Depends(require_permission("load_books")),
):
    """Return cleaned topics_index.json for a book."""
    output_folder = Utils.strip_extension(book_filename)
    index_path = Utils.get_output_path(output_folder) / "topics_index.json"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Index not found")
    try:
        raw = index_path.read_text(encoding="utf-8", errors="replace")
        cleaned = raw.replace("?", "")
        cleaned = re.sub(r"\\ud[0-9a-fA-F]{3}", "", cleaned)
        return {"book_filename": book_filename, "index": cleaned}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
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


@router.get("/exam/options/{book_filename}")
async def exam_options(
    book_filename: str,
    _=Depends(require_permission("exam")),
):
    """Return available chapters/topics for exam generation."""
    generator = ExamGenerator(book_filename)
    options = generator.get_options()
    return {"book_filename": book_filename, **options}


@router.get("/exam/topics/search/{book_filename}")
async def exam_topic_search(
    book_filename: str,
    query: str,
    limit: int = 50,
    _=Depends(require_permission("exam")),
):
    """Search topics by substring for a given book."""
    generator = ExamGenerator(book_filename)
    results = generator.search_topics(query=query, limit=limit)
    return {"book_filename": book_filename, "topics": results}


@router.post("/exam/generate")
async def generate_exam(
    payload: ExamGenerateSchema,
    _=Depends(require_permission("exam")),
):
    """Generate an ephemeral exam based on chapters or topics."""
    generator = ExamGenerator(payload.book_filename)
    try:
        exam = generator.generate_exam(
            mode=payload.mode,
            difficulty=payload.difficulty,
            chapter_numbers=payload.chapter_numbers,
            topics=payload.topics,
        )
    except ValueError as exc:
        Utils.logger.warning("Exam generation failed: %s", exc)
        Utils.logger.warning("Exam payload: %s", payload.model_dump())
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return exam


@router.post("/exam/evaluate")
async def evaluate_exam_answer(
    payload: ExamEvaluateSchema,
    _=Depends(require_permission("exam")),
):
    """Evaluate an open-text exam answer."""
    result = ExamGenerator.evaluate_open_text(
        question=payload.question,
        expected_answer=payload.expected_answer,
        user_answer=payload.user_answer,
        context=payload.context or "",
    )
    return result


@router.post("/exam/evaluate_code")
async def evaluate_exam_code(
    payload: ExamEvaluateCodeSchema,
    _=Depends(require_permission("exam")),
):
    """Evaluate a code-fill exam answer."""
    result = ExamGenerator.evaluate_code(
        code=payload.code,
        function_name=payload.function_name,
        tests=payload.tests,
    )
    return result


@router.get("/check_session/")
async def check_session(token_data=Depends(verify_token)):
    """Checks if the current http cookie has a valid, non-expired token."""
    return {
        "permissions": token_data.get("permissions", ""),
        "session_expiration": token_data.get("exp", ""),
        "username": token_data.get("username", ""),
    }
