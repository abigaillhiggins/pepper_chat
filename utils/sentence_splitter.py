import re

def split_into_sentences(text):
    """Split text into sentences using regex pattern matching."""
    # Simple sentence splitter using regex
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    return [s.strip() for s in sentence_endings.split(text) if s.strip()] 