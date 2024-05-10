from dotenv import find_dotenv, load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceInstructEmbeddings

from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from PyPDF2 import PdfReader

# PGVector needs the connection string to the database.
CONNECTION_STRING = "postgresql+psycopg2://admin:admin@127.0.0.1:5433/vectordb"
COLLECTION_NAME = "vectordb"
load_dotenv(find_dotenv())

def get_pdf_text(pdf_docs):
    text = ''.join(doc.page_content for doc in pdf_docs)
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore_from_docs(pdf_docs):
    
    text = get_pdf_text(pdf_docs)
    print("text", text)
    text_chunks = get_text_chunks(text)
    print("text_chunks", text_chunks)
    embeddings = HuggingFaceInstructEmbeddings(
        model_name="hkunlp/instructor-xl",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vector_store = PGVector.from_texts(
        text_chunks,
        embeddings,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING
    )
    

    return vector_store

loader = PyPDFLoader(
    "./docs/CV_PaquitaEscoi_2023_cat.pdf",
    )
pdf_docs = loader.load()
print("pdf_docs", pdf_docs)


get_vectorstore_from_docs(pdf_docs)

# # embeddings = OpenAIEmbeddings()
# embeddings = HuggingFaceInstructEmbeddings(
#         model_name="hkunlp/instructor-xl",
#         model_kwargs={'device': 'cpu'},
#         encode_kwargs={'normalize_embeddings': True}
#     )
# loader = DirectoryLoader(
#     "./docs", glob="**/*.txt", loader_cls=TextLoader, show_progress=True
# )
# documents = loader.load()
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# docs = text_splitter.split_documents(documents)




# PGVector.from_documents(
#     docs,
#     embeddings,
#     collection_name=COLLECTION_NAME,
#     connection_string=CONNECTION_STRING
# )