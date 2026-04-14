# nvim

基于 `vim.pack` 的 Neovim 配置，默认只使用当前仓库已同步文档覆盖到的插件。

## 结构

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

`nvim-pack-lock.json` 由 `vim.pack` 生成，用于固定插件 revision。
`init.lua` 直接声明 `vim.pack.add(...)`，插件配置按“每个插件一个文件”拆到 `lua/plugins/`。

## 依赖前提

- Neovim 需要支持 `vim.pack`
- `git`：`vim.pack` 安装和更新插件时使用
- `fzf`：`fzf-lua` 需要
- `rg`：`fzf-lua live_grep` 和 `grug-far.nvim` 需要

## 已启用插件

- `Saghen/blink.cmp`
- `akinsho/bufferline.nvim`
- `MagicDuck/grug-far.nvim`
- `mason-org/mason.nvim`
- `mason-org/mason-lspconfig.nvim`
- `stevearc/conform.nvim`
- `ibhagwan/fzf-lua`
- `nvim-lualine/lualine.nvim`
- `neovim/nvim-lspconfig`
- `nvim-treesitter/nvim-treesitter`
- `folke/persistence.nvim`

## 工具安装

LSP server 交给 Mason 管理。当前配置会通过 `mason-lspconfig.nvim`
确保以下 server 已安装并自动启用：

- `bashls` -> `bash-language-server`
- `lua_ls` -> `lua-language-server`
- `pyright` -> `pyright-langserver`
- `rust_analyzer` -> `rust-analyzer`

格式化器仍然需要你自己准备；现在既可以走系统 PATH，也可以直接用 Mason 安装：

- `:MasonInstall stylua shfmt`

`conform.nvim` 当前为以下格式化器预留了映射：

- `stylua`
- `shfmt`

Tree-sitter 解析器请按需在 Neovim 内执行：

```vim
:TSInstall lua vim vimdoc query markdown markdown_inline bash python rust
```
