"""Generate phase6.yaml docstring spec for Phase 6 target files."""
import yaml

spec = [
    {
        "file": "project/c302/CompareMain.py",
        "functions": [
            {
                "name": "comparitor",
                "docstring": (
                    "比较两个 XLS 连接组数据文件的差异。\n\n"
                    "读取两个 XLS 文件，格式化名称后进行配对匹配，\n"
                    "输出匹配对、仅存在于文件1的连接、仅存在于文件2的连接。\n\n"
                    ":param fName1: 第一个 XLS 文件路径\n"
                    ":param fName2: 第二个 XLS 文件路径\n"
                ),
            },
            {
                "name": "getColumns",
                "docstring": (
                    "从制表符分隔的文本文件中读取列数据。\n\n"
                    ":param fileIn: 已打开的文件对象\n"
                    ":param delim: 列分隔符（默认制表符）\n"
                    ":param header: 首行是否为表头\n"
                    ":return: ``(cols, indexName)`` 二元组，cols 为列数据字典，indexName 为列索引映射\n"
                ),
            },
            {
                "name": "getColumnsXls",
                "docstring": (
                    "从 XLS 电子表格文件中读取列数据。\n\n"
                    "使用 xlrd 打开工作簿，读取第一个工作表的前 4 列。\n\n"
                    ":param fileIn: XLS 文件路径\n"
                    ":return: ``(cols, indexName)`` 二元组，cols 为列数据字典，indexName 为列索引映射\n"
                ),
            },
            {
                "name": "sortTwoColumns",
                "docstring": (
                    "按前两列（From/To 神经元）对字典进行排序。\n\n"
                    ":param cols: 列数据字典\n"
                ),
            },
            {
                "name": "formatNames",
                "docstring": (
                    "格式化神经元名称，移除中间的填充零。\n\n"
                    ":param cols: 列数据字典\n"
                    ":param indexName: 列索引映射\n"
                ),
            },
            {
                "name": "matchLists",
                "docstring": (
                    "比较两个连接列表，提取匹配对并从原列表中移除。\n\n"
                    "执行三轮匹配：\n"
                    "1. 在长列表与短列表之间查找完全匹配的连接对\n"
                    "2. 在长列表与已匹配列表之间查找重复连接\n"
                    "3. 在长列表中查找与已匹配对方向相反的连接（A→B vs B→A）\n\n"
                    ":param cols1: 第一个连接列表\n"
                    ":param cols2: 第二个连接列表\n"
                    ":param indexName1: 第一个列表的列索引映射\n"
                    ":param indexName2: 第二个列表的列索引映射\n"
                    ":return: ``(matches, col1, col2)`` 三元组\n"
                ),
            },
            {
                "name": "typeMapping",
                "docstring": (
                    "连接类型映射（未完成）。\n\n"
                    "预期将 ``EJ`` 映射为 ``GapJunction``，\n"
                    "``R``/``Rp``/``S``/``Sp`` 映射为 ``Send``。\n\n"
                    ":param cols1: 第一个连接列表\n"
                    ":param cols2: 第二个连接列表\n"
                    ":param indexName1: 第一个列表的列索引映射\n"
                    ":param indexName2: 第二个列表的列索引映射\n"
                ),
            },
        ],
    },
    {
        "file": "project/c302/backers.py",
        "functions": [
            {
                "name": "get_adopted_cell_names",
                "docstring": (
                    "读取 OpenWorm 赞助者认领的细胞名称映射。\n\n"
                    "从 ``data/adopters.txt`` 文件中解析 ``细胞名:认领名`` 格式的映射关系。\n\n"
                    ":param root: 数据目录路径（默认为模块所在目录下的 ``data/``）\n"
                    ":return: ``{细胞名: 认领名}`` 字典\n"
                ),
            },
        ],
    },
    {
        "file": "project/c302/c302_info.py",
        "functions": [
            {
                "name": "generate_c302_info",
                "docstring": (
                    "从 NeuroML 文档生成神经元和肌肉的汇总信息表。\n\n"
                    "解析网络中所有连续投射和电投射，通过 owmeta 查询细胞类型、\n"
                    "神经递质和受体信息，生成 Markdown 格式汇总文件。\n\n"
                    ":param nml_doc: NeuroML 文档对象\n"
                    ":param verbose: 是否输出详细日志\n"
                ),
            },
            {
                "name": "_info_set",
                "docstring": (
                    "将集合排序后用逗号连接为字符串。\n\n"
                    ":param s: 可迭代对象\n"
                    ":return: 逗号分隔的排序字符串\n"
                ),
            },
        ],
    },
    {
        "file": "project/c302/NeuroMLUtilities.py",
        "functions": [
            {
                "name": "getSegmentIds",
                "docstring": (
                    "提取细胞形态学中所有片段的 ID 列表。\n\n"
                    ":param cell: NeuroML Cell 对象\n"
                    ":return: 片段 ID 列表\n"
                ),
            },
            {
                "name": "get3DPosition",
                "docstring": (
                    "计算细胞指定片段上某点的三维坐标。\n\n"
                    "根据 ``fraction_along`` 在片段的近端（proximal）和远端（distal）之间\n"
                    "进行线性插值。若近端缺失，则使用父片段的远端作为起点。\n\n"
                    ":param cell: NeuroML Cell 对象\n"
                    ":param segment_index: 片段索引\n"
                    ":param fraction_along: 沿片段的分数位置（0.0=近端，1.0=远端）\n"
                    ":return: ``(x, y, z)`` 三维坐标元组\n"
                ),
            },
            {
                "name": "fract",
                "docstring": (
                    "在两点之间进行线性插值。\n\n"
                    "公式：``a + (b - a) * f``\n\n"
                    ":param a: 起始值\n"
                    ":param b: 终止值\n"
                    ":param f: 插值分数（0.0=a，1.0=b）\n"
                    ":return: 插值结果\n"
                ),
            },
        ],
    },
]

with open("scripts/add-docstring/specs/phase6.yaml", "w", encoding="utf-8") as f:
    yaml.dump(spec, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
print("Written scripts/add-docstring/specs/phase6.yaml")
