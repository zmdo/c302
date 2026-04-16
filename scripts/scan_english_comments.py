"""Scan for English-only comments outside SP-CODE header blocks."""
import re
import pathlib
import collections

src_dir = pathlib.Path("project/c302")
py_files = sorted(f for f in src_dir.glob("*.py") if f.name != "__version__.py")

eng_pattern = re.compile(r"#\s*[A-Za-z].*$")
cjk_range = re.compile(r"[\u4e00-\u9fff]")

results = collections.defaultdict(list)
for f in py_files:
    lines = f.read_text(encoding="utf-8").splitlines()
    in_header = False
    in_docstring = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Track SP-CODE header block (between === lines)
        if stripped.startswith("# ===="):
            in_header = not in_header
            continue
        if in_header:
            continue
        # Skip docstrings (rough)
        if '"""' in stripped or "'''" in stripped:
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        # Find inline comments
        m = eng_pattern.search(line)
        if m:
            comment = m.group().strip()
            if cjk_range.search(comment):
                continue
            # Skip shebang, encoding, type: ignore, noqa
            if comment.startswith("#!") or "coding" in comment:
                continue
            if "type:" in comment or "noqa" in comment:
                continue
            results[f.name].append((i, comment[:80]))

total = sum(len(v) for v in results.values())
print(f"Total English comments outside headers: {total}")
print()
for fname, items in sorted(results.items()):
    print(f"{fname}: {len(items)} items")
    for line_no, text in items[:5]:
        print(f"  L{line_no}: {text}")
    if len(items) > 5:
        print(f"  ... and {len(items)-5} more")
