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
