#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
"""
sync_docs.py — 基于 raw/manifest.toml 下载并管理外部文档

支持三种来源类型（由 manifest.toml 中 type 字段决定）：

  github-dir   下载 GitHub 仓库中某个子目录（通过 zip archive）
  github-repo  下载整个 GitHub 仓库（通过 zip archive）
  url          直接下载单个文件（raw URL）

用法:
    uv run scripts/sync_docs.py                         # 同步全部
    uv run scripts/sync_docs.py <name>                  # 同步单个
    uv run scripts/sync_docs.py --update <name> <ref>   # 更新某个来源的 ref 并立即同步
    uv run scripts/sync_docs.py --list                  # 查看所有来源的当前版本

配置文件: raw/manifest.toml
下载目录: raw/<prefix>（整个 raw/ 已在 .gitignore 中，manifest.toml 除外）
"""

from __future__ import annotations

import argparse
import io
import shutil
import sys
import tomllib
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_FILE = REPO_ROOT / "raw" / "manifest.toml"

DEFAULT_MANIFEST_COMMENT = "raw/ 文档来源清单。由 scripts/sync_docs.py 读取，执行下载与更新。"
DEFAULT_USAGE = {
    "sync_all": "uv run scripts/sync_docs.py",
    "sync_one": "uv run scripts/sync_docs.py <name>",
    "update_ref": "uv run scripts/sync_docs.py --update <name> <ref>",
    "list_status": "uv run scripts/sync_docs.py --list",
}
DEFAULT_TYPES = {
    "github-dir": "下载 GitHub 仓库中的某个子目录（通过 zip archive）",
    "github-repo": "下载整个 GitHub 仓库（通过 zip archive）",
    "url": "直接下载单个文件（raw URL）",
}
SOURCE_FIELD_ORDER = (
    "comment",
    "name",
    "category",
    "type",
    "repo",
    "path",
    "url",
    "ref",
    "prefix",
    "last_synced",
)


def load_manifest() -> dict[str, Any]:
    """加载 manifest.toml。"""
    if not MANIFEST_FILE.exists():
        print(f"[ERROR] manifest 不存在: {MANIFEST_FILE}", file=sys.stderr)
        sys.exit(1)

    try:
        with MANIFEST_FILE.open("rb") as file:
            manifest = tomllib.load(file)
    except tomllib.TOMLDecodeError as exc:
        print(f"[ERROR] manifest.toml 解析失败: {exc}", file=sys.stderr)
        sys.exit(1)

    manifest.setdefault("comment", DEFAULT_MANIFEST_COMMENT)
    manifest.setdefault("usage", DEFAULT_USAGE.copy())
    manifest.setdefault("types", DEFAULT_TYPES.copy())
    manifest.setdefault("sources", [])
    return manifest


def save_manifest(manifest: dict[str, Any]) -> None:
    """按固定格式回写 manifest.toml。"""
    comment = manifest.get("comment", DEFAULT_MANIFEST_COMMENT)
    usage = {**DEFAULT_USAGE, **manifest.get("usage", {})}
    source_types = {**DEFAULT_TYPES, **manifest.get("types", {})}

    lines = [f"comment = {format_toml_value(comment)}", ""]
    lines.extend(render_toml_table("usage", usage))
    lines.append("")
    lines.extend(render_toml_table("types", source_types))

    for source in get_sources(manifest):
        lines.append("")
        lines.append("[[sources]]")
        for key in ordered_keys(source, SOURCE_FIELD_ORDER):
            lines.append(f"{format_toml_key(key)} = {format_toml_value(source[key])}")

    MANIFEST_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_sources(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return manifest.get("sources", [])


def find_source(manifest: dict[str, Any], name: str) -> dict[str, Any] | None:
    return next((source for source in get_sources(manifest) if source["name"] == name), None)


def format_toml_key(key: str) -> str:
    if key.replace("-", "").replace("_", "").isalnum():
        return key
    return format_toml_value(key)


def format_toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        escaped = (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\b", "\\b")
            .replace("\t", "\\t")
            .replace("\n", "\\n")
            .replace("\f", "\\f")
            .replace("\r", "\\r")
        )
        return f'"{escaped}"'
    if isinstance(value, list):
        return "[" + ", ".join(format_toml_value(item) for item in value) + "]"

    raise TypeError(f"不支持写入 TOML 的值类型: {type(value).__name__}")


def ordered_keys(data: dict[str, Any], preferred_order: tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for key in preferred_order:
        if key in data:
            result.append(key)
            seen.add(key)

    for key in data:
        if key not in seen:
            result.append(key)

    return result


def render_toml_table(table_name: str, data: dict[str, Any]) -> list[str]:
    lines = [f"[{table_name}]"]
    for key in data:
        lines.append(f"{format_toml_key(key)} = {format_toml_value(data[key])}")
    return lines


def http_get_bytes(url: str) -> bytes:
    """下载 URL 内容，返回原始字节。失败时打印错误并抛出。"""
    print(f"  GET {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "sync_docs/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}: {url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"网络错误: {exc.reason}") from exc


def sync_github_dir(source: dict[str, Any]) -> None:
    """下载 GitHub 仓库中的某个子目录。"""
    repo = source["repo"]
    path = source["path"].strip("/")
    ref = source["ref"]
    target = REPO_ROOT / source["prefix"]

    data = fetch_zip_with_fallback(repo, ref)

    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        if not names:
            raise RuntimeError("zip 内容为空")

        top_dir = names[0].split("/")[0] + "/"
        prefix_in_zip = top_dir + path + "/"
        members = [name for name in names if name.startswith(prefix_in_zip) and not name.endswith("/")]

        if not members:
            raise RuntimeError(
                f"zip 中未找到路径 '{path}'，请检查 manifest.toml 中的 path 字段。\n"
                f"  仓库: {repo}  ref: {ref}"
            )

        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)

        for member in members:
            relative_path = member[len(prefix_in_zip):]
            if not relative_path:
                continue
            destination = target / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(member))

    file_count = sum(1 for path in target.rglob("*") if path.is_file())
    print(f"  已写入 {source['prefix']}（{file_count} 个文件）")


def sync_github_repo(source: dict[str, Any]) -> None:
    """下载整个 GitHub 仓库到 prefix 目录。"""
    repo = source["repo"]
    ref = source["ref"]
    target = REPO_ROOT / source["prefix"]

    data = fetch_zip_with_fallback(repo, ref)

    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        if not names:
            raise RuntimeError("zip 内容为空")

        top_dir = names[0].split("/")[0] + "/"

        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)

        for member in names:
            if member.endswith("/"):
                continue
            relative_path = member[len(top_dir):]
            if not relative_path:
                continue
            destination = target / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(member))

    file_count = sum(1 for path in target.rglob("*") if path.is_file())
    print(f"  已写入 {source['prefix']}（{file_count} 个文件）")


def sync_url(source: dict[str, Any]) -> None:
    """直接下载单个文件到 prefix。"""
    url = source["url"]
    target = REPO_ROOT / source["prefix"]

    data = http_get_bytes(url)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"  已写入 {source['prefix']}（{len(data)} 字节）")


def fetch_zip_with_fallback(repo: str, ref: str) -> bytes:
    """
    尝试 branch 和 tag 两种 zip URL，返回成功的那个。
    优先 heads/{ref}，失败则尝试 tags/{ref}。
    """
    branch_url = f"https://github.com/{repo}/archive/refs/heads/{ref}.zip"
    tag_url = f"https://github.com/{repo}/archive/refs/tags/{ref}.zip"

    try:
        return http_get_bytes(branch_url)
    except RuntimeError:
        pass

    print(f"  branch/{ref} 不存在，尝试 tag/{ref} ...")
    return http_get_bytes(tag_url)


def sync_one(source: dict[str, Any], manifest: dict[str, Any]) -> None:
    name = source["name"]
    source_type = source.get("type", "github-dir")

    print(f"\n{'─' * 60}")
    print(f"[{name}]  type={source_type}  ref={source.get('ref', '-')}")
    if "repo" in source:
        print(f"  repo   : {source['repo']}")
    if "path" in source:
        print(f"  path   : {source['path']}")
    print(f"  prefix : {source['prefix']}")

    if source_type == "github-dir":
        sync_github_dir(source)
    elif source_type == "github-repo":
        sync_github_repo(source)
    elif source_type == "url":
        sync_url(source)
    else:
        raise ValueError(f"未知的 type: {source_type!r}")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for item in get_sources(manifest):
        if item["name"] == name:
            item["last_synced"] = now
            break
    save_manifest(manifest)

    print(f"  [OK] {name} 同步完成（{now}）")


def cmd_list(manifest: dict[str, Any]) -> None:
    """打印所有来源的当前状态。"""
    sources = get_sources(manifest)
    if not sources:
        print("manifest 中没有配置任何来源。")
        return

    column = "{:<20} {:<12} {:<30} {:<12} {}"
    print(column.format("name", "type", "repo / url", "ref", "last_synced"))
    print("─" * 90)
    for source in sources:
        repo_or_url = source.get("repo", source.get("url", "-"))
        path_hint = f"  [{source['path']}]" if "path" in source else ""
        print(
            column.format(
                source["name"],
                source.get("type", "github-dir"),
                repo_or_url + path_hint,
                source.get("ref", "-"),
                source.get("last_synced") or "从未同步",
            )
        )


def cmd_update_ref(manifest: dict[str, Any], name: str, ref: str) -> None:
    """更新某个来源的 ref，然后立即同步。"""
    source = find_source(manifest, name)
    if source is None:
        names = [item["name"] for item in get_sources(manifest)]
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
            names = [item["name"] for item in sources]
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
        except Exception as exc:
            failed.append(source["name"])
            print(f"  [FAIL] {source['name']} 同步失败: {exc}")

    print(f"\n{'═' * 60}")
    if failed:
        print(f"[完成] 失败: {failed}")
        sys.exit(1)

    print(f"[完成] 全部 {len(targets)} 个来源同步成功 [OK]")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="基于 raw/manifest.toml 下载并管理外部文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  uv run scripts/sync_docs.py                        # 同步全部
  uv run scripts/sync_docs.py neovim-docs            # 只同步 neovim-docs
  uv run scripts/sync_docs.py --update neovim-docs stable  # 更新 ref 并同步
  uv run scripts/sync_docs.py --list                 # 查看所有来源状态
        """,
    )

    parser.add_argument("name", nargs="?", help="只同步指定名称的来源（省略则同步全部）")
    parser.add_argument(
        "--update",
        nargs=2,
        metavar=("NAME", "REF"),
        help="更新指定来源的 ref（tag / branch / commit SHA），然后立即同步",
    )
    parser.add_argument("--list", action="store_true", help="列出所有来源及其当前版本")

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
