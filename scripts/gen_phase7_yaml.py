"""Generate phase7.yaml docstring spec for all 16 Phase 7 config scripts."""
import yaml

# Config descriptions map: file -> (chinese description of the circuit/config)
configs = {
    "c302_Full.py": (
        "全连接组配置（302 神经元）",
        "配置 c302 全连接组网络，包含 302 个神经元。\n"
        "随机选取部分神经元施加脉冲刺激，用于整体网络行为验证。\n",
    ),
    "c302_FW.py": (
        "前行运动回路配置",
        "配置 c302 前行（Forward）运动回路。\n"
        "选取 AVB、DB、VB 等前行运动相关神经元，\n"
        "通过参数覆盖调节突触连接权重以产生前行波。\n",
    ),
    "c302_IClamp.py": (
        "电流钳测试配置",
        "配置单个或少量神经元的电流钳注入测试。\n"
        "用于验证单细胞模型在不同参数层级下的响应特性。\n",
    ),
    "c302_IClampMuscle.py": (
        "肌肉电流钳配置",
        "配置肌肉细胞的电流钳注入测试。\n"
        "用于验证肌肉模型在刺激下的膜电位响应。\n",
    ),
    "c302_MuscleTest.py": (
        "肌肉单元测试配置",
        "配置神经元到肌肉连接的单元测试。\n"
        "选取部分运动神经元和对应肌肉，验证神经肌肉接头功能。\n",
    ),
    "c302_Muscles.py": (
        "神经肌肉控制配置",
        "配置包含运动神经元和体壁肌肉的网络。\n"
        "选取 DA/DB/DD/VA/VB/VD 运动神经元及对应肌肉，\n"
        "验证神经肌肉系统的协调控制。\n",
    ),
    "c302_MusclesSine.py": (
        "正弦驱动肌肉配置",
        "配置使用正弦波信号驱动的肌肉网络。\n"
        "对运动神经元施加正弦波电流刺激，\n"
        "验证肌肉系统对周期性输入的响应。\n",
    ),
    "c302_Oscillator.py": (
        "振荡回路配置",
        "配置 AVB/DB/VB 等神经元构成的振荡回路。\n"
        "通过交互抑制和兴奋产生节律性振荡活动。\n",
    ),
    "c302_OscillatorM.py": (
        "振荡驱动肌肉配置",
        "配置振荡回路驱动的肌肉网络。\n"
        "在振荡回路基础上添加运动神经元到肌肉的连接，\n"
        "验证节律性运动输出。\n",
    ),
    "c302_Pharyngeal.py": (
        "咽部摄食回路配置",
        "配置咽部神经系统的摄食回路。\n"
        "选取 I1-I6、M1-M5、MC、MI、NSM 等 20 个咽部神经元，\n"
        "验证摄食泵送节律。\n",
    ),
    "c302_RIA.py": (
        "RIA 单细胞测试配置",
        "配置 RIA 中间神经元的单细胞测试。\n"
        "仅包含 RIAL/RIAR 两个细胞，用于验证单细胞模型响应。\n",
    ),
    "c302_Social.py": (
        "社交决策回路配置",
        "配置社交决策回路（群聚/独居行为）。\n"
        "选取 RMGR、ASHR、ASKR、AWBR、IL2R 等感觉和中间神经元，\n"
        "模拟线虫对社交信号的决策过程。\n",
    ),
    "c302_Syns.py": (
        "突触连接测试配置",
        "配置少量神经元对的突触连接测试。\n"
        "选取 URYDL/SMDDR/VB11 等细胞，验证各类突触模型的功能。\n",
    ),
    "c302_TapWithdrawal.py": (
        "触碰退缩反射配置",
        "配置触碰退缩（Tap Withdrawal）回路。\n"
        "包含 ALM、AVM、PLM 等触觉感觉神经元和 AVA/AVB/AVD 等\n"
        "命令中间神经元，模拟触碰退缩/前行决策。\n"
        "注意：该回路仍在开发中，尚不能产生正确行为。\n",
    ),
    "c302_TargetMuscle.py": (
        "目标肌肉测试配置",
        "配置目标肌肉的单元测试。\n"
        "仅包含少量神经元和肌肉，用于验证特定肌肉的响应。\n",
    ),
}

spec = []

for filename, (short_desc, long_desc) in configs.items():
    filepath = f"project/c302/{filename}"
    functions = []
    
    # range_incl helper exists in FW and TapWithdrawal
    if filename in ("c302_FW.py", "c302_TapWithdrawal.py"):
        functions.append({
            "name": "range_incl",
            "docstring": (
                "生成包含终止值的整数范围。\n\n"
                "等效于 ``range(start, end + 1)``。\n\n"
                ":param start: 起始值（含）\n"
                ":param end: 终止值（含）\n"
                ":return: range 对象\n"
            ),
        })
    
    # MultiSyns has no setup() function
    if filename == "c302_MultiSyns.py":
        # No functions to add docstrings to
        continue
    
    # Standard setup() docstring
    setup_doc = (
        f"{short_desc}的 setup 函数。\n\n"
        f"{long_desc}\n"
        ":param parameter_set: 参数层级（``A``/``B``/``C``/``C0``/``C1``/``C2``/``D``/``D1``/``W2D``）\n"
        ":param generate: 是否生成 NeuroML 文件\n"
        ":param duration: 仿真时长（毫秒）\n"
        ":param dt: 仿真时间步长（毫秒）\n"
        ":param target_directory: 输出目录\n"
        ":param data_reader: 数据读取器名称\n"
        ":param param_overrides: 生物参数覆盖字典\n"
        ":param config_param_overrides: 配置级参数覆盖字典\n"
        ":param verbose: 是否输出详细日志\n"
        ":return: ``(cells, cells_to_stimulate, params, muscles, nml_doc)`` 五元组\n"
    )
    
    functions.append({
        "name": "setup",
        "docstring": setup_doc,
    })
    
    spec.append({
        "file": filepath,
        "functions": functions,
    })

with open("scripts/add-docstring/specs/phase7.yaml", "w", encoding="utf-8") as f:
    yaml.dump(spec, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
print(f"Written scripts/add-docstring/specs/phase7.yaml ({len(spec)} files)")
