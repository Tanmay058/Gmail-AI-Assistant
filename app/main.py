# app/main.py - Updated 13:10
from dotenv import load_dotenv
load_dotenv() # Load env vars immediately

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, chat, email
from app.services.sent_email_service import auto_build_kb_if_needed, sync_recent_sent_emails

app = FastAPI(title="Gmail AI Assistant")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTERS ---
# Include the modular routes from app/api/routes/
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(email.router, prefix="/email", tags=["Email"])

@app.get("/debug/path")
def debug_path():
    import app.llm.reply_generator as rg
    import os
    return {
        "reply_generator_path": os.path.abspath(rg.__file__),
        "cwd": os.getcwd(),
        "timestamp": "12:14"
    }
app.include_router(email.router, prefix="/kb", tags=["Knowledge Base"]) # Shares same file but exposed as /kb/build? Actually it's cleaner if email.py handles both or split. 
# Re-reading my previous step: email.py has /kb/build. 
# But let's check the prefixes. 
# email.py has @router.post("/kb/build"). If I mount it under /email, it becomes /email/kb/build.
# The frontend expects /kb/build. 
# So I should mount email router with NO prefix for those mixed paths, OR refactor deeply.
# To keep frontend working without changes: 
# The email router has: /generate-reply, /send, /kb/build, /unread
# Let's mount it at root "/" or handle specific prefixes?
# Better: Mount at "/" so paths match: /email/generate-reply, /email/send, /kb/build, /emails/unread
# Wait, my email.py defined: @router.post("/generate-reply") -> /email/generate-reply matches? 
# In main.py before it was /email/generate-reply. So mounting at /email works for that.
# But /kb/build was at root /kb/build.
# And /emails/unread was at root /emails/unread.
# So I should probably split them or just mount email router at root "/" to preserve legacy paths?
# Let's see. In email.py:
# @router.post("/generate-reply") -> /email/generate-reply? No, prefix is in main.
# Let's fix email.py paths in my head first.
# If I mount at "/", then email.py needs full paths.
# Let's Update main.py to be simple but compatible.

app.include_router(email.router) # Mounts at root, so paths in email.py must be absolute logic

@app.on_event("startup")
async def startup_event():
    """
    1. Check KB on startup (Build if empty)
    2. Start periodic background sync (every 5 mins)
    """
    import threading
    import time
    
    def background_sync_loop():
        # Initial check
        auto_build_kb_if_needed()
        
        # Loop forever
        while True:
            time.sleep(300) # Wait 5 minutes
            sync_recent_sent_emails()

    # Start the background thread
    threading.Thread(target=background_sync_loop, daemon=True).start()

@app.get("/")
def root():
    return {"message": "Gmail AI Assistant Backend Running (Modular)"}
