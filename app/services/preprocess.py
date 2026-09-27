import re
import html

def clean_email(text: str) -> str:
    """
    NUCLEAR STAGE cleaning: Strips everything that even looks like a tag.
    """
    if not text:
        return ""

    # 1. Handle potential bytes
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')

    # 2. IMPORTANT: Unescape FIRST so we catch &lt;doctype&gt; etc.
    text = html.unescape(text)
    text = text.replace("&nbsp;", " ").replace("\xa0", " ")

    # 3. Remove comments and CDATA
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<!\[CDATA\[.*?\]\]>", " ", text, flags=re.S)

    # 4. Remove script, style, and head blocks entirely
    text = re.sub(r"<(script|style|head|title).*?>.*?</\1>", " ", text, flags=re.S | re.I)
    
    # 5. Strip all XML/HTML tags (including !doctype, html, body)
    text = re.sub(r"<!doctype.*?>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]*>", " ", text, flags=re.S)
    
    # 6. Remove common email artifacts
    text = re.sub(r"--\s*\n.*", "", text, flags=re.S) # Signatures
    text = re.sub(r"On .*? wrote:.*", "", text, flags=re.S | re.I) # Reply threads
    
    # 7. Remove leftover conditional fragments like [if !mso]
    text = re.sub(r"\[if\s+.*?\]", " ", text, flags=re.S | re.I)
    text = re.sub(r"\[endif\]", " ", text, flags=re.S | re.I)
    
    # 8. Collapse all whitespace and normalize
    text = re.sub(r"\s+", " ", text).strip()
    
    # 9. Handle Empty/Image-only bodies
    if not text or len(text) < 10:
        return "(Note: This email consists of images or non-textual content.)"
        
    return text
