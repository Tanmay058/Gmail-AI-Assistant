from app.core.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate
import json
import re
from app.services.rag_service import query_emails
from app.services.sentiment_analyzer import analyze_sentiment
from app.core import config

llm = get_llm()

# ULTRA-FAST RAG Prompt (Reduced tokens)
rag_prompt = PromptTemplate.from_template("""
SYSTEM: Act as the user. Match tone of EXAMPLES.
SENTIMENT: {sentiment}

INCOMING:
{email_body}

EXAMPLES:
{examples}

TASK: Return JSON with 3 short reply options.
{{
    "options": [
        {{ "label": "Brief", "body": "1 sentence reply" }},
        {{ "label": "Standard", "body": "2 sentence reply" }},
        {{ "label": "Detailed", "body": "3 sentence reply" }}
    ]
}}
""")

# ULTRA-FAST Fallback Prompt
fallback_prompt = PromptTemplate.from_template("""
SYSTEM: Act as professional assistant.
SENTIMENT: {sentiment}

INCOMING:
{email_body}

TASK: Return JSON with 3 short reply options.
{{
    "options": [
        {{ "label": "Professional", "body": "..." }},
        {{ "label": "Casual", "body": "..." }},
        {{ "label": "Direct", "body": "..." }}
    ]
}}
""")

def extract_replies_from_json(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None

def generate_reply_options(email_body: str, sender_name: str = None):
    """Generate 3 reply options optimized for SPEED"""
    import time
    start_time = time.time()
    print(f"[REPLY GEN] Generating... (Sender: {sender_name}, Body len: {len(email_body)})")
    
    # 1. Analyze Sentiment (Fast - Local Regex)
    sentiment = analyze_sentiment(email_body)
    
    # 2. Check KB Count & Query (Optimize by skipping if empty)
    from app.services.rag_service import get_collection_count
    docs = []
    kb_count = get_collection_count(config.SENT_EMAIL_COLLECTION_NAME)
    
    if kb_count > 0:
        t_rag = time.time()
        print(f"[REPLY GEN] KB not empty ({kb_count} docs). Querying...")
        try:
            docs = query_emails(
                query=email_body, 
                k=2, 
                collection_name=config.SENT_EMAIL_COLLECTION_NAME
            )
            print(f"[REPLY GEN] RAG query took {time.time() - t_rag:.2f}s")
        except:
            print("[REPLY GEN] RAG query failed, falling back.")
            docs = []
    else:
        print("[REPLY GEN] KB is empty. Skipping RAG to save 2-4 seconds.")

    # 3. Build Prompt Examples
    examples_str = ""
    if docs:
        for i, doc in enumerate(docs):
            reply = doc.metadata.get('your_reply', '')[:200]
            if reply:
                examples_str += f"Ex{i+1}: {reply}\n"
    
    # 4. Generate with Gemini
    try:
        t_llm = time.time()
        prompt = rag_prompt if examples_str else fallback_prompt
        chain = prompt | llm
        
        # Inject sender name into body to help AI personalize if it works
        enhanced_body = f"From: {sender_name}\n\n{email_body}" if sender_name else email_body

        response = chain.invoke({
            "email_body": enhanced_body[:600], 
            "sentiment": sentiment,
            "examples": examples_str
        })
        print(f"[REPLY GEN] Gemini call took {time.time() - t_llm:.2f}s")
            
        result = extract_replies_from_json(response)
        
        total_time = time.time() - start_time
        print(f"[REPLY GEN] Total time: {total_time:.2f}s")

        if result and "options" in result:
            result["metadata"] = {
                "sentiment": sentiment,
                "kb_examples_found": len(docs),
                "kb_used": len(docs) > 0,
                "speed_optimized": kb_count == 0,
                "generation_time": round(total_time, 2)
            }
            return result
        else:
             return get_local_fallback(sentiment, "AI returned invalid format", total_time, sender_name)
            
    except Exception as e:
        print(f"[REPLY GEN] AI Failure (likely quota): {e}")
        return get_local_fallback(sentiment, "AI Quota reached or Timeout", time.time() - start_time, sender_name)

def get_local_fallback(sentiment: str, reason: str, elapsed: float, sender: str = None) -> dict:
    """Generate generic replies with optional sender injection for reliability."""
    print(f"[REPLY GEN] Using local fallback. Reason: {reason}")
    
    # Extract just the name if it's an email address
    clean_name = sender.split('<')[0].strip() if sender else ""
    name_prefix = f"Hi {clean_name}, " if clean_name else ""
    
    fallbacks = {
        "positive": [
            {"label": "Quick Thanks", "body": f"{name_prefix}Thank you for the update! Much appreciated."},
            {"label": "Great", "body": f"{name_prefix}That sounds great, thank you for letting me know."},
            {"label": "Acknowledge", "body": f"{name_prefix}Received with thanks. Will get back to you soon."}
        ],
        "negative": [
            {"label": "Apology", "body": f"Hi {clean_name if clean_name else 'there'}, I'm sorry to hear about this. I will look into it immediately."},
            {"label": "Acknowledge", "body": f"{name_prefix}I've received your concern. Let me check and get back to you."},
            {"label": "Check", "body": f"{name_prefix}Thanks for flagging this issue. I'm on it."}
        ],
        "neutral": [
            {"label": "Acknowledged", "body": f"{name_prefix}Got it, thanks for the info."},
            {"label": "I'll check", "body": f"{name_prefix}Thanks, I will review this and reply shortly."},
            {"label": "Ok", "body": f"{name_prefix}Understood. Thanks for reaching out."}
        ]
    }
    
    return {
        "options": fallbacks.get(sentiment, fallbacks["neutral"]),
        "metadata": {
            "sentiment": sentiment,
            "kb_used": False,
            "error": reason,
            "is_fallback": True,
            "generation_time": round(elapsed, 2)
        }
    }
