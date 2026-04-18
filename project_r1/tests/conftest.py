# =============================================================================
# 功能描述：
#   pytest 共享 fixtures，提供测试所需的公共资源和路径。
#
# 类与方法索引：
#   project_root                         (L21)   — 返回项目根目录路径
#   data_dir                             (L27)   — 返回数据目录路径
#   morphology_dir                       (L33)   — 返回形态文件目录路径
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
import pytest

from c302.utils.helpers import get_data_dir, get_morphology_dir, get_project_root


@pytest.fixture(scope="session")
def project_root():
    """返回项目根目录路径。"""
    return get_project_root()


@pytest.fixture(scope="session")
def data_dir():
    """返回数据目录路径。"""
    return get_data_dir()


@pytest.fixture(scope="session")
def morphology_dir():
    """返回形态文件目录路径。"""
    return get_morphology_dir()
