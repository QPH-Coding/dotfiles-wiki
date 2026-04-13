#!/usr/bin/env python3
"""
deploy_config.py — 将 config/ 部署到系统 Neovim 配置目录

用法:
    python scripts/deploy_config.py          # 部署（覆盖系统目录）
    python scripts/deploy_config.py --dry-run  # 预览将要执行的操作，不实际写入

源目录:  <仓库根>/config/
目标目录 (Windows): %LOCALAPPDATA%\\nvim\\
目标目录 (macOS/Linux): ~/.config/nvim/
"""

import argparse
import os
import platform
import shutil
import sys
from pathlib import Path


# ── 路径常量 ──────────────────────────────────────────────────────────────────

REPO_ROOT   = Path(__file__).resolve().parent.parent
SOURCE_DIR  = REPO_ROOT / "config"


def get_target_dir() -> Path:
    """根据操作系统返回 Neovim 配置目录。"""
    system = platform.system()
    if system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            print("[ERROR] 环境变量 LOCALAPPDATA 未设置。", file=sys.stderr)
            sys.exit(1)
        return Path(local_app_data) / "nvim"
    else:
        # macOS / Linux
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        base = Path(xdg_config) if xdg_config else Path.home() / ".config"
        return base / "nvim"


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def print_tree(root: Path, indent: str = "") -> None:
    """递归打印目录树（仅用于 dry-run 预览）。"""
    for item in sorted(root.iterdir()):
        print(f"{indent}  {'📁' if item.is_dir() else '📄'} {item.name}")
        if item.is_dir():
            print_tree(item, indent + "  ")


def count_files(root: Path) -> int:
    """统计目录下的文件总数。"""
    return sum(1 for _ in root.rglob("*") if _.is_file())


# ── 核心操作 ──────────────────────────────────────────────────────────────────

def deploy(source: Path, target: Path, dry_run: bool) -> None:
    """
    将 source 目录内容覆盖到 target 目录。
    - 先备份 target（如果存在）
    - 再用 source 覆盖
    """
    file_count = count_files(source)

    print(f"源目录  : {source}")
    print(f"目标目录: {target}")
    print(f"文件数量: {file_count} 个文件")

    if dry_run:
        print("\n[DRY-RUN] 以下文件将被复制/覆盖：")
        print_tree(source)
        print("\n[DRY-RUN] 未做任何实际修改。使用 --dry-run 以外的选项执行部署。")
        return

    # 备份现有配置
    if target.exists():
        backup_dir = target.parent / f"{target.name}.backup"
        print(f"\n备份现有配置 → {backup_dir}")

        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(target, backup_dir)
        print(f"  ✓ 备份完成（{count_files(backup_dir)} 个文件）")

    # 删除目标目录，然后复制
    print(f"\n部署配置 → {target}")
    if target.exists():
        shutil.rmtree(target)

    shutil.copytree(source, target)
    print(f"  ✓ 部署完成（{count_files(target)} 个文件）")

    print(f"\n[完成] Neovim 配置已部署 ✓")
    if (target.parent / f"{target.name}.backup").exists():
        print(f"       旧配置已备份至 {target.parent / (target.name + '.backup')}")


# ── 入口 ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 nvim-config/ 部署到系统 Neovim 配置目录"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览操作但不实际执行（不修改任何文件）",
    )
    args = parser.parse_args()

    # 检查源目录
    if not SOURCE_DIR.exists():
        print(
            f"[ERROR] 源目录不存在: {SOURCE_DIR}\n"
            "请先在 nvim-config/ 下放入你的 Neovim 配置文件。",
            file=sys.stderr,
        )
        sys.exit(1)

    if not any(SOURCE_DIR.iterdir()):
        print(
            f"[ERROR] 源目录为空: {SOURCE_DIR}",
            file=sys.stderr,
        )
        sys.exit(1)

    target_dir = get_target_dir()

    print(f"{'═' * 60}")
    print("Neovim 配置部署工具")
    print(f"{'═' * 60}\n")

    deploy(
        source=SOURCE_DIR,
        target=target_dir,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
