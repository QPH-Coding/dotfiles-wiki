---
type: tool
name: Everforest
category: nvim-plugin
repo: sainnhe/everforest
sources: ["raw/doc/neovim/plugin/everforest/everforest.txt"]
last-updated: 2026-04-16
---

# Everforest

> 以绿色为基调、强调柔和对比度的 Vim / Neovim 主题，适合长时间编码

## 定位

Everforest 是一个偏暖、偏柔和的配色方案。官方文档强调它针对 true color 场景设计，除了基础语法高亮之外，还覆盖了 Tree-sitter、语义高亮和常见插件主题。

## 核心特性

- 支持深色 / 浅色背景
- 对比度可选 `hard`、`medium`、`soft`
- 提供 `lualine.nvim` 主题
- 对 Tree-sitter、LSP 诊断和常见插件有额外高亮适配
- 提供 `better_performance` 模式，减少主题加载时的额外开销

## 当前仓库中的接入方式

当前仓库把 Everforest 作为默认主题，配置拆成两部分：

- `dotfiles/nvim/init.lua` 通过 `vim.pack.add()` 安装 `https://github.com/sainnhe/everforest`
- `dotfiles/nvim/lua/plugins/everforest.lua` 在 `colorscheme everforest` 之前设置主题选项并立即应用主题
- `dotfiles/nvim/lua/plugins/lualine.lua` 显式使用 `theme = "everforest"`

对应的 Lua 片段如下：

```lua
vim.o.background = "dark"

vim.g.everforest_background = "medium"
vim.g.everforest_better_performance = 1
vim.g.everforest_show_eob = 0

vim.cmd.colorscheme("everforest")
```

## 关键配置项

| 配置项 | 可选值 | 当前仓库用法 | 说明 |
|--------|--------|--------------|------|
| `g:everforest_background` | `hard` / `medium` / `soft` | `medium` | 控制整体对比度 |
| `g:everforest_enable_italic` | `0` / `1` | 未启用 | 只有字体支持斜体时才值得打开 |
| `g:everforest_show_eob` | `0` / `1` | `0` | 是否显示 `EndOfBuffer` 高亮 |
| `g:everforest_better_performance` | `0` / `1` | `1` | 把部分高亮逻辑延后加载，以换取更短启动耗时 |

## 使用注意

- 需要启用 `termguicolors`，否则颜色效果会明显偏差
- 主题配置项必须放在 `colorscheme everforest` 之前
- 官方 FAQ 提到，若使用原生 `pack` 目录手工装到 `pack/*` 下，某些场景需要先 `packadd! everforest`
- 当前仓库通过 `vim.pack.add(..., { load = true })` 立即加载插件，所以没有额外写 `packadd!`

## 参考

- [[index]] 返回总目录
- [[tools/neovim]] Neovim 主工具页
- [[tools/vim-pack]] vim.pack 说明
- [[my-config/overview]] 当前仓库的 Neovim 配置概览