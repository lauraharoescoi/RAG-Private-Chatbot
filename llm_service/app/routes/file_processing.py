from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils import read_pdf, get_text_chunks
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores.pgvector import PGVector
import os
import uuid
from app.config import store, embeddings

router = APIRouter()


@router.post("/process_file")
async def process_file(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        document_id = str(uuid.uuid4())  # Unique ID for the document
        text = read_pdf(file.file)
        text_chunks = get_text_chunks(text)

        # Generate embeddings for the text chunks
        embeddings_results = embeddings.embed_documents(text_chunks)

        # Store the text chunks and their embeddings using PGVector
        store.add_embeddings(texts=text_chunks, embeddings=embeddings_results)

        return {"status": "Embeddings stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
