"""Writes gmk67/icon.png + icon.ico from the chosen design (neon line-art keyboard, see icon_options.py)."""
import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtGui import QGuiApplication

sys.path.insert(0, str(Path(__file__).resolve().parent))
from icon_options import lineart as draw  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "gmk67"


def png_bytes(img):
    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QIODevice.WriteOnly)
    img.save(buf, "PNG")
    return bytes(ba)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    pngs = [png_bytes(draw(n)) for n in sizes]
    (OUT / "icon.png").write_bytes(pngs[-1])
    head = struct.pack("<HHH", 0, 1, len(sizes))
    offset = 6 + 16 * len(sizes)
    entries, data = b"", b""
    for n, png in zip(sizes, pngs):
        entries += struct.pack("<BBBBHHII", n % 256, n % 256, 0, 0, 1, 32, len(png), offset + len(data))
        data += png
    (OUT / "icon.ico").write_bytes(head + entries + data)
    print("wrote", OUT / "icon.png", OUT / "icon.ico")
