from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
import requests

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload")
async def upload_files(file: UploadFile = File(...)):
    try:
        files = {'file': (file.filename, file.file, file.content_type)}
        response = requests.post("http://llm_service:80/process_file", files=files)
        response.raise_for_status()
        return {"message": "PDF processed successfully", "data": response.json()}
    except Exception as e:
        logger.error(f"File processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
