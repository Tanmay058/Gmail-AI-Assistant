import logging
from app.services.intent_detector import detect_intent
from app.services.rag_service import query_emails, ingest_emails
from app.services.gmail_client import fetch_unread_emails, load_credentials
from app.llm.summarizer import summarize_email, summarize_emails_batch
from app.core.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate

llm = get_llm()

# Prompt for answering questions based on context
qa_prompt = PromptTemplate.from_template("""
You are a helpful email assistant. Use the following context (emails) to answer the user's question.
If the answer is not in the context, say you don't know interactively.

Context:
{context}

Question:
{question}

Answer:
""")

async def handle_todays_briefing():
    """Fetch and summarize today's unread emails."""
    creds = load_credentials()
    if not creds:
        return {"type": "error", "content": "Please login first."}
    
    from datetime import datetime, timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y/%m/%d")
    query = f"is:unread after:{yesterday}"
    
    emails = fetch_unread_emails(creds, max_results=10, query=query)
    if not emails:
        return {"type": "text", "content": "No unread emails found for today."}
    
    return await format_briefing_response(emails, "Here is a summary of today's unread emails.")

async def handle_unread_briefing():
    """Fetch and summarize all unread emails."""
    creds = load_credentials()
    if not creds:
        return {"type": "error", "content": "Please login first."}
    
    emails = fetch_unread_emails(creds, max_results=10, query="is:unread")
    if not emails:
        return {"type": "text", "content": "You have no unread emails."}
    
    return await format_briefing_response(emails, "Here is a summary of all your unread emails.")

async def search_emails_by_sender(sender_name: str):
    """Search emails from a specific sender."""
    creds = load_credentials()
    if not creds:
        return {"type": "error", "content": "Please login first."}
    
    emails = fetch_unread_emails(creds, max_results=10, query=f"from:{sender_name}")
    if not emails:
        return {"type": "text", "content": f"No emails found from {sender_name}."}
    
    return await format_briefing_response(emails, f"Here are the latest emails from {sender_name}:")

async def format_briefing_response(emails, content_text):
    """Helper to summarize and format the response."""
    from app.services.preprocess import clean_email
    # Summarize only top 5 for better stability
    bodies = [e.get('body', '') for e in emails[:5]]
    summaries = summarize_emails_batch(bodies)
    
    email_summaries_debug = []
    for i, email in enumerate(emails):
        summary = summaries[i] if i < len(summaries) else ""
        # Strictly ensure the summary is cleaned text
        clean_s = clean_email(str(summary))
        if not clean_s or clean_s.startswith("(Note:") or len(clean_s) < 10:
            # If AI summary is weak or image-only, use cleaned snippet/body
            clean_s = clean_email(email.get('snippet', email.get('body', '')))[:160]
        
        email['summary'] = clean_s
    
    return {
        "type": "briefing",
        "content": content_text,
        "emails": emails,
        "total_count": len(emails)
    }

async def handle_rag_query(query: str):
    """Query RAG for answers."""
    docs = query_emails(query)
    if not docs:
        return {"type": "text", "content": "I couldn't find any relevant emails matching your query."}

    context = "\n\n".join([doc.page_content for doc in docs])
    
    chain = qa_prompt | llm
    answer = chain.invoke({"context": context, "question": query})
    
    return {
        "type": "text",
        "content": answer,
        "sources": [doc.metadata for doc in docs]
    }

async def handle_chat_query(query: str):
    """
    Main entry point for chat queries.
    Determines intent and routes to appropriate handler.
    """
    print(f"[DEBUG] Starting handle_chat_query with query: {query}")
    intent_data = detect_intent(query)
    intent = intent_data.get("intent", "UNKNOWN")
    
    if "today" in query.lower():
        return await handle_todays_briefing()
    elif intent == "SEARCH_EMAILS" and intent_data.get("sender"):
        return await search_emails_by_sender(intent_data["sender"])
    elif intent == "KB_QUERY":
        return await handle_rag_query(query)
    elif intent == "FETCH_EMAILS":
        if not intent_data.get("date_query") and not intent_data.get("sender"):
            return await handle_unread_briefing()
        
        # General case for fetching emails based on keyword/sender extracts
        creds = load_credentials()
        if not creds: return {"type": "error", "content": "Please login first."}
        
        q_parts = []
        if intent_data.get("is_unread"): q_parts.append("is:unread")
        if intent_data.get("sender"): q_parts.append(f"from:{intent_data['sender']}")
        if intent_data.get("date_query"): q_parts.append(intent_data['date_query'])
        if intent_data.get("keywords"): q_parts.append(intent_data['keywords'])
        
        final_query = " ".join(q_parts) or "is:unread"
        emails = fetch_unread_emails(creds, max_results=10, query=final_query)
        if not emails: return {"type": "text", "content": "No emails found matching your request."}
        return await format_briefing_response(emails, "I found these emails for you:")
    else:
        # Final fallback
        return await handle_unread_briefing()
