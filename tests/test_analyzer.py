"""
tests/test_analyzer.py
=====================
Unit test suite verifying AST complexity, line counts, and Maintainability Index.
"""

import unittest
from code_analyzer import analyze_code, calculate_raw_metrics


class TestCodeAnalyzer(unittest.TestCase):
    """Unit tests for AST complexity and Radon static code analyzer."""

    def test_raw_metrics(self):
        """Verify line count calculation."""
        code = "def foo():\n    # This is a comment\n    return 42\n"
        metrics = calculate_raw_metrics(code)
        self.assertEqual(metrics["loc"], 3)
        self.assertEqual(metrics["comments"], 1)
        self.assertEqual(metrics["sloc"], 2)

    def test_clean_python_code(self):
        """Verify analysis of simple clean code."""
        code = "def add(a: int, b: int) -> int:\n    return a + b\n"
        result = analyze_code(code, language="python")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["cyclomatic_complexity"], 1)
        self.assertGreaterEqual(result["maintainability_index"], 80)
        self.assertIn("A", result["grade"])

    def test_nested_complexity(self):
        """Verify high complexity is flagged."""
        code = (
            "def complex_logic(x):\n"
            "    if x > 0:\n"
            "        for i in range(x):\n"
            "            if i % 2 == 0:\n"
            "                while i > 0:\n"
            "                    i -= 1\n"
            "    return x\n"
        )
        result = analyze_code(code, language="python")
        self.assertGreater(result["cyclomatic_complexity"], 3)

    def test_syntax_error_handling(self):
        """Verify invalid Python syntax is reported gracefully."""
        bad_code = "def broken(:\n    pass"
        result = analyze_code(bad_code, language="python")
        self.assertEqual(result["status"], "syntax_error")
        self.assertIn("SyntaxError", result["error"])


if __name__ == "__main__":
    unittest.main()
