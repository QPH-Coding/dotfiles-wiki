# Neovim Knowledge Wiki — CLAUDE.md

这是 LLM 操作本 wiki 的配置文件。本文档描述 wiki 的结构、约定和操作流程。
你（LLM）是 wiki 的唯一维护者；用户负责提供源材料、引导探索、审阅结果。

---

## 1. Wiki 定位

本 wiki 专为以下目标设计：

- 系统整理 Neovim 官方文档、插件文档、社区文章等知识
- 形成结构化的持久知识库，随源材料积累持续增长
- **首要消费者是 AI**（包括你自己在下次会话中）：内容必须结构化、精确、无歧义，方便 AI 快速定位和引用

Wiki 不是通用笔记本。每张页面都应该回答一个明确的问题，而不是流水账式堆砌信息。

---

## 2. 目录结构

```
~/Documents/ObsidianNeovim/
├── CLAUDE.md                  ← 本文件
├── config/                    ← Neovim 配置源文件（部署到系统 nvim 目录）
├── scripts/                   ← 维护脚本
│   ├── subtrees.json          ← git subtree 配置（remote、prefix、branch）
│   ├── sync_docs.py           ← 拉取所有 subtree 最新文档
│   └── deploy_config.py       ← 将 config/ 部署到系统 nvim 目录
├── raw/                       ← 原始源材料（只读，LLM 不修改）
│   ├── docs/                  ← Neovim 官方文档（git subtree 维护）
│   ├── plugins/               ← 插件 README / 官方文档（git subtree 维护）
│   └── articles/              ← 博客文章、教程、讨论（手动存入）
└── wiki/                      ← LLM 维护的知识库
    ├── index.md               ← 总目录（每次 ingest 后更新）
    ├── log.md                 ← 操作日志（只追加）
    ├── overview.md            ← Neovim 生态全景概述
    ├── plugins/               ← 插件页（每个插件一个文件）
    ├── concepts/              ← 概念页（LSP、Treesitter、Keymap 等）
    ├── comparisons/           ← 对比与方案选型
    ├── my-config/             ← 我的配置全景小结
    └── slides/                ← Marp 幻灯片
```

**规则**：
- `raw/` 目录内容只读，LLM 读取但不修改
- `wiki/` 目录由 LLM 全权维护：创建、更新、保持一致性
- 页面文件名全小写 kebab-case，如 `lazy-nvim.md`、`lsp-basics.md`

---

## 3. 页面类型与模板

### 3.1 插件页（`wiki/plugins/`）

一个插件对应一个文件，文件名为插件名（kebab-case）。

```markdown
---
type: plugin
name: <插件名，保留原始大小写>
category: <分类，如 package-manager / lsp / ui / navigation / editor>
repo: <GitHub repo，如 folke/lazy.nvim>
sources: [<raw/ 下的源文件路径>]
last-updated: <YYYY-MM-DD>
---

# <插件名>

> <一句话：这个插件解决什么问题>

## 定位

<2-3句：插件的核心功能与设计哲学>

## 安装

```lua
-- lazy.nvim 配置示例
{ "<repo>", opts = {} }
```

## 核心配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| ...    | ...  | ...    | ...  |

## 常见用法

<最常用的 2-5 个场景，每个场景附代码片段>

## 依赖与集成

<与哪些插件有依赖关系或常见搭配>

## 已知问题 / 注意事项

<坑、breaking change、版本兼容性等>

## 参考

- [[index]] 返回总目录
- <内链到相关插件页或概念页>
```

---

### 3.2 概念页（`wiki/concepts/`）

```markdown
---
type: concept
name: <概念名>
sources: [<raw/ 下的源文件路径>]
last-updated: <YYYY-MM-DD>
---

# <概念名>

> <一句话定义>

## 是什么

<概念本身的解释，不依赖 Neovim>

## 在 Neovim 中的实现

<Neovim 如何实现或使用这个概念>

## 相关插件

<链接到实现这一概念的插件页>

## 配置要点

<配置时的关键注意点，附代码示例>

## 参考

- [[index]]
- <内链>
```

---

### 3.3 对比 / 方案选型页（`wiki/comparisons/`）

```markdown
---
type: comparison
topic: <对比主题，如 "自动补全插件选型">
candidates: [<插件1>, <插件2>, ...]
recommendation: <推荐选项>
last-updated: <YYYY-MM-DD>
---

# <对比主题>

## 候选方案

| 维度     | <插件1> | <插件2> | <插件3> |
|----------|---------|---------|---------|
| 维护状态 | ...     | ...     | ...     |
| 配置复杂度 | ...   | ...     | ...     |
| 性能     | ...     | ...     | ...     |
| 生态兼容 | ...     | ...     | ...     |
| 文档质量 | ...     | ...     | ...     |

## 推荐

**推荐：<插件名>**

理由：<具体原因>

适用例外场景：<什么情况下选其他方案>

## 参考

- [[index]]
- <内链到各插件页>
```

---

### 3.4 我的配置全景小结（`wiki/my-config/`）

```markdown
---
type: my-config
last-updated: <YYYY-MM-DD>
---

# 我的 Neovim 配置全景

## 整体架构

<描述配置的组织方式，如目录结构、加载顺序>

## 插件选择一览

| 模块         | 选用插件       | 备注 |
|--------------|----------------|------|
| 包管理       | lazy.nvim      | ...  |
| LSP          | ...            | ...  |
| 补全         | ...            | ...  |
| 文件树       | ...            | ...  |
| 模糊搜索     | ...            | ...  |
| 状态栏       | ...            | ...  |
| 主题         | ...            | ...  |

## 关键配置决策

<每个重要选择背后的理由>

## 待解决问题

- [ ] <问题描述>

## 参考

- [[index]]
```

---

## 4. 操作流程

### 4.1 Ingest（摄入新源材料）

**触发**：用户说「处理这个文件」或「ingest raw/...」

**流程（半自动）**：
1. 读取源文件（`raw/` 下）
2. 提取关键信息，向用户汇报：
   - 这是什么内容
   - 将影响哪些 wiki 页面（新建/更新）
   - 有无与现有 wiki 内容矛盾的地方
3. **等待用户确认或调整方向**
4. 执行写入：
   - 创建或更新相关插件页/概念页
   - 如涉及方案选型，更新或创建对比页
   - 如涉及我的配置，更新 `my-config/`
   - 更新 `wiki/index.md`
   - 追加 `wiki/log.md` 条目
5. 汇报本次修改了哪些文件

**原则**：一次 ingest 可能触及 5-15 个 wiki 页面。宁可多更新不要漏更新。

---

### 4.2 Query（查询）

**触发**：用户提问 Neovim 相关问题

**流程**：
1. 读取 `wiki/index.md`，找到相关页面
2. 读取相关页面，综合信息
3. 给出带内链引用的回答
4. 如果回答本身有价值（如一次详细的方案分析），征询用户是否要将其存入 wiki

---

### 4.3 Lint（健康检查）

**触发**：用户说「lint wiki」或「检查 wiki 质量」

**检查项**：
- 孤儿页面（没有被任何页面链接的页）
- 内容矛盾（不同页面对同一问题说法不一）
- 缺失的概念页（被多次提及但没有独立页面）
- 过时的信息（`last-updated` 超过 6 个月）
- index.md 中有但实际不存在的页面
- 实际存在但 index.md 未收录的页面

**输出**：问题清单，附修复建议；严重问题直接修复，疑问征询用户。

---

## 5. 约定规则

### 5.1 语言

- 插件名、配置 key、API 名称、代码：保持英文原文
- 概念解释、分析、决策理由：中文
- 页面标题：如有通用中文译名则中英并列，如无则直接用英文

### 5.2 内链格式

- 使用 Obsidian 双链格式：`[[文件名]]` 或 `[[文件名|显示文字]]`
- 链接路径相对于 wiki 根目录，不带扩展名
- 示例：`[[plugins/lazy-nvim]]`、`[[concepts/lsp-basics|LSP 基础]]`

### 5.3 YAML Frontmatter

每张页面必须有 frontmatter，至少包含 `type` 和 `last-updated`。
`type` 取值：`plugin` / `concept` / `comparison` / `my-config` / `overview`

### 5.4 代码块

所有 Lua 代码块标注语言 ` ```lua `，Shell 命令标注 ` ```bash `。

---

## 6. index.md 维护规则

`wiki/index.md` 是 LLM 查询时的导航入口，每次 ingest 后必须更新。

格式：
```markdown
# Wiki 总目录

_最后更新：YYYY-MM-DD_

## 插件页

| 页面 | 分类 | 一行摘要 |
|------|------|----------|
| [[plugins/lazy-nvim]] | package-manager | 现代 Neovim 插件管理器 |
| ...  | ...  | ... |

## 概念页

| 页面 | 一行摘要 |
|------|----------|
| [[concepts/lsp-basics]] | Language Server Protocol 在 Neovim 中的实现 |
| ... | ... |

## 对比 / 选型

| 页面 | 主题 | 推荐 |
|------|------|------|
| ...  | ...  | ...  |

## 我的配置

- [[my-config/overview]] — 配置全景小结

## 概览

- [[overview]] — Neovim 生态全景
```

---

## 7. log.md 维护规则

`wiki/log.md` 只追加，不修改历史记录。

每条条目格式：
```
## [YYYY-MM-DD] <操作类型> | <标题>

- 操作：ingest / query / lint / update
- 涉及文件：<列表>
- 摘要：<一两句说明做了什么>
```

查询最近 5 条的方式：`grep "^## \[" wiki/log.md | tail -5`

---

## 8. Marp 幻灯片约定（`wiki/slides/`）

当用户请求生成幻灯片时，文件存入 `wiki/slides/`，使用 Marp frontmatter：

```markdown
---
marp: true
theme: default
paginate: true
---

# 标题

---

## 内容页
```

---

## 9. 首次初始化检查

如果 `wiki/` 目录为空，在第一次 ingest 前先创建以下骨架文件：
- `wiki/index.md`（空目录结构）
- `wiki/log.md`（空日志，带标题）
- `wiki/overview.md`（占位，待第一批源材料后填充）
