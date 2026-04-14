#!/usr/bin/env python3
"""
sync_docs.py — 基于 raw/manifest.json 下载并管理外部文档

支持三种来源类型（由 manifest.json 中 type 字段决定）：

  github-dir   下载 GitHub 仓库中某个子目录（通过 zip archive）
  github-repo  下载整个 GitHub 仓库（通过 zip archive）
  url          直接下载单个文件（raw URL）

用法:
    python scripts/sync_docs.py                         # 同步全部
    python scripts/sync_docs.py <name>                  # 同步单个
    python scripts/sync_docs.py --update <name> <ref>   # 更新某个来源的 ref 并立即同步
    python scripts/sync_docs.py --list                  # 查看所有来源的当前版本

配置文件: raw/manifest.json
下载目录: raw/<prefix>（整个 raw/ 已在 .gitignore 中，manifest.json 除外）
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── 路径常量 ──────────────────────────────────────────────────────────────────

REPO_ROOT     = Path(__file__).resolve().parent.parent
MANIFEST_FILE = REPO_ROOT / "raw" / "manifest.json"


# ── Manifest 读写 ─────────────────────────────────────────────────────────────

def load_manifest() -> dict[str, Any]:
    if not MANIFEST_FILE.exists():
        print(f"[ERROR] manifest 不存在: {MANIFEST_FILE}", file=sys.stderr)
        sys.exit(1)
    with MANIFEST_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest: dict[str, Any]) -> None:
    with MANIFEST_FILE.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")


def get_sources(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return manifest.get("sources", [])


def find_source(manifest: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((s for s in get_sources(manifest) if s["name"] == name), None)


# ── HTTP 工具 ─────────────────────────────────────────────────────────────────

def http_get_bytes(url: str) -> bytes:
    """下载 URL 内容，返回原始字节。失败时打印错误并抛出。"""
    print(f"  GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "sync_docs/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {url}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}") from e


# ── 各来源类型的下载逻辑 ──────────────────────────────────────────────────────

def sync_github_dir(source: dict[str, Any]) -> None:
    """
    下载 GitHub 仓库中某个子目录。

    原理：
      1. 通过 {repo}/zipball/{ref} 获取整个仓库的 zip archive
      2. 从 zip 中只提取 {path}/ 下的文件
      3. 写入 prefix 目录（先清空）
    """
    repo   = source["repo"]
    path   = source["path"].strip("/")
    ref    = source["ref"]
    target = REPO_ROOT / source["prefix"]

    url = f"https://github.com/{repo}/archive/refs/heads/{ref}.zip"
    # 如果 ref 看起来像 tag（包含 '.' 且不是 branch 名），用 tags/ 前缀
    if "/" not in ref and not ref.startswith("v") is False:
        # 尝试 tag 路径，fallback 到 branch 路径
        pass  # 默认先用 heads/，后面有 tag fallback

    data = _fetch_zip_with_fallback(repo, ref)

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        # zip 内的顶层目录形如 {repo_name}-{ref}/ 或 {repo_name}-{sha}/
        names = zf.namelist()
        if not names:
            raise RuntimeError("zip 内容为空")

        top_dir = names[0].split("/")[0] + "/"
        prefix_in_zip = top_dir + path + "/"

        members = [n for n in names if n.startswith(prefix_in_zip) and not n.endswith("/")]
        if not members:
            raise RuntimeError(
                f"zip 中未找到路径 '{path}'，请检查 manifest.json 中的 path 字段。\n"
                f"  仓库: {repo}  ref: {ref}"
            )

        # 清空目标目录
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)

        for member in members:
            # 去掉顶层目录和 path 前缀，保留相对路径
            rel = member[len(prefix_in_zip):]
            if not rel:
                continue
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(zf.read(member))

    file_count = sum(1 for _ in target.rglob("*") if _.is_file())
    print(f"  已写入 {source['prefix']}（{file_count} 个文件）")


def sync_github_repo(source: dict[str, Any]) -> None:
    """下载整个 GitHub 仓库到 prefix 目录。"""
    repo   = source["repo"]
    ref    = source["ref"]
    target = REPO_ROOT / source["prefix"]

    data = _fetch_zip_with_fallback(repo, ref)

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
        if not names:
            raise RuntimeError("zip 内容为空")

        top_dir = names[0].split("/")[0] + "/"

        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)

        for member in zf.namelist():
            if member.endswith("/"):
                continue
            rel = member[len(top_dir):]
            if not rel:
                continue
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(zf.read(member))

    file_count = sum(1 for _ in target.rglob("*") if _.is_file())
    print(f"  已写入 {source['prefix']}（{file_count} 个文件）")


def sync_url(source: dict[str, Any]) -> None:
    """直接下载单个文件到 prefix（视为目标文件路径）。"""
    url    = source["url"]
    target = REPO_ROOT / source["prefix"]

    data = http_get_bytes(url)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"  已写入 {source['prefix']}（{len(data)} 字节）")


def _fetch_zip_with_fallback(repo: str, ref: str) -> bytes:
    """
    尝试 branch 和 tag 两种 zip URL，返回成功的那个。
    优先 heads/{ref}，失败则尝试 tags/{ref}。
    """
    branch_url = f"https://github.com/{repo}/archive/refs/heads/{ref}.zip"
    tag_url    = f"https://github.com/{repo}/archive/refs/tags/{ref}.zip"

    try:
        return http_get_bytes(branch_url)
    except RuntimeError:
        pass

    print(f"  branch/{ref} 不存在，尝试 tag/{ref} ...")
    return http_get_bytes(tag_url)


# ── 同步入口 ──────────────────────────────────────────────────────────────────

def sync_one(source: dict[str, Any], manifest: dict[str, Any]) -> None:
    name = source["name"]
    typ  = source.get("type", "github-dir")

    print(f"\n{'─' * 60}")
    print(f"[{name}]  type={typ}  ref={source.get('ref', '-')}")
    if "repo" in source:
        print(f"  repo   : {source['repo']}")
    if "path" in source:
        print(f"  path   : {source['path']}")
    print(f"  prefix : {source['prefix']}")

    if typ == "github-dir":
        sync_github_dir(source)
    elif typ == "github-repo":
        sync_github_repo(source)
    elif typ == "url":
        sync_url(source)
    else:
        raise ValueError(f"未知的 type: {typ!r}")

    # 更新 last_synced
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for s in get_sources(manifest):
        if s["name"] == name:
            s["last_synced"] = now
            break
    save_manifest(manifest)

    print(f"  [OK] {name} 同步完成（{now}）")


# ── 子命令实现 ────────────────────────────────────────────────────────────────

def cmd_list(manifest: dict[str, Any]) -> None:
    """打印所有来源的当前状态。"""
    sources = get_sources(manifest)
    if not sources:
        print("manifest 中没有配置任何来源。")
        return

    col = "{:<20} {:<12} {:<30} {:<12} {}"
    print(col.format("name", "type", "repo / url", "ref", "last_synced"))
    print("─" * 90)
    for s in sources:
        repo_or_url = s.get("repo", s.get("url", "-"))
        path_hint   = f"  [{s['path']}]" if "path" in s else ""
        print(col.format(
            s["name"],
            s.get("type", "github-dir"),
            repo_or_url + path_hint,
            s.get("ref", "-"),
            s.get("last_synced") or "从未同步",
        ))


def cmd_update_ref(manifest: dict[str, Any], name: str, ref: str) -> None:
    """更新某个来源的 ref，然后立即同步。"""
    source = find_source(manifest, name)
    if source is None:
        names = [s["name"] for s in get_sources(manifest)]
        print(f"[ERROR] 找不到来源 '{name}'。可用名称: {names}", file=sys.stderr)
        sys.exit(1)

    old_ref = source.get("ref", "-")
    source["ref"] = ref
    save_manifest(manifest)
    print(f"[{name}] ref 已更新: {old_ref} → {ref}")

    sync_one(source, manifest)


def cmd_sync(manifest: dict[str, Any], name: str | None) -> None:
    """同步一个或全部来源。"""
    sources = get_sources(manifest)
    if not sources:
        print("[WARN] manifest 中没有配置任何来源。")
        return

    if name:
        source = find_source(manifest, name)
        if source is None:
            names = [s["name"] for s in sources]
            print(f"[ERROR] 找不到来源 '{name}'。可用名称: {names}", file=sys.stderr)
            sys.exit(1)
        targets = [source]
    else:
        targets = sources

    print(f"{'═' * 60}")
    print(f"准备同步 {len(targets)} 个来源")
    print(f"{'═' * 60}")

    failed: list[str] = []
    for source in targets:
        try:
            sync_one(source, manifest)
        except Exception as e:
            failed.append(source["name"])
            print(f"  [FAIL] {source['name']} 同步失败: {e}")

    print(f"\n{'═' * 60}")
    if failed:
        print(f"[完成] 失败: {failed}")
        sys.exit(1)
    else:
        print(f"[完成] 全部 {len(targets)} 个来源同步成功 [OK]")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="基于 raw/manifest.json 下载并管理外部文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/sync_docs.py                        # 同步全部
  python scripts/sync_docs.py lazy-nvim              # 只同步 lazy-nvim
  python scripts/sync_docs.py --update lazy-nvim v11.17.0  # 更新 ref 并同步
  python scripts/sync_docs.py --list                 # 查看所有来源状态
        """,
    )

    parser.add_argument(
        "name",
        nargs="?",
        help="只同步指定名称的来源（省略则同步全部）",
    )
    parser.add_argument(
        "--update",
        nargs=2,
        metavar=("NAME", "REF"),
        help="更新指定来源的 ref（tag / branch / commit SHA），然后立即同步",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有来源及其当前版本",
    )

    args = parser.parse_args()

    manifest = load_manifest()

    if args.list:
        cmd_list(manifest)
    elif args.update:
        name, ref = args.update
        cmd_update_ref(manifest, name, ref)
    else:
        cmd_sync(manifest, args.name)


if __name__ == "__main__":
    main()
