#!/usr/bin/env python3
"""Generate README.md and assets/progress.svg for this repository.

Both files are generated artifacts: `.github/workflows/sync_leetcode.yml` runs
this script after each LeetCode sync and commits the result. Edit this file,
not the generated files.

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
from collections import Counter
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
BANNER = ROOT / "assets" / "banner.svg"
PROGRESS = ROOT / "assets" / "progress.svg"

REPOSITORY_URL = "https://github.com/Paranthaman-K6/leetcode-solutions"
LEETCODE_URL = "https://leetcode.com"
CARBON_BLACK = "111111"
GRAPHITE = "2D2D2D"
ASH_GRAY = "9E9E9E"

LEETCODE_USERNAME = os.environ.get("LEETCODE_USERNAME", "").strip() or "paranthamank"
LEETCODE_PROFILE_URL = f"{LEETCODE_URL}/u/{LEETCODE_USERNAME}/"

BANNER_IMG = "assets/banner.svg"
PROGRESS_IMG = "assets/progress.svg"

DIFFICULTY_COLORS = {
    "Easy": ("#ffffff", "#ffffff"),
    "Medium": ("#bdbdbd", "#bdbdbd"),
    "Hard": ("#8a8a8a", "#8a8a8a"),
}


def load_complexity():
    """Curated approach + Big-O data. Tolerates a missing file (renders "—")."""
    try:
        return json.loads((ROOT / "data" / "problems.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


COMPLEXITY = load_complexity()


def complexity_for(folder_name, ext):
    entry = (COMPLEXITY.get(folder_name) or {}).get(ext.lstrip(".").lower(), {})
    approach = str(entry.get("approach", "") or "").replace("|", ";").strip()
    time_o = str(entry.get("time", "") or "").strip()
    space_o = str(entry.get("space", "") or "").strip()
    return approach, time_o, space_o


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
    """Readable fallback title when the LeetCode API is unavailable."""
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

    minor_words = {"a", "an", "and", "for", "from", "in", "of", "the", "to"}
    words = problem_slug(folder.name).replace("_", " ").split()
    title_words = []
    for index, word in enumerate(words):
        lowered = word.lower()
        if index and lowered in minor_words:
            title_words.append(lowered)
        else:
            title_words.append(lowered.capitalize())
    return " ".join(title_words)


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


def fetch_metadata(slugs):
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
            f"q{index}: question(titleSlug: {json.dumps(slug)}) {{ title difficulty }}"
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

            data = body.get("data") or {}
            for index, slug in enumerate(chunk):
                item = data.get(f"q{index}") or {}
                difficulty = item.get("difficulty")
                results[slug] = {
                    "title": html.unescape(str(item.get("title") or "")).strip(),
                    "difficulty": (
                        difficulty if difficulty in DIFFICULTY_ORDER else "Unknown"
                    ),
                }

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
            print("Warning: could not fetch LeetCode question metadata.")
            for slug in chunk:
                results.setdefault(slug, {"title": "", "difficulty": "Unknown"})

    return results


# --------------------------------------------------------------------------- #
# Rendering helpers
# --------------------------------------------------------------------------- #


def shield(label, message, logo=None, color=GRAPHITE, logo_color=ASH_GRAY):
    """A shields.io badge in the Carbon palette."""
    label_part = quote(str(label).upper().replace("-", "--"), safe="")
    message_part = quote(str(message).replace("-", "--").replace("_", "__"), safe="")
    params = ["style=for-the-badge", f"labelColor={CARBON_BLACK}"]
    if logo:
        params += [f"logo={logo}", f"logoColor={logo_color}"]
    query = "&".join(params)
    return f"https://img.shields.io/badge/{label_part}-{message_part}-{color}?{query}"


def img(source, alt, width=None):
    size = f' width="{width}"' if width else ""
    return f'<img src="{source}" alt="{html.escape(alt, quote=True)}"{size} />'


def center(lines):
    body = "\n".join(f"  {line}" if line else "" for line in lines)
    return f'<div align="center">\n{body}\n</div>'


def pretty_big_o(value):
    return value.replace("^2", "²").replace("^3", "³")


def format_approach(approach):
    return html.escape(approach).replace(", ", " · ")


def format_metric(value, percentile):
    if value in {"", "—"}:
        return "—"
    value = value.replace("|", "\\|")
    percentile = percentile.replace("|", "\\|")
    return f"{value} <sub>{percentile}</sub>" if percentile else value


def progress_svg(problem_count, solution_count, language_counts, difficulty_counts):
    total = max(problem_count, 1)
    rows = []

    for index, difficulty in enumerate(("Easy", "Medium", "Hard")):
        count = difficulty_counts.get(difficulty, 0)
        percentage = round(count * 100 / total) if problem_count else 0
        bar_y = 94 + index * 56
        width = max(10, round(count / total * 812)) if count else 0
        base, light = DIFFICULTY_COLORS[difficulty]

        rows.append(
            f'    <circle cx="62" cy="{bar_y + 6}" r="4" fill="{base}"/>\n'
            f'    <text x="80" y="{bar_y + 11}" class="sans" font-size="15" '
            f'font-weight="600" fill="#f2f2f2">{difficulty}</text>\n'
            f'    <text x="210" y="{bar_y + 11}" text-anchor="end" class="terminal" '
            f'font-size="15" fill="#e6e6e6">{count}</text>\n'
            f'    <rect x="240" y="{bar_y}" width="812" height="12" rx="6" fill="#2d2d2d"/>\n'
            f'    <rect class="bar d{index + 1}" x="240" y="{bar_y}" width="{width}" '
            f'height="12" rx="6" fill="url(#g-{difficulty.lower()})"/>\n'
            f'    <text x="1144" y="{bar_y + 11}" text-anchor="end" class="terminal" '
            f'font-size="14" font-weight="700" fill="{light}">{percentage}%</text>'
        )

    language_parts = []
    language_x = 154
    for language, count in sorted(language_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        label = f"{language} · {count}"
        color = "#9e9e9e" if language == "Java" else "#ffffff"
        language_parts.append(
            f'    <circle cx="{language_x}" cy="251" r="3" fill="{color}"/>\n'
            f'    <text x="{language_x + 10}" y="255" class="terminal" font-size="11" '
            f'fill="#bdbdbd">{html.escape(label)}</text>'
        )
        language_x += 28 + round(len(label) * 6.6)

    alt = (
        f"Progress: {difficulty_counts.get('Easy', 0)} easy, "
        f"{difficulty_counts.get('Medium', 0)} medium, "
        f"{difficulty_counts.get('Hard', 0)} hard; "
        f"{problem_count} problems, {solution_count} solutions, "
        f"{len(language_counts)} languages."
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 280" width="1200" height="280" role="img" aria-label="{html.escape(alt, quote=True)}">
  <title>Progress</title>
  <desc>{html.escape(alt)}</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#151515"/>
      <stop offset=".55" stop-color="#0b0b0b"/>
      <stop offset="1" stop-color="#101010"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff" stop-opacity=".5"/>
      <stop offset=".55" stop-color="#2d2d2d" stop-opacity=".55"/>
      <stop offset="1" stop-color="#2d2d2d" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="g-easy" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#d6d6d6"/>
    </linearGradient>
    <linearGradient id="g-medium" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#bdbdbd"/>
      <stop offset="1" stop-color="#8a8a8a"/>
    </linearGradient>
    <linearGradient id="g-hard" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#8a8a8a"/>
      <stop offset="1" stop-color="#5a5a5a"/>
    </linearGradient>
    <radialGradient id="glow" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="#ffffff" stop-opacity=".07"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
    <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="1" fill="#ffffff" opacity=".05"/>
    </pattern>
    <style>
      .terminal {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; }}
      .sans {{ font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; }}
      .bar {{
        transform-box: fill-box;
        transform-origin: left center;
        animation: grow .9s cubic-bezier(.2, .8, .2, 1) both;
      }}
      .d1 {{ animation-delay: .2s; }}
      .d2 {{ animation-delay: .35s; }}
      .d3 {{ animation-delay: .5s; }}
      @keyframes grow {{ from {{ transform: scaleX(0); }} }}
      @media (prefers-reduced-motion: reduce) {{ .bar {{ animation: none; }} }}
    </style>
  </defs>

  <rect x="1" y="1" width="1198" height="278" rx="22" fill="url(#bg)" stroke="#2d2d2d"/>
  <rect x="1" y="1" width="1198" height="278" rx="22" fill="url(#dots)"/>
  <ellipse cx="1090" cy="0" rx="300" ry="190" fill="url(#glow)"/>
  <rect x="1" y="1" width="1198" height="3" rx="1.5" fill="url(#edge)"/>

  <text x="56" y="54" class="terminal" font-size="11" fill="#9e9e9e" letter-spacing="2">SOLVED BY DIFFICULTY</text>
  <text x="1144" y="54" text-anchor="end" class="terminal" font-size="11" fill="#6e6e6e">{problem_count} PROBLEMS · {solution_count} SOLUTIONS</text>

{chr(10).join(rows)}

  <line x1="56" y1="236" x2="1144" y2="236" stroke="#2d2d2d"/>
  <text x="56" y="255" class="terminal" font-size="10" fill="#9e9e9e" letter-spacing="1.6">LANGUAGES</text>
{chr(10).join(language_parts)}
  <text x="1144" y="255" text-anchor="end" class="terminal" font-size="11" fill="#6e6e6e">solve · understand · improve</text>
</svg>
'''


def language_phrase(language_counts):
    names = sorted(language_counts)
    if not names:
        return "multiple languages"
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def banner_svg(language_counts):
    """The hero banner. Pills are derived from the languages actually in the repo."""
    alt = f"LeetCode Solutions — accepted solutions in {language_phrase(language_counts)}"

    pills = []
    if language_counts:
        gap = 12
        labels = [
            f"{language} · {count}"
            for language, count in sorted(
                language_counts.items(), key=lambda kv: (-kv[1], kv[0])
            )
        ]
        widths = [max(54, round(len(label) * 8.0) + 36) for label in labels]
        total_width = sum(widths) + gap * (len(labels) - 1)
        x = 600 - total_width / 2

        for label, width in zip(labels, widths):
            pills.append(
                f'    <rect x="{x:.1f}" y="184" width="{width}" height="34" rx="17" '
                f'fill="#181818" stroke="#2d2d2d"/>\n'
                f'    <text x="{x + width / 2:.1f}" y="206" text-anchor="middle" '
                f'class="terminal" font-size="13" fill="#e6e6e6">'
                f"{html.escape(label)}</text>"
            )
            x += width + gap

    pill_group = (
        "  <g>\n" + "\n".join(pills) + "\n  </g>" if pills else ""
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 270" width="1200" height="270" role="img" aria-label="{html.escape(alt, quote=True)}">
  <title>LeetCode Solutions</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#151515"/>
      <stop offset=".55" stop-color="#0b0b0b"/>
      <stop offset="1" stop-color="#101010"/>
    </linearGradient>
    <linearGradient id="brand" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#9e9e9e"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#2d2d2d" stop-opacity="0"/>
      <stop offset=".5" stop-color="#ffffff" stop-opacity=".55"/>
      <stop offset="1" stop-color="#2d2d2d" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glow-white" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="#ffffff" stop-opacity=".08"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow-gray" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="#9e9e9e" stop-opacity=".07"/>
      <stop offset="1" stop-color="#9e9e9e" stop-opacity="0"/>
    </radialGradient>
    <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="1" fill="#ffffff" opacity=".05"/>
    </pattern>
    <style>
      .terminal {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; }}
      .sans {{ font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; }}
      .pulse {{ animation: pulse 6s ease-in-out infinite alternate; }}
      @keyframes pulse {{ from {{ opacity: .55; }} to {{ opacity: 1; }} }}
      @media (prefers-reduced-motion: reduce) {{ .pulse {{ animation: none; opacity: 1; }} }}
    </style>
  </defs>

  <rect x="1" y="1" width="1198" height="268" rx="24" fill="url(#bg)" stroke="#2d2d2d"/>
  <rect x="1" y="1" width="1198" height="268" rx="24" fill="url(#dots)"/>
  <ellipse cx="600" cy="-30" rx="460" ry="190" fill="url(#glow-white)" class="pulse"/>
  <ellipse cx="140" cy="280" rx="260" ry="140" fill="url(#glow-gray)"/>
  <rect x="1" y="1" width="1198" height="3" rx="1.5" fill="url(#edge)"/>

  <g>
    <rect x="578" y="30" width="44" height="44" rx="13" fill="url(#brand)"/>
    <text x="600" y="59" text-anchor="middle" class="terminal" font-size="18" font-weight="700" fill="#111111">&lt;/&gt;</text>
  </g>

  <text x="600" y="152" text-anchor="middle" class="sans" font-size="64" font-weight="800" letter-spacing="-2" fill="#ffffff">LeetCode <tspan fill="#9e9e9e">Solutions</tspan></text>

{pill_group}
</svg>
'''


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
    metadata = fetch_metadata(slugs)

    for problem in problems.values():
        item = metadata.get(problem["slug"]) or {}
        if item.get("title"):
            problem["title"] = item["title"]
        problem["difficulty"] = item.get("difficulty", "Unknown")

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

    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    BANNER.write_text(banner_svg(language_counts), encoding="utf-8")
    PROGRESS.write_text(
        progress_svg(
            problem_count,
            solution_count,
            language_counts,
            difficulty_counts,
        ),
        encoding="utf-8",
    )

    nav_links = []
    for difficulty in ("Easy", "Medium", "Hard", "Unknown"):
        if not difficulty_counts.get(difficulty):
            continue
        label = difficulty if difficulty != "Unknown" else "More"
        anchor = "more" if difficulty == "Unknown" else difficulty.lower()
        nav_links.append(f'<a href="#{anchor}">{label}</a>')
    nav_links.append(f'<a href="{LEETCODE_PROFILE_URL}">LeetCode profile</a>')

    progress_alt = (
        f"Progress: {difficulty_counts.get('Easy', 0)} easy, "
        f"{difficulty_counts.get('Medium', 0)} medium, "
        f"{difficulty_counts.get('Hard', 0)} hard"
    )

    lines = [
        center([
            img(
                BANNER_IMG,
                f"LeetCode Solutions — accepted solutions in {language_phrase(language_counts)}",
                width="100%",
            ),
            "<br /><br />",
            " ".join([
                img(
                    shield("Problems", problem_count, logo="leetcode", logo_color=ASH_GRAY),
                    f"Problems: {problem_count}",
                ),
                img(
                    shield("Solutions", solution_count, logo="github"),
                    f"Solutions: {solution_count}",
                ),
                img(
                    shield("Languages", len(language_counts)),
                    f"Languages: {len(language_counts)}",
                ),
            ]),
            "<br /><br />",
            " · ".join(nav_links),
        ]),
        "",
        "## Progress",
        "",
        center([img(PROGRESS_IMG, progress_alt, width="100%")]),
        "",
        "## Solutions",
        "",
    ]

    for difficulty in ("Easy", "Medium", "Hard", "Unknown"):
        items = [p for p in problem_list if p["difficulty"] == difficulty]
        if not items:
            continue

        heading = difficulty if difficulty != "Unknown" else "More"
        anchor = "more" if difficulty == "Unknown" else difficulty.lower()
        noun = "problem" if len(items) == 1 else "problems"

        lines += [
            f'<a id="{anchor}"></a>',
            f"### {heading} <sub>· {len(items)} {noun}</sub>",
            "",
            "| # | Problem | Time · Space | Runtime | Memory | Code |",
            "|---:|---|---|---|---|---|",
        ]

        for problem in items:
            number = problem["number"] if problem["number"] is not None else "—"
            title = html.escape(problem["title"]).replace("|", "\\|")
            link = f"{LEETCODE_URL}/problems/{quote(problem['slug'], safe='')}/"

            solutions = sorted(problem["solutions"], key=lambda p: str(p).lower())
            approaches = []
            for path in solutions:
                approach, _, _ = complexity_for(problem["folder"].name, path.suffix)
                if approach and approach not in approaches:
                    approaches.append(approach)

            problem_cell = f"[{title}]({link})"
            if approaches:
                problem_cell += (
                    "<br><sub>"
                    + " · ".join(format_approach(value) for value in approaches)
                    + "</sub>"
                )

            _, time_o, space_o = complexity_for(
                problem["folder"].name, solutions[0].suffix
            )
            complexity_parts = []
            if time_o:
                complexity_parts.append(f"`{pretty_big_o(time_o)}`")
            if space_o:
                complexity_parts.append(f"`{pretty_big_o(space_o)}`")
            complexity_cell = " · ".join(complexity_parts) or "—"

            performance = problem["performance"]
            runtime_cell = format_metric(
                performance["runtime"], performance["runtime_percentile"]
            )
            memory_cell = format_metric(
                performance["memory"], performance["memory_percentile"]
            )

            code_links = []
            for path in solutions:
                language = EXTENSIONS[path.suffix.lower()]
                relative_solution = quote(path.relative_to(ROOT).as_posix(), safe="/")
                code_links.append(f"[`{language}`]({relative_solution})")

            lines.append(
                f"| {number} | {problem_cell} | {complexity_cell} | {runtime_cell} "
                f"| {memory_cell} | {' '.join(code_links)} |"
            )

        lines.append("")

    lines += [
        "---",
        "",
        center([
            " ".join([
                img(
                    shield(
                        "LeetCode",
                        LEETCODE_USERNAME,
                        logo="leetcode",
                        logo_color=CARBON_BLACK,
                        color="FFFFFF",
                    ),
                    f"LeetCode profile: {LEETCODE_USERNAME}",
                ),
                img(
                    shield(
                        "GitHub",
                        "leetcode-solutions",
                        logo="github",
                        color=GRAPHITE,
                    ),
                    "GitHub repository: leetcode-solutions",
                ),
            ]),
        ]),
        "",
    ]

    README.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
