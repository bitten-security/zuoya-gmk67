"""Read-only: USB polling rate of the keyboard, from the endpoint descriptors the USB hubs report
(the same data USBView shows). Nothing is written to the device."""
import ctypes
import struct
from ctypes import wintypes

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
setupapi = ctypes.WinDLL("setupapi", use_last_error=True)
INVALID = ctypes.c_void_p(-1).value
GUID_USB_HUB = "{f18a0e88-c30c-11d0-8815-00a0c906bed8}"
IOCTL_NODE_INFO = 0x220408
IOCTL_NODE_CONN_INFO_EX = 0x220448
IOCTL_DESCRIPTOR_FROM_NODE = 0x220410
SPEEDS = {0: "low", 1: "full", 2: "high", 3: "super"}


class GUID(ctypes.Structure):
    _fields_ = [("a", wintypes.DWORD), ("b", wintypes.WORD), ("c", wintypes.WORD), ("d", ctypes.c_ubyte * 8)]


class IfData(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("guid", GUID), ("flags", wintypes.DWORD), ("res", ctypes.c_void_p)]


def _guid(s):
    g = GUID()
    ctypes.windll.ole32.CLSIDFromString(s, ctypes.byref(g))
    return g


setupapi.SetupDiGetClassDevsW.restype = ctypes.c_void_p
setupapi.SetupDiGetClassDevsW.argtypes = [ctypes.POINTER(GUID), wintypes.LPCWSTR, wintypes.HWND, wintypes.DWORD]
setupapi.SetupDiEnumDeviceInterfaces.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(GUID),
                                                 wintypes.DWORD, ctypes.POINTER(IfData)]
setupapi.SetupDiGetDeviceInterfaceDetailW.argtypes = [ctypes.c_void_p, ctypes.POINTER(IfData), ctypes.c_void_p,
                                                      wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
k32.CreateFileW.restype = ctypes.c_void_p
k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
                            wintypes.DWORD, ctypes.c_void_p]
k32.DeviceIoControl.argtypes = [ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p,
                                wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
k32.CloseHandle.argtypes = [ctypes.c_void_p]


def _hub_paths():
    g = _guid(GUID_USB_HUB)
    dev = setupapi.SetupDiGetClassDevsW(ctypes.byref(g), None, None, 0x12)      # PRESENT | DEVICEINTERFACE
    paths, i = [], 0
    while True:
        d = IfData()
        d.cbSize = ctypes.sizeof(IfData)
        if not setupapi.SetupDiEnumDeviceInterfaces(dev, None, ctypes.byref(g), i, ctypes.byref(d)):
            break
        need = wintypes.DWORD()
        setupapi.SetupDiGetDeviceInterfaceDetailW(dev, ctypes.byref(d), None, 0, ctypes.byref(need), None)
        buf = ctypes.create_string_buffer(need.value)
        struct.pack_into("I", buf, 0, 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6)
        if setupapi.SetupDiGetDeviceInterfaceDetailW(dev, ctypes.byref(d), buf, need.value, None, None):
            paths.append(ctypes.wstring_at(ctypes.addressof(buf) + 4))
        i += 1
    setupapi.SetupDiDestroyDeviceInfoList(ctypes.c_void_p(dev))
    return paths


def _ioctl(h, code, inbuf, outsize):
    out = ctypes.create_string_buffer(outsize)
    ret = wintypes.DWORD()
    inp = ctypes.create_string_buffer(bytes(inbuf), len(inbuf))
    if not k32.DeviceIoControl(h, code, inp, len(inbuf), out, outsize, ctypes.byref(ret), None):
        return None
    return out.raw[:ret.value]


def _endpoints(cfg):
    """[(interface, endpoint address, bInterval)] for interrupt endpoints of a configuration descriptor."""
    out, pos, iface = [], 0, None
    while pos + 2 <= len(cfg):
        ln, typ = cfg[pos], cfg[pos + 1]
        if ln == 0:
            break
        if typ == 4:
            iface = cfg[pos + 2]
        elif typ == 5 and cfg[pos + 3] & 3 == 3:
            out.append((iface, cfg[pos + 2], cfg[pos + 6]))
        pos += ln
    return out


def polling_rates(vid, pid):
    """[{'kind': 'usb'|'dongle', 'speed', 'interval', 'hz'}] for every present device with this VID/PID."""
    found = []
    for path in _hub_paths():
        h = k32.CreateFileW(path, 0x40000000, 2, None, 3, 0, None)
        if h in (None, INVALID):
            continue
        try:
            node = _ioctl(h, IOCTL_NODE_INFO, bytes(76), 76)
            if not node:
                continue
            for port in range(1, node[6] + 1):
                info = _ioctl(h, IOCTL_NODE_CONN_INFO_EX, struct.pack("I", port) + bytes(200), 4 + 200)
                if not info or len(info) < 35:
                    continue
                dvid, dpid = struct.unpack_from("<HH", info, 4 + 8)
                if (dvid, dpid) != (vid, pid):
                    continue
                speed = info[23]
                hdr = struct.pack("<IBBHHH", port, 0x80, 6, 0x0200, 0, 9)
                first = _ioctl(h, IOCTL_DESCRIPTOR_FROM_NODE, hdr + bytes(9), len(hdr) + 9)
                total = struct.unpack_from("<H", first, len(hdr) + 2)[0]
                hdr = struct.pack("<IBBHHH", port, 0x80, 6, 0x0200, 0, total)
                cfg = _ioctl(h, IOCTL_DESCRIPTOR_FROM_NODE, hdr + bytes(total), len(hdr) + total)[len(hdr):]
                eps = [e for e in _endpoints(cfg) if e[1] & 0x80]            # IN endpoints only
                kbd = next((e for e in eps if e[0] == 0), None)               # interface 0 = the keyboard
                if kbd:
                    interval = kbd[2]
                    hz = 1000 / interval if speed < 2 else 8000 / (2 ** (interval - 1))
                    # the cable exposes 2 HID interfaces, the 2.4G dongle 3
                    found.append({"kind": "usb" if len({e[0] for e in eps}) == 2 else "dongle",
                                  "speed": SPEEDS.get(speed, "?"), "interval": interval, "hz": round(hz)})
        finally:
            k32.CloseHandle(h)
    return found


if __name__ == "__main__":
    for r in polling_rates(0x05AC, 0x024F):
        print(r)
