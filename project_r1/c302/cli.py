# =============================================================================
# 功能描述：
#   c302 命令行入口。提供 argparse 风格的参数解析，替代原始代码中
#   基于 sys.argv 字符串匹配的 if/elif 链。
#
# 类与方法索引：
#   build_parser                         (L28)   — 构建命令行参数解析器
#   _get_version                         (L123)  — 获取包版本号
#   process_args                         (L135)  — 解析命令行参数
#   main                                 (L154)  — CLI 入口函数
#
# 更新日志：
#   2026-04-17  Copilot  计划3阶段六：新建
#
# 当前维护者：Copilot
# =============================================================================
"""c302 命令行入口。"""
import argparse
import logging
import sys

from c302.configs import list_configs
from c302.simulation.runner import SIMULATORS, run_c302

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。

    :return: 配置好的 ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        prog="c302",
        description="C. elegans 302 neuron NeuroML 2 network generation and simulation",
    )

    # 必选参数
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="配置名称（如 IClamp, Full, Oscillator）",
    )
    parser.add_argument(
        "-p", "--params",
        required=True,
        help="参数层级（A/B/C/C0/C1/C2/D/D1/W2D）",
    )

    # 仿真参数
    parser.add_argument(
        "-d", "--duration",
        type=float,
        default=500.0,
        help="仿真时长（毫秒，默认 500）",
    )
    parser.add_argument(
        "--dt",
        type=float,
        default=0.05,
        help="仿真步长（毫秒，默认 0.05）",
    )
    parser.add_argument(
        "-s", "--simulator",
        choices=SIMULATORS,
        default="jNeuroML",
        help="仿真后端（默认 jNeuroML）",
    )

    # 输出控制
    parser.add_argument(
        "-o", "--output-dir",
        default="examples",
        help="输出目录（默认 examples）",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="保存绘图图片",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="不显示绘图窗口",
    )
    parser.add_argument(
        "--plot-connectivity",
        action="store_true",
        help="生成连接矩阵图",
    )

    # 数据读取器
    parser.add_argument(
        "--data-reader",
        default="cect.readers.SpreadsheetDataReader",
        help="数据读取器模块路径",
    )

    # 调试选项
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="输出详细日志",
    )

    # 版本信息
    parser.add_argument(
        "--version",
        action="version",
        version=_get_version(),
    )

    # 列出可用配置
    parser.add_argument(
        "--list-configs",
        action="store_true",
        help="列出所有可用的配置名称并退出",
    )

    return parser


def _get_version() -> str:
    """获取包版本号。

    :return: 版本号字符串
    """
    try:
        from c302.__version__ import __version__
        return f"c302 {__version__}"
    except ImportError:
        return "c302 (version unknown)"


def process_args(argv: list[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。

    :param argv: 命令行参数列表（None 时使用 sys.argv）
    :return: 解析后的参数命名空间
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # 处理 --list-configs 特殊操作
    if args.list_configs:
        configs = list_configs()
        for name in sorted(configs):
            print(name)
        sys.exit(0)

    return args


def main(argv: list[str] | None = None) -> None:
    """CLI 入口函数。

    :param argv: 命令行参数列表（None 时使用 sys.argv）
    """
    args = process_args(argv)

    # 配置日志级别
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(name)s - %(message)s")

    # 调用仿真编排函数
    run_c302(
        config=args.config,
        parameter_set=args.params,
        duration=args.duration,
        dt=args.dt,
        simulator=args.simulator,
        data_reader=args.data_reader,
        target_directory=args.output_dir,
        save=args.save,
        show_plot_already=not args.no_plot,
        verbose=args.verbose,
        plot_connectivity=args.plot_connectivity,
    )


if __name__ == "__main__":
    main()
