# RAG_Application
RAG application to chat with the given paragraphs or documents or pdfs using langchains.

##  The AI Consultant (Langchain RAG Test)

A FastAPI microservice that acts as an AI marketing consultant, answering questions using a RAG (Retrieval-Augmented Generation) pipeline powered by a local LLM.

### Prerequisites

- **Ollama:** Install and run [Ollama](https://ollama.com/) locally.
- **Model:** Pull the `phi3:mini` model:
  ```bash
  ollama pull phi3:mini
  ```
  > **Note:** Requires at least 6 GB RAM. Close other memory-intensive apps for best performance.

### Setup & Run

1. **Navigate to the folder:**
   ```bash
   cd part1_langchain
   ```
2. **Create & activate a virtual environment:**
   - **Windows:**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Start the FastAPI server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   > The RAG pipeline initializes on startup (may take a moment).

### Testing

- **Run the test script in a new terminal (with the virtual environment activated):**
  ```bash
  python client_test.py
  ```
  This sends three predefined questions and prints answers, sources, and status.

### API Documentation

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---
