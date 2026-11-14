"""Run the actual shell flow against isolated files and fake service commands."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BmsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.parent = self.root / "vendor"
        self.parent.mkdir(mode=0o755)
        self.marker = self.parent / "bms"
        self.base = self.root / "receipts"
        self.unit = self.root / "bms.service"
        self.unit.write_text("ConditionPathExists=!/opt/usr/share/systemd/system/bms\nExecStart=/opt/usr/apps/com.samsung.tv.slive-daemon/bin/bms-service\n")
        self.osrelease = self.root / "os-release"
        self.osrelease.write_text("BUILD_ID=T-KSU2EDAKUC-0090-REL-202605141700\n")
        self.state = self.root / "state"
        self.state.write_text("active")
        script = (ROOT / "scripts/bms-control.sh").read_text()
        replacements = {"/opt/usr/share/systemd/system": str(self.parent), "/opt/usr/share/samsung-tvplus-disable": str(self.base), "/usr/lib/systemd/system/bms.service": str(self.unit), "/etc/os-release": str(self.osrelease)}
        for old, new in replacements.items():
            script = script.replace(old, new)
        self.unit.write_text(self.unit.read_text().replace("/opt/usr/share/systemd/system", str(self.parent)))
        self.script = self.root / "control.sh"
        self.script.write_text(script)
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ["PATH"], STATE=str(self.state), UNITFILE=str(self.unit))
        self.command("id", "#!/bin/sh\necho 0\n")
        self.command("uname", "#!/bin/sh\necho armv7l\n")
        self.command("sync", "#!/bin/sh\nexit 0\n")
        self.command("sleep", "#!/bin/sh\nexit 0\n")
        # Root ownership is simulated; real permission bits/file IO/hash logic remain.
        self.command("stat", """#!/usr/bin/env python3
import os,sys
from pathlib import Path
p=Path(sys.argv[-1]);s=p.stat();fmt=sys.argv[2];mode=format(s.st_mode & 0o777,'o')
print(fmt.replace('%u','0').replace('%a',mode).replace('%s',str(s.st_size)))
""")
        self.command("sha256sum", """#!/usr/bin/env python3
import hashlib,sys
from pathlib import Path
if sys.argv[1]=='-c':
 digest,path=Path(sys.argv[2]).read_text().strip().split('  ',1)
 sys.exit(0 if hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest else 1)
p=Path(sys.argv[1]);print(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p))
""")
        self.command("systemctl", """#!/usr/bin/env python3
import os,sys
from pathlib import Path
a=sys.argv[1:];p=Path(os.environ['STATE']);state=p.read_text()
if a[0]=='show':
 prop=a[a.index('-p')+1]
 print({'ActiveState':state,'MainPID':'0' if state=='inactive' else '123','FragmentPath':os.environ['UNITFILE'],'DropInPaths':os.environ.get('DROP_INS','')}[prop])
elif 'stop' in a:
 if os.environ.get('FAIL_STOP'):sys.exit(1)
 p.write_text('inactive')
elif 'start' in a:
 if os.environ.get('FAIL_START'):sys.exit(1)
 p.write_text('active')
else:sys.exit(2)
""")

    def command(self, name, contents):
        p = self.bin / name
        p.write_text(contents)
        p.chmod(0o755)

    def run_mode(self, mode, **env):
        return subprocess.run(["sh", str(self.script), mode], capture_output=True, text=True, env=dict(self.env, **env), timeout=15)

    def test_inspect_changes_no_marker_or_receipts(self):
        r = self.run_mode("inspect")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.base.exists())
        self.assertEqual(self.state.read_text(), "active")

    def test_disable_restore_with_real_receipt_and_permissions(self):
        r = self.run_mode("disable")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.state.read_text(), "inactive")
        self.assertEqual(self.marker.stat().st_size, 0)
        self.assertEqual(self.marker.stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.base / "original").stat().st_mode & 0o777, 0o700)
        r = self.run_mode("restore")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.marker.exists())
        self.assertEqual(self.state.read_text(), "active")

    def test_existing_marker_not_adopted_or_removed(self):
        self.marker.write_text("another tool")
        r = self.run_mode("disable")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.marker.read_text(), "another tool")
        self.assertFalse(self.base.exists())

    def test_wrong_build_no_write(self):
        self.osrelease.write_text("BUILD_ID=unverified\n")
        r = self.run_mode("disable")
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.base.exists())

    def test_drop_in_no_write(self):
        r = self.run_mode("disable", DROP_INS="unexpected")
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.marker.exists())

    def test_symlink_marker_no_write(self):
        original = self.root / "keep"
        original.write_text("preserve me")
        self.marker.symlink_to(original)
        self.assertNotEqual(self.run_mode("disable").returncode, 0)
        self.assertEqual(original.read_text(), "preserve me")

    def test_failed_stop_rolls_back_and_does_not_report_success(self):
        r = self.run_mode("disable", FAIL_STOP="1")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("BMS_ROLLBACK_VERIFIED", r.stdout)
        self.assertFalse(self.marker.exists())
        self.assertEqual(self.state.read_text(), "active")

    def test_failed_rollback_is_explicit(self):
        r = self.run_mode("disable", FAIL_STOP="1", FAIL_START="1")
        self.assertEqual(r.returncode, 3)
        self.assertIn("BMS_ROLLBACK_FAILED", r.stderr)

    def test_modified_unit_refuses_restore_preserving_marker(self):
        self.assertEqual(self.run_mode("disable").returncode, 0)
        self.unit.write_text(self.unit.read_text() + "# changed\n")
        self.assertNotEqual(self.run_mode("restore").returncode, 0)
        self.assertTrue(self.marker.exists())
        self.assertEqual(self.state.read_text(), "inactive")

    def test_missing_original_never_removes_marker(self):
        self.marker.touch(mode=0o600)
        self.state.write_text("inactive")
        self.assertNotEqual(self.run_mode("restore").returncode, 0)
        self.assertTrue(self.marker.exists())


if __name__ == "__main__":
    unittest.main()
