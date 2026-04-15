---
name: web-frontend-code-style
description: "Review and enforce Vue 3 + JavaScript frontend code against SP-CODE-2026-002 coding standard. Check file headers (功能描述/更新日志/当前维护者), JSDoc comments, mandatory inline comments, script setup block ordering, naming conventions, template best practices, scoped styles, forbidden patterns, and unit test coverage. Use when the user asks to review frontend code style, enforce coding standards, check Vue component compliance, or write new frontend files. Every exported function and Vue component MUST have comments and corresponding unit tests."
license: MIT
compatibility: "c302（C. elegans 神经网络建模框架，OpenWorm 子项目）。当前为纯 Python 项目，如需前端则使用 Vue 3 + Vite，Composition API with <script setup>。"
metadata:
  author: Copilot
  version: "1.0"
allowed-tools: Read Edit Terminal
---

# Web Frontend Code Style Enforcement

## When to Use

- User asks to review Vue / JS / CSS code for style compliance
- User asks to check or enforce coding standards on frontend files
- User is writing new Vue components and needs to follow project conventions
- User asks to refactor frontend code to match SP-CODE-2026-002
- After completing a frontend feature, to verify compliance

## Core Standard: SP-CODE-2026-002

The full coding standard is stored at `references/SP-CODE-2026-002-summary.md`. Load it for detailed rules.

Key rules summarized below:

### File Header (Required)

Every `.vue`, `.js`, `.ts` source file must start with a header comment block:

```js
/**
 * =============================================================================
 * 功能描述：
 *   简要描述文件职责与使用场景。
 *
 * 更新日志：
 *   YYYY-MM-DD  维护者  改动内容
 *
 * 当前维护者：维护者名称
 * =============================================================================
 */
```

- 在 `.vue` 文件中，该头注释位于 `<script setup>` 标签内的第一行（import 之前）。
- 在 `.js` / `.ts` 文件中，位于文件最顶部。

### Vue 单文件组件 (SFC) 结构

块顺序必须为：`<template>` → `<script setup>` → `<style scoped>`

`<script setup>` 内部声明顺序：
1. 文件头注释
2. `import` 语句（先 Vue 核心，再第三方，再内部模块）
3. `inject` / `provide`
4. `defineProps` / `defineEmits`
5. `ref` / `reactive` / `computed`
6. 函数定义
7. 生命周期钩子（`onMounted` 等）
8. `defineExpose`

### 命名规范

| 类型 | 风格 | 示例 |
|------|------|------|
| 组件文件 | `PascalCase.vue` | `DataSliceConfig.vue` |
| JS/TS 文件 | `camelCase.js` | `api.js`, `router.js` |
| 组件标签 | `PascalCase` | `<DataSliceConfig />` |
| 事件名 | `camelCase` | `@updateValue` |
| prop | `camelCase` | `:modelValue` |
| 变量/函数 | `camelCase` | `loadData()` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_PAGE_SIZE` |
| CSS 类名 | `kebab-case` + BEM | `.card-header__title` |
| 路由路径 | `kebab-case` | `/project-detail` |
| 路由名 | `kebab-case` | `project-detail` |

### 模板规范

- `v-for` 必须配合 `:key`
- `v-if` 与 `v-for` 不得在同一元素上使用
- 模板中禁止复杂的 JS 表达式（三目嵌套、链式调用），应提取为 `computed` 或函数
- HTML 属性使用 **双引号**
- 自闭合无内容组件：`<MyComp />`
- 属性换行规则：≤3 个属性可同行；>3 个属性每行一个
- 事件绑定使用 `@` 而非 `v-on:`
- 动态绑定使用 `:` 而非 `v-bind:`

### 路由规范

- 使用**懒加载**（动态 import）：`component: () => import('../views/Foo.vue')`
- 每个路由必须设置 `meta.title`
- 路由名称使用 `kebab-case`

### 样式规范

- 组件样式使用 `<style scoped>`（全局样式除外）
- 禁止在模板中使用内联 `style` 属性设置布局/间距（应使用 CSS 类）
- CSS 类名使用 `kebab-case`，推荐 BEM 命名法
- 颜色、尺寸等通过 CSS 变量统一管理
- 禁止 `!important`（除非覆盖第三方库样式）

### 字符串与格式

- JS/TS 字符串使用**单引号** `'`
- 模板字符串使用反引号
- HTML 属性使用**双引号** `"`
- 缩进：**2 空格**
- 行宽上限：**120 字符**
- 语句末尾**不加分号**（由 Prettier 统一处理）

### JSDoc 注释

所有导出的函数、工具函数必须添加 JSDoc 注释：

```js
/**
 * 发送 API 请求
 * @param {string} url - 请求路径
 * @param {string} [method='GET'] - HTTP 方法
 * @param {Object} [data] - 请求体数据
 * @returns {Promise<any>} 响应数据
 */
export async function api(url, method = 'GET', data) { ... }
```

### 行内注释（强制）

行内注释是**强制性要求**，不可省略。每一段逻辑都必须附带注释。

- **函数/方法**：除 JSDoc 外，函数体内每段关键逻辑必须有行内注释说明目的
- **条件分支**：`if/else` 分支必须注释说明分支条件的业务含义
- **循环**：`for/while` 循环必须注释说明遍历目的
- **异步操作**：`await` 调用必须注释说明异步操作的用途
- **复杂表达式**：`computed`、三元运算、链式调用等必须附注释
- **watch / 生命周期钩子**：必须注释说明监听/挂载的用途
- 注释使用**中文**，关键词用英文（`TODO`、`FIXME` 等）
- Inline comments: 2 spaces before `//`, 1 space after
- 解释 **why**，而非 **what**
- **缺少注释视为不合规**，与缺少 JSDoc 同等严重

### 禁止项

- 禁止 `console.log` / `console.error` — 在 catch 块中用 toast 或统一错误处理
- 禁止 Options API（`data()`, `methods`, `computed` 写法）
- 禁止 `this` 关键字（Composition API 不需要）
- 禁止 `var` — 使用 `const` / `let`
- 禁止 `==` / `!=` — 使用 `===` / `!==`
- 禁止无意义的 `else`（提前 return）
- 禁止 CSS `!important`

### 单元测试（强制）

单元测试是**强制性要求**，每个前端模块必须有对应的测试文件。

- **测试框架**：使用 `Vitest` + `@vue/test-utils`
- **测试文件命名**：
  - Vue 组件：`{ComponentName}.test.js`，放在同级 `__tests__/` 目录下
  - JS 工具模块：`{moduleName}.test.js`，放在同级 `__tests__/` 目录下
- **测试覆盖要求**：
  - 每个导出函数/工具函数至少 1 个正向测试用例
  - 每个导出函数/工具函数至少 1 个异常/边界测试用例
  - Vue 组件至少测试：渲染、props 传入、关键交互事件
- **测试命名**：`describe('{ComponentName}')` + `it('should {behavior}')` 或 `test('{scenario}', ...)`
- **新增/修改代码时**：必须同步新增/更新对应的单元测试
- **无测试文件视为不合规**，与缺少 JSDoc 同等严重

示例结构：

```
components/
  MyComponent.vue
  __tests__/
    MyComponent.test.js
utils/
  format.js
  __tests__/
    format.test.js
```

示例测试：

```js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '../MyComponent.vue'

describe('MyComponent', () => {
  it('should render correctly', () => {
    // 验证组件可以正常渲染
    const wrapper = mount(MyComponent)
    expect(wrapper.exists()).toBe(true)
  })

  it('should emit update event on click', async () => {
    // 点击按钮后应触发 update 事件
    const wrapper = mount(MyComponent)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('update')).toBeTruthy()
  })
})
```

## Workflow

### Step 1: Identify Target Files

Determine which frontend files need checking — `.vue`, `.js`, `.ts`, `.css` 文件。

### Step 2: Check Each File

逐文件检查以下项目：
1. 文件头注释是否存在且包含功能描述、更新日志、当前维护者
2. SFC 块顺序是否正确（template → script setup → style scoped）
3. script setup 内部声明顺序
4. 命名规范
5. 模板是否有 v-if + v-for 同元素、复杂表达式
6. 路由是否使用懒加载及 meta.title
7. 是否存在 console.log / console.error
8. 样式是否有 scoped、是否滥用内联 style

### Step 3: Fix Issues

Apply fixes following the standard:
- Missing file header → Add standard header block in `<script setup>` (for .vue) or file top (for .js)
- `console.log/error` → Remove or replace with toast/error handler
- Eager route imports → Convert to `() => import(...)`
- Missing `meta.title` → Add to route definitions
- **Missing comments** → Add inline comments for all key logic blocks
- **Missing unit tests** → Create `__tests__/{name}.test.js` with render + interaction tests

### Step 4: Verify Unit Tests

Run `vitest` on the corresponding test files to ensure tests pass:

```bash
npx vitest run __tests__/{name}.test.js
```

### Step 5: Re-check

Re-read each modified file to confirm all issues are resolved.

## Gotchas

- 当前项目使用 `.js` 而非 `.ts`，TypeScript 相关规则可暂缓实施
- 全局样式集中在 `main.css`，组件无 `<style scoped>` 是当前设计选择，不强制要求每个组件都有 scoped 样式 — 但新组件应尽量使用 scoped
- 内联 style 中使用 CSS 变量（如 `color:var(--text-muted)`）属于可接受范围
- `defineProps` 使用运行时对象形式在 JS 项目中是合理的（TypeScript 项目应使用泛型形式）
- **行内注释是强制的**：没有注释的函数体/逻辑块视为不合规，即使逻辑简单也要注释说明意图
- **单元测试是强制的**：每个新增/修改的前端模块必须有对应 `__tests__/*.test.js`，没有测试不可提交
- 测试文件本身也必须遵循 JSDoc 和注释规范
