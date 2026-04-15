# =============================================================================
# 功能描述：
#   Python 代码规范初级检查脚本，基于 SP-CODE-2026-001 规范进行静态分析。
#   检查文件头注释、公开函数 docstring、类型注解、字符串风格、
#   print 调用、通配符导入等常见规范问题。
#
# 类与方法索引：
#   StyleIssue                           (L49)   — 表示一个代码规范问题
#     __init__                           (L59)   — __init__ 函数
#     __str__                            (L73)   — __str__ 函数
#   check_file_header                    (L77)   — 检查文件头注释是否包含必要字段
#   check_docstrings                     (L119)  — 检查公开函数和类是否有 docstring
#   check_type_annotations               (L156)  — 检查公开函数是否有参数和返回值类型注解
#   check_print_usage                    (L201)  — 检查是否使用了 print() 调用（测试文件和脚本除外）
#   check_star_import                    (L232)  — 检查是否使用了 from X import * 通配符导入
#   check_single_quotes                  (L247)  — 检查是否使用了单引号字符串（规范要求双引号）
#   check_file                           (L293)  — 对单个 Python 文件执行全部检查
#   check_directory                      (L321)  — 递归检查目录下所有 Python 文件
#   main                                 (L347)  — 脚本入口
#
# 更新日志：
#   2026-03-28  Copilot  初始创建
#   2026-04-16  Copilot  新增类与方法索引
#
# 当前维护者：Copilot
# =============================================================================
"""
Python 代码规范检查脚本。

用法::

    python check_style.py <file_or_directory> [--verbose]

检查项：
    1. 文件头注释（功能描述 / 类与方法索引 / 更新日志 / 当前维护者）
    2. 公开函数/方法有 docstring
    3. 函数参数与返回值有类型注解
    4. 使用双引号字符串（而非单引号）
    5. 不使用 print()（测试文件除外）
    6. 不使用 from X import *
"""
import ast
import re
import sys
from pathlib import Path
from typing import Any


class StyleIssue:
    """表示一个代码规范问题。

    :param filepath: 文件路径
    :param line: 行号
    :param rule: 规则编号
    :param message: 问题描述
    :param severity: 严重程度（error / warning）
    """

    def __init__(
        self,
        filepath: str,
        line: int,
        rule: str,
        message: str,
        severity: str = "error",
    ) -> None:
        self.filepath = filepath
        self.line = line
        self.rule = rule
        self.message = message
        self.severity = severity

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.filepath}:{self.line} [{self.rule}] {self.message}"


def check_file_header(filepath: str, lines: list[str]) -> list[StyleIssue]:
    """检查文件头注释是否包含必要字段。

    :param filepath: 文件路径
    :param lines: 文件行列表
    :return: 问题列表
    """
    issues: list[StyleIssue] = []
    # 动态提取 # =====...===== 包裹的头部注释块
    # 而非固定行数，以适应索引和更新日志不断增长的情况
    header_lines: list[str] = []
    sep_count = 0
    for line in lines:
        stripped = line.rstrip()
        # 检测分隔线 # ====...====（至少 10 个 =）
        if stripped.startswith("#") and stripped.count("=") >= 10:
            sep_count += 1
            header_lines.append(stripped)
            # 遇到第二条分隔线，头部结束
            if sep_count >= 2:
                break
            continue
        # 在分隔线之间，只收集 # 开头的注释行
        if sep_count == 1 and stripped.startswith("#"):
            header_lines.append(stripped)
        # 遇到非注释行且已进入头部，说明头部异常结束
        elif sep_count == 1 and stripped and not stripped.startswith("#"):
            break
    header_block = "\n".join(header_lines)

    if "功能描述" not in header_block:
        issues.append(StyleIssue(filepath, 1, "H001", "缺少文件头「功能描述」字段"))
    if "类与方法索引" not in header_block:
        issues.append(StyleIssue(filepath, 1, "H004", "缺少文件头「类与方法索引」字段"))
    if "更新日志" not in header_block:
        issues.append(StyleIssue(filepath, 1, "H002", "缺少文件头「更新日志」字段"))
    if "当前维护者" not in header_block:
        issues.append(StyleIssue(filepath, 1, "H003", "缺少文件头「当前维护者」字段"))

    return issues


def check_docstrings(filepath: str, source: str) -> list[StyleIssue]:
    """检查公开函数和类是否有 docstring。

    :param filepath: 文件路径
    :param source: 源代码文本
    :return: 问题列表
    """
    issues: list[StyleIssue] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        issues.append(StyleIssue(filepath, 1, "P001", "文件存在语法错误，无法解析"))
        return issues

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # 跳过私有函数
            if node.name.startswith("_"):
                continue
            docstring = ast.get_docstring(node)
            if not docstring:
                issues.append(
                    StyleIssue(filepath, node.lineno, "D001", f"公开函数 '{node.name}' 缺少 docstring")
                )

        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("_"):
                continue
            docstring = ast.get_docstring(node)
            if not docstring:
                issues.append(
                    StyleIssue(filepath, node.lineno, "D002", f"公开类 '{node.name}' 缺少 docstring")
                )

    return issues


def check_type_annotations(filepath: str, source: str) -> list[StyleIssue]:
    """检查公开函数是否有参数和返回值类型注解。

    :param filepath: 文件路径
    :param source: 源代码文本
    :return: 问题列表
    """
    issues: list[StyleIssue] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return issues

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("_"):
            continue

        # 检查返回值注解
        if node.returns is None:
            issues.append(
                StyleIssue(
                    filepath, node.lineno, "T001",
                    f"函数 '{node.name}' 缺少返回值类型注解",
                    severity="warning",
                )
            )

        # 检查参数注解（跳过 self 和 cls）
        for arg in node.args.args:
            if arg.arg in ("self", "cls"):
                continue
            if arg.annotation is None:
                issues.append(
                    StyleIssue(
                        filepath, node.lineno, "T002",
                        f"函数 '{node.name}' 的参数 '{arg.arg}' 缺少类型注解",
                        severity="warning",
                    )
                )

    return issues


def check_print_usage(filepath: str, lines: list[str]) -> list[StyleIssue]:
    """检查是否使用了 print() 调用（测试文件和脚本除外）。

    :param filepath: 文件路径
    :param lines: 文件行列表
    :return: 问题列表
    """
    issues: list[StyleIssue] = []
    fname = Path(filepath).name

    # 跳过测试文件和 CLI 脚本
    if fname.startswith("test_") or fname == "check_style.py":
        return issues
    # 跳过 scripts 目录下的工具脚本（CLI 工具合理使用 print）
    if "/scripts/" in filepath or "\\scripts\\" in filepath:
        return issues

    pattern = re.compile(r"^\s*print\s*\(")
    for i, line in enumerate(lines, start=1):
        # 跳过注释行
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if pattern.match(stripped):
            issues.append(
                StyleIssue(filepath, i, "L001", "使用了 print()，应改用 logging 模块", severity="warning")
            )

    return issues


def check_star_import(filepath: str, lines: list[str]) -> list[StyleIssue]:
    """检查是否使用了 from X import * 通配符导入。

    :param filepath: 文件路径
    :param lines: 文件行列表
    :return: 问题列表
    """
    issues: list[StyleIssue] = []
    pattern = re.compile(r"^\s*from\s+\S+\s+import\s+\*")
    for i, line in enumerate(lines, start=1):
        if pattern.match(line):
            issues.append(StyleIssue(filepath, i, "I001", "禁止使用 'from X import *' 通配符导入"))
    return issues


def check_single_quotes(filepath: str, lines: list[str]) -> list[StyleIssue]:
    """检查是否使用了单引号字符串（规范要求双引号）。

    仅在行级别进行粗略检查，跳过注释行和 docstring 行。

    :param filepath: 文件路径
    :param lines: 文件行列表
    :return: 问题列表
    """
    issues: list[StyleIssue] = []
    in_docstring = False
    quote_count = 0  # 限制报告数量

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        # 跟踪 docstring 区域
        if '"""' in stripped:
            count = stripped.count('"""')
            if count == 1:
                in_docstring = not in_docstring
            continue
        if in_docstring:
            continue

        # 跳过注释行
        if stripped.startswith("#"):
            continue

        # 检查是否包含单引号字符串（排除 docstring 和转义）
        # 简单匹配：独立的 'xxx' 模式
        if re.search(r"(?<![\"\\])'[^']*'", stripped):
            # 排除 f-string 内的字典键、字符串内的撇号等常见误报
            if quote_count < 5:  # 限制每文件最多报 5 条
                issues.append(
                    StyleIssue(
                        filepath, i, "S001",
                        "建议使用双引号代替单引号",
                        severity="warning",
                    )
                )
                quote_count += 1

    return issues


def check_file(filepath: str, verbose: bool = False) -> list[StyleIssue]:
    """对单个 Python 文件执行全部检查。

    :param filepath: 文件路径
    :param verbose: 是否输出详细信息
    :return: 所有问题的列表
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        return [StyleIssue(filepath, 0, "F001", f"无法读取文件: {e}")]

    lines = content.splitlines()
    if not lines:
        return []

    issues: list[StyleIssue] = []
    issues.extend(check_file_header(filepath, lines))
    issues.extend(check_docstrings(filepath, content))
    issues.extend(check_type_annotations(filepath, content))
    issues.extend(check_print_usage(filepath, lines))
    issues.extend(check_star_import(filepath, lines))
    issues.extend(check_single_quotes(filepath, lines))

    return issues


def check_directory(dirpath: str, verbose: bool = False) -> list[StyleIssue]:
    """递归检查目录下所有 Python 文件。

    :param dirpath: 目录路径
    :param verbose: 是否输出详细信息
    :return: 所有问题的列表
    """
    all_issues: list[StyleIssue] = []
    p = Path(dirpath)
    py_files = sorted(p.rglob("*.py"))

    for py_file in py_files:
        # 跳过虚拟环境和缓存目录
        parts = py_file.parts
        if any(part in (".venv", "venv", "__pycache__", "node_modules") for part in parts):
            continue

        if verbose:
            print(f"检查: {py_file}")  # 脚本自身的 print 是合理的

        issues = check_file(str(py_file), verbose)
        all_issues.extend(issues)

    return all_issues


def main() -> None:
    """脚本入口。"""
    if len(sys.argv) < 2:
        print("用法: python check_style.py <file_or_directory> [--verbose]")
        print()
        print("基于 SP-CODE-2026-001 规范检查 Python 代码风格。")
        sys.exit(1)

    target = sys.argv[1]
    verbose = "--verbose" in sys.argv

    target_path = Path(target)
    if not target_path.exists():
        print(f"错误: 路径不存在: {target}")
        sys.exit(1)

    if target_path.is_file():
        issues = check_file(str(target_path), verbose)
    else:
        issues = check_directory(str(target_path), verbose)

    if not issues:
        print("✅ 未发现代码规范问题。")
        sys.exit(0)

    # 按文件分组输出
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    for issue in issues:
        print(issue)

    print()
    print(f"共发现 {len(issues)} 个问题（{len(errors)} 个错误，{len(warnings)} 个警告）")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
