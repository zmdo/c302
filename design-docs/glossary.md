# c302 项目领域词汇表

> 统一翻译词汇，避免同一概念使用不同中文译名。

## 神经科学术语

| 英文术语 | 中文译名 | 说明 | 主要出现模块 |
|---------|---------|------|------------|
| neuron | 神经元 | 神经系统的基本功能单元 | 全局 |
| synapse | 突触 | 神经元间信号传递的连接结构 | ConnectomeReader, __init__ |
| connectome | 连接组 | 神经元间完整连接图谱 | 全局 |
| gap junction | 缝隙连接 | 两个神经元之间的电突触连接，允许离子直接流通 | ConnectomeReader, __init__ |
| membrane potential | 膜电位 | 细胞膜内外的电位差 | parameters_C, parameters_D |
| conductance | 电导 | 离子通道通过电流的能力，单位 nS | bioparameters, parameters_* |
| ion channel | 离子通道 | 控制特定离子通过细胞膜的蛋白质通道 | parameters_C, parameters_D |
| acetylcholine | 乙酰胆碱 | 兴奋性神经递质 | ConnectomeReader |
| GABA | γ-氨基丁酸 | 抑制性神经递质 | ConnectomeReader |
| glutamate | 谷氨酸 | 兴奋性神经递质 | ConnectomeReader |
| dopamine | 多巴胺 | 调节性神经递质 | ConnectomeReader |
| serotonin | 血清素（5-HT） | 调节性神经递质 | ConnectomeReader |
| capacitance | 电容 | 细胞膜存储电荷的能力，单位 pF | bioparameters |
| axon | 轴突 | 神经元传出信号的突起 | ConnectomeReader |
| dendrite | 树突 | 神经元接收信号的突起 | ConnectomeReader |
| neurotransmitter | 神经递质 | 突触间传递信号的化学物质 | ConnectomeReader, c302_info |
| receptor | 受体 | 与神经递质结合的蛋白质分子 | c302_info |
| motor neuron | 运动神经元 | 控制肌肉收缩的神经元 | gen_graph, c302_FW |
| sensory neuron | 感觉神经元 | 接收外部刺激的神经元 | c302_TapWithdrawal |
| interneuron | 中间神经元 | 连接感觉和运动神经元的神经元 | c302_TapWithdrawal |

## NeuroML/LEMS 建模术语

| 英文术语 | 中文译名 | 说明 | 主要出现模块 |
|---------|---------|------|------------|
| Population | 种群 | 同一类型神经元或肌肉细胞的集合 | __init__ |
| Instance | 实例 | 种群中的单个细胞对象 | __init__ |
| Projection | 投射 | 两个种群之间的化学突触连接集合 | __init__ |
| ElectricalProjection | 电突触投射 | 两个种群之间的缝隙连接集合 | __init__ |
| ContinuousProjection | 持续投射 | 分级/模拟突触连接集合（Level C+） | __init__ |
| Connection | 连接 | 投射中单对细胞之间的具体连接 | __init__ |
| InputList | 输入列表 | 对指定细胞施加外部刺激的列表 | __init__ |
| PulseGenerator | 脉冲发生器 | 产生方波电流刺激的组件 | __init__, c302_IClamp |
| SineGenerator | 正弦发生器 | 产生正弦波电流刺激的组件 | __init__, c302_MusclesSine |
| NeuroMLDocument | NeuroML 文档 | NeuroML 模型的顶层容器 | __init__ |
| Network | 网络 | 包含种群、投射和输入的完整神经网络 | __init__ |
| LEMS | LEMS | 低熵模型规范语言，描述仿真参数 | __init__, runAndPlot |
| Simulation | 仿真 | LEMS 定义的运行参数（时长、步长、输出） | runAndPlot |
| ComponentType | 组件类型 | LEMS 中定义行为的基本类型 | parameters_C, parameters_D |
| Cell | 细胞 | NeuroML 中神经元或肌肉细胞的模型定义 | bioparameters |
| Segment | 片段 | 细胞形态学中的基本空间单元 | NeuroMLUtilities |

## 电生理术语

| 英文术语 | 中文译名 | 说明 | 主要出现模块 |
|---------|---------|------|------------|
| integrate-and-fire (IaF) | 积分放电 | 最简单的神经元模型，膜电位达阈值即放电 | parameters_A |
| Hodgkin-Huxley (HH) | Hodgkin-Huxley 模型 | 基于离子通道动力学的经典神经元模型 | parameters_C, parameters_D |
| leak conductance | 泄漏电导 | 静息状态下细胞膜的基础电导 | bioparameters, parameters_* |
| activation gate | 激活门 | 离子通道的打开门控变量 | parameters_C |
| inactivation gate | 失活门 | 离子通道的关闭门控变量 | parameters_C |
| calcium dynamics | 钙动力学 | 细胞内钙离子浓度变化的数学描述 | parameters_C |
| voltage clamp | 电压钳 | 将膜电位固定在特定值的实验技术 | parameters_C |
| resting potential | 静息电位 | 未受刺激时细胞膜的电位值 | bioparameters |
| threshold | 阈值 | 触发动作电位所需的最小膜电位 | parameters_A, parameters_B |
| reversal potential | 反转电位 | 离子电流方向改变时的膜电位值 | bioparameters, parameters_* |
| time constant | 时间常数 | 描述膜电位变化速度的特征时间 | bioparameters |
| spike | 动作电位（峰电位） | 神经元快速去极化-复极化的电信号 | parameters_A |

## 线虫生物学术语

| 英文术语 | 中文译名 | 说明 | 主要出现模块 |
|---------|---------|------|------------|
| C. elegans | 秀丽隐杆线虫 | 模式生物，成体恰好 302 个神经元 | 全局 |
| hermaphrodite | 雌雄同体 | C. elegans 的主要性别形态，含 302 个神经元 | ConnectomeReader |
| body wall muscle | 体壁肌肉 | 线虫身体运动的肌肉细胞，共 95 块 | __init__, c302_Muscles |
| pharynx | 咽部 | 线虫的进食器官，含独立的 20 个神经元回路 | c302_Pharyngeal |
| tap withdrawal | 触碰退缩 | 线虫受到机械刺激后的退缩反射 | c302_TapWithdrawal |
| forward locomotion | 前行运动 | 线虫正向移动的运动模式 | c302_FW |
| dorsal | 背侧 | 线虫身体的上方（背部方向） | ConnectomeReader |
| ventral | 腹侧 | 线虫身体的下方（腹部方向） | ConnectomeReader |
| L4 larva | L4 幼虫 | 线虫第四期幼虫阶段 | White_L4, parameters_W2D |
| adult | 成体 | 线虫的成年阶段 | White_A |
| nerve ring | 神经环 | 线虫头部的环形神经结构 | ConnectomeReader |
| ventral nerve cord | 腹神经索 | 沿线虫腹侧延伸的神经束 | ConnectomeReader |

## c302 框架术语

| 英文术语 | 中文译名 | 说明 | 主要出现模块 |
|---------|---------|------|------------|
| parameter set | 参数层级 | c302 的模型抽象层级（A/B/C/C0/C1/C2/D/D1） | bioparameters, parameters_* |
| data reader | 数据读取器 | 读取连接组数据的模块（Spreadsheet/Updated/OpenWorm/White） | ConnectomeReader, __init__ |
| configuration script | 配置脚本 | 定义仿真场景的 Python 脚本（c302_*.py） | c302_Full 等 |
| syntype | 突触类型 | 突触的信号传递方式（excitatory/inhibitory） | ConnectomeReader |
| synclass | 突触分类 | 突触的神经递质类别（Acetylcholine/GABA 等） | ConnectomeReader |
| Level A | A 级模型 | 最简积分放电模型，无真实突触 | parameters_A |
| Level B | B 级模型 | 带活动变量的积分放电模型 | parameters_B |
| Level C | C 级模型 | 完整 Hodgkin-Huxley 离子通道模型 | parameters_C |
| Level D | D 级模型 | 多室电导模型，含细胞形态 | parameters_D |
| connection_number_override | 连接数覆盖 | 通过正则表达式批量设置突触连接权重的机制 | __init__ |
| BioParameter | 生物参数 | 封装参数名、值、来源和确信度的数据类 | bioparameters |
| include_nonconnected_cells | 包含非连接细胞 | 是否将无连接的神经元也加入网络 | __init__, ConnectomeReader |
| neuromuscular junction | 神经肌肉接头 | 运动神经元与肌肉细胞之间的突触连接 | __init__, c302_MuscleTest |
| presynaptic | 突触前 | 突触连接中发送信号的一侧 | ConnectomeReader |
| postsynaptic | 突触后 | 突触连接中接收信号的一侧 | ConnectomeReader |
| unphysiological_offset_current | 偏置电流 | 施加于神经元的非生理性恒定电流，用于测试 | c302_Full, c302_IClamp |
| event-driven synapse | 事件驱动突触 | 通过离散脉冲事件而非连续信号传递的突触模型 | __init__ |
| leading zero | 前导零 | 神经元编号中的补零（如 VB01 vs VB1） | ConnectomeReader |
| rhythmic activity | 节律性活动 | 神经元或肌肉的周期性重复放电模式 | c302_Oscillator |
| gap junction / 间隙连接 | 缝隙连接（同义） | 同 gap junction，部分注释中使用"间隙连接"译法 | ConnectomeReader |
