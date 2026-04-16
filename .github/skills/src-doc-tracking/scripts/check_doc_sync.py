"""check_doc_sync.py — 检测 git 暂存区中源码变更但文档未同步的情况。

用法：
    python check_doc_sync.py [--src-root project/c302] [--doc-root project/c302-docs/src]

功能：
    - 扫描 git 暂存区（git diff --cached）
    - 找出所有已变更的 .py 源文件
    - 检查其对应的 .py.md 文档是否也在暂存区中
    - 若有源码变更但文档未变更，报错并以退出码 1 退出（可用于 pre-commit hook）
"""
import argparse
import pathlib
import subprocess
import sys

DEFAULT_SRC_ROOT = "project/c302"
DEFAULT_DOC_ROOT = "project/c302-docs/src"
SKIP_FILES = {"__version__.py"}


def get_staged_files() -> list[str]:
    """获取 git 暂存区中所有变更文件的路径列表。"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True, text=True, check=True,
        )
        return [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ 无法执行 git diff，请确保在 git 仓库中运行", file=sys.stderr)
        sys.exit(2)


def src_to_doc(src_file: str, src_root: str, doc_root: str) -> str:
    """将源文件路径映射为文档路径。"""
    src = pathlib.Path(src_file)
    src_root_p = pathlib.Path(src_root)
    doc_root_p = pathlib.Path(doc_root)
    rel = src.relative_to(src_root_p)
    return str(doc_root_p / (rel.name + ".md"))


def main():
    parser = argparse.ArgumentParser(description="检查源码-文档同步状态")
    parser.add_argument("--src-root", default=DEFAULT_SRC_ROOT, help="源码根目录")
    parser.add_argument("--doc-root", default=DEFAULT_DOC_ROOT, help="文档根目录")
    args = parser.parse_args()

    staged = get_staged_files()
    src_root = args.src_root.replace("\\", "/")
    doc_root = args.doc_root.replace("\\", "/")

    # 筛选出源码目录下变更的 .py 文件
    changed_srcs = []
    for f in staged:
        f_norm = f.replace("\\", "/")
        if f_norm.startswith(src_root + "/") and f_norm.endswith(".py"):
            name = pathlib.Path(f_norm).name
            if name not in SKIP_FILES:
                changed_srcs.append(f_norm)

    if not changed_srcs:
        print("✅ 暂存区中无源码变更，无需检查。")
        return

    # 检查对应文档是否也在暂存区
    staged_set = {f.replace("\\", "/") for f in staged}
    missing = []
    for src in changed_srcs:
        doc = src_to_doc(src, src_root, doc_root)
        if doc not in staged_set:
            # 检查文档文件是否存在
            if pathlib.Path(doc).exists():
                missing.append((src, doc))
            # 文档不存在时不报错（可能是新文件，尚未生成文档）

    if missing:
        print("❌ 以下源码已变更但对应文档未同步更新：\n")
        for src, doc in missing:
            print(f"  源码: {src}")
            print(f"  文档: {doc}")
            print()
        print("请更新文档后再提交，或运行:")
        print(f"  python .github/skills/src-doc-tracking/scripts/gen_src_doc.py {args.src_root}/")
        sys.exit(1)
    else:
        print(f"✅ {len(changed_srcs)} 个源码变更均已同步文档。")


if __name__ == "__main__":
    main()
