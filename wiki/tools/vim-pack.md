---
type: tool
name: vim.pack
category: nvim-core
repo: neovim/neovim
sources: ["raw/doc/neovim/doc/pack.txt"]
last-updated: 2026-04-14
---

# vim.pack

> Neovim 内置的现代化插件管理器，提供 Git 驱动的插件安装、更新和管理功能

## 定位

`vim.pack` 是 Neovim 核心集成的插件管理系统，旨在替代传统的外部插件管理器。它基于 Git 仓库管理，支持版本控制、跨机器同步和现代化的配置体验。

## 核心特性

### 内置集成
- 直接集成在 Neovim 核心中，无需额外安装
- 使用 Lua API 进行配置和管理
- 支持标准的包目录结构（`pack/*/start/*` 和 `pack/*/opt/*`）

### Git 驱动
- 要求目标插件必须是 Git 仓库
- 支持语义化版本控制（semver）
- 可指定分支、标签或提交哈希作为版本

### 锁文件机制
- 使用 `nvim-pack-lock.json` 文件跟踪插件状态
- 支持跨机器配置同步
- 可纳入版本控制系统管理

## 主要 API 函数

### `vim.pack.add({specs}, {opts})`
添加插件到当前会话：

```lua
vim.pack.add({
  'https://github.com/user/plugin1',
  { src = 'https://github.com/user/plugin2', name = 'custom-name' },
  { src = 'https://github.com/user/plugin3', version = 'main' },
  { src = 'https://github.com/user/plugin4', version = vim.version.range('1.0') }
})
```

**参数说明：**
- `specs`: 插件规格列表，可以是字符串或表格
- `opts.load`: 是否加载插件文件（默认在 init.lua 中为 false）
- `opts.confirm`: 是否确认初始安装（默认 true）

### `vim.pack.update({names}, {opts})`
更新插件：

```lua
-- 更新所有插件
vim.pack.update()

-- 更新特定插件
vim.pack.update({'plugin1', 'plugin2'})

-- 离线模式（仅检查状态）
vim.pack.update(nil, {offline = true})
```

**参数说明：**
- `names`: 要更新的插件名称列表
- `opts.force`: 跳过确认直接更新
- `opts.offline`: 仅本地操作，不下载更新
- `opts.target`: 更新目标（"version" 或 "lockfile"）

### `vim.pack.del({names}, {opts})`
删除插件：

```lua
vim.pack.del({'plugin1', 'plugin2'})
```

**参数说明：**
- `names`: 要删除的插件名称列表
- `opts.force`: 允许删除活跃插件

### `vim.pack.get({names}, {opts})`
获取插件信息：

```lua
local plugins = vim.pack.get()
```

## 配置示例

### 基础配置
```lua
-- 在 init.lua 中添加插件
vim.pack.add({
  'https://github.com/nvim-treesitter/nvim-treesitter',
  'https://github.com/ibhagwan/fzf-lua',
  { src = 'https://github.com/nvim-lualine/lualine.nvim', version = 'master' }
})
```

### 自定义辅助函数
```lua
local gh = function(x) return 'https://github.com/' .. x end
vim.pack.add({ gh('nvim-treesitter/nvim-treesitter'), gh('nvim-lualine/lualine.nvim') })
```

### Git 别名配置
```bash
# 配置 Git 别名
git config --global url."https://github.com/".insteadOf "gh:"
git config --global url."https://codeberg.org/".insteadOf "cb:"
```

```lua
-- 使用别名
vim.pack.add({ 'gh:user/plugin1', 'cb:user/plugin2' })
```

## 工作流程

### 1. 初始安装
1. 在 `init.lua` 中添加 `vim.pack.add()` 调用
2. 重启 Neovim
3. 插件自动下载安装

### 2. 更新管理
1. 执行 `vim.pack.update()`
2. 查看确认缓冲区中的变更
3. 使用 `:write` 确认或 `:quit` 取消

### 3. 版本控制
- 支持冻结插件版本（指定具体提交哈希）
- 可回滚到之前的版本
- 支持语义化版本约束

## 事件系统

### PackChangedPre
插件状态变更前触发，可用于预处理操作

### PackChanged
插件状态变更后触发，可用于后处理操作

```lua
vim.api.nvim_create_autocmd('PackChanged', {
  callback = function(ev)
    local name, kind = ev.data.spec.name, ev.data.kind
    
    -- 插件安装或更新后执行构建脚本
    if name == 'plugin1' and (kind == 'install' or kind == 'update') then
      vim.system({ 'make' }, { cwd = ev.data.path })
    end
  end
})
```

## 优势特点

### 内置优势
- 无需额外依赖，开箱即用
- 与 Neovim 深度集成
- 统一的配置管理体验

### 现代化特性
- 并行安装和更新
- 交互式确认界面
- LSP 集成（支持导航和代码操作）

### 生产就绪
- 支持团队协作和跨机器同步
- 详细的错误日志和状态跟踪
- 可预测的版本管理

## 已知问题 / 注意事项

### 实验性状态
- 目前仍标记为实验性功能，但已足够稳定用于日常使用
- API 可能在未来的 Neovim 版本中发生变化

### 系统要求
- 要求系统安装 Git
- 仅支持 Git 仓库作为插件源

### 配置注意事项
- 确保 `site` 目录在 'packpath' 中
- 锁文件应纳入版本控制以实现跨机器同步
- 插件名称冲突时需要使用自定义名称

## 故障排除

### 插件加载失败
```lua
-- 检查插件是否成功加载
if not package.loaded['plugin-name'] then
  vim.notify("插件加载失败", vim.log.levels.WARN)
end
```

### 版本冲突
```lua
-- 回滚到锁文件中的版本
vim.pack.update({'plugin'}, { target = 'lockfile' })
```

### 清理问题插件
```lua
-- 强制删除问题插件
vim.pack.del({'problem-plugin'}, { force = true })
```

## 参考

- [[index]] 返回总目录
- [[tools/neovim]] Neovim 主工具页
- [[concepts/lua-config]] Lua 配置指南
