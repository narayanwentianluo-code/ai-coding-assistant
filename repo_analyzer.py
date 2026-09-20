"""
repo_analyzer.py
================
Multi-file and Repository Architecture Analyzer.
Parses ZIP archives or directory trees, extracts dependency graphs,
detects project entry points, and provides high-level architectural metrics.
"""

import io
import os
import zipfile
from typing import Any, Dict, List, Set


IGNORE_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "env",
    "node_modules", ".pytest_cache", ".idea", ".vscode", "dist", "build"
}

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java",
    ".cpp", ".c", ".h", ".hpp", ".go", ".rs", ".sql", ".html", ".css", ".json", ".md"
}


def parse_zip_archive(zip_bytes: bytes, max_files: int = 50) -> Dict[str, str]:
    """Extract code files from an uploaded zip file buffer."""
    files_dict = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        for member in zf.infolist():
            if member.is_dir():
                continue

            parts = member.filename.replace("\\", "/").split("/")
            if any(p in IGNORE_DIRS for p in parts):
                continue

            ext = os.path.splitext(member.filename)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                try:
                    content = zf.read(member.filename).decode("utf-8", errors="replace")
                    files_dict[member.filename] = content
                    if len(files_dict) >= max_files:
                        break
                except Exception:
                    continue

    return files_dict


def parse_local_directory(dir_path: str, max_files: int = 50) -> Dict[str, str]:
    """Scan a local directory for source code files."""
    files_dict = {}
    for root, dirs, files in os.walk(dir_path):
        # Filter out ignored dirs
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, dir_path)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        files_dict[rel_path] = f.read()
                    if len(files_dict) >= max_files:
                        return files_dict
                except Exception:
                    continue
    return files_dict


def extract_python_imports(code: str) -> Set[str]:
    """Extract imported modules from Python source code."""
    imports = set()
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("import "):
            parts = line.replace("import ", "").split(",")
            for p in parts:
                mod = p.strip().split()[0].split(".")[0]
                imports.add(mod)
        elif line.startswith("from "):
            parts = line.split()
            if len(parts) >= 2:
                mod = parts[1].split(".")[0]
                imports.add(mod)
    return imports


def summarize_repository_metrics(files_dict: Dict[str, str]) -> Dict[str, Any]:
    """Generate aggregate statistics and architecture overview for a project."""
    total_files = len(files_dict)
    total_loc = 0
    total_chars = 0
    ext_counts: Dict[str, int] = {}
    external_deps: Set[str] = set()
    internal_modules: Set[str] = set()

    for path, content in files_dict.items():
        ext = os.path.splitext(path)[1].lower() or "no_ext"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        lines = content.splitlines()
        total_loc += len(lines)
        total_chars += len(content)

        # Track internal Python module names
        base_name = os.path.splitext(os.path.basename(path))[0]
        internal_modules.add(base_name)

        if ext == ".py":
            file_imports = extract_python_imports(content)
            external_deps.update(file_imports)

    # Separate standard/third-party dependencies from internal modules
    third_party_deps = sorted(list(external_deps - internal_modules))

    # Detect candidate entry points
    entry_points = []
    for path, content in files_dict.items():
        if "if __name__ == '__main__':" in content or 'if __name__ == "__main__":' in content:
            entry_points.append(path)
        elif path.lower() in ("app.py", "main.py", "index.js", "server.js", "manage.py"):
            if path not in entry_points:
                entry_points.append(path)

    return {
        "total_files": total_files,
        "total_loc": total_loc,
        "total_chars": total_chars,
        "language_distribution": ext_counts,
        "entry_points": entry_points,
        "detected_dependencies": third_party_deps[:20],
        "file_list": sorted(list(files_dict.keys())),
    }
