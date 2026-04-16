# =============================================================================
# 功能描述：
#   使用原代码批量生成参考输出。对原代码支持矩阵中的全部有效
#   (配置, 参数集) 组合调用 setup(generate=True)，将 .net.nml
#   和 LEMS_*.xml 保存到 project_r1/tests/reference_outputs/，
#   同时为每个组合生成统计摘要 JSON。
#
# 类与方法索引：
#   SUPPORT_MATRIX                   (L22)   — 原代码支持的配置×参数集矩阵
#   generate_reference               (L43)   — 为单个组合生成参考输出
#   collect_stats                    (L81)   — 从 nml_doc 收集统计摘要
#   main                             (L113)  — 脚本入口
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
"""按原代码支持矩阵批量生成参考输出。

使用方法::

    cd project/
    python ../scripts/generate_reference_outputs.py
"""
import importlib
import json
import os
import sys
import traceback
from pathlib import Path

# 原代码 runAndPlot.py -all 使用的标准矩阵：
# 9 个参数层级 × 8 个标准配置 = 72 组合
STANDARD_LEVELS = ["A", "B", "C0", "C", "C1", "C2", "D", "D1", "W2D"]
STANDARD_CONFIGS = ["IClamp", "Syns", "Pharyngeal", "Social", "Oscillator", "Muscles", "Full", "FW"]

# 额外的已知可工作组合（不在标准矩阵中）
EXTRA_CASES = [
    ("OscillatorM", "C0"),
    ("RIA", "D1"),
    ("TargetMuscle", "C0"),
    ("TapWithdrawal", "C2"),
    ("MuscleTest", "C"),
    ("MusclesSine", "C"),
    ("IClampMuscle", "C"),
    ("MultiSyns", "C"),
]

# 参考输出根目录（相对于本脚本运行时的 cwd）
OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "project_r1" / "tests" / "reference_outputs"


def generate_reference(config: str, level: str, output_dir: Path) -> dict | None:
    """为单个 (配置, 参数集) 组合生成参考输出。

    :param config: 配置名称（如 "IClamp"）
    :param level: 参数层级（如 "A"）
    :param output_dir: 输出目录
    :return: 统计摘要字典，或 None（生成失败时）
    """
    combo_name = f"{level}_{config}"
    target = str(output_dir / combo_name)

    # 确保输出目录存在
    os.makedirs(target, exist_ok=True)

    try:
        # 动态导入配置模块
        config_module = importlib.import_module(f"c302.c302_{config}")

        # 调用 setup() 生成 NeuroML 文件
        cells, cells_to_stimulate, params, muscles, nml_doc = config_module.setup(
            level,
            generate=True,
            duration=500,
            dt=0.05,
            target_directory=target,
            verbose=False,
        )

        # 收集统计摘要
        stats = collect_stats(nml_doc, cells, cells_to_stimulate, muscles, params)
        stats["config"] = config
        stats["level"] = level

        # 保存统计摘要为 JSON
        stats_path = output_dir / combo_name / "stats.json"
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f"  OK: {combo_name} — {stats['population_count']} populations, {stats['connection_count']} connections")
        return stats

    except Exception:
        print(f"  FAIL: {combo_name}")
        traceback.print_exc()
        return None


def collect_stats(nml_doc, cells, cells_to_stimulate, muscles, params) -> dict:
    """从生成的 NeuroML 文档收集统计摘要。

    :param nml_doc: NeuroML 文档对象
    :param cells: 细胞名称列表
    :param cells_to_stimulate: 被刺激的细胞列表
    :param muscles: 肌肉名称列表
    :param params: 参数化模型实例
    :return: 统计摘要字典
    """
    # 统计种群数量
    population_count = len(nml_doc.networks[0].populations) if nml_doc.networks else 0

    # 统计连接数量（化学突触 + 电突触）
    connection_count = 0
    if nml_doc.networks:
        net = nml_doc.networks[0]
        # 化学突触 Projections
        for proj in net.projections:
            connection_count += len(proj.connections) + len(proj.connection_wds)
        # 电突触 ElectricalProjections
        for ep in net.electrical_projections:
            connection_count += len(ep.electrical_connections) + len(ep.electrical_connection_instances) + len(ep.electrical_connection_instance_ws)

    # 统计刺激数量
    stimulus_count = 0
    if nml_doc.networks:
        net = nml_doc.networks[0]
        stimulus_count = len(net.input_lists)

    # 收集 BioParameter 名称-值对
    bioparameters = {}
    if hasattr(params, "bioparameters"):
        for bp in params.bioparameters:
            bioparameters[bp.name] = bp.value

    return {
        "population_count": population_count,
        "connection_count": connection_count,
        "stimulus_count": stimulus_count,
        "cell_count": len(cells) if cells else 0,
        "stimulated_cell_count": len(cells_to_stimulate) if cells_to_stimulate else 0,
        "muscle_count": len(muscles) if muscles else 0,
        "bioparameter_count": len(bioparameters),
        "bioparameters": bioparameters,
    }


def main():
    """脚本入口：遍历支持矩阵并生成全部参考输出。"""
    print(f"参考输出目录: {OUTPUT_ROOT}")
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    results = {"success": [], "failed": []}

    # 标准矩阵：9 levels × 8 configs
    print(f"\n=== 标准矩阵: {len(STANDARD_LEVELS)} levels × {len(STANDARD_CONFIGS)} configs ===")
    for level in STANDARD_LEVELS:
        for config in STANDARD_CONFIGS:
            stats = generate_reference(config, level, OUTPUT_ROOT)
            if stats is not None:
                results["success"].append(f"{level}_{config}")
            else:
                results["failed"].append(f"{level}_{config}")

    # 额外组合
    print(f"\n=== 额外组合: {len(EXTRA_CASES)} ===")
    for config, level in EXTRA_CASES:
        stats = generate_reference(config, level, OUTPUT_ROOT)
        if stats is not None:
            results["success"].append(f"{level}_{config}")
        else:
            results["failed"].append(f"{level}_{config}")

    # 保存汇总结果
    summary_path = OUTPUT_ROOT / "generation_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n=== 完成 ===")
    print(f"成功: {len(results['success'])}")
    print(f"失败: {len(results['failed'])}")
    if results["failed"]:
        print(f"失败组合: {results['failed']}")


if __name__ == "__main__":
    main()
