---
name: python-code-style
description: "基于 SP-CODE-2026-001 编码规范审查和强制执行 Python 代码风格。检查文件头（功能描述/类与方法索引/更新日志/当前维护者）、reST 文档字符串、强制行内注释、类型注解、命名规范、导入顺序、字符串风格、日志使用以及单元测试覆盖。当用户要求审查 Python 代码风格、执行编码规范检查、检查代码合规性或重构代码以符合项目规范时使用。编写新 Python 文件时也应使用以确保从一开始就符合规范。每个 Python 函数/方法必须有注释和对应的单元测试。"
license: MIT
compatibility: "c302（C. elegans 神经网络建模框架，OpenWorm 子项目）。Python 3.10+，遵循 SP-CODE-2026-001 编码规范。"
metadata:
  author: Copilot
  version: "1.0"
allowed-tools: Read Edit Terminal
---

# Python 代码风格强制执行

## 何时使用

- 用户要求审查 Python 代码的风格合规性
- 用户要求检查或执行 Python 文件的编码规范
- 用户正在编写新的 Python 模块并需要遵循项目规范
- 用户要求按照 SP-CODE-2026-001 重构代码
- 用户询问"这段代码符合规范吗？"或类似问题
- 完成代码重构后，验证合规性

## 核心规范：SP-CODE-2026-001

完整编码规范位于 `references/SP-CODE-2026-001_Python代码规范.md`，需要详细规则时加载该文件。

以下为关键规则摘要：

### 文件头（必须）

每个 Python 源文件必须以头部注释块开头：

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

### 文档字符串（reST 风格）

所有公开模块、类、函数和方法必须使用 reStructuredText 格式的文档字符串：

```python
def example(param1: str, param2: int) -> bool:
    """简要描述函数功能。

    :param param1: 参数1的说明
    :param param2: 参数2的说明
    :return: 返回值说明
    :raises ValueError: 异常条件说明
    """
```

### 类型注解

- 所有函数参数和返回值必须有类型注解
- 使用 Python 3.10+ 内置泛型语法：`list[str]`、`dict[str, Any]`、`str | None`
- 无返回值的函数标注：`-> None`

### 命名规范

| 类型 | 风格 | 示例 |
|------|------|------|
| 模块/包 | `snake_case` | `data_loader.py` |
| 类 | `PascalCase` | `AgentRunner` |
| 函数/方法 | `snake_case` | `run_agent()` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_RETRY` |
| 私有 | `_前缀` | `_internal_state` |

### 字符串

- 统一使用**双引号** `"` 包裹字符串
- 使用 **f-string** 进行字符串插值
- 禁止使用 `%` 格式化或 `+` 拼接

### 注释（强制）

注释是**强制性要求**，不可省略。每一段逻辑都必须附带注释。

- **函数/方法**：除 docstring 外，函数体内每段关键逻辑必须有行内注释说明目的
- **类**：类属性和关键方法必须有注释
- **条件分支**：`if/elif/else` 分支必须注释说明分支条件的业务含义
- **循环**：`for/while` 循环必须注释说明遍历目的
- **异常处理**：`try/except` 块必须注释说明捕获原因和处理策略
- **复杂表达式**：列表推导、生成器表达式、三元运算等必须附注释
- 注释统一使用**中文**，关键词保持英文（`:param:`、`TODO`、`FIXME` 等）
- 行内注释：`#` 前 2 个空格，`#` 后 1 个空格
- 注释要说明**为什么**，而非**是什么**
- **缺少注释视为不合规**，与缺少 docstring 同等严重

### 导入顺序

顺序：标准库 → 第三方库 → 内部模块，组间空一行。

### 日志规范

- 使用 `logging` 模块，生产代码禁止使用 `print()`
- 使用延迟格式化：`logger.info("处理 %d 条记录", count)`

### 禁止事项

- 禁止 `from module import *`
- 禁止裸 `except:`
- 禁止可变默认参数
- 禁止在生产代码中使用 `print()` 输出日志

### 单元测试（强制）

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

## 自动检查脚本

运行检查脚本进行基础合规性验证：

```bash
python .github/skills/python-code-style/scripts/check_style.py <文件或目录>
```

脚本检查项：
1. 文件头字段是否齐全（功能描述 / 类与方法索引 / 更新日志 / 当前维护者）
2. 类与方法索引是否存在且完整
3. 公开函数是否有 docstring
4. 函数签名是否有类型注解
5. 是否使用了单引号（应使用双引号）
6. 非测试文件是否使用了 `print()`
7. 是否使用了 `import *`

### 索引自动生成

自动生成或更新类与方法索引：

```bash
# 预览索引（不修改文件）
python .github/skills/python-code-style/scripts/gen_index.py <文件或目录>

# 就地更新文件头部索引
python .github/skills/python-code-style/scripts/gen_index.py <文件或目录> --write
```

脚本功能：
- 通过 AST 解析提取所有类/函数/方法定义及其行号
- 使用 docstring 首行作为描述
- 替换现有索引块，或在功能描述段落后插入新索引
- 自引用文件可能需要运行**两次**才能收敛（索引条目数变化会导致行号偏移）

### 索引验证

验证头部索引是否与实际代码一致：

```bash
python .github/skills/python-code-style/scripts/check_index.py <文件或目录>
```

报告内容：缺失条目、多余条目、行号偏差、层级错误。

详细编码规则请加载 `references/sp-code-2026-001-summary.md`。

## 工作流程

### 步骤 1：确定目标文件

确定需要检查的 Python 文件——单个文件、目录或全部后端代码。

### 步骤 2：运行自动检查

对目标文件执行检查脚本，获取合规性报告。

### 步骤 3：审查结果

分析脚本输出，每个问题列出文件、行号和违反的规则。

### 步骤 4：修复问题

按照规范进行修复：
- 缺少文件头 → 添加标准头部注释块（含类与方法索引）
- 类与方法索引缺失或过时 → 重新生成索引，确保行号和描述正确
- 缺少 docstring → 添加 reST 风格的文档字符串
- 缺少类型注解 → 补充参数和返回值类型
- 使用了单引号 → 替换为双引号
- 使用了 `print()` → 替换为 `logging`
- **缺少注释** → 为所有关键逻辑块添加行内注释
- **缺少单元测试** → 创建 `tests/test_{module}.py`，包含正向和边界测试用例

### 步骤 5：更新并验证索引（每次修改后必做）

任何代码修改（新增/删除/移动函数、类或方法）后，运行：

```bash
# 自动更新索引
python .github/skills/python-code-style/scripts/gen_index.py <modified_files> --write

# 检查索引是否正确
python .github/skills/python-code-style/scripts/check_index.py <modified_files>
```

**重要：** 如果 gen_index 更新后 check_index 仍报错，再执行一次 gen_index + check_index（索引条目数变化会导致行号偏移，需迭代收敛）。

### 步骤 6：验证单元测试

对相应测试文件运行 `pytest`，确保测试通过：

```bash
pytest tests/test_{module_name}.py -v
```

### 步骤 7：二次检查

再次运行检查脚本，确认所有问题已解决。

## 注意事项

- 文件头使用 `# =====...=====` 分隔线（至少 10 个 `=`），而非 `"""` 文档字符串
- **类与方法索引是强制的**：头部必须包含文件内所有类、函数、方法的分层索引，并标注行号和一句话描述
- **每次修改代码后必须执行** `gen_index.py --write` + `check_index.py` 确保索引与代码一致
- 自引用文件可能需要执行两次 gen_index 才能收敛（索引条目数变化会导致行号偏移）
- 文档字符串使用 reST 风格（`:param:`、`:return:`），不使用 Google 或 NumPy 风格
- 类型注解必须使用 Python 3.10+ 语法（`list[str]` 而非 `List[str]`，`str | None` 而非 `Optional[str]`）
- 注释统一使用中文，但 `:param:`、`TODO`、`FIXME` 等关键词保持英文
- 检查脚本仅执行基础静态分析，不替代 `ruff` 或 `mypy`
- **注释是强制的**：没有注释的函数体视为不合规，即使逻辑简单也要注释说明意图
- **单元测试是强制的**：每个新增/修改的 Python 模块必须有对应 `tests/test_*.py`，没有测试不可提交
- 测试文件本身也必须遵循 docstring 和注释规范
