#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
"""
deploy.py - 将 dotfiles/<tool>/ 部署到系统对应的配置目录

用法:
    uv run scripts/deploy.py nvim
    uv run scripts/deploy.py all
    uv run scripts/deploy.py nvim --dry-run
    uv run scripts/deploy.py all --dry-run

部署路径由 scripts/targets.toml 配置。
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOTFILES_DIR = REPO_ROOT / "dotfiles"
TARGETS_FILE = REPO_ROOT / "scripts" / "targets.toml"
ENV_VAR_RE = re.compile(r"%([^%]+)%")
IS_WINDOWS = platform.system() == "Windows"


def configure_stdio() -> None:
    """避免终端编码不支持某些字符时直接崩溃。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(errors="backslashreplace")


def load_targets() -> dict[str, dict[str, str]]:
    """加载 targets.toml 并返回 [targets] 配置。"""
    if not TARGETS_FILE.exists():
        print(f"[ERROR] 找不到配置文件: {TARGETS_FILE}", file=sys.stderr)
        raise SystemExit(1)

    try:
        with TARGETS_FILE.open("rb") as file:
            data = tomllib.load(file)
    except tomllib.TOMLDecodeError as exc:
        print(f"[ERROR] targets.toml 解析失败: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    targets = data.get("targets")
    if not isinstance(targets, dict):
        print("[ERROR] targets.toml 缺少 [targets] 配置。", file=sys.stderr)
        raise SystemExit(1)

    return targets


def expand_windows_env(path_str: str) -> str:
    """展开 %VAR% 形式的 Windows 环境变量。"""

    def replace(match: re.Match[str]) -> str:
        var_name = match.group(1)
        value = os.environ.get(var_name)
        if value is None:
            print(f"[ERROR] 环境变量未设置: %{var_name}%", file=sys.stderr)
            raise SystemExit(1)
        return value

    return ENV_VAR_RE.sub(replace, path_str)


def resolve_target(tool: str, targets: dict[str, dict[str, str]]) -> Path | None:
    """根据当前系统解析工具的目标路径。"""
    config = targets.get(tool)
    if config is None:
        print(f"[ERROR] targets.toml 中未找到工具: {tool}", file=sys.stderr)
        raise SystemExit(1)

    system = platform.system()
    if system == "Windows":
        path_str = config.get("windows")
        if path_str is None:
            print(f"[SKIP] {tool}: 当前系统是 Windows，但该工具没有 windows 目标。")
            return None
        return Path(expand_windows_env(path_str))

    path_str = config.get("unix")
    if path_str is None:
        print(f"[SKIP] {tool}: 当前系统 {system} 没有可用目标。")
        return None
    return Path(path_str).expanduser()


def _ps_escape(value: str) -> str:
    """将路径字符串转义为 PowerShell 单引号字面量。"""
    return value.replace("'", "''")


def run_powershell(script: str, *, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    """执行 PowerShell 脚本，失败时直接退出。"""
    wrapped_script = "$ErrorActionPreference = 'Stop'; " + script
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", wrapped_script],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "未知错误"
        error = error.splitlines()[-1]
        print(f"[ERROR] PowerShell 执行失败: {error}", file=sys.stderr)
        raise SystemExit(1)

    if not capture_output and result.stdout:
        print(result.stdout, end="")
    return result


def path_exists(path: Path) -> bool:
    """判断路径是否存在（Windows 下使用 PowerShell，避免 Python Store 虚拟化）。"""
    if not IS_WINDOWS:
        return path.exists() or path.is_symlink()

    escaped = _ps_escape(str(path))
    result = run_powershell(
        f"if (Test-Path -LiteralPath '{escaped}') {{ '1' }} else {{ '0' }}",
        capture_output=True,
    )
    return result.stdout.strip() == "1"


def path_is_dir(path: Path) -> bool:
    """判断路径是否为目录（Windows 下使用 PowerShell）。"""
    if not IS_WINDOWS:
        return path.is_dir()

    escaped = _ps_escape(str(path))
    result = run_powershell(
        f"if (Test-Path -LiteralPath '{escaped}' -PathType Container) {{ '1' }} else {{ '0' }}",
        capture_output=True,
    )
    return result.stdout.strip() == "1"


def ensure_dir(path: Path) -> None:
    """确保目录存在。"""
    if IS_WINDOWS:
        escaped = _ps_escape(str(path))
        run_powershell(f"New-Item -ItemType Directory -Force -Path '{escaped}' | Out-Null")
        return

    path.mkdir(parents=True, exist_ok=True)


def remove_path(path: Path) -> None:
    """删除文件或目录。"""
    if IS_WINDOWS:
        escaped = _ps_escape(str(path))
        run_powershell(
            f"if (Test-Path -LiteralPath '{escaped}') {{ Remove-Item -LiteralPath '{escaped}' -Recurse -Force }}"
        )
        return

    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def copy_path(source: Path, target: Path) -> None:
    """复制单个文件或目录。"""
    if IS_WINDOWS:
        source_escaped = _ps_escape(str(source))
        target_escaped = _ps_escape(str(target))

        if source.is_dir():
            run_powershell(
                f"Copy-Item -LiteralPath '{source_escaped}' -Destination '{target_escaped}' -Recurse -Force"
            )
            return

        parent_escaped = _ps_escape(str(target.parent))
        run_powershell(
            f"New-Item -ItemType Directory -Force -Path '{parent_escaped}' | Out-Null; "
            f"Copy-Item -LiteralPath '{source_escaped}' -Destination '{target_escaped}' -Force"
        )
        return

    if source.is_dir():
        shutil.copytree(source, target)
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def is_home_target(target: Path) -> bool:
    """判断目标是否为用户家目录，家目录只应做受限覆盖，不应整目录替换。"""
    try:
        return target.resolve() == Path.home().resolve()
    except OSError:
        return False


def backup_whole_target(target: Path) -> Path:
    """备份整个目标路径。"""
    backup_dir = target.parent / f"{target.name}.backup"
    if path_exists(backup_dir):
        remove_path(backup_dir)
    copy_path(target, backup_dir)
    return backup_dir


def backup_managed_entries(source: Path, target: Path) -> Path | None:
    """仅备份 source 顶层会覆盖到的目标项，用于家目录类目标。"""
    backup_dir = target / ".dotfiles-wiki-backup"
    if path_exists(backup_dir):
        remove_path(backup_dir)

    if not backup_path_tree(source, target, backup_dir):
        return None

    return backup_dir


def backup_path_tree(source: Path, target: Path, backup: Path) -> bool:
    """递归备份将被覆盖的受管理路径。"""
    backed_up = False

    for item in source.iterdir():
        destination = target / item.name
        backup_path = backup / item.name

        if item.is_dir() and not item.is_symlink() and path_is_dir(destination) and not destination.is_symlink():
            if backup_path_tree(item, destination, backup_path):
                backed_up = True
            continue

        if not path_exists(destination) and not destination.is_symlink():
            continue

        copy_path(destination, backup_path)
        backed_up = True

    return backed_up


def deploy_into_existing_dir(source: Path, target: Path) -> None:
    """将 source 内容复制到现有目录，仅覆盖受管理的条目。"""
    ensure_dir(target)

    for item in source.iterdir():
        destination = target / item.name
        if item.is_dir() and not item.is_symlink():
            if destination.is_symlink() or (path_exists(destination) and not path_is_dir(destination)):
                remove_path(destination)
            copy_path(item, destination)
            continue

        if path_exists(destination) or destination.is_symlink():
            remove_path(destination)
        copy_path(item, destination)


def deploy_tool(tool: str, targets: dict[str, dict[str, str]], dry_run: bool) -> bool:
    """部署单个工具。True 表示完成，False 表示跳过。"""
    source = DOTFILES_DIR / tool
    if not source.exists():
        print(f"[SKIP] {tool}: 源目录不存在: {source}")
        return False

    if not any(source.iterdir()):
        print(f"[SKIP] {tool}: 源目录为空: {source}")
        return False

    target = resolve_target(tool, targets)
    if target is None:
        return False

    print("\n" + "-" * 60)
    print(f"工具      : {tool}")
    print(f"源目录    : {source}")
    print(f"目标路径  : {target}")

    if dry_run:
        print("[DRY-RUN] 未执行任何实际写入。")
        return True

    ensure_dir(target.parent)

    if is_home_target(target):
        backup_dir = backup_managed_entries(source, target)
        if backup_dir is not None:
            print(f"备份路径  : {backup_dir}")
        else:
            print("备份路径  : 无需备份（目标中不存在受管理条目）")

        deploy_into_existing_dir(source, target)
    else:
        if path_exists(target) or target.is_symlink():
            backup_dir = backup_whole_target(target)
            print(f"备份路径  : {backup_dir}")
            remove_path(target)

        copy_path(source, target)

    print(f"部署完成  : {target}")
    return True


def main() -> None:
    configure_stdio()

    parser = argparse.ArgumentParser(
        description="将 dotfiles/<tool>/ 部署到系统配置目录。",
        epilog="示例: uv run scripts/deploy.py nvim --dry-run",
    )
    parser.add_argument("tool", help="要部署的工具名，或 all 表示部署全部工具")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只预览操作，不执行实际写入",
    )
    args = parser.parse_args()

    targets = load_targets()

    print("=" * 60)
    print("Dotfiles 部署工具")
    if args.dry_run:
        print("模式      : DRY-RUN")
    print("=" * 60)

    if args.tool == "all":
        deployed = 0
        skipped = 0
        for tool in targets:
            if deploy_tool(tool, targets, dry_run=args.dry_run):
                deployed += 1
            else:
                skipped += 1

        print("\n" + "=" * 60)
        if args.dry_run:
            print(f"[DRY-RUN 完成] 可部署 {deployed} 个工具，跳过 {skipped} 个。")
        else:
            print(f"[完成] 已部署 {deployed} 个工具，跳过 {skipped} 个。")
        return

    tool = args.tool
    if tool not in targets:
        print(
            f"[ERROR] 未知工具: {tool}\n可用工具: {', '.join(targets.keys())}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    ok = deploy_tool(tool, targets, dry_run=args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"[DRY-RUN 完成] {tool} 预览结束。")
    elif ok:
        print(f"[完成] {tool} 已部署。")
    else:
        print(f"[跳过] {tool} 未部署。")


if __name__ == "__main__":
    main()
