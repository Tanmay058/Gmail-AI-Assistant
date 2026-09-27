from app.llm.summarizer import summarize_email
from app.llm.classifier import classify_email
from app.llm.reply_generator import generate_reply


def generate_auto_reply(email_text: str) -> dict:
    # Step 1: Summarize
    summary_obj = summarize_email(email_text)
    summary = summary_obj.summary

    # Step 2: Classify
    classification_obj = classify_email(email_text)
    classification = classification_obj.dict()

    # Step 3: Generate Reply
    reply = generate_reply(
        original_email=email_text,
        summary=summary,
        classification=classification
    )

    return {
        "summary": summary,
        "classification": classification,
        "reply": reply
    }
