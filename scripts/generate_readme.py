#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

EXTENSIONS = {
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".java": "Java",
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".kt": "Kotlin",
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
    ".scala": "Scala",
    ".sql": "SQL",
}

EXCLUDED_DIRS = {".git", ".github", "scripts", "__pycache__", "node_modules"}
EXCLUDED_FILES = {"README.md", "LICENSE"}

def solution_files():
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.name in EXCLUDED_FILES:
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in EXTENSIONS:
            files.append(path)
    return sorted(files, key=lambda p: str(p).lower())

def display_name(path):
    name = path.stem.replace("-", " ").replace("_", " ").strip()
    return " ".join(word.capitalize() for word in name.split())

def main():
    files = solution_files()
    grouped = defaultdict(list)

    for path in files:
        grouped[EXTENSIONS[path.suffix.lower()]].append(path)

    total = len(files)
    language_count = len(grouped)

    lines = [
        "# LeetCode Solutions",
        "",
        "[![LeetCode](https://img.shields.io/badge/LeetCode-Solutions-orange?logo=leetcode)](https://leetcode.com/)",
        "[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/Paranthaman-K6/leetcode-solutions)",
        "",
        "A personal collection of accepted LeetCode solutions, automatically synchronized to GitHub.",
        "",
        "## Progress",
        "",
        f"- **{total}** solutions",
        f"- **{language_count}** programming languages",
        "- Solutions are synchronized automatically with GitHub Actions.",
        "",
        "## Solutions",
        "",
    ]

    if not files:
        lines += ["No solutions have been synchronized yet.", ""]
    else:
        for language in sorted(grouped):
            items = grouped[language]
            lines += [f"### {language}", ""]
            for path in items:
                rel = path.relative_to(ROOT).as_posix()
                link = quote(rel, safe="/")
                lines.append(f"- [{display_name(path)}]({link})")
            lines.append("")

    lines += [
        "## Automation",
        "",
        "New accepted LeetCode submissions are synchronized using",
        "[LeetCode Sync](https://github.com/joshcai/leetcode-sync) through GitHub Actions.",
        "This README is regenerated automatically after each synchronization run.",
        "",
        "---",
        "",
        "Generated automatically from the solution files in this repository.",
    ]

    README.write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
