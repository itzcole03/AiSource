#!/usr/bin/env python3
"""
Debug the regex patterns for filename and content extraction
"""
import re

def test_regex_patterns():
    instruction = "write a story in a file called story.txt and make the story about pikachu vs kakashi from naruto"
    print(f"Testing instruction: {instruction}")
    
    print("\n=== Filename Patterns ===")
    filename_patterns = [
        r"file\s+(?:called|named)\s+([^\s]+\.txt)",
        r"([a-zA-Z_][a-zA-Z0-9_]*\.txt)",
        r"(?:in|create)\s+([a-zA-Z_][a-zA-Z0-9_]*\.txt)"
    ]
    
    for i, pattern in enumerate(filename_patterns):
        match = re.search(pattern, instruction, re.IGNORECASE)
        if match:
            print(f"  Pattern {i+1}: MATCH - '{match.group(1)}'")
        else:
            print(f"  Pattern {i+1}: NO MATCH")
    
    print("\n=== Content Patterns ===")
    content_patterns = [
        r"with the (?:word|content|text)s?\s+['\"]?([^'\"]+)['\"]?",
        r"containing\s+['\"]?([^'\"]+)['\"]?",
        r"(?:about|with)\s+(.+?)(?:\s+(?:in|and|$))",
        r"story about\s+(.+?)(?:\s+(?:from|in|and|$))",
        r"make.*?about\s+(.+?)(?:\s+(?:from|in|and|$))"
    ]
    
    for i, pattern in enumerate(content_patterns):
        match = re.search(pattern, instruction, re.IGNORECASE)
        if match:
            extracted_content = match.group(1).strip()
            print(f"  Pattern {i+1}: MATCH - '{extracted_content}'")
        else:
            print(f"  Pattern {i+1}: NO MATCH")
    
    print("\n=== Story Detection ===")
    if "story" in instruction.lower():
        print("  Story detected: YES")
        if "pikachu" in instruction.lower() and "kakashi" in instruction.lower():
            print("  Pikachu vs Kakashi detected: YES")
        else:
            print("  Pikachu vs Kakashi detected: NO")
    else:
        print("  Story detected: NO")

if __name__ == "__main__":
    test_regex_patterns()
