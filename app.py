"""
app.py
======
Production-grade Streamlit Web Application for the AI Coding Assistant.
Provides multi-tab navigation, real-time AST complexity analysis, multi-file
repo scanning, interactive pair programming chat, and seamless OpenAI / Offline switching.
"""

import os
import streamlit as st
from assistant import AICodingAssistant
from code_analyzer import analyze_code
from repo_analyzer import (
    parse_zip_archive,
    parse_local_directory,
    summarize_repository_metrics,
)

# -----------------------------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Coding Assistant | Pro Developer Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    /* Metric and Card Styling */
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-live {
        background-color: #d1e7dd;
        color: #0f5132;
    }
    .status-offline {
        background-color: #fff3cd;
        color: #664d03;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Sidebar: Settings, Model Config & Presets
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
    st.title("AI Assistant Settings")
    st.markdown("---")

    mode_choice = st.radio(
        "Engine Mode",
        options=["Auto / Live LLM", "Force Offline Simulator"],
        help="Auto/Live LLM uses OpenAI or compatible endpoints. Offline Simulator works immediately with no API key or network required."
    )
    force_offline = (mode_choice == "Force Offline Simulator")

    api_key_input = st.text_input(
        "OpenAI API Key (Optional)",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Leave blank to use environment variable OPENAI_API_KEY or offline simulator."
    )

    base_url_input = st.text_input(
        "Base URL (Optional / Ollama / Groq)",
        value=os.getenv("OPENAI_BASE_URL", ""),
        placeholder="e.g. http://localhost:11434/v1",
        help="Use for local LLMs via Ollama, LM Studio, or Groq API."
    )

    model_options = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "llama-3.1-70b-versatile",
        "codellama",
        "custom",
    ]
    model_choice = st.selectbox("Model", options=model_options, index=1)
    if model_choice == "custom":
        model_choice = st.text_input("Custom Model Name", value="gpt-4o-mini")

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05)

    st.markdown("---")
    st.subheader("System Status")

    # Instantiate the assistant
    assistant = AICodingAssistant(
        api_key=api_key_input if api_key_input.strip() else None,
        model=model_choice,
        base_url=base_url_input if base_url_input.strip() else None,
        temperature=temperature,
        force_offline=force_offline,
    )

    if assistant.is_live:
        st.markdown(f'<span class="status-badge status-live">🟢 LIVE ({assistant.model})</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-offline">🟡 OFFLINE SIMULATOR</span>', unsafe_allow_html=True)
        st.caption("All features functional using built-in deterministic engine.")

    st.markdown("---")
    st.caption("AI Coding Assistant v2.0 | Built with Python & Streamlit")


# -----------------------------------------------------------------------------
# Main Header
# -----------------------------------------------------------------------------
st.title("⚡ AI Coding Assistant")
st.markdown(
    "Your intelligent developer companion for **code generation**, **explanation**, **bug detection**, "
    "**polyglot conversion**, **unit testing**, **AST complexity scoring**, and **multi-file architecture analysis**."
)

# -----------------------------------------------------------------------------
# Tabs Interface
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "💻 Code Gen",
    "🔍 Explainer",
    "🐞 Bug Fixer",
    "🔄 Polyglot",
    "📝 Docstrings",
    "✅ Unit Tests",
    "⚡ Refactoring",
    "📊 AST Quality",
    "📁 Repo Scanner",
    "💬 Pair Chat",
])


# -----------------------------------------------------------------------------
# Tab 1: Code Generation
# -----------------------------------------------------------------------------
with tabs[0]:
    st.header("💻 Natural Language Code Generation")
    st.markdown("Describe the algorithm, function, or component you want to build.")

    col1, col2 = st.columns([3, 1])
    with col2:
        lang_gen = st.selectbox(
            "Target Language",
            options=["python", "javascript", "typescript", "java", "cpp", "go", "rust", "sql", "html"],
            key="gen_lang"
        )

    with col1:
        default_gen_prompt = "Write an optimized Python function to check whether a given integer is a prime number."
        gen_prompt = st.text_area(
            "Natural Language Prompt",
            value=default_gen_prompt,
            height=120,
            placeholder="e.g., Write a function that downloads an image from a URL with retry logic..."
        )

    with st.expander("Additional Context / Function Signature (Optional)"):
        gen_context = st.text_area("Context / Existing types", height=80)

    if st.button("🚀 Generate Code", type="primary", key="btn_gen"):
        if not gen_prompt.strip():
            st.warning("Please enter a prompt first.")
        else:
            with st.spinner("Generating code with AI..."):
                response = assistant.generate_code(gen_prompt, language=lang_gen, context=gen_context)
            st.markdown(response)
            st.download_button("💾 Download Output", data=response, file_name=f"generated_code.{lang_gen}", mime="text/plain")


# -----------------------------------------------------------------------------
# Tab 2: Code Explanation
# -----------------------------------------------------------------------------
with tabs[1]:
    st.header("🔍 Code Explanation & Complexity Breakdown")
    st.markdown("Paste any code snippet to receive an executive summary, line-by-line breakdown, and Big-O analysis.")

    col1, col2 = st.columns([3, 1])
    with col2:
        lang_exp = st.selectbox("Language", ["python", "javascript", "java", "cpp", "go", "sql"], key="exp_lang")

    with col1:
        default_exp_code = (
            "for i in range(5):\n"
            "    print(i)"
        )
        exp_code = st.text_area("Source Code", value=default_exp_code, height=150)

    if st.button("🔍 Explain Code", type="primary", key="btn_exp"):
        if not exp_code.strip():
            st.warning("Please provide code to explain.")
        else:
            with st.spinner("Analyzing code architecture and complexity..."):
                explanation = assistant.explain_code(exp_code, language=lang_exp)
            st.markdown(explanation)


# -----------------------------------------------------------------------------
# Tab 3: Bug Detection & Debugger
# -----------------------------------------------------------------------------
with tabs[2]:
    st.header("🐞 Bug Detection & Automated Patching")
    st.markdown("Detect syntax bugs, boundary condition errors, null dereferences, and security vulnerabilities.")

    col1, col2 = st.columns([3, 1])
    with col2:
        lang_bug = st.selectbox("Language", ["python", "javascript", "java", "cpp", "go"], key="bug_lang")

    with col1:
        default_bug_code = (
            "numbers = [1, 2, 3]\n"
            "print(numbers[5])"
        )
        bug_code = st.text_area("Problematic Code", value=default_bug_code, height=150)

    if st.button("🐞 Detect & Fix Bugs", type="primary", key="btn_bug"):
        if not bug_code.strip():
            st.warning("Please provide code to debug.")
        else:
            with st.spinner("Inspecting code for defects and runtime failures..."):
                report = assistant.detect_bugs(bug_code, language=lang_bug)
            st.markdown(report)


# -----------------------------------------------------------------------------
# Tab 4: Polyglot Code Converter
# -----------------------------------------------------------------------------
with tabs[3]:
    st.header("🔄 Polyglot Code Transpiler")
    st.markdown("Translate source code between different programming languages and paradigms while preserving logic.")

    col_s, col_t = st.columns(2)
    with col_s:
        source_lang = st.selectbox("Source Language", ["sql", "python", "javascript", "java", "cpp", "go", "rust"], index=0)
    with col_t:
        target_lang = st.selectbox("Target Language", ["pandas", "python", "javascript", "typescript", "java", "go", "rust"], index=0)

    default_trans_code = (
        "SELECT department, COUNT(*), AVG(salary)\n"
        "FROM employees\n"
        "GROUP BY department\n"
        "HAVING COUNT(*) > 5;"
    )
    trans_code = st.text_area("Source Code", value=default_trans_code, height=150)

    if st.button("🔄 Convert Code", type="primary", key="btn_trans"):
        if not trans_code.strip():
            st.warning("Please provide code to convert.")
        else:
            with st.spinner(f"Transpiling from {source_lang} to {target_lang}..."):
                transpiled = assistant.convert_code(trans_code, source_lang, target_lang)
            st.markdown(transpiled)


# -----------------------------------------------------------------------------
# Tab 5: Documentation & Docstrings
# -----------------------------------------------------------------------------
with tabs[4]:
    st.header("📝 Docstrings & Documentation Generator")
    st.markdown("Generate standardized docstrings (Google, NumPy, Sphinx) and API markdown.")

    col1, col2 = st.columns([2, 1])
    with col2:
        doc_style = st.selectbox("Docstring Standard", ["Google Style", "NumPy Style", "Sphinx / reST", "JSDoc"])
        doc_lang = st.selectbox("Language", ["python", "javascript", "typescript", "java"], key="doc_lang")

    with col1:
        default_doc_code = (
            "def is_prime(num):\n"
            "    if num < 2:\n"
            "        return False\n"
            "    for i in range(2, int(num**0.5) + 1):\n"
            "        if num % i == 0:\n"
            "            return False\n"
            "    return True"
        )
        doc_code = st.text_area("Function / Class Code", value=default_doc_code, height=150)

    if st.button("📝 Generate Documentation", type="primary", key="btn_doc"):
        if not doc_code.strip():
            st.warning("Please provide code.")
        else:
            with st.spinner("Generating standardized documentation..."):
                docs = assistant.generate_documentation(doc_code, style=doc_style, language=doc_lang)
            st.markdown(docs)


# -----------------------------------------------------------------------------
# Tab 6: Unit Test Generator
# -----------------------------------------------------------------------------
with tabs[5]:
    st.header("✅ Automated Unit Test Generator")
    st.markdown("Generate parameterized test suites covering normal execution, edge cases, and exceptions.")

    col1, col2 = st.columns([2, 1])
    with col2:
        test_framework = st.selectbox("Framework", ["pytest", "unittest", "Jest", "JUnit 5", "Go testing"])
        test_lang = st.selectbox("Language", ["python", "javascript", "java", "go"], key="test_lang")

    with col1:
        default_test_code = (
            "def is_prime(num):\n"
            "    if num < 2:\n"
            "        return False\n"
            "    for i in range(2, int(num**0.5) + 1):\n"
            "        if num % i == 0:\n"
            "            return False\n"
            "    return True"
        )
        test_code = st.text_area("Target Code to Test", value=default_test_code, height=150)

    if st.button("✅ Generate Test Suite", type="primary", key="btn_test"):
        if not test_code.strip():
            st.warning("Please provide code.")
        else:
            with st.spinner(f"Generating test cases for {test_framework}..."):
                tests = assistant.generate_unit_tests(test_code, framework=test_framework, language=test_lang)
            st.markdown(tests)
            st.download_button("💾 Download Test Suite", data=tests, file_name=f"test_suite.{test_lang}", mime="text/plain")


# -----------------------------------------------------------------------------
# Tab 7: Code Refactoring
# -----------------------------------------------------------------------------
with tabs[6]:
    st.header("⚡ Code Refactoring & Optimization")
    st.markdown("Transform legacy or unoptimized code into clean, idiomatic, high-performance architecture.")

    col1, col2 = st.columns([2, 1])
    with col2:
        refactor_goal = st.selectbox(
            "Optimization Goal",
            [
                "Readability & Clean Code",
                "Runtime Performance (Time Complexity)",
                "Memory Optimization (Space Complexity)",
                "Modern Language Features (Python 3.12+)",
                "Security & Defensive Hardening",
            ]
        )
        ref_lang = st.selectbox("Language", ["python", "javascript", "java", "cpp"], key="ref_lang")

    with col1:
        default_ref_code = (
            "def get_unique_evens(nums):\n"
            "    result = []\n"
            "    for n in nums:\n"
            "        if n % 2 == 0:\n"
            "            if n not in result:\n"
            "                result.append(n)\n"
            "    return result"
        )
        ref_code = st.text_area("Code to Refactor", value=default_ref_code, height=150)

    if st.button("⚡ Refactor Code", type="primary", key="btn_ref"):
        if not ref_code.strip():
            st.warning("Please provide code to refactor.")
        else:
            with st.spinner("Refactoring code for optimal structure..."):
                refactored = assistant.refactor_code(ref_code, objective=refactor_goal, language=ref_lang)
            st.markdown(refactored)


# -----------------------------------------------------------------------------
# Tab 8: AST & Radon Code Quality Scorer
# -----------------------------------------------------------------------------
with tabs[7]:
    st.header("📊 Real-Time AST & Radon Code Complexity Scorer")
    st.markdown("Instant static analysis computing Cyclomatic Complexity, Maintainability Index, and code smells.")

    col_input, col_meta = st.columns([3, 1])
    with col_meta:
        qa_lang = st.selectbox("Language", ["python", "javascript", "java"], key="qa_lang")

    with col_input:
        default_qa_code = (
            "def calculate_tax(income, status, deductions):\n"
            "    # Sample calculation with branching\n"
            "    if income <= 0:\n"
            "        return 0.0\n"
            "    elif status == 'single':\n"
            "        taxable = max(0, income - deductions)\n"
            "        if taxable < 10000:\n"
            "            return taxable * 0.10\n"
            "        elif taxable < 40000:\n"
            "            return 1000 + (taxable - 10000) * 0.12\n"
            "        else:\n"
            "            return 4600 + (taxable - 40000) * 0.22\n"
            "    else:\n"
            "        return max(0, income - deductions) * 0.15\n"
        )
        qa_code = st.text_area("Python Source Code to Score", value=default_qa_code, height=200)

    if st.button("📊 Calculate Metrics", type="primary", key="btn_metrics"):
        if not qa_code.strip():
            st.warning("Please provide code.")
        else:
            results = analyze_code(qa_code, language=qa_lang)

            if results["status"] == "syntax_error":
                st.error(results["error"])
            else:
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Maintainability Index (MI)", f"{results['maintainability_index']}/100")
                with m2:
                    st.metric("Cyclomatic Complexity (CC)", results["cyclomatic_complexity"])
                with m3:
                    st.metric("Source LOC", results["raw_metrics"]["sloc"])
                with m4:
                    st.metric("Code Health Grade", results["grade"])

                st.subheader("Architectural Code Smells & Recommendations")
                for smell in results["code_smells"]:
                    st.info(f"💡 {smell}")

                if results.get("functions"):
                    st.subheader("Function-Level Complexity")
                    func_table = [
                        {"Function": f["name"], "Line": f["lineno"], "Complexity": f["complexity"], "Arguments": f["args_count"]}
                        for f in results["functions"]
                    ]
                    st.table(func_table)


# -----------------------------------------------------------------------------
# Tab 9: Repository & Multi-File Scanner
# -----------------------------------------------------------------------------
with tabs[8]:
    st.header("📁 Multi-File & Repository Architecture Scanner")
    st.markdown("Upload a project ZIP file or inspect a local directory to analyze project architecture and dependencies.")

    scan_mode = st.radio("Scan Source", ["Upload ZIP Archive", "Local Directory Path"], horizontal=True)
    files_dict = {}

    if scan_mode == "Upload ZIP Archive":
        uploaded_zip = st.file_uploader("Upload Project Archive (.zip)", type=["zip"])
        if uploaded_zip:
            files_dict = parse_zip_archive(uploaded_zip.read())
            st.success(f"Extracted {len(files_dict)} source files from archive.")
    else:
        dir_input = st.text_input("Enter Local Directory Path", value=".")
        if st.button("Scan Local Directory"):
            if os.path.exists(dir_input):
                files_dict = parse_local_directory(dir_input)
                st.success(f"Scanned {len(files_dict)} source files in `{dir_input}`.")
            else:
                st.error(f"Directory `{dir_input}` does not exist.")

    if files_dict:
        repo_summary = summarize_repository_metrics(files_dict)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Files Analyzed", repo_summary["total_files"])
        with col_b:
            st.metric("Total Code Lines (LOC)", repo_summary["total_loc"])
        with col_c:
            st.metric("Entry Points Found", len(repo_summary["entry_points"]))

        with st.expander("Detected Dependencies & Extensions Breakdown"):
            st.write("**File Extensions:**", repo_summary["language_distribution"])
            st.write("**External Libraries Detected:**", ", ".join(repo_summary["detected_dependencies"]) or "None")
            st.write("**Entry Points:**", ", ".join(repo_summary["entry_points"]) or "None identified")

        if st.button("🤖 Generate Comprehensive Architecture Review", type="primary"):
            with st.spinner("Synthesizing multi-file codebase architecture..."):
                review = assistant.analyze_repository(files_dict)
            st.markdown(review)


# -----------------------------------------------------------------------------
# Tab 10: Interactive AI Pair Programmer (Chat)
# -----------------------------------------------------------------------------
with tabs[9]:
    st.header("💬 AI Pair Programmer (Interactive Chat)")
    st.markdown("Pair program in real-time. Discuss architecture, refactoring ideas, debugging sessions, and design patterns.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your AI Pair Programmer. What are we building or debugging today?"}
        ]

    # Render previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask a coding question, share a problem, or ask for architectural feedback..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = assistant.chat_completion(st.session_state.messages)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("🧹 Clear Chat History", key="clear_chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat history cleared. How can I assist you now?"}
        ]
        st.rerun()
