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

`nvim-pack-lock.json` 由 `vim.pack` 生成，用于固定插件 revision。
`init.lua` 直接声明 `vim.pack.add(...)`，插件配置按“每个插件一个文件”拆到 `lua/plugins/`。
`lua/core/keymaps.lua` 负责登记自定义按键映射，并提供 cheatsheet 与搜索入口。
`lua/core/terminal.lua` 负责右侧专用终端窗格和 terminal tabs。

## 依赖前提

- Neovim 需要支持 `vim.pack`
- `git`：`vim.pack` 安装和更新插件时使用
- `fzf`：`fzf-lua` 需要
- `rg`：`fzf-lua live_grep` 和 `grug-far.nvim` 需要

## 已启用插件

- `Saghen/blink.cmp`
- `akinsho/bufferline.nvim`
- `sainnhe/everforest`
- `MagicDuck/grug-far.nvim`
- `mason-org/mason.nvim`
- `mason-org/mason-lspconfig.nvim`
- `stevearc/conform.nvim`
- `ibhagwan/fzf-lua`
- `nvim-lualine/lualine.nvim`
- `neovim/nvim-lspconfig`
- `nvim-treesitter/nvim-treesitter`
- `stevearc/oil.nvim`
- `folke/persistence.nvim`

## 主题

默认主题为 `sainnhe/everforest`。

- `lua/plugins/everforest.lua` 会在 `colorscheme everforest` 之前设置主题选项
- 当前固定 `background=dark`、`everforest_background="medium"`
- `everforest_better_performance = 1` 用于缩短主题加载时间
- `everforest_show_eob = 0` 用于隐藏 EndOfBuffer 高亮
- `lualine.nvim` 显式使用 `theme = "everforest"`

## 文件浏览

`oil.nvim` 现在接管目录 buffer，并作为当前配置的文件浏览器。

- `lua/plugins/oil.lua` 负责 `oil.nvim` 的设置和全局键位
- `_`：在当前窗口打开当前文件的父目录
- `<leader>fe`：切换 Oil 浮动文件浏览器
- 默认显示隐藏文件，适合当前 dotfiles 仓库
- 不启用 icon 列，继续保持当前不依赖 `nvim-web-devicons` 的约束
- 为避免覆盖现有窗口跳转，Oil 里的分屏选择改为 `<C-s>` 水平分屏、`<C-v>` 垂直分屏

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
:TSInstallConfigured
```

- `lua/plugins/nvim_treesitter.lua` 已迁移到 `nvim-treesitter` 0.12+ 新接口
- 通过 `FileType` autocmd 按需启用 Tree-sitter 高亮和缩进，并为大于 `1 MB` 的文件增加跳过保护
- `gnn` / `grn` / `grc` / `grm` 这组结构化选择按键现在由仓库内的 Lua 代码维护，不再依赖旧版 `incremental_selection` 配置项

## Buffer 切换

- `<M-h>`：切到上一个 buffer
- `<M-l>`：切到下一个 buffer
- `<leader>bp`：选择 buffer
## Keymap Cheatsheet

当前这份 README 已按 `nvim-treesitter` 0.12+ 更新：`gnn` / `grn` / `grc` / `grm` 来自 `lua/plugins/nvim_treesitter.lua` 里的仓库内实现，而不是旧版插件配置项。

当前配置会把仓库内定义的按键映射按模块登记到 cheatsheet 中，包括 `core`、各插件模块，以及
`blink.cmp` 默认 preset、Tree-sitter incremental selection 这类不是直接通过 `vim.keymap.set`
设置的映射。

- `:Cheatsheet`：打开按模块分组的 cheatsheet 浮动窗口
- `:Cheatsheet <module>`：只看某个模块，例如 `:Cheatsheet LSP`
- `:CheatsheetSearch`：打开可模糊查询的 keymap 列表
- `<leader>fK`：打开分组 cheatsheet
- `<leader>fk`：快速搜索 keymap

## Terminal Panel

右侧终端现在是一个专用窗格，顶部会有一条只属于终端的 terminal tab bar：

- `<leader>tt`：打开或聚焦右侧 terminal tabs
- `<leader>tn`：在右侧创建一个新的 terminal tab
- `<leader>th`：切到上一个 terminal tab
- `<leader>tl`：切到下一个 terminal tab
- `<leader>tb`：从右侧 terminal panel 回到普通编辑区
- `:TerminalPanel`：打开或聚焦右侧 terminal tabs
- `:TerminalPanelNew`：在右侧创建一个新的 terminal tab

这个窗格会把终端 buffer 从普通 `bufferline` 中隐藏，顶部 tab bar 里只显示 terminal tabs；
如果你误把文本 buffer 打开到这个窗格里，它会被挪回普通编辑区。tab bar 里的 `+`
可以直接新建一个 terminal tab，已有 tab 也可以直接点击或回车切换。

另外补了几组更直接的终端切换键。

terminal 模式：

- `<M-h>`：切到左边一个 terminal tab，并保持在 terminal 模式
- `<M-l>`：切到右边一个 terminal tab，并保持在 terminal 模式
- `<M-b>`：直接把焦点切回普通编辑区
- `<Esc><Esc><Esc>`：退出 terminal 模式回到 normal 模式

normal 模式：

- `<M-t>`：如果右侧 terminal panel 已存在，直接切进去并进入 terminal 模式；如果还没有，会先打开它
