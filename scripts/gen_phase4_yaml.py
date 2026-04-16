"""生成 phase4_init.yaml 规范文件。"""
import yaml

spec = [{"file": "project/c302/__init__.py", "functions": []}]
funcs = spec[0]["functions"]

defs = {
    "print_": (
        "带 ``c302`` 前缀的调试输出，用于区分框架自身的日志信息。\n\n"
        ":param msg: 要输出的消息字符串\n"
        ":param print_it: 为 False 时静默（非 verbose 模式）"
    ),
    "load_data_reader": (
        "动态导入并返回数据读取器模块或实例。\n\n"
        "根据 ``data_reader`` 名称中是否包含 ``cect`` 来决定导入路径：\n"
        "- 含 ``cect``：直接导入 cect 子模块并调用 ``get_instance()`` 返回读取器实例\n"
        "- 不含：从 ``c302`` 包导入对应模块\n\n"
        ":param data_reader: 数据读取器的模块路径名\n"
        ":return: 数据读取器实例（cect）或模块对象（c302 内部）"
    ),
    "get_str_from_exponential": (
        "将 float 格式化为定点字符串，避免科学计数法输出。\n\n"
        "例如 ``1e-05`` 返回 15 位小数的定点表示，\n"
        "用于在 NeuroML 属性值中避免科学计数法。\n\n"
        ":param num: 待格式化的数值（int 或 float）\n"
        ":return: 15 位小数的定点字符串"
    ),
    "get_muscle_position": (
        "根据肌肉名称计算其在虫体中的三维坐标。\n\n"
        "按照命名模式 ``M[VD][LR]<index>`` 解析：\n"
        "- D/V 决定 z 轴方向（+80/-80）\n"
        "- L/R 决定 x 轴方向（+80/-80）\n"
        "- index 决定 y 轴位置（-300 + 30*index）\n\n"
        "特殊肌肉（MANAL/MVULVA）返回原点 (0,0,0)。\n\n"
        ":param muscle: 肌肉名称字符串\n"
        ":param data_reader: 数据读取器实例（当前未使用，保留接口）\n"
        ":return: ``(x, y, z)`` 坐标元组\n"
        ":raises Exception: 无法识别的肌肉名称格式"
    ),
    "is_muscle": (
        "判断细胞名称是否为肌肉（匹配 ``M[VD][LR]<digits>`` 模式）。\n\n"
        ":param cell_name: 细胞名称字符串\n"
        ":return: 匹配对象（truthy）或 None"
    ),
    "process_args": (
        "解析 c302 命令行参数。\n\n"
        "必需参数：\n"
        "- ``reference``：网络唯一标识\n"
        "- ``parameters``：参数层级名（如 ``parameters_A``）\n\n"
        "可选参数包括数据读取器、细胞列表、刺激列表、连接覆盖/缩放、\n"
        "肌肉列表、仿真时长/时间步长/电压范围等。\n\n"
        ":return: ``argparse.Namespace`` 对象"
    ),
    "get_next_stim_id": (
        "为指定细胞生成下一个不重复的刺激 ID。\n\n"
        "遍历已有 ``pulse_generators``，计数以 ``stim_{cell}`` 开头的数量，\n"
        "返回 ``stim_{cell}_{n+1}`` 格式的新 ID。\n\n"
        ":param nml_doc: NeuroML 文档对象\n"
        ":param cell: 细胞名称\n"
        ":return: 新的刺激 ID 字符串"
    ),
    "get_cell_position": (
        "从 NeuroML 多室形态文件中读取细胞 soma 位置。\n\n"
        "加载 ``NeuroML2/{cell}.cell.nml`` 文件，返回第一个 segment 的 proximal 坐标。\n\n"
        ":param cell: 细胞名称\n"
        ":return: ``Point3DWithDiam`` 对象（含 x, y, z 属性）"
    ),
    "append_input_to_nml_input_list": (
        "将刺激输入追加到 NeuroML 网络的 ``InputList`` 中。\n\n"
        "创建 ``InputList`` 并添加一个 ``Input`` 条目，将其绑定到指定细胞的\n"
        "突触目标端点上。\n\n"
        ":param stim: 刺激生成器对象（``PulseGenerator`` 或 ``SineGenerator``）\n"
        ":param nml_doc: NeuroML 文档对象\n"
        ":param cell: 目标细胞名称\n"
        ":param params: 参数模型对象"
    ),
    "add_new_sinusoidal_input": (
        "为指定细胞创建正弦波刺激输入。\n\n"
        "根据运动神经元（VB/DB）的 soma 位置自动计算相位偏移，\n"
        "VB 系列的幅度取反以产生反相振荡。\n\n"
        ":param nml_doc: NeuroML 文档对象\n"
        ":param cell: 目标细胞名称\n"
        ":param delay: 延迟时间\n"
        ":param duration: 持续时间\n"
        ":param amplitude: 幅度\n"
        ":param period: 周期\n"
        ":param params: 参数模型对象"
    ),
    "add_new_input": (
        "为指定细胞创建脉冲刺激输入（``PulseGenerator``）。\n\n"
        ":param nml_doc: NeuroML 文档对象\n"
        ":param cell: 目标细胞名称\n"
        ":param delay: 延迟时间\n"
        ":param duration: 持续时间\n"
        ":param amplitude: 幅度\n"
        ":param params: 参数模型对象"
    ),
    "get_muscle_names": (
        "生成全部 96 条体壁肌肉的名称列表。\n\n"
        "按象限顺序（MDR/MVR/MVL/MDL）x 24 条/象限生成，\n"
        "编号 01~24，低位数字补零（如 ``MDR01``）。\n\n"
        ":return: 96 个肌肉名称的列表"
    ),
    "merge_with_template": (
        "使用 Airspeed 模板引擎将变量字典与 LEMS 模板文件合并。\n\n"
        ":param model: 变量字典（传入模板的上下文数据）\n"
        ":param templfile: 模板文件路径\n"
        ":return: 合并后的 XML 字符串"
    ),
    "write_to_file": (
        "将生成的 NeuroML 网络和 LEMS 仿真文件写入磁盘。\n\n"
        "输出两个文件：\n"
        "1. ``{reference}.net.nml`` -- NeuroML 网络描述文件\n"
        "2. ``LEMS_{reference}.xml`` -- LEMS 仿真配置文件（由模板渲染）\n\n"
        "可选进行 NeuroML2 schema 验证。\n\n"
        ":param nml_doc: NeuroML 文档对象\n"
        ":param lems_info: LEMS 模板变量字典\n"
        ":param reference: 网络标识字符串\n"
        ":param template_path: LEMS 模板文件所在目录\n"
        ":param validate: 是否进行 NeuroML2 验证\n"
        ":param verbose: 是否输出详细日志\n"
        ":param target_directory: 输出目录"
    ),
    "get_projection_id": (
        "根据突触前/后细胞和突触类型生成标准 Projection ID。\n\n"
        "格式：``NC_{pre}_{post}_{synclass}``。\n\n"
        ":param pre: 突触前细胞名称\n"
        ":param post: 突触后细胞名称\n"
        ":param synclass: 突触分类名\n"
        ":param syntype: 突触类型名（当前未使用，保留接口）\n"
        ":return: Projection ID 字符串"
    ),
    "get_random_colour_hex": (
        "生成随机十六进制颜色字符串（``#RRGGBB``），用于绘图颜色分配。\n\n"
        ":return: 颜色字符串"
    ),
    "get_file_name_relative_to_c302": (
        "返回相对于 ``C302_HOME`` 环境变量的文件路径。\n\n"
        ":param file_name: 文件名\n"
        ":return: 相对路径字符串，或 None（若环境变量未设置）"
    ),
    "get_cell_names_and_connection": (
        "读取连接组数据，返回所有细胞名称和突触连接列表。\n\n"
        "调用数据读取器的 ``read_data()`` 方法获取完整连接组\n"
        "（包含非连接细胞），并按字母序排列细胞名称。\n\n"
        ":param data_reader: 数据读取器模块路径\n"
        ":param test: 是否为测试模式（当前未使用）\n"
        ":return: ``(cell_names, conns)`` 元组"
    ),
    "get_cell_muscle_names_and_connection": (
        "读取神经元-肌肉连接数据，返回运动神经元、已知肌肉列表和肌肉连接。\n\n"
        "过滤掉非体壁肌肉（``MANAL``/``MVULVA``），仅保留\n"
        "在 ``BODY_WALL_MUSCLE_NAMES`` 中的已知肌肉。\n\n"
        ":param data_reader: 数据读取器模块路径\n"
        ":param test: 是否为测试模式（当前未使用）\n"
        ":return: ``(mneurons, all_known_muscles, muscle_conns)`` 元组"
    ),
    "is_cond_based_cell": (
        "判断参数层级是否为导电模型（Level C 或 D 系列）。\n\n"
        ":param params: 参数模型对象\n"
        ":return: bool"
    ),
    "get_cell_id_string": (
        "构建 NeuroML 中引用细胞实例的路径字符串。\n\n"
        "格式为 ``../{cell_name}/0/{cell_component_id}``，\n"
        "Level D 的神经元使用细胞名本身作为 component ID。\n\n"
        ":param cell: 细胞名称\n"
        ":param params: 参数模型对象\n"
        ":param muscle: 是否为肌肉细胞\n"
        ":return: 路径字符串"
    ),
    "regex_match": (
        "当 pattern 为正则表达式时执行匹配。\n\n"
        ":param pattern: 模式字符串（需含 ``^`` 和 ``$`` 才视为正则）\n"
        ":param str: 待匹配字符串\n"
        ":return: 匹配对象或 False"
    ),
    "is_regex_string": (
        "判断字符串是否为正则表达式格式（同时含 ``^`` 和 ``$``）。\n\n"
        ":param str: 待检查字符串\n"
        ":return: bool"
    ),
    "elem_in_coll_matches_conn": (
        "检查集合中是否有正则元素匹配给定的连接字符串。\n\n"
        ":param coll: 字符串集合（可能含正则模式）\n"
        ":param conn: 连接简写字符串\n"
        ":return: bool"
    ),
    "_get_cell_info": (
        "从 owmeta Bundle 或本地缓存获取细胞的详细注释信息。\n\n"
        "返回两个 OrderedDict：神经元信息和肌肉信息。\n"
        "每个条目包含 ``(cell, types, receptor, neurotransmitter, short, color)``。\n\n"
        "当 ``bnd`` 为 None 时使用本地 JSON 缓存文件\n"
        "（``data/owmeta_cache.json``）。\n\n"
        ":param bnd: owmeta Bundle 对象，或 None（使用缓存）\n"
        ":param cells: 要查询的细胞名称集合\n"
        ":return: ``(all_neuron_info, all_muscle_info)`` 元组"
    ),
    "set_param": (
        "设置或新增生物参数值。\n\n"
        "若参数已存在且值不同则更新；若不存在则添加新参数。\n\n"
        ":param params: 参数模型对象\n"
        ":param param: 参数名称\n"
        ":param value: 参数值字符串"
    ),
    "mirror_param": (
        "为双向缝隙连接参数设置镜像值（A-B 和 B-A 使用相同参数）。\n\n"
        "通过解析参数名中的 ``pre_to_post`` 模式来构建反向键。\n\n"
        ":param params: 参数模型对象\n"
        ":param k: 参数名称（含 ``pre_to_post`` 模式）\n"
        ":param v: 参数值"
    ),
    "generate": (
        "c302 网络生成主入口，将连接组数据转化为完整的 NeuroML2 网络。\n\n"
        "主要步骤：\n"
        "1. 处理参数覆盖（param_overrides）并创建模型组件\n"
        "2. 初始化 NeuroML 文档和网络对象\n"
        "3. 遍历连接组数据创建神经元种群（Population/Instance）\n"
        "4. 为每个神经元加载形态文件并分配 3D 坐标\n"
        "5. 创建偏置电流刺激输入\n"
        "6. 遍历神经元间连接创建突触投射\n"
        "7. 处理连接数量覆盖/缩放和极性覆盖\n"
        "8. 创建肌肉种群和神经元-肌肉连接\n"
        "9. 输出 ``.net.nml`` 和 ``LEMS_*.xml`` 文件\n"
        "10. 返回 NeuroML 文档对象\n\n"
        ":param net_id: 网络唯一标识\n"
        ":param params: 参数化模型对象\n"
        ":param data_reader: 数据读取器模块路径\n"
        ":param cells: 包含的细胞列表（None 表示全部）\n"
        ":param cells_to_plot: 需要绘图的细胞列表\n"
        ":param cells_to_stimulate: 需要刺激的细胞列表\n"
        ":param muscles_to_include: 包含的肌肉列表\n"
        ":param conns_to_include: 包含的连接列表\n"
        ":param conns_to_exclude: 排除的连接列表\n"
        ":param conn_number_override: 连接数量覆盖字典\n"
        ":param conn_number_scaling: 连接数量缩放字典\n"
        ":param conn_polarity_override: 连接极性覆盖字典\n"
        ":param duration: 仿真时长（ms）\n"
        ":param dt: 时间步长（ms）\n"
        ":param vmin: 绘图电压下限（mV）\n"
        ":param vmax: 绘图电压上限（mV）\n"
        ":param seed: 随机数种子\n"
        ":param test: 是否为测试模式\n"
        ":param verbose: 是否输出详细日志\n"
        ":param print_connections: 是否打印连接信息\n"
        ":param param_overrides: 参数覆盖字典\n"
        ":param target_directory: 输出目录\n"
        ":return: ``NeuroMLDocument`` 对象"
    ),
    "parse_list_arg": (
        "解析 CLI 列表参数字符串为 Python 列表。\n\n"
        ":param list_arg: CLI 列表参数字符串，或 None\n"
        ":return: 字符串列表，或 None/空列表"
    ),
    "parse_dict_arg": (
        "解析 CLI 字典参数字符串为 Python 字典。\n\n"
        "值尝试转为 float，失败则保留为字符串。\n\n"
        ":param dict_arg: CLI 字典参数字符串，或 None\n"
        ":return: 字典，或 None"
    ),
    "main": (
        "c302 CLI 主入口，解析命令行参数并调用 ``generate()``。\n\n"
        "动态导入指定参数层级模块，实例化 ``ParameterisedModel``，\n"
        "然后将全部 CLI 参数传递给 ``generate()``。"
    ),
}

for name, doc in defs.items():
    funcs.append({"name": name, "docstring": doc})

with open(
    r"e:\Model-Design\c302\scripts\add-docstring\specs\phase4_init.yaml",
    "w",
    encoding="utf-8",
) as f:
    yaml.dump(spec, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("Written %d functions" % len(funcs))
