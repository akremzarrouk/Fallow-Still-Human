#!/usr/bin/env python
"""Merges every Markdown file of one slice into a single document.

Usage: python merge-slice-docs.py S1.5

Writes Docs/slices/<slice>/<slice>-all.md. The separate files are left as they are.
The report (or review) comes first, then the files in the order the work produced
them, then anything else alphabetically. Each file's headings are moved down two
levels, outside code blocks, so they sit under that file's section.
"""
import re
import sys
from pathlib import Path

ORDER = [
    "report.md",
    "review.md",
    "diagnosis.md",
    "diagnosis-before.md",
    "held-out-predictions.md",
    "experiment-results.md",
    "held-out-results.md",
    "attribution.md",
    "diagnosis-after.md",
    "diagnosis-current.md",
]


def slug(text):
    s = text.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def demote(markdown):
    out, fence = [], None
    for line in markdown.splitlines():
        stripped = line.lstrip()
        match = re.match(r"(`{3,}|~{3,})", stripped)
        if match:
            if fence is None:
                fence = match.group(1)[0]
            elif stripped.startswith(fence * 3):
                fence = None
            out.append(line)
            continue
        if fence is None and re.match(r"#{1,6} ", line):
            hashes = len(line) - len(line.lstrip("#"))
            line = "#" * min(6, hashes + 2) + line[hashes:]
        out.append(line)
    return "\n".join(out)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    name = sys.argv[1]
    root = Path(__file__).resolve().parent / "Docs" / "slices" / name
    if not root.is_dir():
        print("no such slice folder: " + str(root))
        return 2

    output = root / (name + "-all.md")
    files = [p for p in root.rglob("*.md") if p != output and not p.name.endswith("-all.md")]

    def rank(p):
        rel = p.relative_to(root)
        top = len(rel.parts) == 1
        index = ORDER.index(p.name) if top and p.name in ORDER else len(ORDER)
        return (0 if top else 1, index, str(rel).lower())

    files.sort(key=rank)

    parts = [
        "# " + name + ": all documents",
        "",
        "Merged by `merge-slice-docs.py` from the " + str(len(files)) + " Markdown files in `Docs/slices/" + name + "/`, "
        "which remain the sources. Regenerate this file whenever they change.",
        "",
        "## Contents",
        "",
    ]
    for p in files:
        rel = p.relative_to(root).as_posix()
        parts.append("- [`" + rel + "`](#" + slug(rel) + ")")
    parts.append("")

    seen = {}
    for p in files:
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
        parts.append("---")
        parts.append("")
        parts.append("## " + rel)
        parts.append("")
        if text in seen:
            parts.append("*Identical, at the time of merging, to `" + seen[text] + "`.*")
            parts.append("")
        else:
            seen[text] = rel
        parts.append(demote(text))
        parts.append("")

    output.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
    print("wrote " + str(output) + " from " + str(len(files)) + " files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
