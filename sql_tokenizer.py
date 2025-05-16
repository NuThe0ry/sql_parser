import re
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

# Regular expression patterns for each token type
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
        elif pattern == '[a-zA-Z][a-zA-Z0-9_]*':
            def match_identifier(s: str, pos: int) -> Optional[int]:
                if pos >= len(s) or not s[pos].isalpha():
                    return None
                end = pos + 1
                while end < len(s) and (s[end].isalnum() or s[end] == '_'):
                    end += 1
                return end
            return match_identifier
        elif pattern == ',':
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == ',' else None
        elif pattern == '=':
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == '=' else None
        elif pattern == "'[^']*'":
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
        elif pattern == '\\*':
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == '*' else None
        elif pattern == '[ \t\n]+':
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
    pos = 0
    tokens = []
    while pos < len(input_str):
        match_found = False
        for token_type, pattern in TOKEN_PATTERNS:
            end_pos = pattern.match(input_str, pos)
            if end_pos is not None:
                if token_type != SKIP:
                    tokens.append((token_type, input_str[pos:end_pos]))
                pos = end_pos
                match_found = True
                break
        if not match_found:
            raise SyntaxError(f"Unexpected character: '{input_str[pos]}' at position {pos}")
    return tokens
