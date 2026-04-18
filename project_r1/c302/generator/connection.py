# =============================================================================
# 功能描述：
#   连接创建模块。负责遍历连接组数据，创建化学突触 Projection、
#   电突触 ElectricalProjection 和连续突触 ContinuousProjection。
#   处理连接数量覆盖/缩放、极性覆盖和正则参数展开。
#
# 类与方法索引：
#   get_projection_id                    (L52)   — 根据突触前/后细胞和突触分类生成标准 Projection ID
#   set_param                            (L66)   — 设置或新增生物参数值
#   mirror_param                         (L86)   — 为双向缝隙连接参数设置镜像值（A-B 和 B-A 使用相同参数）
#   _apply_regex_param_overrides         (L110)  — 展开正则参数覆盖到具体连接
#   _apply_number_processing             (L177)  — 处理连接数量：全局缩放 → 覆盖 → 缩放
#   _create_projection                   (L226)  — 创建单条投射（化学/电/连续）
#   _ensure_silent_synapse               (L319)  — 确保文档中有 SilentSynapse（模拟/非 NeuroML 连接需要）
#   _process_single_connection           (L328)  — 处理单条连接并创建对应的投射
#   create_neuron_connections            (L443)  — 创建神经元间连接
#   create_muscle_connections            (L492)  — 创建神经元→肌肉和肌肉→肌肉连接
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段四：从 __init__.py 提取重写
#
# 当前维护者：Copilot
# =============================================================================
"""连接创建模块。"""
import logging
import math
import re

from neuroml import (
    Connection,
    ConnectionWD,
    ContinuousConnectionInstanceW,
    ContinuousProjection,
    ElectricalConnectionInstanceW,
    ElectricalProjection,
    Projection,
    SilentSynapse,
)

import c302.parameters.bio as bio_module
from c302.generator.population import get_cell_id_string
from c302.utils.helpers import (
    elem_in_coll_matches_conn,
    get_str_from_exponential,
    is_regex_string,
    regex_match,
)

logger = logging.getLogger(__name__)


def get_projection_id(pre: str, post: str, synclass: str, syntype: str) -> str:
    """根据突触前/后细胞和突触分类生成标准 Projection ID。

    格式：``NC_{pre}_{post}_{synclass}``。

    :param pre: 突触前细胞名称
    :param post: 突触后细胞名称
    :param synclass: 突触分类名
    :param syntype: 突触类型名（当前未使用，保留接口）
    :return: Projection ID 字符串
    """
    return "NC_%s_%s_%s" % (pre, post, synclass)


def set_param(params, param: str, value: str) -> None:
    """设置或新增生物参数值。

    若参数已存在且值不同则更新；若不存在则添加新参数。

    :param params: 参数模型对象
    :param param: 参数名称
    :param value: 参数值字符串
    """
    v = params.get_bioparameter(param, warn_if_missing=False)
    if v:
        if v.value == value:
            return
        logger.info("Setting parameter %s = %s", param, value)
        params.set_bioparameter(param, value, "Set with param_overrides", "0")
    else:
        logger.info("Adding parameter %s = %s", param, value)
        params.add_bioparameter(param, value, "Add with param_overrides", "0")


def mirror_param(params, k: str, v: str) -> None:
    """为双向缝隙连接参数设置镜像值（A-B 和 B-A 使用相同参数）。

    :param params: 参数模型对象
    :param k: 参数名称（含 ``pre_to_post`` 模式）
    :param v: 参数值
    """
    pattern = k.split("_")
    pre = pattern[0]
    pattern[0] = "%s"
    post = pattern[2]
    pattern[2] = "%s"
    tmp_param = pattern[5]
    pattern[5] = "%s"
    pattern_str = "_".join(pattern)

    # 正向和反向键
    override_key1 = pattern_str % (pre, post, tmp_param)
    override_key2 = pattern_str % (post, pre, tmp_param)

    set_param(params, override_key1, v)
    set_param(params, override_key2, v)


def _apply_regex_param_overrides(
    regex_param_overrides: dict,
    conn_shorthand: str,
    conn,
    param_overrides: dict,
    params,
) -> None:
    """展开正则参数覆盖到具体连接。

    :param regex_param_overrides: 正则参数覆盖字典
    :param conn_shorthand: 连接简写（如 ``"AVAL-AVBR"``）
    :param conn: 连接对象
    :param param_overrides: 原始参数覆盖字典
    :param params: 参数模型对象
    """
    # 处理非镜像正则覆盖
    for key in regex_param_overrides.keys():
        if key == "mirrored_elec_conn_params":
            continue

        # 构建匹配模式
        pattern = key.split("$")[0] + "$"
        pattern = pattern.replace("_to_", "-")

        if re.match(pattern, conn_shorthand):
            new_param = conn_shorthand.replace("-", "_to_") + key.split("$")[1]
            new_param = new_param.replace("_GJ", "")
            new_param_v = regex_param_overrides[key]

            # 精确覆盖优先
            if new_param in param_overrides:
                continue
            set_param(params, new_param, new_param_v)

    # 处理镜像电连接正则覆盖
    if "mirrored_elec_conn_params" in regex_param_overrides:
        for k, v in regex_param_overrides["mirrored_elec_conn_params"].items():
            pattern = k.split("$")[0] + "$"
            pattern = pattern.replace("_to_", "-")

            if re.match(pattern, conn_shorthand):
                new_param = conn_shorthand.replace("-", "_to_") + k.split("$")[1]
                new_param = new_param.replace("_GJ", "")
                # 构建镜像参数名
                new_param_mirrored = (
                    conn.post_cell
                    + "_"
                    + new_param.split("_")[1]
                    + "_"
                    + conn.pre_cell
                    + "_"
                    + "_".join(new_param.split("_")[3:])
                )
                new_param_v = v

                # 精确覆盖优先
                mirrored_overrides = param_overrides.get(
                    "mirrored_elec_conn_params", {}
                )
                if (
                    new_param in mirrored_overrides
                    or new_param_mirrored in mirrored_overrides
                ):
                    continue
                mirror_param(params, new_param, new_param_v)


def _apply_number_processing(
    conn,
    params,
    conn_shorthand: str,
    conn_number_override: dict | None,
    conn_number_scaling: dict | None,
) -> float:
    """处理连接数量：全局缩放 → 覆盖 → 缩放。

    :param conn: 连接对象
    :param params: 参数模型对象
    :param conn_shorthand: 连接简写字符串
    :param conn_number_override: 连接数量覆盖字典
    :param conn_number_scaling: 连接数量缩放字典
    :return: 最终连接数量
    """
    number_syns = conn.number

    # 全局连接幂缩放
    scale_param = params.get_bioparameter(
        "global_connectivity_power_scaling", warn_if_missing=False
    )
    if scale_param:
        scale = float(scale_param.value)
        number_syns = math.pow(number_syns, scale)

    # 连接数量覆盖（精确或正则匹配）
    if conn_number_override:
        for key in conn_number_override.keys():
            if key == conn_shorthand:
                number_syns = conn_number_override[conn_shorthand]
                break
            elif regex_match(key, conn_shorthand):
                number_syns = conn_number_override[key]
                break

    # 连接数量缩放（使用原始 conn.number）
    if conn_number_scaling:
        for key in conn_number_scaling.keys():
            if key == conn_shorthand:
                number_syns = conn.number * conn_number_scaling[conn_shorthand]
                break
            elif regex_match(key, conn_shorthand):
                number_syns = conn.number * conn_number_scaling[key]
                break

    return number_syns


def _create_projection(
    net,
    nml_doc,
    proj_id: str,
    conn,
    params,
    syn_new,
    number_syns: float,
    elect_conn: bool,
    analog_conn: bool,
    nonneuroml_conn: bool,
    muscle_post: bool = False,
) -> None:
    """创建单条投射（化学/电/连续）。

    :param net: NeuroML Network 对象
    :param nml_doc: NeuroML 文档对象
    :param proj_id: 投射 ID
    :param conn: 连接对象
    :param params: 参数模型对象
    :param syn_new: 注册后的突触对象
    :param number_syns: 连接数量
    :param elect_conn: 是否为电突触
    :param analog_conn: 是否为模拟突触
    :param nonneuroml_conn: 是否为非 NeuroML 连接
    :param muscle_post: 突触后是否为肌肉
    """
    pre_cell_id = get_cell_id_string(conn.pre_cell, params)
    post_cell_id = get_cell_id_string(conn.post_cell, params, muscle=muscle_post)

    if elect_conn:
        # 电突触
        proj0 = ElectricalProjection(
            id=proj_id,
            presynaptic_population=conn.pre_cell,
            postsynaptic_population=conn.post_cell,
        )
        net.electrical_projections.append(proj0)
        conn0 = ElectricalConnectionInstanceW(
            id="0",
            pre_cell=pre_cell_id,
            post_cell=post_cell_id,
            synapse=syn_new.id,
            weight=number_syns,
        )
        proj0.electrical_connection_instance_ws.append(conn0)

    elif analog_conn or nonneuroml_conn:
        # 连续突触（模拟型/非 NeuroML）
        proj0 = ContinuousProjection(
            id=proj_id,
            presynaptic_population=conn.pre_cell,
            postsynaptic_population=conn.post_cell,
        )
        net.continuous_projections.append(proj0)
        conn0 = ContinuousConnectionInstanceW(
            id="0",
            pre_cell=pre_cell_id,
            post_cell=post_cell_id,
            pre_component="silent",
            post_component=syn_new.id,
            weight=number_syns,
        )
        proj0.continuous_connection_instance_ws.append(conn0)

    else:
        # 化学突触
        proj0 = Projection(
            id=proj_id,
            presynaptic_population=conn.pre_cell,
            postsynaptic_population=conn.post_cell,
            synapse=syn_new.id,
        )
        net.projections.append(proj0)

        if muscle_post:
            # 神经元→肌肉使用无权重 Connection
            conn0 = Connection(
                id="0", pre_cell_id=pre_cell_id, post_cell_id=post_cell_id
            )
            proj0.connections.append(conn0)
        else:
            # 神经元→神经元使用加权 ConnectionWD
            conn0 = ConnectionWD(
                id="0",
                pre_cell_id=pre_cell_id,
                post_cell_id=post_cell_id,
                weight=number_syns,
                delay="0ms",
            )
            proj0.connection_wds.append(conn0)


def _ensure_silent_synapse(nml_doc) -> None:
    """确保文档中有 SilentSynapse（模拟/非 NeuroML 连接需要）。

    :param nml_doc: NeuroML 文档对象
    """
    if len(nml_doc.silent_synapses) == 0:
        nml_doc.silent_synapses.append(SilentSynapse(id="silent"))


def _process_single_connection(
    conn,
    params,
    net,
    nml_doc,
    conn_type: str,
    regex_param_overrides: dict,
    param_overrides: dict,
    conns_to_include: list,
    conns_to_exclude: list,
    conn_number_override: dict | None,
    conn_number_scaling: dict | None,
    conn_polarity_override: dict | None,
    existing_synapses: dict,
    muscle_post: bool = False,
) -> None:
    """处理单条连接并创建对应的投射。

    :param conn: 连接对象
    :param params: 参数模型对象
    :param net: Network 对象
    :param nml_doc: NeuroML 文档
    :param conn_type: 连接类型字符串
    :param regex_param_overrides: 正则参数覆盖字典
    :param param_overrides: 原始参数覆盖字典
    :param conns_to_include: 连接白名单
    :param conns_to_exclude: 连接黑名单
    :param conn_number_override: 连接数量覆盖
    :param conn_number_scaling: 连接数量缩放
    :param conn_polarity_override: 连接极性覆盖
    :param existing_synapses: 已注册突触缓存
    :param muscle_post: 突触后是否为肌肉
    """
    proj_id = get_projection_id(
        conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype
    )
    conn_shorthand = "%s-%s" % (conn.pre_cell, conn.post_cell)

    # 判断连接类型
    elect_conn = False
    analog_conn = False
    nonneuroml_conn = False
    conn_pol = "exc"

    if "GABA" in conn.synclass:
        conn_pol = "inh"
    if "_GJ" in conn.synclass:
        conn_pol = "elec"
        elect_conn = params.is_elec_conn(params.neuron_to_neuron_elec_syn)
        conn_shorthand = "%s-%s_GJ" % (conn.pre_cell, conn.post_cell)

    # 展开正则参数覆盖
    _apply_regex_param_overrides(
        regex_param_overrides, conn_shorthand, conn, param_overrides, params
    )

    # 连接白名单过滤
    if conns_to_include and conn_shorthand not in conns_to_include:
        if not elem_in_coll_matches_conn(conns_to_include, conn_shorthand):
            return
    # 连接黑名单过滤
    if conns_to_exclude:
        if conn_shorthand in conns_to_exclude:
            return
        if elem_in_coll_matches_conn(conns_to_exclude, conn_shorthand):
            return

    # 获取突触原型
    syn0 = params.get_syn(conn.pre_cell, conn.post_cell, conn_type, conn_pol)

    # 处理极性覆盖
    if conn_polarity_override and not elect_conn:
        polarity = None
        for pol_key in conn_polarity_override.keys():
            if pol_key == conn_shorthand:
                polarity = conn_polarity_override[pol_key]
                break
            elif regex_match(pol_key, conn_shorthand):
                polarity = conn_polarity_override[pol_key]
                break
        if polarity:
            syn0 = params.get_syn(conn.pre_cell, conn.post_cell, conn_type, polarity)

    # 检测特殊连接类型
    if params.is_analog_conn(syn0):
        analog_conn = True
        _ensure_silent_synapse(nml_doc)

    if params.is_nonneuroml_conn(syn0):
        nonneuroml_conn = True
        _ensure_silent_synapse(nml_doc)

    # 处理连接数量
    number_syns = _apply_number_processing(
        conn, params, conn_shorthand, conn_number_override, conn_number_scaling
    )

    if number_syns != conn.number:
        logger.info(
            "Changing effective synapse count %s -> %s: %s -> %s",
            conn.pre_cell, conn.post_cell, conn.number, number_syns,
        )

    # 注册突触原型到文档
    syn_new = params.create_n_connection_synapse(
        syn0, number_syns, nml_doc, existing_synapses
    )

    # 创建投射
    _create_projection(
        net, nml_doc, proj_id, conn, params, syn_new, number_syns,
        elect_conn, analog_conn, nonneuroml_conn, muscle_post=muscle_post,
    )


def create_neuron_connections(
    net,
    nml_doc,
    params,
    conns: list,
    lems_info: dict,
    regex_param_overrides: dict,
    param_overrides: dict,
    conns_to_include: list,
    conns_to_exclude: list,
    conn_number_override: dict | None,
    conn_number_scaling: dict | None,
    conn_polarity_override: dict | None,
    existing_synapses: dict,
) -> None:
    """创建神经元间连接。

    :param net: Network 对象
    :param nml_doc: NeuroML 文档
    :param params: 参数模型对象
    :param conns: 连接列表
    :param lems_info: LEMS 信息字典
    :param regex_param_overrides: 正则参数覆盖
    :param param_overrides: 原始参数覆盖
    :param conns_to_include: 白名单
    :param conns_to_exclude: 黑名单
    :param conn_number_override: 数量覆盖
    :param conn_number_scaling: 数量缩放
    :param conn_polarity_override: 极性覆盖
    :param existing_synapses: 已注册突触缓存
    """
    for conn in conns:
        # 仅处理两端都在网络中的连接
        if conn.pre_cell in lems_info["cells"] and conn.post_cell in lems_info["cells"]:
            _process_single_connection(
                conn, params, net, nml_doc,
                conn_type="neuron_to_neuron",
                regex_param_overrides=regex_param_overrides,
                param_overrides=param_overrides,
                conns_to_include=conns_to_include,
                conns_to_exclude=conns_to_exclude,
                conn_number_override=conn_number_override,
                conn_number_scaling=conn_number_scaling,
                conn_polarity_override=conn_polarity_override,
                existing_synapses=existing_synapses,
                muscle_post=False,
            )


def create_muscle_connections(
    net,
    nml_doc,
    params,
    muscle_conns: list,
    lems_info: dict,
    muscles_to_include: list[str],
    regex_param_overrides: dict,
    param_overrides: dict,
    conns_to_include: list,
    conns_to_exclude: list,
    conn_number_override: dict | None,
    conn_number_scaling: dict | None,
    conn_polarity_override: dict | None,
    existing_synapses: dict,
) -> None:
    """创建神经元→肌肉和肌肉→肌肉连接。

    :param net: Network 对象
    :param nml_doc: NeuroML 文档
    :param params: 参数模型对象
    :param muscle_conns: 肌肉连接列表
    :param lems_info: LEMS 信息字典
    :param muscles_to_include: 要包含的肌肉列表
    :param regex_param_overrides: 正则参数覆盖
    :param param_overrides: 原始参数覆盖
    :param conns_to_include: 白名单
    :param conns_to_exclude: 黑名单
    :param conn_number_override: 数量覆盖
    :param conn_number_scaling: 数量缩放
    :param conn_polarity_override: 极性覆盖
    :param existing_synapses: 已注册突触缓存
    """
    for conn in muscle_conns:
        # 突触后必须是要包含的肌肉
        if conn.post_cell not in muscles_to_include:
            continue
        # 突触前必须是网络中的神经元或要包含的肌肉
        if (
            conn.pre_cell not in lems_info["cells"]
            and conn.pre_cell not in muscles_to_include
        ):
            continue

        # 判断连接类型
        conn_type = "neuron_to_muscle"
        if conn.pre_cell in muscles_to_include:
            conn_type = "muscle_to_muscle"

        _process_single_connection(
            conn, params, net, nml_doc,
            conn_type=conn_type,
            regex_param_overrides=regex_param_overrides,
            param_overrides=param_overrides,
            conns_to_include=conns_to_include,
            conns_to_exclude=conns_to_exclude,
            conn_number_override=conn_number_override,
            conn_number_scaling=conn_number_scaling,
            conn_polarity_override=conn_polarity_override,
            existing_synapses=existing_synapses,
            muscle_post=True,
        )
