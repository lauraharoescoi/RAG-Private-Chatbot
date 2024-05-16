from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils import read_pdf, get_text_chunks
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores.pgvector import PGVector
import os
import uuid

router = APIRouter()

CONNECTION_STRING = "postgresql+psycopg2://admin:admin@postgres:5432/vectordb"
COLLECTION_NAME="vectordb"

embeddings = HuggingFaceInstructEmbeddings(
    model_name="hkunlp/instructor-xl",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

store = PGVector(
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
)

@router.post("/process_file")
async def process_file(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        document_id = str(uuid.uuid4())  # Unique ID for the document
        text = read_pdf(file.file)
        text_chunks = get_text_chunks(text)
        embeddings_results = embeddings.embed_documents(text_chunks)
        # Include document_id as metadata for each chunk
        store.add_embeddings(texts=text_chunks, embeddings=embeddings_results, metadata=[{"document_id": document_id} for _ in text_chunks])
        return {"status": "Embeddings stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
