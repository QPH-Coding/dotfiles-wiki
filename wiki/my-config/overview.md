---
type: my-config
name: 配置概览
last-updated: 2026-04-16
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
    │   ├── keymaps.lua
    │   ├── options.lua
    │   └── terminal.lua
    └── plugins/
        ├── blink.lua
        ├── bufferline.lua
        ├── everforest.lua
        ├── conform.lua
        ├── fzf_lua.lua
        ├── grug_far.lua
        ├── lualine.lua
        ├── mason.lua
        ├── mason_lspconfig.lua
        ├── nvim_lspconfig.lua
        ├── nvim_treesitter.lua
        ├── oil.lua
        └── persistence.lua
```

## 关键决策

### 插件管理

- 使用 `vim.pack`
- 在 `init.lua` 中直接通过 `vim.pack.add(..., { load = true, confirm = false })` 安装并立即加载插件
- 默认只使用仓库里已同步文档覆盖到的插件
- 每个插件一个 Lua 文件，插件自己的设置、键位和 autocmd 尽量跟插件文件放在一起

### 视觉主题

- 默认 `colorscheme` 使用 `everforest`
- 在 `lua/plugins/everforest.lua` 里先设置主题选项，再执行 `colorscheme everforest`
- 当前固定深色背景，并显式关闭 `EndOfBuffer` 高亮
- `lualine.nvim` 直接使用 `everforest` 主题，避免和主色板脱节

### 已启用插件

- `blink.cmp`：补全
- `bufferline.nvim`：Buffer 列表
- `everforest`：默认主题
- `conform.nvim`：格式化
- `fzf-lua`：文件查找与搜索
- `grug-far.nvim`：项目级查找替换
- `lualine.nvim`：状态栏
- `mason.nvim`：外部工具包管理
- `mason-lspconfig.nvim`：LSP server 安装与自动启用
- `nvim-lspconfig`：LSP 配置集合
- `nvim-treesitter`：语法高亮与结构化选择
- `oil.nvim`：文件浏览器
- `persistence.nvim`：会话保存与恢复

### 文件浏览

- 使用 `oil.nvim` 接管目录 buffer，并提供仓库内文件浏览
- `lua/plugins/oil.lua` 关闭 icon 列，继续保持不依赖 `nvim-web-devicons`
- 默认显示隐藏文件，更适合当前 dotfiles 仓库
- 全局入口为 `_` 和 `<leader>fe`
- 将 Oil 的分屏入口调整为 `<C-s>` / `<C-v>`，避免和现有 `<C-h>` / `<C-l>` 窗口导航冲突
- Buffer 切换使用 `<M-h>` / `<M-l>`，terminal 模式下的 terminal tab 切换也复用这组键

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
- [[tools/everforest]] Everforest 主题插件
- [[tools/neovim]] Neovim 主工具页
- [[concepts/lua-config]] Lua 配置指南