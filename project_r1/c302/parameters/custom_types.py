# =============================================================================
# 功能描述：
#   自定义 NeuroML 组件类型（非标准 NeuroML，由自定义 XML 定义）。
#   从 factory.py 提取，供多个层级模型复用。
#
# 类与方法索引：
#   IafActivityCell                      (L26)   — IafCell 变体，增加 tau1 时间常数（对应 cell_B.xml 中的 iafActivityCell）
#     __init__                           (L29)   — __init__ 函数
#     export                             (L38)   — 将 iafActivityCell 写入 NeuroML XML
#   GradedSynapse2                       (L56)   — 自定义 GradedSynapse2（对应 custom_synapses.xml 中的 gradedSynapse2）
#     __init__                           (L59)   — __init__ 函数
#     export                             (L68)   — 将 gradedSynapse2 写入 NeuroML XML
#   CellW2D                              (L86)   — W2D 偏置-增益细胞（对应 cell_W2D.xml 中的 cellW2D）
#     __init__                           (L89)   — __init__ 函数
#   OutputSynapse                        (L93)   — W2D 输出突触（对应 custom_synapses.xml 中的 outputSynapse）
#     __init__                           (L96)   — __init__ 函数
#   DelayedGapJunction                   (L105)  — 延迟调制缝隙连接（C2，sigmoid 时间调制）
#     __init__                           (L108)  — __init__ 函数
#     export                             (L115)  — export 函数
#   ProprioGapJunction                   (L123)  — 本体感觉调制缝隙连接（C2）
#     __init__                           (L126)  — __init__ 函数
#     export                             (L136)  — export 函数
#   ProprioGapJunction2                  (L151)  — 增强型本体感觉缝隙连接（C2，支持门控参数）
#     __init__                           (L154)  — __init__ 函数
#     export                             (L180)  — export 函数
#   NeuronMuscle                         (L200)  — 肌肉本体感觉反馈类突触（C2）
#     __init__                           (L203)  — __init__ 函数
#     export                             (L212)  — export 函数
#   MuscleConcentrationModel2            (L228)  — 扩展肌肉钙浓度模型（C2，含 sigmoid 浓度阈值调制）
#     __init__                           (L231)  — __init__ 函数
#     export                             (L259)  — export 函数
#   DelayedGapJunction                   (L285)  — 延迟调制缝隙连接（C2，sigmoid 时间调制）
#     __init__                           (L288)  — __init__ 函数
#     export                             (L295)  — export 函数
#   ProprioGapJunction                   (L303)  — 本体感觉调制缝隙连接（C2）
#     __init__                           (L306)  — __init__ 函数
#     export                             (L316)  — export 函数
#   ProprioGapJunction2                  (L331)  — 增强型本体感觉缝隙连接（C2，支持门控参数）
#     __init__                           (L334)  — __init__ 函数
#     export                             (L360)  — export 函数
#   NeuronMuscle                         (L380)  — 肌肉本体感觉反馈类突触（C2）
#     __init__                           (L383)  — __init__ 函数
#     export                             (L392)  — export 函数
#   MuscleConcentrationModel2            (L408)  — 扩展肌肉钙浓度模型（C2，含 sigmoid 浓度阈值调制）
#     __init__                           (L411)  — __init__ 函数
#     export                             (L439)  — export 函数
#
# 更新日志：
#   2026-04-18  Copilot  计划4阶段二：从 factory.py 提取自定义组件类型
#
# 当前维护者：Copilot
# =============================================================================
"""自定义 NeuroML 组件类型。"""

from c302.parameters.model import NonNeuroMLCustomType


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


class CellW2D(NonNeuroMLCustomType):
    """W2D 偏置-增益细胞（对应 cell_W2D.xml 中的 cellW2D）。"""

    def __init__(self, id):
        self.id = id


class OutputSynapse(NonNeuroMLCustomType):
    """W2D 输出突触（对应 custom_synapses.xml 中的 outputSynapse）。"""

    def __init__(self, id):
        self.id = id


# ---------------------------------------------------------------------------
# C2 自定义组件
# ---------------------------------------------------------------------------


class DelayedGapJunction:
    """延迟调制缝隙连接（C2，sigmoid 时间调制）。"""

    def __init__(self, id, conductance, sigma, mu, weight=1):
        self.id = id
        self.weight = weight
        self.conductance = conductance
        self.sigma = sigma
        self.mu = mu

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        outfile.write(
            "    " * level
            + '<delayedGapJunction id="%s" weight="%s" conductance="%s" sigma="%s" mu="%s" />\n'
            % (self.id, self.weight, self.conductance, self.sigma, self.mu)
        )


class ProprioGapJunction:
    """本体感觉调制缝隙连接（C2）。"""

    def __init__(
        self, id, conductance, p_conductance, mu, weight=1, sigma="0.3 per_mV"
    ):
        self.id = id
        self.weight = weight
        self.conductance = conductance
        self.p_conductance = p_conductance
        self.sigma = sigma
        self.mu = mu

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        outfile.write(
            "    " * level
            + '<proprioGapJunction id="%s" weight="%s" conductance="%s" p_conductance="%s" sigma="%s" mu="%s" />\n'
            % (
                self.id,
                self.weight,
                self.conductance,
                self.p_conductance,
                self.sigma,
                self.mu,
            )
        )


class ProprioGapJunction2:
    """增强型本体感觉缝隙连接（C2，支持门控参数）。"""

    def __init__(
        self,
        id,
        conductance,
        p_conductance,
        mu,
        ar=None,
        ad=None,
        beta=None,
        vth=None,
        erev=None,
        weight=1,
        sigma="0.3 per_mV",
    ):
        self.id = id
        self.weight = weight
        self.conductance = conductance
        self.p_conductance = p_conductance
        self.sigma = sigma
        self.mu = mu
        self.ar = ar
        self.ad = ad
        self.beta = beta
        self.vth = vth
        self.erev = erev

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        outfile.write(
            "    " * level
            + '<proprioGapJunction2 id="%s" weight="%s" ar="%s" ad="%s" beta="%s" vth="%s" erev="%s" conductance="%s" p_conductance="%s" sigma="%s" mu="%s" />\n'
            % (
                self.id,
                self.weight,
                self.ar,
                self.ad,
                self.beta,
                self.vth,
                self.erev,
                self.conductance,
                self.p_conductance,
                self.sigma,
                self.mu,
            )
        )


class NeuronMuscle:
    """肌肉本体感觉反馈类突触（C2）。"""

    def __init__(self, id, conductance, ar, ad, beta, cath, erev):
        self.id = id
        self.conductance = conductance
        self.ar = ar
        self.ad = ad
        self.beta = beta
        self.cath = cath
        self.erev = erev

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        outfile.write(
            "    " * level
            + '<proprio id="%s" conductance="%s" ar="%s" ad="%s" beta="%s" cath="%s" erev="%s"/>\n'
            % (
                self.id,
                self.conductance,
                self.ar,
                self.ad,
                self.beta,
                self.cath,
                self.erev,
            )
        )


class MuscleConcentrationModel2:
    """扩展肌肉钙浓度模型（C2，含 sigmoid 浓度阈值调制）。"""

    def __init__(
        self,
        id,
        ion,
        resting_conc,
        decay_constant,
        rho,
        xRho,
        xrest,
        iCaSigmoidMid="",
        iCaSigmoidSlope="",
        xSigmoidMid="",
        xSigmoidSlope="",
        xDecay="",
    ):
        self.id = id
        self.ion = ion
        self.resting_conc = resting_conc
        self.decay_constant = decay_constant
        self.rho = rho
        self.xRho = xRho
        self.iCaSigmoidMid = iCaSigmoidMid
        self.iCaSigmoidSlope = iCaSigmoidSlope
        self.xSigmoidMid = xSigmoidMid
        self.xSigmoidSlope = xSigmoidSlope
        self.xDecay = xDecay
        self.xrest = xrest

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        outfile.write(
            "    " * level
            + '<muscleConcentrationModel2 id="%s" ion="%s" restingConc="%s" decayConstant="%s" rho="%s" xRho="%s" iCaSigmoidMid="%s" iCaSigmoidSlope="%s" xSigmoidMid="%s" xSigmoidSlope="%s" xDecay="%s" xrest="%s" />\n'
            % (
                self.id,
                self.ion,
                self.resting_conc,
                self.decay_constant,
                self.rho,
                self.xRho,
                self.iCaSigmoidMid,
                self.iCaSigmoidSlope,
                self.xSigmoidMid,
                self.xSigmoidSlope,
                self.xDecay,
                self.xrest,
            )
        )


# ---------------------------------------------------------------------------
# C2 自定义组件
# ---------------------------------------------------------------------------


class DelayedGapJunction:
    """延迟调制缝隙连接（C2，sigmoid 时间调制）。"""

    def __init__(self, id, conductance, sigma, mu, weight=1):
        self.id = id
        self.weight = weight
        self.conductance = conductance
        self.sigma = sigma
        self.mu = mu

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        outfile.write(
            "    " * level
            + '<delayedGapJunction id="%s" weight="%s" conductance="%s" sigma="%s" mu="%s" />\n'
            % (self.id, self.weight, self.conductance, self.sigma, self.mu)
        )


class ProprioGapJunction:
    """本体感觉调制缝隙连接（C2）。"""

    def __init__(
        self, id, conductance, p_conductance, mu, weight=1, sigma="0.3 per_mV"
    ):
        self.id = id
        self.weight = weight
        self.conductance = conductance
        self.p_conductance = p_conductance
        self.sigma = sigma
        self.mu = mu

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        outfile.write(
            "    " * level
            + '<proprioGapJunction id="%s" weight="%s" conductance="%s" p_conductance="%s" sigma="%s" mu="%s" />\n'
            % (
                self.id,
                self.weight,
                self.conductance,
                self.p_conductance,
                self.sigma,
                self.mu,
            )
        )


class ProprioGapJunction2:
    """增强型本体感觉缝隙连接（C2，支持门控参数）。"""

    def __init__(
        self,
        id,
        conductance,
        p_conductance,
        mu,
        ar=None,
        ad=None,
        beta=None,
        vth=None,
        erev=None,
        weight=1,
        sigma="0.3 per_mV",
    ):
        self.id = id
        self.weight = weight
        self.conductance = conductance
        self.p_conductance = p_conductance
        self.sigma = sigma
        self.mu = mu
        self.ar = ar
        self.ad = ad
        self.beta = beta
        self.vth = vth
        self.erev = erev

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        outfile.write(
            "    " * level
            + '<proprioGapJunction2 id="%s" weight="%s" ar="%s" ad="%s" beta="%s" vth="%s" erev="%s" conductance="%s" p_conductance="%s" sigma="%s" mu="%s" />\n'
            % (
                self.id,
                self.weight,
                self.ar,
                self.ad,
                self.beta,
                self.vth,
                self.erev,
                self.conductance,
                self.p_conductance,
                self.sigma,
                self.mu,
            )
        )


class NeuronMuscle:
    """肌肉本体感觉反馈类突触（C2）。"""

    def __init__(self, id, conductance, ar, ad, beta, cath, erev):
        self.id = id
        self.conductance = conductance
        self.ar = ar
        self.ad = ad
        self.beta = beta
        self.cath = cath
        self.erev = erev

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        outfile.write(
            "    " * level
            + '<proprio id="%s" conductance="%s" ar="%s" ad="%s" beta="%s" cath="%s" erev="%s"/>\n'
            % (
                self.id,
                self.conductance,
                self.ar,
                self.ad,
                self.beta,
                self.cath,
                self.erev,
            )
        )


class MuscleConcentrationModel2:
    """扩展肌肉钙浓度模型（C2，含 sigmoid 浓度阈值调制）。"""

    def __init__(
        self,
        id,
        ion,
        resting_conc,
        decay_constant,
        rho,
        xRho,
        xrest,
        iCaSigmoidMid="",
        iCaSigmoidSlope="",
        xSigmoidMid="",
        xSigmoidSlope="",
        xDecay="",
    ):
        self.id = id
        self.ion = ion
        self.resting_conc = resting_conc
        self.decay_constant = decay_constant
        self.rho = rho
        self.xRho = xRho
        self.iCaSigmoidMid = iCaSigmoidMid
        self.iCaSigmoidSlope = iCaSigmoidSlope
        self.xSigmoidMid = xSigmoidMid
        self.xSigmoidSlope = xSigmoidSlope
        self.xDecay = xDecay
        self.xrest = xrest

    def export(self, outfile, level, namespace, name_, pretty_print=True, **kwargs_):
        outfile.write(
            "    " * level
            + '<muscleConcentrationModel2 id="%s" ion="%s" restingConc="%s" decayConstant="%s" rho="%s" xRho="%s" iCaSigmoidMid="%s" iCaSigmoidSlope="%s" xSigmoidMid="%s" xSigmoidSlope="%s" xDecay="%s" xrest="%s" />\n'
            % (
                self.id,
                self.ion,
                self.resting_conc,
                self.decay_constant,
                self.rho,
                self.xRho,
                self.iCaSigmoidMid,
                self.iCaSigmoidSlope,
                self.xSigmoidMid,
                self.xSigmoidSlope,
                self.xDecay,
                self.xrest,
            )
        )
