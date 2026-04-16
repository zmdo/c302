# =============================================================================
# 功能描述：
#   多突触连接测试配置脚本。
#   选取少量神经元验证突触连接生成，仅含 __main__ 执行块，无函数定义。
#
# 类与方法索引：
#   （脚本无函数定义，仅含 __main__ 执行块）
#
# 更新日志：
#   2026-04-16  Copilot  计划2 阶段八收尾：补记汇总校验与最终勘误完成
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================
from c302 import generate, add_new_input, print_

import neuroml.writers as writers

import importlib
import sys


if __name__ == "__main__":
    parameter_set = sys.argv[1] if len(sys.argv) == 2 else "A"

    ParameterisedModel = getattr(
        importlib.import_module("c302.parameters_%s" % parameter_set),
        "ParameterisedModel",
    )
    params = ParameterisedModel()

    # 选取具有多种突触连接类型的 6 个神经元
    cells = ["URYDL", "SMDDR", "ADAL", "RIML", "IL2VL", "RIPL"]
    cells_to_stimulate = []

    reference = "c302_%s_MultiSyns" % parameter_set

    target_directory = "examples"

    nml_doc = generate(
        reference,
        params,
        cells=cells,
        cells_to_stimulate=cells_to_stimulate,
        duration=1000,
        dt=0.1,
        target_directory=target_directory,
        verbose=True,
    )

    # 分时段向 3 个神经元施加阶跃电流，间隔 300ms
    stim_amplitude = "0.35nA"
    add_new_input(nml_doc, "URYDL", "100ms", "200ms", stim_amplitude, params)
    add_new_input(nml_doc, "ADAL", "400ms", "200ms", stim_amplitude, params)
    add_new_input(nml_doc, "IL2VL", "700ms", "200ms", stim_amplitude, params)

    nml_file = target_directory + "/" + reference + ".net.nml"
    writers.NeuroMLWriter.write(
        nml_doc, nml_file
    )  # 覆盖前面生成的网络文件...

    print_("(Re)written network file to: " + nml_file)
