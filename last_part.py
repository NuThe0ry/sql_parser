import re

# Token types
SELECT = 'SELECT'
FROM = 'FROM'
WHERE = 'WHERE'
AND = 'AND'
OR = 'OR'
GROUP = 'GROUP'
BY = 'BY'
ORDER = 'ORDER'
HAVING = 'HAVING'
COMMA = 'COMMA'
SEMICOLON = 'SEMICOLON'
OPERATOR = 'OPERATOR'
NUMBER = 'NUMBER'
STRING = 'STRING'
IDENTIFIER = 'IDENTIFIER'
EOF = 'EOF'

# Token pattern
class Pattern:
    def __init__(self, regex):
        self.regex = re.compile(r'\b' + regex + r'\b', re.IGNORECASE)

# Token patterns
TOKEN_PATTERNS = [
    (SELECT, Pattern('SELECT')),
    (FROM, Pattern('FROM')),
    (WHERE, Pattern('WHERE')),
    (AND, Pattern('AND')),
    (OR, Pattern('OR')),
    (GROUP, Pattern('GROUP')),
    (BY, Pattern('BY')),
    (ORDER, Pattern('ORDER')),
    (HAVING, Pattern('HAVING')),
    (COMMA, re.compile(r',')),
    (SEMICOLON, re.compile(r';')),
    (OPERATOR, re.compile(r'=|<>|<|>|<=|>=')),
    (NUMBER, re.compile(r'\d+')),
    (STRING, re.compile(r'\'[^\']*\'|"[^"]*"')),
    (IDENTIFIER, re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')),
]

# Token class
class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'

# Tokenizer
def tokenize(sql):
    tokens = []
    pos = 0
    while pos < len(sql):
        match = None
        for token_type, pattern in TOKEN_PATTERNS:
            if isinstance(pattern, Pattern):
                regex = pattern.regex
            else:
                regex = pattern
            match = regex.match(sql, pos)
            if match:
                value = match.group(0)
                tokens.append(Token(token_type, value))
                pos = match.end()
                break
        if not match:
            if sql[pos].isspace():
                pos += 1
            else:
                raise SyntaxError(f'Unexpected character: {sql[pos]}')
    tokens.append(Token(EOF, None))
    return tokens

# Parser class
class SQLParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        self._expect(SELECT)
        self._parse_columns()
        self._expect(FROM)
        self._expect(IDENTIFIER)

        if self._match(WHERE):
            self._parse_condition()

        if self._match(GROUP):
            self._expect(BY)
            self._parse_column_list()

        if self._match(HAVING):
            self._parse_condition()

        if self._match(ORDER):
            self._expect(BY)
            self._parse_column_list()

        self._expect(SEMICOLON)

        if self.pos != len(self.tokens):
            raise SyntaxError(f"Unexpected token at the end: {self._peek()}")

        return "Valid SQL query!"

    def _peek(self):
        return self.tokens[self.pos]

    def _expect(self, token_type):
        if self._peek().type == token_type:
            self.pos += 1
        else:
            raise SyntaxError(f"Expected {token_type}, found {self._peek()}")

    def _match(self, token_type):
        if self._peek().type == token_type:
            self.pos += 1
            return True
        return False

    def _parse_columns(self):
        self._expect(IDENTIFIER)
        while self._match(COMMA):
            self._expect(IDENTIFIER)

    def _parse_column_list(self):
        self._expect(IDENTIFIER)
        while self._match(COMMA):
            self._expect(IDENTIFIER)

    def _parse_condition(self):
        self._parse_expression()
        while self._peek().type in (AND, OR):
            self.pos += 1
            self._parse_expression()

    def _parse_expression(self):
        self._expect(IDENTIFIER)
        self._expect(OPERATOR)
        if self._peek().type in (NUMBER, STRING, IDENTIFIER):
            self.pos += 1
        else:
            raise SyntaxError(f"Expected value, found {self._peek()}")
