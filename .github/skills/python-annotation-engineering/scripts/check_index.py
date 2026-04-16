# =============================================================================
# 功能描述：
#   Python 文件头部「类与方法索引」检查脚本。
#   解析文件头部的索引声明，与 AST 提取的实际定义进行比对，
#   报告缺失条目、多余条目和行号偏差。
#
# 类与方法索引：
#   IndexEntry                       (L46)   — 索引条目数据结构
#   ActualDef                        (L56)   — AST 提取的实际定义数据结构
#   parse_header_index               (L65)   — 从文件头部解析类与方法索引
#   extract_actual_defs              (L136)  — 通过 AST 提取文件中所有类、函数和方法定义
#   compare_index                    (L183)  — 比对索引声明与实际定义，生成差异报告
#   check_file                       (L260)  — 对单个文件执行索引检查
#   check_directory                  (L314)  — 递归检查目录下所有 Python 文件
#   main                             (L345)  — 脚本入口
#
# 更新日志：
#   2026-04-16  Copilot  初始创建
#
# 当前维护者：Copilot
# =============================================================================
"""
Python 文件头部「类与方法索引」检查脚本。

用法::

    python check_index.py <file_or_directory> [--verbose]

检查项：
    1. 文件头部是否包含「类与方法索引」段落
    2. 索引中声明的行号是否与实际 def/class 行号一致
    3. 索引中是否遗漏了实际存在的类、函数或方法
    4. 索引中是否包含实际已不存在的条目
    5. 类方法的层级关系是否正确
"""
from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IndexEntry:
    """头部索引中的一条声明。"""

    name: str  # 类/函数/方法名
    line: int  # 声明的行号
    parent: str | None  # 所属类名，None 表示顶层
    description: str  # 描述文字


@dataclass
class ActualDef:
    """AST 提取的一个实际定义。"""

    name: str  # 类/函数/方法名
    line: int  # 实际行号
    parent: str | None  # 所属类名，None 表示顶层
    kind: str  # "class", "function", "method"


def parse_header_index(lines: list[str]) -> tuple[list[IndexEntry], bool]:
    """从文件头部解析「类与方法索引」段落。

    扫描文件前部的注释块，定位「类与方法索引：」行，
    然后逐行解析直到遇到空注释行或下一个段落关键词。

    :param lines: 文件全部行（字符串列表）
    :return: (索引条目列表, 是否找到索引段落)
    """
    entries: list[IndexEntry] = []
    in_index = False
    current_class: str | None = None

    # 匹配索引条目：可选的前导空格 + 名称 + (Lxx) + — + 描述
    pattern = re.compile(
        r"^#\s{3}(\s{0,2})(\w+)\s+\(L(\d+)\)\s+—\s+(.+)$"
    )

    # 仅扫描文件头部注释块（遇到非注释行即停止）
    for line in lines:
        stripped = line.rstrip()

        # 文件头注释块以 # 开头；空行或非注释行则头部结束
        if not stripped.startswith("#") and stripped != "":
            # 允许跳过空行，但遇到实际代码行则停止
            if in_index:
                break
            # 如果还没进入索引段落，继续扫描
            continue

        # 检测索引段落起始——必须是独立的段落标题行
        if re.match(r"^#\s+类与方法索引[：:]", stripped) and not in_index:
            in_index = True
            continue

        # 如果在索引段落中
        if in_index:
            # 遇到下一个段落关键词，结束索引解析
            if re.match(r"^#\s*(更新日志|当前维护者|=)", stripped):
                break

            # 空注释行（仅有 #）作为段落分隔
            if stripped == "#":
                break

            # 尝试匹配索引条目
            match = pattern.match(stripped)
            if match:
                indent = match.group(1)
                name = match.group(2)
                line_num = int(match.group(3))
                desc = match.group(4).strip()

                # 2 空格缩进表示方法属于当前类
                if len(indent) >= 2:
                    parent = current_class
                else:
                    parent = None
                    # 顶层条目可能是类，记录为潜在的父类
                    current_class = name

                entries.append(IndexEntry(
                    name=name,
                    line=line_num,
                    parent=parent,
                    description=desc,
                ))

    return entries, in_index


def extract_actual_defs(source: str) -> list[ActualDef]:
    """通过 AST 提取文件中所有类、函数和方法定义。

    遍历 AST 顶层节点和类体内节点，收集所有 class/def 的名称和行号。

    :param source: Python 源代码文本
    :return: 实际定义列表
    """
    defs: list[ActualDef] = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return defs

    # 遍历顶层节点
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            # 记录类本身
            defs.append(ActualDef(
                name=node.name,
                line=node.lineno,
                parent=None,
                kind="class",
            ))
            # 记录类内的方法
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defs.append(ActualDef(
                        name=child.name,
                        line=child.lineno,
                        parent=node.name,
                        kind="method",
                    ))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # 顶层函数
            defs.append(ActualDef(
                name=node.name,
                line=node.lineno,
                parent=None,
                kind="function",
            ))

    return defs


def compare_index(
    entries: list[IndexEntry],
    actuals: list[ActualDef],
    filepath: str,
) -> list[str]:
    """比对索引声明与实际定义，生成差异报告。

    对每个实际定义检查索引中是否有对应条目、行号是否一致、层级是否正确。
    同时检查索引中是否有已不存在的多余条目。

    :param entries: 头部索引条目列表
    :param actuals: AST 提取的实际定义列表
    :param filepath: 文件路径（用于报告输出）
    :return: 问题描述列表
    """
    issues: list[str] = []

    # 构建索引查找表：(name, parent) → IndexEntry
    index_map: dict[tuple[str, str | None], IndexEntry] = {}
    for entry in entries:
        key = (entry.name, entry.parent)
        index_map[key] = entry

    # 构建实际定义查找表：(name, parent) → ActualDef
    actual_map: dict[tuple[str, str | None], ActualDef] = {}
    for actual in actuals:
        key = (actual.name, actual.parent)
        actual_map[key] = actual

    # 检查每个实际定义是否在索引中
    for actual in actuals:
        key = (actual.name, actual.parent)
        if key not in index_map:
            # 尝试查找仅名称匹配但层级不同的条目
            name_matches = [e for e in entries if e.name == actual.name]
            if name_matches:
                entry = name_matches[0]
                if actual.parent != entry.parent:
                    issues.append(
                        f"[层级错误] {filepath}: '{actual.name}' "
                        f"索引中归属 '{entry.parent}'，"
                        f"实际归属 '{actual.parent}'"
                    )
            else:
                parent_info = f" (类 {actual.parent} 下)" if actual.parent else ""
                issues.append(
                    f"[缺失条目] {filepath}: "
                    f"'{actual.name}'{parent_info} 在 L{actual.line}，"
                    f"但索引中未列出"
                )
        else:
            entry = index_map[key]
            # 检查行号是否一致
            if entry.line != actual.line:
                issues.append(
                    f"[行号偏差] {filepath}: "
                    f"'{actual.name}' 索引声明 L{entry.line}，"
                    f"实际在 L{actual.line}"
                )

    # 检查索引中是否有多余条目（实际已不存在）
    for entry in entries:
        key = (entry.name, entry.parent)
        if key not in actual_map:
            # 也检查是否名称存在但层级不同（已在上面报告过）
            name_matches = [a for a in actuals if a.name == entry.name]
            if not name_matches:
                parent_info = f" (类 {entry.parent} 下)" if entry.parent else ""
                issues.append(
                    f"[多余条目] {filepath}: "
                    f"索引中列出 '{entry.name}'{parent_info} L{entry.line}，"
                    f"但文件中无此定义"
                )

    return issues


def check_file(filepath: str, verbose: bool = False) -> list[str]:
    """对单个文件执行索引检查。

    读取文件内容，解析头部索引和 AST 定义，进行比对。

    :param filepath: 文件路径
    :param verbose: 是否输出详细信息
    :return: 问题描述列表
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as exc:
        return [f"[读取失败] {filepath}: {exc}"]

    lines = content.splitlines()
    if not lines:
        return []

    # 解析头部索引
    entries, has_index = parse_header_index(lines)

    # 提取实际定义
    actuals = extract_actual_defs(content)

    # 如果文件中没有类或函数定义，跳过索引检查
    if not actuals:
        return []

    issues: list[str] = []

    # 检查是否有索引段落
    if not has_index:
        issues.append(f"[缺少索引] {filepath}: 文件头部缺少「类与方法索引」段落")
        return issues

    # 如果有索引段落但没有解析到任何条目
    if not entries:
        issues.append(
            f"[索引为空] {filepath}: 「类与方法索引」段落存在但无条目"
            f"（实际有 {len(actuals)} 个定义）"
        )
        return issues

    # 比对索引与实际定义
    issues.extend(compare_index(entries, actuals, filepath))

    # 输出摘要
    if verbose and not issues:
        print(f"  ✅ {filepath}: 索引与实际一致（{len(actuals)} 个定义）")

    return issues


def check_directory(dirpath: str, verbose: bool = False) -> list[str]:
    """递归检查目录下所有 Python 文件。

    跳过虚拟环境、缓存目录和测试文件。

    :param dirpath: 目录路径
    :param verbose: 是否输出详细信息
    :return: 所有问题的列表
    """
    all_issues: list[str] = []
    p = Path(dirpath)

    # 递归查找所有 Python 文件
    for py_file in sorted(p.rglob("*.py")):
        # 跳过虚拟环境和缓存目录
        parts = py_file.parts
        if any(
            part in (".venv", "venv", "__pycache__", "node_modules")
            for part in parts
        ):
            continue

        if verbose:
            print(f"检查: {py_file}")

        issues = check_file(str(py_file), verbose)
        all_issues.extend(issues)

    return all_issues


def main() -> None:
    """脚本入口，解析命令行参数并执行检查。"""
    if len(sys.argv) < 2:
        print("用法: python check_index.py <file_or_directory> [--verbose]")
        print()
        print("检查 Python 文件头部「类与方法索引」是否与实际代码一致。")
        print()
        print("检查项：")
        print("  1. 头部是否包含「类与方法索引」段落")
        print("  2. 索引行号是否与实际 def/class 行号一致")
        print("  3. 是否有遗漏的类/函数/方法")
        print("  4. 是否有多余的（已删除的）条目")
        print("  5. 类方法的层级关系是否正确")
        sys.exit(1)

    target = sys.argv[1]
    verbose = "--verbose" in sys.argv

    target_path = Path(target)
    if not target_path.exists():
        print(f"错误: 路径不存在: {target}")
        sys.exit(1)

    # 根据目标类型选择检查方式
    if target_path.is_file():
        issues = check_file(str(target_path), verbose)
    else:
        issues = check_directory(str(target_path), verbose)

    # 输出结果
    if not issues:
        print("✅ 所有文件的「类与方法索引」与实际代码一致。")
        sys.exit(0)

    for issue in issues:
        print(issue)

    print()
    print(f"共发现 {len(issues)} 个索引问题。")
    sys.exit(1)


if __name__ == "__main__":
    main()
