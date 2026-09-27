import re
from datetime import datetime, timedelta

def detect_intent(user_query: str) -> dict:
    """
    Simplified keyword-based intent detection.
    Returns a dict with intent, sender, date_query, etc.
    """
    text = user_query.lower().strip()
    now = datetime.now()
    
    # Pre-calculate date strings
    today_str = now.strftime("%Y/%m/%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y/%m/%d")
    day_before_yesterday_str = (now - timedelta(days=2)).strftime("%Y/%m/%d")

    # Initialize results
    intent = "UNKNOWN"
    sender = None
    date_query = None
    keywords = None
    is_unread = "unread" in text or "new" in text
    
    # 1. Check for Sender
    sender_match = re.search(r"\bfrom\s+([a-zA-Z0-9]+)\b", text)
    if sender_match:
        potential_sender = sender_match.group(1)
        if potential_sender not in ["today", "yesterday", "tomorrow", "tonight"]:
            sender = potential_sender
            intent = "FETCH_EMAILS"

    # 2. Check for Dates
    if "today" in text:
        date_query = f"after:{yesterday_str}"
        intent = "FETCH_EMAILS"
    elif "yesterday" in text:
        date_query = f"after:{day_before_yesterday_str} before:{today_str}"
        intent = "FETCH_EMAILS"
    elif "days ago" in text:
        days_match = re.search(r"(\d+)\s+days?\s+ago", text)
        if days_match:
            days = int(days_match.group(1))
            after_date = (now - timedelta(days=days+1)).strftime("%Y/%m/%d")
            before_date = (now - timedelta(days=days)).strftime("%Y/%m/%d")
            date_query = f"after:{after_date} before:{before_date}"
            intent = "FETCH_EMAILS"

    # 3. Check for Search/General
    if any(k in text for k in ["search", "find", "about", "look for"]):
        intent = "SEARCH_EMAILS"
        # Extract keywords after 'about' or 'for'
        keywords_match = re.search(r"(?:search for|find|about)\s+(.+)", text)
        if keywords_match:
            keywords = keywords_match.group(1)

    # 4. Default to FETCH_EMAILS if "unread" or "mails" is mentioned
    if intent == "UNKNOWN" and any(k in text for k in ["unread", "mail", "email", "message"]):
        intent = "FETCH_EMAILS"

    return {
        "intent": intent,
        "sender": sender,
        "date_query": date_query,
        "keywords": keywords,
        "is_unread": is_unread
    }
