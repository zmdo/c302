# =============================================================================
# 功能描述：
#   自动生成或更新 Python 文件头部「类与方法索引」。
#   通过 AST 解析提取所有类、函数和方法定义，
#   生成符合 SP-CODE-2026-001 规范的索引块，并可就地更新文件。
#
# 类与方法索引：
#   generate_index_block                 (L38)   — 根据 AST 解析结果生成索引文本块
#   update_file_header                   (L93)   — 就地更新文件头部的索引段落
#   preview_file                         (L170)  — 预览文件的索引生成结果（不修改文件）
#   process_target                       (L195)  — 处理单个文件或目录
#   main                                 (L233)  — 脚本入口，解析命令行参数并执行索引生成
#   _get_first_line_doc                  (L272)  — 提取节点的 docstring 首行作为描述
#   _find_insert_position                (L295)  — 查找索引段落应插入的位置
#
# 更新日志：
#   2026-04-16  Copilot  初始创建
#
# 当前维护者：Copilot
# =============================================================================
"""
自动生成 Python 文件头部「类与方法索引」。

用法::

    python gen_index.py <file_or_directory> [--write] [--verbose]

默认仅预览生成的索引内容；加 --write 则就地更新文件头部。
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


def generate_index_block(source: str) -> str | None:
    """根据 AST 解析结果生成索引文本块。

    遍历源码的顶层节点，收集类、函数和方法信息，
    按照规范格式生成带行号和描述的索引行。

    :param source: Python 源代码文本
    :return: 索引文本块（不含段落标题），无定义时返回 None
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    # 收集所有定义条目
    entries: list[tuple[str, int, str | None, str]] = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            # 获取类的 docstring 首行作为描述
            desc = _get_first_line_doc(node)
            entries.append((node.name, node.lineno, None, desc))

            # 收集类内方法
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_desc = _get_first_line_doc(child)
                    entries.append((child.name, child.lineno, node.name, method_desc))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            desc = _get_first_line_doc(node)
            entries.append((node.name, node.lineno, None, desc))

    if not entries:
        return None

    # 生成格式化的索引行
    lines: list[str] = []
    for name, lineno, parent, desc in entries:
        # 计算对齐：名称 + 空格 + (Lxxx) 总宽度约 45 字符
        line_tag = f"(L{lineno})"
        if parent is not None:
            # 方法：2 空格缩进
            prefix = f"#     {name}"
        else:
            # 顶层类/函数：3 空格前缀
            prefix = f"#   {name}"

        # 对齐到固定列宽
        padded = f"{prefix:<40s} {line_tag:<8s}— {desc}"
        lines.append(padded)

    return "\n".join(lines)


def update_file_header(filepath: str, verbose: bool = False) -> bool:
    """就地更新文件头部的索引段落。

    如果文件已有「类与方法索引：」段落，替换其内容；
    如果没有，在「功能描述：」段落后插入索引段落。

    :param filepath: 文件路径
    :param verbose: 是否输出详细信息
    :return: 是否成功更新
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"[错误] 无法读取 {filepath}: {exc}")
        return False

    # 生成新的索引块
    index_block = generate_index_block(content)
    if index_block is None:
        if verbose:
            print(f"  跳过 {filepath}: 无类或函数定义")
        return False

    lines = content.splitlines()
    new_index_section = f"# 类与方法索引：\n{index_block}"

    # 查找现有的索引段落位置
    index_start = None
    index_end = None
    in_index = False

    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if re.match(r"^#\s+类与方法索引[：:]", stripped):
            index_start = i
            in_index = True
            continue
        if in_index:
            # 索引段落结束条件：遇到空注释行、段落关键词或分隔线
            if (stripped == "#"
                    or re.match(r"^#\s*(更新日志|当前维护者|=)", stripped)
                    or not stripped.startswith("#")):
                index_end = i
                break
            # 检查是否是索引条目行
            if re.match(r"^#\s{3}", stripped):
                continue
            # 其他情况也结束
            index_end = i
            break

    if index_start is not None:
        # 替换现有索引段落
        if index_end is None:
            index_end = index_start + 1
        new_lines = lines[:index_start] + new_index_section.splitlines() + lines[index_end:]
    else:
        # 没有索引段落——在功能描述段落后插入
        insert_pos = _find_insert_position(lines)
        new_lines = (
            lines[:insert_pos]
            + ["#"]
            + new_index_section.splitlines()
            + lines[insert_pos:]
        )

    # 写回文件
    new_content = "\n".join(new_lines) + "\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    if verbose:
        print(f"  ✅ 已更新 {filepath}")
    return True


def preview_file(filepath: str) -> None:
    """预览文件的索引生成结果（不修改文件）。

    读取文件内容，生成索引块并打印到标准输出。

    :param filepath: 文件路径
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"[错误] 无法读取 {filepath}: {exc}")
        return

    index_block = generate_index_block(source)
    if index_block is None:
        print(f"--- {filepath}: 无类或函数定义 ---")
        return

    print(f"--- {filepath} ---")
    print(f"# 类与方法索引：")
    print(index_block)
    print()


def process_target(target: str, write: bool, verbose: bool) -> int:
    """处理单个文件或目录。

    根据目标类型分发到单文件或目录递归处理。

    :param target: 文件或目录路径
    :param write: 是否就地写入
    :param verbose: 是否输出详细信息
    :return: 处理的文件数
    """
    target_path = Path(target)
    count = 0

    if target_path.is_file():
        # 单文件处理
        if write:
            if update_file_header(str(target_path), verbose):
                count += 1
        else:
            preview_file(str(target_path))
            count += 1
    elif target_path.is_dir():
        # 递归处理目录
        for py_file in sorted(target_path.rglob("*.py")):
            # 跳过虚拟环境和缓存目录
            parts = py_file.parts
            if any(part in (".venv", "venv", "__pycache__", "node_modules") for part in parts):
                continue
            if write:
                if update_file_header(str(py_file), verbose):
                    count += 1
            else:
                preview_file(str(py_file))
                count += 1

    return count


def main() -> None:
    """脚本入口，解析命令行参数并执行索引生成。"""
    if len(sys.argv) < 2:
        print("用法: python gen_index.py <file_or_directory> [--write] [--verbose]")
        print()
        print("自动生成 Python 文件头部「类与方法索引」。")
        print()
        print("选项：")
        print("  --write    就地更新文件头部（默认仅预览）")
        print("  --verbose  输出详细处理信息")
        print()
        print("示例：")
        print("  python gen_index.py src/module.py          # 预览索引")
        print("  python gen_index.py src/module.py --write  # 就地更新")
        print("  python gen_index.py src/ --write --verbose # 批量更新")
        sys.exit(1)

    target = sys.argv[1]
    write = "--write" in sys.argv
    verbose = "--verbose" in sys.argv

    target_path = Path(target)
    if not target_path.exists():
        print(f"错误: 路径不存在: {target}")
        sys.exit(1)

    # 处理目标
    count = process_target(target, write, verbose)

    # 输出摘要
    if write:
        print(f"\n共更新 {count} 个文件的索引。")
    else:
        if count == 0:
            print("未找到包含类或函数定义的 Python 文件。")
        else:
            print(f"共预览 {count} 个文件。使用 --write 参数就地更新。")


def _get_first_line_doc(node: ast.AST) -> str:
    """提取节点的 docstring 首行作为描述。

    如果没有 docstring，返回通用描述。

    :param node: AST 节点
    :return: 描述文字
    """
    docstring = ast.get_docstring(node)
    if docstring:
        # 取首行，去除末尾句号
        first_line = docstring.split("\n")[0].strip()
        if first_line.endswith("。"):
            first_line = first_line[:-1]
        return first_line
    # 无 docstring 时给出默认描述
    if isinstance(node, ast.ClassDef):
        return f"{node.name} 类"
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return f"{node.name} 函数"
    return "（无描述）"


def _find_insert_position(lines: list[str]) -> int:
    """查找索引段落应插入的位置。

    在功能描述段落结束后、更新日志之前插入。

    :param lines: 文件行列表
    :return: 插入位置的行索引
    """
    in_desc = False
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if "功能描述" in stripped:
            in_desc = True
            continue
        if in_desc:
            # 功能描述段落后的空注释行是插入点
            if stripped == "#":
                return i
            # 遇到下一个段落则在其前插入
            if re.match(r"^#\s*(更新日志|当前维护者|=)", stripped):
                return i

    # 回退：在文件开头
    return 0


if __name__ == "__main__":
    main()
