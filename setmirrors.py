#!/usr/bin/env python3
"""Prefer reliable download mirrors without discarding upstream fallbacks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PREFERRED_MIRRORS = {
    "@SF": ["https://downloads.sourceforge.net"],
    "@DEBIAN": ["https://ftp.debian.org/debian"],
    "@APACHE": ["https://dlcdn.apache.org", "https://archive.apache.org/dist"],
    "@GITHUB": ["https://raw.githubusercontent.com"],
    "@GNU": [
        "https://mirrors.rit.edu/gnu",
        "https://ftp.gnu.org/gnu",
        "https://ftpmirror.gnu.org",
    ],
    "@SAVANNAH": [
        "https://download.savannah.nongnu.org/releases",
        "https://cdimage.debian.org/mirror/gnu.org/savannah",
    ],
    "@KERNEL": [
        "https://cdn.kernel.org/pub",
        "https://mirrors.mit.edu/kernel",
        "https://mirrors.ustc.edu.cn/kernel.org",
        "https://mirror.nju.edu.cn/kernel.org",
    ],
    "@GNOME": ["https://download.gnome.org/sources"],
    "@OPENWRT": ["https://sources.cdn.openwrt.org", "https://sources.openwrt.org"],
    "@IMMORTALWRT": [
        "https://sources-cdn.immortalwrt.org",
        "https://sources.immortalwrt.org",
    ],
}


def load_mirrors(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected a JSON object in {path}")
    for name, urls in data.items():
        if not isinstance(urls, list) or not all(isinstance(url, str) for url in urls):
            raise ValueError(f"mirror group {name!r} must be a list of URLs")
    return data


def reorder_mirrors(mirrors: dict[str, Any]) -> int:
    changed = 0
    for group, preferred in PREFERRED_MIRRORS.items():
        urls = mirrors.get(group)
        if not isinstance(urls, list):
            continue
        reordered = [url for url in preferred if url in urls]
        reordered.extend(url for url in urls if url not in reordered)
        if reordered != urls:
            mirrors[group] = reordered
            changed += 1
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("scripts/projectsmirrors.json"),
        help="path to projectsmirrors.json",
    )
    args = parser.parse_args()

    mirrors = load_mirrors(args.path)
    changed = reorder_mirrors(mirrors)
    if changed:
        args.path.write_text(
            json.dumps(mirrors, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(f"Mirror priorities: updated {changed} of {len(mirrors)} groups in {args.path}")


if __name__ == "__main__":
    main()
