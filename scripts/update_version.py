from __future__ import annotations

import argparse
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
PYPROJECT_FILE = ROOT / "pyproject.toml"
PACKAGE_VERSION_FILE = ROOT / "src" / "ranglerpy" / "_version.py"

VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[abrc][0-9]+)?$")


def _replace(pattern: str, replacement: str, path: Path) -> None:
    text = path.read_text()
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Could not update version in {path}")
    path.write_text(updated)


def update_version(version: str) -> None:
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError("version must be a PEP 440-style release like 0.1.1 or 0.2.0b1")

    VERSION_FILE.write_text(f"{version}\n")
    _replace(r'^version = "[^"]+"$', f'version = "{version}"', PYPROJECT_FILE)
    _replace(r'^__version__ = "[^"]+"$', f'__version__ = "{version}"', PACKAGE_VERSION_FILE)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update ranglerpy package version files.")
    parser.add_argument("version")
    args = parser.parse_args()
    update_version(args.version)


if __name__ == "__main__":
    main()
