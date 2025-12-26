# Interactive Textbook Backend

This directory contains the FastAPI backend services for the "Physical AI & Humanoid Robotics" interactive textbook. It provides:

-   A RAG (Retrieval-Augmented Generation) chatbot for answering questions based on book content.
-   User authentication (signup/signin) and profile management with software/hardware background.
-   An API for on-demand chapter content translation into Urdu.

## Technologies Used

-   **FastAPI**: Web framework for building the API.
-   **LangChain**: For building the RAG pipeline.
-   **HuggingFaceEmbeddings**: For generating text embeddings.
-   **Qdrant Cloud**: Vector database for storing book content embeddings.
-   **OpenAI API**: For large language model (LLM) generation in the RAG chatbot.
-   **Neon Serverless Postgres**: Database for user profiles.
-   **Better-Auth.com**: External service for user authentication.
-   **Google Translate API**: For translation services.

## Getting Started

To get the backend services up and running locally, follow these steps.

### Prerequisites

-   Python 3.10+
-   Poetry (recommended for dependency management) or pip
-   Access to external services (OpenAI, Better-Auth, Neon, Qdrant, Google Cloud for Translate API).

### Installation

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Install dependencies using Poetry:**
    ```bash
    poetry install
    ```
    If you don't use Poetry, you would install dependencies from a `requirements.txt` file (which you would generate from `poetry export -f requirements.txt --output requirements.txt --without-hashes`).

3.  **Set up Environment Variables:**
    Create a `.env` file in the `backend/` directory and populate it with your credentials and service URLs:
    ```env
    OPENAI_API_KEY="sk-..."
    GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google-credentials.json"
    BETTER_AUTH_API_KEY="..." # Placeholder, replace with actual
    NEON_DATABASE_URL="postgres://..."
    QDRANT_URL="https://..."
    QDRANT_API_KEY="sk_..."
    ```

## Running the Backend

1.  **Activate your virtual environment (if using Poetry):**
    ```bash
    poetry shell
    ```

2.  **Start the FastAPI server:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The API will be available at `http://localhost:8000`. You can access the auto-generated OpenAPI documentation (Swagger UI) at `http://localhost:8000/docs`.

## Data Ingestion

To populate the Qdrant vector store with the book's content, you must run the ingestion script. This process reads all content from the `frontend/docs` directory, splits it into chunks, creates vector embeddings, and stores them in your Qdrant collection.

1.  **Ensure your `.env` file is correctly configured** with your `QDRANT_URL` and `QDRANT_API_KEY`.

2.  **Navigate to the `backend` directory** and activate your virtual environment if you haven't already.

3.  **Run the ingestion script:**
    ```bash
    python scripts/ingest_data.py
    ```
    This will start the indexing process. Wait for it to complete. You only need to run this once, unless the book's content changes significantly.

## Testing

To run the unit tests for the backend services:

1.  **Activate your virtual environment.**
2.  **Install pytest (if not already installed):**
    ```bash
    pip install pytest
    ```
3.  **Run tests:**
    ```bash
    pytest tests/
    ```
