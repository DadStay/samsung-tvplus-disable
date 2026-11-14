import hashlib
import io
import ipaddress
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import tvplus


class ControllerTests(unittest.TestCase):
    def test_lan_address_and_injection_guard(self):
        valid = str(ipaddress.ip_network("10.0.0.0/8").network_address + 12345)
        self.assertEqual(tvplus.private_address(valid), valid)
        for bad in ("example.com", "127.0.0.1", "0.0.0.0", "::1", "8.8.8.8", valid + ";id", "169.254.0.1", "224.0.0.1"):
            with self.subTest(bad=bad), self.assertRaises(tvplus.Refused):
                tvplus.private_address(bad)

    def test_identity_checks_model_and_binding_before_root(self):
        for model, mode, binding, good in ((tvplus.MODEL, "1", "source", True), ("another-TV", "1", "source", False), (tvplus.MODEL, "0", "source", False), (tvplus.MODEL, "1", "other", False)):
            with self.subTest(model=model, mode=mode, binding=binding):
                if good:
                    tvplus.check_device({"modelName": model, "developerMode": mode, "developerIP": binding}, "source")
                else:
                    with self.assertRaises(tvplus.Refused):
                        tvplus.check_device({"modelName": model, "developerMode": mode, "developerIP": binding}, "source")

    def test_result_allowlist_does_not_forward_private_output(self):
        r = {"authenticated": True, "uid": 0, "euid": 0, "staging_cleaned": True, "system_files_unchanged": True, "host": "DO_NOT_PUBLISH", "token": "DO_NOT_PUBLISH", "commands": [{"exit_code": 0, "timed_out": False, "stdout": "DO_NOT_PUBLISH", "stderr": "DO_NOT_PUBLISH"}]}
        report = tvplus.result_report(r)
        self.assertTrue(report["success"])
        self.assertNotIn("DO_NOT_PUBLISH", json.dumps(report))
        self.assertFalse(report["physical_playback_verified"])
        self.assertFalse(report["full_ui_removal"])
        for key in ("staging_cleaned", "system_files_unchanged", "authenticated"):
            changed = dict(r, **{key: False})
            self.assertFalse(tvplus.result_report(changed)["success"])
        for field, value in (("exit_code", 1), ("timed_out", True)):
            changed = dict(r, commands=[dict(r["commands"][0], **{field: value})])
            self.assertFalse(tvplus.result_report(changed)["success"])

    def test_dependency_checksum_before_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "bad.tar.gz"
            archive.write_bytes(b"not the pinned release")
            destination = root / "out"
            destination.mkdir()
            with self.assertRaises(tvplus.Refused):
                tvplus.extract_release(archive, destination)
            self.assertEqual(list(destination.iterdir()), [])

    def archive(self, root, extra=None):
        archive = root / "input.tar.gz"
        required = {"source/src/samsung_tv_root/archive_root.py": b"# public source", "LICENSE": b"public upstream license"}
        required.update({"_internal/payloads/common/" + name: b"test fixture, not executable" for name in tvplus.PAYLOADS})
        required["unwanted-private-example"] = b"DO_NOT_EXTRACT"
        if extra:
            required.update(extra)
        with tarfile.open(archive, "w:gz") as output:
            for name, data in required.items():
                item = tarfile.TarInfo(tvplus.ARCHIVE_ROOT + "/" + name)
                item.size = len(data)
                output.addfile(item, io.BytesIO(data))
        return archive

    def test_extract_allowlist_and_verify_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.archive(root)
            destination = root / "out"
            destination.mkdir()
            with patch.object(tvplus, "SHA256", hashlib.sha256(archive.read_bytes()).hexdigest()):
                tvplus.extract_release(archive, destination)
            self.assertFalse((destination / "unwanted-private-example").exists())
            manifest_digest = hashlib.sha256((destination / "manifest.json").read_bytes()).hexdigest()
            with patch.object(tvplus, "MANIFEST_SHA256", manifest_digest):
                tvplus.verify_dependencies(destination)
                (destination / "source/src/samsung_tv_root/archive_root.py").write_text("tampered")
                with self.assertRaises(tvplus.Refused):
                    tvplus.verify_dependencies(destination)
            (destination / "manifest.json").write_text('{}')
            with self.assertRaises(tvplus.Refused):
                tvplus.verify_dependencies(destination)

    def test_unsafe_archive_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.archive(root, {"../escape": b"bad"})
            destination = root / "out"
            destination.mkdir()
            with patch.object(tvplus, "SHA256", hashlib.sha256(archive.read_bytes()).hexdigest()), self.assertRaises(tvplus.Refused):
                tvplus.extract_release(archive, destination)
            self.assertFalse((root / "escape").exists())

    def test_symlink_private_workspace_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "actual").mkdir()
            (root / "link").symlink_to(root / "actual", target_is_directory=True)
            with self.assertRaises(tvplus.Refused):
                tvplus.own_directory(root / "link")


if __name__ == "__main__":
    unittest.main()
