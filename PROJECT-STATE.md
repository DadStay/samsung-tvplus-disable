# Project checkpoint — 2026-11-13

Version: 0.1.0, experimental. Independent source-only publication prepared for
`DadStay/samsung-tvplus-disable`; initial public push/release verification pending.

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

## Next action

Audit the exact public files and ZIP, verify clean anonymous commit identity,
publish the authorized public repository/release, enable discussion/reporting,
and verify remote contents, download checksum and CI. Do not change the TV again
as part of release preparation. Public host coverage beyond macOS is unverified.
