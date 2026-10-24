import json
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .audio import Volume

LAYOUT = json.loads((Path(__file__).parent / "layout.json").read_text(encoding="utf-8"))


class KeyboardWidget(QWidget):
    """Virtual keyboard: click / ctrl+click / drag to select keys, each key shows its assigned color."""
    selectionChanged = Signal()
    knobClicked = Signal()
    indicatorClicked = Signal()

    KNOB = {"x": 727, "y": 26, "w": 50, "h": 50}      # rotary knob, top right (not part of the LED matrix)

    def __init__(self):
        super().__init__()
        self.keys = LAYOUT["keys"]
        self.knob_selected = False
        self.volume = Volume()
        self.vol_state = self.volume.read()
        self._vol_timer = QTimer(self, interval=250)
        self._vol_timer.timeout.connect(self._poll_volume)
        self._vol_timer.start()
        self.colors = {}          # light index -> (r, g, b)
        self.selected = set()
        self.setMinimumSize(560, 215)
        self.setMouseTracking(True)
        self._drag_start = None
        self._drag_rect = None
        self._base = set()

    def sizeHint(self):
        return QSize(800, 300)

    def _scale(self):
        pad = 14
        s = min((self.width() - 2 * pad) / (LAYOUT["width"] - 10), (self.height() - 2 * pad) / (LAYOUT["height"] - 100))
        return s, pad

    def _rect(self, k):
        s, pad = self._scale()
        return QRectF(pad + (k["x"] - 29) * s, pad + (k["y"] - 32) * s, k["w"] * s, k["h"] * s)

    def key_at(self, pos):
        for k in self.keys:
            if self._rect(k).contains(QPointF(pos)):
                return k
        return None

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        if self._rect({"x": 606, "y": 229, "w": 16, "h": 38}).contains(e.position()):
            self.indicatorClicked.emit()
            return
        if self._rect(self.KNOB).contains(e.position()):
            self.volume.toggle_mute()          # same effect as pressing the physical knob
            self._poll_volume()
            self.knobClicked.emit()
            return
        ctrl = bool(e.modifiers() & Qt.ControlModifier)
        self._base = set(self.selected) if ctrl else set()
        self._drag_start = e.position()
        self._drag_rect = None
        k = self.key_at(e.position())
        if k:
            if ctrl and k["idx"] in self.selected:
                self.selected.discard(k["idx"])
            else:
                self.selected = self._base | {k["idx"]}
        elif not ctrl:
            self.selected = set()
        self.selectionChanged.emit()
        self.update()

    def mouseMoveEvent(self, e):
        if self._drag_start is None or not (e.buttons() & Qt.LeftButton):
            return
        r = QRectF(self._drag_start, e.position()).normalized()
        if r.width() + r.height() < 8:
            return
        self._drag_rect = r
        hit = {k["idx"] for k in self.keys if self._rect(k).intersects(r)}
        self.selected = self._base | hit
        self.selectionChanged.emit()
        self.update()

    def mouseReleaseEvent(self, e):
        self._drag_start = None
        self._drag_rect = None
        self.update()

    def _paint_indicators(self, p):
        """The two status LEDs beside Fn (battery above, backlight/connection below). They are driven by the
        keyboard firmware and cannot be set or read, so they are drawn as neutral, non-interactive icons."""
        strip = self._rect({"x": 606, "y": 229, "w": 16, "h": 38})
        p.setPen(QPen(QColor("#2f3647"), 1))
        p.setBrush(QColor("#0c0e13"))
        p.drawRoundedRect(strip, 5, 5)
        cx = strip.center().x()
        r = strip.width() * 0.22
        p.setPen(QPen(QColor("#6b7488"), 1.4))
        p.setBrush(Qt.NoBrush)
        y1 = strip.top() + strip.height() * 0.30
        body = QRectF(cx - r * 1.4, y1 - r * 0.9, r * 2.8, r * 1.8)           # battery glyph
        p.drawRoundedRect(body, 1.5, 1.5)
        p.drawLine(QPointF(body.right() + 1, y1 - r * 0.4), QPointF(body.right() + 1, y1 + r * 0.4))
        y2 = strip.top() + strip.height() * 0.72
        p.drawEllipse(QPointF(cx, y2 - r * 0.2), r * 1.1, r * 1.1)             # bulb glyph
        p.drawLine(QPointF(cx - r * 0.5, y2 + r * 1.3), QPointF(cx + r * 0.5, y2 + r * 1.3))

    def _poll_volume(self):
        state = self.volume.read()
        if state != self.vol_state:
            self.vol_state = state
            self.update()

    def _paint_knob(self, p):
        """Knob with a ring showing the Windows volume, the percentage inside, and a mute sign."""
        r = self._rect(self.KNOB)
        c = r.center()
        rad = min(r.width(), r.height()) / 2
        p.setPen(QPen(QColor("#ffffff") if self.knob_selected else QColor("#4a5266"),
                      2.5 if self.knob_selected else 1.5))
        p.setBrush(QColor("#0c0e13"))
        p.drawEllipse(c, rad, rad)
        if self.vol_state is None:
            return
        pct, muted = self.vol_state
        ring = QRectF(c.x() - rad * 0.86, c.y() - rad * 0.86, rad * 1.72, rad * 1.72)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("#2a3040"), 3.5, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(ring, 225 * 16, -270 * 16)                       # track: 270 degrees, gap at the bottom
        p.setPen(QPen(QColor("#e0485a") if muted else QColor("#5b8cff"), 3.5, Qt.SolidLine, Qt.RoundCap))
        if pct > 0:
            p.drawArc(ring, 225 * 16, int(-270 * 16 * pct / 100))
        font = QFont("Segoe UI", max(7, int(rad * 0.42)))
        font.setBold(True)
        p.setFont(font)
        p.setPen(QColor("#8a93a6") if muted else QColor("#ffffff"))
        p.drawText(QRectF(c.x() - rad, c.y() - rad * 0.55, rad * 2, rad * 1.1), Qt.AlignCenter, str(pct))
        if muted:                                                   # mute sign: crossed-out speaker mark
            p.setPen(QPen(QColor("#e0485a"), 2.5, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(c.x() - rad * 0.5, c.y() + rad * 0.55), QPointF(c.x() + rad * 0.5, c.y() - rad * 0.55))
            p.drawEllipse(c, rad * 0.62, rad * 0.62)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#15181f"))
        p.setPen(QPen(QColor("#2a2f3a"), 1))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 14, 14)
        font = QFont("Segoe UI", 8)
        font.setBold(True)
        p.setFont(font)
        for k in self.keys:
            r = self._rect(k).adjusted(2, 2, -2, -2)
            c = self.colors.get(k["idx"])
            fill = QColor(*c) if c and any(c) else QColor("#232834")
            sel = k["idx"] in self.selected
            p.setPen(QPen(QColor("#ffffff") if sel else QColor("#3a4150"), 2.5 if sel else 1))
            p.setBrush(fill)
            p.drawRoundedRect(r, 6, 6)
            p.setPen(QColor("black") if fill.lightness() > 140 else QColor("#c9d1e0"))
            p.drawText(r, Qt.AlignCenter, k["label"].upper() if len(k["label"]) < 3 else k["label"])
        self._paint_knob(p)
        self._paint_indicators(p)
        if self._drag_rect:
            p.setPen(QPen(QColor("#6aa9ff"), 1, Qt.DashLine))
            p.setBrush(QColor(106, 169, 255, 40))
            p.drawRect(self._drag_rect)
