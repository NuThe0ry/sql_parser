from sql_tokenizer import tokenize, SELECT, FROM, WHERE, IDENTIFIER, COMMA, EQUALS, STRING, ASTERISK

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

        if self.pos != len(self.tokens):
            raise SyntaxError(f"Unexpected token at the end: {self._peek()}")

        return "Valid SQL query!"

    def _parse_columns(self):
        if self._match(ASTERISK):
            return
        self._expect(IDENTIFIER)
        while self._match(COMMA):
            self._expect(IDENTIFIER)

    def _parse_condition(self):
        self._expect(IDENTIFIER)
        self._expect(EQUALS)
        self._expect(STRING)

    def _expect(self, token_type):
        if self._peek_type() == token_type:
            self.pos += 1
        else:
            raise SyntaxError(f"Expected {token_type}, got {self._peek_type()} at token {self._peek()}")

    def _match(self, token_type):
        if self._peek_type() == token_type:
            self.pos += 1
            return True
        return False

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _peek_type(self):
        return self._peek()[0] if self._peek() else None

# Example usage
if __name__ == "__main__":
    query = "SELECT name, age FROM users WHERE status = 'active'"
    tokens = tokenize(query)
    parser = SQLParser(tokens)
    try:
        result = parser.parse()
        print(result)
    except SyntaxError as e:
        print("Syntax Error:", e)
