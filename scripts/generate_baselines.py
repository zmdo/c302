# =============================================================================
# 功能描述：
#   用原始 c302 代码批量生成参考基线数据。遍历所有层级与配置组合，
#   调用原始 setup(generate=True) 生成 NeuroML 文档，提取种群/连接/
#   刺激/参数/细胞/突触计数，写入 JSON 文件供等价性测试使用。
#
# 函数索引：
#   extract_baseline                     (L43)   — 从 NeuroML 文档提取基线计数数据
#   main                                 (L105)  — 遍历所有组合，生成基线 JSON
#
# 更新日志：
#   2026-04-17  Copilot  计划4阶段一：新建
#
# 当前维护者：Copilot
# =============================================================================
"""用原始 c302 代码批量生成参考基线数据。"""
import importlib
import json
import os
import sys
import tempfile
import traceback

# 将原始代码路径加入 sys.path（project/ 目录）
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.join(os.path.dirname(_SCRIPT_DIR), "project")
sys.path.insert(0, _PROJECT_DIR)

import c302  # noqa: E402 — 必须在 sys.path 修改后导入

# 全部 10 个层级
LEVELS = ["A", "B", "BC1", "C", "C0", "C1", "C2", "D", "D1", "W2D"]

# 8 个核心配置
CONFIGS = [
    "IClamp", "Syns", "Social", "Pharyngeal",
    "Full", "Muscles", "Oscillator", "FW",
]

# 基线输出目录
OUTPUT_DIR = os.path.join(
    os.path.dirname(_SCRIPT_DIR),
    "project_r1", "tests", "fixtures", "baselines",
)


def extract_baseline(nml_doc, params, config, level):
    """从生成的 NeuroML 文档提取基线计数数据。

    :param nml_doc: NeuroMLDocument 对象
    :param params: 参数化模型实例
    :param config: 配置名称
    :param level: 参数层级
    :return: 基线数据字典
    """
    net = nml_doc.networks[0]

    # 种群名称列表
    pop_names = [p.id for p in net.populations]

    # 连接计数：化学 / 电 / 连续
    chem = sum(
        len(p.connections) + len(p.connection_wds)
        for p in net.projections
    )
    elec = sum(
        len(p.electrical_connections)
        + len(p.electrical_connection_instances)
        + len(getattr(p, "electrical_connection_instance_ws", []))
        for p in net.electrical_projections
    )
    cont = sum(
        len(getattr(p, "continuous_connections", []))
        + len(getattr(p, "continuous_connection_instances", []))
        + len(getattr(p, "continuous_connection_instance_ws", []))
        for p in getattr(net, "continuous_projections", [])
    )

    # 刺激计数
    stimuli = len(net.input_lists)
    stim_count = sum(len(il.input) for il in net.input_lists)

    # BioParameter 计数及值
    bp_count = len(params.bioparameters)
    bp_values = {bp.name: bp.value for bp in params.bioparameters}

    # 细胞模型计数
    iaf = len(nml_doc.iaf_cells)
    hh = len(nml_doc.cells)

    # 突触模型计数
    exp_two = len(nml_doc.exp_two_synapses)
    gap = len(nml_doc.gap_junctions)
    graded = len(nml_doc.graded_synapses)
    graded2 = len(getattr(nml_doc, "graded_synapses2", []))

    return {
        "config": config,
        "level": level,
        "generated_by": "original",
        "populations": {
            "count": len(pop_names),
            "names": sorted(pop_names),
        },
        "connections": {
            "chemical": chem,
            "electrical": elec,
            "continuous": cont,
            "total": chem + elec + cont,
        },
        "stimuli": {
            "input_lists": stimuli,
            "total_inputs": stim_count,
        },
        "bioparameters": {
            "count": bp_count,
            "values": bp_values,
        },
        "cell_models": {
            "iaf_cells": iaf,
            "hh_cells": hh,
        },
        "synapse_models": {
            "exp_two_synapses": exp_two,
            "gap_junctions": gap,
            "graded_synapses": graded,
            "graded_synapses2": graded2,
        },
    }


def main():
    """遍历所有层级×配置组合，生成基线 JSON 文件。"""
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    success = 0
    skipped = 0
    failed = 0
    results = []

    for level in LEVELS:
        for config in CONFIGS:
            combo = f"{config}_{level}"
            print(f"\n{'='*60}")
            print(f"  生成基线: {combo}")
            print(f"{'='*60}")

            try:
                # 动态导入配置脚本
                config_module = f"c302.c302_{config}"
                setup_fn = importlib.import_module(config_module).setup

                # 在临时目录中生成
                with tempfile.TemporaryDirectory() as tmpdir:
                    # D/D1 层级需要 cells/ 子目录存放 per-neuron 文件
                    os.makedirs(os.path.join(tmpdir, "cells"), exist_ok=True)

                    # FW 配置默认使用 FW_DATA_READER，其他使用默认
                    cells, cells_total, params, muscles, nml_doc = setup_fn(
                        level,
                        generate=True,
                        target_directory=tmpdir,
                        verbose=False,
                    )

                    if nml_doc is None:
                        print(f"  [跳过] {combo}: nml_doc 为 None")
                        skipped += 1
                        results.append((combo, "SKIPPED", "nml_doc is None"))
                        continue

                    # 提取基线数据
                    baseline = extract_baseline(nml_doc, params, config, level)

                    # 写入 JSON
                    out_path = os.path.join(OUTPUT_DIR, f"{combo}.json")
                    with open(out_path, "w", encoding="utf-8") as f:
                        json.dump(baseline, f, indent=2, ensure_ascii=False)

                    pop_count = baseline["populations"]["count"]
                    conn_total = baseline["connections"]["total"]
                    stim_total = baseline["stimuli"]["total_inputs"]
                    print(f"  [成功] {combo}: {pop_count} 种群, "
                          f"{conn_total} 连接, {stim_total} 刺激")
                    success += 1
                    results.append((combo, "OK", ""))

            except Exception as e:
                print(f"  [失败] {combo}: {e}")
                traceback.print_exc()
                failed += 1
                results.append((combo, "FAILED", str(e)))

    # 汇总报告
    print(f"\n{'='*60}")
    print(f"  基线生成汇总")
    print(f"{'='*60}")
    print(f"  总计: {len(LEVELS) * len(CONFIGS)} 种组合")
    print(f"  成功: {success}")
    print(f"  跳过: {skipped}")
    print(f"  失败: {failed}")
    print()

    # 按状态分组输出
    for status in ("FAILED", "SKIPPED"):
        entries = [(c, r) for c, s, r in results if s == status]
        if entries:
            print(f"  {status}:")
            for combo, reason in entries:
                print(f"    - {combo}: {reason}")

    # 写入摘要文件
    summary_path = os.path.join(OUTPUT_DIR, "_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "total": len(LEVELS) * len(CONFIGS),
            "success": success,
            "skipped": skipped,
            "failed": failed,
            "details": [
                {"combo": c, "status": s, "reason": r}
                for c, s, r in results
            ],
        }, f, indent=2, ensure_ascii=False)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
