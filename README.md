# ⚡ AI Coding Assistant

🚀 Links

- 🌐 **Live Demo:** https://my-ai-coding-assistant.streamlit.app
- 💻 **Source Code:** https://github.com/narayanwentianluo-code/ai-coding-assistant

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-red.svg)](https://streamlit.io/)
[![LLM Support](https://img.shields.io/badge/LLM-OpenAI%20%7C%20Ollama%20%7C%20Groq-green.svg)](https://platform.openai.com/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

An end-to-end, production-grade **AI-powered Developer Productivity Platform** built with **Python**, **Streamlit**, and **Large Language Models**. 

Designed to boost developer speed across the entire software development lifecycle (SDLC) — from code generation and debugging to AST complexity scoring, polyglot transpilation, and multi-file repository architecture auditing.

---

## 🚀 Key Features

### 🌟 Beginner Suite
- **Natural Language Code Generation**: Generate idiomatic code across Python, JavaScript, TypeScript, Java, C++, Go, Rust, and SQL with edge-case handling and type hints.
- **Code Explanation**: Two-tier breakdown featuring an executive summary, line-by-line trace, and Big-O ($O(N)$) time/space complexity analysis.
- **Bug Detection & Automated Patching**: Identifies defect categories (IndexError, Off-by-one, Syntax, Resource leaks), points to exact faulty lines, and outputs guarded fixes.

### ⚡ Intermediate Suite
- **Polyglot Code Transpiler**: Convert code between languages and paradigms (e.g. SQL Queries to vectorized Pandas DataFrames, procedural Python to OOP Java).
- **Docstrings & Documentation Generator**: Generates professional docstrings formatted to Google, NumPy, Sphinx/reST, and JSDoc standards.
- **Automated Unit Test Generator**: Generates parameterized, robust test suites for `pytest`, `unittest`, `Jest`, and `JUnit` covering edge cases and error bounds.

### 🧠 Advanced Suite
- **Real-Time AST & Radon Complexity Scorer**: Uses Abstract Syntax Tree (AST) parsing and Radon to calculate Cyclomatic Complexity, Maintainability Index (MI: 0-100), SLOC, and flags architectural code smells with an instant letter grade (A-F).
- **Multi-File & Repository Scanner**: Upload `.zip` archives or point to local directories to analyze architecture, cross-file imports, external dependencies, and entry points.
- **Automated Code Refactoring**: Optimize legacy code for readability, execution speed ($O(N^2) \to O(N)$), space efficiency, and modern language idioms (Python 3.12+).
- **Interactive AI Pair Programmer**: Real-time conversational partner with persistent chat history, trade-off reasoning, and debugging guidance.

### 🛡️ Hybrid Engine (Live API + Deterministic Offline Simulator)
- **Zero-barrier Instant Testing**: If no API key is provided or the machine is offline, the assistant automatically switches to a built-in deterministic heuristic simulation engine. Every single feature is 100% testable out of the box!
- **Pluggable LLMs**: Works with OpenAI (`gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`), local models via **Ollama** (`codellama`, `llama3`), or cloud accelerators like **Groq**.

---

## 🏗️ Architecture Overview

```
                                  +-----------------------------+
                                  |     Streamlit Web UI        |
                                  |  (Tabs, Sidebar, Settings)  |
                                  +--------------+--------------+
                                                 |
                       +-------------------------+-------------------------+
                       |                                                   |
         +-------------v-------------+                               +-----v---------------------+
         |     Assistant Engine      |                               | Static Analysis & Metrics |
         |   (assistant.py & prompts)|                               |     (code_analyzer.py)    |
         +-------------+-------------+                               +-------------+-------------+
                       |                                                           |
          +------------+------------+                                              |
          |                         |                                              |
+---------v---------+     +---------v---------+                      +-------------v-------------+
|   OpenAI / LLM    |     | Heuristic Offline |                      | AST & Radon Complexity    |
|   API Provider    |     |      Fallback     |                      | (Cyclomatic, Halstead, MI)|
+-------------------+     +-------------------+                      +---------------------------+
```

---

## 📂 Project Structure

```
ai-coding-assistant/
├── app.py                      # Main Streamlit web application
├── assistant.py                # Core AI Engine (OpenAI caller + Offline Simulator)
├── code_analyzer.py            # Static AST & Radon complexity engine
├── repo_analyzer.py            # Multi-file project & ZIP repository scanner
├── prompts/
│   ├── __init__.py
│   └── system_prompts.py       # Prompt engineering templates for all 10 modules
├── tests/
│   ├── __init__.py
│   ├── test_assistant.py       # Unit tests for assistant engine
│   └── test_analyzer.py        # Unit tests for complexity metrics
├── .env.example                # Sample environment variables
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Project dependencies
├── README.md                   # Full documentation & setup guide
├── generate_docs.py            # Word DOCX reference manual generator
└── AI_Coding_Assistant_Complete_Guide.docx  # Comprehensive reference guide
```

---

## 🛠️ Step-by-Step Setup Guide

### 1. Clone or Open Project
```powershell
cd C:\Users\naray\.gemini\antigravity\scratch\ai-coding-assistant
```

### 2. Create and Activate Virtual Environment (Recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 4. Configure API Key (Optional)
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Open `.env` and set your key:
```ini
OPENAI_API_KEY=sk-...
```
*(Note: If you do not have an API key, the assistant runs in offline simulator mode seamlessly!)*

### 5. Run Unit Tests
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

### 6. Launch the Streamlit Dashboard
```powershell
python -m streamlit run app.py
```
Your default browser will open to `http://localhost:8501`.

---

## 🌐 Deployment Options

### Streamlit Community Cloud (Free & 1-Click)
1. Push this directory to a GitHub repository.
2. Log into [share.streamlit.io](https://share.streamlit.io/).
3. Select your repository and specify `app.py` as the entrypoint.
4. Under **Advanced Settings**, add `OPENAI_API_KEY` to Secrets.

### Render / Railway / Hugging Face Spaces
- Specify start command: `python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- Configure environment variable `OPENAI_API_KEY`.

---

## 💼 Resume & Interview Talking Points

### Resume Description
> **AI Coding Assistant & Developer Intelligence Platform | Python, Streamlit, LLMs, AST, Radon**
> - Architected a multi-modal developer assistant supporting automated code generation, polyglot transpilation (SQL-to-Pandas, Python-to-Java), bug localization, and automated unit testing.
> - Engineered an Abstract Syntax Tree (AST) static analysis engine integrated with Radon to compute Cyclomatic Complexity, Maintainability Index, and code smells in real-time.
> - Designed a resilient hybrid backend with automatic failover between live OpenAI/compatible APIs and a local deterministic heuristic simulation engine.
> - Implemented multi-file repository scanning for architecture analysis, entry-point discovery, and dependency graph mapping.

---

## 📄 Documentation Manual
A publication-quality Microsoft Word manual (`AI_Coding_Assistant_Complete_Guide.docx`) is generated with complete blueprints, mathematical formulas, prompt catalogs, source code listings, and interview questions.

To regenerate the manual at any time:
```powershell
python generate_docs.py
```
