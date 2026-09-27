import re

def analyze_sentiment(text: str) -> str:
    """
    Fast, rule-based sentiment analysis for email content.
    Returns: 'positive', 'negative', or 'neutral'
    """
    text_lower = text.lower()
    
    # Positive keywords
    positive_words = [
        'congratulations', 'congrats', 'thank you', 'thanks', 'great news', 
        'promoted', 'accepted', 'approved', 'welcome', 'excited', 'wonderful',
        'amazing', 'good job', 'well done', 'appreciate', 'happy'
    ]
    
    # Negative keywords
    negative_words = [
        'rejected', 'denied', 'unfortunately', 'regret', 'complaint', 'issue', 
        'problem', 'disappointed', 'sorry', 'error', 'mistake', 'fail', 'bad',
        'upset', 'apologies'
    ]
    
    # Count occurrences
    pos_score = sum(1 for word in positive_words if word in text_lower)
    neg_score = sum(1 for word in negative_words if word in text_lower)
    
    # Analyze
    if pos_score > neg_score and pos_score >= 1:
        return 'positive'
    elif neg_score > pos_score and neg_score >= 1:
        return 'negative'
    else:
        return 'neutral'
