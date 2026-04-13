import unittest
from unittest.mock import patch
import io
import sys

class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b

    def multiply(self, a: int, b: int) -> int:
        return a * b

    def divide(self, a: int, b: int) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero!")
        return a / b

class TestCalculator(unittest.TestCase):
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_add(self, mock_stdout):
        calculator = Calculator()
        result = calculator.add(2, 3)
        self.assertEqual(result, 5)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_subtract(self, mock_stdout):
        calculator = Calculator()
        result = calculator.subtract(5, 2)
        self.assertEqual(result, 3)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_multiply(self, mock_stdout):
        calculator = Calculator()
        result = calculator.multiply(4, 5)
        self.assertEqual(result, 20)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_divide(self, mock_stdout):
        calculator = Calculator()
        result = calculator.divide(6, 2)
        self.assertAlmostEqual(result, 3.0)

if __name__ == '__main__':
    unittest.main()