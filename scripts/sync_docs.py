#!/usr/bin/env python3
"""
sync_docs.py — 拉取所有 git subtree 最新文档

用法:
    python scripts/sync_docs.py              # 拉取全部 subtree
    python scripts/sync_docs.py lazy-nvim    # 只拉取指定 subtree

配置文件: scripts/subtrees.json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


# ── 路径常量 ──────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = Path(__file__).resolve().parent / "subtrees.json"


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def load_config() -> dict:
    """读取 subtrees.json 配置文件。"""
    if not CONFIG_FILE.exists():
        print(f"[ERROR] 配置文件不存在: {CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)

    with CONFIG_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """执行命令，实时打印输出，失败时抛出异常。"""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def is_git_repo(path: Path) -> bool:
    """检查目录是否为 git 仓库。"""
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=path,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def subtree_prefix_exists(prefix: str, cwd: Path) -> bool:
    """检查 git subtree 的 prefix 目录是否已被跟踪（即是否已 add 过）。"""
    result = subprocess.run(
        ["git", "log", "--oneline", f"-- {prefix}"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


# ── 核心操作 ──────────────────────────────────────────────────────────────────

def sync_subtree(entry: dict, cwd: Path) -> None:
    """
    对单个 subtree 执行 pull（已存在）或 add（首次）。
    """
    name   = entry["name"]
    prefix = entry["prefix"]
    remote = entry["remote"]
    branch = entry["branch"]

    print(f"\n{'─' * 60}")
    print(f"[{name}]  {remote}  (branch: {branch})")
    print(f"  prefix: {prefix}")

    if subtree_prefix_exists(prefix, cwd):
        print("  状态: 已存在，执行 pull ...")
        run(
            ["git", "subtree", "pull",
             "--prefix", prefix,
             remote, branch,
             "--squash"],
            cwd=cwd,
        )
    else:
        print("  状态: 首次添加，执行 add ...")
        run(
            ["git", "subtree", "add",
             "--prefix", prefix,
             remote, branch,
             "--squash"],
            cwd=cwd,
        )

    print(f"  ✓ {name} 同步完成")


# ── 入口 ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="拉取 subtrees.json 中配置的所有 git subtree 最新文档"
    )
    parser.add_argument(
        "name",
        nargs="?",
        help="只同步指定名称的 subtree（省略则同步全部）",
    )
    args = parser.parse_args()

    # 检查是否在 git 仓库中
    if not is_git_repo(REPO_ROOT):
        print(
            f"[ERROR] {REPO_ROOT} 不是 git 仓库。\n"
            "请先执行 git init 并进行首次提交。",
            file=sys.stderr,
        )
        sys.exit(1)

    config = load_config()
    subtrees: list[dict] = config.get("subtrees", [])

    if not subtrees:
        print("[WARN] subtrees.json 中没有配置任何 subtree。")
        return

    # 过滤目标
    if args.name:
        targets = [e for e in subtrees if e["name"] == args.name]
        if not targets:
            names = [e["name"] for e in subtrees]
            print(
                f"[ERROR] 找不到名为 '{args.name}' 的 subtree。\n"
                f"可用名称: {names}",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        targets = subtrees

    print(f"准备同步 {len(targets)} 个 subtree（仓库根: {REPO_ROOT}）")

    failed: list[str] = []
    for entry in targets:
        try:
            sync_subtree(entry, cwd=REPO_ROOT)
        except subprocess.CalledProcessError:
            failed.append(entry["name"])
            print(f"  ✗ {entry['name']} 同步失败，继续处理下一个 ...")

    print(f"\n{'═' * 60}")
    if failed:
        print(f"[完成] 失败: {failed}")
        sys.exit(1)
    else:
        print(f"[完成] 全部 {len(targets)} 个 subtree 同步成功 ✓")


if __name__ == "__main__":
    main()
