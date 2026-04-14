---
type: concept
name: LSP
sources: ["raw/doc/neovim/doc/lsp.txt"]
last-updated: 2026-04-14
---

# LSP (Language Server Protocol)

> 语言服务器协议，为编辑器提供代码智能功能的标准协议

## 是什么

LSP 是微软开发的一个开放标准协议，允许编辑器与语言服务器通信，提供代码补全、错误检查、重构等智能功能。

## 在 Neovim 中的应用

Neovim 内置了 LSP 客户端，通过 `nvim-lspconfig` 提供的配置集合可以声明 server 配置；如果希望统一安装和管理语言服务器，可再配合 `mason.nvim` 与 `mason-lspconfig.nvim`。

### 核心组件

- **LSP 客户端**：Neovim 内置的客户端实现
- **语言服务器**：针对特定语言的服务器（如 rust-analyzer、pyright、tsserver）
- **nvim-lspconfig**：配置语言服务器的插件

## 基本配置

```lua
require("mason").setup()

vim.lsp.config("lua_ls", {
  settings = {
    Lua = {},
  },
})

require("mason-lspconfig").setup({
  ensure_installed = { "lua_ls", "pyright" },
  automatic_enable = { "lua_ls", "pyright" },
})
```

## 常用功能

### 代码导航

```lua
-- 跳转到定义
vim.keymap.set('n', 'gd', vim.lsp.buf.definition)

-- 跳转到声明
vim.keymap.set('n', 'gD', vim.lsp.buf.declaration)

-- 跳转到实现
vim.keymap.set('n', 'gi', vim.lsp.buf.implementation)

-- 跳转到类型定义
vim.keymap.set('n', 'gy', vim.lsp.buf.type_definition)
```

### 代码操作

```lua
-- 重命名符号
vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename)

-- 代码操作
vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action)

-- 格式化代码
vim.keymap.set('n', '<leader>f', function()
  vim.lsp.buf.format({async = true})
end)
```

### 诊断信息

```lua
-- 显示诊断信息
vim.keymap.set('n', '<leader>e', vim.diagnostic.open_float)

-- 跳转到下一个诊断
vim.keymap.set('n', '[d', vim.diagnostic.goto_next)

-- 跳转到上一个诊断
vim.keymap.set('n', ']d', vim.diagnostic.goto_prev)
```

## 相关工具

- **nvim-lspconfig**：LSP 服务器配置
- **mason.nvim**：外部工具与语言服务器安装
- **mason-lspconfig.nvim**：将已安装的语言服务器接到 `nvim-lspconfig`
- **blink.cmp**：补全能力
- **fzf-lua**：LSP 结果浏览

## 配置要点

1. **服务器选择**：根据语言选择合适的服务器
2. **性能优化**：配置合适的缓存和并发设置
3. **错误处理**：设置合理的超时和重试机制
4. **诊断配置**：调整诊断级别和显示方式

## 参考

- [[index]] 返回总目录
- [[tools/neovim]] Neovim 主工具页
- [[concepts/lua-config]] Lua 配置指南
