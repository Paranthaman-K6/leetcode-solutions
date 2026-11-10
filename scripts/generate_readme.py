#!/usr/bin/env python3
"""Generate the root README.md for this repository.

The README is a generated artifact: `.github/workflows/sync_leetcode.yml` runs
this script after every LeetCode sync and commits the result. Edit this file,
not README.md, or the changes will be overwritten on the next run.

Visual theme: Carbon Terminal, matching the profile repo
(https://github.com/Paranthaman-K6/Paranthaman-K6):
  Carbon Black #111111  Graphite #2D2D2D  Ash Gray #9E9E9E  Pure White #FFFFFF
The hero banner is a hand-authored, self-contained animated SVG
(`assets/banner.svg`), so the top of the page does not depend on a third-party
image API. The rest is for-the-badge shields.io chips, a dark leetcard, and
progress bars drawn from block characters.

Per-problem approach notes and Big-O figures are curated in
`data/problems.json` (the LeetCode API does not provide them and the synced
solution files carry no annotations). Missing entries render as "—".
"""
import html
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

REPOSITORY_URL = "https://github.com/Paranthaman-K6/leetcode-solutions"
LEETCODE_URL = "https://leetcode.com"
CARBON_BLACK = "111111"
GRAPHITE = "2D2D2D"
ASH_GRAY = "9E9E9E"
PURE_WHITE = "FFFFFF"

DISPLAY_FONT = "DejaVu+Sans"
DISPLAY_FONT_BOLD = "DejaVu+Sans+Bold"

LEETCODE_USERNAME = os.environ.get("LEETCODE_USERNAME", "").strip() or "paranthamank"
LEETCODE_PROFILE_URL = f"{LEETCODE_URL}/u/{LEETCODE_USERNAME}/"

BANNER_IMG = "assets/banner.svg"
LEETCODE_CARD_IMG = (
    f"https://leetcard.jacoblin.cool/{quote(LEETCODE_USERNAME, safe='')}"
    "?theme=dark&font=DejaVu%20Sans&ext=heatmap"
)


def load_complexity():
    """Curated approach + Big-O data. Tolerates a missing file (renders "—")."""
    try:
        return json.loads((ROOT / "data" / "problems.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


COMPLEXITY = load_complexity()


def complexity_for(folder_name, ext):
    entry = (COMPLEXITY.get(folder_name) or {}).get(ext.lstrip(".").lower(), {})
    approach = str(entry.get("approach", "") or "").replace("|", ";").strip() or "—"
    time_o = str(entry.get("time", "") or "").strip() or "—"
    space_o = str(entry.get("space", "") or "").strip() or "—"
    return html.escape(approach), time_o, space_o

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


def problem_number(folder_name):
    match = re.match(r"^(\d+)-", folder_name)
    return int(match.group(1)) if match else None


def problem_slug(folder_name):
    return re.sub(r"^\d+-", "", folder_name)


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
        return empty_performance()

    for subject in result.stdout.splitlines():
        match = PERFORMANCE_RE.search(subject.strip())
        if match:
            return {
                "runtime": match.group("runtime").strip(),
                "runtime_percentile": (match.group("runtime_percentile") or "").strip(),
                "memory": match.group("memory").strip(),
                "memory_percentile": (match.group("memory_percentile") or "").strip(),
            }

    return empty_performance()


def empty_performance():
    return {
        "runtime": "—",
        "runtime_percentile": "",
        "memory": "—",
        "memory_percentile": "",
    }


def fetch_difficulties(slugs):
    session = os.environ.get("LEETCODE_SESSION", "").strip()
    csrf_token = os.environ.get("LEETCODE_CSRF_TOKEN", "").strip()

    if not slugs:
        return {}

    headers = {
        "Content-Type": "application/json",
        "Origin": "https://leetcode.com",
        "Referer": "https://leetcode.com/",
        "User-Agent": "Mozilla/5.0",
    }
    # Public question metadata needs no credentials; send the session when the
    # workflow provides one so the sync account's view is used.
    if session and csrf_token:
        headers["Cookie"] = f"csrftoken={csrf_token}; LEETCODE_SESSION={session};"
        headers["x-csrftoken"] = csrf_token

    results = {}

    for start in range(0, len(slugs), 20):
        chunk = slugs[start : start + 20]
        fields = [
            f"q{index}: question(titleSlug: {json.dumps(slug)}) {{ difficulty }}"
            for index, slug in enumerate(chunk)
        ]

        payload = json.dumps({
            "query": "query { " + " ".join(fields) + " }"
        }).encode("utf-8")

        request = urllib.request.Request(
            "https://leetcode.com/graphql/",
            data=payload,
            method="POST",
            headers=headers,
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))

            data = body.get("data", {})
            for index, slug in enumerate(chunk):
                item = data.get(f"q{index}") or {}
                difficulty = item.get("difficulty")
                results[slug] = (
                    difficulty if difficulty in DIFFICULTY_ORDER else "Unknown"
                )

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
            print("Warning: could not fetch LeetCode difficulty metadata.")
            for slug in chunk:
                results.setdefault(slug, "Unknown")

    return results


def format_metric(value, percentile):
    if value == "—":
        return "—"
    return f"{value} <sub>{percentile}</sub>" if percentile else value


# --------------------------------------------------------------------------- #
# Carbon theme helpers
# --------------------------------------------------------------------------- #


def shield(label, message, logo=None, style="for-the-badge"):
    """A shields.io badge in the Carbon palette: carbon label, graphite value."""
    label_part = quote(str(label).upper(), safe="")
    message_part = quote(str(message), safe="")
    params = [f"style={style}", f"labelColor={CARBON_BLACK}"]
    if logo:
        params += [f"logo={logo}", f"logoColor={ASH_GRAY}"]
    query = "&".join(params)
    return f"https://img.shields.io/badge/{label_part}-{message_part}-{GRAPHITE}?{query}"


def img(source, alt, width=None):
    size = f' width="{width}"' if width else ""
    return f'<img src="{source}" alt="{alt}"{size} />'


def center(lines):
    body = "\n".join(f"  {line}" if line else "" for line in lines)
    return f'<div align="center">\n{body}\n</div>'


def bar(count, total, width=12):
    """Text progress bar, so shares need no image round-trip."""
    if not total:
        return ""
    filled = round(count * width / total)
    if count and not filled:
        filled = 1
    return "█" * filled + "░" * (width - filled)


def share(count, total):
    return f"{round(count * 100 / total)}%" if total else "—"


def share_table(rows, label_header, total):
    """`| label | count | share bar |` — one row per known bucket."""
    lines = [
        f"| {label_header} | Solved | Share |",
        "|---|---:|---|",
    ]
    for label, count in rows:
        lines.append(
            f"| {label} | **{count}** | `{bar(count, total)}` {share(count, total)} |"
        )
    return lines


def layout_tree(problem_count, example_folder, example_files):
    """Repository layout, derived from what is actually on disk."""
    comment_column = 40

    def entry(prefix, name, comment):
        if not comment:
            return f"{prefix}{name}"
        padding = max(1, comment_column - len(prefix) - len(name))
        return f"{prefix}{name}{' ' * padding}# {comment}"

    lines = [
        "leetcode-solutions/",
        entry("├── ", "assets/", ""),
        entry("│   └── ", "banner.svg", "animated hero (hand-authored)"),
        entry("├── ", "data/", ""),
        entry("│   └── ", "problems.json", "approach + Big-O notes"),
        entry("├── ", "scripts/", ""),
        entry("│   └── ", "generate_readme.py", "builds this README"),
        entry("├── ", ".github/workflows/", ""),
        entry("│   └── ", "sync_leetcode.yml", "sync + regenerate + commit"),
    ]

    if example_folder:
        lines.append(entry("├── ", f"{example_folder}/", ""))
        lines.append(entry("│   ├── ", "README.md", "problem statement"))
        for index, name in enumerate(example_files):
            branch = "└── " if index == len(example_files) - 1 else "├── "
            lines.append(entry(f"│   {branch}", name, ""))

    if problem_count > 1:
        plural = "folder" if problem_count == 2 else "folders"
        lines.append(
            entry("├── ", "…", f"{problem_count - 1} more problem {plural}")
        )

    lines.append(entry("└── ", "README.md", "generated index"))
    return lines


# --------------------------------------------------------------------------- #


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

    example_folder = problem_list[0]["folder"].name if problem_list else None
    example_files = (
        [path.name for path in problem_list[0]["solutions"]] if problem_list else []
    )

    known_difficulties = [
        (difficulty, difficulty_counts[difficulty])
        for difficulty in ("Easy", "Medium", "Hard")
        if difficulty_counts.get(difficulty)
    ]

    lines = [
        center([
            img(BANNER_IMG, "leetcode-solutions: an animated terminal banner", width="880"),
            "",
            " ".join([
                img(shield("Problems", problem_count, logo="leetcode"), f"Problems: {problem_count}"),
                img(shield("Solutions", solution_count, logo="github"), f"Solutions: {solution_count}"),
                img(shield("Languages", len(language_counts)), f"Languages: {len(language_counts)}"),
            ]),
            "",
            f'<a href="{LEETCODE_PROFILE_URL}">'
            f'<img src="{LEETCODE_CARD_IMG}" alt="{LEETCODE_USERNAME}\'s LeetCode stats" width="420" />'
            "</a>",
            "",
            f'<a href="{REPOSITORY_URL}">Repository</a> · '
            f'<a href="{LEETCODE_PROFILE_URL}">LeetCode profile</a>',
        ]),
        "",
        "---",
        "",
        "## Overview",
        "",
        "> A continuously growing index of accepted LeetCode solutions.",
        ">",
        "> Each problem lives in its own folder with the original statement, one file",
        "> per language, and the runtime and memory figures reported by LeetCode at",
        "> submission time.",
        "",
        "```bash",
        f"git clone {REPOSITORY_URL}.git",
        "cd leetcode-solutions",
        "```",
        "",
        "## Progress",
        "",
    ]

    if known_difficulties:
        lines += [
            *share_table(known_difficulties, "Difficulty", problem_count),
            "",
        ]
    else:
        lines += [
            "| Problems | Solutions | Languages |",
            "|---:|---:|---:|",
            f"| **{problem_count}** | **{solution_count}** | **{len(language_counts)}** |",
            "",
        ]

    lines += [
        "### Languages",
        "",
        *share_table(
            sorted(language_counts.items(), key=lambda kv: (-kv[1], kv[0])),
            "Language",
            solution_count,
        ),
        "",
        "## Solutions",
        "",
    ]

    for difficulty in ("Easy", "Medium", "Hard", "Unknown"):
        items = [p for p in problem_list if p["difficulty"] == difficulty]
        if not items:
            continue

        heading = difficulty if difficulty != "Unknown" else "Other"
        noun = "problem" if len(items) == 1 else "problems"
        lines += [
            f"### {heading} — {len(items)} {noun}",
            "",
            "| # | Problem | Lang | Time | Space | Runtime | Memory | Solution |",
            "|---:|---|---|---|---|---|---|---|",
        ]

        for problem in items:
            number = problem["number"] if problem["number"] is not None else "—"
            title = problem["title"]
            link = f"{LEETCODE_URL}/problems/{quote(problem['slug'])}/"

            solutions = sorted(problem["solutions"], key=lambda p: str(p).lower())
            for index, path in enumerate(solutions):
                performance = problem["performance"]
                language = EXTENSIONS[path.suffix.lower()]
                relative_solution = quote(path.relative_to(ROOT).as_posix(), safe="/")
                approach, time_o, space_o = complexity_for(
                    problem["folder"].name, path.suffix
                )

                # Only the first row of a problem carries its number, title and
                # approach; extra languages continue the same block.
                if index == 0:
                    problem_cell = (
                        f"[{title}]({link})<br><sub>{approach}</sub>"
                    )
                    number_cell = number
                else:
                    problem_cell = f"↳ [same problem]({link})"
                    number_cell = ""

                runtime_cell = performance["runtime"]
                if performance["runtime_percentile"]:
                    runtime_cell += f" <sub>{performance['runtime_percentile']}</sub>"
                memory_cell = performance["memory"]
                if performance["memory_percentile"]:
                    memory_cell += f" <sub>{performance['memory_percentile']}</sub>"

                lines.append(
                    f"| {number_cell} | {problem_cell} | {language} | `{time_o}` | `{space_o}` "
                    f"| {runtime_cell} | {memory_cell} | [{language}]({relative_solution}) |"
                )

        lines.append("")

    lines += [
        "## Repository layout",
        "",
        "```console",
        *layout_tree(problem_count, example_folder, example_files),
        "```",
        "",
        "<details>",
        "<summary><b>How this index is built</b></summary>",
        "",
        "`.github/workflows/sync_leetcode.yml` runs on demand and does three things:",
        "",
        "1. syncs accepted submissions with `joshcai/leetcode-sync`;",
        "2. runs `python scripts/generate_readme.py`;",
        "3. commits the regenerated `README.md`.",
        "",
        "So this page is never edited by hand. Notes on the data it reports:",
        "",
        "- a folder is indexed only when it holds a `README.md` and at least one",
        "  solution file, which keeps the index honest as the repository grows;",
        "- difficulty comes from the public LeetCode GraphQL question metadata, and",
        "  falls back to `Unknown` when the request fails;",
        "- the time and memory figures are parsed from the sync commit messages, so",
        "  a problem shows `—` until it has been submitted at least once;",
        "- approach notes and Big-O figures are curated by hand in",
        "  `data/problems.json` (keyed by folder and file extension) because neither",
        "  the LeetCode API nor the synced files provide them — edit that file to",
        "  correct a card, then rebuild.",
        "",
        "To rebuild locally:",
        "",
        "```bash",
        "python scripts/generate_readme.py",
        "```",
        "",
        "</details>",
        "",
        "---",
        "",
        center([
            "<sub>Automatically synchronized · Automatically indexed · Built for learning</sub>",
        ]),
        "",
    ]

    README.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
