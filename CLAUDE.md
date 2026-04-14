# DotFile-Wiki — CLAUDE.md

这是 LLM 操作本仓库的配置文件。本文档描述仓库的结构、约定和操作流程。
你（LLM）是 wiki 的唯一维护者；用户负责提供源材料、引导探索、审阅结果。

---

## 1. 仓库定位

本仓库服务于**开发环境配置管理与知识沉淀**，覆盖所有开发工具（Neovim、Zsh、WezTerm、Git、Tmux 等）。

两大核心功能：

1. **Dotfiles 管理** — 将各工具的配置文件统一存储并一键部署到系统目录
2. **Wiki 知识库** — 系统整理工具文档、配置决策、操作流程，形成可持续增长的知识资产

**首要消费者是 AI**（包括你自己在下次会话中）：内容必须结构化、精确、无歧义，方便 AI 快速定位和引用。

Wiki 不是通用笔记本。每张页面都应该回答一个明确的问题，而不是流水账式堆砌信息。

---

## 2. 目录结构

```
~/Documents/DotFile-Wiki/          ← 仓库根目录（原名 ObsidianNeovim）
├── CLAUDE.md                      ← 本文件
├── dotfiles/                      ← 各工具的配置源文件
│   └── nvim/                      ← Neovim 配置（部署到系统 nvim 目录）
├── scripts/                       ← 维护脚本
│   ├── targets.json               ← 工具部署路径配置（跨平台）
│   ├── deploy.py                  ← 部署 dotfiles/<tool>/ 到系统目录
│   └── sync_docs.py               ← 下载 raw/ 目录中的外部文档
├── raw/                           ← 原始源材料（只读，LLM 不修改）
│   ├── manifest.json              ← 文档来源清单（版本/路径/来源，提交到 git）
│   ├── docs/                      ← 官方文档（sync_docs.py 下载，gitignore）
│   ├── tools/                     ← 工具文档（sync_docs.py 下载，gitignore）
│   └── articles/                  ← 文章/博客（sync_docs.py 下载，gitignore）
└── wiki/                          ← LLM 维护的知识库
    ├── index.md                   ← 总目录（每次 ingest 后更新）
    ├── log.md                     ← 操作日志（只追加）
    ├── overview.md                ← 开发环境生态全景概述
    ├── tools/                     ← 工具页（每个工具/插件一个文件）
    ├── systems/                   ← 系统配置页（zsh、tmux、wezterm、git 等）
    ├── workflows/                 ← 跨工具工作流与环境搭建指南
    ├── concepts/                  ← 概念页（LSP、Treesitter、Shell 等）
    ├── comparisons/               ← 对比与方案选型
    ├── my-config/                 ← 我的配置全景小结
    └── slides/                    ← Marp 幻灯片
```

**规则**：
- `raw/` 目录内容只读，LLM 读取但不修改
- `wiki/` 目录由 LLM 全权维护：创建、更新、保持一致性
- `dotfiles/` 由用户维护，LLM 可读取用于生成 my-config 页面
- 页面文件名全小写 kebab-case，如 `lazy-nvim.md`、`lsp-basics.md`、`zsh-config.md`

---

## 3. 脚本说明

### 3.1 部署配置（deploy.py）

```bash
# 部署单个工具
python scripts/deploy.py nvim

# 部署所有工具
python scripts/deploy.py all

# 预览（不实际写入）
python scripts/deploy.py nvim --dry-run
python scripts/deploy.py all --dry-run
```

部署路径由 `scripts/targets.json` 配置，源目录为 `dotfiles/<tool>/`。

### 3.2 同步文档（sync_docs.py）

```bash
# 同步所有来源
python scripts/sync_docs.py

# 只同步单个来源
python scripts/sync_docs.py lazy-nvim

# 更新某个来源的 ref（tag / branch / SHA）并立即同步
python scripts/sync_docs.py --update lazy-nvim v11.17.0

# 查看所有来源的当前版本与同步状态
python scripts/sync_docs.py --list
```

来源清单见 `raw/manifest.json`（提交到 git）；下载内容在 `raw/docs/`、`raw/tools/`、`raw/articles/`（已 gitignore，按需重新下载）。

---

## 4. 页面类型与模板

### 4.1 工具页（`wiki/tools/`）

涵盖 Neovim 插件、命令行工具、开发辅助工具等。一个工具对应一个文件。

```markdown
---
type: tool
name: <工具名，保留原始大小写>
category: <分类，如 nvim-plugin / cli / package-manager / lsp / ui>
repo: <GitHub repo，如 folke/lazy.nvim>
sources: [<raw/ 下的源文件路径>]
last-updated: <YYYY-MM-DD>
---

# <工具名>

> <一句话：这个工具解决什么问题>

## 定位

<2-3句：核心功能与设计哲学>

## 安装

```bash / lua
# 安装命令或配置示例
```

## 核心配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|

## 常见用法

<最常用的 2-5 个场景，每个场景附代码片段>

## 依赖与集成

<与哪些工具有依赖关系或常见搭配>

## 已知问题 / 注意事项

<坑、breaking change、版本兼容性等>

## 参考

- [[index]] 返回总目录
- <内链到相关工具页或概念页>
```

---

### 4.2 系统配置页（`wiki/systems/`）

用于 OS 级别的工具配置：shell（zsh/bash）、终端（wezterm）、版本控制（git）、会话管理（tmux）等。

```markdown
---
type: system
name: <工具名>
category: <分类，如 shell / terminal / vcs / session-manager>
sources: [<raw/ 下的源文件路径>]
last-updated: <YYYY-MM-DD>
---

# <工具名>

> <一句话定位>

## 配置文件位置

| 系统 | 路径 |
|------|------|
| Windows | ... |
| macOS/Linux | ... |

## 核心配置

<关键配置项说明，附代码示例>

## 我的配置要点

<个人配置中的关键决策和原因>

## 常见任务

<日常使用中最高频的操作>

## 参考

- [[index]]
- <内链>
```

---

### 4.3 工作流页（`wiki/workflows/`）

跨工具的操作流程和环境搭建指南。

```markdown
---
type: workflow
name: <工作流名称>
tools: [<涉及的工具列表>]
sources: [<raw/ 下的源文件路径>]
last-updated: <YYYY-MM-DD>
---

# <工作流名称>

> <一句话：这个工作流解决什么场景>

## 前提条件

<需要哪些工具/配置已就绪>

## 步骤

1. <步骤一>
2. <步骤二>
...

## 完整示例

<端到端的操作示例>

## 参考

- [[index]]
- <内链到相关工具页>
```

---

### 4.4 概念页（`wiki/concepts/`）

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

<概念本身的解释>

## 在开发环境中的应用

<具体工具如何实现或使用这个概念>

## 相关工具

<链接到实现这一概念的工具页>

## 配置要点

<配置时的关键注意点，附代码示例>

## 参考

- [[index]]
- <内链>
```

---

### 4.5 对比 / 方案选型页（`wiki/comparisons/`）

```markdown
---
type: comparison
topic: <对比主题，如 "终端模拟器选型">
candidates: [<工具1>, <工具2>, ...]
recommendation: <推荐选项>
last-updated: <YYYY-MM-DD>
---

# <对比主题>

## 候选方案

| 维度       | <工具1> | <工具2> | <工具3> |
|------------|---------|---------|---------|
| 维护状态   | ...     | ...     | ...     |
| 配置复杂度 | ...     | ...     | ...     |
| 性能       | ...     | ...     | ...     |
| 跨平台     | ...     | ...     | ...     |
| 文档质量   | ...     | ...     | ...     |

## 推荐

**推荐：<工具名>**

理由：<具体原因>

适用例外场景：<什么情况下选其他方案>

## 参考

- [[index]]
- <内链到各工具页>
```

---

### 4.6 我的配置全景小结（`wiki/my-config/`）

```markdown
---
type: my-config
last-updated: <YYYY-MM-DD>
---

# 我的开发环境配置全景

## 整体架构

<描述配置的整体组织方式>

## 工具选择一览

| 模块       | 选用工具     | 备注 |
|------------|--------------|------|
| 编辑器     | Neovim       | ...  |
| 终端       | WezTerm      | ...  |
| Shell      | Zsh          | ...  |
| 版本控制   | Git          | ...  |
| 会话管理   | Tmux         | ...  |

## 关键配置决策

<每个重要选择背后的理由>

## 待解决问题

- [ ] <问题描述>

## 参考

- [[index]]
```

---

## 5. 操作流程

### 5.1 Ingest（摄入新源材料）

**触发**：用户说「处理这个文件」或「ingest raw/...」

**流程（半自动）**：
1. 读取源文件（`raw/` 下）
2. 提取关键信息，向用户汇报：
   - 这是什么内容（工具文档 / 概念 / 配置参考）
   - 将影响哪些 wiki 页面（新建/更新）
   - 有无与现有 wiki 内容矛盾的地方
3. **等待用户确认或调整方向**
4. 执行写入：
   - 创建或更新相关工具页 / 系统页 / 概念页
   - 如涉及方案选型，更新或创建对比页
   - 如涉及工作流，更新或创建工作流页
   - 如涉及我的配置，更新 `my-config/`
   - 更新 `wiki/index.md`
   - 追加 `wiki/log.md` 条目
5. 汇报本次修改了哪些文件

**原则**：一次 ingest 可能触及多个 wiki 页面。宁可多更新不要漏更新。

---

### 5.2 Query（查询）

**触发**：用户提问开发环境相关问题

**流程**：
1. 读取 `wiki/index.md`，找到相关页面
2. 读取相关页面，综合信息
3. 给出带内链引用的回答
4. 如果回答本身有价值（如一次详细的方案分析），征询用户是否要将其存入 wiki

---

### 5.3 Lint（健康检查）

**触发**：用户说「lint wiki」或「检查 wiki 质量」

**检查项**：
- 孤儿页面（没有被任何页面链接的页）
- 内容矛盾（不同页面对同一问题说法不一）
- 缺失的页面（被多次提及但没有独立页面）
- 过时的信息（`last-updated` 超过 6 个月）
- index.md 中有但实际不存在的页面
- 实际存在但 index.md 未收录的页面

**输出**：问题清单，附修复建议；严重问题直接修复，疑问征询用户。

---

## 6. 约定规则

### 6.1 语言

- 工具名、配置 key、API 名称、代码：保持英文原文
- 概念解释、分析、决策理由：中文
- 页面标题：如有通用中文译名则中英并列，如无则直接用英文

### 6.2 内链格式

- 使用 Obsidian 双链格式：`[[文件名]]` 或 `[[文件名|显示文字]]`
- 链接路径相对于 wiki 根目录，不带扩展名
- 示例：`[[tools/lazy-nvim]]`、`[[systems/zsh]]`、`[[concepts/lsp-basics|LSP 基础]]`

### 6.3 YAML Frontmatter

每张页面必须有 frontmatter，至少包含 `type` 和 `last-updated`。
`type` 取值：`tool` / `system` / `workflow` / `concept` / `comparison` / `my-config` / `overview`

### 6.4 代码块

Lua 代码块标注 ` ```lua `，Shell 命令标注 ` ```bash `，其余语言同理。

---

## 7. index.md 维护规则

`wiki/index.md` 是 LLM 查询时的导航入口，每次 ingest 后必须更新。

格式：
```markdown
# Wiki 总目录

_最后更新：YYYY-MM-DD_

## 工具页（Tools）

| 页面 | 分类 | 一行摘要 |
|------|------|----------|
| [[tools/lazy-nvim]] | nvim-plugin | 现代 Neovim 插件管理器 |
| ... | ... | ... |

## 系统配置页（Systems）

| 页面 | 一行摘要 |
|------|----------|
| [[systems/zsh]] | Zsh 配置与插件管理 |
| ... | ... |

## 工作流（Workflows）

| 页面 | 一行摘要 |
|------|----------|
| [[workflows/new-machine-setup]] | 新机器开发环境一键搭建流程 |
| ... | ... |

## 概念页（Concepts）

| 页面 | 一行摘要 |
|------|----------|
| [[concepts/lsp-basics]] | Language Server Protocol 在编辑器中的实现 |
| ... | ... |

## 对比 / 选型

| 页面 | 主题 | 推荐 |
|------|------|------|
| ... | ... | ... |

## 我的配置

- [[my-config/overview]] — 配置全景小结

## 概览

- [[overview]] — 开发环境生态全景
```

---

## 8. log.md 维护规则

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

## 9. Marp 幻灯片约定（`wiki/slides/`）

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

## 10. 首次初始化检查

如果 `wiki/` 目录为空，在第一次 ingest 前先创建以下骨架文件：
- `wiki/index.md`（含 Tools / Systems / Workflows / Concepts / Comparisons / My Config / Overview 各节）
- `wiki/log.md`（空日志，带标题）
- `wiki/overview.md`（占位，待第一批源材料后填充）
