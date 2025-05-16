from parser import SQLParser
from sql_tokenizer import tokenize

# List of test cases: (query, expected result)
test_cases = [
    # ✅ Valid cases
    ("SELECT name FROM users", True),
    ("SELECT name, age FROM employees", True),
    ("SELECT * FROM customers", True),
    ("SELECT id, name FROM clients WHERE status = 'active'", True),
    ("SELECT * FROM orders WHERE date = '2023-12-01'", True),

    # ❌ Invalid cases
    ("SELECT FROM users", False),                      # Missing column
    ("SELECT name users", False),                      # Missing FROM
    ("SELECT name, FROM employees", False),            # Comma without identifier
    ("SELECT name FROM WHERE status = 'active'", False), # Missing table name
    ("SELECT name FROM users WHERE status 'active'", False), # Missing =
]

# Run test cases
for i, (query, expected_valid) in enumerate(test_cases, start=1):
    try:
        tokens = tokenize(query)
        parser = SQLParser(tokens)
        parser.parse()
        result = True
    except Exception as e:
        result = False
        print(f"Test {i} failed: {query}")
        print("Error:", e)

    print(f"Test {i}: {'Passed ✅' if result == expected_valid else 'Failed ❌'}")
