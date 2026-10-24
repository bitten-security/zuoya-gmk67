"""Draws the app icon (a dark tile with a rainbow-lit keyboard) and writes gmk67/icon.png + icon.ico."""
import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt
from PySide6.QtGui import QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPen

OUT = Path(__file__).resolve().parent.parent / "gmk67"


def draw(size):
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    s = size / 256
    bg = QLinearGradient(0, 0, size, size)
    bg.setColorAt(0, QColor("#1b2030"))
    bg.setColorAt(1, QColor("#0b0d13"))
    p.setBrush(bg)
    p.setPen(QPen(QColor("#2d3550"), max(1, 3 * s)))
    p.drawRoundedRect(QRectF(8 * s, 8 * s, 240 * s, 240 * s), 52 * s, 52 * s)

    rows = [(5, 0), (4, 0.5), (3, 1.0)]                    # keys per row, left indent in key units
    kw, gap = 31 * s, 10 * s
    x0, y0 = 38 * s, 64 * s
    for r, (n, indent) in enumerate(rows):
        for c in range(n):
            hue = (c / 5 + r * 0.12) * 0.85
            col = QColor.fromHsvF(hue % 1, 0.85, 1.0)
            glow = QColor(col)
            glow.setAlpha(70)
            x = x0 + (indent + c) * (kw + gap) - indent * 0 * s
            y = y0 + r * (kw + gap)
            p.setPen(Qt.NoPen)
            p.setBrush(glow)
            p.drawRoundedRect(QRectF(x - 5 * s, y - 5 * s, kw + 10 * s, kw + 10 * s), 12 * s, 12 * s)
            p.setBrush(col)
            p.drawRoundedRect(QRectF(x, y, kw, kw), 9 * s, 9 * s)
    bar = QLinearGradient(x0 + 1.3 * (kw + gap), 0, x0 + 4.2 * (kw + gap), 0)   # space bar
    bar.setColorAt(0, QColor("#5b8cff"))
    bar.setColorAt(1, QColor("#c35bff"))
    yb = y0 + 3 * (kw + gap)
    p.setBrush(bar)
    p.drawRoundedRect(QRectF(x0 + 1.2 * (kw + gap), yb, 3.1 * (kw + gap) - gap, kw * 0.8), 9 * s, 9 * s)
    p.end()
    return img


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
