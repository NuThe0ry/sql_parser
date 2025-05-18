import tkinter as tk
from tkinter import scrolledtext

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __repr__(self):
        return f"{self.type}({self.value})"

def tokenize(sql):
    tokens = []
    i = 0
    length = len(sql)
    keywords = {"SELECT", "FROM", "WHERE", "AND", "OR", "GROUP", "BY", "HAVING", "ORDER", "ASC", "DESC"}
    while i < length:
        ch = sql[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isalpha() or ch == '_':
            start = i
            while i < length and (sql[i].isalnum() or sql[i] == '_'):
                i += 1
            word = sql[start:i]
            up = word.upper()
            if up in keywords:
                tokens.append(Token(up, word))
            else:
                tokens.append(Token("IDENT", word))
            continue
        if ch.isdigit():
            start = i
            has_dot = False
            while i < length and (sql[i].isdigit() or (sql[i] == '.' and not has_dot)):
                if sql[i] == '.':
                    has_dot = True
                i += 1
            num = sql[start:i]
            tokens.append(Token("NUMBER", num))
            continue
        if ch == "'" or ch == '"':
            quote = ch
            i += 1
            start = i
            while i < length and sql[i] != quote:
                i += 1
            value = sql[start:i]
            tokens.append(Token("STRING", value))
            i += 1
            continue
        if ch == '>':
            if i+1 < length and sql[i+1] == '=':
                tokens.append(Token("GE", ">="))
                i += 2
            else:
                tokens.append(Token("GT", ">"))
                i += 1
            continue
        if ch == '<':
            if i+1 < length and sql[i+1] == '=':
                tokens.append(Token("LE", "<="))
                i += 2
            else:
                tokens.append(Token("LT", "<"))
                i += 1
            continue
        if ch == '=':
            tokens.append(Token("EQ", "="))
            i += 1
            continue
        if ch == '*':
            tokens.append(Token("ASTERISK", "*"))
            i += 1
            continue
        if ch == ',':
            tokens.append(Token("COMMA", ","))
            i += 1
            continue
        if ch == ';':
            tokens.append(Token("SEMICOLON", ";"))
            i += 1
            continue
        # ignore unknown chars
        i += 1
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token("EOF", None)
    def eat(self, type_):
        token = self.current()
        if token.type == type_:
            self.pos += 1
            return token
        else:
            raise SyntaxError(f"Expected token {type_} but got {token.type}")
    def parse(self):
        result = {}
        self.eat("SELECT")
        result['SELECT'] = self.parse_select_list()
        self.eat("FROM")
        result['FROM'] = self.parse_table_list()
        if self.current().type == "WHERE":
            self.eat("WHERE")
            result['WHERE'] = self.parse_condition()
        if self.current().type == "GROUP":
            self.eat("GROUP")
            self.eat("BY")
            result['GROUP BY'] = self.parse_identifier_list()
            if self.current().type == "HAVING":
                self.eat("HAVING")
                result['HAVING'] = self.parse_condition()
        if self.current().type == "ORDER":
            self.eat("ORDER")
            self.eat("BY")
            result['ORDER BY'] = self.parse_order_by_list()
        
        # Check for semicolon at the end
        if self.current().type != "SEMICOLON":
            raise SyntaxError("Expected semicolon (;) at the end of the query")
        self.eat("SEMICOLON")
        
        # Check if there are any remaining tokens
        if self.current().type != "EOF":
            raise SyntaxError(f"Unexpected token after semicolon: {self.current().type}")
            
        return result
    def parse_select_list(self):
        if self.current().type == "ASTERISK":
            self.eat("ASTERISK")
            return ["*"]
        else:
            return self.parse_identifier_list()
    def parse_table_list(self):
        return self.parse_identifier_list()
    def parse_identifier_list(self):
        id_list = []
        id_token = self.eat("IDENT")
        id_list.append(id_token.value)
        while self.current().type == "COMMA":
            self.eat("COMMA")
            id_token = self.eat("IDENT")
            id_list.append(id_token.value)
        return id_list
    def parse_order_by_list(self):
        order_list = []
        col = self.eat("IDENT").value
        direction = "ASC"
        if self.current().type in ("ASC", "DESC"):
            direction = self.eat(self.current().type).value.upper()
        order_list.append((col, direction))
        while self.current().type == "COMMA":
            self.eat("COMMA")
            col = self.eat("IDENT").value
            direction = "ASC"
            if self.current().type in ("ASC", "DESC"):
                direction = self.eat(self.current().type).value.upper()
            order_list.append((col, direction))
        return order_list
    def parse_condition(self):
        left = self.parse_conjunction()
        while self.current().type == "OR":
            self.eat("OR")
            right = self.parse_conjunction()
            left = ("OR", left, right)
        return left
    def parse_conjunction(self):
        left = self.parse_comparison()
        while self.current().type == "AND":
            self.eat("AND")
            right = self.parse_comparison()
            left = ("AND", left, right)
        return left
    def parse_comparison(self):
        if self.current().type == "IDENT":
            left_val = self.eat("IDENT").value
        else:
            raise SyntaxError(f"Expected identifier, got {self.current().type}")
        op_token = self.current()
        if op_token.type in ("EQ", "GT", "LT", "GE", "LE"):
            op = self.eat(op_token.type).value
        else:
            raise SyntaxError(f"Expected comparison operator, got {op_token.type}")
        right_token = self.current()
        if right_token.type == "IDENT":
            right_val = self.eat("IDENT").value
        elif right_token.type == "NUMBER":
            right_val = self.eat("NUMBER").value
        elif right_token.type == "STRING":
            str_val = self.eat("STRING").value
            right_val = f"'{str_val}'"
        else:
            raise SyntaxError(f"Expected identifier, number, or string, got {right_token.type}")
        return (op, left_val, right_val)

def format_condition(cond, indent=0):
    lines = []
    indent_str = "    " * indent
    if isinstance(cond, tuple):
        op = cond[0]
        if op in ("AND", "OR"):
            lines.append(indent_str + op)
            lines.extend(format_condition(cond[1], indent+1))
            lines.extend(format_condition(cond[2], indent+1))
        else:
            lines.append(indent_str + f"{cond[1]} {op} {cond[2]}")
    else:
        lines.append(indent_str + str(cond))
    return lines

def format_parse_tree(parse_tree):
    lines = []
    if 'SELECT' in parse_tree:
        lines.append("SELECT: " + ", ".join(parse_tree['SELECT']))
    if 'FROM' in parse_tree:
        lines.append("FROM: " + ", ".join(parse_tree['FROM']))
    if 'WHERE' in parse_tree:
        lines.append("WHERE:")
        lines.extend(format_condition(parse_tree['WHERE'], indent=1))
    if 'GROUP BY' in parse_tree:
        lines.append("GROUP BY: " + ", ".join(parse_tree['GROUP BY']))
    if 'HAVING' in parse_tree:
        lines.append("HAVING:")
        lines.extend(format_condition(parse_tree['HAVING'], indent=1))
    if 'ORDER BY' in parse_tree:
        lines.append("ORDER BY:")
        for col, dir_ in parse_tree['ORDER BY']:
            lines.append(f"    {col} {dir_}")
    return "\n".join(lines)

root = tk.Tk()
root.title("SQL Parser")

tk.Label(root, text="SQL Query:").pack(anchor='w')
query_text = scrolledtext.ScrolledText(root, height=6)
query_text.pack(fill='both', padx=5, pady=5)

tk.Label(root, text="Tokens:").pack(anchor='w')
tokens_text = scrolledtext.ScrolledText(root, height=10)
tokens_text.pack(fill='both', padx=5, pady=5)

tk.Label(root, text="Parse Tree:").pack(anchor='w')
tree_text = scrolledtext.ScrolledText(root, height=15)
tree_text.pack(fill='both', padx=5, pady=5)

def parse_sql():
    query = query_text.get("1.0", tk.END).strip()
    tokens_text.delete("1.0", tk.END)
    tree_text.delete("1.0", tk.END)
    if not query:
        return
    try:
        tokens = tokenize(query)
        token_lines = [f"{t.type}({t.value})" for t in tokens]
        tokens_text.insert(tk.END, "\n".join(token_lines))
        parser = Parser(tokens)
        parse_tree = parser.parse()
        tree_str = format_parse_tree(parse_tree)
        tree_text.insert(tk.END, tree_str)
    except Exception as e:
        tree_text.insert(tk.END, f"Error: {str(e)}")

btn = tk.Button(root, text="Parse SQL", command=parse_sql)
btn.pack(pady=5)
 

if __name__ == "__main__":
    root.mainloop()