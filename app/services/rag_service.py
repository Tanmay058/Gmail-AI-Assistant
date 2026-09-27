# app/services/rag_service.py
import uuid
from typing import List, Dict
from threading import Lock
import os

from app.services.encryption import encrypt_text, decrypt_text, secure_encrypt_dict, secure_decrypt_dict
from pathlib import Path

from app.core import config
from langchain_core.documents import Document

# -----------------------------
# Chroma / RAG Setup
# -----------------------------
try:
    from langchain_chroma import Chroma
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False
    print("[WARNING] Chroma not found. RAG disabled.")

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    GoogleGenerativeAIEmbeddings = None

# Embeddings (Gemini)
embeddings = None
if config.LLM_PROVIDER.lower() == "gemini" and GoogleGenerativeAIEmbeddings:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=config.GOOGLE_API_KEY
    )

_VECTOR_STORES: dict[str, Chroma] = {}
_VECTOR_STORE_LOCK = Lock()


def get_vector_store(collection_name: str):
    """Return cached Chroma store or create one if missing"""
    if not HAS_CHROMA:
        return None

    with _VECTOR_STORE_LOCK:
        if collection_name not in _VECTOR_STORES:
            _VECTOR_STORES[collection_name] = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings,
                persist_directory=str(config.CHROMA_PERSIST_DIRECTORY)
            )
        return _VECTOR_STORES[collection_name]


# -----------------------------
# Ingest Emails (Encrypt at Rest)
# -----------------------------
def ingest_emails(emails: List[Dict], collection_name: str = config.COLLECTION_NAME):
    """Encrypt emails and store in vector DB"""
    if not emails:
        return

    print(f"[RAG] Ingesting {len(emails)} emails into '{collection_name}'")

    store = get_vector_store(collection_name)
    if not store:
        return

    docs = []
    ids = []

    for email in emails:
        doc_id = email.get("email_id") or str(uuid.uuid4())
        ids.append(doc_id)

        # Encrypt the entire email dict in one call
        encrypted_email = secure_encrypt_dict(email)

        # Create Document for Chroma
        docs.append(
            Document(
                page_content=encrypted_email.get("body", ""),
                metadata={
                    "email_id": email.get("email_id", ""),
                    "subject": encrypted_email.get("subject", ""),
                    "from": encrypted_email.get("from", ""),
                    "date": email.get("date", ""),
                    "sentiment": email.get("sentiment", "neutral"),
                    "your_reply": encrypted_email.get("your_reply", "")
                }
            )
        )

    if not docs:
        return

    try:
        store.add_documents(docs, ids=ids)
        print(f"[RAG] Upserted {len(docs)} encrypted documents.")
    except Exception as e:
        msg = str(e)
        if "RESOURCE_EXHAUSTED" in msg or "Quota" in msg or "429" in msg:
            print("[RAG WARNING] Embedding quota hit. Skipping ingestion.")
            return
        raise


# -----------------------------
# Query Emails (Decrypt in Memory)
# -----------------------------
def query_emails(
    query: str,
    k: int = 4,
    collection_name: str = config.COLLECTION_NAME,
    filter_metadata: Dict | None = None
) -> List[Document]:
    store = get_vector_store(collection_name)
    if not store:
        return []

    results = store.similarity_search(
        query=query,
        k=k,
        filter=filter_metadata
    )

    # Decrypt only in memory
    for doc in results:
        try:
            doc.page_content = decrypt_text(doc.page_content)
            doc.metadata["subject"] = decrypt_text(doc.metadata.get("subject", ""))
            doc.metadata["from"] = decrypt_text(doc.metadata.get("from", ""))
            doc.metadata["your_reply"] = decrypt_text(doc.metadata.get("your_reply", ""))
        except Exception as e:
            print(f"[RAG] Decryption error: {e}")

    return results


# -----------------------------
# Get Collection Count (No Decrypt Needed)
# -----------------------------
def get_collection_count(collection_name: str) -> int:
    try:
        store = get_vector_store(collection_name)
        if not store:
            return 0
        return store._collection.count()
    except Exception as e:
        print(f"[RAG] Count error: {e}")
        return 0


# # -----------------------------
# # Secure Wrapper (Optional)
# # -----------------------------
# def secure_ingest(emails: List[Dict], collection_name: str = config.COLLECTION_NAME):
#     """Encrypt all fields and ingest safely"""
#     for email in emails:
#         email["body"] = encrypt_text(email.get("body", ""))
#         email["subject"] = encrypt_text(email.get("subject", ""))
#         email["from"] = encrypt_text(email.get("from", ""))
#         email["your_reply"] = encrypt_text(email.get("your_reply", ""))
#     ingest_emails(emails, collection_name)




