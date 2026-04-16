"""批量为阶段三文件添加 SP-CODE-2026-001 标准头部。

读取每个文件，在现有 `# 类与方法索引：` 之前插入功能描述段，
在索引末尾之后插入更新日志和当前维护者段，首尾用 `=====` 分隔线包围。
"""

import re

SEP = "# " + "=" * 77

DESCRIPTIONS = {
    "bioparameters.py": (
        "c302 框架的核心参数系统。定义 BioParameter 数据类和参数化模型原型\n"
        "#   （ParameterisedModelPrototype / c302ModelPrototype），提供参数注册、\n"
        "#   查询、更新机制以及多层级细胞和突触模型的抽象接口。"
    ),
    "parameters_A.py": (
        "Level A 参数层级定义。使用最简单的积分放电（Integrate & Fire）神经元\n"
        "#   和事件驱动双指数突触（ExpTwoSynapse），缝隙连接通过事件突触近似\n"
        "#   （非真实 GapJunction）。"
    ),
    "parameters_B.py": (
        "Level B 参数层级定义。在 Level A 基础上增加 activity 变量和真实缝隙\n"
        "#   连接（GapJunction），使用自定义 IafActivityCell 组件。"
    ),
    "parameters_C.py": (
        "Level C 参数层级定义。使用单室导电模型和 Hodgkin-Huxley 型离子通道\n"
        "#   （慢钾/快钾/钙通道），化学突触为事件驱动 ExpTwoSynapse，缝隙连接\n"
        "#   为真实 GapJunction。"
    ),
    "parameters_C0.py": (
        "Level C0 参数层级定义。简化的 Morris-Lecar 类导电模型，无快钾通道、\n"
        "#   钙通道无失活门控，化学突触改为模拟型（GradedSynapse），适合非放电\n"
        "#   神经元网络。"
    ),
    "parameters_C1.py": (
        "Level C1 参数层级定义。保留 C 级完整 HH 离子通道，但化学突触从事件\n"
        "#   驱动改为模拟型（GradedSynapse），是 C 和 C0 之间的混合方案。"
    ),
    "parameters_C2.py": (
        "Level C2 参数层级定义（开发中）。在 C 基础上增加模拟突触、延迟缝隙\n"
        "#   连接（DelayedGapJunction）、本体感觉反馈连接（ProprioGapJunction）\n"
        "#   等自定义组件，用于探索运动回路时序传播。"
    ),
    "parameters_D.py": (
        "Level D 参数层级定义。使用多室导电模型，需加载 NeuroML 细胞形态文件\n"
        "#   （_D.cell.nml），新增胞质电阻率（resistivity）参数，化学突触为事件\n"
        "#   驱动 ExpTwoSynapse。"
    ),
    "parameters_D1.py": (
        "Level D1 参数层级定义。多室导电模型（继承自 D），但化学突触改为模拟型\n"
        "#   （GradedSynapse / GradedSynapse2），可能是「完整规模」模型的中期目标。"
    ),
    "parameters_BC1.py": (
        "Level BC1 混合参数层级定义。细胞使用 B 级的 IafActivityCell，突触使用\n"
        "#   C1 级的 GradedSynapse，兼顾计算效率和模拟型突触传递。"
    ),
    "parameters_W2D.py": (
        "Level W2D 参数层级定义。来自 Worm2D 二维虫体运动模型的简化细胞\n"
        "#   （仅偏置和增益参数），突触为连续型 OutputSynapse，参数数量极少。"
    ),
}

CHANGELOG = "2026-04-16  Copilot  添加中文 docstring 和行内注释（计划1阶段三）"
MAINTAINER = "Copilot"

import os

BASE = r"e:\Model-Design\c302\project\c302"

for filename, desc in DESCRIPTIONS.items():
    filepath = os.path.join(BASE, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 找到现有头部的起始：`#\n# 类与方法索引：\n`
    # 头部从第一行 `#` 开始，到 `"""` 之前结束
    # 替换开头的 `#\n# 类与方法索引：` 为带分隔线和功能描述的版本
    old_start = "#\n# 类与方法索引："
    new_start = (
        f"{SEP}\n"
        f"# 功能描述：\n"
        f"#   {desc}\n"
        f"#\n"
        f"# 类与方法索引："
    )
    if old_start not in content:
        print(f"[SKIP] {filename}: 未找到旧头部起始标记")
        continue
    content = content.replace(old_start, new_start, 1)

    # 找到索引块的结束位置：最后一个 `#   ` 索引行之后、`"""` 之前
    # 在紧挨 `"""` 之前的那个位置插入更新日志/维护者/分隔线
    # 模式：索引结束行 + 换行 + `"""`
    pattern = r'(#\s+\S.*?—.*?\n)(""")'
    # 找到最后一个匹配
    matches = list(re.finditer(pattern, content))
    if not matches:
        print(f"[SKIP] {filename}: 未找到索引块结束位置")
        continue
    last_match = matches[-1]
    insert_pos = last_match.start(2)  # `"""` 的位置

    footer = (
        f"#\n"
        f"# 更新日志：\n"
        f"#   {CHANGELOG}\n"
        f"#\n"
        f"# 当前维护者：{MAINTAINER}\n"
        f"{SEP}\n"
    )
    content = content[:insert_pos] + footer + content[insert_pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] {filename}")
