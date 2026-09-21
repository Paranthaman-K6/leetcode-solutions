#!/usr/bin/env python3
import html
import json
import re
import subprocess
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
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
    ".sh": "Bash",
    ".dart": "Dart",
    ".ex": "Elixir",
    ".erl": "Erlang",
    ".rkt": "Racket",
}

EXCLUDED_DIRS = {
    ".git",
    ".github",
    "scripts",
    "__pycache__",
    "node_modules",
}

DIFFICULTY_ORDER = {
    "Easy": 0,
    "Medium": 1,
    "Hard": 2,
    "Unknown": 3,
}

PERFORMANCE_RE = re.compile(
    r"Runtime\s*-\s*(?P<runtime>.+?)"
    r"(?:\s+\((?P<runtime_percentile>[^)]+)\))?"
    r",\s*Memory\s*-\s*(?P<memory>.+?)"
    r"(?:\s+\((?P<memory_percentile>[^)]+)\))?$",
    re.IGNORECASE,
)


def solution_files():
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.name in {"README.md", "LICENSE"}:
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in EXTENSIONS:
            continue
        if not (path.parent / "README.md").is_file():
            continue
        files.append(path)
    return sorted(files, key=lambda p: str(p).lower())


def problem_slug(folder_name):
    return re.sub(r"^\d+-", "", folder_name)


def problem_number(folder_name):
    match = re.match(r"^(\d+)-", folder_name)
    return int(match.group(1)) if match else None


def clean_problem_title(folder):
    problem_readme = folder / "README.md"

    try:
        content = problem_readme.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        content = ""

    match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE | re.DOTALL)
    if match:
        title = re.sub(r"<[^>]+>", "", match.group(1))
        title = html.unescape(title).strip()
        title = re.sub(r"^\s*\d+\s*[.:\-]\s*", "", title)
        if title:
            return title

    slug = problem_slug(folder.name)
    title = slug.replace("-", " ").replace("_", " ")
    return " ".join(word.capitalize() for word in title.split())


def get_git_performance(folder):
    relative_folder = folder.relative_to(ROOT).as_posix()

    try:
        result = subprocess.run(
            ["git", "log", "-n", "20", "--format=%s", "--", relative_folder],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return {
            "runtime": "—",
            "runtime_percentile": "",
            "memory": "—",
            "memory_percentile": "",
        }

    for subject in result.stdout.splitlines():
        match = PERFORMANCE_RE.search(subject.strip())
        if match:
            return {
                "runtime": match.group("runtime").strip(),
                "runtime_percentile": (match.group("runtime_percentile") or "").strip(),
                "memory": match.group("memory").strip(),
                "memory_percentile": (match.group("memory_percentile") or "").strip(),
            }

    return {
        "runtime": "—",
        "runtime_percentile": "",
        "memory": "—",
        "memory_percentile": "",
    }


def fetch_difficulties(slugs):
    session = (Path("/dev/null") if False else None)
    leetcode_session = __import__("os").environ.get("LEETCODE_SESSION", "").strip()
    csrf_token = __import__("os").environ.get("LEETCODE_CSRF_TOKEN", "").strip()

    if not leetcode_session or not csrf_token or not slugs:
        return {}

    results = {}

    for start in range(0, len(slugs), 20):
        chunk = slugs[start : start + 20]
        fields = []
        for index, slug in enumerate(chunk):
            fields.append(
                f"q{index}: question(titleSlug: {json.dumps(slug)}) {{ difficulty }}"
            )

        payload = json.dumps({
            "query": "query { " + " ".join(fields) + " }"
        }).encode("utf-8")

        request = urllib.request.Request(
            "https://leetcode.com/graphql/",
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Origin": "https://leetcode.com",
                "Referer": "https://leetcode.com/",
                "User-Agent": "Mozilla/5.0",
                "Cookie": (
                    f"csrftoken={csrf_token}; "
                    f"LEETCODE_SESSION={leetcode_session};"
                ),
                "x-csrftoken": csrf_token,
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))

            data = body.get("data", {})
            for index, slug in enumerate(chunk):
                item = data.get(f"q{index}") or {}
                difficulty = item.get("difficulty")
                results[slug] = difficulty if difficulty in DIFFICULTY_ORDER else "Unknown"

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
            print("Warning: could not fetch LeetCode difficulty metadata.")
            for slug in chunk:
                results.setdefault(slug, "Unknown")

    return results


def format_metric(value, percentile):
    if value == "—":
        return "—"
    if percentile:
        return f"{value} ({percentile})"
    return value


def main():
    files = solution_files()

    problems = {}
    for path in files:
        folder = path.parent
        key = folder.relative_to(ROOT).as_posix()

        if key not in problems:
            problems[key] = {
                "folder": folder,
                "number": problem_number(folder.name),
                "slug": problem_slug(folder.name),
                "title": clean_problem_title(folder),
                "performance": get_git_performance(folder),
                "solutions": [],
            }

        problems[key]["solutions"].append(path)

    slugs = sorted({problem["slug"] for problem in problems.values()})
    difficulties = fetch_difficulties(slugs)

    for problem in problems.values():
        problem["difficulty"] = difficulties.get(problem["slug"], "Unknown")

    problem_list = sorted(
        problems.values(),
        key=lambda p: (
            DIFFICULTY_ORDER.get(p["difficulty"], 3),
            p["number"] if p["number"] is not None else 10**9,
            p["title"].lower(),
        ),
    )

    solution_count = len(files)
    problem_count = len(problem_list)
    language_counts = Counter(EXTENSIONS[path.suffix.lower()] for path in files)
    difficulty_counts = Counter(problem["difficulty"] for problem in problem_list)

    lines = [
        "# LeetCode Solutions",
        "",
        "[![LeetCode](https://img.shields.io/badge/LeetCode-Solutions-orange?logo=leetcode)](https://leetcode.com/)",
        "[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/Paranthaman-K6/leetcode-solutions)",
        "",
        "> A personal collection of accepted LeetCode solutions, automatically synchronized to GitHub.",
        "",
        "## Progress",
        "",
        "| Problems | Solutions | Languages | Easy | Medium | Hard |",
        "|---:|---:|---:|---:|---:|---:|",
        f"| {problem_count} | {solution_count} | {len(language_counts)} | {difficulty_counts.get('Easy', 0)} | {difficulty_counts.get('Medium', 0)} | {difficulty_counts.get('Hard', 0)} |",
        "",
        "### Languages",
        "",
        "| Language | Solutions |",
        "|---|---:|",
    ]

    for language, count in sorted(language_counts.items()):
        lines.append(f"| {language} | {count} |")

    lines += ["", "## Solutions", ""]

    for difficulty in ("Easy", "Medium", "Hard", "Unknown"):
        items = [p for p in problem_list if p["difficulty"] == difficulty]
        if not items:
            continue

        heading = difficulty if difficulty != "Unknown" else "Other"
        lines += [
            f"### {heading}",
            "",
            "| # | Problem | Language | Time | Memory | Solution |",
            "|---:|---|---|---|---|---|",
        ]

        for problem in items:
            folder = problem["folder"]
            performance = problem["performance"]
            for path in sorted(problem["solutions"], key=lambda p: str(p).lower()):
                language = EXTENSIONS[path.suffix.lower()]
                relative_solution = quote(
                    path.relative_to(ROOT).as_posix(),
                    safe="/",
                )
                number = problem["number"] if problem["number"] is not None else "—"
                runtime = format_metric(
                    performance["runtime"],
                    performance["runtime_percentile"],
                )
                memory = format_metric(
                    performance["memory"],
                    performance["memory_percentile"],
                )
                problem_link = (
                    f"[{problem['title']}]"
                    f"(https://leetcode.com/problems/{quote(problem['slug'])}/)"
                )
                solution_link = f"[View]({relative_solution})"

                lines.append(
                    f"| {number} | {problem_link} | {language} | {runtime} | {memory} | {solution_link} |"
                )

        lines.append("")

    lines += [
        "## Performance",
        "",
        "Time and memory values are the metrics reported by LeetCode for the accepted submission.",
        "When available, the values in parentheses are the corresponding LeetCode percentiles.",
        "",
        "This table describes observed execution performance; Big-O time and space complexity are not automatically inferred.",
        "",
        "## Automation",
        "",
        "New accepted submissions are synchronized using "
        "[LeetCode Sync](https://github.com/joshcai/leetcode-sync) through GitHub Actions.",
        "The root README is regenerated automatically after each synchronization run.",
        "",
        "---",
        "",
        "Maintained as a learning record of algorithm and data-structure practice.",
        "",
    ]

    README.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
