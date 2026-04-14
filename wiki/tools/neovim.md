---
type: tool
name: Neovim
category: editor
repo: neovim/neovim
sources: ["raw/doc/neovim/doc/nvim.txt", "raw/doc/neovim/doc/lua-guide.txt", "raw/doc/neovim/doc/options.txt"]
last-updated: 2026-04-14
---

# Neovim

> 现代、可扩展的 Vim 编辑器，支持 Lua 配置和 LSP 集成

## 定位

Neovim 是基于 Vim 的现代编辑器，专注于可扩展性和现代开发工作流。它提供了更好的 API、Lua 原生支持、内置 LSP 客户端和异步处理能力。

## 核心特性

- **Lua 原生配置**：支持 Lua 作为一等配置语言
- **LSP 集成**：内置 Language Server Protocol 客户端
- **异步处理**：非阻塞的插件和操作
- **现代 API**：改进的扩展性和集成能力
- **跨平台**：支持 Windows、macOS、Linux

## 安装配置

### 基本配置结构

```lua
-- ~/.config/nvim/init.lua
vim.opt.number = true           -- 显示行号
vim.opt.relativenumber = true   -- 相对行号
vim.opt.tabstop = 4             -- Tab 宽度
vim.opt.shiftwidth = 4          -- 缩进宽度
vim.opt.expandtab = true        -- 使用空格代替 Tab
```

### 使用 `vim.pack` 管理插件

```lua
vim.pack.add({
  'https://github.com/nvim-treesitter/nvim-treesitter',
  'https://github.com/ibhagwan/fzf-lua',
  'https://github.com/nvim-lualine/lualine.nvim',
})
```

## 核心配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `number` | boolean | false | 显示行号 |
| `relativenumber` | boolean | false | 相对行号 |
| `tabstop` | number | 8 | Tab 字符宽度 |
| `shiftwidth` | number | 8 | 自动缩进宽度 |
| `expandtab` | boolean | false | 使用空格代替 Tab |
| `mouse` | string | "" | 鼠标支持 |

## 常见用法

### 基础编辑

```lua
-- 基本移动
vim.keymap.set('n', '<C-d>', '<C-d>zz')  -- 向下滚动并居中
vim.keymap.set('n', '<C-u>', '<C-u>zz')  -- 向上滚动并居中

-- 快速保存
vim.keymap.set('n', '<leader>w', ':w<CR>', {desc = "Save file"})
```

### LSP 配置

```lua
-- LSP 配置示例
local lspconfig = require('lspconfig')
lspconfig.rust_analyzer.setup({
  settings = {
    ['rust-analyzer'] = {
      checkOnSave = {
        command = "clippy"
      }
    }
  }
})
```

### 键位映射

```lua
-- Leader 键定义
vim.g.mapleader = " "
vim.g.maplocalleader = " "

-- 常用映射
vim.keymap.set('n', '<leader>ff', '<cmd>FzfLua files<CR>')
vim.keymap.set('n', '<leader>fg', '<cmd>FzfLua live_grep<CR>')
```

## 依赖与集成

- **Treesitter**：语法高亮和代码分析
- **LSP**：语言服务器协议支持
- **fzf-lua**：模糊查找
- **lualine.nvim**：状态栏展示

## 已知问题 / 注意事项

- 从 Vim 迁移时注意配置差异
- Lua 配置与 Vimscript 配置不能同时使用
- 某些 Vim 插件可能需要适配才能在 Neovim 中正常工作

## 参考

- [[index]] 返回总目录
- [[concepts/lsp-basics]] LSP 基础概念
- [[concepts/lua-config]] Lua 配置指南
