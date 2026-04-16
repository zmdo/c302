# =============================================================================
# 功能描述：
#   BioParameter 数据类定义及 NeuroML 数量字符串解析工具。
#   BioParameter 表示单个生物物理参数（含名称、值、来源、确定性），
#   提供数值修改和提取方法。split_neuroml_quantity() 将含单位的
#   NeuroML 量字符串拆分为 (数值, 单位) 元组。
#
# 类与方法索引：
#   split_neuroml_quantity                (L30)  — 将 NeuroML 数量字符串拆分为 (数值, 单位) 元组
#   BioParameter                          (L53)  — 生物物理参数数据类
#     __init__                            (L68)  — 初始化参数，存储名称、值、来源和确定性
#     __str__                             (L82)  — 返回人类可读的参数字符串表示
#     __repr__                            (L93)  — 返回与 __str__ 相同的调试表示
#     change_magnitude                    (L97)  — 用 Decimal 精度替换参数数值部分，保留单位
#     x                                   (L112) — 以 float 返回参数数值部分（去除单位）
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段三：从 bioparameters.py 提取并重写
#
# 当前维护者：Copilot
# =============================================================================
from decimal import Decimal


def split_neuroml_quantity(quantity: str) -> tuple[float, str]:
    """将 NeuroML 数量字符串拆分为 (数值, 单位) 元组。

    从右向左逐字符截断，尝试将前缀解析为 float 来定位数值与单位的分界点。
    例如 ``"0.01 nS"`` → ``(0.01, "nS")``，``"-50mV"`` → ``(-50.0, "mV")``。

    :param quantity: NeuroML 格式的数量字符串，如 ``"3 ms"``、``"1 uF_per_cm2"``
    :return: ``(magnitude, unit)`` 元组；magnitude 为 float，unit 为单位字符串
    """
    # 从字符串末尾开始向左截断，逐步缩短候选数值前缀
    i = len(quantity)
    while i > 0:
        magnitude = quantity[0:i].strip()  # 候选数值字符串
        unit = quantity[i:].strip()  # 候选单位字符串
        try:
            magnitude = float(magnitude)  # 若前缀可解析为 float，则找到分界点
            i = 0  # 退出循环
        except ValueError:
            i -= 1  # 无法解析，继续向左截断
    return magnitude, unit


class BioParameter:
    """生物物理参数。

    存储单个参数的名称、含单位的值字符串、数据来源和确定性等级。
    提供数值修改（change_magnitude）和数值提取（x 属性）方法。

    :param name: 参数名称，如 ``"neuron_iaf_thresh"``
    :param value: 参数值字符串（含单位），如 ``"-30mV"``
    :param source: 数据来源标识，如 ``"BlindGuess"``
    :param certainty: 确定性等级字符串，如 ``"0.1"``
    """

    def __init__(self, name: str, value: str, source: str, certainty: str) -> None:
        """初始化参数，存储名称、值、来源和确定性。

        :param name: 参数名称
        :param value: 参数值字符串（含单位）
        :param source: 数据来源标识
        :param certainty: 确定性等级字符串
        """
        self.name = name  # 参数名称，如 "neuron_iaf_thresh"
        self.value = value  # 参数值字符串（含单位），如 "-30mV"
        self.source = source  # 数据来源，如 "BlindGuess"
        self.certainty = certainty  # 确定性等级 0-1

    def __str__(self) -> str:
        """返回人类可读的参数字符串表示。

        :return: 格式为 ``"BioParameter: name = value (SRC: source, certainty N)"``
        """
        return "BioParameter: %s = %s (SRC: %s, certainty %s)" % (
            self.name,
            self.value,
            self.source,
            self.certainty,
        )

    def __repr__(self) -> str:
        """返回与 __str__ 相同的调试表示。

        :return: 与 __str__ 相同的字符串
        """
        return self.__str__()

    def change_magnitude(self, magnitude) -> None:
        """用 Decimal 精度替换参数数值部分，保留单位。

        :param magnitude: 新的数值（float 或数字字符串）
        """
        self.value = "%s %s" % (
            Decimal(magnitude),
            split_neuroml_quantity(self.value)[1],
        )

    def x(self) -> float:
        """以 float 返回参数数值部分（去除单位）。

        :return: 参数数值的浮点表示
        """
        return split_neuroml_quantity(self.value)[0]
