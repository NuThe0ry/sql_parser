import unittest
from sql_tokenizer import tokenize, SELECT, FROM, WHERE, IDENTIFIER, COMMA, EQUALS, STRING, ASTERISK

class TestSQLTokenizer(unittest.TestCase):
    def test_basic_select_from_where(self):
        """Test a basic SELECT-FROM-WHERE query"""
        query = "SELECT name FROM users WHERE age = '25'"
        expected = [
            (SELECT, 'SELECT'),
            (IDENTIFIER, 'name'),
            (FROM, 'FROM'),
            (IDENTIFIER, 'users'),
            (WHERE, 'WHERE'),
            (IDENTIFIER, 'age'),
            (EQUALS, '='),
            (STRING, "'25'")
        ]
        self.assertEqual(tokenize(query), expected)

    def test_multiple_columns(self):
        """Test a query with multiple columns"""
        query = "SELECT id, name, email FROM users"
        expected = [
            (SELECT, 'SELECT'),
            (IDENTIFIER, 'id'),
            (COMMA, ','),
            (IDENTIFIER, 'name'),
            (COMMA, ','),
            (IDENTIFIER, 'email'),
            (FROM, 'FROM'),
            (IDENTIFIER, 'users')
        ]
        self.assertEqual(tokenize(query), expected)

    def test_select_all_columns(self):
        """Test a query using SELECT *"""
        query = "SELECT * FROM users"
        expected = [
            (SELECT, 'SELECT'),
            (ASTERISK, '*'),
            (FROM, 'FROM'),
            (IDENTIFIER, 'users')
        ]
        self.assertEqual(tokenize(query), expected)

    def test_illegal_character(self):
        """Test that an illegal character raises a SyntaxError"""
        query = "SELECT @ FROM users"
        with self.assertRaises(SyntaxError):
            tokenize(query)

if __name__ == '__main__':
    unittest.main() 