# How it works

The tested firmware's native `bms.service` includes:

```ini
ConditionPathExists=!/opt/usr/share/systemd/system/bms
ExecStart=/opt/usr/apps/com.samsung.tv.slive-daemon/bin/bms-service
```

A root-owned zero-byte file at the condition path prevents that unit from starting.
The executable belongs to Samsung's TVPLUS/channel-metadata package. The slive
provider is a separate service and is not stopped. Dependency inspection alone
does not prove HDMI compatibility; the owner also tested actual picture/audio.

The controller:

1. Accepts only a private LAN IPv4 address and validates the retail model and
   Developer Mode's Host PC IP against the local route. HTTP proxies are bypassed
   for the local identity request.
2. Verifies the cached upstream files against the manifest created from the
   SHA-256-pinned official v0.0.12 archive. Uses AeroTizen's direct Python SDB
   transport instead of executing a bundled Intel SDB binary.
3. Uses upstream `archive_root.probe` for a temporary authenticated UID-0 session.
   Despite its name, this is actual root acquisition, including namespace staging,
   not a read-only compatibility probe. The upstream tool's own capability,
   runtime, identity and cleanup checks are kept.
4. Sends a single fixed script invocation. There is no arbitrary command option,
   `--force`, firmware override, or remote-shell mode in this project.
5. The script checks exact build/ARM/root, the observed unit/condition/executable,
   lack of drop-ins, ownership, absent marker and absent receipt before a write.
   It saves/fsyncs the original state/unit hash, creates only the marker with
   noclobber, stops BMS, then verifies inactive/MainPID0.
6. The temporary agent exits and cleans its staging. The host reports failures if
   authentication, command status, cleanup, or the two upstream critical-file
   hashes fail. It emits only known report fields, not raw logs.

The block survives reboot because it is stored in the vendor's persistent condition
path. There is no startup patch, host daemon, polling loop or persistent root
service. The host is unnecessary after application. Future firmware may change
this condition; neither that nor factory resets have persistence guarantees.

The root filesystem on the investigated TV was read-only VDFS. TV Plus title UI
also exists within the shared `org.tizen.tv-viewer`. Deleting that viewer would
not be a targeted TV Plus app removal and is not attempted. The public tool does
not patch executable instructions or change global security policy.

## Deliberately excluded experiments

Standard uninstall was followed by the standalone app being reinstalled. App
disable flags, autorun changes and channel deletion did not independently stop
playback reliably. A product-support gate was successfully set False and survived
reboot, but still failed the full-UI test. None is an installation step here.
The public project preserves the smaller BMS/native-UI approach and labels the
uncertainty about prior state rather than claiming a clean-state isolated result.
