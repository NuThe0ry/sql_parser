from typing import List, Tuple, Optional, Callable
import tkinter as tk

# Token types
SELECT = 'SELECT'
FROM = 'FROM'
WHERE = 'WHERE'
IDENTIFIER = 'IDENTIFIER'
COMMA = 'COMMA'
EQUALS = 'EQUALS'
GREATER = 'GREATER'
LESS = 'LESS'
GTE = 'GTE'
LTE = 'LTE'
STRING = 'STRING'
NUMBER = 'NUMBER'   
SKIP = 'SKIP'
ASTERISK = 'ASTERISK'
SEMICOLON = 'SEMICOLON'
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
        elif pattern == '[a-zA-Z][a-zA-Z0-9_]*':
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
        elif pattern == ',':
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == ',' else None
        elif pattern == '=':
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == '=' else None
        elif pattern == '>=':
            return lambda s, pos: pos + 2 if s[pos:pos+2] == '>=' else None
        elif pattern == '<=':
            return lambda s, pos: pos + 2 if s[pos:pos+2] == '<=' else None
        elif pattern == '>':
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == '>' else None
        elif pattern == '<':
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == '<' else None
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
        elif pattern == ';':
            return lambda s, pos: pos + 1 if pos < len(s) and s[pos] == ';' else None
        elif pattern == '[ \t\n]+':
            def match_whitespace(s: str, pos: int) -> Optional[int]:
                if pos >= len(s) or s[pos] not in ' \t\n':
                    return None
                end = pos + 1
                while end < len(s) and s[end] in ' \t\n':
                    end += 1
                return end
            return match_whitespace
        elif pattern == 'NUMBER':
            def match_number(s: str, pos: int) -> Optional[int]:
                if pos >= len(s) or not s[pos].isdigit():
                    return None
                end = pos + 1
                while end < len(s) and s[end].isdigit():
                    end += 1
                return end
            return match_number
        else:
            raise ValueError(f"Unsupported pattern: {pattern}")

    def match(self, input_str: str, pos: int) -> Optional[int]:
        return self.matcher(input_str, pos)

# Token patterns
TOKEN_PATTERNS = [
    (SELECT, Pattern('SELECT')),
    (FROM, Pattern('FROM')),
    (WHERE, Pattern('WHERE')),
    (GTE, Pattern('>=')),
    (LTE, Pattern('<=')),
    (GREATER, Pattern('>')),
    (LESS, Pattern('<')),
    (EQUALS, Pattern('=')),
    (COMMA, Pattern(',')),
    (SEMICOLON, Pattern(';')),
    (STRING, Pattern("'[^']*'")),
    (ASTERISK, Pattern('\\*')),
    (NUMBER, Pattern('NUMBER')),        
    (IDENTIFIER, Pattern('[a-zA-Z][a-zA-Z0-9_]*')),
    (SKIP, Pattern('[ \t\n]+')),
]

def tokenize(input_str: str) -> List[Tuple[str, str]]:
    tokens = []
    pos = 0

    while pos < len(input_str):
        match = None
        for token_type, pattern in TOKEN_PATTERNS:
            end_pos = pattern.match(input_str, pos)
            if end_pos is not None:
                if token_type != SKIP:
                    tokens.append((token_type, input_str[pos:end_pos]))
                pos = end_pos
                match = True
                break

        if not match:
            raise SyntaxError(f"Unrecognized character at position {pos}: {input_str[pos]}")

    return tokens


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
        self._expect(SEMICOLON)
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
        # Accept =, >, <, >=, <= operators
        if self._match(EQUALS) or self._match(GREATER) or self._match(LESS) or self._match(GTE) or self._match(LTE):
            # Accept STRING or NUMBER as right operand
            if not (self._match(STRING) or self._match(NUMBER)):
                raise SyntaxError("Expected STRING or NUMBER after comparison operator")
        else:
            raise SyntaxError("Expected comparison operator in WHERE clause")

    def _expect(self, token_type):
        actual_type = self._peek_type()
        if actual_type == token_type:
            self.pos += 1
        else:
            raise SyntaxError(f"Expected {token_type}, got {actual_type} at token {token_type}")

    def _match(self, token_type):
        if self._peek_type() == token_type:
            self.pos += 1
            return True
        return False

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _peek_type(self):
        return self._peek()[0] if self._peek() else None

# GUI Functions
def generate_sql_gui():
    query = entry.get()
    try:
        tokens = tokenize(query)
        parser = SQLParser(tokens)
        result = parser.parse()

        output = "Tokens:\n"
        for i, (typ, val) in enumerate(tokens, 1):
            output += f"Token {i}: Type={typ}, Value={val}\n"

        output += "\nParse Tree:\n"

        # Extract identifiers for columns and table
        identifiers = [val for t, val in tokens if t == IDENTIFIER]
        columns = []
        table = None
        where_condition = None

        # Columns: After SELECT and before FROM
        # We'll just grab identifiers that appear before FROM
        from_index = next((i for i, (t, _) in enumerate(tokens) if t == FROM), None)
        if from_index is not None:
            columns = [val for t, val in tokens[1:from_index] if t == IDENTIFIER]

        # Table: identifier after FROM
        if from_index is not None and from_index + 1 < len(tokens):
            if tokens[from_index + 1][0] == IDENTIFIER:
                table = tokens[from_index + 1][1]

        # Where condition
        where_indices = [i for i, (t, _) in enumerate(tokens) if t == WHERE]
        if where_indices:
            where_idx = where_indices[0]
            # Expect condition to be: IDENTIFIER operator (STRING or NUMBER)
            if where_idx + 3 < len(tokens):
                where_condition = {
                    'left': tokens[where_idx + 1][1],
                    'op': tokens[where_idx + 2][1],
                    'right': tokens[where_idx + 3][1]
                }

        parse_tree = {
            'type': 'QUERY',
            'columns': columns,
            'table': table,
            'where': where_condition
        }

        output += str(parse_tree)

        output_text.set(output)

    except SyntaxError as e:
        output_text.set(f"Syntax Error: {str(e)}")

def clear_gui():
    entry.delete(0, tk.END)
    output_text.set("")

def exit_app():
    root.destroy()

# GUI Setup
root = tk.Tk()
root.title("SQL Parser GUI")

tk.Label(root, text="Enter SQL Query:").pack()
entry = tk.Entry(root, width=60)
entry.pack()

tk.Button(root, text="Parse SQL", command=generate_sql_gui).pack()
output_text = tk.StringVar()
output_label = tk.Label(root, textvariable=output_text, justify="left")
output_label.pack()

tk.Button(root, text="Clear", command=clear_gui).pack()
tk.Button(root, text="Exit", command=exit_app).pack()

root.mainloop()
