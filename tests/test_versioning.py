from pathlib import Path
import re
import unittest

from ranglerpy import __api_version__, __version__


ROOT = Path(__file__).resolve().parents[1]


def _pyproject_version() -> str:
    match = re.search(r'^version = "([^"]+)"$', (ROOT / "pyproject.toml").read_text(), re.MULTILINE)
    if match is None:
        raise AssertionError("pyproject.toml version is missing")
    return match.group(1)


class VersioningTests(unittest.TestCase):
    def test_package_version_files_are_in_sync(self) -> None:
        self.assertEqual((ROOT / "VERSION").read_text().strip(), __version__)
        self.assertEqual(_pyproject_version(), __version__)

    def test_api_version_is_explicit(self) -> None:
        self.assertEqual(__api_version__, "v1")


if __name__ == "__main__":
    unittest.main()
