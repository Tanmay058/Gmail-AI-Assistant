from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.llm.reply_generator import generate_reply_options
from app.services.gmail_client import load_credentials, fetch_unread_emails, send_email
from app.services.sent_email_service import build_sent_emails_kb

router = APIRouter()

class ReplyRequest(BaseModel):
    email_text: str
    sender: str = None

class SendReplyRequest(BaseModel):
    email_id: str
    reply_body: str

@router.post("/email/generate-reply")
def generate_reply_endpoint(req: ReplyRequest):
    return generate_reply_options(req.email_text, req.sender)

@router.post("/email/send")
def send_reply_endpoint(req: SendReplyRequest):
    creds = load_credentials()
    if not creds:
        raise HTTPException(401, "Not authenticated")
    
    # We need to find the recipient (this is a simplified logic, ideally we pass to_email)
    emails = fetch_unread_emails(creds, max_results=50) 
    target_email = next((e for e in emails if e['email_id'] == req.email_id), None)
    
    if not target_email:
        print(f"[DEBUG] Email {req.email_id} not found in recent unread to reply to.")
        raise HTTPException(404, "Original email not found in recent unread list.")

    send_email(creds, target_email['from'], "Re: " + target_email['subject'], req.reply_body)
    return {"status": "sent"}

# --- KB Routes (Grouped under email as they relate to email data) ---

@router.post("/kb/build")
def build_knowledge_base(background_tasks: BackgroundTasks):
    """Trigger background task to build Knowledge Base from sent emails"""
    background_tasks.add_task(build_sent_emails_kb, max_results=100)
    return {"status": "started", "message": "Knowledge base build started in background."}

@router.get("/emails/unread")
def get_unread_emails():
    """Get all unread emails (for sidebar)"""
    creds = load_credentials()
    if not creds:
        raise HTTPException(401, "Not authenticated. Please login first.")
    
    emails = fetch_unread_emails(creds, max_results=100)  # Get up to 100 emails
    return {"emails": emails, "count": len(emails)}
