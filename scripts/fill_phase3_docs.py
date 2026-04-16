"""Fill in .py.md analysis docs for phase 3 files."""
import os

TODAY = '2026-04-16'

docs = {
    'bioparameters.py': {
        'summary': 'c302 框架核心参数系统。定义 `BioParameter` 数据类封装参数名/值/来源/确定性，`ParameterisedModelPrototype` 提供参数注册/查询/更新接口，`c302ModelPrototype` 定义各层级模型组件的抽象接口（细胞/突触创建）。是所有 `parameters_*.py` 的公共基类，位于参数化层核心。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件，重点 `ParameterisedModelPrototype` 类定义部分\n**发现**：\n- B 类：1 处——L132 `# bioparameters = []`，是旧版类变量写法，当前已改为在 `__init__` 中用实例属性替代，已添加 `[备选]` 标注\n**结论**：勘误完成，verify_comment_only 验证通过',
        'changes': '| 2026-04-16 | 计划2阶段三 | L132 [备选]标注 | 注释勘误：标注旧版类变量写法 |',
    },
    'parameters_A.py': {
        'summary': 'Level A 参数层级定义。使用最简单的 IaF（积分放电）神经元和事件驱动 ExpTwoSynapse 化学突触，缝隙连接通过事件突触近似。适合快速验证网络结构，无真实生物物理特性。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件，重点 `set_default_bioparameters()`\n**发现**：\n- A 类：1 处——`unphysiological_offset_current` 行末 `# Can be activated later` 已翻译为中文\n**结论**：勘误完成，verify_comment_only 验证通过',
        'changes': '| 2026-04-16 | 计划2阶段三 | `unphysiological_offset_current` 行末注释 | A 类翻译：Can be activated later |',
    },
    'parameters_B.py': {
        'summary': 'Level B 参数层级定义。在 A 级基础上增加 `activity` 变量和真实 GapJunction 缝隙连接，使用自定义 `IafActivityCell` 组件，可追踪神经元活动状态。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件审阅\n**发现**：无 A/B/C 类问题，注释质量良好\n**结论**：无需修改',
        'changes': '',
    },
    'parameters_C.py': {
        'summary': 'Level C 参数层级定义。完整 Hodgkin-Huxley 离子通道模型（K_slow/K_fast/Ca_boyle 通道），事件驱动化学突触，真实 GapJunction 缝隙连接，含钙动力学（CaPool）。是最接近真实神经元生物物理特性的单室模型。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件，重点 `create_generic_neuron_cell` / `create_generic_muscle_cell`\n**发现**：\n- A 类 5 处：`unphysiological_offset_current` 行末 `# Can be activated later`（1处）；`IntracellularProperties` 块中 `NOTE:` 轴向电阻率注释（×2）和钙反转电位注释（×2）——均已翻译\n**结论**：勘误完成，verify_comment_only 验证通过',
        'changes': '| 2026-04-16 | 计划2阶段三 | 5 处 A 类注释翻译 | Can be activated later + NOTE:×2×2 |',
    },
    'parameters_C0.py': {
        'summary': 'Level C0 参数层级定义。与 C 相同的 HH 离子通道，但化学突触改为模拟型 GradedSynapse（适合非放电神经元），适合 oscillator 类网络。对应 C 和 C1 之间最常用的研究参数层级。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件，重点 `create_generic_neuron_cell` / `create_generic_muscle_cell`\n**发现**：\n- A 类 5 处（计划标注 3 处，实际发现 5 处）：`Can be activated later`（1处）+ `NOTE:`×2 在神经元细胞块（L280/L283）+ `NOTE:`×2 在肌肉细胞块（L376/L379）——均已翻译\n**结论**：勘误完成，verify_comment_only 验证通过',
        'changes': '| 2026-04-16 | 计划2阶段三 | 5 处 A 类注释翻译（计划3处实发现5处） | Can be activated later + NOTE:×4 |',
    },
    'parameters_C1.py': {
        'summary': 'Level C1 参数层级定义。保留 C 级完整 HH 离子通道，化学突触改为模拟型 GradedSynapse，是 C 和 C0 的混合方案。适用于探索放电神经元与模拟突触耦合的行为。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件审阅\n**发现**：无 A/B/C 类问题，注释质量良好\n**结论**：无需修改',
        'changes': '',
    },
    'parameters_C2.py': {
        'summary': 'Level C2 参数层级定义。在 C0 基础上大量参数化神经元-运动神经元仿真突触（延迟缝隙连接 DelayedGapJunction，sigmoid 调制），含以 AVBL/AVBR 到 DB* 为核心的运动回路。是本层中最复杂的参数集（约 800 行），包含大量备选参数配置（38 处注释掉的备选行）。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件，重点 `set_default_bioparameters()` 函数（约 700 行）\n**发现**：\n- B 类 34 处（真实 `#` 注释，排除三引号块）：注释掉的备选 `add_bioparameter()` 调用、备选 motors 列表、备选单位变量——按 15 个逻辑组各添加一个 `[备选]` 标注\n- A 类 3 处：`Can be activated later`（1处）+ `NOTE:`×2（L783/L786）——已翻译\n- 另有若干注释代码在三引号块内，属于字符串形式的注释，未标注\n**结论**：勘误完成，verify_comment_only 验证通过',
        'changes': '| 2026-04-16 | 计划2阶段三 | 34 处 B 类 [备选] 标注 + 3 处 A 类翻译 | 注释勘误：标注大量备选参数配置 |',
    },
    'parameters_D.py': {
        'summary': 'Level D 参数层级定义。多室导电模型（使用真实细胞形态学文件），保留完整 HH 离子通道，含钙动力学。是最高保真的参数层级，计算代价最大。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件，重点 `create_generic_neuron_cell` / `create_generic_muscle_cell`\n**发现**：\n- A 类 5 处：`Can be activated later`（1处）+ `NOTE:`×2 在神经元块（L280/L285）+ `NOTE:`×2 在肌肉块（L375/L380）——已翻译\n**结论**：勘误完成，verify_comment_only 验证通过',
        'changes': '| 2026-04-16 | 计划2阶段三 | 5 处 A 类注释翻译 | Can be activated later + NOTE:×4 |',
    },
    'parameters_D1.py': {
        'summary': 'Level D1 参数层级定义。D 级的变体，在多室导电模型基础上调整了突触参数，主要用于特定神经环路实验。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件，重点 `set_default_bioparameters()`\n**发现**：\n- A 类 1 处：`unphysiological_offset_current` 行末 `# Can be activated later`——已翻译\n**结论**：勘误完成，verify_comment_only 验证通过',
        'changes': '| 2026-04-16 | 计划2阶段三 | `unphysiological_offset_current` 行末注释 | A 类翻译：Can be activated later |',
    },
    'parameters_BC1.py': {
        'summary': 'Level BC1 参数层级定义（B/C 混合实验层级）。结合 IaF 细胞简单性和部分 C 级模拟突触特性，用于探索混合动力学模式。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件，重点 `set_default_bioparameters()`\n**发现**：\n- A 类 1 处：`unphysiological_offset_current` 行末 `# Can be activated later`——已翻译\n**结论**：勘误完成，verify_comment_only 验证通过',
        'changes': '| 2026-04-16 | 计划2阶段三 | `unphysiological_offset_current` 行末注释 | A 类翻译：Can be activated later |',
    },
    'parameters_W2D.py': {
        'summary': 'Level W2D 参数层级定义。基于 White 等 2D 线虫运动模型的参数集，简化参数结构，无钙动力学，适配 W2D 细胞形态学。',
        'analysis': '### 2026-04-16 注释勘误\n\n**范围**：全文件，重点 `set_default_bioparameters()`\n**发现**：\n- A 类 1 处：`unphysiological_offset_current` 行末 `# Can be activated later`——已翻译\n**结论**：勘误完成，verify_comment_only 验证通过',
        'changes': '| 2026-04-16 | 计划2阶段三 | `unphysiological_offset_current` 行末注释 | A 类翻译：Can be activated later |',
    },
}

base = 'project/c302-docs/src'
for name, info in docs.items():
    fpath = os.path.join(base, f'{name}.md')
    with open(fpath, encoding='utf-8') as f:
        content = f.read()

    content = content.replace('<!-- TODO: 填写模块功能描述 -->', info['summary'])
    content = content.replace('<!-- 按时间倒序记录每次分析/勘误的发现 -->', info['analysis'])

    if info['changes']:
        old_row = '| 日期 | commit | 修改范围 | 修改原因 |'
        sep_row = '|------|--------|---------|---------|'
        # Add separator if missing
        if sep_row not in content:
            content = content.replace(old_row, old_row + '\n' + sep_row)
        # Add data row(s)
        full_header = old_row + '\n' + sep_row
        if full_header in content and info['changes'] not in content:
            content = content.replace(full_header, full_header + '\n' + info['changes'])

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'[OK] {fpath}')

print('Done.')
