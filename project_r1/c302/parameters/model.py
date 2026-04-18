# =============================================================================
# 功能描述：
#   参数化模型原型基类及各层级子类。ParameterisedModelPrototype 提供参数集合
#   管理（add/get/set）；c302ModelPrototype 在此基础上定义模型创建接口
#   （create_models / create_*_syn / get_*_syn 等）和连接参数查询；
#   各层级 ParameterisedModel 子类实现具体的细胞/突触创建逻辑。
#
# 类与方法索引：
#   ParameterisedModelPrototype          (L50)   — 参数集合管理基类，提供 BioParameter 列表的增删改查
#     __init__                           (L53)   — 创建空的生物参数列表
#     print_                             (L57)   — 带 ``c302`` 前缀的调试输出
#     add_bioparameter                   (L65)   — 注册或更新一个生物参数
#     add_bioparameter_obj               (L89)   — 直接注册 BioParameter 对象，若同名已存在则先移除旧对象
#     get_bioparameter                   (L99)   — 按名称查找生物参数
#     set_bioparameter                   (L118)  — 更新已有参数的值/来源/确定性，参数不存在则静默忽略
#     bioparameter_info                  (L134)  — 返回所有参数的格式化摘要，按名称字典序排列
#   NonNeuroMLCustomType                 (L146)  — 非 NeuroML 自定义突触类型占位符
#     __init__                           (L154)  — 初始化，仅存储 ID
#   c302ModelPrototype                   (L162)  — c302 网络构建原型，定义模型创建接口和连接参数查询
#     __init__                           (L165)  — 初始化模型组件属性为默认空值
#     is_level_A                         (L180)  — 判断层级是否为 A
#     is_level_B                         (L187)  — 判断层级是否为 B
#     is_level_C                         (L194)  — 判断层级是否属于 C 系列
#     is_level_C0                        (L201)  — 判断层级是否为 C0
#     is_level_C2                        (L208)  — 判断层级是否为 C2
#     is_level_D1                        (L215)  — 判断层级是否为 D1
#     is_level_D                         (L222)  — 判断层级是否属于 D 系列
#     is_level_X                         (L229)  — 判断层级是否为 X 系列
#     get_conn_param                     (L236)  — 获取特定连接参数，优先精确匹配，否则返回默认值
#     get_syn                            (L267)  — 按极性分发到对应的突触获取方法
#     create_n_connection_synapse        (L283)  — 幂等注册突触原型到 NeuroML 文档
#     is_nonneuroml_conn                 (L314)  — 判断突触是否为非 NeuroML 自定义类型
#     is_analog_conn                     (L322)  — 判断突触是否为模拟型（GradedSynapse）
#     is_elec_conn                       (L330)  — 判断突触是否为电突触（GapJunction）
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段三：从 bioparameters.py 提取并重写
#
# 当前维护者：Copilot
# =============================================================================
import logging

from neuroml import ExpTwoSynapse, GapJunction, GradedSynapse

from c302.parameters.bio import BioParameter

logger = logging.getLogger(__name__)


class ParameterisedModelPrototype:
    """参数集合管理基类，提供 BioParameter 列表的增删改查。"""

    def __init__(self) -> None:
        """创建空的生物参数列表。"""
        self.bioparameters: list[BioParameter] = []

    def print_(self, msg: str) -> None:
        """带 ``c302`` 前缀的调试输出。

        :param msg: 要输出的消息字符串
        """
        pre = "c302      >>> "
        print("%s %s" % (pre, msg.replace("\n", "\n" + pre)))

    def add_bioparameter(
        self, name: str, value: str, source: str, certainty: str
    ) -> None:
        """注册或更新一个生物参数。

        若同名参数已存在则就地更新；否则创建新对象并追加。

        :param name: 参数名称
        :param value: 参数值字符串（含单位）
        :param source: 数据来源标识
        :param certainty: 确定性等级字符串
        """
        found = False
        # 遍历已有参数，若同名则就地更新
        for bp in self.bioparameters:
            if bp.name == name:
                bp.value = value
                bp.source = source
                bp.certainty = certainty
                found = True
        if not found:
            bp = BioParameter(name, value, source, certainty)
            self.bioparameters.append(bp)

    def add_bioparameter_obj(self, bioparameter: BioParameter) -> None:
        """直接注册 BioParameter 对象，若同名已存在则先移除旧对象。

        :param bioparameter: 要注册的 BioParameter 实例
        """
        for bp in self.bioparameters:
            if bp.name == bioparameter.name:
                self.bioparameters.remove(bp)
        self.bioparameters.append(bioparameter)

    def get_bioparameter(
        self, name: str, warn_if_missing: bool = False
    ) -> BioParameter | None:
        """按名称查找生物参数。

        :param name: 要查找的参数名称
        :param warn_if_missing: 未找到时是否打印警告
        :return: 找到的 BioParameter 对象；未找到返回 None
        """
        for bp in self.bioparameters:
            if bp.name == name:
                return bp
        if warn_if_missing:
            self.print_(
                "Cannot find bioparameter: %s; %i known: %s"
                % (name, len(self.bioparameters), [bp.name for bp in self.bioparameters])
            )
        return None

    def set_bioparameter(
        self, name: str, value: str, source: str, certainty: str
    ) -> None:
        """更新已有参数的值/来源/确定性，参数不存在则静默忽略。

        :param name: 参数名称
        :param value: 新参数值
        :param source: 新来源
        :param certainty: 新确定性
        """
        for bp in self.bioparameters:
            if bp.name == name:
                bp.value = value
                bp.source = source
                bp.certainty = certainty

    def bioparameter_info(self, indent: str = "") -> str:
        """返回所有参数的格式化摘要，按名称字典序排列。

        :param indent: 每行缩进
        :return: 多行格式化字符串
        """
        info = indent + "Known BioParameters:\n"
        for bp in sorted(self.bioparameters, key=lambda x: x.name):
            info += indent + indent + "%s\n" % bp
        return info


class NonNeuroMLCustomType:
    """非 NeuroML 自定义突触类型占位符。

    用于 W2D 等层级中无法用标准 NeuroML 描述的突触。

    :param id: 自定义类型唯一标识符
    """

    def __init__(self, id: str) -> None:
        """初始化，仅存储 ID。

        :param id: 自定义类型标识符
        """
        self.id = id


class c302ModelPrototype(ParameterisedModelPrototype):
    """c302 网络构建原型，定义模型创建接口和连接参数查询。"""

    def __init__(self) -> None:
        """初始化模型组件属性为默认空值。"""
        super().__init__()

        self.level = "Level not yet set"  # 参数层级标识
        self.custom_component_types_definitions = None  # 自定义组件 XML 文件
        self.generic_neuron_cell = None  # 通用神经元细胞模型
        self.generic_muscle_cell = None  # 通用肌肉细胞模型
        self.exc_syn = None  # 兴奋性突触原型
        self.inh_syn = None  # 抑制性突触原型
        self.elec_syn = None  # 电突触原型
        self.offset_current = None  # 偏置电流生成器
        self.concentration_model = None  # 离子浓度模型
        self.found_specific_param = False  # 上次 get_conn_param 是否找到精确参数

    def is_level_A(self) -> bool:
        """判断层级是否为 A。

        :return: True 若 level 以 "A" 开头
        """
        return self.level.startswith("A")

    def is_level_B(self) -> bool:
        """判断层级是否为 B。

        :return: True 若 level 以 "B" 开头
        """
        return self.level.startswith("B")

    def is_level_C(self) -> bool:
        """判断层级是否属于 C 系列。

        :return: True 若 level 以 "C" 开头
        """
        return self.level.startswith("C")

    def is_level_C0(self) -> bool:
        """判断层级是否为 C0。

        :return: True 若 level 为 "C0"
        """
        return self.level == "C0"

    def is_level_C2(self) -> bool:
        """判断层级是否为 C2。

        :return: True 若 level 为 "C2"
        """
        return self.level == "C2"

    def is_level_D1(self) -> bool:
        """判断层级是否为 D1。

        :return: True 若 level 为 "D1"
        """
        return self.level == "D1"

    def is_level_D(self) -> bool:
        """判断层级是否属于 D 系列。

        :return: True 若 level 以 "D" 开头
        """
        return self.level.startswith("D")

    def is_level_X(self) -> bool:
        """判断层级是否为 X 系列。

        :return: True 若 level 以 "X" 开头
        """
        return self.level.startswith("X")

    def get_conn_param(
        self,
        pre_cell: str,
        post_cell: str,
        specific_conn_template: str,
        default_conn_template: str,
        param_name: str,
    ) -> str | None:
        """获取特定连接参数，优先精确匹配，否则返回默认值。

        :param pre_cell: 突触前细胞名称
        :param post_cell: 突触后细胞名称
        :param specific_conn_template: 特定连接格式串（含三个 %s）
        :param default_conn_template: 默认连接格式串（含一个 %s）
        :param param_name: 参数名后缀
        :return: 参数值字符串；均未找到返回 None
        """
        # 尝试精确匹配：如 "ADAL_to_ADAR_elec_syn_gbase"
        param = self.get_bioparameter(
            specific_conn_template % (pre_cell, post_cell, param_name),
            warn_if_missing=False,
        )
        if param:
            self.found_specific_param = True
            return param.value
        # 退回默认：如 "neuron_to_neuron_elec_syn_gbase"
        def_param = self.get_bioparameter(default_conn_template % param_name)
        if not def_param:
            return None
        return def_param.value

    def get_syn(self, pre_cell: str, post_cell: str, conn_type: str, pol: str):
        """按极性分发到对应的突触获取方法。

        :param pre_cell: 突触前细胞名
        :param post_cell: 突触后细胞名
        :param conn_type: 连接类型字符串
        :param pol: 极性："elec" / "exc" / "inh"
        :return: 突触对象
        """
        if pol == "elec":
            return self.get_elec_syn(pre_cell, post_cell, conn_type)
        elif pol == "exc":
            return self.get_exc_syn(pre_cell, post_cell, conn_type)
        elif pol == "inh":
            return self.get_inh_syn(pre_cell, post_cell, conn_type)

    def create_n_connection_synapse(self, prototype_syn, n, nml_doc, existing_synapses):
        """幂等注册突触原型到 NeuroML 文档。

        确保同一 ID 的突触只添加到文档一次。

        :param prototype_syn: 突触原型对象
        :param n: 连接数（仅用于错误消息）
        :param nml_doc: NeuroML 文档对象
        :param existing_synapses: 已注册突触的 ID→对象映射
        :return: 注册的突触原型对象
        :raises Exception: 突触类型不被识别
        """
        if prototype_syn.id in existing_synapses:
            return existing_synapses[prototype_syn.id]

        existing_synapses[prototype_syn.id] = prototype_syn
        if isinstance(prototype_syn, ExpTwoSynapse):
            nml_doc.exp_two_synapses.append(prototype_syn)
        elif isinstance(prototype_syn, GapJunction):
            nml_doc.gap_junctions.append(prototype_syn)
        elif isinstance(prototype_syn, GradedSynapse):
            nml_doc.graded_synapses.append(prototype_syn)
        elif isinstance(prototype_syn, NonNeuroMLCustomType):
            pass  # 非 NeuroML 类型不写入文档
        else:
            info = "%s conns; %s" % (n, existing_synapses)
            del existing_synapses[prototype_syn.id]
            raise Exception("Unknown synapse type: %s (%s)" % (prototype_syn.id, info))

        return prototype_syn

    def is_nonneuroml_conn(self, syn) -> bool:
        """判断突触是否为非 NeuroML 自定义类型。

        :param syn: 突触对象
        :return: True 若为 NonNeuroMLCustomType
        """
        return isinstance(syn, NonNeuroMLCustomType)

    def is_analog_conn(self, syn) -> bool:
        """判断突触是否为模拟型（GradedSynapse）。

        :param syn: 突触对象
        :return: True 若为 GradedSynapse
        """
        return isinstance(syn, GradedSynapse)

    def is_elec_conn(self, syn) -> bool:
        """判断突触是否为电突触（GapJunction）。

        :param syn: 突触对象
        :return: True 若为 GapJunction
        """
        return isinstance(syn, GapJunction)
