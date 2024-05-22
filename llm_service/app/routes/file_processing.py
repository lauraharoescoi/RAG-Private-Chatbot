from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils import read_pdf, get_text_chunks 
from app.config import retriever, embeddings, store
import uuid

router = APIRouter()

@router.post("/process_file")
async def process_file(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        original_filename = file.filename
        print("Processing file: ", original_filename)  # For debugging
        documents = read_pdf(file.file, original_filename)
        
        all_text_chunks = []
        all_metadatas = []
        
        for doc in documents:
            text_chunks = get_text_chunks(doc.page_content)
            all_text_chunks.extend(text_chunks)
            all_metadatas.extend([doc.metadata] * len(text_chunks))
            print("Metadatas: ", all_metadatas)  # For debugging
        
        embeddings_results = embeddings.embed_documents(all_text_chunks)
        store.add_embeddings(texts=all_text_chunks, embeddings=embeddings_results, metadatas=all_metadatas)
        
        print("Document stored successfully")  # For debugging
        return {"status": "Document stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
