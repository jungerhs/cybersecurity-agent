import os
from pathlib import Path
import dotenv
dotenv.load_dotenv()

BASE_DIR = Path(__file__).parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

MODEL_CONFIG = {
    "llm_model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 2000,
    "embedding_model": "text-embedding-ada-002"
}

VECTOR_STORE_CONFIG = {
    "persist_directory": str(BASE_DIR / "vector_db"),
    "collection_name": "cybersecurity_docs",
    "embedding_model": "text-embedding-ada-002"
}

DOCUMENT_CONFIG = {
    "documents_path": str(BASE_DIR / "documents"),
    "chunk_size": 500,
    "chunk_overlap": 50,
    "supported_formats": [".pdf", ".md", ".txt"]
}

RETRIEVAL_CONFIG = {
    "top_k": 5,
    "score_threshold": 0.7
}

SEARCH_CONFIG = {
    "max_results": 5,
    "timeout": 10
}

AGENT_CONFIG = {
    "agent_type": "react",
    "max_iterations": 10,
    "verbose": True
}

SECURITY_CONFIG = {
    "sensitive_keywords": ["password", "token", "api_key", "secret", "credential"],
    "mask_pattern": "***"
}

_retriever = None

def get_retriever():
    global _retriever
    return _retriever

def set_retriever(retriever):
    global _retriever
    _retriever = retriever