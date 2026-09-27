from fastapi import APIRouter
from app.schemas.chat import ChatRequest
from app.services.chat_service import handle_chat_query

router = APIRouter()

@router.post("/query")
async def chat_endpoint(payload: ChatRequest):
    """Unified Chat Endpoint"""
    try:
        response = await handle_chat_query(payload.query)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return {"type": "error", "content": str(e)}
