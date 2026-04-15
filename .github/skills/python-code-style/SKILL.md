---
name: python-code-style
description: "Review and enforce Python code against SP-CODE-2026-001 coding standard. Check file headers (功能描述/类与方法索引/更新日志/当前维护者), reST docstrings, mandatory inline comments, type annotations, naming conventions, import order, string style, logging usage, and unit test coverage. Use when the user asks to review Python code style, enforce coding standards, check code compliance, or refactor code to meet the project's Python conventions. Also use when writing new Python files to ensure they conform from the start. Every Python function/method MUST have comments and corresponding unit tests."
license: MIT
compatibility: "c302（C. elegans 神经网络建模框架，OpenWorm 子项目）。Python 3.10+，遵循 SP-CODE-2026-001 编码规范。"
metadata:
  author: Copilot
  version: "1.0"
allowed-tools: Read Edit Terminal
---

# Python Code Style Enforcement

## When to Use

- User asks to review Python code for style compliance
- User asks to check or enforce coding standards on Python files
- User is writing new Python modules and needs to follow project conventions
- User asks to refactor code to match SP-CODE-2026-001
- User asks "does this code follow the standard?" or similar questions
- After completing a code refactoring task, to verify compliance

## Core Standard: SP-CODE-2026-001

The full coding standard is at `references/SP-CODE-2026-001_Python代码规范.md`. Load it for detailed rules.

Key rules summarized below:

### File Header (Required)

Every Python source file must start with a header block:

```python
# =============================================================================
# 功能描述：
#   简要描述模块职责与使用场景，2～5 行。
#
# 类与方法索引：
#   MyClass                          (L25)   — 负责处理数据加载与缓存
#     __init__                       (L30)   — 初始化加载器配置
#     load_data                      (L45)   — 从指定路径加载数据集
#     _parse_row                     (L78)   — 解析单行数据为字典
#   helper_func                      (L120)  — 辅助函数，格式化输出字符串
#   CONSTANT_NAME                    (L5)    — 模块级常量（可选，仅列出关键常量）
#
# 更新日志：
#   YYYY-MM-DD  维护者  改动内容
#
# 当前维护者：维护者名称
# =============================================================================
```

#### 类与方法索引规则

- **必须列出**文件中所有的类、函数和方法（含私有方法）
- 类下的方法使用 **2 空格缩进**表示层级关系
- 每一项后标注 `(L行号)` 表示定义所在行
- 行号后用 `—` 加**一句话**描述其作用
- 如果文件只有函数没有类，直接平铺列出
- 当文件内容发生变更时（新增/删除/移动），必须同步更新索引中的行号和条目
- 模块级常量可选列出，仅在常量数量少且含义重要时列出

### Docstrings (reST Style)

All public modules, classes, functions, and methods must have docstrings using reStructuredText format:

```python
def example(param1: str, param2: int) -> bool:
    """简要描述函数功能。

    :param param1: 参数1的说明
    :param param2: 参数2的说明
    :return: 返回值说明
    :raises ValueError: 异常条件说明
    """
```

### Type Annotations

- All function parameters and return values must have type annotations
- Use Python 3.10+ built-in generics: `list[str]`, `dict[str, Any]`, `str | None`
- Functions with no return value: `-> None`

### Naming

| Type | Style | Example |
|------|-------|---------|
| Module/Package | `snake_case` | `data_loader.py` |
| Class | `PascalCase` | `AgentRunner` |
| Function/Method | `snake_case` | `run_agent()` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRY` |
| Private | `_prefix` | `_internal_state` |

### Strings

- Use **double quotes** `"` for all strings
- Use **f-strings** for interpolation
- No `%` formatting or `+` concatenation

### Comments（强制）

注释是**强制性要求**，不可省略。每一段逻辑都必须附带注释。

- **函数/方法**：除 docstring 外，函数体内每段关键逻辑必须有行内注释说明目的
- **类**：类属性和关键方法必须有注释
- **条件分支**：`if/elif/else` 分支必须注释说明分支条件的业务含义
- **循环**：`for/while` 循环必须注释说明遍历目的
- **异常处理**：`try/except` 块必须注释说明捕获原因和处理策略
- **复杂表达式**：列表推导、生成器表达式、三元运算等必须附注释
- All comments in **Chinese**, keywords in English (`:param:`, `TODO`, `FIXME`, etc.)
- Inline comments: 2 spaces before `#`, 1 space after
- Explain **why**, not **what**
- **缺少注释视为不合规**，与缺少 docstring 同等严重

### Imports

Order: stdlib → third-party → internal, with blank lines between groups.

### Logging

- Use `logging` module, never `print()` in production code
- Use lazy formatting: `logger.info("处理 %d 条记录", count)`

### Forbidden Practices

- No `from module import *`
- No bare `except:`
- No mutable default arguments
- No `print()` for logging

### Unit Tests（强制）

单元测试是**强制性要求**，每个 Python 模块必须有对应的测试文件。

- **测试文件命名**：`test_{module_name}.py`，放在同级 `tests/` 目录下
- **测试覆盖要求**：
  - 每个 public 函数/方法至少 1 个正向测试用例
  - 每个 public 函数/方法至少 1 个异常/边界测试用例
  - 涉及分支逻辑的函数，每个分支至少 1 个测试用例
- **测试框架**：使用 `pytest`
- **测试命名**：`test_{function_name}_{scenario}`，如 `test_login_success`、`test_login_invalid_password`
- **新增/修改代码时**：必须同步新增/更新对应的单元测试
- **无测试文件视为不合规**，与缺少 docstring 同等严重

示例结构：

```
module_name.py
tests/
  test_module_name.py
```

示例测试：

```python
import pytest
from module_name import example


def test_example_normal_case() -> None:
    """测试 example 函数的正常情况。"""
    # 传入有效参数，验证返回 True
    result = example("hello", 42)
    assert result is True


def test_example_empty_string() -> None:
    """测试 example 函数传入空字符串的边界情况。"""
    # 空字符串应返回 False
    result = example("", 0)
    assert result is False
```

## Automated Check Script

Run the checking script to perform basic compliance validation:

```bash
python skills/python-code-style/scripts/check_style.py <file_or_directory>
```

The script checks:
1. File header presence (功能描述 / 类与方法索引 / 更新日志 / 当前维护者)
2. Class & method index presence and completeness
3. Public function docstring presence
4. Type annotation coverage on function signatures
5. Single-quote vs double-quote usage
6. `print()` usage in non-test files
7. `import *` usage

For detailed coding rules, load `references/sp-code-2026-001-summary.md`.

## Workflow

### Step 1: Identify Target Files

Determine which Python files need checking — single file, directory, or all backend code.

### Step 2: Run Automated Check

Execute the check script on the target files to get a compliance report.

### Step 3: Review Results

Analyze the script output. Each issue lists the file, line, and rule violated.

### Step 4: Fix Issues

Apply fixes following the standard:
- Missing file header → Add standard header block (including class/method index)
- Missing/outdated class & method index → Regenerate index with correct line numbers and descriptions
- Missing docstring → Add reST-style docstring
- Missing type annotations → Add parameter and return types
- Single quotes → Replace with double quotes
- `print()` → Replace with `logging`
- **Missing comments** → Add inline comments for all key logic blocks
- **Missing unit tests** → Create `tests/test_{module}.py` with positive + edge case tests

### Step 5: Verify Unit Tests

Run `pytest` on the corresponding test file to ensure tests pass:

```bash
pytest tests/test_{module_name}.py -v
```

### Step 6: Re-check

Run the check script again to confirm all issues are resolved.

## Gotchas

- The file header uses `# =====...=====` separators (at least 10 `=` chars), not `"""` docstrings
- **类与方法索引是强制的**：头部必须包含文件内所有类、函数、方法的分层索引，并标注行号和一句话描述
- 修改代码后必须同步更新索引中的行号，否则视为不合规
- Docstrings use reST (`:param:`, `:return:`) not Google or NumPy style
- Type annotations must use Python 3.10+ syntax (`list[str]` not `List[str]`, `str | None` not `Optional[str]`)
- Comments are in Chinese but keywords like `:param:`, `TODO`, `FIXME` stay in English
- The checking script performs basic static analysis only; it does not replace `ruff` or `mypy`
- **注释是强制的**：没有注释的函数体视为不合规，即使逻辑简单也要注释说明意图
- **单元测试是强制的**：每个新增/修改的 Python 模块必须有对应 `tests/test_*.py`，没有测试不可提交
- 测试文件本身也必须遵循 docstring 和注释规范
