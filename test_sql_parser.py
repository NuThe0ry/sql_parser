from parser import SQLParser
from sql_tokenizer import tokenize


query = "SELECT * FROM users WHERE status = 'active'"


tokens = tokenize(query)


parser = SQLParser(tokens)

try:
    result = parser.parse()
    print("✅ Success:", result)
except SyntaxError as e:
    print("❌ Syntax Error:", e)
