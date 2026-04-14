---
type: my-config
name: 配置概览
last-updated: 2026-04-14
---

# 我的 Neovim 配置概览

> 基于 Lua 的现代 Neovim 配置全景，强调性能、可维护性和开发效率

## 整体架构

### 配置结构

```
~/.config/nvim/
├── init.lua              # 主入口文件
├── lua/
│   ├── core/             # 核心配置模块
│   │   ├── options.lua   # 编辑器选项
│   │   ├── keymaps.lua   # 键位映射
│   │   ├── autocmds.lua  # 自动命令
│   │   └── utils.lua     # 工具函数
│   ├── plugins/          # 插件配置
│   │   ├── init.lua      # 插件管理器配置
│   │   ├── lsp.lua       # LSP 相关插件
│   │   ├── ui.lua        # 界面美化插件
│   │   ├── tools.lua     # 开发工具插件
│   │   └── lang.lua      # 语言特定配置
│   └── config/           # 应用配置
│       ├── telescope.lua  # 文件查找配置
│       ├── treesitter.lua # 语法高亮配置
│       └── lualine.lua    # 状态栏配置
├── after/                # 后处理配置
│   └── plugin/           # 插件后处理配置
└── snippets/             # 代码片段
```

### 设计原则

1. **模块化**：每个功能独立成模块，便于维护和调试
2. **延迟加载**：按需加载插件，优化启动性能
3. **一致性**：统一的配置风格和命名规范
4. **可扩展**：易于添加新功能和插件

## 核心工具选择

| 工具类别 | 选用工具 | 理由 |
|----------|----------|------|
| **插件管理器** | packer.nvim | 稳定、功能完善 |
| **LSP 管理器** | mason.nvim + nvim-lspconfig | 统一管理语言服务器 |
| **语法高亮** | nvim-treesitter | 现代语法解析器 |
| **文件查找** | telescope.nvim | 强大的模糊查找器 |
| **状态栏** | lualine.nvim | 轻量级状态栏 |
| **键位提示** | which-key.nvim | 键位映射提示 |
| **主题** | tokyonight.nvim | 现代深色主题 |

## 关键配置决策

### 性能优先

```lua
-- 禁用不必要的内置插件
vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1
vim.g.loaded_2html_plugin = 1
vim.g.loaded_tutor_mode_plugin = 1

-- 延迟加载策略
-- 具体配置取决于所使用的插件管理器
```

### 键位映射设计

```lua
-- Leader 键定义
vim.g.mapleader = " "
vim.g.maplocalleader = " "

-- 常用操作映射
vim.keymap.set('n', '<leader>w', ':w<CR>', {desc = '保存文件'})
vim.keymap.set('n', '<leader>q', ':q<CR>', {desc = '退出'})
vim.keymap.set('n', '<leader>ff', ':Telescope find_files<CR>', {desc = '查找文件'})
vim.keymap.set('n', '<leader>fg', ':Telescope live_grep<CR>', {desc = '全局搜索'})

-- LSP 相关映射
vim.keymap.set('n', 'gd', vim.lsp.buf.definition, {desc = '跳转到定义'})
vim.keymap.set('n', 'gr', vim.lsp.buf.references, {desc = '查找引用'})
vim.keymap.set('n', 'K', vim.lsp.buf.hover, {desc = '悬停信息'})
```

### LSP 配置策略

```lua
-- 使用 mason.nvim 管理语言服务器
require('mason').setup()
require('mason-lspconfig').setup({
  ensure_installed = {
    'lua_ls',
    'rust_analyzer',
    'pyright',
    'tsserver',
    'gopls',
  },
  automatic_installation = true,
})

-- LSP 服务器配置
local lspconfig = require('lspconfig')
lspconfig.lua_ls.setup({
  settings = {
    Lua = {
      runtime = { version = 'LuaJIT' },
      diagnostics = { globals = {'vim'} },
      workspace = { library = vim.api.nvim_get_runtime_file("", true) },
      telemetry = { enable = false },
    },
  },
})
```

## 开发语言支持

### Lua 开发

```lua
-- Lua 语言服务器配置
lspconfig.lua_ls.setup({
  settings = {
    Lua = {
      runtime = { version = 'LuaJIT' },
      diagnostics = { globals = {'vim'} },
      workspace = { library = vim.api.nvim_get_runtime_file("", true) },
      telemetry = { enable = false },
    },
  },
})
```

### Rust 开发

```lua
-- Rust 语言服务器配置
lspconfig.rust_analyzer.setup({
  settings = {
    ['rust-analyzer'] = {
      checkOnSave = {
        command = "clippy",
      },
    },
  },
})
```

### Python 开发

```lua
-- Python 语言服务器配置
lspconfig.pyright.setup({
  settings = {
    python = {
      analysis = {
        typeCheckingMode = "basic",
        autoSearchPaths = true,
        useLibraryCodeForTypes = true,
      },
    },
  },
})
```

## 性能指标

### 启动时间目标

- **冷启动**：< 50ms
- **热启动**：< 30ms
- **插件加载**：按需延迟加载

### 内存使用

- **基础内存**：< 50MB
- **插件内存**：按需增长
- **缓存策略**：智能缓存管理

## 待解决问题

- [ ] **性能优化**：进一步优化启动时间
- [ ] **插件管理**：清理不常用的插件
- [ ] **配置同步**：实现跨机器配置同步
- [ ] **备份策略**：定期配置备份机制
- [ ] **文档完善**：完善配置文档和注释

## 维护计划

### 定期维护任务

1. **每周**：检查插件更新，备份配置
2. **每月**：清理缓存，优化性能
3. **每季度**：评估插件使用情况，移除不常用插件
4. **每年**：全面审查配置架构

### 故障排除流程

1. **问题诊断**：使用 `:checkhealth` 检查系统状态
2. **性能分析**：使用 `:StartupTime` 分析启动性能
3. **插件隔离**：逐个禁用插件定位问题
4. **配置回滚**：使用 git 回滚到稳定版本

## 参考文档

- [[index]] 返回总目录
- [[tools/neovim]] Neovim 主工具页
- [[concepts/lua-config]] Lua 配置指南
- [[workflows/plugin-management]] 插件管理工作流

## 更新日志

### 2026-04-14
- 初始配置框架搭建
- 完成核心插件选择和配置
- 建立模块化配置结构
- 实现基础性能优化

---

*本配置持续优化中，欢迎反馈和建议*