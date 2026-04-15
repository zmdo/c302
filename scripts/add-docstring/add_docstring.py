#!/usr/bin/env python3
# =============================================================================
# 功能描述：
#   安全地向 Python 函数/方法添加 docstring，保证仅执行插入操作，
#   不修改任何现有代码行。若函数已有 docstring 则跳过（幂等）。
#   添加完成后自动更新文件头「类与方法索引」。
#
# 类与方法索引：
#   find_function_node                   (L61)   — 在 AST 中查找指定名称的函数/方法节点
#   has_docstring                        (L94)   — 检查函数节点是否已有 docstring
#   format_docstring                     (L111)  — 将原始文本格式化为带缩进的三引号行列表
#   insert_docstring                     (L153)  — 在源码行列表中向指定函数节点插入 docstring
#   run_gen_index                        (L192)  — 调用 gen_index.py 更新文件头「类与方法索引」
#   process_file                         (L222)  — 处理单个文件的所有 docstring 添加任务
#   build_parser                         (L296)  — 构建命令行参数解析器
#   main                                 (L344)  — 脚本入口，解析命令行参数并执行
#
# 更新日志：
#   2026-04-16  Copilot  初始创建
#
# 当前维护者：Copilot
# =============================================================================
"""向 Python 函数/方法安全添加 docstring 的工具。

仅执行插入操作，不修改任何现有代码行，确保操作安全可逆。
若函数已有 docstring 则跳过（幂等），完成后自动更新文件头索引。

用法::

    # 批量模式（推荐，使用 YAML 规范文件）
    python add_docstring.py --spec tasks.yaml

    # 单函数模式
    python add_docstring.py project/c302/foo.py my_func --doc "函数说明。"
    python add_docstring.py project/c302/foo.py MyClass.method --doc-file doc.txt

YAML 规范文件格式::

    - file: project/c302/foo.py
      functions:
        - name: my_function            # 顶层函数
          docstring: |
            单行或多行 docstring 文本。

            :param x: 参数说明
            :return: 返回值说明
        - name: MyClass.my_method      # 类方法（用 . 分隔类名和方法名）
          docstring: |
            方法 docstring。
"""
from __future__ import annotations

import ast
import argparse
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Optional

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


def find_function_node(
    tree: ast.AST,
    name: str,
) -> Optional[ast.FunctionDef]:
    """在 AST 中查找指定名称的函数/方法节点。

    支持顶层函数和类方法两种格式：
    - 顶层函数：直接传函数名，如 ``"my_func"``
    - 类方法：用点分隔，如 ``"MyClass.my_method"``

    遇到同名的多个定义时，返回第一个匹配项。

    :param tree: 已解析的 AST 树根节点
    :param name: 函数名（顶层）或 ``'ClassName.method_name'``（类方法）
    :return: 找到的函数节点；未找到时返回 ``None``
    """
    parts = name.split(".", 1)

    if len(parts) == 1:
        # 顶层函数：在整棵树中广度优先搜索
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == name:
                    return node
    else:
        # 类方法：先找类，再在类 body 中找方法
        class_name, method_name = parts
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if (
                        isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and item.name == method_name
                    ):
                        return item

    return None


def has_docstring(func_node: ast.FunctionDef) -> bool:
    """检查函数节点是否已有 docstring。

    判断条件：函数 body 的第一个语句是 ``Expr(Constant(str))`` 形式。

    :param func_node: 函数/方法 AST 节点
    :return: ``True`` 表示已有 docstring，``False`` 表示没有
    """
    body = func_node.body
    return (
        bool(body)
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    )


def format_docstring(text: str, indent: int) -> list[str]:
    """将原始 docstring 文本格式化为带缩进的三引号行列表。

    对单行文本使用 ``'''summary.'''`` 格式（三引号）；
    对多行文本使用展开格式，末尾三引号单独一行。

    每行末尾均附换行符，可直接拼接进源文件行列表。

    :param text: 原始 docstring 文本（不含三引号，可含多行）
    :param indent: 缩进空格数（与函数 body 首个语句对齐）
    :return: 格式化后的行列表，每行末尾含 ``\\n``
    """
    prefix = " " * indent
    # 去除首尾空行，并统一去掉每行尾部空白
    stripped = text.strip()
    lines = [ln.rstrip() for ln in stripped.split("\n")]

    result: list[str] = []

    if len(lines) == 1:
        # 单行 docstring：用单行格式
        result.append(f'{prefix}"""{lines[0]}"""\n')
    else:
        # 多行 docstring：首行紧接开三引号，末尾三引号独占一行
        result.append(f'{prefix}"""{lines[0]}\n')
        for ln in lines[1:]:
            if ln:
                # 有内容的行：加缩进
                result.append(f"{prefix}{ln}\n")
            else:
                # 空行：保留空行（不加缩进，避免尾部空白）
                result.append("\n")
        result.append(f'{prefix}"""\n')

    return result


def insert_docstring(
    source_lines: list[str],
    func_node: ast.FunctionDef,
    docstring_text: str,
) -> list[str]:
    """在源码行列表中向指定函数节点插入 docstring。

    插入位置为函数 body 第一个语句之前。
    缩进与该第一个语句的列偏移对齐。
    **不修改任何已有行**，仅在指定位置插入新行。

    :param source_lines: 文件全部源码行（保留换行符），来自 ``splitlines(keepends=True)``
    :param func_node: 目标函数/方法 AST 节点
    :param docstring_text: 要插入的 docstring 文本（不含三引号）
    :return: 插入后的新行列表（原列表不被修改）
    """
    first_stmt = func_node.body[0]
    # AST lineno 是 1-based；在该行之前插入（0-based index = lineno - 1）
    insert_pos = first_stmt.lineno - 1
    indent = first_stmt.col_offset

    doc_lines = format_docstring(docstring_text, indent)

    # 切片拼接，不修改原列表
    return source_lines[:insert_pos] + doc_lines + source_lines[insert_pos:]


def run_gen_index(file_path: Path) -> None:
    """调用 gen_index.py --write 更新文件头「类与方法索引」。

    从本脚本所在位置向上逐层查找 gen_index.py，兼容不同的项目布局。
    若找不到则静默跳过（不影响主流程）。

    :param file_path: 已修改的 Python 文件路径
    """
    # 从本脚本向上查找 gen_index.py
    gen_index: Optional[Path] = None
    for parent in Path(__file__).parents:
        candidate = (
            parent / ".github" / "skills" / "python-code-style" / "scripts" / "gen_index.py"
        )
        if candidate.exists():
            gen_index = candidate
            break

    if gen_index is None:
        # 找不到 gen_index，静默跳过
        return

    result = subprocess.run(
        [sys.executable, str(gen_index), str(file_path), "--write"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # gen_index 失败不中断主流程，仅打印警告
        print(
            f"  [WARN]  gen_index 更新索引失败: {result.stderr.strip()}",
            file=sys.stderr,
        )


def process_file(
    file_path: Path,
    functions: list[dict],
    dry_run: bool = False,
) -> int:
    """处理单个文件，依次添加所有指定函数的 docstring。

    处理逻辑：
    1. 读取文件内容，解析 AST；
    2. 对每个函数任务，检查是否已有 docstring，若有则跳过；
    3. 每次插入后重新解析 AST，避免行号偏移累积；
    4. 全部任务完成后原子写入文件（写入失败时自动还原备份）；
    5. 调用 gen_index 更新文件头索引。

    :param file_path: 目标 Python 文件路径（必须存在）
    :param functions: 函数任务列表，每项含 ``name`` 和 ``docstring`` 两个字段
    :param dry_run: ``True`` 时仅预览，不写入文件
    :return: 实际添加（或预计添加）的 docstring 数量
    """
    source = file_path.read_text(encoding="utf-8")
    # splitlines(keepends=True) 保留换行符，确保行内容原封不动写回
    lines = source.splitlines(keepends=True)
    # 确保最后一行有换行符（部分编辑器可能省略）
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    added = 0

    for func_spec in functions:
        name: str = func_spec["name"]
        docstring_text: str = func_spec["docstring"]

        # 每次任务开始时重新解析，以获得最新的行号（上一次插入会使行号偏移）
        current_source = "".join(lines)
        try:
            tree = ast.parse(current_source)
        except SyntaxError as exc:
            print(
                f"  [ERROR] 语法错误，无法解析 {file_path.name}: {exc}",
                file=sys.stderr,
            )
            # 语法错误时放弃后续任务，返回已完成数
            return added

        func_node = find_function_node(tree, name)
        if func_node is None:
            print(f"  [SKIP]  未找到函数: {name}")
            continue

        if has_docstring(func_node):
            print(f"  [SKIP]  已有 docstring: {name}")
            continue

        if dry_run:
            print(f"  [DRY]   将在第 {func_node.body[0].lineno} 行前插入 docstring: {name}")
            added += 1
            continue

        lines = insert_docstring(lines, func_node, docstring_text)
        print(f"  [ADD]   已插入 docstring: {name}")
        added += 1

    if added > 0 and not dry_run:
        # 先备份，写入成功后删除备份；写入失败则还原
        backup = file_path.with_suffix(file_path.suffix + ".bak")
        shutil.copy2(file_path, backup)
        try:
            file_path.write_text("".join(lines), encoding="utf-8")
            backup.unlink()
        except Exception as exc:  # noqa: BLE001
            shutil.copy2(backup, file_path)
            backup.unlink()
            print(
                f"  [ERROR] 写入失败，已还原原始文件: {exc}",
                file=sys.stderr,
            )
            return 0

        print(f"  [SAVE]  已写入: {file_path}")
        run_gen_index(file_path)

    return added


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。

    支持两种使用模式：
    - **批量模式**：``--spec <file.yaml>``，从 YAML 文件读取多个文件/函数任务；
    - **单函数模式**：``<file> <func> --doc "..."``，直接在命令行指定。

    :return: 已配置好的 ``ArgumentParser`` 实例
    """
    parser = argparse.ArgumentParser(
        prog="add_docstring",
        description="向 Python 函数安全添加 docstring（仅插入，不删除任何代码行）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            示例：
              # 批量模式
              python add_docstring.py --spec tasks.yaml

              # 单函数模式（顶层函数）
              python add_docstring.py project/c302/foo.py my_func --doc "函数说明。"

              # 单函数模式（类方法）
              python add_docstring.py project/c302/foo.py MyClass.method --doc-file doc.txt

              # 仅预览，不写入
              python add_docstring.py --spec tasks.yaml --dry-run
            """
        ),
    )
    parser.add_argument(
        "--spec",
        metavar="FILE",
        help="YAML 批量规范文件路径（批量模式）",
    )
    parser.add_argument(
        "file",
        nargs="?",
        metavar="FILE",
        help="目标 Python 文件路径（单函数模式）",
    )
    parser.add_argument(
        "func",
        nargs="?",
        metavar="FUNC",
        help="函数名，类方法用 ClassName.method 格式（单函数模式）",
    )
    doc_group = parser.add_mutually_exclusive_group()
    doc_group.add_argument(
        "--doc",
        metavar="TEXT",
        help="docstring 文本（单函数模式）",
    )
    doc_group.add_argument(
        "--doc-file",
        metavar="FILE",
        help="包含 docstring 文本的文件路径（单函数模式）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览将要执行的操作，不写入文件",
    )
    return parser


def main() -> None:
    """脚本入口：解析命令行参数并执行 docstring 添加。"""
    parser = build_parser()
    args = parser.parse_args()

    # ── 批量模式 ──────────────────────────────────────────────────────────────
    if args.spec:
        if not _YAML_AVAILABLE:
            parser.error("批量模式需要 PyYAML，请运行: pip install pyyaml")

        spec_path = Path(args.spec)
        if not spec_path.exists():
            parser.error(f"规范文件不存在: {spec_path}")

        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        if not isinstance(spec, list):
            parser.error("规范文件顶层须为列表（- file: ... functions: ...）")

        total_added = 0
        for entry in spec:
            file_path = Path(entry["file"])
            functions = entry.get("functions", [])
            if not file_path.exists():
                print(f"\n[ERROR] 文件不存在: {file_path}", file=sys.stderr)
                continue
            print(f"\n── 处理: {file_path} ──")
            total_added += process_file(file_path, functions, dry_run=args.dry_run)

        print(f"\n共添加 {total_added} 个 docstring。")
        return

    # ── 单函数模式 ────────────────────────────────────────────────────────────
    if not args.file or not args.func:
        parser.print_help()
        sys.exit(1)

    if not args.doc and not args.doc_file:
        parser.error("单函数模式需要提供 --doc 或 --doc-file")

    file_path = Path(args.file)
    if not file_path.exists():
        parser.error(f"文件不存在: {file_path}")

    if args.doc_file:
        doc_path = Path(args.doc_file)
        if not doc_path.exists():
            parser.error(f"docstring 文件不存在: {doc_path}")
        docstring_text = doc_path.read_text(encoding="utf-8")
    else:
        docstring_text = args.doc

    print(f"\n── 处理: {file_path} ──")
    added = process_file(
        file_path,
        [{"name": args.func, "docstring": docstring_text}],
        dry_run=args.dry_run,
    )
    print(f"\n共添加 {added} 个 docstring。")


if __name__ == "__main__":
    main()
