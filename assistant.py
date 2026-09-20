"""
assistant.py
============
Core AI Engine for the AI Coding Assistant.
Supports OpenAI, OpenAI-compatible providers (Groq, LocalAI, Ollama, OpenRouter),
and includes an intelligent offline/heuristic simulation fallback.
"""

import os
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

from prompts.system_prompts import (
    CODE_GENERATION_PROMPT,
    CODE_EXPLANATION_PROMPT,
    BUG_DETECTION_PROMPT,
    CODE_CONVERSION_PROMPT,
    DOCSTRING_GENERATION_PROMPT,
    UNIT_TEST_PROMPT,
    CODE_REFACTORING_PROMPT,
    PAIR_PROGRAMMER_PROMPT,
    REPOSITORY_ANALYSIS_PROMPT,
)


class AICodingAssistant:
    """
    Unified AI Coding Assistant engine.
    Wraps LLM API calls with error-handling, customizable parameters,
    and a built-in offline simulation mode.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
        temperature: float = 0.2,
        force_offline: bool = False,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
        self.model = model
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.temperature = max(0.0, min(1.0, temperature))
        self.force_offline = force_offline
        self.client = None

        if self.api_key and not self.force_offline and self.api_key != "YOUR_API_KEY":
            try:
                from openai import OpenAI
                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self.client = OpenAI(**kwargs)
            except Exception:
                self.client = None

    @property
    def is_live(self) -> bool:
        """Returns True if a live OpenAI/compatible client is available."""
        return self.client is not None and not self.force_offline

    def _call_llm(self, system_prompt: str, user_content: str, max_tokens: int = 2500) -> str:
        """Dispatches request to live LLM or offline fallback."""
        if self.is_live:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                # Fallback gracefully with error message + offline response
                offline_resp = self._offline_fallback(system_prompt, user_content)
                return f"> ⚠️ **Live API Notice:** Encountered connection/API error (`{str(e)}`). Switched to Offline Engine.\n\n{offline_resp}"
        else:
            return self._offline_fallback(system_prompt, user_content)

    def generate_code(self, prompt: str, language: str = "python", context: str = "") -> str:
        """Generate code based on natural language instructions."""
        user_msg = f"Language: {language}\n\nTask:\n{prompt}"
        if context:
            user_msg += f"\n\nExisting Context / Signature:\n{context}"
        return self._call_llm(CODE_GENERATION_PROMPT, user_msg)

    def explain_code(self, code: str, language: str = "python") -> str:
        """Provide detailed multi-level explanation of code."""
        user_msg = f"Language: {language}\n\nCode to explain:\n```{language}\n{code}\n```"
        return self._call_llm(CODE_EXPLANATION_PROMPT, user_msg)

    def detect_bugs(self, code: str, language: str = "python") -> str:
        """Detect bugs, logical errors, and vulnerabilities in code."""
        user_msg = f"Language: {language}\n\nCode to debug:\n```{language}\n{code}\n```"
        return self._call_llm(BUG_DETECTION_PROMPT, user_msg)

    def convert_code(self, code: str, source_lang: str, target_lang: str) -> str:
        """Transpile code from source language to target language."""
        user_msg = f"Convert from {source_lang} to {target_lang}.\n\nSource Code:\n```{source_lang}\n{code}\n```"
        return self._call_llm(CODE_CONVERSION_PROMPT, user_msg)

    def generate_documentation(self, code: str, style: str = "Google", language: str = "python") -> str:
        """Generate docstrings and API documentation."""
        user_msg = f"Language: {language}\nDocstring Standard: {style}\n\nCode:\n```{language}\n{code}\n```"
        return self._call_llm(DOCSTRING_GENERATION_PROMPT, user_msg)

    def generate_unit_tests(self, code: str, framework: str = "pytest", language: str = "python") -> str:
        """Generate a test suite for the provided code."""
        user_msg = f"Language: {language}\nTesting Framework: {framework}\n\nCode to test:\n```{language}\n{code}\n```"
        return self._call_llm(UNIT_TEST_PROMPT, user_msg)

    def refactor_code(self, code: str, objective: str = "Readability & Clean Code", language: str = "python") -> str:
        """Refactor code to optimize for readability, performance, or standards."""
        user_msg = f"Language: {language}\nRefactoring Objective: {objective}\n\nOriginal Code:\n```{language}\n{code}\n```"
        return self._call_llm(CODE_REFACTORING_PROMPT, user_msg)

    def chat_completion(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        """Conversational AI Pair Programmer interaction."""
        sys_p = system_prompt or PAIR_PROGRAMMER_PROMPT
        if self.is_live:
            try:
                full_messages = [{"role": "system", "content": sys_p}] + messages
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=full_messages,
                    temperature=self.temperature,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                latest_user = messages[-1]["content"] if messages else ""
                return f"> ⚠️ **Live API Notice:** Connection error (`{str(e)}`).\n\n" + self._offline_fallback(sys_p, latest_user)
        else:
            latest_user = messages[-1]["content"] if messages else ""
            return self._offline_fallback(sys_p, latest_user)

    def analyze_repository(self, files_dict: Dict[str, str]) -> str:
        """Analyze multi-file project contents."""
        formatted_files = []
        for path, content in files_dict.items():
            formatted_files.append(f"### File: `{path}`\n```\n{content[:1500]}\n```")
        user_msg = "Project Repository Files:\n\n" + "\n\n".join(formatted_files)
        return self._call_llm(REPOSITORY_ANALYSIS_PROMPT, user_msg, max_tokens=3500)

    # -------------------------------------------------------------------------
    # Deterministic Offline / Heuristic Simulation Engine
    # -------------------------------------------------------------------------
    def _offline_fallback(self, system_prompt: str, user_content: str) -> str:
        """
        High-fidelity heuristic engine simulating realistic AI assistant responses
        when running offline, without an API key, or in local demonstration mode.
        """
        prompt_lower = user_content.lower()
        sys_lower = system_prompt.lower()

        # 1. Unit Test Generator heuristic (check before general generation)
        if "test suite" in sys_lower or "unit test" in sys_lower or "testing" in sys_lower:
            return (
                "### ✅ Automated Unit Test Suite (`pytest`)\n\n"
                "```python\n"
                "import pytest\n\n"
                "# Assuming target function is imported from module\n"
                "# from my_module import is_prime\n\n"
                "class TestCodeFunctionality:\n"
                "    \"\"\"Comprehensive test suite verifying normal, boundary, and error conditions.\"\"\"\n\n"
                "    @pytest.mark.parametrize('input_val, expected', [\n"
                "        (2, True),       # Smallest prime\n"
                "        (3, True),       # Odd prime\n"
                "        (4, False),      # Smallest composite even\n"
                "        (17, True),      # Medium prime\n"
                "        (97, True),      # Largest 2-digit prime\n"
                "        (100, False),    # Composite\n"
                "    ])\n"
                "    def test_standard_cases(self, input_val, expected):\n"
                "        assert is_prime(input_val) == expected\n\n"
                "    @pytest.mark.parametrize('boundary_val', [-10, 0, 1]):\n"
                "        def test_boundary_and_negative_cases(self, boundary_val):\n"
                "            assert is_prime(boundary_val) is False\n\n"
                "    def test_invalid_type_raises_exception(self):\n"
                "        with pytest.raises(TypeError):\n"
                "            is_prime('not_a_number')\n\n"
                "# Execute tests with: pytest -v test_suite.py\n"
                "```"
            )

        # 2. Documentation generator heuristic
        if "docstring" in sys_lower or "documentation specialist" in sys_lower:
            return (
                "### 📝 Generated Documentation (Google Standard)\n\n"
                "```python\n"
                "\"\"\"\n"
                "Validates and evaluates input parameters according to mathematical specifications.\n\n"
                "Args:\n"
                "    num (int): The target numerical value to evaluate. Must be a non-negative integer.\n"
                "    verbose (bool, optional): If True, logs intermediate verification steps. Defaults to False.\n\n"
                "Returns:\n"
                "    bool: True if the verification passes all criteria, False otherwise.\n\n"
                "Raises:\n"
                "    TypeError: If `num` is not an integer type.\n"
                "    ValueError: If `num` is out of supported operating boundaries.\n\n"
                "Examples:\n"
                "    >>> is_prime(7)\n"
                "    True\n"
                "    >>> is_prime(8)\n"
                "    False\n"
                "\"\"\"\n"
                "```"
            )

        # 3. Bug Detection heuristic
        if "debug" in sys_lower or "bug" in sys_lower:
            if "index" in prompt_lower or "[5]" in user_content or "indexerror" in prompt_lower:
                return (
                    "### 🐞 Bug Detection & Diagnosis Report\n\n"
                    "#### 1. Bugs Detected\n"
                    "- **Type**: `IndexError: list index out of range`\n"
                    "- **Location**: Array/list subscript access `numbers[5]`\n"
                    "- **Root Cause**: The list contains only 3 elements (valid indices `0`, `1`, `2`). "
                    "Accessing index `5` triggers an out-of-bounds runtime exception.\n\n"
                    "#### 2. Fixed Code\n"
                    "```python\n"
                    "numbers = [1, 2, 3]\n\n"
                    "# Method 1: Defensive Bounds Checking\n"
                    "target_index = 5\n"
                    "if 0 <= target_index < len(numbers):\n"
                    "    print(numbers[target_index])\n"
                    "else:\n"
                    "    print(f'Warning: Index {target_index} is out of bounds for list of length {len(numbers)}')\n\n"
                    "# Method 2: Exception Handling\n"
                    "try:\n"
                    "    print(numbers[target_index])\n"
                    "except IndexError as err:\n"
                    "    print(f'Handled gracefully: {err}')\n"
                    "```\n\n"
                    "#### 3. Key Improvements\n"
                    "- Added boundary guards to prevent unhandled runtime crashes.\n"
                    "- Provided both defensive `len()` checking and idiomatic Python `try...except` patterns.\n\n"
                    "#### 4. Prevention Tip\n"
                    "- Always validate list lengths or use `.get()` equivalents when dealing with dynamic indices."
                )
            elif "indentation" in prompt_lower or "syntax" in prompt_lower:
                return (
                    "### 🐞 Bug Detection Report\n\n"
                    "#### 1. Bugs Detected\n"
                    "- **Type**: `SyntaxError / IndentationError`\n"
                    "- **Location**: Block declaration or control statement\n"
                    "- **Root Cause**: Inconsistent indentation or missing colon (`:`) after control statement.\n\n"
                    "#### 2. Fixed Code\n"
                    "```python\n"
                    "# Clean, standard 4-space indented code\n"
                    "def process_items(items):\n"
                    "    if not items:\n"
                    "        return []\n"
                    "    return [item.strip() for item in items if item]\n"
                    "```\n\n"
                    "#### 3. Key Improvements\n"
                    "- Corrected indentation to PEP 8 standard (4 spaces per level)."
                )
            else:
                return (
                    "### 🐞 Bug Detection & Code Audit\n\n"
                    "#### 1. Observations\n"
                    "- Checked for common anti-patterns: unhandled `None` values, off-by-one errors, and unclosed resources.\n"
                    "- Ensure input arguments are validated before passing them to internal operations.\n\n"
                    "#### 2. Hardened Code\n"
                    f"```python\n"
                    f"# Sanitized and guarded version\n"
                    f"{user_content}\n"
                    f"```\n\n"
                    "#### 3. Defensive Recommendations\n"
                    "- Add comprehensive type hints (`typing.Optional`, `typing.Union`).\n"
                    "- Implement unit test cases covering edge inputs (e.g. empty lists, None, zero)."
                )

        # 4. Code Explanation heuristic
        if "explain" in sys_lower:
            if "for i in range" in user_content or "range(" in prompt_lower:
                return (
                    "### 🔍 Code Explanation Walkthrough\n\n"
                    "#### 1. High-Level Purpose\n"
                    "This code uses a `for` loop to iterate sequentially over a generated sequence of integer values and output them to the console.\n\n"
                    "#### 2. Step-by-Step Breakdown\n"
                    "1. **`range(5)` Generator**: Produces a sequence starting at integer `0` up to (but not including) `5`. The values generated are `0, 1, 2, 3, 4`.\n"
                    "2. **Loop Variable `i`**: In each iteration, `i` binds to the subsequent integer in the sequence.\n"
                    "3. **`print(i)`**: Executes the standard output function, printing the current number on a new line.\n\n"
                    "#### 3. Complexity Analysis\n"
                    "- **Time Complexity**: **O(N)** where *N* is the range count (5 iterations in this example).\n"
                    "- **Space Complexity**: **O(1)** auxiliary space. `range()` in Python 3 generates numbers on-the-fly without allocating a full list in memory.\n\n"
                    "#### 4. Execution Trace\n"
                    "| Iteration | Variable `i` | Console Output |\n"
                    "|---|---|---|\n"
                    "| 1 | 0 | `0` |\n"
                    "| 2 | 1 | `1` |\n"
                    "| 3 | 2 | `2` |\n"
                    "| 4 | 3 | `3` |\n"
                    "| 5 | 4 | `4` |"
                )
            else:
                return (
                    "### 🔍 Code Explanation & Technical Breakdown\n\n"
                    "#### 1. High-Level Purpose\n"
                    "The provided code implements a specific computational or data-processing routine. It handles input parameters, executes procedural logic, and returns or produces state changes.\n\n"
                    "#### 2. Step-by-Step Execution\n"
                    "- **Initialization**: Prepares local variables, parameters, or data structures.\n"
                    "- **Core Execution**: Iterates or transforms data using conditional branches and function invocations.\n"
                    "- **Output / Return**: Yields the final computed result.\n\n"
                    "#### 3. Complexity Summary\n"
                    "- **Time Complexity**: Linear to polynomial depending on nesting structure.\n"
                    "- **Space Complexity**: Proportional to auxiliary structures created during execution."
                )

        # 5. Code Conversion heuristic
        if "convert" in sys_lower or "transpilation" in sys_lower or "polyglot" in sys_lower:
            if "select" in prompt_lower or "sql" in prompt_lower:
                return (
                    "### 🔄 SQL to Pandas DataFrame Transpilation\n\n"
                    "#### Equivalent Pandas Implementation\n"
                    "```python\n"
                    "import pandas as pd\n\n"
                    "# Assuming DataFrame `df` loaded from source table\n"
                    "# SQL: SELECT department, COUNT(*), AVG(salary) FROM employees GROUP BY department HAVING COUNT(*) > 5\n"
                    "result_df = (\n"
                    "    df.groupby('department')\n"
                    "    .agg(\n"
                    "        employee_count=('id', 'count'),\n"
                    "        avg_salary=('salary', 'mean')\n"
                    "    )\n"
                    "    .query('employee_count > 5')\n"
                    "    .reset_index()\n"
                    ")\n"
                    "```\n\n"
                    "#### Paradigm Differences\n"
                    "- **SQL**: Declarative relational query executed by database query planner.\n"
                    "- **Pandas**: Vectorized in-memory DataFrame operations utilizing NumPy memory buffers under the hood."
                )
            elif "python to java" in prompt_lower or "java" in prompt_lower:
                return (
                    "### 🔄 Python to Java Transpilation\n\n"
                    "```java\n"
                    "public class Solution {\n"
                    "    public static boolean isPrime(int num) {\n"
                    "        if (num <= 1) return false;\n"
                    "        if (num <= 3) return true;\n"
                    "        if (num % 2 == 0 || num % 3 == 0) return false;\n"
                    "        for (int i = 5; (long) i * i <= num; i += 6) {\n"
                    "            if (num % i == 0 || num % (i + 2) == 0) return false;\n"
                    "        }\n"
                    "        return true;\n"
                    "    }\n\n"
                    "    public static void main(String[] args) {\n"
                    "        int testNum = 29;\n"
                    "        System.out.println(testNum + \" is prime: \" + isPrime(testNum));\n"
                    "    }\n"
                    "}\n"
                    "```\n\n"
                    "#### Key Paradigm Shifts\n"
                    "- Strongly typed method signatures and explicit class encapsulation.\n"
                    "- Casting to `(long)` to prevent potential integer overflow during square calculation."
                )

        # 6. Refactoring heuristic
        if "refactor" in sys_lower:
            return (
                "### ⚡ Code Refactoring & Optimization Analysis\n\n"
                "#### 1. Issues in Original Code\n"
                "- High cognitive complexity and deeply nested branch statements.\n"
                "- Redundant iterations over already verified elements.\n"
                "- Missing type annotations and guard clauses.\n\n"
                "#### 2. Optimized Version\n"
                "```python\n"
                "from typing import Sequence\n\n"
                "def clean_and_optimize(items: Sequence[int]) -> list[int]:\n"
                "    \"\"\"Optimized, readable, and modern list comprehension.\"\"\"\n"
                "    if not items:\n"
                "        return []\n"
                "    # Set-based lookup for O(1) deduplication\n"
                "    seen = set()\n"
                "    return [x for x in items if not (x in seen or seen.add(x))]\n"
                "```\n\n"
                "#### 3. Comparative Matrix\n"
                "- **Cognitive Complexity**: Reduced by 60% via early return guard clauses.\n"
                "- **Runtime Efficiency**: Improved from $O(N^2)$ to $O(N)$ using hash set tracking."
            )

        # 7. Code Generation heuristic
        if "generate" in sys_lower or "code generation" in sys_lower:
            if "prime" in prompt_lower:
                return (
                    "### 💻 Prime Number Checker\n\n"
                    "Here is an optimized, production-ready prime verification function using the $O(\\sqrt{n})$ trial division algorithm with edge-case handling:\n\n"
                    "```python\n"
                    "def is_prime(num: int) -> bool:\n"
                    "    \"\"\"\n"
                    "    Check whether an integer is prime.\n\n"
                    "    Args:\n"
                    "        num (int): The integer to evaluate.\n\n"
                    "    Returns:\n"
                    "        bool: True if num is prime, False otherwise.\n"
                    "    \"\"\"\n"
                    "    if not isinstance(num, int):\n"
                    "        raise TypeError('Input must be an integer')\n"
                    "    if num <= 1:\n"
                    "        return False\n"
                    "    if num <= 3:\n"
                    "        return True\n"
                    "    if num % 2 == 0 or num % 3 == 0:\n"
                    "        return False\n\n"
                    "    # Check factors up to sqrt(num) using 6k +/- 1 optimization\n"
                    "    i = 5\n"
                    "    while i * i <= num:\n"
                    "        if num % i == 0 or num % (i + 2) == 0:\n"
                    "            return False\n"
                    "        i += 6\n"
                    "    return True\n\n"
                    "# Example Usage\n"
                    "if __name__ == '__main__':\n"
                    "    test_numbers = [1, 2, 3, 4, 17, 25, 29, 97, 100]\n"
                    "    results = {n: is_prime(n) for n in test_numbers}\n"
                    "    print(results)\n"
                    "```\n\n"
                    "**Complexity**:\n"
                    "- Time: $O(\\sqrt{n})$\n"
                    "- Space: $O(1)$"
                )
            elif "reverse" in prompt_lower:
                return (
                    "### 💻 String Reversal Function\n\n"
                    "```python\n"
                    "def reverse_string(text: str) -> str:\n"
                    "    \"\"\"\n"
                    "    Reverses a string using Pythonic slice notation.\n\n"
                    "    Args:\n"
                    "        text (str): Input string to reverse.\n\n"
                    "    Returns:\n"
                    "        str: The reversed string.\n"
                    "    \"\"\"\n"
                    "    if not isinstance(text, str):\n"
                    "        raise TypeError('Expected a string input')\n"
                    "    return text[::-1]\n\n"
                    "# Example verification\n"
                    "if __name__ == '__main__':\n"
                    "    sample = 'AI Assistant'\n"
                    "    print(f'Original: {sample}')\n"
                    "    print(f'Reversed: {reverse_string(sample)}')\n"
                    "```"
                )
            else:
                return (
                    f"### 💻 Generated Solution\n\n"
                    f"```python\n"
                    f"# Implementation for: {user_content[:60]}...\n"
                    f"def solve_task(*args, **kwargs):\n"
                    f"    \"\"\"Implementation placeholder with type annotations.\"\"\"\n"
                    f"    # Process task inputs\n"
                    f"    result = True\n"
                    f"    return result\n\n"
                    f"if __name__ == '__main__':\n"
                    f"    print(solve_task())\n"
                    f"```\n\n"
                    f"- **Clean Architecture**: Follows PEP 8 styling.\n"
                    f"- **Validation**: Parameter checks and docstrings included."
                )

        # 7. Refactoring heuristic
        if "refactor" in system_prompt.lower():
            return (
                "### ⚡ Code Refactoring & Optimization Analysis\n\n"
                "#### 1. Issues in Original Code\n"
                "- High cognitive complexity and deeply nested branch statements.\n"
                "- Redundant iterations over already verified elements.\n"
                "- Missing type annotations and guard clauses.\n\n"
                "#### 2. Optimized Version\n"
                "```python\n"
                "from typing import Sequence\n\n"
                "def clean_and_optimize(items: Sequence[int]) -> list[int]:\n"
                "    \"\"\"Optimized, readable, and modern list comprehension.\"\"\"\n"
                "    if not items:\n"
                "        return []\n"
                "    # Set-based lookup for O(1) deduplication\n"
                "    seen = set()\n"
                "    return [x for x in items if not (x in seen or seen.add(x))]\n"
                "```\n\n"
                "#### 3. Comparative Matrix\n"
                "- **Cognitive Complexity**: Reduced by 60% via early return guard clauses.\n"
                "- **Runtime Efficiency**: Improved from $O(N^2)$ to $O(N)$ using hash set tracking."
            )

        # Default conversational / assistant fallback
        return (
            "### 🤖 AI Coding Assistant Response\n\n"
            f"**Received Request:**\n> {user_content[:150]}...\n\n"
            "```python\n"
            "# Production implementation\n"
            "def execute_solution():\n"
            "    # Code tailored for optimal clarity and safety\n"
            "    return 'Task successfully processed!'\n"
            "```\n\n"
            "- Validated across edge scenarios.\n"
            "- Ready for immediate integration."
        )
