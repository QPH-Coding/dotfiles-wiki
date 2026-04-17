# 仓库指南

## 项目结构与模块组织

本仓库由 dotfiles、维护脚本和知识库 wiki 组成，修改时请放到正确目录：

- `dotfiles/`：各工具配置的唯一事实来源。当前最活跃的模块是 `dotfiles/nvim/`，包含 `init.lua`、`lua/core/` 和 `lua/plugins/`。
- `scripts/`：仓库维护脚本，主要包括 `deploy.py`、`sync_docs.py` 和 `targets.toml`。
- `wiki/`：持续维护的知识库。查询和补充内容时优先从 `wiki/index.md` 开始；重要维护动作追加到 `wiki/log.md`。
- `raw/`：从外部同步的原始材料。调整来源时修改 `raw/manifest.toml`，其余下载内容视为生成文件，默认只读。

当前仓库没有独立的 `tests/` 目录。

## 构建、测试与开发命令

- `uv run scripts/deploy.py nvim --dry-run`：预览部署，不写入实际文件。
- `uv run scripts/deploy.py nvim`：部署单个工具配置。
- `uv run scripts/deploy.py all`：按 `scripts/targets.toml` 部署全部已配置工具。
- `uv run scripts/sync_docs.py --list`：查看外部文档来源及当前同步版本。
- `uv run scripts/sync_docs.py <name>`：同步 `raw/manifest.toml` 中的单个来源。
- `uv run scripts/sync_docs.py --update <name> <ref>`：更新某个来源的 ref 并立即同步。

## 编码风格与命名约定

- Lua：2 空格缩进，模块保持小而单一；`lua/plugins/` 下遵循“一插件一文件”，文件名使用 snake_case，如 `nvim_lspconfig.lua`。
- Python：使用 UTF-8 编码、4 空格缩进，脚本统一通过 `uv run` 启动，并要求 Python `>=3.12`；优先标准库实现简单脚本。
- Wiki 页面：文件名统一使用小写 kebab-case，例如 `lsp-basics.md`。
- 保持现有约定：工具名、配置项、API 和命令保留英文；解释性文字使用中文。
- 回答问题或补充内容时，优先引用仓库内现有文档和 wiki，再考虑新增或改写内容。

## 测试指南

仓库目前没有自动化测试套件，主要依赖 dry-run 和定向手工验证：

- 对部署相关改动，先运行 `uv run scripts/deploy.py <tool> --dry-run`。
- 部署后重新打开受影响工具，尤其是 Neovim。
- 修改 wiki 导航或新增页面时，同步维护 `wiki/index.md`。

## 提交与 Pull Request 规范

最近提交采用 Conventional Commits 风格，例如 `feat:`、`refactor:`。继续沿用该前缀，并让主题简短、具体。

Pull Request 应说明变更范围、列出涉及目录、记录手工验证结果，并注明是否更新了 `wiki/index.md`、`wiki/log.md`、`raw/manifest.toml` 或 `scripts/targets.toml`。
