# Contributing

Open an issue, discussion, or pull request. Keep changes focused and evidence-based.
Do not remove the fixed model/build guards or advertise support from a matching
series name. New support needs native unit/API evidence, guarded recovery, and a
real post-reboot app/HDMI/playback test on that exact target.

Run `python3 -m unittest discover -s tests -v`, `sh -n scripts/bms-control.sh`,
and `python3 tools/release.py --check` before a PR. No TV is needed for host tests.
Do not run a live disable/restore as an automated test. No telemetry, firmware
payloads, anonymous logs, arbitrary-shell features or persistent root services.

**Never attach personal information.** Model and firmware build are sufficient for
compatibility reports. Do not include IP/MAC addresses, Wi-Fi names, serial numbers,
account names, tokens, passwords, full About TV photos or `.private` files.
Use clean diagrams or tightly redacted images for UI reports.
