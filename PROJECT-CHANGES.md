# Project changes

## 2026-11-13 — Independent publication preparation

- Created a fresh Samsung-specific project, without importing development history
  or private original-TV files. Public AeroTizen source/license copied only after
  matching the pinned upstream hashes.
- Added fixed-target host controller, official dependency download with archive
  and cache-manifest checksums, direct SDB adapter, generic protected receipt,
  native BMS block/inverse and sanitized allowlisted reports.
- Documented tested playback behavior, prior-state uncertainty, failed full UI
  removal, untested complete live restore, compatibility and maintenance cleanup.
- Added English/Arabic guides, clean diagrams, community/privacy files, source ZIP
  builder and host CI. No firmware or proprietary modules redistributed.
- 17 host tests and shell syntax passed. A first fixture run exposed a dependency
  path check incorrectly following host ancestors outside the cache; corrected to
  inspect only cache components and reran all tests successfully.
- New public setup/preflight/root-inspect passed on the development TV; no live
  public disable/restore or additional TV-setting mutation. Publication pending.

## 2026-11-13 — Public repository and release verified

- Published the authorized public MIT repository and v0.1.0 source-only ZIP with
  SHA256SUMS. Issues, Discussions, private vulnerability reporting, secret scanning
  and push protection enabled. No private original-TV material or old Git history.
- Anonymous download matched the audited local ZIP byte-for-byte; all28 files/CRC
  passed. Anonymous remote source audit matched all28 files and generic-author
  initial history. The initial Git push lacked a credential helper; retried with
  the existing authenticated GitHub CLI's one-operation Git helper, without
  exposing, copying or writing credential values.
- GitHub CI run43534590065 completed successfully on Ubuntu and macOS.17 tests
  per host, shell syntax and release checks passed. No live Linux-TV test implied.
- Frozen release tag points to daf0286a75d2071ed6f5e5724dc37548b2fd1b28; this
  documentation follow-up records actual publication evidence without moving it.

## 2026-11-13 — English video walkthrough

- Attached approved1080p30English MP4,SRT,poster and separatevideo checksums to
  existingv0.1.0release; existing sourceZIP/checksums/tag unchanged.
- Linked the film from English/ArabicREADME and docs/video.md, retaining all
  compatibility and incomplete-uninstall/clean-state/rollback limitations.
- Isolated public documentation tree passed release allowlist/privacy/local-link
  checks. No private-device/account records or local audit history included.
