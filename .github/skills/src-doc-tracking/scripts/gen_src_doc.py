"""gen_src_doc.py — 为 Python 源文件生成对应的分析文档骨架。

用法：
    python gen_src_doc.py <源文件或目录> [--doc-root <文档根目录>]

功能：
    - 若文档不存在，生成完整骨架（模块概要 + 分析记录 + 修改记忆 + 踩坑记录）
    - 若文档已存在，跳过（不覆盖手工内容）
    - 代码结构目录已在源码头部注释块中维护，文档中不重复收录
"""
import argparse
import datetime
import pathlib
import subprocess
import sys

# ── 默认映射：project/c302/*.py → project/c302-docs/src/*.py.md ──
DEFAULT_SRC_ROOT = "project/c302"
DEFAULT_DOC_ROOT = "project/c302-docs/src"

# 跳过的文件
SKIP_FILES = {"__version__.py", "__pycache__", ".pyc"}


def src_to_doc_path(src_path: str, doc_root: str | None = None) -> pathlib.Path:
    """将源文件路径转换为对应的文档路径。"""
    src = pathlib.Path(src_path)
    if doc_root:
        doc_dir = pathlib.Path(doc_root)
    else:
        # project/c302/xxx.py → project/c302-docs/src/xxx.py.md
        parent = src.parent
        doc_dir = parent.parent / (parent.name + "-docs") / "src"
    return doc_dir / (src.name + ".md")


def get_short_hash() -> str:
    """获取当前 git 短哈希。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def generate_skeleton(src_path: str, doc_path: pathlib.Path) -> str:
    """生成完整的文档骨架。"""
    src_name = pathlib.Path(src_path).name
    today = datetime.date.today().isoformat()
    short_hash = get_short_hash()

    skeleton = f"""# {src_name} 源码分析

> 自动生成于 {today}，基于 commit {short_hash}

## 模块概要

<!-- TODO: 填写模块功能描述 -->

## 分析记录

<!-- 按时间倒序记录每次分析/勘误的发现 -->

## 修改记忆

| 日期 | commit | 修改范围 | 修改原因 |
|------|--------|---------|---------|

## 踩坑记录

<!-- 记录非显而易见的问题和解决方案 -->
"""
    return skeleton


def process_file(src_path: str, doc_root: str | None = None) -> None:
    """处理单个源文件。"""
    src = pathlib.Path(src_path)
    if src.name in SKIP_FILES or src.suffix != ".py":
        return

    doc_path = src_to_doc_path(src_path, doc_root)

    if not doc_path.exists():
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        content = generate_skeleton(src_path, doc_path)
        doc_path.write_text(content, encoding="utf-8")
        print(f"  [NEW] {doc_path}")
    else:
        print(f"  [OK]  {doc_path} (已存在)")


def main():
    parser = argparse.ArgumentParser(description="生成/更新源码分析文档")
    parser.add_argument("path", help="源文件或目录路径")
    parser.add_argument("--doc-root", default=None, help="文档输出根目录（默认自动推导）")
    args = parser.parse_args()

    target = pathlib.Path(args.path)

    if target.is_file():
        process_file(str(target), args.doc_root)
    elif target.is_dir():
        py_files = sorted(target.glob("*.py"))
        count = 0
        for f in py_files:
            if f.name not in SKIP_FILES:
                process_file(str(f), args.doc_root)
                count += 1
        print(f"\n共处理 {count} 个文件。")
    else:
        print(f"路径不存在: {target}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
