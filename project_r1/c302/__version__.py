# =============================================================================
# 功能描述：
#   运行时版本导出模块。从包元数据中读取由 setuptools-scm 生成的版本号，
#   对外提供 __version__ 字符串供其他模块和用户引用。
#
# 类与方法索引：
#   __version__                      (L17)   — 包版本号字符串常量
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
from importlib.metadata import PackageNotFoundError, version

try:
    # 从已安装包的元数据中读取版本号
    __version__: str = version("c302")
except PackageNotFoundError:
    # 未安装时回退为开发版本标识
    __version__: str = "0.0.0.dev0"
