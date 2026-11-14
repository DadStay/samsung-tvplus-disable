#!/usr/bin/env python3
"""Audit the public allowlist and create a source-only, reproducible ZIP."""
import argparse
import hashlib
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tvplus import VERSION

TOP = {"tvplus.py", "README.md", "LICENSE", "NOTICE.md", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md", "AGENTS.md", "PROJECT-STATE.md", "PROJECT-CHANGES.md", ".gitignore"}
DIRECTORIES = {"scripts", "docs", "assets", "vendor", "tests", "tools", ".github"}
SUFFIXES = {".py", ".sh", ".md", ".svg", ".yml", ".yaml"}
PATTERNS = [r"gh[pousr]_[A-Za-z0-9_]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"AKIA[0-9A-Z]{16}", r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", r"/Users/[A-Za-z0-9_.-]+/", r"\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b"]


def public_files():
    selected = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if relative.parts[0] not in DIRECTORIES and str(relative) not in TOP:
            continue
        if any(part in {"__pycache__", ".private", ".venv"} for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError("Public symlink refused: " + str(relative))
        if not path.is_file():
            continue
        if relative.parts[0] in DIRECTORIES and path.suffix not in SUFFIXES and str(relative) not in {"vendor/AeroTizen-LICENSE"}:
            raise ValueError("Unexpected public file: " + str(relative))
        if path.stat().st_size > 256 * 1024:
            raise ValueError("Unexpected large public file: " + str(relative))
        selected.append(path)
    for name in TOP:
        if not (ROOT / name).is_file():
            raise ValueError("Missing public file: " + name)
    return selected


def audit(files):
    for path in files:
        text = path.read_text(encoding="utf-8")
        for pattern in PATTERNS:
            if re.search(pattern, text):
                raise ValueError("Privacy pattern needs review: " + str(path.relative_to(ROOT)))
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)", text):
                if ":" in target or target.startswith("#"):
                    continue
                local = (path.parent / target.split("#", 1)[0]).resolve()
                if not local.is_relative_to(ROOT) or not local.exists():
                    raise ValueError("Broken/escaping local link: " + str(path.relative_to(ROOT)) + " -> " + target)


def build(files):
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    archive = destination / ("samsung-tvplus-disable-" + VERSION + ".zip")
    prefix = "samsung-tvplus-disable-" + VERSION + "/"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for path in files:
            item = zipfile.ZipInfo(prefix + path.relative_to(ROOT).as_posix(), date_time=(2026, 11, 13, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            output.writestr(item, path.read_bytes())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (destination / "SHA256SUMS.txt").write_text(checksum + "  " + archive.name + "\n")
    with zipfile.ZipFile(archive) as check:
        if check.testzip() is not None or len(check.namelist()) != len(files):
            raise ValueError("Release ZIP verification failed.")
    print(archive.name + ": " + checksum)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = public_files()
    audit(files)
    print("Public allowlist/privacy-pattern/local-link checks passed:", len(files), "files")
    if not args.check:
        build(files)


if __name__ == "__main__":
    main()
