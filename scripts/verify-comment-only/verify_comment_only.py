# =============================================================================
# 功能描述：
#   代码等价性验证工具，用于确认对 Python 源文件的修改仅涉及注释变更。
#   通过去除注释后格式化再比较 SHA-256 哈希值来判断代码是否等价。
#
# 类与方法索引：
#   StripDocstrings                      (L37)   — AST 转换器：移除模块、类、函数中的 docstring，以便对比时忽略 docstring 变更
#     _strip_body                        (L40)   — 若 body 首个语句为字符串常量（docstring），则移除它
#     visit_Module                       (L58)   — 处理模块级 docstring
#     visit_FunctionDef                  (L68)   — 处理普通函数/方法的 docstring
#     visit_ClassDef                     (L81)   — 处理类的 docstring
#   strip_comments                       (L92)   — 去除 Python 源码中所有注释，保留其他所有 token
#   normalize_code                       (L110)  — 通过 ast.parse + StripDocstrings + ast.unparse 格式化代码，消除空白与 docstring 差异
#   hash_code                            (L128)  — 计算代码字符串的 SHA-256 哈希值
#   verify_file                          (L138)  — 验证两个文件是否代码等价（仅注释不同）
#   verify_directory                     (L176)  — 批量验证目录下所有 .py 文件的代码等价性
#   main                                 (L197)  — CLI 入口：接收原始路径和修改后路径，执行验证
#
# 更新日志：
#   2026-04-16  zmdo  初始版本
#
# 当前维护者：zmdo
# =============================================================================
import ast
import hashlib
import io
import logging
import os
import sys
import tokenize
from pathlib import Path

# 配置 logger，仅输出消息本身（不附加时间戳或级别前缀），用于 CLI 工具输出
logger = logging.getLogger(__name__)


class StripDocstrings(ast.NodeTransformer):
    """AST 转换器：移除模块、类、函数中的 docstring，以便对比时忽略 docstring 变更。"""

    def _strip_body(self, body: list) -> list:
        """若 body 首个语句为字符串常量（docstring），则移除它。

        :param body: AST 语句列表
        :return: 去除 docstring 后的语句列表；若 body 因此变空则插入 pass 防止非法 AST
        """
        # 判断首句是否为 Expr(Constant(str)) 形式的 docstring
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            remaining = body[1:]
            # 若去掉 docstring 后 body 为空，插入 pass 语句防止生成非法 AST
            return remaining if remaining else [ast.Pass()]
        return body

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """处理模块级 docstring。

        :param node: 模块 AST 节点
        :return: 移除 docstring 后的模块节点
        """
        node.body = self._strip_body(node.body)
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """处理普通函数/方法的 docstring。

        :param node: 函数定义 AST 节点
        :return: 移除 docstring 后的函数节点
        """
        node.body = self._strip_body(node.body)
        self.generic_visit(node)
        return node

    # 异步函数与普通函数处理方式相同
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """处理类的 docstring。

        :param node: 类定义 AST 节点
        :return: 移除 docstring 后的类节点
        """
        node.body = self._strip_body(node.body)
        self.generic_visit(node)
        return node


def strip_comments(source: str) -> str:
    """去除 Python 源码中所有注释，保留其他所有 token。

    :param source: 原始 Python 源码字符串
    :return: 去除注释后的源码字符串
    :raises tokenize.TokenError: 源码存在词法错误时抛出
    """
    # 使用 tokenize 精确识别注释 token，避免误处理字符串中的 #
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    result_tokens = []
    for tok_type, tok_string, tok_start, tok_end, tok_line in tokens:
        # 跳过所有 COMMENT 类型 token，保留其他所有内容
        if tok_type == tokenize.COMMENT:
            continue
        result_tokens.append((tok_type, tok_string, tok_start, tok_end, tok_line))
    return tokenize.untokenize(result_tokens)


def normalize_code(source: str) -> str:
    """通过 ast.parse + StripDocstrings + ast.unparse 格式化代码，消除空白与 docstring 差异。

    :param source: 去除注释后的 Python 源码字符串
    :return: 格式化后的代码字符串；解析失败时返回原字符串
    """
    try:
        tree = ast.parse(source)
        # 移除所有 docstring，使 docstring 的新增/修改不触发代码变更警告
        tree = StripDocstrings().visit(tree)
        ast.fix_missing_locations(tree)
        # ast.unparse 将语法树重新序列化，消除注释行造成的空行差异
        return ast.unparse(tree)
    except SyntaxError:
        # 解析失败时直接使用去注释后的原始文本
        return source


def hash_code(source: str) -> str:
    """计算代码字符串的 SHA-256 哈希值。

    :param source: 代码字符串
    :return: 十六进制哈希字符串
    """
    # 使用 UTF-8 编码，确保中文字符一致处理
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def verify_file(original_path: str, modified_path: str) -> bool:
    """验证两个文件是否代码等价（仅注释不同）。

    :param original_path: 原始文件路径
    :param modified_path: 修改后文件路径
    :return: True 表示仅注释变更，False 表示代码被修改
    """
    # 读取两个文件的源码
    original_src = Path(original_path).read_text(encoding="utf-8")
    modified_src = Path(modified_path).read_text(encoding="utf-8")

    # 分别去除注释并格式化
    original_norm = normalize_code(strip_comments(original_src))
    modified_norm = normalize_code(strip_comments(modified_src))

    # 计算哈希值并比较
    original_hash = hash_code(original_norm)
    modified_hash = hash_code(modified_norm)

    if original_hash == modified_hash:
        logger.info("[OK]   %s — 代码等价，仅注释变更", os.path.basename(modified_path))
        return True
    else:
        logger.error("[FAIL] %s — 代码不等价！", os.path.basename(modified_path))
        logger.error("       原始 Hash:  %s", original_hash)
        logger.error("       修改后 Hash: %s", modified_hash)
        # 输出首个差异行以辅助定位
        orig_lines = original_norm.splitlines()
        mod_lines = modified_norm.splitlines()
        for i, (ol, ml) in enumerate(zip(orig_lines, mod_lines), 1):
            if ol != ml:
                logger.error("       首个差异行 %d:", i)
                logger.error("         原始:   %r", ol)
                logger.error("         修改后: %r", ml)
                break
        return False


def verify_directory(original_dir: str, modified_dir: str) -> bool:
    """批量验证目录下所有 .py 文件的代码等价性。

    :param original_dir: 原始目录路径
    :param modified_dir: 修改后目录路径
    :return: True 表示全部通过，False 表示存在失败
    """
    all_passed = True
    # 遍历修改后目录中的所有 .py 文件
    for py_file in sorted(Path(modified_dir).rglob("*.py")):
        # 计算原始目录中对应文件的路径
        rel = py_file.relative_to(modified_dir)
        orig_file = Path(original_dir) / rel
        if not orig_file.exists():
            logger.warning("[SKIP] %s — 原始文件不存在，跳过", rel)
            continue
        if not verify_file(str(orig_file), str(py_file)):
            all_passed = False
    return all_passed


def main() -> None:
    """CLI 入口：接收原始路径和修改后路径，执行验证。"""
    # 配置 logging 输出到 stdout，格式仅保留消息本身，与原 print 行为一致
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    if len(sys.argv) != 3:
        logger.error("用法: python verify_comment_only.py <原始文件或目录> <修改后文件或目录>")
        sys.exit(1)

    original_path = sys.argv[1]
    modified_path = sys.argv[2]

    # 根据路径类型选择文件验证还是目录验证
    if os.path.isdir(original_path) and os.path.isdir(modified_path):
        success = verify_directory(original_path, modified_path)
    elif os.path.isfile(original_path) and os.path.isfile(modified_path):
        success = verify_file(original_path, modified_path)
    else:
        logger.error("错误：两个路径必须同为文件或同为目录")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
