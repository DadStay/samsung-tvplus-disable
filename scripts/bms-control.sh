#!/bin/sh
# One exact firmware, one existing vendor condition. No firmware patch or agent.
set -eu
umask 077
MODE=${1:-inspect}
UNIT=bms.service
UNITFILE=/usr/lib/systemd/system/bms.service
PARENT=/opt/usr/share/systemd/system
MARKER=$PARENT/bms
BASE=/opt/usr/share/samsung-tvplus-disable
SAVE=$BASE/original
fail() { echo "REFUSED_$1" >&2; exit 2; }
case "$MODE" in inspect|disable|restore) ;; *) fail OPERATION;; esac
[ "$(id -u)" = 0 ] && [ "$(uname -m)" = armv7l ] || fail ROOT_OR_ARCH
grep -qxF 'BUILD_ID=T-KSU2EDAKUC-0090-REL-202605141700' /etc/os-release || fail FIRMWARE
[ -d "$PARENT" ] && [ ! -L "$PARENT" ] || fail MARKER_PARENT
case "$(stat -c %u:%a "$PARENT")" in 0:755|0:700) ;; *) fail PARENT_OWNER;; esac
[ ! -L "$MARKER" ] && [ ! -L "$BASE" ] && [ ! -L "$SAVE" ] || fail SYMBOLIC_LINK
grep -qxF 'ConditionPathExists=!/opt/usr/share/systemd/system/bms' "$UNITFILE" || fail VENDOR_CONDITION
grep -qxF 'ExecStart=/opt/usr/apps/com.samsung.tv.slive-daemon/bin/bms-service' "$UNITFILE" || fail VENDOR_EXECUTABLE
[ "$(systemctl show "$UNIT" -p FragmentPath --value)" = "$UNITFILE" ] || fail UNIT_PATH
[ -z "$(systemctl show "$UNIT" -p DropInPaths --value)" ] || fail DROP_INS
active_state() { systemctl show "$UNIT" -p ActiveState --value; }
marker_owned() {
    [ -f "$MARKER" ] && [ ! -L "$MARKER" ] && [ "$(stat -c %u:%a:%s "$MARKER")" = 0:600:0 ]
}
check_base() { [ -d "$BASE" ] && [ ! -L "$BASE" ] && [ "$(stat -c %u:%a "$BASE")" = 0:700 ]; }
check_original() {
    check_base || return 1
    [ -d "$SAVE" ] && [ ! -L "$SAVE" ] && [ "$(stat -c %u:%a "$SAVE")" = 0:700 ] || return 1
    for name in original-state.txt unit-original.sha256; do
        [ -f "$SAVE/$name" ] && [ ! -L "$SAVE/$name" ] && [ "$(stat -c %u:%a "$SAVE/$name")" = 0:600 ] || return 1
    done
    [ "$(cat "$SAVE/original-state.txt")" = active ] || return 1
    # A receipt may only name this unit; never pass arbitrary paths to sha256sum.
    [ "$(wc -l < "$SAVE/unit-original.sha256")" -eq 1 ] || return 1
    grep -qxE '[0-9a-f]{64}  /usr/lib/systemd/system/bms.service' "$SAVE/unit-original.sha256" || return 1
    sha256sum -c "$SAVE/unit-original.sha256" >/dev/null || return 1
}
restore_original() {
    check_original && marker_owned || return 1
    rm -- "$MARKER" || return 1
    systemctl start "$UNIT" || return 1
    [ ! -e "$MARKER" ] && [ "$(active_state)" = active ] || return 1
    echo BMS_ORIGINAL_ACTIVE_VERIFIED
}
report() {
    echo BMS_ACTIVE_STATE:$(active_state)
    echo BMS_MAIN_PID:$(systemctl show "$UNIT" -p MainPID --value)
    if marker_owned; then echo BMS_VENDOR_MARKER_PRESENT; else echo BMS_VENDOR_MARKER_NOT_OWNED; fi
    if check_original; then echo BMS_ORIGINAL_RECEIPT_VERIFIED; else echo BMS_ORIGINAL_RECEIPT_UNAVAILABLE; fi
}
if [ "$MODE" = inspect ]; then report; exit 0; fi
if [ "$MODE" = restore ]; then
    check_original || fail ORIGINAL_RECEIPT
    [ "$(active_state)" = inactive ] || fail ORIGINAL_STATE_CHANGED
    restore_original || fail RESTORE_NOT_VERIFIED
    report
    exit 0
fi
# Never adopt a pre-existing block, even one created by an older experiment.
[ ! -e "$MARKER" ] && [ ! -e "$SAVE" ] || fail EXISTING_MARKER_OR_RECEIPT
[ "$(active_state)" = active ] || fail SERVICE_NOT_ACTIVE
if [ ! -e "$BASE" ]; then mkdir -m 700 "$BASE"; fi
check_base || fail BACKUP_DIRECTORY
mkdir -m 700 "$SAVE"
active_state > "$SAVE/original-state.txt"
sha256sum "$UNITFILE" > "$SAVE/unit-original.sha256"
chmod 600 "$SAVE/original-state.txt" "$SAVE/unit-original.sha256"
sync
check_original || fail BACKUP_NOT_VERIFIED
echo BMS_ORIGINAL_SAVED
changed=0
rollback() {
    code=$?
    trap - EXIT HUP INT TERM
    if [ "$changed" = 1 ]; then
        if restore_original; then echo BMS_ROLLBACK_VERIFIED; else echo BMS_ROLLBACK_FAILED >&2; exit 3; fi
    fi
    [ "$code" -ne 0 ] || code=1
    exit "$code"
}
trap rollback EXIT HUP INT TERM
(set -C; : > "$MARKER")
changed=1
marker_owned || fail MARKER_NOT_VERIFIED
systemctl --no-block stop "$UNIT"
n=0
while [ "$(active_state)" != inactive ] && [ "$n" -lt 10 ]; do n=$((n+1)); sleep 1; done
[ "$(active_state)" = inactive ] || fail STOP_NOT_VERIFIED
[ "$(systemctl show "$UNIT" -p MainPID --value)" = 0 ] || fail PROCESS_STILL_RUNNING
marker_owned || fail MARKER_NOT_VERIFIED
changed=0
trap - EXIT HUP INT TERM
echo BMS_VENDOR_BLOCK_VERIFIED
report
echo PHYSICAL_PLAYBACK_AND_HDMI_TEST_REQUIRED
