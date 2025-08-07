import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# LangChain Imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ai_consultant")

# --- Knowledge Base Articles ---
ARTICLE_1 = """
Article 1: Introduction to Google Ads for Small Business

"""

ARTICLE_2 = """
Article 2: Understanding Meta (Facebook) Ad Campaigns

"""

ARTICLE_3 = """
Article 3: The Importance of Landing Pages
"""
ARTICLE_4 = """
Article 4: UrbanClap Case Study
"""
KNOWLEDGE_BASE = [
    Document(page_content=ARTICLE_1, metadata={"source": "Article 1: Introduction to Google Ads"}),
    Document(page_content=ARTICLE_2, metadata={"source": "Article 2: Understanding Meta Ads"}),
    Document(page_content=ARTICLE_3, metadata={"source": "Article 3: The Importance of Landing Pages"}),
    Document(page_content=ARTICLE_4, metadata={"source": "UrbanClap Case Study"})
]

app = FastAPI(
    title="AI Marketing Consultant API",
    description="A RAG-powered API to answer marketing questions based on a fixed knowledge base."
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to hold the vector store
vector_store = None

@app.on_event("startup")
def startup_event():
    """
    On application startup, load articles, create embeddings, and build the vector store.
    """
    global vector_store
    logger.info("Application startup: Initializing RAG pipeline...")
    
    try:
        # 1. Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(KNOWLEDGE_BASE)
        logger.info(f"Split knowledge base into {len(chunks)} chunks.")

        # 2. Load open-source embeddings model
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # 3. Create FAISS vector store
        vector_store = FAISS.from_documents(chunks, embedding=embeddings)
        logger.info("FAISS vector store created successfully.")

    except Exception as e:
        logger.error(f"Error during startup initialization: {e}")
        # If the pipeline fails to build, the app should not start correctly.
        # In a real-world scenario, you might want more robust error handling.
        raise RuntimeError(f"Failed to initialize the RAG pipeline: {e}")


# --- Pydantic Models for Request and Response ---
class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    source: str
    status: str # "ANSWERED_FROM_CONTEXT" or "CONTEXT_NOT_FOUND"


@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Accepts a question, retrieves relevant context, and generates an answer.
    """
    if vector_store is None:
        logger.error("Vector store not initialized. The application may have failed to start correctly.")
        raise HTTPException(status_code=500, detail="Vector store is not available.")
    
    logger.info(f"Received question: {request.question}")

    try:
        # Initialize LLM - using Ollama 
        # modify this as per your need. This phi3:mini is the basic one for small text based conversations
        # running using local ollama 
        llm = OllamaLLM(model="phi3:mini")

        # Create a prompt template that forces the LLM to answer only from context
        # and to output a specific string if the answer is not found.
        prompt = ChatPromptTemplate.from_template("""
        Answer the user's question based strictly and exclusively on the provided context.

        <context>
        {context}
        </context>

        Question: {input}
        """)

        # Create the RAG chain
        retriever = vector_store.as_retriever(search_kwargs={'k': 2}) # Retrieve top 2 chunks
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # Invoke the chain
        response = retrieval_chain.invoke({"input": request.question})
        
        answer = response.get("answer", "").strip()
        context_docs = response.get("context", [])

        # Format the source text from the retrieved documents
        source_text = "\n---\n".join([doc.page_content for doc in context_docs])

        # Check if the LLM indicated that the context was not found
        if "CONTEXT_NOT_FOUND" or "context_not_found" or "ConTEXT_NOT_FOUND" in answer:
            status = "CONTEXT_NOT_FOUND"
            final_answer = "I could not find an answer to your question in the provided marketing articles."
            source_text = "No relevant context found." # Clear source if not found
        else:
            status = "ANSWERED_FROM_CONTEXT"
            final_answer = answer

        logger.info(f"Generated Answer: {final_answer}")
        logger.info(f"Status: {status}")
        
        return AskResponse(answer=final_answer, source=source_text, status=status)

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your request: {e}")