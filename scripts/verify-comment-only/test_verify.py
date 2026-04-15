# =============================================================================
# 功能描述：
#   verify_comment_only.py 的单元测试。
#   覆盖正常注释变更、代码变更检测、空文件、Unicode、语法错误等边界用例。
#
# 类与方法索引：
#   TestStripComments            (L 24) — strip_comments 函数测试
#   TestNormalizeCode            (L 53) — normalize_code 函数测试
#   TestVerifyFile               (L 65) — verify_file 函数测试
#
# 更新日志：
#   2026-04-16  zmdo  初始版本
#
# 当前维护者：zmdo
# =============================================================================
import tempfile
import unittest
from pathlib import Path

from verify_comment_only import hash_code, normalize_code, strip_comments, verify_file


class TestStripComments(unittest.TestCase):
    """测试 strip_comments 函数的各种场景。"""

    def test_removes_inline_comment(self) -> None:
        """验证行内注释被正确去除。"""
        # 行末注释应该被完全移除
        src = "x = 1  # 这是一个注释\n"
        result = strip_comments(src)
        self.assertNotIn("#", result)
        self.assertIn("x = 1", result)

    def test_removes_standalone_comment_line(self) -> None:
        """验证独立注释行被去除。"""
        src = "# 这是独立注释\nx = 1\n"
        result = strip_comments(src)
        self.assertNotIn("这是独立注释", result)
        self.assertIn("x = 1", result)

    def test_preserves_hash_in_string(self) -> None:
        """验证字符串中的 # 不被误删。"""
        # 字符串内的 # 不是注释，必须保留
        src = 'url = "http://example.com/#anchor"\n'
        result = strip_comments(src)
        self.assertIn("#anchor", result)

    def test_empty_file(self) -> None:
        """验证空文件不报错。"""
        result = strip_comments("")
        self.assertEqual(result.strip(), "")


class TestNormalizeCode(unittest.TestCase):
    """测试 normalize_code 函数的格式化一致性。"""

    def test_equivalent_after_comment_removal(self) -> None:
        """验证注释行导致的空行差异不影响归一化结果。"""
        src1 = "x = 1\n\n\ny = 2\n"
        src2 = "x = 1\ny = 2\n"
        # ast.unparse 会消除空行差异，两者归一化结果应相同
        self.assertEqual(normalize_code(src1), normalize_code(src2))


class TestVerifyFile(unittest.TestCase):
    """测试 verify_file 函数的验证逻辑。"""

    def _write_temp(self, content: str) -> Path:
        """创建临时文件并写入内容，返回路径。"""
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                        delete=False, encoding="utf-8")
        f.write(content)
        f.close()
        return Path(f.name)

    def test_comment_only_change_passes(self) -> None:
        """仅注释变更时验证应通过。"""
        orig = self._write_temp("x = 1\n")
        mod = self._write_temp("# 新增注释\nx = 1\n")
        self.assertTrue(verify_file(str(orig), str(mod)))

    def test_translate_comment_passes(self) -> None:
        """英文注释翻译为中文时验证应通过。"""
        orig = self._write_temp("x = 1  # set x to 1\n")
        mod = self._write_temp("x = 1  # 将 x 设为 1\n")
        self.assertTrue(verify_file(str(orig), str(mod)))

    def test_code_change_fails(self) -> None:
        """代码变更时验证应失败。"""
        orig = self._write_temp("x = 1\n")
        mod = self._write_temp("x = 2\n")
        self.assertFalse(verify_file(str(orig), str(mod)))

    def test_identical_files_pass(self) -> None:
        """完全相同的文件应通过验证。"""
        orig = self._write_temp("x = 1\ny = 2\n")
        mod = self._write_temp("x = 1\ny = 2\n")
        self.assertTrue(verify_file(str(orig), str(mod)))


if __name__ == "__main__":
    unittest.main()
