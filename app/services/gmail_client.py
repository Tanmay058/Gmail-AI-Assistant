import os
import pickle
import base64
from datetime import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
from email.mime.text import MIMEText

# ---------------- CONFIG ---------------- #
CREDENTIALS_FILE = os.path.join(os.getcwd(), "credentials.json")
TOKEN_FILE = os.path.join(os.getcwd(), "token.pickle")

from supabase import create_client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- HELPERS ---------------- #
def save_credentials(creds):
    """Save credentials to Supabase (Cloud) and fallback to local file."""
    if supabase:
        try:
            # Serialize for DB storage
            token_data = base64.b64encode(pickle.dumps(creds)).decode('utf-8')
            supabase.table("user_tokens").upsert({
                "email": "primary_user",
                "auth_token": token_data
            }).execute()
            print("[SUPABASE] Token saved to cloud.")
        except Exception as e:
            print(f"[SUPABASE] Error saving to cloud: {e}")

    # Local fallback
    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(creds, f)

def load_credentials():
    """Load credentials from Supabase (Cloud) first, then local file."""
    if supabase:
        try:
            response = supabase.table("user_tokens").select("auth_token").eq("email", "primary_user").execute()
            if response.data:
                token_data = response.data[0]["auth_token"]
                print("[SUPABASE] Token loaded from cloud.")
                return pickle.loads(base64.b64decode(token_data))
        except Exception as e:
            print(f"[SUPABASE] Error fetching from cloud: {e}")

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            return pickle.load(f)
    return None

def get_gmail_service(creds):
    return build('gmail', 'v1', credentials=creds)

def decode_email_body(payload):
    """Decode email body, preferring HTML over plain text."""
    parts = payload.get('parts', [])
    
    # 1. If no parts, check the main body
    if not parts:
        data = payload.get('body', {}).get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
        return ""
    
    # 2. Search for HTML part first
    for part in parts:
        if part.get('mimeType') == 'text/html':
            data = part.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
                
    # 3. Fallback to Plain Text
    for part in parts:
        if part.get('mimeType') == 'text/plain':
            data = part.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
                
    # 4. Deep search (recursive for nested parts like multipart/related)
    for part in parts:
        if 'parts' in part:
            return decode_email_body(part)
            
    return ""

def fetch_unread_emails(creds, max_results=10, query='is:unread'):
    """Fetch unread emails with subject, sender, and body. Supports custom query."""
    service = get_gmail_service(creds)

    print(f"[GMAIL] Searching: {query} (max={max_results})")
    results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])

    email_data = []

    for msg in messages:
        try:
            msg_id = msg['id']
            msg_obj = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            payload = msg_obj.get('payload', {})

            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), "")
            snippet = msg_obj.get('snippet', '')

            body = decode_email_body(payload) or snippet

            email_data.append({
                "email_id": msg_id,
                "subject": subject,
                "from": sender,
                "date": date_str,
                "body": body,
                "snippet": snippet
            })
        except Exception as e:
            print(f"[GMAIL] Error fetching message: {e}")

    return email_data

def send_email(creds, to_email, subject, body_text):
    """Send email via Gmail API"""
    service = get_gmail_service(creds)
    message = MIMEText(body_text)
    message['to'] = to_email
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()


