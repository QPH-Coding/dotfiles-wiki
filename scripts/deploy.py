#!/usr/bin/env python3
"""
deploy.py — 将 dotfiles/<tool>/ 部署到系统对应配置目录

用法:
    python scripts/deploy.py nvim              # 部署单个工具
    python scripts/deploy.py all               # 部署所有工具
    python scripts/deploy.py nvim --dry-run    # 预览，不实际写入
    python scripts/deploy.py all --dry-run     # 预览所有工具

部署路径由 scripts/targets.json 配置。
源目录: <仓库根>/dotfiles/<tool>/
"""

import argparse
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path
from typing import Optional


# ── 路径常量 ──────────────────────────────────────────────────────────────────

REPO_ROOT    = Path(__file__).resolve().parent.parent
DOTFILES_DIR = REPO_ROOT / "dotfiles"
TARGETS_FILE = REPO_ROOT / "scripts" / "targets.json"


# ── 配置加载 ──────────────────────────────────────────────────────────────────

def load_targets() -> dict:
    """加载 targets.json，返回 targets 字典。"""
    if not TARGETS_FILE.exists():
        print(f"[ERROR] 找不到配置文件: {TARGETS_FILE}", file=sys.stderr)
        sys.exit(1)

    with TARGETS_FILE.open(encoding="utf-8") as f:
        data = json.load(f)

    return data.get("targets", {})


# ── 路径解析 ──────────────────────────────────────────────────────────────────

_ENV_VAR_RE = re.compile(r"%([^%]+)%")


def _expand_windows_env(path_str: str) -> str:
    """将 %VAR% 形式的 Windows 环境变量展开为实际值。"""
    def replace(match: re.Match) -> str:
        var = match.group(1)
        value = os.environ.get(var)
        if value is None:
            print(f"[ERROR] 环境变量未设置: %{var}%", file=sys.stderr)
            sys.exit(1)
        return value

    return _ENV_VAR_RE.sub(replace, path_str)


def resolve_target(tool: str, targets: dict) -> Optional[Path]:
    """
    根据当前操作系统解析工具的部署目标路径。
    若当前系统不支持该工具，返回 None 并打印警告。
    """
    config = targets.get(tool)
    if config is None:
        print(f"[ERROR] targets.json 中未找到工具: {tool}", file=sys.stderr)
        sys.exit(1)

    system = platform.system()
    if system == "Windows":
        path_str = config.get("windows")
        if path_str is None:
            print(f"[SKIP] {tool}: 不支持 Windows，跳过。")
            return None
        return Path(_expand_windows_env(path_str))
    else:
        path_str = config.get("unix")
        if path_str is None:
            print(f"[SKIP] {tool}: 不支持当前系统（{system}），跳过。")
            return None
        return Path(path_str).expanduser()


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def print_tree(root: Path, indent: str = "") -> None:
    """递归打印目录树（仅用于 dry-run 预览）。"""
    for item in sorted(root.iterdir()):
        marker = "[dir]" if item.is_dir() else "[file]"
        print(f"{indent}  {marker} {item.name}")
        if item.is_dir():
            print_tree(item, indent + "  ")


def count_files(root: Path) -> int:
    """统计目录下的文件总数。"""
    return sum(1 for p in root.rglob("*") if p.is_file())


# ── 核心操作 ──────────────────────────────────────────────────────────────────

def deploy_tool(tool: str, targets: dict, dry_run: bool) -> bool:
    """
    部署单个工具。返回 True 表示成功（或 dry-run），False 表示跳过。
    """
    source = DOTFILES_DIR / tool
    if not source.exists():
        print(f"[SKIP] {tool}: 源目录不存在 ({source})，跳过。")
        return False

    if not any(source.iterdir()):
        print(f"[SKIP] {tool}: 源目录为空 ({source})，跳过。")
        return False

    target = resolve_target(tool, targets)
    if target is None:
        return False

    file_count = count_files(source)
    print(f"\n{'─' * 50}")
    print(f"工具    : {tool}")
    print(f"源目录  : {source}")
    print(f"目标目录: {target}")
    print(f"文件数量: {file_count} 个文件")

    if dry_run:
        print("\n[DRY-RUN] 将要复制的文件：")
        print_tree(source)
        print("[DRY-RUN] 未做任何实际修改。")
        return True

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

    return True


# ── 入口 ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 dotfiles/<tool>/ 部署到系统配置目录",
        epilog="示例: python scripts/deploy.py nvim --dry-run",
    )
    parser.add_argument(
        "tool",
        help="要部署的工具名称，或 'all' 部署所有工具",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览操作但不实际执行（不修改任何文件）",
    )
    args = parser.parse_args()

    targets = load_targets()

    print(f"{'═' * 50}")
    print("DotFile-Wiki 配置部署工具")
    mode_label = "（DRY-RUN 模式）" if args.dry_run else ""
    print(f"{'═' * 50}{mode_label}\n")

    if args.tool == "all":
        deployed = 0
        skipped = 0
        for tool in targets:
            ok = deploy_tool(tool, targets, dry_run=args.dry_run)
            if ok:
                deployed += 1
            else:
                skipped += 1

        print(f"\n{'═' * 50}")
        if args.dry_run:
            print(f"[DRY-RUN 完成] 共 {deployed} 个工具可部署，{skipped} 个跳过。")
        else:
            print(f"[完成] 已部署 {deployed} 个工具，{skipped} 个跳过。✓")
    else:
        tool = args.tool
        if tool not in targets:
            print(
                f"[ERROR] 未知工具: '{tool}'\n"
                f"可用工具: {', '.join(targets.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)

        ok = deploy_tool(tool, targets, dry_run=args.dry_run)

        print(f"\n{'═' * 50}")
        if args.dry_run:
            print(f"[DRY-RUN 完成] {tool} 预览结束，未做任何修改。")
        elif ok:
            print(f"[完成] {tool} 配置已部署 ✓")
        else:
            print(f"[跳过] {tool} 未部署（见上方提示）。")


if __name__ == "__main__":
    main()
