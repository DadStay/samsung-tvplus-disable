# Troubleshooting

| Result | What to check |
| --- | --- |
| Python version error | Use Python 3.12+. Do not edit the minimum version |
| OpenSSL unavailable | Install OpenSSL for your host; check `openssl version` |
| Setup hash mismatch | Stop. Do not replace the pinned checksum with the downloaded file's hash |
| Unsupported model | Stop; the exact retail SKU must match. Submit model/build only |
| Developer binding mismatch | TV Developer Mode must be On and Host PC IP must match this computer's active LAN route; restart TV if requested |
| HTTP unavailable | Check the TV is on, same LAN, and that you used the TV address rather than your phone address |
| Root/transport operation fails | Guest isolation, firewall, changed firmware or absent root prerequisites can cause this; do not open router ports or disable TV security globally |
| Operation exit code 2 | A target/unit/path/receipt guard refused. Do not erase the marker/receipt or force retry |
| Existing marker/receipt | A previous or interrupted change exists. Inspect first; this tool intentionally refuses to adopt it |
| Rollback/restore fails | Stop and retain original receipts; see recovery. Do not claim the TV is restored |
| `success: false` or cleanup false | Treat the operation as unverified; inspect before another write |
| Black screen with title | Known residual UI. The tool is a playback block, not complete interface removal |
| Disabled message on remote key | Expected native disabled-service notice. The remote button is not remapped |
| Broadcast returns | Physical failure even if JSON was successful. Report supported model/build and steps, not identifiers |
| YouTube/HDMI fails | Use guarded recovery, then report exactly what stopped working. Do not stop shared TV services |

For public reports, copy only the project's allowlisted JSON result and inspect it
yourself first. Do not paste unrelated terminal history, setup/host-address output,
system logs, screenshots containing home/account/device information, or `.private`.
