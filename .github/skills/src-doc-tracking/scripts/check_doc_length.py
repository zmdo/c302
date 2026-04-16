"""check_doc_length.py — 检测源码分析文档是否超过长度阈值。

用法：
    python check_doc_length.py <文档文件或目录> [--max-lines 300]

功能：
    - 统计文档行数
    - 超过阈值时输出警告和压缩建议
    - 退出码 0 表示全部通过，1 表示有文档超长
"""
import argparse
import pathlib
import sys


DEFAULT_MAX_LINES = 300


def check_file(doc_path: pathlib.Path, max_lines: int) -> bool:
    """检查单个文档，返回 True 表示通过。"""
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    count = len(lines)

    if count <= max_lines:
        return True

    # 统计各章节行数
    sections = {}
    current = "(前言)"
    section_start = 0
    for i, line in enumerate(lines):
        if line.startswith("## "):
            if current:
                sections[current] = i - section_start
            current = line[3:].strip()
            section_start = i
    if current:
        sections[current] = len(lines) - section_start

    print(f"⚠️  {doc_path.name}: {count} 行（超过阈值 {max_lines}）")
    print(f"    各章节行数：")
    for name, cnt in sorted(sections.items(), key=lambda x: -x[1]):
        marker = " ← 建议压缩" if cnt > max_lines // 3 else ""
        print(f"      {name}: {cnt} 行{marker}")
    print()
    return False


def main():
    parser = argparse.ArgumentParser(description="检查文档长度")
    parser.add_argument("path", help="文档文件或目录")
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES,
                        help=f"最大行数阈值（默认 {DEFAULT_MAX_LINES}）")
    args = parser.parse_args()

    target = pathlib.Path(args.path)

    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = sorted(target.glob("*.py.md"))
    else:
        print(f"路径不存在: {target}", file=sys.stderr)
        sys.exit(2)

    if not files:
        print("未找到 .py.md 文档文件。")
        return

    passed = 0
    failed = 0
    for f in files:
        if check_file(f, args.max_lines):
            passed += 1
        else:
            failed += 1

    print(f"共检查 {passed + failed} 个文档：{passed} 通过，{failed} 超长。")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
