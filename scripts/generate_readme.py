#!/usr/bin/env python3
"""Generate the root README.md for this repository.

The README is a generated artifact: `.github/workflows/sync_leetcode.yml` runs
this script after every LeetCode sync and commits the result. Edit this file,
not README.md, or the changes will be overwritten on the next run.

Visual theme: Carbon (theme-factory), rendered entirely through image APIs
(no local assets, so there is nothing extra to commit or sync):
  Carbon Black #111111  Graphite #2D2D2D  Ash Gray #9E9E9E  Pure White #FFFFFF
  capsule-render (header/footer) + readme-typing-svg (strips) + shields.io
  (badges) + leetcard (LeetCode stats card).
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

HEADER_IMG = (
    "https://capsule-render.vercel.app/api"
    "?type=waving&height=180&section=header"
    f"&color={CARBON_BLACK}&fontColor={PURE_WHITE}"
    "&text=LeetCode%20Solutions&fontSize=38&fontAlignY=38"
    "&desc=DSA%20%7C%20Problem%20Solving%20%7C%20Continuous%20Learning&descAlignY=62"
    "&animation=twinkling"
)
FOOTER_IMG = (
    "https://capsule-render.vercel.app/api"
    "?type=waving&height=110&section=footer"
    f"&color={CARBON_BLACK}&fontColor={ASH_GRAY}"
    "&text=Keep%20Solving%20%7C%20Keep%20Learning&fontSize=24&fontAlignY=70"
    "&animation=twinkling"
)
LEETCODE_CARD_IMG = (
    f"https://leetcard.jacoblin.cool/{quote(LEETCODE_USERNAME, safe='')}"
    "?theme=dark&ext=heatmap"
)

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
    r"(?:\s+\((?P<memory_percentile>[^)]+)\))?$\n",
    re.IGNORECASE,
)
