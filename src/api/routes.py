"""Entry point for the api ."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .assistant import Assistant
from .generate_embeddings import EmbeddingsGenerator
from .utils import Utils
from .logging import setup_logging

app = FastAPI()

# Define input schema for user queries
class Query(BaseModel):
    question: str

class BookData(BaseModel):
    book_filename: str

@app.post("/generate_embeddings/")
async def generate_embeddings(book_data: BookData):
    """Endpoint to generate the embeddings database"""
    book_filename = book_data.book_filename
    output_folder = Utils.strip_extension(book_filename)
    Utils.logger = setup_logging(output_folder)
    embeddings_collection = Utils.get_embeddings_db(output_folder)

    embeddings_generator = EmbeddingsGenerator(book_filename)
    embeddings = embeddings_generator.generate_embeddings()
    if embeddings:
        return {"message": f"Embeddings generated successfully. Vector database stored at /output/{output_folder}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate embeddings")

@app.post("/ask/")
async def ask_question(query: Query, book_data: BookData):
    """Endpoint for asking a question"""
    book_filename = book_data.book_filename
    embeddings_collection = Utils.get_embeddings_db(book_filename)  # Get existing embeddings collection

    if not embeddings_collection:
        raise HTTPException(status_code=400, detail="Embeddings not generated. Please run 'generate_embeddings' first.")
    
    assistant = Assistant(book_filename, embeddings_collection)
    answer = assistant.ask(query.question)
    return {"answer": answer}

@app.post("/process_all/")
async def process_all(book_data: BookData):
    """Endpoint to run all actions (generate embeddings, then ask questions)"""
    # Generate embeddings first
    await generate_embeddings(book_data)
    return {"message": "Embeddings generated and ready for querying."}
