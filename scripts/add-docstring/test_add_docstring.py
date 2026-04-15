# =============================================================================
# 功能描述：
#   add_docstring.py 的单元测试。
#   覆盖函数查找、docstring 检测、格式化、插入、幂等性等核心场景。
#
# 类与方法索引：
#   TestFindFunctionNode                 (L50)   — 测试 find_function_node 查找逻辑
#     test_finds_top_level_function      (L53)   — 可找到顶层函数
#     test_finds_class_method            (L60)   — 可找到类方法（ClassName.method 格式）
#     test_returns_none_for_missing      (L69)   — 找不到时返回 None
#   TestHasDocstring                     (L75)   — 测试 has_docstring 检测逻辑
#     test_detects_docstring             (L78)   — 有 docstring 的函数返回 True
#     test_no_docstring                  (L85)   — 无 docstring 的函数返回 False
#   TestFormatDocstring                  (L92)   — 测试 docstring 格式化
#     test_single_line                   (L95)   — 单行格式化
#     test_multiline                     (L103)  — 多行格式化：首行紧接三引号，末尾三引号独行
#     test_empty_line_preserved          (L114)  — 多行中空行被保留
#     test_indent_applied                (L124)  — 缩进正确应用
#   TestInsertDocstring                  (L131)  — 测试 insert_docstring 插入操作
#     test_inserts_before_first_stmt     (L134)  — docstring 插入到函数 body 第一行之前
#     test_original_lines_unchanged      (L147)  — 已有行不被修改（纯插入）
#     test_method_in_class               (L158)  — 类方法也能正确插入
#   TestProcessFile                      (L172)  — 测试 process_file 端到端处理
#     test_adds_docstring                (L179)  — 正常添加 docstring
#     test_skips_existing_docstring      (L193)  — 已有 docstring 时跳过（幂等）
#     test_skips_missing_function        (L207)  — 找不到函数时跳过，不修改文件
#     test_dry_run_no_write              (L222)  — dry_run 模式不写入文件
#
# 更新日志：
#   2026-04-16  Copilot  初始创建
#
# 当前维护者：Copilot
# =============================================================================
"""add_docstring.py 的单元测试。"""
from __future__ import annotations

import ast
import sys
import tempfile
import unittest
from pathlib import Path

# 将脚本目录加入 sys.path，使 import 可以找到 add_docstring 模块
sys.path.insert(0, str(Path(__file__).parent))

from add_docstring import (
    find_function_node,
    format_docstring,
    has_docstring,
    insert_docstring,
    process_file,
)


class TestFindFunctionNode(unittest.TestCase):
    """测试 find_function_node 查找逻辑。"""

    def test_finds_top_level_function(self) -> None:
        """可找到顶层函数。"""
        # 顶层函数应可通过函数名直接找到
        tree = ast.parse("def foo():\n    pass\n")
        node = find_function_node(tree, "foo")
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "foo")

    def test_finds_class_method(self) -> None:
        """可找到类方法（ClassName.method 格式）。"""
        # 类方法通过 'ClassName.method' 格式查找
        src = "class Bar:\n    def baz(self):\n        pass\n"
        tree = ast.parse(src)
        node = find_function_node(tree, "Bar.baz")
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "baz")

    def test_returns_none_for_missing(self) -> None:
        """找不到时返回 None。"""
        # 不存在的函数名应返回 None
        tree = ast.parse("def foo():\n    pass\n")
        self.assertIsNone(find_function_node(tree, "nonexistent"))


class TestHasDocstring(unittest.TestCase):
    """测试 has_docstring 检测逻辑。"""

    def test_detects_docstring(self) -> None:
        """有 docstring 的函数返回 True。"""
        # 函数首语句是字符串常量时视为 docstring
        tree = ast.parse('def foo():\n    """说明。"""\n    pass\n')
        node = find_function_node(tree, "foo")
        self.assertTrue(has_docstring(node))

    def test_no_docstring(self) -> None:
        """无 docstring 的函数返回 False。"""
        # 首语句是普通语句时无 docstring
        tree = ast.parse("def foo():\n    x = 1\n")
        node = find_function_node(tree, "foo")
        self.assertFalse(has_docstring(node))


class TestFormatDocstring(unittest.TestCase):
    """测试 docstring 格式化。"""

    def test_single_line(self) -> None:
        """单行格式化。"""
        # 单行文本应使用单行格式 `"""text"""`
        result = format_docstring("说明。", indent=4)
        self.assertEqual(len(result), 1)
        self.assertIn('"""说明。"""', result[0])

    def test_multiline(self) -> None:
        """多行格式化：首行紧接三引号，末尾三引号独行。"""
        # 多行时首行紧接开三引号；最后一个元素是仅含关闭三引号的行
        result = format_docstring("首行。\n\n:return: 值", indent=4)
        self.assertTrue(result[0].startswith('    """首行。'))
        self.assertTrue(result[-1].strip() == '"""')

    def test_empty_line_preserved(self) -> None:
        """多行中空行被保留。"""
        # docstring 文本中的空行应出现在输出行列表里
        result = format_docstring("行一。\n\n行三。", indent=4)
        # 空行应在结果中（作为 '\n'）
        self.assertIn("\n", result)

    def test_indent_applied(self) -> None:
        """缩进正确应用。"""
        # indent=8 时每行应以 8 个空格开头
        result = format_docstring("说明。", indent=8)
        self.assertTrue(result[0].startswith("        "))


class TestInsertDocstring(unittest.TestCase):
    """测试 insert_docstring 插入操作。"""

    def test_inserts_before_first_stmt(self) -> None:
        """docstring 插入到函数 body 第一行之前。"""
        src = "def foo():\n    x = 1\n    return x\n"
        tree = ast.parse(src)
        func_node = find_function_node(tree, "foo")
        lines = src.splitlines(keepends=True)
        new_lines = insert_docstring(lines, func_node, "说明。")
        new_src = "".join(new_lines)
        # docstring 应出现在函数定义之后、x = 1 之前
        idx_def = new_src.index("def foo")
        idx_doc = new_src.index('"""说明。"""')
        idx_stmt = new_src.index("x = 1")
        self.assertLess(idx_def, idx_doc)
        self.assertLess(idx_doc, idx_stmt)

    def test_original_lines_unchanged(self) -> None:
        """已有行不被修改（纯插入）。"""
        src = "def foo():\n    return 42\n"
        tree = ast.parse(src)
        func_node = find_function_node(tree, "foo")
        original_lines = src.splitlines(keepends=True)
        new_lines = insert_docstring(list(original_lines), func_node, "说明。")
        # 原行数 + 新插入行数 = 新行数；原始行内容不变
        self.assertGreater(len(new_lines), len(original_lines))
        # 最后两行应与原始最后两行一致（return 42 未被修改）
        self.assertEqual(new_lines[-1], original_lines[-1])

    def test_method_in_class(self) -> None:
        """类方法也能正确插入。"""
        src = "class A:\n    def m(self):\n        pass\n"
        tree = ast.parse(src)
        func_node = find_function_node(tree, "A.m")
        lines = src.splitlines(keepends=True)
        new_lines = insert_docstring(lines, func_node, "方法说明。")
        new_src = "".join(new_lines)
        self.assertIn('"""方法说明。"""', new_src)


class TestProcessFile(unittest.TestCase):
    """测试 process_file 端到端处理。"""

    def _write_temp(self, content: str) -> Path:
        """创建临时文件并写入内容，返回路径。"""
        # 使用 delete=False 以便在 Windows 上也能读取
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        )
        f.write(content)
        f.close()
        return Path(f.name)

    def test_adds_docstring(self) -> None:
        """正常添加 docstring。"""
        src = "def foo():\n    return 1\n"
        p = self._write_temp(src)
        try:
            added = process_file(p, [{"name": "foo", "docstring": "说明。"}])
            self.assertEqual(added, 1)
            new_src = p.read_text(encoding="utf-8")
            self.assertIn('"""说明。"""', new_src)
            # 原有代码行未被修改
            self.assertIn("return 1", new_src)
        finally:
            p.unlink(missing_ok=True)

    def test_skips_existing_docstring(self) -> None:
        """已有 docstring 时跳过（幂等）。"""
        src = 'def foo():\n    """已有说明。"""\n    return 1\n'
        p = self._write_temp(src)
        try:
            added = process_file(p, [{"name": "foo", "docstring": "新说明。"}])
            self.assertEqual(added, 0)
            # 文件内容应与原始相同
            self.assertEqual(p.read_text(encoding="utf-8"), src)
        finally:
            p.unlink(missing_ok=True)

    def test_skips_missing_function(self) -> None:
        """找不到函数时跳过，不修改文件。"""
        src = "def foo():\n    return 1\n"
        p = self._write_temp(src)
        try:
            added = process_file(p, [{"name": "bar", "docstring": "说明。"}])
            self.assertEqual(added, 0)
            self.assertEqual(p.read_text(encoding="utf-8"), src)
        finally:
            p.unlink(missing_ok=True)

    def test_dry_run_no_write(self) -> None:
        """dry_run 模式不写入文件。"""
        src = "def foo():\n    return 1\n"
        p = self._write_temp(src)
        try:
            added = process_file(
                p, [{"name": "foo", "docstring": "说明。"}], dry_run=True
            )
            self.assertEqual(added, 1)
            # 文件内容不应被修改
            self.assertEqual(p.read_text(encoding="utf-8"), src)
        finally:
            p.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
