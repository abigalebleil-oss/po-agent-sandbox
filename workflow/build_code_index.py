"""Build a deterministic index of the codebase for the AI to be grounded on. No AI involved.

Walks sandbox_codebase/labbridge with Python's own parser (ast) and records every module,
function, class and method, with the first line of its docstring.

Output: workflow/code_index.json

Why: the impact-analysis skill may only cite code listed here, and verify_citations.py
checks every citation against this same file. Same code in, same index out, every time.
"""

import ast
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = REPO_ROOT / "sandbox_codebase" / "labbridge"
OUTPUT = REPO_ROOT / "workflow" / "code_index.json"


def first_line(doc):
    return doc.strip().splitlines()[0] if doc else ""


def index_file(path):
    tree = ast.parse(path.read_text(), filename=str(path))
    symbols = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols[node.name] = {"kind": "function", "line": node.lineno,
                                  "doc": first_line(ast.get_docstring(node))}
        elif isinstance(node, ast.ClassDef):
            symbols[node.name] = {"kind": "class", "line": node.lineno,
                                  "doc": first_line(ast.get_docstring(node))}
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols[f"{node.name}.{item.name}"] = {
                        "kind": "method", "line": item.lineno,
                        "doc": first_line(ast.get_docstring(item))}
    return {"module_doc": first_line(ast.get_docstring(tree)), "symbols": symbols}


def build_index():
    files = {}
    for path in sorted(CODE_DIR.glob("*.py")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        files[rel] = index_file(path)
    return {"generated_from": CODE_DIR.relative_to(REPO_ROOT).as_posix(), "files": files}


def main():
    index = build_index()
    OUTPUT.write_text(json.dumps(index, indent=2) + "\n")
    n_symbols = sum(len(f["symbols"]) for f in index["files"].values())
    print(f"Indexed {len(index['files'])} files, {n_symbols} symbols -> "
          f"{OUTPUT.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
