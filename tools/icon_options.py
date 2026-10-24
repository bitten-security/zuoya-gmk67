"""Draws several icon candidates and a contact sheet:  python tools/icon_options.py <output dir>"""
import math
import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QConicalGradient, QFont, QGuiApplication, QImage, QLinearGradient, QPainter,
                           QPainterPath, QPen, QRadialGradient)


def canvas(size):
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    return img, p, size / 256


def tile(p, s, c1, c2, border="#2d3550"):
    g = QLinearGradient(0, 0, 256 * s, 256 * s)
    g.setColorAt(0, QColor(c1))
    g.setColorAt(1, QColor(c2))
    p.setBrush(g)
    p.setPen(QPen(QColor(border), max(1, 3 * s)))
    p.drawRoundedRect(QRectF(8 * s, 8 * s, 240 * s, 240 * s), 52 * s, 52 * s)


def rainbow(size):                       # A: rainbow keys (current)
    img, p, s = canvas(size)
    tile(p, s, "#1b2030", "#0b0d13")
    kw, gap, x0, y0 = 31 * s, 10 * s, 38 * s, 64 * s
    for r, (n, ind) in enumerate([(5, 0), (4, .5), (3, 1)]):
        for c in range(n):
            col = QColor.fromHsvF(((c / 5 + r * .12) * .85) % 1, .85, 1)
            glow = QColor(col)
            glow.setAlpha(70)
            x, y = x0 + (ind + c) * (kw + gap), y0 + r * (kw + gap)
            p.setPen(Qt.NoPen)
            p.setBrush(glow)
            p.drawRoundedRect(QRectF(x - 5 * s, y - 5 * s, kw + 10 * s, kw + 10 * s), 12 * s, 12 * s)
            p.setBrush(col)
            p.drawRoundedRect(QRectF(x, y, kw, kw), 9 * s, 9 * s)
    bar = QLinearGradient(x0 + 1.3 * (kw + gap), 0, x0 + 4.2 * (kw + gap), 0)
    bar.setColorAt(0, QColor("#5b8cff"))
    bar.setColorAt(1, QColor("#c35bff"))
    p.setBrush(bar)
    p.drawRoundedRect(QRectF(x0 + 1.2 * (kw + gap), y0 + 3 * (kw + gap), 3.1 * (kw + gap) - gap, kw * .8), 9 * s, 9 * s)
    p.end()
    return img


def keycap(size):                        # B: one big keycap with an RGB ring
    img, p, s = canvas(size)
    tile(p, s, "#14161d", "#07080c")
    cx = cy = 128 * s
    ring = QConicalGradient(QPointF(cx, cy), 0)
    for i in range(7):
        ring.setColorAt(i / 6, QColor.fromHsvF(i / 6 % 1 if i < 6 else 0, .9, 1))
    p.setPen(QPen(ring, 16 * s))
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(QRectF(46 * s, 46 * s, 164 * s, 164 * s), 36 * s, 36 * s)
    cap = QLinearGradient(0, 70 * s, 0, 190 * s)
    cap.setColorAt(0, QColor("#2c3140"))
    cap.setColorAt(1, QColor("#1a1d27"))
    p.setPen(Qt.NoPen)
    p.setBrush(cap)
    p.drawRoundedRect(QRectF(70 * s, 70 * s, 116 * s, 116 * s), 24 * s, 24 * s)
    f = QFont("Segoe UI", int(46 * s))
    f.setBold(True)
    p.setFont(f)
    p.setPen(QColor("#e8ecf6"))
    p.drawText(QRectF(70 * s, 70 * s, 116 * s, 116 * s), Qt.AlignCenter, "67")
    p.end()
    return img


def monogram(size):                      # C: neon gradient tile with a monogram
    img, p, s = canvas(size)
    tile(p, s, "#7c3aed", "#06b6d4", "#a78bfa")
    f = QFont("Segoe UI", int(92 * s))
    f.setBold(True)
    p.setFont(f)
    p.setPen(QColor(0, 0, 0, 70))
    p.drawText(QRectF(4 * s, 8 * s, 256 * s, 256 * s), Qt.AlignCenter, "G67")
    p.setPen(QColor("#ffffff"))
    p.drawText(QRectF(0, 0, 256 * s, 256 * s), Qt.AlignCenter, "G67")
    p.setPen(QPen(QColor(255, 255, 255, 200), 7 * s, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(64 * s, 196 * s), QPointF(192 * s, 196 * s))
    p.end()
    return img


def lineart(size):                       # D: neon line-art keyboard
    img, p, s = canvas(size)
    tile(p, s, "#0d1020", "#05060d", "#1f2a4d")
    g = QLinearGradient(30 * s, 0, 226 * s, 0)
    g.setColorAt(0, QColor("#22d3ee"))
    g.setColorAt(1, QColor("#f472b6"))
    for width, alpha in ((14, 50), (6, 255)):
        c1, c2 = QColor("#22d3ee"), QColor("#f472b6")
        gg = QLinearGradient(30 * s, 0, 226 * s, 0)
        c1.setAlpha(alpha)
        c2.setAlpha(alpha)
        gg.setColorAt(0, c1)
        gg.setColorAt(1, c2)
        p.setPen(QPen(gg, width * s, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(34 * s, 76 * s, 188 * s, 108 * s), 18 * s, 18 * s)
        for r, n in enumerate((6, 6)):
            for c in range(n):
                p.drawPoint(QPointF((58 + c * 28) * s, (102 + r * 26) * s))
        p.drawLine(QPointF(76 * s, 160 * s), QPointF(180 * s, 160 * s))
    p.end()
    return img


def knob(size):                          # E: rotary knob with a rainbow arc
    img, p, s = canvas(size)
    tile(p, s, "#171a24", "#08090e")
    cx = cy = 128 * s
    arc = QConicalGradient(QPointF(cx, cy), 225)
    for i, h in enumerate((0.0, .15, .33, .5, .66, .83)):
        arc.setColorAt(i / 5 * .75, QColor.fromHsvF(h, .9, 1))
    p.setPen(QPen(arc, 18 * s, Qt.SolidLine, Qt.RoundCap))
    p.setBrush(Qt.NoBrush)
    p.drawArc(QRectF(48 * s, 48 * s, 160 * s, 160 * s), 225 * 16, -270 * 16)
    face = QRadialGradient(QPointF(cx, cy - 20 * s), 80 * s)
    face.setColorAt(0, QColor("#3a4052"))
    face.setColorAt(1, QColor("#12141c"))
    p.setPen(QPen(QColor("#4a5266"), 2 * s))
    p.setBrush(face)
    p.drawEllipse(QPointF(cx, cy), 56 * s, 56 * s)
    p.setPen(QPen(QColor("#5b8cff"), 8 * s, Qt.SolidLine, Qt.RoundCap))
    a = math.radians(-35)
    p.drawLine(QPointF(cx + math.cos(a) * 18 * s, cy + math.sin(a) * 18 * s),
               QPointF(cx + math.cos(a) * 44 * s, cy + math.sin(a) * 44 * s))
    p.end()
    return img


OPTIONS = {"A-rainbow-keys": rainbow, "B-keycap-ring": keycap, "C-monogram": monogram,
           "D-neon-lineart": lineart, "E-knob-arc": knob}

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    sheet = QImage(5 * 270 + 20, 330, QImage.Format_ARGB32)
    sheet.fill(QColor("#e9edf5"))
    sp = QPainter(sheet)
    sp.setRenderHint(QPainter.Antialiasing)
    for i, (name, fn) in enumerate(OPTIONS.items()):
        img = fn(256)
        img.save(str(out / f"{name}.png"))
        sp.drawImage(10 + i * 270, 10, img)
        sp.setPen(QColor("#222"))
        f = QFont("Segoe UI", 13)
        f.setBold(True)
        sp.setFont(f)
        sp.drawText(QRectF(10 + i * 270, 272, 256, 40), Qt.AlignCenter, name.split("-")[0] + " · " + name.split("-", 1)[1])
    sp.end()
    sheet.save(str(out / "sheet.png"))
    print("ok", out)
