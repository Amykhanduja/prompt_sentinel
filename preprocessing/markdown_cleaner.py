import re
from bs4 import BeautifulSoup

def clean_markdown(text: str):
    changed = False
    
    soup = BeautifulSoup(text, 'html.parser')
    clean = soup.get_text()
    if clean != text:
        changed = True
    
    old = clean
    clean = re.sub(r'\*\*(.*?)\*\*', r'\1', clean)
    clean = re.sub(r'\*(.*?)\*', r'\1', clean)
    clean = re.sub(r'__(.*?)__', r'\1', clean)
    clean = re.sub(r'_(.*?)_', r'\1', clean)
    clean = re.sub(r'`(.*?)`', r'\1', clean)
    clean = re.sub(r'^>\s*(.*)', r'\1', clean, flags=re.MULTILINE)
    clean = re.sub(r'^#{1,6}\s*(.*)', r'\1', clean, flags=re.MULTILINE)
    
    if clean != old:
        changed = True
        
    return clean, changed
