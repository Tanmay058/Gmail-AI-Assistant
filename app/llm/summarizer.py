import json
import re
# from langchain_ollama import OllamaLLM # Removed for lean cloud build
from langchain_core.prompts import PromptTemplate
from app.schemas.summary import SummaryResult


from app.core.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate
from app.schemas.summary import SummaryResult
from app.services.preprocess import clean_email

llm = get_llm()

prompt = PromptTemplate.from_template("""
You are an email summarization assistant.

Return ONLY a short natural language summary.
DO NOT return JSON.
DO NOT return markdown.
DO NOT return lists.

Email:
{email}

Short summary (1-2 sentences):
""")


def extract_summary_from_json(text: str) -> str | None:
    """
    If model returns JSON by mistake, extract summary safely.
    """
    try:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        data = json.loads(match.group())

        # Handle multiple formats
        if isinstance(data.get("summary"), list):
            return " ".join(data["summary"])
        elif isinstance(data.get("summary"), str):
            return data["summary"]
    except Exception:
        return None

    return None


def summarize_email(email: str) -> SummaryResult:
    clean_text = clean_email(email)
    chain = prompt | llm
    raw_output = chain.invoke({"email": clean_text})

    if raw_output is None:
        raise ValueError("LLM returned None for summary")

    raw_output = raw_output.strip()

    print("\n----- RAW SUMMARY OUTPUT -----")
    print(raw_output)
    print("------------------------------\n")

    # Try JSON fallback
    json_summary = extract_summary_from_json(raw_output)
    if json_summary:
        return SummaryResult(summary=json_summary)

    # Validate plain text
    if len(raw_output) < 5:
        raise ValueError(f"Invalid LLM output:\n{raw_output}")

    # ✅ ALWAYS RETURN
    return SummaryResult(summary=raw_output)


def summarize_email_light(email_text: str) -> str:
    """
    Ultra-fast summarization for list views.
    Returns 1 sentence summary (max 15 words) or fallback.
    """
    try:
        clean_text = clean_email(email_text)
        if not clean_text or len(clean_text) < 50:
            return clean_text[:100]  # Too short to summarize
            
        # Truncate aggressively for speed
        truncated_text = clean_text[:400]
        
        # Simple prompt
        prompt = f"Summarize in 1 short sentence (max 12 words):\n{truncated_text}"
        
        # Invoke LLM (assuming LLM object is reusable/thread-safe)
        response = llm.invoke(prompt)
        
        # Cleanup
        summary = response.strip().replace('"', '').replace('\n', ' ')
        
        # Post-process cleanup
        if len(summary) > 150:
            return summary[:147] + "..."
            
        return clean_email(summary)
        
    except Exception as e:
        print(f"[SUMMARIZER] Error: {e}")
        return clean_email(email_text)[:100] + "..."


def summarize_emails_batch(emails: list[str]) -> list[str]:
    """
    Summarize multiple emails in a SINGLE LLM call to save time.
    """
    if not emails:
        return []
        
    print(f"[SUMMARIZER] Batch summarizing {len(emails)} emails...")
    
    # Construct a batched prompt
    combined_text = ""
    for i, email in enumerate(emails):
        # Clean and truncate each email for the prompt
        clean_body = clean_email(email)[:400].replace('\n', ' ')
        combined_text += f"\n--- EMAIL {i+1} ---\n{clean_body}\n"
        
    prompt = f"""
    SYSTEM: You are a JSON-only API. 
    TASK: Summarize these {len(emails)} emails.
    REQUIREMENT: 
    1. Output MUST be a valid raw JSON list of strings.
    2. One sentence per email. Max 15 words each.
    3. NO introduction. NO explanation. NO markdown formatting.
    
    EMAILS:
    {combined_text}
    
    OUTPUT FORMAT: ["Summary 1", "Summary 2"]
    JSON RESPONSE:
    """
    
    try:
        response = llm.invoke(prompt)
        print(f"[SUMMARIZER] Raw Layout: {response[:100]}...") # Debug log
        
        # Robust Parsing Strategy
        import json
        
        # 1. Try simple clean
        clean_resp = response.strip()
        if clean_resp.startswith("```json"):
            clean_resp = clean_resp[7:]
        if clean_resp.endswith("```"):
            clean_resp = clean_resp[:-3]
        clean_resp = clean_resp.strip()
            
        # 2. Try regex extraction of list
        match = re.search(r"\[.*\]", clean_resp, re.DOTALL)
        if match:
            clean_resp = match.group(0)
            
        try:
            summaries = json.loads(clean_resp)
        except json.JSONDecodeError:
            # 3. Fallback: If not valid JSON, maybe it's just a list of lines?
            # Model might return:
            # 1. Summary one
            # 2. Summary two
            lines = [line.strip() for line in clean_resp.split('\n') if line.strip() and not line.strip().startswith('[')]
            if len(lines) == len(emails):
                print("[SUMMARIZER] JSON failed, but found matching line count. Using lines.")
                return [clean_email(line) for line in lines]
            else:
                 raise ValueError(f"Could not parse JSON. Raw: {clean_resp[:50]}...")

        # Validation
        if isinstance(summaries, list) and len(summaries) == len(emails):
            return [clean_email(str(s)) for s in summaries]
        else:
            print(f"[SUMMARIZER] Batch size mismatch. Expected {len(emails)}, got {len(summaries) if isinstance(summaries, list) else 0}")
            return [clean_email(e)[:100]+"..." for e in emails]
            
    except Exception as e:
        print(f"[SUMMARIZER] Batch error: {e}")
        # Return fallback instead of error string so user sees SOMETHING
        return [clean_email(e)[:200]+"..." for e in emails]




