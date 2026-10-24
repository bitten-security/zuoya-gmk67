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


class Keyboard:
    def __init__(self):
        self.dev = None

    @staticmethod
    def find():
        """Wired keyboard interface (keyboard collection that exposes the 64-byte feature report)."""
        for d in hid.enumerate(VID, PID):
            if d["usage_page"] == 1 and d["usage"] == 6 and d["interface_number"] == 0 \
                    and d["product_string"] == "USB DEVICE":
                return d
        return None

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
