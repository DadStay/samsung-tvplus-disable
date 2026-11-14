# Validation record

Release: **0.1.0, experimental**. Updated 2026-11-13 (Pacific time).
No personal TV identifiers, photographs, network settings, raw receipts or firmware
binaries are included. Model/build are compatibility information, not a serial.

| Check | Evidence and limit |
| --- | --- |
| Exact tested TV | UN85DU7200FXZA, Tizen 9.0/ARMv7, build listed in README |
| Original BMS mechanism | Native condition/path/exec and original unit hash read on TV; applied predecessor saved original before write, inactive/MainPID0 verified |
| Reboot persistence | Different kernel boot and boot-complete confirmed privately; inactive BMS/marker/unchanged unit verified |
| Owner functional test | No TV Plus broadcast audio/video; YouTube and PS5 picture/audio normal, including after restart |
| Native Home action | Owner confirmed icon and recommendations hidden; latest postboot reply confirmed icon hidden; recommendations not separately rechecked in that final reply |
| Full UI removal | **Failed**: PS5-off black screen retains channel title on OK; TV Plus key shows native disabled notice |
| Public code vs prototype | Public code uses a new generic receipt path, stronger receipt/rollback checks, and sanitized CLI reports; it does not adopt the development TV's existing marker |
| Isolated fresh-state effectiveness | **Not tested**: the one owner TV had earlier app/channel changes; do not attribute the combined result solely to the public two-step recipe |
| Full live inverse | **Not tested**. Host tests exercise restore and failure guards; no promise of complete TV recovery |
| Other TVs/firmware | **Not tested; refused**. No Samsung-wide compatibility claim |
| Other host OSes | **Not tested**; only macOS Apple silicon validated |

The release preparation's automated and live-inspection results are recorded in
[PROJECT-STATE.md](../PROJECT-STATE.md). Host tests use isolated service/filesystem
fixtures and fake transport results, not a real TV. A JSON success report is not
proof of panel behavior. No clean-state live disable/restore is claimed for the
public release.

## Community reports

Use the issue form. State exact model/build, operation, reboot result, app/HDMI
behavior and whether picture/audio or only a title/notice remains. Never upload
About TV screens, IP/MAC addresses, Wi-Fi names, account details or complete logs.
Stars are welcome; only evidence-based compatibility reports will expand support.
