import logging
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import tempfile

ROLE_CLASS_MAP = {
    "assistant": AIMessage,
    "user": HumanMessage,
    "system": SystemMessage
}

def create_messages(conversation):
    return [ROLE_CLASS_MAP[message.role](content=message.content) for message in conversation]

def extract_last_assistant_message(full_response):
    messages = full_response.split('</s>')
    for message in reversed(messages):
        return message.strip()
    return "No response found from the assistant."

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_text(text)
    return chunks

def read_pdf(file, original_filename):
    # Crear un archivo temporal para que PyMuPDFLoader lo procese
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file.read())
        tmp_file_path = tmp_file.name

    loader = PyMuPDFLoader(tmp_file_path)
    documents = loader.load()
    
    # Añadir el nombre original del archivo a los metadatos
    for doc in documents:
        doc.metadata["source"] = original_filename
    
    # Eliminar el archivo temporal
    tmp_file.close()
    
    return documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
