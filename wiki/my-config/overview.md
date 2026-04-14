---
type: my-config
name: 配置概览
last-updated: 2026-04-14
---

# 我的 Neovim 配置概览

> 当前仓库内已经提交并可通过 `scripts/deploy.py nvim` 部署的 Neovim 配置

## 目录结构

```text
dotfiles/nvim/
├── init.lua
├── nvim-pack-lock.json
└── lua/
    ├── core/
    │   ├── editor.lua
    │   └── options.lua
    └── plugins/
        ├── blink.lua
        ├── bufferline.lua
        ├── conform.lua
        ├── fzf_lua.lua
        ├── grug_far.lua
        ├── lualine.lua
        ├── mason.lua
        ├── mason_lspconfig.lua
        ├── nvim_lspconfig.lua
        ├── nvim_treesitter.lua
        └── persistence.lua
```

## 关键决策

### 插件管理

- 使用 `vim.pack`
- 在 `init.lua` 中直接通过 `vim.pack.add(..., { load = true, confirm = false })` 安装并立即加载插件
- 默认只使用仓库里已同步文档覆盖到的插件
- 每个插件一个 Lua 文件，插件自己的设置、键位和 autocmd 尽量跟插件文件放在一起

### 已启用插件

- `blink.cmp`：补全
- `bufferline.nvim`：Buffer 列表
- `conform.nvim`：格式化
- `fzf-lua`：文件查找与搜索
- `grug-far.nvim`：项目级查找替换
- `lualine.nvim`：状态栏
- `mason.nvim`：外部工具包管理
- `mason-lspconfig.nvim`：LSP server 安装与自动启用
- `nvim-lspconfig`：LSP 配置集合
- `nvim-treesitter`：语法高亮与结构化选择
- `persistence.nvim`：会话保存与恢复

### 依赖约束

- 没有引入 `nvim-web-devicons`，对应功能一律关闭图标
- LSP 直接走 `nvim-lspconfig` 暴露的 `vim.lsp.config()` / `vim.lsp.enable()` 接口

### LSP 策略

- 先用 `vim.lsp.config()` 声明 server 配置，再交给 `mason-lspconfig.nvim` 自动安装和启用
- 当前预置 server：
  - `bashls`
  - `lua_ls`
  - `pyright`
  - `rust_analyzer`
- `blink.cmp` 提供补全能力并补齐客户端 capabilities

### 外部工具

- `git`：`vim.pack` 必需
- `curl` / `wget`、`unzip`、`tar`、`gzip`：`mason.nvim` 推荐依赖
- `fzf`：`fzf-lua` 必需
- `rg`：`fzf-lua live_grep` 和 `grug-far.nvim` 需要
- `stylua`、`shfmt`：`conform.nvim` 当前已配置的格式化器，可通过 `:MasonInstall stylua shfmt` 安装
- Tree-sitter parser 需要在 Neovim 内按需安装

## 参考文档

- [[index]] 返回总目录
- [[tools/neovim]] Neovim 主工具页
- [[concepts/lua-config]] Lua 配置指南
