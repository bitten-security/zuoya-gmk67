"""GMK67 (HFD801, VID 05AC / PID 024F) lighting protocol over 64-byte HID feature reports (wired USB)."""
import time
import hid

VID, PID = 0x05AC, 0x024F

# Effect ids as sent by the vendor app (1..8 confirmed from captures; order follows the vendor list, rest provisional).
EFFECTS = {
    0x01: "Static", 0x02: "SingleOn", 0x03: "SingleOff", 0x04: "Glittering", 0x05: "Falling",
    0x06: "Colourful", 0x07: "Breath", 0x08: "Spectrum", 0x09: "Outward", 0x0A: "Scrolling",
    0x0B: "Rolling", 0x0C: "Rotating", 0x0D: "Explode", 0x0E: "Launch", 0x0F: "Ripples",
    0x10: "Flowing", 0x11: "Pulsating", 0x12: "Tilt", 0x13: "Shuttle", 0x14: "LED Off",
}


MACRO_BASE, MACRO_END = 400, 574      # macro bodies live in bytes 400..573 of the 576-byte area
_LETTERS = {c: 0x04 + i for i, c in enumerate("abcdefghijklmnopqrstuvwxyz")}
_DIGITS = {c: 0x1E + i for i, c in enumerate("1234567890")}
_PUNCT = {" ": 0x2C, "-": 0x2D, "=": 0x2E, "[": 0x2F, "]": 0x30, "\\": 0x31, ";": 0x33, "'": 0x34,
          "`": 0x35, ",": 0x36, ".": 0x37, "/": 0x38, "\n": 0x28, "\t": 0x2B}
_SHIFTED = {c: _DIGITS[d] for c, d in zip("!@#$%^&*()", "1234567890")}
_SHIFTED.update({"_": 0x2D, "+": 0x2E, "{": 0x2F, "}": 0x30, "|": 0x31, ":": 0x33, '"': 0x34, "~": 0x35,
                 "<": 0x36, ">": 0x37, "?": 0x38})
SPECIAL = {"ENTER": 0x28, "TAB": 0x2B, "ESC": 0x29, "BACKSPACE": 0x2A, "SPACE": 0x2C, "DEL": 0x4C,
           "UP": 0x52, "DOWN": 0x51, "LEFT": 0x50, "RIGHT": 0x4F, "CTRL": 0xE0, "SHIFT": 0xE1, "ALT": 0xE2,
           "WIN": 0xE3}


def text_to_events(text):
    """'Hello{ENTER}' -> [(usage, pressed)]. {NAME} inserts a special key; uppercase/symbols add Shift."""
    out, i = [], 0

    def tap(usage, shift=False):
        if shift:
            out.append((0xE1, True))
        out.extend([(usage, True), (usage, False)])
        if shift:
            out.append((0xE1, False))

    while i < len(text):
        ch = text[i]
        if ch == "{" and "}" in text[i:]:
            name = text[i + 1:text.index("}", i)].upper()
            if name in SPECIAL:
                tap(SPECIAL[name])
                i += len(name) + 2
                continue
        if ch.lower() in _LETTERS:
            tap(_LETTERS[ch.lower()], ch.isupper())
        elif ch in _DIGITS:
            tap(_DIGITS[ch])
        elif ch in _PUNCT:
            tap(_PUNCT[ch])
        elif ch in _SHIFTED:
            tap(_SHIFTED[ch], True)
        i += 1
    return out


def macro_body(events, delay_ms=0):
    """Header [n_items, 0*9]; items are events [usage, 0xB0 down / 0x30 up] and delays [lo, hi, 0, 0x50, 0, 0]
    placed between events."""
    items = bytearray()
    n = 0
    for k, (usage, pressed) in enumerate(events):
        if k and delay_ms:
            items += bytes((delay_ms & 0xFF, delay_ms >> 8, 0, 0x50, 0, 0))
            n += 1
        items += bytes((usage, 0xB0 if pressed else 0x30))
        n += 1
    return bytes((n & 0xFF,)) + bytes(9) + bytes(items)


def build_macro_area(macros):
    """macros: [(events, delay_ms)] -> (576-byte area, bytes used). Raises ValueError when it does not fit."""
    area = bytearray(576)
    pos = MACRO_BASE
    for slot, (events, delay) in enumerate(macros):
        body = macro_body(events, delay)
        if pos + len(body) > MACRO_END:
            raise ValueError("macro space full")
        area[slot * 2:slot * 2 + 2] = pos.to_bytes(2, "little")
        area[pos:pos + len(body)] = body
        pos += len(body)
    area[574:576] = b"\xaa\x55"
    return bytes(area), pos - MACRO_BASE


class Keyboard:
    def __init__(self):
        self.dev = None

    @staticmethod
    def find():
        """Wired keyboard interface (keyboard collection that exposes the 64-byte feature report)."""
        found = {}
        for d in hid.enumerate(VID, PID):
            if d["usage_page"] == 1 and d["usage"] == 6 and d["interface_number"] == 0:
                found[d["product_string"]] = d
        # cable first, then the 2.4G dongle (it relays the same 64-byte feature reports)
        return found.get("USB DEVICE") or found.get("USB Dongle")

    @staticmethod
    def connections():
        """Which links are present: wired USB and/or the 2.4G dongle."""
        names = {d["product_string"] for d in hid.enumerate(VID, PID)}
        return {"usb": "USB DEVICE" in names, "dongle": "USB Dongle" in names}

    def open(self):
        d = self.find()
        if not d:
            raise OSError("Keyboard (USB) not found")
        self.dev = hid.device()
        self.dev.open_path(d["path"])

    def close(self):
        if self.dev:
            self.dev.close()
            self.dev = None

    def _send(self, payload):
        buf = bytearray(65)
        buf[1:1 + len(payload)] = bytes(payload)
        self.dev.send_feature_report(bytes(buf))
        time.sleep(0.03)
        self.dev.get_feature_report(0, 65)

    def set_light(self, effect, rgb=(255, 255, 255), random_color=False, brightness=16, speed=11, direction=0):
        """brightness / speed are 1..16 (as observed from the vendor app)."""
        r, g, b = rgb
        self._send([4, 0x18])
        self._send([4, 0x13, 0, 0, 0, 0, 0, 0, 1])
        self._send([effect, r, g, b, 0, 0, 0, 0, 1 if random_color else 0,
                    max(1, min(16, brightness)), max(1, min(16, speed)), direction, 0, 0, 0xAA, 0x55])
        self._send([4, 0xF0])

    def write_macros(self, macros):
        """macros: [(events, delay_ms)] stored in slots 0..n-1 (command 0x19 / 0x15, same 9-page layout)."""
        area, _ = build_macro_area(macros)
        self._send([4, 0x19])
        self._send([4, 0x15, 0, 0, 0, 0, 0, 0, 9])
        for i in range(9):
            self._send(list(area[i * 64:(i + 1) * 64]))
        self._send([4, 0x02])

    def set_custom(self, colors, brightness=15):
        """Per-key colors. colors: {light_index: (r, g, b)}. Data is 9 pages of 64 bytes, 4 bytes per key
        [index, r, g, b] stored at index * 4, ending with aa 55; then custom mode 0x80 is selected."""
        data = bytearray(576)
        for idx, (r, g, b) in colors.items():
            if 0 <= idx <= 142:
                data[idx * 4:idx * 4 + 4] = bytes((idx, r, g, b))
        data[574:576] = b"\xaa\x55"
        self._send([4, 0x18])
        self._send([4, 0x23, 0, 0, 0, 0, 0, 0, 9])
        for i in range(9):
            self._send(list(data[i * 64:(i + 1) * 64]))
        self._send([4, 0xF0])
        self._send([4, 0x18])
        self._send([4, 0x13, 0, 0, 0, 0, 0, 0, 1])
        self._send([0x80, 0xFF, 0, 0, 0, 0, 0, 0, 1, max(1, min(16, brightness)), 0x0F, 0, 0, 0, 0xAA, 0x55])
        self._send([4, 0xF0])
