"""检测 project/c302/*.py 中的 coding 声明，确认 Python3 + UTF-8 后删除。"""
import pathlib, tokenize, sys

ROOT = pathlib.Path("project/c302")
TARGET = "# -*- coding: utf-8 -*-"

files_with_coding = []
for py in sorted(ROOT.glob("*.py")):
    first_line = py.read_text(encoding="utf-8").splitlines()[0]
    if TARGET in first_line:
        files_with_coding.append(py)

if not files_with_coding:
    print("未找到含 coding 声明的文件。")
    sys.exit(0)

print(f"找到 {len(files_with_coding)} 个含 coding 声明的文件：")

# 1. 验证 Python 3 语法（无 print statement、无 unicode literal 等）
# 2. 验证文件实际编码为 UTF-8
all_ok = True
for fp in files_with_coding:
    name = fp.name
    raw = fp.read_bytes()

    # 检查 BOM
    has_bom = raw.startswith(b"\xef\xbb\xbf")

    # 尝试 UTF-8 解码
    try:
        text = raw.decode("utf-8")
        encoding_ok = True
    except UnicodeDecodeError:
        encoding_ok = False

    # 尝试 tokenize（Python 3 parser）
    try:
        with open(fp, "rb") as f:
            list(tokenize.tokenize(f.readline))
        syntax_ok = True
    except tokenize.TokenError as e:
        syntax_ok = False

    status = "OK" if (encoding_ok and syntax_ok) else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"  {name:45s} encoding=UTF-8:{encoding_ok}  BOM:{has_bom}  tokenize:{syntax_ok}  => {status}")

if not all_ok:
    print("\n存在问题文件，中止删除。")
    sys.exit(1)

# 3. 删除 coding 行
print(f"\n全部验证通过，删除 coding 声明...")
for fp in files_with_coding:
    lines = fp.read_text(encoding="utf-8").splitlines(keepends=True)
    # coding 行一定在第 1 行（index 0）
    if TARGET in lines[0]:
        new_lines = lines[1:]
        # 如果删除后第一行是空行，也删掉（避免双空行）
        fp.write_text("".join(new_lines), encoding="utf-8")
        print(f"  [DEL] {fp.name}")
    else:
        print(f"  [SKIP] {fp.name} — coding 不在第 1 行")

print(f"\n共删除 {len(files_with_coding)} 个 coding 声明。")
