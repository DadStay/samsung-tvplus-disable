# Recovery

The protected receipt is **not a full television backup**. It saves the original
BMS service state and unit SHA-256. It does not back up channels, accounts, apps or
firmware. Keep it intact. Full live restore on the owner TV has not been tested.

## Undo this tool's BMS block

Temporarily enable Developer Mode for your computer as in the quick start, then:

```sh
python3 tvplus.py preflight --tv-address <TV_IP>
python3 tvplus.py restore --tv-address <TV_IP>
python3 tvplus.py inspect --tv-address <TV_IP>
```

Restore requires the exact supported build, unchanged unit hash, safe directories,
an inactive service and this tool's original receipt. It removes only the owned
zero-byte marker and starts BMS, then checks the service is active. Other TV Plus
app/channel/feature experiments are not managed or undone by this tool.

If the marker existed before using this public tool, it refuses to adopt it. That
includes a previous development version. Do not delete another tool's marker or
copy a different TV's receipt to make restore pass. Use the creator of that
original change's recovery procedure instead.

## Undo the native Home action

Restore the TV Plus icon through Home → Connected Devices → TV Plus → Add to Home
if offered on your software. Follow Samsung's native prompt. This is separate
from BMS restore. It may restore TV Plus channels; lower the volume first.

## Failure during application or recovery

- A failed application attempts its inverse once after it created the marker.
  A rollback failure is returned as a failure, never as success.
- A lost connection/interrupted computer may prevent cleanup. Do not assume the
  TV changed or did not change; reconnect and run `inspect` before another action.
- An original receipt left by an interrupted attempt is intentionally not
  overwritten. It needs inspection, not another blind `disable` run.
- If restoration cannot be verified, stop. A power cycle or factory reset is not
  presented as a guaranteed recovery method. Do not change firmware to force it.

After normal recovery, close Developer Mode and verify maintenance access is
closed as described in the quick start. Reports never prove physical playback;
test ordinary streaming, HDMI and TV Plus on the screen yourself.
