# =============================================================================
# 功能描述：
#   细胞构建器函数，从 factory.py 提取的 HH 导电细胞创建逻辑。
#   供 C/C0/D 族模型共用。
#
# 类与方法索引：
#   create_hh_cell                       (L25)  — 创建单室 HH 导电细胞（ca_boyle 通道）
#   create_c0_cell                       (L117) — 创建 C0 级 HH 导电细胞（ca_simple 通道）
#
# 更新日志：
#   2026-04-18  Copilot  计划4阶段二：从 factory.py 提取细胞构建器
#
# 当前维护者：Copilot
# =============================================================================
"""细胞构建器函数。"""
from neuroml import (
    BiophysicalProperties,
    Cell,
    ChannelDensity,
    InitMembPotential,
    IntracellularProperties,
    MembraneProperties,
    Morphology,
    Point3DWithDiam,
    Resistivity,
    Segment,
    SpecificCapacitance,
    Species,
    SpikeThresh,
)


def create_hh_cell(model, cell_id, is_muscle=True):
    """创建单室 HH 导电细胞（供 C/D 族共用）。

    :param model: 模型实例（含 bioparameters）
    :param cell_id: 细胞 ID 字符串
    :param is_muscle: True 使用肌肉参数前缀，False 使用神经元参数前缀
    :return: Cell 对象
    """
    cell = Cell(id=cell_id)
    morphology = Morphology()
    morphology.id = "morphology_" + cell.id
    cell.morphology = morphology

    diameter = model.get_bioparameter("cell_diameter").value
    prox = Point3DWithDiam(x="0", y="0", z="0", diameter=diameter)

    if is_muscle:
        # 肌肉有长度
        length = model.get_bioparameter("muscle_length").value
        dist = Point3DWithDiam(x="0", y=length, z="0", diameter=diameter)
    else:
        # 神经元为球形（prox == dist）
        dist = Point3DWithDiam(x="0", y="0", z="0", diameter=diameter)

    segment = Segment(id="0", name="soma", proximal=prox, distal=dist)
    morphology.segments.append(segment)

    # 生物物理属性
    cell.biophysical_properties = BiophysicalProperties(id="biophys_" + cell.id)
    mp = MembraneProperties()
    cell.biophysical_properties.membrane_properties = mp

    mp.init_memb_potentials.append(
        InitMembPotential(value=model.get_bioparameter("initial_memb_pot").value)
    )
    mp.specific_capacitances.append(
        SpecificCapacitance(
            value=model.get_bioparameter("specific_capacitance").value
        )
    )

    # 放电阈值
    prefix = "muscle" if is_muscle else "neuron"
    mp.spike_threshes.append(
        SpikeThresh(value=model.get_bioparameter(f"{prefix}_spike_thresh").value)
    )

    # 离子通道密度
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(f"{prefix}_leak_cond_density").value,
            id="Leak_all",
            ion_channel="Leak",
            erev=model.get_bioparameter("leak_erev").value,
            ion="non_specific",
        )
    )
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(f"{prefix}_k_slow_cond_density").value,
            id="k_slow_all",
            ion_channel="k_slow",
            erev=model.get_bioparameter("k_slow_erev").value,
            ion="k",
        )
    )
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(f"{prefix}_k_fast_cond_density").value,
            id="k_fast_all",
            ion_channel="k_fast",
            erev=model.get_bioparameter("k_fast_erev").value,
            ion="k",
        )
    )
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(
                f"{prefix}_ca_boyle_cond_density"
            ).value,
            id="ca_boyle_all",
            ion_channel="ca_boyle",
            erev=model.get_bioparameter("ca_boyle_erev").value,
            ion="ca",
        )
    )

    # 胞内属性
    ip = IntracellularProperties()
    cell.biophysical_properties.intracellular_properties = ip

    # resistivity 参数：D 族在 YAML 中定义，C 族写死
    resis_bp = model.get_bioparameter("resistivity")
    ip.resistivities.append(
        Resistivity(value=resis_bp.value if resis_bp else "0.1 kohm_cm")
    )

    # 钙离子物种
    species = Species(
        id="ca",
        ion="ca",
        concentration_model="CaPool",
        initial_concentration="0 mM",
        initial_ext_concentration="2E-6 mol_per_cm3",
    )
    ip.species.append(species)

    return cell


def create_c0_cell(model, cell_id, is_muscle=True):
    """创建 C0 级 HH 导电细胞（使用 ca_simple 通道和分离比膜电容）。"""
    cell = Cell(id=cell_id)
    morphology = Morphology()
    morphology.id = "morphology_" + cell.id
    cell.morphology = morphology

    diameter = model.get_bioparameter("cell_diameter").value
    prox = Point3DWithDiam(x="0", y="0", z="0", diameter=diameter)

    if is_muscle:
        length = model.get_bioparameter("muscle_length").value
        dist = Point3DWithDiam(x="0", y=length, z="0", diameter=diameter)
    else:
        dist = Point3DWithDiam(x="0", y="0", z="0", diameter=diameter)

    segment = Segment(id="0", name="soma", proximal=prox, distal=dist)
    morphology.segments.append(segment)

    cell.biophysical_properties = BiophysicalProperties(id="biophys_" + cell.id)
    mp = MembraneProperties()
    cell.biophysical_properties.membrane_properties = mp

    mp.init_memb_potentials.append(
        InitMembPotential(value=model.get_bioparameter("initial_memb_pot").value)
    )

    # C0 使用分离的 muscle/neuron specific_capacitance
    prefix = "muscle" if is_muscle else "neuron"
    mp.specific_capacitances.append(
        SpecificCapacitance(
            value=model.get_bioparameter(f"{prefix}_specific_capacitance").value
        )
    )
    mp.spike_threshes.append(
        SpikeThresh(value=model.get_bioparameter(f"{prefix}_spike_thresh").value)
    )

    # 漏泄通道
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(f"{prefix}_leak_cond_density").value,
            id="Leak_all",
            ion_channel="Leak",
            erev=model.get_bioparameter("leak_erev").value,
            ion="non_specific",
        )
    )
    # 慢钾通道
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(f"{prefix}_k_slow_cond_density").value,
            id="k_slow_all",
            ion_channel="k_slow",
            erev=model.get_bioparameter("k_slow_erev").value,
            ion="k",
        )
    )
    # C0 使用 ca_simple 通道（而非 ca_boyle）
    mp.channel_densities.append(
        ChannelDensity(
            cond_density=model.get_bioparameter(
                f"{prefix}_ca_simple_cond_density"
            ).value,
            id="ca_simple_all",
            ion_channel="ca_simple",
            erev=model.get_bioparameter("ca_simple_erev").value,
            ion="ca",
        )
    )

    ip = IntracellularProperties()
    cell.biophysical_properties.intracellular_properties = ip
    ip.resistivities.append(Resistivity(value="0.1 kohm_cm"))

    species = Species(
        id="ca",
        ion="ca",
        concentration_model="CaPool",
        initial_concentration="0 mM",
        initial_ext_concentration="2E-6 mol_per_cm3",
    )
    ip.species.append(species)

    return cell
