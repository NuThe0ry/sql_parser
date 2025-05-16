import re
from typing import List, Tuple

# Token types
SELECT = 'SELECT'
FROM = 'FROM'
WHERE = 'WHERE'
IDENTIFIER = 'IDENTIFIER'
COMMA = 'COMMA'
EQUALS = 'EQUALS'
STRING = 'STRING'
SKIP = 'SKIP'
MISMATCH = 'MISMATCH'

# Regular expression patterns for each token type
TOKEN_PATTERNS = [
    (SELECT, r'SELECT'),
    (FROM, r'FROM'),
    (WHERE, r'WHERE'),
    (IDENTIFIER, r'[a-zA-Z][a-zA-Z0-9_]*'),  # Must start with letter
    (COMMA, r','),
    (EQUALS, r'='),
    (STRING, r"'[^']*'"),  # Single-quoted strings
    (SKIP, r'[ \t\n]+'),  # Whitespace and newlines
    (MISMATCH, r'.'),  # Any other character
]

def tokenize(input_str: str) -> List[Tuple[str, str]]:
    """
    Tokenize the input SQL string into a list of (token_type, value) tuples.
    
    Args:
        input_str: The SQL query string to tokenize
        
    Returns:
        List of (token_type, value) tuples
        
    Raises:
        SyntaxError: If an unrecognized character is found
    """
    tokens = []
    pos = 0
    
    while pos < len(input_str):
        match = None
        for token_type, pattern in TOKEN_PATTERNS:
            regex = re.compile(pattern)
            match = regex.match(input_str, pos)
            if match:
                value = match.group(0)
                if token_type != SKIP:  # Skip whitespace tokens
                    tokens.append((token_type, value))
                pos = match.end()
                break
        
        if not match:
            raise SyntaxError(f"Unrecognized character at position {pos}: {input_str[pos]}")
            
    return tokens 