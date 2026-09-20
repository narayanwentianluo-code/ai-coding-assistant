"""
code_analyzer.py
================
Static Code & Complexity Analysis Engine.
Computes real-time Cyclomatic Complexity, Maintainability Index (MI),
AST structures, and code health ratings using Python's `ast` and `radon`.
"""

import ast
import math
from typing import Any, Dict, List, Optional


def calculate_raw_metrics(code: str) -> Dict[str, int]:
    """Calculate raw line metrics (LOC, SLOC, Comments, Blank lines)."""
    lines = code.splitlines()
    loc = len(lines)
    blank = 0
    comments = 0
    sloc = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank += 1
        elif stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
            comments += 1
        else:
            sloc += 1

    return {
        "loc": loc,
        "sloc": sloc,
        "comments": comments,
        "blank": blank,
    }


class ASTComplexityVisitor(ast.NodeVisitor):
    """Calculates Cyclomatic Complexity using AST traversal."""

    def __init__(self):
        self.complexity = 1  # Base complexity for a routine
        self.functions: List[Dict[str, Any]] = []
        self.classes: List[str] = []
        self.current_function = None
        self.func_complexity = 1
        self.try_blocks = 0
        self.loops = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        prev_func = self.current_function
        prev_comp = self.func_complexity
        self.current_function = node.name
        self.func_complexity = 1

        self.generic_visit(node)

        self.functions.append({
            "name": node.name,
            "lineno": node.lineno,
            "complexity": self.func_complexity,
            "args_count": len(node.args.args),
            "is_async": False,
        })
        self.current_function = prev_func
        self.func_complexity = prev_comp

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        prev_func = self.current_function
        prev_comp = self.func_complexity
        self.current_function = node.name
        self.func_complexity = 1

        self.generic_visit(node)

        self.functions.append({
            "name": node.name,
            "lineno": node.lineno,
            "complexity": self.func_complexity,
            "args_count": len(node.args.args),
            "is_async": True,
        })
        self.current_function = prev_func
        self.func_complexity = prev_comp

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes.append(node.name)
        self.generic_visit(node)

    def visit_If(self, node: ast.If):
        self.complexity += 1
        self.func_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.complexity += 1
        self.func_complexity += 1
        self.loops += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self.complexity += 1
        self.func_complexity += 1
        self.loops += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self.complexity += 1
        self.func_complexity += 1
        self.loops += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        self.try_blocks += 1
        # Each except handler adds a conditional branch
        self.complexity += len(node.handlers)
        self.func_complexity += len(node.handlers)
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        # And/Or operators introduce additional decision points
        self.complexity += len(node.values) - 1
        self.func_complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.generic_visit(node)


def calculate_maintainability_index(sloc: int, cyclomatic_complexity: int, halstead_volume: float = 100.0) -> float:
    """
    Computes Maintainability Index (MI) based on SEI standard formula:
    MI = max(0, (171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC)) * 100 / 171)
    """
    if sloc <= 0:
        return 100.0

    v = max(1.0, halstead_volume)
    cc = max(1, cyclomatic_complexity)
    loc = max(1, sloc)

    try:
        raw_mi = 171.0 - 5.2 * math.log(v) - 0.23 * cc - 16.2 * math.log(loc)
        normalized_mi = max(0.0, min(100.0, (raw_mi * 100.0) / 171.0))
        return round(normalized_mi, 2)
    except Exception:
        return 75.0


def analyze_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Run comprehensive static analysis on code.
    Returns AST metrics, complexity scores, grade, and actionable smells.
    """
    raw_metrics = calculate_raw_metrics(code)
    smells = []

    if language.lower() == "python":
        try:
            tree = ast.parse(code)
            visitor = ASTComplexityVisitor()
            visitor.visit(tree)

            overall_cc = visitor.complexity
            func_details = visitor.functions
            class_count = len(visitor.classes)
            func_count = len(visitor.functions)
            loop_count = visitor.loops
            try_count = visitor.try_blocks

            # Detect code smells
            if overall_cc > 15:
                smells.append("High Cyclomatic Complexity (> 15). Consider breaking down nested conditionals.")
            if raw_metrics["loc"] > 80:
                smells.append("Long code block (> 80 lines). Consider modularizing into smaller functions.")
            if raw_metrics["comments"] == 0 and raw_metrics["sloc"] > 15:
                smells.append("Low documentation: zero comments or docstrings detected.")

            for func in func_details:
                if func["complexity"] > 10:
                    smells.append(f"Function `{func['name']}` has high complexity ({func['complexity']}).")
                if func["args_count"] > 5:
                    smells.append(f"Function `{func['name']}` accepts {func['args_count']} arguments (consider grouping into dataclass/dict).")

            # Try to calculate Radon metrics if available
            try:
                from radon.complexity import cc_visit
                from radon.metrics import mi_visit
                radon_cc_list = cc_visit(code)
                radon_mi = mi_visit(code, multi=False)
                mi_score = round(radon_mi, 2)
            except Exception:
                mi_score = calculate_maintainability_index(raw_metrics["sloc"], overall_cc)

            # Determine letter grade
            if mi_score >= 80 and overall_cc <= 8:
                grade = "A (Excellent)"
                grade_color = "#28a745"
            elif mi_score >= 65 and overall_cc <= 15:
                grade = "B (Good)"
                grade_color = "#17a2b8"
            elif mi_score >= 50:
                grade = "C (Moderate)"
                grade_color = "#ffc107"
            elif mi_score >= 35:
                grade = "D (Poor)"
                grade_color = "#fd7e14"
            else:
                grade = "F (High Risk)"
                grade_color = "#dc3545"

            return {
                "status": "success",
                "language": "python",
                "raw_metrics": raw_metrics,
                "cyclomatic_complexity": overall_cc,
                "maintainability_index": mi_score,
                "grade": grade,
                "grade_color": grade_color,
                "function_count": func_count,
                "class_count": class_count,
                "loop_count": loop_count,
                "try_count": try_count,
                "functions": func_details,
                "classes": visitor.classes,
                "code_smells": smells if smells else ["No critical code smells detected! Clean architecture."],
            }

        except SyntaxError as syn_err:
            return {
                "status": "syntax_error",
                "language": "python",
                "raw_metrics": raw_metrics,
                "error": f"SyntaxError at line {syn_err.lineno}: {syn_err.msg}",
                "grade": "F (Syntax Error)",
                "grade_color": "#dc3545",
                "cyclomatic_complexity": 0,
                "maintainability_index": 0.0,
                "code_smells": [f"Syntax Error: {syn_err.msg} at line {syn_err.lineno}"],
            }
    else:
        # Generic heuristic for other languages (JS, Java, C++, etc.)
        loc = raw_metrics["loc"]
        sloc = raw_metrics["sloc"]
        # Approximate CC by counting control keywords
        keywords = ["if ", "else if ", "for ", "while ", "catch ", "case ", "&&", "||"]
        cc_approx = 1 + sum(code.count(kw) for kw in keywords)
        mi_approx = calculate_maintainability_index(sloc, cc_approx)

        if mi_approx >= 80:
            grade = "A (Estimated)"
            grade_color = "#28a745"
        elif mi_approx >= 65:
            grade = "B (Estimated)"
            grade_color = "#17a2b8"
        else:
            grade = "C (Estimated)"
            grade_color = "#ffc107"

        return {
            "status": "success",
            "language": language,
            "raw_metrics": raw_metrics,
            "cyclomatic_complexity": cc_approx,
            "maintainability_index": mi_approx,
            "grade": grade,
            "grade_color": grade_color,
            "function_count": code.count("function ") + code.count("def "),
            "class_count": code.count("class "),
            "loop_count": code.count("for ") + code.count("while "),
            "try_count": code.count("try ") + code.count("catch "),
            "functions": [],
            "classes": [],
            "code_smells": smells or ["Standard multi-language structural heuristic applied."],
        }
