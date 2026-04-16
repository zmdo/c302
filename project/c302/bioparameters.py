# =============================================================================
# 功能描述：
#   c302 框架的核心参数系统。定义 BioParameter 数据类和参数化模型原型
#   （ParameterisedModelPrototype / c302ModelPrototype），提供参数注册、
#   查询、更新机制以及多层级细胞和突触模型的抽象接口。
#
# 类与方法索引：
#   split_neuroml_quantity               (L56)   — 将 NeuroML 数量字符串分解为数值与单位两部分
#   BioParameter                         (L78)   — BioParameter 类
#     __init__                           (L79)   — 初始化生物参数对象，存储名称、数值字符串、来源及确定性信息
#     __str__                            (L92)   — 返回参数的人类可读字符串表示，包含名称、值、来源和确定性
#     __repr__                           (L104)  — 返回与 ``__str__`` 相同的调试表示，便于在容器中查看
#     change_magnitude                   (L111)  — 更新参数的数值部分，保留原有单位不变
#     x                                  (L123)  — 以 float 形式返回参数的数值（去除单位）
#   ParameterisedModelPrototype          (L131)  — ParameterisedModelPrototype 类
#     __init__                           (L134)  — 初始化参数化模型原型，创建空的生物参数列表
#     print_                             (L138)  — 带 ``c302`` 前缀的调试输出，用于区分 c302 框架自身的日志信息
#     add_bioparameter                   (L146)  — 注册或更新一个生物参数
#     add_bioparameter_obj               (L170)  — 直接注册 ``BioParameter`` 对象，若同名已存在则先移除旧对象
#     get_bioparameter                   (L183)  — 按名称查找生物参数，返回第一个匹配项
#     set_bioparameter                   (L204)  — 更新已有生物参数的值、来源和确定性，若参数不存在则静默忽略
#     bioparameter_info                  (L218)  — 返回所有已注册生物参数的格式化摘要字符串，按名称字典序排列
#   NonNeuroMLCustomType                 (L230)  — NonNeuroMLCustomType 类
#     __init__                           (L231)  — 初始化非 NeuroML 自定义突触类型，仅存储 ID
#   c302ModelPrototype                   (L242)  — c302ModelPrototype 类
#     __init__                           (L243)  — 初始化 c302 网络构建原型，设置各网络组件属性的默认空值
#     is_level_A                         (L264)  — 判断当前参数层级是否为 A（积分放电神经元 + 事件突触）
#     is_level_B                         (L273)  — 判断当前参数层级是否为 B（带 activity 变量的积分放电 + 真实缝隙连接）
#     is_level_C                         (L282)  — 判断当前参数层级是否属于 C 系列（单室导电模型 + HH 型离子通道）
#     is_level_C0                        (L291)  — 判断是否为 C0（简化导电模型，无快钾通道，模拟突触，适合非放电神经元）
#     is_level_C2                        (L298)  — 判断是否为 C2（含专有缝隙连接类型和本体感觉反馈的高级导电模型）
#     is_level_D1                        (L305)  — 判断是否为 D1（多室导电模型 + 模拟突触变体）
#     is_level_D                         (L312)  — 判断是否属于 D 系列（多室导电模型，含细胞形态数据）
#     is_level_X                         (L321)  — 判断是否为 X 系列（扩展或实验性层级）
#     get_conn_param                     (L328)  — 获取特定细胞对连接的参数值，优先返回精确匹配，否则返回默认模板值
#     get_syn                            (L360)  — 根据突触极性类型（``pol``）分发到对应的突触获取方法
#     create_n_connection_synapse        (L379)  — 获取或注册突触原型对象，确保同一 ID 的突触只添加到文档一次（幂等）
#     is_nonneuroml_conn                 (L413)  — 判断突触是否为非 NeuroML 自定义类型（如 W2D 的 OutputSynapse）
#     is_analog_conn                     (L423)  — 判断突触是否为模拟（连续传递）型突触（GradedSynapse）
#     is_elec_conn                       (L434)  — 判断突触是否为电突触（缝隙连接，GapJunction）
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释（计划1阶段三）
#
# 当前维护者：Copilot
# =============================================================================
from decimal import Decimal

from neuroml import ExpTwoSynapse, GapJunction, GradedSynapse

"""
    Subject to much change & refactoring once owmeta is stable...
"""


def split_neuroml_quantity(quantity):
    """将 NeuroML 数量字符串分解为数值与单位两部分。

    例如 ``"0.01 nS"`` → ``(0.01, "nS")``，``"-50mV"`` → ``(-50.0, "mV")``。
    通过从右到左逐字符截断尝试将前缀解析为 float 来定位分界点。

    :param quantity: NeuroML 格式的数量字符串，如 ``"3 ms"``、``"1 uF_per_cm2"``
    :return: ``(magnitude, unit)`` 元组；magnitude 为 float，unit 为单位字符串
    """
    i = len(quantity)  # 从字符串末尾开始向左截断，逐步缩短候选数值前缀
    while i > 0:
        magnitude = quantity[0:i].strip()  # 候选数值字符串
        unit = quantity[i:].strip()  # 候选单位字符串

        try:
            magnitude = float(magnitude)  # 若前缀可解析为 float，则已找到分界点
            i = 0  # 退出循环
        except ValueError:
            i -= 1  # 无法解析，继续向左截断
    return magnitude, unit


class BioParameter:
    def __init__(self, name, value, source, certainty):
        """初始化生物参数对象，存储名称、数值字符串、来源及确定性信息。

        :param name: 参数名称，如 ``"neuron_iaf_thresh"``
        :param value: 参数值字符串，含单位，如 ``"-30mV"``
        :param source: 数据来源标识，如 ``"BlindGuess"``、``"Experimental"``
        :param certainty: 确定性等级，0（完全未知）到 1（完全确定），通常为字符串 ``"0.1"``
        """
        self.name = name  # 参数名称，如 "neuron_iaf_thresh"
        self.value = value  # 参数值字符串（含单位），如 "-30mV"
        self.source = source  # 数据来源，如 "BlindGuess"（盲猜）或 "Experimental"
        self.certainty = certainty  # 确定性等级 0-1，"0.1" 表示低确定性

    def __str__(self):
        """返回参数的人类可读字符串表示，包含名称、值、来源和确定性。

        :return: 格式为 ``"BioParameter: name = value (SRC: source, certainty N)"`` 的字符串
        """
        return "BioParameter: %s = %s (SRC: %s, certainty %s)" % (
            self.name,
            self.value,
            self.source,
            self.certainty,
        )

    def __repr__(self):
        """返回与 ``__str__`` 相同的调试表示，便于在容器中查看。

        :return: 与 ``__str__`` 相同的字符串
        """
        return self.__str__()

    def change_magnitude(self, magnitude):
        """更新参数的数值部分，保留原有单位不变。

        先将 magnitude 转换为 ``Decimal`` 以保留精度，再拼接原始单位字符串。

        :param magnitude: 新的数值（float 或数字字符串）
        """
        self.value = "%s %s" % (
            Decimal(magnitude),
            split_neuroml_quantity(self.value)[1],
        )

    def x(self):
        """以 float 形式返回参数的数值（去除单位）。

        :return: 参数数值的浮点表示
        """
        return split_neuroml_quantity(self.value)[0]


class ParameterisedModelPrototype(object):
    # [备选] 以下为旧版类变量写法，当前已改为在 __init__ 中用实例属性替代
    # bioparameters = []
    def __init__(self):
        """初始化参数化模型原型，创建空的生物参数列表。"""
        self.bioparameters = []

    def print_(self, msg):
        """带 ``c302`` 前缀的调试输出，用于区分 c302 框架自身的日志信息。

        :param msg: 要输出的消息字符串，支持多行（每行均加前缀）
        """
        pre = "c302      >>> "
        print("%s %s" % (pre, msg.replace("\n", "\n" + pre)))

    def add_bioparameter(self, name, value, source, certainty):
        """注册或更新一个生物参数。

        若同名参数已存在，则就地更新其值、来源和确定性；
        若不存在，则创建新的 ``BioParameter`` 对象并追加到列表末尾。

        :param name: 参数名称
        :param value: 参数值字符串（含单位）
        :param source: 数据来源标识
        :param certainty: 确定性等级字符串
        """
        found = False
        # 遍历已有参数，若同名则就地更新（不重复添加）
        for bp in self.bioparameters:
            if bp.name == name:
                bp.value = value
                bp.source = source
                bp.certainty = certainty
                found = True
        if not found:
            # 参数不存在时创建新对象并追加到列表末尾
            bp = BioParameter(name, value, source, certainty)
            self.bioparameters.append(bp)

    def add_bioparameter_obj(self, bioparameter):
        """直接注册 ``BioParameter`` 对象，若同名已存在则先移除旧对象。

        与 ``add_bioparameter`` 的区别在于直接接受对象，适合复制另一模型的参数。

        :param bioparameter: 要注册的 ``BioParameter`` 实例
        """
        for bp in self.bioparameters:
            if bp.name == bioparameter.name:
                self.bioparameters.remove(bp)

        self.bioparameters.append(bioparameter)

    def get_bioparameter(self, name, warn_if_missing=False):
        """按名称查找生物参数，返回第一个匹配项。

        :param name: 要查找的参数名称
        :param warn_if_missing: 为 ``True`` 时若未找到则打印警告信息
        :return: 找到的 ``BioParameter`` 对象；未找到时返回 ``None``
        """
        for bp in self.bioparameters:
            if bp.name == name:
                return bp
        if warn_if_missing:
            self.print_(
                "Cannot find bioparameter: %s; %i known: %s"
                % (
                    name,
                    len(self.bioparameters),
                    [bp.name for bp in self.bioparameters],
                )
            )
        return None

    def set_bioparameter(self, name, value, source, certainty):
        """更新已有生物参数的值、来源和确定性，若参数不存在则静默忽略。

        :param name: 参数名称
        :param value: 新的参数值字符串
        :param source: 新的数据来源
        :param certainty: 新的确定性等级
        """
        for bp in self.bioparameters:
            if bp.name == name:
                bp.value = value
                bp.source = source
                bp.certainty = certainty

    def bioparameter_info(self, indent=""):
        """返回所有已注册生物参数的格式化摘要字符串，按名称字典序排列。

        :param indent: 每行的缩进字符串，默认为空字符串
        :return: 包含全部参数信息的多行字符串
        """
        info = indent + "Known BioParameters:\n"
        for bp in sorted(self.bioparameters, key=lambda x: x.name):
            info += indent + indent + "%s\n" % bp
        return info


class NonNeuroMLCustomType:
    def __init__(self, id):
        """初始化非 NeuroML 自定义突触类型，仅存储 ID。

        用于表示无法用标准 NeuroML 元素描述的特殊突触类型（如 W2D 的 OutputSynapse），
        在 ``create_n_connection_synapse`` 中会特判此类型跳过 NeuroML 文档注册。

        :param id: 自定义类型的唯一标识符
        """
        self.id = id


class c302ModelPrototype(ParameterisedModelPrototype):
    def __init__(self):
        """初始化 c302 网络构建原型，设置各网络组件属性的默认空值。

        各属性将由子类的 ``create_models()`` 方法填充：
        ``generic_neuron_cell``、``generic_muscle_cell`` 为细胞模型；
        ``exc_syn``、``inh_syn``、``elec_syn`` 为三类突触；
        ``offset_current`` 为偏置电流生成器。
        """
        super(c302ModelPrototype, self).__init__()

        self.level = "Level not yet set"  # 参数层级标识，如 "A", "B", "C", "D"
        self.custom_component_types_definitions = None  # 自定义组件 XML 文件（如 "cell_C.xml"）
        self.generic_neuron_cell = None  # 通用神经元细胞模型
        self.generic_muscle_cell = None  # 通用肌肉细胞模型
        self.exc_syn = None  # 兴奋性突触原型（已废弃，由 get_exc_syn() 动态生成）
        self.inh_syn = None  # 抑制性突触原型（已废弃，由 get_inh_syn() 动态生成）
        self.elec_syn = None  # 电突触原型（已废弃，由 get_elec_syn() 动态生成）
        self.offset_current = None  # 偏置电流生成器（PulseGenerator）
        self.concentration_model = None  # 离子浓度模型（Level C/D 的 Ca²⁺ 动力学）
        self.found_specific_param = False  # 标志位：上一次 get_conn_param() 是否找到了精确参数

    def is_level_A(self):
        """判断当前参数层级是否为 A（积分放电神经元 + 事件突触）。

        Level A 是最简单的层级，适合快速连接组探索但不具生物真实性。

        :return: ``True`` 若 level 以 ``"A"`` 开头
        """
        return self.level.startswith("A")

    def is_level_B(self):
        """判断当前参数层级是否为 B（带 activity 变量的积分放电 + 真实缝隙连接）。

        Level B 在 A 的基础上引入了 activity 状态变量和真实 GapJunction 连接。

        :return: ``True`` 若 level 以 ``"B"`` 开头
        """
        return self.level.startswith("B")

    def is_level_C(self):
        """判断当前参数层级是否属于 C 系列（单室导电模型 + HH 型离子通道）。

        包含 C、C0、C1、C2 所有变体，用于需要离子通道动力学的场景。

        :return: ``True`` 若 level 以 ``"C"`` 开头
        """
        return self.level.startswith("C")

    def is_level_C0(self):
        """判断是否为 C0（简化导电模型，无快钾通道，模拟突触，适合非放电神经元）。

        :return: ``True`` 若 level 为精确字符串 ``"C0"``
        """
        return self.level == "C0"

    def is_level_C2(self):
        """判断是否为 C2（含专有缝隙连接类型和本体感觉反馈的高级导电模型）。

        :return: ``True`` 若 level 为精确字符串 ``"C2"``
        """
        return self.level == "C2"

    def is_level_D1(self):
        """判断是否为 D1（多室导电模型 + 模拟突触变体）。

        :return: ``True`` 若 level 为精确字符串 ``"D1"``
        """
        return self.level == "D1"

    def is_level_D(self):
        """判断是否属于 D 系列（多室导电模型，含细胞形态数据）。

        多室模型对细胞内阻抗敏感，存在内阻高低权衡问题，见 GitHub #71。

        :return: ``True`` 若 level 以 ``"D"`` 开头
        """
        return self.level.startswith("D")

    def is_level_X(self):
        """判断是否为 X 系列（扩展或实验性层级）。

        :return: ``True`` 若 level 以 ``"X"`` 开头
        """
        return self.level.startswith("X")

    def get_conn_param(
        self,
        pre_cell,
        post_cell,
        specific_conn_template,
        default_conn_template,
        param_name,
    ):
        """获取特定细胞对连接的参数值，优先返回精确匹配，否则返回默认模板值。

        查找顺序：先检查形如 ``"ADAL_to_ADAR_elec_syn_gbase"`` 的精确参数；
        若无精确参数则退回到形如 ``"neuron_to_neuron_elec_syn_gbase"`` 的默认参数。

        :param pre_cell: 突触前细胞名称，如 ``"ADAL"``
        :param post_cell: 突触后细胞名称，如 ``"ADAR"``
        :param specific_conn_template: 特定连接格式串，含三个 ``%s`` 占位符（pre, post, param）
        :param default_conn_template: 默认连接格式串，含一个 ``%s`` 占位符（param）
        :param param_name: 参数名后缀，如 ``"gbase"``、``"erev"``
        :return: 参数值字符串；若均未找到则返回 ``None``
        """
        param = self.get_bioparameter(
            specific_conn_template % (pre_cell, post_cell, param_name),
            warn_if_missing=False,
        )
        if param:
            self.found_specific_param = True
            return param.value
        def_param = self.get_bioparameter(default_conn_template % param_name)
        if not def_param:
            return None
        return def_param.value

    def get_syn(self, pre_cell, post_cell, type, pol):
        """根据突触极性类型（``pol``）分发到对应的突触获取方法。

        突触 ID 命名规则：``{pre_type}_to_{post_type}_{pol}_syn``，
        如 ``"neuron_to_neuron_elec_syn"``、``"neuron_to_muscle_exc_syn"``。

        :param pre_cell: 突触前细胞名
        :param post_cell: 突触后细胞名
        :param type: 连接类型字符串，如 ``"neuron_to_neuron"``
        :param pol: 极性，取值 ``"elec"``（电突触）、``"exc"``（兴奋性）、``"inh"``（抑制性）
        :return: 对应的突触对象（``GapJunction``、``ExpTwoSynapse`` 或 ``GradedSynapse``）
        """
        if pol == "elec":
            return self.get_elec_syn(pre_cell, post_cell, type)
        elif pol == "exc":
            return self.get_exc_syn(pre_cell, post_cell, type)
        elif pol == "inh":
            return self.get_inh_syn(pre_cell, post_cell, type)

    def create_n_connection_synapse(self, prototype_syn, n, nml_doc, existing_synapses):
        """获取或注册突触原型对象，确保同一 ID 的突触只添加到文档一次（幂等）。

        当多个细胞对共享相同突触参数时，通过 ``existing_synapses`` 字典缓存原型，
        避免在 NeuroML 文档中重复注册相同 ID 的突触元素。

        :param prototype_syn: 突触原型对象（``ExpTwoSynapse``、``GapJunction`` 或 ``GradedSynapse``）
        :param n: 连接数（仅用于错误消息，不影响逻辑）
        :param nml_doc: NeuroML 文档对象，用于注册新突触
        :param existing_synapses: 已注册突触的 ID→对象 映射字典（可变，会被修改）
        :return: 已注册或输入的突触原型对象
        :raises Exception: 若突触类型不被识别
        """
        if prototype_syn.id in existing_synapses:
            # 突触已注册，直接返回缓存对象（避免重复添加到 NeuroML 文档）
            return existing_synapses[prototype_syn.id]

        # 首次注册：加入缓存后按类型追加到对应 NeuroML 文档集合
        existing_synapses[prototype_syn.id] = prototype_syn
        if isinstance(prototype_syn, ExpTwoSynapse):
            nml_doc.exp_two_synapses.append(prototype_syn)  # 双指数事件突触
        elif isinstance(prototype_syn, GapJunction):
            nml_doc.gap_junctions.append(prototype_syn)  # 缝隙连接（电突触）
        elif isinstance(prototype_syn, GradedSynapse):
            nml_doc.graded_synapses.append(prototype_syn)  # 模拟连续突触
        elif isinstance(prototype_syn, NonNeuroMLCustomType):
            pass  # 非 NeuroML 自定义类型：不写入文档，由各参数层级自行管理
        else:
            info = "%s conns; %s" % (n, existing_synapses)
            del existing_synapses[prototype_syn.id]  # 回滚缓存注册
            raise Exception("Unknown synapse type: %s (%s)" % (prototype_syn.id, info))

        return prototype_syn

    def is_nonneuroml_conn(self, syn):
        """判断突触是否为非 NeuroML 自定义类型（如 W2D 的 OutputSynapse）。

        非 NeuroML 突触不会被写入 NeuroML 文档，由参数层级自定义处理。

        :param syn: 突触对象
        :return: ``True`` 若为 ``NonNeuroMLCustomType`` 实例
        """
        return isinstance(syn, NonNeuroMLCustomType)

    def is_analog_conn(self, syn):
        """判断突触是否为模拟（连续传递）型突触（GradedSynapse）。

        模拟突触的传递量连续依赖于突触前膜电位，无需动作电位触发，
        适合非放电神经元（Level C0、C1、BC1）。

        :param syn: 突触对象
        :return: ``True`` 若为 ``GradedSynapse`` 实例
        """
        return isinstance(syn, GradedSynapse)

    def is_elec_conn(self, syn):
        """判断突触是否为电突触（缝隙连接，GapJunction）。

        电突触在两细胞间双向传导电流，强度与膜电位差成正比，
        是 Level B 及以上层级的真实缝隙连接实现。

        :param syn: 突触对象
        :return: ``True`` 若为 ``GapJunction`` 实例
        """
        return isinstance(syn, GapJunction)
