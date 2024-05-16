# Private Company Chatbot

This repository contains the code for a private chatbot developed by Insdo SL. The chatbot uses a language model (LLM) with LangChain to answer questions about employees based on their resumes and other stored information.

## Project Structure

The application is divided into several microservices that communicate with each other. Below is a description of the structure and function of each microservice:

### Microservices

- **Postgres**: PostgreSQL database used to store embeddings with the `pgvector` extension.
- **Mongo**: MongoDB database used to store chatbot conversations.
- **Backend**: API developed with FastAPI that handles chatbot requests and responses, and communicates with MongoDB and the LLM service.
- **LLM Service**: Service responsible for processing requests to the language model using LangChain and HuggingFace.
- **Frontend**: User interface developed in Angular to interact with the chatbot.

## Deployment and Execution

To deploy and run the application, follow these steps:

1. Clone the repository.
2. Build and bring up the Docker containers using `docker-compose`:
   ```sh
   docker-compose up --build
   ```
3. Access the web interface at `http://localhost:4201`.



