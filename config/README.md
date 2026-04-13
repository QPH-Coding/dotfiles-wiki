# nvim-config

Neovim 配置源文件目录。

此目录的内容由 `scripts/deploy_config.py` 部署到系统 Neovim 配置目录：
- **Windows**: `%LOCALAPPDATA%\nvim\`
- **macOS/Linux**: `~/.config/nvim/`

## 使用方式

```bash
# 预览将要部署的内容（不实际修改）
python scripts/deploy_config.py --dry-run

# 执行部署（会先备份现有系统配置）
python scripts/deploy_config.py
```

## 目录结构参考

```
nvim-config/
├── init.lua
├── lua/
│   ├── config/
│   │   ├── options.lua
│   │   ├── keymaps.lua
│   │   └── autocmds.lua
│   └── plugins/
│       ├── init.lua      ← lazy.nvim 入口
│       └── ...           ← 各插件配置
└── ...
```
