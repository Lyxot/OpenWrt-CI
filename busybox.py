#!/usr/bin/env python3
"""Enable safe BusyBox defaults referenced by the selected BusyBox applets."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SOURCE_RE = re.compile(r'^\s*(source|rsource|osource|orsource)\s+"?([^"\s]+)"?')
DEFAULT_RE = re.compile(r"^\s*default\s+(BUSYBOX_DEFAULT_[A-Za-z0-9_]+)\b")
CONFIG_RE = re.compile(r"^\s*(?:menu)?config\s+(\S+)")
VALUE_RE = re.compile(r"^(\s*default\s+)(\S+)(.*)$")

SOURCE_EXCLUDES = (
    "archival",
    "init",
    "mailutils",
    "networking",
    "selinux",
    "sysklogd",
)

CONFIG_EXCLUDES = (
    "_FEATURE_",
    "_BEEP",
    "_DEVFSD",
    "BUSYBOX_DEFAULT_LSBLK",
)


def source_files(config_in: Path) -> list[Path]:
    """Return recursively sourced Kconfig files, excluding risky applet groups."""
    source_root = config_in.resolve().parent
    pending = [config_in.resolve()]
    visited: set[Path] = set()
    result: list[Path] = []

    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)

        try:
            lines = current.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            continue

        for line in lines:
            match = SOURCE_RE.match(line)
            if not match or "$" in match.group(2):
                continue
            directive, source_path = match.groups()
            bases = [current.parent]
            if directive not in {"rsource", "orsource"} and current.parent != source_root:
                bases = [source_root, current.parent]
            candidates = [(base / source_path).resolve() for base in bases]
            child = next((path for path in candidates if path.is_file()), candidates[0])
            try:
                relative_parts = child.relative_to(source_root).parts
            except ValueError:
                relative_parts = child.parts
            if any(part in SOURCE_EXCLUDES for part in relative_parts):
                continue
            if child.is_file():
                result.append(child)
                pending.append(child)

    return list(dict.fromkeys(result))


def referenced_defaults(files: list[Path]) -> set[str]:
    referenced: set[str] = set()
    for path in files:
        choice_depth = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            token = line.strip()
            if token == "choice":
                choice_depth += 1
                continue
            if token == "endchoice":
                choice_depth = max(0, choice_depth - 1)
                continue
            if choice_depth == 0 and (match := DEFAULT_RE.match(line)):
                referenced.add(match.group(1))
    return referenced


def modify_defaults(defaults_path: Path, config_in: Path, verbose: bool) -> int:
    if not defaults_path.is_file():
        raise FileNotFoundError(f"BusyBox defaults file not found: {defaults_path}")
    if not config_in.is_file():
        raise FileNotFoundError(f"BusyBox Config.in not found: {config_in}")

    sources = source_files(config_in)
    referenced = referenced_defaults(sources)
    lines = defaults_path.read_text(encoding="utf-8").splitlines(keepends=True)
    modified: list[str] = []
    changes: list[str] = []

    index = 0
    while index < len(lines):
        match = CONFIG_RE.match(lines[index])
        if not match:
            modified.append(lines[index])
            index += 1
            continue

        end = index + 1
        while end < len(lines) and not CONFIG_RE.match(lines[end]):
            end += 1
        block = lines[index:end]
        name = match.group(1)

        eligible = (
            name in referenced
            and not any(item in name for item in CONFIG_EXCLUDES)
            and any(line.strip() == "bool" or line.lstrip().startswith("bool ") for line in block)
        )
        if eligible:
            for offset, line in enumerate(block):
                value = VALUE_RE.match(line.rstrip("\n"))
                if value and value.group(2) != "y":
                    newline = "\n" if line.endswith("\n") else ""
                    block[offset] = f"{value.group(1)}y{value.group(3)}{newline}"
                    changes.append(name)
                    break

        modified.extend(block)
        index = end

    if changes:
        defaults_path.write_text("".join(modified), encoding="utf-8")

    if verbose:
        for name in changes:
            print(f"enabled: {name}")
    print(
        f"BusyBox defaults: scanned {len(sources)} files, "
        f"found {len(referenced)} references, changed {len(changes)} options"
    )
    return len(changes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("defaults", type=Path, help="path to Config-defaults.in")
    parser.add_argument(
        "--config-in",
        type=Path,
        help="path to BusyBox config/Config.in (derived from defaults path by default)",
    )
    parser.add_argument("--verbose", action="store_true", help="list modified options")
    args = parser.parse_args()

    config_in = args.config_in or args.defaults.parent / "config" / "Config.in"
    modify_defaults(args.defaults, config_in, args.verbose)


if __name__ == "__main__":
    main()
