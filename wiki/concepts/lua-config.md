---
type: concept
name: Lua 配置
sources: ["raw/doc/neovim/doc/lua-guide.txt", "raw/doc/neovim/doc/lua.txt"]
last-updated: 2026-04-14
---

# Lua 配置

> Neovim 中使用 Lua 进行配置的指南和最佳实践

## 是什么

Lua 是 Neovim 的一等配置语言，相比 Vimscript 更现代、性能更好、语法更清晰。

## 配置结构

### 基本配置文件

```lua
-- ~/.config/nvim/init.lua
vim.opt.number = true           -- 显示行号
vim.opt.relativenumber = true   -- 相对行号
vim.opt.tabstop = 4             -- Tab 宽度
vim.opt.shiftwidth = 4          -- 缩进宽度
vim.opt.expandtab = true        -- 使用空格代替 Tab

-- Leader 键定义
vim.g.mapleader = " "
vim.g.maplocalleader = " "
```

### 模块化配置

```lua
-- 模块化结构示例
-- ~/.config/nvim/
-- ├── init.lua          -- 主配置文件
-- ├── lua/
-- │   ├── options.lua   -- 选项配置
-- │   ├── keymaps.lua   -- 键位映射
-- │   ├── plugins.lua   -- 插件配置
-- │   └── autocmds.lua  -- 自动命令

-- init.lua
require('options')
require('keymaps')
require('plugins')
require('autocmds')
```

## API 层次结构

### Vim API（继承自 Vim）

```lua
-- Vim 命令
vim.cmd('set number')
vim.cmd('colorscheme gruvbox')

-- Vimscript 函数
vim.fn.getcwd()
vim.fn.expand('%:p')
```

### Nvim API（C 语言实现）

```lua
-- API 函数
vim.api.nvim_set_option('number', true)
vim.api.nvim_buf_set_lines(0, 0, -1, false, {'Hello', 'World'})
```

### Lua API（Lua 专用）

```lua
-- Lua 专用函数
vim.opt.number = true           -- 选项设置
vim.keymap.set('n', '<leader>w', ':w<CR>')  -- 键位映射
vim.diagnostic.open_float()     -- 诊断信息
```

## 常用配置模式

### 选项设置

```lua
-- 基本选项
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true
vim.opt.mouse = 'a'             -- 启用鼠标
vim.opt.clipboard = 'unnamedplus' -- 系统剪贴板

-- 搜索相关
vim.opt.ignorecase = true       -- 忽略大小写
vim.opt.smartcase = true        -- 智能大小写
vim.opt.hlsearch = true         -- 高亮搜索
vim.opt.incsearch = true        -- 增量搜索
```

### 键位映射

```lua
-- 普通模式映射
vim.keymap.set('n', '<leader>w', ':w<CR>', {desc = 'Save file'})
vim.keymap.set('n', '<leader>q', ':q<CR>', {desc = 'Quit'})
vim.keymap.set('n', '<C-s>', ':w<CR>', {desc = 'Save file'})

-- 插入模式映射
vim.keymap.set('i', 'jk', '<Esc>', {desc = 'Exit insert mode'})

-- 可视模式映射
vim.keymap.set('v', '<leader>y', '"+y', {desc = 'Copy to clipboard'})
vim.keymap.set('v', '<leader>p', '"+p', {desc = 'Paste from clipboard'})
```

### 自动命令

```lua
-- 自动命令组
local augroup = vim.api.nvim_create_augroup('MyGroup', {clear = true})

-- 文件类型特定设置
vim.api.nvim_create_autocmd('FileType', {
  group = augroup,
  pattern = 'python',
  callback = function()
    vim.opt_local.tabstop = 4
    vim.opt_local.shiftwidth = 4
  end
})

-- 保存时自动格式化
vim.api.nvim_create_autocmd('BufWritePre', {
  group = augroup,
  pattern = '*',
  callback = function()
    vim.lsp.buf.format({async = false})
  end
})
```

## 性能优化

### 延迟加载

```lua
-- 使用 packer.nvim 的延迟加载
use {
  'nvim-telescope/telescope.nvim',
  cmd = 'Telescope',  -- 命令触发加载
  keys = {'<leader>ff'},  -- 键位触发加载
  config = function()
    require('telescope').setup()
  end
}
```

### 条件加载

```lua
-- 只在特定条件下加载插件
if vim.fn.has('nvim-0.8') == 1 then
  require('some-new-feature')
end
```

## 调试技巧

```lua
-- 打印调试信息
:lua =vim.inspect(vim.opt)

-- 检查 Lua 模块
:lua =package.loaded['my-module']

-- 重新加载模块
:lua package.loaded['my-module'] = nil
:lua require('my-module')
```

## 常见问题

### 与 Vimscript 的互操作

```lua
-- 调用 Vimscript 函数
local result = vim.fn.system('ls -la')

-- 执行 Vim 命令
vim.cmd('echo "Hello from Vimscript"')
```

### 作用域问题

```lua
-- 注意：每个 :lua 命令有独立作用域
:lua local x = 1
:lua print(x)  -- 输出 nil

-- 正确方式：使用全局变量
:lua _G.my_var = 1
:lua print(_G.my_var)  -- 输出 1
```

## 参考

- [[index]] 返回总目录
- [[tools/neovim]] Neovim 主工具页
- [[concepts/lsp-basics]] LSP 基础概念