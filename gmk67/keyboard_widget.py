import json
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

LAYOUT = json.loads((Path(__file__).parent / "layout.json").read_text(encoding="utf-8"))


class KeyboardWidget(QWidget):
    """Virtual keyboard: click / ctrl+click / drag to select keys, each key shows its assigned color."""
    selectionChanged = Signal()
    knobClicked = Signal()

    KNOB = {"x": 730, "y": 30, "w": 44, "h": 44}      # rotary knob, top right (not part of the LED matrix)

    def __init__(self):
        super().__init__()
        self.keys = LAYOUT["keys"]
        self.knob_selected = False
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
        if self._rect(self.KNOB).contains(e.position()):
            self.knob_selected = not self.knob_selected
            self.update()
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

    def _paint_knob(self, p):
        r = self._rect(self.KNOB)
        c = r.center()
        rad = min(r.width(), r.height()) / 2
        p.setPen(QPen(QColor("#ffffff") if self.knob_selected else QColor("#4a5266"), 2.5 if self.knob_selected else 1.5))
        p.setBrush(QColor("#0c0e13"))
        p.drawEllipse(c, rad, rad)
        p.setPen(QPen(QColor("#2f3647"), 1))
        p.drawEllipse(c, rad * 0.62, rad * 0.62)
        p.setPen(QPen(QColor("#5b8cff"), 3, Qt.SolidLine, Qt.RoundCap))      # indicator notch
        p.drawLine(QPointF(c.x(), c.y() - rad * 0.28), QPointF(c.x(), c.y() - rad * 0.78))

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
        if self._drag_rect:
            p.setPen(QPen(QColor("#6aa9ff"), 1, Qt.DashLine))
            p.setBrush(QColor(106, 169, 255, 40))
            p.drawRect(self._drag_rect)
