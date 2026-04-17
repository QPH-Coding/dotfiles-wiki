# dotfiles

各开发工具的配置文件目录。每个工具对应一个子目录，统一由 `scripts/deploy.py` 读取 `scripts/targets.toml` 后部署到系统目标路径。

## 目录结构

```
dotfiles/
├── nvim/       ← Neovim 配置
└── ...         ← 其他工具配置（按需添加）
```

## 添加新工具

1. 在 `dotfiles/` 下创建工具同名目录（如 `dotfiles/zsh/`）
2. 在 `scripts/targets.toml` 中添加对应的部署路径
3. 执行 `uv run scripts/deploy.py <tool>` 部署

## 部署命令

```bash
# 部署单个工具
uv run scripts/deploy.py nvim

# 部署所有工具
uv run scripts/deploy.py all

# 预览（不实际写入）
uv run scripts/deploy.py nvim --dry-run
uv run scripts/deploy.py all --dry-run
```
