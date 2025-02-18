# Simple ISP company chat backend

This is a simple Streamlit chatapp for an ISP company. Ultilizing RAG with Langchain, using Cohere's Command R+ and Groq's fast LLMs.

## Setup

1. put stack.env in the same directory as this file
2. put the sample data folder in the src directory
3. run `docker compose up`

## Environment Variables

- **Credentials**:

* `POSTGRES_USER`: The username for the PostgreSQL database
* `POSTGRES_PASSWORD`: The password for the PostgreSQL database
* `LLM_DB_USER`: The username for the read-only account of the llm.
* `LLM_DB_PASSWORD`: The password for the read-only account of the llm.
* `DB_HOST`: The host for the PostgreSQL database
* `DB_PORT`: The port for the PostgreSQL database
* `COHERE_API_KEY`: The API key for the Cohere API
* `GROQ_API_KEY`: The API key for the Groq API

- **Options**:

* `INIT_DB_ON_STARTUP`: Set to "TRUE" to run the database initialization (db, user, table creation, data insertion and vectordb creation) script every time the app starts. Else "False" if you have already ran the script and want to use the existing database.
* `LANGSMITH_TRACING`: Set to "true" to enable tracing for LangSmith API. Else "false" if you want to disable tracing.
* `LANGSMITH_ENDPOINT`: The endpoint for the LangSmith API.
* `LAMGSMITH_PROJECT`: The project ID for the LangSmith API.
* `LANGSMITH_API_KEY`: The API key for the LangSmith API

## Optional

- put the config.json and credentials.json in the src directory to use those instead of the environment variables
