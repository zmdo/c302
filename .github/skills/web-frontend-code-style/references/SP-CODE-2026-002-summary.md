# SP-CODE-2026-002 Web 前端代码规范 · 摘要

> 文档编号：SP-CODE-2026-002  
> 适用范围：Vue 3 + Vite + Composition API 前端项目

---

## 1 文件头注释

所有 `.vue`、`.js`、`.ts` 文件**必须**包含标准头注释块：

```js
/**
 * =============================================================================
 * 功能描述：
 *   <模块职责，2-5 行>
 *
 * 更新日志：
 *   YYYY-MM-DD  维护者  改动内容
 *
 * 当前维护者：<姓名>
 * =============================================================================
 */
```

- `.vue` 文件中置于 `<script setup>` 内、import 之前
- `.js`/`.ts` 文件中置于文件顶部

## 2 SFC 结构

```
<template> → <script setup> → <style scoped>
```

`<script setup>` 内部顺序：

1. 文件头注释
2. import（Vue 核心 → 第三方 → 内部）
3. inject / provide
4. defineProps / defineEmits
5. ref / reactive / computed
6. 函数
7. 生命周期钩子
8. defineExpose

## 3 命名

| 类型 | 风格 | 示例 |
|------|------|------|
| 组件文件名 | PascalCase | `UserCard.vue` |
| JS/TS 文件名 | camelCase | `api.js` |
| 组件标签 | PascalCase | `<UserCard />` |
| prop / emit | camelCase | `:modelValue`, `@update` |
| 变量 / 函数 | camelCase | `loadData()` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY` |
| CSS 类 | kebab-case / BEM | `.card-header__title` |
| 路由路径与名称 | kebab-case | `/project-detail` |

## 4 模板规范

- `v-for` + `:key` 必须配对
- `v-if` 与 `v-for` 禁止同元素
- 禁止复杂表达式（嵌套三目、链式调用），改用 computed / 函数
- `@` 代替 `v-on:`，`:` 代替 `v-bind:`
- 自闭合组件：`<Comp />`
- ≤3 属性可同行，>3 属性每行一个

## 5 路由

- **懒加载**：`component: () => import('../views/Foo.vue')`
- 路由需设 `meta: { title: '...' }`
- 路由名称 kebab-case

## 6 样式

- 组件样式使用 `<style scoped>`
- 禁止布局相关的内联 style（CSS 变量引用除外）
- 类名 kebab-case / BEM
- 颜色、尺寸使用 CSS 变量
- 禁止 `!important`（覆盖第三方库除外）

## 7 字符串与格式

- JS/TS：单引号 `'`
- HTML 属性：双引号 `"`
- 缩进：2 空格
- 行宽：≤120 字符
- 不加分号（Prettier）

## 8 JSDoc

导出 & 工具函数必须加 JSDoc：

```js
/**
 * 描述
 * @param {string} url - 说明
 * @returns {Promise<any>} 结果
 */
```

## 9 禁止项

| 禁止 | 替代 |
|------|------|
| `console.log/error` | toast / 统一错误处理 |
| Options API | Composition API + `<script setup>` |
| `this` | 直接引用响应式变量 |
| `var` | `const` / `let` |
| `==` / `!=` | `===` / `!==` |
| CSS `!important` | 提升选择器优先级 |
