# =============================================================================
# 功能描述：
#   所有层级模型的基类 _ModelBase，从 YAML 加载生物参数并提供模板方法。
#   子类通过设置类属性（_exc_syn_cls / _inh_syn_cls / _elec_syn_cls /
#   _exc_param_fields / _inh_param_fields / _chem_prefix 等）控制
#   create_neuron_to_neuron_syn / create_neuron_to_muscle_syn /
#   get_exc_syn / get_inh_syn / get_elec_syn 的行为。
#   _GradedSynapse2Mixin 为使用 GradedSynapse2 的层级提供
#   create_n_connection_synapse 和 is_analog_conn 共享方法。
#
# 类与方法索引：
#   _ModelBase                           (L43)   — 所有层级模型的基类，从 YAML 加载生物参数
#     __init__                           (L71)   — 加载 YAML 参数并初始化基类
#     _build_syn_from_params             (L92)   — 根据参数字段从 BioParameter 查找值并构造突触对象
#     _build_elec_syn_from_params        (L124)  — 构造电突触对象
#     create_neuron_to_neuron_syn        (L147)  — 创建神经元间突触（模板方法）
#     create_neuron_to_muscle_syn        (L175)  — 创建神经元到肌肉突触（模板方法）
#     get_exc_syn                        (L201)  — 获取兴奋性化学突触（模板方法）
#     get_inh_syn                        (L244)  — 获取抑制性化学突触（模板方法）
#     get_elec_syn                       (L286)  — 获取电突触（模板方法）
#     _get_elec_syn_params               (L309)  — 提取电突触连接参数（gbase + conn_id）
#   _GradedSynapse2Mixin                 (L352)  — 为使用 GradedSynapse2 的层级（C0, D1）提供共享方法
#     create_n_connection_synapse        (L358)  — 注册突触原型（含 GradedSynapse2 支持）
#     is_analog_conn                     (L381)  — 判断是否为模拟连接（含 GradedSynapse2）
#
# 更新日志：
#   2026-04-19  Copilot  计划5阶段二：从 factory.py 提取基类
#
# 当前维护者：Copilot
# =============================================================================
"""参数工厂基类与混入。"""
import logging

from neuroml import ExpTwoSynapse, GapJunction, GradedSynapse

from c302.parameters.custom_types import GradedSynapse2
from c302.parameters.loader import ParameterLoader
from c302.parameters.model import c302ModelPrototype

logger = logging.getLogger(__name__)


class _ModelBase(c302ModelPrototype):
    """所有层级模型的基类，从 YAML 加载生物参数。

    子类通过覆盖以下类属性控制模板方法行为：

    - ``_exc_syn_cls`` / ``_inh_syn_cls``：化学突触类
    - ``_elec_syn_cls``：电突触类（GapJunction 或 ExpTwoSynapse）
    - ``_exc_param_fields`` / ``_inh_param_fields``：参数字段元组
    - ``_exc_param_to_kwarg`` / ``_inh_param_to_kwarg``：字段→构造参数映射
    - ``_chem_prefix``：参数名化学前缀（ExpTwoSynapse 用 ``"chem_"``，其余用 ``""``）
    """

    # -- 突触类配置（子类覆盖） --
    _exc_syn_cls: type = ExpTwoSynapse
    _inh_syn_cls: type = ExpTwoSynapse
    _elec_syn_cls: type = GapJunction

    # -- 参数字段（子类覆盖） --
    _exc_param_fields: tuple[str, ...] = ("gbase", "erev", "decay", "rise")
    _inh_param_fields: tuple[str, ...] = ("gbase", "erev", "decay", "rise")

    # -- 字段名→构造参数名映射 --
    _exc_param_to_kwarg: dict[str, str] | None = {"decay": "tau_decay", "rise": "tau_rise"}
    _inh_param_to_kwarg: dict[str, str] | None = {"decay": "tau_decay", "rise": "tau_rise"}

    # -- 参数名化学前缀 --
    _chem_prefix: str = "chem_"

    def __init__(self, level: str) -> None:
        """加载 YAML 参数并初始化基类。

        :param level: 参数层级标识
        """
        super().__init__()
        self.level = level

        # 从 YAML 加载生物参数
        loader = ParameterLoader()
        for bp in loader.load_parameters(level):
            self.add_bioparameter_obj(bp)

        # 加载元数据（如 custom_component_types_definitions）
        raw = loader.load_raw(level)
        self.custom_component_types_definitions = raw.get(
            "custom_component_types_definitions"
        )

    # -- 辅助构造方法 --

    def _build_syn_from_params(
        self,
        syn_cls: type,
        primary_template: str,
        common_template: str,
        param_fields: tuple[str, ...],
        param_to_kwarg: dict[str, str] | None = None,
    ) -> object:
        """根据参数字段从 BioParameter 查找值并构造突触对象。

        :param syn_cls: 突触类（如 ExpTwoSynapse, GradedSynapse）
        :param primary_template: 首字段参数名模板（含连接类型前缀）
        :param common_template: 后续字段参数名模板（共享前缀）
        :param param_fields: 参数字段名元组
        :param param_to_kwarg: 字段名→构造参数名映射
        :return: 突触对象实例
        """
        kwargs: dict[str, str] = {}
        for i, field in enumerate(param_fields):
            # 首字段使用连接类型前缀模板，后续字段使用共享模板
            template = primary_template if i == 0 else common_template
            bp = self.get_bioparameter(template % field)
            if bp:
                # 映射字段名到构造参数名（如 decay→tau_decay）
                kwarg_name = field
                if param_to_kwarg and field in param_to_kwarg:
                    kwarg_name = param_to_kwarg[field]
                kwargs[kwarg_name] = bp.value
        # id = 主模板去掉尾部 _%s 并移除 chem_ 前缀
        syn_id = primary_template.replace("_%s", "").replace("chem_", "")
        return syn_cls(id=syn_id, **kwargs)

    def _build_elec_syn_from_params(self, prefix: str) -> object:
        """构造电突触对象。

        :param prefix: 连接类型前缀（如 ``"neuron_to_neuron"``）
        :return: GapJunction 或 ExpTwoSynapse 实例
        """
        gbase = self.get_bioparameter(f"{prefix}_elec_syn_gbase").value
        if self._elec_syn_cls is GapJunction:
            return GapJunction(id=f"{prefix}_elec_syn", conductance=gbase)
        # ExpTwoSynapse（Level A 的假电突触）
        erev = self.get_bioparameter("elec_syn_erev").value
        decay = self.get_bioparameter("elec_syn_decay").value
        rise = self.get_bioparameter("elec_syn_rise").value
        return ExpTwoSynapse(
            id=f"{prefix}_elec_syn",
            gbase=gbase,
            erev=erev,
            tau_decay=decay,
            tau_rise=rise,
        )

    # -- 模板方法：create_neuron_to_neuron_syn / create_neuron_to_muscle_syn --

    def create_neuron_to_neuron_syn(self) -> None:
        """创建神经元间突触（模板方法）。

        子类通过类属性 ``_exc_syn_cls`` / ``_inh_syn_cls`` / ``_elec_syn_cls``
        以及 ``_chem_prefix`` / ``_exc_param_fields`` 等控制具体行为。
        """
        chem = self._chem_prefix
        # 兴奋性化学突触
        self.neuron_to_neuron_exc_syn = self._build_syn_from_params(
            self._exc_syn_cls,
            f"neuron_to_neuron_{chem}exc_syn_%s",
            f"{chem}exc_syn_%s",
            self._exc_param_fields,
            self._exc_param_to_kwarg,
        )
        # 抑制性化学突触
        self.neuron_to_neuron_inh_syn = self._build_syn_from_params(
            self._inh_syn_cls,
            f"neuron_to_neuron_{chem}inh_syn_%s",
            f"{chem}inh_syn_%s",
            self._inh_param_fields,
            self._inh_param_to_kwarg,
        )
        # 电突触
        self.neuron_to_neuron_elec_syn = self._build_elec_syn_from_params(
            "neuron_to_neuron"
        )

    def create_neuron_to_muscle_syn(self) -> None:
        """创建神经元到肌肉突触（模板方法）。"""
        chem = self._chem_prefix
        # 兴奋性化学突触
        self.neuron_to_muscle_exc_syn = self._build_syn_from_params(
            self._exc_syn_cls,
            f"neuron_to_muscle_{chem}exc_syn_%s",
            f"{chem}exc_syn_%s",
            self._exc_param_fields,
            self._exc_param_to_kwarg,
        )
        # 抑制性化学突触
        self.neuron_to_muscle_inh_syn = self._build_syn_from_params(
            self._inh_syn_cls,
            f"neuron_to_muscle_{chem}inh_syn_%s",
            f"{chem}inh_syn_%s",
            self._inh_param_fields,
            self._inh_param_to_kwarg,
        )
        # 电突触
        self.neuron_to_muscle_elec_syn = self._build_elec_syn_from_params(
            "neuron_to_muscle"
        )

    # -- 模板方法：get_exc_syn / get_inh_syn / get_elec_syn --

    def get_exc_syn(self, pre_cell, post_cell, type):
        """获取兴奋性化学突触（模板方法）。

        子类通过 ``_exc_syn_cls`` / ``_exc_param_fields`` /
        ``_exc_param_to_kwarg`` / ``_chem_prefix`` 控制行为。
        """
        self.found_specific_param = False
        chem = self._chem_prefix
        specific = f"%s_to_%s_{chem}exc_syn_%s"

        # 按连接类型确定默认模板
        if type == "neuron_to_neuron":
            default = f"neuron_to_neuron_{chem}exc_syn_%s"
        elif type == "neuron_to_muscle":
            default = f"neuron_to_muscle_{chem}exc_syn_%s"
        else:
            default = f"neuron_to_neuron_{chem}exc_syn_%s"

        # 非首字段的共享回退模板
        common = f"{chem}exc_syn_%s"

        # 逐字段查询参数值
        kwargs: dict[str, str] = {}
        for i, field in enumerate(self._exc_param_fields):
            # 首字段用 default（含连接类型），后续用 common（共享）
            fallback = default if i == 0 else common
            val = self.get_conn_param(pre_cell, post_cell, specific, fallback, field)
            kwarg_name = field
            if self._exc_param_to_kwarg and field in self._exc_param_to_kwarg:
                kwarg_name = self._exc_param_to_kwarg[field]
            kwargs[kwarg_name] = val

        # 构造 conn_id
        conn_id = (
            "neuron_to_neuron_exc_syn"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_exc_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_exc_syn" % (pre_cell, post_cell)

        return self._exc_syn_cls(id=conn_id, **kwargs)

    def get_inh_syn(self, pre_cell, post_cell, type):
        """获取抑制性化学突触（模板方法）。

        子类通过 ``_inh_syn_cls`` / ``_inh_param_fields`` /
        ``_inh_param_to_kwarg`` / ``_chem_prefix`` 控制行为。
        """
        self.found_specific_param = False
        chem = self._chem_prefix
        specific = f"%s_to_%s_{chem}inh_syn_%s"

        # 按连接类型确定默认模板
        if type == "neuron_to_neuron":
            default = f"neuron_to_neuron_{chem}inh_syn_%s"
        elif type == "neuron_to_muscle":
            default = f"neuron_to_muscle_{chem}inh_syn_%s"
        else:
            default = f"neuron_to_neuron_{chem}inh_syn_%s"

        # 非首字段的共享回退模板
        common = f"{chem}inh_syn_%s"

        # 逐字段查询参数值
        kwargs: dict[str, str] = {}
        for i, field in enumerate(self._inh_param_fields):
            fallback = default if i == 0 else common
            val = self.get_conn_param(pre_cell, post_cell, specific, fallback, field)
            kwarg_name = field
            if self._inh_param_to_kwarg and field in self._inh_param_to_kwarg:
                kwarg_name = self._inh_param_to_kwarg[field]
            kwargs[kwarg_name] = val

        # 构造 conn_id
        conn_id = (
            "neuron_to_neuron_inh_syn"
            if type == "neuron_to_neuron"
            else "neuron_to_muscle_inh_syn"
        )
        if self.found_specific_param:
            conn_id = "%s_to_%s_inh_syn" % (pre_cell, post_cell)

        return self._inh_syn_cls(id=conn_id, **kwargs)

    def get_elec_syn(self, pre_cell, post_cell, type):
        """获取电突触（模板方法）。

        Level A（_elec_syn_cls = ExpTwoSynapse）返回假电突触，
        其余层级（_elec_syn_cls = GapJunction）返回 GapJunction。
        """
        gbase, conn_id = self._get_elec_syn_params(pre_cell, post_cell, type)
        if self._elec_syn_cls is GapJunction:
            return GapJunction(id=conn_id, conductance=gbase)
        # ExpTwoSynapse（Level A）— 需要额外参数
        erev = self.get_conn_param(
            pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "erev"
        )
        decay = self.get_conn_param(
            pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "decay"
        )
        rise = self.get_conn_param(
            pre_cell, post_cell, "%s_to_%s_elec_syn_%s", "elec_syn_%s", "rise"
        )
        return ExpTwoSynapse(
            id=conn_id, gbase=gbase, erev=erev, tau_decay=decay, tau_rise=rise
        )

    def _get_elec_syn_params(self, pre_cell, post_cell, type):
        """提取电突触连接参数（gbase + conn_id）。

        :param pre_cell: 突触前细胞
        :param post_cell: 突触后细胞
        :param type: 连接类型
        :return: (gbase, conn_id) 元组
        """
        self.found_specific_param = False
        specific = "%s_to_%s_elec_syn_%s"

        # 按连接类型确定默认模板
        if type == "neuron_to_neuron":
            default_gbase = "neuron_to_neuron_elec_syn_%s"
        elif type == "neuron_to_muscle":
            default_gbase = "neuron_to_muscle_elec_syn_%s"
        elif type == "muscle_to_muscle":
            default_gbase = "muscle_to_muscle_elec_syn_%s"
        else:
            default_gbase = "neuron_to_neuron_elec_syn_%s"

        gbase = self.get_conn_param(
            pre_cell, post_cell, specific, default_gbase, "gbase"
        )

        # 构造 conn_id
        id_map = {
            "neuron_to_neuron": "neuron_to_neuron_elec_syn",
            "neuron_to_muscle": "neuron_to_muscle_elec_syn",
            "muscle_to_muscle": "muscle_to_muscle_elec_syn",
        }
        conn_id = id_map.get(type, "neuron_to_neuron_elec_syn")
        if self.found_specific_param:
            conn_id = "%s_to_%s_elec_syn" % (pre_cell, post_cell)

        return gbase, conn_id


# ---------------------------------------------------------------------------
# GradedSynapse2 共享方法混入
# ---------------------------------------------------------------------------


class _GradedSynapse2Mixin:
    """为使用 GradedSynapse2 的层级（C0, D1）提供共享方法。

    需要配合 _ModelBase 子类使用（MRO 中 super() 调用父类方法）。
    """

    def create_n_connection_synapse(self, prototype_syn, n, nml_doc, existing_synapses):
        """注册突触原型（含 GradedSynapse2 支持）。

        :param prototype_syn: 突触原型对象
        :param n: 连接数
        :param nml_doc: NeuroML 文档
        :param existing_synapses: 已注册突触映射
        :return: 注册的突触对象
        """
        if prototype_syn.id in existing_synapses:
            return existing_synapses[prototype_syn.id]

        # GradedSynapse2 直接追加到 graded_synapses
        if isinstance(prototype_syn, GradedSynapse2):
            existing_synapses[prototype_syn.id] = prototype_syn
            nml_doc.graded_synapses.append(prototype_syn)
            return prototype_syn

        # 其他类型委托给父类
        return super().create_n_connection_synapse(
            prototype_syn, n, nml_doc, existing_synapses
        )

    def is_analog_conn(self, syn) -> bool:
        """判断是否为模拟连接（含 GradedSynapse2）。

        :param syn: 突触对象
        :return: True 若为 GradedSynapse 或 GradedSynapse2
        """
        return super().is_analog_conn(syn) or isinstance(syn, GradedSynapse2)
