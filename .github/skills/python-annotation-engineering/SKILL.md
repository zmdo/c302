---
name: python-annotation-engineering
description: "Python 代码注释工程：为已有 Python 代码库批量添加中文注释（docstring + 行内注释 + 文件头）。执行标准化 7 步流程：调研 → docstring YAML 规范 → add_docstring.py → 文件头 → 行内注释 → 索引收敛 → 等价性验证。Use when: 用户要求为 Python 文件添加中文注释、翻译英文注释为中文、批量注释工程、按注释计划执行文件注释任务。内置 add_docstring.py / gen_index.py / check_index.py / verify_comment_only.py 四个工具脚本。依赖 python-code-style skill 的文件头规范。"
license: MIT
compatibility: "任何 Python 3.10+ 项目。需要 PyYAML（pip install pyyaml）。"
metadata:
  author: Copilot
  version: "1.1"
allowed-tools: Read Edit Terminal
---

# Python 代码注释工程

## 何时使用

- 用户要求为 Python 源文件批量添加中文注释
- 用户要求翻译 Python 文件中的英文注释为中文
- 用户要求按照注释计划/任务清单逐文件执行注释任务
- 用户要求为函数添加 docstring
- 用户执行类似"执行计划N的阶段M"的注释类任务
- 用户要求验证修改是否仅涉及注释变更

## 依赖

| 依赖 skill | 用途 | 必须？ |
|-----------|------|--------|
| `python-code-style` | 文件头格式规范（SP-CODE-2026-001） | 推荐 |

> 若项目中无 `python-code-style` skill，本 skill 内置的 `gen_index.py` / `check_index.py`
> 仍可独立工作，但文件头的「功能描述/更新日志/维护者」等非索引段落需手动维护。

## 核心约束

**只增改注释，不动代码。** 这是注释工程的硬性约束。

| 允许 | 禁止 |
|------|------|
| 新增 `#` 行内注释 | 修改任何语句或表达式 |
| 替换英文 `#` 注释为中文 | 修改变量名、函数名、类名 |
| 在函数体内插入 docstring | 修改字符串字面量 |
| 在代码行末尾添加 `  # 说明` | 重新格式化代码（空格、缩进） |

## 内置工具

所有工具位于 [scripts/](./scripts/) 目录：

| 工具 | 文件 | 用途 |
|------|------|------|
| add_docstring.py | [scripts/add_docstring.py](./scripts/add_docstring.py) | 安全插入 docstring（幂等，不改已有代码行） |
| gen_index.py | [scripts/gen_index.py](./scripts/gen_index.py) | 自动生成/更新文件头「类与方法索引」 |
| check_index.py | [scripts/check_index.py](./scripts/check_index.py) | 验证索引与 AST 实际定义一致 |
| verify_comment_only.py | [scripts/verify_comment_only.py](./scripts/verify_comment_only.py) | 验证修改仅涉及注释（SHA-256 等价性比对） |

## 标准 7 步流程

**每个待注释文件必须按以下顺序执行，不可跳步。**

```
步骤 1  调研目标文件
   ↓
步骤 2  编写 docstring YAML 规范
   ↓
步骤 3  运行 add_docstring.py
   ↓
步骤 4  添加文件头（功能描述 / 索引 / 更新日志 / 维护者）
   ↓
步骤 5  添加/翻译行内注释
   ↓
步骤 6  更新索引（gen_index.py 收敛 + check_index.py）
   ↓
步骤 7  等价性验证（verify_comment_only.py）
```

### 步骤 1：调研目标文件

在动手之前全面了解目标文件：

1. 统计文件总行数、函数数量、类数量
2. 统计现有注释数量及语言（英文/中文/混合）：
   ```bash
   grep -c '^\s*#' <file>
   ```
3. 识别哪些函数/方法已有 docstring、哪些没有
4. 识别需要翻译的英文注释行：
   ```bash
   grep -n '^\s*#\s*[A-Z]' <file>
   ```
5. 区分**活跃注释**和**注释掉的代码**（后者保持原样，不翻译）

**输出**：明确以下数字——N 个函数需要 docstring，M 条英文注释需翻译，K 个段落需注释。

### 步骤 2：编写 docstring YAML 规范

YAML 规范文件格式：

```yaml
- file: path/to/target.py
  functions:
    - name: function_name          # 顶层函数
      docstring: |
        函数功能的中文描述。

        :param arg1: 参数说明
        :return: 返回值说明
    - name: ClassName.method_name  # 类方法（用 . 分隔）
      docstring: |
        方法功能的中文描述。
```

**关键规则**：
- 顶层必须是**列表**（以 `- file:` 开头），不能是字典
- docstring 使用 `|` 块标量，保持换行
- 若函数已有 docstring，工具会自动跳过（幂等）
- **建议使用 Python `yaml.dump()` 生成 YAML**，避免手写时的缩进/引号问题
- docstring 使用 reST 格式（`:param:`、`:return:`、`:raises:`）
- 不翻译参数名、变量名、类名（保持代码原名）

### 步骤 3：运行 add_docstring.py

```bash
python .github/skills/python-annotation-engineering/scripts/add_docstring.py --spec <yaml>
```

验收标准：
- 输出显示 "共添加 N 个 docstring"
- "已存在 docstring，跳过" 属于正常情况
- 报错 "规范文件顶层须为列表" → 检查 YAML 格式

### 步骤 4：添加文件头

文件头必须包含以下完整结构：

```python
# =============================================================================
# 功能描述：
#   一句话说明文件用途。
#
# 类与方法索引：
#   function_name                        (L行号)  — 一句话描述
#   ClassName                            (L行号)  — 类描述
#     method_name                        (L行号)  — 方法描述
#
# 更新日志：
#   YYYY-MM-DD  操作者  操作描述
#
# 当前维护者：操作者
# =============================================================================
```

**关键规则**：
- 「功能描述」「类与方法索引」「更新日志」「当前维护者」四块缺一不可
- 索引块由 `gen_index.py --write` 自动生成，**不要手写行号**
- 若文件无头部，先手动写功能描述 + 更新日志 + 维护者，再运行 gen_index.py

### 步骤 5：添加/翻译行内注释

三种操作：

**5a. 翻译现有英文注释**
- `# English comment` → `# 中文注释`
- **注释掉的代码**（`# print(x)`, `# old_var = ...`）保持原样，不翻译
- 若项目有术语表，参照术语表统一翻译

**5b. 添加段落注释（大函数分段）**
- 对超过 50 行的函数，在逻辑段之间添加段落注释
- 推荐格式：`# ── 步骤 N：描述 ──`

```python
    # ── 步骤 1：处理参数覆盖 ──
    overrides = parse_overrides(config)

    # ── 步骤 2：初始化数据库连接 ──
    db = connect(config.db_url)
```

**5c. 添加关键行尾注释**
- 仅注释**需要领域知识才能理解的行**，不要逐行注释

**批量操作**：对 >30 条注释的文件，建议编写 Python 脚本批量替换（`str.replace(old, new, 1)`），
而非逐条手动编辑。

### 步骤 6：更新索引并验证收敛

```bash
# 获取 skill 脚本路径（后续步骤复用）
SKILL_SCRIPTS=".github/skills/python-annotation-engineering/scripts"

# 第一遍：更新行号
python $SKILL_SCRIPTS/gen_index.py <file> --write

# 第二遍：索引本身改变行号，需再更新
python $SKILL_SCRIPTS/gen_index.py <file> --write

# 验证收敛
python $SKILL_SCRIPTS/check_index.py <file>
```

**关键规则**：
- gen_index.py 必须**逐文件**调用
- 至少运行 **2 遍**直到 check_index.py 输出 ✅
- 若 2 遍后仍不收敛，继续运行直到收敛

**安全护栏**：
- gen_index.py 仅在 `# ===` 分隔线包围的头部块内搜索和替换
- 若文件无 SP-CODE-2026-001 文件头，会打印警告并跳过（不会在文件开头误插索引）
- **运行 gen_index.py 后必须目视检查**：确认文件首行仍为 `# ===` 或 `# -*- coding` 而非裸的 `# 类与方法索引：`

### 步骤 7：等价性验证

```bash
# 从 git 提取原始文件（避免 BOM 问题，必须用 Python）
python -c "
import subprocess
data = subprocess.check_output(['git', 'show', 'HEAD:path/to/file.py'])
open('/tmp/original.py', 'wb').write(data)
"

# 运行验证
python $SKILL_SCRIPTS/verify_comment_only.py /tmp/original.py path/to/file.py
```

验收标准：`[OK]   文件名 — 代码等价，仅注释变更`

> **Windows 注意**：不要用 PowerShell 的 `Out-File` 导出 git 内容，会引入 BOM 导致哈希不匹配。
> 始终使用 Python `subprocess.check_output()` 以二进制方式提取。

## 提交规范

每个阶段/批次完成后整体提交：

```bash
git add <所有修改文件>
git commit -m "style: 为 <模块名> 添加中文注释" \
  -m "- 为 N 个函数添加中文 docstring" \
  -m "- 添加文件头（功能描述/索引/更新日志/维护者）" \
  -m "- 翻译 M 条英文注释为中文" \
  -m "- verify_comment_only.py 验证通过"
```

### 提交前检查清单

- [ ] 所有目标文件都有完整的文件头
- [ ] 所有函数/方法都有 docstring
- [ ] 所有英文活跃注释已翻译为中文
- [ ] `check_index.py` 输出 ✅
- [ ] `verify_comment_only.py` 对每个文件输出 `[OK]`

## 已知陷阱

| 陷阱 | 症状 | 解决方案 |
|------|------|---------|
| YAML 格式错误 | `规范文件顶层须为列表` | 用 Python `yaml.dump()` 生成 YAML |
| gen_index.py 批量调用 | 多文件参数只更新 1 个 | 必须逐文件循环调用 |
| gen_index.py 未收敛 | check_index.py 报行号不匹配 | 多跑几遍 `--write` || gen_index.py 头部块外插入 | 文件开头出现裸的 `# 类与方法索引：` 块，与 `# ===` 头部块内的索引重复 | **已修复**：现仅在 `# ===` 分隔线内搜索；无头部块时拒绝插入并打印警告。若已产生重复块，手动删除 `# ===` 外的索引行后重新运行 || PowerShell BOM | verify 报首行差异 `\ufeff` | 用 Python subprocess 提取 git 文件 |
| 注释掉的代码被翻译 | verify 报 FAIL | 仅翻译活跃注释，`# code` 保持原样 |
| 多处重复上下文 | replace_string_in_file 报多处匹配 | 增加上下文行数，或用行号定位脚本 |
