"""为阶段七的 16 个配置脚本添加 SP-CODE-2026-001 文件头。"""
import re, pathlib

BASE = pathlib.Path("project/c302")

# (文件名, 功能描述, [(函数名, 简述), ...])
# line numbers 由 gen_index 后续修正
CONFIGS = [
    ("c302_Full.py",
     "全连接组（302 神经元）配置脚本。\n#   随机选取部分神经元施加脉冲刺激，用于整体网络行为验证。",
     [("setup", "配置全连接组网络（302 神经元）")]),

    ("c302_FW.py",
     "正向运动（Forward locomotion）配置脚本。\n#   选取 DB/VB 类运动神经元及中间神经元，构建正向运动回路。",
     [("range_incl", "生成包含终止值的整数范围"),
      ("setup", "配置正向运动回路网络")]),

    ("c302_IClamp.py",
     "电流钳（IClamp）单细胞刺激配置脚本。\n#   对 ADAL 神经元施加阶跃电流，用于验证单个神经元响应。",
     [("setup", "配置电流钳单细胞刺激")]),

    ("c302_IClampMuscle.py",
     "肌肉电流钳刺激配置脚本。\n#   对 MDL08 肌肉细胞施加阶跃电流，验证肌肉模型响应。",
     [("setup", "配置肌肉电流钳刺激")]),

    ("c302_MultiSyns.py",
     "多突触连接测试配置脚本。\n#   选取少量神经元验证突触连接生成，仅含 __main__ 执行块，无函数定义。",
     []),  # 无函数

    ("c302_MuscleTest.py",
     "肌肉测试配置脚本。\n#   选取运动神经元和肌肉细胞，施加指定电流脉冲，验证肌肉驱动。",
     [("setup", "配置肌肉测试回路")]),

    ("c302_Muscles.py",
     "含肌肉的全连接组配置脚本。\n#   包含 302 神经元和全部 96 块体壁肌肉，验证神经-肌肉连接。",
     [("setup", "配置含肌肉的全连接组网络")]),

    ("c302_MusclesSine.py",
     "正弦波肌肉刺激配置脚本。\n#   向体壁肌肉施加正弦波电流，模拟节律性收缩。",
     [("setup", "配置正弦波肌肉刺激网络")]),

    ("c302_Oscillator.py",
     "神经振荡器配置脚本。\n#   选取 DB/VB 类运动神经元构建振荡回路，验证节律性活动。",
     [("setup", "配置神经振荡器回路")]),

    ("c302_OscillatorM.py",
     "含肌肉的振荡器配置脚本。\n#   在神经振荡器基础上增加体壁肌肉，验证肌肉驱动的节律性运动。",
     [("setup", "配置含肌肉的振荡器回路")]),

    ("c302_Pharyngeal.py",
     "咽部神经系统配置脚本。\n#   选取 I1–I6、M1–M5、MI、MC、NSM 等咽部神经元，构建咽泵回路。",
     [("setup", "配置咽部神经系统网络")]),

    ("c302_RIA.py",
     "RIA 中间神经元配置脚本。\n#   选取 RIAL/RIAR 及连接神经元，验证 RIA 中间层信号处理。",
     [("setup", "配置 RIA 中间神经元回路")]),

    ("c302_Social.py",
     "社交决策回路配置脚本。\n#   选取 RMGR、ASHR、ASKR、AWBR、IL2R 等感觉/中间神经元，\n#   模拟线虫群聚/独居行为的决策过程。",
     [("setup", "配置社交决策回路")]),

    ("c302_Syns.py",
     "突触连接测试配置脚本。\n#   选取 URYDL、SMDDR、IL2VL 等少量神经元，测试突触生成。",
     [("setup", "配置突触连接测试回路")]),

    ("c302_TapWithdrawal.py",
     "触碰回缩反射配置脚本（开发中）。\n#   构建触觉感觉→中间→运动神经元回路，模拟触碰回缩行为。",
     [("range_incl", "生成包含终止值的整数范围"),
      ("setup", "配置触碰回缩反射回路")]),

    ("c302_TargetMuscle.py",
     "目标肌肉配置脚本。\n#   选取少量运动神经元和肌肉细胞，验证目标肌肉激活。",
     [("setup", "配置目标肌肉回路")]),
]


def find_functions(text):
    """返回 {函数名: 行号} 映射。"""
    result = {}
    for i, line in enumerate(text.splitlines(), 1):
        m = re.match(r'^def (\w+)\(', line)
        if m:
            result[m.group(1)] = i
    return result


def build_header(desc, funcs_spec, func_lines):
    """构建 SP-CODE 文件头字符串。"""
    lines = [
        "# =============================================================================",
        "# 功能描述：",
        "#   " + desc.split('\n')[0],  # first line
    ]
    # 多行描述
    for extra in desc.split('\n')[1:]:
        lines.append(extra)
    lines.append("#")

    lines.append("# 类与方法索引：")
    if not funcs_spec:
        lines.append("#   （脚本无函数定义，仅含 __main__ 执行块）")
    else:
        for fname, fdesc in funcs_spec:
            lnum = func_lines.get(fname, "?")
            padded = f"{fname:<40s}"
            lines.append(f"#   {padded} (L{lnum})   — {fdesc}")
    lines.append("#")

    lines.append("# 更新日志：")
    lines.append("#   2026-04-16  Copilot  添加中文 docstring 和行内注释")
    lines.append("#")
    lines.append("# 当前维护者：Copilot")
    lines.append("# =============================================================================")
    return "\n".join(lines) + "\n"


def add_header(filepath, desc, funcs_spec):
    text = filepath.read_text(encoding="utf-8")
    original_lines = text.splitlines()

    # 先计算函数行号（header 还没插入，后续 gen_index 会修正）
    func_lines = find_functions(text)

    # header 行数
    header_text = build_header(desc, funcs_spec, {})
    header_nlines = len(header_text.splitlines())

    # 用偏移后的行号重建
    adjusted = {fn: ln + header_nlines for fn, ln in func_lines.items()}
    header_text = build_header(desc, funcs_spec, adjusted)

    # 特殊处理 c302_Social.py：删除开头的英文注释块（到第一个 import 之前）
    if filepath.name == "c302_Social.py":
        # 找到第一个非注释、非空行
        cut = 0
        for i, line in enumerate(original_lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                cut = i
                break
        text = "\n".join(original_lines[cut:]) + "\n"

    filepath.write_text(header_text + text, encoding="utf-8")
    return header_nlines


count = 0
for fname, desc, funcs in CONFIGS:
    fp = BASE / fname
    if not fp.exists():
        print(f"  [SKIP] {fname} 不存在")
        continue
    # 检查是否已有文件头
    first_line = fp.read_text(encoding="utf-8").splitlines()[0]
    if first_line.startswith("# ===="):
        print(f"  [SKIP] {fname} 已有文件头")
        continue
    nlines = add_header(fp, desc, funcs)
    count += 1
    print(f"  [ADD]  {fname} (+{nlines} 行文件头)")

print(f"\n共添加 {count} 个文件头。")
