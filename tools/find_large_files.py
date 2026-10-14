#!/usr/bin/env python3
"""列出指定目录(缺省为脚本所在目录的上级目录)及其子目录下超过阈值(默认 100MB)的文件。

位于 git 工作区内时通过 git ls-files 取文件清单,自动跳过 .git 并遵守 .gitignore /
.git/info/exclude / 全局 excludes;不在 git 工作区(或 git 不可用)时退回 os.walk,但仍跳过 .git。
"""

import argparse
import os
import subprocess
import sys

UNITS = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}


def parse_size(text):
    """把 '100MB' / '1.5G' / '2048' 这类写法换算成字节。"""
    s = text.strip().upper().replace(" ", "")
    for suffix in ("TB", "GB", "MB", "KB", "B"):
        if s.endswith(suffix):
            number = s[: -len(suffix)]
            return int(float(number) * UNITS[suffix])
    return int(float(s))


def human(size):
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:,.2f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024


def use_git(root, force_off):
    """判断能否用 git 列举文件,返回 (是否使用 git, 原因说明)。"""
    if force_off:
        return False, "普通遍历(--no-git)"
    try:
        probe = subprocess.run(
            ["git", "-C", root, "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False, "普通遍历(未找到 git)"
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return False, "普通遍历(不在 git 工作区内)"
    return True, "git ls-files(已应用 .gitignore,跳过 .git)"


def paths_from_git(root):
    """git 索引里的文件 + 未被忽略的未跟踪文件。"""
    listed = subprocess.run(
        ["git", "-C", root, "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        capture_output=True,
    )
    if listed.returncode != 0:
        raise OSError(listed.stderr.decode("utf-8", "replace").strip() or "git ls-files 失败")
    for raw in listed.stdout.split(b"\0"):
        if raw:
            yield os.path.join(root, os.fsdecode(raw).replace("/", os.sep))


def paths_from_walk(root):
    """深度优先遍历,不跟随符号链接,并跳过 .git 目录。"""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d != ".git" and not os.path.islink(os.path.join(dirpath, d))]
        for name in filenames:
            path = os.path.join(dirpath, name)
            if not os.path.islink(path):
                yield path


def find_files(root, minimum, git_mode):
    source = paths_from_git(root) if git_mode else paths_from_walk(root)
    matches = []
    for path in source:
        try:
            size = os.stat(path, follow_symlinks=False).st_size
        except FileNotFoundError:
            continue  # git 索引里仍在册、磁盘上已删除的文件
        except OSError as exc:
            print(f"跳过无法访问的文件 {path}: {exc}", file=sys.stderr)
            continue
        if size > minimum:
            matches.append((size, path))
    return matches


def main():
    default_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(
        description="列出目录下超过指定大小的文件",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("directory", nargs="?", default=default_dir, help="要扫描的根目录,省略时使用脚本所在目录的上级目录")
    parser.add_argument("-s", "--min-size", default="100MB", help="大小阈值,支持 B/KB/MB/GB/TB")
    parser.add_argument("--asc", action="store_true", help="按大小升序排列(默认降序)")
    parser.add_argument("--no-git", action="store_true", help="即使处于 git 工作区也用普通遍历,不应用 .gitignore")
    args = parser.parse_args()

    root = os.path.abspath(args.directory)
    if not os.path.isdir(root):
        parser.error(f"不是有效目录: {root}")

    git_mode, mode_note = use_git(root, args.no_git)
    minimum = parse_size(args.min_size)
    try:
        matches = find_files(root, minimum, git_mode)
    except OSError as exc:
        print(f"git ls-files 失败,改用普通遍历: {exc}", file=sys.stderr)
        matches = find_files(root, minimum, git_mode=False)
        mode_note = "普通遍历(git ls-files 失败后回退)"
    matches.sort(key=lambda item: item[0], reverse=not args.asc)

    for size, path in matches:
        print(f"{human(size):>14}  {path}")

    sys.stdout.flush()
    total = sum(size for size, _ in matches)
    print(
        f"\n共 {len(matches)} 个文件超过 {human(minimum)}  ({minimum:,} 字节),"
        f" 合计 {human(total)}  ({total:,} 字节)\n位置: {root}\n模式: {mode_note}",
        file=sys.stderr,
    )
    return 0 if matches else 1


if __name__ == "__main__":
    sys.exit(main())
