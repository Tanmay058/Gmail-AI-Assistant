from app.services.gmail_client import get_gmail_service, load_credentials, decode_email_body
from app.services.rag_service import ingest_emails
from app.services.sentiment_analyzer import analyze_sentiment
from app.core import config
import logging

def build_sent_emails_kb(max_results=50):
    """
    Fetches sent emails, finds the original email in the thread,
    pairs them, analyzes sentiment, and stores in ChromaDB.
    """
    print("[KB BUILD] Starting knowledge base construction...")
    creds = load_credentials()
    if not creds:
        print("[KB BUILD] Error: No credentials found")
        return {"status": "error", "message": "Not authenticated"}

    service = get_gmail_service(creds)
    
    # 1. Fetch Sent Emails
    # query = 'label:SENT -label:DRAFT' (using 'me' as userId implies 'from:me')
    print("[KB BUILD] Fetching sent emails...")
    results = service.users().messages().list(
        userId='me', q='label:SENT', maxResults=max_results
    ).execute()
    sent_messages = results.get('messages', [])
    
    print(f"[KB BUILD] Found {len(sent_messages)} sent emails. Processing...")
    
    kb_entries = []
    
    for i, msg in enumerate(sent_messages):
        try:
            # Get full sent message details
            sent_msg_full = service.users().messages().get(
                userId='me', id=msg['id'], format='full'
            ).execute()
            
            thread_id = sent_msg_full.get('threadId')
            headers = sent_msg_full.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            
            # Extract your reply body
            my_reply_body = decode_email_body(sent_msg_full.get('payload', {}))
            
            # Skip empty replies
            if not my_reply_body or len(my_reply_body) < 10:
                continue

            # 2. Fetch the entire thread to find the PREVIOUS message (what you replied to)
            thread = service.users().threads().get(userId='me', id=thread_id).execute()
            messages_in_thread = thread.get('messages', [])
            
            # Find the message immediately before my sent message
            # Messages are usually chronological. 
            # We want the last message from someone else BEFORE my current sent message.
            original_email_body = None
            original_sender = None
            
            # Iterate backwards from the current message
            # Find index of current message in thread
            curr_idx = -1
            for idx, m in enumerate(messages_in_thread):
                if m['id'] == msg['id']:
                    curr_idx = idx
                    break
            
            if curr_idx > 0:
                # Look at message before it
                prev_msg = messages_in_thread[curr_idx - 1]
                # Verify it's not also from me (in case of double reply) - logic simplified
                prev_msg_full = service.users().messages().get(
                    userId='me', id=prev_msg['id'], format='full'
                ).execute()
                
                original_email_body = decode_email_body(prev_msg_full.get('payload', {}))
                prev_headers = prev_msg_full.get('payload', {}).get('headers', [])
                original_sender = next((h['value'] for h in prev_headers if h['name'] == 'From'), "Unknown")
            
            if original_email_body:
                # 3. Analyze Sentiment of the ORIGINAL email (the context)
                sentiment = analyze_sentiment(original_email_body)
                
                # 4. Prepare Entry
                # We store the ORIGINAL email body as the content to embed
                # So when we query with a NEW incoming email, we find similar received emails
                entry = {
                    "email_id": msg['id'],
                    "subject": subject,
                    "body": original_email_body, # The 'Question' / Context
                    "from": original_sender,
                    "your_reply": my_reply_body, # The 'Answer' / Target
                    "sentiment": sentiment
                }
                kb_entries.append(entry)
                print(f"[KB BUILD] Processed pair {i+1}/{len(sent_messages)}...")
            
        except Exception as e:
            print(f"[KB BUILD] Error processing message {msg['id']}: {e}")
            continue

    # 5. Ingest into ChromaDB
    if kb_entries:
        print(f"[KB BUILD] Ingesting {len(kb_entries)} pairs into Vector DB...")
        ingest_emails(kb_entries, collection_name=config.SENT_EMAIL_COLLECTION_NAME)
        print("[KB BUILD] Knowledge base updated successfully!")
        return {"status": "success", "count": len(kb_entries)}
    else:
        print("[KB BUILD] No valid pairs found to ingest.")
        return {"status": "warning", "message": "No pairs found"}

def auto_build_kb_if_needed():
    """
    Check if KB exists and has data. If not, trigger build.
    Runs on server startup.
    """
    try:
        from app.services.rag_service import get_vector_store
        store = get_vector_store(config.SENT_EMAIL_COLLECTION_NAME)
        
        # Check if empty (using simple get call)
        # Chroma doesn't have a direct count() method on the class easily accessible
        # so we try to get 1 item
        existing = store.get(limit=1)
        
        if existing and existing['ids']:
            print(f"[AUTO KB] Knowledge Base '{config.SENT_EMAIL_COLLECTION_NAME}' already exists. Skipping auto-build.")
            return
        
        print(f"[AUTO KB] Knowledge Base '{config.SENT_EMAIL_COLLECTION_NAME}' is empty. Triggering auto-build...")
        build_sent_emails_kb(max_results=50)
        
    except Exception as e:
        print(f"[AUTO KB] Error during check: {e}")

def sync_recent_sent_emails():
    """
    Background task to fetch ONLY recent sent emails (e.g. last 10)
    and add them to KB. Relying on Chroma's ID-based upsert to handle duplicates.
    """
    try:
        print("[AUTO SYNC] Checking for new sent emails...")
        # Re-use build logic but with small limit
        result = build_sent_emails_kb(max_results=10)
        
        if result.get('status') == 'success':
            print(f"[AUTO SYNC] Synced {result['count']} emails.")
        else:
            print(f"[AUTO SYNC] operational: {result.get('message')}")
            
    except Exception as e:
        print(f"[AUTO SYNC] Sync failed: {e}")
