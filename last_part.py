
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


KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'GROUP', 'BY', 'ORDER', 'HAVING'
}

OPERATORS = {'=', '<>', '<', '>', '<=', '>='}

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'

def is_letter(ch):
    return ch.isalpha() or ch == '_'

def is_digit(ch):
    return ch.isdigit()

def tokenize(sql):
    tokens = []
    pos = 0
    length = len(sql)

    while pos < length:
        ch = sql[pos]

        if ch.isspace():
            pos += 1
            continue

       
        if ch == ',':
            tokens.append(Token(COMMA, ','))
            pos += 1
            continue

      
        if ch == ';':
            tokens.append(Token(SEMICOLON, ';'))
            pos += 1
            continue

        
        if ch == "'" or ch == '"':
            quote_char = ch
            pos += 1
            start = pos
            while pos < length and sql[pos] != quote_char:
                pos += 1
            if pos == length:
                raise SyntaxError("Unterminated string literal")
            string_val = sql[start:pos]
            tokens.append(Token(STRING, string_val))
            pos += 1  
            continue

        
        if pos + 1 < length:
            two_char = sql[pos:pos+2]
            if two_char in OPERATORS:
                tokens.append(Token(OPERATOR, two_char))
                pos += 2
                continue
      
        if ch in {'=', '<', '>'}:
            tokens.append(Token(OPERATOR, ch))
            pos += 1
            continue

        
        if is_digit(ch):
            start = pos
            while pos < length and is_digit(sql[pos]):
                pos += 1
            number_val = sql[start:pos]
            tokens.append(Token(NUMBER, number_val))
            continue

   
        if is_letter(ch):
            start = pos
            while pos < length and (is_letter(sql[pos]) or is_digit(sql[pos])):
                pos += 1
            word = sql[start:pos].upper()
            if word in KEYWORDS:
                tokens.append(Token(word, word))
            else:
                tokens.append(Token(IDENTIFIER, word))
            continue

        raise SyntaxError(f'Unexpected character: {ch}')

    tokens.append(Token(EOF, None))
    return tokens
