
from typing import List, Tuple, Optional, Callable

# Token types
SELECT = 'SELECT'
FROM = 'FROM'
WHERE = 'WHERE'
IDENTIFIER = 'IDENTIFIER'
COMMA = 'COMMA'
EQUALS = 'EQUALS'
STRING = 'STRING'
SKIP = 'SKIP'
ASTERISK = 'ASTERISK'
MISMATCH = 'MISMATCH'

class Pattern:
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.matcher = self._compile_pattern(pattern)
    
    def _compile_pattern(self, pattern: str) -> Callable[[str, int], Optional[int]]:
        if pattern == 'SELECT':
            return lambda s, pos: pos + 6 if s[pos:pos+6].upper() == 'SELECT' else None
        elif pattern == 'FROM':
            return lambda s, pos: pos + 4 if s[pos:pos+4].upper() == 'FROM' else None
        elif pattern == 'WHERE':
            return lambda s, pos: pos + 5 if s[pos:pos+5].upper() == 'WHERE' else None
        elif pattern == '[a-zA-Z][a-zA-Z0-9_]*':  # Identifier pattern
            def match_identifier(s: str, pos: int) -> Optional[int]:
                if pos >= len(s) or not ('a' <= s[pos].lower() <= 'z'):
                    return None
                end = pos + 1
                while end < len(s) and (
                    'a' <= s[end].lower() <= 'z' or 
                    '0' <= s[end] <= '9' or 
                    s[end] == '_'
                ):
                    end += 1
                return end
            return match_identifier
        elif pattern == ',':  # Comma
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == ',' else None
        elif pattern == '=':  # Equals
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == '=' else None
        elif pattern == "'[^']*'":  # String pattern
            def match_string(s: str, pos: int) -> Optional[int]:
                if pos >= len(s) or s[pos] != "'":
                    return None
                end = pos + 1
                while end < len(s):
                    if s[end] == "'":
                        return end + 1
                    end += 1
                return None
            return match_string
        elif pattern == '\\*':  # Asterisk
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == '*' else None
        elif pattern == '[ \t\n]+':  # Whitespace
            def match_whitespace(s: str, pos: int) -> Optional[int]:
                if pos >= len(s) or s[pos] not in ' \t\n':
                    return None
                end = pos + 1
                while end < len(s) and s[end] in ' \t\n':
                    end += 1
                return end
            return match_whitespace
        else:
            raise ValueError(f"Unsupported pattern: {pattern}")

    def match(self, input_str: str, pos: int) -> Optional[int]:
        """Returns the end position if match found, None otherwise"""
        return self.matcher(input_str, pos)

# Token patterns
TOKEN_PATTERNS = [
    (SELECT, Pattern('SELECT')),
    (FROM, Pattern('FROM')),
    (WHERE, Pattern('WHERE')),
    (IDENTIFIER, Pattern('[a-zA-Z][a-zA-Z0-9_]*')),
    (COMMA, Pattern(',')),
    (EQUALS, Pattern('=')),
    (STRING, Pattern("'[^']*'")),
    (ASTERISK, Pattern('\\*')),
    (SKIP, Pattern('[ \t\n]+')),
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
            end_pos = pattern.match(input_str, pos)
            if end_pos is not None:
                if token_type != SKIP:  # Skip whitespace tokens
                    tokens.append((token_type, input_str[pos:end_pos]))
                pos = end_pos
                match = True
                break
        
        if not match:
            raise SyntaxError(f"Unrecognized character at position {pos}: {input_str[pos]}")
            
    return tokens 
