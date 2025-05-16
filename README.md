# SQL Tokenizer

A simple lexical analyzer (tokenizer) for a subset of SQL queries, implemented as part of a Theory of Computation project.

## Features

- Tokenizes basic SQL queries using regular expressions (DFA-style)
- Supports the following token types:
  - Keywords: SELECT, FROM, WHERE
  - Identifiers (column and table names)
  - Commas
  - Equals operator
  - Single-quoted strings
  - Whitespace (skipped)
  - Illegal characters (raises SyntaxError)

## Usage

```python
from sql_tokenizer import tokenize

# Example query
query = "SELECT name, age FROM users WHERE status = 'active'"
tokens = tokenize(query)

# tokens will be a list of (token_type, value) tuples
```

## Running Tests

```bash
python -m unittest test_sql_tokenizer.py
```

## Implementation Details

The tokenizer uses regular expressions to match different token types in order of precedence. The implementation:

1. Defines patterns for each token type
2. Processes the input string character by character
3. Matches the longest possible token at each position
4. Skips whitespace
5. Raises SyntaxError for unrecognized characters

## Supported SQL Features

- Basic SELECT-FROM-WHERE queries
- Multiple columns (comma-separated)
- Simple WHERE conditions with equals operator
- Single-quoted string literals
- Alphanumeric identifiers (must start with a letter)
