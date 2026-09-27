# import os

# # LLM Configuration
# LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama") # ollama, openai, vertexai
# OLLAMA_MODEL = "llama3.1:8b"
# OPENAI_MODEL = "gpt-4o"
# GEMINI_MODEL = "gemini-flash-lite-latest"
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# # RAG Configuration
# CHROMA_PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
# COLLECTION_NAME = "emails"
# SENT_EMAIL_COLLECTION_NAME = "sent_emails_kb"


from pathlib import Path
import os

# Base directory of the project (…/Gmail Assistant Chatbot(AI))
BASE_DIR = Path(__file__).resolve().parents[2]

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # ollama, openai, gemini
OLLAMA_MODEL = "llama3.1:8b"
OPENAI_MODEL = "gpt-4o"
GEMINI_MODEL = "gemini-flash-lite-latest"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# RAG Configuration
CHROMA_PERSIST_DIRECTORY = BASE_DIR / "data" / "chroma_db"
CHROMA_PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)

COLLECTION_NAME = "emails"
SENT_EMAIL_COLLECTION_NAME = "sent_emails_kb"
