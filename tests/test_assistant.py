"""
tests/test_assistant.py
======================
Unit test suite verifying the functionality of AICodingAssistant.
Tests both live (if configured) and deterministic offline fallback routines.
"""

import unittest
from assistant import AICodingAssistant


class TestAICodingAssistant(unittest.TestCase):
    """Test suite for AICodingAssistant methods."""

    def setUp(self):
        # Force offline mode to ensure deterministic, reproducible test runs
        self.assistant = AICodingAssistant(force_offline=True)

    def test_initialization_offline(self):
        """Verify assistant initializes in offline mode cleanly."""
        self.assertFalse(self.assistant.is_live)
        self.assertEqual(self.assistant.temperature, 0.2)

    def test_code_generation_prime(self):
        """Test prime number code generation fallback."""
        resp = self.assistant.generate_code("Write a prime number function", language="python")
        self.assertIn("def is_prime", resp)
        self.assertIn("return", resp)

    def test_code_explanation(self):
        """Test loop code explanation."""
        code = "for i in range(5):\n    print(i)"
        resp = self.assistant.explain_code(code, language="python")
        self.assertIn("range(5)", resp)
        self.assertIn("Complexity", resp)

    def test_bug_detection(self):
        """Test detection of IndexError."""
        code = "numbers = [1, 2, 3]\nprint(numbers[5])"
        resp = self.assistant.detect_bugs(code, language="python")
        self.assertIn("IndexError", resp)
        self.assertIn("numbers", resp)

    def test_code_conversion_sql(self):
        """Test SQL to Pandas conversion."""
        sql = "SELECT department, COUNT(*) FROM employees GROUP BY department;"
        resp = self.assistant.convert_code(sql, source_lang="sql", target_lang="pandas")
        self.assertIn("pd", resp)
        self.assertIn("groupby", resp)

    def test_documentation_generation(self):
        """Test docstring creation."""
        code = "def add(a, b): return a + b"
        resp = self.assistant.generate_documentation(code, style="Google")
        self.assertIn("Args:", resp)
        self.assertIn("Returns:", resp)

    def test_unit_test_generation(self):
        """Test unit test generation."""
        code = "def is_prime(n): pass"
        resp = self.assistant.generate_unit_tests(code, framework="pytest")
        self.assertIn("pytest", resp)
        self.assertIn("def test_", resp)

    def test_refactoring(self):
        """Test code refactoring suggestion."""
        code = "def foo(items):\n    return items"
        resp = self.assistant.refactor_code(code, objective="Readability")
        self.assertIn("Refactoring", resp)

    def test_chat_interaction(self):
        """Test conversational chat completion."""
        messages = [
            {"role": "user", "content": "How do I optimize a search query?"}
        ]
        resp = self.assistant.chat_completion(messages)
        self.assertTrue(len(resp) > 20)


if __name__ == "__main__":
    unittest.main()
