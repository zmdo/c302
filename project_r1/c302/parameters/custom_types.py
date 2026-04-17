# =============================================================================
# 功能描述：
#   自定义 NeuroML 组件类型（非标准 NeuroML，由自定义 XML 定义）。
#   从 factory.py 提取，供多个层级模型复用。
#
# 类与方法索引：
#   IafActivityCell                      (L26)  — IafCell 变体，增加 tau1 时间常数（对应 cell_B.xml 中的 iafActivityCell）
#     __init__                           (L29)  — __init__ 函数
#     export                             (L38)  — 将 iafActivityCell 写入 NeuroML XML
#   GradedSynapse2                       (L56)  — 自定义 GradedSynapse2（对应 custom_synapses.xml 中的 gradedSynapse2）
#     __init__                           (L59)  — __init__ 函数
#     export                             (L68)  — 将 gradedSynapse2 写入 NeuroML XML
#
# 更新日志：
#   2026-04-18  Copilot  计划4阶段二：从 factory.py 提取自定义组件类型
#
# 当前维护者：Copilot
# =============================================================================
"""自定义 NeuroML 组件类型。"""


class IafActivityCell:
    """IafCell 变体，增加 tau1 时间常数（对应 cell_B.xml 中的 iafActivityCell）。"""

    def __init__(self, id, C, thresh, reset, leak_conductance, leak_reversal, tau1):
        self.id = id
        self.C = C
        self.thresh = thresh
        self.reset = reset
        self.leak_conductance = leak_conductance
        self.leak_reversal = leak_reversal
        self.tau1 = tau1

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        """将 iafActivityCell 写入 NeuroML XML。"""
        outfile.write(
            "    " * level
            + '<iafCell type="iafActivityCell" id="%s" C="%s" thresh="%s" reset="%s"'
            ' leakConductance="%s" leakReversal="%s" tau1="%s"/>\n'
            % (
                self.id,
                self.C,
                self.thresh,
                self.reset,
                self.leak_conductance,
                self.leak_reversal,
                self.tau1,
            )
        )


class GradedSynapse2:
    """自定义 GradedSynapse2（对应 custom_synapses.xml 中的 gradedSynapse2）。"""

    def __init__(self, id, conductance, ar, ad, beta, vth, erev):
        self.id = id
        self.conductance = conductance
        self.ar = ar
        self.ad = ad
        self.beta = beta
        self.vth = vth
        self.erev = erev

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        """将 gradedSynapse2 写入 NeuroML XML。"""
        outfile.write(
            "    " * level
            + '<gradedSynapse2 id="%s" conductance="%s" ar="%s" ad="%s"'
            ' beta="%s" vth="%s" erev="%s"/>\n'
            % (
                self.id,
                self.conductance,
                self.ar,
                self.ad,
                self.beta,
                self.vth,
                self.erev,
            )
        )
