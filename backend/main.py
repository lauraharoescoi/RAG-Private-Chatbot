from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from routes import conversation, file_upload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversation.router, prefix="/conversation", tags=["conversation"])
app.include_router(file_upload.router, prefix="/files", tags=["file_upload"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
