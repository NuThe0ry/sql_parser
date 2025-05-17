from sql_tokenizer import tokenize

query = "SELECT * FROM users"

tokens = tokenize(query)

print("Tokens:")
for token_type, token_value in tokens:
    print(f"{token_type}: '{token_value}'")
