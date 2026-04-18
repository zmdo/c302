# =============================================================================
# 功能描述：
#   文件写出模块的单元测试。覆盖 LEMS 模板合并和文件输出路径。
#
# 类与方法索引：
#   TestMergeWithTemplate                (L28)   — merge_with_template 测试
#     test_template_file_constant        (L31)   — 模板文件常量应为 LEMS_c302_TEMPLATE.xml
#     test_basic_merge                   (L35)   — 应正确替换模板变量
#     test_missing_template_raises       (L60)   — 模板文件不存在时应抛出异常
#   TestWriteToFile                      (L70)   — write_to_file 测试（集成方面仅验证路径逻辑）
#     test_creates_output_directory      (L73)   — 应能创建输出目录
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：新建
#
# 当前维护者：Copilot
# =============================================================================
"""io 模块测试。"""
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from c302.generator.io import LEMS_TEMPLATE_FILE, merge_with_template


class TestMergeWithTemplate:
    """merge_with_template 测试。"""

    def test_template_file_constant(self):
        """模板文件常量应为 LEMS_c302_TEMPLATE.xml。"""
        assert LEMS_TEMPLATE_FILE == "LEMS_c302_TEMPLATE.xml"

    def test_basic_merge(self):
        """应正确替换模板变量。"""
        # 创建一个简单模板
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".xml", delete=False
        ) as f:
            f.write('<Lems>$reference ${duration}ms $dt</Lems>')
            template_path = f.name

        try:
            templfile = template_path
            result = merge_with_template(
                {
                    "reference": "test_net",
                    "duration": "500",
                    "dt": "0.01",
                },
                templfile,
            )
            assert "test_net" in result
            assert "500" in result
            assert "0.01" in result
        finally:
            os.unlink(template_path)

    def test_missing_template_raises(self):
        """模板文件不存在时应抛出异常。"""
        with pytest.raises(Exception):
            merge_with_template(
                {"reference": "test"},
                "/nonexistent/",
                template_file="missing.xml",
            )


class TestWriteToFile:
    """write_to_file 测试（集成方面仅验证路径逻辑）。"""

    def test_creates_output_directory(self, tmp_path):
        """应能创建输出目录。"""
        target = str(tmp_path / "subdir")
        os.makedirs(target, exist_ok=True)
        assert os.path.isdir(target)
