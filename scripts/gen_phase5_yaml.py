"""生成阶段五 docstring YAML 规范文件。"""
import yaml
from pathlib import Path

specs = [
    {
        "file": "project/c302/c302_utils.py",
        "functions": [
            {
                "name": "natsort",
                "docstring": (
                    "对字符串进行自然排序的辅助键函数。\n\n"
                    "将字符串按数字和非数字片段拆分，数字部分转为整数，\n"
                    "使得 ``VB2`` 排在 ``VB11`` 之前（而非字典序的 ``VB11 < VB2``）。\n\n"
                    ":param s: 待排序的字符串\n"
                    ":return: 可用于 ``sorted(key=...)`` 的混合类型列表"
                ),
            },
            {
                "name": "plots",
                "docstring": (
                    "将仿真数据矩阵绘制为热图（pcolormesh）。\n\n"
                    "当细胞数量超过 24 个时自动增大图形高度以保证标签可读。\n"
                    "X 轴为时间（ms），Y 轴为各细胞名称。\n\n"
                    ":param a_n: 二维 numpy 数组，行为细胞、列为时间步\n"
                    ":param info: 图表标题字符串\n"
                    ":param cells: 细胞名称列表（与矩阵行对应）\n"
                    ":param dt: 仿真时间步长（秒）"
                ),
            },
            {
                "name": "generate_traces_plot",
                "docstring": (
                    "使用 pyNeuroML 绘制各细胞的膜电位或活性轨迹叠加图。\n\n"
                    ":param config: 配置名称（如 ``Full``、``Syns``）\n"
                    ":param parameter_set: 参数集名称（如 ``A``、``C1``）\n"
                    ":param xvals: 时间序列列表（每个细胞一条）\n"
                    ":param yvals: 电压/活性值列表\n"
                    ":param info: 图表标题\n"
                    ":param labels: 曲线标签列表\n"
                    ":param save: 是否保存为 PNG 文件\n"
                    ":param save_fig_path: 保存路径模板\n"
                    ":param voltage: ``True`` 绘制膜电位，``False`` 绘制活性/钙浓度\n"
                    ":param muscles: ``True`` 表示绘制肌肉数据"
                ),
            },
            {
                "name": "plot_c302_results",
                "docstring": (
                    "c302 仿真结果的主绘图函数。\n\n"
                    "从 LEMS 仿真结果字典中提取神经元和肌肉数据，依次生成：\n"
                    "1. 神经元膜电位热图和轨迹图\n"
                    "2. 肌肉膜电位热图和轨迹图\n"
                    "3. 神经元活性/钙浓度热图和轨迹图（可选）\n"
                    "4. 肌肉活性/钙浓度热图和轨迹图（可选）\n\n"
                    ":param lems_results: LEMS 仿真结果字典，键为变量路径，值为时间序列\n"
                    ":param config: 配置名称\n"
                    ":param parameter_set: 参数集名称\n"
                    ":param directory: 图片保存目录\n"
                    ":param save: 是否保存图片\n"
                    ":param show_plot_already: 是否立即显示图形窗口\n"
                    ":param data_reader: 数据读取器名称\n"
                    ":param plot_ca: 是否绘制活性/钙浓度图"
                ),
            },
            {
                "name": "_show_conn_matrix",
                "docstring": (
                    "内部辅助函数：显示单个连接矩阵热图。\n\n"
                    "当矩阵数据全为零时直接返回。否则使用 imshow 绘制热图，\n"
                    "突触前细胞为 Y 轴、突触后细胞为 X 轴。\n\n"
                    ":param data: 二维 numpy 连接权重矩阵\n"
                    ":param t: 图表副标题\n"
                    ":param all_info_pre: 突触前细胞信息有序字典\n"
                    ":param all_info_post: 突触后细胞信息有序字典\n"
                    ":param type: 网络 ID（用于图表主标题）\n"
                    ":param save_figure_to: 保存路径，``False`` 表示不保存\n"
                    ":param verbose: 是否输出详细日志\n"
                    ":param figsize: 图形尺寸元组\n"
                    ":param colormap: matplotlib 色彩映射名称"
                ),
            },
            {
                "name": "generate_conn_matrix",
                "docstring": (
                    "从 NeuroML 文档生成完整的连接矩阵可视化。\n\n"
                    "解析网络中的所有连续投射（化学突触）和电投射（缝隙连接），\n"
                    "按兴奋性/抑制性和神经元/肌肉四象限分别绘制热图。\n\n"
                    ":param nml_doc: NeuroML 文档对象\n"
                    ":param save_fig_dir: 图片保存目录，``None`` 表示不保存\n"
                    ":param verbose: 是否输出详细日志\n"
                    ":param figsize: 图形尺寸元组\n"
                    ":param order_by_type: 是否按细胞类型排序（保留未实现）\n"
                    ":param colormap: matplotlib 色彩映射名称"
                ),
            },
        ],
    },
    {
        "file": "project/c302/runAndPlot.py",
        "functions": [
            {
                "name": "run_c302",
                "docstring": (
                    "c302 仿真编排主函数：生成网络 → 运行仿真 → 绘制结果。\n\n"
                    "完整工作流程：\n"
                    "1. 导入指定配置模块并调用其 ``setup()`` 生成 NeuroML 网络\n"
                    "2. 使用 jNeuroML 或 jNeuroML_NEURON 后端执行 LEMS 仿真\n"
                    "3. 调用 ``plot_c302_results()`` 绘制膜电位和活性图\n"
                    "4. 可选生成连接矩阵可视化\n\n"
                    ":param config: 配置名称（如 ``Full``、``Syns``、``Oscillator``）\n"
                    ":param parameter_set: 参数层级（``A``/``B``/``C``/``C0``/``C1``/``C2``/``D``/``D1``/``W2D``）\n"
                    ":param prefix: 文件名前缀（通常为空字符串）\n"
                    ":param duration: 仿真时长（毫秒）\n"
                    ":param dt: 仿真时间步长（毫秒）\n"
                    ":param simulator: 仿真后端，``'jNeuroML'`` 或 ``'jNeuroML_NEURON'``\n"
                    ":param save: 是否保存图片\n"
                    ":param show_plot_already: 是否立即显示图形窗口\n"
                    ":param data_reader: 数据读取器名称\n"
                    ":param verbose: 是否输出详细日志\n"
                    ":param plot_ca: 是否绘制钙浓度/活性图\n"
                    ":param plot_connectivity: 是否绘制连接矩阵\n"
                    ":param param_overrides: 生物参数覆盖字典\n"
                    ":param config_param_overrides: 配置级参数覆盖字典\n"
                    ":param config_package: 配置模块包路径（默认 ``'c302'``）\n"
                    ":param target_directory: 输出目录\n"
                    ":param save_fig_to: 图片保存目录覆盖\n"
                    ":return: ``(cells, cells_to_stimulate, params, muscles)`` 四元组"
                ),
            },
        ],
    },
    {
        "file": "project/c302/gen_graph.py",
        "functions": [
            {
                "name": "usage",
                "docstring": (
                    "打印命令行用法说明并退出程序。\n\n"
                    ":param script: 脚本文件名"
                ),
            },
            {
                "name": "is_muscle",
                "docstring": (
                    "判断细胞名称是否为肌肉（以 ``MV`` 或 ``MD`` 开头）。\n\n"
                    ":param cell: 细胞名称字符串\n"
                    ":return: ``True`` 表示是肌肉"
                ),
            },
            {
                "name": "get_cells",
                "docstring": (
                    "从 NeuroML XML 根节点提取所有种群（Population）的细胞名称。\n\n"
                    ":param root: XML ElementTree 根节点\n"
                    ":return: 细胞名称列表"
                ),
            },
            {
                "name": "get_elec_conns",
                "docstring": (
                    "从 NeuroML XML 中提取所有电突触（缝隙连接）并生成 Graphviz 边描述。\n\n"
                    "电连接使用虚线样式（``dashed``）和无箭头（``arrowhead=none``）表示。\n"
                    "自动去重反向连接（A→B 和 B→A 只保留一条）。\n\n"
                    ":param root: XML ElementTree 根节点\n"
                    ":return: Graphviz 边描述字符串列表"
                ),
            },
            {
                "name": "get_chem_conns",
                "docstring": (
                    "从 NeuroML XML 中提取所有化学突触连接并生成 Graphviz 边描述。\n\n"
                    "抑制性连接（含 ``inh``）使用红色 T 形箭头，\n"
                    "兴奋性连接使用黑色普通箭头。\n\n"
                    ":param root: XML ElementTree 根节点\n"
                    ":return: Graphviz 边描述字符串列表"
                ),
            },
            {
                "name": "write_graph_file",
                "docstring": (
                    "将细胞和连接数据写入 Graphviz DOT 格式文件。\n\n"
                    "节点颜色编码：肌肉为橄榄绿、运动神经元为浅灰蓝、其他为淡紫。\n\n"
                    ":param filename: 输出 ``.gv`` 文件路径\n"
                    ":param cells: 细胞名称列表\n"
                    ":param elec_conns: 电连接边描述列表\n"
                    ":param chem_conns: 化学连接边描述列表\n"
                    ":param layout: Graphviz 布局引擎（默认 ``neato``）"
                ),
            },
            {
                "name": "find_nml_files",
                "docstring": (
                    "在指定目录中查找所有 ``.nml`` 文件。\n\n"
                    ":param directory: 搜索目录路径\n"
                    ":param recursive: 是否递归搜索子目录\n"
                    ":return: ``.nml`` 文件路径列表"
                ),
            },
            {
                "name": "execute_graph_generator",
                "docstring": (
                    "调用 Graphviz 命令行工具将 DOT 文件转换为 PNG 图片。\n\n"
                    "先用 ``neato`` 直接渲染，再用 ``dot → neato`` 两步渲染以优化布局。\n\n"
                    ":param graphviz_file: 输入 ``.gv`` 文件路径\n"
                    ":param fig_file: 输出 ``.png`` 文件路径"
                ),
            },
            {
                "name": "main",
                "docstring": (
                    "gen_graph 主入口：解析命令行参数，批量生成网络拓扑图。\n\n"
                    "对每个 ``.nml`` 文件生成 dot 和 neato 两种布局的图形。"
                ),
            },
        ],
    },
]

out = Path("scripts/add-docstring/specs/phase5.yaml")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(yaml.dump(specs, allow_unicode=True, sort_keys=False, default_flow_style=False), encoding="utf-8")
print(f"Written {out}")
