"""USB polling rate of the keyboard (read-only). Implemented for Windows only; elsewhere it reports nothing."""
import sys


def polling_rates(vid, pid):
    """[{'kind': 'usb'|'dongle', 'speed', 'interval', 'hz'}]; empty list where unsupported."""
    if sys.platform != "win32":
        return []
    from ._usbrate_win import polling_rates as _rates
    return _rates(vid, pid)
