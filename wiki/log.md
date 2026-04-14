# 操作日志

记录 wiki 的创建、更新和维护操作。

---

## [2026-04-14] Ingest | Neovim 文档初始导入

- **操作**：ingest
- **涉及文件**：
  - wiki/tools/neovim.md
  - wiki/concepts/lsp-basics.md
  - wiki/concepts/lua-config.md
  - wiki/tools/plugins.md
  - wiki/workflows/plugin-management.md
  - wiki/my-config/overview.md
  - wiki/index.md
  - wiki/log.md
- **摘要**：基于 raw/doc/neovim/doc/ 目录下的文档，创建了 Neovim 相关的核心工具页、概念页和工作流页，建立了 wiki 的基础架构

---

## [2026-04-14] Cleanup | 清理 lazy.nvim 相关文档

- **操作**：cleanup
- **涉及文件**：
  - wiki/tools/lazy-nvim.md (已删除)
  - wiki/index.md
  - wiki/workflows/plugin-management.md
  - wiki/my-config/overview.md
  - wiki/tools/neovim.md
  - wiki/log.md
- **摘要**：根据用户要求，清理了所有与 lazy.nvim 相关的文档引用和配置示例

---

## [2026-04-14] Cleanup | 清理插件相关内容

- **操作**：cleanup
- **涉及文件**：
  - wiki/tools/plugins.md (已删除)
  - wiki/workflows/plugin-management.md (已删除)
  - wiki/index.md
  - wiki/log.md
- **摘要**：根据用户要求，清理了所有插件相关的内容，仅保留 Neovim 官方文档相关内容

---

## [2026-04-14] Update | 添加 vim.pack 功能总结

- **操作**：update
- **涉及文件**：
  - wiki/tools/vim-pack.md
  - wiki/index.md
  - wiki/log.md
- **摘要**：基于 raw/doc/neovim/doc/pack.txt 文档，创建了 vim.pack 工具页，总结 Neovim 内置插件管理器的功能和使用方法

---

## [2026-04-14] Sync | 拉取插件文档

- **操作**：sync
- **涉及文件**：
  - raw/manifest.json（添加了 11 个插件文档源）
  - raw/doc/neovim/plugin/（所有插件文档目录）
  - wiki/log.md
- **摘要**：成功拉取以下插件的文档到 raw/doc/neovim/plugin/ 目录：
  - MagicDuck/grug-far.nvim
  - stevearc/conform.nvim
  - neovim/nvim-lspconfig
  - mason-org/mason-lspconfig.nvim
  - nvim-treesitter/nvim-treesitter
  - akinsho/bufferline.nvim
  - nvim-lualine/lualine.nvim
  - folke/persistence.nvim
  - ibhagwan/fzf-lua
  - Saghen/blink.cmp

---

## [2026-04-14] Reorganize | 重组 raw 目录结构

- **操作**：reorganize
- **涉及文件**：
  - raw/manifest.json（更新所有 prefix 路径）
  - wiki/log.md
  - wiki/concepts/lsp-basics.md
  - wiki/concepts/lua-config.md
  - wiki/tools/neovim.md
  - wiki/tools/vim-pack.md
- **摘要**：将目录结构从 raw/docs/neovim 和 raw/docs/plugins 重组为：
  - raw/doc/neovim/doc（Neovim 官方文档）
  - raw/doc/neovim/plugin（插件文档）

---

## [2026-04-14] Cleanup | 收缩 wiki 到当前可验证状态

- **操作**：cleanup
- **涉及文件**：
  - wiki/index.md
  - wiki/my-config/overview.md
  - wiki/tools/neovim.md
  - wiki/tools/vim-pack.md
  - wiki/concepts/lsp-basics.md
  - wiki/concepts/lua-config.md
  - wiki/log.md
- **摘要**：移除了缺失页面引用、旧插件管理器示例和与当前仓库状态不一致的设想性配置，wiki 只保留可由仓库内容和已同步文档支持的内容

---

## [2026-04-14] Config | 创建基于 vim.pack 的 Neovim 配置

- **操作**：config
- **涉及文件**：
  - dotfiles/nvim/README.md
  - dotfiles/nvim/init.lua
  - dotfiles/nvim/lua/config/options.lua
  - dotfiles/nvim/lua/config/plugins.lua
  - dotfiles/nvim/lua/config/keymaps.lua
  - dotfiles/nvim/lua/config/autocmds.lua
  - dotfiles/nvim/lua/config/lsp.lua
  - wiki/my-config/overview.md
  - wiki/tools/vim-pack.md
  - wiki/log.md
- **摘要**：基于已同步的 Neovim 与插件文档，创建了一个只使用已建档插件的 Lua 配置；插件管理使用 `vim.pack`，LSP 直接使用 `nvim-lspconfig`，未默认引入无文档依赖插件

---

## [2026-04-14] Update | 引入 mason.nvim 并切换为 Mason 管理 LSP

- **操作**：update
- **涉及文件**：
  - raw/manifest.json
  - raw/doc/neovim/plugin/mason-nvim/
  - dotfiles/nvim/README.md
  - dotfiles/nvim/lua/config/keymaps.lua
  - dotfiles/nvim/lua/config/lsp.lua
  - dotfiles/nvim/lua/config/plugins.lua
  - wiki/concepts/lsp-basics.md
  - wiki/my-config/overview.md
  - wiki/log.md
- **摘要**：新增 `mason.nvim` 文档源并同步到本地；Neovim 配置改为使用 `mason.nvim + mason-lspconfig.nvim` 安装和启用 LSP server，同时保留 `vim.lsp.config()` 作为具体 server 配置入口

---

## [2026-04-15] Refactor | 重组 Neovim 配置目录

- **操作**：refactor
- **涉及文件**：
  - dotfiles/nvim/init.lua
  - dotfiles/nvim/README.md
  - dotfiles/nvim/lua/core/editor.lua
  - dotfiles/nvim/lua/core/options.lua
  - dotfiles/nvim/lua/plugins/
  - dotfiles/nvim/lua/config/ (已删除)
  - wiki/my-config/overview.md
  - wiki/log.md
- **摘要**：将 Neovim 配置从集中式 `lua/config/` 改为 `lua/core/ + lua/plugins/` 结构；`vim.pack.add(...)` 直接放回 `init.lua`，插件相关设置、键位和 autocmd 迁移到各自插件文件中

---

*日志开始于 2026-04-14*
