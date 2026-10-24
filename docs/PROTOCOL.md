# GMK67 protocol notes

Reverse-engineered from the traffic of the vendor driver (HID feature reports) and checked on a real
Zuoya GMK67 (USB `05AC:024F`, firmware family HFD801). Everything here was **verified on the keyboard**
unless marked *guess*. Use at your own risk.

## Transport

- Wired USB only. Interface 0 (keyboard, `Usage Page 1 / Usage 6`) exposes a 64-byte feature report
  (no report id). With hidapi that is a 65-byte buffer whose first byte is `0`.
- Every command is a `SetFeature` followed by a `GetFeature` (the reply echoes the command).
- The 2.4G dongle (`USB Dongle`, same VID/PID) does **not** accept these reports. The vendor app does not
  control the keyboard through the dongle either.

## Commands

All start with `04`. A transaction is `04 18` (begin) … `04 f0` (end); macro writes use `04 19` … `04 02`.

| Bytes | Meaning |
|---|---|
| `04 18` / `04 f0` | begin / end |
| `04 13 00 00 00 00 00 00 01` + 1 page | lighting mode (16 bytes used) |
| `04 23 00 00 00 00 00 00 09` + 9 pages | per-key colors (custom mode) |
| `04 11 …09` + 9 pages | key remap table, top layer |
| `04 27 …09` + 9 pages | key remap table, Fn layer |
| `04 19`, `04 15 …09` + 9 pages, `04 02` | macros |
| `04 f5 …09` | read (the vendor app polls it) |

"9 pages" = 576 bytes sent as nine consecutive 64-byte feature reports; the last two bytes are `aa 55`.

### Lighting mode (`04 13`)

```
byte  0     effect id (1 Static, 2 SingleOn, 3 SingleOff, 4 Glittering, 5 Falling, 6 Colourful, 7 Breath,
            8 Spectrum, ... order of the vendor list; 0x80 = custom per-key mode)
byte  1-3   R G B
byte  8     1 = random/rainbow color, 0 = use R G B
byte  9     brightness 1..16
byte 10     speed 1..16
byte 11     direction (some effects)
byte 14-15  aa 55
```

Only ids 1-8 were captured from the vendor app; the names above 8 follow the vendor list order and are unverified.

### Per-key colors (`04 23`)

576-byte area, 4 bytes per key at `light_index * 4`: `[index, R, G, B]`. Then select mode `0x80` with `04 13`.
`light_index` values come from the vendor `KeyboardLayout.xml` (see `gmk67/layout.json`). The two LEDs next to Fn and the
rotary knob are not in this matrix.

### Remap tables (`04 11` top layer, `04 27` Fn layer)

576 bytes, 4 bytes per key at `light_index * 4`. All zero = default function.

| Entry | Meaning |
|---|---|
| `02 00 usage 00` | normal key (HID keyboard usage) |
| `03 lo hi 00` | consumer/media key (16-bit usage, e.g. `e9 00` volume up) |
| `06 00 slot 00` | run macro `slot` (*slots above 0 are a guess*) |

A write replaces the whole table: anything not listed returns to its default.

### Macros (`04 19`, `04 15`)

576-byte area: bytes `0..399` hold one little-endian `u16` offset per macro slot (0 = unused), bodies start at `400`
and end before the `aa 55` trailer (174 bytes of space). A body is a 10-byte header `[n_items, 0 × 9]` followed by
`n_items` items: key event `[usage, 0xb0]` (down) / `[usage, 0x30]` (up), and delay `[lo, hi, 0x00, 0x50, 0x00, 0x00]`
(milliseconds). Events and delays **must alternate**; without delay items the keyboard holds the key down.

## Read-only extras

- USB polling rate: from the endpoint descriptors reported by the hub (`gmk67/usbrate.py`, same data as USBView).
  The keyboard runs at 1000 Hz (full speed, `bInterval = 1`). Changing it is not supported: the vendor app has no such
  setting and no command is known.
- The battery and mode LEDs beside Fn are driven by the firmware; they cannot be set (indexes 97/98 do nothing) or read.
- The Windows volume shown in the knob comes from Core Audio, not from the keyboard.

## Tools

`tools/sniff.py` hooks `NtDeviceIoControlFile` of the vendor `DeviceDriver.exe` with Frida and logs every feature report.
