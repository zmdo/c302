"""Phase 3 B-class annotation for parameters_C2.py.
Adds [备选] labels before each group of consecutive commented-out code lines.
"""
import re

path = 'project/c302/parameters_C2.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Determine which line indices are inside triple-quoted strings
def get_triple_quote_lines(lines):
    inside = False
    result = set()
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        count = stripped.count('"""')
        if inside:
            result.add(i)
        if count % 2 == 1:
            inside = not inside
            if inside:
                result.add(i)  # opening line also counts
    return result

triple_lines = get_triple_quote_lines(lines)

# Debug: show triple-quote status around expected B-class lines
for suspect in [153, 154, 161, 162, 163, 164]:
    print(f'  L{suspect+1} in triple_lines: {suspect in triple_lines} | content: {lines[suspect].rstrip()[:60] if suspect < len(lines) else "OOB"}')

# Identify real B-class lines (not in triple-quote blocks)
BCLASS_PAT = re.compile(r'^\s+#\s*(self\.add_bioparameter|motors\s*=|neuron_to_neuron_\w+_unit\s*=)')

b_indices = []
for i, line in enumerate(lines):
    if i not in triple_lines and BCLASS_PAT.match(line):
        b_indices.append(i)

print(f"Real B-class lines found: {len(b_indices)}")

# Group consecutive indices (within 1 line gap to allow for blank lines)
groups = []
if b_indices:
    group = [b_indices[0]]
    for idx in b_indices[1:]:
        if idx <= group[-1] + 2:  # consecutive or 1-blank-line gap
            group.append(idx)
        else:
            groups.append(group)
            group = [idx]
    groups.append(group)

print(f"Groups: {len(groups)}")
for g in groups:
    print(f"  Group lines L{g[0]+1}-L{g[-1]+1}: {lines[g[0]].rstrip()[:60]}")

# Get indentation prefix from first line of each group
LABEL = '# [备选] 以下为该参数（组）的备选值，可取消注释以替换当前设定\n'

# Build new file: insert label before the first line of each group
group_starts = {g[0] for g in groups}
new_lines = []
for i, line in enumerate(lines):
    if i in group_starts:
        # Get indentation
        indent = re.match(r'^(\s*)', line).group(1)
        # Only insert if previous non-blank line isn't already a [备选] label
        prev_code = ''.join(new_lines[-3:]).strip()
        if '[备选]' not in prev_code:
            new_lines.append(indent + LABEL)
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

added = len(new_lines) - len(lines)
print(f"Inserted {added} [备选] label lines into {path}")
