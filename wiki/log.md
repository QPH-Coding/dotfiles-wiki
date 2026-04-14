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

*日志开始于 2026-04-14*