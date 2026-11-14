#!/usr/bin/env python3
"""Fixed-target Samsung TV Plus BMS control. No pairing credentials required."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parent
MODEL = "UN85DU7200FXZA"
BUILD = "T-KSU2EDAKUC-0090-REL-202605141700"
VERSION = "0.1.0"
URL = "https://github.com/chris-ritsen/samsung-tv-root/releases/download/v0.0.12/samsung-tv-root-0.0.12-macos-arm64.tar.gz"
SHA256 = "8ee4587462963f8ad0374f921e41050bd9198a7cb0b15899a5f35a7ad8f50f2c"
MANIFEST_SHA256 = "756b026ef44266f75aa63f18fd56ce85847bef7e40997fb894e698684cd6484e"
ARCHIVE_ROOT = "samsung-tv-root-0.0.12-macos-arm64"
RFC1918 = tuple(ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
PAYLOADS = {"SamsungTvArchiveRoot.dll", "SamsungTvRootAgent.dll"}


class Refused(RuntimeError):
    """A guard failed; the caller should not retry by weakening it."""


def private_address(value):
    try:
        address = ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError:
        raise Refused("Use a LAN IPv4 address, not a hostname or command.") from None
    if not any(address in block for block in RFC1918):
        raise Refused("Only RFC1918 private LAN addresses are accepted.")
    return str(address)


def own_directory(path):
    if path.is_symlink():
        raise Refused("Private workspace must not be a symbolic link.")
    path.mkdir(mode=0o700, parents=False, exist_ok=True)
    if not path.is_dir():
        raise Refused("Private workspace is not a directory.")
    if os.name == "posix":
        if path.stat().st_uid != os.getuid():
            raise Refused("Private workspace has another owner.")
        path.chmod(0o700)


def private_root():
    path = ROOT / ".private"
    own_directory(path)
    return path


def extract_release(archive, destination):
    """Extract only pinned public Python modules, two payloads and license."""
    if archive.stat().st_size > 160 * 1024 * 1024 or hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise Refused("Upstream archive SHA-256 mismatch; nothing extracted.")
    selected = {}
    with tarfile.open(archive, "r:gz") as source:
        for member in source.getmembers():
            parts = PurePosixPath(member.name).parts
            if not parts or parts[0] != ARCHIVE_ROOT or ".." in parts or member.name.startswith("/"):
                raise Refused("Unsafe archive path.")
            relative = PurePosixPath(*parts[1:])
            name = str(relative)
            keep = (name.startswith("source/src/samsung_tv_root/") and name.endswith(".py")) or name == "LICENSE" or (relative.parent == PurePosixPath("_internal/payloads/common") and relative.name in PAYLOADS)
            if not keep:
                continue
            if not member.isfile() or member.size > 4 * 1024 * 1024 or name in selected:
                raise Refused("Unexpected archive member.")
            stream = source.extractfile(member)
            if stream is None:
                raise Refused("Archive member could not be read.")
            selected[name] = stream.read()
    required = {"source/src/samsung_tv_root/archive_root.py", "LICENSE"} | {"_internal/payloads/common/" + name for name in PAYLOADS}
    if not required.issubset(selected):
        raise Refused("Incomplete upstream archive.")
    for name, data in selected.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(0o600)
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in selected.items()}
    (destination / "manifest.json").write_text(json.dumps(manifest, sort_keys=True) + "\n")
    return manifest


def setup(archive=None):
    base = private_root()
    final = base / "upstream-v0.0.12"
    if final.exists() or final.is_symlink():
        verify_dependencies(final)
        return {"status": "dependencies_verified", "tv_contacted": False}
    with tempfile.TemporaryDirectory(prefix="setup-", dir=base) as temporary:
        stage = Path(temporary)
        if archive is None:
            archive = stage / "release.tar.gz"
            request = urllib.request.Request(URL, headers={"User-Agent": "samsung-tvplus-disable/" + VERSION})
            with urllib.request.urlopen(request, timeout=45) as response, archive.open("wb") as output:
                total = 0
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > 160 * 1024 * 1024:
                        raise Refused("Upstream download exceeded the size limit.")
                    output.write(chunk)
        destination = stage / "verified"
        destination.mkdir(mode=0o700)
        extract_release(Path(archive), destination)
        destination.rename(final)
    return {"status": "dependencies_installed", "tv_contacted": False}


def verify_dependencies(directory):
    if directory.is_symlink() or not directory.is_dir():
        raise Refused("Run setup first; dependency cache unavailable.")
    manifest_path = directory / "manifest.json"
    if manifest_path.is_symlink():
        raise Refused("Dependency manifest is a symbolic link.")
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != MANIFEST_SHA256:
        raise Refused("Dependency manifest does not match the pinned release.")
    manifest = json.loads(manifest_path.read_text())
    if not isinstance(manifest, dict) or not manifest:
        raise Refused("Invalid dependency manifest.")
    for name, digest in manifest.items():
        p = PurePosixPath(name)
        if p.is_absolute() or ".." in p.parts:
            raise Refused("Invalid dependency path.")
        path = directory / name
        components = [directory.joinpath(*p.parts[:i]) for i in range(1, len(p.parts) + 1)]
        if any(component.is_symlink() for component in components) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise Refused("Dependency cache changed; use a fresh project download.")
    for required in ("source/src/samsung_tv_root/archive_root.py", *["_internal/payloads/common/" + n for n in PAYLOADS]):
        if required not in manifest:
            raise Refused("Dependency manifest is incomplete.")
    return directory


def host_address(host):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as route:
        route.connect((private_address(host), 9))
        return private_address(route.getsockname()[0])


def check_device(device, source):
    if not isinstance(device, dict) or device.get("modelName") != MODEL:
        raise Refused("Unsupported retail model. No root session started.")
    if str(device.get("developerMode")) != "1" or device.get("developerIP") != source:
        raise Refused("Developer Mode/Host PC IP does not match this computer. No root session started.")


def preflight(host):
    source = host_address(host)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open("http://" + host + ":8001/api/v2/", timeout=5) as response:
        raw = response.read(262145)
    if len(raw) > 262144:
        raise Refused("TV identity response is too large.")
    check_device(json.loads(raw).get("device"), source)
    return source


def result_report(result):
    commands = result.get("commands", [])
    success = (result.get("authenticated") is True and result.get("uid") == 0 and result.get("euid") == 0 and result.get("staging_cleaned") is True and result.get("system_files_unchanged") is True and len(commands) == 1 and commands[0].get("exit_code") == 0 and not commands[0].get("timed_out"))
    # Deliberate allowlist: never forward raw results, commands, paths or exceptions.
    return {"success": success, "authenticated_root": result.get("authenticated") is True and result.get("euid") == 0, "staging_cleaned": result.get("staging_cleaned") is True, "two_system_file_hashes_unchanged": result.get("system_files_unchanged") is True, "operation_exit_code": commands[0].get("exit_code") if len(commands) == 1 else None, "physical_playback_verified": False, "full_ui_removal": False}


async def operate(mode, host):
    source = preflight(host)
    directory = verify_dependencies(private_root() / "upstream-v0.0.12")
    if shutil.which("openssl") is None:
        raise Refused("OpenSSL must be installed and on PATH.")
    sys.path.insert(0, str(ROOT / "vendor"))
    sys.path.insert(0, str(directory / "source/src"))
    from aerotizen_sdb import Sdb
    from samsung_tv_root import archive_root
    from samsung_tv_root.sdb import SdbClient, SdbError

    def direct_run(client_self, arguments, *, check, timeout=None):
        if client_self.tv_host != host:
            raise SdbError("Unexpected target refused.")
        args, client, out, err, code = list(arguments), None, "", "", 0
        limit = timeout or client_self.timeout
        try:
            if args == ["disconnect", client_self.serial]:
                out = "No persistent SDB host server.\n"
            else:
                client = Sdb(host, timeout=min(limit, 10), source_address=source).connect(attempts=3)
                if args == ["connect", client_self.serial]:
                    out = "connected to " + client_self.serial + "\n"
                elif args == ["devices"]:
                    out = "List of devices attached\n" + client_self.serial + "\tdevice\n"
                elif len(args) >= 4 and args[:3] == ["-s", client_self.serial, "shell"]:
                    out = client.shell_bounded(" ".join(args[3:]), timeout=limit, max_output=2 * 1024 * 1024)
                elif len(args) == 5 and args[:3] == ["-s", client_self.serial, "push"]:
                    local, remote = Path(args[3]), args[4]
                    if not remote.startswith("/home/owner/share/tmp/sdk_tools/") or ".." in remote.split("/") or local.stat().st_size > 4 * 1024 * 1024:
                        raise SdbError("Unexpected payload destination/size refused.")
                    client.push(local.read_bytes(), remote)
                    out = "push complete\n"
                else:
                    raise SdbError("Unsupported transport operation.")
        except Exception:
            code, err = 1, "SDB transport operation failed; check local connectivity."
        finally:
            if client:
                client.close()
        completed = subprocess.CompletedProcess(arguments, code, out, err)
        if check and code:
            raise SdbError(err)
        return completed

    SdbClient.run = direct_run
    # Locator only: direct_run handles every request; no Intel executable is run.
    os.environ["SDB"] = str(Path(__file__).resolve())
    script = (ROOT / "scripts/bms-control.sh").read_text()
    result = await archive_root.probe(host, model=MODEL, callback_host=source, bind_host=source, sdb_timeout=12, accept_timeout=30, command_timeout=60, commands=("set -- " + mode + "\n" + script,), payloads=directory / "_internal/payloads/common")
    return result_report(result)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("setup", "host-address", "preflight", "inspect", "disable", "restore"))
    parser.add_argument("--tv-address")
    parser.add_argument("--archive", type=Path, help="setup only: a local official release archive, SHA-256 checked")
    args = parser.parse_args(argv)
    if sys.version_info < (3, 12):
        parser.error("Python 3.12 or newer is required.")
    try:
        if args.command == "setup":
            if args.tv_address:
                raise Refused("setup does not contact a TV; omit --tv-address.")
            report = setup(args.archive)
        else:
            if not args.tv_address or args.archive:
                raise Refused("Provide --tv-address; --archive is only for setup.")
            host = private_address(args.tv_address)
            if args.command == "host-address":
                print(host_address(host))
                return 0
            if args.command == "preflight":
                preflight(host)
                report = {"supported_model": True, "developer_binding_matches": True, "temporary_root_started": False, "firmware_check": "performed inside guarded root operation"}
            else:
                report = asyncio.run(operate(args.command, host))
                report["operation"] = args.command
        print(json.dumps(report, indent=2))
        return 0 if report.get("success", True) else 1
    except Refused as error:
        print("Refused: " + str(error), file=sys.stderr)
    except Exception as error:
        print("Operation failed (" + type(error).__name__ + "). No raw device details printed. See docs/troubleshooting.md.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
