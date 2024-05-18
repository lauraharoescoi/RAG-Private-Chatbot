from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils import read_pdf
from app.config import loader
import uuid
from langchain_core.documents import Document

router = APIRouter()

@router.post("/process_file")
async def process_file(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        document_id = str(uuid.uuid4())  # Unique ID for the document
        text = read_pdf(file.file)
        doc = Document(page_content=text, metadata={"custom_id": document_id, "source": file.filename})
        print(doc)  # Para depuración
        # Use the loader to add documents
        loader.add_documents([doc])
        print("Document stored successfully")  # Para depuración
        return {"status": "Document stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
