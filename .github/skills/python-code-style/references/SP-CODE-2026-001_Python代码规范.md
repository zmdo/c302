# Python 代码规范

<!--
  文档编号：SP-CODE-2026-001
  文档简介：定义 Python 后端代码的编码风格、命名约定、注释格式、类型注解、
            导入顺序、异常处理和日志使用等规范，确保代码库风格统一、可读性高。
  发布状态：ACTIVE
  适用范围：全系统
  创建日期：2026-03-23
  最后更新：2026-03-23
  负责智能体：Copilot
  文件类型：规范文件（SP）
-->

## 目录

1. [一、概述](#一概述)
2. [二、文件与编码](#二文件与编码)
3. [三、命名规范](#三命名规范)
4. [四、代码格式](#四代码格式)
5. [五、注释规范](#五注释规范)
6. [六、类型注解](#六类型注解)
7. [七、导入规范](#七导入规范)
8. [八、异常处理](#八异常处理)
9. [九、日志规范](#九日志规范)
10. [十、禁止事项](#十禁止事项)

---

## 一、概述

本规范定义 Python 后端代码的统一编码风格，适用于使用 Python 3.10+ 的所有后端模块。

### 1.1 总体原则

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 风格指南
- 代码应具备**可读性**优先于简洁性
- 所有注释、文档字符串使用**中文**，关键词（如 `:param:`、`:return:`、`:raises:`、`TODO`、`FIXME`、`NOTE` 等）保持英文
- 使用 `ruff` 进行代码格式化与 lint 检查，使用 `mypy` 进行静态类型检查

---

## 二、文件与编码

- 源文件统一使用 **UTF-8** 编码，文件头无需 `# -*- coding: utf-8 -*-` 声明（Python 3 默认）
- 每个文件末尾保留**一个空行**
- 文件名使用**小写字母加下划线**（snake_case），例如 `agent_runner.py`

### 2.1 文件头部注释

每个 Python 源文件（模块）顶部必须包含文件头注释，位于 `shebang`（如有）之后、模块 docstring 之前。

**格式规范：**

```python
# =============================================================================
# 功能描述：
#   任务执行器，负责驱动多步骤任务的工具调用循环，
#   维护执行上下文、工具调用记录与最大步数限制。
#
# 类与方法索引：
#   TaskRunner                       (L25)   — 驱动多步骤任务的执行器
#     __init__                       (L30)   — 初始化执行器配置
#     run                            (L45)   — 执行任务循环
#     _call_tool                     (L78)   — 调用单个工具并返回结果
#   parse_config                     (L120)  — 解析配置文件为字典
#
# 更新日志：
#   2026-03-18  张三  初始创建，实现基础执行循环与异常处理
#   2026-04-02  李四  新增并发执行支持，引入 asyncio.gather
#   2026-05-10  李四  优化上下文窗口裁剪策略，减少 token 消耗
#
# 当前维护者：李四
# =============================================================================
```

**字段说明：**

| 字段 | 是否必填 | 说明 |
|------|----------|------|
| 功能描述 | **必填** | 简要说明本模块的职责与使用场景，2～5 行为宜 |
| 类与方法索引 | **必填** | 列出文件内所有类、函数、方法，标注行号和一句话描述（详见下方规则） |
| 更新日志 | **必填** | 每次有实质性改动时追加一条，格式为 `日期  维护者  改动内容` |
| 当前维护者 | **必填** | 标注当前负责维护该文件的人员或智能体名称 |

**类与方法索引规则：**

- **必须列出**文件中所有的类、函数和方法（含私有方法）
- 类下的方法使用 **2 空格缩进**表示层级关系
- 每一项后标注 `(L行号)` 表示定义所在行
- 行号后用 `—` 加**一句话**描述其作用
- 如果文件只有函数没有类，直接平铺列出
- 当文件内容发生变更时（新增/删除/移动），必须同步更新索引中的行号和条目
- 模块级常量可选列出，仅在常量数量少且含义重要时列出

**注意事项：**

- 更新日志按**时间升序**排列，最新记录在最后
- 维护者名称须与项目组成员管理系统保持一致

---

## 三、命名规范

### 3.1 基本规则

| 类型 | 命名风格 | 示例 |
|------|----------|------|
| 模块 / 包 | `snake_case` | `data_loader.py` |
| 类 | `PascalCase` | `AgentRunner` |
| 函数 / 方法 | `snake_case` | `run_agent()` |
| 变量 | `snake_case` | `task_queue` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| 私有属性 / 方法 | 前缀单下划线 `_` | `_internal_state` |
| 名称改写（避免子类覆盖） | 前缀双下划线 `__` | `__secret` |
| 类型变量 | `PascalCase` 或单大写字母 | `T`、`AgentT` |

### 3.2 命名原则

- 名称应**具有语义**，避免使用 `tmp`、`data2`、`foo` 等无意义名称
- 布尔变量 / 函数以 `is_`、`has_`、`can_` 为前缀，例如 `is_running`、`has_permission`
- 集合类型变量使用复数，例如 `agents`、`task_ids`
- 避免使用内置名称（如 `id`、`type`、`list`、`input`）作为变量名

---

## 四、代码格式

### 4.1 缩进与行宽

- 使用 **4 个空格**缩进，不使用 Tab
- 每行最大宽度 **120 个字符**（文档字符串和注释保持 **80 个字符**以内）

### 4.2 空行

- 顶层定义（类、函数）之间保留 **2 个空行**
- 类内方法之间保留 **1 个空行**
- 函数内部逻辑分组之间可保留 **1 个空行**，但不得超过 1 个

### 4.3 空格

```python
# ✅ 正确：操作符两侧各一个空格
result = x + y

# ✅ 正确：函数调用括号内无空格
func(arg1, arg2)

# ✅ 正确：切片中冒号两侧无空格
items[1:3]

# ✅ 正确：关键字参数不加空格
func(key=value)

# ❌ 错误
result=x+y
func( arg1, arg2 )
```

### 4.4 括号与续行

```python
# ✅ 推荐：使用括号隐式续行
result = (
    some_very_long_variable_name
    + another_long_variable_name
    + yet_another_variable
)

# ✅ 函数参数过多时，每个参数独占一行
def create_agent(
    name: str,
    model: str,
    tools: list[str],
    max_steps: int = 10,
) -> "Agent":
    ...
```

### 4.5 字符串

- 统一使用**双引号** `"` 包裹字符串
- 多行字符串使用三引号 `"""`
- 字符串拼接优先使用 **f-string**，避免 `%` 格式化和 `+` 拼接

```python
# ✅ 推荐
name = "agent"
message = f"当前智能体：{name}"

# ❌ 避免
message = "当前智能体：" + name
message = "当前智能体：%s" % name
```

---

## 五、注释规范

> **核心约定**：所有注释与文档字符串使用**中文**；关键词（`:param:`、`:type:`、`:return:`、`:rtype:`、`:raises:`、`TODO`、`FIXME`、`NOTE`、`HACK`）保留英文。

### 5.1 行内注释

- 行内注释与代码之间保留 **2 个空格**，`#` 后跟 **1 个空格**
- 注释应解释**为什么**而非**是什么**（代码本身已经说明了"是什么"）

```python
MAX_RETRY_COUNT = 3  # 超过此次数则放弃重试，避免无限循环

# ❌ 无意义注释（与代码重复）
x = x + 1  # 将 x 加 1
```

### 5.2 块注释

- 块注释与被注释代码保持相同缩进
- 多行块注释每行以 `# ` 开头

```python
# 初始化任务队列：从配置中读取优先级，
# 高优先级任务将被优先调度执行
task_queue = PriorityQueue(config.priority)
```

### 5.3 文档字符串（Docstring）

所有**公开的**模块、类、函数、方法都必须有文档字符串，使用 **reStructuredText（reST）** 风格。

#### 函数 / 方法

```python
def fetch_tool_result(tool_name: str, arguments: dict) -> str:
    """调用指定工具并返回执行结果。

    :param tool_name: 工具的唯一标识名称
    :param arguments: 传递给工具的参数字典
    :return: 工具执行后返回的文本结果
    :raises ToolNotFoundError: 当工具名称不存在时抛出
    :raises ToolExecutionError: 当工具执行过程中发生错误时抛出
    """
    ...
```

#### 类

```python
class AgentRunner:
    """负责驱动智能体完成多步骤任务的执行器。

    该执行器维护智能体的状态、工具调用记录与上下文窗口，
    支持同步和异步两种运行模式。

    :param agent: 待运行的智能体实例
    :param max_steps: 最大执行步数，默认为 20
    """

    def __init__(self, agent: "Agent", max_steps: int = 20) -> None:
        ...
```

#### 模块

```python
"""
智能体任务调度模块。

本模块提供任务队列管理、优先级调度与并发控制功能，
供上层编排层调用。
"""
```

#### 简单属性注释

```python
class Config:
    host: str  # 服务监听地址
    port: int  # 服务监听端口，默认 8080
    debug: bool  # 是否开启调试模式
```

### 5.4 特殊标记注释

```python
# TODO: 待实现流式响应支持
# FIXME: 在并发场景下存在竞态条件，需加锁
# NOTE: 此处顺序不可更改，依赖初始化先后关系
# HACK: 临时绕过上游 SDK 的 bug，待官方修复后移除
```

---

## 六、类型注解

- 所有**函数参数和返回值**必须添加类型注解
- 类的**实例属性**在 `__init__` 中注解，或使用 `dataclass` / `pydantic` 模型
- 使用 Python 3.10+ 的内置泛型语法（如 `list[str]`，而非 `List[str]`）
- 无返回值的函数标注 `-> None`

```python
from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from typing import Any


def run_pipeline(
    steps: list[Callable[[dict], dict]],
    initial_input: dict[str, Any],
    *,
    timeout: float | None = None,
) -> dict[str, Any]:
    """按顺序执行管道中的所有步骤并返回最终结果。

    :param steps: 按顺序执行的处理函数列表，每个函数接收并返回一个字典
    :param initial_input: 传入管道第一个步骤的初始数据
    :param timeout: 单步骤超时时间（秒），为 None 时不限制
    :return: 管道最后一个步骤的输出字典
    """
    result = initial_input
    for step in steps:
        result = step(result)
    return result


async def stream_tokens(prompt: str) -> AsyncGenerator[str, None]:
    """流式生成模型的 token 输出。

    :param prompt: 发送给模型的提示文本
    :return: 异步生成器，逐个产出 token 字符串
    """
    ...
    yield ""
```

---

## 七、导入规范

### 7.1 导入顺序

按以下三组顺序排列，**组间空一行**：

1. 标准库
2. 第三方库
3. 本项目内部模块

```python
# 标准库
import asyncio
import json
from pathlib import Path
from typing import Any

# 第三方库
import httpx
from pydantic import BaseModel

# 内部模块
from myproject.core.runner import TaskRunner
from myproject.tools.base import BaseTool
```

### 7.2 导入规则

- 每行只导入**一个模块**
- 优先使用 `from module import name` 导入具体名称
- 禁止使用 `from module import *`（测试文件除外）
- 避免循环导入；如有必要，在函数内部进行局部导入

```python
# ✅ 正确
from pathlib import Path

# ❌ 错误
import os, sys
from module import *
```

---

## 八、异常处理

### 8.1 基本原则

- 捕获**具体的异常类型**，禁止裸 `except:` 或 `except Exception:` 兜底（日志/顶层边界除外）
- 异常信息应提供足够的上下文，便于排查
- 自定义异常继承自项目基础异常类 `AppError`，并以 `Error` 结尾

### 8.2 自定义异常

```python
class AppError(Exception):
    """项目所有自定义异常的基类。"""


class ToolNotFoundError(AppError):
    """请求的工具在注册表中不存在时抛出。"""


class ToolExecutionError(AppError):
    """工具执行过程中发生错误时抛出。"""
```

### 8.3 异常捕获与上下文链

```python
# ✅ 保留原始异常上下文（raise from）
try:
    result = await tool.execute(arguments)
except httpx.HTTPError as exc:
    raise ToolExecutionError(
        f"调用工具 '{tool_name}' 时发生网络错误：{exc}"
    ) from exc

# ✅ 仅在确实需要忽略异常时使用 contextlib.suppress
from contextlib import suppress

with suppress(FileNotFoundError):
    cache_file.unlink()
```

### 8.4 禁止的写法

```python
# ❌ 裸 except，会捕获 KeyboardInterrupt 等系统异常
try:
    ...
except:
    pass

# ❌ 吞掉异常而不记录
try:
    ...
except Exception:
    pass
```

---

## 九、日志规范

- 使用标准库 `logging`，禁止使用 `print` 输出运行时信息
- 每个模块获取以模块名命名的 logger，不在库代码中配置 handler
- 日志消息使用**中文**；格式化参数使用 `%s` 懒加载风格（不提前格式化字符串）

```python
import logging

logger = logging.getLogger(__name__)


def load_skill(skill_path: str) -> None:
    """加载指定路径的技能文件。

    :param skill_path: 技能目录的绝对路径
    :raises FileNotFoundError: 路径不存在时抛出
    """
    logger.debug("开始加载技能，路径：%s", skill_path)

    if not Path(skill_path).exists():
        logger.error("技能路径不存在：%s", skill_path)
        raise FileNotFoundError(f"技能路径不存在：{skill_path}")

    logger.info("技能加载完成：%s", skill_path)
```

### 日志级别使用指南

| 级别 | 使用场景 |
|------|----------|
| `DEBUG` | 详细的诊断信息，仅开发/调试时使用 |
| `INFO` | 正常的业务流程节点（启动、任务开始/完成等） |
| `WARNING` | 非预期但可以继续执行的情况（降级、重试等） |
| `ERROR` | 发生了错误，当前操作无法完成 |
| `CRITICAL` | 严重错误，可能导致程序无法继续运行 |

---

## 十、禁止事项

1. **禁止裸 `except:`**：必须捕获具体的异常类型，不得使用裸 `except:` 或 `except Exception:` 兜底（日志/顶层边界除外）
2. **禁止 `from module import *`**：除测试文件外，禁止使用通配符导入
3. **禁止 `print` 输出运行时信息**：必须使用 `logging` 模块
4. **禁止使用 `%` 格式化字符串**：统一使用 f-string
5. **禁止忽略类型注解**：所有公开函数的参数和返回值必须添加类型注解
6. **禁止循环导入**：如有必要，在函数内部进行局部导入
7. **禁止使用可变默认参数**：如 `def func(items=[]):`，应改为 `def func(items: list | None = None):`
