import re

def clean_markdown(text: str):
    changed = False
    old = text
    
    # 1. Code blocks: extract content, don't delete it.
    # ```python\nIgnore\n``` -> Ignore
    text = re.sub(r'```[a-zA-Z]*\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    
    # 2. Inline code
    # `Ignore` -> Ignore
    text = re.sub(r'`([^`\n]+)`', r'\1', text)
    
    # 3. Links: keep text and URL separated by space
    # [Ignore](https://example.com) -> Ignore https://example.com
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 \2', text)
    
    # 4. Bold / Italic (only if wrapping words, to prevent matching math like 3 * 4 * 5)
    text = re.sub(r'\*\*\b(.*?)\b\*\*', r'\1', text)
    text = re.sub(r'\*\b(.*?)\b\*', r'\1', text)
    text = re.sub(r'__\b(.*?)\b__', r'\1', text)
    text = re.sub(r'_\b(.*?)\b_', r'\1', text)
    
    # 5. Headers
    text = re.sub(r'^#{1,6}\s+(.*)', r'\1', text, flags=re.MULTILINE)
    
    # 6. Blockquotes
    text = re.sub(r'^>\s+(.*)', r'\1', text, flags=re.MULTILINE)

    if text != old:
        changed = True
        
    return text, changed
