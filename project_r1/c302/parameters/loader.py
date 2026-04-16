# =============================================================================
# 功能描述：
#   YAML 参数集加载器，支持参数继承（inherits）、覆盖（parameter_overrides）
#   和删除（parameter_removals，含通配符）机制。ParameterLoader 从
#   data/parameters/ 目录加载 level_*.yaml 文件，解析为 BioParameter 列表。
#
# 类与方法索引：
#   ParameterLoader                       (L30)  — YAML 参数集加载器
#     __init__                            (L32)  — 初始化缓存字典
#     load_raw                            (L37)  — 加载原始 YAML 数据（带缓存）
#     load_parameters                     (L56)  — 加载参数集并处理继承逻辑
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段三：新建 YAML 参数加载器
#
# 当前维护者：Copilot
# =============================================================================
import logging
from pathlib import Path

import yaml

from c302.parameters.bio import BioParameter
from c302.utils.helpers import get_data_dir

logger = logging.getLogger(__name__)


class ParameterLoader:
    """YAML 参数集加载器，支持继承和覆盖机制。"""

    def __init__(self) -> None:
        """初始化加载器，创建缓存字典。"""
        self._cache: dict[str, dict] = {}

    def load_raw(self, level: str) -> dict:
        """加载原始 YAML 数据，带缓存。

        :param level: 参数层级名称（如 ``"A"``、``"C0"``）
        :return: YAML 解析后的字典
        :raises FileNotFoundError: YAML 文件不存在
        """
        # 规范化文件名
        filename = f"level_{level.lower()}.yaml"
        if filename in self._cache:
            return self._cache[filename]

        yaml_path = get_data_dir() / "parameters" / filename
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self._cache[filename] = data
        return data

    def load_parameters(self, level: str) -> list[BioParameter]:
        """加载指定层级的参数集，处理继承逻辑。

        继承机制：
        1. 若 YAML 含 ``inherits`` 键，先递归加载基类参数
        2. 应用 ``parameter_overrides``（覆盖或新增参数）
        3. 应用 ``parameter_removals``（删除参数，支持 ``*`` 前缀通配）

        :param level: 参数层级名称（如 ``"A"``、``"C0"``）
        :return: BioParameter 列表
        """
        data = self.load_raw(level)

        # 处理继承：先加载基类参数
        if "inherits" in data:
            base_level = data["inherits"].replace("level_", "")
            params = self.load_parameters(base_level)
            param_dict = {p.name: p for p in params}

            # 应用覆盖（parameter_overrides 中的参数替换或新增）
            for override in data.get("parameter_overrides", []):
                bp = BioParameter(
                    name=override["name"],
                    value=override["value"],
                    source=override["source"],
                    certainty=override["certainty"],
                )
                param_dict[bp.name] = bp

            # 应用删除（parameter_removals 中的参数移除，支持通配符）
            for removal in data.get("parameter_removals", []):
                if "*" in removal:
                    # 通配符前缀匹配
                    prefix = removal.replace("*", "")
                    to_remove = [k for k in param_dict if k.startswith(prefix)]
                    for k in to_remove:
                        del param_dict[k]
                elif removal in param_dict:
                    del param_dict[removal]

            return list(param_dict.values())

        # 常规加载（无继承）
        return [
            BioParameter(
                name=p["name"],
                value=p["value"],
                source=p["source"],
                certainty=p["certainty"],
            )
            for p in data.get("parameters", [])
        ]
