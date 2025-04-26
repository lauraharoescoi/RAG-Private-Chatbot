# 🤖 RAG Private Chatbot

This repository contains the code for my final degree project in Computer Engineering, developed during an internship. The project consists of a private chatbot that uses Retrieval-Augmented Generation (RAG) technology to answer questions about employees based on their resumes and other stored information.

---

## 📝 Overview

The chatbot leverages the combination of a **Language Model (LLM)** and a **retrieval system** to generate more accurate and context-aware answers. Instead of relying solely on the model's knowledge, the chatbot first **retrieves relevant information** from a database and then **uses the LLM to generate the final response**.

---

## 🏗️ Project Structure

The project is composed of several microservices, each handling a specific part of the system:

### 🧩 Microservices

- **Postgres**: PostgreSQL database with the `pgvector` extension, used to store document embeddings.
- **MongoDB**: NoSQL database to store conversations between users and the chatbot.
- **Backend (Conversation Service)**: FastAPI server that handles the user messages, manages conversations, and interacts with the LLM service.
- **LLM Service**: FastAPI server that processes queries using LangChain, retrieves context from the vector database, and generates answers with HuggingFace models.
- **Frontend**: Angular application where users interact with the chatbot and can upload PDF documents.

<p align="center">
  <img src="https://github.com/user-attachments/assets/56d03ed2-7ad4-4036-86e1-ce9b313c3bbf" alt="Project Architecture" width="600"/>
</p>

---

## ⚙️ How It Works

### 📥 Ingestion Pipeline (Document Upload)

1. **Loading**: Users upload PDF files via the frontend. These documents are parsed and text is extracted.
2. **Chunking**: Extracted text is split into smaller chunks to facilitate efficient retrieval.
3. **Embedding**: Each chunk is transformed into a high-dimensional vector (embedding) using a HuggingFace model.
4. **Storage**: The embeddings are stored in PostgreSQL with `pgvector`.

<p align="center">
  <img src="https://github.com/user-attachments/assets/32ba2728-6c20-45fb-99e3-585481a2e5f4" alt="Document Upload Pipeline" width="1000"/>
</p>

### 💬 Query Pipeline (Chat Interaction)

1. **User Query**: The user sends a question through the frontend.
2. **Embedding Query**: The question is converted into an embedding.
3. **Retrieval**: The system searches for the most similar chunks in the vector store (Postgres + pgvector).
4. **Context Construction**: The retrieved chunks are collected to build a context.
5. **Answer Generation**: The LLM (using LangChain and HuggingFace) generates the final answer based on the retrieved context.

<p align="center">
  <img src="https://github.com/user-attachments/assets/550d5b28-35a7-48f1-9226-ca97e69057c5" alt="Query Pipeline" width="1000"/>
</p>

---

## 🛠️ Key Technologies

- **FastAPI**: Backend APIs (Conversation Service and LLM Service).
- **LangChain**: LLM orchestration and retrieval management.
- **PostgreSQL + pgvector**: Vector storage and similarity search.
- **MongoDB**: Storage of chat histories.
- **Angular**: Frontend interface.
- **HuggingFace**: Pre-trained models for embeddings and generation.

---

## 🚀 Setup and Deployment

### ⚡ Requirements
- Docker and Docker Compose installed.

### 🖥️ Running the Project
Clone the repository and run:
```bash
docker-compose up --build
```
The services will be available at:
- Frontend: `http://localhost:4201`
- Conversation API: `http://localhost:8000`
- LLM API: `http://localhost:8001`
- Postgres: `localhost:5432`
- MongoDB: `localhost:27017`

---

## 🙌 Acknowledgements

Special thanks to **David Sarrat González** and **Victor Albà Solé** for their support and guidance throughout this project.

---

## 📚 Related Work

If you are interested in a deeper technical explanation, you can check the full [Final Degree Thesis Report (TFG)](https://repositori.udl.cat/items/788cdb52-03a2-4423-a2f7-a232aca416f3).
