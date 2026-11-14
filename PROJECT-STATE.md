# Project checkpoint — 2026-11-13

Version: 0.1.0, experimental. Published at https://github.com/DadStay/samsung-tvplus-disable.
Release v0.1.0 source commit: daf0286a75d2071ed6f5e5724dc37548b2fd1b28.
GitHub Issues/Discussions/private vulnerability reporting/secret scanning and push
protection are enabled. Anonymous repository access and ZIP download were verified.
ZIP SHA-256:1296c3b1faaa492001e303b7fee503aca682a66c8ecebe28baff6c636bb5f23f.
The28-file source-only ZIP exactly matched the audited local artifact and CRC.
Remote source files matched the audited tree; fresh generic-author history only.
CI run43534590065 passed both Ubuntu/macOS host jobs. This is host-fixture
coverage, not live-TV validation on Linux. The release tag remains immutable.

## Scope and evidence

1. Open, reproducible exact-target playback control: implemented as `tvplus.py` and
   `scripts/bms-control.sh`; no arbitrary command or firmware override.
2. Privacy: new publication tree; no original project history, raw TV receipts,
   private connection files, account data, firmware or household photographs.
   Graphics are original schematic SVGs, rendered and visually reviewed. All28 public
   files passed the release allowlist/privacy-pattern/local-link checks and the
   separate repository-audit helper. ZIP structure/CRC and SHA-256 were checked.
3. Documentation: English/Arabic setup, native Home action, mechanism, recovery,
   troubleshooting, contribution and sanitized issue template are present.
4. Local verification: 17 host tests PASS on Python 3.12/macOS, including isolated
   native-script disable/restore, rollback failure, pre-existing marker, wrong
   firmware, changed unit, symlink, dependency tamper, address/identity guards,
   and report allowlisting. Shell syntax check PASS.
5. Public setup: official archive downloaded, SHA-256 checked, filtered extraction
   succeeded; dependency manifest pinned to the measured canonical checksum.
6. Actual TV: new public preflight and temporary-root **inspect** PASS, command0,
   staging cleaned and two critical-file hashes unchanged. No new BMS setting,
   source/channel/feature change or reboot performed for publication.
7. Live disable/restore of the public version: NOT RUN. The predecessor mechanism
   was applied and quiet playback/normal YouTube/PS5 confirmed, including after
   reboot, on a TV with prior changes. No clean-state isolated-effect claim.
8. Complete UI removal: FAILED in the investigation; title/disabled notice remain.
   This publication is a playback block, not a full uninstall. Developer Mode
   closure on that development TV is not confirmed; no claim that it was closed.

## Remaining boundaries and next action

Publication scope is complete and verified. No background task or TV change is
needed. Maintain the exact compatibility/rollback/privacy guards for community
reports; do not label black/title-only TV Plus as full removal. Live public
application from a clean factory state and full live inverse remain unverified.
Live TV host connectivity beyond macOS is unverified. Development-TV maintenance
closure is still pending owner action. Release ZIP reflects the tagged source;
this post-publication checkpoint on main adds verified distribution evidence.
