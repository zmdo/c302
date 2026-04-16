"""为 __init__.py 批量翻译英文注释和添加关键行内中文注释。"""
import re

filepath = r"e:\Model-Design\c302\project\c302\__init__.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# ── 翻译现有英文注释为中文 ──
translations = {
    # 4.1.1: 翻译现有英文注释
    '# soma positions from http://www.wormatlas.org/neuronalwiring.html - 2.2 Neuron Description (Neuron Types)':
        '# 运动神经元 soma 位置（来源：wormatlas.org - 2.2 神经元描述）',
    '    # Use the data reader to give a list of all cells and a list of all connections':
        '    # 使用数据读取器获取所有细胞列表和连接列表',
    '    # This could be replaced with a call to "DatabaseReader" or "OpenWormNeuroLexReader" in future...':
        '    # 将来可替换为 DatabaseReader 或 OpenWormNeuroLexReader',
    '    # If called from unittest folder ammend path to "../../../../"':
        '    # 若从单元测试目录调用，需修正路径',
    '        # Go through our list and get the neuron object associated with each name.':
        '        # 遍历细胞名称列表，获取每个名称对应的神经元对象',
    '        # Store these in another list.':
        '        # 存入独立的信息字典',
    '                # At this point, we should only have Neurons and Muscles because the reader':
        '                # 此时应仅剩 Neuron 和 Muscle（数据读取器已过滤非神经/肌肉细胞）',
    '                # filters them out':
        '                # 因此遇到其他类型则抛出异常',
    '    # To hold all Cell NeuroML objects vs. names':
        '    # 存储所有 Cell NeuroML 对象（键为细胞名称）',
    '                # build a Population data structure out of the cell name\n                pop0 = Population(\n                    id=cell,\n                    component=params.generic_neuron_cell.id,':
        '                # 用细胞名称构建 Population 数据结构（非 D 级使用通用神经元组件）\n                pop0 = Population(\n                    id=cell,\n                    component=params.generic_neuron_cell.id,',
    '                # build a Population data structure out of the cell name\n                pop0 = Population(\n                    id=cell, component=cell,':
        '                # D 级使用细胞本身作为 Population 组件（多室模型，每个细胞独立）\n                pop0 = Population(\n                    id=cell, component=cell,',
    '            # neuron, neuron.type(), neuron.receptor(), neuron.neurotransmitter(), short, color':
        '            # 从 owmeta 信息中提取颜色、类型、受体和神经递质属性',
    '            # put that Population into the Network data structure from above':
        '            # 将 Population 加入网络数据结构',
    '            # also use the cell name to grab the morphology file, as a NeuroML data structure':
        '            # 同时使用细胞名加载形态文件（NeuroML 格式），',
    '            #  into the \'all_cells\' dict':
        '            # 存入 all_cells 字典',
    '            # build a Population data structure out of the cell name\n            pop0 = Population(\n                id=muscle,':
        '            # 为肌肉构建 Population 数据结构\n            pop0 = Population(\n                id=muscle,',
    '                # No muscles adopted yet, but just in case they are in future...':
        '                # 目前尚无被领养的肌肉，但预留接口以防将来有',
    '            # take information about each connection and package it into a\n            # NeuroML Projection data structure\n            proj_id = get_projection_id(\n                conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype\n            )\n            conn_shorthand = "%s-%s" % (conn.pre_cell, conn.post_cell)\n\n            elect_conn = False\n            analog_conn = False\n            nonneuroml_conn = False\n\n            conn_type = "neuron_to_neuron"':
        '            # 将每条连接信息封装为 NeuroML Projection 数据结构\n            proj_id = get_projection_id(\n                conn.pre_cell, conn.post_cell, conn.synclass, conn.syntype\n            )\n            conn_shorthand = "%s-%s" % (conn.pre_cell, conn.post_cell)\n\n            elect_conn = False  # 是否为电突触（缝隙连接）\n            analog_conn = False  # 是否为模拟突触\n            nonneuroml_conn = False  # 是否为非 NeuroML 自定义连接\n\n            conn_type = "neuron_to_neuron"',
    '                # Add a Connection with the closest locations\n                conn0 = ElectricalConnectionInstanceW(':
        '                # 创建加权电连接实例\n                conn0 = ElectricalConnectionInstanceW(',
    '                # Add a Connection with the closest locations\n\n                pre_cell_id = get_cell_id_string(conn.pre_cell, params)\n                post_cell_id = get_cell_id_string(conn.post_cell, params, muscle=True)':
        '                # 创建事件驱动化学突触连接\n\n                pre_cell_id = get_cell_id_string(conn.pre_cell, params)\n                post_cell_id = get_cell_id_string(conn.post_cell, params, muscle=True)',
    '        # if running unittest concat template_path':
        '        # 单元测试时拼接模板路径前缀',
    '# Get the standard name for a network connection':
        '# 获取网络连接的标准命名',
}

for eng, chn in translations.items():
    if eng in content:
        content = content.replace(eng, chn, 1)

# ── 4.1.2: 在 generate() 中添加十大步骤段落注释 ──
# 步骤1: 参数覆盖处理
content = content.replace(
    '    regex_param_overrides = {"mirrored_elec_conn_params": {}}',
    '    # ── 步骤 1：处理参数覆盖（param_overrides）──\n    regex_param_overrides = {"mirrored_elec_conn_params": {}}',
    1
)
# 步骤2: 创建模型组件
content = content.replace(
    '    params.create_models()\n\n    if vmin is None:',
    '    # ── 步骤 2：创建所有细胞和突触模型组件 ──\n    params.create_models()\n\n    # ── 步骤 3：设置绘图电压范围默认值 ──\n    if vmin is None:',
    1
)
# 步骤4: 初始化 NeuroML 文档
content = content.replace(
    '    nml_doc = NeuroMLDocument(id=net_id, notes=info)',
    '    # ── 步骤 4：初始化 NeuroML 文档和网络对象 ──\n    nml_doc = NeuroMLDocument(id=net_id, notes=info)',
    1
)
# 步骤5: 细胞种群创建
content = content.replace(
    '    cell_names, conns = get_cell_names_and_connection(data_reader)',
    '    # ── 步骤 5：读取连接组数据，创建神经元种群（Population） ──\n    cell_names, conns = get_cell_names_and_connection(data_reader)',
    1
)
# 步骤6: 肌肉种群创建
content = content.replace(
    '    mneurons, all_muscles, muscle_conns = get_cell_muscle_names_and_connection(',
    '    # ── 步骤 6：创建肌肉种群 ──\n    mneurons, all_muscles, muscle_conns = get_cell_muscle_names_and_connection(',
    1
)
# 步骤7: 神经元间连接遍历
content = content.replace(
    '    existing_synapses = {}\n\n    for conn in conns:',
    '    # ── 步骤 7：遍历神经元间连接，创建突触投射 ──\n    existing_synapses = {}  # 突触原型缓存，避免重复注册\n\n    for conn in conns:',
    1
)
# 步骤8: 肌肉连接遍历
content = content.replace(
    '    if len(muscles_to_include) > 0:\n        for conn in muscle_conns:',
    '    # ── 步骤 8：遍历神经元-肌肉/肌肉-肌肉连接 ──\n    if len(muscles_to_include) > 0:\n        for conn in muscle_conns:',
    1
)
# 步骤9: 写入文件
content = content.replace(
    '    template_path = root_dir',
    '    # ── 步骤 9：输出 .net.nml 和 LEMS 仿真文件 ──\n    template_path = root_dir',
    1
)

# ── 4.1.3: owmeta 导入注释 ──
content = content.replace(
    '    owmeta_installed = True',
    '    owmeta_installed = True  # owmeta 安装成功标记',
    1
)
content = content.replace(
    '    print("owmeta not installed! Proceeding anyway...")',
    '    print("owmeta not installed! Proceeding anyway...")  # owmeta 未安装，仅使用缓存数据',
    1
)

# ── 4.1.6: connection_number_override 注释 ──
content = content.replace(
    '            if conn_number_override:\n                # number_syns = conn_number_override[conn_shorthand]\n\n                for conn_num_override in conn_number_override.keys():',
    '            # 连接数量覆盖：精确匹配或正则匹配覆盖连接数量\n            if conn_number_override:\n                for conn_num_override in conn_number_override.keys():',
    1
)

# ── 4.1.10: load_data_reader 工厂注释 ──
content = content.replace(
    'DEFAULT_DATA_READER = "cect.readers.SpreadsheetDataReader"',
    '# 默认数据读取器：使用 cect 包的 SpreadsheetDataReader\nDEFAULT_DATA_READER = "cect.readers.SpreadsheetDataReader"',
    1
)
content = content.replace(
    'FW_DATA_READER = "cect.readers.UpdatedSpreadsheetDataReader2"',
    '# 前向运动专用数据读取器\nFW_DATA_READER = "cect.readers.UpdatedSpreadsheetDataReader2"',
    1
)

# ── 4.1.9: write_to_file 注释 ──
content = content.replace(
    '    #######   Write to file  ######',
    '    # ── 写入 NeuroML 网络文件和 LEMS 仿真文件 ──',
    1
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done: inline comments added to __init__.py")
