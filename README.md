<div align="center">
  <img src="assets/banner.svg" alt="leetcode-solutions: an animated terminal banner" width="880" />

  <img src="https://img.shields.io/badge/PROBLEMS-20-2D2D2D?style=for-the-badge&labelColor=111111&logo=leetcode&logoColor=9E9E9E" alt="Problems: 20" /> <img src="https://img.shields.io/badge/SOLUTIONS-21-2D2D2D?style=for-the-badge&labelColor=111111&logo=github&logoColor=9E9E9E" alt="Solutions: 21" /> <img src="https://img.shields.io/badge/LANGUAGES-2-2D2D2D?style=for-the-badge&labelColor=111111" alt="Languages: 2" />

  <a href="https://leetcode.com/u/paranthamank/"><img src="https://leetcard.jacoblin.cool/paranthamank?theme=dark&font=DejaVu%20Sans&ext=heatmap" alt="paranthamank's LeetCode stats" width="420" /></a>

  <a href="https://github.com/Paranthaman-K6/leetcode-solutions">Repository</a> · <a href="https://leetcode.com/u/paranthamank/">LeetCode profile</a>
</div>

---

## Overview

> A continuously growing index of accepted LeetCode solutions.
>
> Each problem lives in its own folder with the original statement, one file
> per language, and the runtime and memory figures reported by LeetCode at
> submission time.

```bash
git clone https://github.com/Paranthaman-K6/leetcode-solutions.git
cd leetcode-solutions
```

## Progress

| Difficulty | Solved | Share |
|---|---:|---|
| Easy | **13** | `████████░░░░` 65% |
| Medium | **6** | `████░░░░░░░░` 30% |
| Hard | **1** | `█░░░░░░░░░░░` 5% |

### Languages

| Language | Solved | Share |
|---|---:|---|
| C | **19** | `███████████░` 90% |
| Java | **2** | `█░░░░░░░░░░░` 10% |

## Solutions

### Easy — 13 problems

| # | Problem | Lang | Time | Space | Runtime | Memory | Solution |
|---:|---|---|---|---|---|---|---|
| 1 | [Two Sum](https://leetcode.com/problems/two-sum/)<br><sub>brute force, nested loops</sub> | C | `O(n^2)` | `O(1)` | 33 ms <sub>44.58%</sub> | 47.2 MB <sub>41.16%</sub> | [C](0001-two-sum/solution.c) |
|  | ↳ [same problem](https://leetcode.com/problems/two-sum/) | Java | `O(n^2)` | `O(1)` | 33 ms <sub>44.58%</sub> | 47.2 MB <sub>41.16%</sub> | [Java](0001-two-sum/solution.java) |
| 9 | [Palindrome Number](https://leetcode.com/problems/palindrome-number/)<br><sub>reverse number, compare original</sub> | C | `O(log x)` | `O(1)` | 0 ms <sub>100.00%</sub> | 8.8 MB <sub>62.57%</sub> | [C](0009-palindrome-number/solution.c) |
| 20 | [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/)<br><sub>stack, match brackets</sub> | C | `O(n)` | `O(n)` | 0 ms <sub>100.00%</sub> | 8.7 MB <sub>67.84%</sub> | [C](0020-valid-parentheses/solution.c) |
| 21 | [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/)<br><sub>copy nodes into new list</sub> | C | `O(m+n)` | `O(m+n)` | 0 ms <sub>100.00%</sub> | 11.6 MB <sub>8.90%</sub> | [C](0021-merge-two-sorted-lists/solution.c) |
| 27 | [Remove Element](https://leetcode.com/problems/remove-element/)<br><sub>shift left on match, in place</sub> | Java | `O(n^2)` | `O(1)` | 0 ms <sub>100.00%</sub> | 43.4 MB <sub>61.13%</sub> | [Java](0027-remove-element/solution.java) |
| 58 | [Length Of Last Word](https://leetcode.com/problems/length-of-last-word/)<br><sub>scan for last word start</sub> | C | `O(n)` | `O(1)` | 0 ms <sub>100.00%</sub> | 8.9 MB <sub>16.33%</sub> | [C](0058-length-of-last-word/solution.c) |
| 66 | [Plus One](https://leetcode.com/problems/plus-one/)<br><sub>handle carry, copy array</sub> | C | `O(n)` | `O(n)` | 0 ms <sub>100.00%</sub> | 10 MB <sub>67.92%</sub> | [C](0066-plus-one/solution.c) |
| 125 | [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/)<br><sub>filter alnum, two pointer compare</sub> | C | `O(n)` | `O(n)` | 0 ms <sub>100.00%</sub> | 9.3 MB <sub>21.39%</sub> | [C](0125-valid-palindrome/solution.c) |
| 136 | [Single Number](https://leetcode.com/problems/single-number/)<br><sub>brute force, nested loops</sub> | C | `O(n^2)` | `O(1)` | 731 ms <sub>11.74%</sub> | 10.2 MB <sub>33.58%</sub> | [C](0136-single-number/solution.c) |
| 485 | [Max Consecutive Ones](https://leetcode.com/problems/max-consecutive-ones/)<br><sub>single pass, count streak</sub> | C | `O(n)` | `O(1)` | 0 ms <sub>100.00%</sub> | 13.1 MB <sub>90.02%</sub> | [C](0485-max-consecutive-ones/solution.c) |
| 1580 | [Shuffle The Array](https://leetcode.com/problems/shuffle-the-array/)<br><sub>interleave two halves in order</sub> | C | `O(n)` | `O(n)` | 12 ms <sub>72.80%</sub> | 12.2 MB <sub>92.26%</sub> | [C](1580-shuffle-the-array/solution.c) |
| 1894 | [Merge Strings Alternately](https://leetcode.com/problems/merge-strings-alternately/)<br><sub>alternate chars, append remainder</sub> | C | `O(n+m)` | `O(n+m)` | 0 ms <sub>100.00%</sub> | 8.8 MB <sub>40.76%</sub> | [C](1894-merge-strings-alternately/solution.c) |
| 2058 | [Concatenation Of Array](https://leetcode.com/problems/concatenation-of-array/)<br><sub>duplicate array via modulo</sub> | C | `O(n)` | `O(n)` | 0 ms <sub>100.00%</sub> | 15.1 MB <sub>27.39%</sub> | [C](2058-concatenation-of-array/solution.c) |

### Medium — 6 problems

| # | Problem | Lang | Time | Space | Runtime | Memory | Solution |
|---:|---|---|---|---|---|---|---|
| 2 | [Add Two Numbers](https://leetcode.com/problems/add-two-numbers/)<br><sub>iterative digit addition, new list</sub> | C | `O(n)` | `O(n)` | 0 ms <sub>100.00%</sub> | 13.3 MB <sub>83.88%</sub> | [C](0002-add-two-numbers/solution.c) |
| 3 | [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/)<br><sub>sliding start, inner duplicate scan</sub> | C | `O(n^2)` | `O(1)` | 22 ms <sub>14.46%</sub> | 9.5 MB <sub>99.49%</sub> | [C](0003-longest-substring-without-repeating-characters/solution.c) |
| 7 | [Reverse Integer](https://leetcode.com/problems/reverse-integer/)<br><sub>extract digits, check overflow</sub> | C | `O(log x)` | `O(1)` | 0 ms <sub>100.00%</sub> | 9.3 MB <sub>49.14%</sub> | [C](0007-reverse-integer/solution.c) |
| 19 | [Remove Nth Node From End Of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)<br><sub>two pass, count then delete</sub> | C | `O(n)` | `O(1)` | 0 ms <sub>100.00%</sub> | 10.2 MB <sub>81.60%</sub> | [C](0019-remove-nth-node-from-end-of-list/solution.c) |
| 61 | [Rotate List](https://leetcode.com/problems/rotate-list/)<br><sub>repeatedly move tail to head</sub> | C | `O(k*n)` | `O(1)` | 0 ms <sub>100.00%</sub> | 11.5 MB <sub>33.45%</sub> | [C](0061-rotate-list/solution.c) |
| 189 | [Rotate Array](https://leetcode.com/problems/rotate-array/)<br><sub>buffer tail, shift, restore</sub> | C | `O(n)` | `O(k)` | 0 ms <sub>100.00%</sub> | 27.4 MB <sub>76.77%</sub> | [C](0189-rotate-array/solution.c) |

### Hard — 1 problem

| # | Problem | Lang | Time | Space | Runtime | Memory | Solution |
|---:|---|---|---|---|---|---|---|
| 4 | [Median Of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/)<br><sub>merge sorted arrays, pick middle</sub> | C | `O(m+n)` | `O(m+n)` | 0 ms <sub>100.00%</sub> | 11.9 MB <sub>87.29%</sub> | [C](0004-median-of-two-sorted-arrays/solution.c) |

## Repository layout

```console
leetcode-solutions/
├── assets/
│   └── banner.svg                      # animated hero (hand-authored)
├── data/
│   └── problems.json                   # approach + Big-O notes
├── scripts/
│   └── generate_readme.py              # builds this README
├── .github/workflows/
│   └── sync_leetcode.yml               # sync + regenerate + commit
├── 0001-two-sum/
│   ├── README.md                       # problem statement
│   ├── solution.c
│   └── solution.java
├── …                                   # 19 more problem folders
└── README.md                           # generated index
```

<details>
<summary><b>How this index is built</b></summary>

`.github/workflows/sync_leetcode.yml` runs on demand and does three things:

1. syncs accepted submissions with `joshcai/leetcode-sync`;
2. runs `python scripts/generate_readme.py`;
3. commits the regenerated `README.md`.

So this page is never edited by hand. Notes on the data it reports:

- a folder is indexed only when it holds a `README.md` and at least one
  solution file, which keeps the index honest as the repository grows;
- difficulty comes from the public LeetCode GraphQL question metadata, and
  falls back to `Unknown` when the request fails;
- the time and memory figures are parsed from the sync commit messages, so
  a problem shows `—` until it has been submitted at least once;
- approach notes and Big-O figures are curated by hand in
  `data/problems.json` (keyed by folder and file extension) because neither
  the LeetCode API nor the synced files provide them — edit that file to
  correct a card, then rebuild.

To rebuild locally:

```bash
python scripts/generate_readme.py
```

</details>

---

<div align="center">
  <sub>Automatically synchronized · Automatically indexed · Built for learning</sub>
</div>
