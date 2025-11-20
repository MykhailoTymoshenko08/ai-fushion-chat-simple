import re

def normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace and normalizing punctuation"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\s*\.\s*\.', '...', text)
    return text.strip()

def extract_key_phrases(text: str, max_phrases: int = 5) -> list:
    """Extract key phrases from text (simple implementation)"""
    sentences = re.split(r'[.!?]', text)
    phrases = []
    for sentence in sentences:
        words = sentence.strip().split()
        if len(words) >= 3 and len(words) <= 8:
            phrases.append(sentence.strip())
        if len(phrases) >= max_phrases:
            break
    return phrases